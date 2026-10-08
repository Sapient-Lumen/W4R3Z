#!/usr/bin/env python3
"""Validate canonical platform-media companion header tags.

Checks every `companions=`, `companions_overflow=`, and `companions_detail=` occurrence in the repository for:
- ascending doc-number order,
- no duplicate doc numbers within a line,
- known companion doc range (`540–581`),
- canonical doc-native state tokens derived from each companion doc's own minimal grammar,
- valid optional `header_pick_order=<...>` and `detail_pick_order=<...>` declarations inside companion docs, and
- the archive-wide three-tag budget for each companion line, and
- no duplicate companion docs across header/overflow pairs (overflow is for additional companion docs only), and
- no uncarried, duplicated, or multi-tag same-doc residue in `companions_detail=`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

PRINCIPAL_FIELDS = {
    540: "carrier",
    541: "delivered_target_status",
    542: "app_class",
    543: "resume_class",
    544: "jump_class",
    545: "texttrack_class",
    546: "viewstate_class",
    547: "rendition_class",
    548: "rate_class",
    549: "audio_class",
    550: "remote_class",
    551: "transition_class",
    552: "audio_track_class",
    553: "saved_class",
    554: "metadata_class",
    555: "collection_alias",
    556: "repeat_class",
    557: "pane_state",
    558: "pane_state",
    559: "live_position",
    560: "next_item_state",
    561: "readiness_state",
    562: "aipane_state",
    563: "thread_state",
    564: "answer_language_state",
    565: "grounding_state",
    566: "source_basis_state",
    567: "answer_outcome_state",
    568: "qualification_state",
    569: "feedback_state",
    570: "eligibility_state",
    571: "data_handling_state",
    572: "sufficiency_state",
    573: "governing_transcript_state",
    574: "in_video_basis_state",
    575: "transcript_language_alignment_state",
    576: "terminology_fidelity_state",
    577: "question_scope_state",
    578: "safety_control_state",
    579: "task_mode_state",
    580: "prompt_affordance_state",
    581: "remediation_authority_state",
}
DOC_GLOBS = {n: next(DOCS.glob(f"{n}-*.md")) for n in PRINCIPAL_FIELDS}


def normalize_token(token: str) -> str:
    token = token.strip().lower()
    token = token.replace('-', '_').replace(' ', '_')
    token = re.sub(r'_+', '_', token)
    return token.strip('_')


def derive_allowed(docno: int) -> set[str]:
    field = PRINCIPAL_FIELDS[docno]
    text = DOC_GLOBS[docno].read_text(encoding='utf-8')
    pattern = re.compile(rf"{re.escape(field)}=<([^>]+)>")
    m = pattern.search(text)
    if not m:
        raise SystemExit(f"FAIL: could not find {field}=<...> in doc {docno}")
    vals = set()
    for raw in m.group(1).split('|'):
        tok = normalize_token(raw)
        if not tok or tok == 'other_bounded_class' or tok == 'other_saved_media_class':
            continue
        vals.add(tok)
    return vals

ALLOWED = {n: derive_allowed(n) for n in PRINCIPAL_FIELDS}


def check_pick_orders() -> list[str]:
    errs: list[str] = []
    for decl in ("header_pick_order", "detail_pick_order"):
        pat = re.compile(rf"(?m)^`{decl}=<([^>]+)>`$")
        for docno, path in DOC_GLOBS.items():
            text = path.read_text(encoding='utf-8')
            matches = pat.findall(text)
            if len(matches) > 1:
                errs.append(f"docs/{path.name}: multiple {decl} declarations")
                continue
            if not matches:
                continue
            seen: set[str] = set()
            toks = [normalize_token(x) for x in matches[0].split('|')]
            for tok in toks:
                if not tok:
                    errs.append(f"docs/{path.name}: empty token in {decl}")
                    continue
                if tok in seen:
                    errs.append(f"docs/{path.name}: duplicate token `{tok}` in {decl}")
                seen.add(tok)
                if tok not in ALLOWED[docno]:
                    sample = ', '.join(sorted(ALLOWED[docno]))
                    errs.append(f"docs/{path.name}: non-canonical {decl} token `{tok}`; allowed from doc {docno}: {sample}")
    return errs
TARGETS = [p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts]
COMP_RE = re.compile(r"(companions(?:_overflow|_detail)?)=((?:\d+:[a-z0-9_]+)(?:,\s*\d+:[a-z0-9_]+)*)")
LINE_COMP_RE = re.compile(r"^\s*(?:[-*]\s*)?`?(companions(?:_overflow|_detail)?)=((?:\d+:[a-z0-9_]+)(?:,\s*\d+:[a-z0-9_]+)*)`?\s*$")
TAG_RE = re.compile(r"(\d+):([a-z0-9_]+)")
MAX_COMPANION_TAGS = 3
AI_SPILL_ORDER = {562: 0, 570: 1, 581: 2, 572: 3, 575: 4, 576: 5, 573: 6, 563: 7, 580: 8, 577: 9, 579: 10, 578: 11, 571: 12, 565: 13, 567: 14, 564: 15, 566: 16, 574: 17, 568: 18, 569: 19}


def selection_priority(docno: int) -> tuple[int, int]:
    if 540 <= docno <= 561:
        return (0, docno)
    if docno in AI_SPILL_ORDER:
        return (1, AI_SPILL_ORDER[docno])
    return (2, docno)


def parse_doc_tokens(body: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for tag in [t.strip() for t in body.split(',') if t.strip()]:
        tm = TAG_RE.fullmatch(tag)
        if tm:
            out.append((int(tm.group(1)), tm.group(2)))
    return out


def check_companion_line(rel: str, full: str, field: str, body: str) -> list[str]:
    errs: list[str] = []
    tags = [t.strip() for t in body.split(',')]
    seen = set()
    docs = []
    limit = 1 if field == "companions_detail" else MAX_COMPANION_TAGS
    if len(tags) > limit:
        errs.append(f"{rel}: too many companion tags ({len(tags)} > {limit}) in `{full}`")
    for tag in tags:
        tm = TAG_RE.fullmatch(tag)
        if not tm:
            errs.append(f"{rel}: invalid companion tag syntax in {field}: {tag}")
            continue
        docno = int(tm.group(1))
        token = tm.group(2)
        docs.append(docno)
        if docno in seen:
            errs.append(f"{rel}: duplicate companion doc {docno} in `{full}`")
        seen.add(docno)
        if docno not in ALLOWED:
            errs.append(f"{rel}: unsupported companion doc {docno} in `{full}`")
            continue
        if token not in ALLOWED[docno]:
            sample = ', '.join(sorted(ALLOWED[docno]))
            errs.append(f"{rel}: non-canonical token `{docno}:{token}`; allowed from doc {docno}: {sample}")
    if docs != sorted(docs):
        errs.append(f"{rel}: {field} out of ascending doc order in `{full}`")
    return errs


def check_pair_selection(rel: str, header_body: str, overflow_body: str, context: str) -> list[str]:
    errs: list[str] = []
    header = parse_doc_tokens(header_body)
    overflow = parse_doc_tokens(overflow_body)
    if not header or not overflow:
        return errs
    header_docs = [doc for doc, _ in header]
    overflow_docs = [doc for doc, _ in overflow]
    dup = sorted(set(header_docs) & set(overflow_docs))
    if dup:
        errs.append(f"{rel}: duplicate companion docs across header/overflow {dup} in {context}; overflow is only for additional companion docs")
        return errs
    all_docs = header_docs + overflow_docs
    if len(all_docs) <= MAX_COMPANION_TAGS:
        errs.append(f"{rel}: unnecessary companions_overflow for {context}; total companion docs {len(all_docs)} fit in the header budget")
        return errs
    ordered = sorted(all_docs, key=selection_priority)
    expected_header = sorted(ordered[:MAX_COMPANION_TAGS])
    expected_overflow = sorted(ordered[MAX_COMPANION_TAGS:MAX_COMPANION_TAGS * 2])
    if header_docs != expected_header:
        errs.append(
            f"{rel}: companions header does not match deterministic selection order in {context}; "
            f"expected header docs {expected_header}, found {header_docs}"
        )
    if overflow_docs != expected_overflow:
        errs.append(
            f"{rel}: companions_overflow does not match deterministic selection order in {context}; "
            f"expected overflow docs {expected_overflow}, found {overflow_docs}"
        )
    return errs




def check_detail_selection(rel: str, carried_bodies: list[str], detail_body: str, context: str) -> list[str]:
    errs: list[str] = []
    detail = parse_doc_tokens(detail_body)
    if not detail:
        return errs
    if len(detail) > 1:
        errs.append(f"{rel}: companions_detail must contain at most one tag in {context}")
        return errs
    carried_map: dict[int, str] = {}
    for body in carried_bodies:
        for doc, tok in parse_doc_tokens(body):
            carried_map[doc] = tok
    for doc, tok in detail:
        if doc not in carried_map:
            errs.append(f"{rel}: companions_detail references doc {doc} that is not carried in header/overflow for {context}")
            continue
        if carried_map[doc] == tok:
            errs.append(f"{rel}: companions_detail duplicates carried token `{doc}:{tok}` in {context}")
    return errs

errors: list[str] = []
errors.extend(check_pick_orders())
for path in sorted(TARGETS):
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith('dist/') or rel.startswith('evidence/cache/'):
        continue
    text = path.read_text(encoding='utf-8', errors='ignore')
    for m in COMP_RE.finditer(text):
        field = m.group(1)
        body = m.group(2).strip()
        errors.extend(check_companion_line(rel, m.group(0), field, body))

    lines = text.splitlines()
    pending_header: tuple[int, str] | None = None
    pending_overflow: tuple[int, str] | None = None
    for idx, line in enumerate(lines, start=1):
        lm = LINE_COMP_RE.match(line)
        line_matches = {lm.group(1): lm.group(2).strip()} if lm else {}
        if not line_matches:
            if line.strip():
                pending_header = None
                pending_overflow = None
            continue

        if 'companions' in line_matches and 'companions_overflow' in line_matches:
            errors.extend(check_pair_selection(rel, line_matches['companions'], line_matches['companions_overflow'], f'line {idx}'))
            pending_header = (idx, line_matches['companions'])
            pending_overflow = (idx, line_matches['companions_overflow'])
        elif 'companions' in line_matches:
            pending_header = (idx, line_matches['companions'])
            pending_overflow = None
        elif 'companions_overflow' in line_matches:
            if pending_header is not None and idx == pending_header[0] + 1:
                errors.extend(check_pair_selection(rel, pending_header[1], line_matches['companions_overflow'], f'lines {pending_header[0]}-{idx}'))
                pending_overflow = (idx, line_matches['companions_overflow'])
            else:
                pending_header = None
                pending_overflow = None
        if 'companions_detail' in line_matches:
            carried_bodies: list[str] = []
            context = f'line {idx}'
            if 'companions' in line_matches:
                carried_bodies.append(line_matches['companions'])
                context = f'line {idx}'
            elif pending_header is not None and idx in (pending_header[0] + 1, pending_header[0] + 2):
                carried_bodies.append(pending_header[1])
                context = f'lines {pending_header[0]}-{idx}'
            if 'companions_overflow' in line_matches:
                carried_bodies.append(line_matches['companions_overflow'])
            elif pending_overflow is not None and idx == pending_overflow[0] + 1:
                carried_bodies.append(pending_overflow[1])
                context = f'lines {pending_header[0] if pending_header else pending_overflow[0]}-{idx}'
            if not carried_bodies:
                errors.append(f"{rel}: companions_detail without preceding carried companions in line {idx}")
            else:
                errors.extend(check_detail_selection(rel, carried_bodies, line_matches['companions_detail'], context))
            pending_header = None
            pending_overflow = None
            continue
        if line.strip() and 'companions_detail' not in line_matches and 'companions' not in line_matches and 'companions_overflow' not in line_matches:
            pending_header = None
            pending_overflow = None

if errors:
    print('FAIL: platform-media companion header tags')
    for e in errors:
        print(' -', e)
    sys.exit(2)

print('PASS: platform-media companion header tags')
