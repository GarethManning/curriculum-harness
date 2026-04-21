"""Detect a curriculum source's developmental scope.

DEVELOPMENTAL SCOPE vs PROGRESSION STRUCTURE
============================================
``detect_progression`` detects the source's *native progression framework* —
the band structure published by the issuing jurisdiction (Welsh Progression
Steps 1-5, NZ Curriculum Levels 1-8, Ontario grade levels, etc.). A source
is matched to its framework based on URL and slug signals, independent of
what the source document actually contains.

``detect_developmental_scope`` detects a different property: whether the
*specific source document* spans a single developmental point, an explicit
multi-band progression, or a multi-year range without internal banding.

The three values:

- ``single_band``: source targets a single grade, course, or equivalent
  single developmental point. Examples: Common Core 7.RP (Grade 7 only),
  AP US Gov Unit 1 (one course unit), Ontario Grade 7 History.

- ``explicit_progression``: source spans multiple developmental levels AND
  specifies internal bands with expectations at each band. Examples: Welsh
  CfW H&W (Progression Steps 1-5), Scottish CfE (named Levels).

- ``range_without_bands``: source covers a developmental range WITHOUT
  explicit internal banding within that range. The test is whether the
  source provides per-level or per-year expectations within the range —
  NOT merely whether it spans multiple years. Examples: Secondary RSHE 2025
  (KS3+KS4 combined terminal outcomes), DfE KS3 Mathematics (Years 7-9
  without per-year breakdown), NZ Curriculum Social Sciences (multiple NZ
  levels without per-level decomposition in the ingested content).

DETECTION ORDER
===============
1. Curated source_type mapping — the primary high-confidence path.
   ``detect_progression`` has already authenticated the source's jurisdiction;
   this module maps each known source_type to the correct developmental scope.

2. Content inspection for ambiguous source types (e.g. ``nz_curriculum``) —
   scans content_blocks for per-level markers. Present → ``explicit_progression``;
   absent in a multi-level framework → ``range_without_bands``.

3. General content inspection fallback for unknown source_types — scans for
   Year/Level/Grade markers and terminal-outcome language.

CONFIDENCE
==========
- ``high``: source_type is in the curated map, OR source_type is a multi-level
  type (e.g. nz_curriculum) and content inspection is conclusive (>= 2 distinct
  level markers present or conclusively absent).
- ``medium``: inferred/unknown source_type, or content inspection with partial
  signals (single ambiguous marker, or mixed terminal + per-level language).
- ``low``: contradictory signals (e.g. source text contains both per-level
  decomposition and terminal-outcome "by end of range" framing). The flag
  surfaces the ambiguity rather than asserting the classification.

FLAGS
=====
``range_without_bands`` sources emit a ``developmental_scope_range_without_bands``
flag on LTs, rubrics, and criterion bank outputs. The flag carries:
- ``domain_type`` so downstream tools (band decomposer) know what developmental
  methodology to apply. Values: "sequential" | "horizontal" | "dispositional".
- Layered explanations: technical, pedagogical-cognitive, pedagogical-dispositional.
  The correct pedagogical explanation is selected based on ``domain_type``.

CONSTRAINTS
===========
- This module detects and flags only. It does NOT attempt developmental
  decomposition. Band decomposition is out of scope for this module.
- Existing reference corpora are NOT retroactively re-processed by this module.
  The flag applies to future pipeline runs. Retroactive flagging of the three
  known range_without_bands sources is a separate task.
- This module does NOT modify detect_progression or any Phase 1-5 pipeline code.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from curriculum_harness.reference_authoring.progression.detect_progression import (
    ProgressionStructure,
)
from curriculum_harness.reference_authoring.types import SourceInventory

DEVELOPMENTAL_SCOPE_VERSION = "0.1.0"

DEVELOPMENTAL_SCOPE_VALUES = (
    "single_band",
    "explicit_progression",
    "range_without_bands",
)
DEVELOPMENTAL_SCOPE_CONFIDENCE_VALUES = ("high", "medium", "low")

DEVELOPMENTAL_SCOPE_FLAG_TYPE = "developmental_scope_range_without_bands"

# ---------------------------------------------------------------------------
# Curated source_type → developmental_scope mapping.
#
# Keyed by the source_type strings emitted by detect_progression. The value
# tuple is (developmental_scope, confidence_from_type_alone). Confidence
# reflects how reliably the source_type alone determines the scope:
#
# - "high": the source_type unambiguously implies the developmental scope.
#   No content inspection needed.
# - "medium": inferred source_type variants (suffix "_inferred") carry the
#   same scope as their curated counterparts, but at reduced confidence
#   because the underlying structure was inferred, not verified from a
#   curated URL/slug table.
#
# Source types NOT in this table (e.g. "nz_curriculum", unknown future types)
# proceed to content inspection.
# ---------------------------------------------------------------------------

_CURATED_MAP: dict[str, tuple[str, str]] = {
    # Single developmental point — single grade, year group, or course unit.
    "us_common_core_grade": ("single_band", "high"),
    "single_grade_inferred": ("single_band", "medium"),
    "ontario_grade": ("single_band", "high"),
    "us_ap_course_unit": ("single_band", "high"),
    # Explicit multi-band progression — source specifies internal bands with
    # per-band expectations.
    "welsh_cfw_aole": ("explicit_progression", "high"),
    "welsh_cfw_aole_inferred": ("explicit_progression", "medium"),
    "scottish_cfe": ("explicit_progression", "high"),
    "scottish_cfe_inferred": ("explicit_progression", "medium"),
    "england_national_curriculum": ("explicit_progression", "high"),
    "england_national_curriculum_inferred": ("explicit_progression", "medium"),
    # Range without internal banding — source covers a multi-year range but
    # presents terminal outcomes without per-year/per-level decomposition.
    "england_rshe_secondary": ("range_without_bands", "high"),
    "england_nc_ks3_only": ("range_without_bands", "high"),
    # Multi-band SEL frameworks with explicit grade-band progression.
    "england_rshe_full": ("explicit_progression", "high"),
    "casel_sel_grade_band": ("explicit_progression", "high"),
    "circle_solutions_sel": ("explicit_progression", "high"),
    # Internal school framework (REAL School Budapest).
    "internal_school_framework": ("explicit_progression", "high"),
}

# ---------------------------------------------------------------------------
# Content inspection regexes.
#
# Used for source types not in the curated map and for content-verification
# of multi-level types like nz_curriculum.
# ---------------------------------------------------------------------------

_LEVEL_RE = re.compile(r"\bLevel\s+\d+\b", re.IGNORECASE)
_PROGRESSION_STEP_RE = re.compile(r"\bProgression Step\s+\d+\b", re.IGNORECASE)
_GRADE_ONLY_RE = re.compile(r"\bGrade\s+\d{1,2}\b", re.IGNORECASE)
_YEAR_ONLY_RE = re.compile(r"\bYear\s+\d{1,2}\b", re.IGNORECASE)
_KEY_STAGE_RE = re.compile(r"\bKey Stage\s+\d\b", re.IGNORECASE)
_TERMINAL_OUTCOME_RE = re.compile(
    r"\b(by the end of|by end of|terminal outcome|end of (key stage|ks\d|secondary|primary)|"
    r"students will know by (age|year)|on completion of)\b",
    re.IGNORECASE,
)


@dataclass
class DevelopmentalScopeResult:
    """The developmental scope classification for a single curriculum source.

    ``developmental_scope`` is one of ``DEVELOPMENTAL_SCOPE_VALUES``.
    ``developmental_scope_confidence`` is one of
    ``DEVELOPMENTAL_SCOPE_CONFIDENCE_VALUES``.

    ``detection_rationale`` explains how the classification was reached.
    ``ambiguity_notes`` (optional) records contradictory signals that were
    resolved or that caused a ``low`` confidence rating.

    ``source_slug`` and ``source_type`` carry forward from the input objects
    for traceability.
    """

    developmental_scope: str
    developmental_scope_confidence: str
    detection_rationale: str
    source_slug: str = ""
    source_type: str = ""
    ambiguity_notes: str = ""
    detection_module_version: str = DEVELOPMENTAL_SCOPE_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _fulltext(inventory: SourceInventory) -> str:
    return "\n".join(b.raw_text for b in inventory.content_blocks)


def _distinct_level_count(text: str) -> int:
    """Number of distinct 'Level N' references found in text."""
    return len(set(re.findall(r"\bLevel\s+(\d+)\b", text, re.IGNORECASE)))


def _distinct_grade_count(text: str) -> int:
    return len(set(re.findall(r"\bGrade\s+(\d{1,2})\b", text, re.IGNORECASE)))


def _distinct_key_stage_count(text: str) -> int:
    return len(set(re.findall(r"\bKey Stage\s+(\d)\b", text, re.IGNORECASE)))


def _has_progression_steps(text: str) -> bool:
    return bool(_PROGRESSION_STEP_RE.search(text))


def _has_terminal_outcome_language(text: str) -> bool:
    return bool(_TERMINAL_OUTCOME_RE.search(text))


def _classify_nz_curriculum(
    inventory: SourceInventory,
    progression_structure: ProgressionStructure,
) -> DevelopmentalScopeResult:
    """Content-inspection path for nz_curriculum source type.

    The NZ curriculum framework has per-level achievement objectives
    (Levels 1-8). A specific source document may or may not present those
    objectives with per-level differentiation. This function checks whether
    the ingested content contains explicit 'Level N' markers.

    If >= 2 distinct Level markers are present: the content IS decomposed
    by level → ``explicit_progression, high``.

    If < 2 Level markers (including zero): the source covers a multi-level
    range but the ingested content does not differentiate by level →
    ``range_without_bands, high``.

    Confidence is high in both cases because:
    - The NZ curriculum URL/slug match already gave us high-confidence
      identification of the jurisdiction.
    - The content inspection result is clear (either multiple Level markers
      are present or they are not).
    The only case that would give medium confidence is if exactly 1 Level
    marker is found (ambiguous: could be a passing reference rather than
    structural decomposition).
    """
    text = _fulltext(inventory)
    level_count = _distinct_level_count(text)

    if level_count >= 2:
        return DevelopmentalScopeResult(
            developmental_scope="explicit_progression",
            developmental_scope_confidence="high",
            detection_rationale=(
                f"NZ curriculum source (high-confidence URL/slug match). "
                f"Content contains {level_count} distinct 'Level N' markers — "
                "per-level decomposition is present."
            ),
            source_slug=inventory.source_slug,
            source_type=progression_structure.source_type,
        )

    if level_count == 1:
        # Single Level reference is ambiguous — could be a passing mention.
        return DevelopmentalScopeResult(
            developmental_scope="range_without_bands",
            developmental_scope_confidence="medium",
            detection_rationale=(
                "NZ curriculum source (high-confidence URL/slug match). "
                "Content contains only 1 'Level N' marker — ambiguous; "
                "classified as range_without_bands but with medium confidence "
                "because the single marker may be a contextual reference rather "
                "than per-level decomposition."
            ),
            source_slug=inventory.source_slug,
            source_type=progression_structure.source_type,
            ambiguity_notes=(
                "Exactly 1 Level marker found. If this source genuinely provides "
                "per-level content, add it to the curated source_type map with "
                "explicit_progression."
            ),
        )

    # Zero Level markers: content covers multiple NZ levels as a range.
    return DevelopmentalScopeResult(
        developmental_scope="range_without_bands",
        developmental_scope_confidence="high",
        detection_rationale=(
            "NZ curriculum source (high-confidence URL/slug match; "
            f"progression_structure has {progression_structure.band_count} bands). "
            "Content contains no 'Level N' markers — source presents "
            "multi-level NZ curriculum content without per-level decomposition."
        ),
        source_slug=inventory.source_slug,
        source_type=progression_structure.source_type,
    )


def _classify_from_content(
    inventory: SourceInventory,
    progression_structure: ProgressionStructure,
) -> DevelopmentalScopeResult:
    """General content-inspection fallback for unknown source types.

    Signal hierarchy (first match wins):
    1. Multiple Progression Step markers → explicit_progression
    2. Multiple Key Stage markers AND no terminal-outcome language → explicit_progression
    3. Multiple Level markers (>= 2 distinct) → explicit_progression
    4. Exactly 1 Grade reference AND no terminal-outcome language → single_band
    5. Terminal-outcome language → range_without_bands
    6. Multiple Year or Grade references → range_without_bands
    7. No interpretable signals → range_without_bands, low (conservative)

    Confidence:
    - high: >= 2 distinct per-level markers with no contradictory signals
    - medium: single marker or mixed signals
    - low: contradictory signals (per-level markers AND terminal-outcome language)
    """
    text = _fulltext(inventory)
    slug = inventory.source_slug
    source_type = progression_structure.source_type

    ps_count = len(set(re.findall(r"\bProgression Step\s+(\d+)\b", text, re.IGNORECASE)))
    ks_count = _distinct_key_stage_count(text)
    lv_count = _distinct_level_count(text)
    gr_count = _distinct_grade_count(text)
    yr_matches = set(re.findall(r"\bYear\s+(\d{1,2})\b", text, re.IGNORECASE))
    has_terminal = _has_terminal_outcome_language(text)

    # Check for explicit_progression signals.
    multi_level_signal = ps_count >= 2 or ks_count >= 2 or lv_count >= 2

    # Check for single_band signals.
    single_grade_signal = gr_count == 1 and lv_count == 0 and ps_count == 0

    # Check for contradictory signals (per-level AND terminal).
    contradictory = multi_level_signal and has_terminal

    if contradictory:
        # Both per-level markers and terminal-outcome language — genuinely ambiguous.
        scope = "explicit_progression" if (ps_count >= 2 or ks_count >= 2 or lv_count >= 2) else "range_without_bands"
        return DevelopmentalScopeResult(
            developmental_scope=scope,
            developmental_scope_confidence="low",
            detection_rationale=(
                f"Content inspection (source_type='{source_type}', slug='{slug}'). "
                f"Contradictory signals: {ps_count} PS / {ks_count} KS / {lv_count} Level markers "
                f"AND terminal-outcome language detected. Classified as '{scope}' "
                "with low confidence; manual review recommended."
            ),
            source_slug=slug,
            source_type=source_type,
            ambiguity_notes=(
                f"Progression Step markers: {ps_count}. Key Stage markers: {ks_count}. "
                f"Level markers: {lv_count}. Terminal-outcome language: yes. "
                "This source may provide per-band content at some levels while "
                "also using terminal-outcome framing."
            ),
        )

    if ps_count >= 2:
        return DevelopmentalScopeResult(
            developmental_scope="explicit_progression",
            developmental_scope_confidence="high",
            detection_rationale=(
                f"Content inspection: {ps_count} distinct Progression Step markers "
                f"found in source text (slug='{slug}'). Per-band decomposition present."
            ),
            source_slug=slug,
            source_type=source_type,
        )

    if ks_count >= 2 and not has_terminal:
        return DevelopmentalScopeResult(
            developmental_scope="explicit_progression",
            developmental_scope_confidence="high",
            detection_rationale=(
                f"Content inspection: {ks_count} distinct Key Stage markers found "
                f"(slug='{slug}'). No terminal-outcome language — per-KS decomposition."
            ),
            source_slug=slug,
            source_type=source_type,
        )

    if lv_count >= 2 and not has_terminal:
        return DevelopmentalScopeResult(
            developmental_scope="explicit_progression",
            developmental_scope_confidence="high",
            detection_rationale=(
                f"Content inspection: {lv_count} distinct Level markers found "
                f"(slug='{slug}'). No terminal-outcome language — per-level decomposition."
            ),
            source_slug=slug,
            source_type=source_type,
        )

    if single_grade_signal and not has_terminal:
        grade_vals = re.findall(r"\bGrade\s+(\d{1,2})\b", text, re.IGNORECASE)
        grade_val = grade_vals[0] if grade_vals else "unknown"
        return DevelopmentalScopeResult(
            developmental_scope="single_band",
            developmental_scope_confidence="high",
            detection_rationale=(
                f"Content inspection: single Grade {grade_val} reference "
                f"(slug='{slug}'). No multi-level markers or terminal-outcome language."
            ),
            source_slug=slug,
            source_type=source_type,
        )

    if has_terminal:
        confidence = "high" if len(yr_matches) == 0 and gr_count == 0 else "medium"
        return DevelopmentalScopeResult(
            developmental_scope="range_without_bands",
            developmental_scope_confidence=confidence,
            detection_rationale=(
                f"Content inspection: terminal-outcome language detected "
                f"(slug='{slug}'). No per-level decomposition markers found. "
                "Source presents outcomes as terminal goals for a developmental range."
            ),
            source_slug=slug,
            source_type=source_type,
        )

    if len(yr_matches) > 1 or gr_count > 1:
        return DevelopmentalScopeResult(
            developmental_scope="range_without_bands",
            developmental_scope_confidence="medium",
            detection_rationale=(
                f"Content inspection: {len(yr_matches)} Year / {gr_count} Grade references "
                f"without per-level decomposition (slug='{slug}'). "
                "Multiple year references without structured per-year learning objectives."
            ),
            source_slug=slug,
            source_type=source_type,
        )

    # No clear signal — conservative fallback.
    return DevelopmentalScopeResult(
        developmental_scope="range_without_bands",
        developmental_scope_confidence="low",
        detection_rationale=(
            f"Content inspection (slug='{slug}'): no clear developmental scope signals. "
            "Conservative fallback to range_without_bands with low confidence. "
            "Add this source to the curated map in detect_scope.py."
        ),
        source_slug=slug,
        source_type=source_type,
        ambiguity_notes="No per-level markers, no terminal-outcome language, no clear single-grade signal.",
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_developmental_scope(
    inventory: SourceInventory,
    progression_structure: ProgressionStructure,
) -> DevelopmentalScopeResult:
    """Detect the developmental scope of a curriculum source.

    This is a companion to ``detect_progression``. Where ``detect_progression``
    identifies the source's native band framework (e.g. NZ Levels 1-8),
    this function determines whether the specific source document provides
    per-band content (``explicit_progression``), targets a single developmental
    point (``single_band``), or covers a range without internal banding
    (``range_without_bands``).

    Detection order:
    1. Curated ``source_type`` → scope mapping (high confidence).
    2. Content inspection for multi-level types (e.g. ``nz_curriculum``).
    3. General content inspection fallback for unknown source types.

    See module docstring for full specification.
    """
    source_type = progression_structure.source_type

    # Step 1: curated map.
    if source_type in _CURATED_MAP:
        scope, confidence = _CURATED_MAP[source_type]
        return DevelopmentalScopeResult(
            developmental_scope=scope,
            developmental_scope_confidence=confidence,
            detection_rationale=(
                f"Curated source_type map: '{source_type}' → '{scope}' "
                f"(confidence={confidence}). No content inspection required."
            ),
            source_slug=inventory.source_slug,
            source_type=source_type,
        )

    # Step 2: content inspection for known multi-level types.
    if source_type == "nz_curriculum":
        return _classify_nz_curriculum(inventory, progression_structure)

    # Step 3: general content inspection fallback.
    return _classify_from_content(inventory, progression_structure)


# ---------------------------------------------------------------------------
# Flag emission
# ---------------------------------------------------------------------------


def make_developmental_scope_flag(
    scope_result: DevelopmentalScopeResult,
    domain_type: str,
) -> dict[str, Any] | None:
    """Emit a developmental scope flag for ``range_without_bands`` sources.

    Returns ``None`` for ``single_band`` and ``explicit_progression`` sources —
    no flag is needed.

    ``domain_type`` should be one of:
    - ``"sequential"``  — hierarchical/propositional knowledge (Type 1/2 cognitive)
    - ``"horizontal"``  — lateral knowledge (Type 2 horizontal)
    - ``"dispositional"`` — dispositional knowledge (Type 3)
    - ``"mixed"``       — source contains multiple domain types

    The flag includes layered explanations:
    - ``explanation_technical``: always present.
    - ``explanation_pedagogical_cognitive``: present when domain_type is not
      "dispositional" — explains why single-grade planning needs band decomposer.
    - ``explanation_pedagogical_dispositional``: present when domain_type is
      "dispositional" or "mixed" — explains why dispositional progression
      doesn't cleanly map to year groups even after decomposition.
    """
    if scope_result.developmental_scope != "range_without_bands":
        return None

    is_dispositional = domain_type in ("dispositional", "mixed")
    is_cognitive = domain_type not in ("dispositional",)

    flag: dict[str, Any] = {
        "flag_type": DEVELOPMENTAL_SCOPE_FLAG_TYPE,
        "confidence_tier": scope_result.developmental_scope_confidence,
        "domain_type": domain_type,
        "source_slug": scope_result.source_slug,
        "source_type": scope_result.source_type,
        "developmental_scope": scope_result.developmental_scope,
        "developmental_scope_confidence": scope_result.developmental_scope_confidence,
        "detection_rationale": scope_result.detection_rationale,
        "explanation_technical": (
            "Source covers a developmental range without explicit source-native bands. "
            "Output describes terminal outcomes for the full range, not expectations "
            "appropriate to any specific year group within the range."
        ),
    }

    if is_cognitive:
        flag["explanation_pedagogical_cognitive"] = (
            "LTs and rubrics describe what students should achieve by end of range, "
            "not what is appropriate for any specific year group within the range. "
            "Use the band decomposer tool before using these outputs for "
            "single-grade planning."
        )

    if is_dispositional:
        flag["explanation_pedagogical_dispositional"] = (
            "LTs describe terminal dispositional outcomes. Dispositional progression "
            "does not cleanly map to year groups even after band decomposition — "
            "teacher judgement is required alongside any banded output from the "
            "band decomposer tool."
        )

    return flag
