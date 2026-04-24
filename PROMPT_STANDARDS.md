# Curriculum Harness — Prompt Standards

*Read this file at the start of every Claude Code session that touches this repo.*

## Invariant rules — apply to every session

**No overwriting.** Never overwrite an existing file. Always write to a new versioned filename (e.g. criterion-bank-v3.json, not criterion-bank-v2.json). The one explicit exception is quality corrections to the current version where the session brief says "overwrite" and explains why — and even then, confirm before saving.

**Verify before reporting.** Never report a task as complete without running a verification command. For file moves: run `ls` on both old and new paths. For character counts: run `python3 -c "print(len('text'))"`. For JSON validity: run `python3 -c "import json; json.load(open('path'))"`. Self-reporting without verification is a failure.

**Description field character limit.** Skill description fields have a hard 250-character limit enforced by CI. After writing or editing any description field, run the character count check before committing. Count must be 250 or below.

**Registry and bundle steps are mandatory.** Every session that adds, moves, or modifies a skill must end with these steps in order — never skip any:
1. `python3 scripts/generate-registry.py`
2. Confirm count. Update `validate.yml` if count changed.
3. `cd mcp-server && npm run bundle-skills`
4. `cd ..`
5. `git add registry.json mcp-server/src/skills.json validate.yml`
6. Commit and push

**h2 Prompt sections.** Every skill's prompt section must use `## Prompt` (h2), never `# Prompt` (h1). A skill with an h1 Prompt header is invisible as a callable tool.

**School-agnostic outputs.** No skill output may reference any named school, programme, unit, or institution. Skills work from LT definitions and framework theory only.

**Panel gate before downstream build.** No downstream artefact is built until the upstream artefact has passed a panel review gate with human sign-off. For the REAL wellbeing framework: KUD charts → criterion bank → unified data file → programme guide. Schema checks confirm well-formedness only — they are not quality gates.

**Generic output is a failure.** Any descriptor, criterion, or artefact that could apply to any other entry without modification is a failure. Every generation prompt must include an explicit rule prohibiting generic output.

**Fix scope must be stated.** Every targeted fix session must end with an explicit statement of what the fix did not cover. A fix that addresses one flaw while leaving adjacent flaws untouched must name the adjacent flaws before closing.

## Criterion bank invariants

**Field order for competency_level_descriptors** — always in this exact order, no exceptions:
1. no_evidence
2. emerging
3. developing
4. competent
5. extending

**T3 entries do not have competency_level_descriptors.** T3 entries have: observation_indicators, confusable_behaviours, absence_indicators, conversation_prompts.

**criterion_statement for T2/T1** must capture the full cognitive demand of the KUD Do statement — not just the first clause.

**criterion_ids** are never reused or reordered. New entries continue from the highest existing ID.

**schema_version** on new or modified entries is always "v2" or higher.

**DAG validation must pass** before any criterion bank file is committed. Run the validation check and report the result.

**`within_lt_band` edge semantics depend on LT type.** The `within_lt_band` edge type has two distinct meanings, and applying the wrong reading produces spurious review flags.

- **T1 and T2 LTs:** `within_lt_band` is a **strict skill prerequisite**. Band N+1 cannot be demonstrated without Band N being secured first — the Band N+1 observable requires the Band N capacity as a building block. An edge is semantically correct only if the downstream criterion literally depends on the upstream skill or knowledge being in place.

- **T3 LTs:** `within_lt_band` is **developmental staging**, not a gated task dependency. Band N+1 represents a more mature expression of the same underlying disposition — it presupposes the developmental ground of Band N (the earlier-band dispositional move having become available to the student) but does not require Band N to have been evidenced first in order for Band N+1 evidence to count. Dispositions do not gate on prior-band performance the way skills do; they deepen and integrate across bands.

Consequence for review: do not remove T3 `within_lt_band` edges on the basis that the Band N+1 observable is "achievable without demonstrating Band N". That test applies to T2 strict prerequisites; under T3 developmental-staging semantics, the edge is correct even when each band's observable can in principle be evidenced independently. Removing T3 staging edges under the T2 test breaks the schema convention that every T3 LT carries an unbroken A→B→C→D→E→F chain.

If a T3 Band N+1 observable is genuinely unrelated to the Band N developmental ground (not merely a "different move that could arrive by other routes"), the issue is a KUD-chart defect, not an edge-semantics defect. Flag at chart level, not by edge removal.

## Preflight as session-start discipline

Every Claude Code session brief working on the REAL Wellbeing Framework begins with a run of python scripts/preflight.py, with the full output pasted into the session report before any other action. This rule is unskippable: no session brief, no matter how targeted or narrow, is exempt. Preflight status is recorded in every session report alongside all other deliverables.

If preflight fails at session start, the session does not proceed to its intended work. It addresses the preflight failure first — either as the substantive task for that session or by explicitly halting and reporting the failure.

This converts verification from "operator remembers to check" to "every session visibly reports on it". Preflight is the single integration-verification tool for the framework; it covers band-label compliance, LT count, DAG validity at both unified-data and criterion-level, schema compliance, field-derivation consistency, absence of inline BAND_LABELS in active scripts, unified-data band consistency, canonical self-check, criterion-to-LT referential integrity, LT-to-criterion referential integrity, orphan detection, and criterion-level prerequisite edge integrity. Twelve checks, all of which must pass.

## Specificity rule

A criterion-bank descriptor or competency-level descriptor is specific if and only if a teacher, reading the descriptor without knowing which band it describes, could correctly identify the band from the descriptor alone. The rule has two operational tests.

**Adjacency test.** The descriptor distinguishes this band from the bands immediately above and below it — a teacher given the same descriptor for Band C and Band D side-by-side can tell which is which on content alone, not on a "more" or "better" modifier.

**Observable-behaviour test.** For Type 1 and Type 2 criteria, the descriptor names a specific student action, product, or demonstration that could be observed or assessed. For Type 3 criteria, the descriptor names a specific observable behaviour, absence, confusable behaviour, or conversation prompt tied to that band's developmental territory — not a trait claim abstracted from behaviour.

A descriptor fails the rule if it uses vague modifiers ("appropriately", "effectively", "with increasing independence") without naming what the student does that justifies the modifier. A descriptor fails the rule if removing the band-letter header from the descriptor block makes two bands indistinguishable.

**Measurement procedure for gates.** At Gate 2, five random criteria are drawn from the criterion bank. Each is presented to a reviewer (persona or human) without its band header alongside the descriptors for the two adjacent bands, also headerless. The reviewer assigns band letters. If the reviewer assigns all five correctly, the rule is satisfied. If the reviewer misassigns one or more, the rule is failed and the gate-failure procedure applies.

## Named gate criteria

Four gates sit between the build stages of the REAL Wellbeing Framework. Each gate has specific, named pass criteria. An artefact does not proceed past a gate until every criterion is met.

### Gate 1 — KUD authoring → criterion generation

All six quality checks from the kud-chart-author skill pass on the KUD chart (Check 1: Understand independence; Check 2: Understand transfer; Check 3: Know specificity; Check 4: Progression lever; Check 5: Compound knowledge-type; Check 6: Know placement). Supplementary Checks A–D used in authoring annotations are not gate criteria. Zero unresolved compound-Do flags. Canonical band labels throughout. Preflight clean (all twelve checks pass). Independent-mode panel mean on the KUD chart ≥ 88.

### Gate 2 — Criterion generation → unified data integration

Independent-mode panel mean on the criterion bank ≥ 88. Preflight clean. The specificity rule is satisfied on a spot-check of five random criteria drawn from the newly-authored set (see Specificity rule section above for measurement procedure).

### Gate 3 — Unified data → external-facing artefact

Preflight clean on the integrated state (all twelve checks, including Checks 9–12 covering referential integrity). No remaining integration warnings from the build script's own verification steps. The independent-mode panel mean requirement does not apply to integration per se — integration is a mechanical operation, not a generative one — but any artefact derived from the integrated state downstream is subject to Gate 4.

### Gate 4 — External-facing artefact → publication

Independent-mode panel mean on the artefact ≥ 88. Teacher validation convergence above the thresholds set in the teacher validation protocol (docs/reference-corpus/real-wellbeing/teacher-validation-protocol-v1.md once Phase 0.4 ships; interim: documented external reviewer sign-off). Gareth's explicit sign-off on accuracy.

### Interim note on panel mode

Phase 0.3 has shipped in sequential-isolation mode (claude-education-skills, panel-review skill v1.0.1, commit 72e2c77 + cleanup). Gate criteria referencing panel review now invoke this skill, which executes seven segmented-context role reviews within a single session. This is an improvement on shared-context mode but is not full parallel-API mode — true parallel independence is deferred to a future skill version. The interim caveat from the prior draft is considered closed as of 24 April 2026.

### Note on the 88 threshold

The 88 threshold is currently convention — no calibration study has validated it. Phase 0.5 empirically validates the threshold against a known-high-quality artefact (LT 4.5 KUD v2) and a known-flawed artefact (LT 4.4 KUD v1 or a constructed flawed version with seeded issues). If the threshold discriminates meaningfully, 88 stands with evidence recorded in this document. If it does not, 88 is recalibrated and the new threshold is documented here alongside the supporting evidence. This note is updated or removed when Phase 0.5 ships.

## Gate-failure procedure

When an artefact fails a gate, the following three-cycle procedure applies.

**Cycle 1 — targeted revision.** The session that produced the artefact is re-opened with specific revision scope drawn from the panel flags, check failures, or preflight failures that caused the gate failure. Only the flagged elements get revised; unrelated content is preserved. The gate is re-run.

**Cycle 2 — expanded-scope revision.** If the revised artefact still fails the gate, revision scope expands. Previously-unflagged elements are re-examined for why they did not surface issues earlier. A second revision pass addresses both the original flags and any newly-surfaced concerns. The gate is re-run.

**Cycle 3 — methodology review escalation.** If the artefact still fails after two revision cycles, work on that artefact halts. Gareth is notified explicitly. A methodology review session is triggered. The assumption shifts from "this artefact needs more revision" to "the authoring approach or the gate criteria themselves may be miscalibrated". Methodology review produces one of three outcomes: a revised authoring approach (and the artefact is re-authored under the new approach); revised gate criteria (and the gate is re-applied under the new criteria); or an explicit decision to accept the artefact at its current state, with caveats recorded in both this document and the artefact itself.

An artefact that has been through all three cycles without acceptance is surfaced to Gareth as a structural blocker for the build plan, not a completed artefact.
