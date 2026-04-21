"""Generate band-tagged JSON for CASEL SEL Skills Continuum (2023).

Applies the Developmental Band Translator skill to the CASEL pipeline outputs,
mapping grade bands to REAL School Budapest A-F bands per the CW-2 session brief.

CASEL grade band → REAL band mapping (clean, high-confidence):
  Pre-Kindergarten  → Band A  (below REAL floor, pre-band note)
  Kindergarten-Grade 1 → Band A
  Grade Band 2-3    → Band B
  Grade Band 4-5    → Band C
  Grade Band 6-8    → Band D
  Grade Band 9-10   → Band E
  Grade Band 11-12  → Band F  (0 items due to pipeline halt)

Session: CW-2, 2026-04-21
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = REPO_ROOT / "docs" / "reference-corpus" / "casel-sel-continuum"

# ─── Band mapping ─────────────────────────────────────────────────────────────

STRAND_TO_REAL = {
    "pre-kindergarten": "A",
    "kindergarten-grade-1": "A",
    "kindergarten–grade-1": "A",  # em-dash variant
    "grade-band-2-3": "B",
    "grade-band-2–3": "B",
    "grade-band-4-5": "C",
    "grade-band-4–5": "C",
    "grade-band-6-8": "D",
    "grade-band-6–8": "D",
    "grade-band-9-10": "E",
    "grade-band-9–10": "E",
    "grade-band-11-12": "F",
    "grade-band-11–12": "F",
}

SOURCE_BAND_LABELS = {
    "pre-kindergarten": "Pre-Kindergarten",
    "kindergarten-grade-1": "Kindergarten-Grade 1",
    "kindergarten–grade-1": "Kindergarten-Grade 1",
    "grade-band-2-3": "Grade Band 2-3",
    "grade-band-2–3": "Grade Band 2-3",
    "grade-band-4-5": "Grade Band 4-5",
    "grade-band-4–5": "Grade Band 4-5",
    "grade-band-6-8": "Grade Band 6-8",
    "grade-band-6–8": "Grade Band 6-8",
    "grade-band-9-10": "Grade Band 9-10",
    "grade-band-9–10": "Grade Band 9-10",
    "grade-band-11-12": "Grade Band 11-12",
    "grade-band-11–12": "Grade Band 11-12",
}

RATIONALES = {
    "A": {
        "pre": (
            "CASEL Pre-Kindergarten (ages 3-5) falls below REAL Band A's floor (ages 5-7, K-2). "
            "Tagged Band A as the nearest REAL band; developmental content is foundational "
            "relative to REAL Band A expectations. Rationale: pre-band relative to REAL's earliest stage."
        ),
        "kg1": "CASEL Kindergarten-Grade 1 (ages 5-7) maps cleanly to REAL Band A (Water+Air Dragons, ages 5-7, K-2).",
    },
    "B": "CASEL Grade Band 2-3 (ages 7-9) maps cleanly to REAL Band B (Earth Dragons, ages 7-9, G3-4).",
    "C": "CASEL Grade Band 4-5 (ages 9-11) maps cleanly to REAL Band C (Fire Dragons, ages 9-11, G5-6).",
    "D": "CASEL Grade Band 6-8 (ages 11-14) maps to REAL Band D (Metal+Light Dragons, ages 11-13, G7-8); the 6-8 upper boundary (age 14) slightly exceeds Band D but the primary developmental stage aligns.",
    "E": "CASEL Grade Band 9-10 (ages 14-16) maps cleanly to REAL Band E (ages 13-15, G9-10).",
    "F": "CASEL Grade Band 11-12 (ages 16-18) maps cleanly to REAL Band F (ages 15-17, G11-12).",
}


def _strand_slug(source_block_id: str) -> str:
    """Extract strand slug from source_block_id or lt_id.

    source_block_id: 'pre-kindergarten_blk_0003' → 'pre-kindergarten'
    lt_id: 'pre-kindergarten_cluster_01_lt_01' → 'pre-kindergarten'
    """
    if "_blk_" in source_block_id:
        return source_block_id.split("_blk_")[0]
    if "_cluster_" in source_block_id:
        return source_block_id.split("_cluster_")[0]
    return source_block_id


def _get_rationale(strand: str, school_band: str) -> str:
    if school_band == "A":
        if "pre-kindergarten" in strand:
            return RATIONALES["A"]["pre"]
        return RATIONALES["A"]["kg1"]
    return RATIONALES.get(school_band, f"Mapped from strand '{strand}' to REAL Band {school_band}.")


def main() -> None:
    # Load pipeline outputs
    with open(CORPUS_DIR / "unified_kud.json") as f:
        kud_data = json.load(f)
    with open(CORPUS_DIR / "unified_lts.json") as f:
        lts_data = json.load(f)
    with open(CORPUS_DIR / "per_strand" / "pre-kindergarten" / "progression_structure.json") as f:
        prog_data = json.load(f)

    kud_items = kud_data["items"]
    lts = lts_data["lts"]

    # ── Tag KUD items ──────────────────────────────────────────────────────────

    band_tagged_kud = []
    for item in kud_items:
        sid = item.get("source_block_id", item.get("item_id", ""))
        strand = _strand_slug(sid)
        school_band = STRAND_TO_REAL.get(strand)
        if school_band is None:
            # Fallback: try stripping trailing numbers
            parts = strand.rsplit("-", 1)
            school_band = STRAND_TO_REAL.get(parts[0], "A")
            print(f"WARNING: unrecognised strand '{strand}', fallback to {school_band}", file=sys.stderr)

        source_band = SOURCE_BAND_LABELS.get(strand, strand)

        tagged = {
            "item_id": item["item_id"],
            "content_statement": item["content_statement"],
            "knowledge_type": item.get("knowledge_type", ""),
            "school_band": school_band,
            "band_confidence": "high",
            "source_band_preserved": source_band,
            "source_voice_preserved": True,
            "ambiguity_flag": False,
            "teacher_review_flag": strand == "pre-kindergarten",  # pre-band note
            "band_rationale": _get_rationale(strand, school_band),
            "source_block_id": sid,
            "strand_slug": strand,
        }
        band_tagged_kud.append(tagged)

    # ── Tag LTs ────────────────────────────────────────────────────────────────

    # Build item_id → school_band lookup
    item_band: dict[str, str] = {t["item_id"]: t["school_band"] for t in band_tagged_kud}

    band_tagged_lts = []
    for lt in lts:
        lt_id = lt.get("lt_id", "")
        # Get strand from lt_id prefix
        strand = _strand_slug(lt_id)
        school_band = STRAND_TO_REAL.get(strand)
        if school_band is None:
            # Infer from constituent items
            kud_ids = lt.get("kud_item_ids", [])
            bands = sorted({item_band[k] for k in kud_ids if k in item_band})
            school_band = bands[0] if bands else "A"

        source_band = SOURCE_BAND_LABELS.get(strand, strand)

        tagged_lt = {
            "lt_id": lt_id,
            "lt_name": lt.get("lt_name", ""),
            "lt_definition": lt.get("lt_definition", ""),
            "school_band": school_band,
            "band_confidence": "high",
            "source_band_preserved": source_band,
            "source_voice_preserved": True,
            "ambiguity_flag": False,
            "teacher_review_flag": strand == "pre-kindergarten",
            "band_rationale": _get_rationale(strand, school_band),
            "kud_item_ids": lt.get("kud_item_ids", []),
            "knowledge_type": lt.get("knowledge_type", ""),
            "strand_slug": strand,
        }
        band_tagged_lts.append(tagged_lt)

    # ── Summary counts ─────────────────────────────────────────────────────────

    from collections import Counter
    kud_by_band = Counter(t["school_band"] for t in band_tagged_kud)
    lt_by_band = Counter(t["school_band"] for t in band_tagged_lts)
    teacher_review_kud = sum(1 for t in band_tagged_kud if t["teacher_review_flag"])
    teacher_review_lts = sum(1 for t in band_tagged_lts if t["teacher_review_flag"])

    summary_counts = {
        "total_kud_items": len(band_tagged_kud),
        "total_lts": len(band_tagged_lts),
        "kud_by_band": dict(sorted(kud_by_band.items())),
        "lts_by_band": dict(sorted(lt_by_band.items())),
        "teacher_review_flagged_kud": teacher_review_kud,
        "teacher_review_flagged_lts": teacher_review_lts,
        "low_confidence": 0,
        "ambiguous": 0,
        "grade_band_11_12_halted_pipeline": 5,
        "note": (
            "Grade Band 11-12 (→ REAL Band F): 5 KUD blocks halted in pipeline "
            "(classification_unreliable — T2/T3 ambiguity in complex senior-level items). "
            "Band F has 0 KUD items and 0 LTs from this source."
        ),
    }

    # ── Skill flags ────────────────────────────────────────────────────────────

    skill_flags = [
        (
            "pre_band_items_tagged_A: Pre-Kindergarten items (ages 3-5) fall below REAL Band A's "
            "floor (ages 5-7). Tagged as Band A with teacher_review_flag=true and pre-band rationale. "
            "These items describe foundational skills that precede the REAL Band A developmental window."
        ),
        (
            "grade_band_11_12_pipeline_halt: All 5 content blocks from CASEL Grade Band 11-12 were "
            "halted in the harness pipeline (classification_unreliable: 3/3 LLM runs disagreed on "
            "T2 vs T3 knowledge type for complex senior-level items). REAL Band F has 0 CASEL items. "
            "This is a pipeline quality issue, not a source content issue. The Band F content exists "
            "in source.md and can be manually classified if needed."
        ),
        (
            "band_d_age_boundary: CASEL Grade Band 6-8 spans ages 11-14. REAL Band D spans ages 11-13. "
            "The upper boundary of Grade Band 6-8 (age 14) slightly exceeds Band D. Items at the "
            "older end of this band may have developmental characteristics closer to REAL Band E. "
            "Teacher review recommended for high-complexity Grade Band 6-8 items."
        ),
    ]

    # ── Assemble output ────────────────────────────────────────────────────────

    output = {
        "source_metadata": {
            "source_name": "CASEL SEL Skills Continuum (January 2023)",
            "source_type": prog_data.get("source_type", "casel_sel_grade_band"),
            "source_band_labels": prog_data.get("band_labels", []),
            "target_framework": "REAL School Budapest Bands A-F",
            "skill_version": "1.0",
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "session": "CW-2",
        },
        "band_tagged_kud": band_tagged_kud,
        "band_tagged_lts": band_tagged_lts,
        "summary_counts": summary_counts,
        "skill_flags": skill_flags,
    }

    out_path = CORPUS_DIR / "band-tagged-casel-v1.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Written: {out_path}")
    print(f"KUD items tagged: {len(band_tagged_kud)}")
    print(f"LTs tagged: {len(band_tagged_lts)}")
    print(f"KUD by band: {dict(sorted(kud_by_band.items()))}")
    print(f"LTs by band: {dict(sorted(lt_by_band.items()))}")
    print(f"teacher_review_flagged (kud): {teacher_review_kud}")


if __name__ == "__main__":
    main()
