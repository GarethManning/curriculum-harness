# Ontario 937-bullet classification — diagnosis (2026-04-18, Session 3d)

Read-only diagnostic pass. Classifies every bullet in
`outputs/ontario-2026-04-18-session-3c-e2e/ontario_session3c_e2e_source_bullets_v1.json`
by semantic category so the coverage gate denominator can be calibrated.
No code edits in this document; Session 3d Steps 2–3 apply the
bullet-type tagging and coverage-gate weighting.

## Dataset

- Source run: `outputs/ontario-2026-04-18-session-3c-e2e/` (Session 3c
  end-to-end, Phase 1 v4.1 post-nondeterminism fix).
- Total bullets: **937**.
- Detector mix (from `source_bullets.py`'s three extractors):
  - `marker_bullet` — 510
  - `topic_statement` — 394
  - `numbered_outcome` — 33
- Line-position distribution of bullets:
  - lines 41–7999 (document front-matter / framework chapters): ~674
  - lines 8000–8999 (pre-Grade-1 inquiry/process sections + early Grade 1): ~98
  - lines 9000–9823 (Grade 1 specific expectations + adjacent bullets): ~173
- `numbered_outcome` bullets (33) all fall in line band 8771–9802 and
  carry codes `A1.1`–`B3.8`. All are Grade 1 outcomes; no Grade 7
  numbered outcomes are present in the extracted text. The Phase 1
  scoped slice for this Grade 7 run captured the document's
  introduction through the Grade 1 specific expectations but did not
  reach the Grade 7 History section.

## Proposed bullet-type enum

Session 3d binds the following enum in the source-bullet schema:

| Value                   | Coverage-gate role     |
|-------------------------|------------------------|
| `specific_expectation`  | coverage-relevant      |
| `overall_expectation`   | coverage-relevant      |
| `sample_question`       | illustrative, excluded |
| `teacher_prompt`        | illustrative, excluded |
| `cross_grade`           | extraction error       |
| `front_matter`          | excluded by default    |
| `other`                 | excluded by default    |

## Classification heuristics (Ontario-shape)

Applied in order; first match wins.

1. **`sample_question`** — bullet text ends with `?`. Signal: sample
   questions posed to students or teachers.
2. **`teacher_prompt`** — bullet text begins with `e.g.`, `e.g `,
   `(e.g.`, or `for example`. Signal: illustrative parenthetical.
3. **`specific_expectation`** — bullet was captured by the
   `numbered_outcome` detector (line starts with `A1.1 describe ...`,
   `1. solve ...`, etc.). Structural signal regardless of grade.
4. **`cross_grade`** — bullet text contains `(Grade N` where N is not
   the target grade (7 for this run). Caught on Ontario's
   sample-questions-cross-referenced-to-grade pattern
   (`... (Grade 2, A3.4)`).
5. **`front_matter`** — bullet's `source_location` "under: HEADER" text
   matches one of the known front-matter header tokens (Version
   history, the achievement chart, mathematical literacy, students will
   learn skills to, etc.), OR the bullet's line number is < 8000
   (before the Grade 1 section header in this PDF's line layout).
6. **`other`** — default.

## Counts per category (Ontario Session 3c, 937 bullets)

| Category               | Count | % of 937 |
|------------------------|------:|---------:|
| `front_matter`         | 676   | 72.1 %   |
| `other`                | 181   | 19.3 %   |
| `sample_question`      |  38   |  4.1 %   |
| `specific_expectation` |  33   |  3.5 %   |
| `cross_grade`          |   9   |  1.0 %   |
| `teacher_prompt`       |   0   |  0.0 %   |
| `overall_expectation`  |   0   |  0.0 %   |

Coverage-relevant bullets (specific_expectation + overall_expectation)
total: **33 of 937 (3.5 %)**. These 33 are all Grade 1 specific
expectations; zero of them are at the target Grade 7 grain.

## Representative examples

### `specific_expectation` (33)

All Grade 1, from the Social Studies Grades 1–6 section. Caught by the
`numbered_outcome` detector.

- `A1.1 describe how and why a person's roles, relationships, and responsibilities, in relation to others and …`
- `A2.1 formulate questions to guide investigations into some aspects of the interrelationship between …`
- `B3.5 demonstrate an understanding of the basic elements of a map (e.g., title, symbols in the legend …`
- `B2.3 analyse maps, and construct simple maps using appropriate elements, as part of their …`
- `B3.8 identify some of the services in the community for which the government and/or community is …`

### `overall_expectation` (0)

No bullets matched the heuristic. Ontario's overall expectations
("A1. Application: Students will …") appear as section headers in the
PDF, not as detector-visible bullet lines.

### `sample_question` (38)

Questions posed to students/teachers; excluded from coverage gate.

- `What role does an Elder, Knowledge Holder, or Métis Senator play in your community?`
- `In what ways might your responsibilities at home, or to the land, change as you get older?`
- `Who were the parties to the Treaty of Niagara or the 1760 Treaty of Peace and Friendship?`
- `Do all students have equitable access to the tools they need to complete the tasks being set?`
- `How would you describe the park nearby? What makes a park a park?`

### `teacher_prompt` (0)

Ontario does not prefix illustrative examples with `e.g.` at line
start; they appear inline (e.g., `describe … (e.g., the birth of a
sibling …)`). The heuristic misses the inline case by design — those
are embedded in specific_expectation bullets, not separate bullets.

### `cross_grade` (9)

Sample questions cross-referenced to non-target grades.

- `What are some of the big celebrations in your family during the year? (Grade 2, A3.4)`
- `How do we determine the importance of certain developments or events? (Grade 6, …`
- `Why don't farmers in Ontario grow bananas or pineapples? (Grade 2, B1.2)`
- `What makes a region a region? (Grade 4, Overview)`
- `What similarities have you found in the housing of people who live in cold regions? (Grade 2, …`

### `front_matter` (676)

Framework / preamble / cross-cutting guidance from the PDF's first
~8000 lines, plus bullets explicitly under known front-matter headers.

- `the Program Planning and Assessment and Evaluation sections of the Curriculum and Resources` (line 41)
- `the 2023 curriculum policy focused on learning in Grades 1 to 3 and Grade 6 social studies.` (line 51, under `website`)
- `All students can succeed.` (line 519, "Beliefs" list)
- `Fairness is not sameness.` (line 528, "Beliefs")
- `knowledge of content (e.g., facts, terms, definitions)` (line 7378, "The achievement chart categories")

### `other` (181)

Fragments and inquiry-process content lines that don't match any
specific heuristic. Most are continuation lines or context bullets
from the Grade 1 Social Studies inquiry-process sections
(lines 8000–9800).

- `synthesize evidence and information, and make informed, critical judgements based on that` (line 8027)
- `analyse data, evidence, and information, applying the relevant concepts of geographic` (line 8246)
- `to help them determine which key concept (or concepts) of geographic thinking is relevant to` (line 8226)

## Which detectors over-extract?

- `topic_statement` (394) is the biggest contributor to front-matter
  noise. Any block of short-ish period-terminating lines following a
  colon-terminated header triggers it, and the PDF's front-matter is
  full of colon-terminated prose headers (`as follows:`, `In this
  diagram:`, `The student:`, etc.) whose subsequent lines are just
  prose wraps, not content bullets. 394/937 = 42 % of the corpus.
- `marker_bullet` (510) captures genuine bullets but has no way to
  distinguish content bullets from sample-question or beliefs-list
  bullets. Every bulleted line in the framework section is emitted as
  a bullet.
- `numbered_outcome` (33) does what it should. It's the cleanest
  detector and captured the Grade 1 specific expectations exactly.

The over-extraction is not a detector bug — it's a scope problem. The
Phase 1 scoped slice contains the full front-matter and the Grade 1
section. The detectors extract faithfully from what they're given.

## Heuristic signals that separate coverage-relevant from illustrative

Strong, easy:

- `?` terminator → sample question.
- `(Grade N)` tag where N ≠ target → cross-grade.
- `numbered_outcome` detector fires → specific expectation
  (structurally).
- Bullet's immediate header contains known front-matter phrase
  (Version history, achievement chart, …) → front matter.

Weak, curriculum-specific:

- Line-position proxy ("line < 8000 in this PDF's layout = front
  matter") is Ontario-file-specific and will not transfer to other
  sources without recalibration.
- Overall-expectation detection requires reading section headers, not
  bullets. Phase 1's current schema carries only the immediate
  "under: HEADER" for topic_statement and nothing for marker_bullet /
  numbered_outcome.

## Root-cause observation (not in scope for Steps 2–3)

The 937-bullet corpus is dominated by front-matter because Phase 1's
Haiku scope extractor, even at `temperature=0`, failed to narrow the
PDF to the Grade 7 History section. The extracted text is the full
document up to Grade 1's specific expectations. Zero bullets are Grade
7 specific expectations.

Session 3d's calibration (bullet-type weighting) will correctly reject
the 676 front-matter + 181 other + 38 sample-question + 9 cross-grade
bullets from the coverage denominator, leaving 33 specific-expectation
bullets. Those 33 are Grade 1, not Grade 7, so the Phase 4 LTs (which
are at Grade 7 grain) will still not trace to them.

Post-calibration the coverage gate will therefore report ~0 % coverage
against a 33-bullet denominator — a clean signal that the scoping
problem is upstream of the coverage gate, not a noise problem in the
gate itself. Fixing Phase 1 scoping is a separate session.

## Adjacent-mechanism declaration

The bullet classification as specified does NOT:

- Verify Grade 7 content is actually at Grade 7 grain. A bullet tagged
  `cross_grade` is known-wrong; a bullet tagged `specific_expectation`
  may still be at Grade 1 or 8 grain.
- Distinguish illustrative sample questions (which show what teachers
  might ask) from prompt-style inquiry questions (which students ask
  as part of work). Both end with `?` and tag as `sample_question`.
- Detect inline `e.g.` examples that are part of a specific_expectation
  bullet. Those are correctly kept inside the specific_expectation and
  not split out.
- Detect overall_expectations. Ontario's overall expectations live in
  section headers that the Phase 1 extractors don't emit.
- Generalise beyond Ontario-shape documents. AP CED, IB, UK NC, and
  felvételi PDFs will need their own heuristic recalibration.
- Weight bullets by importance within their type. All 33 Grade 1
  specific_expectations count equally even though A2.1 "formulate
  questions" is broader than A3.5 "treat others with respect".
