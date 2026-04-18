# Phase 1 scoping nondeterminism — diagnosis (2026-04-18)

Read-only diagnostic pass to identify the cause(s) of variance in Phase 1's
`source_bullets` output across runs of the same Ontario source document. No
code edits in this document; a separate Session 3b commit applies the fix.

## Observed variance

Two Ontario `source_bullets_v1.json` artefacts produced from the same URL
(`SocialStudiesHistoryGeography-AODA.pdf`), same config (Grade 7, History,
Ontario), same code at head of main:

| Run                                | Bullets | marker | numbered | topic |
|------------------------------------|--------:|-------:|---------:|------:|
| `outputs/ontario_grade7_history/`  | **237** | 186    | 50       | 1     |
| Session 3a snapshot (today)        | **5**   | 5      | 0        | 0     |

The numbered-outcome collapse (50 → 0) is diagnostic. Ontario's specific
expectations are `A1.1 describe...`, `A1.2 analyse...`, etc. — a textual
form the rule-based extractor matches deterministically whenever those lines
appear verbatim (`source_bullets.py:91–94` regex). Their absence from the
Session 3a artefact means the input to `extract_source_bullets` no longer
contained the verbatim `A1.N <lowercase-verb>` lines; they had been rewritten,
summarised, or omitted upstream.

That upstream step is Haiku's scope extractor — the only component between
PDF text and `extract_source_bullets` that rewrites content.

## Pipeline walk — Phase 1 extraction order

`phase1_ingestion.py:437–682` (`phase1_ingestion`) runs in this order:

1. Fetch bytes (`_fetch_bytes`, deterministic).
2. Extract text (`_extract_pdf_text` / `_extract_html_text`, deterministic).
3. **Haiku classification** (`_haiku_classify_curriculum`,
   `phase1_ingestion.py:360–401`) — emits `document_family`,
   `level_model`, `scoping_strategy`, `assessment_signals`. Stochastic.
4. Multi-level-progression heuristic override (`_document_indicates_multi_level_progression`,
   regex-only, deterministic).
5. Profile merge with config defaults (deterministic).
6. Candidate-window selection (`_scope_candidate_windows`,
   `phase1_ingestion.py:196–229`, deterministic given profile).
7. **Haiku scope extraction** (`_haiku_extract_scoped_curriculum`,
   `phase1_ingestion.py:404–434`) per window; `_scoped_content_ok` gate
   decides whether each window's output is kept or the next window is
   tried (`phase1_ingestion.py:582–605`). Stochastic.
8. Metadata Haiku pass (non-fatal, does not affect `source_bullets`).
9. **Rule-based `extract_source_bullets`** on `raw_curriculum`
   (`phase1_ingestion.py:665`). Deterministic given input string.

Steps 3 and 7 are the only stochastic stages. Step 9 is deterministic, so
its output variance is fully explained by variance in the string fed to it,
which is the output of step 7 (or, when step 7 fails its gate, the output
of `_scope_fallback_slice` which is deterministic).

## Stochastic-call configuration

All Haiku calls in Phase 1 route through `haiku_stream_text`
(`_anthropic.py:103–151`). The streaming kwargs are literally:

```python
async with client.messages.stream(
    model=model,
    max_tokens=max_tokens,
    system=system,
    messages=[{"role": "user", "content": user_blocks}],
) as stream:
```

**No `temperature` is passed.** The Anthropic Messages API defaults
`temperature` to `1.0` when the field is omitted. There is no
`top_p`, `top_k`, or `seed` argument either. Every Haiku call in Phase 1
runs at the API's maximum-entropy default.

This affects:

- `phase1_haiku_classify` (`_anthropic.py`, `label="phase1_haiku_classify"`)
  — `max_tokens=1024`, can flip `document_family`, `scoping_strategy`,
  `assessment_signals` across runs. If `document_family` flips between
  runs, the system prompt chosen in `_scope_system_prompt`
  (`phase1_ingestion.py:261–312`) also flips, which changes the scope
  extraction's instructions.
- `phase1_haiku_scope_extract` (`_anthropic.py`, `label="phase1_haiku_scope_extract"`)
  — `max_tokens=16384`, instructed to "extract text" and "preserve
  headings, numbering, and assessment language where present"
  (`phase1_ingestion.py:268–269`). At temperature 1.0 the model can
  paraphrase instead of copy, drop numbered-outcome prefixes, summarise
  bullet blocks into prose, or truncate to a short digest even when
  the window contains the full grade 7 history section.
- `phase1_haiku_metadata` — downstream only; does not touch
  `raw_curriculum`, irrelevant to bullet count.

## Candidate-window loop interaction

`phase1_ingestion.py:582–605`:

```python
for window in windows:
    if not window or len(window.strip()) < 200:
        continue
    candidate = await _haiku_extract_scoped_curriculum(
        window, subject, grade, jurisdiction, profile_dict
    )
    if _scoped_content_ok(candidate, profile_dict):
        scoped = candidate
        break
if scoped:
    raw_curriculum = scoped
else:
    errs.append("phase1: scoped extraction returned empty or unfound — using profile-aware fallback slice")
    raw_curriculum = _scope_fallback_slice(...)
```

`_scoped_content_ok` (`phase1_ingestion.py:128–186`) accepts any candidate
where `len(t) >= 12000`, and otherwise requires at least one family-specific
English cue word. For the Session 3a run the profile was
`national_framework`, cues are
`{"attainment", "programme of study", "expectation", "key stage", "subject content", "aims"}`.
The 6,285-char Session 3a candidate contained the word `expectation`, so
the gate passed on the first window and the loop broke immediately. A
longer Haiku output from the same first window (as in the prior 237-bullet
run) would have passed via the 12k shortcut. Either way the gate does not
control for bullet-count fidelity — only for non-emptiness and cue
presence.

This means the gate does not catch Haiku's under-extraction. A thin but
cue-bearing digest is accepted as equivalent to a faithful full copy.

## Diagnosis

The 47x variance in emitted bullets (237 → 5) between Ontario runs of the
same URL with the same code is explained by the interaction of three
mechanisms, in descending order of contribution:

1. **Haiku scope extractor runs at temperature 1.0** with no seed.
   `haiku_stream_text` omits the `temperature` kwarg
   (`_anthropic.py:117–122`). The scope extractor is instructed to
   "preserve numbering" but at max entropy can instead paraphrase,
   summarise, or drop content. This is the dominant source of variance.
   The disappearance of the 50 `A1.N <verb>` numbered outcomes between
   runs (the deterministic rule-based extractor detects them iff they
   appear verbatim) is consistent only with Haiku having rewritten or
   omitted those lines.
2. **Haiku classifier also runs at temperature 1.0.** If its output
   flips `document_family` or `scoping_strategy` between runs,
   downstream prompt selection (`_scope_system_prompt`) changes the
   scope extractor's instructions, compounding variance. Ontario is
   borderline between `national_framework` and
   `school_scoped_programme` shapes, so this flip is realistic.
3. **`_scoped_content_ok` accepts thin Haiku output.** A 6,285-char
   digest containing one cue word passes the gate; a 50,000-char copy
   also passes. The gate's first-acceptable-window short-circuit does
   not defend against under-extraction. This is not itself a
   nondeterminism source but it lets the nondeterminism cash through.

## Candidate fixes (for Step 3, not applied here)

- **Shape A — add `temperature=0` to `haiku_stream_text`.** Direct fix
  for (1) and (2). Does not address (3).
- **Shape B — make rule-based extraction primary.** Run
  `extract_source_bullets` on the full text (pre-Haiku) as the source
  of bullets; treat Haiku scope output as a presentation aid only.
  Sidesteps (1), (2), (3) together. Loses Haiku's ability to narrow
  multi-grade documents to the requested grade/subject slice, which is
  load-bearing for Ontario (Grade 7 of an all-grades PDF).
- **Shape C — majority-vote across 3 runs.** Overkill.

Recommendation: apply Shape A first; re-run; measure variance. If Shape A
alone drops variance below the 15% threshold in
`docs/vision/binding-specifications.md`, stop there. If it does not — most
likely because Haiku at temperature 0 still paraphrases numbered outcomes
or still fails the `_scoped_content_ok` gate on shorter runs — escalate
to a hybrid: Shape A + feed `extract_source_bullets` on the
grade/subject-windowed text rather than on the Haiku output. That hybrid
is Shape B-lite and does not require abandoning the scope extractor for
its intended purpose (narrowing the multi-grade PDF).

## Fields referenced

- `phase1_ingestion.py:24` — `_MAX_INPUT_FOR_SCOPE = 320_000`
- `phase1_ingestion.py:25` — `_CLASSIFY_EXCERPT_CHARS = 40_000`
- `phase1_ingestion.py:128–186` — `_scoped_content_ok`
- `phase1_ingestion.py:196–229` — `_scope_candidate_windows`
- `phase1_ingestion.py:261–312` — `_scope_system_prompt`
- `phase1_ingestion.py:360–401` — `_haiku_classify_curriculum`
- `phase1_ingestion.py:404–434` — `_haiku_extract_scoped_curriculum`
- `phase1_ingestion.py:582–605` — candidate-window loop
- `phase1_ingestion.py:665` — `extract_source_bullets(raw_curriculum.strip())`
- `_anthropic.py:103–151` — `haiku_stream_text` (no temperature kwarg)
- `source_bullets.py:91–94` — `_NUMBERED_OUTCOME_RE` (deterministic)
