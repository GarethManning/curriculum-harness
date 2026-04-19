# Hand-Curated Prerequisite Edges — Validation Set v1

**Status:** Approved by Gareth Manning, 2026-04-19.
**Scope:** Anchor sources only. Welsh CfW H&W, Common Core 7.RP, Ontario G7 History.
**Purpose:** Known-true prerequisite edges used to compute agreement rate against generated criterion banks. LT-level; mapped to criterion-level via `associated_lt_ids` after generation.

**Revisions applied:** Welsh edges 8, 9, 12 dropped. Ontario edges 1, 2, 3, 6 tags changed from `ontological_prerequisite` to `pedagogical_sequencing`.

## Agreement Rate Reporting

Two levels reported per source:

- **Primary (floor applies):** Edge exists — generator produces at least one criterion-level edge that recovers this LT-level edge via `associated_lt_ids` mapping. 50% floor. Below floor → halt and report.
- **Secondary (diagnostic only):** Edge exists AND the `reasoning_tag` on the generated edge matches. No floor. Reported for calibration.

---

## Welsh CfW H&W — 9 edges

Type 3 LTs excluded (no criteria in bank). Edges 8, 9, 12 dropped per review.

| # | LT A (prerequisite) | LT B (requires A) | Tag | Strength | Rationale |
|---|---|---|---|---|---|
| 1 | `cluster_05_lt_01` Analysing Decision Impacts | `cluster_05_lt_02` Evaluating Implications and Risks | ontological_prerequisite | high | Analysis of what impacts a decision has is cognitively required before evaluation of risks can be meaningful |
| 2 | `cluster_06_lt_01` Identifying Consequences of Career Choices | `cluster_06_lt_02` Making Informed Career Pathway Decisions | ontological_prerequisite | high | Must identify consequences (declarative) before reasoning about which pathway to choose (evaluative) |
| 3 | `cluster_07_lt_01` Identifying Social Influences on Identity | `cluster_07_lt_02` Analysing Cultural Development of Norms | ontological_prerequisite | high | Must know what social influences operate before analysing how those influences produce norms across cultures |
| 4 | `cluster_09_lt_01` Analysing Relationship Dynamics for Warning Signs | `cluster_09_lt_02` Evaluating Support Resources and Safety Strategies | pedagogical_sequencing | high | Must identify that a relationship is unhealthy before selecting strategies to address it |
| 5 | `cluster_08_lt_01` Understanding Healthy Relationships and Belonging | `cluster_09_lt_01` Analysing Relationship Dynamics for Warning Signs | pedagogical_sequencing | high | Recognising warning signs requires a prior concept of what a healthy relationship looks like (contrast model) |
| 6 | `cluster_03_lt_01` Connecting Experiences to Emotional Well-being | `cluster_04_lt_01` Communicating Feelings Appropriately | pedagogical_sequencing | medium | Understanding the link between experiences and emotion (conceptual) precedes communicating those emotions (expressive) |
| 7 | `cluster_01_lt_01` Understanding Health and Well-being Factors | `cluster_05_lt_01` Analysing Decision Impacts and Influencing Factors | ontological_prerequisite | medium | Domain knowledge about health factors is prerequisite content for analysing health-affecting decisions |
| 8 | `cluster_02_lt_02` Understanding Self-Care Impact | `cluster_05_lt_01` Analysing Decision Impacts and Influencing Factors | ontological_prerequisite | medium | Self-care knowledge is prerequisite domain content for the decision-analysis LT |
| 9 | `cluster_08_lt_01` Understanding Healthy Relationships and Belonging | `cluster_07_lt_02` Analysing Cultural Development of Norms | pedagogical_sequencing | low | Relationship understanding provides concrete examples against which cultural norms about relationships can be examined |

---

## Common Core 7.RP — 12 edges

All LTs are Type 1 or Type 2. Approved as-is.

| # | LT A (prerequisite) | LT B (requires A) | Tag | Strength | Rationale |
|---|---|---|---|---|---|
| 1 | `cluster_01_lt_02` Understanding Unit Rate Concepts | `cluster_01_lt_01` Computing Unit Rates from Ratios | ontological_prerequisite | high | Conceptual understanding of what a unit rate is precedes procedural computation of one |
| 2 | `cluster_02_lt_01` Recognizing Proportional Relationships | `cluster_02_lt_02` Representing Proportional Relationships | ontological_prerequisite | high | Must recognise a proportional relationship exists before representing it in any form |
| 3 | `cluster_03_lt_01` Identifying the Constant of Proportionality | `cluster_03_lt_02` Using the Constant in Proportional Equations | ontological_prerequisite | high | Must identify k before using it to write or interpret equations |
| 4 | `cluster_01_lt_01` Computing Unit Rates from Ratios | `cluster_04_lt_01` Solving Multistep Ratio and Percent Problems | ontological_prerequisite | high | Unit rate computation is a core tool in multistep ratio problems |
| 5 | `cluster_02_lt_01` Recognizing Proportional Relationships | `cluster_04_lt_01` Solving Multistep Ratio and Percent Problems | ontological_prerequisite | high | Must recognise when proportionality applies before selecting it as a solution strategy |
| 6 | `cluster_03_lt_02` Using the Constant in Proportional Equations | `cluster_04_lt_01` Solving Multistep Ratio and Percent Problems | ontological_prerequisite | high | Writing and using y = kx is a required tool for multistep proportional problem solving |
| 7 | `cluster_02_lt_01` Recognizing Proportional Relationships | `cluster_03_lt_01` Identifying the Constant of Proportionality | ontological_prerequisite | high | k only exists in proportional relationships — must recognise proportionality before extracting k |
| 8 | `cluster_02_lt_02` Representing Proportional Relationships | `cluster_04_lt_01` Solving Multistep Ratio and Percent Problems | pedagogical_sequencing | high | Representational fluency (tables, graphs, equations) is required to set up and solve multistep problems |
| 9 | `cluster_04_lt_01` Solving Multistep Ratio and Percent Problems | `cluster_04_lt_02` Applying Proportional Relationships to Real-World Contexts | pedagogical_sequencing | medium | Real-world application requires procedural fluency established in structured problem solving |
| 10 | `cluster_01_lt_02` Understanding Unit Rate Concepts | `cluster_02_lt_01` Recognizing Proportional Relationships | ontological_prerequisite | medium | Unit rate is a specific case of proportional relationship; conceptual understanding supports recognition of the broader class |
| 11 | `cluster_03_lt_01` Identifying the Constant of Proportionality | `cluster_04_lt_01` Solving Multistep Ratio and Percent Problems | ontological_prerequisite | high | k identification is prerequisite for equation-based multistep approaches |
| 12 | `cluster_02_lt_02` Representing Proportional Relationships | `cluster_04_lt_02` Applying Proportional Relationships to Real-World Contexts | pedagogical_sequencing | medium | Representing relationships in multiple forms is required for contextual application |

---

## Ontario G7 History — 12 edges

Type 3 LTs (cluster_06_lt_03, cluster_08_lt_02) excluded. Edges 1, 2, 3, 6 tags changed to `pedagogical_sequencing` per review; strength unchanged.

| # | LT A (prerequisite) | LT B (requires A) | Tag | Strength | Rationale |
|---|---|---|---|---|---|
| 1 | `cluster_04_lt_03` Recalling Key Events and Treaties | `cluster_04_lt_01` Analysing Causes of Key Events | pedagogical_sequencing | high | Must know what the events were before reasoning about their causes |
| 2 | `cluster_04_lt_01` Analysing Causes of Key Events | `cluster_04_lt_02` Evaluating Consequences and Significance | pedagogical_sequencing | high | Causal analysis is prerequisite to evaluating significance |
| 3 | `cluster_04_lt_03` Recalling Key Events and Treaties | `cluster_04_lt_02` Evaluating Consequences and Significance | pedagogical_sequencing | high | Cannot evaluate consequences of events you cannot identify |
| 4 | `cluster_05_lt_01` Describing Daily Life and Community Practices | `cluster_05_lt_02` Analysing Interactions and Historical Significance | ontological_prerequisite | high | Descriptive knowledge of communities is prerequisite to analysing how they interacted |
| 5 | `cluster_06_lt_01` Identifying Historical Contexts and Values | `cluster_06_lt_02` Analysing Values and Displacement Across Communities | ontological_prerequisite | high | Must identify what values/contexts existed before analysing how they shaped displacement |
| 6 | `cluster_08_lt_03` Identifying Key Events, Treaties, and Changes | `cluster_08_lt_01` Analysing Causes and Consequences of Historical Events | pedagogical_sequencing | high | Factual identification of events precedes causal and consequence analysis |
| 7 | `cluster_01_lt_01` Analysing Primary Sources for Historical Evidence | `cluster_04_lt_01` Analysing Causes of Key Events | ontological_prerequisite | high | Source analysis is the methodological tool through which causal claims are evidenced |
| 8 | `cluster_01_lt_01` Analysing Primary Sources for Historical Evidence | `cluster_05_lt_02` Analysing Interactions and Historical Significance | ontological_prerequisite | medium | Primary source analysis underpins evidence-based claims about interactions |
| 9 | `cluster_01_lt_02` Interpreting and Creating Historical Maps | `cluster_05_lt_01` Describing Daily Life and Community Practices | pedagogical_sequencing | medium | Geographic/spatial context supports description of where and how communities lived |
| 10 | `cluster_04_lt_02` Evaluating Consequences and Significance (1713–1800) | `cluster_08_lt_01` Analysing Causes and Consequences (1800+) | pedagogical_sequencing | medium | Temporal scaffolding: consequence reasoning from earlier period frames later causal analysis |
| 11 | `cluster_05_lt_02` Analysing Interactions and Historical Significance | `cluster_06_lt_02` Analysing Values and Displacement Across Communities | pedagogical_sequencing | medium | Interaction analysis precedes values-and-displacement analysis |
| 12 | `cluster_01_lt_01` Analysing Primary Sources for Historical Evidence | `cluster_08_lt_01` Analysing Causes and Consequences of Historical Events | ontological_prerequisite | medium | Source analysis methods transfer across time periods; prerequisite methodological competency for all analytical LTs |

---

*Curated by Claude Code, 2026-04-19. Approved by Gareth Manning, 2026-04-19. Used as validation input for Session 4c-4 criterion bank generation.*
