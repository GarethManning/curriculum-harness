# Decomposition candidates — REAL wellbeing criterion bank v2

Source: `docs/reference-corpus/real-wellbeing/criterion-bank-v2.json`
Audit date: 2026-04-23
Scope: All T1 (11 criteria) + T2 (116 criteria) = **127 criteria reviewed**. T3 entries (42) are out of scope because they use observation_indicators rather than competency_level_descriptors.

Purpose: Phase 1 of the decomposition audit — identify criteria whose `criterion_statement` contains two or more distinct, independently-assessable cognitive operations. This is a candidate report only. No data files have been modified. Human review and approval required before Phase 2 (execute approved decompositions).

## Decision rule applied

A criterion was flagged as a candidate if its `criterion_statement`:
- contains two or more cognitive operations joined by "and" / ", and" / "(a) ... (b) ... (c) ..." / numbered clauses, AND
- each operation is independently assessable (a student could demonstrate one without the other in a real assessment context).

A criterion was NOT flagged if:
- clauses describe one integrated performance (e.g. doing X and reflecting on it in the same moment),
- the "and" connects modalities rather than operations (e.g. "in writing or conversation"),
- the compound is an intentional capstone integration at Band E or F where integration is the assessment point.

For Bands E and F, borderline cases were flagged (per brief) — human review decides whether integration is intentional.

## Summary

- **Total T1/T2 criteria reviewed:** 127
- **Decomposition candidates identified:** 34
- **Candidates by band:** A=6, B=3, C=7, D=6, E=10, F=2
- **LTs with at least one candidate:** 13 of 13 (all T1/T2 LTs have at least one)

### Candidates by LT

| LT | Candidates |
|---|---|
| lt_1_3 (Personal Identity & Cultural Self-Awareness) | 4 |
| lt_2_1 (Focused Attention & Strategy) | 1 |
| lt_2_2 (Reflective Decision-Making) | 1 |
| lt_3_1 (Health Literacy & Habits) | 2 |
| lt_4_1 (Bodies, Boundaries & Consent) | 3 |
| lt_4_2 (Puberty, Health & Safe Choices) | 1 |
| lt_4_3 (Active Bystander & Anti-Discrimination) | 5 |
| lt_5_1 (Interpersonal Skills & Communication) | 2 |
| lt_6_1 (Brain, Body & Wellbeing Science) | 1 |
| lt_6_2 (Health Information Literacy) | 4 |
| lt_7_1 (Pattern Analysis & Adjustment) | 2 |
| lt_8_1 (Information Verification & Media Literacy) | 5 |
| lt_8_2 (Digital Influence & Psychological Agency) | 3 |

---

## Candidates grouped by associated_lt_ids

### lt_1_3 — Personal Identity & Cultural Self-Awareness

**crit_0152 — Band A**
- Statement: "I can name something that is part of my own home or family life that is different from a classmate's, describe it in my own words, and talk about the difference without saying one is better than the other."
- Rationale: Three operations — (1) naming a difference, (2) describing it, (3) maintaining non-evaluative framing. A student could name and describe the difference but fail to hold the non-evaluative stance, or vice versa — non-evaluative framing is a dispositional skill distinct from description.
- Proposed split:
  - A1: Name and describe one aspect of my home or family life that is different from a classmate's in my own words.
  - A2: Talk about a difference in home or family life without ranking one as better or worse.

**crit_0153 — Band B**
- Statement: "I can describe more than one aspect of my own identity — including at least one cultural aspect — in my own words, and explain that belonging to more than one group at once is a normal part of identity."
- Rationale: Two operations — (1) describing multiple aspects of own identity (self-report), (2) explaining the abstract principle of multi-group belonging (meta-concept). Describing one's own identity does not require articulating the generalised normative claim.
- Proposed split:
  - B1: Describe more than one aspect of my own identity, including at least one cultural aspect, in my own words.
  - B2: Explain that belonging to more than one group at once is a normal part of identity.

**crit_0154 — Band C**
- Statement: "I can describe how my own cultural background shapes how I see and interpret things, identify one way someone with a different background might see the same situation differently, and recognise stereotypes as oversimplifications."
- Rationale: Three distinct operations — own-cultural-lens description, cross-perspective identification, stereotype-as-oversimplification recognition. Each could be demonstrated without the others.
- Proposed split:
  - C1: Describe how my own cultural background shapes how I see and interpret things.
  - C2: Identify one way someone with a different background might see the same situation differently.
  - C3: Recognise stereotypes as oversimplifications of group experience.

**crit_0155 — Band D**
- Statement: "I can identify at least one group I did not choose to belong to, analyse how that group membership shapes my experience or perspective in a specific situation, and explain how intersecting identities produce experiences that single-dimension analysis misses."
- Rationale: Three operations — (1) identify-and-analyse unchosen group membership in a specific situation, (2) explain the intersectionality principle. Clauses 1–2 are tightly paired (identification and situational analysis of the same group), but the intersectionality explanation is a separate theoretical claim.
- Proposed split:
  - D1: Identify at least one group I did not choose to belong to and analyse how that group membership shapes my experience or perspective in a specific situation.
  - D2: Explain how intersecting identities produce experiences that single-dimension analysis misses.

### lt_2_1 — Focused Attention & Strategy

**crit_0108 — Band E**
- Statement: "I can design the conditions for sustained attention in a piece of my own work — including managing digital distractions — and produce a written evaluation of how different attentional strategies interacted with different types of tasks."
- Rationale: Two distinct deliverables — (1) generative design of attention conditions for a current piece of work, (2) retrospective written evaluation comparing strategies across different task types. Different cognitive modes (applied design vs. comparative analysis).
- Proposed split:
  - E1: Design the conditions for sustained attention in a piece of my own work, including managing digital distractions.
  - E2: Produce a written evaluation of how different attentional strategies interacted with different types of tasks.

### lt_2_2 — Reflective Decision-Making

**crit_0110 — Band E**
- Statement: "I can write a decision analysis that identifies at least one cognitive bias or assumption likely to be affecting my reasoning, describes an adjustment I made to my process to reduce its impact, and evaluates the quality of the reasoning independent of the outcome."
- Rationale: Three operations — bias identification, adjustment description, outcome-independent reasoning evaluation. The third operation (judging reasoning quality independent of outcome) is a distinct and demanding skill that a student could fail even when they identify bias and describe an adjustment.
- Proposed split:
  - E1: Identify at least one cognitive bias or assumption likely to be affecting my reasoning in a decision I face.
  - E2: Describe an adjustment I made to my reasoning process to reduce the bias's impact.
  - E3: Evaluate the quality of my decision-making reasoning independent of the outcome.

### lt_3_1 — Health Literacy & Habits

**crit_0112 — Band E**
- Statement: "I can write an analysis identifying the structural and social factors affecting my access to healthy habits, evaluate health claims in two sources using evidence-quality criteria, and produce a redesigned habits plan that accounts for conditions I cannot individually control."
- Rationale: Three independent operations — structural/social analysis (sociological), source evaluation (information literacy), plan design (generative). A student could do any subset well without the others.
- Proposed split:
  - E1: Analyse the structural and social factors affecting my access to healthy habits.
  - E2: Evaluate health claims in two sources using evidence-quality criteria.
  - E3: Produce a redesigned habits plan that accounts for conditions I cannot individually control.

**crit_0113 — Band F**
- Statement: "I can produce a designed health maintenance approach sustainable across the demands of adult life, accounting for competing priorities, social pressures, and systems-level constraints, and articulate in writing why sustainable habits require external conditions, not only personal willpower."
- Rationale: Two operations — (1) design a personal health approach, (2) articulate a generalised systems-level argument. Different cognitive modes (design vs. argument) and different deliverables. Despite F integration norms, the argument about willpower is a freestanding theoretical claim.
- Proposed split:
  - F1: Produce a designed health maintenance approach sustainable across the demands of adult life, accounting for competing priorities, social pressures, and systems-level constraints.
  - F2: Articulate in writing why sustainable habits require external conditions, not only personal willpower.

### lt_4_1 — Bodies, Boundaries & Consent

**crit_0042 — Band A**
- Statement: "I can identify at least two trusted adults in my specific context (home and school), and state one situation in which I would tell a trusted adult."
- Rationale: Two operations — (1) identifying specific trusted adults (relational mapping), (2) recognising a help-seeking scenario (judgment of when to disclose). Very young students may list adults without clearly recognising a disclosure scenario, or vice versa.
- Proposed split:
  - A1: Identify at least two trusted adults in my specific context (home and school).
  - A2: State one situation in which I would tell a trusted adult.

**crit_0049 — Band D**
- Statement: "I can state a refusal and a prepared exit plan in direct language in response to a pressure scenario."
- Rationale: Two operations — verbal refusal (in-the-moment) and exit-plan articulation (advance planning). A student could state a clear refusal without having a prepared exit plan, or describe an exit plan but struggle to voice refusal directly.
- Proposed split:
  - D1: State a refusal in direct language in response to a pressure scenario.
  - D2: Describe a prepared exit plan in direct language in response to a pressure scenario.

**crit_0114 — Band E**
- Statement: "I can complete a written analysis of a coercion, grooming, or exploitation scenario (online or institutional) that applies the relevant legal framework, evaluates the institutional context, and drafts a non-directive, trauma-aware response to a friend disclosing a similar situation."
- Rationale: Three operations in distinct cognitive modes — legal-framework application (rule-based reasoning), institutional evaluation (structural analysis), and drafting a trauma-aware non-directive response (interpersonal/pastoral composition).
- Proposed split:
  - E1: Apply the relevant legal framework to a coercion, grooming, or exploitation scenario (online or institutional).
  - E2: Evaluate the institutional context surrounding a coercion, grooming, or exploitation scenario.
  - E3: Draft a non-directive, trauma-aware response to a friend disclosing a coercion, grooming, or exploitation situation.

### lt_4_2 — Puberty, Health & Safe Choices

**crit_0116 — Band E**
- Statement: "I can complete a written analysis of a reproductive or sexual-health question that identifies the relevant healthcare service, states the access pathway and confidentiality conditions in this jurisdiction, and evaluates at least two information sources against stated evidence-based guideline criteria."
- Rationale: Three operations — (1) service identification, (2) access-pathway and confidentiality articulation, (3) source evaluation against guideline criteria. Jurisdictional knowledge (2) is distinct from information-literacy judgement (3).
- Proposed split:
  - E1: Identify the relevant healthcare service for a reproductive or sexual-health question.
  - E2: State the access pathway and confidentiality conditions for that service in this jurisdiction.
  - E3: Evaluate at least two information sources on the question against stated evidence-based guideline criteria.

### lt_4_3 — Active Bystander & Anti-Discrimination

**crit_0126 — Band A**
- Statement: "I can complete a short scenario-response (oral or drawing-plus-sentence) that describes a situation where someone was left out or treated unkindly, names what I saw, and identifies a specific trusted adult I could tell."
- Rationale: Three operations — situation description, observation naming, trusted-adult identification. Adult identification (help-seeking mapping) is a distinct skill from observational description.
- Proposed split:
  - A1: Describe a situation where someone was left out or treated unkindly and name what I saw.
  - A2: Identify a specific trusted adult I could tell about an exclusion or unkindness I witnessed.

**crit_0127 — Band B**
- Statement: "I can complete a written or oral scenario-response task that describes what happened when someone was excluded or treated unfairly, suggests how the person might have felt, and selects one helpful action from a short list of options with one-sentence reasoning for my choice."
- Rationale: Three operations — situation description, empathic emotion inference, helpful-action selection with reasoning. A student might describe accurately but fail to infer emotion, or choose without reasoning.
- Proposed split:
  - B1: Describe what happened when someone was excluded or treated unfairly.
  - B2: Suggest how the excluded or unfairly-treated person might have felt.
  - B3: Select one helpful action from a short list of options with one-sentence reasoning for my choice.

**crit_0128 — Band C**
- Statement: "I can complete a written scenario-response task that identifies the form of exclusion or discrimination present, assesses whether it is safe to intervene directly, and names and justifies my choice from the four bystander options."
- Rationale: Three distinct cognitive operations — classification of discrimination form (conceptual), safety assessment (risk judgment), and choice justification (decision).
- Proposed split:
  - C1: Identify the form of exclusion or discrimination present in a scenario.
  - C2: Assess whether it is safe to intervene directly in the scenario.
  - C3: Name and justify my choice from the four bystander options.

**crit_0129 — Band D**
- Statement: "I can complete a written analytical task on a bystander scenario that identifies the forms of discrimination present, names the specific group and power dynamics at play, and justifies a proposed response based on safety, proportionality, and what the targeted person is likely to need."
- Rationale: Three operations — discrimination identification, power-dynamic analysis, response justification grounded in multiple named criteria.
- Proposed split:
  - D1: Identify the forms of discrimination present in a bystander scenario.
  - D2: Name the specific group and power dynamics at play in the scenario.
  - D3: Justify a proposed response based on safety, proportionality, and what the targeted person is likely to need.

**crit_0130 — Band E**
- Statement: "I can complete a written evaluation that compares two or more possible responses to a discrimination scenario, identifies my own likely default response and its probable sources, and explains how specific group norms and institutional context factors shape which interventions are possible or effective."
- Rationale: Three operations — (1) comparative evaluation of response options, (2) self-knowledge about own default response and its sources, (3) structural/contextual analysis of group-norm and institutional factors. Self-knowledge (2) is particularly separable from the others.
- Proposed split:
  - E1: Compare two or more possible responses to a discrimination scenario.
  - E2: Identify my own likely default response and its probable sources.
  - E3: Explain how group norms and institutional context factors shape which bystander interventions are possible or effective.

### lt_5_1 — Interpersonal Skills & Communication

**crit_0062 — Band A**
- Statement: "I can apply an I-statement when something has bothered me, followed by a brief verbal reflection on my word choice."
- Rationale: Two operations — (1) in-the-moment I-statement performance, (2) metacognitive reflection on word choice. Performance and metacognitive reflection are routinely separable skills, especially at Band A.
- Proposed split:
  - A1: Apply an I-statement when something has bothered me.
  - A2: Give a brief verbal reflection on my word choice in the I-statement.

**crit_0119 — Band F**
- Statement: "I can complete a rubric-assessed communication task across significant difference (cultural, generational, or positional) in which I adjust my register and tone to the context without losing my own perspective, and demonstrate in written reflection my awareness of the power dynamics shaping who gets heard."
- Rationale: Two distinct deliverables — (1) a live cross-difference communication performance (interactional skill), (2) a separate written reflection on power dynamics (sociological analysis). Strong F performers often excel in one but not the other.
- Proposed split:
  - F1: Complete a communication task across significant difference (cultural, generational, or positional) in which I adjust my register and tone to the context without losing my own perspective.
  - F2: Demonstrate in written reflection my awareness of the power dynamics shaping who gets heard in cross-difference communication.

### lt_6_1 — Brain, Body & Wellbeing Science

**crit_0124 — Band E**
- Statement: "I can complete a rubric-assessed written evaluation of a specific wellbeing intervention (mindfulness, exercise, breathwork, sleep-hygiene, or similar), explaining its proposed mechanism, summarising what the evidence suggests about its effectiveness, and articulating what it would and would not change in the stress-emotion-attention-habit system."
- Rationale: Three operations — mechanism explanation (causal reasoning), evidence summary (literature-literacy), and systems-effect articulation (applied systems thinking). Each is a distinct cognitive demand.
- Proposed split:
  - E1: Explain the proposed mechanism of a specific wellbeing intervention (mindfulness, exercise, breathwork, sleep-hygiene, or similar).
  - E2: Summarise what the evidence suggests about the effectiveness of that intervention.
  - E3: Articulate what the intervention would and would not change in the stress-emotion-attention-habit system.

### lt_6_2 — Health Information Literacy

**crit_0085 — Band A**
- Statement: "I can complete a short rubric-assessed oral or written task in which I identify whether a simple health claim comes from a trusted source, and name who I would ask if unsure."
- Rationale: Two operations — trust judgment about the claim, and help-seeking adult identification when uncertain. At Band A these are clearly separable early literacy skills.
- Proposed split:
  - A1: Identify whether a simple health claim comes from a trusted source.
  - A2: Name who I would ask if unsure about a health claim.

**crit_0090 — Band C**
- Statement: "I can name any bias indicators present in a health information source and state and justify my conclusion about how much weight to give the claim."
- Rationale: Two operations — (1) bias-indicator identification (surface analysis), (2) weighted-conclusion justification (synthesis). A student may spot bias indicators but fail to translate that into a justified weighting.
- Proposed split:
  - C1: Name any bias indicators present in a health information source.
  - C2: State and justify my conclusion about how much weight to give a health claim.

**crit_0120 — Band E**
- Statement: "I can complete a rubric-assessed written analysis of an evidence base supporting a specific health claim (not a single study — the cumulative research) that (a) judges whether the body of evidence warrants the confidence placed in the claim, (b) identifies the commercial or institutional interests that may have shaped what research was done and published, and (c) justifies my conclusion using peer-review, RCT-design, statistical, and funding-bias criteria."
- Rationale: Three operations — evidence-base confidence judgment, interests/publication-bias analysis, conclusion justification using technical criteria. Each targets a different analytical skill (epistemic calibration vs. sociology of science vs. technical appraisal).
- Proposed split:
  - E1: Judge whether the body of evidence supporting a specific health claim warrants the confidence placed in the claim.
  - E2: Identify the commercial or institutional interests that may have shaped what research was done and published on the claim.
  - E3: Justify my conclusion using peer-review, RCT-design, statistical, and funding-bias criteria.

**crit_0121 — Band F**
- Statement: "I can complete a rubric-assessed analysis that (a) reads and interprets a provided systematic review or meta-analysis at an introductory level (identifying PICO, risk-of-bias findings, pooled effect, and GRADE rating), (b) traces how a named policy recommendation or guideline was derived from an evidence base, and (c) evaluates whether that guideline is well-supported, weakly-supported, or contested, articulating what I am certain of, what remains uncertain, and why."
- Rationale: Three genuinely distinct advanced skills — technical literature reading (PICO/GRADE), evidence-to-policy tracing (policy analysis), and guideline-strength evaluation with uncertainty articulation. Despite F capstone norms, these are separable enough that a student could succeed on (a) while failing (b), or vice versa. Flagging for human review.
- Proposed split:
  - F1: Read and interpret a provided systematic review or meta-analysis at an introductory level, identifying PICO, risk-of-bias findings, pooled effect, and GRADE rating.
  - F2: Trace how a named policy recommendation or guideline was derived from an evidence base.
  - F3: Evaluate whether the guideline is well-supported, weakly-supported, or contested, articulating what I am certain of, what remains uncertain, and why.

### lt_7_1 — Pattern Analysis & Adjustment

**crit_0103 — Band D**
- Statement: "I can describe a specific adjustment I have implemented and report the effect observed."
- Rationale: Two operations — (1) adjustment description (intervention documentation), (2) observed-effect report (empirical tracking). A student may describe an adjustment clearly without having tracked or accurately reported its effect.
- Proposed split:
  - D1: Describe a specific adjustment I have implemented in response to an observed pattern.
  - D2: Report the effect I observed after implementing the adjustment.

**crit_0122 — Band E**
- Statement: "I can complete a rubric-assessed structured metacognitive protocol applied to a named high-stakes academic or personal challenge, comprising: (a) a mapping of my typical patterns in this domain, (b) an identification of the sustaining conditions, (c) a specific intervention designed against those conditions, (d) a tracking record of the intervention's effects over a defined period, and (e) an iteration based on what the tracking showed."
- Rationale: Five distinct protocol components, each with its own cognitive demand — pattern mapping, sustaining-condition identification, intervention design, tracking, iteration. Each is independently assessable and separately trainable.
- Proposed split:
  - E1: Map my typical patterns in a named high-stakes academic or personal domain.
  - E2: Identify the conditions sustaining the mapped pattern.
  - E3: Design a specific intervention targeting the sustaining conditions.
  - E4: Maintain a tracking record of the intervention's effects over a defined period.
  - E5: Iterate on the intervention based on what the tracking showed.

### lt_8_1 — Information Verification & Media Literacy

**crit_0132 — Band A**
- Statement: "I can complete a rubric-assessed short oral or written task in which I am shown an age-appropriate piece of digital content (a picture, a short video clip, a made-up story), say whether I think it is real or made up, explain my reasoning in a sentence, and name a trusted adult I would ask if I wasn't sure."
- Rationale: Three operations — real/fake classification, reasoning explanation, help-seeking adult identification. Young students may classify accurately without articulating reasoning, or know a trusted adult without classifying well.
- Proposed split:
  - A1: Say whether an age-appropriate piece of digital content is real or made up.
  - A2: Explain my real/fake reasoning in a sentence.
  - A3: Name a trusted adult I would ask if I wasn't sure about a piece of digital content.

**crit_0133 — Band B**
- Statement: "I can complete a rubric-assessed short written task, given two pieces of digital content on the same topic, in which I (a) identify the maker of each, (b) state whether each maker is from a 'trusted place' and why, and (c) explain why I do or do not believe each piece of content."
- Rationale: Three operations — source-maker identification, trusted-place judgment with reasoning, belief judgment with reasoning. Each is a distinct early information-literacy skill.
- Proposed split:
  - B1: Identify the maker of each of two pieces of digital content on the same topic.
  - B2: State whether each maker is from a trusted place and why.
  - B3: Explain why I do or do not believe each piece of content.

**crit_0134 — Band C**
- Statement: "I can complete a rubric-assessed written comparison of two sources making the same claim in which I (a) apply lateral reading to find out who is behind each source, (b) name specific manipulation signs present or absent in each, and (c) justify which source I trust more with at least two named criteria."
- Rationale: Three operations — lateral-reading investigation, manipulation-sign identification, trust justification with criteria. Each targets a discrete media-literacy sub-skill.
- Proposed split:
  - C1: Apply lateral reading to find out who is behind each of two sources making the same claim.
  - C2: Name specific manipulation signs present or absent in each source.
  - C3: Justify which source I trust more with at least two named criteria.

**crit_0135 — Band D**
- Statement: "I can complete a rubric-assessed written analysis of a digital claim in which I (a) apply a named verification process (e.g. SIFT) to the claim, (b) identify the origin, the evidence behind it, and the motivation of the source, and (c) justify my separate conclusions about what I would believe, what I would share, and what I would act on."
- Rationale: Three operations — verification-process application, origin/evidence/motivation identification, differentiated believe/share/act judgment. The believe/share/act differentiation (c) is a distinct judgment layered on top of the identifications in (b).
- Proposed split:
  - D1: Apply a named verification process (e.g. SIFT) to a digital claim.
  - D2: Identify the origin, the evidence behind a digital claim, and the motivation of the source.
  - D3: Justify separate conclusions about what I would believe, what I would share, and what I would act on.

**crit_0136 — Band E**
- Statement: "I can complete a rubric-assessed written evaluation of a contested claim in which I (a) weigh evidence across multiple sources using named criteria, (b) identify at least two specific algorithmic, platform, or production-incentive factors that shaped how the claim reached me, (c) name the self-bias most likely to affect my interpretation (confirmation, motivated reasoning, in-group alignment), and (d) justify my conclusion with explicit awareness of that bias."
- Rationale: Four operations — evidence weighing, algorithmic/platform factor identification, self-bias naming, bias-aware conclusion justification. The self-bias naming (c) is a metacognitive skill distinct from evidence weighing (a) and from platform analysis (b).
- Proposed split:
  - E1: Weigh evidence across multiple sources about a contested claim using named criteria.
  - E2: Identify at least two algorithmic, platform, or production-incentive factors that shaped how the claim reached me.
  - E3: Name the self-bias most likely to affect my interpretation (confirmation, motivated reasoning, in-group alignment).
  - E4: Justify my conclusion about the contested claim with explicit awareness of the named self-bias.

### lt_8_2 — Digital Influence & Psychological Agency

**crit_0138 — Band C**
- Statement: "I can complete a rubric-assessed short written analysis (e.g. 200–300 words) of a chosen digital product in which I (a) identify one specific persuasive-design feature using correct vocabulary, (b) describe one reason (drawing on dopamine / reward / habit-loop mechanism) the design works on people, and (c) explain one specific effect I have noticed on myself (time, mood, behaviour)."
- Rationale: Three operations — feature identification (vocabulary), mechanism-based design-reason description (science), personal-effect explanation (self-report). Each targets a different cognitive demand.
- Proposed split:
  - C1: Identify one specific persuasive-design feature in a chosen digital product using correct vocabulary.
  - C2: Describe one reason a persuasive-design feature works on people, drawing on dopamine, reward, or habit-loop mechanism.
  - C3: Explain one specific effect a digital product has had on me in time, mood, or behaviour.

**crit_0139 — Band D**
- Statement: "I can complete a rubric-assessed written analysis of a chosen digital product using the 'attention / emotion / behaviour' framework in which I (a) identify at least two interacting persuasive-design features using correct vocabulary, (b) analyse how each shapes attention, emotion, or behaviour in the product, and (c) explain one specific effect I have noticed on my own thinking, mood, or time."
- Rationale: Three operations — feature identification, framework-based shaping analysis, personal-effect explanation. Framework application (b) is distinct from both technical identification (a) and self-report (c).
- Proposed split:
  - D1: Identify at least two interacting persuasive-design features in a chosen digital product using correct vocabulary.
  - D2: Analyse how each feature shapes attention, emotion, or behaviour in the product.
  - D3: Explain one specific effect the product has had on my own thinking, mood, or time.

**crit_0140 — Band E**
- Statement: "I can complete a rubric-assessed written evaluation of a chosen digital platform in which I (a) evaluate how the platform algorithmically curates what I see (with evidence from my own observation or documentation), (b) explain at least two specific psychological or economic incentives driving that design decision, and (c) justify one specific change I will make to my use of the platform based on my analysis — including why that change addresses the mechanism, not just the symptom."
- Rationale: Three operations — algorithmic-curation evaluation with evidence, incentive explanation (psychological + economic), mechanism-addressing behaviour-change justification. Each is a distinct analytic move.
- Proposed split:
  - E1: Evaluate how a chosen digital platform algorithmically curates what I see, with evidence from my own observation or documentation.
  - E2: Explain at least two psychological or economic incentives driving that platform's design decisions.
  - E3: Justify one specific change I will make to my use of the platform, showing why the change addresses the mechanism rather than the symptom.

---

## Criteria considered and not flagged (summary note)

The remaining 93 T1/T2 criteria were judged to describe a single integrated cognitive operation, to use "and/or" for modality rather than operation, or to be an intentional capstone integration at Band F. Notable non-flag decisions worth human attention:

- **crit_0156 (lt_1_3, E)**: "analyse ... and articulate what I might be missing" — treated as one integrated analytical act (articulation is part of the analysis). Could be reconsidered if the panel treats articulation as separable.
- **crit_0157 (lt_1_3, F)**, **crit_0109 (lt_2_1, F)**, **crit_0111 (lt_2_2, F)**, **crit_0115 (lt_4_1, F)**, **crit_0117 (lt_4_2, F)**, **crit_0131 (lt_4_3, F)**, **crit_0125 (lt_6_1, F)**, **crit_0123 (lt_7_1, F)**, **crit_0137 (lt_8_1, F)**, **crit_0141 (lt_8_2, F)**: Band F capstone statements with compound clauses were not flagged because integration is the intended point at F. If the panel prefers decomposition at F as well, these should be reconsidered.
- **crit_0044 (lt_4_1, B)**: "describe what a clear request and a clear answer sound like" — treated as one descriptive act about a consent exchange. Could be split if the panel views request and answer as independently assessable.
- **crit_0126 vs crit_0127 (lt_4_3, A/B)** were both flagged, but **crit_0046 (lt_4_1, C)** "applies consent reasoning to non-sexual, physical, and online scenarios" was not — treated as multi-scenario coverage of one reasoning skill rather than multiple operations.

## Next step

Human review of this candidate report. Approved decompositions will be executed in Phase 2 (Opus) per STATE.md section 5 step 4. No Phase 2 work has been performed in this session.
