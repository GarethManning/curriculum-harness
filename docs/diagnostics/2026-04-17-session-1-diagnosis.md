# Session 1 diagnosis — 2026-04-17

Read-only diagnostic pass following the felvételi run
(`outputs/palya-felveteli-2026-04-17/`). No code or prompts edited;
findings only.

---

## Question 1 — Phase 3 behaviour

**Implementation file:** `kaku_decomposer/phases/phase3_kud.py`
(200 lines). **Inputs read from state:** `architecture_diagnosis`
(dict), `raw_curriculum` (string), `mcp_server_url`,
`mcp_server_name` (phase3_kud.py:110–123). **No other state fields
are read by Phase 3.**

### Is consolidation a prompt instruction, an architectural constraint, or both?

**Neither explicit.** Consolidation is emergent, not instructed.

There is no prompt fragment that says "consolidate" or "prefer one
KUD item per strand." Equally, there is no prompt fragment that
says "produce one KUD item per source bullet" or any other
fan-out directive. The Phase 3 prompts are silent on cardinality.

Two prompts are issued inside Phase 3:

- **MCP path instruction** (phase3_kud.py:125–130):

  > "Invoke `{TOOL_NAME}` using the curriculum text and this
  > architecture diagnosis:\n{arch_text}\n\nAfter tool results,
  > reply with ONLY a JSON object for know, understand, do_skills,
  > do_dispositions arrays (items with content, knowledge_type,
  > assessment_route, notes)."

  `TOOL_NAME = "kud-knowledge-type-mapper"` (phase3_kud.py:26).
  The MCP tool's own behaviour is external to this repo.

- **Sonnet-direct fallback** `SYSTEM_DIRECT` (phase3_kud.py:69–77):

  > "You map curriculum expectations into KUD lists. Output ONLY
  > valid JSON: {... four arrays ...}. Tags must align with the
  > architecture diagnosis provided. No markdown."

Only two semantic anchors exist: the verb "map" and the clause
**"Tags must align with the architecture diagnosis provided."** The
architecture JSON passed as `arch_text` (phase3_kud.py:123) contains
**six strands** for felvételi (4 hierarchical, 1 horizontal, 1
dispositional — see `architecture_v1.json`). "Tags must align" is
the only instruction tying KUD items to the architecture, and given
only six strands are offered, the model clusters content into a
similarly small number of buckets per list.

### Can Phase 3 represent a one-to-many fan-out?

**Structurally yes; behaviourally no.**

- **Structurally unbounded.** `KUD` is four Python lists of
  `KUDItem` with no cap (types.py:403–445). There is no code that
  trims or caps the list lengths. A KUD with 80 `do_skills` items
  would parse, serialize, and flow through Phase 4 exactly as a KUD
  with 14 does.
- **Behaviourally constrained by two signals.** (1) The six-strand
  architecture diagnosis passed into the prompt, and (2) the
  external MCP tool's aggregation tendency. The felvételi output
  was 7 know + 7 understand + 14 do_skills + 3 do_dispositions =
  31 items. Phase 4 emits 1 LT per KUD item (phase4_lt_generation.py:419
  — `for bucket, item in kud.all_items():`), so the Phase 3
  cardinality directly drives the final LT count (31 LTs, matching).
- **Only filter that removes items** is `_filter_recall_only_know`
  (phase3_kud.py:57–66), and it only shrinks the `know` bucket; it
  never fans out.

### Which driver: prompt or architecture?

Both, indirectly. The prompt tells the model to align with the
architecture; the architecture is a six-strand summary; no prompt
directive pushes toward per-bullet granularity. The architectural
constraint that enforces the consolidation is **the fact that
Phase 3's only shape signal is a six-strand diagnosis, and the
prompt instructs alignment with it.**

---

## Question 2 — Phase 2 signal and its propagation

### What Phase 2 produces

Phase 2 writes `architecture_diagnosis` via `ArchitectureDiagnosis`
(types.py:279–381). Fields:

- `architecture_type: str`
- `proportions: dict[str, float]`
- `hierarchical_elements`, `horizontal_elements`,
  `dispositional_elements: list[str]` (derived labels)
- `strands: list[ArchitectureStrand]` — each with
  `{id, label, lane, expected_lt_types, values_basis}`
- `structural_flaw: str`
- `auto_assessable_pct: float`

The felvételi Phase 2 JSON
(`palya_felveteli_2026_04_17_v1_architecture_v1.json`) shows six
strands, with `values_basis` strings that are editorial commentary
(e.g. the strand `procedural-fluency-habits` on line 73 of the
architecture JSON: *"Development of mathematical persistence,
precision in calculations, and self-monitoring represents enacted
mathematical dispositions that develop through practice."*).

### Does any field distinguish bare bullet list vs narrative prose vs designed outline?

**No — not in `architecture_diagnosis`.**

Phase 2's schema has no field for document shape / text density /
bullet-vs-prose. The free-text `structural_flaw` is editorial, not
structural.

**BUT Phase 1's `curriculum_profile` does carry this signal:**

- `curriculum_profile.scoping_strategy` — felvételi: `"full_document"`
  (distinguishes compact docs from keystage/grade-filtered longer docs)
- `curriculum_profile.assessment_signals.format` — felvételi:
  `"10 short tasks, 45 minutes, 50 points total"` (a free-text shape
  hint, document-typology-like)
- `curriculum_profile.assessment_signals.has_assessment_objectives`,
  `has_command_words`, `has_mark_scheme` — felvételi: all `false`
- `curriculum_profile.confidence` — felvételi: `"high"`
- `curriculum_profile.document_family` — felvételi:
  `"exam_specification"` (but so is GCSE AQA; family alone does not
  distinguish bullet list from exam paper-style spec)

These signals are preserved on state by Phase 1 (phase1_ingestion.py:670–674)
and read by Phase 4 (phase4_lt_generation.py:397–399,
`doc_fam = ...curriculum_profile...document_family`) and Phase 5
(phase5_formatting.py:424, `resolve_lt_statement_format`). Phase 2 also
does not read the profile directly (phase2_architecture.py:97 only
reads `raw_curriculum`; the architecture prompt has no knowledge that
the document is a topic list).

### Does Phase 3 read any of this signal?

**No.** Phase 3's state reads are exhaustively listed in
phase3_kud.py:110–123. `curriculum_profile` is not read. The document
shape, entrance-exam flag, full-document scoping, and free-text
format hint are all on state but invisible to Phase 3.

### If Phase 3 ignores relevant signal, name it and the point it should be used

- **Signal ignored:** the full `curriculum_profile` dict (with
  document_family, scoping_strategy, and especially
  `assessment_signals.format`) and also the `confidence` level.
- **Point in Phase 3 where it should be consulted:** at
  phase3_kud.py:110–123 (input gathering), the profile would need
  to be pulled from state alongside `arch` and `raw`. Downstream,
  either (a) a profile-conditional branch selects a different
  prompt / tool invocation (per-bullet mode vs strand-aggregated
  mode), or (b) the profile's shape hints are serialized into the
  prompt body so the model can adjust its own cardinality. Neither
  path exists today.

---

## Question 3 — Hard-fail validation delta

### Decision record

**Not found in repo.** There is no `docs/` directory
(`ls` on repo root confirms only `checkpoints/ configs/
kaku_decomposer/ outputs/ pyproject.toml README.md scripts/ tests/
VALIDITY.md`). No `docs/decisions/`, no ADR, no file dated
2026-04-02. `git log --all` returns only three commits, the
earliest of which (`f39c919`) is the output-file-naming fix; the
commit history does not reach back to 2 April 2026. A text search
for hard-fail / regeneration patterns returns only three files:
VALIDITY.md, `scripts/validity-gate/validate_regenerate_loop.py`,
and `scripts/validity-gate/README.md`.

Stating this explicitly per the session rules: **the decision
record referenced in the task brief could not be located in this
repository.** The closest in-repo articulation of the intended
behaviour is VALIDITY.md foundation moment 2 (VALIDITY.md:116–137)
and `validate_regenerate_loop.py:1–44`, both scaffolded on
2026-04-17 (commit a8713d5).

### What the in-repo articulation says the behaviour should be

VALIDITY.md:128–137:

> "`validate_regenerate_loop.py` — a **known gap.** If any LT
> initially failed surface validation, Phase 4 is supposed to
> regenerate it. At present, regeneration-on-failure is not
> guaranteed to run. The gate script will assert, for any run
> where Phase 4 emitted a regeneration event, that the final LT
> set passes surface-form. Without regeneration, this gate will
> fail and the loop becomes a tracked dev item."

`validate_regenerate_loop.py:31–38` (notes field):

> "KNOWN GAP — Phase 4 does not yet emit a regeneration-event
> log, and regeneration-on-failure is not guaranteed to run.
> Implementing this gate requires (1) Phase 4 to record initial
> failures and regeneration attempts in the run report, and (2)
> this script to read that record and re-validate the final LT
> set."

### What the code actually does

Phase 4's validator is `_validate_lt` (phase4_lt_generation.py:235–273).
Flags it can append:

- `MISSING_LT_STATEMENT` (line 243)
- `MISSING_I_CAN_FORMAT` (line 246) / `LT_FORMAT_EXPECTATION_MISMATCH`
  (lines 249, 253)
- `COMPOUND_TYPE` (line 255 — pre-decided in `_lt_type_and_compound`)
- `EXCEEDS_WORD_LIMIT` (line 258, `wc > 25`)
- `POSSIBLE_COMPOUND` (lines 260–266, detects " and " between two
  verb-like halves)
- `EMBEDDED_EXAMPLE` (line 268, `r"\([^)]+\)"`)
- `DISPOSITION_RUBRIC_ERROR` (lines 269–272, rubric vocabulary in a
  Type-3 LT)

After validation, the LT is appended to `targets` unconditionally
(phase4_lt_generation.py:509–510):

```
lt.flags = _validate_lt(lt, compound_type=compound, fmt=fmt)
targets.append(lt.to_dict())
```

**There is no branch that inspects `lt.flags` and triggers a
regeneration call.** The only retry paths in Phase 4 are for API
timeouts / exceptions (lines 459–494), which fall back to the direct
Sonnet path; they do not retry on validation-flag content.

### Delta, precisely

- **Intended (per VALIDITY.md / validate_regenerate_loop stub):**
  initial LT fails surface validation → regenerate → re-validate →
  repeat until clean → record the regeneration event → emit the
  clean final LT. Runs with no regenerations emit no regeneration
  events; runs with regenerations record them.
- **Actual:** surface validation attaches flags; the flagged LT is
  written to the output regardless; no regeneration event is ever
  emitted because no regeneration is ever attempted. The felvételi
  run shipped with three flagged items directly in
  `learning_targets_v1.json` (`POSSIBLE_COMPOUND` ×2 on LT #6 and
  LT #27, `DISPOSITION_RUBRIC_ERROR` ×1 on LT #29 — see REVIEW.md
  §1 flag distribution).
- **Size of the gap:** a regenerate-on-fail loop around
  phase4_lt_generation.py:509 (an `if lt.flags & FAIL_SET: retry`
  branch writing to the run report) does not exist. The stub
  correctly diagnoses this as "known gap"; the stub is the only
  in-repo documentation of the intended behaviour.

---

## Question 4 — VALIDITY.md state

**File:** `VALIDITY.md` (312 lines, scaffolded 2026-04-17, commit
a8713d5). Also `scripts/validity-gate/README.md` carries the
status table; the stub scripts all exit `NOT_IMPLEMENTED` via
`_stub.py`. **No gate has been implemented.**

### Assertion table

| # | Foundation moment | Assertion | Gate script | Status |
|---|---|---|---|---|
| a | 1 — source → LT coverage | Every source content element traces to ≥1 LT | `validate_source_coverage.py` | **pending** |
| b | 1 — no-fabrication | No LT introduces content unsupported by the source | `validate_source_faithfulness.py` | **pending** |
| c | 1 — architecture verifiability | Phase 2 strand/level diagnosis is justifiable from source | `validate_architecture_diagnosis.py` | **pending** |
| d | 2 — LT surface form | Word count, format stem, single-construct, no embedded examples | `validate_lt_surface_form.py` | **pending** |
| e | 2 — regenerate loop | Phase 4 regeneration ran for any initial surface-form failure | `validate_regenerate_loop.py` | **pending (known gap)** |
| f | 3 — profile-conditional prompt scope | `GCSE_AQA_EXAM_BLOCK` attached iff source is AQA-shaped | `validate_exam_block_scope.py` | **pending (known bug)** |
| g | 4 — LT → criterion coverage | Every LT decomposes to ≥1 criterion | `validate_lt_criterion_coverage.py` | **deferred** |
| h | 4 — prerequisite DAG | Prerequisite edges form a DAG | `validate_prerequisite_dag.py` | **deferred** |

"Implemented" status: **0 / 8**.

### Which assertions become implementable once (a) a coverage judge exists and (b) a no-invention judge exists?

- **(a) `validate_source_coverage.py`** — this *is* the coverage
  judge, in a narrow framing. A coverage judge that can decide "does
  this source bullet trace to ≥1 LT?" is exactly the primitive this
  gate needs (VALIDITY.md:98–113 confirms all inputs already land in
  `outputs/<run>/`: source text, Phase 1/2 JSON, learning_targets
  JSON).
- **(b) `validate_source_faithfulness.py`** — this *is* the
  no-invention judge. Inverse framing of the same primitive: "does
  this LT map back to ≥1 source bullet (or support)?" If the
  no-invention judge yields per-LT source-support evidence, the
  gate passes when every LT has ≥1 source match.
- **(c) `validate_architecture_diagnosis.py`** — becomes
  implementable once a source-evidence matching primitive exists
  (which is what (a) and (b) share). Strand labels, level model,
  and scoping strategy would each need to be linked back to a
  specific source passage; a no-invention judge's matcher supplies
  this.

**All three Foundation-Moment-1 assertions (a/b/c) become
implementable once both judges exist.** The stub README
(`scripts/validity-gate/README.md:17–27`) lists them together
under foundation moment 1.

Assertions (d), (e), (f) are independent of the coverage /
no-invention judges:

- **(d) surface form** is a purely syntactic check — writable today
  from the output JSON alone.
- **(e) regenerate loop** requires a pipeline change first
  (Phase 4 to emit a regeneration-event log); not a judge problem.
- **(f) exam-block scope** needs a source-jurisdiction field or
  Phase 1 `awarding_body` inference; not a judge problem.

Assertions (g) and (h) are deferred pending the criterion-bank phase.

---

## Question 5 — Judges and adjacent-mechanism declarations

Multiple filters / validators / heuristics exist across the
pipeline. None carries an "adjacent mechanisms not checked"
declaration today; the missing declarations are written here.

### 5.1 Phase 3 recall filter (`_filter_recall_only_know`)

**Location:** `phase3_kud.py:28–66`. Public name
`is_recall_only_know_content` (used also by Phase 4 at
phase4_lt_generation.py:420).

**What it checks.** Walks `kud.know[]`; drops items whose
`content` matches any of nine recall-patterns
(phase3_kud.py:28–38 — `dates of`, `key dates`, `key events`,
`names of`, `definitions of`, `key events and dates`, `historical
dates`, `factual recall`, `vocabulary`) AND does not contain a
"substantive" verb (phase3_kud.py:40–44 —
`analyse/evaluate/interpret/compare/apply/construct/inquiry/
framework/perspective/significance/continuity/change/cause/
consequence/synthes/argu/judg`). Counts drops via
`recall_filtered_count` in state and in the run report.

**What it does NOT check — adjacent mechanisms:**

- **Only the `know` bucket.** `understand`, `do_skills`,
  `do_dispositions` are never scanned. A rote-recall item smuggled
  into `do_skills` (e.g. *"Recall prime factorisation steps"*)
  passes.
- **English-only regexes.** None of the nine patterns matches
  Hungarian, French, Spanish, etc. A Hungarian source could place
  recall items into `know` under Hungarian phrasing and none would
  trip the filter. The felvételi source is Hungarian; the KUD was
  generated in English, so the filter happened to apply — but the
  dependency is accidental.
- **Consolidation / cardinality.** The filter cannot detect that 32
  source bullets have collapsed to 14 items. It is item-by-item.
- **Source-faithfulness.** The filter never reads the source. It
  cannot detect that a KUD item's content is fabricated (e.g.
  felvételi LT #0 introduced "factorial notation" which is not in
  the source — REVIEW.md §2). It can only decide whether the KUD
  item's text *looks* recall-only.
- **Coverage.** The filter cannot detect that a strand has been
  dropped from the source (e.g. "triangle congruence", "word
  problems", "axial vs central reflection distinguished" — all
  missing from the felvételi KUD per REVIEW.md §3).
- **Domain relevance.** The filter cannot detect that a recall
  item for one subject has been imported into a different subject
  (cross-source prompt leakage per VALIDITY.md's pre-mortem).

### 5.2 Phase 4 LT surface-form validator (`_validate_lt`)

**Location:** `phase4_lt_generation.py:235–273`.

**What it checks.** Per-LT string-level checks: missing statement,
format prefix (`I can ` / no `I can ` / no first-person per fmt),
`EXCEEDS_WORD_LIMIT` (>25 words), `POSSIBLE_COMPOUND` (" and "
between two verb-like halves from `VERB_HINTS`),
`EMBEDDED_EXAMPLE` (parentheses), `DISPOSITION_RUBRIC_ERROR`
(rubric vocabulary in a Type-3 LT), `COMPOUND_TYPE` (decided
upstream in `_lt_type_and_compound`).

**What it does NOT check — adjacent mechanisms:**

- **No regeneration.** Flags are attached; the LT ships regardless
  (see Question 3).
- **Source-faithfulness / no-invention.** The validator never
  inspects `raw_curriculum`. Nothing prevents an LT from inventing
  content (felvételi LT #0 — factorial notation).
- **Semantic compound-ness.** `POSSIBLE_COMPOUND` is lexical — it
  tests "verb ... and ... verb" via a hard-coded 14-verb hint list
  (phase4_lt_generation.py:94–110). A compound joined by a comma,
  semicolon, "while", or "as well as" will pass. A compound in
  non-English wording will pass.
- **Type correctness.** `_validate_lt` accepts the assigned type as
  given; it does not re-check whether the LT's content actually
  matches that type. A dispositional behaviour dressed as a T1
  rubric-criterion LT slips through.
- **Observable verb quality.** The `LT_ACTION_RULES_ICAN` prompt
  instructs "no demonstrate understanding" (phase4_lt_generation.py:48–61),
  but `_validate_lt` does not enforce it. An LT starting
  "I can demonstrate understanding of..." would pass the validator
  silently.
- **English-only rubric terms.** `RUBRIC_TERMS` (phase4_lt_generation.py:81–92)
  are English.
- **Topical drift.** A Type-3 LT about maths persistence that drifts
  to classroom behaviour would not trip any flag.

### 5.3 Phase 4 HE disposition cosine de-dup

**Location:** `phase4_lt_generation.py:119–140` (helpers),
applied at `phase4_lt_generation.py:371` (threshold 0.92).

**What it checks.** Only for `higher_ed_syllabus` runs. Token-
frequency cosine similarity of each inferred HE disposition
statement against the existing LT corpus; if `max >= 0.92`, skip.

**What it does NOT check — adjacent mechanisms:**

- **Non-HE runs have no cross-LT duplicate check in Phase 4.** The
  Phase 5 duplicate-name check (`_flag_duplicate_lt_names`,
  phase5_formatting.py:353–367) runs at the structured-table level,
  not the raw-LT level.
- **Token-frequency only.** No embeddings; synonyms ("persist" vs
  "persevere") do not register as near-duplicates.
- **Intra-non-HE.** A fabricated duplicate T1 LT in a K-12 run
  would pass the full pipeline without dedup.
- **Cross-strand duplicates** — the felvételi run produced
  `EXCEEDS_WORD_LIMIT=0` but LT rephrasings across strands are
  never checked for near-duplicate meaning.

### 5.4 Phase 5 strand-similarity router (`map_lt_to_strand_label`)

**Location:** `phase5_formatting.py:127–158` (with supporting
`_competency_relevance_score` at phase5_formatting.py:70–86 and
`_assignable_strands_for_type` at phase5_formatting.py:94–109).

**What it checks.** Chooses a strand label for each LT. Candidate
strands are first filtered by lane matching the LT's type; within
that set, token-overlap similarity between
LT statement+kud_source and strand label is used as tiebreaker.
Flags `COMPETENCY_MAPPING_UNCERTAIN` when lane relaxation is needed
or top-two scores are within 0.05 above 0.35.

**What it does NOT check — adjacent mechanisms:**

- **Domain-semantic correctness.** Token overlap between
  *"I can classify decimal representations..."* and strand label
  *"Number Systems and Operations"* is near zero — no word overlap.
  The felvételi run routed "Decimal Classification" and "Exponent
  Rules" to *"Geometric Properties and Measurements"* as the first
  hierarchical-lane strand (REVIEW.md §4 point 3).
- **No embeddings / no domain-keyword index.** Strand labels are
  the only comparison target; the router has no per-strand keyword
  list.
- **Lane-relaxed fallbacks silently succeed** if any lane match
  exists; `COMPETENCY_MAPPING_UNCERTAIN` is attached but the LT
  is still routed.
- **English-only token splitting.** Non-English LTs would not
  score against English strand labels.

### 5.5 Phase 5 level-statement drift flags (`_level_statement_validation_flags`)

**Location:** `phase5_formatting.py:161–227`.

**What it checks.** Two hard-coded regex families flag drift in
per-level cells: `_HISTORY_CIVIC_DRIFT` (history-subject only:
"school council", "classroom rules", "good citizen", etc.),
`_T2_ANALYTICAL_IN_T3`, `_T2_LIKE_FOR_T1`, `_T3_LIKE_FOR_T2`.
Emits `LEVEL_STATEMENT_DOMAIN_DRIFT` and
`LEVEL_STATEMENT_TYPE_DRIFT`.

**What it does NOT check — adjacent mechanisms:**

- **Domain drift is history-only.** `_statement_domain_drift`
  (phase5_formatting.py:189–194) returns `False` for any non-
  history subject. Maths, science, languages, humanities are not
  covered. A maths LT that drifts into classroom civics at a Y6
  level would not flag.
- **Type drift regexes are history-coded.** All patterns use
  history vocabulary (source reliability, historical source,
  perspective of historical sources). Maths type drift (e.g., a
  T3 disposition rewritten as T1 procedural) would not trip.
- **No source check.** Drift detection is wording-only.
- **Pattern coverage is narrow.** Each type-drift regex is a
  single hand-written pattern; broad drift classes are uncovered.

### 5.6 Phase 5 duplicate LT name flag (`_flag_duplicate_lt_names`)

**Location:** `phase5_formatting.py:353–367`.

**What it checks.** Exact-match duplicates on `lt_name` across the
structured rows; attaches `DUPLICATE_LT_NAME`.

**What it does NOT check — adjacent mechanisms:**

- **Case-insensitive / whitespace-normalised variants** (e.g.
  "Solve equations" vs "solve  equations" — `str.strip()` is applied
  but no case fold).
- **Near-duplicate names** ("Apply exponent laws" vs "Apply
  exponent rules").
- **Duplicate `lt_definition`s with differing `lt_name`s** — the
  definition body is not hashed.

### 5.7 Phase 1 multi-level-progression heuristic (`_document_indicates_multi_level_progression`)

**Location:** `phase1_ingestion.py:314–356`.

**What it checks.** English-language regex for "Key Stage", "KS1–4",
"Year N to Year M", "Grade K–12", "F–10", "Stage 1 / Stage 2". If
matched, overrides Haiku's `level_model` to
`multi_level_progression`.

**What it does NOT check — adjacent mechanisms:**

- **Non-English curriculum terminology.** Hungarian `évfolyam`,
  French `cycle`, German `Klasse / Stufe`, Italian `anno /
  triennio` — none are in the pattern set. For the felvételi run
  the heuristic did not fire; the profile was stored as
  `single_intended_level`, which happened to be correct for the
  topic list but is not robust for Hungarian-language docs that
  do span stages.
- **Implicit progression via section headings.**

### 5.8 Phase 1 scoped-content adequacy (`_scoped_content_ok`)

**Location:** `phase1_ingestion.py:127–185`.

**What it checks.** Per document family, whether the Haiku-scoped
extract contains any of an English cue list (e.g.
`"assessment objective"`, `"mark scheme"`, `"specification"` for
exam specs; `"key stage"`, `"programme of study"` for national
frameworks).

**What it does NOT check — adjacent mechanisms:**

- **Non-English cues.** For the felvételi run this filter failed
  (run report: *"phase1: scoped extraction returned empty or unfound
  — using profile-aware fallback slice"*). Hungarian `vizsga`,
  `követelmény`, `téma` are not in any cue list.
- **Longer-than-12k docs silently bypass the cue check**
  (phase1_ingestion.py:136–137 — `if len(t) >= 12000: return True`).

---

## Summary

The diagnosis points to **Shape C — Phase 2 / profile-conditional
branching** as best supported.

1. **Shape A (prompt-only fix) is insufficient.** There is no
   consolidation instruction in Phase 3's prompts to rewrite —
   only an "align with architecture" clause. Rewriting it toward
   "do not consolidate" still leaves Phase 3 working from a
   six-strand summary with no per-bullet signal, and still
   routes through an external MCP tool whose aggregation
   behaviour is out of this repo's control. Prompt-only will move
   the output some, but cannot overcome the signal bottleneck.
2. **Shape B (phase redesign) is heavier than the evidence
   demands.** The existing phase topology (Phase 1 → 2 → 3 → 4 →
   5) and the KUD data model already admit any cardinality
   (Q1 — structural fan-out is unbounded). The redesign that would
   be required is only at the entry of Phase 3, not the phase as
   a whole.
3. **Shape C is where the evidence concentrates.** The signal
   needed to branch — `curriculum_profile.scoping_strategy=
   full_document`, `assessment_signals.format="10 short tasks..."`,
   `document_family="exam_specification"` with `has_mark_scheme=false`
   and `has_command_words=false` — is already on state, already
   written to the `curriculum_profile_v1.json` artefact, and
   already read by Phase 4 and Phase 5, but **never read by
   Phase 3 or Phase 2 after ingestion**. A branch at Phase 3 entry
   that detects a bare-bullet exam spec and either (a) switches
   prompt/tool to a per-bullet mode, or (b) pre-chunks the input
   along strand lines before calling the MCP, is the minimum
   change that this diagnosis's evidence supports.

The factorial-injection bug (Q5.1 / REVIEW §2), the
flag-and-ship behaviour (Q3), and the geometry-coarseness
(REVIEW §3–4) are **three faces of the same missing primitive: a
source-faithfulness / source-coverage judge that neither Phase 3
nor Phase 4 currently calls.** Closing the VALIDITY.md foundation-
moment-1 gates (Q4 items a–c) and using those judges inside Phase
3/4 would address the content-quality half of the problem that a
Shape C routing change would not reach.
