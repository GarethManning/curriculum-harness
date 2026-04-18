"""LangGraph shared state (TypedDict)."""

from __future__ import annotations

from typing import Any, TypedDict


class DecomposerState(TypedDict, total=False):
    config_path: str
    config: dict[str, Any]
    source_url: str
    subject: str
    grade: str
    jurisdiction: str
    year: str
    raw_curriculum: str
    curriculum_metadata: dict[str, Any]
    architecture_diagnosis: dict[str, Any]
    kud: dict[str, Any]
    learning_targets: list[dict[str, Any]]
    human_review_queue: list[dict[str, Any]]
    run_id: str
    errors: list[str]
    current_phase: str
    output_path_resolved: str
    checkpoint_db_resolved: str
    mcp_server_url: str
    mcp_server_name: str
    lt_constraints: dict[str, Any]
    recall_filtered_count: int
    curriculum_profile: dict[str, Any]
    curriculum_classification_notes: str
    source_bullets: list[dict[str, Any]]
    phase3_faithfulness_flagged_count: int
    phase4_faithfulness_flagged_count: int
    # Session 3b — Phase 3 profile-conditional branch (Shape C fix).
    phase3_branch: str
    phase3_input_bullet_count: int
    phase3_output_kud_item_count: int
    phase3_merge_events: list[dict[str, Any]]
    # Session 3c — exam-spec output-shape discipline + Phase 4 regeneration.
    # output_mode is "exam_specification" when Phase 3 ran per_bullet (bare-
    # bullet exam spec per v4.1); "curriculum" otherwise. Determines the
    # top-level artefact label (kud vs assessed_demonstrations_map).
    output_mode: str
    # Phase 1 source-language detection result: "en" or "non-en". Phase 4's
    # regeneration loop skips SOURCE_FAITHFULNESS_FAIL retries when non-en
    # because the matcher is English-only.
    source_language: str
    source_language_signal: dict[str, Any]
    # Phase 4 regeneration-event log (one entry per LT that initially
    # failed FAIL_SET validation). Read by validate_regenerate_loop gate.
    regeneration_events: list[dict[str, Any]]
    # LTs that exhausted the regeneration budget — source bullets surfaced
    # for human review rather than shipping the flagged LT as if valid.
    human_review_required: list[dict[str, Any]]
    # Phase 3 exam-spec refusal counters (understand / dispositions dropped).
    phase3_exam_spec_refusals: dict[str, int]
