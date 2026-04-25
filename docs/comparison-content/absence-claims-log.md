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

---

## Batch 3 absence claims (11 cards)

### LT 5.2 × RSHE — "doesn't develop community engagement as a sustained curriculum thread" → QUALIFIED
- **Search terms:** community, civic, volunteer, service, citizenship, engagement, participation
- **Corpora:** rshe-pilot-extracts.md, rshe-foreword.md, rshe-strand-introductions.md
- **Hits:** §11 lists "community participation and volunteering or acts of kindness" among the ingredients of mental wellbeing in the secondary mental-wellbeing topic; §1 foreword references generic "moral, social, mental and physical development". Zero hits on civic/community engagement as a developmental thread or curriculum strand.
- **Verdict:** QUALIFIED. Card explicitly names the §11 mention ("RSHE lists 'community participation and volunteering or acts of kindness' among the ingredients of mental wellbeing"), then qualifies the absence to the "as a sustained curriculum thread" scope.

### LT 6.1 × RSHE — "doesn't develop neuroscience vocabulary at mechanism level" → QUALIFIED
- **Search terms:** brain, amygdala, cortex, neuroscience, neural, dopamine, cortisol, HPA, neuroplasticity, mechanism
- **Corpora:** rshe-pilot-extracts.md, rshe-foreword.md, rshe-strand-introductions.md
- **Hits:** §14 secondary "the facts about puberty, the changing adolescent body, including brain development". Zero hits on amygdala / cortex / dopamine / cortisol / HPA / neuroplasticity. Zero hits on mechanism-level neuroscience vocabulary.
- **Verdict:** QUALIFIED. Card opens with the RSHE content ("RSHE addresses mental wellbeing and the changing adolescent body … 'the facts about puberty, the changing adolescent body, including brain development'"), then locates REAL's addition at vocabulary and mechanism level rather than asserting bare absence.

### LT 6.1 × CfW — "doesn't develop neuroscience vocabulary at mechanism level" → CLEAN
- **Search terms:** brain, amygdala, cortex, neuroscience, neural, dopamine, cortisol, HPA, neuroplasticity, mechanism
- **Corpora:** cfw-pilot-extracts.md, cfw-what-matters.md, cfw-four-purposes.md, cfw-rse-statutory-principles.md
- **Hits:** zero across all four corpora.
- **Verdict:** CLEAN. WM2 and the Four Purposes use plain emotional-regulation language; no neuroscience vocabulary appears.

### LT 6.1 × CASEL — "doesn't develop neuroscience vocabulary at mechanism level" → CLEAN
- **Search terms:** brain, amygdala, cortex, neuroscience, neural, dopamine, cortisol, HPA, neuroplasticity, mechanism
- **Corpora:** casel-pilot-extracts.md, casel-framework-definition.md, casel-equity-transformative-sel.md
- **Hits:** zero across all three corpora.
- **Verdict:** CLEAN. Self-Management at upper bands handles coping behaviour; no neuroscience vocabulary appears.

### LT 6.2 × RSHE — "doesn't develop a sustained health-information-literacy thread" → QUALIFIED
- **Search terms:** evidence, evaluate, research, study, trial, systematic review, RCT, evidence hierarchy, source, claim, critically
- **Corpora:** rshe-pilot-extracts.md, rshe-foreword.md, rshe-strand-introductions.md
- **Hits:** §8 primary "how to critically evaluate their online relationships and sources of information"; §18 secondary signposts "towards medically accurate online information about sexual and reproductive health to support contraceptive decision-making". Zero hits on evidence hierarchy / RCT / systematic review / critical appraisal as curriculum content.
- **Verdict:** QUALIFIED. Card names both RSHE touchpoints (§8, §18), then locates REAL's addition as the "sustained evidence-evaluation thread" — evidence types, hierarchy, reading meta-analyses — not asserting bare absence.

### LT 6.2 × CfW — "doesn't develop health-specific information literacy" → QUALIFIED
- **Search terms:** evidence, evaluate, research, study, trial, systematic review, RCT, evidence hierarchy, source, claim, critically, health information
- **Corpora:** cfw-pilot-extracts.md, cfw-what-matters.md, cfw-four-purposes.md
- **Hits:** WM3 PS4 §10 "research, examine and evaluate a range of evidence to make considered and informed decisions"; PS5 §13 "critically evaluate factors and implications, including risks". Purpose 1 §4 "use digital technologies creatively to communicate, find and analyse information". All generic decision-making, none health-specific or with an evidence hierarchy.
- **Verdict:** QUALIFIED. Card describes the WM3 generic-evaluation content (PS4 §10, PS5 §13), then narrows REAL's contribution to "health information specifically and adds an explicit evidence hierarchy".

### LT 6.2 × CASEL — "doesn't specify what counts as evidence in a decision process" → QUALIFIED
- **Search terms:** evidence, evaluate, research, study, trial, RCT, source, critically, health information
- **Corpora:** casel-pilot-extracts.md, casel-framework-definition.md, casel-equity-transformative-sel.md
- **Hits:** Responsible Decision-Making G6–8 §10 "utilize the steps of a decision-making model"; G9–10 §16 "gather evidence and apply the steps of a decision-making process to support and solve academic, physical, and/or emotional challenges". Generic. No specification of what counts as evidence.
- **Verdict:** QUALIFIED. Card describes CASEL's generic decision-process content (§10, §16) and narrows REAL's addition to specifying evidence types and tracing evidence-to-guideline derivation.

### LT 7.2 × RSHE — "metacognitive self-direction sits outside the curriculum content" → CLEAN
- **Search terms:** metacognit, self-direct, reflect, monitor, pattern, self-aware, adjust, strategy
- **Corpora:** rshe-pilot-extracts.md, rshe-foreword.md, rshe-strand-introductions.md
- **Hits:** §1 foreword references generic character outcomes ("resilience, self-worth, self-respect, honesty, integrity, courage, kindness, and trustworthiness"); zero hits on metacognition, self-direction, or pattern-monitoring as curriculum content.
- **Verdict:** CLEAN. The foreword character list is named in the card; the absence claim is scoped to "metacognitive self-direction — noticing, analysing, and adjusting one's own patterns without external prompting", which is genuinely absent.

### LT 7.2 × CASEL — "doesn't develop metacognitive self-direction as a sustained disposition" → QUALIFIED
- **Search terms:** metacognit, self-direct, reflect, monitor, pattern, self-aware, adjust, goal
- **Corpora:** casel-pilot-extracts.md, casel-framework-definition.md
- **Hits:** Self-Management G6–8 §7 "reflect on progress toward a goal and evaluate the steps needed"; G9–10 §13 "monitor progress toward a specific goal by developing check-points or adjusting the plan as needed". Self-Awareness §3, §8, §14 reference reflection and emotional self-knowledge. No specification of metacognitive self-direction as a stable, articulated stance that holds in novel/unfamiliar contexts without scaffolding.
- **Verdict:** QUALIFIED. Card names CASEL's reflection-on-goal-progress content (§7, §13) and locates REAL's extension at "Band F: a stable, articulated way the student learns, reflects, and adjusts that holds in highly novel or unfamiliar contexts without scaffolding".

### LT 8.2 × CfW — "persuasive design sits outside CfW's digital framing" → QUALIFIED
- **Search terms:** persuasive, design, algorithm, attention economy, recommendation, addictive, dark pattern, surveillance, dopamine, platform, social media
- **Corpora:** cfw-pilot-extracts.md, cfw-what-matters.md, cfw-four-purposes.md, cfw-rse-statutory-principles.md
- **Hits:** Purpose 1 §4 "use digital technologies creatively to communicate, find and analyse information" (productive-use framing only). WM4 §15 references social influences in general terms but not platform/design specifically. Zero hits on persuasive design, algorithms, or attention economy.
- **Verdict:** QUALIFIED. Card opens with the Purpose 1 productive-use framing (§4), then states the absence in scoped terms ("Persuasive design — the way digital products are engineered to capture attention and shape behaviour — sits outside that framing").

### LT 8.3 × CfW — "WM5 runs without a digital-specific subdivision" → QUALIFIED
- **Search terms:** digital, online, social media, platform, screen, device, internet
- **Corpora:** cfw-pilot-extracts.md, cfw-what-matters.md, cfw-four-purposes.md, cfw-rse-statutory-principles.md
- **Hits:** Purpose 1 §4 "use digital technologies creatively to communicate, find and analyse information"; CfW more broadly references digital citizenship in framework-level documents not extracted here. Within WM5 healthy-relationships content (PS3 §15, PS5 §16), zero hits on digital, online, social media, or platform.
- **Verdict:** QUALIFIED. Card scopes the absence claim explicitly to WM5 ("Healthy relationships in CfW's WM5 run without a digital-specific subdivision"), not to CfW as a whole. Purpose 1's productive-use framing (§4) is acknowledged elsewhere in the LT 8.2 card.

---

## Process going forward

For Batch 3:
- Every card claiming absence runs this search before being committed.
- Results recorded here in the same format.
- If a search returns hits, the card is QUALIFIED (claim refined to acknowledge what's there) or RETRACTED (claim wrong, card rewritten).
- The audit report at the end of each batch lists the new absence-claim verifications.
