# Absence-claim verification log

For every card making a claim about absence in an external framework, the per-batch audit searches the framework's source corpus for the absent topic and certifies absence (or refines the claim if partial overlap exists). This file records the searches.

## Convention

- **Card:** LT × framework
- **Claim:** the specific wording of the absence claim in the card
- **Search terms:** what was queried in the source corpus
- **Source corpus searched:** which files
- **Verdict:** CLEAN (zero source hits), QUALIFIED (some hits — claim refined), or RETRACTED (claim was wrong, card rewritten without absence)

---

## Pilot + Batch 1 absence claims (9 cards)

### LT 4.2 × CfW — "Puberty, contraception and sexual health are not included within CfW's Health and Well-being Area's What Matters statements"
- **Search terms:** puberty, contraception, STI, sexual health
- **Corpora:** source-ps-descriptions.md (H&W AoLE), cfw-what-matters.md, cfw-rse-statutory-principles.md
- **Hits:** "STI" matched as substring of "stimuli" in PS descriptions (false positive). Real STI / sexual health hits exist only in cfw-rse-statutory-principles.md — the separate RSE Code, which the card explicitly names as where this content sits.
- **Verdict:** CLEAN. Card's distinction (H&W What Matters statements vs. separate RSE Code) holds.

### LT 4.2 × CASEL — "CASEL's five competencies don't extend to puberty, sexual health or contraception"
- **Search terms:** puberty, contraception, sexual
- **Corpora:** casel-sel-continuum/source.md, casel-framework-definition.md
- **Hits:** zero
- **Verdict:** CLEAN.

### LT 4.4 × CASEL — "biology and psychology of emotional development sit outside the framework"
- **Search terms:** neuroscience, attachment theory, biology, dopamine, neurobiology
- **Corpora:** casel-sel-continuum/source.md, casel-framework-definition.md
- **Hits:** zero
- **Verdict:** CLEAN.

### LT 7.1 × RSHE — "RSHE doesn't address metacognition"
- **Search terms:** metacognition, metacognitive, patterns in thinking
- **Corpora:** uk-statutory-rshe content.txt, secondary-rshe-2025 content.txt
- **Hits:** zero
- **Verdict:** CLEAN.

### LT 8.1 × CfW — "information verification isn't a named focus"
- **Search terms:** verification, media literacy, fact-check, credibility
- **Corpora:** source-ps-descriptions.md, cfw-what-matters.md, cfw-rse-statutory-principles.md
- **Hits:** zero
- **Verdict:** CLEAN.

### LT 8.1 × CASEL — "Media verification doesn't appear in any of them"
- **Search terms:** verification, media literacy, credibility, fact-check
- **Corpora:** casel-sel-continuum/source.md, casel-framework-definition.md
- **Hits:** zero
- **Verdict:** CLEAN.

### LT 1.3 × RSHE — "Personal identity sits outside that scope" → REFINED
- **Search terms:** personal identity, cultural identity, cultural background, identity
- **Corpora:** uk-statutory-rshe content.txt, secondary-rshe-2025 content.txt
- **Hits:** 1 hit on "identity" — "a strong sense of their own identity, including through developing skills and interests" (Primary, Respectful kind relationships, item 8). One incidental mention as a by-product of self-esteem.
- **Verdict:** QUALIFIED. Card revised to acknowledge: "Identity appears once in primary, as a by-product of self-esteem — 'a strong sense of their own identity' through developing skills and interests — and isn't developed as a curriculum thread."

### LT 2.1 × RSHE — "Attention as a topic doesn't appear; the curriculum has no progression for sustaining focus or designing conditions for it"
- **Search terms:** attention strategies, sustaining attention, focus my attention, concentration
- **Corpora:** uk-statutory-rshe content.txt, secondary-rshe-2025 content.txt
- **Hits:** zero on attention-as-cognitive-resource. The word "attention" appears 8 times in RSHE but exclusively in interpersonal contexts ("pay attention to the needs of others"), in sexual-harassment definitions ("unsolicited sexual attention"), or in medical contexts ("seek medical attention"). None are attention-as-cognitive-strategy.
- **Verdict:** CLEAN. The card's specific claim ("Attention as a topic doesn't appear") accurately distinguishes from the interpersonal/medical uses of the word.

### LT 3.1 × CASEL — "Physical health habits — nutrition, sleep, movement — sit outside this scope"
- **Search terms:** nutrition, sleep, exercise, physical health, movement, diet
- **Corpora:** casel-sel-continuum/source.md, casel-framework-definition.md
- **Hits:** 1 hit on "sleep" — "(e.g., health and wellness, sleep, healthy relationships)" in the CASEL Adults section as a parenthetical example of health-related content. Not a competency element for K-12 students.
- **Verdict:** CLEAN at the framework-design level. The five competencies don't include physical health as their content; the one Adult-section parenthetical doesn't constitute a curriculum specification.

---

---

## Batch 2 absence claims (1 new card)

### LT 4.3 × CfW — "Bullying isn't named within Health and Well-being" → REFINED
- **Search terms:** bullying, bully, harassment, anti-discrimination, discrimination
- **Corpora:** source-ps-descriptions.md (H&W AoLE), cfw-what-matters.md, cfw-rse-statutory-principles.md, cfw-pilot-extracts.md, cfw-four-purposes.md
- **Hits:** 2 hits on "bullying" + 1 hit on "discrimination" — all in `cfw-rse-statutory-principles.md` (the separate RSE Code section), specifically §4 ("help reduce all bullying, including homophobic, biphobic and transphobic bullying") and §7 (Empowerment-safety-respect strand of RSE: "protect learners from all forms of discrimination, violence, abuse and neglect"). Zero hits in the H&W AoLE What Matters statements (the originally-intended scope of the claim).
- **Verdict:** QUALIFIED. Original draft "Bullying as a named topic doesn't appear in CfW" rewritten to "Bullying isn't named within Health and Well-being; it appears in the separate RSE Code as something RSE can help reduce [cfw-rse-statutory-principles §4]." Card now precisely names which scope of CfW lacks bullying-as-named-topic.

---

## Process going forward

For Batch 2 and Batch 3:
- Every card claiming absence runs this search before being committed.
- Results recorded here in the same format.
- If a search returns hits, the card is QUALIFIED (claim refined to acknowledge what's there) or RETRACTED (claim wrong, card rewritten).
- The audit report at the end of each batch lists the new absence-claim verifications.
