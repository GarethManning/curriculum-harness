"""Unit tests for Phase 3 exam-spec output-shape refusal (Session 3c).

Exam-spec mode (``per_bullet`` branch) must empty ``understand`` and
``do_dispositions`` after the KUD is built, so downstream phases and
the output artefact honour the v4.1 Assessed Demonstrations Map shape.
"""
from __future__ import annotations

from curriculum_harness.phases.phase3_kud import _classify_profile_mode
from curriculum_harness.phases.phase1_ingestion import (
    _detect_source_language_from_bullets,
)


def test_per_bullet_mode_is_equivalent_to_exam_spec_output() -> None:
    # Sanity: the branch classifier used by Phase 3's refusal gate.
    profile = {
        "document_family": "exam_specification",
        "scoping_strategy": "full_document",
        "assessment_signals": {
            "has_command_words": False,
            "has_mark_scheme": False,
        },
    }
    assert _classify_profile_mode(profile) == "per_bullet"


def test_language_detection_flags_hungarian_bullets_as_non_en() -> None:
    bullets = [
        {"text": "Elemi kombinatorika (összeszámolás, sorrendek száma, kiválasztás)."},
        {"text": "Műveletek törtekkel."},
        {"text": "A tizedes törtek fajtái (véges, végtelen, végtelen szakaszos)."},
        {"text": "A kerekítés szabályainak alkalmazása."},
        {"text": "Pozitív egész kitevőjű hatványok ismerete."},
        {"text": "Számrendszerek ismerete."},
        {"text": "Összetett számok prímtényezős felbontása."},
        {"text": "Két halmaz közötti hozzárendelések, alaphalmaz, képhalmaz fogalma."},
    ]
    lang, signal = _detect_source_language_from_bullets(bullets)
    assert lang == "non-en"
    assert signal["status"] == "measured"
    assert signal["en_stopword_ratio"] < 0.05


def test_language_detection_flags_english_bullets_as_en() -> None:
    bullets = [
        {"text": "describe the significance of the fur trade to diverse communities in Canada"},
        {"text": "analyse the impact of colonialism on Indigenous governance structures"},
        {"text": "explain how treaties shaped early settlement patterns across the region"},
        {"text": "evaluate the perspectives of different historical sources on contact and conflict"},
        {"text": "identify the key events and dates of the Seven Years War period"},
    ]
    lang, signal = _detect_source_language_from_bullets(bullets)
    assert lang == "en"
    assert signal["status"] == "measured"
    assert signal["en_stopword_ratio"] >= 0.05


def test_empty_bullet_corpus_defaults_to_en() -> None:
    lang, signal = _detect_source_language_from_bullets([])
    assert lang == "en"
    assert signal["status"] == "empty_bullet_corpus"
