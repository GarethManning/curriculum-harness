"""Source-bullet extraction — Phase 1 emits a structured list of the
content bullets detected in the scoped curriculum text.

The session-3a plan binds this primitive. Downstream gates
(`validate_source_coverage`, `validate_source_faithfulness`,
`validate_architecture_diagnosis`) prefer this artefact over the Phase
1/2 proxy corpus because bullet-level granularity raises precision on
the source-evidence matcher sharply — Session 2's baseline on felvételi
(18.8 % coverage / 9.7 % faithfulness) was a proxy-corpus artefact,
not a real fidelity measurement.

## What this module does

Rule-based, mechanical bullet detection against the Phase 1 scoped text
(`raw_curriculum`). Three orthogonal detectors, tried in order per
line:

1. `marker_bullet` — lines starting with an explicit bullet character
   (``•``, ``·``, ``▪``, ``■``, ``▫``, ``◦``, ``○``, ``●``, ``*``,
   ``-``, ``–``, ``—``, ``+``).
2. `numbered_outcome` — lines starting with an alphanumeric expectation
   code followed by a lowercase verb (``A1.1 describe...``,
   ``1. solve...``, ``1) compute...``, ``(1) analyse...``,
   ``a) identify...``). Common in national-framework and
   standards-based documents that number learning outcomes.
3. `topic_statement` — a block of short-ish lines (≤ 300 chars) that
   end with a period and sit inside a list block following a line
   ending with a colon (the introducing header). Common in exam
   specifications that list topic areas without explicit markers (the
   felvételi source is the canonical case).

Each emitted bullet carries:

- ``id`` — stable sb_NNN ID.
- ``text`` — the bullet text (whitespace-normalised).
- ``source_location`` — ``line N`` plus ``(under: HEADER)`` where
  applicable.
- ``detector`` — which of the three extractors caught it
  (``marker_bullet | numbered_outcome | topic_statement``). Session 3d
  renamed this from ``bullet_type`` to free that name for the semantic
  classification below.
- ``bullet_type`` (Session 3d) — a semantic category from the enum
  below, used by the coverage gate to weight bullets.

## Semantic bullet_type enum (Session 3d)

The coverage gate is not well served by a 1:1 weighting of every line
the detectors emit — a PDF's front-matter, sample questions, and
teacher prompts all produce bullets indistinguishable from specific
expectations at the detector level. `bullet_type` classifies each
bullet into one of seven categories so the gate can weight them
correctly.

| Value                    | Coverage-gate role     |
|--------------------------|------------------------|
| ``specific_expectation`` | coverage-relevant      |
| ``overall_expectation``  | coverage-relevant      |
| ``sample_question``      | illustrative, excluded |
| ``teacher_prompt``       | illustrative, excluded |
| ``cross_grade``          | extraction error       |
| ``front_matter``         | excluded by default    |
| ``other``                | excluded by default    |

Heuristics (applied in order, first match wins; see
`docs/diagnostics/2026-04-18-ontario-bullet-classification.md` for the
Ontario calibration that produced these):

1. text ends with ``?`` → ``sample_question``.
2. text begins with ``e.g.`` / ``e.g `` / ``(e.g.`` / ``for example``
   → ``teacher_prompt``.
3. text contains ``(Grade N`` where N is present and not the target
   grade → ``cross_grade``. When no target grade is known to the
   extractor, any ``(Grade N`` tag is treated as cross_grade only if
   N ∈ {1..6, 8}. Target grade context is not yet threaded through to
   the classifier; the classifier is intentionally decoupled from
   config so the rule is static.
4. detector == ``numbered_outcome`` → ``specific_expectation``.
5. ``under: HEADER`` phrase matches a known front-matter header token
   (Version history, as follows, The achievement chart, …) →
   ``front_matter``.
6. bullet line number is below ``_FRONT_MATTER_LINE_CUTOFF`` (8000)
   → ``front_matter``. This rule is Ontario-PDF-shaped; see
   adjacent-mechanism #9. Other documents will need calibration.
7. otherwise → ``other``.

## Adjacent mechanisms — what this module does NOT do

Future readers should add to this list, not remove from it.

1. **Narrative prose.** If the source is an unstructured essay (a
   Constitution-style text), no bullets will be emitted. The
   Constitution Tool (upstream, out of this repo) is the correct owner
   for narrative ingestion; this harness explicitly rejects narrative
   as an input mode.
2. **Wrapped continuation lines.** A bullet whose text wraps across
   several extracted lines will be emitted as multiple separate
   bullets, or partially missed if only the continuation ends with a
   period. Merging wrapped lines is not implemented.
3. **Semantic coherence.** The detector does not judge whether a
   detected line is *actually* a content element vs a heading, a date,
   a page number, a figure caption, or metadata. It extracts
   structurally.
4. **Non-Latin scripts / language handling.** The detectors rely on
   ASCII punctuation (``.``, ``:``, ``-``) and work across Latin-script
   languages (English, Hungarian, French, etc.). Fully non-Latin
   scripts (Arabic, Chinese) or right-to-left languages may
   under-extract.
5. **Deduplication.** Text-identical duplicates are collapsed, but
   near-duplicates (whitespace / case variants, paraphrases) are not.
6. **Level assignment.** Bullets do not carry a year / key-stage / band
   tag. Level is the Phase 2 architecture's concern.
7. **Ordering semantics.** Bullets are emitted in reading order, but
   the detector does not preserve hierarchy between a numbered
   expectation and its sub-items. `A1.1` and `A1.2` are siblings, but
   the output is a flat list; nesting is lost.
8. **Confidence.** Every emitted bullet is treated equally; the
   detector cannot say "this one is a clear bullet" vs "this one is
   borderline". Thresholding is by line-length heuristics only.
9. **Grade-grain verification** (Session 3d). The ``bullet_type``
   classifier tags structurally. A bullet tagged
   ``specific_expectation`` is guaranteed to be a detector-captured
   numbered outcome, but **not** guaranteed to be at the target grade
   of the run — Ontario's Grade 7 run captured Grade 1's A1.N
   expectations because Phase 1 scoping under-narrowed. The classifier
   has no target-grade context to tag those as cross_grade.
10. **Curriculum-shape generalisation** (Session 3d). The bullet_type
    heuristics are tuned to Ontario-shape documents. AP CED, IB, UK NC,
    and felvételi PDFs will mis-tag until recalibrated against their
    own corpora.
11. **Overall-expectation detection** (Session 3d). Ontario's overall
    expectations live in section headers the extractors don't emit as
    bullets; ``overall_expectation`` is an enum value but currently
    unreachable by these heuristics on Ontario-shape sources. A future
    calibration pass will need a header-level detector.
12. **Within-type importance weighting** (Session 3d). All 33 Ontario
    specific_expectations count equally in the coverage gate even
    though some are broader and more consequential than others.

## Public API

- ``extract_source_bullets(raw_text: str) -> list[dict]`` — the flat
  extraction. Returns ``[]`` on empty / trivially short input.
- ``classify_bullet_type(text, source_location, detector) -> str`` —
  the semantic classifier. Pure function over bullet fields.
- ``SourceBullet`` dict shape:
  ``{"id": "sb_001", "text": "...", "source_location": "...",
     "detector": "marker_bullet|numbered_outcome|topic_statement",
     "bullet_type": "<one of the enum values above>"}``.
"""

from __future__ import annotations

import re

_MARKER_BULLET_RE = re.compile(
    r"^\s*(?:[•·▪■▫◦○●]|\*|[-–—+])\s+(?P<text>.+?)\s*$"
)

# Header introducing a statutory "Pupils should be taught to:" list.
# The England NC (gov.uk) emits bullet items as plain lines after this
# header — no bullet marker, no trailing period. See adjacent-mechanism
# #12 (doc pending) for the taught_to_item detector rationale.
_TAUGHT_TO_HEADER_RE = re.compile(
    r"pupils\s+should\s+be\s+taught\s+to\s*:", re.IGNORECASE
)

# Major section breaks that end a taught_to block. These are section/stage
# headings, not sub-headers within the list.
_TAUGHT_TO_BLOCK_END_RE = re.compile(
    r"^(?:key\s+stage|lower\s+key\s+stage|upper\s+key\s+stage|"
    r"year\s+\d|years?\s+\d|notes?\s+and\s+guidance|"
    r"statutory\s+requirements|appendix|programme\s+of\s+study)",
    re.IGNORECASE,
)

# Code + lowercase-verb rule. We require the first character of the
# description to be a lowercase letter so that section headers ("A1.
# Application: ...", "Strand A. New France...") do not match — only
# actual learning outcomes that lead with a verb ("A1.1 describe...").
_NUMBERED_OUTCOME_RE = re.compile(
    r"^\s*(?P<code>(?:[A-Z]\d+(?:\.\d+)?|\d+\.|\d+\)|\(\d+\)|[a-z]\)))\s+"
    r"(?P<text>[a-z].+?)\s*$"
)

_MIN_BULLET_CHARS = 10
_MIN_NUMBERED_OUTCOME_TEXT_CHARS = 25
_MAX_TOPIC_BULLET_CHARS = 300
_MAX_HEADER_CHARS = 200

# Session 3d — bullet_type classifier constants.
BULLET_TYPES = (
    "specific_expectation",
    "overall_expectation",
    "sample_question",
    "teacher_prompt",
    "cross_grade",
    "front_matter",
    "other",
    "taught_to_item",
)

# Lowercase header-token substrings that mark a bullet's parent section
# as front-matter. Curated from the Ontario 2018 Social Studies /
# History / Geography PDF — see
# `docs/diagnostics/2026-04-18-ontario-bullet-classification.md`.
# Heuristic; other documents need their own calibration.
_FRONT_MATTER_HEADER_TOKENS = (
    "version history",
    "account. they focus",
    "the following elements",
    "the following components",
    "as follows",
    "follows",
    "one of two distinct programs",
    "the following questions",
    "the achievement chart",
    "the categories of knowledge and skills",
    "options is appropriate",
    "courses and programs",
    "secondary program",
    "equipment, as well as",
    "meet with success",
    "three types of accommodations",
    "learning for all students",
    "particular attention to these beliefs",
    "students will learn skills to",
    "mathematical literacy",
    "students will work towards",
    "citizenship education",
    "the two grades are",
    "the student",
    "students",
    "points within the process",
    "topics covered in the two grades",
    "by the end of grade 1",
    "by the end of grade 2",
    "by the end of grade 3",
    "by the end of grade 4",
    "by the end of grade 5",
    "by the end of grade 6",
    "further information on supporting english language",
    "associations or government",
    "in the classroom, teachers",
    "in addition, teacher-librarians",
    "website",
)

# Below this line number the Ontario PDF is front-matter (preamble,
# program planning, assessment, equity). Above it, grade-specific
# expectations. Calibrated on Session 3c Ontario corpus. See
# adjacent-mechanism #9/#10 for the generalisation caveat.
_FRONT_MATTER_LINE_CUTOFF = 8000

_LINE_LOC_RE = re.compile(
    r"line\s+(?P<line>\d+)(?:\s*\(under:\s*(?P<header>[^)]*)\s*\))?"
)
_GRADE_TAG_IN_TEXT_RE = re.compile(r"\(grade\s+(?P<grade>\d+)", re.IGNORECASE)


def classify_bullet_type(
    text: str,
    source_location: str,
    detector: str,
    *,
    target_grade: str = "",
) -> str:
    """Classify a bullet into the semantic enum.

    See module docstring for heuristics. ``target_grade`` is currently
    only used to distinguish ``cross_grade`` from a same-grade
    sample-question tag; when the caller does not know the target
    grade, pass ``""`` and the default set of cross-grade numbers
    applies.
    """
    t = (text or "").strip()
    if not t:
        return "other"

    lower = t.lower()

    # 1. sample_question — a literal question.
    if t.rstrip().endswith("?"):
        return "sample_question"

    # 2. teacher_prompt — example / prompt leads.
    if lower.startswith(("e.g.", "e.g ", "(e.g.", "for example")):
        return "teacher_prompt"

    # 3. cross-grade signal in text itself (Ontario sample questions
    # cross-referenced to specific grades).
    m_grade = _GRADE_TAG_IN_TEXT_RE.search(lower)
    if m_grade:
        g = m_grade.group("grade")
        if target_grade:
            if g != str(target_grade).strip():
                return "cross_grade"
        else:
            if g in {"1", "2", "3", "4", "5", "6", "8"}:
                return "cross_grade"

    # 4a. taught_to_item detector → specific_expectation (statutory list item).
    if detector == "taught_to_item":
        return "specific_expectation"

    # 4b. numbered_outcome detector → specific_expectation (structural).
    if detector == "numbered_outcome":
        return "specific_expectation"

    # 5. front_matter by header match.
    header = ""
    line_no: int | None = None
    m_loc = _LINE_LOC_RE.match(source_location or "")
    if m_loc:
        line_no = int(m_loc.group("line"))
        header = (m_loc.group("header") or "").strip().lower()
    if header:
        for tok in _FRONT_MATTER_HEADER_TOKENS:
            if tok in header:
                return "front_matter"

    # 6. front_matter by line-position proxy (Ontario-shape).
    if line_no is not None and line_no < _FRONT_MATTER_LINE_CUTOFF:
        return "front_matter"

    return "other"


def extract_source_bullets(
    raw_text: str, *, target_grade: str = ""
) -> list[dict]:
    """Walk `raw_text` line by line and emit bullets per the rules above.

    Returns a flat list of dicts:
    ``{id, text, source_location, detector, bullet_type}``.
    Empty or too-short input returns ``[]``.

    ``target_grade`` (optional) is passed to the bullet_type classifier
    so cross-grade detection can use the run's target grade. When
    omitted, the classifier falls back to a static cross-grade set.
    """
    if not raw_text or len(raw_text.strip()) < 100:
        return []

    bullets: list[dict] = []
    seen_texts: set[str] = set()
    in_block = False
    block_header = ""

    def push(text: str, detector: str, line_no: int, header: str = "") -> None:
        text = text.strip()
        if len(text) < _MIN_BULLET_CHARS:
            return
        # Collapse internal whitespace runs — PDF extraction often leaves
        # ragged whitespace that creates false "unique" duplicates.
        normalised = re.sub(r"\s+", " ", text)
        key = normalised.lower()
        if key in seen_texts:
            return
        seen_texts.add(key)
        if header:
            location = f"line {line_no} (under: {header[:80]})"
        else:
            location = f"line {line_no}"
        btype = classify_bullet_type(
            normalised, location, detector, target_grade=target_grade
        )
        bullets.append(
            {
                "id": f"sb_{len(bullets) + 1:03d}",
                "text": normalised,
                "source_location": location,
                "detector": detector,
                "bullet_type": btype,
            }
        )

    in_taught_to_block = False
    taught_to_header = ""

    for idx, raw_line in enumerate(raw_text.splitlines()):
        line_no = idx + 1
        line = raw_line.strip()
        if not line:
            continue

        m = _MARKER_BULLET_RE.match(raw_line)
        if m:
            push(m.group("text"), "marker_bullet", line_no)
            continue

        m = _NUMBERED_OUTCOME_RE.match(raw_line)
        if m:
            code = m.group("code").strip()
            text = m.group("text").strip()
            # Min text length guards against date-like false positives
            # (e.g. "2023. szeptember 1." in felvételi) — real outcomes
            # carry a verb phrase of meaningful length.
            if len(text) >= _MIN_NUMBERED_OUTCOME_TEXT_CHARS:
                push(f"{code} {text}", "numbered_outcome", line_no)
                continue

        # taught_to_item detector — handles England NC "Pupils should be
        # taught to:" lists where items are plain lines without markers or
        # trailing periods. Entered when a taught-to header is detected;
        # exited on major section breaks (Key Stage, Year N headings, Notes).
        if _TAUGHT_TO_HEADER_RE.search(line):
            in_taught_to_block = True
            taught_to_header = line.rstrip(":").strip()
            in_block = False  # taught_to takes priority over topic_statement
            block_header = ""
            continue

        if in_taught_to_block:
            # Major section heading ends the block.
            if _TAUGHT_TO_BLOCK_END_RE.match(line):
                in_taught_to_block = False
                taught_to_header = ""
            # Sub-headers (short lines ending with ":") update the label
            # but don't end the block — they introduce sub-categories
            # (e.g. "spell:", "name the letters:").
            elif line.endswith(":") and len(line) <= _MAX_HEADER_CHARS:
                taught_to_header = line.rstrip(":").strip()
            # Long prose paragraphs end the block.
            elif len(line) > 400:
                in_taught_to_block = False
                taught_to_header = ""
            elif _MIN_BULLET_CHARS <= len(line) <= _MAX_TOPIC_BULLET_CHARS:
                push(line, "taught_to_item", line_no, header=taught_to_header)
                continue

        # Section header that introduces a topic-statement block.
        if line.endswith(":") and len(line) <= _MAX_HEADER_CHARS and not line.endswith("::"):
            in_block = True
            block_header = line.rstrip(":").strip()
            continue

        if in_block:
            # A topic statement: short-ish line ending with a period.
            if (
                line.endswith(".")
                and _MIN_BULLET_CHARS <= len(line) <= _MAX_TOPIC_BULLET_CHARS
                and not line.endswith("::")
            ):
                push(line, "topic_statement", line_no, header=block_header)
                continue
            # Long paragraphs break the block. Short lines that don't end
            # with a period (continuations, fragments) are skipped but do
            # not break the block.
            if len(line) > 400:
                in_block = False
                block_header = ""

    return bullets


__all__ = ["BULLET_TYPES", "classify_bullet_type", "extract_source_bullets"]
