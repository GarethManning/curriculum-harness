# Binding specifications — Curriculum Harness

This document is the in-repo subset of vision v4.1 that directly binds code. The full vision lives in Gareth's project knowledge. This file contains only the load-bearing specifications that phase implementations, validators, and gates must honour.

## Two-tool architecture

The Curriculum Harness is one of two tools in the pipeline. Upstream, a Constitution Tool (not yet built) takes unstructured source material and produces a curriculum-document-shaped intermediate artefact. Downstream, the Curriculum Harness consumes that artefact and produces KUDs, LTs, and criteria. The split is load-bearing: constitution is judgement-heavy reasoning with human in the loop; translation is mechanical reasoning verified at every phase. The harness never does constitution work; it refuses malformed input rather than inventing content.

## Supported input modes

Two modes. Narrative-prose input is explicitly rejected and routes through the Constitution Tool when it exists.

### Curriculum mode (primary)
Rich curriculum documents: Ontario, AP CED, IB subject guides, Common Core standards, IGCSE syllabuses. Full four-column KUD, full LT set, full pedagogical criterion bank.

### Exam-spec mode (secondary)
Exam specifications: felvételi, GCSE content lists, érettségi specs. Output labelled "Assessed Demonstrations Map" — not a KUD. Populates assessed topics, tested demonstrations, and a demonstration criterion bank. Refuses to produce Understandings, Dispositions, or a pedagogical criterion bank from exam-spec input.

## Numeric thresholds

- **Source-faithfulness matching:** 0.35 (lemma Jaccard + char-4gram, Session 2 matcher). Provisional; recalibrate after three test-corpus runs complete. English-only in v4.1; multilingual upgrade deferred.
- **Classifier confidence:** >=0.80 silent routing; 0.60-0.80 warned routing; <0.60 halts pipeline for human review.
- **Self-consistency variance:** artefact count variance >=15% OR content drift >=20% (lemma-overlap <0.50) flags a phase as unreliable. Sample size 3 minimum; 5 when compute allows.
- **Artefact-count targets (curriculum mode):** KUD 0.8-1.5x source bullets for hierarchical and horizontal domains; KUD 0.8-2.2x source bullets for dispositional domains (PROVISIONAL, 4b-2 revision — see `docs/plans/session-4b-gate-revisions-v1.md`). First real-corpus data from 4b-1 revised the dispositional ceiling from 1.5 to 2.2 provisionally; re-review against next dispositional source. LTs ~1:1 with KUD +/-20%; criteria 2-4 per LT hierarchical / 1-3 per LT horizontal.
- **Artefact-count targets (exam-spec mode):** assessed topics 1:1 with source bullets (strict); tested demonstrations 1:1 with assessed topics; demonstration criteria 1-3 per tested demonstration (upper bound watched).

## Schema versioning

Curriculum Schema uses MAJOR.MINOR.PATCH semantic versioning. Harness accepts current MAJOR and immediately preceding MAJOR. Preceding-MAJOR window closes 90 days after a new MAJOR ships. Every artefact carries the schema version it consumed.

## Human-review workflow

Triggered by: classifier confidence <0.60, self-consistency flag, unresolvable source-faithfulness flag after regeneration.

Reviewer sees: source document, failing phase with triggering artefact, adjacent-mechanism declaration for the relevant judge, plain-English explanation of why the flag fired. Reviewer chooses: override, regenerate with modified prompt, or abort.

Review-load target: fewer than 1 review event per document. Provisional until N>=20 documents processed.

## Provenance commitment

Every artefact emitted by any phase carries a source_provenance pointer to the source bullet(s) supporting it. Artefacts without traceable provenance are rejected at the phase boundary. Each phase's provenance check carries an adjacent-mechanism declaration stating what it does not verify.

## Deferred specifications

Named explicitly so they are not forgotten:
- Multilingual source-faithfulness matcher.
- Generative-frame artefact type for horizontal/dispositional domains.
- Multi-source constitution.
- Provenance pass-through for curriculum documents citing their own sources.
- Schema migration tooling.
- Second criterion-bank pathway for contested horizontal domains.
- Edge weights for tutor-side adaptive item selection.
- Symmetric output-schema discipline for the harness's own emissions.
