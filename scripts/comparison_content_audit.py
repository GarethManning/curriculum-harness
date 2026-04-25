#!/usr/bin/env python3
"""
Comparison-content audit suite — standing infrastructure for any source-quoting
work in docs/comparison-content/.

Four checks (Stop 4 lessons, captured in Second Brain 1b1e7096):

  1. Citation resolution        — every [slug §N] tag points to an existing paragraph ID.
  2. Quote-to-source match      — every "…" quoted span is verbatim present in at least
                                  one of the source paragraphs cited in the same bracket.
                                  A quote with no nearby citation is itself a failure.
  3. Absence-claim verification — every absence-pattern claim has an entry in
                                  absence-claims-log.md.
  4. Cross-artefact consistency — the same quoted phrase, where it appears in more than
                                  one artefact, cites the same canonical paragraph ID
                                  (allowing documented bundle-citations).

Usage:
    python scripts/comparison_content_audit.py [--scope cards|themes|all]

Exit code 0 only if all enabled checks pass on the in-scope artefacts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
COMP = REPO_ROOT / "docs" / "comparison-content"
SOURCES_DIR = COMP / "sources"
CARDS_DIR = COMP / "level-2-cards"
THEMES_DIR = COMP / "level-3-themes"
LEVEL_1 = COMP / "level-1-essay.md"
COG_BRIEFS = COMP / "centre-of-gravity-briefs.md"
ABSENCE_LOG = COMP / "absence-claims-log.md"

CITATION_RE = re.compile(r"\[([a-z][a-z0-9-]+)((?:\s*§\s*\d+)(?:\s*,\s*§\s*\d+)*)\]")
PARA_IDS_RE = re.compile(r"§\s*(\d+)")
PARA_HEADER_RE = re.compile(r"^§\s*(\d+)\s*$")
QUOTE_RE = re.compile(r"[\"“]([^\"“”]+?)[\"”]")

ABSENCE_PATTERNS = [
    r"doesn['’]t (?:address|appear|extend|cover|include|reach|develop|involve|carry|name|specify|build)",
    r"isn['’]t (?:part of|named|in |present|developed|specified|included|on the|a named)",
    r"is not (?:part of|named|present|developed|specified|included|in )",
    r"(?:sit|sits|stay) outside",
    r"not included",
    r"no (?:progression|sustained|named|equivalent|digital-specific|explicit)",
    r"don['’]t (?:extend|reach|address|cover|specify|name|include)",
    r"absent in",
    r"not (?:foreground(?:ed)?|name(?:d)?|developed)",
    r"runs without",
    r"has no (?:progression|equivalent|named|named ?focus|digital)",
    r"zero hits",
]
ABSENCE_RE = re.compile("|".join(ABSENCE_PATTERNS), re.IGNORECASE)


def log(level: str, msg: str) -> None:
    print(f"[{level}] {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# Source corpus parsing
# ─────────────────────────────────────────────────────────────────────────────


def load_sources() -> dict[tuple[str, int], str]:
    """Return mapping {(slug, paragraph_id_int): paragraph_text} for every source paragraph."""
    paragraphs: dict[tuple[str, int], str] = {}
    for src_file in sorted(SOURCES_DIR.rglob("*.md")):
        if src_file.name == "README.md":
            continue
        slug = src_file.stem
        text = src_file.read_text(encoding="utf-8")
        # Walk lines, accumulate text under each §N header until the next §M or section heading.
        current_id: int | None = None
        buf: list[str] = []
        for line in text.splitlines():
            m = PARA_HEADER_RE.match(line.strip())
            if m:
                if current_id is not None:
                    paragraphs[(slug, current_id)] = "\n".join(buf).strip()
                current_id = int(m.group(1))
                buf = []
            else:
                if current_id is not None:
                    buf.append(line)
        if current_id is not None:
            paragraphs[(slug, current_id)] = "\n".join(buf).strip()
    return paragraphs


# ─────────────────────────────────────────────────────────────────────────────
# Artefact discovery
# ─────────────────────────────────────────────────────────────────────────────


def collect_artefacts(scope: str) -> list[Path]:
    files: list[Path] = []
    if scope in ("cards", "all"):
        if CARDS_DIR.exists():
            files += sorted(CARDS_DIR.glob("*.md"))
    if scope in ("themes", "all"):
        if THEMES_DIR.exists():
            files += sorted(THEMES_DIR.glob("*.md"))
    if scope == "all":
        if LEVEL_1.exists():
            files.append(LEVEL_1)
        if COG_BRIEFS.exists():
            files.append(COG_BRIEFS)
    return files


# ─────────────────────────────────────────────────────────────────────────────
# Normalization for substring matching
# ─────────────────────────────────────────────────────────────────────────────


def normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    # Quote chars
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("‘", "'").replace("’", "'")
    # Dashes — treat em-dash, en-dash, hyphen as themselves (no flattening; preserve)
    # Ellipsis
    s = s.replace("…", "...")
    # Whitespace normalization — collapse all runs of whitespace (incl. newlines) to a single space
    s = re.sub(r"\s+", " ", s)
    return s.strip()


# American → British verb-ending normalisation, scoped to verb suffixes only.
# Per audit-policy.md: cards may selectively anglicise verb forms while preserving
# American noun spellings as they appear in the source. Anglicising nouns on the
# audit side would over-correct and miss legitimate quotes that preserve "behaviors",
# "color", etc. verbatim.
_AM_BR_VERB_PAIRS = [
    (re.compile(r"ize\b"), "ise"),
    (re.compile(r"izing\b"), "ising"),
    (re.compile(r"ized\b"), "ised"),
    (re.compile(r"ization\b"), "isation"),
    (re.compile(r"yze\b"), "yse"),
    (re.compile(r"yzing\b"), "ysing"),
    (re.compile(r"yzed\b"), "ysed"),
]


def anglicise(s: str) -> str:
    out = s
    for rx, repl in _AM_BR_VERB_PAIRS:
        out = rx.sub(repl, out)
    return out


def _substring_or_segments_in_order(quote_norm: str, source_norm: str) -> bool:
    """Substring match, supporting mid-quote ellipsis-elision: if the quote contains
    '...' (after normalisation), split on it and require each segment to appear in
    source in order.
    """
    if "..." not in quote_norm:
        return quote_norm in source_norm
    segments = [s.strip() for s in quote_norm.split("...") if s.strip()]
    cursor = 0
    for seg in segments:
        idx = source_norm.find(seg, cursor)
        if idx < 0:
            return False
        cursor = idx + len(seg)
    return True


def quote_matches_source(quote: str, source_text: str) -> bool:
    """Return True if quote is a verbatim substring of source_text under the operational
    definition documented in docs/comparison-content/audit-policy.md.

    Accepted normalisations:
      - whitespace, quote chars, ellipsis (already applied via normalize_text)
      - first-letter case difference at start of quote (editorial integration)
      - American → British verb-ending anglicisation (override; nouns preserved)
      - mid-quote ellipsis-elision marked with '...' (segments matched in order)
      - truncation up to natural sentence boundary (substring match accepts)
    NOT accepted: verb-form changes elsewhere in the quote, pronoun strips that
    change meaning, paraphrase presented as quote, prefix strips that remove
    framework-context which disambiguated the quote.
    """
    q = normalize_text(quote)
    src = normalize_text(source_text)
    if not q:
        return False
    if _substring_or_segments_in_order(q, src):
        return True
    q_flip = (q[0].swapcase() + q[1:]) if q else q
    if _substring_or_segments_in_order(q_flip, src):
        return True
    src_ang = anglicise(src)
    if _substring_or_segments_in_order(q, src_ang):
        return True
    if _substring_or_segments_in_order(q_flip, src_ang):
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# Check 1 — citation resolution
# ─────────────────────────────────────────────────────────────────────────────


def parse_citations_in_text(text: str) -> list[tuple[str, list[int], int, int]]:
    """Return list of (slug, [paragraph_ids], start_offset, end_offset) for each citation tag in text."""
    out = []
    for m in CITATION_RE.finditer(text):
        slug = m.group(1)
        ids = [int(x) for x in PARA_IDS_RE.findall(m.group(2))]
        out.append((slug, ids, m.start(), m.end()))
    return out


def check_citation_resolution(artefacts: list[Path], sources: dict[tuple[str, int], str]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    total_cites = 0
    for art in artefacts:
        text = art.read_text(encoding="utf-8")
        for slug, ids, start, _end in parse_citations_in_text(text):
            for pid in ids:
                total_cites += 1
                if (slug, pid) not in sources:
                    line_no = text[:start].count("\n") + 1
                    failures.append(f"{art.relative_to(REPO_ROOT)}:{line_no} unresolved [{slug} §{pid}]")
    log("CHECK 1", f"citation resolution: {total_cites} citation refs scanned, {len(failures)} unresolved")
    return (len(failures) == 0, failures)


# ─────────────────────────────────────────────────────────────────────────────
# Check 2 — quote-to-source substring match
# ─────────────────────────────────────────────────────────────────────────────


def find_following_citation(text: str, after: int) -> tuple[str, list[int], int] | None:
    """Find the next [slug §N…] that follows position `after`.
    Bound the search to end of current sentence (period+space, period+newline, or blank line).
    Intervening quotes do NOT close the search window — the corpus uses the pattern
    `"X" and "Y" [citation]` where one citation covers both quotes.
    Returns (slug, [ids], end_offset) or None.
    """
    snippet = text[after:after + 600]
    blank = re.search(r"\n\s*\n", snippet)
    sentence_end = re.search(r"\.\s", snippet)
    boundary = len(snippet)
    if blank:
        boundary = min(boundary, blank.start())
    if sentence_end:
        # Allow the citation to live at the end of the sentence — search up to and
        # including the period+space.
        boundary = min(boundary, sentence_end.end())
    cite_match = CITATION_RE.search(snippet[:boundary])
    if cite_match:
        slug = cite_match.group(1)
        ids = [int(x) for x in PARA_IDS_RE.findall(cite_match.group(2))]
        return (slug, ids, after + cite_match.end())
    return None


def check_quote_to_source(artefacts: list[Path], sources: dict[tuple[str, int], str]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    quotes_checked = 0
    skip_short = 0
    for art in artefacts:
        text = art.read_text(encoding="utf-8")
        for qm in QUOTE_RE.finditer(text):
            quoted = qm.group(1).strip()
            # Skip very short quotes that may be section labels / single words / single non-attributed phrases
            if len(quoted) < 4:
                skip_short += 1
                continue
            quotes_checked += 1
            cite = find_following_citation(text, qm.end())
            line_no = text[:qm.start()].count("\n") + 1
            if cite is None:
                failures.append(f"{art.relative_to(REPO_ROOT)}:{line_no} phantom-quote (no citation): \"{quoted[:80]}\"")
                continue
            slug, ids, _ = cite
            matched = False
            for pid in ids:
                src = sources.get((slug, pid))
                if src is None:
                    continue  # citation-resolution failure handled in Check 1
                if quote_matches_source(quoted, src):
                    matched = True
                    break
            if not matched:
                failures.append(
                    f"{art.relative_to(REPO_ROOT)}:{line_no} quote not in source [{slug} §{','.join(str(i) for i in ids)}]: \"{quoted[:120]}\""
                )
    log("CHECK 2", f"quote-to-source: {quotes_checked} quoted spans checked ({skip_short} short skipped), {len(failures)} mismatches")
    return (len(failures) == 0, failures)


# ─────────────────────────────────────────────────────────────────────────────
# Check 3 — absence-claim coverage
# ─────────────────────────────────────────────────────────────────────────────


def load_absence_log_keys() -> set[str]:
    """Return set of card identifiers from absence-claims-log.md headings (rough match)."""
    keys: set[str] = set()
    if not ABSENCE_LOG.exists():
        return keys
    for line in ABSENCE_LOG.read_text(encoding="utf-8").splitlines():
        # Match lines like "### LT 4.2 × CfW — ..." or "### LT 4.2 × CASEL ..."
        m = re.match(r"###\s+LT\s+([\d.]+)\s+[×x]\s+(\S+)", line, re.IGNORECASE)
        if m:
            lt = m.group(1).strip()
            fw = m.group(2).strip().rstrip(":,").lower()
            # Normalize framework names
            fw_map = {"cfw": "cfw", "rshe": "rshe", "casel": "casel", "welsh": "cfw"}
            fw_norm = fw_map.get(fw.split("—")[0].strip().lower(), fw)
            keys.add(f"lt-{lt} × {fw_norm}")
    return keys


def card_key_from_path(path: Path, h2_text: str) -> str | None:
    """Map a card file + H2 heading text to absence-log key form: lt-N.M × {framework}."""
    name = path.stem  # lt-1-1
    m = re.match(r"lt-(\d+)-(\d+)", name)
    if not m:
        return None
    lt = f"{m.group(1)}.{m.group(2)}"
    h = h2_text.lower()
    if "rshe" in h:
        fw = "rshe"
    elif "cfw" in h or "welsh" in h:
        fw = "cfw"
    elif "casel" in h:
        fw = "casel"
    else:
        return None
    return f"lt-{lt} × {fw}"


def check_absence_claims(artefacts: list[Path]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    log_keys = load_absence_log_keys()
    sections_with_absence = 0
    sections_logged = 0
    for art in artefacts:
        if art.parent != CARDS_DIR:
            # Themes have a different absence-tracking convention; skip for now (informational only).
            continue
        text = art.read_text(encoding="utf-8")
        # Split by ## headings
        sections = re.split(r"^##\s+(.+)$", text, flags=re.MULTILINE)
        # sections = [pre, h2_1, body_1, h2_2, body_2, ...]
        for i in range(1, len(sections), 2):
            h2 = sections[i].strip()
            body = sections[i + 1] if i + 1 < len(sections) else ""
            if ABSENCE_RE.search(body):
                sections_with_absence += 1
                key = card_key_from_path(art, h2)
                if key is None:
                    continue
                if key not in log_keys:
                    failures.append(f"{art.relative_to(REPO_ROOT)} ## {h2}: absence claim present but no entry in absence-claims-log.md (expected key: {key})")
                else:
                    sections_logged += 1
    log("CHECK 3", f"absence claims: {sections_with_absence} sections with absence-pattern, {sections_logged} have log entry, {len(failures)} missing")
    return (len(failures) == 0, failures)


# ─────────────────────────────────────────────────────────────────────────────
# Check 4 — cross-artefact consistency
# ─────────────────────────────────────────────────────────────────────────────


# Documented bundle-citation equivalences. Per audit-policy.md: when source paragraphs
# are duplicates of each other (verbatim same competency text under different grade
# bands), citations to either are acceptable cross-artefact. Add new entries here as
# they are documented.
DOCUMENTED_BUNDLE_EQUIVALENCES: list[set[tuple[str, int]]] = [
    # CASEL §22 (G11–12 Self-Management) and §6 (G6–8 Self-Management) both contain
    # "Practice various coping skills to process thoughts and manage stressful situations"
    # verbatim. Either citation is acceptable when this phrase appears.
    {("casel-pilot-extracts", 6), ("casel-pilot-extracts", 22)},
]


def _ids_under_same_bundle(slug_a: str, ids_a: tuple[int, ...], slug_b: str, ids_b: tuple[int, ...]) -> bool:
    if slug_a != slug_b:
        return False
    set_a = {(slug_a, i) for i in ids_a}
    set_b = {(slug_b, i) for i in ids_b}
    for bundle in DOCUMENTED_BUNDLE_EQUIVALENCES:
        if set_a.issubset(bundle) and set_b.issubset(bundle):
            return True
    return False


def check_cross_artefact_consistency(artefacts: list[Path]) -> tuple[bool, list[str]]:
    """Quoted phrases appearing in more than one artefact must cite the same canonical paragraph ID(s),
    except where citations fall under a documented bundle-equivalence (see DOCUMENTED_BUNDLE_EQUIVALENCES)."""
    failures: list[str] = []
    occurrences: dict[str, list[tuple[Path, str, tuple[int, ...], int]]] = defaultdict(list)
    for art in artefacts:
        text = art.read_text(encoding="utf-8")
        for qm in QUOTE_RE.finditer(text):
            quoted = qm.group(1).strip()
            if len(quoted) < 12:
                continue
            cite = find_following_citation(text, qm.end())
            if cite is None:
                continue
            slug, ids, _ = cite
            qnorm = normalize_text(quoted)
            line_no = text[:qm.start()].count("\n") + 1
            occurrences[qnorm].append((art, slug, tuple(sorted(ids)), line_no))
    distinct_quotes_multi = 0
    inconsistent = 0
    bundle_accepted = 0
    for qnorm, occs in occurrences.items():
        if len(occs) < 2:
            continue
        distinct_quotes_multi += 1
        groups = {(s, ids) for (_a, s, ids, _ln) in occs}
        if len(groups) <= 1:
            continue
        # Check whether ALL pairs of differing groups fall under bundle equivalence
        groups_list = list(groups)
        all_bundled = True
        for i in range(len(groups_list)):
            for j in range(i + 1, len(groups_list)):
                a_slug, a_ids = groups_list[i]
                b_slug, b_ids = groups_list[j]
                if not _ids_under_same_bundle(a_slug, a_ids, b_slug, b_ids):
                    all_bundled = False
        if all_bundled:
            bundle_accepted += 1
            continue
        inconsistent += 1
        grp_lines = []
        for (a, s, ids, ln) in occs:
            grp_lines.append(f"  {a.relative_to(REPO_ROOT)}:{ln} [{s} §{','.join(str(i) for i in ids)}]")
        failures.append(
            f"Quote cited under different paragraph IDs in different artefacts:\n  \"{qnorm[:100]}\"\n" + "\n".join(grp_lines)
        )
    log("CHECK 4", f"cross-artefact consistency: {distinct_quotes_multi} quotes appear in 2+ artefacts, {bundle_accepted} bundle-accepted, {inconsistent} cite inconsistently")
    return (len(failures) == 0, failures)


# ─────────────────────────────────────────────────────────────────────────────
# Driver
# ─────────────────────────────────────────────────────────────────────────────


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=["cards", "themes", "all"], default="all")
    ap.add_argument("--json", action="store_true", help="Output structured JSON summary")
    args = ap.parse_args()

    sources = load_sources()
    artefacts = collect_artefacts(args.scope)
    log("SCAN", f"scope={args.scope}: {len(artefacts)} artefacts, {len(sources)} source paragraphs")

    ok1, f1 = check_citation_resolution(artefacts, sources)
    ok2, f2 = check_quote_to_source(artefacts, sources)
    ok3, f3 = check_absence_claims(artefacts)
    ok4, f4 = check_cross_artefact_consistency(artefacts)

    overall = ok1 and ok2 and ok3 and ok4

    print()
    print("=" * 72)
    print(f"CHECK 1 (citation resolution):       {'PASS' if ok1 else 'FAIL'}")
    print(f"CHECK 2 (quote-to-source match):     {'PASS' if ok2 else 'FAIL'}")
    print(f"CHECK 3 (absence-claim verified):    {'PASS' if ok3 else 'FAIL'}")
    print(f"CHECK 4 (cross-artefact consistent): {'PASS' if ok4 else 'FAIL'}")
    print(f"OVERALL: {'PASS' if overall else 'FAIL'}")
    print("=" * 72)

    if not overall:
        print()
        if f1:
            print("--- Citation resolution failures ---")
            for f in f1[:50]:
                print(f"  {f}")
            if len(f1) > 50:
                print(f"  ... and {len(f1) - 50} more")
        if f2:
            print("--- Quote-to-source failures ---")
            for f in f2[:50]:
                print(f"  {f}")
            if len(f2) > 50:
                print(f"  ... and {len(f2) - 50} more")
        if f3:
            print("--- Absence-claim failures ---")
            for f in f3[:50]:
                print(f"  {f}")
            if len(f3) > 50:
                print(f"  ... and {len(f3) - 50} more")
        if f4:
            print("--- Cross-artefact consistency failures ---")
            for f in f4[:20]:
                print(f"  {f}")
            if len(f4) > 20:
                print(f"  ... and {len(f4) - 20} more")

    if args.json:
        print()
        print("JSON_SUMMARY=" + json.dumps({
            "scope": args.scope,
            "artefacts": len(artefacts),
            "sources": len(sources),
            "check_1_citation_resolution": {"pass": ok1, "failures": f1},
            "check_2_quote_to_source": {"pass": ok2, "failures": f2},
            "check_3_absence_claims": {"pass": ok3, "failures": f3},
            "check_4_cross_artefact": {"pass": ok4, "failures": f4},
            "overall": overall,
        }))

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
