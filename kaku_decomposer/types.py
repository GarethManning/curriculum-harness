"""Dataclasses, serialization helpers, and shared constants."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any, TypedDict

HAIKU_MODEL = "claude-haiku-4-5-20251001"

DOCUMENT_FAMILIES = frozenset({
    "exam_specification",
    "national_framework",
    "school_scoped_programme",
    "higher_ed_syllabus",
    "other",
})
LEVEL_MODELS = frozenset({
    "single_intended_level",
    "multi_level_progression",
    "unstructured",
})
SCOPING_STRATEGIES = frozenset({
    "grade_subject_filter",
    "full_document",
    "section_anchor",
})
LT_STATEMENT_FORMATS = frozenset({
    "i_can",
    "outcome_statement",
    "competency_descriptor",
})


class CurriculumProfile(TypedDict, total=False):
    """v1.1 curriculum classification + conventions (stored; Phase 4/5 rendering deferred)."""

    document_family: str
    level_model: str
    scoping_strategy: str
    assessment_signals: dict[str, Any]
    confidence: str
    rationale: str
    source_hints: dict[str, Any]
    output_conventions: dict[str, Any]


def default_output_conventions_for_family(document_family: str) -> dict[str, Any]:
    fam = (document_family or "other").strip().lower()
    if fam == "higher_ed_syllabus":
        return {
            "lt_statement_format": "outcome_statement",
            "recommended_adjacent_radius": 1,
        }
    return {
        "lt_statement_format": "i_can",
        "recommended_adjacent_radius": 1,
    }


def default_scoping_strategy_for_family(document_family: str) -> str:
    fam = (document_family or "other").strip().lower()
    if fam == "higher_ed_syllabus":
        return "full_document"
    if fam == "exam_specification":
        return "section_anchor"
    return "grade_subject_filter"


def normalize_curriculum_profile_fragment(data: dict[str, Any] | None) -> CurriculumProfile:
    """Validate/normalize keys from model or config; fill safe defaults."""
    raw = dict(data or {})
    fam = str(raw.get("document_family", "other")).strip().lower().replace(" ", "_")
    if fam not in DOCUMENT_FAMILIES:
        fam = "other"
    level = str(raw.get("level_model", "unstructured")).strip().lower().replace(" ", "_")
    if level not in LEVEL_MODELS:
        level = "unstructured"
    scope = str(raw.get("scoping_strategy", "")).strip().lower().replace(" ", "_")
    if scope not in SCOPING_STRATEGIES:
        scope = default_scoping_strategy_for_family(fam)
    conf = str(raw.get("confidence", "medium")).strip().lower()
    if conf not in ("high", "medium", "low"):
        conf = "medium"
    signals = raw.get("assessment_signals")
    if not isinstance(signals, dict):
        signals = {}
    oc = raw.get("output_conventions")
    base_oc = default_output_conventions_for_family(fam)
    if isinstance(oc, dict):
        fmt = str(oc.get("lt_statement_format", base_oc["lt_statement_format"])).strip().lower()
        if fmt not in LT_STATEMENT_FORMATS:
            fmt = base_oc["lt_statement_format"]
        try:
            rad = int(oc.get("recommended_adjacent_radius", base_oc["recommended_adjacent_radius"]))
        except (TypeError, ValueError):
            rad = base_oc["recommended_adjacent_radius"]
        base_oc = {"lt_statement_format": fmt, "recommended_adjacent_radius": max(0, rad)}
    hints = raw.get("source_hints")
    if not isinstance(hints, dict):
        hints = {}
    return CurriculumProfile(
        document_family=fam,
        level_model=level,
        scoping_strategy=scope,
        assessment_signals=signals,
        confidence=conf,
        rationale=str(raw.get("rationale", "")).strip(),
        source_hints=hints,
        output_conventions=base_oc,
    )


def merge_curriculum_profile_with_config(
    profile: CurriculumProfile,
    cfg: dict[str, Any],
) -> CurriculumProfile:
    """Config overrides: source.documentFamily, curriculumProfile deep-merge."""
    src = cfg.get("source") or {}
    override_family = src.get("documentFamily")
    if override_family is not None and str(override_family).strip():
        profile = normalize_curriculum_profile_fragment(
            {
                **dict(profile),
                "document_family": str(override_family).strip().lower().replace(" ", "_"),
            }
        )
    user_cp = cfg.get("curriculumProfile")
    if isinstance(user_cp, dict) and user_cp:
        merged = {**dict(profile), **user_cp}
        if isinstance(user_cp.get("assessment_signals"), dict):
            merged["assessment_signals"] = {
                **(profile.get("assessment_signals") or {}),
                **user_cp["assessment_signals"],
            }
        if isinstance(user_cp.get("source_hints"), dict):
            merged["source_hints"] = {**(profile.get("source_hints") or {}), **user_cp["source_hints"]}
        if isinstance(user_cp.get("output_conventions"), dict):
            oc0 = dict(profile.get("output_conventions") or default_output_conventions_for_family(
                str(merged.get("document_family", "other")),
            ))
            oc0.update(user_cp["output_conventions"])
            merged["output_conventions"] = oc0
        profile = normalize_curriculum_profile_fragment(merged)
    oc = dict(profile.get("output_conventions") or {})
    oc.setdefault("recommended_adjacent_radius", 1)
    if "lt_statement_format" not in oc:
        oc["lt_statement_format"] = default_output_conventions_for_family(
            str(profile.get("document_family", "other")),
        )["lt_statement_format"]
    profile = normalize_curriculum_profile_fragment({**dict(profile), "output_conventions": oc})
    return profile
SONNET_MODEL = "claude-sonnet-4-20250514"
API_HARD_TIMEOUT = 240.0
MCP_BETA = "mcp-client-2025-11-20"


class OutputLevel(TypedDict):
    id: str
    label: str
    age_range: str
    cognitive_demand: str


class OutputStructure(TypedDict):
    type: str
    levels: list[OutputLevel]
    input_level_id: str
    generate_adjacent: bool
    adjacent_count: int


class StructuredLT(TypedDict):
    competency: str
    competency_definition: str
    lt_name: str
    lt_definition: str
    level_statements: dict[str, str]
    knowledge_type: str
    flags: list[str]


@dataclass
class ArchitectureDiagnosis:
    architecture_type: str = ""
    proportions: dict[str, float] = field(default_factory=dict)
    hierarchical_elements: list[str] = field(default_factory=list)
    horizontal_elements: list[str] = field(default_factory=list)
    dispositional_elements: list[str] = field(default_factory=list)
    structural_flaw: str = ""
    auto_assessable_pct: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ArchitectureDiagnosis:
        if not data:
            return cls()
        props = data.get("proportions") or {}
        if isinstance(props, dict):
            proportions = {str(k): float(v) for k, v in props.items()}
        else:
            proportions = {}
        return cls(
            architecture_type=str(data.get("architecture_type", "")),
            proportions=proportions,
            hierarchical_elements=list(data.get("hierarchical_elements") or []),
            horizontal_elements=list(data.get("horizontal_elements") or []),
            dispositional_elements=list(data.get("dispositional_elements") or []),
            structural_flaw=str(data.get("structural_flaw", "")),
            auto_assessable_pct=float(data.get("auto_assessable_pct") or 0.0),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class KUDItem:
    content: str
    knowledge_type: str = ""
    assessment_route: str = ""
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KUDItem:
        return cls(
            content=str(data.get("content", "")),
            knowledge_type=str(data.get("knowledge_type", "")),
            assessment_route=str(data.get("assessment_route", "")),
            notes=str(data.get("notes", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class KUD:
    know: list[KUDItem] = field(default_factory=list)
    understand: list[KUDItem] = field(default_factory=list)
    do_skills: list[KUDItem] = field(default_factory=list)
    do_dispositions: list[KUDItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> KUD:
        if not data:
            return cls()

        def items(key: str) -> list[KUDItem]:
            raw = data.get(key) or []
            return [KUDItem.from_dict(x) if isinstance(x, dict) else KUDItem(content=str(x)) for x in raw]

        return cls(
            know=items("know"),
            understand=items("understand"),
            do_skills=items("do_skills"),
            do_dispositions=items("do_dispositions"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "know": [k.to_dict() for k in self.know],
            "understand": [k.to_dict() for k in self.understand],
            "do_skills": [k.to_dict() for k in self.do_skills],
            "do_dispositions": [k.to_dict() for k in self.do_dispositions],
        }

    def all_items(self) -> list[tuple[str, KUDItem]]:
        out: list[tuple[str, KUDItem]] = []
        for k in self.know:
            out.append(("know", k))
        for k in self.understand:
            out.append(("understand", k))
        for k in self.do_skills:
            out.append(("do_skills", k))
        for k in self.do_dispositions:
            out.append(("do_dispositions", k))
        return out


@dataclass
class LearningTarget:
    statement: str
    type: int = 1
    knowledge_type: str = ""
    assessment_route: str = ""
    kud_source: str = ""
    word_count: int = 0
    flags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LearningTarget:
        stmt = str(data.get("statement", ""))
        wc = int(data.get("word_count") or len(stmt.split()))
        return cls(
            statement=stmt,
            type=int(data.get("type") or 1),
            knowledge_type=str(data.get("knowledge_type", "")),
            assessment_route=str(data.get("assessment_route", "")),
            kud_source=str(data.get("kud_source", "")),
            word_count=wc,
            flags=list(data.get("flags") or []),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HumanReviewItem:
    item_type: str
    summary: str
    decision_needed: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def extract_json_object(text: str) -> dict[str, Any] | None:
    """Parse a JSON object from model output (fenced or raw)."""
    if not text or not text.strip():
        return None
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        blob = fence.group(1).strip()
        try:
            return json.loads(blob)
        except json.JSONDecodeError:
            pass
    # raw object
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None
