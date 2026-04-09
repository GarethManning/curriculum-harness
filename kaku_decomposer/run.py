"""CLI: `python -m kaku_decomposer.run --config path.json [--dry-run] [--resume]`."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env", override=False)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Curriculum decomposer (LangGraph)")
    p.add_argument("--config", required=True, help="Path to run config JSON")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preflight only: load config, resolve paths, imports — no API calls",
    )
    p.add_argument(
        "--resume",
        action="store_true",
        help="Resume from Sqlite checkpoint (thread_id = config runId)",
    )
    return p.parse_args()


def _load_config(path: str) -> dict:
    cfg_path = Path(path)
    if not cfg_path.exists():
        print(f"[run] ERROR: config not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(cfg_path, encoding="utf-8") as f:
        return json.load(f)


def _has_checkpoint(db_path: Path, thread_id: str) -> bool:
    if not db_path.exists():
        return False
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver

        cp = SqliteSaver.from_conn_string(str(db_path))
        state = cp.get({"configurable": {"thread_id": thread_id}})
        return state is not None
    except Exception:
        return False


def preflight(config_path: str, cfg: dict) -> list[str]:
    errors: list[str] = []
    from kaku_decomposer.graph import build_initial_state, compile_graph

    try:
        st = build_initial_state(config_path, cfg)
    except Exception as exc:
        return [f"build_initial_state failed: {exc}"]

    out = Path(st.get("output_path_resolved", ""))
    cp = Path(st.get("checkpoint_db_resolved", ""))

    try:
        out.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        errors.append(f"outputPath not creatable ({out}): {exc}")

    try:
        cp.parent.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        errors.append(f"checkpoint parent not creatable ({cp.parent}): {exc}")

    if not str(st.get("mcp_server_url", "")).startswith("https://"):
        errors.append("mcpServer.url should be an https URL")

    src = cfg.get("source") or {}
    if not src.get("url"):
        errors.append("source.url is required")

    # Import/async compile smoke (opens DB file — no network)
    async def _compile_once() -> None:
        await compile_graph(cp)

    try:
        asyncio.run(_compile_once())
    except Exception as exc:
        errors.append(f"graph compile failed: {exc}")

    return errors


async def _run_pipeline(args: argparse.Namespace, cfg: dict) -> None:
    from kaku_decomposer.graph import build_initial_state, compile_graph

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[run] ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    st = build_initial_state(args.config, cfg)
    st["output_structure"] = cfg.get("outputStructure")
    thread_id = st.get("run_id") or "default_run"
    cp = Path(st.get("checkpoint_db_resolved", ""))

    compiled = await compile_graph(cp)
    thread_cfg = {"configurable": {"thread_id": thread_id}}

    resume = args.resume
    has_cp = _has_checkpoint(cp, thread_id)

    if resume and has_cp:
        print(f"[run] Resuming thread_id={thread_id} from {cp}")
        await compiled.ainvoke(None, config=thread_cfg)
        return

    print(f"[run] Starting run_id={thread_id}, checkpoint={cp}")
    await compiled.ainvoke(dict(st), config=thread_cfg)


def main() -> None:
    args = _parse_args()
    cfg = _load_config(args.config)

    if args.dry_run:
        print("[run] Dry-run preflight (no API calls)")
        errs = preflight(args.config, cfg)
        if errs:
            print("  ✗ Preflight failed:")
            for e in errs:
                print(f"    • {e}")
            sys.exit(1)
        print("  ✓ Preflight passed")
        print(f"  runId:      {cfg.get('runId')}")
        print(f"  outputPath: {cfg.get('outputPath')}")
        print(f"  checkpoint: {cfg.get('checkpointDb')}")
        sys.exit(0)

    asyncio.run(_run_pipeline(args, cfg))


if __name__ == "__main__":
    main()
