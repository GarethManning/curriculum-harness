#!/usr/bin/env python3
"""
Phase 2a: Build visualisation-ready JSON files from REAL wellbeing framework artefacts.

Produces four normalised JSON files + README in:
  docs/reference-corpus/real-wellbeing/visualisation-data/

Source artefacts (read-only):
  unified-wellbeing-data-v6.json  — KUD content, LT structure, band arrays
  criterion-bank-v5_1.json        — 269 criteria with full descriptors
  band-conventions.json           — canonical band labels
  real-wellbeing-x-all-frameworks-v4-matrix.md  — crosswalk data
"""

import json
import re
import os
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "docs/reference-corpus/real-wellbeing"
CROSSWALK_DIR = REPO_ROOT / "docs/reference-corpus/crosswalks"
OUT_DIR = DATA_DIR / "visualisation-data"

UNIFIED_DATA = DATA_DIR / "unified-wellbeing-data-v6.json"
CRITERION_BANK = DATA_DIR / "criterion-bank-v5_1.json"
BAND_CONVENTIONS = DATA_DIR / "band-conventions.json"
CROSSWALK_MATRIX = CROSSWALK_DIR / "real-wellbeing-x-all-frameworks-v4-matrix.md"

ALL_BANDS = ["A", "B", "C", "D", "E", "F"]

# One-paragraph descriptions for each competency — authored from KUD and LT content.
COMPETENCY_DESCRIPTIONS = {
    "C1": (
        "Emotional Intelligence encompasses students' capacities to notice, name, and regulate their own emotions; "
        "read and respond to others' emotional states with empathy and perspective; and develop a stable, "
        "culturally-situated sense of personal identity. It is the affective and relational foundation for all "
        "learning and wellbeing in the REAL framework, sequenced from naming feelings and using calming strategies "
        "at Band A through to articulating a personal regulation system and navigating identity across cultural "
        "contexts at Band F."
    ),
    "C2": (
        "Attention and Reflective Practices develops students' capacity to direct and sustain focused attention "
        "using deliberate strategies, notice when attention breaks down and recover it, and apply reflective "
        "decision-making that weighs options, values, and evidence before acting. These are the executive-function "
        "anchors of self-directed learning, progresssing from single-sense attention tasks and single-option "
        "reflection at Band A to metacognitive attention audits and reasoned position-taking on high-stakes "
        "decisions at Band F."
    ),
    "C3": (
        "Physical Wellbeing and Self-Care builds students' knowledge of how bodily needs, health habits, and "
        "self-care routines support overall functioning, alongside the capacity to access reliable health "
        "information, maintain protective practices under stress, and construct a personalised resilience "
        "framework. It sequences from naming basic bodily needs and practising simple routines at Band A to "
        "designing sustainable habits that account for structural and social constraints at Band F."
    ),
    "C4": (
        "Consent, Safety and Healthy Relationships equips students to navigate bodily autonomy, consent, puberty, "
        "sexual health, relationship dynamics, bystander responsibility, and the emotional development "
        "underlying healthy relationships. It integrates propositional knowledge with relational and dispositional "
        "skill across five LTs, spanning T2 sequential content (LTs 4.1–4.4) and a T3 dispositional strand "
        "(LT 4.5), from naming trusted adults and body parts at Band A to facilitating peer discussion on "
        "consent and critically evaluating complex relational dynamics at Band F."
    ),
    "C5": (
        "Community, Purpose and Belonging develops students' interpersonal communication across contexts — "
        "including disagreement, cultural difference, and power asymmetry — and their capacity to engage "
        "meaningfully with communities, act on real needs, and develop a sense of purpose grounded in values "
        "and collective contribution. It sequences from active listening and offering kind responses at Band A "
        "to navigating systemic factors in empathic responses and leading civic action at Band F."
    ),
    "C6": (
        "Wellbeing Science and Literacy gives students a working scientific vocabulary for understanding stress, "
        "emotion, attention, and habit mechanisms, and the evidence-literacy skills to evaluate health "
        "information critically. It treats scientific knowledge of wellbeing as learnable curriculum content, "
        "not background assumption, progressing from naming body signals and basic physiological needs at Band A "
        "to integrating multiple systems in an evidence-grounded explanation and evaluating health claims "
        "using source and study-design criteria at Band F."
    ),
    "C7": (
        "Metacognitive Self-Direction develops students' capacity to notice, name, and analyse their own patterns "
        "of thinking and behaviour; design and test targeted adjustments; and sustain independent self-direction "
        "in practice as a dispositional orientation across contexts and over time. It sequences from identifying "
        "a simple behaviour pattern at Band A to constructing and applying a named personal metacognitive "
        "framework across sustained high-stakes challenges at Band F."
    ),
    "C8": (
        "Critical Digital Literacy equips students to evaluate claims and information in digital environments, "
        "analyse how digital products are designed to shape attention and behaviour through persuasive design, "
        "and maintain healthy boundaries and wellbeing-supporting practices in their digital lives. It is REAL's "
        "most systematic SEL-adjacent treatment of digital wellbeing, covering epistemic (LT 8.1), psychological "
        "(LT 8.2), and practical-dispositional (LT 8.3) dimensions from Band A through Band F."
    ),
}

THEME_LABELS = {
    "T01": "Emotional Awareness, Vocabulary & Self-Regulation",
    "T02": "Empathy & Perspective-Taking",
    "T03": "Conflict Resolution & Relationship Repair",
    "T04": "Focused Attention & Mindfulness",
    "T05": "Reflective & Values-Based Decision-Making",
    "T06": "Physical Health Habits",
    "T07": "Self-Care, Help-Seeking & Resilience",
    "T08": "Bodies, Boundaries & Consent",
    "T09": "Puberty, Sexual Health & Safe Choices",
    "T10": "Interpersonal & Assertive Communication",
    "T11": "Community Engagement, Purpose & Civic Action",
    "T12": "Wellbeing Science & Neuroscience Literacy",
    "T13": "Health & Evidence Literacy",
    "T14": "Metacognition & Self-Directed Learning",
    "T15": "Personal Identity & Self-Concept",
    "T16": "Family Diversity & Relationship Structures",
    "T17": "Online Safety & Digital Wellbeing",
    "T18": "Bullying, Stereotyping & Anti-Discrimination",
    "T19": "Physical Activity & Movement",
    "T20": "Nutrition & Food Literacy",
    "T21": "Risk Assessment & Safety",
    "T22": "Growth Mindset & Self-Efficacy",
    "T23": "Social Justice, Rights & Advocacy",
}


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────

def extract_competency_id(comp_string):
    """'C1 — Emotional Intelligence' → 'C1'"""
    if not comp_string:
        return None
    m = re.match(r"(C\d+)", comp_string)
    return m.group(1) if m else None


def extract_competency_name(comp_string):
    """'C1 — Emotional Intelligence' → 'Emotional Intelligence'"""
    if not comp_string:
        return None
    parts = comp_string.split(" — ", 1)
    return parts[1].strip() if len(parts) > 1 else comp_string


def lt_type_to_knowledge_type(lt_type):
    """'Type 1' → 'T1'"""
    return {"Type 1": "T1", "Type 2": "T2", "Type 3": "T3"}.get(lt_type, lt_type)


def band_range_to_list(band_range):
    """{'start': 'A', 'end': 'F'} → ['A','B','C','D','E','F']"""
    if not band_range:
        return list(ALL_BANDS)
    start = band_range.get("start", "A")
    end = band_range.get("end", "F")
    si = ALL_BANDS.index(start) if start in ALL_BANDS else 0
    ei = ALL_BANDS.index(end) + 1 if end in ALL_BANDS else 6
    return ALL_BANDS[si:ei]


def normalize_list(value):
    """Ensure value is a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v is not None]
    return [str(value)]


# ─────────────────────────────────────────
# 1. framework.json
# ─────────────────────────────────────────

def build_framework(unified, bands_meta):
    lts_by_comp = {}

    for lt in unified["learning_targets"]:
        comp_str = lt.get("competency", "")
        comp_id = extract_competency_id(comp_str)
        comp_name = extract_competency_name(comp_str)

        if comp_id not in lts_by_comp:
            lts_by_comp[comp_id] = {
                "competency_id": comp_id,
                "competency_name": comp_name,
                "competency_description": COMPETENCY_DESCRIPTIONS.get(comp_id, ""),
                "lts": [],
            }

        bands_obj = {}
        for band_letter in ALL_BANDS:
            band_data = lt["bands"].get(band_letter)
            if band_data is None:
                # LT doesn't cover this band (e.g. LT 4.2 starts at B)
                continue
            band_label = bands_meta["bands"][band_letter]["band_label"]
            bands_obj[band_letter] = {
                "band_letter": band_letter,
                "band_label": band_label,
                "know_items": normalize_list(band_data.get("know")),
                "understand_items": normalize_list(band_data.get("understand")),
                "do_items": normalize_list(band_data.get("do")),
                "criterion_ids": band_data.get("criterion_ids") or [],
            }

        lt_obj = {
            "lt_id": lt["lt_id"],
            "lt_name": lt.get("lt_name", ""),
            "competency_id": comp_id,
            "knowledge_type": lt.get("knowledge_type", ""),
            "lt_description": lt.get("summary", ""),
            "compound": lt.get("compound", False),
            "band_range": lt.get("band_range", {}),
            "bands": bands_obj,
        }
        lts_by_comp[comp_id]["lts"].append(lt_obj)

    competencies = [lts_by_comp[k] for k in sorted(lts_by_comp.keys())]
    lt_total = sum(len(c["lts"]) for c in competencies)

    return {
        "meta": {
            "schema_version": "1.0",
            "generated_date": str(date.today()),
            "source_files": [
                "docs/reference-corpus/real-wellbeing/unified-wellbeing-data-v6.json",
                "docs/reference-corpus/real-wellbeing/band-conventions.json",
            ],
            "competency_count": len(competencies),
            "lt_count": lt_total,
        },
        "competencies": competencies,
    }


# ─────────────────────────────────────────
# 2. criteria.json
# ─────────────────────────────────────────

def build_criteria(bank, unified):
    # Build lt_id → competency_id lookup
    lt_to_comp = {}
    for lt in unified["learning_targets"]:
        comp_id = extract_competency_id(lt.get("competency", ""))
        lt_to_comp[lt["lt_id"]] = comp_id

    criteria_out = []
    for c in bank["criteria"]:
        lt_ids = c.get("associated_lt_ids", [])
        lt_id = lt_ids[0] if lt_ids else None
        comp_id = lt_to_comp.get(lt_id)

        band_letter = c.get("band")   # 'A'–'F' (field name is 'band', not 'band_letter')
        band_label = c.get("band_label", "")
        lt_type = c.get("lt_type", "")
        kt = lt_type_to_knowledge_type(lt_type)

        obj = {
            "criterion_id": c["criterion_id"],
            "lt_id": lt_id,
            "competency_id": comp_id,
            "band_letter": band_letter,
            "band_label": band_label,
            "band_position": band_letter,
            "knowledge_type": kt,
            "criterion_statement": c.get("criterion_statement", ""),
        }

        if lt_type in ("Type 1", "Type 2"):
            obj["competency_level_descriptors"] = c.get("competency_level_descriptors") or {}
        elif lt_type == "Type 3":
            obj["observation_indicators"] = c.get("observation_indicators") or []
            obj["confusable_behaviours"] = c.get("confusable_behaviours") or []
            obj["absence_indicators"] = c.get("absence_indicators") or []
            obj["conversation_prompts"] = c.get("conversation_prompts") or []

        obj["prerequisite_criterion_ids"] = c.get("prerequisite_criterion_ids") or []
        criteria_out.append(obj)

    return {
        "meta": {
            "schema_version": "1.0",
            "generated_date": str(date.today()),
            "source_file": "docs/reference-corpus/real-wellbeing/criterion-bank-v5_1.json",
            "total_criteria": len(criteria_out),
        },
        "criteria": criteria_out,
    }


# ─────────────────────────────────────────
# 3. crosswalk.json — pairs
# ─────────────────────────────────────────

EXTERNAL_FRAMEWORKS = ["RSHE", "Welsh CfW", "CASEL", "Circle Solutions"]


def _lt_header_to_id(header):
    """'LT 1.1 Self-Awareness & Regulation *(new in v4)*' → 'lt_1_1'"""
    m = re.search(r"LT\s+(\d+)\.(\d+)", header)
    if m:
        return f"lt_{m.group(1)}_{m.group(2)}"
    return None


def _parse_alignment_cell(cell):
    """
    Return (alignment_form, rationale) from a table cell like:
      'partial-alignment (RSHE names managing emotions...)'
    or just:
      'absent'
    """
    cell = cell.strip().rstrip("*").strip()
    # Match: form (rationale)
    m = re.match(r"^([\w-]+)\s*\((.+)\)\s*$", cell, re.DOTALL)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    # No parenthetical — just a form
    valid_forms = {
        "aligned-with-reciprocal-treatment",
        "partial-alignment",
        "reversed",
        "absent",
    }
    token = cell.split()[0] if cell.split() else ""
    if token in valid_forms:
        return token, None
    return cell, None


def parse_pairs(matrix_text, unified):
    """Parse 84 LT × framework alignment pairs from the Per-LT alignment forms table."""
    lt_lookup = {}
    for lt in unified["learning_targets"]:
        comp_id = extract_competency_id(lt.get("competency", ""))
        lt_lookup[lt["lt_id"]] = {
            "lt_name": lt.get("lt_name", ""),
            "competency_id": comp_id,
            "band_range": lt.get("band_range", {"start": "A", "end": "F"}),
        }

    # Find the Per-LT section
    marker = "## Per-LT alignment forms"
    if marker not in matrix_text:
        print("  WARNING: Per-LT alignment forms section not found in matrix.", file=sys.stderr)
        return []
    section = matrix_text.split(marker, 1)[1]

    pairs = []
    for line in section.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Skip separator rows (|---|---|...)
        if re.match(r"\|[-| ]+\|", line):
            continue

        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 5:
            continue

        lt_header = cells[0].strip()
        # Skip header row
        if lt_header in ("LT", "LT name", ""):
            continue

        lt_id = _lt_header_to_id(lt_header)
        if not lt_id:
            continue
        if lt_id not in lt_lookup:
            print(f"  WARNING: lt_id '{lt_id}' from crosswalk not found in unified data.", file=sys.stderr)
            continue

        lt_info = lt_lookup[lt_id]
        bands_real = band_range_to_list(lt_info["band_range"])

        for i, fw in enumerate(EXTERNAL_FRAMEWORKS):
            cell = cells[i + 1] if (i + 1) < len(cells) else ""
            alignment_form, rationale = _parse_alignment_cell(cell)

            pairs.append({
                "lt_id": lt_id,
                "lt_name": lt_info["lt_name"],
                "competency_id": lt_info["competency_id"],
                "external_framework": fw,
                "alignment_form": alignment_form,
                "rationale": rationale,
                "bands_covered_real": bands_real,
                # Not parseable from prose matrix without invention — null per spec instruction.
                "bands_covered_external": None,
            })

    return pairs


# ─────────────────────────────────────────
# 3. crosswalk.json — themes
# ─────────────────────────────────────────

def parse_themes(matrix_text):
    """
    Parse 23 theme objects with band-level coverage flags and gap_count from the main matrix table.

    Matrix columns: Theme | Band | REAL | RSHE | Welsh CfW | CASEL SEL | Circle Solutions | gap_count
    """
    FW_NORM = ["REAL", "RSHE", "Welsh CfW", "CASEL", "Circle Solutions"]

    marker = "## Matrix"
    if marker not in matrix_text:
        print("  WARNING: ## Matrix section not found.", file=sys.stderr)
        return []
    matrix_section = matrix_text.split(marker, 1)[1]
    # Stop at next ## section
    next_section = re.search(r"\n## ", matrix_section)
    if next_section:
        matrix_section = matrix_section[: next_section.start()]

    themes = {}
    current_theme_id = None

    for line in matrix_section.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        if re.match(r"\|[-| ]+\|", line):
            continue

        cells = [c.strip() for c in line.split("|")[1:-1]]
        if not cells:
            continue

        first = cells[0]

        # Theme header row: | **T01 — Emotional Awareness...** | | ... |
        header_m = re.match(r"\*\*(T\d{2})\s*[—-]\s*(.+?)\*\*", first)
        if header_m:
            current_theme_id = header_m.group(1)
            label = THEME_LABELS.get(current_theme_id, header_m.group(2).strip())
            if current_theme_id not in themes:
                themes[current_theme_id] = {
                    "theme_id": current_theme_id,
                    "theme_name": label,
                    "coverage_by_framework_by_band": {fw: {} for fw in FW_NORM},
                    "gap_count_by_band": {},
                }
            continue

        # Data row: | T01 | A | ... | ... | ... | ... | ... | 0 |
        if len(cells) >= 8 and current_theme_id:
            row_theme = cells[0]
            band = cells[1]
            if row_theme == current_theme_id and band in ALL_BANDS:
                t = themes[current_theme_id]
                # gap_count is last column (index 7)
                try:
                    gap_count = int(cells[7])
                except (ValueError, IndexError):
                    gap_count = None
                t["gap_count_by_band"][band] = gap_count

                # Framework cells: indices 2–6 → REAL, RSHE, Welsh CfW, CASEL SEL, CS
                fw_cells = cells[2:7]
                for fw_norm, cell_content in zip(FW_NORM, fw_cells):
                    covered = bool(cell_content) and cell_content not in ("—", "--", "")
                    t["coverage_by_framework_by_band"][fw_norm][band] = covered

    return [themes[k] for k in sorted(themes.keys())]


def build_crosswalk(matrix_text, unified):
    pairs = parse_pairs(matrix_text, unified)
    themes = parse_themes(matrix_text)
    return {
        "meta": {
            "schema_version": "1.0",
            "generated_date": str(date.today()),
            "source_file": "docs/reference-corpus/crosswalks/real-wellbeing-x-all-frameworks-v4-matrix.md",
            "pair_count": len(pairs),
            "theme_count": len(themes),
            "note_bands_covered_external": (
                "bands_covered_external is null for all pairs. "
                "The v4 matrix prose does not express external band coverage per LT in a parseable form; "
                "null is reported per the Phase 2a gap-handling rule rather than invented."
            ),
        },
        "pairs": pairs,
        "themes": themes,
    }


# ─────────────────────────────────────────
# 4. frameworks-meta.json
# ─────────────────────────────────────────

def build_frameworks_meta():
    frameworks = [
        {
            "framework_id": "REAL",
            "framework_name": "REAL School Budapest Wellbeing Framework",
            "framework_description": (
                "The REAL Wellbeing Framework is an internal school curriculum framework developed by REAL School "
                "Budapest, covering 7 competencies and 21 learning targets across 6 developmental bands (A–F, "
                "Kindergarten through Grade 12). It integrates social-emotional learning, wellbeing science, and "
                "dispositional development using a three-type knowledge architecture: T1 (Sequential — propositional "
                "knowledge with a fixed learning order), T2 (Horizontal — competency assessed by rubric), and T3 "
                "(Dispositional — observed across contexts rather than assessed at a point in time). All content is "
                "first-party authored with high confidence."
            ),
            "source_jurisdiction": "Hungary (Budapest)",
            "year_published": 2026,
            "band_mapping": {
                "A": "K–2 — Water + Air Dragons (approx ages 5–7)",
                "B": "G3–4 — Earth Dragons (approx ages 8–10)",
                "C": "G5–6 — Fire Dragons (approx ages 10–12)",
                "D": "G7–8 — Metal + Light Dragons (approx ages 12–13)",
                "E": "G9–10",
                "F": "G11–12",
            },
            "source_file_path": "docs/reference-corpus/real-wellbeing/unified-wellbeing-data-v6.json",
            "confidence": "high",
            "license_note": "Proprietary — REAL School Budapest internal framework. All rights reserved.",
        },
        {
            "framework_id": "RSHE",
            "framework_name": "UK DfE Statutory Relationships, Sex and Health Education (July 2025)",
            "framework_description": (
                "The UK Department for Education statutory RSHE programme (July 2025 edition) mandates Relationships "
                "Education, Relationships and Sex Education, and Health Education for all state schools in England. "
                "It is structured in two developmental phases — End of Primary (KS1–2) and End of Secondary (KS3–4) "
                "— which map to REAL Bands A–C and C–E respectively at medium confidence. Band F has no equivalent "
                "RSHE content. The framework is primarily propositionally framed with a lower proportion of "
                "observational or dispositional content than REAL."
            ),
            "source_jurisdiction": "England (UK)",
            "year_published": 2025,
            "band_mapping": {
                "End of Primary": "Bands A–C (medium confidence, ambiguous; covers KS1–2, approx ages 5–11)",
                "End of Secondary": "Bands C–E (medium confidence, ambiguous; covers KS3–4, approx ages 11–16)",
                "Band F equivalent": "None — RSHE has no post-16 content",
            },
            "source_file_path": "docs/reference-corpus/uk-statutory-rshe/band-tagged-rshe-v1.json",
            "confidence": "medium",
            "license_note": "Crown Copyright. Open Government Licence v3.0. Source: DfE, July 2025.",
        },
        {
            "framework_id": "Welsh CfW",
            "framework_name": "Welsh Curriculum for Wales — Health and Well-being Area of Learning and Experience",
            "framework_description": (
                "The Welsh Curriculum for Wales (formally adopted 2022) Health and Well-being Area of Learning and "
                "Experience (AoLE) describes learning progressions across five Progression Steps (PS1–PS5), covering "
                "ages 3–16. Content is drawn from the Descriptions of Learning per Progression Step (source: "
                "hwb.gov.wales). PS1 maps to Band A; PS2 to Bands B–C; PS3 to Bands C–D; PS4 to Bands D–E; PS5 to "
                "Bands E–F — all at medium confidence with two-band ambiguity for PS2–PS5. Notable for coverage of "
                "physical health and emotional wellbeing, with less systematic treatment of consent and "
                "media/digital literacy."
            ),
            "source_jurisdiction": "Wales (UK)",
            "year_published": 2022,
            "band_mapping": {
                "PS1": "Band A",
                "PS2": "Bands B–C (ambiguous)",
                "PS3": "Bands C–D (ambiguous)",
                "PS4": "Bands D–E (ambiguous)",
                "PS5": "Bands E–F (ambiguous)",
            },
            "source_file_path": "docs/reference-corpus/welsh-cfw-health-wellbeing/band-tagged-cfw-v2.json",
            "confidence": "medium",
            "license_note": "Crown Copyright — Welsh Government. © Crown copyright 2022.",
        },
        {
            "framework_id": "CASEL",
            "framework_name": "CASEL SEL Skills Continuum (January 2023)",
            "framework_description": (
                "The Collaborative for Academic, Social, and Emotional Learning (CASEL) SEL Skills Continuum "
                "(January 2023 edition) describes social-emotional learning competencies across five domains "
                "(Self-Awareness, Self-Management, Social Awareness, Relationship Skills, Responsible "
                "Decision-Making) from Pre-K through Grade 12. Grade bands map cleanly to REAL bands A–F with "
                "high confidence, making CASEL the best-aligned external framework overall. It is the most "
                "widely-used SEL framework in North American schools and has been adopted internationally."
            ),
            "source_jurisdiction": "United States (international use)",
            "year_published": 2023,
            "band_mapping": {
                "PK / K-1": "Band A",
                "G2-3": "Band B",
                "G4-5": "Band C",
                "G6-8": "Band D",
                "G9-10": "Band E",
                "G11-12": "Band F",
            },
            "source_file_path": "docs/reference-corpus/casel-sel-continuum/band-tagged-casel-v2.json",
            "confidence": "high",
            "license_note": "© CASEL 2023. Educational use permitted; not for commercial redistribution.",
        },
        {
            "framework_id": "Circle Solutions",
            "framework_name": "Circle Solutions SEL Framework (Cowie & Myers, 2016)",
            "framework_description": (
                "The Circle Solutions Social and Emotional Learning Framework (Cowie & Myers, 2016) is an "
                "evidence-based SEL framework originating in Australia, used internationally. It is organised by "
                "Year levels (Y2, Y6, Y9, Y12) and covers twelve dimensions of social-emotional development through "
                "circle-based classroom practices. Y2 maps to Bands A–B (ambiguous, medium confidence); Y6 to "
                "Band C; Y9 to Bands D–E (ambiguous, medium confidence); Y12 to Band F. It has particularly "
                "strong coverage of emotional literacy, relational skills, and social justice themes."
            ),
            "source_jurisdiction": "Australia (international use)",
            "year_published": 2016,
            "band_mapping": {
                "Year 2": "Bands A–B (ambiguous)",
                "Year 6": "Band C",
                "Year 9": "Bands D–E (ambiguous)",
                "Year 12": "Band F",
            },
            "source_file_path": "docs/reference-corpus/circle-solutions-sel/band-tagged-circle-solutions-v2.json",
            "confidence": "medium",
            "license_note": "© Cowie & Myers 2016. Academic publication; educational use permitted.",
        },
    ]

    return {
        "meta": {
            "schema_version": "1.0",
            "generated_date": str(date.today()),
            "framework_count": len(frameworks),
        },
        "frameworks": frameworks,
    }


# ─────────────────────────────────────────
# Validation
# ─────────────────────────────────────────

def validate(framework_data, criteria_data, crosswalk_data):
    errors = []
    warnings = []

    # Collect sets from framework.json
    fw_lt_ids = set()
    fw_criterion_refs = set()
    for comp in framework_data["competencies"]:
        for lt in comp["lts"]:
            fw_lt_ids.add(lt["lt_id"])
            for band_data in lt["bands"].values():
                for cid in band_data.get("criterion_ids", []):
                    fw_criterion_refs.add(cid)

    # Collect sets from criteria.json
    crit_ids = set(c["criterion_id"] for c in criteria_data["criteria"])
    crit_lt_ids = set(c["lt_id"] for c in criteria_data["criteria"] if c["lt_id"])

    # 1. Every lt_id referenced in criteria exists in framework
    orphan_lts = crit_lt_ids - fw_lt_ids
    if orphan_lts:
        errors.append(f"Criteria reference LT IDs not in framework: {sorted(orphan_lts)}")

    # 2. Every criterion_id referenced in framework bands exists in criteria
    missing_crits = fw_criterion_refs - crit_ids
    if missing_crits:
        errors.append(
            f"{len(missing_crits)} criterion IDs referenced in framework.json not found in criteria.json"
        )

    # 3. Criterion count
    expected = 269
    actual = len(criteria_data["criteria"])
    if actual != expected:
        errors.append(f"Criterion count mismatch: expected {expected}, got {actual}")

    # 4. LT count in framework
    lt_count = sum(len(c["lts"]) for c in framework_data["competencies"])
    if lt_count != 21:
        errors.append(f"LT count mismatch: expected 21, got {lt_count}")

    # 5. Crosswalk pair count
    pair_count = len(crosswalk_data["pairs"])
    if pair_count != 84:
        errors.append(f"Crosswalk pair count: expected 84, got {pair_count}")

    # 6. Theme count
    theme_count = len(crosswalk_data["themes"])
    if theme_count != 23:
        errors.append(f"Theme count: expected 23, got {theme_count}")

    # 7. Every lt_id in crosswalk pairs exists in framework
    cw_lt_ids = set(p["lt_id"] for p in crosswalk_data["pairs"])
    missing_cw_lts = cw_lt_ids - fw_lt_ids
    if missing_cw_lts:
        errors.append(f"Crosswalk pairs reference LT IDs not in framework: {sorted(missing_cw_lts)}")

    # 8. alignment_form values are valid
    valid_forms = {"aligned-with-reciprocal-treatment", "partial-alignment", "reversed", "absent"}
    invalid_forms = [
        (p["lt_id"], p["external_framework"], p["alignment_form"])
        for p in crosswalk_data["pairs"]
        if p["alignment_form"] not in valid_forms
    ]
    if invalid_forms:
        errors.append(f"Invalid alignment_form values in {len(invalid_forms)} pairs: {invalid_forms[:3]}...")

    return errors, warnings


# ─────────────────────────────────────────
# README
# ─────────────────────────────────────────

README_CONTENT = """\
# REAL Wellbeing Framework — Visualisation-Ready Data

**Generated**: {generated_date}
**Schema version**: 1.0
**Source of truth**: `unified-wellbeing-data-v6.json` and `criterion-bank-v5_1.json`

These four JSON files are **derivative read-only outputs** for downstream consumers (visualisation, website build, future tools). They are not edited directly — regenerate by running `scripts/build_visualisation_data.py`.

---

## Files

### `framework.json`

Hierarchical structure: 8 competencies → 21 learning targets → bands (A–F) → KUD content + criterion IDs.

**Top-level fields**: `meta`, `competencies`

**Competency object**:
| Field | Type | Description |
|---|---|---|
| `competency_id` | string | e.g. `"C1"` |
| `competency_name` | string | e.g. `"Emotional Intelligence"` |
| `competency_description` | string | One-paragraph prose description |
| `lts` | array | Learning target objects |

**Learning target object**:
| Field | Type | Description |
|---|---|---|
| `lt_id` | string | e.g. `"lt_1_1"` |
| `lt_name` | string | e.g. `"Self-Awareness & Regulation"` |
| `competency_id` | string | Back-reference to parent competency |
| `knowledge_type` | string | `"T1"` or `"T2"` or `"T3"` |
| `lt_description` | string | Summary from unified data |
| `compound` | boolean | Whether LT is a compound construct |
| `band_range` | object | `{start, end}` — first and last band covered |
| `bands` | object | Keys A–F (only bands the LT covers) |

**Band object** (within `bands`):
| Field | Type | Description |
|---|---|---|
| `band_letter` | string | `"A"` through `"F"` |
| `band_label` | string | Canonical label from `band-conventions.json` |
| `know_items` | array of strings | Know layer items (KUD Know) |
| `understand_items` | array of strings | Understand layer items (KUD Understand) |
| `do_items` | array of strings | Do layer items (KUD Do) |
| `criterion_ids` | array of strings | Criterion IDs at this band for this LT |

---

### `criteria.json`

Flat array of all 269 criteria with full descriptor content.

**Top-level fields**: `meta`, `criteria`

**Criterion object** (T1 / T2):
| Field | Type | Description |
|---|---|---|
| `criterion_id` | string | e.g. `"real-wellbeing-2026-04_crit_0001"` |
| `lt_id` | string | Back-reference to parent LT |
| `competency_id` | string | Back-reference to parent competency |
| `band_letter` | string | `"A"` through `"F"` |
| `band_label` | string | Canonical band label |
| `band_position` | string | Same as `band_letter` (synonym) |
| `knowledge_type` | string | `"T1"` or `"T2"` |
| `criterion_statement` | string | Full criterion statement |
| `competency_level_descriptors` | object | Keys: `no_evidence`, `emerging`, `developing`, `competent`, `extending` |
| `prerequisite_criterion_ids` | array of strings | IDs of prerequisite criteria |

**Criterion object** (T3):
| Field | Type | Description |
|---|---|---|
| `criterion_id` | string | |
| `lt_id` | string | |
| `competency_id` | string | |
| `band_letter` | string | |
| `band_label` | string | |
| `band_position` | string | |
| `knowledge_type` | string | `"T3"` |
| `criterion_statement` | string | |
| `observation_indicators` | array of strings | Observable behaviours |
| `confusable_behaviours` | array of strings | Behaviours that resemble the criterion but are not it |
| `absence_indicators` | array of strings | What absence of the disposition looks like |
| `conversation_prompts` | array of strings | Prompts for calibration conversations |
| `prerequisite_criterion_ids` | array of strings | |

---

### `crosswalk.json`

84 LT × external-framework alignment pairs + 23 theme-level coverage objects.

**Top-level fields**: `meta`, `pairs`, `themes`

**Pair object**:
| Field | Type | Description |
|---|---|---|
| `lt_id` | string | REAL LT ID |
| `lt_name` | string | Display name |
| `competency_id` | string | Parent competency |
| `external_framework` | string | `"RSHE"`, `"Welsh CfW"`, `"CASEL"`, or `"Circle Solutions"` |
| `alignment_form` | string | One of four forms (see below) |
| `rationale` | string or null | Prose note from the v4 matrix |
| `bands_covered_real` | array of strings | Bands REAL covers for this LT |
| `bands_covered_external` | null | Not parseable from matrix prose — null per Phase 2a gap rule |

**Alignment forms**:
- `aligned-with-reciprocal-treatment` — both frameworks cover this territory similarly
- `partial-alignment` — both cover the territory but differ in grain, depth, or emphasis
- `reversed` — one framework approaches the territory from a divergent direction (no instances in v4)
- `absent` — the external framework does not address this LT's territory

**Theme object**:
| Field | Type | Description |
|---|---|---|
| `theme_id` | string | `"T01"` through `"T23"` |
| `theme_name` | string | Full theme label |
| `coverage_by_framework_by_band` | object | Keys: framework names → object of band → boolean (covered) |
| `gap_count_by_band` | object | Band letter → integer gap count (number of frameworks with no coverage) |

---

### `frameworks-meta.json`

One object per framework — REAL plus the four external frameworks.

**Framework object**:
| Field | Type | Description |
|---|---|---|
| `framework_id` | string | Short identifier |
| `framework_name` | string | Full name |
| `framework_description` | string | One-paragraph description |
| `source_jurisdiction` | string | Country/region |
| `year_published` | integer | Publication year |
| `band_mapping` | object | Native levels mapped to REAL bands A–F |
| `source_file_path` | string | Relative path to source artefact in this repo |
| `confidence` | string | `"high"` or `"medium"` |
| `license_note` | string | License / copyright note |

---

## Contract

These files are the **contract between the framework artefacts and downstream consumers**. Any change to the source-of-truth artefacts (`unified-wellbeing-data-v6.json`, `criterion-bank-v5_1.json`, `band-conventions.json`, the v4 crosswalk matrix) that affects structure or content should trigger a regeneration of all four files and a re-run of the internal validation step.

**Do not edit these files directly.** Fix the source artefact and regenerate.

## Regeneration

```bash
cd ~/Github/curriculum-harness
python3 scripts/preflight.py           # must be 12/12 PASS first
python3 scripts/build_visualisation_data.py
```
"""


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

def main():
    print("=== Phase 2a: Build visualisation-ready JSON ===")
    print()

    # Load sources
    print("Loading source artefacts...")
    with open(UNIFIED_DATA) as f:
        unified = json.load(f)
    with open(CRITERION_BANK) as f:
        bank = json.load(f)
    with open(BAND_CONVENTIONS) as f:
        bands_meta = json.load(f)
    with open(CROSSWALK_MATRIX) as f:
        matrix_text = f.read()
    print(f"  unified data: {len(unified['learning_targets'])} LTs")
    print(f"  criterion bank: {bank['total_criteria']} criteria")
    print(f"  crosswalk matrix: {len(matrix_text):,} chars")
    print()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build files
    print("Building framework.json...")
    framework_data = build_framework(unified, bands_meta)
    fw_path = OUT_DIR / "framework.json"
    with open(fw_path, "w") as f:
        json.dump(framework_data, f, indent=2, ensure_ascii=False)
    print(f"  {fw_path.name}: {os.path.getsize(fw_path):,} bytes")

    print("Building criteria.json...")
    criteria_data = build_criteria(bank, unified)
    cr_path = OUT_DIR / "criteria.json"
    with open(cr_path, "w") as f:
        json.dump(criteria_data, f, indent=2, ensure_ascii=False)
    print(f"  {cr_path.name}: {os.path.getsize(cr_path):,} bytes")

    print("Building crosswalk.json...")
    crosswalk_data = build_crosswalk(matrix_text, unified)
    cw_path = OUT_DIR / "crosswalk.json"
    with open(cw_path, "w") as f:
        json.dump(crosswalk_data, f, indent=2, ensure_ascii=False)
    print(f"  {cw_path.name}: {os.path.getsize(cw_path):,} bytes")
    print(f"    pairs: {crosswalk_data['meta']['pair_count']}, themes: {crosswalk_data['meta']['theme_count']}")

    print("Building frameworks-meta.json...")
    meta_data = build_frameworks_meta()
    fm_path = OUT_DIR / "frameworks-meta.json"
    with open(fm_path, "w") as f:
        json.dump(meta_data, f, indent=2, ensure_ascii=False)
    print(f"  {fm_path.name}: {os.path.getsize(fm_path):,} bytes")

    print("Writing README.md...")
    readme_path = OUT_DIR / "README.md"
    with open(readme_path, "w") as f:
        f.write(README_CONTENT.replace("{generated_date}", str(date.today())))
    readme_lines = len(README_CONTENT.splitlines())
    print(f"  README.md: {readme_lines} lines")

    # Validate
    print()
    print("Validating cross-references...")
    errors, warnings = validate(framework_data, criteria_data, crosswalk_data)
    if errors:
        print("  ERRORS:")
        for e in errors:
            print(f"    ✗ {e}")
        sys.exit(1)
    else:
        print("  All cross-references valid. ✓")

    if warnings:
        print("  Warnings:")
        for w in warnings:
            print(f"    ⚠ {w}")

    # Summary
    print()
    print("=== Summary ===")
    print(f"  framework.json  : {os.path.getsize(fw_path):>10,} bytes — {framework_data['meta']['competency_count']} competencies, {framework_data['meta']['lt_count']} LTs")
    print(f"  criteria.json   : {os.path.getsize(cr_path):>10,} bytes — {criteria_data['meta']['total_criteria']} criteria")
    print(f"  crosswalk.json  : {os.path.getsize(cw_path):>10,} bytes — {crosswalk_data['meta']['pair_count']} pairs, {crosswalk_data['meta']['theme_count']} themes")
    print(f"  frameworks-meta : {os.path.getsize(fm_path):>10,} bytes — {meta_data['meta']['framework_count']} frameworks")
    print(f"  README.md       : {readme_lines} lines")
    print()
    print("Done.")


if __name__ == "__main__":
    main()
