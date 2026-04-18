"""Source-evidence matcher.

Primitive shared by three VALIDITY gates (source coverage, no-invention,
architecture verifiability). Given a *claim* (a source bullet, a
learning-target statement, or a strand label) and a *corpus* (candidate
strings drawn from the counterpart side), returns a confidence score
per corpus item that the claim and item support each other, plus the
matched passage and a short reason.

## What this matcher does

Hybrid lexical matcher:

- **Lemmatisation**: lowercase → strip punctuation → remove stopwords →
  strip common English suffixes (-ing, -ed, -ies/-es/-s, -ly, -tion,
  -sion, -ment, -ness, -ity). Rule-based, no external dependency.
- **Lemma Jaccard overlap**: intersection-over-union of lemmatised
  token sets between claim and each corpus item.
- **Character n-gram Jaccard**: same idea on 4-character n-grams of the
  cleaned (lowercased, punctuation-stripped) strings. Captures morphology
  and subword overlap that whole-word lemmatisation misses.
- **Final score**: `max(lemma_jaccard, 0.7 * ngram_jaccard)`. The ngram
  signal is discounted because it can over-score on short strings with
  shared function-word bigrams; the lemma signal is the primary channel.

## What this matcher does NOT do — adjacent mechanisms

Every judge carries an adjacent-mechanism declaration. Future readers
should add to this list, not remove from it.

1. **Grain.** The matcher cannot detect that a single coarse LT
   ("I can use number operations") trivially matches many source
   bullets and inflates the coverage number. A high match score is not
   evidence of *appropriate* decomposition, only of lexical contact.
2. **Semantic-vs-lexical injection.** An LT can claim a capability not
   present in the source while still sharing vocabulary with it. If the
   source discusses "prime factorisation" and the LT introduces
   "factorial notation", the token `factor` overlaps even though the
   construct is invented. Lexical match cannot distinguish these.
3. **Domain relevance.** A maths LT matched against a history source
   scores near zero, but the failure mode is "no match" not "wrong
   domain". The matcher cannot tell the user the domains disagree —
   only that the claim has no lexical support.
4. **Language.** This matcher assumes **English**. Its stopword list,
   suffix rules, and tokenisation are English-only. It does not handle
   Hungarian, French, German, Spanish, or any other language. On
   non-English content it will produce low-confidence matches that may
   look like "no coverage" or "invented" when the real issue is
   language-mismatch. The felvételi source is Hungarian and the
   felvételi KUD/LT output is English; the matcher compares
   English-against-English in that pairing, which *happens to work*
   but is an accidental dependency. Any Hungarian-against-Hungarian
   comparison must either translate first or use a different matcher.
5. **Synonyms and paraphrase.** "Persist" and "persevere" are treated
   as unrelated tokens. A source bullet worded in one register and an
   LT worded in another will under-score. Upgrade path: swap in a
   sentence-embedding model.
6. **Word order and syntax.** "The student explains the teacher's
   method" and "The teacher explains the student's method" score
   identically. The matcher is a bag-of-lemmas.
7. **Negation.** "Solve equations" and "does not solve equations"
   score identically. No negation handling.
8. **Polysemy.** "Bank" (river) and "bank" (financial) lemmatise
   identically.
9. **Quantity calibration.** Scores are unitless and not calibrated
   to a human notion of "confident match". Thresholds in gate scripts
   are empirical — tuned against the `eval/test_cases/` known-good and
   known-bad fixtures and documented where used.

## Public API

- `match(claim: str, corpus: list[str], *, top_k: int | None = None,
         threshold: float = 0.0) -> list[Match]`
- `Match` is a frozen dataclass: `{score, matched_item, matched_index,
   reason}`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

# Default confidence threshold, shared by every gate script and the
# matcher fixture tests. Raised from 0.20 → 0.35 in Session 3a
# (2026-04-18) alongside the move to real source bullets. The 0.20
# value was calibrated against strand-level proxy corpora where score
# distributions were narrower; bullet-level matching produces a wider
# distribution so 0.35 is a safer no-invention bar. Moving this
# invalidates prior baselines — re-run the gates on all baseline-corpus
# runs and append a dated entry to docs/project-log/ before changing.
DEFAULT_THRESHOLD: float = 0.35

# ---------------------------------------------------------------------------
# Lemmatisation and tokenisation (English-only, rule-based).
# ---------------------------------------------------------------------------

_STOPWORDS: frozenset[str] = frozenset(
    """
    a an and are as at be been being but by can could did do does done
    during each either else few for from had has have having he her here
    hers him his how i if in into is it its itself just let me might more
    most must my myself no nor not now of off on once only or other ought
    our ours out over own same she should so some such than that the their
    theirs them themselves then there these they this those through to too
    under until up upon us very was we were what when where which while who
    whom why will with within without would you your yours yourself
    """.split()
)

# Ordered: longest suffix first so '-tion' beats '-on'.
_SUFFIXES: tuple[tuple[str, str], ...] = (
    ("ational", "ate"),
    ("tional", "tion"),
    ("iveness", "ive"),
    ("fulness", "ful"),
    ("ousness", "ous"),
    ("biliti", "ble"),
    ("alize", "al"),
    ("aliti", "al"),
    ("iciti", "ic"),
    ("ical", "ic"),
    ("ness", ""),
    ("ment", ""),
    ("tion", ""),
    ("sion", ""),
    ("able", ""),
    ("ible", ""),
    ("ance", ""),
    ("ence", ""),
    ("ship", ""),
    ("ful", ""),
    ("less", ""),
    ("ive", ""),
    ("ous", ""),
    ("ize", ""),
    ("ise", ""),
    ("ies", "y"),
    ("ied", "y"),
    ("ing", ""),
    ("ed", ""),
    ("es", ""),
    ("ly", ""),
    ("er", ""),
    ("or", ""),
    ("s", ""),
)

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")


def _strip_suffix(tok: str) -> str:
    # Don't lemmatise very short tokens — too destructive.
    if len(tok) <= 3:
        return tok
    for suf, repl in _SUFFIXES:
        if tok.endswith(suf) and len(tok) - len(suf) >= 3:
            return tok[: -len(suf)] + repl
    return tok


def lemmatise(text: str) -> list[str]:
    """Lowercase → token-extract → drop stopwords → strip suffixes.

    Rule-based and English-only. See module docstring, adjacent-mechanism
    declaration #4.
    """
    toks = [m.group(0).lower() for m in _TOKEN_RE.finditer(text)]
    out: list[str] = []
    for tok in toks:
        if tok in _STOPWORDS:
            continue
        # Strip internal apostrophes ("teacher's" → "teachers" → "teacher").
        tok = tok.replace("'", "")
        if not tok or tok in _STOPWORDS:
            continue
        out.append(_strip_suffix(tok))
    return [t for t in out if t]


# ---------------------------------------------------------------------------
# Similarity primitives.
# ---------------------------------------------------------------------------

def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _char_ngrams(text: str, n: int = 4) -> set[str]:
    cleaned = re.sub(r"[^a-z0-9 ]", " ", text.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) < n:
        return set()
    return {cleaned[i : i + n] for i in range(len(cleaned) - n + 1)}


def _score(claim: str, item: str) -> tuple[float, set[str]]:
    """Return (score, shared_lemmas) for a single claim/item pair."""
    claim_lemmas = set(lemmatise(claim))
    item_lemmas = set(lemmatise(item))
    lemma_j = _jaccard(claim_lemmas, item_lemmas)

    claim_ngrams = _char_ngrams(claim)
    item_ngrams = _char_ngrams(item)
    ngram_j = _jaccard(claim_ngrams, item_ngrams)

    score = max(lemma_j, 0.7 * ngram_j)
    shared = claim_lemmas & item_lemmas
    return score, shared


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Match:
    """One candidate match of a claim against a corpus item.

    - `score`: unitless similarity in [0, 1]. See module docstring for
      what this score does and does not measure (adjacent mechanism #9).
    - `matched_item`: the corpus string that scored.
    - `matched_index`: its index in the corpus list.
    - `reason`: short human-readable blurb — shared lemmas, else a
      signal that only character-overlap contributed.
    """

    score: float
    matched_item: str
    matched_index: int
    reason: str


def match(
    claim: str,
    corpus: Iterable[str],
    *,
    top_k: int | None = None,
    threshold: float = 0.0,
) -> list[Match]:
    """Score `claim` against every item in `corpus`.

    Returns matches sorted by descending score, filtered to those at or
    above `threshold`, truncated to `top_k` if set.

    Callers that only want the best match: `match(...)[:1]` after a
    threshold, or use `best_match()`.
    """
    corpus_list = list(corpus)
    scored: list[Match] = []
    for i, item in enumerate(corpus_list):
        s, shared = _score(claim, item)
        if s < threshold:
            continue
        if shared:
            reason = f"shared lemmas: {', '.join(sorted(shared))}"
        elif s > 0:
            reason = "character-ngram overlap only (no shared content lemmas)"
        else:
            reason = "no overlap"
        scored.append(
            Match(
                score=round(s, 4),
                matched_item=item,
                matched_index=i,
                reason=reason,
            )
        )
    scored.sort(key=lambda m: m.score, reverse=True)
    if top_k is not None:
        scored = scored[:top_k]
    return scored


def best_match(claim: str, corpus: Iterable[str]) -> Match | None:
    """Single highest-scoring match, or None if corpus is empty."""
    results = match(claim, corpus, top_k=1)
    return results[0] if results else None


EN_STOPWORDS = _STOPWORDS
EN_TOKEN_RE = _TOKEN_RE


__all__ = [
    "Match",
    "match",
    "best_match",
    "lemmatise",
    "DEFAULT_THRESHOLD",
    "EN_STOPWORDS",
    "EN_TOKEN_RE",
]
