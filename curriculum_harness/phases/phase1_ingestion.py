"""Phase 1 — fetch curriculum document, extract text (Haiku-assisted metadata + scope)."""

from __future__ import annotations

import html as html_stdlib
import io
import re
from typing import Any

import httpx
from pypdf import PdfReader

from curriculum_harness._anthropic import get_async_client, haiku_stream_text
from curriculum_harness.source_bullets import extract_source_bullets
from curriculum_harness.state import DecomposerState
from eval.source_evidence_matcher import EN_STOPWORDS, EN_TOKEN_RE
from curriculum_harness.types import (
    HAIKU_MODEL,
    extract_json_object,
    merge_curriculum_profile_with_config,
    normalize_curriculum_profile_fragment,
)

# Full-document excerpt cap before Haiku scope pass (chars)
_MAX_INPUT_FOR_SCOPE = 320_000
_CLASSIFY_EXCERPT_CHARS = 40_000

# Language detection — English stopword density.
# Bullet corpora in English hit a stopword token at ~15-30% density;
# Hungarian / Spanish / etc. bullet corpora hit English stopwords at
# near-zero density (occasional loanwords). 0.05 is the conservative
# cutoff — below that, the source is not English and Phase 4's
# regeneration-on-SOURCE_FAITHFULNESS_FAIL is skipped because the
# English-only matcher cannot repair the mismatch (see
# eval/source_evidence_matcher.py adjacent-mechanism #4).
_LANG_DETECT_MIN_TOKENS = 40
_LANG_DETECT_EN_STOPWORD_RATIO = 0.05


def _detect_source_language_from_bullets(
    bullets: list[dict],
) -> tuple[str, dict]:
    """Classify the bullet corpus as English or non-English.

    Rule-based stopword-density signal. Returns ``(language, signal)``
    where language is ``"en"`` or ``"non-en"`` and ``signal`` records
    the inputs to the decision so the run report can explain why.

    Adjacent mechanism — what this does NOT decide:
    - Which non-English language. Any sub-threshold stopword density is
      reported as ``"non-en"``; consumers should not assume Hungarian,
      French, etc.
    - Mixed-language bullets. If half the bullets are English and half
      Hungarian, this produces an aggregated ratio that may fall either
      side of the threshold. A per-bullet language tag would be an
      upgrade.
    - Raw source text (pre-extraction). Only the bullet corpus is
      sampled — if Phase 1 extraction dropped the non-English portions
      and kept only English headings, this signal will say "en" when
      the real source is not.
    """
    if not bullets:
        return "en", {"status": "empty_bullet_corpus", "total_tokens": 0}
    tokens: list[str] = []
    for b in bullets:
        text = (b.get("text") or "").strip()
        if not text:
            continue
        tokens.extend(m.group(0).lower() for m in EN_TOKEN_RE.finditer(text))
    total = len(tokens)
    if total < _LANG_DETECT_MIN_TOKENS:
        return "en", {
            "status": "below_minimum_tokens",
            "total_tokens": total,
            "min_tokens": _LANG_DETECT_MIN_TOKENS,
        }
    stopword_hits = sum(1 for t in tokens if t in EN_STOPWORDS)
    ratio = stopword_hits / total
    signal = {
        "status": "measured",
        "total_tokens": total,
        "en_stopword_hits": stopword_hits,
        "en_stopword_ratio": round(ratio, 4),
        "threshold": _LANG_DETECT_EN_STOPWORD_RATIO,
    }
    if ratio < _LANG_DETECT_EN_STOPWORD_RATIO:
        return "non-en", signal
    return "en", signal


async def _fetch_bytes(url: str, timeout: float = 120.0) -> tuple[bytes, str | None]:
    limits = httpx.Limits(max_keepalive_connections=5)
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=timeout,
        limits=limits,
        max_redirects=30,
    ) as client:
        r = await client.get(url)
        r.raise_for_status()
        ct = r.headers.get("content-type")
        return r.content, ct


def _extract_pdf_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    chunks: list[str] = []
    for page in reader.pages:
        t = page.extract_text() or ""
        if t.strip():
            chunks.append(t)
    return "\n\n".join(chunks)


def _looks_like_html(body: bytes) -> bool:
    head = body[:8000].lstrip().lower()
    if not head:
        return False
    if head.startswith((b"<!", b"<html", b"<?xml")):
        return True
    if b"<!doctype html" in head[:200]:
        return True
    if b"<head" in head[:4000] or b"<body" in head[:4000]:
        return True
    return False


def _extract_html_text(data: bytes) -> str:
    """Strip tags enough for syllabus pages (no extra deps)."""
    s = data.decode("utf-8", errors="replace")
    s = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", s)
    s = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", s)
    s = re.sub(r"(?is)<noscript[^>]*>.*?</noscript>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html_stdlib.unescape(s)
    return re.sub(r"[ \t\r\f\v]+", " ", s).strip()


def _window_text_for_grade_subject(
    full_text: str,
    grade: str,
    subject: str,
    max_chars: int = _MAX_INPUT_FOR_SCOPE,
) -> str:
    """Prefer a slice of the PDF text likely containing the requested grade/subject section."""
    g = (grade or "").strip()
    subj = (subject or "").strip()
    lower = full_text.lower()
    anchors: list[int] = []
    for needle in (
        f"grades {g} and",
        f"grade {g}",
        f"grades {g} and {int(g) + 1}" if g.isdigit() else "",
        subj.lower()[:20] if subj else "",
        "history, grade",
        "history and geography",
        f"{g} and 8",
    ):
        if not needle:
            continue
        idx = lower.find(needle.lower())
        if idx >= 0:
            anchors.append(idx)
    start = min(anchors) if anchors else 0
    # begin slightly before the anchor for headings / TOC context
    start = max(0, start - 8000)
    end = min(len(full_text), start + max_chars)
    return full_text[start:end]


def _window_history_grade7(full_text: str, max_chars: int = _MAX_INPUT_FOR_SCOPE) -> str:
    """Anchor on History / Grade 7 headings common in Ontario SSHG PDFs."""
    lower = full_text.lower()
    needles = [
        "grades 7 and 8 history",
        "history, grade",
        "the ontario curriculum grades 7 and 8 history",
        "grade 7 history",
        "strands: history",
    ]
    positions = [lower.find(n) for n in needles]
    positions = [p for p in positions if p >= 0]
    if not positions:
        h = lower.find("history")
        positions = [h] if h >= 0 else [0]
    start = max(0, min(positions) - 12000)
    end = min(len(full_text), start + max_chars)
    return full_text[start:end]


def _scoped_content_ok(scoped: str, profile: dict[str, Any]) -> bool:
    t = (scoped or "").strip()
    if len(t) < 2000:
        return False
    first_line = t.splitlines()[0].strip().upper()
    if first_line.startswith("NO_SCOPED_CONTENT"):
        return False
    fam = str(profile.get("document_family") or "other").lower()
    lower = t.lower()
    if len(t) >= 12000:
        return True
    cues: dict[str, tuple[str, ...]] = {
        "exam_specification": (
            "assessment objective",
            "assessment objectives",
            "scheme of assessment",
            "mark scheme",
            "specification",
            "subject content",
            "question paper",
        ),
        "national_framework": (
            "attainment",
            "programme of study",
            "expectation",
            "key stage",
            "subject content",
            "aims",
        ),
        "school_scoped_programme": (
            "expectation",
            "outcome",
            "learning goal",
            "strand",
            "standard",
            "benchmark",
        ),
        "higher_ed_syllabus": (
            "syllabus",
            "objective",
            "assignment",
            "grading",
            "reading",
            "assessment",
            "schedule",
            "policy",
        ),
        "other": (
            "expectation",
            "outcome",
            "objective",
            "content",
            "assessment",
        ),
    }
    needles = cues.get(fam, cues["other"])
    if any(n in lower for n in needles):
        return True
    return len(t) >= 8000


def _use_ontario_grade7_window(profile: dict[str, Any], jurisdiction: str, pages_note: str) -> bool:
    if str(profile.get("document_family") or "") != "school_scoped_programme":
        return False
    blob = f"{jurisdiction} {pages_note}".lower()
    return "ontario" in blob


def _scope_candidate_windows(
    full_text: str,
    profile: dict[str, Any],
    subject: str,
    grade: str,
    jurisdiction: str,
    pages_note: str,
) -> list[str]:
    """Ordered windows to try for scoped Haiku extraction."""
    strategy = str(profile.get("scoping_strategy") or "grade_subject_filter")
    seen: set[int] = set()
    out: list[str] = []

    def add_window(w: str) -> None:
        w = (w or "").strip()
        if len(w) < 200:
            return
        h = hash(w[:5000])
        if h in seen:
            return
        seen.add(h)
        out.append(w)

    if strategy == "full_document":
        add_window(full_text[:_MAX_INPUT_FOR_SCOPE])
        return out or [full_text[:_MAX_INPUT_FOR_SCOPE]]

    if subject.strip() and grade.strip():
        add_window(_window_text_for_grade_subject(full_text, grade, subject))
        if _use_ontario_grade7_window(profile, jurisdiction, pages_note):
            add_window(_window_history_grade7(full_text))

    add_window(full_text[:_MAX_INPUT_FOR_SCOPE])
    return out or [full_text[:_MAX_INPUT_FOR_SCOPE]]


def _scope_fallback_slice(
    full_text: str,
    profile: dict[str, Any],
    subject: str,
    grade: str,
    jurisdiction: str,
    pages_note: str,
) -> str:
    strategy = str(profile.get("scoping_strategy") or "")
    if strategy == "full_document":
        return full_text[:_MAX_INPUT_FOR_SCOPE].strip()
    if (
        subject.strip()
        and grade.strip()
        and _use_ontario_grade7_window(profile, jurisdiction, pages_note)
    ):
        return (
            _window_history_grade7(full_text).strip()
            or _window_text_for_grade_subject(full_text, grade, subject).strip()
            or full_text[:_MAX_INPUT_FOR_SCOPE]
        )
    if subject.strip() and grade.strip():
        return (
            _window_text_for_grade_subject(full_text, grade, subject).strip()
            or full_text[:_MAX_INPUT_FOR_SCOPE]
        )
    return full_text[:_MAX_INPUT_FOR_SCOPE].strip()


def _scope_system_prompt(profile: dict[str, Any], subject: str, grade: str, jurisdiction: str) -> str:
    fam = str(profile.get("document_family") or "other")
    strategy = str(profile.get("scoping_strategy") or "grade_subject_filter")
    juris = jurisdiction or "the stated jurisdiction"
    subj = subject or "the stated subject"
    lvl = grade or "the stated level or stage"
    base_rules = (
        "Output **plain text only** (no markdown fences, no preamble, no commentary).\n"
        "Preserve headings, numbering, and assessment language where present.\n"
        "If the excerpt contains no usable instructional content for the requested scope, output exactly:\n"
        "NO_SCOPED_CONTENT_FOUND\n"
    )
    if fam == "exam_specification" and strategy == "section_anchor":
        return (
            "You extract text from **exam board specifications** (GCSE, A Level, etc.).\n"
            f"{base_rules}\n"
            f"Keep **Assessment objectives**, **scheme of assessment**, **subject content**, and related "
            f"sections relevant to **{subj}** at **{lvl}** for **{juris}**.\n"
            "Drop unrelated qualifications, unrelated subjects, and purely administrative boilerplate "
            "that does not support teaching or assessment of this subject.\n"
        )
    if fam == "national_framework":
        return (
            "You extract text from **national or state curriculum frameworks**.\n"
            f"{base_rules}\n"
            f"Keep attainment targets, programmes of study, and subject content aligned with **{subj}** "
            f"and **{lvl}** (e.g. key stage / phase) for **{juris}**.\n"
            "Exclude unrelated subjects and phases unless they are prerequisite context in the same paragraph.\n"
        )
    if fam == "higher_ed_syllabus" or strategy == "full_document":
        return (
            "You extract text from **higher education syllabi / course pages**.\n"
            f"{base_rules}\n"
            f"Keep course outcomes, topics, readings, assignments, grading, policies, and schedules "
            f"relevant to **{subj}** as taught at **{lvl}** ({juris}).\n"
            "Remove navigation chrome, unrelated courses, and boilerplate only if clearly not part of "
            "the course requirements.\n"
        )
    if fam == "school_scoped_programme":
        return (
            "You extract text from **school- or trust-scoped curriculum documents** (e.g. REAL School, "
            "academy, or district programmes).\n"
            f"{base_rules}\n"
            f"Keep goals, strands, outcomes, and progressions for **{subj}** at **{lvl}** under **{juris}**.\n"
            "Exclude unrelated grades/subjects unless they are explicitly cross-referenced in the same block.\n"
        )
    return (
        "You extract instructional curriculum text from official or institutional documents.\n"
        f"{base_rules}\n"
        f"Keep content tied to **{subj}** at **{lvl}** for **{juris}**.\n"
        "Drop unrelated subjects, unrelated phases, and policy-only filler not tied to teaching this subject.\n"
    )


def _document_indicates_multi_level_progression(text: str) -> bool:
    """
    True when the document text clearly spans multiple stages/years/bands.
    Used to correct misclassification (e.g. UK NC as single_intended_level).
    """
    if not text or len(text.strip()) < 80:
        return False
    sample = text[:800_000]
    low = sample.lower()

    if re.search(r"key\s*stages?\b", low):
        return True
    if re.search(r"\bks\s*[1-4]\b", low) or re.search(r"\bks[1-4]\b", low):
        return True
    if re.search(r"foundation\s+to\s+year", low):
        return True
    if re.search(r"(?:grades?|year\s*levels?)\s+k\s*[-–]\s*12\b", low):
        return True
    if re.search(r"\bk\s*[-–]\s*12\b", low):
        return True
    if re.search(r"\bf\s*[-–]\s*10\b", low):
        return True

    stage_hits = re.findall(r"\bstage\s*[123]\b", low)
    if len(stage_hits) >= 2:
        return True
    if re.search(r"stage\s*1[/\s,]+(?:stage\s*)?2", low):
        return True
    if re.search(r"stage\s*2[/\s,]+(?:stage\s*)?3", low):
        return True

    year_nums = re.findall(r"\byear\s*(?:([1-9]|1[0-3]))\b", low)
    if len(set(year_nums)) >= 2:
        return True
    if re.search(
        r"\byears?\s*(?:[1-9]|1[0-3])\s*(?:[-–,]|to|through|until)\s*(?:[1-9]|1[0-3])\b",
        low,
    ):
        return True
    if re.search(r"\byears?\s*[1-9]\s*[,;]\s*(?:[1-9]|1[0-3])\b", low):
        return True

    return False


async def _haiku_classify_curriculum(
    excerpt: str,
    hints: dict[str, Any],
) -> dict[str, Any]:
    system = (
        "You classify curriculum documents for downstream processing. Reply with ONLY a JSON object:\n"
        "{\n"
        '  "document_family": one of '
        '"exam_specification|national_framework|school_scoped_programme|higher_ed_syllabus|other",\n'
        '  "level_model": one of '
        '"single_intended_level|multi_level_progression|unstructured",\n'
        '  "scoping_strategy": one of '
        '"grade_subject_filter|full_document|section_anchor",\n'
        '  "assessment_signals": { optional booleans/strings e.g. '
        '"has_assessment_objectives", "has_command_words", "has_mark_scheme" },\n'
        '  "confidence": "high"|"medium"|"low",\n'
        '  "rationale": short string (max 200 chars)\n'
        "}\n"
        "Use the document excerpt and the hints; if unsure, set confidence low and document_family other.\n"
        "If the document spans Key Stages (e.g. UK), multiple school years (e.g. Years 1–10), "
        "Stages 1–3, K–12, or F–10 bands, set level_model to multi_level_progression — "
        "not single_intended_level — even when hints name one target grade or key stage.\n"
        "No markdown."
    )
    user_blocks: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": f"Hints JSON: {hints}\n\nDocument excerpt:\n\n{excerpt}",
        }
    ]
    client = get_async_client()
    raw = (
        await haiku_stream_text(
            client,
            model=HAIKU_MODEL,
            max_tokens=1024,
            system=system,
            user_blocks=user_blocks,
            label="phase1_haiku_classify",
        )
    ).strip()
    return extract_json_object(raw) or {}


async def _haiku_extract_scoped_curriculum(
    window_text: str,
    subject: str,
    grade: str,
    jurisdiction: str,
    profile: dict[str, Any],
) -> str:
    system = _scope_system_prompt(profile, subject, grade, jurisdiction)
    user_blocks: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"Subject filter: {subject or '(infer from document)'}\n"
                f"Level / grade filter: {grade or '(infer from document)'}\n"
                f"Jurisdiction: {jurisdiction or '(infer from document)'}\n\n"
                "Document excerpt to filter:\n\n"
                f"{window_text}"
            ),
        }
    ]
    client = get_async_client()
    return (
        await haiku_stream_text(
            client,
            model=HAIKU_MODEL,
            max_tokens=16384,
            system=system,
            user_blocks=user_blocks,
            label="phase1_haiku_scope_extract",
        )
    ).strip()


async def phase1_ingestion(state: DecomposerState) -> dict[str, Any]:
    errs = list(state.get("errors") or [])
    cfg = state.get("config") or {}
    src = cfg.get("source") or {}
    url = str(src.get("url") or state.get("source_url") or "")
    src_type = str(src.get("type") or "pdf_url")
    subject = str(src.get("subject") or "")
    grade = str(src.get("grade") or "")
    jurisdiction = str(src.get("jurisdiction") or "")

    if not url:
        errs.append("phase1: missing source URL")
        return {
            "current_phase": "phase1:error",
            "errors": errs,
            "curriculum_profile": {},
            "curriculum_classification_notes": "",
        }

    curriculum_bits: list[str] = []
    try:
        body, content_type = await _fetch_bytes(url)
        ct_low = (content_type or "").lower()
        wants_pdf = bool(
            "pdf" in ct_low
            or url.lower().endswith(".pdf")
            or src_type == "pdf_url",
        )
        raw_piece = ""
        if "text/html" in ct_low or _looks_like_html(body):
            raw_piece = _extract_html_text(body)
        elif wants_pdf:
            try:
                raw_piece = _extract_pdf_text(body)
            except Exception as exc:
                errs.append(f"phase1: PDF extract failed: {exc}")
                raw_piece = ""
                if "pdf" not in ct_low and _looks_like_html(body):
                    raw_piece = _extract_html_text(body)
                    errs.append("phase1: treating response as HTML after PDF failure")
            if len(raw_piece.strip()) < 120 and _looks_like_html(body):
                fallback = _extract_html_text(body)
                if len(fallback.strip()) > len(raw_piece.strip()):
                    if raw_piece.strip():
                        errs.append("phase1: PDF text thin; preferring HTML text extraction")
                    raw_piece = fallback
        else:
            raw_piece = body.decode("utf-8", errors="replace")
        curriculum_bits.append(raw_piece)
    except Exception as exc:
        errs.append(f"phase1: fetch/extract failed: {exc}")
        return {
            "current_phase": "phase1:error",
            "errors": errs,
            "raw_curriculum": "",
            "curriculum_metadata": {},
            "curriculum_profile": {},
            "curriculum_classification_notes": "",
        }

    full_text = "\n\n".join(curriculum_bits).strip()
    if not full_text:
        errs.append("phase1: empty curriculum text after extraction")
        return {
            "current_phase": "phase1:error",
            "errors": errs,
            "raw_curriculum": "",
            "curriculum_metadata": {},
            "curriculum_profile": {},
            "curriculum_classification_notes": "",
        }

    metadata = {
        "subject": subject,
        "grade": grade,
        "jurisdiction": jurisdiction,
        "year": str(src.get("year") or ""),
        "source_type": src_type,
        "pages_note": str(src.get("pages") or ""),
        "url": url,
        "scope": f"Grade {grade} {subject}".strip(),
    }

    classification_notes_parts: list[str] = []
    classify_hints = {
        "subject": subject,
        "grade": grade,
        "jurisdiction": jurisdiction,
        "year": metadata.get("year", ""),
        "pages_note": metadata.get("pages_note", ""),
        "source_type": src_type,
    }
    excerpt_for_classify = full_text[:_CLASSIFY_EXCERPT_CHARS]
    try:
        inferred_raw = await _haiku_classify_curriculum(excerpt_for_classify, classify_hints)
        if not inferred_raw:
            classification_notes_parts.append("phase1: classification returned empty JSON (using defaults)")
            errs.append("phase1: classification empty JSON — defaults applied")
        inferred = normalize_curriculum_profile_fragment(inferred_raw)
    except Exception as exc:
        errs.append(f"phase1: classification failed — defaults applied: {exc}")
        classification_notes_parts.append(str(exc))
        inferred = normalize_curriculum_profile_fragment({})

    if _document_indicates_multi_level_progression(full_text):
        idict = dict(inferred)
        if idict.get("level_model") != "multi_level_progression":
            prev = str(idict.get("rationale") or "").strip()
            note = "[heuristic: multi-level progression signals in document]"
            idict["level_model"] = "multi_level_progression"
            idict["rationale"] = f"{prev} {note}".strip() if prev else note
            inferred = normalize_curriculum_profile_fragment(idict)
            classification_notes_parts.append(
                "phase1: level_model set to multi_level_progression (document text signals)"
            )

    profile_dict = merge_curriculum_profile_with_config(inferred, cfg)
    sh = dict(profile_dict.get("source_hints") or {})
    sh.update(
        {
            k: v
            for k, v in {
                "subject": subject,
                "grade": grade,
                "jurisdiction": jurisdiction,
                "pages_note": str(src.get("pages") or ""),
                "url": url,
            }.items()
            if v
        }
    )
    profile_dict["source_hints"] = sh
    if profile_dict.get("rationale"):
        classification_notes_parts.append(str(profile_dict["rationale"]))

    raw_curriculum = full_text
    try:
        windows = _scope_candidate_windows(
            full_text,
            profile_dict,
            subject,
            grade,
            jurisdiction,
            str(src.get("pages") or ""),
        )
        scoped = ""
        for window in windows:
            if not window or len(window.strip()) < 200:
                continue
            candidate = await _haiku_extract_scoped_curriculum(
                window, subject, grade, jurisdiction, profile_dict
            )
            if _scoped_content_ok(candidate, profile_dict):
                scoped = candidate
                break
        if scoped:
            raw_curriculum = scoped
        else:
            errs.append(
                "phase1: scoped extraction returned empty or unfound — using profile-aware fallback slice"
            )
            raw_curriculum = _scope_fallback_slice(
                full_text,
                profile_dict,
                subject,
                grade,
                jurisdiction,
                str(src.get("pages") or ""),
            )
    except Exception as exc:
        errs.append(f"phase1: Haiku scope extraction failed (using fallback slice): {exc}")
        raw_curriculum = _scope_fallback_slice(
            full_text,
            profile_dict,
            subject,
            grade,
            jurisdiction,
            str(src.get("pages") or ""),
        )

    if not raw_curriculum.strip():
        errs.append("phase1: empty after scope extraction")
        return {
            "current_phase": "phase1:error",
            "errors": errs,
            "raw_curriculum": "",
            "curriculum_metadata": metadata,
            "curriculum_profile": profile_dict,
            "curriculum_classification_notes": " | ".join(classification_notes_parts),
        }

    excerpt = raw_curriculum[:12000]
    system = (
        "You extract curriculum metadata. Reply with ONLY a compact JSON object: "
        '{"subject","grade","jurisdiction","year"} inferred from the excerpt. '
        "Use provided hints when the excerpt is silent. No markdown prose."
    )
    user_blocks: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"Hints JSON: {metadata}\n\n"
                "Curriculum excerpt (after grade/subject scoping):\n\n"
                f"{excerpt}"
            ),
        }
    ]

    try:
        client = get_async_client()
        haiku_out = await haiku_stream_text(
            client,
            model=HAIKU_MODEL,
            max_tokens=512,
            system=system,
            user_blocks=user_blocks,
            label="phase1_haiku_metadata",
        )
        parsed = extract_json_object(haiku_out) or {}
        for key in ("subject", "grade", "jurisdiction", "year"):
            if parsed.get(key):
                metadata[key] = str(parsed[key])
    except Exception as exc:
        errs.append(f"phase1: Haiku metadata pass failed (non-fatal): {exc}")

    # Source bullets — rule-based structural extraction. Fed from the
    # DETERMINISTIC profile-aware slice (`_scope_fallback_slice`), not
    # from the Haiku-scoped `raw_curriculum`. Haiku at temperature 0
    # still paraphrases between runs (see
    # `docs/diagnostics/2026-04-18-phase1-scoping-diagnosis.md`), so
    # rule-based extraction from Haiku output was the dominant source
    # of inter-run variance. Feeding the deterministic slice pins the
    # bullet set; `raw_curriculum` keeps the Haiku narrowing for
    # downstream LLM phases. Adjacent-mechanism declaration in
    # `curriculum_harness/source_bullets.py`.
    bullet_source = _scope_fallback_slice(
        full_text,
        profile_dict,
        subject,
        grade,
        jurisdiction,
        str(src.get("pages") or ""),
    )
    bullets = extract_source_bullets(bullet_source, target_grade=str(grade or ""))
    if not bullets:
        # Fallback: if the deterministic slice yielded no bullets
        # (unusual — suggests a document with no structural markers),
        # retry on the Haiku-scoped text so the pipeline does not ship
        # zero bullets from a document that clearly contains outcomes.
        bullets = extract_source_bullets(
            raw_curriculum.strip(), target_grade=str(grade or "")
        )

    source_language, source_language_signal = _detect_source_language_from_bullets(bullets)

    return {
        "current_phase": "phase1:complete",
        "errors": errs,
        "raw_curriculum": raw_curriculum.strip(),
        "curriculum_metadata": metadata,
        "subject": metadata.get("subject", ""),
        "grade": metadata.get("grade", ""),
        "jurisdiction": metadata.get("jurisdiction", ""),
        "year": metadata.get("year", ""),
        "source_url": url,
        "curriculum_profile": dict(profile_dict),
        "curriculum_classification_notes": " | ".join(
            [p for p in classification_notes_parts if p],
        ).strip(),
        "source_bullets": bullets,
        "source_language": source_language,
        "source_language_signal": source_language_signal,
    }
