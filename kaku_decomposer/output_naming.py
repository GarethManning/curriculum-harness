"""Versioned artifact filenames: {runId}_{base}_v{n}.ext — never overwrite."""

from __future__ import annotations

from pathlib import Path


def next_available_artifact_path(out_dir: Path, run_id: str, artifact_base: str, ext: str) -> Path:
    """
    Return the first path ``out_dir / f"{run_id}_{artifact_base}_v{n}.{ext}"`` that does not exist (n >= 1).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    rid = (run_id or "run").strip() or "run"
    base = (artifact_base or "artifact").strip() or "artifact"
    e = ext.lstrip(".")
    n = 1
    while True:
        candidate = out_dir / f"{rid}_{base}_v{n}.{e}"
        if not candidate.exists():
            return candidate
        n += 1


def next_available_structured_lts_paths(out_dir: Path, run_id: str) -> tuple[Path, Path]:
    """JSON + CSV share the same version index so paired artifacts stay aligned."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rid = (run_id or "run").strip() or "run"
    n = 1
    while True:
        json_p = out_dir / f"{rid}_structured_lts_v{n}.json"
        csv_p = out_dir / f"{rid}_structured_lts_v{n}.csv"
        if not json_p.exists() and not csv_p.exists():
            return json_p, csv_p
        n += 1
