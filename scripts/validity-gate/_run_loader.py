"""Helpers for validity-gate scripts that read a curriculum-harness
run directory.

A "run directory" is `outputs/<run>/` and contains some subset of:
  - `<runId>_curriculum_profile_v1.json` or `curriculum_profile_v1.json`
  - `<runId>_architecture_v1.json`          or `architecture_v1.json`
  - `<runId>_kud_v1.json`                   or `kud_v1.json`
  - `<runId>_learning_targets_v1.json`      or `learning_targets_v1.json`
  - `<runId>_source_bullets_v1.json`        or `source_bullets_v1.json`  (v3a+)

This module hides the runId-prefixed-vs-plain naming convention and
builds the source corpus that the three foundation-moment-1 gates
match against.

### Corpus selection — bullets preferred, proxy fallback

Since Session 3a (2026-04-18) Phase 1 emits a discrete
`_source_bullets_v1.json` artefact (topic statements / numbered
outcomes / marker bullets extracted from the Phase 1 scoped text).
Bullet-level granularity raises the matcher's precision sharply over
the Session-2 proxy corpus, which inflated orphan counts because it
only had strand-label-coarse items.

`load_run()` prefers the bullet artefact when present; falls back to
the proxy and sets `corpus_mode = "proxy"` with a warning when absent.

### When the proxy fallback kicks in — and why its baseline is unreliable

The proxy mode exists for backwards compatibility with runs predating
Session 3a that never emitted bullets. Its corpus is the pipeline's
own *English rendering* of the source:
`curriculum_profile.rationale`, strand labels + `values_basis`,
hierarchical / horizontal / dispositional element lists,
`structural_flaw`. For a Hungarian source (felvételi), this means
matching English LTs against the English re-rendering of a Hungarian
bullet list — an accidental dependency that systematically
under-scores. Any baseline taken in proxy mode is high-sensitivity /
low-precision and should not be compared against a baseline taken in
bullets mode.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceItem:
    """One item in the source-proxy corpus.

    `provenance` — where this item came from in the run dir, so reports
    can cite it. Examples: "architecture.strands[2].label",
    "curriculum_profile.rationale".
    """

    text: str
    provenance: str


@dataclass
class RunArtefacts:
    run_dir: Path
    curriculum_profile: dict | None
    architecture: dict | None
    learning_targets: list[dict]
    source_corpus: list[SourceItem]
    # "bullets" when built from `_source_bullets_v1.json`, "proxy" when
    # falling back to Phase 1/2 artefacts. Proxy-mode baselines are
    # unreliable (see module docstring).
    corpus_mode: str
    # Human-readable warning when corpus_mode is "proxy" or the bullet
    # artefact was found but empty. Empty string on happy path.
    corpus_warning: str


def _find_json(run_dir: Path, suffix: str) -> Path | None:
    """Find `<runId>_<suffix>` or plain `<suffix>` inside run_dir."""
    # Preferred: runId-prefixed filename.
    hits = sorted(run_dir.glob(f"*_{suffix}"))
    if hits:
        return hits[0]
    # Legacy: plain filename.
    plain = run_dir / suffix
    if plain.exists():
        return plain
    return None


def _load_json(path: Path | None) -> dict | None:
    if path is None:
        return None
    return json.loads(path.read_text())


def _build_source_corpus(
    profile: dict | None, architecture: dict | None
) -> list[SourceItem]:
    items: list[SourceItem] = []

    if profile:
        if rationale := profile.get("rationale"):
            items.append(
                SourceItem(rationale, "curriculum_profile.rationale")
            )
        hints = profile.get("source_hints") or {}
        if pages_note := hints.get("pages_note"):
            items.append(
                SourceItem(pages_note, "curriculum_profile.source_hints.pages_note")
            )
        assess = profile.get("assessment_signals") or {}
        if fmt := assess.get("format"):
            items.append(
                SourceItem(fmt, "curriculum_profile.assessment_signals.format")
            )

    if architecture:
        strands = architecture.get("strands") or []
        # v1.2+ shape: architecture.strands[] with label + values_basis.
        for i, strand in enumerate(strands):
            label = strand.get("label") or ""
            basis = strand.get("values_basis") or ""
            combined = (label + ". " + basis).strip(". ").strip()
            if combined:
                items.append(
                    SourceItem(combined, f"architecture.strands[{i}].label+values_basis")
                )
            # Strand IDs carry hyphen-separated content tokens
            # ("procedural-fluency-habits") that expand the lexical
            # coverage of the corpus without restating the label.
            sid = strand.get("id") or ""
            if sid:
                expanded = sid.replace("-", " ").replace("_", " ")
                items.append(
                    SourceItem(expanded, f"architecture.strands[{i}].id")
                )
        # Legacy element lists are only used when strands[] is absent
        # (pre-v1.2 runs). When strands[] exists, the element lists are
        # just the strand labels in another shape; adding them back
        # creates short label-only items that inflate false positives
        # on LTs sharing generic subject vocabulary.
        if not strands:
            for key in (
                "hierarchical_elements",
                "horizontal_elements",
                "dispositional_elements",
            ):
                for j, el in enumerate(architecture.get(key) or []):
                    if el:
                        items.append(SourceItem(el, f"architecture.{key}[{j}]"))
        # Structural flaw commentary carries subject-specific vocabulary
        # useful for faithfulness matching.
        if flaw := architecture.get("structural_flaw"):
            items.append(SourceItem(flaw, "architecture.structural_flaw"))

    return items


def _build_bullet_corpus(bullets_doc: dict) -> list[SourceItem]:
    """Lift `{source_bullets: [{id, text, ...}]}` into SourceItem rows.

    Each bullet becomes one corpus item; the bullet's `sb_NNN` id is
    folded into the provenance so gate output traces cleanly back to
    the bullet artefact.
    """
    items: list[SourceItem] = []
    for b in bullets_doc.get("source_bullets") or []:
        text = (b.get("text") or "").strip()
        bid = (b.get("id") or "").strip()
        # Session 3d — `bullet_type` is the semantic category; the
        # detector name moved to `detector`. Provenance surfaces the
        # semantic category so gate reports read cleanly.
        btype = (b.get("bullet_type") or "").strip()
        if not text or not bid:
            continue
        prov = f"source_bullets.{bid}"
        if btype:
            prov = f"{prov} ({btype})"
        items.append(SourceItem(text, prov))
    return items


def load_run(run_dir: str | Path) -> RunArtefacts:
    """Load a run's Phase 1/2/4 JSON and build the source corpus.

    Corpus selection:
    - If `_source_bullets_v1.json` is present and non-empty, the corpus
      is built from its bullets (`corpus_mode = "bullets"`).
    - Otherwise the Phase 1/2 proxy is used with a warning
      (`corpus_mode = "proxy"`) — see module docstring.

    Raises FileNotFoundError if `learning_targets` JSON is missing —
    gates cannot run without it.
    """
    run_dir = Path(run_dir)
    if not run_dir.is_dir():
        raise FileNotFoundError(f"run directory does not exist: {run_dir}")

    profile = _load_json(_find_json(run_dir, "curriculum_profile_v1.json"))
    architecture = _load_json(_find_json(run_dir, "architecture_v1.json"))
    lts_path = _find_json(run_dir, "learning_targets_v1.json")
    if lts_path is None:
        raise FileNotFoundError(
            f"no learning_targets_v1.json in {run_dir} — gate cannot run"
        )
    lts_doc = _load_json(lts_path) or {}
    lts = lts_doc.get("learning_targets") or []

    bullets_path = _find_json(run_dir, "source_bullets_v1.json")
    bullets_doc = _load_json(bullets_path) if bullets_path else None

    corpus_mode = "proxy"
    corpus_warning = ""
    if bullets_doc is not None:
        bullet_corpus = _build_bullet_corpus(bullets_doc)
        if bullet_corpus:
            source_corpus = bullet_corpus
            corpus_mode = "bullets"
        else:
            source_corpus = _build_source_corpus(profile, architecture)
            corpus_warning = (
                f"source_bullets artefact at {bullets_path} is empty; "
                "falling back to proxy corpus — baseline unreliable."
            )
    else:
        source_corpus = _build_source_corpus(profile, architecture)
        corpus_warning = (
            "no source_bullets_v1.json artefact in run dir; "
            "running on proxy corpus — baseline unreliable."
        )

    return RunArtefacts(
        run_dir=run_dir,
        curriculum_profile=profile,
        architecture=architecture,
        learning_targets=lts,
        source_corpus=source_corpus,
        corpus_mode=corpus_mode,
        corpus_warning=corpus_warning,
    )


__all__ = ["RunArtefacts", "SourceItem", "load_run"]
