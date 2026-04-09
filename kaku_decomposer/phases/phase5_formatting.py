"""Phase 5 — structure LTs into competency-grouped, level-aware output."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

from kaku_decomposer._anthropic import beta_messages_create, get_async_client, response_text_content
from kaku_decomposer.output_naming import next_available_structured_lts_paths
from kaku_decomposer.state import DecomposerState
from kaku_decomposer.types import SONNET_MODEL, StructuredLT, extract_json_object

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

DEMAND_LEVELS = ["concrete", "transitional", "abstract"]


def _effective_levels(output_structure: dict[str, Any]) -> list[dict[str, str]]:
    levels = list(output_structure.get("levels") or [])
    if not output_structure.get("generate_adjacent"):
        return levels
    adjacent_count = int(output_structure.get("adjacent_count") or 0)
    if adjacent_count <= 0:
        return levels

    expanded: list[dict[str, str]] = []
    for level in levels:
        base_demand = str(level.get("cognitive_demand", "transitional")).lower()
        try:
            base_i = DEMAND_LEVELS.index(base_demand)
        except ValueError:
            base_i = 1
        for offset in range(-adjacent_count, adjacent_count + 1):
            i = max(0, min(len(DEMAND_LEVELS) - 1, base_i + offset))
            if offset == 0:
                expanded.append(level)
            else:
                expanded.append(
                    {
                        "id": f"{level.get('id')}_adj_{offset:+d}",
                        "label": f"{level.get('label')} (adj {offset:+d})",
                        "age_range": str(level.get("age_range", "")),
                        "cognitive_demand": DEMAND_LEVELS[i],
                    }
                )
    return expanded


def _knowledge_bucket(lt: dict[str, Any]) -> str:
    k = str(lt.get("knowledge_type", "")).lower()
    t = int(lt.get("type") or 0)
    if "hierarchical" in k or t == 1:
        return "hierarchical"
    if "horizontal" in k or t == 2:
        return "horizontal"
    return "dispositional"


def _competency_name_variants(competency_name: str) -> list[str]:
    raw = competency_name.strip()
    if not raw:
        return []
    head = raw.split("→")[0].split("–")[0].strip()
    out = [raw]
    if head and head.lower() != raw.lower():
        out.append(head)
    return out


def _competency_relevance_score(lt: dict[str, Any], competency_name: str) -> float:
    ks = str(lt.get("kud_source", ""))
    detail = ks.split(":", 1)[1].strip().lower() if ":" in ks else ks.lower()
    blob = f"{ks} {detail} {lt.get('statement', '')}".lower()
    if not blob.strip():
        return 0.0
    best = 0.0
    for variant in _competency_name_variants(competency_name):
        name = variant.lower()
        if name and name in blob:
            return 1.0
        words = [w for w in re.split(r"[^\w]+", name) if len(w) > 2]
        if not words:
            continue
        hits = sum(1 for w in set(words) if w in blob)
        best = max(best, hits / len(set(words)))
    return best


def _map_to_competency(
    lt: dict[str, Any],
    groups: list[dict[str, str]],
) -> tuple[str, bool]:
    if not groups:
        return "", True

    kind = _knowledge_bucket(lt)
    candidates = [g for g in groups if g["kind"] == kind]
    kind_relaxed = False
    if not candidates:
        candidates = list(groups)
        kind_relaxed = True

    scored = [(g["name"], _competency_relevance_score(lt, g["name"])) for g in candidates]
    scored.sort(key=lambda x: -x[1])
    best_name, best_s = scored[0]
    second_s = scored[1][1] if len(scored) > 1 else -1.0

    # Reserve COMPETENCY_MAPPING_UNCERTAIN for kind-mismatch fallback or a high-score dead heat.
    uncertain = kind_relaxed
    if (
        not uncertain
        and len(scored) > 1
        and best_s >= 0.35
        and second_s >= 0.35
        and (best_s - second_s) < 0.05
    ):
        uncertain = True

    return best_name, uncertain


def _level_statement_fallback(statement: str, max_words: int = 20) -> str:
    s = (statement or "").strip()
    if not s:
        return ""
    if not s.startswith("I can "):
        return s
    words = s.split()
    return " ".join(words[:max_words])




def _type_label(lt: dict[str, Any]) -> str:
    t = int(lt.get("type") or 1)
    return f"T{t}" if t in (1, 2, 3) else "T1"


async def _format_competency_batch(
    competency: str,
    items: list[dict[str, Any]],
    levels: list[dict[str, str]],
    subject: str,
    grade: str,
) -> list[dict[str, Any]]:
    client = get_async_client()
    payload = {
        "competency": competency,
        "subject": subject,
        "grade": grade,
        "levels": levels,
        "learning_targets": [
            {
                "idx": i,
                "statement": x["statement"],
                "knowledge_type": x["knowledge_type"],
                "kud_source": x["kud_source"],
                "type": x["type"],
            }
            for i, x in enumerate(items)
        ],
    }
    subj = subject.strip() or "this subject"
    gr = grade.strip() or "this grade"
    comp_def_rules = (
        f"For each row, competency_definition must be ONE sentence defining this competency group "
        f"as it applies to {subj} at {gr} level. "
        "Do NOT echo, restate, or lightly paraphrase the group name or internal slug (e.g. snake_case). "
        "Write a genuine description of what students in this competency group are learning to do. "
        "Example format: 'The ability to locate, sequence, and interpret geographical and chronological "
        "information as foundations for historical analysis.' "
        "(Use different wording per row; this is style only.) "
    )
    system = (
        "You convert learning targets into a structured competency table. Return ONLY JSON object with "
        "'rows' list. Each row must have keys: idx, competency_definition, lt_name, lt_definition, "
        "level_statements. "
        f"{comp_def_rules}"
        "Constraints: lt_name 2-4 words; lt_definition must be I-can and <=15 words, generic across levels; "
        "each level_statement must be I-can and <=20 words; align each level statement to its "
        "cognitive_demand (concrete/transitional/abstract). "
        "level_statements MUST be an object whose keys are EXACTLY the strings in levels[].id from "
        "the input payload (no other keys)."
    )
    msg = await beta_messages_create(
        client,
        model=SONNET_MODEL,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": system},
                    {"type": "text", "text": json.dumps(payload, ensure_ascii=True)},
                ],
            }
        ],
        label=f"phase5_format_{competency[:24]}",
    )
    text = response_text_content(msg)
    parsed = extract_json_object(text) or {}
    rows = parsed.get("rows") if isinstance(parsed, dict) else None
    if isinstance(rows, list):
        return [r for r in rows if isinstance(r, dict)]
    return []


def _flag_duplicate_lt_names(structured_lts: list[StructuredLT]) -> None:
    from collections import Counter

    names = [str(row.get("lt_name") or "").strip() for row in structured_lts]
    counts = Counter(names)
    dup = {n for n, c in counts.items() if n and c > 1}
    if not dup:
        return
    for row in structured_lts:
        if str(row.get("lt_name") or "").strip() in dup:
            flags = list(row.get("flags") or [])
            if "DUPLICATE_LT_NAME" not in flags:
                flags.append("DUPLICATE_LT_NAME")
            row["flags"] = list(dict.fromkeys(flags))


def _write_phase5_outputs(
    out_dir: Path,
    run_id: str,
    structured_lts: list[StructuredLT],
    levels: list[dict[str, str]],
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path, csv_path = next_available_structured_lts_paths(out_dir, run_id)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"structured_lts": structured_lts}, f, indent=2, ensure_ascii=False)

    level_cols = [str(level.get("label", level.get("id", ""))) for level in levels]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Competency",
                "Competency Definition",
                "LT Name",
                "LT Definition",
                *level_cols,
                "Knowledge Type",
                "Flags",
            ]
        )
        for row in structured_lts:
            cells = [
                row["competency"],
                row["competency_definition"],
                row["lt_name"],
                row["lt_definition"],
            ]
            for lvl in levels:
                cells.append(str(row["level_statements"].get(str(lvl.get("id")), "")))
            cells.append(row["knowledge_type"])
            cells.append("|".join(row["flags"]))
            writer.writerow(cells)
    return json_path, csv_path


async def phase5_formatting(state: DecomposerState) -> dict[str, Any]:
    output_structure = state.get("output_structure") or (state.get("config") or {}).get("outputStructure")
    if not output_structure:
        return {"current_phase": "phase5:skipped", "structured_lts": []}

    lts = list(state.get("learning_targets") or [])
    arch = state.get("architecture_diagnosis") or {}
    input_level_id = str(output_structure.get("input_level_id") or "")
    run_id = str(state.get("run_id") or "run")
    subject = str(state.get("subject") or "")
    grade = str(state.get("grade") or "")
    review = list(state.get("human_review_queue") or [])
    errs = list(state.get("errors") or [])

    levels = _effective_levels(output_structure)

    groups: list[dict[str, str]] = []
    for x in arch.get("hierarchical_elements") or []:
        groups.append({"kind": "hierarchical", "name": str(x)})
    for x in arch.get("horizontal_elements") or []:
        groups.append({"kind": "horizontal", "name": str(x)})
    for x in arch.get("dispositional_elements") or []:
        groups.append({"kind": "dispositional", "name": str(x)})

    if not groups:
        return {
            "current_phase": "phase5:skipped",
            "errors": errs + ["phase5: skipped — architecture_diagnosis has no competency elements"],
            "human_review_queue": review,
            "structured_lts": [],
            "phase5_summary": {},
        }

    by_comp: dict[str, list[dict[str, Any]]] = {}
    uncertain_count = 0
    for lt in lts:
        comp, uncertain = _map_to_competency(lt, groups)
        if not comp:
            continue
        row = dict(lt)
        row["_uncertain"] = uncertain
        by_comp.setdefault(comp, []).append(row)
        if uncertain:
            uncertain_count += 1

    structured: list[StructuredLT] = []
    group_counts: dict[str, int] = {}
    for comp, comp_lts in by_comp.items():
        rows = await _format_competency_batch(comp, comp_lts, levels, subject, grade)
        rows_by_idx = {int(r.get("idx")): r for r in rows if str(r.get("idx", "")).isdigit()}

        for i, lt in enumerate(comp_lts):
            gen = rows_by_idx.get(i, {})
            flags = list(lt.get("flags") or [])
            if lt.get("_uncertain"):
                flags.append("COMPETENCY_MAPPING_UNCERTAIN")
            level_statements = {}
            for lvl in levels:
                lvl_id = str(lvl.get("id"))
                val = ""
                if isinstance(gen.get("level_statements"), dict):
                    val = str(gen["level_statements"].get(lvl_id, "")).strip()
                if (
                    not val
                    and input_level_id
                    and lvl_id == input_level_id
                ):
                    val = _level_statement_fallback(str(lt.get("statement", "")))
                level_statements[lvl_id] = val

            structured.append(
                {
                    "competency": comp,
                    "competency_definition": str(gen.get("competency_definition", "")).strip(),
                    "lt_name": str(gen.get("lt_name", "")).strip(),
                    "lt_definition": str(gen.get("lt_definition", "")).strip(),
                    "level_statements": level_statements,
                    "knowledge_type": _type_label(lt),
                    "flags": list(dict.fromkeys(flags)),
                }
            )
        group_counts[comp] = len(comp_lts)

    _flag_duplicate_lt_names(structured)
    orp = str(state.get("output_path_resolved") or "").strip()
    out_dir_p = Path(orp).resolve() if orp else (REPO_ROOT / "outputs")
    json_path, csv_path = _write_phase5_outputs(out_dir_p, run_id, structured, levels)
    review.append(
        {
            "item_type": "phase5_outputs",
            "summary": "Structured outputs generated.",
            "decision_needed": f"CSV: {csv_path} | JSON: {json_path}",
        }
    )
    return {
        "current_phase": "phase5:complete",
        "errors": errs,
        "human_review_queue": review,
        "structured_lts": structured,
        "phase5_summary": {
            "group_counts": group_counts,
            "level_columns": [str(level.get("label", level.get("id", ""))) for level in levels],
            "mapping_uncertain_count": uncertain_count,
            "json_path": str(json_path),
            "csv_path": str(csv_path),
        },
    }

