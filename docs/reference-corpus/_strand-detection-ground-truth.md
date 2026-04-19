# Strand Detection — Ground Truth

**Purpose:** Hand-curated ground truth for strand detection, committed before the detection module runs. Claude Code makes the ground-truth calls below and commits to them in writing. These entries are used to score precision and recall of the detector.

**Date:** 2026-04-19  
**Session:** 4c-3a

---

## 1. DfE KS3 Maths — Expected: 6 strands

**Source artefact:** `docs/run-snapshots/2026-04-18-session-4a-4-5-dfe-ks3-maths-pdf/content.txt`

### Expected strands

| # | Strand name | Starts at | Basis in source |
|---|-------------|-----------|-----------------|
| 1 | Number | Line 110 | Headed "Number" under "Subject content" |
| 2 | Algebra | Line 150 | Headed "Algebra" under "Subject content" |
| 3 | Ratio, proportion and rates of change | Line 192 | Headed "Ratio, proportion and rates of change" |
| 4 | Geometry and measures | Line 214 | Headed "Geometry and measures" |
| 5 | Probability | Line 256 | Headed "Probability" |
| 6 | Statistics | Line 266 | Headed "Statistics" |

### Rationale

The document has a two-part structure. Pages 3–4 ("Working mathematically") contain cross-cutting process goals: Develop fluency, Reason mathematically, Solve problems. These apply to all strands and are **not strands**. The remainder of the document (pages 5–9) is headed "Subject content" and contains six named content sections. Each section opens with "Pupils should be taught to:" followed by a list of bullet-point content statements. The sections are structurally disjoint — a learner outcome in Number is not repeated in Algebra.

**"Working mathematically"** is a cross-cutting section and must not be detected as a strand. It sets expectations for how pupils engage with all content areas, not a content domain in itself. The DfE document itself places it before "Subject content" and does not label it with "Pupils should be taught to:" in the same structural way.

The build plan names these as "Number, Algebra, Geometry, Statistics, Ratio and Proportion, Probability." This matches the six subject-content sections in the source, with the source using the fuller names "Geometry and measures" and "Ratio, proportion and rates of change." The detector should use the source's own names, not the abbreviated plan names.

---

## 2. NZ Curriculum Social Sciences (Phase 2, Years 4–6) — Expected: 4 strands

**Source artefact:** `docs/run-snapshots/2026-04-18-session-4a-3-nz-curriculum/content.txt`

### Expected strands

| # | Strand name | Basis in source |
|---|-------------|-----------------|
| 1 | History | Top-level section heading; has Knowledge + Practices sub-sections |
| 2 | Civics and Society | Top-level section heading; has Knowledge + Practices sub-sections |
| 3 | Geography | Top-level section heading; has Knowledge + Practices sub-sections |
| 4 | Economic Activity | Top-level section heading; has Knowledge + Practices sub-sections |

### Rationale

The NZ Curriculum Social Sciences Phase 2 page delivers four named top-level divisions. Each division follows an identical structural template: a strand name, then two parallel sub-sections ("Knowledge" and "Practices"), each further divided by year (Year 4, Year 5, Year 6). This repeated structural pattern — same template, same sub-section labels, one per strand — is the primary signal that these are genuine strands rather than sub-topics.

The README for the 4a-3 run snapshot (written at ingestion time) confirms: "NZ Phase 2 curriculum has four strands instead of Ontario's two; Knowledge + Practices substructure rather than overall-expectations + specific-expectations."

**Year-group subdivisions** (Year 4, Year 5, Year 6) within each strand are **not strands** — they are progression steps within a strand. The detector must not confuse these with strand boundaries.

**"New Zealand History"** and **"Global History"** within the History strand are sub-topics, not separate strands. They appear within the History strand and are not given the same top-level structural treatment.

---

## 3. Welsh CfW Health & Wellbeing — Decision: **Single-strand source**

**Source artefact:** `docs/run-snapshots/2026-04-19-session-4a-5-wales-cfw-health-wellbeing-sow/content.txt`

### Decision

**Single-strand. The five "Statements of what matters" are conceptual lenses, not structural content divisions.**

### The five statements (for the record)

1. Developing physical health and well-being has lifelong benefits.
2. How we process and respond to our experiences affects our mental health and emotional well-being.
3. Our decision-making impacts on the quality of our lives and the lives of others.
4. How we engage with social influences shapes who we are and affects our health and well-being.
5. Healthy relationships are fundamental to our well-being.

### Rationale

The five headings in the Welsh CfW H&W source are explicitly labelled "Statements of what matters" — not content domains, strands, or topic areas. This naming is the Welsh Curriculum for Wales framework's own terminology for cross-cutting conceptual principles.

**Why these are not strands:**

1. **No structural parallelism beneath the headings.** DfE KS3 Maths strands each open with "Pupils should be taught to:" followed by a disjoint bullet list. NZ strands each have "Knowledge" and "Practices" sub-sections. The Welsh statements do not share this pattern — they are explanatory paragraphs that describe how the whole Area of Learning supports various conceptual dimensions.

2. **Content is not partitioned.** A lesson on "decision-making around relationships" would legitimately fall under statements 3 (decision-making), 4 (social influences), and 5 (healthy relationships) simultaneously. The content cannot be cleanly divided by statement without repeating or fragmenting it.

3. **The ingested source is already scoped.** The source is "Statements of what matters" for the Health and Well-being AoLE — it does not include separate content sequences per statement. The full CfW framework has elaborations ("What this means in practice" pages) that are statement-specific, but those were not the ingested scope.

4. **No prerequisite structure across statements.** Strands can be run independently through the pipeline. The five Welsh statements cannot — they share a common body of learning content and are better treated as tagging dimensions than as pipeline sub-runs.

**Expected detector output:** `"single_strand"` with rationale citing the "Statements of what matters" label, the lack of structural teaching-point lists beneath each heading, and the cross-cutting nature of the content.

---

## Precision/recall scoring guide

For each source, score the detector as follows:

| Metric | Definition |
|--------|-----------|
| **True positive (TP)** | A detected strand that matches a ground-truth strand name (case-insensitive, allowing reasonable abbreviation) |
| **False positive (FP)** | A detected strand not in ground truth (over-detection) |
| **False negative (FN)** | A ground-truth strand not detected |

Single-strand sources: correct = `single_strand` result; incorrect = any strand split detected.

**Over-detection is worse than under-detection.** A false positive creates a phantom sub-run. A false negative causes a ratio gate halt, which is the current known failure mode and is recoverable. Document both, but flag FPs with higher urgency.
