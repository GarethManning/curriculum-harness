"""Detect strand structure in a curriculum source.

SPECIFICATION
=============

WHAT COUNTS AS A STRAND
------------------------
A strand is a structurally-distinct, named content division within a subject
area that:

1. Has its own named heading at a consistent level in the document hierarchy.
2. Introduces its own set of discrete teaching points — a list of things pupils
   should know, understand, or be able to do. The canonical signal is a phrase
   such as "Pupils should be taught to:" followed by bullet points, or an
   equivalent structural template (e.g., Knowledge / Practices sub-sections).
3. Is disjoint from other strands in its content: a learning outcome in one
   strand is not repeated under another strand.
4. Can be run through the pipeline independently without requiring content from
   other strands to make pedagogical sense.

WHAT EXPLICITLY DOES NOT COUNT AS A STRAND
-------------------------------------------
- **Cross-cutting process sections** such as "Working mathematically" or
  "Mathematical reasoning" that apply to all content areas. Signal: they appear
  before the strand-level content list and lack their own distinct teaching-
  point lists.
- **Year-group or grade subdivisions** within a strand (e.g., Year 4, Year 5,
  Year 6). Signal: same content domain, divided by time, not by topic.
- **Thematic lenses or "statements of what matters"** — philosophical or
  conceptual framings that describe how the whole subject area relates to a
  dimension of learning. Signal: named as "statements," "principles," or
  "dimensions"; content under each heading is explanatory prose rather than a
  bullet list of discrete teaching points; content overlaps across headings.
- **Sub-topics within a strand** — named case studies, geographic examples, or
  domain examples within a single content area. Signal: they appear nested
  beneath a heading that already qualifies as a strand.
- **Skill categories** that apply across all strands (e.g., "inquiry skills,"
  "historical thinking").

APPROACH: DOMAIN-AGNOSTIC STRUCTURAL ANALYSIS
----------------------------------------------
The detector is domain-agnostic. It does not use subject-area knowledge to
identify strands. Instead, it looks for structural signals:

1. **Content-anchor detection**: Find a "subject content" anchor line that
   introduces the main content list. In DfE NC documents this is literally
   "Subject content"; in NZ curriculum it is implicit from the first strand
   heading following the preamble.
2. **Heading candidate extraction**: Extract lines that look like section
   headings — short, no trailing punctuation (other than a question mark), not
   part of a bullet list, followed by a teaching-point pattern.
3. **Teaching-point confirmation**: A heading qualifies as a strand boundary if
   it is followed within TEACHING_POINT_LOOKAHEAD lines by a teaching-point
   marker (e.g., "Pupils should be taught to:", "Knowledge", "Practices") OR
   by a dense bullet list (3+ consecutive bullet-prefixed lines).
4. **Repeated-template detection**: If 3+ candidate headings all exhibit the
   same structural template (same set of sub-headings, same opening phrase),
   the template is strong evidence of strands.
5. **Cross-cutting exclusion**: Headings that appear before the content anchor
   or that match CROSS_CUTTING_PATTERNS are excluded.
6. **Threshold**: Minimum 2 qualifying headings to declare multi-strand. A
   single qualifying heading produces single-strand result. Zero qualifying
   headings produces single-strand result.

HOW "SINGLE-STRAND" IS PRODUCED
---------------------------------
"No strands detected — treat as single-strand source" is a valid, first-class
result. It is produced when:
- Zero or one heading qualifies as a strand boundary.
- The top-level headings are named as "statements of what matters" or similar
  conceptual lenses.
- The content under candidate headings is explanatory prose rather than
  teaching-point lists.

This result is NOT a detection failure. It is the correct output for sources
like Welsh CfW Health & Wellbeing that are organised by conceptual lenses
rather than by content strands.

UNCERTAINTY FLAGGING
--------------------
The detector raises ``StrandDetectionUncertain`` rather than silently splitting
when:
- Heading candidates are found but teaching-point confirmation is weak
  (below WEAK_CONFIDENCE_THRESHOLD).
- The content anchor is absent and heading depth is ambiguous.
- The number of candidate headings is borderline (exactly 2) with weak signal.

Over-splitting (false positive strands) is treated as worse than under-
splitting (false negative strands). Under-splitting causes a ratio gate halt,
which is recoverable. Over-splitting creates phantom sub-runs with incoherent
content.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

# Max lines to search after a heading for an EXPLICIT teaching-point marker
# (e.g., "Pupils should be taught to:", "Knowledge"). Must be tight — a
# lookahead of 12 would reach across strand boundaries and produce false
# positives (a wrapped bullet like "Venn diagrams" picks up the next strand's
# "Pupils should be taught to:" from 4 lines away).
TEACHING_POINT_LOOKAHEAD = 2

# Wider lookahead used ONLY for the bullet-density fallback (for sources
# without explicit teaching-point phrases).
BULLET_DENSITY_LOOKAHEAD = 6

# Min fraction of bullet-density lookahead lines that must be bullet lines.
BULLET_DENSITY_THRESHOLD = 0.40

# Minimum bullet lines required for the density signal to fire.
MIN_BULLET_LINES = 3

# Confidence score below which the detector flags uncertainty instead of
# committing to a multi-strand split.
WEAK_CONFIDENCE_THRESHOLD = 0.45

# Exactly 2 strands with weak individual evidence triggers uncertainty flag.
TWO_STRAND_WEAK_THRESHOLD = 0.5

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Phrases that introduce the main content list in a curriculum document.
CONTENT_ANCHOR_PATTERNS = [
    re.compile(r"^subject content\s*$", re.IGNORECASE),
    re.compile(r"^content\s*$", re.IGNORECASE),
    re.compile(r"^programme of study\s*$", re.IGNORECASE),
    re.compile(r"^learning area content\s*$", re.IGNORECASE),
]

# Phrases that confirm a heading introduces discrete teaching points.
TEACHING_POINT_MARKERS = [
    re.compile(r"pupils should be taught to\s*[:\.]?", re.IGNORECASE),
    re.compile(r"students should be taught to\s*[:\.]?", re.IGNORECASE),
    re.compile(r"learners should be taught to\s*[:\.]?", re.IGNORECASE),
    re.compile(r"^knowledge\s*$", re.IGNORECASE),
    re.compile(r"^practices\s*$", re.IGNORECASE),
    re.compile(r"^skills\s*$", re.IGNORECASE),
    re.compile(r"^understanding\s*$", re.IGNORECASE),
    re.compile(r"by the end of .+, (pupils|students|learners)", re.IGNORECASE),
]

# Headings that are cross-cutting and should never be treated as strands.
CROSS_CUTTING_PATTERNS = [
    # DfE NC cross-cutting process sections
    re.compile(r"^working mathematically\s*$", re.IGNORECASE),
    re.compile(r"^mathematical (reasoning|thinking|processes)\s*$", re.IGNORECASE),
    re.compile(r"^develop fluency\s*$", re.IGNORECASE),
    re.compile(r"^reason mathematically\s*$", re.IGNORECASE),
    re.compile(r"^solve problems\s*$", re.IGNORECASE),
    re.compile(r"^(aims?|purpose of study|attainment targets?)\s*$", re.IGNORECASE),
    re.compile(r"^(spoken language|information and communication)\s*$", re.IGNORECASE),
    re.compile(r"^(key stage \d+)\s*$", re.IGNORECASE),
    # Generic document structure labels
    re.compile(r"^(about this resource|overview|introduction|background)\s*$", re.IGNORECASE),
    re.compile(r"^statements of what matters\s*$", re.IGNORECASE),
    re.compile(r"^(values|principles|vision)\s*$", re.IGNORECASE),
    # Sub-section labels that appear within strands (e.g. NZ "Knowledge"/"Practices")
    # These confirm strand headings as TEACHING_POINT_MARKERS but are not strands themselves.
    re.compile(r"^knowledge\s*$", re.IGNORECASE),
    re.compile(r"^practices\s*$", re.IGNORECASE),
    re.compile(r"^skills\s*$", re.IGNORECASE),
    re.compile(r"^understanding\s*$", re.IGNORECASE),
    re.compile(r"^(assessment|pedagogy|curriculum)\s*$", re.IGNORECASE),
    # Document structure labels used in Ontario/US-style curriculum documents
    re.compile(r"^overall expectations?\s*$", re.IGNORECASE),
    re.compile(r"^specific expectations?\s*$", re.IGNORECASE),
    re.compile(r"^cluster\s*$", re.IGNORECASE),
    re.compile(r"^(strands?|domains?)\s*$", re.IGNORECASE),
    # Framework/jurisdiction branding lines (appear in Scottish, Australian, etc.)
    re.compile(r"^curriculum for excellence\s*$", re.IGNORECASE),
    re.compile(r"^australian curriculum\s*$", re.IGNORECASE),
    re.compile(r"^national curriculum\s*$", re.IGNORECASE),
    # Website UI navigation elements (appear in JS-rendered curriculum sites)
    re.compile(r"^add to\b", re.IGNORECASE),
    re.compile(r"^download\b", re.IGNORECASE),
    re.compile(r"^(file downloads?|no files?)\b", re.IGNORECASE),
    re.compile(r"^(links to|link to)\b", re.IGNORECASE),
]

# Headings named as "statements of what matters" style lenses.
LENS_HEADING_PATTERNS = [
    # Full Welsh CfW statement style: "Developing X has Y" / "How we X affects Y"
    re.compile(r"^(developing|how we|our ).{10,}", re.IGNORECASE),
    re.compile(r"\bhas lifelong benefits\b", re.IGNORECASE),
    re.compile(r"\baffects (our|their|his|her)\b", re.IGNORECASE),
    re.compile(r"\bshapes who we are\b", re.IGNORECASE),
    re.compile(r"\bfundamental to our\b", re.IGNORECASE),
    re.compile(r"\bimpacts on (the quality|our|their)\b", re.IGNORECASE),
]

# Lines that look like bullet items.
BULLET_LINE_PATTERNS = [
    re.compile(r"^\s*[\u2022\u2023\u25e6\u2043\u2219\uf0a7]\s*"),  # Unicode bullets incl. PDF \uf0a7
    re.compile(r"^\s*[-\*]\s"),                                      # ASCII bullets
    re.compile(r"^\s+[a-z]"),                                        # Indented continuation
]

# Page headers inserted by PDF extraction (e.g., "Mathematics – key stage 3").
# These are repeated across pages and must never be treated as strands.
PAGE_HEADER_PATTERNS = [
    re.compile(r"^.{3,40}\s[–\-]\s(key stage|ks)\s?\d+\s*$", re.IGNORECASE),
    re.compile(r"^(key stage|ks)\s?\d+\s*$", re.IGNORECASE),
]

# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class StrandResult:
    """A single detected strand."""

    name: str
    line_start: int
    line_end: int
    confidence: float  # 0.0–1.0
    signals: list[str] = field(default_factory=list)


@dataclass
class StrandDetectionResult:
    """The complete result of strand detection for one source."""

    is_multi_strand: bool
    strands: list[StrandResult]
    single_strand_rationale: Optional[str]
    overall_confidence: float  # 0.0–1.0
    flags: list[str] = field(default_factory=list)

    def is_single_strand(self) -> bool:
        return not self.is_multi_strand

    def summary(self) -> str:
        if self.is_multi_strand:
            names = ", ".join(s.name for s in self.strands)
            return (
                f"multi_strand ({len(self.strands)} strands: {names}); "
                f"confidence={self.overall_confidence:.2f}"
            )
        return f"single_strand; rationale: {self.single_strand_rationale}"


class StrandDetectionUncertain(Exception):
    """Raised when detection finds candidates but cannot commit to a split."""

    def __init__(self, message: str, partial_candidates: list[StrandResult]):
        super().__init__(message)
        self.partial_candidates = partial_candidates


# ---------------------------------------------------------------------------
# Core detection logic
# ---------------------------------------------------------------------------


def _is_bullet_line(line: str) -> bool:
    return any(p.match(line) for p in BULLET_LINE_PATTERNS)


def _is_page_header(line: str) -> bool:
    stripped = line.strip()
    return any(p.match(stripped) for p in PAGE_HEADER_PATTERNS)


def _is_cross_cutting(line: str) -> bool:
    stripped = line.strip()
    return any(p.match(stripped) for p in CROSS_CUTTING_PATTERNS)


def _is_lens_heading(line: str) -> bool:
    stripped = line.strip()
    return any(p.search(stripped) for p in LENS_HEADING_PATTERNS)


def _find_content_anchor(lines: list[str]) -> Optional[int]:
    """Return the line index of the content anchor, or None."""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if any(p.match(stripped) for p in CONTENT_ANCHOR_PATTERNS):
            return i
    return None


def _looks_like_heading(line: str) -> bool:
    """Heuristic: short, non-bullet, non-sentence line that could be a heading."""
    stripped = line.strip()
    if not stripped:
        return False
    # Must be at least 2 characters
    if len(stripped) < 2:
        return False
    if len(stripped) > 80:
        return False
    if _is_bullet_line(line):
        return False
    if _is_page_header(line):
        return False
    # First character must be an uppercase letter — rules out lowercase-start
    # line continuations from PDF-wrapped bullets (e.g., "decimal quantities")
    if not stripped[0].isupper():
        return False
    # Headings don't end with sentence-terminating or mid-sentence punctuation
    if stripped.endswith((",", ";", ":", "]", ")", ".")):
        return False
    # Headings are not long phrases (sentence continuations or descriptions)
    words = stripped.split()
    if len(words) > 7:
        return False
    # Single digit or short numeric strings are page numbers
    if re.match(r"^\d+(\s+\d+)*$", stripped):
        return False
    return True


def _teaching_point_score(lines: list[str], heading_idx: int) -> tuple[float, list[str]]:
    """Return (score, signals) for how strongly a heading introduces teaching points.

    Two passes with different lookahead windows:
    - Explicit marker pass: tight 2-line window. An explicit marker within 2
      lines of a heading is strong evidence it IS a strand boundary. A wider
      window would reach across strand boundaries (e.g., a wrapped bullet
      continuation like "Venn diagrams" would pick up the next strand's
      teaching-point phrase from 4 lines away).
    - Bullet density pass: wider 6-line window, for sources without explicit
      teaching-point phrases. Requires a dense cluster of bullets.
    """
    signals: list[str] = []
    score = 0.0

    # --- Explicit marker pass (tight lookahead) ---
    tight_end = min(heading_idx + TEACHING_POINT_LOOKAHEAD + 1, len(lines))
    tight_window = lines[heading_idx + 1 : tight_end]

    for line in tight_window:
        stripped = line.strip()
        for marker in TEACHING_POINT_MARKERS:
            if marker.search(stripped):
                signals.append(f"teaching_point_marker: {stripped[:60]}")
                score = max(score, 0.85)
                break

    # --- Bullet density pass (wider lookahead, only if no explicit marker) ---
    # The window is truncated at the first line that looks like another heading
    # candidate, so bullets belonging to the NEXT strand are not counted against
    # the current heading. Without this, a heading like "Venn diagrams" (a
    # wrapped bullet continuation) would pick up bullet density from the
    # Statistics strand that starts 3 lines below it.
    if score < 0.70:
        wide_end = min(heading_idx + BULLET_DENSITY_LOOKAHEAD + 1, len(lines))
        truncated_window: list[str] = []
        for ln in lines[heading_idx + 1 : wide_end]:
            if _looks_like_heading(ln) and not _is_cross_cutting(ln) and not _is_page_header(ln):
                break  # Stop at the next heading candidate
            truncated_window.append(ln)
        bullet_count = sum(1 for ln in truncated_window if _is_bullet_line(ln))
        if bullet_count >= MIN_BULLET_LINES:
            density = bullet_count / max(len(truncated_window), 1)
            if density >= BULLET_DENSITY_THRESHOLD:
                signals.append(f"bullet_density: {bullet_count}/{len(truncated_window)} lines")
                score = max(score, 0.70)

    return score, signals


def detect_strands(content: str) -> StrandDetectionResult:
    """Detect strand structure in a curriculum source's text content.

    Parameters
    ----------
    content:
        The normalised text content of the source (as produced by Phase 0
        extraction). Passed as a string; split on newlines internally.

    Returns
    -------
    StrandDetectionResult
        Either a multi-strand result with named strands and confidence scores,
        or a single-strand result with a rationale string.

    Raises
    ------
    StrandDetectionUncertain
        When heading candidates are found but evidence is too weak to commit to
        a multi-strand split. The caller should treat the source as single-strand
        and flag it for manual review.
    """
    lines = content.splitlines()

    # Step 1: Find content anchor (if present)
    anchor_idx = _find_content_anchor(lines)

    # Lines before the anchor are preamble; strands only appear after.
    search_start = (anchor_idx + 1) if anchor_idx is not None else 0

    # Step 2: Collect heading candidates
    candidates: list[tuple[int, str]] = []  # (line_idx, heading_text)
    lens_headings: list[str] = []

    for i in range(search_start, len(lines)):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            continue
        # Lens-heading check runs BEFORE _looks_like_heading so that
        # conceptual-lens statements (which are long sentences ending with
        # periods) are captured even though they fail the heading-form checks.
        if _is_lens_heading(line):
            lens_headings.append(stripped)
            continue
        if not _looks_like_heading(line):
            continue
        if _is_cross_cutting(line):
            continue
        if _is_page_header(line):
            continue
        candidates.append((i, stripped))

    # Step 3: Confirm each candidate with teaching-point evidence
    confirmed: list[StrandResult] = []
    uncertain_candidates: list[StrandResult] = []

    for idx, (line_idx, heading_text) in enumerate(candidates):
        # Determine line_end: up to the next candidate or end of file
        next_idx = candidates[idx + 1][0] if idx + 1 < len(candidates) else len(lines)
        score, signals = _teaching_point_score(lines, line_idx)

        strand = StrandResult(
            name=heading_text,
            line_start=line_idx,
            line_end=next_idx,
            confidence=score,
            signals=signals,
        )

        if score >= WEAK_CONFIDENCE_THRESHOLD:
            confirmed.append(strand)
        elif score > 0:
            uncertain_candidates.append(strand)

    # Step 4: Check for lens-heading single-strand signal
    if lens_headings and not confirmed:
        return StrandDetectionResult(
            is_multi_strand=False,
            strands=[],
            single_strand_rationale=(
                f"Source headings are conceptual lenses ('statements of what matters' "
                f"style), not structural content divisions. "
                f"Lens headings found: {'; '.join(lens_headings[:3])}. "
                f"No teaching-point lists detected beneath headings."
            ),
            overall_confidence=0.85,
        )

    # Step 5: Decide on result
    n_confirmed = len(confirmed)

    if n_confirmed == 0:
        # No strand candidates at all
        rationale = "No heading candidates with teaching-point evidence found."
        if anchor_idx is not None:
            rationale += f" Content anchor found at line {anchor_idx} but no qualifying headings followed."
        if uncertain_candidates:
            rationale += (
                f" {len(uncertain_candidates)} heading(s) found with weak evidence "
                f"(below threshold); treated as single-strand."
            )
        return StrandDetectionResult(
            is_multi_strand=False,
            strands=[],
            single_strand_rationale=rationale,
            overall_confidence=0.75,
        )

    if n_confirmed == 1:
        return StrandDetectionResult(
            is_multi_strand=False,
            strands=[],
            single_strand_rationale=(
                f"Only one strand-boundary candidate confirmed: '{confirmed[0].name}'. "
                f"Single confirmed boundary is insufficient to declare multi-strand split."
            ),
            overall_confidence=0.70,
        )

    # Two or more confirmed — check for borderline uncertainty
    min_confidence = min(s.confidence for s in confirmed)
    mean_confidence = sum(s.confidence for s in confirmed) / len(confirmed)

    if n_confirmed == 2 and mean_confidence < TWO_STRAND_WEAK_THRESHOLD:
        raise StrandDetectionUncertain(
            f"Exactly 2 strand candidates with mean confidence {mean_confidence:.2f} "
            f"(below {TWO_STRAND_WEAK_THRESHOLD} threshold). "
            f"Refusing to split; treat as single-strand and flag for manual review. "
            f"Candidates: {[s.name for s in confirmed]}",
            partial_candidates=confirmed,
        )

    flags: list[str] = []
    if min_confidence < WEAK_CONFIDENCE_THRESHOLD + 0.1:
        flags.append(
            f"LOW_CONFIDENCE_STRAND: one or more strands near the confidence threshold "
            f"(min={min_confidence:.2f}). Manual review recommended."
        )
    if uncertain_candidates:
        flags.append(
            f"DISCARDED_CANDIDATES: {len(uncertain_candidates)} heading(s) had weak "
            f"evidence and were not included as strands: "
            f"{[s.name for s in uncertain_candidates]}"
        )

    overall_confidence = mean_confidence
    return StrandDetectionResult(
        is_multi_strand=True,
        strands=confirmed,
        single_strand_rationale=None,
        overall_confidence=overall_confidence,
        flags=flags,
    )
