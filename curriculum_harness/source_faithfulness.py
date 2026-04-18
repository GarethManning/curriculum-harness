"""Shared source-faithfulness primitives for Phase 3 and Phase 4.

Phases 3 and 4 each check their emitted items against the Phase 1
`source_bullets` artefact before emission. This module gives them the
shared helper so both phases compute provenance and the same
`SOURCE_FAITHFULNESS_FAIL` flag against the same threshold.

## What this module does

- `compute_source_provenance(text, source_bullets)` → runs the
  source-evidence matcher against the bullet corpus, returns the
  top-k matches as a provenance list `[{bullet_id, score,
  matched_text, bullet_type}]` plus a pass/fail boolean for the
  configured threshold. ``bullet_type`` here is the Session-3d
  semantic category (``specific_expectation``, ``sample_question``,
  …) rather than the extractor name (which now lives on ``detector``
  on the source-bullet dict).
- `compute_parent_provenance(text, parent_texts, parent_ids)` → same
  shape but over an arbitrary parent corpus (used by Phase 4 to trace
  an LT back to its KUD item before the bullet check).
- `SOURCE_FAITHFULNESS_FAIL_FLAG` — the flag string both phases
  append when the best score is below threshold.

## Adjacent mechanisms not checked

Every judge carries an adjacent-mechanism declaration. Future readers
should add to this list, not remove from it.

1. **Grain appropriateness.** A coarse KUD item ("understand number
   systems") can match many source bullets trivially. High score is
   not evidence of appropriate decomposition.
2. **Semantic injection with overlapping vocabulary.** An invented
   item that reuses source vocabulary can clear the threshold without
   being faithful. "Factorial" → "factor" lemma overlap already
   demonstrated this failure mode once; the factorial LT only fails
   because the felvételi source contains no `factor*` vocabulary at
   all. A subtler invention using lexically-present terms can evade.
3. **Domain relevance when score is near zero.** Below-threshold is
   reported as "failed faithfulness" regardless of whether the item
   is genuinely invented, out-of-domain, or simply wrongly-worded.
   The gate does not disambiguate.
4. **Language boundary.** The underlying matcher is English-only
   (`eval/source_evidence_matcher.py` adjacent-mechanism #4). For
   non-English source bullets, every item will be flagged regardless
   of faithfulness. Felvételi is the canonical case. The flag is
   still recorded — Session 3b/3c will decide how to handle this
   (translate bullets, multilingual matcher, or profile-conditional
   skip of the faithfulness check).
5. **Empty bullet corpus.** When `source_bullets` is empty or absent
   (pre-Session-3a runs, or runs where Phase 1 extracted no bullets),
   the helper returns `passed=True` and empty provenance, so items
   are not falsely flagged on missing-data. Operators must notice the
   empty corpus as a separate signal (run report's source-bullet
   count).
6. **No regeneration.** This module only flags. Regeneration on flag
   is Session 3b's scope — flagged items ship with the flag.
7. **No multi-bullet corroboration.** Best-score pass is sufficient.
   There is no requirement that an item trace to multiple converging
   bullets to be considered faithful.
"""

from __future__ import annotations

from typing import Iterable

from eval.source_evidence_matcher import DEFAULT_THRESHOLD, match

SOURCE_FAITHFULNESS_FAIL_FLAG = "SOURCE_FAITHFULNESS_FAIL"


def compute_source_provenance(
    text: str,
    source_bullets: list[dict],
    *,
    top_k: int = 3,
    threshold: float = DEFAULT_THRESHOLD,
) -> tuple[list[dict], bool]:
    """Match ``text`` against the source_bullets corpus.

    Returns a (provenance, passed) tuple.

    `provenance` — up to ``top_k`` top matches as dicts with
    ``{bullet_id, score, matched_text, bullet_type}``. Empty list when
    the corpus is empty or the matcher produces no non-zero overlap.

    `passed` — True when the best-match score is at or above
    ``threshold``. For empty / missing corpus returns True (see
    adjacent-mechanism #5 above) so Phase 3/4 don't flood flags on
    pre-Session-3a runs.
    """
    text = (text or "").strip()
    if not text or not source_bullets:
        return [], True
    corpus_texts = [str(b.get("text") or "") for b in source_bullets]
    matches = match(text, corpus_texts, top_k=top_k)
    entries: list[dict] = []
    for m in matches:
        bullet = source_bullets[m.matched_index]
        entries.append(
            {
                "bullet_id": str(bullet.get("id") or ""),
                "score": m.score,
                "matched_text": m.matched_item,
                "bullet_type": str(bullet.get("bullet_type") or ""),
            }
        )
    best_score = matches[0].score if matches else 0.0
    return entries, best_score >= threshold


def compute_parent_provenance(
    text: str,
    parents: Iterable[dict],
    *,
    top_k: int = 1,
    threshold: float = DEFAULT_THRESHOLD,
) -> tuple[list[dict], bool]:
    """Match ``text`` against arbitrary parent items (each with a
    ``content`` or ``statement`` field + an ``id``-like key).

    Used by Phase 4 to record which KUD item an LT derives from. The
    parent list is expected to be the KUD items the LT iterates over.

    Returns the same (provenance, passed) shape as
    `compute_source_provenance`. When parents are absent, returns
    ``([], True)``.
    """
    text = (text or "").strip()
    parent_list = list(parents)
    if not text or not parent_list:
        return [], True
    # Accept either "content" (KUD shape) or "statement" (LT shape).
    corpus_texts = [
        str(p.get("content") or p.get("statement") or "") for p in parent_list
    ]
    matches = match(text, corpus_texts, top_k=top_k)
    entries: list[dict] = []
    for m in matches:
        parent = parent_list[m.matched_index]
        entries.append(
            {
                "parent_id": str(parent.get("id") or m.matched_index),
                "score": m.score,
                "matched_text": m.matched_item,
            }
        )
    best_score = matches[0].score if matches else 0.0
    return entries, best_score >= threshold


__all__ = [
    "SOURCE_FAITHFULNESS_FAIL_FLAG",
    "compute_source_provenance",
    "compute_parent_provenance",
]
