"""Detect a curriculum source's native progression structure.

DESIGN PRINCIPLE — DOMAIN-AGNOSTIC

The reference-authoring pipeline does NOT impose any specific school's
band framework (such as REAL School Budapest's A-D bands across ages
5-14) on the outputs it produces from external curriculum sources.
Each source has its own native progression structure — Welsh
Curriculum for Wales uses Progression Steps 1-5; US Common Core uses
US grade levels; Scottish CfE uses Early/First/Second/Third/Fourth
Levels; English National Curriculum uses Key Stages 1-4; New Zealand
Curriculum uses Levels 1-8; Ontario uses Canadian grade levels. The
LT authoring skill's "typically A-D across ages 5-14" example is a
REAL-School calibration, not a mandatory output format.

This module reads the source (via its ``SourceInventory``) and returns
a ``ProgressionStructure`` describing the source's own bands. Single-
band sources (a single Common Core grade, a single Ontario grade) are
first-class — ``band_count = 1`` and downstream stages produce a single
statement per LT rather than a band progression.

DETECTION ORDER

1. Lookup by ``source_reference`` URL host + path against a curated
   table of known jurisdictions. This is the high-confidence path. Age
   ranges in the lookup are taken from each issuing body's own
   published documentation, not guessed.
2. Lookup by ``source_slug`` pattern as a backup signal.
3. Source-text inspection: scan ``content_blocks`` for explicit
   progression markers ("Progression Step", "Grade", "Key Stage",
   "Level"). This is the medium-confidence path; it sets
   ``progression_structure_uncertain`` downstream.
4. If nothing matches, raise ``ProgressionDetectionError`` with a
   diagnostic. The pipeline must NOT silently default to A-D.

DETECTION CONFIDENCE → STABILITY FLAG

- ``high``: the structure is taken from the curated lookup. Outputs
  are emitted without a progression-structure-uncertainty flag.
- ``medium``: the structure was inferred from source-text markers.
  Outputs are flagged ``progression_structure_uncertain`` so a
  reviewer knows the band framework itself may need verification.
- ``low``: a permissive fallback was applied because nothing
  authoritative matched. The pipeline normally halts before this; if
  it ever fires, the same uncertainty flag applies.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import urlparse

from curriculum_harness.reference_authoring.types import SourceInventory

PROGRESSION_DETECTION_VERSION = "0.1.0"

DETECTION_CONFIDENCE_LEVELS = ("high", "medium", "low")

PROGRESSION_STRUCTURE_UNCERTAIN_FLAG = "progression_structure_uncertain"


class ProgressionDetectionError(RuntimeError):
    """Raised when no progression structure can be detected for a source.

    The pipeline does NOT default to A-D. A halt with a specific
    diagnostic is the correct behaviour; the operator must add the
    source to the lookup table or correct its source_reference / slug.
    """


@dataclass
class ProgressionStructure:
    """The native progression structure of a single curriculum source.

    For a multi-band source (Welsh CfW, Scottish CfE, etc.)
    ``band_labels`` lists the source's own band names in developmental
    order and ``band_count`` matches its length.

    For a single-band source (one Common Core grade, one Ontario
    grade, etc.) ``band_count == 1`` and ``band_labels`` is a single-
    element list with the grade label. Downstream generators interpret
    this as "no progression sequence inside the source — produce a
    single statement per LT at this grade level".
    """

    band_labels: list[str]
    band_count: int
    age_range_hint: str
    source_type: str
    detection_confidence: str
    detection_rationale: str
    band_self_reflection_prompts: dict[str, str] = field(default_factory=dict)
    source_reference: str = ""
    source_slug: str = ""
    detection_module_version: str = PROGRESSION_DETECTION_VERSION

    def is_single_band(self) -> bool:
        return self.band_count == 1

    def uncertain(self) -> bool:
        return self.detection_confidence in ("medium", "low")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Curated jurisdiction lookup. Each entry's ``age_range_hint`` is taken
# from the issuing jurisdiction's own published documentation, not
# guessed. Citations:
#
# - Welsh Curriculum for Wales: Progression Steps 1-5 across ages 3 to
#   16 — Welsh Government, Curriculum for Wales overview, including the
#   "Designing your curriculum" guidance and the Progression Code 2022
#   (statutory under the Curriculum and Assessment (Wales) Act 2021),
#   published at hwb.gov.wales.
# - US Common Core State Standards: K-12 grade-level standards
#   (Council of Chief State School Officers, CCSSO; Common Core State
#   Standards Initiative). Grade 7 = US Grade 7, age band 12-13 per
#   the Initiative's age/grade alignment.
# - Ontario K-8 curriculum, Grade 7: ages 12-13 per the Ontario
#   Ministry of Education's K-12 schedule.
# - Scottish CfE: Early / First / Second / Third / Fourth Levels +
#   Senior Phase — Education Scotland, "Building the Curriculum" and
#   the CfE benchmarks. Age guidance per Education Scotland: Early
#   3-6, First 5/6-8/9, Second 8/9-11/12, Third 11/12-13/14,
#   Fourth 13/14-14/15, Senior Phase 15-18.
# - England National Curriculum: Key Stages 1-4 per DfE statutory
#   framework. KS1 5-7, KS2 7-11, KS3 11-14, KS4 14-16.
# - New Zealand Curriculum: Levels 1-8 per Ministry of Education NZ
#   "The New Zealand Curriculum"; ages roughly 5-18 across Levels.
# ---------------------------------------------------------------------------

WELSH_CFW_PS_LABELS = [
    "Progression Step 1",
    "Progression Step 2",
    "Progression Step 3",
    "Progression Step 4",
    "Progression Step 5",
]

# Self-reflection prompts for Welsh CfW Progression Steps. Calibrated
# to the cognitive demand expected at each Step in the Welsh
# Government's own Descriptions of Learning across Areas of Learning
# and Experience: PS1 names a single observation; PS2 notices simple
# patterns; PS3 compares own and others' perspectives; PS4 analyses
# patterns across two or more contexts; PS5 articulates developmental
# trajectories and reasoned values.
WELSH_CFW_PS_SELF_REFLECTION_PROMPTS: dict[str, str] = {
    "Progression Step 1": (
        "Tell me about a time this term when you tried something new. What did you do, and how did it feel?"
    ),
    "Progression Step 2": (
        "Describe one thing you have noticed about yourself this term. When does it happen, and when does it not?"
    ),
    "Progression Step 3": (
        "Compare what you have noticed in yourself with what your teacher or family has noticed. Where do these accounts agree, and where do they differ?"
    ),
    "Progression Step 4": (
        "Analyse a pattern you can see in yourself across two or more different settings this term. What changes across settings, and why do you think it changes?"
    ),
    "Progression Step 5": (
        "Trace how your understanding of yourself in this area has developed over time. What values now guide how you act, and what would you still like to develop?"
    ),
}

# Scottish CfE Levels. Self-reflection prompts mapped by analogous
# cognitive demand bands.
SCOTTISH_CFE_LEVEL_LABELS = [
    "Early Level",
    "First Level",
    "Second Level",
    "Third Level",
    "Fourth Level",
    "Senior Phase",
]
SCOTTISH_CFE_SELF_REFLECTION_PROMPTS: dict[str, str] = {
    "Early Level": (
        "Tell me about a time you tried something at school. What did you do, and how did it feel?"
    ),
    "First Level": (
        "Describe one thing you have noticed about yourself this term. When does it happen most?"
    ),
    "Second Level": (
        "Compare what you have noticed about yourself with what your teacher or family has noticed."
    ),
    "Third Level": (
        "Analyse a pattern you can see in yourself across two or more settings. What changes, and why?"
    ),
    "Fourth Level": (
        "Trace how your understanding of yourself in this area has developed across this stage of your learning."
    ),
    "Senior Phase": (
        "Articulate the values that now guide how you act in this area, the evidence those values rest on, and what you still want to develop."
    ),
}

# England NC Key Stages.
ENGLAND_KS_LABELS = ["Key Stage 1", "Key Stage 2", "Key Stage 3", "Key Stage 4"]
ENGLAND_KS_SELF_REFLECTION_PROMPTS: dict[str, str] = {
    "Key Stage 1": (
        "Tell me about a time you tried something hard. What did you do, and how did it feel?"
    ),
    "Key Stage 2": (
        "Describe one thing you have noticed about yourself this term. When does it happen?"
    ),
    "Key Stage 3": (
        "Compare what you have noticed about yourself with what your teachers or family have noticed."
    ),
    "Key Stage 4": (
        "Analyse how your understanding of yourself in this area has developed, and articulate what now guides how you act."
    ),
}

# NZ Curriculum Levels 1-8.
NZ_LEVEL_LABELS = [f"Level {i}" for i in range(1, 9)]


def _nz_self_reflection_prompts() -> dict[str, str]:
    base = {
        1: "Tell me about a time you tried something at school. What did you do?",
        2: "Tell me about a time you tried something hard. What did you do, and how did it feel?",
        3: "Describe one thing you have noticed about yourself this term.",
        4: "Compare what you have noticed about yourself with what your teacher or family has noticed.",
        5: "Compare what you have noticed in yourself across two settings.",
        6: "Analyse a pattern you can see in yourself across two or more settings.",
        7: "Trace how your understanding of yourself in this area has developed over time.",
        8: "Articulate the values that now guide how you act in this area, and what you still want to develop.",
    }
    return {f"Level {i}": text for i, text in base.items()}


def _single_grade_self_reflection_prompt(grade_label: str) -> dict[str, str]:
    """Generic single-grade self-reflection prompt for a grade-level source.

    Single-band sources (one Common Core grade, one Ontario grade) do
    not progress across bands inside the source. The Mode 3 prompt is
    a single grade-appropriate reflection prompt rather than a
    progression. Calibration to the grade's own developmental band is
    deliberately conservative — the pipeline does not have access to
    cross-grade Common Core or Ontario "developmental" wording, so the
    prompt is held at "describe one thing you have noticed" middle-
    grade level.
    """

    return {
        grade_label: (
            f"Describe one thing you have noticed about yourself this term in this area. "
            f"When does it happen, and when does it not? "
            f"(Single-grade source: {grade_label}.)"
        )
    }


def _welsh_cfw_structure(
    *, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    return ProgressionStructure(
        band_labels=list(WELSH_CFW_PS_LABELS),
        band_count=len(WELSH_CFW_PS_LABELS),
        age_range_hint="ages 3-16 (Welsh Government Curriculum for Wales overview, statutory under the Curriculum and Assessment (Wales) Act 2021)",
        source_type="welsh_cfw_aole",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=dict(WELSH_CFW_PS_SELF_REFLECTION_PROMPTS),
        source_reference=source_reference,
        source_slug=source_slug,
    )


def _common_core_grade_structure(
    *, grade: int, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    label = f"Grade {grade}"
    age_low = grade + 5
    age_high = grade + 6
    return ProgressionStructure(
        band_labels=[label],
        band_count=1,
        age_range_hint=(
            f"ages {age_low}-{age_high} (Common Core State Standards Initiative; CCSSO grade alignment)"
        ),
        source_type="us_common_core_grade",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=_single_grade_self_reflection_prompt(label),
        source_reference=source_reference,
        source_slug=source_slug,
    )


def _ontario_grade_structure(
    *, grade: int, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    label = f"Grade {grade}"
    age_low = grade + 5
    age_high = grade + 6
    return ProgressionStructure(
        band_labels=[label],
        band_count=1,
        age_range_hint=(
            f"ages {age_low}-{age_high} (Ontario Ministry of Education K-12 schedule)"
        ),
        source_type="ontario_grade",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=_single_grade_self_reflection_prompt(label),
        source_reference=source_reference,
        source_slug=source_slug,
    )


def _scottish_cfe_structure(
    *, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    return ProgressionStructure(
        band_labels=list(SCOTTISH_CFE_LEVEL_LABELS),
        band_count=len(SCOTTISH_CFE_LEVEL_LABELS),
        age_range_hint=(
            "ages 3-18 (Education Scotland; Building the Curriculum; CfE benchmarks)"
        ),
        source_type="scottish_cfe",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=dict(SCOTTISH_CFE_SELF_REFLECTION_PROMPTS),
        source_reference=source_reference,
        source_slug=source_slug,
    )


def _england_nc_structure(
    *, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    return ProgressionStructure(
        band_labels=list(ENGLAND_KS_LABELS),
        band_count=len(ENGLAND_KS_LABELS),
        age_range_hint=(
            "ages 5-16 (DfE statutory National Curriculum framework; KS1 5-7, KS2 7-11, KS3 11-14, KS4 14-16)"
        ),
        source_type="england_national_curriculum",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=dict(ENGLAND_KS_SELF_REFLECTION_PROMPTS),
        source_reference=source_reference,
        source_slug=source_slug,
    )


def _nz_curriculum_structure(
    *, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    return ProgressionStructure(
        band_labels=list(NZ_LEVEL_LABELS),
        band_count=len(NZ_LEVEL_LABELS),
        age_range_hint=(
            "ages 5-18 (Ministry of Education NZ; The New Zealand Curriculum)"
        ),
        source_type="nz_curriculum",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=_nz_self_reflection_prompts(),
        source_reference=source_reference,
        source_slug=source_slug,
    )


# ---------------------------------------------------------------------------
# URL- and slug-based dispatch
# ---------------------------------------------------------------------------


def _match_url(source_reference: str) -> tuple[str, str] | None:
    """Return (host_lower, path_lower) tuple if the URL parses cleanly."""
    if not source_reference:
        return None
    try:
        parsed = urlparse(source_reference.strip())
    except ValueError:
        return None
    host = (parsed.netloc or "").lower().lstrip("www.")
    path = (parsed.path or "").lower()
    return host, path


_GRADE_FROM_SLUG = re.compile(r"(?:^|[-_])g(?:rade)?[-_]?(\d{1,2})(?:[-_]|$)")


def _grade_from_slug(slug: str) -> int | None:
    if not slug:
        return None
    m = _GRADE_FROM_SLUG.search(slug.lower())
    if not m:
        return None
    g = int(m.group(1))
    if 1 <= g <= 12:
        return g
    return None


def _lookup_high_confidence(
    *, source_reference: str, source_slug: str
) -> ProgressionStructure | None:
    matched = _match_url(source_reference)
    slug_lower = (source_slug or "").lower()

    # --- Welsh CfW (any AOLE) --------------------------------------------------
    if matched is not None:
        host, path = matched
        if host.endswith("hwb.gov.wales") and "curriculum-for-wales" in path:
            return _welsh_cfw_structure(
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    "URL host hwb.gov.wales with /curriculum-for-wales path — "
                    "Welsh Curriculum for Wales uses Progression Steps 1-5 across "
                    "ages 3-16 per Welsh Government statutory specification."
                ),
            )
    if "wales-cfw" in slug_lower or "welsh-cfw" in slug_lower or slug_lower.startswith("wales-"):
        return _welsh_cfw_structure(
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches Welsh CfW pattern — "
                "Welsh Curriculum for Wales uses Progression Steps 1-5."
            ),
        )

    # --- US Common Core (single-grade) ----------------------------------------
    if matched is not None:
        host, path = matched
        if "corestandards.org" in host or "commoncore" in slug_lower:
            grade = _grade_from_slug(slug_lower)
            # Common Core 7.RP slug contains "common-core-7rp" or similar.
            m_rp = re.search(r"(\d{1,2})\.rp", path) if path else None
            if grade is None and m_rp:
                grade = int(m_rp.group(1))
            m_slug_rp = re.search(r"(\d{1,2})rp", slug_lower)
            if grade is None and m_slug_rp:
                grade = int(m_slug_rp.group(1))
            if grade is None:
                grade = _grade_from_slug(slug_lower)
            if grade is not None:
                return _common_core_grade_structure(
                    grade=grade,
                    source_reference=source_reference,
                    source_slug=source_slug,
                    rationale=(
                        f"Common Core source detected (host={host}, slug={source_slug}); "
                        f"grade {grade} extracted. Single-grade source — band_count=1."
                    ),
                )
    if slug_lower.startswith("common-core-") or "common-core-" in slug_lower:
        grade = _grade_from_slug(slug_lower)
        m = re.search(r"(\d{1,2})rp", slug_lower)
        if grade is None and m:
            grade = int(m.group(1))
        if grade is not None:
            return _common_core_grade_structure(
                grade=grade,
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"Source slug '{source_slug}' matches Common Core pattern; "
                    f"grade {grade} extracted. Single-grade source — band_count=1."
                ),
            )

    # --- Ontario K-8 (single-grade) -------------------------------------------
    if matched is not None:
        host, path = matched
        if "edu.gov.on.ca" in host or "ontario.ca" in host:
            grade = _grade_from_slug(slug_lower) or _grade_from_slug(path)
            if grade is not None:
                return _ontario_grade_structure(
                    grade=grade,
                    source_reference=source_reference,
                    source_slug=source_slug,
                    rationale=(
                        f"Ontario Ministry of Education source (host={host}); "
                        f"grade {grade} extracted. Single-grade source — band_count=1."
                    ),
                )
    if slug_lower.startswith("ontario-") or "ontario" in slug_lower:
        grade = _grade_from_slug(slug_lower)
        if grade is not None:
            return _ontario_grade_structure(
                grade=grade,
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"Source slug '{source_slug}' matches Ontario pattern; "
                    f"grade {grade} extracted. Single-grade source — band_count=1."
                ),
            )

    # --- Scottish CfE ---------------------------------------------------------
    if matched is not None:
        host, _path = matched
        if "education.gov.scot" in host or "scotland.gov.uk" in host:
            return _scottish_cfe_structure(
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"Scottish source detected (host={host}); CfE uses Early / "
                    "First / Second / Third / Fourth Levels + Senior Phase."
                ),
            )
    if "scottish-cfe" in slug_lower or "scotland-cfe" in slug_lower:
        return _scottish_cfe_structure(
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches Scottish CfE pattern."
            ),
        )

    # --- England NC -----------------------------------------------------------
    if matched is not None:
        host, path = matched
        if "gov.uk" in host and "national-curriculum" in path:
            return _england_nc_structure(
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"England National Curriculum source detected (host={host}, "
                    f"path includes /national-curriculum). Key Stages 1-4."
                ),
            )
    if slug_lower.startswith("dfe-") or "national-curriculum" in slug_lower or "uk-national-curriculum" in slug_lower:
        return _england_nc_structure(
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches England National Curriculum pattern."
            ),
        )

    # --- NZ Curriculum --------------------------------------------------------
    if matched is not None:
        host, _path = matched
        if "education.govt.nz" in host or "tki.org.nz" in host:
            return _nz_curriculum_structure(
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"New Zealand Curriculum source (host={host}). Levels 1-8."
                ),
            )
    if "nz-curriculum" in slug_lower or "new-zealand-curriculum" in slug_lower:
        return _nz_curriculum_structure(
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches NZ Curriculum pattern."
            ),
        )

    return None


# ---------------------------------------------------------------------------
# Source-text inspection fallback (medium confidence)
# ---------------------------------------------------------------------------


_PROGRESSION_STEP_RE = re.compile(
    r"\bProgression Step ?(\d+)\b", re.IGNORECASE
)
_GRADE_TEXT_RE = re.compile(r"\bGrade ?(\d{1,2})\b", re.IGNORECASE)
_KEY_STAGE_RE = re.compile(r"\bKey Stage ?(\d)\b", re.IGNORECASE)
_LEVEL_RE = re.compile(r"\bLevel ?(\d{1,2})\b", re.IGNORECASE)
_CFE_LEVEL_RE = re.compile(
    r"\b(Early|First|Second|Third|Fourth)\s+Level\b", re.IGNORECASE
)


def _inspect_source_text(
    inventory: SourceInventory, *, source_reference: str, source_slug: str
) -> ProgressionStructure | None:
    text = "\n".join(b.raw_text for b in inventory.content_blocks)

    ps_matches = sorted({int(m.group(1)) for m in _PROGRESSION_STEP_RE.finditer(text)})
    if ps_matches:
        labels = [f"Progression Step {i}" for i in sorted(set(ps_matches))]
        if all(1 <= n <= 5 for n in ps_matches) and len(labels) >= 2:
            # Looks Welsh-CfW-shaped but the URL/slug didn't match.
            return ProgressionStructure(
                band_labels=labels,
                band_count=len(labels),
                age_range_hint="age range unverified — source-text inspection only",
                source_type="welsh_cfw_aole_inferred",
                detection_confidence="medium",
                detection_rationale=(
                    f"Source text contains explicit 'Progression Step' markers "
                    f"({sorted(set(ps_matches))}); structure inferred without "
                    "URL/slug match."
                ),
                band_self_reflection_prompts={
                    label: WELSH_CFW_PS_SELF_REFLECTION_PROMPTS.get(label, "")
                    for label in labels
                },
                source_reference=source_reference,
                source_slug=source_slug,
            )

    cfe_matches = sorted(
        {m.group(1).capitalize() + " Level" for m in _CFE_LEVEL_RE.finditer(text)}
    )
    if cfe_matches and len(cfe_matches) >= 2:
        ordered = [
            label
            for label in SCOTTISH_CFE_LEVEL_LABELS
            if label in cfe_matches
        ]
        return ProgressionStructure(
            band_labels=ordered,
            band_count=len(ordered),
            age_range_hint="age range unverified — source-text inspection only",
            source_type="scottish_cfe_inferred",
            detection_confidence="medium",
            detection_rationale=(
                f"Source text contains CfE Level markers ({ordered}); "
                "structure inferred without URL/slug match."
            ),
            band_self_reflection_prompts={
                label: SCOTTISH_CFE_SELF_REFLECTION_PROMPTS.get(label, "")
                for label in ordered
            },
            source_reference=source_reference,
            source_slug=source_slug,
        )

    ks_matches = sorted({int(m.group(1)) for m in _KEY_STAGE_RE.finditer(text)})
    if ks_matches and all(1 <= n <= 4 for n in ks_matches) and len(ks_matches) >= 2:
        labels = [f"Key Stage {i}" for i in sorted(set(ks_matches))]
        return ProgressionStructure(
            band_labels=labels,
            band_count=len(labels),
            age_range_hint="age range unverified — source-text inspection only",
            source_type="england_national_curriculum_inferred",
            detection_confidence="medium",
            detection_rationale=(
                f"Source text contains explicit Key Stage markers ({ks_matches})."
            ),
            band_self_reflection_prompts={
                label: ENGLAND_KS_SELF_REFLECTION_PROMPTS.get(label, "")
                for label in labels
            },
            source_reference=source_reference,
            source_slug=source_slug,
        )

    grade_matches = sorted({int(m.group(1)) for m in _GRADE_TEXT_RE.finditer(text)})
    if grade_matches and len(grade_matches) == 1 and 1 <= grade_matches[0] <= 12:
        grade = grade_matches[0]
        label = f"Grade {grade}"
        return ProgressionStructure(
            band_labels=[label],
            band_count=1,
            age_range_hint="age range unverified — single-grade source-text inspection",
            source_type="single_grade_inferred",
            detection_confidence="medium",
            detection_rationale=(
                f"Source text contains a single Grade marker ({grade}); "
                "treated as a single-grade source — band_count=1."
            ),
            band_self_reflection_prompts=_single_grade_self_reflection_prompt(label),
            source_reference=source_reference,
            source_slug=source_slug,
        )

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_progression(inventory: SourceInventory) -> ProgressionStructure:
    """Detect the source's native progression structure.

    Tries (1) the curated jurisdiction lookup, then (2) source-text
    inspection. Raises ``ProgressionDetectionError`` if neither
    produces a usable structure — the pipeline is required to halt
    rather than silently default to A-D.
    """

    source_reference = inventory.source_reference or ""
    source_slug = inventory.source_slug or ""

    high = _lookup_high_confidence(
        source_reference=source_reference, source_slug=source_slug
    )
    if high is not None:
        return high

    medium = _inspect_source_text(
        inventory, source_reference=source_reference, source_slug=source_slug
    )
    if medium is not None:
        return medium

    raise ProgressionDetectionError(
        "Could not detect a native progression structure for source "
        f"slug='{source_slug}' reference='{source_reference}'. The "
        "reference-authoring pipeline does NOT default to A-D; add this "
        "source to curriculum_harness.reference_authoring.progression."
        "detect_progression's curated lookup table, or correct its "
        "source_reference / source_slug so an existing entry matches. "
        "Source-text inspection found no Progression Step / Key Stage / "
        "Level / single-Grade markers either."
    )


def load_progression_structure(path: str) -> ProgressionStructure:
    """Load a ``ProgressionStructure`` previously written to JSON."""

    import json

    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return ProgressionStructure(
        band_labels=list(raw.get("band_labels") or []),
        band_count=int(raw.get("band_count") or 0),
        age_range_hint=str(raw.get("age_range_hint") or ""),
        source_type=str(raw.get("source_type") or ""),
        detection_confidence=str(raw.get("detection_confidence") or "low"),
        detection_rationale=str(raw.get("detection_rationale") or ""),
        band_self_reflection_prompts=dict(raw.get("band_self_reflection_prompts") or {}),
        source_reference=str(raw.get("source_reference") or ""),
        source_slug=str(raw.get("source_slug") or ""),
        detection_module_version=str(
            raw.get("detection_module_version") or PROGRESSION_DETECTION_VERSION
        ),
    )


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def band_label_slug(label: str) -> str:
    """Convert a band label to a CSV-safe lowercase slug.

    "Progression Step 1" -> "progression_step_1"
    "Grade 7"            -> "grade_7"
    "Early Level"        -> "early_level"
    """

    s = (label or "").strip().lower()
    s = _SLUG_RE.sub("_", s)
    return s.strip("_")
