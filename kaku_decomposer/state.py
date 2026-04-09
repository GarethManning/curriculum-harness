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
