# Criterion Decomposition Rules — v1

**Status:** Active. Governs Session 4c-4 criterion generation.
**Date:** 2026-04-19

## Purpose

These rules determine how a Learning Target (LT) is decomposed into one or more criteria in the criterion bank. They exist because:

1. Some LTs encode a single, indivisible competency — one criterion is correct.
2. Others encode compound or multi-target competencies — forcing a single criterion loses the granularity that adaptive systems need.
3. The decomposition approach differs between procedural/hierarchical domains (maths, science) and horizontal/dispositional domains (history, RSHE, wellbeing).

Criteria must be independently demonstrable. A criterion that always co-occurs with another, with no assessment scenario where one fires without the other, should be merged.

---

## Rule 1 — When one criterion is sufficient

Produce exactly one criterion when all of the following hold:

- The LT has a **single action verb** (or a single cognitive operation: recall, identify, explain, apply).
- The LT targets a **single knowledge domain** or a single narrowly-scoped skill cluster.
- There is **no plausible assessment scenario** in which a student could demonstrate part of the LT but not the rest.

**Examples of single-criterion LTs:**

- `Recognizing Proportional Relationships` (Common Core, cluster_02_lt_01) — recognition is a single cognitive act applied to a class of inputs. Although recognition can occur via graphs, tables, or equations, these are alternative *representations* of the same competency, not distinct sub-skills. → 1 criterion.
- `Identifying Consequences of Career Choices` (Welsh CfW, cluster_06_lt_01) — identification is a single cognitive act. The plural "consequences" refers to the domain scope, not to decomposable sub-skills. → 1 criterion.
- `Recalling Key Events and Treaties` (Ontario, cluster_04_lt_03) — though the domain is broad, recall of content knowledge within a defined scope is one assessable act. → 1 criterion.

---

## Rule 2 — When to decompose into multiple criteria

Decompose when one or more of the following triggers are present:

### Trigger A: Compound verbs at different cognitive levels

The LT statement contains two or more verbs that are **independently assessable at different cognitive levels**.

Test: could a student demonstrate the first verb without the second, in a realistic assessment scenario?

**Example (hierarchical domain):** `Computing Unit Rates from Ratios` + `Understanding Unit Rate Concepts` are separate LTs in Common Core — correctly so. If they were one LT, the verb "compute" (procedural) and "explain" (conceptual) would each demand their own criterion. A student can compute by rote without being able to explain; a student can explain a concept without yet computing fluently.

**Example (horizontal domain):** `Analysing Causes of Key Events` (Ontario, cluster_04_lt_01) contains a single analysis verb applied to a complex domain. It does not decompose on verb grounds — but see Trigger B.

### Trigger B: Multi-target statements covering distinct knowledge domains

The LT covers domains that are **separately teachable and separately assessable**.

Test: could a teacher design a lesson that addresses domain A without touching domain B? Could a student be competent on domain A and not yet on domain B?

**Example (hierarchical domain):** A hypothetical LT "I can identify ratios and explain proportional reasoning" spans declarative identification and conceptual explanation. These are separately teachable and separately assessable → decompose.

**Example (horizontal domain):** `Analysing Interactions and Historical Significance` (Ontario, cluster_05_lt_02) involves two domains — interactions between groups, and historical significance of key figures. A student might reliably analyse interactions (patterns, dynamics) while struggling with significance judgements (which require historical perspective and context). → decompose into: (a) analysing interactions between groups/individuals; (b) assessing historical significance of key figures and communities.

### Trigger C: Distinct procedural sub-skills with separable failure modes

The LT involves a procedural sequence where failure at step N does not imply failure at step N+1 (or vice versa).

**Example (hierarchical domain):** `Using the Constant in Proportional Equations` (Common Core, cluster_03_lt_02) — writing an equation (procedural encoding) and interpreting ordered pairs (reading/decoding) are separable. A student can write y = kx correctly but mis-read (3, 6) as meaning k = 3. → decompose: (a) write proportional equations using k; (b) interpret ordered pairs in proportional contexts.

**Example (horizontal domain):** `Interpreting and Creating Historical Maps` (Ontario, cluster_01_lt_02) — interpreting (reading existing maps) and creating (constructing maps to represent information) are separable skills with distinct failure modes. A student can interpret without creating, or vice versa. → decompose: (a) interpret historical maps for spatial/temporal information; (b) create historical maps to represent information.

---

## Rule 3 — Granularity test

Before finalising a decomposition, apply this test to each proposed criterion:

> "Can a teacher design a task or assessment moment that would give clear evidence for this criterion and this criterion alone?"

If the answer is no — if every task that touches this criterion also necessarily touches another — merge the two criteria.

If the answer is yes for each criterion independently, the decomposition is valid.

**Anti-pattern:** Over-decomposing a single act into component steps that are never separable in practice. For example, decomposing `Identifying Social Influences on Identity` (Welsh, cluster_07_lt_01) into (a) identifying economic influences, (b) identifying cultural influences, (c) identifying media influences is an over-decomposition — the LT requires integrative awareness, not enumeration of each category separately. The source treats these as examples of a single act. → 1 criterion.

---

## Rule 4 — Horizontal-domain decomposition

Horizontal domains (history, RSHE, wellbeing, social sciences) do not follow procedural step-chains. The maths-style "step A → step B → step C" decomposition does not transfer.

### What drives decomposition in horizontal domains

| Driver | Example | Decision |
|---|---|---|
| Distinct analytical operations | Cause vs consequence | Decompose |
| Different evidence types | Primary source analysis vs map reading | Decompose |
| Different stance requirements | Description vs evaluation | Decompose |
| Content vs method | Recall of events vs analytical reasoning about them | Decompose |
| Alternative expressions of the same capacity | Identifying social influences via media, culture, peers | Do NOT decompose — these are examples, not sub-skills |

### Worked example — Ontario G7 History

**LT:** `Analysing Causes of Key Events` (cluster_04_lt_01)
Definition: "identify immediate triggers and underlying conditions contributing to key events between 1713 and 1800, distinguishing short-term from long-term causes."

Decomposition analysis:
- "Identify immediate triggers" — recall-proximate act, domain-specific knowledge
- "Identify underlying conditions" — conceptual inference act, requires pattern recognition across events
- "Distinguish short-term from long-term causes" — analytical categorisation requiring comparative judgment

These are three distinct cognitive operations that are independently assessable:
- A student can identify immediate triggers (what happened) without correctly distinguishing short/long-term causality (why it mattered over time).
- Distinguishing cause type requires both kinds of identification.

→ Decompose into:
1. Identify immediate triggers of key events (recall + recognition)
2. Identify underlying long-term conditions (inference + pattern recognition)
3. Distinguish and categorise short-term from long-term causes (comparative analysis)

### Worked example — Dispositional content (Welsh CfW H&W)

**LT:** `Analysing Decision Impacts and Influencing Factors` (cluster_05_lt_01)
Definition: "analyse how decisions and actions impact myself, others, and society, and identify the factors that influence decisions."

Note: This is a Type 2 LT (reasoning_quality_rubric). The dispositional layer (Type 3) is handled separately via observation indicators. Type 2 criteria capture the observable reasoning quality.

Decomposition analysis:
- "Analyse how decisions impact self, others, and society" — three-scope analysis (personal, social, societal); these scopes are distinct enough that a student may demonstrate self-focused analysis without yet extending to societal impacts.
- "Identify factors that influence decisions" — a separate cognitive act: recognising external and internal influence. A student can enumerate influencing factors without demonstrating multi-scope impact analysis.

→ Decompose into:
1. Analyse decision impacts across personal, social, and societal scope (multi-scope analysis)
2. Identify and explain factors that influence decision-making (factor identification)

**Important scoping note for dispositional LTs:** The criterion bank captures what is *observable and demonstrable* in a teacher-designed assessment context. For Type 2 dispositional LTs, this means the quality of *reasoning displayed*, not the authenticity of dispositional orientation (which belongs to Type 3 observation indicators). Do not decompose on dispositional grounds — only on reasoning-quality grounds.

---

## Rule 5 — Procedural vs conceptual decomposition

These differ not in *whether* to decompose but in *what drives the decomposition*:

| | Procedural (Hierarchical) | Conceptual (Horizontal) |
|---|---|---|
| **Primary decomposition driver** | Separable procedural steps with distinct failure modes | Distinct cognitive operations at different abstraction levels |
| **Over-decomposition risk** | Splitting steps that always co-occur in any valid task | Splitting into content categories that are examples, not distinct skills |
| **Underdecomposition risk** | Collapsing computation with interpretation | Treating multi-scope analysis as a single act |
| **Prerequisite structure** | Often linear (step A required before step B) | Often branching (multiple inputs required for a synthesis criterion) |
| **Granularity test** | "Can a student fail at step N and still succeed at step N+2?" | "Can a student demonstrate analytical operation A without yet mastering B?" |

Procedural decomposition produces criteria that are typically linked in linear prerequisite chains. Conceptual decomposition in horizontal domains typically produces criteria with branching prerequisites — where a higher-order criterion (e.g. "distinguish cause type") requires multiple lower-order criteria (e.g. "identify triggers", "identify long-term conditions") as simultaneous prerequisites.

---

## Summary: decomposition decision table

| LT characteristic | Action |
|---|---|
| Single verb, single domain, no separable failure mode | 1 criterion |
| Compound verbs at different cognitive levels | Decompose (one criterion per cognitive level) |
| Multi-target covering separately teachable domains | Decompose (one criterion per domain) |
| Procedural sub-skills with separable failure modes | Decompose (one criterion per sub-skill) |
| Content examples listed within a single act | Do NOT decompose (examples ≠ sub-skills) |
| Type 3 LT (dispositional / observation indicator) | Exclude from criterion bank v1 |

---

*Rules v1 written 2026-04-19 (Session 4c-4 pre-work). Governs anchor source generation: Welsh CfW H&W, Common Core 7.RP, Ontario G7 History.*
