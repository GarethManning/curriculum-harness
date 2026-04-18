"""Phase 3 — KUD mapping (Sonnet + MCP kud-knowledge-type-mapper).

## Profile-conditional branch (Session 3b — Shape C fix)

Phase 3 reads `curriculum_profile` from state and selects one of three
branches at entry:

- **per_bullet** — bare-bullet exam spec (document_family=exam_specification
  AND has_command_words=false AND has_mark_scheme=false AND
  scoping_strategy=full_document). Bullets are passed in the prompt
  one-per-line and the Sonnet instruction forbids consolidation;
  target cardinality is 1 KUD item per source bullet.
- **strand_aggregated** — the pre-Session-3b behaviour: Sonnet is
  instructed to "align with the architecture diagnosis" with no bullet
  enumeration. This is chosen for every profile that carries command-
  words, a mark scheme, or is a non-exam-spec family (national_framework,
  school_scoped_programme, higher_ed_syllabus).
- **default** — anything that matches neither shape cleanly. Runs the
  strand_aggregated path and records the defaulting in the run report.

## Adjacent-mechanism declaration — what this branch does NOT decide

1. **Criterion grain.** Per-bullet KUDs still produce Phase 4 LTs and
   Phase 5 criteria at whatever grain those phases decide. This branch
   only pins KUD cardinality at entry.
2. **Source-faithfulness matching.** Orthogonal — still computed by
   ``_attach_source_faithfulness`` against the ``source_bullets``
   artefact after the KUD is generated, regardless of branch.

## Exam-spec output-shape refusal (Session 3c, v4.1 discipline)

When the profile resolves to ``per_bullet`` (bare-bullet exam spec per
binding-specifications.md), Phase 3 post-processes the generated KUD
to drop ``understand`` and ``do_dispositions`` items. v4.1 specifies
that exam-spec mode produces an Assessed Demonstrations Map (know =
assessed topics, do_skills = tested demonstrations), NOT a four-column
KUD; pedagogical artefacts are refused.

The refusal is structural: the fields are emptied here and marked in
the run report. The output-node then writes the artefact under the
``assessed_demonstrations_map_v1.json`` filename with those fields
explicitly ``null``. ``state["output_mode"]`` is set so downstream
phases and the run report can display which shape discipline fired.

### Adjacent-mechanism declaration — refusal does NOT check

1. **Content smuggled into the allowed columns.** A prompt that
   emits disposition-like content dressed as a Do-Skill in exam-spec
   mode slips past this gate. The gate only checks which mode is
   active, not whether an item's content "fits" the column it landed
   in. Separate failure mode; flagged here but not addressed in
   Session 3c per the brief.
2. **Cases where the exam source carries command words / mark
   scheme.** Those profiles route to ``strand_aggregated`` and retain
   full KUD output (intentional — richer exam specs get the four-
   column treatment).
"""

from __future__ import annotations

import re
from typing import Any

from curriculum_harness._anthropic import (
    AnthropicCallTimeout,
    beta_messages_create,
    get_async_client,
    mcp_servers_param,
    mcp_toolset_single_tool,
    response_debug_dump,
    response_text_content,
)
from curriculum_harness.source_faithfulness import (
    SOURCE_FAITHFULNESS_FAIL_FLAG,
    compute_source_provenance,
)
from curriculum_harness.state import DecomposerState
from curriculum_harness.types import (
    HumanReviewItem,
    KUD,
    KUDItem,
    SONNET_MODEL,
    extract_json_object,
)

TOOL_NAME = "kud-knowledge-type-mapper"

_RECALL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bdates?\s+of\b", re.IGNORECASE),
    re.compile(r"\bkey\s+dates?\b", re.IGNORECASE),
    re.compile(r"\bkey\s+events?\b", re.IGNORECASE),
    re.compile(r"\bnames?\s+of\b", re.IGNORECASE),
    re.compile(r"\bdefinition(?:s)?\s+of\b", re.IGNORECASE),
    re.compile(r"\bkey\s+events?\s+and\s+dates?\b", re.IGNORECASE),
    re.compile(r"\bhistorical\s+dates?\b", re.IGNORECASE),
    re.compile(r"\bfactual\s+recall\b", re.IGNORECASE),
    re.compile(r"\bvocabulary\b", re.IGNORECASE),
)

_SUBSTANTIVE = re.compile(
    r"\b(analy[sz]e|evaluate|interpret|compare|apply|construct|inquiry|framework|"
    r"perspective|significance|continuity|change|cause|consequence|synthes|argu|judg)\b",
    re.IGNORECASE,
)


def is_recall_only_know_content(content: str) -> bool:
    """True if know[] item is recall-only listing (dates, names, definitions) without substantive task."""
    t = (content or "").strip()
    if not t:
        return False
    if _SUBSTANTIVE.search(t):
        return False
    return any(p.search(t) for p in _RECALL_PATTERNS)


def _filter_recall_only_know(kud: KUD) -> tuple[KUD, int]:
    kept: list[KUDItem] = []
    removed = 0
    for item in kud.know:
        if is_recall_only_know_content(item.content):
            removed += 1
        else:
            kept.append(item)
    kud.know = kept
    return kud, removed


def _attach_source_faithfulness(kud: KUD, source_bullets: list[dict]) -> int:
    """Attach source_provenance + SOURCE_FAITHFULNESS_FAIL flag to every
    KUD item. Returns the count of items flagged below threshold.

    Items ship with the flag rather than being dropped — Session 3b
    will add a regeneration loop. See
    ``curriculum_harness/source_faithfulness.py`` for the matcher's
    adjacent-mechanism declaration, including language-boundary and
    grain-appropriateness limits.
    """
    flagged = 0
    for _bucket, item in kud.all_items():
        provenance, passed = compute_source_provenance(
            item.content, source_bullets
        )
        item.source_provenance = provenance
        if not passed:
            if SOURCE_FAITHFULNESS_FAIL_FLAG not in item.flags:
                item.flags.append(SOURCE_FAITHFULNESS_FAIL_FLAG)
            flagged += 1
    return flagged


SYSTEM_DIRECT = """You map curriculum expectations into KUD lists. Output ONLY valid JSON:
{
  "know": [{"content": str, "knowledge_type": "hierarchical"|"horizontal"|"dispositional",
            "assessment_route": "rubric_criterion"|"rubric_reasoning"|"observation_protocol", "notes": str}],
  "understand": [same shape],
  "do_skills": [same shape],
  "do_dispositions": [same shape]
}
Tags must align with the architecture diagnosis provided. No markdown."""

SYSTEM_DIRECT_PER_BULLET = """You map curriculum source bullets into KUD lists, one KUD item per source bullet.
The input is a numbered list of source bullets from an exam specification or content list.

Cardinality rule: produce exactly one KUD item per source bullet where the
bullet expresses a distinct piece of content. Do not consolidate multiple
bullets into a single KUD item. Do not group bullets by theme. If two
bullets restate the same content verbatim (rare — the source-bullet
extractor already dedupes), you may emit one KUD item and note the
merger in the `notes` field.

Output ONLY valid JSON:
{
  "know": [{"content": str, "knowledge_type": "hierarchical"|"horizontal"|"dispositional",
            "assessment_route": "rubric_criterion"|"rubric_reasoning"|"observation_protocol",
            "notes": str, "source_bullet_ids": [str]}],
  "understand": [same shape],
  "do_skills": [same shape],
  "do_dispositions": [same shape]
}

`source_bullet_ids` lists the sb_NNN IDs the KUD item was derived from
(usually a single ID; a list of two or more means you merged those
bullets and the merge must be justified in `notes`). Tags must align
with the architecture diagnosis provided. No markdown."""


def _classify_profile_mode(profile: dict[str, Any]) -> str:
    """Return one of ``per_bullet``, ``strand_aggregated``, ``default``.

    Reads `document_family`, `scoping_strategy`, and
    `assessment_signals.has_command_words` /
    `assessment_signals.has_mark_scheme` from the curriculum profile.
    See Session 1 diagnosis (`docs/diagnostics/2026-04-17-session-1-diagnosis.md`)
    Q2 / Q5 for why these three signals, and the module docstring above
    for the resolution rules.
    """
    if not profile:
        return "default"
    fam = str(profile.get("document_family") or "").strip().lower()
    strategy = str(profile.get("scoping_strategy") or "").strip().lower()
    signals = profile.get("assessment_signals") or {}
    has_cmd = bool(signals.get("has_command_words"))
    has_mark = bool(signals.get("has_mark_scheme"))

    if (
        fam == "exam_specification"
        and not has_cmd
        and not has_mark
        and strategy == "full_document"
    ):
        return "per_bullet"
    # Richer designed source: any non-exam family, or an exam spec that
    # carries command words or a mark scheme.
    rich_families = {
        "national_framework",
        "school_scoped_programme",
        "higher_ed_syllabus",
        "curriculum_document",
    }
    if fam in rich_families or has_cmd or has_mark:
        return "strand_aggregated"
    return "default"


def _format_bullets_for_prompt(bullets: list[dict]) -> str:
    lines = []
    for b in bullets:
        bid = b.get("id") or ""
        text = (b.get("text") or "").strip()
        if not bid or not text:
            continue
        lines.append(f"{bid}: {text}")
    return "\n".join(lines)


async def _direct_sonnet_kud_per_bullet(
    bullets: list[dict],
    arch_summary: str,
) -> KUD:
    client = get_async_client()
    bullet_block = _format_bullets_for_prompt(bullets)
    body = (
        f"Architecture diagnosis (JSON):\n{arch_summary}\n\n"
        f"Source bullets ({len(bullets)} total, one per line, `sb_NNN: text`):\n\n"
        f"{bullet_block[:90000]}"
    )
    msg = await beta_messages_create(
        client,
        model=SONNET_MODEL,
        max_tokens=16384,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": SYSTEM_DIRECT_PER_BULLET},
                {"type": "text", "text": body},
            ],
        }],
        label="phase3_sonnet_direct_kud_per_bullet",
    )
    text = response_text_content(msg)
    parsed = extract_json_object(text)
    if parsed:
        return KUD.from_dict(parsed)
    return KUD()


async def _direct_sonnet_kud(
    raw_curriculum: str,
    arch_summary: str,
) -> KUD:
    client = get_async_client()
    body = f"Architecture diagnosis (JSON):\n{arch_summary}\n\nCurriculum:\n{raw_curriculum[:95000]}"
    msg = await beta_messages_create(
        client,
        model=SONNET_MODEL,
        max_tokens=16384,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": SYSTEM_DIRECT},
                {"type": "text", "text": body},
            ],
        }],
        label="phase3_sonnet_direct_kud",
    )
    text = response_text_content(msg)
    parsed = extract_json_object(text)
    if parsed:
        return KUD.from_dict(parsed)
    return KUD()


async def phase3_kud(state: DecomposerState) -> dict[str, Any]:
    errs = list(state.get("errors") or [])
    review_dicts = list(state.get("human_review_queue") or [])

    raw = state.get("raw_curriculum") or ""
    arch = state.get("architecture_diagnosis") or {}
    # Session 3b — Shape C fix. See module docstring.
    profile = state.get("curriculum_profile") or {}
    source_bullets = list(state.get("source_bullets") or [])
    branch = _classify_profile_mode(profile)
    if branch == "default":
        errs.append(
            "phase3: curriculum_profile did not match per_bullet or "
            "strand_aggregated cleanly — defaulting to strand_aggregated branch"
        )
    if not raw.strip():
        errs.append("phase3: skipped — empty raw_curriculum")
        return {
            "current_phase": "phase3:skipped",
            "errors": errs,
            "kud": KUD().to_dict(),
            "recall_filtered_count": 0,
            "phase3_branch": branch,
            "phase3_input_bullet_count": len(source_bullets),
        }

    mcp_url = state.get("mcp_server_url") or ""
    mcp_name = state.get("mcp_server_name") or "claude-education-skills"
    arch_text = str(arch)[:20000]

    if branch == "per_bullet":
        if not source_bullets:
            errs.append(
                "phase3: per_bullet branch selected but source_bullets empty — "
                "falling back to strand_aggregated instruction"
            )
            branch = "strand_aggregated"

    if branch == "per_bullet":
        bullet_block = _format_bullets_for_prompt(source_bullets)
        instruction = (
            f"Invoke `{TOOL_NAME}` using these source bullets and architecture diagnosis.\n\n"
            f"Cardinality rule: produce exactly one KUD item per source bullet. Do not "
            f"consolidate multiple bullets into a single KUD item. Do not group bullets by "
            f"theme.\n\n"
            f"Architecture diagnosis (JSON):\n{arch_text}\n\n"
            f"Source bullets ({len(source_bullets)} total, one per line, `sb_NNN: text`):\n\n"
            f"{bullet_block[:90000]}\n\n"
            "After tool results, reply with ONLY a JSON object for know, understand, do_skills, "
            "do_dispositions arrays (items with content, knowledge_type, assessment_route, "
            "notes, source_bullet_ids)."
        )
        user_content = [{"type": "text", "text": instruction}]
    else:
        instruction = (
            f"Invoke `{TOOL_NAME}` using the curriculum text and this architecture diagnosis:\n"
            f"{arch_text}\n\n"
            "After tool results, reply with ONLY a JSON object for know, understand, do_skills, "
            "do_dispositions arrays (items with content, knowledge_type, assessment_route, notes)."
        )
        user_content = [
            {"type": "text", "text": instruction},
            {"type": "text", "text": f"Curriculum text:\n\n{raw[:100000]}"},
        ]

    messages = [{"role": "user", "content": user_content}]

    kud = KUD()
    used_mcp = False
    resp: Any = None

    try:
        client = get_async_client()
        resp = await beta_messages_create(
            client,
            model=SONNET_MODEL,
            max_tokens=16384,
            messages=messages,
            label="phase3_mcp_kud",
            mcp_servers=mcp_servers_param(mcp_url, mcp_name),
            tools=[mcp_toolset_single_tool(mcp_name, TOOL_NAME)],
        )
        used_mcp = True
        text = response_text_content(resp)
        parsed = extract_json_object(text)
        if parsed:
            kud = KUD.from_dict(parsed)
        else:
            raise ValueError("no_json_in_mcp_response")
    except AnthropicCallTimeout:
        errs.append("phase3: API timeout after 240s")
        return {
            "current_phase": "phase3:timeout",
            "errors": errs,
            "human_review_queue": review_dicts,
            "kud": KUD().to_dict(),
            "recall_filtered_count": 0,
            "phase3_branch": branch,
            "phase3_input_bullet_count": len(source_bullets),
        }
    except Exception as exc:
        raw_dump = response_debug_dump(resp) if resp is not None else str(exc)
        err_line = f"phase3: MCP/tools failed: {exc}"
        errs.append(err_line)
        review_dicts.append(
            HumanReviewItem(
                item_type="phase3_mcp",
                summary=err_line[:500],
                decision_needed="Review MCP failure; fallback JSON follows in pipeline output.",
            ).to_dict(),
        )
        review_dicts.append(
            HumanReviewItem(
                item_type="phase3_mcp_raw",
                summary="MCP response / error (truncated)",
                decision_needed=raw_dump[:8000],
            ).to_dict(),
        )
        if branch == "per_bullet":
            kud = await _direct_sonnet_kud_per_bullet(source_bullets, arch_text)
        else:
            kud = await _direct_sonnet_kud(raw, arch_text)

    kud, recall_filtered_count = _filter_recall_only_know(kud)

    # Session 3c — exam-spec output-shape discipline (v4.1).
    # per_bullet mode ⇒ bare-bullet exam spec ⇒ refuse Understand and
    # Disposition items. Refusal is structural: the arrays are emptied
    # here so downstream phases (Phase 4, Phase 5, output_node) see an
    # exam-spec-shaped KUD without special-case branching.
    exam_spec_refusals = {"understand_dropped": 0, "dispositions_dropped": 0}
    if branch == "per_bullet":
        exam_spec_refusals["understand_dropped"] = len(kud.understand)
        exam_spec_refusals["dispositions_dropped"] = len(kud.do_dispositions)
        kud.understand = []
        kud.do_dispositions = []
    output_mode = "exam_specification" if branch == "per_bullet" else "curriculum"

    faithfulness_flagged = _attach_source_faithfulness(kud, source_bullets)
    if not source_bullets:
        errs.append(
            "phase3: no source_bullets corpus available — "
            "SOURCE_FAITHFULNESS_FAIL flags suppressed for this run"
        )

    kud_item_count = sum(1 for _b, _i in kud.all_items())
    merge_events: list[dict[str, Any]] = []
    if branch == "per_bullet":
        for _bucket, item in kud.all_items():
            ids = getattr(item, "source_bullet_ids", None) or []
            if len(ids) > 1:
                merge_events.append(
                    {
                        "kud_content": item.content,
                        "merged_bullet_ids": list(ids),
                    }
                )

    return {
        "current_phase": "phase3:complete" if used_mcp else "phase3:fallback",
        "errors": errs,
        "human_review_queue": review_dicts,
        "kud": kud.to_dict(),
        "recall_filtered_count": recall_filtered_count,
        "phase3_faithfulness_flagged_count": faithfulness_flagged,
        "phase3_branch": branch,
        "phase3_input_bullet_count": len(source_bullets),
        "phase3_output_kud_item_count": kud_item_count,
        "phase3_merge_events": merge_events,
        "output_mode": output_mode,
        "phase3_exam_spec_refusals": exam_spec_refusals,
    }
