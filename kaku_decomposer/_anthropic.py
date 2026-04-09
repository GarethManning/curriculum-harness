"""Anthropic async client helpers: hard timeouts, streaming, MCP toolsets."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from anthropic import AsyncAnthropic

from kaku_decomposer.types import API_HARD_TIMEOUT, MCP_BETA

API_HEARTBEAT_INTERVAL = 30.0


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
    try:
        return await asyncio.wait_for(
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


async def haiku_stream_text(
    client: AsyncAnthropic,
    *,
    model: str,
    max_tokens: int,
    system: str,
    user_blocks: list[dict[str, Any]],
    label: str,
) -> str:
    """Accumulate assistant text from a streaming Haiku call with hard timeout."""
    started = time.monotonic()

    async def _consume() -> str:
        parts: list[str] = []
        async with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_blocks}],
        ) as stream:
            async for text in stream.text_stream:
                parts.append(text)
        return "".join(parts)

    print(
        f"[api_call] {label} → Anthropic stream ({model}) timeout={API_HARD_TIMEOUT}s",
        flush=True,
    )
    hb = asyncio.create_task(_heartbeat_loop(label, started))
    try:
        return await asyncio.wait_for(_consume(), timeout=API_HARD_TIMEOUT)
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
