# Reference review — uk-statutory-rshe

Source snapshot: `docs/run-snapshots/uk-statutory-rshe`. Classifier: `claude-sonnet-4-20250514` at temperature 0.3 with 3x self-consistency.

## Progression structure (source-native)

- **source type:** `england_rshe_full`
- **band count:** 2
- **bands (developmental order):** End of Primary, End of Secondary
- **age range hint:** ages 5-16 (DfE RSHE statutory guidance July 2025; primary phase = Years 1-6, secondary phase = Years 7-11; two-phase structure, no within-phase KS subdivision)
- **detection confidence:** `high`
- **detection rationale:** Source slug 'uk-statutory-rshe' matches DfE RSHE full-programme pattern. Two-band structure: End of Primary (ages 5-11) + End of Secondary (ages 11-16). DfE statutory RSHE guidance (July 2025).

**Progression philosophy.**

> The DfE RSHE statutory guidance (July 2025) uses a two-phase architecture: 'content to be covered by the end of primary' and 'content to be covered by the end of secondary'. Neither phase is subdivided into individual Key Stages within the curriculum content sections. Two-band output reflects the guidance's own structure. Per DfE statutory RSHE guidance (England), Children and Social Work Act 2017.

### Per-band developmental index

| Band | Approximate age | Approximate grade/year | Developmental descriptor |
|---|---|---|---|
| End of Primary | ages 5-11 | Years 1-6 (KS1 and KS2) | Primary pupils develop the foundational skills and knowledge needed for positive relationships, personal safety, and health. Outcomes are framed as terminal goals for all primary pupils; year-group and KS1/KS2 sequencing is a school decision. Primary relationships education does not include RSE content; sex education in primary is non-statutory. |
| End of Secondary | ages 11-16 | Years 7-11 (KS3 and KS4) | Secondary pupils develop the knowledge, values and personal qualities needed to navigate relationships, sex and health across the full secondary phase. Outcomes are framed as terminal goals for all secondary pupils; KS3/KS4 and year-group sequencing is a school decision. |

## Summary

- KUD items: **279**
- Halted KUD blocks: **72**
- Competency clusters: **19**
  - overall stability: `cluster_unstable`
- Learning Targets: **44**
  - knowledge types: Type 1=15, Type 2=19, Type 3=10
  - stability: {'stable': 37, 'lt_set_unstable': 7}
- Band-statement sets (Type 1/2): **33**
  - stability: {'band_statements_unstable': 5, 'stable': 28}
- Observation indicator sets (Type 3): **10**
  - stability: {'stable': 8, 'observation_indicators_unstable': 2}
- Criterion rubrics (Type 1/2): **34** (gate pass=26; halted=0)
  - stability: {'stable': 20, 'rubric_unstable': 9, 'rubric_unreliable': 5}
- Supporting components (Type 1/2): **18** (halted=16)
- Halted at any stage: 90
- Pipeline: all KUD halting gates passed

## Competencies

### Body Awareness and Personal Boundaries — `cluster_01`

**Definition.** The ability to understand body parts, personal boundaries, and express needs around physical safety and privacy.

**Dominant knowledge type:** Type 1. **Stability:** `stable`. **Source lines:** L3-568. **KUD items:** 5.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0002_item_01` | Type 1 | know | Young people understand the correct terms for different parts of the body |
| `blk_0002_item_02` | Type 1 | do_skill | Young people are able to confidently use correct terms for different parts of the body |
| `blk_0346_item_01` | Type 1 | know | The correct names of body parts, including the penis, vulva, vagina, testicles, scrotum, nipples |
| `blk_0346_item_02` | Type 1 | understand | All of these parts of the body are private |
| `blk_0346_item_03` | Type 2 | do_skill | Skills to understand and express their own boundaries around these body parts |

#### Learning Targets

##### Identifying Body Parts and Privacy — `cluster_01_lt_01`

**Definition.** I can identify and name body parts including private areas and explain which parts are private.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0002_item_01`, `blk_0002_item_02`, `blk_0346_item_01`, `blk_0346_item_02`

**Band progression** — stability `band_statements_unstable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify and name body parts including private areas and explain which parts are private. |
| End of Secondary | I can accurately identify body parts including private areas and explain privacy boundaries with detailed reasoning across different contexts. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently identifies and names' and 'clearly explains', indicating complete mastery of the learning target.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify body parts or privacy concepts. |
| emerging | With support, names some body parts but shows confusion about privacy concepts. |
| developing | Independently identifies most body parts but inconsistently explains which areas are private. |
| competent | Independently identifies and names body parts including private areas and clearly explains which parts are private. |
| extending | Applies body awareness knowledge to explain privacy boundaries in different contexts or situations. |

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Introduce the idea that we'll create a guide together about knowing our bodies and privacy
- stage: Have students share what they already know about body parts and which ones might be private
- stage: Work together to organize their ideas into different levels of understanding
- stage: Refine the levels by discussing what each one looks like in practice
- prompt: What body parts can you name and how do you know which ones are private?
- prompt: How would you explain to a friend which body parts should stay covered?
- prompt: What does it look like when someone really understands body parts and privacy?
- anchor-examples guidance: Choose examples that show clear differences in naming accuracy and privacy understanding without being overly detailed or inappropriate for the age group.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet tried to name body parts or talk about privacy. |
| emerging | I can name some body parts with help but get confused about which ones are private. |
| developing | I can name most body parts on my own but sometimes mix up which areas are private. |
| competent | I can name body parts including private areas and clearly explain which parts are private. |
| extending | I can use my knowledge about body parts and privacy to explain boundaries in different situations. |

- self-check: Can I name the main body parts and explain which ones are private?
- self-check: Am I able to explain privacy rules clearly to others?

_Feedback moves by level:_
- **no_evidence**
  - Start with basic body part identification using simple pictures or diagrams
  - Introduce the concept that some body parts are private and should be covered
- **emerging**
  - Practice naming body parts with visual supports and gentle correction
  - Use simple language to clarify which areas are private and why
- **developing**
  - Review privacy concepts through role-play or discussion scenarios
  - Provide consistent reminders about which body parts are considered private
- **competent**
  - Challenge thinking by discussing privacy in different settings or contexts
  - Encourage explaining privacy concepts to help others understand

##### Expressing Personal Boundaries — `cluster_01_lt_02`

**Definition.** I can communicate my boundaries about physical contact and privacy needs.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**Prerequisites:** `cluster_01_lt_01`

**KUD items covered:** `blk_0346_item_03`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can communicate my boundaries about physical contact and privacy needs in familiar situations. |
| End of Secondary | I can communicate my boundaries about physical contact and privacy needs clearly and assertively across various contexts. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as demonstrated independently with 'clearly communicates' showing successful achievement of the learning target.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to communicate personal boundaries. |
| emerging | With support, attempts to express boundaries but communication is unclear or inconsistent. |
| developing | Independently communicates some boundaries about physical contact but struggles with privacy needs or clarity. |
| competent | Clearly communicates personal boundaries about both physical contact and privacy needs in age-appropriate situations. |
| extending | Adapts boundary communication effectively across different contexts and supports others in expressing their boundaries. |

_Prerequisite edges:_
- `cluster_01_lt_01` [ontological_prerequisite/high] — Cannot communicate boundaries about private areas without first identifying which body parts are private.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Discuss what boundaries mean and why they matter for feeling safe and comfortable
- stage: Brainstorm different types of boundaries we might need with our bodies and personal space
- stage: Explore how we can communicate boundaries clearly using words and actions
- stage: Practice identifying when boundaries are communicated well versus when they need improvement
- prompt: What does it mean to have boundaries about your body and personal space?
- prompt: How can we tell someone about our boundaries in a clear way?
- prompt: What makes boundary communication work well in different situations?
- anchor-examples guidance: Choose examples that show clear progression from unclear boundary attempts to confident communication across various age-appropriate contexts.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet tried to communicate my boundaries about physical contact or privacy. |
| emerging | I can try to express my boundaries with help but my communication is unclear or inconsistent. |
| developing | I can communicate some boundaries about physical contact but struggle with privacy needs or being clear. |
| competent | I can clearly communicate my boundaries about both physical contact and privacy needs in appropriate situations. |
| extending | I can adapt my boundary communication effectively across different contexts and help others express their boundaries. |

- self-check: Can I clearly tell others about my boundaries for both physical contact and privacy?
- self-check: Do I communicate my boundaries in ways that work well in different situations?

_Feedback moves by level:_
- **no_evidence**
  - Model simple boundary statements and practice together
  - Create safe opportunities to express basic comfort preferences
- **emerging**
  - Help clarify specific boundary language and practice consistent messaging
  - Provide sentence starters for expressing boundaries clearly
- **developing**
  - Practice communicating privacy boundaries using the same clarity as physical contact boundaries
  - Role-play boundary communication in different scenarios
- **competent**
  - Explore how boundary communication changes across different contexts and relationships
  - Practice supporting peers in expressing their own boundaries

### Foundational Relationship Skills and Safety — `cluster_02`

**Definition.** The ability to build positive relationships, maintain safety, and develop caring dispositions toward others.

**Dominant knowledge type:** Type 2. **Stability:** `stable`. **Source lines:** L10-14. **KUD items:** 5.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0006_item_01` | Type 1 | know | skills and knowledge that form the building blocks of all positive relationships |
| `blk_0006_item_02` | Type 2 | do_skill | know how to keep themselves and others safe |
| `blk_0006_item_03` | Type 3 | do_disposition | grow into kind, caring adults who have respect for others |
| `blk_0008_item_01` | Type 2 | do_skill | skills for managing difficult feelings in their friendships, like disappointment or anger |
| `blk_0008_item_02` | Type 2 | do_skill | reflect on how to behave with kindness in more complex or challenging relationships |

#### Learning Targets

##### Building Safe and Positive Relationships — `cluster_02_lt_01`

**Definition.** I can apply foundational relationship skills and safety knowledge to build and maintain positive connections with others.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**KUD items covered:** `blk_0006_item_01`, `blk_0006_item_02`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can apply basic relationship skills to build positive connections with familiar people in structured settings. |
| End of Secondary | I can independently apply comprehensive relationship skills and safety knowledge to build and maintain positive connections across diverse social contexts. |

**Criterion rubric** — stability `rubric_unstable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor clearly states the learner 'independently applies' the required skills, demonstrating complete achievement of the learning target without hedging language or positioning it as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to demonstrate relationship skills or safety knowledge. |
| emerging | With support, identifies some relationship skills but applies them inconsistently or inaccurately. |
| developing | Independently demonstrates basic relationship skills in familiar contexts but struggles with complex situations. |
| competent | Independently applies foundational relationship skills and safety knowledge to build and maintain positive connections with others. |
| extending | Transfers relationship skills to unfamiliar contexts and integrates safety knowledge with advanced interpersonal strategies. |

_Prerequisite edges:_
- `cluster_01_lt_02` [ontological_prerequisite/high] — Cannot build safe relationships without ability to communicate personal boundaries.
- `cluster_05_lt_01` [pedagogical_sequencing/high] — Understanding healthy friendship characteristics typically precedes applying broader relationship skills.
- `cluster_06_lt_01` [ontological_prerequisite/high] — Assertive communication and boundary setting are fundamental components of building positive relationships.

##### Managing Complex Relationship Challenges — `cluster_02_lt_02`

**Definition.** I can manage difficult feelings and reflect on kind behaviors when navigating challenging relationship situations.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**KUD items covered:** `blk_0008_item_01`, `blk_0008_item_02`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify my difficult feelings and choose kind behaviors when facing simple relationship challenges. |
| End of Secondary | I can analyze complex emotions and evaluate the effectiveness of kind behaviors across varied challenging relationship situations. |

**Criterion rubric** — stability `stable`, quality gate **FAIL**.

_Gate failures:_ observable_verb

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently manages' and 'effectively', positioning Competent as complete success without hedging language.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to manage feelings or reflect on behaviors. |
| emerging | With support, identifies some difficult feelings but struggles to manage them appropriately. |
| developing | Independently recognises difficult feelings and attempts reflection but responses lack consistency or effectiveness. |
| competent | Independently manages difficult feelings and reflects on kind behaviors to navigate challenging relationship situations effectively. |
| extending | Transfers emotional management skills to novel contexts and supports others in challenging situations. |

_Prerequisite edges:_
- `cluster_02_lt_01` [pedagogical_sequencing/high] — Basic relationship skills provide foundation for managing complex challenges.
- `cluster_14_lt_01` [ontological_prerequisite/high] — Cannot manage difficult feelings without understanding emotions and mental health concepts.

##### Caring and Respectful Disposition — `cluster_02_lt_03`

**Definition.** The student enacts kindness, care, and respect for others as a sustained orientation across relationships.

**Knowledge type:** Type 3. **Assessment route:** `multi_informant_observation`. **Stability:** `stable`.

**KUD items covered:** `blk_0006_item_03`

**Observation protocol** — stability `stable`, Mode 3 gate **PASS**.

_Prerequisites (knowledge-contingent Type 3):_ `Building Safe and Positive Relationships`

**End of Primary**

- The student spontaneously offers help to classmates who are struggling or upset
- The student uses gentle words and tone when speaking to peers, even during disagreements
- The student shows consideration for others' feelings by waiting their turn and sharing materials without being reminded

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Primary):_ Think about one relationship in your life — with a friend, family member, or classmate. What makes it feel safe and kind? Is there anything you would like to be different?

**End of Secondary**

- The student consistently demonstrates empathy by actively listening to others' perspectives and responding thoughtfully
- The student advocates for peers who are being treated unfairly or excluded from group activities
- The student maintains respectful communication and supportive behaviour even in challenging social situations or conflicts

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Secondary):_ Think about a situation this term where you had to make a decision about a relationship or your own wellbeing. What did you consider, and what would you do differently now?

**Parent / caregiver prompts**

- What have you noticed about how your child treats siblings, friends, or family members when they are upset or need help?
- When your child disagrees with someone at home, how do they express their feelings and work through the situation?
- Have you observed your child showing consideration for others' needs or feelings in everyday family situations?

**Developmental conversation protocol.** The conversation explores specific examples of caring and respectful interactions the student has demonstrated, examining how their orientation toward kindness manifests across different relationships and contexts.

### Family Diversity and Acceptance — `cluster_03`

**Definition.** The ability to understand diverse family structures and maintain respectful attitudes toward different family forms.

**Dominant knowledge type:** Type 1. **Stability:** `stable`. **Source lines:** L19-224. **KUD items:** 13.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0010_item_01` | Type 1 | know | Many forms of families provide a nurturing environment for children, and can include single parent families, same-sex parents, families headed by grandparents, young carers, kinship carers, adoptive p |
| `blk_0010_item_02` | Type 3 | do_disposition | Care should be taken to ensure that children are not stigmatised based on their home circumstances. |
| `blk_0022_item_01` | Type 1 | know | Families can provide love, security and stability for children growing up safe and happy |
| `blk_0024_item_01` | Type 1 | understand | The characteristics of safe and happy family life, including commitment to each other in times of difficulty, protection and care for children and other family members, the importance of spending time |
| `blk_0026_item_01` | Type 1 | know | that the families of other children, either in school or in the wider world, sometimes look different from their family, but that other children's families are also characterised by love and care |
| `blk_0026_item_02` | Type 3 | do_disposition | respect those differences in other children's families |
| `blk_0028_item_01` | Type 1 | understand | That stable, caring relationships are at the heart of safe and happy families and are important for children's security as they grow up. |
| `blk_0030_item_01` | Type 1 | know | That marriage and civil partnerships represent a formal and legally recognised commitment of two people to each other which is intended to be lifelong. |
| `blk_0126_item_01` | Type 1 | know | The legal status of marriage and civil partnership, including that they carry legal rights, benefits and protections that are not available to couples who are cohabiting or who have, for example, unde |
| `blk_0128_item_01` | Type 1 | know | Cohabitants do not obtain marriage-like status or rights from living together or by having children |
| `blk_0131_item_01` | Type 1 | understand | How families and relationships change over time, including through birth, death, separation and new relationships |
| `blk_0133_item_01` | Type 1 | know | characteristics of successful parenting |
| `blk_0133_item_02` | Type 1 | understand | the importance of the early years of a child's life for brain development |

#### Learning Targets

##### Identifying Diverse Family Structures — `cluster_03_lt_01`

**Definition.** I can identify and describe various family forms and their characteristics.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0010_item_01`, `blk_0022_item_01`, `blk_0024_item_01`, `blk_0026_item_01`, `blk_0028_item_01`, `blk_0030_item_01`, `blk_0126_item_01`, `blk_0128_item_01`, `blk_0131_item_01`, `blk_0133_item_01`, `blk_0133_item_02`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify different types of families and describe their basic characteristics with support. |
| End of Secondary | I can independently identify diverse family structures and describe their detailed characteristics across various contexts. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as demonstrated independently and accurately, standing alone as evidence that the learning target is met.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify family structures. |
| emerging | With support, names some family types but descriptions are incomplete or inaccurate. |
| developing | Independently identifies several family forms but descriptions lack detail or contain minor gaps. |
| competent | Independently identifies and describes various family structures including nuclear, single-parent, blended, extended, adoptive, and same-sex parent families accurately. |
| extending | Compares family structures across cultures or explains how family diversity strengthens communities. |

**Supporting components** — stability `stable`.

_Co-construction plan:_
- stage: Students brainstorm all the different types of families they know from their lives and communities.
- stage: Teacher guides students to group similar family types together and create category names.
- stage: Students discuss what makes each family type unique and special.
- stage: Class creates success criteria for describing family structures clearly and accurately.
- prompt: What different kinds of families do you see in your neighborhood or school?
- prompt: How would you group these families that are similar?
- prompt: What makes each type of family special or unique?
- prompt: What should we include when we describe a family structure well?
- anchor-examples guidance: Choose examples that represent the full range of family structures students identified, ensuring cultural diversity and avoiding stereotypes.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet attempted to identify different family structures. |
| emerging | I can name some family types with help but my descriptions need more work. |
| developing | I can identify several family forms on my own but my descriptions could be more detailed. |
| competent | I can independently identify and accurately describe various family structures including nuclear, single-parent, blended, extended, adoptive, and same-sex parent families. |
| extending | I can compare family structures across different cultures or explain how family diversity makes communities stronger. |

- self-check: Can I name at least six different types of family structures?
- self-check: Are my descriptions accurate and detailed enough for someone else to understand each family type?

_Feedback moves by level:_
- **no_evidence**
  - Provide visual examples of different family structures from books or photos.
  - Start with one familiar family type and guide student to describe what they notice.
- **emerging**
  - Ask student to choose one family type they named and help them add more details.
  - Provide sentence starters to help student describe family characteristics more completely.
- **developing**
  - Encourage student to add specific details about family roles or living arrangements.
  - Guide student to check their descriptions against real examples to ensure accuracy.
- **competent**
  - Challenge student to research family structures from different cultures or time periods.
  - Ask student to explain connections between family diversity and community strengths.

##### Respectful Family Acceptance — `cluster_03_lt_02`

**Definition.** The student holds respectful attitudes toward different family forms and avoids stigmatising others based on family circumstances.

**Knowledge type:** Type 3. **Assessment route:** `multi_informant_observation`. **Stability:** `stable`.

**KUD items covered:** `blk_0010_item_02`, `blk_0026_item_02`

**Observation protocol** — stability `stable`, Mode 3 gate **PASS**.

_Prerequisites (knowledge-contingent Type 3):_ `Identifying Diverse Family Structures`

**End of Primary**

- The student speaks positively about classmates' different family arrangements without making comparisons or judgements
- The student includes children from various family structures in play and group activities without questioning their family circumstances
- The student responds with curiosity rather than surprise when learning about unfamiliar family forms

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Primary):_ Think about one relationship in your life — with a friend, family member, or classmate. What makes it feel safe and kind? Is there anything you would like to be different?

**End of Secondary**

- The student actively challenges stereotypes or negative comments about non-traditional families in peer conversations
- The student demonstrates consistent inclusive language when discussing family topics across different social contexts
- The student seeks to understand rather than judge when encountering family situations different from their own experience

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Secondary):_ Think about a situation this term where you had to make a decision about a relationship or your own wellbeing. What did you consider, and what would you do differently now?

**Parent / caregiver prompts**

- What have you noticed about how your child talks about their friends' families at home?
- When your child encounters families that look different from yours, how do they respond or what questions do they ask?
- Have you observed your child standing up for or supporting friends whose family situations might be different or challenging?

**Developmental conversation protocol.** The conversation explores specific instances where the student has demonstrated respectful attitudes toward family diversity, examining their natural responses to different family forms and their developing capacity to challenge stigmatising attitudes in their peer group.

### Abuse Recognition and Protection — `cluster_04`

**Definition.** The ability to recognise abuse, understand personal rights, and seek help when safety is compromised.

**Dominant knowledge type:** Type 2. **Stability:** `cluster_unstable`. **Source lines:** L25-399. **KUD items:** 21.

_Stability diagnostics:_
- dominant_type_drift_run2: Type 2→Type 1
- dominant_type_drift_run3: Type 2→Type 1

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0012_item_01` | Type 1 | understand | positive relationships, boundaries, privacy, and children's rights over their own bodies and personal information |
| `blk_0012_item_02` | Type 2 | do_skill | recognise emotional, physical and sexual abuse |
| `blk_0012_item_03` | Type 2 | do_skill | recognise and report risks and abuse, including online |
| `blk_0012_item_04` | Type 3 | do_disposition | keep themselves and others safe |
| `blk_0015_item_01` | Type 1 | know | Being a victim of abuse is never the fault of the child |
| `blk_0032_item_01` | Type 2 | do_skill | how to recognise if family relationships are making them feel unhappy or unsafe, and how to seek help or advice from others if needed |
| `blk_0114_item_01` | Type 1 | know | Being a victim of abuse is never the fault of the child or young person |
| `blk_0114_item_02` | Type 1 | know | Different forms of abuse exist and should be addressed sensitively and clearly at appropriate ages |
| `blk_0114_item_03` | Type 1 | understand | Schools have an important role as a place of consistency and safety where pupils can find support, particularly for those experiencing unhealthy or unsafe relationships |
| `blk_0205_item_01` | Type 1 | know | Sexual harassment and sexual violence are unacceptable behaviours, and it is never the fault of the person experiencing it. |
| `blk_0207_item_01` | Type 1 | know | Sexual harassment includes unsolicited sexual language / attention / touching, taking and/or sharing intimate or sexual images without consent, public sexual harassment, pressuring other people to do  |
| `blk_0210_item_01` | Type 1 | know | sexual harassment and sexual violence among young people but also includes other forms of concerning behaviour like using age-inappropriate sexual language |
| `blk_0212_item_01` | Type 1 | know | The concepts and laws relating to domestic abuse, including controlling or coercive behaviour, emotional, sexual, economic or physical abuse, and violent or threatening behaviour |
| `blk_0216_item_01` | Type 1 | know | The concepts and laws relating to harms which are exploitative, including sexual exploitation, criminal exploitation and abuse, grooming, and financial exploitation |
| `blk_0220_item_01` | Type 1 | know | The Domestic Abuse Act 2021 recognised children who see, hear, or experience the effects of abuse, and are related to either the victim of the abusive behaviour, or the perpetrator, as victims of dome |
| `blk_0220_item_02` | Type 1 | know | The Domestic Abuse Act 2021 statutory guidance is designed to support statutory and non-statutory bodies working with victims of domestic abuse, including children |
| `blk_0222_item_01` | Type 1 | know | It is illegal to assist in the performance of FGM, virginity testing or hymenoplasty, in the UK or abroad, or to fail to protect a person under 16 for whom they are responsible |
| `blk_0224_item_01` | Type 1 | know | Strangulation (applying pressure to the neck) is an offence, regardless of whether it causes injury |
| `blk_0225_item_01` | Type 1 | know | That any activity that involves applying force or pressure to someone's neck or covering someone's mouth and nose is dangerous and can lead to serious injury or death. |
| `blk_0227_item_01` | Type 1 | know | That pornography presents some activities as normal which many people do not and will never engage in, some of which can be emotionally and/or physically harmful. |
| `blk_0229_item_01` | Type 1 | know | How to seek support for their own worrying or abusive behaviour or for worrying or abusive behaviour they have experienced from others, including information on where to report abuse, and where to see |

#### Learning Targets

##### Recognising Abuse and Unsafe Situations — `cluster_04_lt_01`

**Definition.** I can identify different forms of abuse and recognise when situations are unsafe or harmful.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**KUD items covered:** `blk_0012_item_02`, `blk_0012_item_03`, `blk_0032_item_01`, `blk_0114_item_02`, `blk_0205_item_01`, `blk_0207_item_01`, `blk_0210_item_01`, `blk_0212_item_01`, `blk_0216_item_01`, `blk_0222_item_01`, `blk_0224_item_01`, `blk_0225_item_01`, `blk_0227_item_01`

**Band progression** — stability `band_statements_unstable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify basic forms of abuse and recognise when situations feel unsafe with adult guidance. |
| End of Secondary | I can analyse different forms of abuse and evaluate potential risks in complex situations independently. |

**Criterion rubric** — stability `rubric_unstable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor clearly states the learner 'independently identifies' the required capabilities, demonstrating complete achievement of the learning target without hedging language or positioning it as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify abuse or unsafe situations. |
| emerging | With support, identifies some obvious forms of abuse but misses subtle indicators. |
| developing | Independently recognises clear abuse forms but struggles with complex or ambiguous unsafe situations. |
| competent | Independently identifies different forms of abuse and recognises when situations are unsafe or harmful. |
| extending | Identifies abuse patterns and unsafe situations across diverse contexts with sophisticated reasoning. |

_Prerequisite edges:_
- `cluster_01_lt_01` [ontological_prerequisite/high] — Understanding body parts and privacy is essential for recognising physical and sexual abuse.
- `cluster_01_lt_02` [pedagogical_sequencing/high] — Understanding personal boundaries helps learners recognise when those boundaries are being violated.
- `cluster_09_lt_01` [ontological_prerequisite/medium] — Recognising trust and safety risks provides foundational skills for identifying unsafe situations.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Introduce the concept of safety and harm through student experiences
- stage: Explore different types of unsafe situations students might encounter
- stage: Develop criteria for recognising when situations become harmful
- stage: Create descriptors for different levels of recognition ability
- prompt: What makes a situation feel unsafe to you?
- prompt: How can we tell the difference between something uncomfortable and something harmful?
- prompt: What clues help us recognise when someone needs help?
- anchor-examples guidance: Select scenarios that range from obvious safety concerns to more subtle warning signs, ensuring examples are age-appropriate and culturally relevant.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet shown I can identify abuse or unsafe situations. |
| emerging | I can identify some obvious forms of abuse with help but miss subtle warning signs. |
| developing | I can recognise clear forms of abuse on my own but struggle with complex unsafe situations. |
| competent | I can independently identify different forms of abuse and recognise when situations are unsafe or harmful. |
| extending | I can identify abuse patterns and unsafe situations across different contexts with detailed reasoning. |

- self-check: Can I explain why this situation is unsafe without help from others?
- self-check: Am I able to spot warning signs even when they're not obvious?

_Feedback moves by level:_
- **no_evidence**
  - Provide clear examples of safe versus unsafe situations
  - Use visual aids to highlight obvious warning signs
- **emerging**
  - Guide students to notice subtle indicators through questioning
  - Practice with scenarios that have less obvious warning signs
- **developing**
  - Present complex scenarios for analysis and discussion
  - Encourage reasoning about why situations might be harmful
- **competent**
  - Challenge with diverse contexts and cultural situations
  - Ask students to explain patterns they notice across different scenarios

##### Understanding Rights and Support Systems — `cluster_04_lt_02`

**Definition.** I can explain personal rights, legal protections, and how to seek help when safety is compromised.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0012_item_01`, `blk_0015_item_01`, `blk_0114_item_01`, `blk_0114_item_03`, `blk_0220_item_01`, `blk_0220_item_02`, `blk_0229_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify my basic rights and describe who to tell when I feel unsafe. |
| End of Secondary | I can explain personal rights, legal protections, and evaluate appropriate support systems when safety is compromised. |

**Criterion rubric** — stability `rubric_unreliable`, quality gate **FAIL**.

_Gate failures:_ rubric_generation_failed

_Competent-framing judge:_ `error` — no structural signature reached 2/3 agreement; signatures=[(('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'describe'), ('competent', 'within_limit', 'describe'), ('extending', 'within_limit', 'apply'), ('competent_scope', 'unscoped')), (('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'describe'), ('competent', 'within_limit', 'describe'), ('extending', 'within_limit', 'analyse'), ('competent_scope', 'unscoped')), (('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'describe'), ('competent', 'within_limit', 'describe'), ('extending', 'within_limit', 'apply'), ('competent_scope', 'scoped'))]

| Level | Descriptor |
|---|---|
| no_evidence |  |
| emerging |  |
| developing |  |
| competent |  |
| extending |  |

##### Maintaining Personal Safety — `cluster_04_lt_03`

**Definition.** The student practises protective behaviours and actively seeks help to keep themselves and others safe.

**Knowledge type:** Type 3. **Assessment route:** `multi_informant_observation`. **Stability:** `stable`.

**KUD items covered:** `blk_0012_item_04`

**Observation protocol** — stability `stable`, Mode 3 gate **PASS**.

_Prerequisites (knowledge-contingent Type 3):_ `Recognising Abuse and Unsafe Situations`, `Understanding Rights and Support Systems`

**End of Primary**

- The student tells a trusted adult when they feel unsafe or uncomfortable in a situation
- The student uses clear body language and words to say no when someone makes them feel uncomfortable
- The student stays close to safe adults in unfamiliar environments or when meeting new people

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Primary):_ Think about one relationship in your life — with a friend, family member, or classmate. What makes it feel safe and kind? Is there anything you would like to be different?

**End of Secondary**

- The student removes themselves from situations they recognise as potentially harmful or exploitative
- The student actively intervenes or seeks immediate help when they observe peers in unsafe situations
- The student maintains consistent protective behaviours across different social contexts including online interactions

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Secondary):_ Think about a situation this term where you had to make a decision about a relationship or your own wellbeing. What did you consider, and what would you do differently now?

**Parent / caregiver prompts**

- What have you noticed about how your child responds when they feel uncomfortable or unsafe at home or in the community?
- When has your child come to you or another trusted adult for help with a situation that worried them?
- How does your child react when they see someone else being treated unfairly or in a way that seems wrong?

**Developmental conversation protocol.** The conversation explores specific instances where the student has practised protective behaviours, identifying what helped them recognise unsafe situations and how they sought or provided help. Discussion includes planning for future scenarios and reinforcing the student's growing confidence in maintaining safety for themselves and others.

### Friendship Development and Management — `cluster_05`

**Definition.** The ability to form, maintain, and navigate challenges in healthy friendships.

**Dominant knowledge type:** Type 1. **Stability:** `stable`. **Source lines:** L67-81. **KUD items:** 7.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0035_item_01` | Type 1 | understand | How people choose and make friends |
| `blk_0037_item_01` | Type 1 | understand | That healthy friendships are positive and welcoming towards others, and do not make others feel lonely or excluded |
| `blk_0037_item_02` | Type 2 | do_skill | Skills for developing caring, kind friendships |
| `blk_0039_item_01` | Type 1 | know | That most people feel lonely sometimes, and that there is no shame in feeling lonely or talking about it. |
| `blk_0041_item_01` | Type 1 | know | The characteristics of friendships that lead to happiness and security, including mutual respect, honesty, trustworthiness, loyalty, kindness, generosity, trust, sharing interests and experiences, and |
| `blk_0043_item_01` | Type 1 | understand | Most friendships have ups and downs, and that these can often be worked through so that the friendship is repaired or even strengthened. |
| `blk_0046_item_01` | Type 2 | do_skill | how to recognise when a friendship is making them feel unhappy or uncomfortable, and how to get support when needed |

#### Learning Targets

##### Understanding Healthy Friendship Characteristics — `cluster_05_lt_01`

**Definition.** I can identify and explain the key characteristics that make friendships positive, caring, and supportive.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0035_item_01`, `blk_0037_item_01`, `blk_0039_item_01`, `blk_0041_item_01`, `blk_0043_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify key characteristics that make friendships positive and caring with guidance. |
| End of Secondary | I can explain and justify the essential characteristics that create supportive friendships across different contexts. |

**Criterion rubric** — stability `rubric_unreliable`, quality gate **FAIL**.

_Gate failures:_ rubric_generation_failed

_Competent-framing judge:_ `error` — no structural signature reached 2/3 agreement; signatures=[(('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'recognise'), ('competent', 'within_limit', 'recognise'), ('extending', 'within_limit', 'apply'), ('competent_scope', 'unscoped')), (('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'recognise'), ('competent', 'within_limit', 'recognise'), ('extending', 'within_limit', 'analyse'), ('competent_scope', 'scoped')), (('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'recognise'), ('competent', 'within_limit', 'recognise'), ('extending', 'within_limit', 'apply'), ('competent_scope', 'scoped'))]

| Level | Descriptor |
|---|---|
| no_evidence |  |
| emerging |  |
| developing |  |
| competent |  |
| extending |  |

##### Developing and Managing Friendship Skills — `cluster_05_lt_02`

**Definition.** I can apply strategies to build caring friendships and respond appropriately when friendships face challenges.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**Prerequisites:** `cluster_05_lt_01`

**KUD items covered:** `blk_0037_item_02`, `blk_0046_item_01`

**Band progression** — stability `band_statements_unstable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can apply basic strategies to build caring friendships and respond to simple friendship challenges. |
| End of Secondary | I can independently apply sophisticated strategies to build caring friendships and respond effectively to complex friendship challenges. |

**Criterion rubric** — stability `rubric_unstable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as demonstrated independently and can stand alone as evidence that the learning target is met.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to apply friendship strategies. |
| emerging | With support, attempts some friendship strategies but application is inconsistent or inappropriate. |
| developing | Independently applies basic friendship strategies but struggles when challenges become complex or unfamiliar. |
| competent | Independently applies effective strategies to build caring friendships and responds appropriately to friendship challenges. |
| extending | Transfers friendship strategies to diverse contexts and helps others navigate complex friendship situations. |

_Prerequisite edges:_
- `cluster_05_lt_01` [ontological_prerequisite/high] — Cannot apply friendship strategies without understanding what healthy friendships look like.
- `cluster_02_lt_01` [pedagogical_sequencing/medium] — Foundational relationship skills provide the base for more specific friendship management strategies.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Students share what makes a good friend and identify friendship challenges they've experienced
- stage: Students brainstorm strategies for building friendships and handling conflicts
- stage: Students sort strategies from simple to complex and discuss when each might be used
- stage: Students create criteria for what friendship success looks like at different levels
- prompt: What does it look like when someone is really good at making and keeping friends?
- prompt: What strategies help when friendships get difficult or complicated?
- prompt: How can you tell if your friendship strategies are working well?
- anchor-examples guidance: Choose examples that show clear progression from basic friendship behaviors to complex social navigation and peer support.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet tried to use strategies for building or maintaining friendships. |
| emerging | I can try some friendship strategies with help but don't always use them at the right time. |
| developing | I can use basic friendship strategies on my own but need help with complicated friendship problems. |
| competent | I can use effective strategies to build caring friendships and handle friendship challenges appropriately. |
| extending | I can use friendship strategies in many different situations and help others with their friendship challenges. |

- self-check: Can I handle friendship problems without always needing adult help?
- self-check: Do I use different strategies depending on the friendship situation?

_Feedback moves by level:_
- **no_evidence**
  - Model one simple friendship strategy and practice it together
  - Help identify one specific friendship goal to work toward
- **emerging**
  - Practice timing when to use specific friendship strategies
  - Provide prompts before social situations to remind of available strategies
- **developing**
  - Discuss how to adapt basic strategies for more complex situations
  - Practice problem-solving steps for unfamiliar friendship challenges
- **competent**
  - Explore how friendship strategies work in different social contexts
  - Create opportunities to mentor others with friendship skills

### Interpersonal Skills and Boundaries — `cluster_06`

**Definition.** The ability to balance needs, set boundaries, and communicate assertively in relationships.

**Dominant knowledge type:** Type 2. **Stability:** `stable`. **Source lines:** L87-249. **KUD items:** 10.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0050_item_01` | Type 2 | do_skill | How to balance the needs and wishes of different people in relationships and why this can be complicated |
| `blk_0052_item_01` | Type 3 | do_disposition | Setting and respecting healthy boundaries in relationships with friends, family, peers and adults |
| `blk_0054_item_01` | Type 2 | do_skill | how to be assertive and express needs and boundaries |
| `blk_0054_item_02` | Type 2 | do_skill | how to manage feelings, including disappointment and frustration |
| `blk_0056_item_01` | Type 1 | understand | The difference between being assertive and being controlling, and conversely the difference between being kind to other people and neglecting your own needs |
| `blk_0058_item_01` | Type 3 | do_disposition | respecting others, including those who are different (for example, physically, in character, personality or backgrounds), or make different choices, or have different preferences or beliefs |
| `blk_0060_item_01` | Type 2 | do_skill | Take practical steps and develop skills in a range of different contexts to improve or support their relationships |
| `blk_0063_item_01` | Type 2 | do_skill | think about how they foster their own self-esteem and build a strong sense of their own identity, including through developing skills and interests |
| `blk_0086_item_01` | Type 1 | understand | What sorts of boundaries are appropriate in friendships with peers and others (including online). This can include learning about boundaries in play and in negotiations about space, toys, books, resou |
| `blk_0146_item_01` | Type 2 | do_skill | skills for communicating respectfully within relationships and with strangers, including in situations of conflict |

#### Learning Targets

##### Assertive Communication and Boundary Setting — `cluster_06_lt_01`

**Definition.** I can communicate assertively to express needs and set appropriate boundaries while managing my emotions effectively.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**KUD items covered:** `blk_0050_item_01`, `blk_0054_item_01`, `blk_0054_item_02`, `blk_0056_item_01`, `blk_0060_item_01`, `blk_0063_item_01`, `blk_0086_item_01`, `blk_0146_item_01`

_No band statements produced._

##### Respectful Relationship Practices — `cluster_06_lt_02`

**Definition.** The student practises respectful communication and maintains healthy boundaries across diverse relationships and contexts.

**Knowledge type:** Type 3. **Assessment route:** `multi_informant_observation`. **Stability:** `stable`.

**KUD items covered:** `blk_0052_item_01`, `blk_0058_item_01`

**Observation protocol** — stability `stable`, Mode 3 gate **PASS**.

_Prerequisites (knowledge-contingent Type 3):_ `Assertive Communication and Boundary Setting`

**End of Primary**

- The student uses polite language and listens when others are speaking in group activities
- The student says no clearly when uncomfortable with physical contact or requests from peers
- The student asks permission before borrowing items or entering others' personal spaces

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Primary):_ Think about one relationship in your life — with a friend, family member, or classmate. What makes it feel safe and kind? Is there anything you would like to be different?

**End of Secondary**

- The student maintains respectful communication during disagreements across different social groups
- The student consistently enforces personal boundaries while respecting others' limits in various relationship contexts
- The student navigates complex social situations by balancing assertiveness with consideration for others' perspectives

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Secondary):_ Think about a situation this term where you had to make a decision about a relationship or your own wellbeing. What did you consider, and what would you do differently now?

**Parent / caregiver prompts**

- What have you noticed about how your child communicates when they disagree with family members or friends?
- When your child feels uncomfortable with something someone asks them to do, how do they typically respond?
- Have you observed your child showing respect for others' personal space, belongings, or privacy at home or in social situations?

**Developmental conversation protocol.** The conversation explores specific examples of respectful communication and boundary-setting the student has demonstrated, connecting observed behaviours to their understanding of healthy relationship dynamics across different contexts.

### Bullying Prevention and Response — `cluster_07`

**Definition.** The ability to recognise, challenge, and respond to bullying and stereotyping behaviours.

**Dominant knowledge type:** Type 2. **Stability:** `cluster_unstable`. **Source lines:** L109-252. **KUD items:** 8.

_Stability diagnostics:_
- dominant_type_drift_run3: Type 2→Type 1

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0065_item_01` | Type 1 | know | responsibilities of bystanders (primarily reporting bullying to an adult), and how to get help |
| `blk_0067_item_01` | Type 1 | know | What a stereotype is, how stereotypes can be unfair, negative, destructive or lead to bullying |
| `blk_0067_item_02` | Type 2 | do_skill | How to challenge a stereotype |
| `blk_0069_item_01` | Type 2 | do_skill | How to seek help when needed, including when they are concerned about violence, harm, or when they are unsure who to trust. |
| `blk_0148_item_01` | Type 1 | know | The different types of bullying (including online bullying) |
| `blk_0148_item_02` | Type 1 | understand | The impact of bullying |
| `blk_0148_item_03` | Type 2 | do_skill | How and where to get help regarding bullying |
| `blk_0148_item_04` | Type 3 | do_disposition | Responsibilities of bystanders to report bullying |

#### Learning Targets

##### Understanding Bullying and Stereotypes — `cluster_07_lt_01`

**Definition.** I can identify different types of bullying and stereotypes and explain their harmful impacts.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0065_item_01`, `blk_0067_item_01`, `blk_0148_item_01`, `blk_0148_item_02`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify different types of bullying and stereotypes and describe why they are harmful. |
| End of Secondary | I can identify different types of bullying and stereotypes and explain their complex psychological and social impacts. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as demonstrated independently and accurately, standing alone as evidence that the learning target is met.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify bullying types or stereotypes. |
| emerging | With support, names some bullying types but explanations are incomplete or inaccurate. |
| developing | Independently identifies basic bullying types and stereotypes but explanations of harmful impacts lack detail. |
| competent | Independently identifies different types of bullying and stereotypes and explains their harmful impacts accurately and clearly. |
| extending | Analyses complex bullying scenarios and connects stereotypes to broader patterns of discrimination and harm. |

_Prerequisite edges:_
- `cluster_05_lt_01` [pedagogical_sequencing/medium] — Understanding positive friendship characteristics helps distinguish bullying from normal relationship challenges.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Students share experiences or observations about unfair treatment to activate prior knowledge.
- stage: Guide students to categorize different types of harmful behaviors they've identified.
- stage: Students discuss and define what makes these behaviors harmful to individuals and groups.
- stage: Collaboratively create criteria for recognizing and explaining different types of bullying and stereotypes.
- prompt: What are different ways people can be mean or unfair to others?
- prompt: How do these behaviors affect the people who experience them?
- prompt: What makes someone really good at spotting and explaining these problems?
- anchor-examples guidance: Select clear scenarios that show distinct bullying types and obvious stereotypes with visible harmful effects on individuals or groups.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet attempted to identify types of bullying or stereotypes. |
| emerging | I can name some types of bullying with help but my explanations need work. |
| developing | I can identify basic types of bullying and stereotypes but need to add more detail about their harmful impacts. |
| competent | I can identify different types of bullying and stereotypes and clearly explain how they cause harm. |
| extending | I can analyze complex bullying situations and connect stereotypes to bigger patterns of discrimination. |

- self-check: Can I name specific types of bullying and stereotypes without help?
- self-check: Can I clearly explain how these behaviors harm people?

_Feedback moves by level:_
- **no_evidence**
  - Provide concrete examples of bullying scenarios to analyze together.
  - Use visual aids or stories to help identify different harmful behaviors.
- **emerging**
  - Ask guiding questions to help elaborate on incomplete explanations.
  - Provide sentence starters for describing harmful impacts.
- **developing**
  - Prompt for specific details about how bullying affects victims emotionally and socially.
  - Encourage use of precise vocabulary to describe different stereotype categories.
- **competent**
  - Challenge to examine more complex scenarios with multiple bullying types.
  - Guide analysis of how stereotypes connect to larger social patterns.

##### Responding to Bullying and Stereotypes — `cluster_07_lt_02`

**Definition.** I can challenge stereotypes and seek appropriate help when bullying occurs.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**Prerequisites:** `cluster_07_lt_01`

**KUD items covered:** `blk_0067_item_02`, `blk_0069_item_01`, `blk_0148_item_03`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify stereotypes and tell a trusted adult when bullying happens to me or others. |
| End of Secondary | I can challenge stereotypes confidently and evaluate appropriate support strategies when responding to different bullying situations. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently' and 'effectively' without any hedging language or positioning it as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to challenge stereotypes or seek help. |
| emerging | With support, identifies some stereotypes or help-seeking options but responses are incomplete. |
| developing | Independently recognises stereotypes or identifies help sources but challenges or responses lack effectiveness. |
| competent | Independently challenges stereotypes effectively and seeks appropriate help when bullying occurs using suitable strategies and channels. |
| extending | Transfers challenging skills to novel contexts and advocates for others facing bullying situations. |

_Prerequisite edges:_
- `cluster_07_lt_01` [ontological_prerequisite/high] — Cannot challenge what you cannot identify or understand.
- `cluster_06_lt_01` [pedagogical_sequencing/medium] — Assertive communication skills support effective challenging of stereotypes.
- `cluster_09_lt_02` [pedagogical_sequencing/medium] — General help-seeking skills provide foundation for bullying-specific responses.

##### Bystander Responsibility — `cluster_07_lt_03`

**Definition.** The student enacts responsibility to report bullying and support others when witnessing harmful behaviour.

**Knowledge type:** Type 3. **Assessment route:** `multi_informant_observation`. **Stability:** `stable`.

**KUD items covered:** `blk_0148_item_04`

**Observation protocol** — stability `stable`, Mode 3 gate **PASS**.

_Prerequisites (knowledge-contingent Type 3):_ `Understanding Bullying and Stereotypes`

**End of Primary**

- The student tells a trusted adult when they see someone being hurt or excluded by others
- The student offers comfort or inclusion to peers who have been treated unkindly
- The student speaks up or gets help when witnessing name-calling or physical aggression

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Primary):_ Think about one relationship in your life — with a friend, family member, or classmate. What makes it feel safe and kind? Is there anything you would like to be different?

**End of Secondary**

- The student consistently intervenes safely or seeks appropriate support when observing bullying across different social contexts
- The student advocates for peers experiencing discrimination or harassment in both face-to-face and digital environments
- The student takes initiative to create inclusive spaces and challenge harmful behaviour without prompting

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Secondary):_ Think about a situation this term where you had to make a decision about a relationship or your own wellbeing. What did you consider, and what would you do differently now?

**Parent / caregiver prompts**

- What have you noticed about how your child responds when they see others being treated unfairly or unkindly?
- Has your child mentioned helping classmates or friends who were having difficulties with other children?
- When your child witnesses conflict or meanness, what actions have you observed them taking?

**Developmental conversation protocol.** The conversation explores specific instances where the student witnessed harmful behaviour and examines their decision-making process about when and how to intervene or seek help. Discussion includes identifying trusted adults, safe intervention strategies, and reflecting on the impact of their bystander choices on school community wellbeing.

### Online Safety and Digital Citizenship — `cluster_08`

**Definition.** The ability to navigate online relationships safely and protect personal information in digital spaces.

**Dominant knowledge type:** Type 1. **Stability:** `stable`. **Source lines:** L120-338. **KUD items:** 40.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0073_item_01` | Type 1 | understand | That people should be respectful in online interactions, and that the same principles apply to online relationships as to face-to-face relationships, including where people are anonymous |
| `blk_0073_item_02` | Type 2 | do_skill | Strategies for avoiding putting pressure on others to share information and images online, and strategies for resisting peer pressure |
| `blk_0075_item_01` | Type 1 | know | awareness of the risks associated with people they have never met, including that people sometimes behave differently online, including pretending to be someone else, or pretending to be a child, and  |
| `blk_0075_item_02` | Type 2 | do_skill | how to critically evaluate their online relationships and sources of information |
| `blk_0075_item_03` | Type 2 | do_skill | how to recognise harmful content or harmful contact, and how to report this |
| `blk_0077_item_01` | Type 1 | know | That there is a minimum age for joining social media sites (currently 13), which protects children from inappropriate content or unsafe contact with older social media users, who may be strangers, inc |
| `blk_0079_item_01` | Type 1 | know | Understanding the importance of privacy and location settings to protect information online |
| `blk_0079_item_02` | Type 3 | do_disposition | The importance of exercising caution about sharing any information about themselves online |
| `blk_0081_item_01` | Type 1 | know | that once a picture or words has been circulated there is no way of deleting it everywhere and no control over where it ends up |
| `blk_0083_item_01` | Type 1 | know | where to go for advice and support when they feel worried or concerned about something they have seen or engaged with online |
| `blk_0164_item_01` | Type 1 | understand | The same expectations of behaviour apply in all contexts, including online |
| `blk_0166_item_01` | Type 1 | know | the importance of being cautious about sharing personal information online and of using privacy and location settings appropriately to protect information online |
| `blk_0166_item_02` | Type 1 | understand | the difference between public and private online spaces and related safety issues |
| `blk_0168_item_01` | Type 1 | know | Social media accounts may be fake and may post things which aren't real or have been created with AI |
| `blk_0168_item_02` | Type 1 | know | Social media users may say things in more extreme ways than they might in face-to-face situations |
| `blk_0168_item_03` | Type 1 | know | Some social media users present highly exaggerated or idealised profiles of themselves online |
| `blk_0170_item_01` | Type 1 | understand | Any material provided online might be circulated, and that once this has happened there is no way of controlling where it ends up |
| `blk_0170_item_02` | Type 1 | understand | The serious risks of sending material to others, including the law concerning the sharing of images |
| `blk_0170_item_03` | Type 3 | do_disposition | Not to provide material to others that they would not want to be distributed further and not to pass on personal material which is sent to them |
| `blk_0172_item_01` | Type 1 | know | That keeping or forwarding indecent or sexual images of someone under 18 is a crime, even if the photo is of themselves or of someone who has consented, and even if the image was created by the child  |
| `blk_0172_item_02` | Type 1 | understand | The potentially serious consequences of acquiring or generating indecent or sexual images of someone under 18, including the potential for criminal charges and severe penalties including imprisonment |
| `blk_0172_item_03` | Type 1 | know | How to seek support and that they will not be in trouble for asking for help, either at school or with the police, if an image of themselves has been shared |
| `blk_0172_item_04` | Type 1 | know | That sharing indecent images of people over 18 without consent is a crime |
| `blk_0174_item_01` | Type 2 | do_skill | What to do and how to report when they are concerned about material that has been circulated, including personal information, images or videos, and how to manage issues online |
| `blk_0176_item_01` | Type 1 | know | the prevalence of deepfakes including videos and photos |
| `blk_0176_item_02` | Type 1 | understand | how deepfakes can be used maliciously as well as for entertainment |
| `blk_0176_item_03` | Type 1 | understand | the harms that can be caused by deepfakes |
| `blk_0176_item_04` | Type 2 | do_skill | how to identify deepfakes |
| `blk_0178_item_01` | Type 1 | know | That the internet contains inappropriate and upsetting content, some of which is illegal, including unacceptable content that encourages misogyny, violence or use of weapons |
| `blk_0179_item_01` | Type 1 | know | Where to go for advice and support about something they have seen online |
| `blk_0179_item_02` | Type 1 | understand | That online content can present a distorted picture of the world and normalise or glamorise behaviours which are unhealthy and wrong |
| `blk_0183_item_01` | Type 2 | do_skill | How to identify when technology and social media is used as part of bullying, harassment, stalking, coercive and controlling behaviour, and other forms of abusive and/or illegal behaviour and how to s |
| `blk_0186_item_01` | Type 1 | understand | That pornography, and other online content, often presents a distorted picture of people and their sexual behaviours and can negatively affect how people behave towards sexual partners. This can affec |
| `blk_0189_item_01` | Type 1 | know | That websites may share personal data about their users, and information collected on their internet use, for commercial purposes (e.g. to enable targeted advertising). |
| `blk_0191_item_01` | Type 1 | know | That criminals can operate online scams, for example using fake websites or emails to extort money or valuable personal information. This information can be used to the detriment of the person or wide |
| `blk_0191_item_02` | Type 1 | know | About risks of sextortion |
| `blk_0191_item_03` | Type 2 | do_skill | how to identify online scams relating to sex |
| `blk_0191_item_04` | Type 2 | do_skill | how to seek support if they have been scammed or involved in sextortion |
| `blk_0193_item_01` | Type 1 | know | AI chatbots are an example of how AI is rapidly developing, and that these can pose risks by creating fake intimacy or offering harmful advice |
| `blk_0193_item_02` | Type 2 | do_skill | critically think about new types of technology as they appear online and how they might pose a risk |

#### Learning Targets

##### Understanding Digital Risks and Safety Principles — `cluster_08_lt_01`

**Definition.** I can identify online risks and explain safety principles for protecting personal information and navigating digital relationships.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0073_item_01`, `blk_0075_item_01`, `blk_0077_item_01`, `blk_0079_item_01`, `blk_0081_item_01`, `blk_0083_item_01`, `blk_0164_item_01`, `blk_0166_item_01`, `blk_0166_item_02`, `blk_0168_item_01`, `blk_0168_item_02`, `blk_0168_item_03`, `blk_0170_item_01`, `blk_0170_item_02`, `blk_0172_item_01`, `blk_0172_item_02`, `blk_0172_item_03`, `blk_0172_item_04`, `blk_0176_item_01`, `blk_0176_item_02`, `blk_0176_item_03`, `blk_0178_item_01`, `blk_0179_item_01`, `blk_0179_item_02`, `blk_0186_item_01`, `blk_0189_item_01`, `blk_0191_item_01`, `blk_0191_item_02`, `blk_0193_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify basic online risks and explain simple safety rules for protecting personal information. |
| End of Secondary | I can analyse complex digital risks and justify comprehensive safety principles for protecting information and managing relationships online. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as demonstrated independently and comprehensively, standing alone as evidence that the learning target is met.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify online risks or safety principles. |
| emerging | With support, names some online risks but explanations are incomplete or inaccurate. |
| developing | Independently identifies basic online risks and explains simple safety principles with minor gaps. |
| competent | Independently identifies diverse online risks and explains comprehensive safety principles for protecting personal information and navigating digital relationships. |
| extending | Applies safety principles to novel scenarios and evaluates emerging digital risks beyond standard contexts. |

_Prerequisite edges:_
- `cluster_01_lt_02` [pedagogical_sequencing/medium] — Understanding personal boundaries supports recognizing digital boundary violations and privacy needs.
- `cluster_04_lt_01` [pedagogical_sequencing/medium] — Recognizing unsafe situations generally helps identify when online interactions become harmful or inappropriate.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Students brainstorm what could go wrong online from their own experiences.
- stage: Groups categorize risks and discuss what makes information personal or private.
- stage: Class develops safety rules for different online situations.
- stage: Students test safety principles against real-world scenarios.
- stage: Groups refine and finalize comprehensive safety guidelines.
- prompt: What online experiences have made you feel unsafe or uncomfortable?
- prompt: How do you decide what information is safe to share online?
- prompt: What would you do if someone online asked for your personal details?
- prompt: How can you tell if an online relationship is healthy or concerning?
- anchor-examples guidance: Select student work samples that show clear progression from basic risk awareness to comprehensive safety application across different digital contexts.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet identified online risks or explained safety principles. |
| emerging | I can name some online risks with help but my explanations need work. |
| developing | I can identify basic online risks and explain simple safety principles on my own. |
| competent | I can identify many different online risks and explain complete safety principles for protecting my information and relationships. |
| extending | I can apply safety principles to new situations and evaluate risks beyond typical online scenarios. |

- self-check: Can I explain why this online situation might be risky?
- self-check: Do my safety principles cover both personal information and digital relationships?

_Feedback moves by level:_
- **no_evidence**
  - Provide concrete examples of common online risks students encounter.
  - Guide students to reflect on their own digital experiences.
- **emerging**
  - Ask students to explain their thinking about specific risks.
  - Connect incomplete ideas to real-world consequences.
- **developing**
  - Challenge students to consider less obvious risks.
  - Push for more detailed explanations of safety principles.
- **competent**
  - Present novel digital scenarios for safety principle application.
  - Encourage evaluation of emerging technologies and their risks.

##### Evaluating and Responding to Online Threats — `cluster_08_lt_02`

**Definition.** I can critically evaluate online relationships and content, identify harmful situations, and apply appropriate response strategies.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**Prerequisites:** `cluster_08_lt_01`

**KUD items covered:** `blk_0073_item_02`, `blk_0075_item_02`, `blk_0075_item_03`, `blk_0174_item_01`, `blk_0176_item_04`, `blk_0183_item_01`, `blk_0191_item_03`, `blk_0191_item_04`, `blk_0193_item_02`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify harmful online situations and explain basic strategies to respond safely. |
| End of Secondary | I can critically evaluate complex online relationships and content to justify appropriate response strategies across varied digital contexts. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated and independently achieved at the learning target's level of demand without hedging language or positioning it as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to evaluate online threats or responses. |
| emerging | With support, identifies some obvious online risks but responses are inappropriate or incomplete. |
| developing | Independently recognises clear online threats but struggles to evaluate complex situations or select effective responses. |
| competent | Critically evaluates online relationships and content, identifies harmful situations accurately, and applies appropriate response strategies independently. |
| extending | Transfers evaluation skills to novel online contexts and helps others develop threat recognition capabilities. |

_Prerequisite edges:_
- `cluster_08_lt_01` [ontological_prerequisite/high] — Cannot evaluate online threats without understanding digital risks and safety principles.
- `cluster_04_lt_01` [pedagogical_sequencing/medium] — General ability to recognise unsafe situations supports online threat identification.
- `cluster_09_lt_02` [pedagogical_sequencing/medium] — Help-seeking skills are typically established before applying response strategies to online threats.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Students share experiences of feeling uncertain or uncomfortable online without naming specifics
- stage: Class brainstorms what makes online situations feel safe versus unsafe
- stage: Students work in groups to categorise different types of online threats from general to complex
- stage: Groups develop response strategies for each threat category
- stage: Class creates shared language for describing levels of threat evaluation skills
- prompt: What are some warning signs that an online situation might not be safe?
- prompt: How do you decide whether to respond, report, or remove yourself from an online situation?
- prompt: What would it look like to help a friend recognise online threats?
- anchor-examples guidance: Select scenarios that progress from obvious scams to subtle manipulation tactics and include both relationship-based and content-based threats.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet shown that I can evaluate online threats or plan responses |
| emerging | I can spot obvious online risks with help but my responses need improvement |
| developing | I can recognise clear online threats on my own but find complex situations challenging |
| competent | I can evaluate online relationships and content critically and choose appropriate responses |
| extending | I can apply my evaluation skills to new online situations and help others recognise threats |

- self-check: Can I explain why a specific online situation feels unsafe and what I would do about it?
- self-check: Am I able to help others think through online safety decisions?

_Feedback moves by level:_
- **no_evidence**
  - Provide concrete examples of online threats and walk through identification together
  - Use guided questions to help recognise one obvious warning sign
- **emerging**
  - Practice identifying threats in scenarios with decreasing support
  - Focus on one appropriate response strategy at a time
- **developing**
  - Present complex scenarios that require deeper analysis of multiple factors
  - Practice evaluating the effectiveness of different response options
- **competent**
  - Introduce novel online contexts that require transfer of existing skills
  - Provide opportunities to mentor others in threat recognition

##### Practising Digital Caution and Responsibility — `cluster_08_lt_03`

**Definition.** The student practises cautious sharing of personal information and responsible handling of digital content across online contexts.

**Knowledge type:** Type 3. **Assessment route:** `multi_informant_observation`. **Stability:** `stable`.

**KUD items covered:** `blk_0079_item_02`, `blk_0170_item_03`

**Observation protocol** — stability `observation_indicators_unstable`, Mode 3 gate **PASS**.

_Prerequisites (knowledge-contingent Type 3):_ `Understanding Digital Risks and Safety Principles`

**End of Primary**

- The student pauses before sharing personal details in digital activities and asks for adult guidance
- The student demonstrates careful consideration when posting or sharing content online, often checking with others first

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Primary):_ Think about one relationship in your life — with a friend, family member, or classmate. What makes it feel safe and kind? Is there anything you would like to be different?

**End of Secondary**

- The student consistently applies privacy settings and information-sharing protocols across different digital platforms
- The student demonstrates thoughtful evaluation of digital content before sharing or responding, considering potential consequences
- The student takes initiative to protect others' digital privacy and challenges inappropriate sharing when encountered

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Secondary):_ Think about a situation this term where you had to make a decision about a relationship or your own wellbeing. What did you consider, and what would you do differently now?

**Parent / caregiver prompts**

- What have you noticed about how your child approaches sharing photos, personal information, or content online at home?
- When your child encounters something concerning or inappropriate online, how do they typically respond or seek help?
- Have you observed your child thinking carefully about their digital footprint or considering how their online actions might affect others?

**Developmental conversation protocol.** The conversation explores specific instances where the student has demonstrated digital caution and responsibility, examining their decision-making process and identifying areas for continued growth in online citizenship.

### Trust and Safety Assessment — `cluster_09`

**Definition.** The ability to assess trustworthiness, recognise unsafe situations, and seek appropriate help.

**Dominant knowledge type:** Type 2. **Stability:** `cluster_unstable`. **Source lines:** L148-357. **KUD items:** 16.

_Stability diagnostics:_
- dominant_type_drift_run3: Type 2→Type 1

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0088_item_01` | Type 1 | understand | that it is not always right to keep secrets if they relate to being safe |
| `blk_0090_item_01` | Type 1 | understand | the differences between appropriate and inappropriate or unsafe contact, including physical contact |
| `blk_0092_item_01` | Type 2 | do_skill | How to respond safely and appropriately to adults they may encounter (in all contexts, including online), including those they do and do not know |
| `blk_0094_item_01` | Type 2 | do_skill | recognising who to trust and who not to trust |
| `blk_0096_item_01` | Type 1 | know | The vocabulary needed to report abuse, concerns about something seen online or experienced in real life, or feelings of being unsafe or feeling bad about any adult. |
| `blk_0096_item_02` | Type 2 | do_skill | How to report abuse, concerns about something seen online or experienced in real life, or feelings of being unsafe or feeling bad about any adult. |
| `blk_0096_item_03` | Type 3 | do_disposition | The confidence needed to report abuse, concerns about something seen online or experienced in real life, or feelings of being unsafe or feeling bad about any adult. |
| `blk_0098_item_01` | Type 1 | know | Where to get advice e.g. family, school and/or other sources |
| `blk_0135_item_01` | Type 2 | do_skill | Judge when a relationship is unsafe and where to seek help when needed, including when pupils are concerned about violence, harm, or when they are unsure who to trust |
| `blk_0201_item_01` | Type 2 | do_skill | how to determine whether other children, adults or sources of information are trustworthy, how to judge when a relationship is unsafe (and recognise this in the relationships of others) |
| `blk_0201_item_02` | Type 2 | do_skill | how to seek help or advice, including reporting concerns about others, if needed |
| `blk_0203_item_01` | Type 1 | know | Ways of seeking help when needed and how to report harmful behaviour |
| `blk_0203_item_02` | Type 1 | understand | That there are strategies they can use to increase their safety, and that this does not mean they will be blamed if they are victims of harmful behaviour |
| `blk_0203_item_03` | Type 1 | understand | That in some situations a person might appear trustworthy but have harmful intentions |
| `blk_0203_item_04` | Type 2 | do_skill | How to increase their personal safety in public spaces, including when socialising with friends, family, the wider community or strangers |
| `blk_0203_item_05` | Type 3 | do_disposition | Trusting their instincts when something doesn't feel right |

#### Learning Targets

##### Recognising Trust and Safety Risks — `cluster_09_lt_01`

**Definition.** I can identify trustworthy versus untrustworthy people and recognise unsafe situations or inappropriate contact.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**KUD items covered:** `blk_0090_item_01`, `blk_0092_item_01`, `blk_0094_item_01`, `blk_0135_item_01`, `blk_0201_item_01`, `blk_0203_item_03`, `blk_0203_item_04`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify trustworthy people and recognise when situations or contact feel unsafe with adult support. |
| End of Secondary | I can independently evaluate trustworthiness and analyse complex situations to identify potential safety risks and inappropriate contact. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently identifies' and 'recognises' without any hedging language or positioning as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify trustworthy people or unsafe situations. |
| emerging | With support, identifies some obvious trust or safety indicators but makes frequent errors. |
| developing | Independently recognises clear trustworthy behaviours and obvious unsafe situations but misses subtle warning signs. |
| competent | Independently identifies trustworthy versus untrustworthy people and recognises unsafe situations or inappropriate contact across various contexts. |
| extending | Applies trust and safety recognition skills to complex or ambiguous situations with sophisticated reasoning. |

_Prerequisite edges:_
- `cluster_01_lt_01` [ontological_prerequisite/high] — Understanding private body parts is essential for recognising inappropriate contact.
- `cluster_01_lt_02` [pedagogical_sequencing/medium] — Understanding personal boundaries supports recognition of boundary violations by others.

##### Seeking Help and Reporting Concerns — `cluster_09_lt_02`

**Definition.** I can report safety concerns and seek appropriate help using proper vocabulary and channels.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**KUD items covered:** `blk_0088_item_01`, `blk_0096_item_01`, `blk_0096_item_02`, `blk_0098_item_01`, `blk_0201_item_02`, `blk_0203_item_01`, `blk_0203_item_02`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify trusted adults and report safety concerns using simple vocabulary. |
| End of Secondary | I can evaluate appropriate reporting channels and communicate complex safety concerns with precise vocabulary. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently' and 'consistently' indicating complete mastery of the learning target.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to report concerns or seek help. |
| emerging | With support, attempts to communicate safety concerns using limited vocabulary or inappropriate channels. |
| developing | Independently identifies need for help but uses unclear vocabulary or selects inappropriate reporting channels. |
| competent | Independently reports safety concerns and seeks appropriate help using clear vocabulary and proper channels consistently. |
| extending | Adapts reporting strategies to complex situations and guides others in seeking appropriate help effectively. |

_Prerequisite edges:_
- `cluster_09_lt_01` [ontological_prerequisite/high] — Must recognise unsafe situations before being able to report them.
- `cluster_04_lt_01` [ontological_prerequisite/high] — Must identify abuse and unsafe situations to know what requires reporting.
- `cluster_04_lt_02` [pedagogical_sequencing/medium] — Understanding rights and support systems typically precedes learning specific reporting procedures.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Discuss what safety concerns look like in different settings
- stage: Identify who we can turn to for help in various situations
- stage: Practice using clear words to describe problems
- stage: Explore different ways to report concerns based on the situation
- prompt: What are some safety concerns you might encounter at school or home?
- prompt: Who are the trusted adults you can talk to when you need help?
- prompt: How can you explain a problem clearly so others understand?
- anchor-examples guidance: Choose examples that show different types of safety concerns and various appropriate reporting channels students might actually encounter.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet tried to report concerns or ask for help. |
| emerging | I can try to tell someone about safety concerns with help. |
| developing | I can recognize when I need help but sometimes use unclear words or tell the wrong person. |
| competent | I can report safety concerns and ask for help using clear words and telling the right person. |
| extending | I can adjust how I report concerns based on different situations and help others know how to seek help. |

- self-check: Did I use clear words that help others understand my concern?
- self-check: Did I choose the right person or place to report my concern?

_Feedback moves by level:_
- **no_evidence**
  - Model simple ways to ask for help in safe situations
  - Practice identifying trusted adults together
- **emerging**
  - Provide sentence starters for reporting concerns
  - Help identify the most appropriate person to tell
- **developing**
  - Practice using specific vocabulary to describe different types of concerns
  - Review which channels work best for different situations
- **competent**
  - Present complex scenarios requiring adapted reporting strategies
  - Encourage peer mentoring opportunities

##### Trusting Safety Instincts — `cluster_09_lt_03`

**Definition.** The student practises trusting their instincts and maintains confidence when reporting safety concerns.

**Knowledge type:** Type 3. **Assessment route:** `multi_informant_observation`. **Stability:** `stable`.

**KUD items covered:** `blk_0096_item_03`, `blk_0203_item_05`

**Observation protocol** — stability `stable`, Mode 3 gate **PASS**.

_Prerequisites (knowledge-contingent Type 3):_ `Recognising Trust and Safety Risks`, `Seeking Help and Reporting Concerns`

**End of Primary**

- The student speaks up immediately when something feels wrong without waiting for adult permission
- The student maintains their position about safety concerns even when peers dismiss or question their worries
- The student approaches trusted adults with confidence when reporting incidents rather than appearing hesitant or apologetic

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Primary):_ Think about one relationship in your life — with a friend, family member, or classmate. What makes it feel safe and kind? Is there anything you would like to be different?

**End of Secondary**

- The student acts on safety instincts in unfamiliar social situations without seeking validation from others first
- The student persists in raising safety concerns through appropriate channels when initial reports are not taken seriously
- The student demonstrates unwavering confidence when supporting peers who express safety concerns

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Secondary):_ Think about a situation this term where you had to make a decision about a relationship or your own wellbeing. What did you consider, and what would you do differently now?

**Parent / caregiver prompts**

- When your child tells you something doesn't feel right about a situation, how do they express this and what do you notice about their confidence level?
- Have you observed your child standing firm about safety concerns even when others around them seem unconcerned or dismissive?
- What have you noticed about how your child approaches you or other trusted adults when they need to report something that worries them?

**Developmental conversation protocol.** The conversation explores specific instances where the student trusted their safety instincts and examines their confidence levels when reporting concerns. Teacher, student, and optionally parent discuss how the student's trust in their own judgment has developed and identify any barriers to confident reporting.

### Sex Education Framework — `cluster_10`

**Definition.** The ability to understand the educational framework and parental rights regarding sex education.

**Dominant knowledge type:** Type 1. **Stability:** `stable`. **Source lines:** L164-199. **KUD items:** 11.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0102_item_01` | Type 1 | know | Sex education is not compulsory in primary schools, but is recommended in years 5 and/or 6, in line with content about conception and birth, which forms part of the national curriculum for science |
| `blk_0102_item_02` | Type 1 | know | The national curriculum for science includes subject content in related areas, such as the main external body parts, the human body as it grows from birth to old age (including puberty) and reproducti |
| `blk_0102_item_03` | Type 1 | know | Schools may also cover human reproduction in the science curriculum, but where they do so, this should be in line with the factual description of conception in the science curriculum |
| `blk_0104_item_01` | Type 1 | know | Primary schools should consult parents about the content of anything that will be taught within sex education |
| `blk_0104_item_02` | Type 1 | know | Schools should offer parents support in talking to their children about sex education and how to link this with what is being taught in school |
| `blk_0104_item_03` | Type 1 | know | Parents have the right to request withdrawal from sex education |
| `blk_0107_item_01` | Type 1 | know | Knowledge needed in later life to keep themselves and others safe, and how to avoid sexually transmitted infections and unplanned pregnancies |
| `blk_0107_item_02` | Type 3 | do_disposition | Develop healthy, safe and nurturing relationships of all kinds |
| `blk_0110_item_01` | Type 3 | do_disposition | RSE will enable young people to make their own choices about whether or when to develop safe, fulfilling and healthy sexual relationships, once they reach the age of consent, and to resist pressure to |
| `blk_0112_item_01` | Type 2 | do_skill | discuss and critically evaluate complex relationship scenarios |
| `blk_0117_item_01` | Type 2 | do_skill | Use approaches such as distancing techniques, setting ground rules with the class to help manage sensitive discussion, and using question boxes to allow pupils to raise issues anonymously when teachin |

#### Learning Targets

### Healthy Romantic Relationships — `cluster_11`

**Definition.** The ability to understand and develop respectful, ethical romantic and sexual relationships.

**Dominant knowledge type:** Type 1. **Stability:** `stable`. **Source lines:** L235-273. **KUD items:** 14.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0139_item_01` | Type 1 | understand | The role of consent, trust, mutual respect, honesty, kindness, loyalty, shared interests and outlooks, generosity, boundaries, tolerance, privacy, and the management of conflict, reconciliation and en |
| `blk_0141_item_01` | Type 3 | do_disposition | treat others with kindness and respect, including in public spaces and including strangers |
| `blk_0141_item_02` | Type 1 | understand | understand the legal rights and responsibilities regarding equality, and that everyone is unique and equal |
| `blk_0143_item_01` | Type 1 | understand | The importance of self-esteem, independence and having a positive relationship with oneself, and how these characteristics support healthy relationships with others |
| `blk_0143_item_02` | Type 3 | do_disposition | Developing one's own interests, hobbies, friendship groups, and skills |
| `blk_0143_item_03` | Type 1 | understand | What it means to be treated with respect by others |
| `blk_0150_item_01` | Type 2 | do_skill | Skills for ending relationships or friendships with kindness and managing the difficult feelings that endings might bring, including disappointment, hurt or frustration |
| `blk_0152_item_01` | Type 1 | understand | Ethical behaviour goes beyond consent and involves kindness, care, attention to the needs and vulnerabilities of the other person, as well as an awareness of power dynamics |
| `blk_0152_item_02` | Type 1 | understand | Just because someone says yes to doing something, that doesn't automatically make it ethically ok |
| `blk_0154_item_01` | Type 1 | understand | How stereotypes, in particular stereotypes based on sex, gender reassignment, race, religion, sexual orientation or disability, can cause damage (e.g. how they might normalise non-consensual behaviour |
| `blk_0154_item_02` | Type 2 | do_skill | Recognise misogyny and other forms of prejudice |
| `blk_0156_item_01` | Type 1 | understand | How inequalities of power can impact behaviour within relationships, including sexual relationships. For example, how people who are disempowered can feel they are not entitled to be treated with resp |
| `blk_0158_item_01` | Type 1 | understand | How pornography can negatively influence sexual attitudes and behaviours by normalising harmful sexual behaviours and by disempowering some people, especially women, to feel a sense of autonomy over t |
| `blk_0160_item_01` | Type 2 | do_skill | Discuss how some sub-cultures might influence our understanding of sexual ethics, including the sexual norms endorsed by so-called "involuntary celibates" (incels) or online influencers |

#### Learning Targets

##### Understanding Healthy Relationship Foundations — `cluster_11_lt_01`

**Definition.** I can explain the key elements that create respectful, ethical romantic relationships including consent, boundaries, equality, and power dynamics.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0139_item_01`, `blk_0141_item_02`, `blk_0143_item_01`, `blk_0143_item_03`, `blk_0152_item_01`, `blk_0152_item_02`, `blk_0154_item_01`, `blk_0156_item_01`, `blk_0158_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify basic elements of respectful relationships including kindness, fairness, and listening to others. |
| End of Secondary | I can explain how consent, boundaries, equality, and power dynamics create respectful, ethical romantic relationships. |

**Criterion rubric** — stability `rubric_unreliable`, quality gate **FAIL**.

_Gate failures:_ rubric_generation_failed

_Competent-framing judge:_ `error` — no structural signature reached 2/3 agreement; signatures=[(('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'recognise'), ('competent', 'within_limit', 'describe'), ('extending', 'within_limit', 'analyse'), ('competent_scope', 'unscoped')), (('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'recognise'), ('competent', 'within_limit', 'describe'), ('extending', 'within_limit', 'apply'), ('competent_scope', 'unscoped')), (('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'describe'), ('competent', 'within_limit', 'describe'), ('extending', 'within_limit', 'apply'), ('competent_scope', 'unscoped'))]

| Level | Descriptor |
|---|---|
| no_evidence |  |
| emerging |  |
| developing |  |
| competent |  |
| extending |  |

##### Analysing Relationship Challenges and Influences — `cluster_11_lt_02`

**Definition.** I can evaluate how stereotypes, power imbalances, and cultural influences affect relationship dynamics and apply strategies for managing conflict and endings.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**Prerequisites:** `cluster_11_lt_01`

**KUD items covered:** `blk_0150_item_01`, `blk_0154_item_02`, `blk_0160_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify basic stereotypes and unfairness in relationships and describe simple strategies for resolving disagreements. |
| End of Secondary | I can evaluate how stereotypes, power imbalances, and cultural influences affect relationship dynamics and apply strategies for managing conflict and endings. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated at the learning target's level of demand without hedging language or positioning it as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to analyse relationship challenges or influences. |
| emerging | With support, identifies some stereotypes or influences but analysis lacks depth or accuracy. |
| developing | Independently identifies relationship challenges and influences but evaluation remains superficial or strategies are basic. |
| competent | Evaluates how stereotypes, power imbalances, and cultural influences affect relationship dynamics and applies effective strategies for managing conflict and endings. |
| extending | Transfers evaluation skills to complex scenarios and integrates multiple strategies for relationship challenges fluently. |

_Prerequisite edges:_
- `cluster_11_lt_01` [ontological_prerequisite/high] — Cannot evaluate relationship dynamics without understanding healthy relationship foundations.
- `cluster_07_lt_01` [pedagogical_sequencing/high] — Understanding stereotypes generally precedes analysing their specific impact on relationships.
- `cluster_02_lt_02` [pedagogical_sequencing/medium] — Managing basic relationship challenges builds foundation for analysing complex relationship dynamics.

##### Practising Respectful Interpersonal Conduct — `cluster_11_lt_03`

**Definition.** The student treats others with kindness and respect across all interactions while developing personal independence and interests.

**Knowledge type:** Type 3. **Assessment route:** `multi_informant_observation`. **Stability:** `stable`.

**KUD items covered:** `blk_0141_item_01`, `blk_0143_item_02`

**Observation protocol** — stability `stable`, Mode 3 gate **PASS**.

_Prerequisites (knowledge-contingent Type 3):_ `Understanding Healthy Relationship Foundations`

**End of Primary**

- The student consistently uses polite language and listens when others are speaking during group activities
- The student includes different classmates in games and activities without being prompted by adults
- The student maintains personal space and asks permission before touching others' belongings or engaging in physical contact

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Primary):_ Think about one relationship in your life — with a friend, family member, or classmate. What makes it feel safe and kind? Is there anything you would like to be different?

**End of Secondary**

- The student demonstrates respectful communication patterns in peer interactions while maintaining their own viewpoints and boundaries
- The student actively pursues individual interests and friendships independently of romantic relationships
- The student intervenes appropriately when witnessing disrespectful behaviour toward others in social settings

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Secondary):_ Think about a situation this term where you had to make a decision about a relationship or your own wellbeing. What did you consider, and what would you do differently now?

**Parent / caregiver prompts**

- What have you noticed about how your child treats friends and family members when they disagree or have different opinions?
- How does your child balance time with friends or romantic interests alongside their own hobbies and personal goals?
- When your child sees someone being treated unkindly, what do you observe about their response?

**Developmental conversation protocol.** The conversation explores observed patterns of respectful conduct across different relationships and settings, examining how the student maintains personal autonomy while treating others with consistent kindness and respect.

### Sexual Consent and Ethics — `cluster_12`

**Definition.** The ability to understand consent, communicate boundaries, and engage in ethical sexual decision-making.

**Dominant knowledge type:** Type 1. **Stability:** `cluster_unstable`. **Source lines:** L346-412. **KUD items:** 7.

_Stability diagnostics:_
- dominant_type_drift_run2: Type 1→Type 2
- dominant_type_drift_run3: Type 1→Type 2

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0197_item_01` | Type 2 | do_skill | How to recognise, respect and communicate consent and boundaries in relationships, including in early romantic relationships (in all contexts, including online) and early sexual relationships that mig |
| `blk_0197_item_02` | Type 1 | understand | That kindness and care for others requires more than just consent |
| `blk_0233_item_01` | Type 1 | know | Sex, for people who feel ready and are over the age of consent, can and should be enjoyable and positive |
| `blk_0235_item_01` | Type 1 | know | that many young people wait until they are older, and that people of all ages can enjoy intimate and romantic relationships without sex |
| `blk_0237_item_01` | Type 1 | know | Sexual consent can be given, withheld or removed at any time, even if initially given |
| `blk_0237_item_02` | Type 1 | know | Considerations that people might take into account prior to sexual activity include the law, faith and family values |
| `blk_0237_item_03` | Type 1 | understand | Kindness and care for others require more than just consent |

#### Learning Targets

##### Communicating Consent and Boundaries — `cluster_12_lt_01`

**Definition.** I can recognise, respect and communicate consent and boundaries in relationships including early romantic and sexual relationships.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**Prerequisites:** `cluster_01_lt_02`

**KUD items covered:** `blk_0197_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can recognise and communicate basic personal boundaries in friendships and family relationships. |
| End of Secondary | I can recognise, respect and clearly communicate consent and boundaries in romantic and sexual relationships. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently' and 'effectively' indicating complete mastery of the learning target.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to communicate consent or boundaries. |
| emerging | With support, identifies some consent concepts but communicates boundaries inconsistently or inaccurately. |
| developing | Communicates basic consent and boundaries in familiar situations but struggles with complex or unfamiliar relationship contexts. |
| competent | Independently recognises, respects and communicates consent and boundaries effectively in early romantic and sexual relationships. |
| extending | Transfers consent communication skills to novel contexts and supports others in understanding boundary dynamics. |

_Prerequisite edges:_
- `cluster_01_lt_02` [ontological_prerequisite/high] — Cannot communicate consent and boundaries without foundational boundary communication skills.
- `cluster_06_lt_01` [ontological_prerequisite/high] — Assertive communication is essential for effectively communicating consent and boundaries.
- `cluster_11_lt_01` [pedagogical_sequencing/high] — Understanding healthy relationship foundations typically precedes applying consent communication in romantic contexts.
- `cluster_12_lt_02` [ontological_prerequisite/high] — Cannot communicate sexual consent without understanding its fundamental principles.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Explore what consent and boundaries mean in different relationships
- stage: Identify what effective communication looks like in relationship scenarios
- stage: Examine how consent and boundaries apply in romantic and sexual contexts
- stage: Discuss how to support others with boundary understanding
- prompt: What does it mean to respect someone's boundaries in a relationship?
- prompt: How do we know when someone is giving clear consent?
- prompt: What makes boundary communication challenging in different situations?
- prompt: How can we help others understand consent and boundaries?
- anchor-examples guidance: Select scenarios that show clear progression from basic boundary recognition to complex relationship navigation and peer support situations.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet attempted to communicate consent or boundaries. |
| emerging | I can identify some consent concepts with support but communicate boundaries inconsistently. |
| developing | I can communicate basic consent and boundaries in familiar situations. |
| competent | I can independently recognise, respect and communicate consent and boundaries effectively in early romantic and sexual relationships. |
| extending | I can transfer consent communication skills to new contexts and support others in understanding boundary dynamics. |

- self-check: Can I clearly communicate my own boundaries and respect others' boundaries?
- self-check: Do I understand consent in different relationship contexts?
- self-check: Can I help others navigate consent and boundary situations?

_Feedback moves by level:_
- **no_evidence**
  - Provide clear examples of what consent and boundaries look like in relationships
  - Practice identifying boundary statements in simple scenarios
- **emerging**
  - Focus on consistent language for expressing boundaries
  - Practice recognising consent cues in structured activities
- **developing**
  - Explore boundary communication in more complex relationship scenarios
  - Discuss how consent applies differently across various relationship contexts
- **competent**
  - Apply consent and boundary skills to unfamiliar or challenging situations
  - Practice supporting peers through boundary-related discussions

##### Understanding Sexual Consent Principles — `cluster_12_lt_02`

**Definition.** I can explain the principles of sexual consent including that it can be given, withheld or removed at any time.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**Prerequisites:** `cluster_12_lt_01`

**KUD items covered:** `blk_0197_item_02`, `blk_0233_item_01`, `blk_0235_item_01`, `blk_0237_item_01`, `blk_0237_item_02`, `blk_0237_item_03`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can explain that people can say yes or no to physical contact and change their mind. |
| End of Secondary | I can explain the principles of sexual consent including that it can be given, withheld or removed at any time. |

**Criterion rubric** — stability `rubric_unstable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as demonstrated with accurate understanding, standing alone as evidence the learning target is met.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to explain sexual consent principles. |
| emerging | With support, identifies some consent concepts but explanations are incomplete or inaccurate. |
| developing | Explains basic consent principles but misses key aspects like withdrawal or timing flexibility. |
| competent | Explains that sexual consent can be given, withheld, or removed at any time with accurate understanding. |
| extending | Connects consent principles to broader ethical frameworks and real-world relationship scenarios. |

_Prerequisite edges:_
- `cluster_01_lt_02` [ontological_prerequisite/high] — Understanding personal boundaries is essential before grasping consent principles.
- `cluster_11_lt_01` [pedagogical_sequencing/high] — General relationship foundations including consent concepts typically precede specific sexual consent principles.
- `cluster_12_lt_01` [pedagogical_sequencing/medium] — Practical consent communication skills often develop alongside theoretical understanding.

### Sexual and Reproductive Health — `cluster_13`

**Definition.** The ability to understand contraception, pregnancy options, and maintain sexual health.

**Dominant knowledge type:** Type 1. **Stability:** `stable`. **Source lines:** L416-769. **KUD items:** 15.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0239_item_01` | Type 1 | understand | That all aspects of health can be affected by choices they make in sex and relationships, positively or negatively, e.g. physical, emotional, mental, sexual and reproductive health and wellbeing. |
| `blk_0242_item_01` | Type 1 | know | The facts about the full range of contraceptive choices, efficacy and options available, including male and female condoms |
| `blk_0242_item_02` | Type 2 | do_skill | Signposting towards medically accurate online information about sexual and reproductive health to support contraceptive decision-making |
| `blk_0244_item_01` | Type 1 | know | medically and legally accurate and impartial information on all pregnancy options, including keeping the baby, adoption, abortion and where to get further help |
| `blk_0246_item_01` | Type 1 | know | How risk can be reduced through safer sex including through condom use and the use and availability of HIV prevention drugs Pre-Exposure Prophylaxis (PrEP) and Post-Exposure Prophylaxis |
| `blk_0247_item_01` | Type 1 | know | Exposure Prophylaxis (PEP) and how and where to access them |
| `blk_0247_item_02` | Type 1 | understand | The importance of, and facts about, regular testing |
| `blk_0247_item_03` | Type 1 | understand | The role of stigma |
| `blk_0249_item_01` | Type 1 | know | The prevalence of STIs, the short and long term impact they can have on those who contract them and key facts about treatment. |
| `blk_0252_item_01` | Type 1 | know | How and where to seek support for concerns around sexual relationships including sexual violence or harms |
| `blk_0254_item_01` | Type 1 | know | Where to access confidential sexual and reproductive health advice and treatment |
| `blk_0254_item_02` | Type 2 | do_skill | How to counter misinformation about sexual and reproductive health, including signposting towards medically accurate information and further advice |
| `blk_0465_item_01` | Type 1 | know | period problems such as premenstrual syndrome; heavy menstrual bleeding; endometriosis; and polycystic ovary syndrome (PCOS) |
| `blk_0465_item_02` | Type 1 | understand | when to seek help from healthcare professionals |
| `blk_0467_item_01` | Type 1 | know | The facts about reproductive health, including fertility and menopause, and the potential impact of lifestyle on fertility for men and women |

#### Learning Targets

##### Understanding Sexual Health Knowledge — `cluster_13_lt_01`

**Definition.** I can explain contraceptive options, pregnancy choices, STI prevention, and reproductive health facts.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0239_item_01`, `blk_0242_item_01`, `blk_0244_item_01`, `blk_0246_item_01`, `blk_0247_item_01`, `blk_0247_item_02`, `blk_0247_item_03`, `blk_0249_item_01`, `blk_0252_item_01`, `blk_0254_item_01`, `blk_0465_item_01`, `blk_0465_item_02`, `blk_0467_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify basic facts about how babies are made and born with adult guidance. |
| End of Secondary | I can explain contraceptive methods, pregnancy options, STI prevention strategies, and reproductive health information accurately. |

**Criterion rubric** — stability `rubric_unreliable`, quality gate **FAIL**.

_Gate failures:_ rubric_generation_failed

_Competent-framing judge:_ `error` — no structural signature reached 2/3 agreement; signatures=[(('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'describe'), ('competent', 'within_limit', 'describe'), ('extending', 'within_limit', 'analyse'), ('competent_scope', 'scoped')), (('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'describe'), ('competent', 'within_limit', 'describe'), ('extending', 'within_limit', 'describe'), ('competent_scope', 'scoped')), (('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'describe'), ('competent', 'within_limit', 'describe'), ('extending', 'within_limit', 'apply'), ('competent_scope', 'scoped'))]

| Level | Descriptor |
|---|---|
| no_evidence |  |
| emerging |  |
| developing |  |
| competent |  |
| extending |  |

##### Applying Sexual Health Information Skills — `cluster_13_lt_02`

**Definition.** I can evaluate and signpost medically accurate sexual health information and counter misinformation effectively.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**Prerequisites:** `cluster_13_lt_01`

**KUD items covered:** `blk_0242_item_02`, `blk_0254_item_02`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify trusted sources for basic sexual health information with adult guidance. |
| End of Secondary | I can evaluate sexual health information sources independently and effectively counter misinformation with evidence. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently evaluates' and 'effectively counters' without any hedging language or positioning as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to evaluate sexual health information. |
| emerging | With support, identifies some accurate information but struggles to counter misinformation effectively. |
| developing | Independently evaluates basic sexual health information but inconsistently identifies or addresses misinformation. |
| competent | Independently evaluates medically accurate sexual health information and effectively counters misinformation with appropriate signposting. |
| extending | Transfers evaluation skills to complex contexts and proactively educates others about misinformation. |

_Prerequisite edges:_
- `cluster_13_lt_01` [ontological_prerequisite/high] — Cannot evaluate sexual health information without understanding the foundational knowledge being evaluated.
- `cluster_08_lt_02` [pedagogical_sequencing/medium] — Critical evaluation of online content provides transferable skills for evaluating health information.

**Supporting components** — stability `stable`.

_Co-construction plan:_
- stage: Students brainstorm what makes health information trustworthy or untrustworthy.
- stage: Students examine different sexual health sources and discuss quality indicators.
- stage: Students practice identifying misinformation and develop counter-strategies.
- stage: Students create criteria for evaluating information and helping others.
- stage: Students refine rubric levels based on their evaluation experiences.
- prompt: What clues tell you if sexual health information is reliable?
- prompt: How would you help someone who believes misinformation?
- prompt: What makes someone ready to teach others about information quality?
- anchor-examples guidance: Select diverse sexual health information sources ranging from clearly credible to obviously problematic, including social media posts and peer conversations that students commonly encounter.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet attempted to evaluate sexual health information. |
| emerging | I can identify some accurate information with help but struggle to counter misinformation effectively. |
| developing | I can evaluate basic sexual health information independently but inconsistently identify or address misinformation. |
| competent | I can independently evaluate medically accurate sexual health information and effectively counter misinformation with appropriate signposting. |
| extending | I can transfer evaluation skills to complex contexts and proactively educate others about misinformation. |

- self-check: Can I explain why this source is trustworthy or not?
- self-check: Would I feel confident helping a friend evaluate sexual health information?

_Feedback moves by level:_
- **no_evidence**
  - Provide a simple checklist for evaluating one sexual health source.
  - Model thinking aloud while evaluating information quality.
- **emerging**
  - Practice identifying red flags in misinformation with guided support.
  - Rehearse simple phrases for redirecting to accurate sources.
- **developing**
  - Compare multiple sources on the same topic to build consistency.
  - Practice addressing misinformation scenarios with peer feedback.
- **competent**
  - Apply evaluation skills to unfamiliar or complex sexual health topics.
  - Develop strategies for teaching evaluation skills to peers.

### Mental Health and Emotional Wellbeing — `cluster_14`

**Definition.** The ability to understand emotions, recognise mental health needs, and seek appropriate support.

**Dominant knowledge type:** Type 1. **Stability:** `stable`. **Source lines:** L448-633. **KUD items:** 29.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0259_item_01` | Type 1 | know | The benefits of physical activity, time outdoors, and helping others for health, wellbeing and happiness |
| `blk_0259_item_02` | Type 1 | know | Simple self-care techniques, including the importance of rest, time spent with friends and family, as well as hobbies, interests and community participation |
| `blk_0262_item_01` | Type 1 | know | The range and scale of emotions (e.g. happiness, sadness, anger, fear, surprise, nervousness) that they might experience in different situations |
| `blk_0262_item_02` | Type 1 | understand | That worrying and feeling down are normal, affect everyone at different times, and are not in themselves a sign of a mental health condition |
| `blk_0264_item_01` | Type 2 | do_skill | How to recognise feelings and use varied vocabulary to talk about their own and others' feelings |
| `blk_0266_item_01` | Type 2 | do_skill | How to judge whether what they are feeling and how they are behaving is appropriate and proportionate |
| `blk_0270_item_01` | Type 1 | understand | That bullying (including cyberbullying) has a negative and often lasting impact on mental wellbeing |
| `blk_0270_item_02` | Type 2 | do_skill | How to seek help for themselves or others when experiencing bullying impacts on mental wellbeing |
| `blk_0272_item_01` | Type 1 | know | that grief is a natural response to bereavement, and that everyone grieves differently |
| `blk_0274_item_01` | Type 1 | know | Who in school they should speak to if they are worried about their own or someone else's mental wellbeing or ability to control their emotions (including issues arising online) |
| `blk_0274_item_02` | Type 2 | do_skill | Recognising the triggers for seeking support for mental wellbeing concerns |
| `blk_0355_item_01` | Type 1 | know | recognising and talking about emotions |
| `blk_0355_item_02` | Type 3 | do_disposition | looking after one's own and others' wellbeing |
| `blk_0355_item_03` | Type 2 | do_skill | judging whether feelings or behaviour require support |
| `blk_0355_item_04` | Type 2 | do_skill | how to cope when things go wrong in life |
| `blk_0355_item_05` | Type 1 | understand | how to seek help from a trusted adult, including when they are concerned about another person |
| `blk_0357_item_01` | Type 1 | know | Staff need evidence-based training before addressing suicide directly with secondary aged pupils to ensure they have the knowledge and skills to do this safely |
| `blk_0357_item_02` | Type 2 | do_skill | Use language and content that is accurate, straightforward and appropriate when addressing suicide with pupils |
| `blk_0362_item_01` | Type 2 | do_skill | How to talk about their emotions accurately and sensitively, using appropriate vocabulary |
| `blk_0364_item_01` | Type 1 | understand | participation and volunteering or acts of kindness for mental wellbeing and happiness |
| `blk_0366_item_01` | Type 1 | understand | understand what makes them feel happy and what makes them feel unhappy |
| `blk_0366_item_02` | Type 1 | understand | recognising that loneliness can be for most people an inevitable part of life at times and is not something of which to be ashamed |
| `blk_0368_item_01` | Type 1 | understand | That worrying and feeling down are normal, can affect everyone at different times and are not in themselves a sign of a mental health condition, and that managing those feelings can be helped by seein |
| `blk_0370_item_01` | Type 1 | know | Factual information about the prevalence and characteristics of common types of mental ill health and more serious mental health conditions |
| `blk_0370_item_02` | Type 1 | understand | The distinction between normal feelings and mental health conditions |
| `blk_0373_item_01` | Type 1 | understand | It's possible to overcome barriers to participating in fun, enjoyable or rewarding activities using coping strategies, and that finding the courage to participate in activities which initially feel ch |
| `blk_0375_item_01` | Type 1 | know | That gambling can lead to serious mental health harms, including anxiety, depression, and suicide, and that some gambling products are more likely to cause these harms than others |
| `blk_0377_item_01` | Type 1 | understand | That the co-occurrence of alcohol/drug use and poor mental health is common and that the relationship is bi-directional: mental health problems can increase the risk of alcohol/drug use, and alcohol/d |
| `blk_0377_item_02` | Type 1 | understand | That stopping smoking can improve people's mental health and decrease anxiety |

#### Learning Targets

##### Understanding Emotions and Mental Health — `cluster_14_lt_01`

**Definition.** I can identify emotions, explain mental health concepts, and describe factors that support or harm wellbeing.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `lt_set_unstable`.

**KUD items covered:** `blk_0259_item_01`, `blk_0259_item_02`, `blk_0262_item_01`, `blk_0262_item_02`, `blk_0270_item_01`, `blk_0272_item_01`, `blk_0274_item_01`, `blk_0355_item_01`, `blk_0355_item_05`, `blk_0357_item_01`, `blk_0364_item_01`, `blk_0366_item_01`, `blk_0366_item_02`, `blk_0368_item_01`, `blk_0370_item_01`, `blk_0370_item_02`, `blk_0373_item_01`, `blk_0375_item_01`, `blk_0377_item_01`, `blk_0377_item_02`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify basic emotions and describe simple factors that help keep me mentally healthy. |
| End of Secondary | I can explain complex mental health concepts and analyse how multiple factors interact to support or harm wellbeing. |

**Criterion rubric** — stability `rubric_unstable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as demonstrated independently and can stand alone as evidence that the learning target is met.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify emotions or mental health concepts. |
| emerging | With support, names basic emotions but shows limited understanding of mental health concepts. |
| developing | Independently identifies common emotions and describes some mental health concepts but explanations lack detail. |
| competent | Independently identifies range of emotions, explains mental health concepts clearly, and describes factors supporting or harming wellbeing. |
| extending | Connects emotions to mental health concepts and analyses complex wellbeing factors across different contexts. |

##### Recognising and Responding to Mental Health Needs — `cluster_14_lt_02`

**Definition.** I can assess emotional responses, judge when support is needed, and communicate about mental health appropriately.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `lt_set_unstable`.

**Prerequisites:** `cluster_14_lt_01`

**KUD items covered:** `blk_0264_item_01`, `blk_0266_item_01`, `blk_0270_item_02`, `blk_0274_item_02`, `blk_0355_item_03`, `blk_0355_item_04`, `blk_0357_item_02`, `blk_0362_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can recognise basic emotional responses in myself and others and identify when adult help is needed. |
| End of Secondary | I can assess complex emotional situations, evaluate appropriate support options, and communicate effectively about mental health concerns. |

**Criterion rubric** — stability `rubric_unstable`, quality gate **FAIL**.

_Gate failures:_ single_construct

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently' performing all required actions without hedging language or positioning it as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to assess emotional responses or mental health needs. |
| emerging | With support, identifies basic emotions but struggles to judge when help is needed. |
| developing | Recognises obvious emotional distress and communicates about mental health with some prompting or guidance. |
| competent | Independently assesses emotional responses, judges when support is needed, and communicates appropriately about mental health concerns. |
| extending | Applies mental health assessment skills to complex situations and supports others in seeking help. |

_Prerequisite edges:_
- `cluster_14_lt_01` [ontological_prerequisite/high] — Cannot assess emotional responses without understanding emotions and mental health concepts.
- `cluster_09_lt_02` [pedagogical_sequencing/medium] — Help-seeking skills are typically established before applying them to mental health contexts.

##### Sustaining Personal and Others' Wellbeing — `cluster_14_lt_03`

**Definition.** The student practises ongoing care for their own and others' mental health across different contexts.

**Knowledge type:** Type 3. **Assessment route:** `multi_informant_observation`. **Stability:** `lt_set_unstable`.

**KUD items covered:** `blk_0355_item_02`

**Observation protocol** — stability `stable`, Mode 3 gate **PASS**.

_Prerequisites (knowledge-contingent Type 3):_ `Understanding Emotions and Mental Health`

**End of Primary**

- The student notices when classmates appear upset and offers simple comfort or seeks adult help
- The student uses basic strategies like deep breathing or asking for a break when feeling overwhelmed
- The student talks about feelings with trusted adults when experiencing difficult emotions

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Primary):_ Think about one relationship in your life — with a friend, family member, or classmate. What makes it feel safe and kind? Is there anything you would like to be different?

**End of Secondary**

- The student consistently checks in with friends about their wellbeing and responds appropriately to signs of distress
- The student independently applies multiple coping strategies and seeks appropriate support when facing mental health challenges
- The student advocates for mental health awareness in their peer group and challenges stigma when it arises

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Secondary):_ Think about a situation this term where you had to make a decision about a relationship or your own wellbeing. What did you consider, and what would you do differently now?

**Parent / caregiver prompts**

- What have you noticed about how your child responds when family members or friends seem upset or stressed?
- How does your child handle their own difficult emotions or stressful situations at home?
- Have you observed your child talking about mental health or supporting others' wellbeing in your community or family?

**Developmental conversation protocol.** The conversation explores how the student recognises and responds to mental health needs in themselves and others, examining their growing repertoire of wellbeing strategies and their developing sense of responsibility for collective mental health in their communities.

### Digital Wellbeing and Online Behaviour — `cluster_15`

**Definition.** The ability to manage online time, recognise digital risks, and maintain healthy digital relationships.

**Dominant knowledge type:** Type 2. **Stability:** `cluster_unstable`. **Source lines:** L478-659. **KUD items:** 23.

_Stability diagnostics:_
- dominant_type_drift_run2: Type 2→Type 1
- unmatched_in_run3

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0280_item_01` | Type 2 | do_skill | Think about positive and negative aspects of the internet |
| `blk_0282_item_01` | Type 2 | do_skill | discuss how online relationships can complement and support meaningful in-person relationships, but also how they might be in tension, and the reasons why online relationships are unlikely to be a goo |
| `blk_0284_item_01` | Type 1 | understand | The benefits of limiting time spent online, the risks of excessive time spent on electronic devices and the impact of positive and negative content online on their own and others' mental and physical  |
| `blk_0286_item_01` | Type 2 | do_skill | recognise and display respectful behaviour online |
| `blk_0288_item_01` | Type 1 | know | Why social media, some apps, computer games and online gaming, including gambling sites, are age restricted |
| `blk_0290_item_01` | Type 1 | know | The risks relating to online gaming, video game monetisation, scams, fraud and other financial harms, and that gaming can become addictive |
| `blk_0292_item_01` | Type 2 | do_skill | Take a critical approach to what they see and read online and make responsible decisions about which content, including content on social media and apps, is appropriate for them |
| `blk_0294_item_01` | Type 1 | know | That abuse, bullying and harassment can take place online and that this can impact wellbeing |
| `blk_0294_item_02` | Type 2 | do_skill | How to seek support from trusted adults |
| `blk_0296_item_01` | Type 1 | know | know how information is selected and targeted |
| `blk_0381_item_01` | Type 1 | understand | About the benefits of limiting time spent online, the risks of excessive time spent on electronic devices and the impact of positive and negative content online on their own and others' mental and phy |
| `blk_0383_item_01` | Type 1 | understand | The impact of unhealthy or obsessive comparison with others online including through setting unrealistic expectations for body image |
| `blk_0383_item_02` | Type 1 | understand | How people may curate a specific image of their life online |
| `blk_0383_item_03` | Type 1 | understand | The impact that an over-reliance on online relationships, including relationships formed through social media, can have |
| `blk_0385_item_01` | Type 2 | do_skill | how to report, or find support, if they have been affected by harmful behaviours online |
| `blk_0387_item_01` | Type 1 | know | The risks related to online gambling and gambling-like content within gaming, including the accumulation of debt |
| `blk_0389_item_01` | Type 1 | understand | understanding the prevalence of misinformation and disinformation online, including conspiracy theories |
| `blk_0389_item_02` | Type 2 | do_skill | how to be a discerning consumer of information online |
| `blk_0389_item_03` | Type 1 | understand | how advertising and information is targeted at them |
| `blk_0391_item_01` | Type 1 | know | The risks of illegal behaviours online, including drug and knife supply or the sale or purchasing of illicit drugs online |
| `blk_0393_item_01` | Type 1 | know | The serious risks of viewing online content that promotes self-harm, suicide or violence |
| `blk_0393_item_02` | Type 2 | do_skill | How to safely report material that promotes self-harm, suicide or violence |
| `blk_0393_item_03` | Type 2 | do_skill | How to access support after viewing content that promotes self-harm, suicide or violence |

#### Learning Targets

##### Understanding Digital Risks and Impacts — `cluster_15_lt_01`

**Definition.** I can identify the risks and benefits of online activities and their impact on wellbeing.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `lt_set_unstable`.

**KUD items covered:** `blk_0284_item_01`, `blk_0288_item_01`, `blk_0290_item_01`, `blk_0294_item_01`, `blk_0296_item_01`, `blk_0381_item_01`, `blk_0383_item_01`, `blk_0383_item_02`, `blk_0383_item_03`, `blk_0387_item_01`, `blk_0389_item_01`, `blk_0389_item_03`, `blk_0391_item_01`, `blk_0393_item_01`

**Band progression** — stability `band_statements_unstable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify basic risks and benefits of online activities with guidance. |
| End of Secondary | I can analyse complex digital risks and benefits and evaluate their long-term impact on wellbeing. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as demonstrated independently and can stand alone as evidence that the learner has met the learning target.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify online risks or benefits. |
| emerging | With support, names some online risks or benefits but explanations are incomplete. |
| developing | Independently identifies basic online risks and benefits but struggles to explain wellbeing impacts. |
| competent | Independently identifies various online risks and benefits and explains their specific impacts on personal wellbeing. |
| extending | Analyses complex digital scenarios and evaluates nuanced impacts on different aspects of wellbeing. |

_Prerequisite edges:_
- `cluster_14_lt_01` [ontological_prerequisite/high] — Understanding wellbeing concepts is essential to explain impacts on wellbeing.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Students brainstorm what happens when they use digital devices and apps
- stage: Teacher guides sorting of student ideas into helpful and harmful categories
- stage: Students discuss how digital activities make them feel physically and emotionally
- stage: Class creates shared language for describing different levels of understanding about digital impacts
- prompt: What are some things that happen when you spend time online or using apps?
- prompt: How do these digital activities affect how you feel in your body and mind?
- prompt: What makes someone really good at understanding digital risks and benefits?
- anchor-examples guidance: Choose student work samples that show clear progression from basic naming of risks to detailed explanations of wellbeing impacts.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet tried to identify online risks or benefits |
| emerging | I can name some online risks or benefits with help |
| developing | I can identify basic online risks and benefits on my own |
| competent | I can identify various online risks and benefits and explain how they affect my wellbeing |
| extending | I can analyze complex digital situations and evaluate detailed impacts on different parts of wellbeing |

- self-check: Can I explain how this digital activity affects my physical, emotional, or social wellbeing?
- self-check: Am I identifying both risks and benefits rather than just one side?

_Feedback moves by level:_
- **no_evidence**
  - Provide concrete examples of common online activities to analyze
  - Use visual prompts showing digital scenarios
- **emerging**
  - Ask students to explain their thinking about identified risks or benefits
  - Provide sentence starters for describing digital impacts
- **developing**
  - Guide students to connect digital activities to specific feelings or physical effects
  - Prompt reflection on personal experiences with digital wellbeing
- **competent**
  - Present complex scenarios with multiple digital elements to analyze
  - Encourage consideration of long-term and varied wellbeing impacts

##### Making Responsible Digital Decisions — `cluster_15_lt_02`

**Definition.** I can evaluate online content and relationships to make informed decisions about digital engagement.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `lt_set_unstable`.

**Prerequisites:** `cluster_15_lt_01`

**KUD items covered:** `blk_0280_item_01`, `blk_0282_item_01`, `blk_0286_item_01`, `blk_0292_item_01`, `blk_0294_item_02`, `blk_0385_item_01`, `blk_0389_item_02`, `blk_0393_item_02`, `blk_0393_item_03`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify helpful and harmful online content with guidance to make basic digital choices. |
| End of Secondary | I can evaluate complex online content and relationships independently to make informed decisions about digital engagement. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently evaluates' and 'make informed decisions' without any hedging language or positioning it as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to evaluate online content or relationships. |
| emerging | With support, identifies some online risks but makes decisions without clear evaluation. |
| developing | Independently recognises basic online risks and benefits but evaluation lacks depth or consistency. |
| competent | Independently evaluates online content and relationships using clear criteria to make informed decisions about digital engagement. |
| extending | Transfers evaluation skills to novel digital contexts and helps others make informed decisions. |

_Prerequisite edges:_
- `cluster_15_lt_01` [ontological_prerequisite/high] — Cannot evaluate digital decisions without understanding digital risks and impacts.
- `cluster_08_lt_01` [pedagogical_sequencing/medium] — Understanding basic digital safety principles typically precedes making complex digital decisions.

### Physical Health and Lifestyle — `cluster_16`

**Definition.** The ability to maintain physical health through nutrition, exercise, and healthy lifestyle choices.

**Dominant knowledge type:** Type 1. **Stability:** `stable`. **Source lines:** L508-719. **KUD items:** 34.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0303_item_01` | Type 1 | know | how to achieve building regular physical activity into daily and weekly routines; for example, walking or cycling to school, a daily active mile or other forms of regular, moderate and/or vigorous phy |
| `blk_0306_item_01` | Type 1 | know | which adults to speak to in school if they are worried about their health |
| `blk_0306_item_02` | Type 2 | do_skill | how and when to seek support when worried about their health |
| `blk_0309_item_01` | Type 1 | know | nutritional content including understanding calories and other nutritional content |
| `blk_0313_item_01` | Type 1 | know | The characteristics of a poor diet and risks associated with unhealthy eating including obesity and tooth decay and other behaviours such as the impact of alcohol on diet or health |
| `blk_0316_item_01` | Type 1 | know | The facts about legal and illegal harmful substances and associated risks, including smoking, vaping, alcohol use and drug-taking, including the risks of nicotine addiction caused by nicotine products |
| `blk_0320_item_01` | Type 1 | know | Early signs of physical illness, such as weight loss or unexplained changes to the body |
| `blk_0322_item_01` | Type 1 | know | About safe and unsafe exposure to the sun, and how to reduce the risk of sun damage, including skin cancer. |
| `blk_0324_item_01` | Type 1 | know | recommended amount of sleep for their age |
| `blk_0324_item_02` | Type 1 | know | practical steps for improving sleep, such as not using screens in the bedroom |
| `blk_0324_item_03` | Type 1 | understand | the impact of poor sleep on weight, mood and ability to learn |
| `blk_0326_item_01` | Type 1 | know | twice a day with fluoride toothpaste, cleaning between teeth, and regular check-ups at the dentist |
| `blk_0328_item_01` | Type 1 | know | About personal hygiene and germs including bacteria, viruses, how they are spread and treated, and the importance of handwashing. |
| `blk_0330_item_01` | Type 1 | know | The introduction of topics relating to vaccination and immunisation should be aligned with when vaccinations are offered to pupils |
| `blk_0396_item_01` | Type 1 | know | the characteristics of a healthy lifestyle, including physical activity and maintaining a healthy weight, including the links between an inactive lifestyle and ill-health, including cardiovascular ill |
| `blk_0403_item_01` | Type 1 | know | the links between a poor diet and health risks, including tooth decay, unhealthy weight gain, and cardiovascular disease |
| `blk_0405_item_01` | Type 1 | know | Unhealthy weight gain increases risks of cancer, type 2 diabetes and cardiovascular disease |
| `blk_0410_item_01` | Type 1 | know | The facts about which drugs are illegal, the risks of taking illegal drugs, including the increased risk of potent synthetic drugs being added to illegal drugs, the risks of illicit vapes containing d |
| `blk_0413_item_01` | Type 1 | know | What constitutes low risk alcohol consumption in adulthood, and the legal age of sale for alcohol in England |
| `blk_0413_item_02` | Type 1 | understand | Understanding how to increase personal safety while drinking alcohol, including how to decrease the risks of having a drink spiked or of poisoning from potentially fatal substances such as methanol |
| `blk_0415_item_01` | Type 1 | know | alcohol dependency |
| `blk_0418_item_01` | Type 1 | know | The facts about the multiple serious harms from smoking tobacco (particularly the link to lung cancer and cardiovascular disease), the benefits of quitting and how to access support to do so |
| `blk_0420_item_01` | Type 1 | know | The facts about vaping, including the harms posed to young people, and the role that vapes can play in helping adult smokers to quit |
| `blk_0424_item_01` | Type 1 | know | treatment and prevention of infection, and about antibiotics |
| `blk_0426_item_01` | Type 1 | know | Dental health and the benefits of good oral hygiene, including brushing teeth twice a day with fluoride toothpaste and cleaning between teeth, reducing consumption of sugar-containing food and drinks, |
| `blk_0428_item_01` | Type 1 | know | knowledgeable healthcare professionals |
| `blk_0430_item_01` | Type 1 | know | the benefits of regular self-examination and screening |
| `blk_0430_item_02` | Type 3 | do_disposition | taking responsibility for their own health through regular self-examination and screening |
| `blk_0432_item_01` | Type 1 | know | The facts and scientific evidence relating to vaccination, immunisation and antimicrobial resistance |
| `blk_0434_item_01` | Type 1 | know | screen-free time before bed and removing phones from the bedroom are important for good-quality sleep |
| `blk_0434_item_02` | Type 1 | understand | how a lack of sleep can affect weight, mood and ability to learn |
| `blk_0436_item_01` | Type 1 | know | The importance of pre-conception health, including taking folic acid |
| `blk_0436_item_02` | Type 1 | know | The importance of pelvic floor health |
| `blk_0436_item_03` | Type 1 | know | Information on miscarriage and pregnancy loss, and how to access care and support |

#### Learning Targets

##### Understanding Health Knowledge and Risks — `cluster_16_lt_01`

**Definition.** I can identify key facts about nutrition, physical activity, substance use, hygiene, and health maintenance practices.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0303_item_01`, `blk_0306_item_01`, `blk_0309_item_01`, `blk_0313_item_01`, `blk_0316_item_01`, `blk_0320_item_01`, `blk_0322_item_01`, `blk_0324_item_01`, `blk_0324_item_02`, `blk_0324_item_03`, `blk_0326_item_01`, `blk_0328_item_01`, `blk_0330_item_01`, `blk_0396_item_01`, `blk_0403_item_01`, `blk_0405_item_01`, `blk_0410_item_01`, `blk_0413_item_01`, `blk_0413_item_02`, `blk_0415_item_01`, `blk_0418_item_01`, `blk_0420_item_01`, `blk_0424_item_01`, `blk_0426_item_01`, `blk_0428_item_01`, `blk_0430_item_01`, `blk_0432_item_01`, `blk_0434_item_01`, `blk_0434_item_02`, `blk_0436_item_01`, `blk_0436_item_02`, `blk_0436_item_03`

**Band progression** — stability `band_statements_unstable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify basic facts about healthy eating, exercise, cleanliness, and avoiding harmful substances. |
| End of Secondary | I can analyse complex health information about nutrition, physical activity, substance risks, and preventive health practices. |

**Criterion rubric** — stability `rubric_unstable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as demonstrated independently and accurately, standing alone as evidence that the learning target is met.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify health facts. |
| emerging | With support, names some health facts but demonstrates inaccurate understanding. |
| developing | Independently identifies basic health facts but shows gaps in nutrition or hygiene knowledge. |
| competent | Independently identifies key facts about nutrition, physical activity, substance use, hygiene, and health maintenance practices accurately. |
| extending | Connects health facts across domains and explains relationships between different health practices. |

_Prerequisite edges:_
- `cluster_01_lt_01` [pedagogical_sequencing/medium] — Body awareness typically precedes understanding health maintenance practices.

**Supporting components** — stability `stable`.

_Co-construction plan:_
- stage: Brainstorm what we already know about staying healthy
- stage: Sort health knowledge into categories like nutrition, exercise, and hygiene
- stage: Define what makes health information accurate versus incomplete
- stage: Create quality levels from basic naming to explaining connections
- prompt: What health facts do you think are most important to know?
- prompt: How can we tell if our health knowledge is complete or has gaps?
- prompt: What would it look like to connect different areas of health together?
- anchor-examples guidance: Select student work samples that clearly show progression from naming isolated health facts to demonstrating comprehensive understanding across all health domains.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet attempted to identify health facts |
| emerging | I can name some health facts with help but my understanding has errors |
| developing | I can identify basic health facts on my own but have gaps in nutrition or hygiene knowledge |
| competent | I can independently identify key facts about nutrition, physical activity, substance use, hygiene, and health maintenance practices accurately |
| extending | I can connect health facts across different areas and explain relationships between health practices |

- self-check: Can I accurately name important facts in all five health areas without help?
- self-check: Am I able to explain how different health practices connect to each other?

_Feedback moves by level:_
- **no_evidence**
  - Provide visual health fact cards to sort and discuss
  - Start with one familiar health topic like handwashing
- **emerging**
  - Correct misconceptions immediately with accurate information
  - Use graphic organizers to organize health facts by category
- **developing**
  - Focus practice on the specific health domains showing gaps
  - Provide targeted resources for nutrition or hygiene knowledge building
- **competent**
  - Challenge to find connections between different health practices
  - Ask how one health choice affects other areas of wellness

##### Seeking Health Support — `cluster_16_lt_02`

**Definition.** I can determine when and how to seek appropriate health support from trusted adults and healthcare professionals.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**KUD items covered:** `blk_0306_item_02`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify when I need help with health concerns and ask trusted adults for support. |
| End of Secondary | I can evaluate health situations to determine appropriate support sources and communicate effectively with healthcare professionals. |

**Criterion rubric** — stability `rubric_unreliable`, quality gate **FAIL**.

_Gate failures:_ rubric_generation_failed

_Competent-framing judge:_ `error` — no structural signature reached 2/3 agreement; signatures=[(('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'apply'), ('competent', 'within_limit', 'evaluate'), ('extending', 'within_limit', 'evaluate'), ('competent_scope', 'unscoped')), (('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'recognise'), ('competent', 'within_limit', 'evaluate'), ('extending', 'within_limit', 'apply'), ('competent_scope', 'unscoped')), (('no_evidence', 'within_limit', 'recognise'), ('emerging', 'within_limit', 'recognise'), ('developing', 'within_limit', 'recognise'), ('competent', 'within_limit', 'evaluate'), ('extending', 'within_limit', 'evaluate'), ('competent_scope', 'unscoped'))]

| Level | Descriptor |
|---|---|
| no_evidence |  |
| emerging |  |
| developing |  |
| competent |  |
| extending |  |

##### Personal Health Responsibility — `cluster_16_lt_03`

**Definition.** The student holds responsibility for maintaining their own health through regular self-examination and screening practices.

**Knowledge type:** Type 3. **Assessment route:** `multi_informant_observation`. **Stability:** `stable`.

**KUD items covered:** `blk_0430_item_02`

**Observation protocol** — stability `observation_indicators_unstable`, Mode 3 gate **PASS**.

_Prerequisites (knowledge-contingent Type 3):_ `Understanding Health Knowledge and Risks`

**End of Primary**

- The student independently performs basic self-care routines like teeth brushing and handwashing without reminders
- The student notices and reports physical changes or discomfort to trusted adults
- The student asks questions about their body and health during appropriate conversations

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Primary):_ Think about one relationship in your life — with a friend, family member, or classmate. What makes it feel safe and kind? Is there anything you would like to be different?

**End of Secondary**

- The student maintains consistent personal health routines across different environments and schedules
- The student seeks appropriate health information and screening opportunities when needed
- The student takes initiative to address health concerns through proper channels rather than ignoring symptoms

_Self-reflection prompt (calibrated to this source's own developmental expectations at End of Secondary):_ Think about a situation this term where you had to make a decision about a relationship or your own wellbeing. What did you consider, and what would you do differently now?

**Parent / caregiver prompts**

- What have you noticed about how your child takes care of their own health routines at home?
- When your child feels unwell or notices something different about their body, how do they typically respond?
- Have you observed your child seeking out health information or asking health-related questions independently?

**Developmental conversation protocol.** The conversation explores how the student demonstrates ownership of their health through self-monitoring behaviours and help-seeking patterns. Teacher and student discuss observed consistency in health practices across settings, with parent input on home behaviours when appropriate.

### Healthcare Access and Medical Decision-Making — `cluster_17`

**Definition.** The ability to access healthcare services and understand medical consent and decision-making processes.

**Dominant knowledge type:** Type 1. **Stability:** `stable`. **Source lines:** L723-729. **KUD items:** 3.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0438_item_01` | Type 1 | know | what a GP is; when to use A&E / minor injuries; accessing sexual health and family planning clinics; the role of local pharmacies; and how to seek help via local third sector partners which may have s |
| `blk_0440_item_01` | Type 1 | know | Before age 16, a child's parents will have responsibility for consenting to medical treatment on their behalf unless they are Gillick competent to take this decision for themselves |
| `blk_0441_item_01` | Type 1 | understand | Pupils should understand the circumstances in which someone over 16 may not be deemed to have capacity to make decisions about medical treatment. |

#### Learning Targets

##### Navigating Healthcare Services — `cluster_17_lt_01`

**Definition.** I can identify appropriate healthcare services for different needs and explain how to access them.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0438_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify basic healthcare services like doctors and dentists and describe simple ways to access them. |
| End of Secondary | I can evaluate appropriate healthcare services for diverse health needs and explain comprehensive access pathways including barriers. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently identifies' and 'clearly explains' without any hedging language or positioning as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify healthcare services or access methods. |
| emerging | With support, names some healthcare services but provides incomplete or inaccurate access information. |
| developing | Independently identifies basic healthcare services and explains simple access methods but lacks detail for complex needs. |
| competent | Independently identifies appropriate healthcare services for different needs and clearly explains how to access them effectively. |
| extending | Evaluates healthcare service options and explains access strategies for complex or specialised healthcare needs. |

_Prerequisite edges:_
- `cluster_16_lt_02` [pedagogical_sequencing/high] — Understanding when to seek health support precedes knowing how to navigate specific healthcare services.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Brainstorm different types of healthcare needs students or families might have
- stage: Identify various healthcare services that address these needs
- stage: Discuss how people find and access these services
- stage: Create criteria for matching appropriate services to specific needs
- stage: Develop language for describing access methods clearly
- prompt: What healthcare needs have you or your family experienced?
- prompt: How do people find the right healthcare service when they need help?
- prompt: What makes one healthcare service more appropriate than another for a specific need?
- prompt: What information would someone need to successfully access a healthcare service?
- anchor-examples guidance: Select examples that show clear progression from basic services with simple access to complex services requiring multiple steps or specialized knowledge.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet attempted to identify healthcare services or how to access them |
| emerging | I can name some healthcare services with help but my access information is incomplete |
| developing | I can identify basic healthcare services and explain simple ways to access them |
| competent | I can identify appropriate healthcare services for different needs and clearly explain how to access them |
| extending | I can evaluate healthcare service options and explain access strategies for complex healthcare needs |

- self-check: Can I match the right type of healthcare service to specific needs?
- self-check: Can I explain the steps someone would take to access the services I identified?

_Feedback moves by level:_
- **no_evidence**
  - Provide a simple scenario and ask what type of healthcare help might be needed
  - Show examples of common healthcare services and discuss when they might be used
- **emerging**
  - Ask clarifying questions about the access steps they described
  - Provide additional information to fill gaps in their access explanations
- **developing**
  - Present more complex healthcare scenarios that require specialized services
  - Guide them to consider multiple access methods or steps for the same service
- **competent**
  - Challenge them to compare different service options for the same need
  - Ask them to consider barriers or complications in accessing specialized services

##### Understanding Medical Consent Capacity — `cluster_17_lt_02`

**Definition.** I can explain the legal framework for medical consent including age-related capacity and competency requirements.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0440_item_01`, `blk_0441_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify that adults help children make important decisions about their health and medical care. |
| End of Secondary | I can explain the legal framework for medical consent including age-related capacity and competency requirements. |

**Criterion rubric** — stability `rubric_unstable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as demonstrated accurately and independently, standing alone as evidence that the learning target is met.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to explain medical consent frameworks. |
| emerging | With support, identifies some basic consent concepts but explanations are incomplete or inaccurate. |
| developing | Explains basic medical consent principles but gaps remain in understanding age-related capacity requirements. |
| competent | Explains the legal framework for medical consent including age-related capacity and competency requirements accurately and independently. |
| extending | Applies consent framework knowledge to analyse complex scenarios involving capacity assessment and legal considerations. |

_Prerequisite edges:_
- `cluster_12_lt_02` [ontological_prerequisite/high] — Understanding general consent principles is essential before learning specific medical consent frameworks.
- `cluster_04_lt_02` [pedagogical_sequencing/medium] — Understanding personal rights and legal protections provides foundation for medical consent legal frameworks.

### Personal Safety and Risk Management — `cluster_18`

**Definition.** The ability to assess and manage personal safety risks in various environments and situations.

**Dominant knowledge type:** Type 2. **Stability:** `cluster_unstable`. **Source lines:** L551-753. **KUD items:** 11.

_Stability diagnostics:_
- dominant_type_drift_run3: Type 2→Type 1

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0333_item_01` | Type 1 | know | About hazards (including fire risks) that may cause harm, injury or risk and ways to reduce risks |
| `blk_0335_item_01` | Type 1 | know | How to recognise risk and keep safe around roads, railways, including level crossings, and water, including the water safety code |
| `blk_0338_item_01` | Type 1 | know | the importance of reporting incidents rather than filming them |
| `blk_0340_item_01` | Type 1 | know | Concepts of basic first aid for head injuries |
| `blk_0445_item_01` | Type 2 | do_skill | identify risk and manage personal safety in increasingly independent situations, including around roads, railways – including level crossings - and water (including the water safety code), and in unfa |
| `blk_0447_item_01` | Type 2 | do_skill | How to recognise and manage peer influence in relation to risk-taking behaviour and personal safety, including peer influence online and on social media |
| `blk_0449_item_01` | Type 2 | do_skill | Skills to support self-awareness, self-management, social awareness, relationship skills and responsible decision making in contexts involving conflict and violence |
| `blk_0449_item_02` | Type 2 | do_skill | Skills to recognise and manage peer pressure |
| `blk_0453_item_01` | Type 1 | know | Carrying weapons is uncommon among young people |
| `blk_0453_item_02` | Type 1 | understand | Misconceptions about weapon prevalence can lead to the false belief that carrying a knife is necessary for protection |
| `blk_0455_item_01` | Type 2 | do_skill | seek help where there is a concern about grooming or exploitation |

#### Learning Targets

##### Identifying Safety Hazards and Risks — `cluster_18_lt_01`

**Definition.** I can identify potential hazards and assess safety risks across different environments and situations.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `lt_set_unstable`.

**KUD items covered:** `blk_0333_item_01`, `blk_0335_item_01`, `blk_0445_item_01`, `blk_0453_item_01`, `blk_0453_item_02`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify obvious hazards and describe basic safety risks in familiar environments with guidance. |
| End of Secondary | I can independently assess complex safety risks and evaluate potential consequences across diverse unfamiliar situations. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently identifies' and 'accurately assesses' without any hedging language or implications of incompleteness.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify hazards or assess risks. |
| emerging | With support, identifies obvious hazards but struggles to assess actual risk levels. |
| developing | Independently identifies common hazards but assessment of risk levels lacks depth or accuracy. |
| competent | Independently identifies potential hazards across different environments and accurately assesses their associated safety risks. |
| extending | Systematically evaluates complex risk scenarios and prioritises multiple hazards by severity and likelihood. |

_Prerequisite edges:_
- `cluster_04_lt_01` [pedagogical_sequencing/medium] — Understanding unsafe situations provides foundation for broader hazard identification skills.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Students brainstorm what makes something dangerous or unsafe in familiar places
- stage: Groups categorize hazards by how likely they are to happen and how serious the harm could be
- stage: Class discusses what it means to assess risk versus just spotting hazards
- stage: Students test their understanding by ranking hazards from different scenarios
- prompt: What could hurt someone in this environment?
- prompt: How likely is this hazard to actually cause harm?
- prompt: Which hazard would you worry about most and why?
- anchor-examples guidance: Choose scenarios from varied environments that show clear differences between spotting hazards and evaluating their actual risk levels.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet attempted to identify hazards or assess risks |
| emerging | I can spot obvious hazards with help but struggle to judge how risky they really are |
| developing | I can find common hazards on my own but my risk assessment needs more depth |
| competent | I can identify potential hazards in different places and accurately assess their safety risks |
| extending | I can systematically evaluate complex risk scenarios and rank multiple hazards by how severe and likely they are |

- self-check: Can I explain why this hazard is more or less risky than others?
- self-check: Have I considered both how likely the hazard is and how much harm it could cause?

_Feedback moves by level:_
- **no_evidence**
  - Point out one obvious hazard and ask what could go wrong
  - Provide a simple checklist of things to look for
- **emerging**
  - Ask them to explain why one hazard is riskier than another
  - Guide them to consider both likelihood and severity
- **developing**
  - Challenge them to find less obvious hazards in the same environment
  - Have them justify their risk assessment with specific reasoning
- **competent**
  - Present complex scenarios with multiple interacting hazards
  - Ask them to create a priority ranking system for different types of risks

##### Managing Personal Safety and Seeking Help — `cluster_18_lt_02`

**Definition.** I can implement safety strategies, manage peer influence, and seek appropriate help when facing safety concerns.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `lt_set_unstable`.

**Prerequisites:** `cluster_18_lt_01`

**KUD items covered:** `blk_0338_item_01`, `blk_0340_item_01`, `blk_0445_item_01`, `blk_0447_item_01`, `blk_0449_item_01`, `blk_0449_item_02`, `blk_0455_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify basic safety strategies and ask trusted adults for help when I feel unsafe. |
| End of Secondary | I can evaluate complex safety situations, resist negative peer influence, and independently access appropriate support services. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor clearly states the learner independently demonstrates all required capabilities without hedging language or positioning it as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to implement safety strategies or seek help. |
| emerging | With support, identifies some safety strategies but struggles to apply them effectively. |
| developing | Independently applies basic safety strategies but inconsistently manages peer influence or help-seeking. |
| competent | Independently implements appropriate safety strategies, manages peer influence effectively, and seeks help when facing safety concerns. |
| extending | Transfers safety management skills to novel situations and supports others in developing safety strategies. |

_Prerequisite edges:_
- `cluster_18_lt_01` [ontological_prerequisite/high] — Cannot implement safety strategies without first identifying hazards and risks.
- `cluster_04_lt_01` [pedagogical_sequencing/high] — Recognising unsafe situations typically precedes learning to manage them.
- `cluster_09_lt_02` [pedagogical_sequencing/medium] — Basic help-seeking skills provide foundation for broader safety management.
- `cluster_01_lt_02` [pedagogical_sequencing/medium] — Expressing boundaries supports managing peer influence in safety contexts.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Students brainstorm what safety means in different contexts and situations.
- stage: Students identify specific strategies they already use to stay safe.
- stage: Students discuss challenges with peer pressure and when help-seeking is needed.
- stage: Students organize strategies and help-seeking behaviors from basic to advanced levels.
- prompt: What does staying safe look like in different places or situations?
- prompt: When have you successfully handled peer pressure or asked for help?
- prompt: What makes some safety strategies harder to use than others?
- prompt: How could you help someone else learn to stay safe?
- anchor-examples guidance: Choose examples that show clear differences between basic safety awareness and effective implementation across various contexts.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet shown that I can use safety strategies or ask for help. |
| emerging | I can identify some safety strategies with help but find them hard to use effectively. |
| developing | I can use basic safety strategies on my own but sometimes struggle with peer pressure or asking for help. |
| competent | I can use appropriate safety strategies, handle peer pressure well, and ask for help when I need it. |
| extending | I can apply safety skills in new situations and help others develop their own safety strategies. |

- self-check: Can I name specific safety strategies I use and explain when to seek help?
- self-check: How well do I handle situations where peers might influence my safety choices?

_Feedback moves by level:_
- **no_evidence**
  - Help identify one specific safety strategy relevant to the student's daily life.
  - Practice recognizing trusted adults who can provide help.
- **emerging**
  - Guide practice applying identified strategies in low-risk scenarios.
  - Provide sentence starters for help-seeking conversations.
- **developing**
  - Role-play peer pressure scenarios with response strategies.
  - Create a personal help-seeking plan with specific steps and contacts.
- **competent**
  - Present novel safety scenarios requiring strategy adaptation.
  - Facilitate opportunities to mentor peers in safety planning.

### Puberty and Physical Development — `cluster_19`

**Definition.** The ability to understand physical development, puberty, and health changes during adolescence.

**Dominant knowledge type:** Type 1. **Stability:** `stable`. **Source lines:** L565-770. **KUD items:** 7.

#### KUD items

| Item ID | Type | Column | Content |
|---|---|---|---|
| `blk_0344_item_01` | Type 1 | know | The human lifecycle and puberty as a stage in this process, including growth and other ways the body can change and develop during adolescence |
| `blk_0348_item_01` | Type 1 | know | The average age of the onset of menstruation is twelve, periods can start at eight |
| `blk_0348_item_02` | Type 1 | understand | Covering menstruation before girls' periods start helps them understand what to expect and avoid distress |
| `blk_0351_item_01` | Type 1 | understand | understand their changing bodies and their feelings |
| `blk_0351_item_02` | Type 2 | do_skill | how to protect their own health and wellbeing |
| `blk_0351_item_03` | Type 2 | do_skill | when a physical or mental health issue requires attention |
| `blk_0468_item_01` | Type 1 | know | Cardiopulmonary Resuscitation is usually best taught after 12 years old |

#### Learning Targets

##### Understanding Physical Development During Puberty — `cluster_19_lt_01`

**Definition.** I can explain the physical changes that occur during puberty and adolescence.

**Knowledge type:** Type 1. **Assessment route:** `rubric_with_clear_criteria`. **Stability:** `stable`.

**KUD items covered:** `blk_0344_item_01`, `blk_0348_item_01`, `blk_0348_item_02`, `blk_0351_item_01`, `blk_0468_item_01`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can describe the basic physical changes that happen during puberty with guidance. |
| End of Secondary | I can explain the physical changes during puberty and adolescence including their biological causes and individual variation. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as demonstrated independently and comprehensively, standing alone as clear evidence that the learning target is met.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to explain physical changes during puberty. |
| emerging | With support, identifies some physical changes but explanations are incomplete or inaccurate. |
| developing | Independently identifies physical changes during puberty but explanations lack detail or contain minor gaps. |
| competent | Independently explains the physical changes that occur during puberty and adolescence accurately and comprehensively. |
| extending | Explains puberty changes and connects them to individual variation, timing differences, or broader development. |

_Prerequisite edges:_
- `cluster_01_lt_01` [ontological_prerequisite/high] — Must know body parts and anatomy before understanding how they change during puberty.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Brainstorm what students already know about physical changes during puberty
- stage: Discuss what makes a good explanation versus just listing changes
- stage: Sort student examples of physical changes into categories of explanation quality
- stage: Refine criteria for complete and accurate explanations
- prompt: What physical changes do you think happen during puberty?
- prompt: What's the difference between naming a change and explaining it well?
- prompt: How would you know if someone really understands these changes?
- anchor-examples guidance: Select student work samples that show clear differences in explanation depth and accuracy rather than just listing physical changes.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet attempted to explain physical changes during puberty. |
| emerging | I can identify some physical changes with help but my explanations need work. |
| developing | I can identify physical changes during puberty but my explanations could be more detailed. |
| competent | I can explain the physical changes that occur during puberty and adolescence accurately and completely. |
| extending | I can explain puberty changes and connect them to how timing and development vary between individuals. |

- self-check: Did I explain the changes or just list them?
- self-check: Are my explanations accurate and complete?

_Feedback moves by level:_
- **no_evidence**
  - Provide sentence starters about one specific physical change
  - Use visual aids to prompt discussion of observable changes
- **emerging**
  - Ask students to elaborate on one change they mentioned
  - Provide accurate information to correct misconceptions
- **developing**
  - Prompt for more detail about how or why changes occur
  - Encourage connections between related physical changes
- **competent**
  - Challenge students to consider individual differences in timing
  - Ask them to connect physical changes to broader developmental patterns

##### Protecting Health and Wellbeing — `cluster_19_lt_02`

**Definition.** I can identify when health issues require attention and apply strategies to protect wellbeing.

**Knowledge type:** Type 2. **Assessment route:** `reasoning_quality_rubric`. **Stability:** `stable`.

**Prerequisites:** `cluster_19_lt_01`

**KUD items covered:** `blk_0351_item_02`, `blk_0351_item_03`

**Band progression** — stability `stable`, quality gate **PASS**.

| Band | Statement |
|---|---|
| End of Primary | I can identify basic health issues that need adult help and follow simple wellbeing strategies. |
| End of Secondary | I can evaluate complex health concerns requiring professional attention and independently apply comprehensive wellbeing protection strategies. |

**Criterion rubric** — stability `stable`, quality gate **PASS**.

_Competent-framing judge:_ `pass` — The descriptor declares the capability as fully demonstrated with 'independently identifies' and 'applies appropriate strategies...effectively' without any hedging language or positioning as incomplete.

| Level | Descriptor |
|---|---|
| no_evidence | No attempt to identify health issues or strategies. |
| emerging | With support, recognises some obvious health concerns but applies strategies inaccurately. |
| developing | Independently identifies clear health issues and applies basic strategies but misses subtle concerns. |
| competent | Independently identifies when health issues require attention and applies appropriate strategies to protect wellbeing effectively. |
| extending | Transfers health identification skills to complex situations and integrates multiple protective strategies. |

_Prerequisite edges:_
- `cluster_16_lt_01` [ontological_prerequisite/high] — Cannot identify when health issues require attention without understanding basic health knowledge.
- `cluster_16_lt_02` [pedagogical_sequencing/medium] — Understanding how to seek health support typically precedes applying broader wellbeing strategies.

**Supporting components** — stability `supporting_unstable`.

_Co-construction plan:_
- stage: Students share experiences of recognizing when they or others needed health attention
- stage: Class discusses what makes health concerns obvious versus subtle
- stage: Students brainstorm different strategies people use to protect their wellbeing
- stage: Groups categorize health identification skills from simple to complex situations
- stage: Class agrees on what effective application of protective strategies looks like
- prompt: When have you noticed someone needed health help and what made you realize it?
- prompt: What's the difference between a health concern that's easy to spot and one that's harder to notice?
- prompt: How do you know if a wellbeing strategy is working effectively?
- prompt: What makes some health situations more complex than others?
- anchor-examples guidance: Choose examples that show clear progression from obvious to subtle health concerns and from single to multiple protective strategies.

_Student-facing rubric:_

| Level | Descriptor |
|---|---|
| no_evidence | I have not yet attempted to identify health issues or apply protective strategies |
| emerging | I can recognize obvious health concerns with help but apply strategies inaccurately |
| developing | I can identify clear health issues and apply basic strategies but miss subtle concerns |
| competent | I can identify when health issues require attention and apply appropriate strategies to protect wellbeing effectively |
| extending | I can transfer health identification skills to complex situations and integrate multiple protective strategies |

- self-check: Can I spot both obvious and subtle signs that health attention is needed?
- self-check: Are my protective strategies working effectively to maintain wellbeing?
- self-check: Can I handle complex health situations using multiple strategies?

_Feedback moves by level:_
- **no_evidence**
  - Guide student to notice one obvious health concern in a simple scenario
  - Demonstrate one basic protective strategy step by step
- **emerging**
  - Help student practice identifying health concerns without prompting
  - Show how to check if a strategy is working before moving to the next step
- **developing**
  - Point out subtle health indicators the student missed
  - Encourage combining two protective strategies for better effectiveness
- **competent**
  - Challenge student with complex scenarios involving multiple health factors
  - Guide integration of several protective strategies simultaneously

## Halted items

### KUD halted blocks

- `blk_0003` — severe_underspecification: meta_or_nonteachable
- `blk_0004` — severe_underspecification: meta_or_nonteachable
- `blk_0013` — classification_unreliable: no signature achieved 2/3 agreement across runs; observed signatures: [('items', (('know', 'Type 1'), ('know', 'Type 1'))), ('items', (('do_skill', 'Type 2'), ('know', 'Type 1'))), ('items', (('do_disposition', 'Type 3'), ('know', 'Type 1'), ('know', 'Type 1')))]
- `blk_0017` — severe_underspecification: This content is a meta-instructional statement about how schools should approach teaching protective content, not a specification of what students should know, understand, or be able to do. It provides guidance to educators about pedagogical approach but contains no teachable learning destination for students.
- `blk_0018` — severe_underspecification: This content is procedural guidance for schools about policy implementation and communication with parents, not learning objectives for pupils. It describes administrative processes rather than teachable content for students.
- `blk_0019` — severe_underspecification: meta_or_nonteachable
- `blk_0020` — severe_underspecification: meta_or_nonteachable
- `blk_0033` — severe_underspecification: meta_or_nonteachable - this is a section header/label with no substantive teachable content, just indicating a curriculum category
- `blk_0047` — severe_underspecification: meta_or_nonteachable
- `blk_0048` — severe_underspecification: meta_or_nonteachable - this is a curriculum section header with no substantive teachable content, only a category label
- `blk_0070` — severe_underspecification: meta_or_nonteachable
- `blk_0071` — severe_underspecification: meta_or_nonteachable
- `blk_0084` — severe_underspecification: meta_or_nonteachable
- `blk_0099` — severe_underspecification: meta_or_nonteachable
- `blk_0100` — severe_underspecification: meta_or_nonteachable
- `blk_0105` — severe_underspecification: meta_or_nonteachable
- `blk_0109` — severe_underspecification: This is a fragment of a larger sentence that provides no complete teachable claim or expectation. The content appears to be the middle portion of a sentence about what effective RSE does not do and how it supports learners, but without the complete context, no specific learning destination can be identified.
- `blk_0115` — severe_underspecification: meta_or_nonteachable
- `blk_0118` — severe_underspecification: meta_or_nonteachable
- `blk_0120` — severe_underspecification: meta_or_nonteachable
- `blk_0121` — severe_underspecification: meta_or_nonteachable
- `blk_0124` — severe_underspecification: This appears to be a fragment of a sentence or heading continuation with no complete teachable claim. The phrase 'up children.' lacks sufficient context to determine what propositional knowledge, skill, or disposition is being described.
- `blk_0136` — severe_underspecification: meta_or_nonteachable - this appears to be a reference citation or document metadata (Age of Marriage Act 2023 with page number 13) rather than teachable curriculum content
- `blk_0137` — severe_underspecification: meta_or_nonteachable - this is a section header/label with no substantive teachable content
- `blk_0161` — severe_underspecification: meta_or_nonteachable
- `blk_0162` — severe_underspecification: meta_or_nonteachable - this is a section header/label with no substantive teachable content, only indicating a curriculum category
- `blk_0181` — severe_underspecification: This fragment appears to be a continuation of a previous statement and lacks sufficient context to determine what specific knowledge, understanding, or capability is being described. The phrase 'and where to go for help and advice' by itself does not specify what help is needed for, what advice is sought, or what the learner should know or be able to do.
- `blk_0184` — severe_underspecification: meta_or_nonteachable - this is a footnote reference with no teachable content, only directing readers to an external report
- `blk_0194` — severe_underspecification: meta_or_nonteachable
- `blk_0195` — severe_underspecification: meta_or_nonteachable
- `blk_0199` — classification_unreliable: no signature achieved 2/3 agreement across runs; observed signatures: [('items', (('do_skill', 'Type 2'), ('do_skill', 'Type 2'))), ('items', (('do_skill', 'Type 2'),)), ('items', (('do_skill', 'Type 2'), ('know', 'Type 1')))]
- `blk_0214` — severe_underspecification: The content fragment 'to get help if needed' appears to be an incomplete sentence or continuation from previous content. It lacks sufficient context to determine what specific knowledge, understanding, or capability is being described. Without knowing what the 'help' refers to or under what circumstances it would be needed, no teachable learning target can be operationalised.
- `blk_0219` — severe_underspecification: This appears to be a sentence fragment from a larger statement about FGM, virginity testing and hymenoplasty. The content cuts off mid-sentence ('criminal offence for anyone to perform or') and lacks sufficient context to determine what specific knowledge, understanding, or capability is being targeted. Without the complete statement, no teachable destination can be identified.
- `blk_0221` — severe_underspecification: meta_or_nonteachable - content is only a page number with no teachable substance
- `blk_0230` — severe_underspecification: meta_or_nonteachable
- `blk_0231` — severe_underspecification: meta_or_nonteachable - this is a section header/label that contains no teachable content, only a navigation/organizational phrase
- `blk_0255` — severe_underspecification: meta_or_nonteachable - content is only a page number with no teachable claim, propositional content, or behavioural expectation
- `blk_0257` — severe_underspecification: meta_or_nonteachable
- `blk_0268` — severe_underspecification: The content is a sentence fragment 'support.' with no subject, verb, or complete propositional claim. Without the full sentence structure, there is no identifiable teachable destination - no factual knowledge to hold, no conceptual understanding to develop, no skill to deploy, and no sustained orientation to enact.
- `blk_0276` — severe_underspecification: The content 'help.' is a sentence fragment that provides no teachable destination - no propositional knowledge to understand, no skill to deploy, and no disposition to enact. It appears to be an incomplete statement that cannot be operationalised through any assessment route.
- `blk_0277` — severe_underspecification: meta_or_nonteachable
- `blk_0278` — severe_underspecification: meta_or_nonteachable
- `blk_0299` — severe_underspecification: meta_or_nonteachable
- `blk_0300` — severe_underspecification: meta_or_nonteachable
- `blk_0307` — severe_underspecification: meta_or_nonteachable - this is a section header/label with no substantive teachable content, only indicating a curriculum category
- `blk_0314` — severe_underspecification: meta_or_nonteachable
- `blk_0317` — severe_underspecification: meta_or_nonteachable
- `blk_0318` — severe_underspecification: meta_or_nonteachable
- `blk_0331` — severe_underspecification: meta_or_nonteachable
- `blk_0336` — severe_underspecification: meta_or_nonteachable - this is a section header/label that contains no teachable content, only indicating that basic first aid curriculum content will follow
- `blk_0341` — severe_underspecification: meta_or_nonteachable
- `blk_0342` — severe_underspecification: meta_or_nonteachable
- `blk_0349` — severe_underspecification: meta_or_nonteachable
- `blk_0353` — severe_underspecification: meta_or_nonteachable
- `blk_0359` — severe_underspecification: meta_or_nonteachable
- `blk_0360` — severe_underspecification: meta_or_nonteachable
- `blk_0378` — severe_underspecification: meta_or_nonteachable - content is only a page number with no teachable substance
- `blk_0379` — severe_underspecification: meta_or_nonteachable
- `blk_0394` — severe_underspecification: meta_or_nonteachable
- `blk_0398` — severe_underspecification: The content is a sentence fragment ('conditions.') that provides no teachable substance. It appears to be an incomplete heading or navigation element with no propositional content, procedural knowledge, or behavioral expectation that could be operationalized.
- `blk_0401` — severe_underspecification: meta_or_nonteachable
- `blk_0407` — severe_underspecification: meta_or_nonteachable - content is only a page number with no teachable substance
- `blk_0408` — severe_underspecification: meta_or_nonteachable
- `blk_0421` — severe_underspecification: meta_or_nonteachable
- `blk_0422` — severe_underspecification: meta_or_nonteachable
- `blk_0442` — severe_underspecification: meta_or_nonteachable
- `blk_0443` — severe_underspecification: meta_or_nonteachable - this is a section header/navigation label with no substantive teachable content
- `blk_0451` — severe_underspecification: Fragment appears to be continuation of previous content ('and/or knife crime') with no standalone teachable claim, propositional content, or behavioural expectation that could be operationalised
- `blk_0456` — severe_underspecification: meta_or_nonteachable - this is a section header/label with no substantive teachable content, only indicating a curriculum area
- `blk_0460` — severe_underspecification: meta_or_nonteachable
- `blk_0462` — severe_underspecification: The content is a sentence fragment that lacks both subject and predicate. 'emotional and physical health' appears to be the end of a larger statement about implications, but without the complete sentence structure, there is no teachable propositional claim, skill, or orientation that can be operationalised.
- `blk_0469` — severe_underspecification: meta_or_nonteachable

### LT stage halted clusters

- `cluster_10` — lt_set_unreliable: only 0/3 runs produced parseable output

### Band-statement stage halted LTs

- `cluster_06_lt_01` (Assertive Communication and Boundary Setting) — band_statements_gate_failed: 1 format/quality failures
  - failures: ['End of Primary:no_observable_verb']

### Supporting-components stage halted LTs

- `cluster_02_lt_01` (Building Safe and Positive Relationships) — supporting_unreliable: no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
- `cluster_07_lt_02` (Responding to Bullying and Stereotypes) — supporting_unreliable: no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
- `cluster_09_lt_01` (Recognising Trust and Safety Risks) — supporting_unreliable: no structural signature reached 2/3 agreement; signatures=[(('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
- `cluster_11_lt_02` (Analysing Relationship Challenges and Influences) — supporting_unreliable: no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
- `cluster_12_lt_02` (Understanding Sexual Consent Principles) — supporting_unreliable: no structural signature reached 2/3 agreement; signatures=[(('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
- `cluster_14_lt_01` (Understanding Emotions and Mental Health) — supporting_unreliable: no structural signature reached 2/3 agreement; signatures=[(('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
- `cluster_15_lt_02` (Making Responsible Digital Decisions) — supporting_unreliable: no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
- `cluster_17_lt_02` (Understanding Medical Consent Capacity) — supporting_unreliable: no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
- `cluster_02_lt_02` () — supporting_skipped_gate_fail: rubric has gate failures ['observable_verb']; not a stable anchor for supporting materials
- `cluster_06_lt_01` () — supporting_skipped_gate_fail: rubric has gate failures ['single_construct']; not a stable anchor for supporting materials
- `cluster_14_lt_02` () — supporting_skipped_gate_fail: rubric has gate failures ['single_construct']; not a stable anchor for supporting materials
- `cluster_04_lt_02` () — supporting_skipped_gen_fail: rubric generation failed for cluster_04_lt_02; no content to build from
- `cluster_05_lt_01` () — supporting_skipped_gen_fail: rubric generation failed for cluster_05_lt_01; no content to build from
- `cluster_11_lt_01` () — supporting_skipped_gen_fail: rubric generation failed for cluster_11_lt_01; no content to build from
- `cluster_13_lt_01` () — supporting_skipped_gen_fail: rubric generation failed for cluster_13_lt_01; no content to build from
- `cluster_16_lt_02` () — supporting_skipped_gen_fail: rubric generation failed for cluster_16_lt_02; no content to build from

