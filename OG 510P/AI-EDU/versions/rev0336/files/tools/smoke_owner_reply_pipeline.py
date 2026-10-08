#!/usr/bin/env python3
"""Run a local FT-0181 owner-reply intake smoke test.

The smoke path proves the triage -> proceed-staged-note handoff is runnable
without treating the synthetic fixture as owner evidence. It is intentionally
narrow: it accepts only a CSV that triages to PROCEED-STAGED, emits a staging
note or summary, and refuses to upgrade source truth, close FT-0181, or create
public claims.
"""
import argparse
import hashlib
import json
from pathlib import Path

from stage_owner_reply_csv import staged_note
from triage_owner_reply_csv import triage_csv

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / 'fixtures' / 'owner-reply-pipeline' / 'ft0181-proceed-staged-smoke.csv'
DEFAULT_NEXT = 'docs/30-operations/ft0181-owner-packet-workbench.md'
ARCHIVE_OUTPUT_BLOCK_ROOTS = {'docs', 'examples', 'fixtures', 'schemas', 'templates', 'tools'}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def row_count(path: Path) -> int:
    # Subtract the CSV header. This intentionally avoids parsing owner content.
    return max(0, sum(1 for _ in path.open(encoding='utf-8')) - 1)


def is_archive_output_path(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return False
    return bool(rel.parts) and rel.parts[0] in ARCHIVE_OUTPUT_BLOCK_ROOTS


def smoke_pipeline(csv_path: Path = DEFAULT_FIXTURE, output_note: Path | None = None):
    path = csv_path if csv_path.is_absolute() else ROOT / csv_path
    result = triage_csv(path, allow_src0_smoke=True)
    if result.get('outcome') != 'PROCEED-STAGED':
        return {
            'ok': False,
            'source_truth_class': 'SRC0-SMOKE' if 'fixtures/' in path.as_posix() else 'UNVERIFIED-LOCAL',
            'fixture_path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix(),
            'outcome': result.get('outcome'),
            'next_action': result.get('next_action'),
            'reasons': result.get('reasons', []),
            'message': 'Owner-reply smoke path accepts only PROCEED-STAGED CSVs; route this outcome without opening the workbench.',
        }

    note = staged_note(path, allow_src0_smoke=True)
    if output_note:
        out = output_note if output_note.is_absolute() else ROOT / output_note
        if is_archive_output_path(out):
            return {
                'ok': False,
                'source_truth_class': 'SRC0-SMOKE',
                'fixture_path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix(),
                'outcome': 'SMOKE-OUTPUT-BLOCKED',
                'message': 'Smoke-generated notes cannot be written into archive-controlled dirs such as docs, examples, fixtures, schemas, templates, or tools.',
                'claim_ceiling': 'Smoke output may be written only to a temporary/scratch location and is not evidence.',
            }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(note + '\n', encoding='utf-8')
        output_rel = out.relative_to(ROOT).as_posix() if out.is_relative_to(ROOT) else out.as_posix()
    else:
        output_rel = None

    return {
        'ok': True,
        'source_truth_class': 'SRC0-SMOKE',
        'fixture_path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix(),
        'row_count': row_count(path),
        'outcome': result.get('outcome'),
        'next_action': result.get('next_action'),
        'generated_note_sha256': sha256_text(note),
        'output_note_path': output_rel,
        'next_artifact': DEFAULT_NEXT,
        'claim_ceiling': 'Smoke proves executable intake plumbing only; it is not real owner evidence, not SRC2+, not closure evidence, and not a public effectiveness claim.',
        'do_not': [
            'do not copy the synthetic fixture into evidence custody',
            'do not close FT-0181 from smoke output',
            'do not publish learning, safety, access, workload, compliance, scale, or effectiveness claims',
            'do not widen the owner request because the smoke path passed',
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Smoke-test the FT-0181 owner-reply triage and staging path with a local CSV.')
    parser.add_argument('--csv-path', type=Path, default=DEFAULT_FIXTURE, help='CSV to triage and stage. Defaults to the SRC0 synthetic smoke fixture.')
    parser.add_argument('--output-note', type=Path, help='Optional path to write the generated proceed-staged note.')
    parser.add_argument('--json', action='store_true', help='Emit machine-readable JSON only.')
    args = parser.parse_args(argv)

    result = smoke_pipeline(args.csv_path, args.output_note)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"ok: {str(result['ok']).lower()}")
        print(f"source_truth_class: {result['source_truth_class']}")
        print(f"outcome: {result.get('outcome')}")
        print(f"fixture_path: {result.get('fixture_path')}")
        if result.get('generated_note_sha256'):
            print(f"generated_note_sha256: {result['generated_note_sha256']}")
        if result.get('output_note_path'):
            print(f"output_note_path: {result['output_note_path']}")
        print(f"claim_ceiling: {result.get('claim_ceiling') or result.get('message')}")
    return 0 if result.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
