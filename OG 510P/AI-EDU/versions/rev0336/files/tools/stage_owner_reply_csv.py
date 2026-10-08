#!/usr/bin/env python3
"""Create a minimized FT-0181 proceed-staged note from a real owner CSV.

The normal CLI deliberately refuses SRC0 smoke fixtures. Synthetic fixtures are
only allowed through smoke_owner_reply_pipeline.py, which opts in explicitly and
labels the generated note as non-evidence.
"""
import argparse
import csv
import json
import hashlib
from pathlib import Path

from ft0181_field_guards import operator_today_iso, output_allowed, returned_owner_csv_source_block, returned_owner_csv_source_truth_class
from triage_owner_reply_csv import triage_csv

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / 'fixtures'
EXPECTED_COLUMNS = ['row_id', 'required_owner_reply', 'owner_response', 'local_only_check', 'intake_note']
ROW_LABELS = {
    '1': 'Selected service / owner path / source / date range',
    '2': 'Aggregate workflow counts',
    '3': 'Action boundary',
    '4': 'Fallback / rollback / stop condition',
    '5': 'Workload signal',
    '6': 'Training or use guidance',
    '7': 'Public claim ceiling',
    '8': 'Redaction and owner attestation',
}
TEMPLATE_PATH = 'templates/ft0181-proceed-staged-note-template.md'
NEXT_WORKBENCH = 'docs/30-operations/ft0181-owner-packet-workbench.md'
SMOKE_LABELS = [
    'synthetic smoke fixture',
    'not a returned owner packet',
    'not src2+ evidence',
    'not closure evidence',
]
ARCHIVE_OUTPUT_BLOCK_ROOTS = {'docs', 'examples', 'fixtures', 'schemas', 'templates', 'tools'}


def relative_to_root(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()




def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def load_rows(path: Path):
    with path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    return reader.fieldnames or [], rows


def clean(value: str) -> str:
    text = (value or '').strip()
    if not text:
        return '[blank]'
    return ' '.join(text.split())


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def is_archive_output_path(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return True
    return rel.parts[0] in ARCHIVE_OUTPUT_BLOCK_ROOTS or len(rel.parts) == 1


def has_smoke_labels(rows) -> bool:
    joined = ' '.join((row.get('owner_response') or '').lower() for row in rows)
    return any(label in joined for label in SMOKE_LABELS)


def source_truth_class(path: Path, rows, allow_src0_smoke: bool = False) -> str:
    src_class = returned_owner_csv_source_truth_class(path, archive_root=ROOT, allow_src0_smoke=allow_src0_smoke)
    if src_class == 'UNVERIFIED-OWNER-REPLY' and has_smoke_labels(rows):
        return 'SRC0-SMOKE'
    return src_class


def staged_note(path: Path, allow_src0_smoke: bool = False) -> str:
    fieldnames, rows = load_rows(path)
    if fieldnames != EXPECTED_COLUMNS:
        raise ValueError('CSV columns changed between triage and staging')

    src_class = source_truth_class(path, rows, allow_src0_smoke=allow_src0_smoke)
    if src_class == 'SRC0-SMOKE' and not allow_src0_smoke:
        raise ValueError(json.dumps({
            'outcome': 'SRC0-STAGING-BLOCKED',
            'source_truth_class': src_class,
            'csv_path': relative_to_root(path),
            'message': 'Synthetic smoke fixtures cannot be staged by the normal staging CLI. Use tools/smoke_owner_reply_pipeline.py for plumbing checks only; do not copy smoke output into evidence, docs, examples, or release records.',
            'next_action': {
                'outcome': 'SRC0-STAGING-BLOCKED',
                'next_artifact': 'tools/smoke_owner_reply_pipeline.py',
                'ceiling': 'Smoke-only execution check; not real owner evidence, not SRC2+, and not closure material.',
            },
        }, indent=2))
    source_block = returned_owner_csv_source_block(path, archive_root=ROOT, allow_src0_smoke=allow_src0_smoke)
    if source_block:
        raise ValueError(json.dumps({
            'outcome': 'RETURNED-CSV-SOURCE-BLOCKED',
            'source_truth_class': src_class,
            'csv_path': relative_to_root(path),
            'message': f'Archive-controlled CSV source is not a returned owner packet ({source_block}). Route a local scratch/external returned CSV through make owner-field-next before staging.',
            'next_action': {
                'outcome': 'RETURNED-CSV-SOURCE-BLOCKED',
                'next_artifact': 'tools/decide_ft0181_field_next_action.py',
                'ceiling': 'No staging from archive-controlled CSV sources; not evidence, not SRC2+, and not closure material.',
            },
        }, indent=2))

    result = triage_csv(path, allow_src0_smoke=allow_src0_smoke)
    if result.get('outcome') != 'PROCEED-STAGED':
        raise ValueError(json.dumps({
            'outcome': result.get('outcome'),
            'next_action': result.get('next_action'),
            'reasons': result.get('reasons', []),
            'message': 'Only PROCEED-STAGED owner replies can be converted into a staging note.',
        }, indent=2))

    responses = {row.get('row_id', '').strip(): clean(row.get('owner_response', '')) for row in rows}
    source_line = relative_to_root(path)
    lines = [
        '# FT-0181 proceed-staged owner reply note',
        '',
        f'Date staged: {operator_today_iso()}',
        f'Source CSV: {source_line}',
        f'Source CSV SHA-256: {sha256_file(path)}',
        f'Source truth class at staging: {src_class}',
        'Triage outcome: PROCEED-STAGED',
        f'Staging template: {TEMPLATE_PATH}',
        f'Next artifact: {NEXT_WORKBENCH}',
        '',
    ]
    if src_class == 'SRC0-SMOKE':
        lines.extend([
            'Synthetic smoke fixture: this generated note is a plumbing rehearsal only. It is not a returned owner packet, not `SRC2+` evidence, not closure evidence, not proof of learning, and must not be copied into evidence custody, public summaries, release records, or workbench fields.',
            '',
        ])
    else:
        lines.extend([
            'This note is a minimized staging artifact generated from a triaged eight-row owner reply. It is not closure evidence, not a public summary, and not proof of learning, safety, access, workload reduction, compliance, scale, or effectiveness. `FT-0181` remains live until a real `SRC2+` packet is custody-staged, normalized, accepted, rendered safely, given lifecycle treatment, signed off, and recorded in closure-ready minutes.',
            '',
        ])

    lines.extend([
        '## Staged row answers',
        '',
        '| Row | Staging slot | Minimized owner answer |',
        '|---|---|---|',
    ])
    for rid in [str(i) for i in range(1, 9)]:
        answer = responses.get(rid, '[missing]')
        answer = answer.replace('|', '\\|')
        lines.append(f'| {rid} | {ROW_LABELS[rid]} | {answer} |')

    lines.extend([
        '',
        '## Workbench copy rule',
        '',
        '- Copy only the minimized answers above into `docs/30-operations/ft0181-owner-packet-workbench.md` after confirming the source is a real owner reply, not a smoke fixture.',
        '- Do not add raw learner data, protected facts, small cells, security payloads, screenshots, vendor dashboards, or new source systems.',
        '- Do not add public claims beyond the row 7 ceiling.',
        '- Treat source truth as candidate `SRC2+` only after downstream custody, dictionary, import-map, acceptance, public-summary, lifecycle, signoff, closeout, and closure checklist gates pass.',
        '',
        '## Generated triage summary',
        '',
    ])
    for reason in result.get('reasons', []):
        lines.append(f'- {reason}')
    lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Convert a PROCEED-STAGED FT-0181 owner reply CSV into a minimized staging note.')
    parser.add_argument('csv_path', type=Path)
    parser.add_argument('--output', type=Path, help='Optional path to write the staging note. Defaults to stdout.')
    parser.add_argument('--allow-src0-smoke', action='store_true', help='Internal smoke-harness opt-in only. Do not use for real owner staging.')
    args = parser.parse_args(argv)
    try:
        note = staged_note(args.csv_path, allow_src0_smoke=args.allow_src0_smoke)
    except ValueError as exc:
        print(str(exc))
        return 2
    if args.output:
        out = args.output if args.output.is_absolute() else ROOT / args.output
        allowed, output_boundary = output_allowed(out, archive_root=ROOT)
        if not allowed:
            print(json.dumps({
                'outcome': 'STAGING-OUTPUT-BLOCKED',
                'output_boundary': output_boundary,
                'message': 'Owner-reply staging notes are local/scratch artifacts and cannot be written into the release archive outside scratch or to controlled release surfaces.',
                'claim_ceiling': 'Staging note only; not SRC2+ acceptance, not custody evidence, not closure evidence, and not public claim support.',
            }, indent=2))
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(note + '\n', encoding='utf-8')
        print(out.as_posix())
    else:
        print(note)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
