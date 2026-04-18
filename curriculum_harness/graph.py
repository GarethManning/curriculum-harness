"""LangGraph StateGraph: four phases + artifact writer, Sqlite checkpointing."""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, StateGraph

from curriculum_harness.phases.phase1_ingestion import phase1_ingestion
from curriculum_harness.phases.phase2_architecture import phase2_architecture
from curriculum_harness.phases.phase3_kud import phase3_kud
from curriculum_harness.phases.phase4_lt_generation import phase4_lt_generation
from curriculum_harness.phases.phase5_formatting import phase5_formatting
from curriculum_harness.output_naming import next_available_artifact_path
from curriculum_harness.state import DecomposerState
from curriculum_harness.types import (
    ArchitectureDiagnosis,
    HE_DISPOSITION_INFERRED,
    resolve_lt_statement_format,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def build_initial_state(config_path: str, cfg: dict[str, Any]) -> DecomposerState:
    out_raw = cfg.get("outputPath", "outputs/")
    out_p = Path(out_raw)
    outp = out_p if out_p.is_absolute() else (REPO_ROOT / out_p)

    cp_raw = cfg.get("checkpointDb", "checkpoints/run.db")
    cp_p = Path(cp_raw)
    cp_path = cp_p if cp_p.is_absolute() else (REPO_ROOT / cp_p)

    mcp = cfg.get("mcpServer") or {}
    src = cfg.get("source") or {}

    return {
        "config_path": str(Path(config_path).resolve()),
        "config": cfg,
        "source_url": str(src.get("url", "")),
        "subject": str(src.get("subject", "")),
        "grade": str(src.get("grade", "")),
        "jurisdiction": str(src.get("jurisdiction", "")),
        "year": str(src.get("year", "")),
        "raw_curriculum": "",
        "curriculum_metadata": {},
        "architecture_diagnosis": {},
        "kud": {},
        "learning_targets": [],
        "human_review_queue": [],
        "run_id": str(cfg.get("runId", "")),
        "errors": [],
        "current_phase": "init",
        "output_path_resolved": str(outp),
        "checkpoint_db_resolved": str(cp_path),
        "mcp_server_url": str(mcp.get("url", "")),
        "mcp_server_name": str(mcp.get("name", "claude-education-skills")),
        "lt_constraints": dict(cfg.get("ltConstraints") or {}),
        "output_structure": cfg.get("outputStructure"),
        "structured_lts": [],
        "phase5_summary": {},
        "recall_filtered_count": 0,
        "curriculum_profile": {},
        "curriculum_classification_notes": "",
        "source_bullets": [],
    }


def _resolve_phase5_artifact_paths(
    out_dir: Path, run_id: str, phase5_summary: dict[str, Any]
) -> tuple[Path | None, Path | None]:
    rid = (run_id or "run").strip() or "run"
    jp = phase5_summary.get("json_path")
    cp = phase5_summary.get("csv_path")
    json_p = Path(jp) if jp else None
    csv_p = Path(cp) if cp else None
    if json_p and json_p.is_file() and csv_p and csv_p.is_file():
        return json_p, csv_p
    jpaths = sorted(
        out_dir.glob(f"{rid}_structured_lts_v*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    cpaths = sorted(
        out_dir.glob(f"{rid}_structured_lts_v*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return (jpaths[0] if jpaths else None), (cpaths[0] if cpaths else None)


def _write_kud_artefact(
    out_dir: Path,
    run_id: str,
    kud: dict[str, Any],
    output_mode: str,
) -> tuple[Path, str]:
    """Write the KUD / assessed-demonstrations-map artefact.

    Session 3c — output-shape discipline. In curriculum mode the
    artefact is written as ``<runId>_kud_v1.json`` with the legacy
    bare-KUD top-level shape. In exam-spec mode the artefact is
    written as ``<runId>_assessed_demonstrations_map_v1.json`` with an
    explanatory wrapper that names the mode and nullifies the
    pedagogical columns refused by Phase 3 (understandings,
    dispositions, pedagogical_criteria).

    Returns ``(written_path, artefact_kind)`` where ``artefact_kind``
    is ``"kud"`` or ``"assessed_demonstrations_map"``.
    """
    if output_mode == "exam_specification":
        path = next_available_artifact_path(
            out_dir, run_id, "assessed_demonstrations_map", "json"
        )
        payload = {
            "output_mode": "exam_specification",
            "schema_version": "1.0",
            "assessed_demonstrations_map": {
                "assessed_topics": kud.get("know") or [],
                "tested_demonstrations": kud.get("do_skills") or [],
                "understandings": None,
                "dispositions": None,
                "pedagogical_criteria": None,
            },
        }
        kind = "assessed_demonstrations_map"
    else:
        path = next_available_artifact_path(out_dir, run_id, "kud", "json")
        payload = kud
        kind = "kud"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path, kind


def output_node(state: DecomposerState) -> dict[str, Any]:
    orp = str(state.get("output_path_resolved") or "").strip()
    out_dir = Path(orp).resolve() if orp else (REPO_ROOT / "outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = str(state.get("run_id") or "").strip() or "run"

    arch_path = next_available_artifact_path(out_dir, run_id, "architecture", "json")
    profile_path = next_available_artifact_path(out_dir, run_id, "curriculum_profile", "json")
    lt_path = next_available_artifact_path(out_dir, run_id, "learning_targets", "json")
    hr_path = next_available_artifact_path(out_dir, run_id, "human_review_queue", "json")
    report_path = next_available_artifact_path(out_dir, run_id, "run_report", "md")
    bullets_path = next_available_artifact_path(out_dir, run_id, "source_bullets", "json")

    architecture = state.get("architecture_diagnosis") or {}
    kud = state.get("kud") or {}
    lts = state.get("learning_targets") or []
    reviews = state.get("human_review_queue") or []
    output_mode = str(state.get("output_mode") or "curriculum")
    regeneration_events = list(state.get("regeneration_events") or [])
    human_review_required = list(state.get("human_review_required") or [])
    exam_spec_refusals = dict(state.get("phase3_exam_spec_refusals") or {})
    source_language = str(state.get("source_language") or "en")
    source_language_signal = dict(state.get("source_language_signal") or {})

    kud_path, kud_kind = _write_kud_artefact(out_dir, run_id, kud, output_mode)
    phase5_summary = state.get("phase5_summary") or {}
    phase5_json, phase5_csv = _resolve_phase5_artifact_paths(out_dir, run_id, phase5_summary)
    phase5_group_counts: dict[str, int] = {}
    phase5_level_columns = list(phase5_summary.get("level_columns") or [])
    phase5_uncertain_count = 0
    phase5_flags: set[str] = set()
    if phase5_json and phase5_json.is_file():
        try:
            with open(phase5_json, encoding="utf-8") as f:
                phase5_data = json.load(f)
            for row in phase5_data.get("structured_lts", []):
                comp = str(row.get("competency", ""))
                if comp:
                    phase5_group_counts[comp] = phase5_group_counts.get(comp, 0) + 1
                flags = row.get("flags") or []
                if "COMPETENCY_MAPPING_UNCERTAIN" in flags:
                    phase5_uncertain_count += 1
                for fl in flags:
                    if isinstance(fl, str) and fl.strip():
                        phase5_flags.add(fl.strip())
        except Exception:
            pass
    elif phase5_summary.get("group_counts"):
        phase5_group_counts = dict(phase5_summary["group_counts"])
        phase5_uncertain_count = int(phase5_summary.get("mapping_uncertain_count") or 0)
    if phase5_csv and phase5_csv.is_file():
        try:
            with open(phase5_csv, encoding="utf-8") as f:
                header = f.readline().strip().split(",")
            if len(header) >= 7:
                phase5_level_columns = header[4:-2]
        except Exception:
            pass

    with open(arch_path, "w", encoding="utf-8") as f:
        json.dump(architecture, f, indent=2)

    source_bullets = state.get("source_bullets") or []
    with open(bullets_path, "w", encoding="utf-8") as f:
        json.dump({"source_bullets": source_bullets}, f, indent=2)

    curriculum_profile = state.get("curriculum_profile") or {}
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(curriculum_profile, f, indent=2)

    # kud_path already written by `_write_kud_artefact` — the file name
    # (`kud_v1.json` vs `assessed_demonstrations_map_v1.json`) reflects
    # output_mode. No second write here.

    with open(lt_path, "w", encoding="utf-8") as f:
        json.dump({"learning_targets": lts}, f, indent=2)

    with open(hr_path, "w", encoding="utf-8") as f:
        json.dump({"items": reviews}, f, indent=2)

    # Regeneration events + human-review-required are written alongside
    # the LT artefact so the validate_regenerate_loop gate can read them.
    regen_path = next_available_artifact_path(
        out_dir, run_id, "regeneration_events", "json"
    )
    with open(regen_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "regeneration_events": regeneration_events,
                "human_review_required": human_review_required,
                "source_language": source_language,
                "source_language_signal": source_language_signal,
                "output_mode": output_mode,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    type_counts: dict[int, int] = {1: 0, 2: 0, 3: 0}
    word_counts: list[int] = []
    flag_items = 0
    total_flags = 0
    for lt in lts:
        t = int(lt.get("type") or 1)
        type_counts[t] = type_counts.get(t, 0) + 1
        wc = int(lt.get("word_count") or 0)
        if wc:
            word_counts.append(wc)
        flags = lt.get("flags") or []
        if flags:
            flag_items += 1
            total_flags += len(flags)

    wc_stats = "n/a"
    if word_counts:
        wc_stats = (
            f"min={min(word_counts)}, max={max(word_counts)}, "
            f"mean={statistics.mean(word_counts):.1f}"
        )

    recall_filtered = int(state.get("recall_filtered_count") or 0)
    phase3_faithfulness_flagged = int(
        state.get("phase3_faithfulness_flagged_count") or 0
    )
    phase4_faithfulness_flagged = int(
        state.get("phase4_faithfulness_flagged_count") or 0
    )

    profile_notes = str(state.get("curriculum_classification_notes") or "").strip()
    oc = curriculum_profile.get("output_conventions") or {}
    lt_fmt = oc.get("lt_statement_format", "")
    lt_fmt_resolved = resolve_lt_statement_format(curriculum_profile)
    adj_r = oc.get("recommended_adjacent_radius", "")

    lt_flags: set[str] = set()
    he_disposition_lts: list[dict[str, Any]] = []
    for lt in lts:
        for fl in lt.get("flags") or []:
            if isinstance(fl, str) and fl.strip():
                lt_flags.add(fl.strip())
        if HE_DISPOSITION_INFERRED in (lt.get("flags") or []):
            he_disposition_lts.append(lt)

    lines = [
        "# Curriculum Harness run report",
        "",
        f"**Run ID:** {run_id}",
        f"**Output directory:** `{out_dir}`",
        "",
        "## Output-shape discipline (Session 3c)",
        "",
        f"- **Output mode:** `{output_mode}`",
        f"- KUD / map artefact kind: `{kud_kind}`",
        f"- KUD / map artefact path: `{kud_path}`",
    ]
    if output_mode == "exam_specification":
        u_dropped = exam_spec_refusals.get("understand_dropped", 0)
        d_dropped = exam_spec_refusals.get("dispositions_dropped", 0)
        lines.extend(
            [
                "- Exam-spec discipline active: Understands and Dispositions "
                "refused per v4.1.",
                f"- Understand items dropped by Phase 3: {u_dropped}",
                f"- Disposition items dropped by Phase 3: {d_dropped}",
                "- Pedagogical criterion bank: NOT produced (not yet emitted "
                "by any phase; exam-spec refusal is pre-emptive).",
                "- Demonstration criterion bank: not yet produced (no "
                "criterion phase in harness yet — tracked in VALIDITY.md §4).",
            ]
        )
    else:
        lines.append(
            "- Curriculum mode: full KUD emitted (know, understand, "
            "do_skills, do_dispositions)."
        )
    lines.extend(
        [
            "",
            "## Source language (Session 3c)",
            "",
            f"- Detected language: `{source_language}`",
            f"- Signal: {source_language_signal}",
            (
                "- Phase 4 regeneration loop skips `SOURCE_FAITHFULNESS_FAIL` "
                "retries for non-en sources (English-only matcher)."
                if source_language == "non-en"
                else "- Phase 4 regeneration loop retries all FAIL_SET flags normally."
            ),
            "",
            "## Source bullets",
            "",
            f"- Count: {len(source_bullets)}",
            f"- Artefact: `{bullets_path}`",
            "",
            "## Curriculum profile",
            "",
            f"- document_family: {curriculum_profile.get('document_family', '')}",
            f"- level_model: {curriculum_profile.get('level_model', '')}",
            f"- scoping_strategy: {curriculum_profile.get('scoping_strategy', '')}",
            f"- lt_statement_format (profile output_conventions): {lt_fmt}",
            f"- lt_statement_format (resolved for pipeline): {lt_fmt_resolved}",
            f"- recommended_adjacent_radius (product default ±1): {adj_r}",
            f"- confidence: {curriculum_profile.get('confidence', '')}",
            f"- Profile JSON: `{profile_path}`",
        ]
    )
    if profile_notes:
        lines.extend(["", f"_Classification notes:_ {profile_notes}", ""])
    else:
        lines.append("")

    arch_diag = ArchitectureDiagnosis.from_dict(architecture)
    content_themes = arch_diag.content_theme_strands()
    lines.extend(
        [
            "",
            "## Curriculum coverage (content themes)",
            "",
            "_These strands describe topic or period coverage. They are **not** used for learning-target "
            "assignment in Phase 5._",
            "",
        ]
    )
    if content_themes:
        for s in content_themes:
            lines.append(f"- **{s.label}** (`{s.id}`): {s.values_basis}")
    else:
        lines.append("- _(none listed)_")
    lines.append("")

    lines.extend(
        [
        "## Learning targets",
        "",
        f"- Count by type: 1={type_counts.get(1, 0)}, 2={type_counts.get(2, 0)}, 3={type_counts.get(3, 0)}",
        f"- Word count stats: {wc_stats}",
        f"- Items with any validation flag: {flag_items}",
        f"- Total flags across items: {total_flags}",
        f"- HE disposition inferred (Phase 4 supplement): {len(he_disposition_lts)}",
        "",
    ]
    )
    if he_disposition_lts:
        lines.append("_HE supplement statements (truncated):_")
        for lt in he_disposition_lts[:12]:
            st = str(lt.get("statement") or "").strip()
            if len(st) > 220:
                st = st[:217] + "..."
            lines.append(f"- {st}")
        remainder = len(he_disposition_lts) - 12
        if remainder > 0:
            lines.append(f"- _…and {remainder} more_")
        lines.append("")
    phase3_branch = str(state.get("phase3_branch") or "")
    phase3_input_bullets = int(state.get("phase3_input_bullet_count") or 0)
    phase3_output_items = int(state.get("phase3_output_kud_item_count") or 0)
    phase3_merge_events = list(state.get("phase3_merge_events") or [])
    lines.extend(
        [
        "## Phase 3 profile-conditional branch (Session 3b)",
        "",
        f"- Branch selected: **{phase3_branch or 'unknown'}**",
        f"- Input source bullets: {phase3_input_bullets}",
        f"- Output KUD items: {phase3_output_items}",
        f"- Merge events (per_bullet only): {len(phase3_merge_events)}",
        "",
        ]
    )
    if phase3_branch == "default":
        lines.append(
            "_Profile did not match per_bullet or strand_aggregated cleanly; "
            "defaulted to strand_aggregated._"
        )
        lines.append("")
    if phase3_merge_events:
        lines.append("_Bullet merges recorded in Phase 3 per_bullet branch:_")
        for ev in phase3_merge_events[:20]:
            ids = ", ".join(ev.get("merged_bullet_ids") or [])
            content = (ev.get("kud_content") or "")[:160]
            lines.append(f"- `{ids}` → {content}")
        remainder = len(phase3_merge_events) - 20
        if remainder > 0:
            lines.append(f"- _…and {remainder} more_")
        lines.append("")
    lines.extend(
        [
        "## Phase 3 recall filter",
        "",
        f"- recall_filtered_count: {recall_filtered}",
        "",
        "## Source faithfulness flagging (Session 3a)",
        "",
        f"- Phase 3 KUD items flagged SOURCE_FAITHFULNESS_FAIL: {phase3_faithfulness_flagged}",
        f"- Phase 4 LTs flagged SOURCE_FAITHFULNESS_FAIL: {phase4_faithfulness_flagged}",
        "",
        "## Regeneration loop (Session 3c)",
        "",
        f"- Total LTs that entered regeneration: {len(regeneration_events)}",
        f"- LTs that exhausted the retry budget: {len(human_review_required)}",
        f"- Regeneration artefact: `{regen_path}`",
        ]
    )
    if regeneration_events:
        outcomes: dict[str, int] = {}
        for ev in regeneration_events:
            outcome = str(ev.get("outcome") or "unknown")
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        for k in sorted(outcomes):
            lines.append(f"  - outcome `{k}`: {outcomes[k]}")
    if human_review_required:
        lines.append("")
        lines.append("_Human-review entries (budget exhausted):_")
        for entry in human_review_required[:12]:
            sbid = ", ".join(entry.get("source_bullet_ids") or []) or "(no sb_ids)"
            flags = ", ".join(entry.get("final_fail_flags") or [])
            lines.append(
                f"- `{sbid}` → flags: [{flags}]; outcome: {entry.get('outcome')}"
            )
        remainder = len(human_review_required) - 12
        if remainder > 0:
            lines.append(f"- _…and {remainder} more_")
    lines.extend(
        [
        "",
        "## Flags (unique)",
        "",
        f"- Learning target flags: {sorted(lt_flags)}",
        f"- Structured LT (Phase 5) flags: {sorted(phase5_flags)}",
        "",
        "## Comparison note",
        "",
        "_Reserved for manual comparison against the validation experiment._",
        "",
        "## Phase 5 structured output",
        "",
        f"- Competency groups: {len(phase5_group_counts)}",
        f"- Group LT counts: {phase5_group_counts}",
        f"- Level columns generated: {phase5_level_columns}",
        f"- COMPETENCY_MAPPING_UNCERTAIN count: {phase5_uncertain_count}",
        f"- Structured JSON path: `{phase5_json}`",
        f"- Structured CSV path: `{phase5_csv}`",
        "",
        "## Phase errors",
        "",
        ],
    )
    for e in state.get("errors") or []:
        lines.append(f"- {e}")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return {"current_phase": "output:complete"}


async def compile_graph(checkpoint_db: Path) -> Any:
    checkpoint_db.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(str(checkpoint_db))
    checkpointer = AsyncSqliteSaver(conn)

    graph = StateGraph(DecomposerState)
    graph.add_node("phase1_ingestion", phase1_ingestion)
    graph.add_node("phase2_architecture", phase2_architecture)
    graph.add_node("phase3_kud", phase3_kud)
    graph.add_node("phase4_lt_generation", phase4_lt_generation)
    graph.add_node("phase5_formatting", phase5_formatting)
    graph.add_node("output_node", output_node)

    graph.set_entry_point("phase1_ingestion")
    graph.add_edge("phase1_ingestion", "phase2_architecture")
    graph.add_edge("phase2_architecture", "phase3_kud")
    graph.add_edge("phase3_kud", "phase4_lt_generation")
    graph.add_edge("phase4_lt_generation", "phase5_formatting")
    graph.add_edge("phase5_formatting", "output_node")
    graph.add_edge("output_node", END)

    return graph.compile(checkpointer=checkpointer)
