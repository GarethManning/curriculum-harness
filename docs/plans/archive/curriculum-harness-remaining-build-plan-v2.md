# Curriculum Harness — remaining build plan, v2

**Date:** 2026-04-19 (after Session 4b-4 closed)
**Project repo:** `~/Github/curriculum-harness` (renamed from curriculum-decomposer on 2026-04-19)
**Status:** Reference-authoring pipeline v0.5 shipped. Two anchor references complete (Welsh CfW, Common Core 7.RP). Ontario anchor partial — awaiting re-cluster + criterion bank. Harness Phase 1 onwards unchanged since project start; awaiting diagnostic output from the comparison pipeline.

## Important clarification: what we've built vs what still needs work

This project has two distinct pipelines. Confusion between them has been a real risk.

**The reference-authoring pipeline** is what we've been building through the 4b arc. It takes a curriculum source and produces a high-quality neutral reference output (KUD, LTs, band statements, observation indicators, criterion bank). Two anchor references are now complete; Ontario is partial. This pipeline is substantially working and producing usable output.

**The harness itself** is the tool the project exists to build. It takes a curriculum source and produces its own output via Phases 1-5 of the original harness. This pipeline is **unchanged since the project started** and has known failures: injection from model priors, Phase 3 consolidation collapse (32 bullets to 14 Do-Skills on felvételi), knowledge-type misclassification, flag-and-continue validation rather than hard-fail regeneration, English-only cue list in Phase 1, hardcoded GCSE_AQA_EXAM_BLOCK in Phase 4, Phase 5 strand mis-routing.

**The diagnostic path**: the reference pipeline produces references that represent what the harness *should* produce. Session 4b-6 (comparison pipeline) compares harness output against references. Session 4b-7 reads the comparison output and names Phase 1 rebuild priorities. Then Phase 1 rebuild begins — which is the actual work of fixing the harness.

Everything done so far is diagnostic infrastructure. The harness has not yet been improved. That work starts after 4b closes.

## Excellence criteria

Three things define "done" for this project, in load-bearing order.

**First, the harness reliably produces all four artefacts across all source types.** Requires Phase 1 rebuild informed by 4b-7 diagnostics.

**Second, the harness handles sources it hasn't seen before without breaking.** The generalisation claim. Testing requires running the harness on sources beyond the reference corpus and observing whether outputs stay within grain ratios, pass source-faithfulness checks, and correctly classify knowledge types.

**Third, the harness's outputs are good enough to be used directly by downstream consumers (teachers, AI tutors) without manual reconstruction.** The vision doc's one-line goal.

Excellent is not "no errors." Honest halts and flagged instability are features. Excellent is "high-quality output on most sources, flags low-quality output honestly, hands downstream consumers a useful input."

## First action for next session — commit this build plan to the repo

The build plan should live in the repo so Claude Code sessions can read it. First action when the next session opens: Claude Code commits this file to `docs/plans/curriculum-harness-remaining-build-plan-v1.md` (the v1 filename is fine for the repo copy; this v2 in /mnt/user-data/outputs is the handoff artefact). Also update `docs/plans/session-4b-arc-plan-v3.md` to reflect the 2026-04-19 scope change — Hungarian felvételi removed from the arc, remaining sessions reordered as Ontario follow-up → comparators → 4b-6 comparison pipeline → 4b-7 diagnostic.

Small housekeeping commit: `[docs] Update 4b arc plan and add remaining-build-plan to docs/plans/`.

## Remaining 4b arc sessions

Four sessions remain in the 4b arc. Each completes a specific piece of diagnostic infrastructure before Phase 1 rebuild begins.

### Session: Ontario re-cluster follow-up

Small session. Opus required for clustering stability (188-item source exposed Sonnet's clustering limits in 4b-3). Re-runs Ontario Grade 7 History clustering to address the 43% membership drift and 11 vs 15 cluster count variance. Once clustering stabilises, runs the Type 1/2 criterion generator on Ontario's LTs to complete the third anchor reference.

Expected output: stable Ontario clustering (target <20% membership drift across runs), approximately 15-20 Type 1/2 rubrics for Ontario, observation indicators for any Type 3 LTs that emerge post-stabilisation, updated cross-source summary.

### Session: Comparator sources

Medium session. Runs DfE KS3 Maths and AP US Government Unit 1 through the pipeline. Both are second-instance sources within their respective domain types (DfE is second hierarchical after Common Core; AP US Gov is second horizontal after Ontario). Load-bearing for the within-domain generalisation claim — until we see the pipeline behave on multiple hierarchical sources, we don't know whether Common Core's specific shape was the anchor or whether the pipeline generalises.

Expected output: two new reference corpora, each with full KUD/LT/band/criterion output. Cross-source summary extends to five sources. Within-domain comparison data.

Model: Sonnet unless either source exceeds 100 items at any classification stage, in which case Opus.

### Session 4b-6 — Comparison pipeline

Substantial session. Opus likely needed for architecture. Builds the comparison pipeline that takes harness output and a corresponding reference output and produces diagnostic reports. Four comparison dimensions:

- **Structural metrics**: item counts per stage, knowledge-type distribution, classification_unstable rates, gate pass rates. Numerical comparison.
- **Semantic comparison via LLM-as-judge**: does each harness LT correspond to a reference LT? Does each harness KUD item map to a reference KUD item? Where does the harness introduce content not in the reference? Where does it omit content the reference has?
- **Injection detection**: specifically checks whether harness LTs or KUDs introduce content not present in the source document. This is the failure pattern documented on felvételi (factorial notation invented by model priors).
- **Negative reference matching**: for sources where we have known-good reference output, does the harness get close? For sources where we don't have references, structural-only comparison still applies.

Output format: per-source diagnostic report with quantitative summary, semantic findings, and specific examples of drift.

### Session 4b-7 — Diagnostic reports and Phase 1 rebuild priorities

Substantial session. Runs the comparison pipeline against the harness's current output for each source in the corpus. Produces diagnostic reports. Then names Phase 1 rebuild priorities in order, with rationale grounded in the diagnostic data.

Expected output: comparison reports for each source (5 reports after comparator session: Welsh CfW, Common Core, Ontario, DfE KS3, AP US Gov). Phase 1 rebuild priority list with rationale tied to specific diagnostic findings. This is the last 4b session; output defines the Phase 1 rebuild arc.

## After 4b closes — Phase 1 rebuild

Multi-session arc. Addresses the specific failures that the 4b-7 diagnostic reports identified. Anticipated areas based on known failures:

- Phase 3 consolidation fix (prompt work, phase redesign, or branch on Phase 2 signal — determined by diagnostic)
- Hard-fail regeneration on validation failure (current behaviour is flag-and-continue)
- Multilingual support in Phase 1 scope filter (English-only cue list currently)
- Jurisdiction-agnostic command words in Phase 4 (currently hardcoded to GCSE AQA)
- Phase 5 strand routing (token-overlap heuristic currently mis-routes when label vocabulary doesn't match)
- Criterion bank phase added to the harness (currently absent; reference pipeline's criterion generator is the target shape)
- VALIDITY.md populated with construct-validity assertions (currently scaffolded but not populated)

Anticipated session count: 5-10 depending on diagnostic findings.

## Architectural decisions (saved to Second Brain)

- Source-native progression structure preserved in harness output. Welsh CfW uses Progression Steps 1-5, Common Core uses Grade 7, Ontario uses Grade 7, Scottish CfE uses Levels, etc. The harness does NOT translate between band frameworks.
- Any-framework translation is a separate Claude skill, not part of the harness. Handles REAL's A-D, any school's Year 1-6, research projects' custom bands. Source-native output is authoritative; Type 3 translations flagged as higher-judgement; metadata names source/target/rationale/semantic-losses; philosophical differences between frameworks surfaced not smoothed.
- Single-band sources handled correctly. Common Core 7.RP and Ontario Grade 7 History produce single statements, not progressions. Welsh CfW produces progressions across Progression Steps 1-5.
- Three content categories within wellbeing curricula distinguished. Cat 1 (propositional about dispositions), Cat 2 (enabling skills / occasion-prompted), Cat 3 (sustained operating states).
- Type 3 LTs never get rubrics. Absolute rule from the LT skill. Type 3 uses observation indicators instead.
- FOCUS ON placement rule enforced via verification-flag-disagreement, not silent override. When classifier disagrees, classifier's reasoning is preserved alongside the rule for human review.
- LT-level generic rubrics, not task-specific. Reference corpus produces criterion banks; task-specific rubric assembly is a downstream concern.

## Failure patterns (saved to Second Brain)

- Imposing REAL School's A-D band framework on domain-agnostic references. Sessions 4b-1 and 4b-2 inherited A-D from the LT skill's example calibration. Fixed in 4b-2.5; output preserved as generated-in-error artefact with honest framing.
- Provisional thresholds consistently need real-corpus revision. Artefact-count ratio ceiling 1.5 → 2.2 dispositional → 2.5 hierarchical. Rubric self-consistency signature revised after word-count-class and scope-keyword specificity fired on prose-surface noise. Rule: label thresholds as provisional from start; expect first-corpus revision.
- Claude Code's root-cause diagnosis beats design-change fixes from planning conversations. Rule: take Claude Code's root-cause fixes seriously when they contradict framing from planning.
- Dominant-element signatures become less stable with dictionary expansion. Rule: fix asymmetric bugs rather than widening input space.
- Two code paths that should agree but don't. Three instances in Session 4b-4 alone (lemmatiser mismatch; verb list desync; signature granularity mismatch). Rule: when adding a new code path that mirrors existing logic, verify both paths use identical logic.
- Model selection depends on architectural judgement AND execution scale. Rule: if largest single stage involves classifying or clustering more than roughly 100 items at once, use Opus.

## Model selection policy for remaining sessions

- Default to Sonnet for well-specified execution.
- Opus when either architectural judgement inside the session is load-bearing (4b-6 comparison pipeline) or when item counts exceed 100 at any stage (Ontario clustering, possibly DfE KS3 Maths depending on source size).
- Opus for planning conversations regardless of session model — architectural clarity at the planning stage prevents Claude Code sessions from drifting.

## Personas used in panel reviews

The curriculum-harness project uses a consistent panel of five voices for reviewing session prompts before execution. Personas operate in written reasoning mode, not Council MCP. Each persona has a specific disciplinary lens. Panel is run after v1 drafts; revisions folded into v2; v2 shipped unless score falls below 88.

- **Dylan Wiliam** — assessment, formative feedback, grain and calibration
- **Guy Claxton** — dispositional learning, self-regulation, metacognitive development; load-bearing for Type 3 and Welsh CfW
- **Daisy Christodoulou** — explicit instruction, cognitive load, evidence-based curriculum design
- **Ken Koedinger** — learning science, methodology rigour, measurement discipline; pushes on operationalised signatures, threshold calibration, descriptive statistics
- **Sam Wineburg** — historical thinking, horizontal domain expertise; load-bearing for Ontario G7 History

Other personas appear when session topic warrants it. Average-below-88 triggers a v2 revision.

## Artefact inventory — what exists

**Reference corpora at `docs/reference-corpus/`**:

- `welsh-cfw-health-wellbeing/` — KUD (33), competency clusters (9), LTs (20), Progression Step 1-5 band statements (11 sets), Progression Step 1-5 observation indicators (5 sets), Type 1/2 rubrics (12, 11 gate pass), supporting components (9), progression structure metadata, quality report, reference review markdown, three CSV exports, `_generated-in-error-a-d-version/` preserved subdirectory
- `common-core-g7-rp/` — KUD (22), competency clusters (4), LTs (8), Grade 7 band statements (6 sets), no observation indicators (no Type 3 content), Type 1/2 rubrics (7, 6 gate pass), supporting components (4), progression structure metadata, quality report, reference review markdown, four CSV exports
- `ontario-g7-history/` — KUD (188), competency clusters (11 unstable), LTs (23), Grade 7 band statements (21 sets), observation indicators (2 sets), quality report, FOCUS ON verification outcome (0 agree / 1 disagree / 6 unstable), reference review markdown, three CSV exports. Criterion bank NOT YET GENERATED — awaiting Ontario follow-up session.
- `_cross-source-summary.md` — cross-source comparison

**Pipeline code at `curriculum_harness/reference_authoring/`**:

Inventory module, KUD classifier, KUD gates, competency clustering, LT generator, band statement generator, observation indicator generator, criterion generator (Type 1/2), criterion gates, supporting components generator, progression detection module with per-jurisdiction lookup table.

Scripts at `scripts/reference_authoring/`: CSV exporter (dynamic source-native band columns), reference review renderer, standalone criterion runner.

**Planning and log documents**:

- `docs/plans/session-4b-arc-plan-v3.md` — arc plan (needs update to reflect Hungarian felvételi drop and revised session order; first action of next session handles this)
- `docs/plans/session-4b-gate-revisions-v1.md` — gate threshold revision history
- `docs/project-log/harness-log.md` — session-by-session log
- Session prompts preserved at `docs/plans/` and `/mnt/user-data/outputs/`

**Harness itself (Phase 1+ state unchanged since project start)**: unchanged. Produces KUD and LT output with known failures listed above. Awaits Phase 1 rebuild informed by 4b-7 diagnostic.

## Operating discipline

- Plan before executing. Panel v1 drafts before shipping; fold revisions into v2.
- Commit after every step within a session. Each session has 5-9 commits.
- Log sessions in `docs/project-log/harness-log.md` at session close.
- Save state snapshots and failure patterns to Second Brain at session close.
- Never overwrite planning documents or analysis outputs; create new versioned files.
- No work after 8:30pm Budapest time.
- Prompts always given in code blocks for copy-pasting.
- Give the Claude Code invocation command explicitly with model named: `cd ~/Github/curriculum-harness && claude --dangerously-skip-permissions --model [sonnet|opus]`.

## What this build plan does NOT cover

- Palya integration (separate project)
- Kaku product decisions (separate project)
- School-specific curriculum implementations
- REAL School-specific band translation (separate Claude skill work)
- Curriculum visualisation app (deferred product work, not in 4b arc)
- Cross-referencing multiple wellbeing curricula for Oura (deferred; depends on harness producing stable outputs first)

---

*Build plan v2 generated 2026-04-19 after Session 4b-4 close. Next update expected after Ontario follow-up session.*
