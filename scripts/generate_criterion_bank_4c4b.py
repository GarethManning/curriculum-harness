"""Criterion bank generator for Session 4c-4b.

Produces criterion_bank.json and criterion_bank_quality_report.json for
the four remaining sources:
  - ap-usgov-ced-unit1       (single-strand, 26 LTs)
  - secondary-rshe-2025      (single-strand, 66 LTs — 62 Type 1/2 eligible)
  - dfe-ks3-maths            (multi-strand/unified, 6 strands, 29 LTs)
  - nz-social-sciences       (multi-strand/per-dir, 4 strands, 57 LTs eligible)

No hand-curated validation sets for these sources (Option A from session plan).
Agreement rate is NOT computed. DAG validation, spot-checks, and decomposition
audit are the primary quality gates.

Horizontal spot-check: NZ Social Sciences triggers a 5-LT horizontal review
before the commit. The script prints the spot-check and halts with a prompt
for the operator to approve before proceeding.

Usage:
    python scripts/generate_criterion_bank_4c4b.py <source_slug>

Where source_slug is one of:
    ap-usgov-ced-unit1
    secondary-rshe-2025
    dfe-ks3-maths
    nz-social-sciences
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from curriculum_harness._anthropic import LEDGER, get_async_client, haiku_stream_text
from curriculum_harness.types import SONNET_MODEL, extract_json_object

# Import shared components from anchor generator.
from scripts.generate_criterion_bank import (
    PASS1_SYSTEM,
    PASS2_SYSTEM,
    SCHEMA_VERSION,
    SINGLE_STRAND_SENTINEL,
    build_pass1_user,
    build_pass2_user,
    decomposition_audit,
    detect_cycles,
    detect_self_loops,
    detect_unresolved_ids,
    detect_cross_strand,
    over_generation_spot_check,
    run_dag_validation,
    validate_pass1_output,
    validate_pass2_output,
)

CORPUS_ROOT = Path(__file__).resolve().parent.parent / "docs" / "reference-corpus"

TYPE_1_2 = ("Type 1", "Type 2")

# ── Source configs ─────────────────────────────────────────────────────────────

SOURCES_4C4B: dict[str, dict] = {
    "ap-usgov-ced-unit1": {
        "type": "single_strand",
        "name": "AP US Government — CED Unit 1",
        "corpus_dir": "ap-usgov-ced-unit1",
        "strand": SINGLE_STRAND_SENTINEL,
        "lts_file": "lts.json",
        "kud_file": "kud.json",
        "criteria_file": "criteria.json",
        "horizontal_spot_check": False,
    },
    "secondary-rshe-2025": {
        "type": "single_strand",
        "name": "Secondary RSHE 2025",
        "corpus_dir": "secondary-rshe-2025",
        "strand": SINGLE_STRAND_SENTINEL,
        "lts_file": "lts.json",
        "kud_file": "kud.json",
        "criteria_file": "criteria.json",
        "horizontal_spot_check": False,
    },
    "dfe-ks3-maths": {
        "type": "multi_strand_unified",
        "name": "DfE KS3 Mathematics",
        "corpus_dir": "dfe-ks3-maths-4c3b",
        "lts_file": "unified_lts.json",
        "kud_file": "unified_kud.json",
        "criteria_file": "unified_criteria.json",
        "horizontal_spot_check": False,
        "strands": [
            {"slug": "number", "name": "Number"},
            {"slug": "algebra", "name": "Algebra"},
            {"slug": "ratio-proportion-and-rates-of-change",
             "name": "Ratio, proportion and rates of change"},
            {"slug": "geometry-and-measures", "name": "Geometry and measures"},
            {"slug": "probability", "name": "Probability"},
            {"slug": "statistics", "name": "Statistics"},
        ],
    },
    "nz-social-sciences": {
        "type": "multi_strand_per_dir",
        "name": "NZ Curriculum — Social Sciences",
        "corpus_dir": "nz-ss-social-sciences-4c3b",
        "lts_file": "unified_lts.json",
        "kud_file": "unified_kud.json",
        "criteria_file": "unified_criteria.json",
        "horizontal_spot_check": True,
        "strands": [
            {"slug": "history", "name": "History"},
            {"slug": "civics-and-society", "name": "Civics and Society"},
            {"slug": "geography", "name": "Geography"},
            {"slug": "economic-activity", "name": "Economic Activity"},
        ],
    },
}


# ── Strand data loaders ────────────────────────────────────────────────────────

def _load_lts(path: Path) -> list[dict]:
    with open(path) as f:
        raw = json.load(f)
    return raw if isinstance(raw, list) else raw.get("learning_targets", raw.get("lts", []))


def _load_kud(path: Path) -> list[dict]:
    with open(path) as f:
        raw = json.load(f)
    return raw.get("items", []) if isinstance(raw, dict) else raw


def _strand_slug_from_field(val: Any) -> str:
    """Extract strand slug from a strand field that may be a dict or string."""
    if isinstance(val, dict):
        return val.get("strand_slug", str(val))
    return str(val) if val else SINGLE_STRAND_SENTINEL


def load_strand_data_single(source_cfg: dict, corpus_dir: Path) -> dict[str, dict]:
    """Single-strand: returns {single_strand: {lts, kud_items, strand_name}}."""
    lts = _load_lts(corpus_dir / source_cfg["lts_file"])
    kud_items = _load_kud(corpus_dir / source_cfg["kud_file"])
    return {
        SINGLE_STRAND_SENTINEL: {
            "lts": lts,
            "kud_items": kud_items,
            "strand_name": source_cfg["name"],
            "strand_slug": SINGLE_STRAND_SENTINEL,
        }
    }


def load_strand_data_unified(source_cfg: dict, corpus_dir: Path) -> dict[str, dict]:
    """Multi-strand with unified files: group LTs and KUD items by strand_slug."""
    lts_all = _load_lts(corpus_dir / source_cfg["lts_file"])
    kud_all = _load_kud(corpus_dir / source_cfg["kud_file"])

    slug_to_info = {s["slug"]: s for s in source_cfg["strands"]}
    result: dict[str, dict] = {}

    for s in source_cfg["strands"]:
        slug = s["slug"]
        strand_lts = [
            lt for lt in lts_all
            if _strand_slug_from_field(lt.get("strand")) == slug
        ]
        strand_kud = [
            item for item in kud_all
            if _strand_slug_from_field(item.get("strand")) == slug
        ]
        result[slug] = {
            "lts": strand_lts,
            "kud_items": strand_kud,
            "strand_name": s["name"],
            "strand_slug": slug,
        }

    return result


def load_strand_data_per_dir(source_cfg: dict, corpus_dir: Path) -> dict[str, dict]:
    """Multi-strand with per-directory layout: load lts.json/kud.json per strand."""
    result: dict[str, dict] = {}
    per_strand_root = corpus_dir / "per_strand"

    for s in source_cfg["strands"]:
        slug = s["slug"]
        strand_dir = per_strand_root / slug
        lts = _load_lts(strand_dir / "lts.json")
        kud_items = _load_kud(strand_dir / "kud.json")
        result[slug] = {
            "lts": lts,
            "kud_items": kud_items,
            "strand_name": s["name"],
            "strand_slug": slug,
        }

    return result


# ── Cost estimate ──────────────────────────────────────────────────────────────

def estimate_cost(strand_data: dict[str, dict], n_pass2_runs: int) -> float:
    """Sonnet pricing: $3/MTok in, $15/MTok out."""
    n_lts_total = sum(
        len([lt for lt in sd["lts"] if lt.get("knowledge_type") in TYPE_1_2])
        for sd in strand_data.values()
    )
    in_tok = (n_lts_total * 1500 + n_pass2_runs * 3000) / 1_000_000
    out_tok = (n_lts_total * 800 + n_pass2_runs * 1500) / 1_000_000
    return in_tok * 3.0 + out_tok * 15.0


# ── Hallucination / scope-drift spot-check ─────────────────────────────────────

def scope_drift_check(criteria: list[dict], lts: list[dict], sample_size: int = 10) -> dict:
    """Check whether criterion statements introduce content absent from the source LT.

    Heuristic: extract meaningful content words from the LT definition and name,
    then check whether the criterion_statement contains at least one of them.
    Flags criteria where no LT content word appears — these may be hallucinations.
    """
    import random
    import re

    # Build LT lookup
    lt_map = {lt["lt_id"]: lt for lt in lts}

    # Simple stopword filter
    STOPWORDS = {
        "a", "an", "the", "and", "or", "of", "to", "in", "for", "with", "on",
        "is", "are", "that", "this", "can", "how", "by", "at", "from", "as",
        "be", "it", "its", "their", "they", "we", "our", "not", "no", "so",
        "which", "when", "where", "who", "what", "between", "through", "about",
        "across", "into", "over", "under", "between", "among", "within",
    }

    def content_words(text: str) -> set[str]:
        words = re.findall(r"[a-z]{3,}", text.lower())
        return {w for w in words if w not in STOPWORDS}

    # Sample criteria
    n = min(sample_size, len(criteria))
    sampled = random.sample(criteria, n) if len(criteria) > n else criteria[:]

    flags = []
    rows = []
    for c in sampled:
        lt_ids = c.get("associated_lt_ids", [])
        lt = None
        for lid in lt_ids:
            if lid in lt_map:
                lt = lt_map[lid]
                break
        if not lt:
            continue

        lt_text = (lt.get("lt_name", "") + " " + lt.get("lt_definition", "")).lower()
        lt_words = content_words(lt_text)
        crit_words = content_words(c.get("criterion_statement", ""))

        overlap = lt_words & crit_words
        if not overlap:
            flags.append({
                "criterion_id": c["criterion_id"],
                "criterion_statement": c["criterion_statement"],
                "lt_id": lt_ids[0] if lt_ids else "?",
                "lt_name": lt.get("lt_name", ""),
                "issue": "no content-word overlap with source LT — possible scope drift",
            })
        rows.append({
            "criterion_id": c["criterion_id"],
            "lt_id": lt_ids[0] if lt_ids else "?",
            "overlap_word_count": len(overlap),
            "overlap_sample": sorted(overlap)[:5],
        })

    return {
        "sample_size": n,
        "flags_found": len(flags),
        "flags": flags,
        "rows": rows,
    }


# ── Horizontal spot-check ──────────────────────────────────────────────────────

def print_horizontal_spot_check(criteria: list[dict], lts: list[dict], n: int = 5) -> None:
    """Print n decomposed LTs for operator approval before committing NZ SS."""
    import random
    lt_map = {lt["lt_id"]: lt for lt in lts}
    from collections import defaultdict
    crit_per_lt: dict[str, list[dict]] = defaultdict(list)
    for c in criteria:
        for lt_id in c["associated_lt_ids"]:
            crit_per_lt[lt_id].append(c)

    eligible_lt_ids = [lt_id for lt_id, crits in crit_per_lt.items() if crits]
    sample = random.sample(eligible_lt_ids, min(n, len(eligible_lt_ids)))

    print("\n" + "=" * 70)
    print("HORIZONTAL SPOT-CHECK — NZ Social Sciences")
    print("Review these 5 decomposed LTs before approving the commit.")
    print("=" * 70)

    for i, lt_id in enumerate(sample, 1):
        lt = lt_map.get(lt_id, {})
        crits = crit_per_lt[lt_id]
        print(f"\n[{i}] LT: {lt_id} [{lt.get('knowledge_type', '?')}]")
        print(f"     Name: {lt.get('lt_name', '?')}")
        print(f"     Def:  {lt.get('lt_definition', '(no definition)')[:120]}")
        print(f"     → {len(crits)} criterion/criteria:")
        for c in crits:
            print(f"        [{c['criterion_id']}] {c['criterion_statement']}")
            decomp = c.get("decomposition_rationale", "")
            if decomp:
                print(f"        Rationale: {decomp[:120]}")

    print("\n" + "=" * 70)
    print("STOP: Horizontal spot-check above requires operator approval.")
    print("If the decompositions are correct, re-run with --approve-horizontal.")
    print("If not, adjust generation and re-run.")
    print("=" * 70 + "\n")


# ── Per-strand criterion generation ───────────────────────────────────────────

async def generate_pass1_for_strand(
    strand_slug: str,
    lts: list[dict],
    kud_items: list[dict],
    client: Any,
) -> tuple[dict[str, list[dict]], list[dict]]:
    """Run Pass 1 for all Type 1/2 LTs in a strand. Returns (by_lt, failed)."""
    type12_lts = [lt for lt in lts if lt.get("knowledge_type") in TYPE_1_2]
    kud_item_ids = {k["item_id"] for k in kud_items}
    raw_by_lt: dict[str, list[dict]] = {}
    failed: list[dict] = []

    async def _process(lt: dict) -> None:
        user_prompt = build_pass1_user(lt, kud_items, type12_lts)
        label = f"refauth_critbank_4c4b_pass1 {lt['lt_id']}"
        try:
            text = await haiku_stream_text(
                client,
                model=SONNET_MODEL,
                max_tokens=2048,
                system=PASS1_SYSTEM,
                user_blocks=[{"type": "text", "text": user_prompt}],
                label=label,
                temperature=0.1,
            )
        except Exception as exc:
            print(f"  ERROR {lt['lt_id']}: {exc}")
            failed.append({"lt_id": lt["lt_id"], "error": str(exc)})
            return

        parsed = extract_json_object(text)
        validated = validate_pass1_output(parsed, kud_item_ids)
        if not validated:
            print(f"  PARSE FAIL {lt['lt_id']}: {text[:200]!r}")
            failed.append({
                "lt_id": lt["lt_id"],
                "error": "pass1 output did not validate",
                "raw": text[:500],
            })
            return
        raw_by_lt[lt["lt_id"]] = validated
        print(f"  {lt['lt_id']}: {len(validated)} criterion/criteria")

    sem = asyncio.Semaphore(4)

    async def _bounded(lt: dict) -> None:
        async with sem:
            await _process(lt)

    await asyncio.gather(*[_bounded(lt) for lt in type12_lts])
    return raw_by_lt, failed


async def generate_pass2_for_strand(
    criteria: list[dict],
    source_name: str,
    strand_name: str,
    client: Any,
) -> list[dict]:
    """Run Pass 2 for a strand's criteria. Returns validated edge list.

    max_tokens scales with bank size: ~120 tokens per criterion for edges
    (empirical), minimum 4096, capped at 16000 (Sonnet output limit).
    """
    criterion_ids = {c["criterion_id"] for c in criteria}
    label = f"refauth_critbank_4c4b_pass2 {strand_name}"
    # Scale max_tokens with number of criteria to avoid truncation on large banks.
    # Cap at 8192 (Sonnet output limit). For very large banks, the PASS2_SYSTEM
    # instructs focus on strongest edges — the output should remain tractable.
    max_tokens = min(8192, max(4096, len(criteria) * 100))
    # Pass 2 gets no curated edges for 4c-4b sources.
    pass2_user = build_pass2_user(criteria, f"{source_name} — {strand_name}", curated_lt_edges=[])
    # For large banks, add a sparsity note to prevent over-generation.
    if len(criteria) > 60:
        pass2_user += (
            "\n\nNOTE: This is a large criterion bank. Generate only the "
            "STRONGEST and most educationally necessary prerequisite edges "
            "(max ~3 per criterion). Omit weak or marginal edges to keep "
            "the output tractable. Quality over completeness."
        )
    try:
        text = await haiku_stream_text(
            client,
            model=SONNET_MODEL,
            max_tokens=max_tokens,
            system=PASS2_SYSTEM,
            user_blocks=[{"type": "text", "text": pass2_user}],
            label=label,
            temperature=0.1,
        )
    except Exception as exc:
        raise RuntimeError(f"Pass 2 failed for {strand_name}: {exc}") from exc

    parsed = extract_json_object(text)
    validated = validate_pass2_output(parsed, criterion_ids)
    if validated is None:
        raise RuntimeError(f"Pass 2 output did not validate for {strand_name}: {text[:500]!r}")
    return validated


# ── Rename helpers ─────────────────────────────────────────────────────────────

def rename_criteria_files(source_cfg: dict, corpus_dir: Path) -> list[dict]:
    """Rename criteria artefact(s) to rubrics for a source. Returns list of results."""
    results = []

    def _rename_one(src_path: Path, dst_path: Path) -> dict:
        if not src_path.exists():
            return {"status": "skipped", "reason": f"{src_path.name} not found", "path": str(src_path)}
        with open(src_path) as f:
            data = json.load(f)
        items = data if isinstance(data, list) else data.get("criteria", data.get("rubrics", []))
        pre_count = len(items)
        pre_gate_fail = sum(1 for r in items if not r.get("quality_gate_passed", True))
        pre_keys = set(items[0].keys()) if items else set()
        with open(dst_path, "w") as f:
            json.dump(data, f, indent=2)
        with open(dst_path) as f:
            check = json.load(f)
        check_items = check if isinstance(check, list) else check.get("criteria", check.get("rubrics", []))
        post_count = len(check_items)
        post_gate_fail = sum(1 for r in check_items if not r.get("quality_gate_passed", True))
        post_keys = set(check_items[0].keys()) if check_items else set()
        ok = pre_count == post_count and pre_gate_fail == post_gate_fail and pre_keys == post_keys
        return {
            "status": "ok" if ok else "regression",
            "from": src_path.name,
            "to": dst_path.name,
            "pre_count": pre_count, "post_count": post_count,
            "pre_gate_fail": pre_gate_fail, "post_gate_fail": post_gate_fail,
            "regression_ok": ok,
        }

    src_type = source_cfg["type"]
    if src_type == "single_strand":
        r = _rename_one(corpus_dir / "criteria.json", corpus_dir / "rubrics.json")
        results.append(r)
    elif src_type == "multi_strand_unified":
        r = _rename_one(corpus_dir / "unified_criteria.json", corpus_dir / "unified_rubrics.json")
        results.append(r)
    elif src_type == "multi_strand_per_dir":
        r = _rename_one(corpus_dir / "unified_criteria.json", corpus_dir / "unified_rubrics.json")
        results.append(r)
        per_strand_root = corpus_dir / "per_strand"
        for s in source_cfg["strands"]:
            strand_dir = per_strand_root / s["slug"]
            r2 = _rename_one(strand_dir / "criteria.json", strand_dir / "rubrics.json")
            results.append(r2)

    return results


# ── LT-level prerequisite regeneration ────────────────────────────────────────

def regenerate_lt_prerequisites_4c4b(
    source_cfg: dict,
    corpus_dir: Path,
    criteria: list[dict],
) -> dict:
    """Aggregate criterion edges up to LT-level prerequisite_lts.
    Updates lts.json for single-strand and unified_lts.json for multi-strand.
    For per-dir multi-strand, also updates per-strand lts.json files.
    """
    crit_to_lts: dict[str, list[str]] = {c["criterion_id"]: c["associated_lt_ids"] for c in criteria}
    lt_prereqs: dict[str, set[str]] = {}
    lossy: list[dict] = []

    for c in criteria:
        for lt_id in c["associated_lt_ids"]:
            if lt_id not in lt_prereqs:
                lt_prereqs[lt_id] = set()
        for prereq_crit_id in c.get("prerequisite_criterion_ids", []):
            prereq_lts = crit_to_lts.get(prereq_crit_id, [])
            for lt_id in c["associated_lt_ids"]:
                for p_lt_id in prereq_lts:
                    if p_lt_id != lt_id:
                        lt_prereqs[lt_id].add(p_lt_id)
            if not prereq_lts:
                lossy.append({
                    "criterion_id": c["criterion_id"],
                    "prereq_criterion_id": prereq_crit_id,
                    "reason": "prerequisite criterion has no associated_lt_ids",
                })

    src_type = source_cfg["type"]
    lts_file = corpus_dir / source_cfg["lts_file"]

    def _update_lts_file(path: Path, prereq_map: dict[str, set[str]]) -> int:
        with open(path) as f:
            raw = json.load(f)
        lts_list = raw if isinstance(raw, list) else raw.get("learning_targets", raw.get("lts", []))
        changes = 0
        updated = []
        for lt in lts_list:
            lt_copy = dict(lt)
            new_prereqs = sorted(prereq_map.get(lt["lt_id"], set()))
            old_prereqs = lt.get("prerequisite_lts", [])
            if new_prereqs != old_prereqs:
                changes += 1
            lt_copy["prerequisite_lts"] = new_prereqs
            updated.append(lt_copy)
        if isinstance(raw, list):
            out = updated
        else:
            out = dict(raw)
            key = "learning_targets" if "learning_targets" in raw else "lts"
            out[key] = updated
        with open(path, "w") as f:
            json.dump(out, f, indent=2)
        return changes

    total_changes = _update_lts_file(lts_file, lt_prereqs)

    if src_type == "multi_strand_per_dir":
        # For per-dir sources, associated_lt_ids are prefixed with strand slug
        # (e.g. "history_cluster_01_lt_01"). Per-strand lts.json files use the
        # original unprefixed IDs. Build a strand-stripped prereq map per strand.
        per_strand_root = corpus_dir / "per_strand"
        for s in source_cfg["strands"]:
            slug = s["slug"]
            prefix = f"{slug}_"
            strand_prereqs: dict[str, set[str]] = {}
            for prefixed_lt_id, prereqs in lt_prereqs.items():
                if not prefixed_lt_id.startswith(prefix):
                    continue
                raw_lt_id = prefixed_lt_id[len(prefix):]
                stripped: set[str] = set()
                for p in prereqs:
                    if p.startswith(prefix):
                        stripped.add(p[len(prefix):])
                    # Cross-strand prereqs omitted — out of scope for v1.
                strand_prereqs[raw_lt_id] = stripped

            strand_lts_path = per_strand_root / slug / "lts.json"
            if strand_lts_path.exists():
                _update_lts_file(strand_lts_path, strand_prereqs)

    return {
        "lt_prereqs_updated": total_changes,
        "lossy_cases": lossy,
        "lt_prereq_summary": {lt_id: sorted(prereqs) for lt_id, prereqs in lt_prereqs.items() if prereqs},
    }


# ── Main generation ────────────────────────────────────────────────────────────

async def generate_criterion_bank_4c4b(
    source_slug: str,
    approve_horizontal: bool = False,
) -> dict:
    if source_slug not in SOURCES_4C4B:
        raise ValueError(f"Unknown source: {source_slug}. Valid: {list(SOURCES_4C4B)}")

    source_cfg = SOURCES_4C4B[source_slug]
    corpus_dir = CORPUS_ROOT / source_cfg["corpus_dir"]
    source_name = source_cfg["name"]
    src_type = source_cfg["type"]

    print(f"\n{'='*70}")
    print(f"Criterion Bank Generation (4c-4b): {source_slug}")
    print(f"Type: {src_type}")
    print(f"{'='*70}\n")

    # ── Load strand data ──────────────────────────────────────────────────────
    if src_type == "single_strand":
        strand_data = load_strand_data_single(source_cfg, corpus_dir)
    elif src_type == "multi_strand_unified":
        strand_data = load_strand_data_unified(source_cfg, corpus_dir)
    elif src_type == "multi_strand_per_dir":
        strand_data = load_strand_data_per_dir(source_cfg, corpus_dir)
    else:
        raise ValueError(f"Unknown source type: {src_type}")

    for slug, sd in strand_data.items():
        t12 = [lt for lt in sd["lts"] if lt.get("knowledge_type") in TYPE_1_2]
        print(f"  Strand {slug!r}: {len(sd['lts'])} LTs ({len(t12)} Type 1+2 eligible)")

    # ── Cost estimate ─────────────────────────────────────────────────────────
    n_pass2 = len(strand_data)
    est_cost = estimate_cost(strand_data, n_pass2)
    n_eligible = sum(
        len([lt for lt in sd["lts"] if lt.get("knowledge_type") in TYPE_1_2])
        for sd in strand_data.values()
    )
    print(f"\nCost estimate: ${est_cost:.2f} ({n_eligible} eligible LTs, {n_pass2} Pass 2 run(s))")
    if est_cost > 10.0:
        raise RuntimeError(
            f"Cost estimate ${est_cost:.2f} exceeds $10 ceiling — halting for review."
        )

    client = get_async_client()
    LEDGER.reset()

    # ── Per-strand generation ─────────────────────────────────────────────────
    all_criteria: list[dict] = []
    all_edges: list[dict] = []
    crit_counter = 1
    strand_summaries: list[dict] = []
    all_lts: list[dict] = []

    for slug, sd in strand_data.items():
        strand_name = sd["strand_name"]
        strand_slug_out = slug  # Use the directory slug as the strand value
        lts = sd["lts"]
        kud_items = sd["kud_items"]

        # For multi_strand_per_dir sources, LT IDs are not unique across strands
        # (each strand starts its own cluster_01_lt_01 etc.). Prefix with strand
        # slug to guarantee globally unique associated_lt_ids in the bank.
        if src_type == "multi_strand_per_dir":
            lt_id_prefix = f"{slug}_"
            # Build prefixed-ID LTs for all_lts (used for audit/spot-check)
            prefixed_lts = [{**lt, "lt_id": f"{lt_id_prefix}{lt['lt_id']}"} for lt in lts]
            all_lts.extend(prefixed_lts)
        else:
            lt_id_prefix = ""
            all_lts.extend(lts)

        type12_lts = [lt for lt in lts if lt.get("knowledge_type") in TYPE_1_2]

        if not type12_lts:
            print(f"\n--- Strand {slug!r}: no Type 1/2 LTs — skipping ---")
            strand_summaries.append({"strand": slug, "criteria_count": 0, "skipped": True})
            continue

        print(f"\n--- Pass 1: {slug!r} ({len(type12_lts)} Type 1/2 LTs) ---")
        raw_by_lt, failed = await generate_pass1_for_strand(slug, lts, kud_items, client)

        if not raw_by_lt:
            raise RuntimeError(f"Pass 1 produced no criteria for strand {slug!r} — aborting.")

        # Assign criterion IDs
        strand_criteria: list[dict] = []
        for lt in type12_lts:
            lt_id = lt["lt_id"]
            if lt_id not in raw_by_lt:
                continue
            for raw in raw_by_lt[lt_id]:
                crit_id = f"{source_slug}_crit_{crit_counter:04d}"
                strand_criteria.append({
                    "criterion_id": crit_id,
                    "associated_lt_ids": [f"{lt_id_prefix}{lt_id}"],
                    "strand": strand_slug_out,
                    "criterion_statement": raw["criterion_statement"],
                    "criterion_label": raw["criterion_label"],
                    "source_provenance": raw["source_kud_item_ids"],
                    "competency_level_descriptors": raw["competency_level_descriptors"],
                    "decomposition_rationale": raw["decomposition_rationale"],
                    "prerequisite_criterion_ids_raw": [],
                })
                crit_counter += 1

        print(f"  {len(strand_criteria)} criteria generated for strand {slug!r}")

        # ── Pass 2: prerequisite edges ──────────────────────────────────────
        print(f"\n--- Pass 2: {slug!r} ---")
        strand_edges = await generate_pass2_for_strand(
            strand_criteria, source_name, strand_name, client
        )
        print(f"  {len(strand_edges)} edges generated")

        # Attach edges
        edge_map: dict[str, list[str]] = {}
        for e in strand_edges:
            edge_map.setdefault(e["to_criterion_id"], []).append(e["from_criterion_id"])
        for c in strand_criteria:
            c["prerequisite_criterion_ids_raw"] = edge_map.get(c["criterion_id"], [])

        # ── DAG Validation ──────────────────────────────────────────────────
        print(f"\n--- DAG Validation: {slug!r} ---")
        dag_errors = run_dag_validation(strand_criteria, strand_edges)
        if dag_errors:
            print(f"DAG VALIDATION FAILED for {slug!r} — {len(dag_errors)} error(s):")
            for err in dag_errors:
                print(f"  [{err['type']}] {err['detail']}")
            raise RuntimeError(
                f"DAG validation failed for strand {slug!r} in {source_slug}. "
                "Halt: human review required."
            )
        print(f"  DAG validation passed (no cycles, self-loops, unresolved IDs, cross-strand edges)")

        strand_summaries.append({
            "strand": slug,
            "criteria_count": len(strand_criteria),
            "edge_count": len(strand_edges),
            "failed_lts": failed,
            "skipped": False,
        })
        all_criteria.extend(strand_criteria)
        all_edges.extend(strand_edges)

    if not all_criteria:
        raise RuntimeError("No criteria generated across all strands — aborting.")

    print(f"\nTotal criteria across all strands: {len(all_criteria)}")
    print(f"Total edges: {len(all_edges)}")

    # ── Over-generation Spot-Check ────────────────────────────────────────────
    print("\n--- Over-generation Spot-Check ---")
    spot = over_generation_spot_check(all_criteria)
    print(f"Sampled {spot['sample_size']} / {spot['total_criteria']} criteria")
    if spot["issues_found"]:
        print(f"Issues found ({spot['issues_found']}):")
        for iss in spot["issues"]:
            print(f"  {iss}")
    else:
        print("  No issues found")

    # ── Decomposition Audit ───────────────────────────────────────────────────
    print("\n--- Decomposition Audit ---")
    # Deduplicate all_lts for audit (per-dir strands may have separate lists)
    unique_lts = {lt["lt_id"]: lt for lt in all_lts}.values()
    audit = decomposition_audit(all_criteria, list(unique_lts))
    print(f"Audited {audit['lts_audited']} LTs")
    for row in audit["audit_rows"]:
        print(f"  {row['lt_id']} [{row['knowledge_type']}]: {row['criteria_count']} criteria")
    if audit["flags"]:
        print("Flags (possible over-decomposition or issues):")
        for f_ in audit["flags"]:
            print(f"  {f_}")
        # Enumerated-example check: if any flag suggests over-decomposition,
        # report it explicitly.
        overdecomp_flags = [f for f in audit["flags"] if "over-decomposition" in f]
        if overdecomp_flags:
            print("\nENUMERATED-EXAMPLE CHECK: Over-decomposition flags found above.")
            print("Verify each flagged LT does not have enumerated examples split into N criteria.")
    else:
        print("  No decomposition flags")

    # ── Hallucination / Scope Drift Check ─────────────────────────────────────
    print("\n--- Hallucination / Scope Drift Check ---")
    drift = scope_drift_check(all_criteria, list(unique_lts))
    print(f"Sampled {drift['sample_size']} criteria for scope-drift check")
    if drift["flags_found"]:
        print(f"Scope-drift flags ({drift['flags_found']}):")
        for flag in drift["flags"]:
            print(f"  {flag['criterion_id']}: {flag['issue']}")
            print(f"    Criterion: {flag['criterion_statement'][:100]}")
            print(f"    LT ({flag['lt_id']}): {flag['lt_name'][:80]}")
    else:
        print("  No scope-drift flags")

    # ── Horizontal Spot-Check (NZ SS only) ────────────────────────────────────
    if source_cfg.get("horizontal_spot_check"):
        if not approve_horizontal:
            print_horizontal_spot_check(all_criteria, list(unique_lts))
            sys.exit(0)  # Halt for operator review.
        else:
            print("\n--- Horizontal Spot-Check: APPROVED (--approve-horizontal) ---")

    # ── Build final criterion bank ────────────────────────────────────────────
    final_criteria = []
    for c in all_criteria:
        entry = {
            "criterion_id": c["criterion_id"],
            "associated_lt_ids": c["associated_lt_ids"],
            "strand": c["strand"],
            "criterion_statement": c["criterion_statement"],
            "criterion_label": c["criterion_label"],
            "source_provenance": c["source_provenance"],
            "competency_level_descriptors": c["competency_level_descriptors"],
            "prerequisite_criterion_ids": c["prerequisite_criterion_ids_raw"],
            "prerequisite_edges_detail": [
                e for e in all_edges if e["to_criterion_id"] == c["criterion_id"]
            ],
            "schema_version": SCHEMA_VERSION,
        }
        final_criteria.append(entry)

    # ── Token usage ───────────────────────────────────────────────────────────
    token_summary = LEDGER.to_dict()
    print(f"\nToken usage: {LEDGER.summary_line()}")

    # ── Write outputs ─────────────────────────────────────────────────────────
    criterion_bank = {
        "schema_version": SCHEMA_VERSION,
        "source_slug": source_slug,
        "source_name": source_name,
        "total_criteria": len(final_criteria),
        "strand_summaries": strand_summaries,
        "criteria": final_criteria,
    }
    bank_path = corpus_dir / "criterion_bank.json"
    with open(bank_path, "w") as f:
        json.dump(criterion_bank, f, indent=2)
    print(f"\nWrote {bank_path}")

    quality_report = {
        "source_slug": source_slug,
        "strand_summaries": strand_summaries,
        "dag_validation": {"passed": True, "errors": []},
        "over_generation_spot_check": spot,
        "decomposition_audit": audit,
        "scope_drift_check": drift,
        "token_usage": token_summary,
    }
    report_path = corpus_dir / "criterion_bank_quality_report.json"
    with open(report_path, "w") as f:
        json.dump(quality_report, f, indent=2)
    print(f"Wrote {report_path}")

    return quality_report


# ── Post-generation steps ──────────────────────────────────────────────────────

async def post_generation(source_slug: str, approve_horizontal: bool) -> None:
    source_cfg = SOURCES_4C4B[source_slug]
    corpus_dir = CORPUS_ROOT / source_cfg["corpus_dir"]

    print(f"\n{'='*70}")
    print(f"Post-generation: {source_slug}")
    print(f"{'='*70}")

    # Rename criteria → rubrics
    print("\n--- Rename criteria.json → rubrics.json ---")
    rename_results = rename_criteria_files(source_cfg, corpus_dir)
    for r in rename_results:
        status = r.get("status", "unknown")
        print(f"  {r.get('from', '?')} → {r.get('to', '?')}: {status}")
        if r.get("regression_ok") is False:
            print(f"    REGRESSION: pre_count={r.get('pre_count')}, post_count={r.get('post_count')}")
            raise RuntimeError(f"Rename regression detected for {source_slug}: {r}")

    # Regenerate LT-level prerequisites
    print("\n--- Regenerate LT-level prerequisite_lts ---")
    with open(corpus_dir / "criterion_bank.json") as f:
        bank = json.load(f)
    criteria = bank["criteria"]
    lt_regen = regenerate_lt_prerequisites_4c4b(source_cfg, corpus_dir, criteria)
    print(f"  LTs updated: {lt_regen['lt_prereqs_updated']}")
    if lt_regen["lossy_cases"]:
        print(f"  Lossy cases ({len(lt_regen['lossy_cases'])}):")
        for lc in lt_regen["lossy_cases"]:
            print(f"    {lc}")
    if lt_regen["lt_prereq_summary"]:
        print("  LT prerequisite summary:")
        for lt_id, prereqs in lt_regen["lt_prereq_summary"].items():
            print(f"    {lt_id}: {prereqs}")

    # Append to quality report
    report_path = corpus_dir / "criterion_bank_quality_report.json"
    with open(report_path) as f:
        qr = json.load(f)
    qr["rename_results"] = rename_results
    qr["lt_prerequisite_regeneration"] = lt_regen
    with open(report_path, "w") as f:
        json.dump(qr, f, indent=2)
    print(f"\nUpdated quality report: {report_path}")
    print(f"\n✓ {source_slug} complete")


# ── Entry point ────────────────────────────────────────────────────────────────

async def main_async(source_slug: str, approve_horizontal: bool) -> None:
    await generate_criterion_bank_4c4b(source_slug, approve_horizontal=approve_horizontal)
    await post_generation(source_slug, approve_horizontal=approve_horizontal)


def main() -> None:
    approve_horizontal = "--approve-horizontal" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(f"Usage: python {sys.argv[0]} <source_slug> [--approve-horizontal]")
        print(f"Valid: {list(SOURCES_4C4B)}")
        sys.exit(1)
    source_slug = args[0]
    asyncio.run(main_async(source_slug, approve_horizontal=approve_horizontal))


if __name__ == "__main__":
    main()
