#!/usr/bin/env python3
"""Validate the rev0052 filing-field map layer.

This helper intentionally does not require a current upstream checkout. It checks that
rev0052 did not drift from the seven production-gated packet set and that every filing
field points to an included artifact. Optional source-bundle validation is still handled
by rev0051's helper.
"""
from __future__ import annotations
import csv, json, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'U-123', 'PB-01', 'SEARCH-RESP-01A', 'SEARCH-RESP-01B-BUDDY',
    'SEARCH-RESP-01C-ROOM', 'SEARCH-RESP-PARSE-BUDGET-A', 'SEARCH-RESP-PARSE-BUDGET-B'
}


def read_csv(rel):
    with (ROOT/rel).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def split_refs(value):
    return [p for p in value.split(';') if p]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def validate_manifest(rel):
    errors=[]
    manifest = ROOT/rel
    if not manifest.exists():
        return [f'missing manifest {rel}']
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        digest, file_rel = line.split('  ', 1)
        p = ROOT/file_rel
        if not p.exists():
            errors.append(f'missing manifest target {file_rel}')
            continue
        actual = sha256(p)
        if actual != digest:
            errors.append(f'hash mismatch {file_rel}')
    return errors


def main():
    errors=[]
    checks=[]
    fmap = read_csv('data/rev0052_filing_field_map.csv')
    packets = {r['packet'] for r in fmap}
    if packets != EXPECTED:
        errors.append(f'packet set mismatch: {sorted(packets)}')
    checks.append({'check':'packet set', 'status':'pass' if packets == EXPECTED else 'fail', 'count':len(fmap)})

    required_fields = [
        'primary_report','fix_skeleton','patch_basis','regression_artifacts','rerun_evidence',
        'claim_capsule','source_anchor_capsule','filing_field_capsule'
    ]
    missing=[]
    for row in fmap:
        for field in required_fields:
            refs = split_refs(row[field])
            if not refs:
                missing.append({'packet':row['packet'], 'field':field, 'path':'<empty>'})
            for ref in refs:
                if not (ROOT/ref).exists():
                    missing.append({'packet':row['packet'], 'field':field, 'path':ref})
        try:
            if int(row['source_anchor_rows']) <= 0:
                missing.append({'packet':row['packet'], 'field':'source_anchor_rows', 'path':row['source_anchor_rows']})
        except Exception:
            missing.append({'packet':row['packet'], 'field':'source_anchor_rows', 'path':row.get('source_anchor_rows','')})
    checks.append({'check':'artifact refs', 'status':'pass' if not missing else 'fail', 'missing':missing})
    errors.extend(f"missing {m['packet']} {m['field']} {m['path']}" for m in missing)

    # Inherited and new ledgers
    for rel, expected_count in [
        ('data/rev0050_claim_ledger.csv', 7),
        ('data/rev0051_source_anchor_summary.csv', 7),
        ('data/rev0052_source_freshness_spotcheck.csv', 6),
        ('data/rev0052_filing_field_refactor.csv', 5),
        ('data/rev0052_strict_promotions.csv', 7),
    ]:
        rows = read_csv(rel)
        ok = len(rows) == expected_count
        checks.append({'check':rel, 'status':'pass' if ok else 'fail', 'rows':len(rows), 'expected':expected_count})
        if not ok:
            errors.append(f'{rel} expected {expected_count} rows got {len(rows)}')

    # Evidence from inherited rev0051 helper should be present and passing.
    inherited = ROOT/'evidence/rev0052-inherited-source-anchor-helper-rerun.json'
    if not inherited.exists():
        errors.append('missing inherited rev0051 helper rerun evidence')
        checks.append({'check':'inherited helper evidence', 'status':'fail'})
    else:
        try:
            data=json.loads(inherited.read_text(encoding='utf-8'))
            ok=data.get('status') == 'pass'
            checks.append({'check':'inherited helper evidence', 'status':'pass' if ok else 'fail', 'summary':data.get('status')})
            if not ok:
                errors.append('inherited rev0051 helper did not pass')
        except Exception as exc:
            errors.append(f'inherited helper JSON parse failed: {exc}')
            checks.append({'check':'inherited helper evidence', 'status':'fail'})

    manifest_errors = validate_manifest('handoff/rev0052/MANIFEST.sha256')
    checks.append({'check':'rev0052 handoff manifest', 'status':'pass' if not manifest_errors else 'fail', 'errors':manifest_errors})
    errors.extend(manifest_errors)

    bad=[]
    for p in ROOT.rglob('*'):
        rel=str(p.relative_to(ROOT))
        if '__pycache__' in rel or '.pytest_cache' in rel or rel.startswith('source-trees') or rel.startswith('git-full') or '/.git/' in rel:
            bad.append(rel)
    checks.append({'check':'package hygiene', 'status':'pass' if not bad else 'fail', 'bad_count':len(bad), 'examples':bad[:10]})
    errors.extend(f'hygiene {x}' for x in bad)

    output={'revision':'rev0052','status':'pass' if not errors else 'fail','checks':checks,'errors':errors}
    print(json.dumps(output, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
