# Session 4b arc plan v3 — automated reference corpus and comparison

**Version note.** v2 held together under panel; two open questions resolved. v3 folds in: 3/3 self-consistency required for reference item stability (2/3 flags as unstable, ≤1/3 halts the item); comparator sources committed in advance rather than contingent on first-pass results.

## The goal

Produce reference KUDs, LTs, and criteria for anchor sources automatically. Compare harness output against references automatically. Surface diagnostic failures for Gareth to react to. All execution fully automated.

## Sources

**Three anchor sources:**

- **Hierarchical:** Common Core Grade 7 Ratios and Proportional Relationships (7.RP). Already extracted.
- **Horizontal:** Ontario Grade 7 History. Already extracted (two source variants — PDF and DCP).
- **Dispositional:** Welsh Curriculum for Wales Health and Well-being Statements of What Matters. Already extracted.

**Two committed comparators** (per panel, no longer optional):

- **Second hierarchical:** DfE KS3 Mathematics. Already extracted.
- **Second horizontal:** AP US Government Unit 1. Already extracted.

**One exam-spec companion:**

- **Hungarian felvételi.** Comparison target against the existing Palya run output with documented failures.

Six sources total across the 4b arc. All already extracted; no new Phase 0 work needed.

## Reference authoring — fully automated

Dedicated reference-authoring pipeline. Not the harness; not called by the harness. Produces comparison targets once per source.

**Pipeline steps:**

1. **Source-content inventory.** Reads extracted source; produces structured inventory of verbatim content blocks with source-position metadata. No interpretation.

2. **KUD classifier.** Applies LT authoring skill's knowledge-type decision tree to each block. Produces KUD items with Type 1/2/3 classification, assessment route, source traceability. Runs 3x at temperature 0.3 for self-consistency.

3. **LT generator.** Applies LT authoring skill per competency cluster. 2-3 LTs per competency. Type 1/2 get band statements A-D with progression levers; Type 3 get observation indicator sets per band. Runs 3x self-consistency.

4. **Criterion/indicator generator.** Applies rubric logic skill to Type 1/2 LTs (five-level rubrics, Competent IS success). Applies Type 3 observation protocol to Type 3 LTs (indicator sets + self-reflection prompts + parent prompts + conversation protocol reference). Runs 3x self-consistency.

5. **Quality gates.** Each artefact runs LT skill and rubric skill quality checklists automatically. Failures halt the artefact with specific diagnostic.

6. **Underspecification handling:**
   - Mild (source states capability, lacks progression) → pipeline fills progression using LT skill's levers, flags `underspecification: mild`.
   - Moderate (source states orientation without operational criteria) → pipeline produces operational criteria with rationale, flags `underspecification: moderate, rationale: <text>`.
   - Severe (source states aspiration without teachable destination) → pipeline produces no assessable reference, flags `underspecification: severe, aspirational_only`.

7. **Self-consistency resolution:**
   - 3/3 agreement → stable, item retained
   - 2/3 agreement → retained with `classification_unstable` flag; majority classification used
   - ≤1/3 agreement → item halted with `classification_unreliable` flag; no reference item produced

8. **Output.** Structured reference corpus at `docs/reference-corpus/<source-slug>/`: architecture diagnosis, KUD, LTs, criteria or observation indicators, all flags.

**Key discipline: pipeline does not consult harness output.** Neutral references, independent of harness.

## Structural checks in reference authoring

Run automatically; fail reference if out of band:

- **Artefact count ratios** per vision v4.1, with a dispositional-domain revision in 4b-2 (see `docs/plans/session-4b-gate-revisions-v1.md`): KUD 0.8–1.5 per source bullet for hierarchical/horizontal, KUD 0.8–2.2 (PROVISIONAL) for dispositional; LTs 1:1 ±20% with KUD; criteria 2–4 hierarchical, 1–3 horizontal per LT.
- **Knowledge-type distribution** vs source expectation (hierarchical → predominantly Type 1; dispositional → meaningful Type 3; horizontal → predominantly Type 2 with Type 3 for disciplinary thinking).
- **Source coverage** — every source bullet maps to ≥1 KUD item.
- **No injection** — every item carries source-position traceability; untraceable items rejected.

## Comparison — fully automated

Once references exist and harness has run on the same sources, comparison runs automatically.

- **Structural comparison (deterministic).** Counts, distributions, coverage, traceability metrics between reference and harness. Numerical diagnostic report.
- **Semantic comparison (LLM-as-judge, flagging only).** Classifies harness-item-vs-reference-item as same / different / partial / missing. Pre-calibrated against known-match and known-differ fixture before running.
- **Injection detection.** Harness items without source traceability flagged.
- **Negative reference matching.** Domain-plausible content not in source found in harness output → high-confidence injection flag.

Output: per-source diagnostic report. Gareth reads, reacts.

## Placement decisions

- **FOCUS ON tags (Ontario):** Do-Disposition column, Type 3 classification.
- **Statements of What Matters (Welsh CfW):** primarily Do-Disposition, Type 3; supporting propositional content routes to Know/Understand.
- **Neutral references only** — pipeline does not consult harness output.

## Session sequencing

Hardest case first, checkpoint after Welsh CfW KUD.

- **4b-1:** Build reference-authoring pipeline end-to-end. Run on Welsh CfW. Produce reference KUD only. Checkpoint — Gareth reacts to output.
- **4b-2:** If Welsh CfW KUD passes: pipeline produces Welsh CfW LTs and Type 3 observation indicators. Full Welsh CfW reference.
- **4b-3:** Pipeline runs on Common Core 7.RP and Ontario G7 History. Full references.
- **4b-4:** Pipeline runs on DfE KS3 Maths and AP US Gov Unit 1. Full comparator references.
- **4b-5:** Pipeline runs on Hungarian felvételi (exam-spec mode). Companion reference.
- **4b-6:** Comparison pipeline built. Runs against all six reference/harness pairs. Diagnostic reports.
- **4b-7:** Gareth reads diagnostic reports. Names Phase 1 rebuild priorities.

## What Gareth does

At 4b-1 close: look at Welsh CfW KUD. Right or not right. Feedback.

Same at each subsequent session close.

At 4b-7: read diagnostic reports, name Phase 1 priorities.

No per-item validation.

## Files

- New: `curriculum_harness/reference_authoring/` — pipeline.
- New: `docs/reference-corpus/` — per-source outputs.
- New: `curriculum_harness/comparison/` — comparison tooling.
- Updated: harness log and Second Brain snapshots per session.

## What the arc produces

- Automated reference-authoring pipeline.
- Reference corpus for three anchors + two comparators + one exam-spec companion.
- Automated comparison pipeline.
- Diagnostic report format.
- Named Phase 1 rebuild priorities.
