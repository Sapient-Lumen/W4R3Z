#!/usr/bin/env python3
"""Hash and normalize a BVPS evidence drop into a chain-of-custody ledger.

The tool deliberately does not adjudicate readiness. It records provenance inputs
and file hashes so a later reviewer can decide whether an artifact is admissible.
"""
from __future__ import annotations
import argparse, csv, hashlib, sys
from pathlib import Path

REQUIRED_META = ['filename','artifact_class','custodian_or_source','received_at','scope_jurisdiction','redaction_state','sensitivity_class','linked_request_id']
FORBIDDEN_STATES = {'readiness_closure','passed_exercise','certified_ready','local_readiness_proved'}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def read_sidecar(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_META if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit('FAIL sidecar_missing_columns=' + ','.join(missing))
        rows = {}
        for row in reader:
            name = (row.get('filename') or '').strip()
            if not name:
                raise SystemExit('FAIL sidecar_blank_filename')
            rows[name] = {k:(v or '').strip() for k,v in row.items()}
        return rows

def classify(meta: dict[str,str], fixture_mode: bool, errors: list[str]) -> str:
    if errors:
        return 'quarantined_needs_review'
    return 'candidate_fixture_only' if fixture_mode else 'candidate_received'

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--drop-dir', required=True)
    ap.add_argument('--sidecar', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--fixture-mode', action='store_true', help='Mark all rows as validator fixtures, not evidence.')
    ap.add_argument('--strict', action='store_true', help='Exit nonzero if any file is quarantined.')
    args = ap.parse_args()
    drop = Path(args.drop_dir)
    sidecar = Path(args.sidecar)
    out = Path(args.out)
    if not drop.exists() or not drop.is_dir():
        print('FAIL drop_dir_missing=' + str(drop))
        return 2
    if not sidecar.exists():
        print('FAIL sidecar_missing=' + str(sidecar))
        return 2
    meta_by_name = read_sidecar(sidecar)
    files = sorted([p for p in drop.iterdir() if p.is_file() and p.resolve() != sidecar.resolve()])
    rows=[]
    quarantined=0
    for p in files:
        meta = meta_by_name.get(p.name, {})
        errors=[]
        if not meta:
            errors.append('missing_sidecar_row')
        for col in REQUIRED_META:
            if not meta.get(col):
                errors.append('missing_' + col)
        lower_state_blob = ' '.join(meta.values()).lower()
        if any(fs in lower_state_blob for fs in FORBIDDEN_STATES):
            errors.append('forbidden_closure_language_in_sidecar')
        state = classify(meta, args.fixture_mode, errors)
        if state == 'quarantined_needs_review':
            quarantined += 1
        rows.append({
            'intake_row_id': f'INTAKE-0365-{len(rows)+1:03d}',
            'filename': p.name,
            'artifact_path': str(p.relative_to(drop.parent.parent.parent) if 'fixtures' in p.parts else p),
            'artifact_class': meta.get('artifact_class',''),
            'custodian_or_source': meta.get('custodian_or_source',''),
            'received_at': meta.get('received_at',''),
            'scope_jurisdiction': meta.get('scope_jurisdiction',''),
            'redaction_state': meta.get('redaction_state',''),
            'sensitivity_class': meta.get('sensitivity_class',''),
            'linked_request_id': meta.get('linked_request_id',''),
            'size_bytes': p.stat().st_size,
            'sha256': sha256(p),
            'packet_state': state,
            'fixture_only': 'yes' if args.fixture_mode else 'no',
            'claim_effect': 'candidate_fixture_no_readiness_closure' if args.fixture_mode else 'candidate_evidence_no_readiness_closure_until_adjudicated',
            'intake_errors': ';'.join(errors),
            'notes': meta.get('notes',''),
        })
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames=list(rows[0].keys()) if rows else ['intake_row_id','filename']
    with out.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)
    print(f'PASS intake rows={len(rows)} quarantined={quarantined} fixture_mode={args.fixture_mode} out={out}')
    return 1 if args.strict and quarantined else 0

if __name__ == '__main__':
    raise SystemExit(main())
