"""Reference-authoring pipeline entry point.

Sequences (full): inventory → KUD classifier → KUD gates → competency
clustering → LT generator → Type 1/2 band statements + Type 3
observation indicators → Type 1/2 criterion rubrics + criterion gates
→ supporting components → extended quality report → output.

Supports ``--resume-from-kud``: skip inventory + KUD classification
and read the existing ``inventory.json`` and ``kud.json`` from
``--out``. This is the 4b-2 default path for Welsh CfW (KUD was
produced in 4b-1 and accepted post-review). Supports ``--skip-criteria``
to stop before the Type 1/2 rubric + supporting-components stages.

Writes the following artefacts to the output directory:

- ``inventory.json`` (unless resuming): full ``SourceInventory``.
- ``kud.json`` (unless resuming): full ``ReferenceKUD``.
- ``quality_report.md`` / ``quality_report.json``: extended gate and
  stage results.
- ``competency_clusters.json``: competency cluster set.
- ``lts.json``: LT set.
- ``band_statements.json``: Type 1/2 band progressions.
- ``observation_indicators.json``: Type 3 observation indicator sets.
- ``criteria.json``: Type 1/2 five-level rubrics (gate-annotated).
- ``criteria_quality_report.md`` / ``criteria_quality_report.json``:
  per-LT criterion gate results.
- ``supporting_components.json``: co-construction plan, student
  rubric, and feedback guide for every rubric that passed its gates.

If any halting gate fails OR any generation stage produces zero output
where output is required (e.g. no LTs), the pipeline exits with a
non-zero status and the partial artefacts are preserved for diagnosis.
No retry loop, no cleanup pass, no paper-overs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from dotenv import load_dotenv

from curriculum_harness._anthropic import LEDGER as _TOKEN_LEDGER
from curriculum_harness.reference_authoring.criterion.generate_criteria import (
    generate_criteria_sync,
)
from curriculum_harness.reference_authoring.criterion.generate_supporting_components import (
    generate_supporting_components_sync,
)
from curriculum_harness.reference_authoring.gates.criterion_gates import (
    criterion_report_to_markdown,
    run_criterion_gates,
)
from curriculum_harness.reference_authoring.gates.kud_gates import (
    quality_report_to_markdown,
    run_kud_gates,
)
from curriculum_harness.reference_authoring.inventory import (
    build_inventory_from_snapshot,
)
from curriculum_harness.reference_authoring.kud.classify_kud import (
    classify_inventory_sync,
    DEFAULT_MODEL,
    DEFAULT_RUNS,
    DEFAULT_TEMPERATURE,
)
from curriculum_harness.reference_authoring.lt.cluster_competencies import (
    cluster_competencies_sync,
)
from curriculum_harness.reference_authoring.lt.generate_lts import (
    generate_lts_sync,
)
from curriculum_harness.reference_authoring.lt.generate_band_statements import (
    generate_band_statements_sync,
)
from curriculum_harness.reference_authoring.lt.generate_observation_indicators import (
    generate_observation_indicators_sync,
)
from curriculum_harness.reference_authoring.progression import (
    ProgressionDetectionError,
    detect_progression,
)
from curriculum_harness.reference_authoring.strand.detect_strands import (
    StrandDetectionUncertain,
    detect_strands,
)
from curriculum_harness.reference_authoring.strand.orchestrate import (
    _strand_slug,
    run_multi_strand_pipeline,
)
from curriculum_harness.reference_authoring.strand.stitch import stitch_corpora
from curriculum_harness.reference_authoring.types import (
    ContentBlock,
    HaltedBlock,
    KUDItem,
    ReferenceKUD,
    Rubric,
    RubricCollection,
    SourceInventory,
    dump_json,
)


# ---------------------------------------------------------------------------
# Flag explanation data and confidence tier logic (Session 4c-1).
# ---------------------------------------------------------------------------

# Per-gate explanation layers. Keys match gate name prefixes (before ":lt_id").
# Each entry carries:
#   technical  — what the gate was actually checking
#   pedagogical — why a teacher reviewing the output might care
#   horizontal_note — (optional) conditional prompt for horizontal-domain sources
_GATE_EXPLANATIONS: dict[str, dict[str, str]] = {
    "classification_unreliable": {
        "technical": (
            "The KUD classifier ran 3 times on this source block; fewer than 2/3 "
            "runs agreed on the knowledge type (Type 1 / 2 / 3). The block was "
            "halted rather than forced into an uncertain classification."
        ),
        "pedagogical": (
            "If the classifier can't agree on whether this is declarative knowledge, "
            "a skill, or a disposition, the LT derived from it may not accurately "
            "reflect the source intent. A teacher should check the original source "
            "block and decide the classification manually before using this LT."
        ),
        "horizontal_note": (
            "In horizontal domains, a single source block may legitimately describe "
            "both a cognitive skill (Type 2) and a dispositional orientation (Type 3). "
            "The classification disagreement may reflect genuine domain complexity "
            "rather than an error."
        ),
    },
    "source_coverage": {
        "technical": (
            "The source_coverage gate checks that every non-heading inventory block "
            "that was not halted for severe underspecification produced at least one "
            "KUD item. A block that produced no items was silently dropped."
        ),
        "pedagogical": (
            "Source content that was skipped without explanation means the KUD may "
            "not fully represent the curriculum. A teacher relying on this KUD to "
            "plan learning targets may be missing competencies from those blocks."
        ),
    },
    "traceability": {
        "technical": (
            "The traceability gate checks that every KUD item's source_block_id "
            "refers to a real inventory block. An untraceable item cannot be verified "
            "against the original source."
        ),
        "pedagogical": (
            "A KUD item that cannot be traced to a source block may have been "
            "hallucinated or injected from model priors. Teachers should not use "
            "untraceable items as the basis for learning targets without source verification."
        ),
    },
    "no_compound_unsplit": {
        "technical": (
            "The no_compound_unsplit gate checks that each KUD item carries a single "
            "knowledge type (Type 1, 2, or 3) with a consistent kud_column and "
            "assessment_route. Inconsistent triples indicate a compound item that "
            "was not split during classification."
        ),
        "pedagogical": (
            "A KUD item that mixes knowledge types will produce an LT that is "
            "genuinely ambiguous about what kind of learning it targets. This makes "
            "assessment route selection (rubric vs. observation vs. reasoning) unreliable."
        ),
    },
    "cluster_unstable": {
        "technical": (
            "The cluster_unstable flag means the clustering model's output varied "
            "across runs — cluster count or member assignment differed across 3 "
            "self-consistency runs. The canonical cluster set was retained using "
            "the majority-vote result, but alternative groupings exist."
        ),
        "pedagogical": (
            "Cluster instability means the competency groupings may not be the only "
            "reasonable arrangement. A teacher reviewing these LTs should check "
            "whether each LT genuinely represents one distinct capability, or whether "
            "some LTs could reasonably be grouped differently."
        ),
        "horizontal_note": (
            "Horizontal-domain knowledge tends to form denser semantic networks where "
            "competency boundaries are legitimately less distinct than in hierarchical "
            "domains. This flag may reflect genuine domain complexity rather than "
            "a clustering error."
        ),
    },
    "cluster_unreliable": {
        "technical": (
            "The cluster_unreliable flag means fewer than 2/3 clustering runs agreed "
            "on a stable cluster structure. No reliable canonical cluster set could "
            "be extracted; the pipeline continues with whatever clusters were produced "
            "in the first run."
        ),
        "pedagogical": (
            "Without stable clusters, the LTs may not accurately group related "
            "competencies. The competency structure visible in these LTs may not "
            "reflect the source's actual organisation. Human review of the source "
            "material and the resulting LT set is strongly recommended."
        ),
        "horizontal_note": (
            "In horizontal domains, the entire source may form one tightly-connected "
            "semantic network. If clusters are genuinely unstable, consider running "
            "the pipeline on a smaller subsection of the source."
        ),
    },
    "count_differs": {
        "technical": (
            "The count_differs diagnostic means the number of clusters varied across "
            "runs. This is a sub-type of cluster instability — the model did not "
            "consistently choose the same number of competency groups."
        ),
        "pedagogical": (
            "The number of LTs generated may not be the only defensible count. "
            "A smaller number of broader LTs or a larger number of narrower LTs "
            "may both be reasonable representations of the source curriculum."
        ),
        "horizontal_note": (
            "Horizontal domains often support multiple valid granularities of "
            "competency description. The count variation may reflect legitimate "
            "domain flexibility rather than an error."
        ),
    },
    "lt_set_unreliable": {
        "technical": (
            "The LT generator ran 3 times on this cluster; fewer than 2/3 runs "
            "produced parseable LT output with a consistent count and knowledge-type "
            "distribution. No LTs were produced for this cluster."
        ),
        "pedagogical": (
            "The source content in this competency cluster did not produce stable "
            "learning targets. The content may be too loosely specified, or the "
            "cluster may contain content from multiple distinct competencies. "
            "A teacher should review the cluster's KUD items and consider manual LT authoring."
        ),
        "horizontal_note": (
            "In horizontal domains, large clusters containing conceptually dense "
            "content are more prone to LT generation instability. This may reflect "
            "genuine conceptual depth rather than a pipeline error."
        ),
    },
    "lt_set_unstable": {
        "technical": (
            "The LT generator reached 2/3 agreement on a majority signature, but "
            "not 3/3 stability. The LT set was retained using the majority result."
        ),
        "pedagogical": (
            "The learning targets in this set are the most consistent description "
            "produced, but alternative valid descriptions exist. A teacher reviewing "
            "these LTs should be aware that the boundaries between LTs may have "
            "shifted in different runs."
        ),
        "horizontal_note": (
            "LT instability is more common in horizontal domains where conceptual "
            "overlap between adjacent LTs is normal. The instability may reflect "
            "legitimate conceptual continuity rather than a generation error."
        ),
    },
    "band_statements_unreliable": {
        "technical": (
            "The band statement generator ran 3 times; fewer than 2/3 runs produced "
            "parseable output with a consistent signature. No band statements were "
            "produced for this LT."
        ),
        "pedagogical": (
            "Without band statements, teachers cannot use this LT to assess learners "
            "across the source's progression bands. The content may need manual "
            "authoring of band-level descriptors."
        ),
    },
    "band_statements_unstable": {
        "technical": (
            "Band statement generation reached 2/3 agreement but not 3/3 stability. "
            "The majority-vote statements were retained."
        ),
        "pedagogical": (
            "The band-level statements may be rephrased differently in alternative "
            "valid runs. The substance is stable but specific wording should be "
            "reviewed by a teacher before use."
        ),
    },
    "observation_indicators_unreliable": {
        "technical": (
            "The observation indicator generator ran 3 times; fewer than 2/3 runs "
            "produced parseable output with a consistent signature. No indicators "
            "were produced for this Type 3 LT."
        ),
        "pedagogical": (
            "Without observation indicators, this disposition cannot be assessed "
            "using the multi-informant observation route the LT requires. The "
            "source content may need review before indicators can be authored."
        ),
        "horizontal_note": (
            "Type 3 dispositional LTs in horizontal domains often describe rich, "
            "multi-faceted orientations that are difficult to reduce to a consistent "
            "indicator set. This may reflect genuine construct complexity."
        ),
    },
    "rubric_generation_failed": {
        "technical": (
            "The rubric generator ran 3 times; fewer than 2/3 runs produced "
            "parseable output with a consistent level-signature. No rubric was "
            "produced for this LT. This entry is a placeholder flag — no descriptor "
            "text is available."
        ),
        "pedagogical": (
            "Without a rubric, this LT cannot be used for criterion-referenced "
            "assessment. The LT exists in the output and represents a real "
            "competency from the source; a teacher can author a rubric manually "
            "using the LT name and definition as the starting point."
        ),
        "horizontal_note": (
            "Rubric instability is more common in horizontal-domain sources where "
            "political, social, or contested vocabulary is used. The generator may "
            "be producing legitimately different-but-valid rubric formulations "
            "across runs rather than disagreeing about the construct."
        ),
    },
    "single_construct": {
        "technical": (
            "The single_construct gate checks that adjacent applied levels (Emerging, "
            "Developing, Competent, Extending) share at least one topic-lemma. No "
            "topic-lemma overlap between adjacent levels is a signal that the rubric "
            "may be describing two different things across the progression."
        ),
        "pedagogical": (
            "A rubric where adjacent levels use entirely different vocabulary may "
            "be assessing different capabilities at different levels, rather than "
            "the same capability at different depths. A teacher reviewing this rubric "
            "should check whether the construct is genuinely the same across all levels."
        ),
        "horizontal_note": (
            "In horizontal domains, legitimate conceptual deepening often introduces "
            "new vocabulary as the learner moves to higher levels. A single_construct "
            "flag may reflect authentic progression rather than construct drift. "
            "A teacher should judge whether the vocabulary shift represents deepening "
            "the same construct or introducing a different one."
        ),
    },
    "observable_verb": {
        "technical": (
            "The observable_verb gate checks that each applied level descriptor "
            "contains at least one verb from the observable-action-verb list "
            "(identify, describe, compare, explain, analyse, evaluate, apply, etc.). "
            "No observable verb means the level cannot be reliably assessed."
        ),
        "pedagogical": (
            "A rubric level with no observable action verb describes a state of "
            "being rather than a demonstrable performance. Teachers need observable "
            "verbs to assess whether a learner has met each level — without them, "
            "the assessment criteria become subjective."
        ),
        "horizontal_note": (
            "Horizontal-domain content sometimes uses relational or orientational "
            "language rather than action verbs. A flag here may indicate that the "
            "rubric is using legitimately different (but observable) language that "
            "the gate's verb list does not include."
        ),
    },
    "competent_framing_judge": {
        "technical": (
            "An LLM-as-judge was asked to verify that the Competent descriptor "
            "reads as a success statement (the learner can do X) rather than "
            "an 'acceptable-but-deficient' statement (the learner almost does X "
            "but not quite). The judge returned a fail verdict."
        ),
        "pedagogical": (
            "Competent must always read as success, not as 'barely adequate'. "
            "If Competent sounds like 'the learner struggles but manages' rather "
            "than 'the learner can do this independently', the rubric sends a "
            "deficit message to learners and misrepresents what the grade means."
        ),
    },
    "competent_framing_regex": {
        "technical": (
            "The competent_framing_regex gate checks the Competent descriptor for "
            "deficit hedge-phrases (e.g. 'with limited', 'not yet', 'struggles to', "
            "'approaching', 'but fails'). One or more such phrases were found."
        ),
        "pedagogical": (
            "Deficit language in the Competent descriptor sends learners the wrong "
            "message: that 'meeting expectations' means being almost-but-not-quite "
            "adequate. Competent should describe what learners CAN do, not what "
            "they cannot."
        ),
    },
    "level_progression": {
        "technical": (
            "The level_progression gate checks that Competent does not borrow "
            "hedge-phrasing that belongs to Developing, and that Developing "
            "contains at least one qualifier or gap-marker that distinguishes it "
            "from Competent. A violation means adjacent levels are not clearly "
            "differentiated."
        ),
        "pedagogical": (
            "If Developing and Competent use the same kind of language, teachers "
            "and learners cannot tell them apart. Clear level differentiation "
            "is essential for the rubric to function as an assessment tool."
        ),
    },
    "word_limit": {
        "technical": (
            "The word_limit gate checks that each level descriptor falls within "
            "its asymmetric word limit (Competent ≤25 words; others smaller). "
            "A descriptor that is too long or empty fails this gate."
        ),
        "pedagogical": (
            "Long rubric descriptors are harder for teachers and students to "
            "apply consistently. Concise descriptors reduce assessment variability."
        ),
    },
    "no_inline_examples": {
        "technical": (
            "The no_inline_examples gate rejects descriptors that contain "
            "inline example phrasing ('such as', 'for example', 'e.g.', "
            "parenthetical content). Examples embedded in descriptors narrow "
            "the scope of what counts as evidence for that level."
        ),
        "pedagogical": (
            "Inline examples anchor assessment to specific instances, making the "
            "rubric context-dependent rather than transferable. Rubric descriptors "
            "should describe the capability, not list specific instances of it."
        ),
    },
    "propositional_thin_flag": {
        "technical": (
            "The propositional_thin_flag is informational — it fires when a Type 1 "
            "LT rubric uses only one verb bucket across all four applied levels. "
            "Structurally valid, but differentiation may rely only on degree "
            "(e.g. scope or independence) rather than qualitatively different operations."
        ),
        "pedagogical": (
            "A rubric that uses the same kind of cognitive operation at every level "
            "may make it hard for teachers to distinguish what Developing vs Competent "
            "actually look like in practice. A reviewer should check whether the "
            "levels are genuinely differentiated even if the verb type is the same."
        ),
    },
    "supporting_unreliable": {
        "technical": (
            "The supporting components generator (co-construction plan, student rubric, "
            "feedback guide) ran 3 times; fewer than 2/3 runs produced parseable "
            "output with a consistent signature."
        ),
        "pedagogical": (
            "The supporting materials help teachers introduce the rubric to students "
            "and give actionable feedback. Without stable supporting components, "
            "teachers will need to author these materials manually."
        ),
    },
    "supporting_skipped_gate_fail": {
        "technical": (
            "Supporting components were not generated for this LT because the "
            "rubric failed one or more semantic quality gates. A rubric with "
            "gate failures is not a stable anchor for co-construction materials."
        ),
        "pedagogical": (
            "The rubric for this LT has known quality issues (listed under the "
            "rubric's gate failures). Generating student-facing materials from "
            "a flawed rubric risks amplifying those issues. Resolve the rubric "
            "quality flags before generating supporting components."
        ),
    },
    "supporting_skipped_gen_fail": {
        "technical": (
            "Supporting components were not generated for this LT because the "
            "rubric generator itself failed (rubric_generation_failed). There is "
            "no rubric content to base co-construction materials on."
        ),
        "pedagogical": (
            "No rubric was produced for this LT, so supporting materials cannot "
            "be generated. A teacher would need to author a rubric manually first."
        ),
    },
}


def _confidence_tier(failure_count: int, stability_flag: str) -> str:
    """Compute HIGH / MEDIUM / LOW confidence tier per 4c-1 taxonomy.

    HIGH:   single gate failure; output stable across re-runs.
    MEDIUM: multiple gate failures on the same artefact OR output unstable.
    LOW:    multiple gate failures AND output unstable.
    """
    unstable_flags = {
        "rubric_unreliable", "rubric_unstable",
        "lt_set_unreliable", "lt_set_unstable",
        "cluster_unreliable", "cluster_unstable",
        "band_statements_unreliable", "band_statements_unstable",
        "observation_indicators_unreliable", "observation_indicators_unstable",
        "supporting_unreliable", "supporting_unstable",
        "classification_unreliable", "classification_unstable",
    }
    is_unstable = stability_flag in unstable_flags
    if failure_count > 1 and is_unstable:
        return "LOW"
    if failure_count > 1 or is_unstable:
        return "MEDIUM"
    return "HIGH"


def _explain_gate(gate_name: str) -> dict[str, str]:
    """Return explanation layers for a gate, falling back to generic."""
    prefix = gate_name.split(":")[0]
    return _GATE_EXPLANATIONS.get(
        prefix,
        {
            "technical": f"Gate `{prefix}` fired; see diagnostic above.",
            "pedagogical": "Review the gate diagnostic and the artefact content.",
        },
    )


def _flag_row(
    *,
    artefact: str,
    stage: str,
    gate: str,
    confidence: str,
    explanation: dict[str, str],
    source_domain: str,
) -> list[str]:
    """Render one flag as a markdown block."""
    lines = [
        f"### `{artefact}` — `{gate}` — **{confidence}**",
        "",
        f"**Stage:** {stage}",
        "",
        f"**Technical:** {explanation['technical']}",
        "",
        f"**Pedagogical:** {explanation['pedagogical']}",
    ]
    if source_domain == "horizontal" and "horizontal_note" in explanation:
        lines += [
            "",
            f"**Horizontal-domain note:** {explanation['horizontal_note']}",
        ]
    lines.append("")
    return lines


def _flags_section_markdown(
    *,
    kud: "ReferenceKUD",
    kud_report: "QualityReport",
    cluster_set: Any,
    lt_set: Any,
    band_coll: Any,
    indicator_coll: Any,
    rubric_coll: Any,
    supporting_coll: Any,
    source_domain: str,
) -> str:
    """Render the ## Flags section for the quality report."""
    lines: list[str] = ["## Flags", ""]
    flag_count = 0

    # KUD classification_unreliable blocks
    for h in kud.halted_blocks:
        if h.halt_reason == "classification_unreliable":
            exp = _explain_gate("classification_unreliable")
            confidence = _confidence_tier(1, "classification_unreliable")
            lines += _flag_row(
                artefact=h.block_id,
                stage="KUD classification",
                gate="classification_unreliable",
                confidence=confidence,
                explanation=exp,
                source_domain=source_domain,
            )
            flag_count += 1

    # KUD halting gate failures (non-artefact_count_ratio)
    for g in kud_report.gate_results:
        if not g.passed and g.halting and g.name != "artefact_count_ratio":
            exp = _explain_gate(g.name)
            confidence = _confidence_tier(1, "stable")
            lines += _flag_row(
                artefact="kud",
                stage="KUD gates",
                gate=g.name,
                confidence=confidence,
                explanation=exp,
                source_domain=source_domain,
            )
            flag_count += 1

    # Clustering flags
    overall_flag = getattr(cluster_set, "overall_stability_flag", "stable")
    if overall_flag != "stable":
        diagnostics = getattr(cluster_set, "overall_stability_diagnostics", [])
        gate_key = "cluster_unreliable" if overall_flag == "cluster_unreliable" else "cluster_unstable"
        diag_str = "; ".join(diagnostics) if diagnostics else overall_flag
        exp = _explain_gate(gate_key)
        confidence = _confidence_tier(1, overall_flag)
        lines += _flag_row(
            artefact="competency_clusters",
            stage="competency clustering",
            gate=f"{gate_key} ({diag_str})",
            confidence=confidence,
            explanation=exp,
            source_domain=source_domain,
        )
        flag_count += 1

    # Per-cluster instability
    for c in getattr(cluster_set, "clusters", []):
        if c.stability_flag != "stable":
            exp = _explain_gate("cluster_unstable")
            confidence = _confidence_tier(1, c.stability_flag)
            lines += _flag_row(
                artefact=c.cluster_id,
                stage="competency clustering",
                gate=c.stability_flag,
                confidence=confidence,
                explanation=exp,
                source_domain=source_domain,
            )
            flag_count += 1

    # LT generation halts (halted clusters)
    for h in getattr(lt_set, "halted_clusters", []):
        exp = _explain_gate("lt_set_unreliable")
        confidence = _confidence_tier(1, "lt_set_unreliable")
        lines += _flag_row(
            artefact=h.get("cluster_id", "(unknown)"),
            stage="LT generation",
            gate=f"lt_set_unreliable — {h.get('diagnostic', '')}",
            confidence=confidence,
            explanation=exp,
            source_domain=source_domain,
        )
        flag_count += 1

    # Unstable LTs
    for lt in getattr(lt_set, "lts", []):
        if lt.stability_flag not in ("stable", ""):
            exp = _explain_gate(lt.stability_flag)
            confidence = _confidence_tier(1, lt.stability_flag)
            lines += _flag_row(
                artefact=lt.lt_id,
                stage="LT generation",
                gate=lt.stability_flag,
                confidence=confidence,
                explanation=exp,
                source_domain=source_domain,
            )
            flag_count += 1

    # Band statement halts
    for h in getattr(band_coll, "halted_lts", []):
        exp = _explain_gate("band_statements_unreliable")
        confidence = _confidence_tier(1, "band_statements_unreliable")
        lines += _flag_row(
            artefact=h.get("lt_id", "(unknown)"),
            stage="band statements",
            gate=f"band_statements_unreliable — {h.get('diagnostic', '')}",
            confidence=confidence,
            explanation=exp,
            source_domain=source_domain,
        )
        flag_count += 1

    # Unstable band statements
    for bs in getattr(band_coll, "sets", []):
        if bs.stability_flag not in ("stable", ""):
            exp = _explain_gate(bs.stability_flag)
            confidence = _confidence_tier(1, bs.stability_flag)
            lines += _flag_row(
                artefact=bs.lt_id,
                stage="band statements",
                gate=bs.stability_flag,
                confidence=confidence,
                explanation=exp,
                source_domain=source_domain,
            )
            flag_count += 1

    # Observation indicator halts
    for h in getattr(indicator_coll, "halted_lts", []):
        exp = _explain_gate("observation_indicators_unreliable")
        confidence = _confidence_tier(1, "observation_indicators_unreliable")
        lines += _flag_row(
            artefact=h.get("lt_id", "(unknown)"),
            stage="observation indicators",
            gate=f"observation_indicators_unreliable — {h.get('diagnostic', '')}",
            confidence=confidence,
            explanation=exp,
            source_domain=source_domain,
        )
        flag_count += 1

    # Rubric flags
    if rubric_coll is not None:
        for r in rubric_coll.rubrics:
            failures = r.quality_gate_failures or []
            if not failures and r.stability_flag == "stable":
                continue
            # Determine gate label
            if "rubric_generation_failed" in failures:
                gate = "rubric_generation_failed"
                failure_count = 1
                stability = "rubric_unreliable"
            else:
                gate = ", ".join(failures) if failures else "gate_unknown"
                failure_count = len(failures)
                stability = r.stability_flag
            exp = _explain_gate(failures[0] if failures else "rubric_generation_failed")
            confidence = _confidence_tier(failure_count, stability)
            lines += _flag_row(
                artefact=r.lt_id,
                stage="criterion rubrics",
                gate=gate,
                confidence=confidence,
                explanation=exp,
                source_domain=source_domain,
            )
            flag_count += 1

    # Supporting component halts
    if supporting_coll is not None:
        for h in getattr(supporting_coll, "halted_lts", []):
            gate = h.get("halt_reason", "supporting_unreliable")
            exp = _explain_gate(gate)
            confidence = _confidence_tier(1, "supporting_unreliable")
            lines += _flag_row(
                artefact=h.get("lt_id", "(unknown)"),
                stage="supporting components",
                gate=gate,
                confidence=confidence,
                explanation=exp,
                source_domain=source_domain,
            )
            flag_count += 1

    if flag_count == 0:
        lines.append("No flags raised. All stages passed with stable output.")
        lines.append("")
    else:
        lines.insert(1, f"Total flags: **{flag_count}**\n")

    return "\n".join(lines) + "\n"


# Classifier priming for Ontario FOCUS ON historical-thinking concepts.
# Drawn from Seixas and Morton, "The Big Six Historical Thinking Concepts"
# (Nelson Education, 2013) — the research basis Ontario's FOCUS ON tags
# descend from. These descriptions calibrate the classifier to produce
# Type 3 indicators that reflect what historical-thinking research says
# these orientations look like as sustained dispositions, not just
# paraphrases of the tag names.
FOCUS_ON_PRIMING = """ONTARIO FOCUS ON HISTORICAL-THINKING CONCEPTS — PRIMING FOR THIS SOURCE

Ontario curriculum documents mark certain content with a "FOCUS ON" tag to
indicate a historical-thinking concept that should receive sustained emphasis
throughout the course. These concepts are SUSTAINED ORIENTATIONS in the sense
of the LT authoring skill's Type 3 definition — they operate by default across
all historical contexts the learner encounters, not merely when a specific
situation calls for them.

The four FOCUS ON concepts for Ontario Grade 7 History are defined below as
sustained orientations per Seixas and Morton's Big Six Historical Thinking
Concepts framework (Nelson Education, 2013):

FOCUS ON: Continuity and Change
A sustained orientation to notice what persists and what transforms across time,
resisting both "everything changes" and "nothing really changes" as default
framings. The learner by default attends to rate and scale of change across
different dimensions (political, social, economic, cultural) rather than
treating change as all-or-nothing. This is NOT merely a skill deployed when
asked to compare two time periods; it is an orientation that shapes HOW the
learner reads ALL historical material by default.
→ Classification: Type 3 Do-Disposition, multi_informant_observation.

FOCUS ON: Cause and Consequence
A sustained orientation to look for multiple contributing causes rather than
single causes; distinguishing immediate triggers from underlying conditions;
resisting monocausal or deterministic explanation as a default response to
historical events. The learner by default asks "what else contributed?" and
attends to intended vs unintended consequences. This is NOT merely a skill
deployed when asked "what caused X?"; it shapes HOW the learner interprets
ALL historical events by default.
→ Classification: Type 3 Do-Disposition, multi_informant_observation.

FOCUS ON: Historical Perspective
A sustained orientation to understand historical actors' decisions within their
own context's values, beliefs, knowledge, and constraints, rather than judging
them by present-day frames. The learner by default resists presentism — the
impulse to evaluate the past by today's standards — across all historical
encounters. This is NOT an occasion-triggered analytical skill; it is a
default orientation to HOW the learner reads accounts of historical actors.
→ Classification: Type 3 Do-Disposition, multi_informant_observation.

FOCUS ON: Historical Significance
A sustained orientation to recognise that significance is constructed, varies
across communities and historical traditions, and changes over time. The
learner by default resists the assumption that what appears in the textbook
is inherently what mattered, and sustains this across all historical content.
→ Classification: Type 3 Do-Disposition, multi_informant_observation.

IMPORTANT: When you encounter a content block that explicitly invokes one of
these FOCUS ON concepts (e.g., "FOCUS ON: Continuity and Change" or content
describing what students should develop in relation to one of these concepts),
apply Type 3 classification UNLESS the block describes ONLY a one-time
analytical task (e.g., "compare these two events using Cause and Consequence"),
in which case it may be Type 2 Do-Skill. Record your reasoning in
classification_rationale so the pipeline can record agreement/disagreement
with this placement rule.

Other Ontario curriculum content (specific historical events, facts, inquiry
skills) should be classified normally using the standard decision tree.
"""


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot",
        required=False,
        default=None,
        help="Path to a Phase 0 run-snapshot directory containing content.txt and manifest.json. Required unless --resume-from-kud is set.",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for the reference corpus (will be created).",
    )
    parser.add_argument(
        "--resume-from-kud",
        action="store_true",
        help="Skip inventory + KUD classification; read existing inventory.json and kud.json from --out and proceed from competency clustering onwards.",
    )
    parser.add_argument(
        "--dispositional",
        action="store_true",
        help="Declare the source as a dispositional-domain anchor (enables Type 3 distribution check; also sets domain to 'dispositional' if --domain is unset).",
    )
    parser.add_argument(
        "--domain",
        choices=("hierarchical", "horizontal", "dispositional"),
        default=None,
        help="Source domain for the artefact-count-ratio gate. If omitted, inferred from --dispositional (True → dispositional, False → hierarchical).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model ID for all per-item stages: KUD classification, LT generation, band statements, observation indicators, rubrics, supporting components (default {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=DEFAULT_RUNS,
        help=f"Self-consistency runs per block (default {DEFAULT_RUNS})",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Classification sampling temperature (default {DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "--cluster-model",
        default=None,
        help=(
            "Override the clustering-stage model. Defaults to the clustering "
            "module default (Haiku). Set to an Opus ID when the KUD exceeds "
            "~100 items and Haiku clustering is unstable."
        ),
    )
    parser.add_argument(
        "--skip-lts",
        action="store_true",
        help="Stop after KUD gates (legacy 4b-1 behaviour).",
    )
    parser.add_argument(
        "--skip-criteria",
        action="store_true",
        help="Skip the Type 1/2 criterion (rubric) and supporting-components stages. For debugging a band/indicator change without re-running rubrics.",
    )
    parser.add_argument(
        "--focus-on-priming",
        action="store_true",
        help=(
            "Prime the KUD classifier with Seixas/Morton Big Six developmental "
            "descriptions for Ontario FOCUS ON historical-thinking concepts. "
            "Use when running Ontario History sources where FOCUS ON tags should "
            "be classified as Type 3 Do-Disposition sustained orientations."
        ),
    )
    parser.add_argument(
        "--sub-run",
        action="store_true",
        help=(
            "Mark this run as a strand sub-run (invoked by the multi-strand "
            "orchestrator). Converts artefact_count_ratio from a hard halt to "
            "a flag, because per-strand slices are intentionally small and dense "
            "(many KUD items from few blocks) compared to whole-curriculum sources "
            "the ratio gate was calibrated on."
        ),
    )
    return parser.parse_args(argv)


def _load_inventory(path: str) -> SourceInventory:
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return SourceInventory(
        source_slug=raw["source_slug"],
        snapshot_path=raw["snapshot_path"],
        manifest_content_hash=raw["manifest_content_hash"],
        phase0_version=raw["phase0_version"],
        source_reference=raw["source_reference"],
        content_blocks=[ContentBlock(**b) for b in raw["content_blocks"]],
    )


def _load_kud(path: str) -> ReferenceKUD:
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return ReferenceKUD(
        source_slug=raw["source_slug"],
        snapshot_path=raw["snapshot_path"],
        classification_model=raw.get("classification_model", ""),
        classification_temperature=raw.get("classification_temperature", 0.3),
        self_consistency_runs=raw.get("self_consistency_runs", 3),
        items=[KUDItem(**i) for i in raw["items"]],
        halted_blocks=[HaltedBlock(**h) for h in raw["halted_blocks"]],
    )


_FOCUS_ON_KEYWORDS = [
    "continuity and change",
    "cause and consequence",
    "historical perspective",
    "historical significance",
    "focus on",
]


def _verify_focus_on_classification(kud: Any) -> dict:
    """Check FOCUS ON items against Type 3 Do-Disposition placement rule.

    Returns a dict with:
      - focus_on_items: list of item_ids whose content_statement or
        source_block_id is FOCUS ON content
      - agrees: items correctly classified as Type 3 Do-Disposition
      - disagrees: items classified as Type 1 or Type 2 (placement rule disagrees)
      - unstable: items with classification_unstable flag
      - outcome: 'all_agree' | 'disagree' | 'unstable' | 'no_focus_on_items'
    """
    focus_items = []
    for item in kud.items:
        text = (item.content_statement or "").lower()
        if any(kw in text for kw in _FOCUS_ON_KEYWORDS):
            focus_items.append(item)

    if not focus_items:
        return {"focus_on_items": [], "agrees": [], "disagrees": [], "unstable": [], "outcome": "no_focus_on_items"}

    agrees = []
    disagrees = []
    unstable = []
    for item in focus_items:
        if item.stability_flag in ("classification_unstable", "classification_unreliable"):
            unstable.append(item.item_id)
        elif item.kud_column == "do_disposition" and item.knowledge_type == "Type 3":
            agrees.append(item.item_id)
        else:
            disagrees.append({"item_id": item.item_id, "actual": f"{item.kud_column}/{item.knowledge_type}", "rationale": item.classification_rationale})

    if unstable:
        outcome = "unstable"
    elif disagrees:
        outcome = "disagree"
    elif agrees:
        outcome = "all_agree"
    else:
        outcome = "no_focus_on_items"

    return {
        "focus_on_items": [i.item_id for i in focus_items],
        "agrees": agrees,
        "disagrees": disagrees,
        "unstable": unstable,
        "outcome": outcome,
    }


def _stage_summary_markdown(
    *,
    kud_report_md: str,
    progression: Any,
    cluster_set: Any,
    lt_set: Any,
    band_coll: Any,
    indicator_coll: Any,
    rubric_coll: Any = None,
    rubric_report_md: str | None = None,
    supporting_coll: Any = None,
    focus_on_verification: dict | None = None,
) -> str:
    lines: list[str] = []
    lines.append(kud_report_md.rstrip())
    lines.append("")
    lines.append("## Stage: source-native progression structure")
    lines.append("")
    lines.append(f"- source type: `{progression.source_type}`")
    lines.append(f"- band count: **{progression.band_count}**")
    lines.append(
        f"- band labels: {', '.join(progression.band_labels)}"
        if progression.band_labels
        else "- band labels: (none)"
    )
    lines.append(f"- age range hint: {progression.age_range_hint}")
    lines.append(f"- detection confidence: `{progression.detection_confidence}`")
    if progression.uncertain():
        lines.append(
            "- **flag:** `progression_structure_uncertain` — band framework "
            "may need human verification."
        )
    lines.append(f"- detection rationale: {progression.detection_rationale}")
    lines.append("")
    lines.append("## Stage: competency clustering")
    lines.append("")
    lines.append(f"- clusters: **{len(cluster_set.clusters)}**")
    lines.append(f"- overall stability flag: `{cluster_set.overall_stability_flag}`")
    if cluster_set.overall_stability_diagnostics:
        lines.append("- diagnostics:")
        for d in cluster_set.overall_stability_diagnostics:
            lines.append(f"  - {d}")
    lines.append("- per-cluster stability:")
    for c in cluster_set.clusters:
        lines.append(
            f"  - `{c.cluster_id}` ({c.competency_name}): {c.stability_flag} — "
            f"{len(c.kud_item_ids)} items, dkt={c.dominant_knowledge_type}"
        )
    lines.append("")
    lines.append("## Stage: LT generation")
    lines.append("")
    lines.append(f"- LTs: **{len(lt_set.lts)}** (halted clusters: {len(lt_set.halted_clusters)})")
    kt_counts = {"Type 1": 0, "Type 2": 0, "Type 3": 0}
    for lt in lt_set.lts:
        kt_counts[lt.knowledge_type] = kt_counts.get(lt.knowledge_type, 0) + 1
    lines.append(
        f"- knowledge-type split: Type 1={kt_counts['Type 1']}, "
        f"Type 2={kt_counts['Type 2']}, Type 3={kt_counts['Type 3']}"
    )
    stability_counts: dict[str, int] = {}
    for lt in lt_set.lts:
        stability_counts[lt.stability_flag] = stability_counts.get(lt.stability_flag, 0) + 1
    lines.append(f"- LT stability: {dict(stability_counts)}")
    if lt_set.halted_clusters:
        lines.append("- halted clusters:")
        for h in lt_set.halted_clusters:
            lines.append(f"  - `{h.get('cluster_id')}`: {h.get('halt_reason')} — {h.get('diagnostic', '')}")
    lines.append("")
    lines.append("## Stage: Type 1/2 band statements")
    lines.append("")
    lines.append(f"- band sets: **{len(band_coll.sets)}** (halted LTs: {len(band_coll.halted_lts)})")
    b_stability: dict[str, int] = {}
    for s in band_coll.sets:
        b_stability[s.stability_flag] = b_stability.get(s.stability_flag, 0) + 1
    lines.append(f"- stability: {dict(b_stability)}")
    if band_coll.halted_lts:
        lines.append("- halted:")
        for h in band_coll.halted_lts:
            lines.append(f"  - `{h.get('lt_id')}`: {h.get('halt_reason')} — {h.get('diagnostic', '')}")
    lines.append("")
    lines.append("## Stage: Type 3 observation indicators")
    lines.append("")
    lines.append(f"- indicator sets: **{len(indicator_coll.sets)}** (halted LTs: {len(indicator_coll.halted_lts)})")
    i_stability: dict[str, int] = {}
    for s in indicator_coll.sets:
        i_stability[s.stability_flag] = i_stability.get(s.stability_flag, 0) + 1
    lines.append(f"- stability: {dict(i_stability)}")
    if indicator_coll.halted_lts:
        lines.append("- halted:")
        for h in indicator_coll.halted_lts:
            lines.append(f"  - `{h.get('lt_id')}`: {h.get('halt_reason')} — {h.get('diagnostic', '')}")
    lines.append("")

    if rubric_coll is not None:
        lines.append("## Stage: Type 1/2 criterion rubrics")
        lines.append("")
        lines.append(
            f"- rubrics: **{len(rubric_coll.rubrics)}** "
            f"(halted LTs: {len(rubric_coll.halted_lts)})"
        )
        r_stability: dict[str, int] = {}
        r_gate_failed = 0
        r_judge_fail = 0
        r_thin = 0
        for r in rubric_coll.rubrics:
            r_stability[r.stability_flag] = r_stability.get(r.stability_flag, 0) + 1
            if not r.quality_gate_passed:
                r_gate_failed += 1
            if (r.competent_framing_flag or "").lower() == "fail":
                r_judge_fail += 1
            if r.propositional_lt_rubric_thin_flag:
                r_thin += 1
        lines.append(f"- stability: {dict(r_stability)}")
        lines.append(f"- rubrics with gate failures: {r_gate_failed}")
        lines.append(f"- competent-framing judge: {r_judge_fail} fail")
        lines.append(f"- propositional_lt_rubric_thin_flag: {r_thin}")
        if rubric_coll.halted_lts:
            lines.append("- halted:")
            for h in rubric_coll.halted_lts:
                lines.append(
                    f"  - `{h.get('lt_id')}`: {h.get('halt_reason')} — "
                    f"{h.get('diagnostic', '')}"
                )
        lines.append("")
        if rubric_report_md:
            lines.append("### Criterion gate details")
            lines.append("")
            # Strip the top-level heading the gate module emits so we
            # don't duplicate headings under the main report.
            gated = "\n".join(
                line
                for line in rubric_report_md.splitlines()
                if not line.startswith("# Criterion quality report")
            ).strip()
            lines.append(gated)
            lines.append("")

    if supporting_coll is not None:
        lines.append("## Stage: supporting components")
        lines.append("")
        lines.append(
            f"- components: **{len(supporting_coll.components)}** "
            f"(halted LTs: {len(supporting_coll.halted_lts)})"
        )
        s_stability: dict[str, int] = {}
        for c in supporting_coll.components:
            s_stability[c.stability_flag] = s_stability.get(c.stability_flag, 0) + 1
        lines.append(f"- stability: {dict(s_stability)}")
        if supporting_coll.halted_lts:
            lines.append("- halted:")
            for h in supporting_coll.halted_lts:
                lines.append(
                    f"  - `{h.get('lt_id')}`: {h.get('halt_reason')} — "
                    f"{h.get('diagnostic', '')}"
                )
        lines.append("")

    if focus_on_verification is not None:
        lines.append("## Stage: FOCUS ON placement-rule verification (Ontario)")
        lines.append("")
        outcome = focus_on_verification.get("outcome", "no_focus_on_items")
        lines.append(f"- **outcome:** `{outcome}`")
        lines.append(f"- focus_on_items identified: {focus_on_verification.get('focus_on_items', [])}")
        lines.append(f"- agrees (Type 3 Do-Disposition): {focus_on_verification.get('agrees', [])}")
        disagrees = focus_on_verification.get("disagrees", [])
        if disagrees:
            lines.append("- **disagrees (classifier routed differently — placement rule not silently overridden):**")
            for d in disagrees:
                lines.append(f"  - `{d['item_id']}` classified as {d['actual']}: {d['rationale']}")
        else:
            lines.append("- disagrees: none")
        unstable = focus_on_verification.get("unstable", [])
        if unstable:
            lines.append(f"- **unstable:** {unstable}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    load_dotenv()
    _TOKEN_LEDGER.reset()
    os.makedirs(args.out, exist_ok=True)

    inventory_path = os.path.join(args.out, "inventory.json")
    kud_path = os.path.join(args.out, "kud.json")

    if args.resume_from_kud:
        if not os.path.exists(inventory_path) or not os.path.exists(kud_path):
            print(
                f"[refauth] --resume-from-kud requires existing {inventory_path} and {kud_path}",
                flush=True,
            )
            return 2
        print(f"[refauth] resuming from existing KUD at {kud_path}", flush=True)
        inventory = _load_inventory(inventory_path)
        kud = _load_kud(kud_path)
    else:
        if not args.snapshot:
            print("[refauth] --snapshot is required unless --resume-from-kud is set", flush=True)
            return 2

        # --- Strand detection (4c-3b) ----------------------------------------
        # Run before inventory building so multi-strand sources can be split
        # into per-strand sub-runs before any expensive classification happens.
        content_txt_path = os.path.join(args.snapshot, "content.txt")
        with open(content_txt_path, "r", encoding="utf-8") as _fh:
            _raw_content = _fh.read()

        print("[refauth] strand detection...", flush=True)
        try:
            _strand_result = detect_strands(_raw_content)
            print(f"[refauth] strand detection: {_strand_result.summary()}", flush=True)
            if _strand_result.flags:
                for _flag in _strand_result.flags:
                    print(f"[refauth] strand flag: {_flag}", flush=True)
        except StrandDetectionUncertain as _exc:
            # Pipeline halts — does not silently proceed with uncertain split.
            print(
                f"[refauth] HALT: strand detection uncertain — {_exc}",
                flush=True,
            )
            print(
                f"[refauth] Partial candidates: {[s.name for s in _exc.partial_candidates]}",
                flush=True,
            )
            print(
                "[refauth] Action required: inspect the source manually and either "
                "confirm one or both candidates as strands, or confirm single-strand. "
                "Do not re-run without resolving this uncertainty.",
                flush=True,
            )
            return 3  # Distinct exit code for strand uncertainty halt

        if _strand_result.is_multi_strand:
            print(
                f"[refauth] multi-strand source detected ({len(_strand_result.strands)} strands); "
                "invoking sub-run orchestration.",
                flush=True,
            )
            _all_lines = _raw_content.splitlines()
            _base_args = {
                "model": args.model,
                "runs": args.runs,
                "temperature": args.temperature,
                "cluster_model": getattr(args, "cluster_model", None),
                "domain": args.domain,
                "dispositional": args.dispositional,
                "skip_criteria": getattr(args, "skip_criteria", False),
                "skip_lts": getattr(args, "skip_lts", False),
            }
            _orch_exit, _run_summary = run_multi_strand_pipeline(
                original_snapshot_path=args.snapshot,
                unified_out_dir=args.out,
                all_lines=_all_lines,
                strand_result=_strand_result,
                base_args=_base_args,
            )

            if _run_summary["failed_strands"]:
                print(
                    f"[refauth] WARNING: {len(_run_summary['failed_strands'])} strand(s) "
                    f"failed sub-run: {_run_summary['failed_strands']}",
                    flush=True,
                )

            print("[refauth] stitching strand corpora...", flush=True)
            _stitch_ok, _stitch_failures = stitch_corpora(
                per_strand_dirs=_run_summary["per_strand_dirs"],
                unified_out_dir=args.out,
                strand_result=_strand_result,
                strand_slugs=_run_summary["strand_slugs"],
                strand_names=_run_summary["strand_names"],
                ledger_by_strand=_run_summary["ledger_by_strand"],
            )

            if _stitch_failures:
                print("[refauth] SANITY CHECK FAILURES:", flush=True)
                for _f in _stitch_failures:
                    print(f"  {_f}", flush=True)
            else:
                print("[refauth] all sanity checks passed.", flush=True)

            print("[refauth] multi-strand pipeline complete.", flush=True)
            return _orch_exit if _orch_exit != 0 else (0 if _stitch_ok else 2)
        # --- End strand detection branch -------------------------------------

        print(f"[refauth] inventory: reading {args.snapshot}", flush=True)
        inventory = build_inventory_from_snapshot(args.snapshot)
        dump_json(inventory.to_dict(), inventory_path)
        print(
            f"[refauth] inventory: {len(inventory.content_blocks)} blocks → {inventory_path}",
            flush=True,
        )
        print(
            f"[refauth] classifying with model={args.model} runs={args.runs} temperature={args.temperature}",
            flush=True,
        )
        source_context = FOCUS_ON_PRIMING if getattr(args, "focus_on_priming", False) else ""
        if source_context:
            print("[refauth] FOCUS ON priming active (Ontario historical-thinking concepts)", flush=True)
        kud = classify_inventory_sync(
            inventory,
            model=args.model,
            temperature=args.temperature,
            runs=args.runs,
            source_context=source_context,
        )
        dump_json(kud.to_dict(), kud_path)
        print(
            f"[refauth] kud: {len(kud.items)} items, {len(kud.halted_blocks)} halted blocks → {kud_path}",
            flush=True,
        )

    print("[refauth] detecting source-native progression structure", flush=True)
    try:
        progression = detect_progression(inventory)
    except ProgressionDetectionError as e:
        print(f"[refauth] HALTED: {e}", flush=True)
        return 2
    progression_path = os.path.join(args.out, "progression_structure.json")
    dump_json(progression.to_dict(), progression_path)
    print(
        f"[refauth] progression: {progression.source_type} | "
        f"{progression.band_count} band(s) | confidence={progression.detection_confidence} "
        f"→ {progression_path}",
        flush=True,
    )
    if progression.uncertain():
        print(
            "[refauth] WARNING: progression_structure_uncertain — band framework "
            "inferred from source text; human verification recommended.",
            flush=True,
        )

    source_domain = args.domain or ("dispositional" if args.dispositional else "hierarchical")
    print(
        f"[refauth] KUD gates (dispositional={args.dispositional}, domain={source_domain})",
        flush=True,
    )
    report = run_kud_gates(
        inventory,
        kud,
        source_is_dispositional=args.dispositional,
        source_domain=source_domain,
    )
    kud_report_md = quality_report_to_markdown(report)
    report_json_path = os.path.join(args.out, "quality_report.json")
    dump_json(report.to_dict(), report_json_path)

    if report.halted_by:
        if report.halted_by == "artefact_count_ratio":
            if getattr(args, "sub_run", False):
                # Sub-run mode (4c-3b): artefact_count_ratio becomes a flag.
                # Per-strand slices are intentionally dense (many KUD items from
                # few blocks), so the ratio gate calibrated for whole-curriculum
                # sources does not apply at the strand level.
                print(
                    f"[refauth] FLAG (sub-run): KUD gate `{report.halted_by}` "
                    "fired but converted to flag in sub-run context; pipeline continues.",
                    flush=True,
                )
                report.halted_by = None  # Allow pipeline to continue
            else:
                # Top-level run: artefact_count_ratio stays a hard halt.
                report_path = os.path.join(args.out, "quality_report.md")
                with open(report_path, "w", encoding="utf-8") as fh:
                    fh.write(kud_report_md)
                print(
                    f"[refauth] HALTED by KUD gate `{report.halted_by}` (hard halt; "
                    "use multi-strand pipeline path for this source). "
                    "Output preserved for diagnosis; exiting non-zero.",
                    flush=True,
                )
                return 2
        # All other KUD gate failures become flags — pipeline continues.
        if report.halted_by:
            print(
                f"[refauth] FLAG: KUD gate `{report.halted_by}` failed "
                "(converted to flag per 4c-1; pipeline continues).",
                flush=True,
            )

    if args.skip_lts:
        report_path = os.path.join(args.out, "quality_report.md")
        with open(report_path, "w", encoding="utf-8") as fh:
            fh.write(kud_report_md)
        try:
            import json as _json
            with open(report_json_path, encoding="utf-8") as _fh:
                _rpt = _json.load(_fh)
            _rpt["token_usage"] = _TOKEN_LEDGER.to_dict()
            with open(report_json_path, "w", encoding="utf-8") as _fh:
                _json.dump(_rpt, _fh, indent=2)
        except Exception:
            pass
        print(_TOKEN_LEDGER.summary_line(), flush=True)
        print("[refauth] --skip-lts set; stopping after KUD gates.", flush=True)
        return 0

    cluster_kwargs: dict[str, Any] = {"runs": args.runs}
    if args.cluster_model:
        cluster_kwargs["model"] = args.cluster_model
        print(
            f"[refauth] competency clustering (3x self-consistency, model={args.cluster_model})",
            flush=True,
        )
    else:
        print("[refauth] competency clustering (3x self-consistency)", flush=True)
    cluster_set = cluster_competencies_sync(inventory, kud, **cluster_kwargs)
    dump_json(cluster_set.to_dict(), os.path.join(args.out, "competency_clusters.json"))
    print(
        f"[refauth] clusters: {len(cluster_set.clusters)}; "
        f"overall={cluster_set.overall_stability_flag}",
        flush=True,
    )
    if cluster_set.overall_stability_flag == "cluster_unreliable":
        # Flag and continue — pipeline produces what it can from the first-run clusters.
        print(
            "[refauth] FLAG: clustering unreliable (converted to flag per 4c-1; "
            "pipeline continues with first-run clusters).",
            flush=True,
        )

    print("[refauth] LT generation (3x self-consistency)", flush=True)
    lt_set = generate_lts_sync(kud, cluster_set, runs=args.runs, model=args.model)
    dump_json(lt_set.to_dict(), os.path.join(args.out, "lts.json"))
    print(
        f"[refauth] LTs: {len(lt_set.lts)} (halted clusters: {len(lt_set.halted_clusters)})",
        flush=True,
    )
    if not lt_set.lts:
        # Flag and emit quality report — downstream LT-dependent stages are skipped.
        print(
            "[refauth] FLAG: no LTs produced (converted to flag per 4c-1; "
            "skipping downstream LT-dependent stages).",
            flush=True,
        )

    # Guard: if no LTs produced, skip all LT-dependent downstream stages.
    from curriculum_harness.reference_authoring.types import (
        BandStatementCollection,
        ObservationIndicatorCollection,
        SupportingComponentsCollection,
    )

    band_coll = BandStatementCollection(source_slug=kud.source_slug)
    indicator_coll = ObservationIndicatorCollection(source_slug=kud.source_slug)
    rubric_coll = None
    rubric_report_md = None
    supporting_coll = None

    if lt_set.lts:
        print(
            f"[refauth] Type 1/2 band statements (3x self-consistency) — "
            f"bands: {progression.band_labels}",
            flush=True,
        )
        band_coll = generate_band_statements_sync(lt_set, progression, runs=args.runs, model=args.model)
        dump_json(band_coll.to_dict(), os.path.join(args.out, "band_statements.json"))
        print(
            f"[refauth] band sets: {len(band_coll.sets)} (halted: {len(band_coll.halted_lts)})",
            flush=True,
        )

        print(
            f"[refauth] Type 3 observation indicators (3x self-consistency) — "
            f"bands: {progression.band_labels}",
            flush=True,
        )
        indicator_coll = generate_observation_indicators_sync(lt_set, progression, runs=args.runs, model=args.model)
        dump_json(indicator_coll.to_dict(), os.path.join(args.out, "observation_indicators.json"))
        print(
            f"[refauth] indicator sets: {len(indicator_coll.sets)} "
            f"(halted: {len(indicator_coll.halted_lts)})",
            flush=True,
        )

        if args.skip_criteria:
            print("[refauth] --skip-criteria set; skipping rubric + supporting stages.", flush=True)
        else:
            type12_count = sum(
                1 for lt in lt_set.lts if lt.knowledge_type in ("Type 1", "Type 2")
            )
            print(
                f"[refauth] Type 1/2 criterion rubrics (3x self-consistency) — "
                f"{type12_count} Type 1/2 LTs",
                flush=True,
            )
            rubric_coll = generate_criteria_sync(lt_set, progression, runs=args.runs, model=args.model)
            print(
                f"[refauth] rubrics: {len(rubric_coll.rubrics)} "
                f"(halted: {len(rubric_coll.halted_lts)})",
                flush=True,
            )

            # --- Halts-to-flags (4c-1): convert rubric generation halts to
            # flagged Rubric placeholder entries so criteria.json carries an
            # entry for EVERY Type 1/2 LT, not just the ones that generated.
            lt_by_id = {lt.lt_id: lt for lt in lt_set.lts}
            gen_halt_lt_ids: set[str] = set()
            for halt_entry in rubric_coll.halted_lts:
                lt_id = halt_entry.get("lt_id", "")
                lt_obj = lt_by_id.get(lt_id)
                kt = lt_obj.knowledge_type if lt_obj else "Type 1"
                flagged_rubric = Rubric(
                    lt_id=lt_id,
                    knowledge_type=kt,
                    levels=[],
                    stability_flag="rubric_unreliable",
                    quality_gate_passed=False,
                    quality_gate_failures=["rubric_generation_failed"],
                    competent_framing_flag="error",
                    competent_framing_judge_rationale=halt_entry.get(
                        "diagnostic", "rubric generation failed — fewer than 2/3 runs parseable"
                    ),
                )
                rubric_coll.rubrics.append(flagged_rubric)
                gen_halt_lt_ids.add(lt_id)
            if gen_halt_lt_ids:
                print(
                    f"[refauth] {len(gen_halt_lt_ids)} rubric-generation halt(s) "
                    "converted to flagged placeholder entries.",
                    flush=True,
                )
            # Clear halted_lts — they are now represented as flagged rubrics.
            rubric_coll.halted_lts = []

            dump_json(
                rubric_coll.to_dict(), os.path.join(args.out, "criteria.json")
            )

            rubric_report, rubric_coll = run_criterion_gates(rubric_coll)
            dump_json(
                rubric_report.to_dict(),
                os.path.join(args.out, "criteria_quality_report.json"),
            )
            rubric_report_md = criterion_report_to_markdown(rubric_report)
            with open(
                os.path.join(args.out, "criteria_quality_report.md"),
                "w",
                encoding="utf-8",
            ) as fh:
                fh.write(rubric_report_md)
            # Re-dump criteria.json with gate-result fields populated on each rubric.
            dump_json(
                rubric_coll.to_dict(), os.path.join(args.out, "criteria.json")
            )
            gate_failed = sum(
                1 for r in rubric_coll.rubrics if not r.quality_gate_passed
            )
            gen_failed = sum(
                1 for r in rubric_coll.rubrics
                if "rubric_generation_failed" in (r.quality_gate_failures or [])
            )
            print(
                f"[refauth] criterion gates: {gate_failed} rubric(s) with failures "
                f"({gen_failed} generation-failed placeholders, "
                f"{gate_failed - gen_failed} semantic gate failures); judge_fail="
                f"{sum(1 for r in rubric_coll.rubrics if (r.competent_framing_flag or '').lower() == 'fail')}",
                flush=True,
            )

            # Supporting components — only for rubrics whose halting gates passed
            # and that were actually generated (not generation-halt placeholders).
            # Flag skipped LTs explicitly in supporting_coll.halted_lts.
            passing_rubrics = [r for r in rubric_coll.rubrics if r.quality_gate_passed]
            skipped_rubrics = [r for r in rubric_coll.rubrics if not r.quality_gate_passed]
            print(
                f"[refauth] supporting components (3x self-consistency) — "
                f"{len(passing_rubrics)} passing rubric(s)",
                flush=True,
            )
            passing_coll = RubricCollection(
                source_slug=rubric_coll.source_slug,
                rubrics=passing_rubrics,
                halted_lts=[],
                model=rubric_coll.model,
                temperature=rubric_coll.temperature,
                runs=rubric_coll.runs,
            )
            supporting_coll = generate_supporting_components_sync(
                lt_set, passing_coll, runs=args.runs, model=args.model
            )
            # Record skipped rubrics as flagged halts in supporting_coll.
            for r in skipped_rubrics:
                if "rubric_generation_failed" in (r.quality_gate_failures or []):
                    halt_reason = "supporting_skipped_gen_fail"
                else:
                    halt_reason = "supporting_skipped_gate_fail"
                supporting_coll.halted_lts.append({
                    "lt_id": r.lt_id,
                    "halt_reason": halt_reason,
                    "diagnostic": (
                        f"rubric generation failed for {r.lt_id}; no content to build from"
                        if halt_reason == "supporting_skipped_gen_fail"
                        else f"rubric has gate failures {r.quality_gate_failures}; "
                             "not a stable anchor for supporting materials"
                    ),
                })
            dump_json(
                supporting_coll.to_dict(),
                os.path.join(args.out, "supporting_components.json"),
            )
            print(
                f"[refauth] supporting components: {len(supporting_coll.components)} "
                f"(halted/skipped: {len(supporting_coll.halted_lts)})",
                flush=True,
            )
    else:
        # No LTs — write empty stubs for artefacts that downstream expects.
        print("[refauth] skipping band/indicator/rubric stages (no LTs).", flush=True)
        dump_json(band_coll.to_dict(), os.path.join(args.out, "band_statements.json"))
        dump_json(indicator_coll.to_dict(), os.path.join(args.out, "observation_indicators.json"))

    focus_on_verification = None
    if getattr(args, "focus_on_priming", False):
        focus_on_verification = _verify_focus_on_classification(kud)
        outcome = focus_on_verification.get("outcome", "")
        print(f"[refauth] FOCUS ON verification outcome: {outcome}", flush=True)
        if focus_on_verification.get("disagrees"):
            print(
                f"[refauth] NOTE: {len(focus_on_verification['disagrees'])} FOCUS ON item(s) "
                "classified differently from placement rule. See quality_report.md.",
                flush=True,
            )

    extended_md = _stage_summary_markdown(
        kud_report_md=kud_report_md,
        progression=progression,
        cluster_set=cluster_set,
        lt_set=lt_set,
        band_coll=band_coll,
        indicator_coll=indicator_coll,
        rubric_coll=rubric_coll,
        rubric_report_md=rubric_report_md,
        supporting_coll=supporting_coll,
        focus_on_verification=focus_on_verification,
    )

    # Append the flags section (4c-1: every flag with confidence tier + layered explanation).
    flags_md = _flags_section_markdown(
        kud=kud,
        kud_report=report,
        cluster_set=cluster_set,
        lt_set=lt_set,
        band_coll=band_coll,
        indicator_coll=indicator_coll,
        rubric_coll=rubric_coll,
        supporting_coll=supporting_coll,
        source_domain=source_domain,
    )
    extended_md = extended_md + "\n" + flags_md

    report_path = os.path.join(args.out, "quality_report.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(extended_md)
    print(f"[refauth] extended quality report → {report_path}", flush=True)

    # Append token_usage to quality_report.json now that all stages have run.
    try:
        import json as _json
        with open(report_json_path, encoding="utf-8") as _fh:
            _rpt = _json.load(_fh)
        _rpt["token_usage"] = _TOKEN_LEDGER.to_dict()
        with open(report_json_path, "w", encoding="utf-8") as _fh:
            _json.dump(_rpt, _fh, indent=2)
    except Exception as _exc:
        print(f"[refauth] WARNING: could not write token_usage to quality_report.json: {_exc}", flush=True)

    print(_TOKEN_LEDGER.summary_line(), flush=True)
    print("[refauth] pipeline complete.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
