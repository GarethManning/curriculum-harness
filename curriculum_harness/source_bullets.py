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

Every bullet gets a stable `sb_NNN` ID, the detector it came from
(`bullet_type`), a human-readable `source_location` (line number plus
the introducing header text where applicable), and the bullet text.

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

## Public API

- `extract_source_bullets(raw_text: str) -> list[dict]` — the flat
  extraction. Returns `[]` on empty / trivially short input.
- `SourceBullet` dict shape:
  ``{"id": "sb_001", "text": "...", "source_location": "...",
     "bullet_type": "marker_bullet|numbered_outcome|topic_statement"}``.
"""

from __future__ import annotations

import re

_MARKER_BULLET_RE = re.compile(
    r"^\s*(?:[•·▪■▫◦○●]|\*|[-–—+])\s+(?P<text>.+?)\s*$"
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


def extract_source_bullets(raw_text: str) -> list[dict]:
    """Walk `raw_text` line by line and emit bullets per the rules above.

    Returns a flat list of dicts: `{id, text, source_location, bullet_type}`.
    Empty or too-short input returns `[]`.
    """
    if not raw_text or len(raw_text.strip()) < 100:
        return []

    bullets: list[dict] = []
    seen_texts: set[str] = set()
    in_block = False
    block_header = ""
    block_header_line = 0

    def push(text: str, bullet_type: str, line_no: int, header: str = "") -> None:
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
        bullets.append(
            {
                "id": f"sb_{len(bullets) + 1:03d}",
                "text": normalised,
                "source_location": location,
                "bullet_type": bullet_type,
            }
        )

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

        # Section header that introduces a topic-statement block.
        if line.endswith(":") and len(line) <= _MAX_HEADER_CHARS and not line.endswith("::"):
            in_block = True
            block_header = line.rstrip(":").strip()
            block_header_line = line_no
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


__all__ = ["extract_source_bullets"]
