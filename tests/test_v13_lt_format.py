"""v1.3: profile-driven lt_statement_format (resolver, Phase 4 validation, Phase 5 fallback)."""

from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path

import pytest

from curriculum_harness.phases.phase4_lt_generation import (
    _validate_lt,
    cosine_similarity_text,
)
from curriculum_harness.phases.phase5_formatting import _level_statement_fallback
from curriculum_harness.types import (
    HE_DISPOSITION_INFERRED,
    LearningTarget,
    resolve_lt_statement_format,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
GCSE_CONFIG = REPO_ROOT / "configs" / "gcse_aqa_history_v1_0.json"
UNI_CONFIG = REPO_ROOT / "configs" / "university_history_syllabus_v1_0.json"


def test_resolve_lt_statement_format_defaults() -> None:
    assert resolve_lt_statement_format({}) == "i_can"
    assert resolve_lt_statement_format({"document_family": "exam_specification"}) == "i_can"
    assert resolve_lt_statement_format({"document_family": "national_framework"}) == "i_can"
    assert resolve_lt_statement_format({"document_family": "higher_ed_syllabus"}) == "outcome_statement"


def test_resolve_lt_statement_format_config_override() -> None:
    p = {
        "document_family": "exam_specification",
        "output_conventions": {"lt_statement_format": "competency_descriptor"},
    }
    assert resolve_lt_statement_format(p) == "competency_descriptor"


def test_validate_lt_per_format() -> None:
    lt_ok = LearningTarget(statement="I can explain causes of the war.", type=2)
    assert "MISSING_I_CAN_FORMAT" not in _validate_lt(lt_ok, compound_type=False, fmt="i_can")

    lt_bad = LearningTarget(statement="Explains causes without prefix.", type=2)
    assert "MISSING_I_CAN_FORMAT" in _validate_lt(lt_bad, compound_type=False, fmt="i_can")

    out_bad = LearningTarget(statement="I can explain causes.", type=2)
    assert "LT_FORMAT_EXPECTATION_MISMATCH" in _validate_lt(
        out_bad, compound_type=False, fmt="outcome_statement"
    )

    comp_bad = LearningTarget(statement="I can use evidence.", type=2)
    assert "LT_FORMAT_EXPECTATION_MISMATCH" in _validate_lt(
        comp_bad, compound_type=False, fmt="competency_descriptor"
    )


def test_level_statement_fallback_word_cap() -> None:
    long_ic = "I can " + "word " * 30
    short = _level_statement_fallback(long_ic, "i_can", max_words=10)
    assert len(short.split()) == 10

    long_plain = "word " * 30
    short2 = _level_statement_fallback(long_plain, "outcome_statement", max_words=8)
    assert len(short2.split()) == 8


def test_cosine_similarity_identical() -> None:
    s = "Critical evaluation of historical sources for utility"
    assert cosine_similarity_text(s, s) == pytest.approx(1.0, abs=1e-9)


def test_learning_target_lt_statement_format_roundtrip() -> None:
    d = {
        "statement": "I can test.",
        "type": 1,
        "lt_statement_format": "i_can",
        "flags": [],
    }
    lt = LearningTarget.from_dict(d)
    assert lt.lt_statement_format == "i_can"
    assert lt.to_dict()["lt_statement_format"] == "i_can"


def _latest_run_artifact(out_dir: Path, run_id: str, artifact_base: str, ext: str) -> Path | None:
    rid = (run_id or "run").strip() or "run"
    paths = sorted(
        out_dir.glob(f"{rid}_{artifact_base}_v*.{ext.lstrip('.')}"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return paths[0] if paths else None


_GCSE_CMD_VERB = re.compile(
    r"\b(analyse|analyze|evaluate|explain|assess|compare|describe)\b",
    re.IGNORECASE,
)


@pytest.mark.integration
def test_gcse_pipeline_lt_format_i_can_and_command_language(tmp_path: Path) -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY required")
    if not GCSE_CONFIG.is_file():
        pytest.skip("GCSE config missing")

    cfg = json.loads(GCSE_CONFIG.read_text(encoding="utf-8"))
    out_path = tmp_path / "out"
    cfg["outputPath"] = str(out_path)
    cfg["checkpointDb"] = str(tmp_path / "cp.db")
    run_id = "test_gcse_v13_lt_format"
    cfg["runId"] = run_id
    cfg["curriculumProfile"] = {
        "document_family": "exam_specification",
        "output_conventions": {"lt_statement_format": "i_can"},
    }

    async def _run() -> None:
        from curriculum_harness.graph import build_initial_state, compile_graph

        st = build_initial_state(str(GCSE_CONFIG), cfg)
        st["output_structure"] = cfg.get("outputStructure")
        cp = Path(st["checkpoint_db_resolved"])
        graph = await compile_graph(cp)
        await graph.ainvoke(dict(st), config={"configurable": {"thread_id": st["run_id"]}})

    asyncio.run(_run())

    prof_path = _latest_run_artifact(out_path, run_id, "curriculum_profile", "json")
    assert prof_path and prof_path.is_file()
    profile = json.loads(prof_path.read_text(encoding="utf-8"))
    oc = profile.get("output_conventions") or {}
    assert str(oc.get("lt_statement_format", "")).lower() == "i_can"

    lt_path = _latest_run_artifact(out_path, run_id, "learning_targets", "json")
    assert lt_path and lt_path.is_file()
    lts = json.loads(lt_path.read_text(encoding="utf-8")).get("learning_targets") or []
    assert lts
    assert all(str(lt.get("lt_statement_format", "")).lower() == "i_can" for lt in lts)
    hits = [
        lt
        for lt in lts
        if _GCSE_CMD_VERB.search(str(lt.get("statement", "")))
    ]
    assert hits, "expected ≥1 LT with GCSE-style command language in statement"


@pytest.mark.integration
def test_university_pipeline_he_disposition_inferred(tmp_path: Path) -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY required")
    if not UNI_CONFIG.is_file():
        pytest.skip("University config missing")

    cfg = json.loads(UNI_CONFIG.read_text(encoding="utf-8"))
    out_path = tmp_path / "out"
    cfg["outputPath"] = str(out_path)
    cfg["checkpointDb"] = str(tmp_path / "cp2.db")
    run_id = "test_uni_v13_he_disposition"
    cfg["runId"] = run_id
    cfg["curriculumProfile"] = {"document_family": "higher_ed_syllabus"}

    async def _run() -> None:
        from curriculum_harness.graph import build_initial_state, compile_graph

        st = build_initial_state(str(UNI_CONFIG), cfg)
        st["output_structure"] = cfg.get("outputStructure")
        cp = Path(st["checkpoint_db_resolved"])
        graph = await compile_graph(cp)
        await graph.ainvoke(dict(st), config={"configurable": {"thread_id": st["run_id"]}})

    asyncio.run(_run())

    lt_path = _latest_run_artifact(out_path, run_id, "learning_targets", "json")
    assert lt_path and lt_path.is_file()
    lts = json.loads(lt_path.read_text(encoding="utf-8")).get("learning_targets") or []
    t3_he = [
        lt
        for lt in lts
        if int(lt.get("type") or 0) == 3
        and HE_DISPOSITION_INFERRED in (lt.get("flags") or [])
    ]
    assert t3_he, "expected ≥1 Type 3 LT with HE_DISPOSITION_INFERRED"
