"""Sub-run orchestration for multi-strand sources.

When detect_strands() identifies a source as multi-strand, this module
creates a temporary per-strand snapshot for each detected strand (slicing
the original content.txt to the strand's line range), then invokes the
single-strand pipeline on each slice independently.

Each sub-run produces a full reference corpus under a per-strand output
directory. The caller is responsible for stitching the sub-run outputs.

Design decisions:
- Temporary snapshots contain sliced content.txt and a copy of the original
  manifest.json (with source_slug updated to the strand-specific slug).
- Per-strand pipeline is called by invoking main() from run_pipeline with
  strand-specific argv. This reuses all existing pipeline logic unchanged.
- Token ledger is reset per strand so per-strand cost accounting is possible.
  The orchestrator accumulates per-strand totals and reports them.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from curriculum_harness.reference_authoring.strand.detect_strands import (
        StrandDetectionResult,
        StrandResult,
    )


def _strand_slug(name: str) -> str:
    """Normalise a strand name to a slug suitable for use in file paths and ID prefixes."""
    slug = name.lower()
    slug = re.sub(r"[/\\]", "-", slug)
    slug = re.sub(r"[^a-z0-9-]", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def create_strand_snapshot(
    original_snapshot_path: str,
    strand: "StrandResult",
    all_lines: list[str],
    strand_slug: str,
    parent_dir: str,
) -> str:
    """Create a temporary snapshot directory for one detected strand.

    The strand's content.txt contains lines [strand.line_start, strand.line_end)
    from the original content. The manifest.json is copied with source_slug
    updated to "<original_slug>-<strand_slug>".

    Returns the path to the created snapshot directory.
    """
    strand_dir = os.path.join(parent_dir, f"strand-{strand_slug}")
    os.makedirs(strand_dir, exist_ok=True)

    strand_lines = all_lines[strand.line_start : strand.line_end]
    content = "\n".join(strand_lines)
    with open(os.path.join(strand_dir, "content.txt"), "w", encoding="utf-8") as fh:
        fh.write(content)

    manifest_path = os.path.join(original_snapshot_path, "manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as fh:
        manifest: dict[str, Any] = json.load(fh)

    original_slug = os.path.basename(os.path.normpath(original_snapshot_path))
    manifest["source_slug"] = f"{original_slug}-{strand_slug}"
    manifest["parent_source_slug"] = original_slug
    manifest["strand_name"] = strand.name
    manifest["strand_slug"] = strand_slug
    with open(os.path.join(strand_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    return strand_dir


def run_strand_sub_run(
    strand_snapshot_dir: str,
    strand_output_dir: str,
    base_args: dict[str, Any],
) -> int:
    """Invoke the single-strand pipeline on one strand's snapshot.

    Parameters
    ----------
    strand_snapshot_dir:
        Path to the temporary strand snapshot (created by create_strand_snapshot).
    strand_output_dir:
        Output directory for this strand's reference corpus.
    base_args:
        Dict of pipeline arguments to forward: model, runs, temperature,
        cluster_model, domain, dispositional, skip_criteria, skip_lts.

    Returns
    -------
    int
        Exit code from the pipeline main(). 0 = success.
    """
    from curriculum_harness.reference_authoring.pipeline.run_pipeline import main
    from curriculum_harness._anthropic import LEDGER as _TOKEN_LEDGER

    _TOKEN_LEDGER.reset()

    argv = [
        "--snapshot", strand_snapshot_dir,
        "--out", strand_output_dir,
    ]
    if base_args.get("model"):
        argv += ["--model", base_args["model"]]
    if base_args.get("runs") is not None:
        argv += ["--runs", str(base_args["runs"])]
    if base_args.get("temperature") is not None:
        argv += ["--temperature", str(base_args["temperature"])]
    if base_args.get("cluster_model"):
        argv += ["--cluster-model", base_args["cluster_model"]]
    if base_args.get("domain"):
        argv += ["--domain", base_args["domain"]]
    if base_args.get("dispositional"):
        argv.append("--dispositional")
    if base_args.get("skip_criteria"):
        argv.append("--skip-criteria")
    if base_args.get("skip_lts"):
        argv.append("--skip-lts")
    # Mark as sub-run: converts artefact_count_ratio from hard halt to flag.
    # Per-strand slices are dense (many KUD items from few blocks) and the
    # gate threshold was calibrated for whole-curriculum sources.
    argv.append("--sub-run")

    exit_code = main(argv)
    per_strand_ledger = _TOKEN_LEDGER.to_dict()
    return exit_code, per_strand_ledger


def run_multi_strand_pipeline(
    original_snapshot_path: str,
    unified_out_dir: str,
    all_lines: list[str],
    strand_result: "StrandDetectionResult",
    base_args: dict[str, Any],
) -> tuple[int, dict[str, Any]]:
    """Orchestrate per-strand sub-runs for a multi-strand source.

    Creates temporary strand snapshots, runs the single-strand pipeline on each,
    and returns the per-strand output directories and token ledger totals.

    Returns
    -------
    (exit_code, run_summary)
        exit_code: 0 if all strands succeeded, 2 if any strand failed.
        run_summary: dict with per_strand_dirs, ledger_by_strand, failed_strands.
    """
    per_strand_out_root = os.path.join(unified_out_dir, "per_strand")
    os.makedirs(per_strand_out_root, exist_ok=True)

    # Temporary directory for strand snapshot content — kept alive for full session
    tmp_snapshot_root = tempfile.mkdtemp(prefix="strand_snapshots_")

    per_strand_dirs: dict[str, str] = {}
    ledger_by_strand: dict[str, dict] = {}
    failed_strands: list[str] = []

    for strand in strand_result.strands:
        slug = _strand_slug(strand.name)
        print(
            f"[refauth:orchestrate] strand '{strand.name}' (slug={slug}, "
            f"lines {strand.line_start}–{strand.line_end}, "
            f"confidence={strand.confidence:.2f})",
            flush=True,
        )

        strand_snapshot_dir = create_strand_snapshot(
            original_snapshot_path=original_snapshot_path,
            strand=strand,
            all_lines=all_lines,
            strand_slug=slug,
            parent_dir=tmp_snapshot_root,
        )
        strand_output_dir = os.path.join(per_strand_out_root, slug)
        os.makedirs(strand_output_dir, exist_ok=True)

        print(f"[refauth:orchestrate] running pipeline on strand '{strand.name}'...", flush=True)
        exit_code, strand_ledger = run_strand_sub_run(
            strand_snapshot_dir=strand_snapshot_dir,
            strand_output_dir=strand_output_dir,
            base_args=base_args,
        )

        per_strand_dirs[slug] = strand_output_dir
        ledger_by_strand[slug] = strand_ledger

        if exit_code != 0:
            print(
                f"[refauth:orchestrate] WARNING: strand '{strand.name}' sub-run "
                f"exited with code {exit_code}. Continuing with remaining strands.",
                flush=True,
            )
            failed_strands.append(slug)
        else:
            print(
                f"[refauth:orchestrate] strand '{strand.name}' complete. "
                f"tokens={strand_ledger.get('total_input_tokens', 0)}in+"
                f"{strand_ledger.get('total_output_tokens', 0)}out",
                flush=True,
            )

    overall_exit = 2 if failed_strands else 0
    return overall_exit, {
        "per_strand_dirs": per_strand_dirs,
        "ledger_by_strand": ledger_by_strand,
        "failed_strands": failed_strands,
        "strand_slugs": [_strand_slug(s.name) for s in strand_result.strands],
        "strand_names": {_strand_slug(s.name): s.name for s in strand_result.strands},
    }
