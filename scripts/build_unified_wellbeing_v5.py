"""
Build unified-wellbeing-data-v5.json and wellbeing-index-v5.json from
criterion-bank-v4_1.json (253 criteria, 506 edges) plus KUD v3 (existing
18 LTs) plus LT 4.4 KUD v2 (new, from LT_4_4_KUD_v2_20260423.md).

This script adds LT 4.4 — Emotional Development & Relationships — as the
20th learning target (inserted after lt_4_3 in the C4 competency group).

Does NOT overwrite unified-wellbeing-data-v4.json or wellbeing-index-v4.json.
"""
import json

CRIT_BANK_PATH = "docs/reference-corpus/real-wellbeing/criterion-bank-v4_1.json"
V4_UNIFIED     = "docs/reference-corpus/real-wellbeing/unified-wellbeing-data-v4.json"
V4_INDEX       = "docs/reference-corpus/real-wellbeing/wellbeing-index-v4.json"
UNIFIED_OUT    = "docs/reference-corpus/real-wellbeing/unified-wellbeing-data-v5.json"
INDEX_OUT      = "docs/reference-corpus/real-wellbeing/wellbeing-index-v5.json"

# ── Load inputs ───────────────────────────────────────────────────────────────
with open(CRIT_BANK_PATH) as f:
    bank = json.load(f)

with open(V4_UNIFIED) as f:
    v4_unified = json.load(f)

with open(V4_INDEX) as f:
    v4_index = json.load(f)

# ── Build (lt_id, band) → {criterion_ids, observation_indicators} from v4_1 ──
lt_band_data: dict = {}
for c in bank["criteria"]:
    for lt in c.get("associated_lt_ids", []):
        key = (lt, c["band"])
        if key not in lt_band_data:
            lt_band_data[key] = {"criterion_ids": [], "observation_indicators": []}
        lt_band_data[key]["criterion_ids"].append(c["criterion_id"])
        if c.get("observation_indicators"):
            lt_band_data[key]["observation_indicators"].extend(c["observation_indicators"])

# ── LT 4.4 KUD content (from LT_4_4_KUD_v2_20260423.md) ──────────────────────
LT_4_4_META = {
    "lt_name":        "Emotional Development & Relationships",
    "competency":     "C4 — Consent, Safety & Healthy Relationships",
    "knowledge_type": "T2",
    "compound":       True,
    "band_range":     {"start": "A", "end": "F"},
    "summary":        "Use knowledge of emotional and relational development to identify, explain, and analyse patterns in emotional experiences and relationships.",
    "prereq_lt_ids":  ["lt_4_1", "lt_4_2"],
    "bands": {
        "A": {
            "know": [
                "Feelings have names — common examples include happy, sad, angry, scared, proud, ashamed, excited, and surprised.",
                "People can have different feelings about the same situation; neither person’s feeling is wrong.",
            ],
            "understand": [
                "My feelings give me information about what I care about and what I need.",
            ],
            "do": "I can name my feelings and describe how I want to be treated by my friends.",
        },
        "B": {
            "know": [
                "Caring friendships have observable and repeatable qualities: they include listening, kindness, fairness, and showing up when the other person is upset.",
                "A friendship that consistently makes someone feel bad, scared, or ashamed is not a healthy one.",
                "Feelings within a relationship can change over time — both within the same relationship and from one relationship to another.",
            ],
            "understand": [
                "The way a friendship makes me feel over time, not just on one bad day, tells me something important about whether it is good for me.",
            ],
            "do": "I can describe what a caring friendship looks like and explain how my feelings change when a friendship is going well or not going well.",
        },
        "C": {
            "know": [
                "Sex hormones released during puberty — including oestrogen and testosterone — affect the intensity of emotional reactions, which is why feelings can feel stronger or more confusing during early adolescence. (Cross-reference LT 4.2 Band C for fuller biological content on puberty development.)",
                "A pattern in a relationship is a repeated tendency across multiple situations, not a single event; caring patterns include consistent mutual respect, and uncaring patterns include dismissal, control, or persistent disregard for the other person’s feelings.",
                "Emotional intensity during puberty is a normal developmental phase, not a permanent personality trait or evidence that something is wrong.",
            ],
            "understand": [
                "When my emotions feel unusually intense or confusing, this is often my developing body, not a sign that something is permanently wrong with me or with my relationships.",
            ],
            "do": "I can describe how physical and emotional changes during puberty affect my feelings and relationships, and identify patterns that distinguish a caring relationship from an uncaring one.",
        },
        "D": {
            "know": [
                "The prefrontal cortex — responsible for emotional regulation and impulse control — is not fully mature until the mid-twenties; the amygdala is fully developed earlier, which explains why adolescent emotional responses can be fast and intense before conscious reflection catches up. (Cross-reference LT 4.2 Band D for hormonal and puberty-specific biological content.)",
                "Attraction is associated with elevated dopamine and norepinephrine activity; rejection activates neural pathways that overlap with physical pain; loss triggers a non-linear grief response involving multiple emotional states.",
                "Healthy relational patterns include reciprocity, honest communication, and respect for boundaries; unhealthy patterns include attempts to control, emotional manipulation, deliberate inconsistency designed to create dependency, and consistent dismissal of the other person’s feelings.",
                "The course teaches three theoretical frameworks for understanding emotional systems, and these function as the analytical toolkit for Band D work: (i) dual-process models of emotion and cognition — fast, intuitive, automatic processing alongside slower, deliberative, reflective processing, and how the two interact; (ii) the stress-response window — how arousal level shapes access to analytical thinking, and what falls outside a person’s window of tolerance; (iii) habit formation — cue–routine–reward loops and how repeated emotional responses become patterned over time.",
                "Claims about emotional experience come in different kinds, and good analysis distinguishes them. (i) Empirical neuroscientific claims — such as prefrontal cortex maturation timelines — are supported by converging evidence and held with high confidence. (ii) Interpretive claims — such as ‘rejection activates neural pathways that overlap with physical pain’ — make reasonable inferences from more limited evidence and should be held more provisionally. (iii) Normative claims — such as what counts as a ‘healthy’ relational pattern — reflect values and cultural context, not biological necessity. At Band D, students identify which kind of claim they are making or evaluating when they analyse a scenario.",
            ],
            "understand": [
                "My emotional experiences, including attraction, rejection, and loss, have biological and psychological explanations — understanding those explanations does not make the experience less real, but it does give me more agency in choosing how to respond.",
            ],
            "do": "I can explain the biological and psychological basis of an emotional experience, identify healthy and unhealthy patterns in a described relationship, and use course concepts to analyse a personal or fictional experience of attraction, rejection, or loss.",
        },
        "E": {
            "know": [
                "Social learning theory holds that relationship scripts — learned patterns for how relationships are supposed to work — are absorbed from family, peer culture, and media and are often treated as natural rather than learned.",
                "Power in a relationship is not always visible; in peer relationships it shows up in specific observable patterns — who changes their plans when the other asks, who apologises more often regardless of who was actually wrong, whose emotional state sets the tone for the interaction, whose interests are talked about more often, whose social reputation is protected at the other’s expense, and who would bear the greater cost if the relationship ended.",
                "The same behaviour can carry different meanings depending on the relational history, the power differential involved, and the cultural context in which the relationship exists.",
            ],
            "understand": [
                "Every relational dynamic has multiple perspectives — what feels normal or acceptable from inside a relationship may look very different from outside it, or from the other person’s vantage point.",
            ],
            "do": "I can evaluate how biological, psychological, and social factors interact to shape a relational pattern, comparing the perspectives of the people involved and explaining how power or context affects the dynamic.",
        },
        "F": {
            "know": [
                "Attachment theory (Bowlby; Ainsworth; Mikulincer & Shaver) describes patterns — commonly named secure, anxious-preoccupied, dismissive-avoidant, and disorganised — that develop in early childhood and shape later relational tendencies. The theory has a strong empirical core (the basic secure/insecure distinction and its early-childhood origins are well-evidenced), a contested middle (the stability and exact structure of the four-style taxonomy into adulthood is debated in the research literature), and a popularised periphery (social-media and self-help ‘attachment style’ discourse routinely outruns the underlying evidence). At Band F, attachment theory is used both as an analytical framework for examining relationships and as a body of claims to evaluate critically against the evidence base.",
                "Cultural scripts for relationships vary substantially across cultures, generations, and social contexts; what is considered healthy, normal, or appropriate in a relationship reflects cultural and historical power, not biological necessity.",
                "Relational repair — following conflict, harm, or breakdown — involves acknowledgement, accountability, and negotiated restoration of trust; it is a skill that can be developed rather than an innate capacity.",
            ],
            "understand": [
                "The frameworks I use to analyse a relationship are not neutral — each illuminates certain aspects and obscures others; choosing a framework is itself an analytical and ethical act.",
            ],
            "do": "I can critically evaluate complex relational dynamics using multiple analytical frameworks, explaining how biological, psychological, social, and cultural factors intersect, and constructing a justified position on how the dynamic might be navigated or improved.",
        },
    },
}

# ── Build the LT 4.4 unified entry ───────────────────────────────────────────
ALL_BANDS = ["A", "B", "C", "D", "E", "F"]
T3_LTS = {"lt_1_1", "lt_1_2", "lt_1_3", "lt_3_2", "lt_5_2", "lt_7_2", "lt_8_3"}

def build_lt44_entry() -> dict:
    meta = LT_4_4_META
    start = meta["band_range"]["start"]
    end   = meta["band_range"]["end"]
    active_bands = ALL_BANDS[ALL_BANDS.index(start): ALL_BANDS.index(end) + 1]

    bands_out = {}
    for band in active_bands:
        band_kud = meta["bands"][band]
        cb = lt_band_data.get(("lt_4_4", band), {"criterion_ids": [], "observation_indicators": []})
        is_t3 = "lt_4_4" in T3_LTS  # False for LT 4.4
        obs = cb["observation_indicators"] if is_t3 else []

        bands_out[band] = {
            "know":                   band_kud["know"],
            "understand":             band_kud["understand"],
            "do":                     band_kud["do"],
            "criterion_ids":          cb["criterion_ids"],
            "prerequisite_lt_ids":    meta["prereq_lt_ids"],
            "observation_indicators": obs,
        }

    return {
        "lt_id":          "lt_4_4",
        "lt_name":        meta["lt_name"],
        "competency":     meta["competency"],
        "knowledge_type": meta["knowledge_type"],
        "compound":       meta["compound"],
        "band_range":     meta["band_range"],
        "summary":        meta["summary"],
        "bands":          bands_out,
    }


lt_4_4_entry = build_lt44_entry()

# ── Build v5 unified data ─────────────────────────────────────────────────────
v5_lts = []
for lt in v4_unified["learning_targets"]:
    v5_lts.append(lt)
    if lt["lt_id"] == "lt_4_3":
        v5_lts.append(lt_4_4_entry)

v5_unified = {
    "meta": {
        "schema_version": v4_unified["meta"]["schema_version"],
        "generated_date": "2026-04-23",
        "lt_count": len(v5_lts),
    },
    "learning_targets": v5_lts,
}

with open(UNIFIED_OUT, "w") as f:
    json.dump(v5_unified, f, indent=2, ensure_ascii=False)

print(f"Wrote {UNIFIED_OUT} ({len(v5_lts)} LTs)")

# ── Build v5 index ────────────────────────────────────────────────────────────
v5_index_entries = []
for entry in v4_index["learning_targets"]:
    v5_index_entries.append(entry)
    if entry["lt_id"] == "lt_4_3":
        v5_index_entries.append({
            "lt_id":          "lt_4_4",
            "lt_name":        LT_4_4_META["lt_name"],
            "competency":     LT_4_4_META["competency"],
            "knowledge_type": LT_4_4_META["knowledge_type"],
            "band_range":     LT_4_4_META["band_range"],
            "summary":        LT_4_4_META["summary"],
        })

v5_index = {
    "meta": {
        "schema_version": v4_index["meta"]["schema_version"],
        "generated_date": "2026-04-23",
        "lt_count": len(v5_index_entries),
    },
    "learning_targets": v5_index_entries,
}

with open(INDEX_OUT, "w") as f:
    json.dump(v5_index, f, indent=2, ensure_ascii=False)

print(f"Wrote {INDEX_OUT} ({len(v5_index_entries)} LTs)")
