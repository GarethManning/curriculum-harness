"""Verification: detect_developmental_scope against all 7 existing reference sources.

Loads stored progression_structure.json and inventory.json for each source.
Does NOT re-run the full pipeline. Reports actual vs expected classifications.

Expected results per task spec (Session 4c-5):
  Common Core 7.RP      → (single_band, high)
  Ontario G7 History    → (single_band, high)
  AP US Gov Unit 1      → (single_band, high)
  Welsh CfW H&W         → (explicit_progression, high)
  Secondary RSHE 2025   → (range_without_bands, high)
  DfE KS3 Mathematics   → (range_without_bands, high)
  NZ Social Sciences    → (range_without_bands, high)

Usage:
    python scripts/verify_developmental_scope_7sources.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from curriculum_harness.reference_authoring.developmental_scope.detect_scope import (
    detect_developmental_scope,
)
from curriculum_harness.reference_authoring.progression.detect_progression import (
    load_progression_structure,
)
from curriculum_harness.reference_authoring.types import ContentBlock, SourceInventory

CORPUS_ROOT = Path(__file__).resolve().parent.parent / "docs" / "reference-corpus"


def _load_inventory(path: Path) -> SourceInventory:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    blocks = [
        ContentBlock(
            block_id=b["block_id"],
            raw_text=b.get("raw_text", ""),
            block_type=b.get("block_type", "paragraph"),
            line_start=b.get("line_start", 0),
            line_end=b.get("line_end", 0),
            heading_path=list(b.get("heading_path", [])),
        )
        for b in raw.get("content_blocks", [])
    ]
    return SourceInventory(
        source_slug=raw.get("source_slug", ""),
        snapshot_path=raw.get("snapshot_path", ""),
        manifest_content_hash=raw.get("manifest_content_hash", ""),
        phase0_version=raw.get("phase0_version", ""),
        source_reference=raw.get("source_reference", ""),
        content_blocks=blocks,
    )


@dataclass
class SourceSpec:
    label: str
    corpus_dir: str
    inventory_path: str  # relative to corpus_dir; None = skip if not found
    progression_path: str
    expected_scope: str
    expected_confidence: str


SOURCES: list[SourceSpec] = [
    SourceSpec(
        label="Common Core 7.RP",
        corpus_dir="common-core-g7-rp",
        inventory_path="inventory.json",
        progression_path="progression_structure.json",
        expected_scope="single_band",
        expected_confidence="high",
    ),
    SourceSpec(
        label="Ontario G7 History",
        corpus_dir="ontario-g7-history",
        inventory_path="inventory.json",
        progression_path="progression_structure.json",
        expected_scope="single_band",
        expected_confidence="high",
    ),
    SourceSpec(
        label="AP US Gov Unit 1",
        corpus_dir="ap-usgov-ced-unit1",
        inventory_path="inventory.json",
        progression_path="progression_structure.json",
        expected_scope="single_band",
        expected_confidence="high",
    ),
    SourceSpec(
        label="Welsh CfW H&W",
        corpus_dir="welsh-cfw-health-wellbeing",
        inventory_path="inventory.json",
        progression_path="progression_structure.json",
        expected_scope="explicit_progression",
        expected_confidence="high",
    ),
    SourceSpec(
        label="Secondary RSHE 2025",
        corpus_dir="secondary-rshe-2025-4c2b",
        inventory_path="inventory.json",
        progression_path="progression_structure.json",
        expected_scope="range_without_bands",
        expected_confidence="high",
    ),
    SourceSpec(
        label="DfE KS3 Mathematics",
        corpus_dir="dfe-ks3-maths",
        inventory_path="inventory.json",
        progression_path="progression_structure.json",
        expected_scope="range_without_bands",
        expected_confidence="high",
    ),
    SourceSpec(
        # NZ SS: use history strand as representative inventory.
        # All 4 strands share the same source_type (nz_curriculum) and
        # the same Level-marker absence pattern. One strand is sufficient
        # for verification.
        label="NZ Social Sciences (history strand)",
        corpus_dir="nz-ss-social-sciences-4c3b/per_strand/history",
        inventory_path="inventory.json",
        progression_path="progression_structure.json",
        expected_scope="range_without_bands",
        expected_confidence="high",
    ),
]


def run_verification() -> int:
    failures = 0
    print("Developmental scope verification — 7 existing reference sources")
    print("=" * 65)
    print()

    for spec in SOURCES:
        corpus_dir = CORPUS_ROOT / spec.corpus_dir
        inv_path = corpus_dir / spec.inventory_path
        prog_path = corpus_dir / spec.progression_path

        if not inv_path.exists():
            print(f"  SKIP  {spec.label}: inventory not found at {inv_path}")
            continue
        if not prog_path.exists():
            print(f"  SKIP  {spec.label}: progression_structure not found at {prog_path}")
            continue

        try:
            inventory = _load_inventory(inv_path)
            progression = load_progression_structure(str(prog_path))
            result = detect_developmental_scope(inventory, progression)
        except Exception as exc:
            failures += 1
            print(f"  ERROR {spec.label}: {exc}")
            continue

        scope_ok = result.developmental_scope == spec.expected_scope
        conf_ok = result.developmental_scope_confidence == spec.expected_confidence

        if scope_ok and conf_ok:
            print(f"  PASS  {spec.label}")
            print(f"        → ({result.developmental_scope}, {result.developmental_scope_confidence})")
            print(f"        source_type={result.source_type}")
        else:
            failures += 1
            print(f"  FAIL  {spec.label}")
            print(f"        Expected: ({spec.expected_scope}, {spec.expected_confidence})")
            print(f"        Got:      ({result.developmental_scope}, {result.developmental_scope_confidence})")
            print(f"        source_type={result.source_type}")
            print(f"        Rationale: {result.detection_rationale}")
            if result.ambiguity_notes:
                print(f"        Ambiguity: {result.ambiguity_notes}")
        print()

    print("-" * 65)
    total = len(SOURCES)
    print(f"Results: {total - failures}/{total} matched expected classifications.")
    if failures == 0:
        print("All sources match. No unexpected classifications.")
    else:
        print(f"STOP: {failures} source(s) did not match — review before committing.")
    return failures


if __name__ == "__main__":
    sys.exit(run_verification())
