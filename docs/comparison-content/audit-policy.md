# Comparison-content audit policy

**Purpose.** Define the operational standards the four-check audit suite enforces against the comparison-content corpus (Level 1 essay, Level 2 cards, Level 3 themes, centre-of-gravity briefs). The audit script lives at `scripts/comparison_content_audit.py`.

**Scope.** Any artefact in `docs/comparison-content/` that quotes from a source paragraph captured under `docs/comparison-content/sources/`.

**Status.** Standing infrastructure — the four-check suite runs after every artefact is drafted, before commit. Standards documented here are the compliance bar.

---

## The four checks

1. **Citation resolution.** Every `[slug §N]` tag in an artefact resolves to an existing paragraph ID in `docs/comparison-content/sources/{slug}.md`. Multi-paragraph forms `[slug §N, §M]` resolve every ID.

2. **Quote-to-source substring match.** Every `"…"` quoted span in an artefact is verbatim-present (under the operational definition below) in at least one of the source paragraphs cited within the same citation bracket. A quoted span with no nearby citation is itself a failure.

3. **Absence-claim verification.** Every absence-pattern claim about an external framework (e.g. "doesn't appear in framework Y", "isn't part of", "sits outside") has a corresponding entry in `docs/comparison-content/absence-claims-log.md`. The log records the search terms, the corpora searched, and the verdict (CLEAN / QUALIFIED / RETRACTED). The absence search runs across all captured documents for the framework, not only the primary AoLE/competency document.

4. **Cross-card / cross-theme consistency.** Any quoted phrase appearing in more than one artefact cites the same canonical paragraph ID(s) across all instances, with documented bundle-citations as the only exception (see "Bundle-citation equivalences" below).

---

## Operational definition of verbatim quotation

The substring match in Check 2 applies the following normalisations to both the quote and the source text before comparison. A quote that matches under any combination of these is treated as verbatim.

### Accepted

- **Whitespace normalisation.** Multiple whitespace characters (spaces, tabs, newlines) collapsed to a single space. Surrounding whitespace stripped.
- **Quote character normalisation.** Curly quotes (`"`, `"`, `'`, `'`) treated as their straight ASCII equivalents (`"`, `'`).
- **Ellipsis normalisation.** Unicode ellipsis (`…`) treated as three full stops (`...`).
- **First-letter case difference at start of quote.** A card may lowercase the first letter of a source quote when the quote is integrated mid-sentence into the card prose. This is standard editorial practice. Mid-quote case differences are not accepted (see "Not accepted").
- **Truncation up to natural sentence boundary.** A quote may truncate the source mid-clause at a natural punctuation boundary (comma, semicolon, full stop). Substring match accepts this.
- **Mid-quote ellipsis-elision with marker.** A card may omit intervening source text mid-quote *only* when the omission is marked with `…` or `...`. The audit splits the quote on the ellipsis marker and requires each segment to appear in the source in order. The marker is required — unmarked elision is treated as paraphrase regardless of how short or innocuous the omitted material seems (this includes parentheticals such as `(interests)` and qualifying clauses such as `, where appropriate, I can`).
- **American → British verb-ending anglicisation.** Card prose is consistently anglicised (British English). Source verbs ending in `-ize`, `-izing`, `-ized`, `-ization`, `-yze`, `-yzing`, `-yzed` may be matched against their British equivalents (`-ise`, etc.). Anglicisation is scoped to verb suffixes only — American noun spellings (e.g. `behaviors`, `colors`) are preserved verbatim from source. Source-language preservation is the default; verb anglicisation is the only spelling override.

### Not accepted

- **Verb-form changes** (e.g. `notice` → `noticing`, `pay` → `paying`, `use` → `using`) anywhere in the quote. Treated as paraphrase, not editorial integration.
- **Pronoun strips that change meaning** (e.g. removing "I can" from a first-person source statement and rendering it as a gerund without first-person framing).
- **Mid-quote case changes** away from the start. The first-letter override is the only case tolerance; case differences elsewhere indicate paraphrase.
- **Unmarked mid-quote elision.** If source text is omitted mid-quote, the omission must be marked with `…` or `...`.
- **Prefix strips that remove framework-context.** E.g. removing the bolded competency-name prefix is acceptable; removing context that disambiguated which competency or grade band the source statement belongs to is not.
- **Paraphrase presented as quote.** Any change to the source text beyond the accepted normalisations.
- **Section-header quoting.** Section headers (e.g. `## Secondary — Respectful relationships`) are structural metadata about how the source document is organised, not paragraph content the source statutorily commits to. They may not be enclosed in quote marks as if they were source paragraph text. Cards that need to refer to a section name use it in card prose without quote marks, with the citation pointing to the relevant `§N` paragraph(s) under that section.

The four-check audit suite enforces this definition. It does not redefine it. Changes to the definition require a deliberate update to this document and an explanation of the reason.

---

## Bundle-citation equivalences

When a source corpus contains the same competency text verbatim under more than one paragraph ID — typically because the competency reappears across grade bands — citations to either paragraph are acceptable cross-artefact, and Check 4 treats them as consistent. New bundle-citation equivalences are added to `DOCUMENTED_BUNDLE_EQUIVALENCES` in the audit script and listed below.

### Current equivalences

- **CASEL §22 ≡ §6 — `Practice various coping skills to process thoughts and manage stressful situations`.** This phrase appears verbatim in both `casel-pilot-extracts.md §6` (Grade 6–8 Self-Management) and `casel-pilot-extracts.md §22` (Grade 11–12 Self-Management). Either citation is acceptable when this phrase appears.

---

## Absence-claim discipline

Per Check 3, every section that contains absence-pattern language must have a corresponding entry in `absence-claims-log.md`. The audit detects absence patterns via the regex set in `ABSENCE_PATTERNS`. The expected key in the log is `LT N.M × {framework}`.

When an absence-claim section appears under an existing log entry but with refined wording, either (a) link the refined claim to the existing entry by adjusting the entry to cover both wordings, or (b) add a new sub-entry below the existing one. Empty log entries for absence sections that exist in the corpus are a Check 3 failure.

---

## Process

1. Run the audit before any commit that touches `docs/comparison-content/`.
2. Audit must report `OVERALL: PASS` before commit. Failure is a hard block.
3. New themes, cards, or essay revisions are drafted under the same standards as existing artefacts. The audit's compliance bar is identical for first-draft and revision.
4. The audit script lives at `scripts/comparison_content_audit.py`. Run with `--scope all` to cover every artefact, or `--scope themes` / `--scope cards` for narrower scope.

---

## Change log

- **2026-04-25.** Initial version. Drafted alongside Stop 5 baseline audit. Captures the operational definition of verbatim quotation as accepted by 14 prior panel reviews of the existing 63-card corpus, plus the bundle-citation exception introduced in Batch 3.
