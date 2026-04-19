"""Type 1/2 criterion-rubric quality gates.

Structural gates (word-limit, five-level-present, schema correctness)
are enforced inline by the criterion generator's validator — any run
that violates them is dropped and cannot contribute to the 3x self-
consistency vote. This module applies the RICHER semantic gates to
rubrics that have already passed structural validation and won the
self-consistency majority:

1. word_limit                 — each level within its hard limit (defensive; validator already enforced)
2. observable_verb            — each descriptor contains at least one observable action verb
3. single_construct           — every level references the SAME capability (shared lemma-set)
4. no_inline_examples         — no "such as" / "for example" / "e.g." / parentheses
5. competent_framing_regex    — no deficit hedge-phrases in the Competent descriptor
6. competent_framing_judge    — LLM-as-judge verdict (set on the rubric by the generator)
7. level_progression          — no level borrows hedge-phrasing from the next/previous level
8. propositional_thin_flag    — informational; raised for Type 1 Understand-propositional
                                LTs whose rubric uses only one verb bucket across all five
                                levels (structurally valid but thin differentiation)

Halting gates (1, 2, 3, 4, 5, 6, 7) halt the rubric — the rubric is
emitted with ``quality_gate_passed=False`` and named failures, but it
is NOT deleted from the collection. Gate (8) is informational.

Notes on Competent framing:

- The regex gate is the first pass: deterministic, fails on deficit
  substrings that should never appear in a Competent descriptor.
- The judge gate is the LLM-as-judge verdict already stored on the
  rubric by the generator (``competent_framing_flag``). This gate just
  promotes that verdict into the quality report. A "fail" verdict is
  halting; an "error" verdict is informational (retry needed).
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from curriculum_harness.reference_authoring.types import (
    GateResult,
    QualityReport,
    RUBRIC_LEVEL_ORDER,
    RUBRIC_LEVEL_WORD_LIMITS,
    Rubric,
    RubricCollection,
)

# Shared with the band-statement gate — one source of truth for
# what counts as an observable action verb in a Type 1/2 descriptor.
OBSERVABLE_VERBS = {
    # Kept in sync with generate_criteria._VERB_BUCKETS keys. The two
    # lists MUST agree — if the generator accepts a verb as bucketable
    # but the gate rejects it as non-observable, rubrics halt on the
    # gate rather than on real content issues.
    #
    # Core Bloom's taxonomy verbs (original set):
    "identify", "describe", "compare", "explain", "justify", "analyse", "analyze",
    "evaluate", "create", "apply", "interpret", "construct", "communicate",
    "recognise", "recognize", "use", "select", "choose", "perform", "demonstrate",
    "distinguish", "relate", "represent", "solve", "calculate", "compute",
    "recall", "name", "contrast", "critique",
    #
    # Transfer and integration verbs — dominate the Extending level in
    # horizontal and dispositional domains. All clearly measurable.
    # Added in 4c-2b after 17 false-positive observable_verb failures on
    # Secondary RSHE 2025 and 3 on AP US Gov (Sonnet run, 2026-04-19).
    "transfer", "connect", "guide", "model", "advise", "notice", "assess",
    "adapt", "integrate", "signpost", "state", "help", "articulate",
    "anticipate", "provide", "synthesize", "synthesise", "facilitate", "mentor",
}

BANNED_SUBSTRINGS = (
    " such as ",
    "(",
    ")",
    " e.g.",
    " for example",
    " for instance",
)

# Hedge phrases that, if present in Competent, flip it to "acceptable-
# but-deficient". Whole-word matches only — "limited" is fine in a
# content-level phrase like "limited fraction context"; we match the
# hedge constructions.
COMPETENT_DEFICIT_PATTERNS = (
    r"\bbut\b.*\b(struggles?|fails?|misses?|omits?|lacks?)\b",
    r"\bwith limited\b",
    r"\bwith some\b .*\b(gap|error|confusion|help)\b",
    r"\bnot yet\b",
    r"\bnot always\b",
    r"\bnot consistently\b",
    r"\bstill needs?\b",
    r"\bapproaching\b",
    r"\bstruggles? to\b",
    r"\bemerging\b",
    r"\bdeveloping\b",  # borrowing from the Developing level name
    r"\bhowever\b",
    r"\balthough\b",
)

# Lemma tokens reserved for "topic" words (domain nouns) — if level
# descriptors share <3 of these we flag single_construct violation.
_TOPIC_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]{3,}")

_STOPWORDS = {
    "with", "the", "and", "for", "into", "from", "this", "that", "some", "them",
    "they", "their", "there", "have", "which", "when", "what", "will", "shall",
    "each", "been", "being", "such", "more", "most", "less", "than", "then",
    "very", "also", "same", "still", "over", "across", "within", "while",
    "under", "above", "below", "upon", "onto", "through", "during", "between",
    "other", "another", "both", "neither", "either", "every", "never", "ever",
    "student", "students", "learner", "learners", "child", "children",
    "context", "contexts", "support", "prompt", "prompts", "prompting",
    "independently", "correctly", "accurately", "precisely", "without",
    "identify", "identifies", "describe", "describes", "explain", "explains",
    "compare", "compares", "analyse", "analyses", "analyze", "analyzes",
    "evaluate", "evaluates", "apply", "applies", "use", "uses", "select",
    "selects", "choose", "chooses", "perform", "performs", "demonstrate",
    "demonstrates", "recognise", "recognises", "recognize", "recognizes",
    "solve", "solves", "calculate", "calculates", "interpret", "interprets",
    "justify", "justifies", "construct", "constructs", "communicate",
    "communicates", "distinguish", "distinguishes", "relate", "relates",
    "represent", "represents", "create", "creates",
    "recall", "recalls", "recalled", "recalling",
    "name", "names", "named", "naming",
    "contrast", "contrasts", "contrasted", "contrasting",
    "critique", "critiques", "critiqued", "critiquing",
}


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z']+", text))


def _topic_lemmas(text: str) -> set[str]:
    return {
        m.group(0).lower()
        for m in _TOPIC_WORD_RE.finditer(text)
        if m.group(0).lower() not in _STOPWORDS
    }


_INFLECTION_SUFFIXES = ("ies", "ing", "ed", "es", "s", "d")


def _lemmatise(word: str) -> set[str]:
    """Return a small set of candidate lemmas for ``word``."""
    w = word.lower()
    candidates = {w}
    for suf in _INFLECTION_SUFFIXES:
        if len(w) > len(suf) + 2 and w.endswith(suf):
            stem = w[: -len(suf)]
            candidates.add(stem)
            if suf == "ies":
                candidates.add(stem + "y")
            if suf in ("ed", "ing"):
                candidates.add(stem + "e")
    return candidates


def _has_observable_verb(text: str) -> bool:
    for m in re.finditer(r"[A-Za-z']+", text):
        if _lemmatise(m.group(0)) & OBSERVABLE_VERBS:
            return True
    return False


def _gate_word_limit(rubric: Rubric) -> GateResult:
    offenders: list[dict[str, int | str]] = []
    for lvl in rubric.levels:
        limit = RUBRIC_LEVEL_WORD_LIMITS[lvl.name]
        wc = _word_count(lvl.descriptor)
        if wc == 0 or wc > limit:
            offenders.append({"level": lvl.name, "word_count": wc, "limit": limit})
    passed = not offenders
    return GateResult(
        name=f"word_limit:{rubric.lt_id}",
        passed=passed,
        halting=not passed,
        diagnostic=(
            "all five levels within their respective word limits"
            if passed
            else f"{len(offenders)} level(s) outside word limits: {offenders}"
        ),
        details={"lt_id": rubric.lt_id, "offenders": offenders},
    )


def _gate_observable_verb(rubric: Rubric) -> GateResult:
    missing = [
        lvl.name
        for lvl in rubric.levels
        if lvl.name != "no_evidence" and not _has_observable_verb(lvl.descriptor)
    ]
    # no_evidence legitimately has no action — exempt.
    passed = not missing
    return GateResult(
        name=f"observable_verb:{rubric.lt_id}",
        passed=passed,
        halting=not passed,
        diagnostic=(
            "every level (except no_evidence) contains an observable action verb"
            if passed
            else f"levels without observable action verb: {missing}"
        ),
        details={"lt_id": rubric.lt_id, "levels_missing_verb": missing},
    )


def _gate_single_construct(rubric: Rubric) -> GateResult:
    """Require topic-lemma overlap between consecutive applied levels.

    no_evidence is excluded (too terse to anchor). We then compare
    emerging/developing/competent/extending pairwise — each adjacent
    pair should share ≥1 topic lemma. Not sharing any topic lemma is
    strong evidence of a construct shift across levels.
    """
    applied = [lvl for lvl in rubric.levels if lvl.name != "no_evidence"]
    pairs_without_overlap: list[tuple[str, str]] = []
    for a, b in zip(applied, applied[1:]):
        if not (_topic_lemmas(a.descriptor) & _topic_lemmas(b.descriptor)):
            pairs_without_overlap.append((a.name, b.name))
    passed = not pairs_without_overlap
    return GateResult(
        name=f"single_construct:{rubric.lt_id}",
        passed=passed,
        halting=not passed,
        diagnostic=(
            "adjacent applied levels share topic-lemma overlap — single construct preserved"
            if passed
            else f"adjacent level pairs with no topic-lemma overlap: {pairs_without_overlap}"
        ),
        details={
            "lt_id": rubric.lt_id,
            "pairs_without_overlap": pairs_without_overlap,
        },
    )


def _gate_no_inline_examples(rubric: Rubric) -> GateResult:
    offenders: list[dict[str, str]] = []
    for lvl in rubric.levels:
        lower = lvl.descriptor.lower()
        for banned in BANNED_SUBSTRINGS:
            if banned in lower:
                offenders.append({"level": lvl.name, "substring": banned.strip()})
    passed = not offenders
    return GateResult(
        name=f"no_inline_examples:{rubric.lt_id}",
        passed=passed,
        halting=not passed,
        diagnostic=(
            "no inline examples or banned substrings in any descriptor"
            if passed
            else f"banned substrings present: {offenders}"
        ),
        details={"lt_id": rubric.lt_id, "offenders": offenders},
    )


def _gate_competent_framing_regex(rubric: Rubric) -> GateResult:
    comp = next((lvl for lvl in rubric.levels if lvl.name == "competent"), None)
    if comp is None:
        return GateResult(
            name=f"competent_framing_regex:{rubric.lt_id}",
            passed=False,
            halting=True,
            diagnostic="no competent level found",
            details={"lt_id": rubric.lt_id},
        )
    lower = comp.descriptor.lower()
    hits = [p for p in COMPETENT_DEFICIT_PATTERNS if re.search(p, lower)]
    passed = not hits
    return GateResult(
        name=f"competent_framing_regex:{rubric.lt_id}",
        passed=passed,
        halting=not passed,
        diagnostic=(
            "Competent descriptor contains no deficit hedge-phrases"
            if passed
            else f"Competent descriptor uses deficit hedge-phrasing: {hits}"
        ),
        details={"lt_id": rubric.lt_id, "patterns_matched": hits},
    )


def _gate_competent_framing_judge(rubric: Rubric) -> GateResult:
    verdict = (rubric.competent_framing_flag or "").lower()
    rationale = rubric.competent_framing_judge_rationale or ""
    if verdict == "pass":
        return GateResult(
            name=f"competent_framing_judge:{rubric.lt_id}",
            passed=True,
            halting=False,
            diagnostic=f"LLM-as-judge verdict: pass — {rationale}",
            details={"lt_id": rubric.lt_id, "verdict": verdict, "rationale": rationale},
        )
    if verdict == "fail":
        return GateResult(
            name=f"competent_framing_judge:{rubric.lt_id}",
            passed=False,
            halting=True,
            diagnostic=f"LLM-as-judge verdict: fail — {rationale}",
            details={"lt_id": rubric.lt_id, "verdict": verdict, "rationale": rationale},
        )
    # "error" or unknown — informational, not halting.
    return GateResult(
        name=f"competent_framing_judge:{rubric.lt_id}",
        passed=True,
        halting=False,
        diagnostic=f"LLM-as-judge verdict unavailable ({verdict or 'missing'}) — retry recommended",
        details={"lt_id": rubric.lt_id, "verdict": verdict, "rationale": rationale},
    )


def _gate_level_progression(rubric: Rubric) -> GateResult:
    """No level borrows hedge-phrasing that belongs to an adjacent level.

    A Developing descriptor that reads like Competent (no gap, full
    independence, etc.) flattens the progression; a Competent
    descriptor that reads like Developing breaks Competent-is-success.
    We check a light heuristic: Competent must NOT contain the
    developing-level hedge marker "but" clauses, and Developing must
    contain at least one hedge/qualifier token (because by definition
    it stops short).
    """
    levels = {lvl.name: lvl.descriptor.lower() for lvl in rubric.levels}
    failures: list[str] = []

    comp = levels.get("competent", "")
    if re.search(r"\bbut\b", comp) and re.search(
        r"\b(gap|omit|miss|inconsistent|partial)\w*\b", comp
    ):
        failures.append("competent_contains_developing_hedge")

    dev = levels.get("developing", "")
    dev_hedge_markers = (
        r"\bbut\b", r"\binconsistent\w*\b", r"\bpartial\w*\b",
        r"\bsome\b", r"\bomit\w*\b", r"\bprompt\w*\b", r"\bgap\w*\b",
        r"\bfamiliar\b", r"\bstops? short\b", r"\bwith support\b",
        r"\bwith guidance\b", r"\bunprompted\b",
    )
    if not any(re.search(p, dev) for p in dev_hedge_markers):
        failures.append("developing_missing_hedge_or_gap_marker")

    passed = not failures
    return GateResult(
        name=f"level_progression:{rubric.lt_id}",
        passed=passed,
        halting=not passed,
        diagnostic=(
            "adjacent levels preserve progression roles"
            if passed
            else f"level-progression violations: {failures}"
        ),
        details={"lt_id": rubric.lt_id, "failures": failures},
    )


def _verb_bucket(text: str) -> str | None:
    """Compact verb-bucket probe for the thin-flag check."""
    groups = {
        "recognise": {"identify", "recognise", "recognize", "recall", "name"},
        "describe": {"describe", "explain", "communicate", "represent", "state"},
        "analyse": {"compare", "analyse", "analyze", "distinguish", "relate", "interpret", "contrast"},
        "evaluate": {"evaluate", "justify", "critique"},
        "apply": {
            "apply", "use", "solve", "calculate", "compute", "construct",
            "perform", "demonstrate", "create", "select", "choose",
        },
    }
    tokens: set[str] = set()
    for m in re.finditer(r"[A-Za-z']+", text):
        tokens |= _lemmatise(m.group(0))
    for bucket, verbs in groups.items():
        if tokens & verbs:
            return bucket
    return None


def _gate_propositional_thin_flag(rubric: Rubric) -> GateResult:
    """Informational: Type 1 Understand LTs that stay in one verb bucket.

    A rubric whose applied levels all share a single verb bucket may
    still be structurally valid — but it suggests the differentiation
    is thin (only one kind of cognitive operation being scaled by
    independence/scope/precision). This is common and legitimate for
    propositional Type 1 LTs, but worth flagging so a reviewer can
    confirm the rubric genuinely distinguishes the levels.
    """
    if rubric.knowledge_type != "Type 1":
        return GateResult(
            name=f"propositional_thin_flag:{rubric.lt_id}",
            passed=True,
            halting=False,
            diagnostic="propositional-thin check skipped (not Type 1)",
            details={"lt_id": rubric.lt_id, "flagged": False},
        )
    applied = [lvl for lvl in rubric.levels if lvl.name != "no_evidence"]
    buckets = Counter(
        b for b in (_verb_bucket(lvl.descriptor) for lvl in applied) if b is not None
    )
    flagged = len(buckets) == 1 and sum(buckets.values()) == len(applied)
    return GateResult(
        name=f"propositional_thin_flag:{rubric.lt_id}",
        passed=True,
        halting=False,
        diagnostic=(
            "propositional_lt_rubric_thin: all four applied levels share one verb bucket; "
            "structurally valid but differentiation may be thin (reviewer-confirm)"
            if flagged
            else "verb-bucket diversity across applied levels — no thin flag"
        ),
        details={
            "lt_id": rubric.lt_id,
            "flagged": flagged,
            "buckets": dict(buckets),
        },
    )


def _run_rubric_gates(rubric: Rubric) -> tuple[list[GateResult], bool, list[str]]:
    gates = [
        _gate_word_limit(rubric),
        _gate_observable_verb(rubric),
        _gate_single_construct(rubric),
        _gate_no_inline_examples(rubric),
        _gate_competent_framing_regex(rubric),
        _gate_competent_framing_judge(rubric),
        _gate_level_progression(rubric),
        _gate_propositional_thin_flag(rubric),
    ]
    halting_failures = [g for g in gates if g.halting and not g.passed]
    failures = [g.name.split(":", 1)[0] for g in halting_failures]
    passed = not halting_failures
    return gates, passed, failures


def run_criterion_gates(
    collection: RubricCollection,
) -> tuple[QualityReport, RubricCollection]:
    """Run the full criterion gate suite across every rubric in ``collection``.

    Returns (report, updated_collection). Each rubric in the updated
    collection has ``quality_gate_passed`` and ``quality_gate_failures``
    set, and ``propositional_lt_rubric_thin_flag`` set per the
    informational gate.

    Rubrics that already carry ``"rubric_generation_failed"`` in their
    ``quality_gate_failures`` list are generation-halt placeholders — no
    semantic gates are meaningful on empty descriptors, so they are
    counted but skipped.
    """
    all_gates: list[GateResult] = []
    halted_any = False
    propositional_thin_count = 0
    competent_judge_fail_count = 0
    stability_counter: Counter[str] = Counter()

    for rubric in collection.rubrics:
        # Skip semantic gates for generation-halt placeholders.
        if "rubric_generation_failed" in (rubric.quality_gate_failures or []):
            stability_counter[rubric.stability_flag] += 1
            halted_any = True
            continue
        gates, passed, failures = _run_rubric_gates(rubric)
        all_gates.extend(gates)
        rubric.quality_gate_passed = passed
        rubric.quality_gate_failures = failures
        stability_counter[rubric.stability_flag] += 1

        thin_gate = next(
            (g for g in gates if g.name.startswith("propositional_thin_flag:")), None
        )
        if thin_gate and thin_gate.details.get("flagged"):
            rubric.propositional_lt_rubric_thin_flag = True
            propositional_thin_count += 1

        judge_gate = next(
            (g for g in gates if g.name.startswith("competent_framing_judge:")), None
        )
        if judge_gate and not judge_gate.passed:
            competent_judge_fail_count += 1

        if not passed:
            halted_any = True

    summary = {
        "rubrics_total": len(collection.rubrics),
        "rubrics_halted_lts": len(collection.halted_lts),
        "rubrics_with_gate_failures": sum(
            1 for r in collection.rubrics if not r.quality_gate_passed
        ),
        "rubrics_competent_judge_fail": competent_judge_fail_count,
        "rubrics_propositional_thin_flag": propositional_thin_count,
        "stability_distribution": dict(stability_counter),
    }
    report = QualityReport(
        source_slug=collection.source_slug,
        gate_results=all_gates,
        halted_by=("criterion_gates" if halted_any else None),
        summary=summary,
    )
    return report, collection


def criterion_report_to_markdown(report: QualityReport) -> str:
    """Render a criterion QualityReport as a human-readable markdown document."""
    lines: list[str] = []
    lines.append(f"# Criterion quality report — {report.source_slug}")
    lines.append("")
    status = "HALTED" if report.halted_by else "PASSED"
    lines.append(f"**Overall:** {status}")
    if report.halted_by:
        lines.append(f"**Halted by:** `{report.halted_by}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for k, v in report.summary.items():
        if isinstance(v, dict):
            pretty = ", ".join(f"{kk}={vv}" for kk, vv in sorted(v.items()))
            lines.append(f"- **{k}:** {pretty or '(empty)'}")
        else:
            lines.append(f"- **{k}:** {v}")
    lines.append("")
    # Group gates by LT id for readability.
    by_lt: dict[str, list[GateResult]] = {}
    for g in report.gate_results:
        # Gate names are "<gate>:<lt_id>".
        lt_id = g.name.split(":", 1)[1] if ":" in g.name else "(unknown)"
        by_lt.setdefault(lt_id, []).append(g)
    lines.append("## Per-LT gate results")
    lines.append("")
    for lt_id in sorted(by_lt):
        lines.append(f"### `{lt_id}`")
        lines.append("")
        for g in by_lt[lt_id]:
            verdict = "PASS" if g.passed else ("FAIL (halts)" if g.halting else "FLAG")
            gate_name = g.name.split(":", 1)[0]
            lines.append(f"- **{gate_name}** — {verdict}: {g.diagnostic}")
        lines.append("")
    return "\n".join(lines) + "\n"
