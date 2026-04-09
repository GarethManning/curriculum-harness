# curriculum-decomposer

Standalone **LangGraph** pipeline that ingests a curriculum document (URL — PDF or plain text), diagnoses its knowledge architecture, derives a **KUD** (Know / Understand / Do) map with assessment routes, and generates **learning targets** aligned to Claude Education Skills MCP tools.

## Setup

```bash
cd curriculum-decomposer
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
# set ANTHROPIC_API_KEY in .env
```

## Usage

```bash
python -m kaku_decomposer.run --config configs/ontario_grade7_history_v1_0.json --dry-run
python -m kaku_decomposer.run --config configs/ontario_grade7_history_v1_0.json
python -m kaku_decomposer.run --config configs/ontario_grade7_history_v1_0.json --resume
```

Outputs are written under the configured `outputPath` (versioned `*_v1.*` files). Checkpoints use Sqlite (`checkpointDb`).

## Curriculum profile (v1.1)

Phase 1 classifies the document into a **`curriculum_profile`** (JSON + run report section). The model infers `document_family`, `level_model`, `scoping_strategy`, and `assessment_signals`; **`output_conventions`** includes `lt_statement_format` (stored for future rendering; Phase 4 still uses I-can today) and **`recommended_adjacent_radius`** (product default **±1** when using adjacent bands).

**Overrides**

- `source.documentFamily` — if set, overrides the inferred family. Values: `exam_specification`, `national_framework`, `school_scoped_programme`, `higher_ed_syllabus`, `other`.
- `curriculumProfile` — optional object merged into the profile (e.g. `output_conventions`, `scoping_strategy`, `assessment_signals`).

**REAL School** — use `document_family: "school_scoped_programme"` (or leave inference) and set **`source.jurisdiction`** (e.g. REAL School / location).

**Adjacent levels** — prefer `outputStructure.adjacent_count: 1` for ±1 bands; you can still set `2` for wider spreads.

## Models

- **Haiku**: Phase 1 ingestion / parsing volume.
- **Sonnet** (`claude-sonnet-4-20250514`): Phases 2–4, including MCP tool calls against the configured remote MCP server.
