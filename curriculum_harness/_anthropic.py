"""Anthropic async client helpers: hard timeouts, streaming, MCP toolsets, token ledger."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from anthropic import AsyncAnthropic

from curriculum_harness.types import API_HARD_TIMEOUT, MCP_BETA

API_HEARTBEAT_INTERVAL = 30.0

# ---------------------------------------------------------------------------
# Cost constants — USD per million tokens (update when Anthropic reprices).
# ---------------------------------------------------------------------------
_COST_PER_MILLION: dict[str, dict[str, float]] = {
    "haiku":  {"input": 0.80,  "output": 4.00},   # claude-haiku-4-5
    "sonnet": {"input": 3.00,  "output": 15.00},   # claude-sonnet-4
    "opus":   {"input": 15.00, "output": 75.00},   # claude-opus-4
}

# Label prefix → canonical stage name (used by TokenLedger.record).
_LABEL_TO_STAGE: dict[str, str] = {
    "refauth_kud":              "kud_classification",
    "refauth_cluster":          "clustering",
    "refauth_lt":               "lt_generation",
    "refauth_band":             "band_statements",
    "refauth_indicator":        "observation_indicators",
    "refauth_criterion_judge":  "rubric_judge",
    "refauth_criterion":        "rubric_generation",
    "refauth_supporting":       "supporting_components",
}


class _StageTotals:
    __slots__ = ("input_tokens", "output_tokens", "calls", "model")

    def __init__(self, model: str) -> None:
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.calls: int = 0
        self.model: str = model


class TokenLedger:
    """Accumulates per-stage and total token usage across a pipeline run."""

    def __init__(self) -> None:
        self._stages: dict[str, _StageTotals] = {}

    def reset(self) -> None:
        self._stages = {}

    def record(self, *, label: str, model: str, input_tokens: int, output_tokens: int) -> None:
        stage = self._stage_for_label(label)
        if stage not in self._stages:
            self._stages[stage] = _StageTotals(model=model)
        s = self._stages[stage]
        s.input_tokens += input_tokens
        s.output_tokens += output_tokens
        s.calls += 1
        if not s.model:
            s.model = model

    def _stage_for_label(self, label: str) -> str:
        # Longest prefix wins (criterion_judge before criterion).
        for prefix in sorted(_LABEL_TO_STAGE, key=len, reverse=True):
            if label.startswith(prefix):
                return _LABEL_TO_STAGE[prefix]
        return "other"

    @staticmethod
    def _model_family(model_id: str) -> str:
        m = model_id.lower()
        if "haiku" in m:
            return "haiku"
        if "opus" in m:
            return "opus"
        return "sonnet"

    def _stage_cost(self, s: _StageTotals) -> float:
        rates = _COST_PER_MILLION.get(self._model_family(s.model), _COST_PER_MILLION["sonnet"])
        return (s.input_tokens * rates["input"] + s.output_tokens * rates["output"]) / 1_000_000

    def total_input(self) -> int:
        return sum(s.input_tokens for s in self._stages.values())

    def total_output(self) -> int:
        return sum(s.output_tokens for s in self._stages.values())

    def total_cost(self) -> float:
        return sum(self._stage_cost(s) for s in self._stages.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_input_tokens": self.total_input(),
            "total_output_tokens": self.total_output(),
            "per_stage": {
                stage: {
                    "input": s.input_tokens,
                    "output": s.output_tokens,
                    "calls": s.calls,
                    "model": s.model,
                }
                for stage, s in sorted(self._stages.items())
            },
        }

    def summary_line(self) -> str:
        ti = self.total_input()
        to = self.total_output()
        cost = self.total_cost()
        return (
            f"Run complete. Total tokens: {ti:,} input, {to:,} output. "
            f"Estimated cost: ${cost:.4f}."
        )


# Module-level ledger — reset at start of each pipeline run.
LEDGER = TokenLedger()


class AnthropicCallTimeout(RuntimeError):
    """Raised when an Anthropic call exceeds the hard asyncio timeout."""


def get_async_client() -> AsyncAnthropic:
    return AsyncAnthropic()


def mcp_servers_param(url: str, name: str) -> list[dict[str, Any]]:
    return [{"type": "url", "url": url, "name": name}]


def mcp_toolset_single_tool(mcp_server_name: str, tool_name: str) -> dict[str, Any]:
    return {
        "type": "mcp_toolset",
        "mcp_server_name": mcp_server_name,
        "default_config": {"enabled": False},
        "configs": {tool_name: {"enabled": True}},
    }


async def _heartbeat_loop(label: str, started: float) -> None:
    try:
        while True:
            await asyncio.sleep(API_HEARTBEAT_INTERVAL)
            elapsed = time.monotonic() - started
            print(
                f"[api_heartbeat] {label} still in flight — "
                f"elapsed {elapsed:.0f}s / {API_HARD_TIMEOUT:.0f}s",
                flush=True,
            )
    except asyncio.CancelledError:
        return


async def beta_messages_create(
    client: AsyncAnthropic,
    *,
    model: str,
    max_tokens: int,
    messages: list[dict[str, Any]],
    label: str,
    mcp_servers: list[dict[str, Any]] | None = None,
    tools: list[dict[str, Any]] | None = None,
) -> Any:
    """Non-streaming Messages API call with hard timeout (beta MCP optional)."""
    started = time.monotonic()
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if mcp_servers is not None:
        kwargs["mcp_servers"] = mcp_servers
        kwargs["tools"] = tools or []
        kwargs["betas"] = [MCP_BETA]

    print(
        f"[api_call] {label} → Anthropic ({model}) timeout={API_HARD_TIMEOUT}s",
        flush=True,
    )
    hb = asyncio.create_task(_heartbeat_loop(label, started))
    response: Any = None
    try:
        response = await asyncio.wait_for(
            client.beta.messages.create(**kwargs),
            timeout=API_HARD_TIMEOUT,
        )
    except asyncio.TimeoutError as exc:
        elapsed = time.monotonic() - started
        msg = (
            f"[api_timeout] {label} exceeded {API_HARD_TIMEOUT}s "
            f"(elapsed {elapsed:.0f}s)"
        )
        print(msg, flush=True)
        raise AnthropicCallTimeout(msg) from exc
    finally:
        hb.cancel()
        try:
            await hb
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        elapsed = time.monotonic() - started
        print(f"[api_done] {label} completed in {elapsed:.1f}s", flush=True)

    if response is not None:
        try:
            usage = getattr(response, "usage", None)
            if usage is not None:
                LEDGER.record(
                    label=label,
                    model=model,
                    input_tokens=getattr(usage, "input_tokens", 0),
                    output_tokens=getattr(usage, "output_tokens", 0),
                )
        except Exception:
            pass
    return response


async def haiku_stream_text(
    client: AsyncAnthropic,
    *,
    model: str,
    max_tokens: int,
    system: str,
    user_blocks: list[dict[str, Any]],
    label: str,
    temperature: float = 0.0,
) -> str:
    """Accumulate assistant text from a streaming call with hard timeout.

    Temperature defaults to 0.0 so Phase 1 classification and scope
    extraction are deterministic across runs. See
    `docs/diagnostics/2026-04-18-phase1-scoping-diagnosis.md`.
    """
    started = time.monotonic()
    _usage: list[tuple[int, int]] = []  # mutable container to capture from inner coroutine

    async def _consume() -> str:
        parts: list[str] = []
        async with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_blocks}],
            temperature=temperature,
        ) as stream:
            async for text in stream.text_stream:
                parts.append(text)
            try:
                final = await stream.get_final_message()
                usage = getattr(final, "usage", None)
                if usage is not None:
                    _usage.append((
                        getattr(usage, "input_tokens", 0),
                        getattr(usage, "output_tokens", 0),
                    ))
            except Exception:
                pass
        return "".join(parts)

    print(
        f"[api_call] {label} → Anthropic stream ({model}) timeout={API_HARD_TIMEOUT}s",
        flush=True,
    )
    hb = asyncio.create_task(_heartbeat_loop(label, started))
    try:
        result = await asyncio.wait_for(_consume(), timeout=API_HARD_TIMEOUT)
    except asyncio.TimeoutError as exc:
        elapsed = time.monotonic() - started
        msg = (
            f"[api_timeout] {label} exceeded {API_HARD_TIMEOUT}s "
            f"(elapsed {elapsed:.0f}s)"
        )
        print(msg, flush=True)
        raise AnthropicCallTimeout(msg) from exc
    finally:
        hb.cancel()
        try:
            await hb
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        elapsed = time.monotonic() - started
        print(f"[api_done] {label} completed in {elapsed:.1f}s", flush=True)

    if _usage:
        input_t, output_t = _usage[0]
        LEDGER.record(label=label, model=model, input_tokens=input_t, output_tokens=output_t)

    return result


def response_text_content(message: Any) -> str:
    """Concatenate text blocks from a final message object."""
    parts: list[str] = []
    for block in getattr(message, "content", []) or []:
        btype = getattr(block, "type", None)
        if btype == "text":
            parts.append(getattr(block, "text", "") or "")
    return "\n".join(parts)


def response_debug_dump(message: Any) -> str:
    """Serialize message for logging (MCP failures)."""
    try:
        return message.model_dump_json(indent=2)  # type: ignore[no-any-return]
    except Exception:
        return repr(message)
