# REAL Wellbeing Framework — Visualisation-Ready Data

**Generated**: 2026-04-24
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
