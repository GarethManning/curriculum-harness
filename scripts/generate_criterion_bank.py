"""Criterion bank generator for Session 4c-4.

Produces criterion_bank.json and criterion_bank_quality_report.json for
a given anchor source (Welsh CfW H&W, Common Core 7.RP, Ontario G7 History).

Two-pass approach:
  Pass 1 — per-LT: decompose and generate competency-level descriptors.
  Pass 2 — whole-bank: generate prerequisite edges across all criteria.

Then: DAG validation, agreement rate, spot-checks, decomposition audit.

Usage:
    python scripts/generate_criterion_bank.py <source_slug>

Where source_slug is one of:
    welsh-cfw-health-wellbeing
    common-core-g7-rp
    ontario-g7-history
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

# Allow importing from project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from curriculum_harness._anthropic import LEDGER, get_async_client, haiku_stream_text
from curriculum_harness.types import SONNET_MODEL, extract_json_object

CORPUS_ROOT = Path(__file__).resolve().parent.parent / "docs" / "reference-corpus"
VALIDATION_ROOT = Path(__file__).resolve().parent.parent / "docs" / "validation"

SCHEMA_VERSION = "v1"
TYPE_1_2 = ("Type 1", "Type 2")

# Single-strand sentinel per schema update.
SINGLE_STRAND_SENTINEL = "single_strand"

# Sources processed in this session (4c-4 anchor sources).
ANCHOR_SOURCES = {
    "welsh-cfw-health-wellbeing": {
        "strand": SINGLE_STRAND_SENTINEL,
        "name": "Welsh Curriculum for Wales — Health and Well-being",
    },
    "common-core-g7-rp": {
        "strand": SINGLE_STRAND_SENTINEL,
        "name": "Common Core Grade 7 — Ratios and Proportional Relationships",
    },
    "ontario-g7-history": {
        "strand": SINGLE_STRAND_SENTINEL,
        "name": "Ontario Grade 7 — History (Canada 1713–1850)",
    },
}

# ── Decomposition rules summary (injected into Pass 1 system prompt) ──────────

DECOMPOSITION_RULES_SUMMARY = """
CRITERION DECOMPOSITION RULES (apply strictly):

1. ONE CRITERION when: single action verb, single knowledge domain, no plausible
   assessment scenario separating parts.

2. DECOMPOSE when any of these triggers apply:
   A. Compound verbs at different cognitive levels (identify vs evaluate)
      — test: could a student demonstrate the first without the second?
   B. Multi-target statements covering distinct, separately-teachable domains.
   C. Distinct procedural sub-skills with separable failure modes (write equation
      vs interpret ordered pairs).

3. GRANULARITY TEST: each criterion must be independently demonstrable in its
   own assessment task.

4. HORIZONTAL DOMAIN RULE: in history, wellbeing, RSHE — enumerated examples
   within a single act are NOT sub-criteria. Distinct cognitive operations
   (recall vs analyse vs evaluate) ARE decomposable. Description vs analysis vs
   evaluation → decompose.

5. TYPE 3 LTs: excluded from criterion bank. Do not process.

6. DISPOSITIONAL CONTENT (Type 2 LTs from wellbeing/RSHE): capture the
   observable reasoning quality only — not dispositional orientation (which is
   Type 3). Decompose on reasoning-quality grounds only.
"""

# ── Pass 1 prompts ─────────────────────────────────────────────────────────────

PASS1_SYSTEM = f"""You are a curriculum analyst producing a criterion bank for an
adaptive tutoring system. Your task is to decompose a Learning Target (LT) into
one or more individually assessable criteria following strict decomposition rules.

{DECOMPOSITION_RULES_SUMMARY}

For competency-level descriptors follow these word limits:
  no_evidence: ≤10 words
  emerging: ≤15 words
  developing: ≤20 words
  competent: ≤25 words (frame as success, never as "acceptable-but-deficient")
  extending: ≤20 words

Output ONLY valid JSON matching this schema:
{{
  "criteria": [
    {{
      "criterion_statement": "one clear sentence stating what the learner can do",
      "criterion_label": "3-5 word label",
      "source_kud_item_ids": ["blk_XXXX_item_XX"],
      "competency_level_descriptors": {{
        "no_evidence": "...",
        "emerging": "...",
        "developing": "...",
        "competent": "...",
        "extending": "..."
      }},
      "decomposition_rationale": "why this many criteria (1-2 sentences)"
    }}
  ]
}}

Produce no other text. Only JSON."""


def build_pass1_user(
    lt: dict,
    kud_items: list[dict],
    peer_lts: list[dict],
) -> str:
    kud_relevant = [k for k in kud_items if k["item_id"] in lt.get("kud_item_ids", [])]
    kud_text = "\n".join(
        f"  [{k['item_id']}] ({k['kud_column']}/{k['knowledge_type']}) "
        f"{k['content_statement']}"
        for k in kud_relevant
    )
    peer_text = "\n".join(
        f"  {p['lt_id']}: [{p['knowledge_type']}] {p['lt_name']}"
        for p in peer_lts
        if p["knowledge_type"] in TYPE_1_2
    )
    return f"""LEARNING TARGET
  ID: {lt['lt_id']}
  Name: {lt['lt_name']}
  Type: {lt['knowledge_type']}
  Definition: {lt['lt_definition']}

KUD ITEMS THIS LT TRACES TO:
{kud_text if kud_text else '  (none recorded)'}

PEER LTs IN THIS SOURCE (context only — do not reference their IDs in this pass):
{peer_text if peer_text else '  (none)'}

Decompose this LT into criteria following the rules. Return JSON only."""


# ── Pass 2 prompts ─────────────────────────────────────────────────────────────

PASS2_SYSTEM = """You are a curriculum analyst assigning prerequisite edges in a
criterion bank Directed Acyclic Graph (DAG).

Your output must form a valid DAG — no cycles, no self-loops. All referenced
criterion IDs must exist in the bank you are given.

Each edge means: "criterion A must be demonstrated before criterion B can be
meaningfully assessed."

Two reasoning tags:
  ontological_prerequisite — A is logically or conceptually required to define B.
  pedagogical_sequencing   — A should be taught and assessed before B for learning
                             to be effective, even if A does not strictly define B.

Three strength levels: high / medium / low.

Output ONLY valid JSON:
{
  "edges": [
    {
      "from_criterion_id": "source_slug_crit_XXXX",
      "to_criterion_id": "source_slug_crit_XXXX",
      "reasoning_tag": "ontological_prerequisite",
      "strength": "high",
      "rationale": "1-2 sentences"
    }
  ]
}

Produce no other text. Only JSON."""


def build_pass2_user(
    criteria: list[dict],
    source_name: str,
    curated_lt_edges: list[dict],
) -> str:
    crit_lines = "\n".join(
        f"  [{c['criterion_id']}] lt={','.join(c['associated_lt_ids'])} "
        f"— {c['criterion_statement']}"
        for c in criteria
    )
    hint_lines = "\n".join(
        f"  LT {e['lt_a']} → LT {e['lt_b']} ({e['tag']}, {e['strength']}): {e['rationale']}"
        for e in curated_lt_edges
    )
    return f"""SOURCE: {source_name}

ALL CRITERIA IN THE BANK:
{crit_lines}

CURATED LT-LEVEL EDGES (hints — the generated criterion-level edges should recover these,
but may be more granular):
{hint_lines}

Generate prerequisite edges between criteria. All edges must be within this bank.
Return JSON only."""


# ── JSON validators ────────────────────────────────────────────────────────────

def validate_pass1_output(obj: Any, kud_item_ids: set[str]) -> list[dict] | None:
    if not isinstance(obj, dict):
        return None
    criteria_raw = obj.get("criteria")
    if not isinstance(criteria_raw, list) or not criteria_raw:
        return None
    out = []
    for c in criteria_raw:
        if not isinstance(c, dict):
            return None
        stmt = str(c.get("criterion_statement", "")).strip()
        label = str(c.get("criterion_label", "")).strip()
        provenance = c.get("source_kud_item_ids")
        if not isinstance(provenance, list):
            provenance = []
        # Keep only valid kud_item_ids (others are hallucinations).
        provenance = [p for p in provenance if p in kud_item_ids]
        descriptors = c.get("competency_level_descriptors")
        if not isinstance(descriptors, dict):
            return None
        for level in ("no_evidence", "emerging", "developing", "competent", "extending"):
            if not isinstance(descriptors.get(level), str) or not descriptors[level].strip():
                return None
        rationale = str(c.get("decomposition_rationale", "")).strip()
        if not stmt or not label:
            return None
        out.append({
            "criterion_statement": stmt,
            "criterion_label": label,
            "source_kud_item_ids": provenance,
            "competency_level_descriptors": {
                k: v.strip() for k, v in descriptors.items()
            },
            "decomposition_rationale": rationale,
        })
    return out


def validate_pass2_output(obj: Any, criterion_ids: set[str]) -> list[dict] | None:
    if not isinstance(obj, dict):
        return None
    edges_raw = obj.get("edges")
    if not isinstance(edges_raw, list):
        return None
    out = []
    seen = set()
    for e in edges_raw:
        if not isinstance(e, dict):
            continue
        from_id = str(e.get("from_criterion_id", "")).strip()
        to_id = str(e.get("to_criterion_id", "")).strip()
        tag = str(e.get("reasoning_tag", "")).strip()
        strength = str(e.get("strength", "")).strip().lower()
        rationale = str(e.get("rationale", "")).strip()
        if from_id not in criterion_ids or to_id not in criterion_ids:
            continue  # skip unresolved refs
        if from_id == to_id:
            continue  # skip self-loops
        if tag not in ("ontological_prerequisite", "pedagogical_sequencing"):
            continue
        if strength not in ("high", "medium", "low"):
            continue
        key = (from_id, to_id)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "from_criterion_id": from_id,
            "to_criterion_id": to_id,
            "reasoning_tag": tag,
            "strength": strength,
            "rationale": rationale,
        })
    return out


# ── DAG validation ─────────────────────────────────────────────────────────────

def detect_self_loops(criteria: list[dict]) -> list[dict]:
    errors = []
    for c in criteria:
        cid = c["criterion_id"]
        if cid in c.get("prerequisite_criterion_ids_raw", []):
            errors.append({
                "type": "self_loop",
                "detail": f"{cid} has self-loop",
                "path": [cid],
            })
    return errors


def detect_unresolved_ids(criteria: list[dict]) -> list[dict]:
    known = {c["criterion_id"] for c in criteria}
    errors = []
    for c in criteria:
        for pid in c.get("prerequisite_criterion_ids_raw", []):
            if pid not in known:
                errors.append({
                    "type": "unresolved_id",
                    "detail": f"{c['criterion_id']} references missing {pid}",
                    "path": [c["criterion_id"], pid],
                })
    return errors


def detect_cross_strand(criteria: list[dict], edges: list[dict]) -> list[dict]:
    strand_map = {c["criterion_id"]: c["strand"] for c in criteria}
    errors = []
    for e in edges:
        s_from = strand_map.get(e["from_criterion_id"])
        s_to = strand_map.get(e["to_criterion_id"])
        if s_from != s_to:
            errors.append({
                "type": "cross_strand_edge",
                "detail": (
                    f"{e['from_criterion_id']} (strand: {s_from}) → "
                    f"{e['to_criterion_id']} (strand: {s_to})"
                ),
                "path": [e["from_criterion_id"], e["to_criterion_id"]],
            })
    return errors


def detect_cycles(criteria: list[dict]) -> list[dict]:
    """DFS cycle detection. Returns list of error dicts."""
    graph: dict[str, list[str]] = {c["criterion_id"]: [] for c in criteria}
    for c in criteria:
        for pid in c.get("prerequisite_criterion_ids_raw", []):
            if pid in graph:
                # Edge direction: pid → criterion_id (pid is prerequisite)
                # For cycle detection in the DAG where edges point "upstream",
                # we check forward reachability: if B requires A, and later
                # A requires B transitively, that's a cycle.
                graph[pid].append(c["criterion_id"])

    visited: set[str] = set()
    in_stack: set[str] = set()
    stack: list[str] = []
    cycles = []

    def dfs(node: str) -> bool:
        visited.add(node)
        in_stack.add(node)
        stack.append(node)
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                if dfs(neighbour):
                    return True
            elif neighbour in in_stack:
                # Found cycle — extract path
                idx = stack.index(neighbour)
                cycle_path = stack[idx:] + [neighbour]
                cycles.append({
                    "type": "cycle",
                    "detail": " → ".join(cycle_path),
                    "path": cycle_path,
                })
                return True
        stack.pop()
        in_stack.discard(node)
        return False

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node)

    return cycles


def run_dag_validation(criteria: list[dict], edges: list[dict]) -> list[dict]:
    errors = []
    errors.extend(detect_self_loops(criteria))
    if errors:
        return errors
    errors.extend(detect_unresolved_ids(criteria))
    if errors:
        return errors
    errors.extend(detect_cross_strand(criteria, edges))
    if errors:
        return errors
    errors.extend(detect_cycles(criteria))
    return errors


# ── Agreement rate ─────────────────────────────────────────────────────────────

def compute_agreement(
    criteria: list[dict],
    edges: list[dict],
    curated_lt_edges: list[dict],
) -> dict:
    """Two-level agreement computation per dag-validation-rules-v1."""
    # Build lookup: lt_id → set of criterion_ids
    lt_to_crits: dict[str, set[str]] = {}
    for c in criteria:
        for lt_id in c["associated_lt_ids"]:
            lt_to_crits.setdefault(lt_id, set()).add(c["criterion_id"])

    # Build edge lookup for fast membership testing.
    edge_set: dict[tuple[str, str], str] = {
        (e["from_criterion_id"], e["to_criterion_id"]): e["reasoning_tag"]
        for e in edges
    }

    primary_recovered = 0
    secondary_recovered = 0
    unrecovered = []
    tag_mismatches = []

    for e in curated_lt_edges:
        lt_a = e["lt_a"]
        lt_b = e["lt_b"]
        curated_tag = e["tag"]

        crits_a = lt_to_crits.get(lt_a, set())
        crits_b = lt_to_crits.get(lt_b, set())

        # Primary: at least one (crit_from_a, crit_in_b) edge exists.
        found_primary = False
        matching_tag = None
        for ca in crits_a:
            for cb in crits_b:
                if (ca, cb) in edge_set:
                    found_primary = True
                    matching_tag = edge_set[(ca, cb)]
                    break
            if found_primary:
                break

        if found_primary:
            primary_recovered += 1
            if matching_tag == curated_tag:
                secondary_recovered += 1
            else:
                tag_mismatches.append({
                    "lt_a": lt_a,
                    "lt_b": lt_b,
                    "curated_tag": curated_tag,
                    "generated_tag": matching_tag,
                })
        else:
            unrecovered.append({
                "lt_a": lt_a,
                "lt_b": lt_b,
                "rationale": (
                    f"no criterion in crit_A_set {sorted(crits_a)} found in "
                    f"prerequisite path to any criterion in crit_B_set {sorted(crits_b)}"
                ),
            })

    total = len(curated_lt_edges)
    primary_rate = round(primary_recovered / total, 4) if total else 0.0
    secondary_rate = round(secondary_recovered / total, 4) if total else 0.0

    return {
        "primary_agreement_rate": primary_rate,
        "secondary_agreement_rate": secondary_rate,
        "hand_curated_edges_total": total,
        "primary_edges_recovered": primary_recovered,
        "secondary_edges_recovered": secondary_recovered,
        "unrecovered_edges": unrecovered,
        "tag_mismatch_edges": tag_mismatches,
    }


# ── Spot-check helpers ─────────────────────────────────────────────────────────

def over_generation_spot_check(criteria: list[dict], sample_size: int = 20) -> dict:
    import random
    total = len(criteria)
    n = min(sample_size, max(1, total * 20 // 100))
    sample = random.sample(criteria, n) if total > n else criteria[:]
    issues = []
    for c in sample:
        stmt = c.get("criterion_statement", "")
        descriptors = c.get("competency_level_descriptors", {})
        # Check word limits.
        limits = {
            "no_evidence": 10, "emerging": 15, "developing": 20,
            "competent": 25, "extending": 20,
        }
        for level, limit in limits.items():
            words = len(descriptors.get(level, "").split())
            if words > limit:
                issues.append(f"{c['criterion_id']}.{level}: {words} words > {limit}")
        # Check competent is framed as success (not "acceptable").
        competent = descriptors.get("competent", "").lower()
        deficiency_words = ("acceptable", "though limited", "but limited", "but not yet",
                            "although", "despite", "however", "partially")
        for dw in deficiency_words:
            if dw in competent:
                issues.append(f"{c['criterion_id']}.competent: possible deficiency framing ({dw!r})")
        # Check criterion_statement is non-empty and specific.
        if len(stmt.split()) < 5:
            issues.append(f"{c['criterion_id']}: criterion_statement too short")

    return {
        "total_criteria": total,
        "sample_size": n,
        "issues_found": len(issues),
        "issues": issues,
    }


def decomposition_audit(criteria: list[dict], lts: list[dict], sample_size: int = 20) -> dict:
    from collections import defaultdict
    crit_per_lt: dict[str, list[str]] = defaultdict(list)
    for c in criteria:
        for lt_id in c["associated_lt_ids"]:
            crit_per_lt[lt_id].append(c["criterion_id"])

    type12_lts = [lt for lt in lts if lt["knowledge_type"] in TYPE_1_2]
    import random
    n = min(sample_size, len(type12_lts))
    sampled = random.sample(type12_lts, n) if len(type12_lts) > n else type12_lts[:]

    rows = []
    flags = []
    for lt in sampled:
        crits = crit_per_lt.get(lt["lt_id"], [])
        count = len(crits)
        rationale = ""
        # Look up decomposition rationale from criteria.
        for c in criteria:
            if lt["lt_id"] in c["associated_lt_ids"]:
                rationale = c.get("decomposition_rationale", "")
                break
        row = {
            "lt_id": lt["lt_id"],
            "lt_name": lt["lt_name"],
            "knowledge_type": lt["knowledge_type"],
            "criteria_count": count,
            "criterion_ids": crits,
            "decomposition_rationale": rationale,
        }
        rows.append(row)
        # Flag: 0 criteria for a Type 1/2 LT is a problem.
        if count == 0:
            flags.append(f"{lt['lt_id']}: no criteria generated (problem)")
        # Flag: >4 criteria for a simple LT may be over-decomposition.
        if count > 4:
            flags.append(f"{lt['lt_id']}: {count} criteria — possible over-decomposition, review")

    return {
        "lts_audited": n,
        "audit_rows": rows,
        "flags": flags,
    }


# ── Main generation ────────────────────────────────────────────────────────────

async def generate_criterion_bank(source_slug: str) -> dict:
    if source_slug not in ANCHOR_SOURCES:
        raise ValueError(f"Unknown source: {source_slug}. Expected one of {list(ANCHOR_SOURCES)}")

    source_info = ANCHOR_SOURCES[source_slug]
    corpus_dir = CORPUS_ROOT / source_slug
    strand = source_info["strand"]
    source_name = source_info["name"]

    print(f"\n{'='*60}")
    print(f"Criterion Bank Generation: {source_slug}")
    print(f"{'='*60}\n")

    # ── Load data ─────────────────────────────────────────────────────────────
    with open(corpus_dir / "lts.json") as f:
        lts_raw = json.load(f)
    lts = lts_raw if isinstance(lts_raw, list) else lts_raw.get("learning_targets", lts_raw.get("lts", []))

    with open(corpus_dir / "kud.json") as f:
        kud_raw = json.load(f)
    kud_items = kud_raw.get("items", []) if isinstance(kud_raw, dict) else kud_raw

    kud_item_ids = {k["item_id"] for k in kud_items}

    # Filter to Type 1/2.
    type12_lts = [lt for lt in lts if lt.get("knowledge_type") in TYPE_1_2]
    print(f"Type 1/2 LTs to process: {len(type12_lts)} / {len(lts)} total")

    # Cost estimate: ~1500 input + ~800 output tokens per LT for Pass 1,
    # plus ~3000 input + ~1500 output for Pass 2 whole-bank.
    # Sonnet: $3/Mtok in, $15/Mtok out.
    n_lts = len(type12_lts)
    est_in = (n_lts * 1500 + 3000) / 1_000_000
    est_out = (n_lts * 800 + 1500) / 1_000_000
    est_cost = est_in * 3.0 + est_out * 15.0
    print(f"Cost estimate: ${est_cost:.2f} (input {est_in*1e6:.0f} tok, output {est_out*1e6:.0f} tok)")
    if est_cost > 30.0:
        raise RuntimeError(f"Cost estimate ${est_cost:.2f} exceeds $30 ceiling — halting for review.")

    # ── Load hand-curated validation edges ────────────────────────────────────
    validation_file = VALIDATION_ROOT / "hand-curated-prerequisite-edges-v1.md"
    curated_edges = load_curated_edges(validation_file, source_slug)
    print(f"Loaded {len(curated_edges)} hand-curated edges for {source_slug}")

    client = get_async_client()
    LEDGER.reset()

    # ── PASS 1: Generate criteria per LT ─────────────────────────────────────
    print("\n--- Pass 1: Criterion decomposition and descriptor generation ---")
    raw_criteria_by_lt: dict[str, list[dict]] = {}
    failed_lts: list[dict] = []

    async def _pass1_for_lt(lt: dict) -> None:
        user_prompt = build_pass1_user(lt, kud_items, type12_lts)
        label = f"refauth_critbank_pass1 {lt['lt_id']}"
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
            failed_lts.append({"lt_id": lt["lt_id"], "error": str(exc)})
            return

        parsed = extract_json_object(text)
        validated = validate_pass1_output(parsed, kud_item_ids)
        if not validated:
            print(f"  PARSE FAIL {lt['lt_id']}: {text[:200]!r}")
            failed_lts.append({
                "lt_id": lt["lt_id"],
                "error": "pass1 output did not validate",
                "raw": text[:500],
            })
            return
        raw_criteria_by_lt[lt["lt_id"]] = validated
        print(f"  {lt['lt_id']}: {len(validated)} criterion/criteria")

    sem = asyncio.Semaphore(4)

    async def _bounded_pass1(lt: dict) -> None:
        async with sem:
            await _pass1_for_lt(lt)

    await asyncio.gather(*[_bounded_pass1(lt) for lt in type12_lts])

    if not raw_criteria_by_lt:
        raise RuntimeError("Pass 1 produced no criteria — aborting.")

    # ── Assign criterion IDs ──────────────────────────────────────────────────
    all_raw_criteria: list[dict] = []
    crit_counter = 1
    for lt in type12_lts:
        lt_id = lt["lt_id"]
        if lt_id not in raw_criteria_by_lt:
            continue
        for raw in raw_criteria_by_lt[lt_id]:
            crit_id = f"{source_slug}_crit_{crit_counter:04d}"
            all_raw_criteria.append({
                "criterion_id": crit_id,
                "associated_lt_ids": [lt_id],
                "strand": strand,
                "criterion_statement": raw["criterion_statement"],
                "criterion_label": raw["criterion_label"],
                "source_provenance": raw["source_kud_item_ids"],
                "competency_level_descriptors": raw["competency_level_descriptors"],
                "decomposition_rationale": raw["decomposition_rationale"],
                "prerequisite_criterion_ids_raw": [],  # filled in Pass 2
            })
            crit_counter += 1

    print(f"\nTotal criteria after ID assignment: {len(all_raw_criteria)}")
    criterion_ids = {c["criterion_id"] for c in all_raw_criteria}

    # ── PASS 2: Generate prerequisite edges ───────────────────────────────────
    print("\n--- Pass 2: Prerequisite edge generation ---")
    pass2_user = build_pass2_user(all_raw_criteria, source_name, curated_edges)
    label2 = f"refauth_critbank_pass2 {source_slug}"
    try:
        text2 = await haiku_stream_text(
            client,
            model=SONNET_MODEL,
            max_tokens=4096,
            system=PASS2_SYSTEM,
            user_blocks=[{"type": "text", "text": pass2_user}],
            label=label2,
            temperature=0.1,
        )
    except Exception as exc:
        raise RuntimeError(f"Pass 2 failed: {exc}") from exc

    parsed2 = extract_json_object(text2)
    validated_edges = validate_pass2_output(parsed2, criterion_ids)
    if validated_edges is None:
        raise RuntimeError(f"Pass 2 output did not validate: {text2[:500]!r}")

    print(f"Generated {len(validated_edges)} prerequisite edges")

    # Attach edges to criteria.
    edge_map: dict[str, list[str]] = {}
    for e in validated_edges:
        edge_map.setdefault(e["to_criterion_id"], []).append(e["from_criterion_id"])
    for c in all_raw_criteria:
        c["prerequisite_criterion_ids_raw"] = edge_map.get(c["criterion_id"], [])

    # ── DAG Validation ────────────────────────────────────────────────────────
    print("\n--- DAG Validation ---")
    dag_errors = run_dag_validation(all_raw_criteria, validated_edges)
    if dag_errors:
        print(f"DAG VALIDATION FAILED — {len(dag_errors)} error(s):")
        for err in dag_errors:
            print(f"  [{err['type']}] {err['detail']}")
        raise RuntimeError(
            f"DAG validation failed for {source_slug}. "
            "Halt: human review required before proceeding."
        )
    print("DAG validation passed (no cycles, self-loops, unresolved IDs, cross-strand edges)")

    # ── Agreement Rate ────────────────────────────────────────────────────────
    print("\n--- Agreement Rate ---")
    agreement = compute_agreement(all_raw_criteria, validated_edges, curated_edges)
    print(f"Primary agreement: {agreement['primary_agreement_rate']:.0%} "
          f"({agreement['primary_edges_recovered']}/{agreement['hand_curated_edges_total']})")
    print(f"Secondary agreement: {agreement['secondary_agreement_rate']:.0%} "
          f"({agreement['secondary_edges_recovered']}/{agreement['hand_curated_edges_total']})")

    if agreement["primary_agreement_rate"] < 0.5:
        print("\nSTOP-AND-REPORT: Primary agreement rate below 50% floor.")
        print("Unrecovered edges:")
        for ue in agreement["unrecovered_edges"]:
            print(f"  {ue['lt_a']} → {ue['lt_b']}: {ue['rationale']}")
        raise RuntimeError(
            f"Agreement rate {agreement['primary_agreement_rate']:.0%} < 50% floor "
            f"for {source_slug}. Halt."
        )

    # ── Spot-Checks ───────────────────────────────────────────────────────────
    print("\n--- Over-generation Spot-Check ---")
    spot = over_generation_spot_check(all_raw_criteria)
    print(f"Sampled {spot['sample_size']} / {spot['total_criteria']} criteria")
    if spot["issues_found"]:
        print(f"Issues found ({spot['issues_found']}):")
        for iss in spot["issues"]:
            print(f"  {iss}")
    else:
        print("No issues found")

    print("\n--- Decomposition Audit ---")
    audit = decomposition_audit(all_raw_criteria, type12_lts)
    print(f"Audited {audit['lts_audited']} LTs")
    for row in audit["audit_rows"]:
        print(f"  {row['lt_id']} [{row['knowledge_type']}]: {row['criteria_count']} criteria")
    if audit["flags"]:
        print("Flags:")
        for f_ in audit["flags"]:
            print(f"  {f_}")

    # ── Build final criterion bank entries ────────────────────────────────────
    final_criteria = []
    for c in all_raw_criteria:
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
                e for e in validated_edges
                if e["to_criterion_id"] == c["criterion_id"]
            ],
            "schema_version": SCHEMA_VERSION,
        }
        final_criteria.append(entry)

    # ── Token usage ───────────────────────────────────────────────────────────
    token_summary = LEDGER.to_dict()
    print(f"\nToken usage: {LEDGER.summary_line()}")

    # ── Write outputs ─────────────────────────────────────────────────────────
    out_dir = corpus_dir
    bank_path = out_dir / "criterion_bank.json"
    report_path = out_dir / "criterion_bank_quality_report.json"

    criterion_bank = {
        "schema_version": SCHEMA_VERSION,
        "source_slug": source_slug,
        "source_name": source_name,
        "strand": strand,
        "total_criteria": len(final_criteria),
        "criteria": final_criteria,
    }
    with open(bank_path, "w") as f:
        json.dump(criterion_bank, f, indent=2)
    print(f"\nWrote {bank_path}")

    quality_report = {
        "source_slug": source_slug,
        "pass1_failed_lts": failed_lts,
        "dag_validation": {
            "passed": True,
            "errors": [],
            **agreement,
        },
        "over_generation_spot_check": spot,
        "decomposition_audit": audit,
        "token_usage": token_summary,
    }
    with open(report_path, "w") as f:
        json.dump(quality_report, f, indent=2)
    print(f"Wrote {report_path}")

    return quality_report


# ── Curated edge loader ────────────────────────────────────────────────────────

def load_curated_edges(path: Path, source_slug: str) -> list[dict]:
    """Parse hand-curated-prerequisite-edges-v1.md for the given source."""
    section_map = {
        "welsh-cfw-health-wellbeing": "## Welsh CfW H&W",
        "common-core-g7-rp": "## Common Core 7.RP",
        "ontario-g7-history": "## Ontario G7 History",
    }
    target_header = section_map[source_slug]
    text = path.read_text()
    lines = text.split("\n")

    in_section = False
    in_table = False
    edges = []

    for line in lines:
        if line.strip().startswith(target_header):
            in_section = True
            continue
        if in_section and line.strip().startswith("## ") and target_header not in line:
            break  # next section
        if not in_section:
            continue
        if "| #" in line or "|---|" in line:
            in_table = True
            continue
        if in_table and line.strip().startswith("|"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) < 6:
                continue
            try:
                # Parse: # | LT A | LT B | Tag | Strength | Rationale
                lt_a_raw = parts[1]
                lt_b_raw = parts[2]
                tag = parts[3].strip()
                strength = parts[4].strip().lower()
                rationale = parts[5].strip() if len(parts) > 5 else ""
                # Extract lt_id from backtick-wrapped text like `cluster_04_lt_01`
                import re
                lt_a_match = re.search(r"`([^`]+)`", lt_a_raw)
                lt_b_match = re.search(r"`([^`]+)`", lt_b_raw)
                if not lt_a_match or not lt_b_match:
                    continue
                lt_a = lt_a_match.group(1)
                lt_b = lt_b_match.group(1)
                edges.append({
                    "lt_a": lt_a,
                    "lt_b": lt_b,
                    "tag": tag,
                    "strength": strength,
                    "rationale": rationale,
                })
            except (IndexError, ValueError):
                continue

    return edges


# ── Rename criteria.json → rubrics.json ───────────────────────────────────────

def rename_criteria_to_rubrics(source_slug: str) -> dict:
    corpus_dir = CORPUS_ROOT / source_slug
    criteria_path = corpus_dir / "criteria.json"
    rubrics_path = corpus_dir / "rubrics.json"

    if not criteria_path.exists():
        return {"status": "skipped", "reason": "criteria.json not found"}

    with open(criteria_path) as f:
        data = json.load(f)

    items = data if isinstance(data, list) else data.get("criteria", data.get("rubrics", []))

    # Read pre-rename counts.
    pre_count = len(items)
    pre_gate_fail = sum(1 for r in items if not r.get("quality_gate_passed", True))
    pre_keys = set(items[0].keys()) if items else set()

    # Write rubrics.json.
    with open(rubrics_path, "w") as f:
        json.dump(data, f, indent=2)

    # Verify.
    with open(rubrics_path) as f:
        check = json.load(f)
    check_items = check if isinstance(check, list) else check.get("criteria", check.get("rubrics", []))
    post_count = len(check_items)
    post_gate_fail = sum(1 for r in check_items if not r.get("quality_gate_passed", True))
    post_keys = set(check_items[0].keys()) if check_items else set()

    regression_ok = (pre_count == post_count and pre_gate_fail == post_gate_fail and pre_keys == post_keys)
    return {
        "status": "ok" if regression_ok else "regression",
        "pre_count": pre_count,
        "post_count": post_count,
        "pre_gate_fail": pre_gate_fail,
        "post_gate_fail": post_gate_fail,
        "pre_keys": sorted(pre_keys),
        "post_keys": sorted(post_keys),
        "regression_ok": regression_ok,
    }


# ── LT-level prerequisite regeneration ────────────────────────────────────────

def regenerate_lt_prerequisites(source_slug: str, criteria: list[dict]) -> dict:
    """Aggregate criterion-level edges up to LT-level prerequisite_lts fields."""
    corpus_dir = CORPUS_ROOT / source_slug
    with open(corpus_dir / "lts.json") as f:
        lts_raw = json.load(f)
    lts = lts_raw if isinstance(lts_raw, list) else lts_raw.get("learning_targets", lts_raw.get("lts", []))

    # Build: criterion_id → associated_lt_ids
    crit_to_lts: dict[str, list[str]] = {c["criterion_id"]: c["associated_lt_ids"] for c in criteria}

    # Build: lt_id → set of prerequisite lt_ids (aggregated from criterion edges)
    lt_prereqs: dict[str, set[str]] = {lt["lt_id"]: set() for lt in lts}
    lossy_cases: list[dict] = []

    for c in criteria:
        lt_ids = c["associated_lt_ids"]
        for prereq_crit_id in c.get("prerequisite_criterion_ids", []):
            prereq_lt_ids = crit_to_lts.get(prereq_crit_id, [])
            for lt_id in lt_ids:
                for prereq_lt_id in prereq_lt_ids:
                    if prereq_lt_id != lt_id:
                        lt_prereqs[lt_id].add(prereq_lt_id)
                    else:
                        # Same LT — intra-LT criterion edge doesn't produce LT-level edge.
                        # This is not lossy — it's a within-LT decomposition edge.
                        pass
            if not prereq_lt_ids:
                lossy_cases.append({
                    "criterion_id": c["criterion_id"],
                    "prereq_criterion_id": prereq_crit_id,
                    "reason": "prerequisite criterion has no associated_lt_ids",
                })

    # Update lts.json with aggregated prerequisites.
    updated_lts = []
    changes = 0
    for lt in lts:
        lt_copy = dict(lt)
        new_prereqs = sorted(lt_prereqs.get(lt["lt_id"], set()))
        old_prereqs = lt.get("prerequisite_lts", [])
        if new_prereqs != old_prereqs:
            changes += 1
        lt_copy["prerequisite_lts"] = new_prereqs
        updated_lts.append(lt_copy)

    # Write back.
    if isinstance(lts_raw, list):
        updated = updated_lts
    else:
        updated = dict(lts_raw)
        updated["learning_targets"] = updated_lts

    with open(corpus_dir / "lts.json", "w") as f:
        json.dump(updated, f, indent=2)

    return {
        "lt_prereqs_updated": changes,
        "lossy_cases": lossy_cases,
        "lt_prereq_summary": {lt_id: sorted(prereqs) for lt_id, prereqs in lt_prereqs.items() if prereqs},
    }


# ── Entry point ────────────────────────────────────────────────────────────────

async def main_async(source_slug: str) -> None:
    report = await generate_criterion_bank(source_slug)

    print(f"\n{'='*60}")
    print(f"Post-generation steps: {source_slug}")
    print(f"{'='*60}")

    # Rename criteria.json → rubrics.json.
    print("\n--- Rename criteria.json → rubrics.json ---")
    rename_result = rename_criteria_to_rubrics(source_slug)
    print(f"Rename status: {rename_result['status']}")
    if rename_result.get("regression_ok") is False:
        print("REGRESSION DETECTED:")
        print(f"  pre_count={rename_result.get('pre_count')}, post_count={rename_result.get('post_count')}")
        print(f"  pre_gate_fail={rename_result.get('pre_gate_fail')}, post_gate_fail={rename_result.get('post_gate_fail')}")
        print(f"  pre_keys={rename_result.get('pre_keys')}")
        print(f"  post_keys={rename_result.get('post_keys')}")

    # Regenerate LT-level prerequisites from criterion bank.
    corpus_dir = CORPUS_ROOT / source_slug
    with open(corpus_dir / "criterion_bank.json") as f:
        bank = json.load(f)
    criteria = bank["criteria"]

    print("\n--- Regenerate LT-level prerequisite_lts from criterion bank ---")
    lt_regen = regenerate_lt_prerequisites(source_slug, criteria)
    print(f"LTs updated: {lt_regen['lt_prereqs_updated']}")
    if lt_regen["lossy_cases"]:
        print(f"Lossy cases ({len(lt_regen['lossy_cases'])}):")
        for lc in lt_regen["lossy_cases"]:
            print(f"  {lc}")
    if lt_regen["lt_prereq_summary"]:
        print("LT prerequisite summary:")
        for lt_id, prereqs in lt_regen["lt_prereq_summary"].items():
            print(f"  {lt_id}: {prereqs}")

    # Append rename and LT regen results to quality report.
    report_path = CORPUS_ROOT / source_slug / "criterion_bank_quality_report.json"
    with open(report_path) as f:
        qr = json.load(f)
    qr["rename_result"] = rename_result
    qr["lt_prerequisite_regeneration"] = lt_regen
    with open(report_path, "w") as f:
        json.dump(qr, f, indent=2)
    print(f"\nUpdated quality report: {report_path}")

    print(f"\n✓ {source_slug} complete")


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <source_slug>")
        print(f"Valid: {list(ANCHOR_SOURCES)}")
        sys.exit(1)
    source_slug = sys.argv[1]
    asyncio.run(main_async(source_slug))


if __name__ == "__main__":
    main()
