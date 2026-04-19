"""Dataclasses shared across the reference-authoring pipeline.

These are structurally independent from ``curriculum_harness.types`` —
the reference-authoring subsystem does not reuse harness primitives.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

KUD_COLUMNS = ("know", "understand", "do_skill", "do_disposition")
KNOWLEDGE_TYPES = ("Type 1", "Type 2", "Type 3")
ASSESSMENT_ROUTES = (
    "rubric_with_clear_criteria",
    "reasoning_quality_rubric",
    "multi_informant_observation",
)
UNDERSPECIFICATION_FLAGS = (None, "mild", "moderate", "severe")
STABILITY_FLAGS = (
    "stable",
    "classification_unstable",
    "classification_unreliable",
)

REFERENCE_AUTHORING_VERSION = "0.1.0"


@dataclass
class ContentBlock:
    """One verbatim unit of source content with traceability metadata."""

    block_id: str
    raw_text: str
    block_type: str
    line_start: int
    line_end: int
    heading_path: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SourceInventory:
    source_slug: str
    snapshot_path: str
    manifest_content_hash: str
    phase0_version: str
    source_reference: str
    content_blocks: list[ContentBlock] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_authoring_version": REFERENCE_AUTHORING_VERSION,
            "source_slug": self.source_slug,
            "snapshot_path": self.snapshot_path,
            "manifest_content_hash": self.manifest_content_hash,
            "phase0_version": self.phase0_version,
            "source_reference": self.source_reference,
            "content_blocks": [b.to_dict() for b in self.content_blocks],
        }


@dataclass
class KUDItem:
    """One reference KUD item with full traceability and self-consistency flags."""

    item_id: str
    kud_column: str
    knowledge_type: str
    assessment_route: str
    content_statement: str
    source_block_id: str
    classification_rationale: str
    underspecification_flag: str | None = None
    prerequisite_lts: list[str] = field(default_factory=list)
    stability_flag: str = "stable"
    per_run_classifications: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HaltedBlock:
    """A source block whose KUD classification failed self-consistency or hit severe underspec."""

    block_id: str
    source_block_raw_text: str
    halt_reason: str
    per_run_classifications: list[dict[str, Any]] = field(default_factory=list)
    diagnostic: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReferenceKUD:
    source_slug: str
    snapshot_path: str
    items: list[KUDItem] = field(default_factory=list)
    halted_blocks: list[HaltedBlock] = field(default_factory=list)
    classification_model: str = ""
    classification_temperature: float = 0.3
    self_consistency_runs: int = 3

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_authoring_version": REFERENCE_AUTHORING_VERSION,
            "source_slug": self.source_slug,
            "snapshot_path": self.snapshot_path,
            "classification_model": self.classification_model,
            "classification_temperature": self.classification_temperature,
            "self_consistency_runs": self.self_consistency_runs,
            "items": [i.to_dict() for i in self.items],
            "halted_blocks": [b.to_dict() for b in self.halted_blocks],
        }


@dataclass
class GateResult:
    name: str
    passed: bool
    halting: bool
    diagnostic: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QualityReport:
    source_slug: str
    gate_results: list[GateResult] = field(default_factory=list)
    halted_by: str | None = None
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_authoring_version": REFERENCE_AUTHORING_VERSION,
            "source_slug": self.source_slug,
            "halted_by": self.halted_by,
            "summary": self.summary,
            "gate_results": [g.to_dict() for g in self.gate_results],
        }


def dump_json(obj: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
