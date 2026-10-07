#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS = ['freshness_id','surface_path','surface_kind','check','expected_value','observed_value','severity','status','note']
EXPORT_FIELDS = ['export_name_without_zip','package_export_name_without_zip','package_export_name','package_export','package_name_without_zip','root_directory','package_root_directory','generated_from_package']
REV_FIELDS = ['revision','package_revision','revision_updated']
FRONT_DOOR = [
    '000-START-HERE.txt','CURRENT-SPINE.md','DATA-CARD-current.md','META/Data-Card-current.md',
    'CUBE-MAP.md','LivingChristFigures.txt','PUBLIC/README-public-edition.md',
    'SIGNATURE-STATUS-current.md','SIGNATURE-READINESS-current.md',
]
IDENTITY_JSON = [
    'manifest.json','datapackage.json','BUILD-PROVENANCE-current.json',
    'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json',
]
CURRENT_REV_PATTERNS = [
    re.compile(r'Current revision:\s*(rev\d{4})', re.I),
    re.compile(r'current package revision\s*(?:is|:)\s*(rev\d{4})', re.I),
    re.compile(r'package_revision["\s:=]+(rev\d{4})', re.I),
    re.compile(r'revision_updated["\s:=]+(rev\d{4})', re.I),
]


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def add(rows, rel, kind, check, expected, observed, severity, status, note):
    rows.append({
        'freshness_id': f'fresh_{len(rows)+1:04d}',
        'surface_path': rel,
        'surface_kind': kind,
        'check': check,
        'expected_value': str(expected),
        'observed_value': str(observed),
        'severity': severity,
        'status': status,
        'note': note,
    })


def stale_current_mentions(body: str, current_rev: str) -> list[str]:
    found=[]
    for pat in CURRENT_REV_PATTERNS:
        for m in pat.finditer(body):
            token=m.group(1)
            if token != current_rev:
                found.append(token)
    return sorted(set(found))


def run(root: Path):
    rows=[]
    manifest=read_json(root/'manifest.json') or {}
    current_rev=str(manifest.get('revision',''))
    export=str(manifest.get('export_name_without_zip',''))
    date=str(manifest.get('date',''))
    pass_type=str(manifest.get('pass_type',''))
    add(rows,'manifest.json','identity_json','manifest_revision_present','rev#### current revision',current_rev,'high','pass' if re.fullmatch(r'rev\d{4}', current_rev) else 'fail','manifest must carry a parseable current revision token')
    add(rows,'package root','filesystem','root_matches_manifest_export',export,root.name,'high','pass' if export and root.name==export else 'fail','package root folder must equal manifest export name')

    for rel in IDENTITY_JSON:
        path=root/rel
        obj=read_json(path)
        if not isinstance(obj, dict):
            add(rows,rel,'identity_json','json_parse','object','missing or invalid','high','fail','identity surface must be valid JSON')
            continue
        for field in REV_FIELDS:
            if field in obj:
                observed=obj.get(field,'')
                add(rows,rel,'identity_json',f'{field}_matches_manifest',current_rev,observed,'high','pass' if observed==current_rev else 'fail',f'{field} must be current, not inherited from a previous package')
        for field in EXPORT_FIELDS:
            if field in obj:
                observed=obj.get(field,'')
                add(rows,rel,'identity_json',f'{field}_matches_root',export,observed,'high','pass' if observed==export else 'fail',f'{field} must point to this package export name')
        release_text='\n'.join(str(obj.get(k,'')) for k in ['title','description','release_note','central_sentence','notes',f'{current_rev}_note'])
        add(rows,rel,'identity_json','release_text_mentions_current_revision',current_rev,'present' if current_rev in release_text else 'missing','high','pass' if current_rev in release_text else 'fail','release-facing machine text must mention the current revision')
        stale=stale_current_mentions(release_text, current_rev)
        add(rows,rel,'identity_json','release_text_has_no_stale_current_claims',f'no stale current-revision tokens other than history labels; current={current_rev}','|'.join(stale) if stale else 'none','high','pass' if not stale else 'fail','old revision notes may exist, but current-claim phrasing must not point to an older revision')

    for rel in FRONT_DOOR:
        path=root/rel
        if not path.exists():
            add(rows,rel,'front_door_text','front_door_exists','present','missing','high','fail','required front-door surface is missing')
            continue
        body=path.read_text(encoding='utf-8', errors='ignore')
        add(rows,rel,'front_door_text','front_door_mentions_current_revision',current_rev,'present' if current_rev in body else 'missing','high','pass' if current_rev in body else 'fail','front-door text must identify the current revision')
        signal=pass_type.replace('_','-')
        observed='present' if (pass_type and pass_type.replace('_',' ')[:24].lower() in body.lower()) or (signal and any(tok in body.lower() for tok in signal.split('-')[:3])) else 'missing'
        add(rows,rel,'front_door_text','front_door_mentions_current_pass_shape',pass_type,observed,'high','pass' if observed=='present' else 'fail','front-door text must describe the current pass shape, not only inherited history')
        stale=stale_current_mentions(body, current_rev)
        add(rows,rel,'front_door_text','front_door_has_no_stale_current_claims',current_rev,'|'.join(stale) if stale else 'none','high','pass' if not stale else 'fail','stale current-revision phrases were the concrete rev0085/rev0093 failure class')

    handoff_rows=read_csv(root/'META/Handoff-Review-Digest-current.csv')
    topics={r.get('topic',''):r.get('value','') for r in handoff_rows}
    add(rows,'META/Handoff-Review-Digest-current.csv','review_digest','digest_revision_matches_manifest',current_rev,topics.get('revision',''),'high','pass' if topics.get('revision','')==current_rev else 'fail','handoff digest must not pass if it advertises an old revision')
    add(rows,'META/Handoff-Review-Digest-current.csv','review_digest','digest_export_matches_manifest',export,topics.get('export_name_without_zip',''),'high','pass' if topics.get('export_name_without_zip','')==export else 'fail','handoff digest export pointer must match manifest export name')

    fp=read_json(root/'META/Previous-Release-Fingerprint-current.json') or {}
    fp_md_path=root/'META/Previous-Release-Fingerprint-current.md'
    fp_md=fp_md_path.read_text(encoding='utf-8', errors='ignore') if fp_md_path.exists() else ''
    prev_rev=str(manifest.get('previous_revision',''))
    prev_export=str(manifest.get('previous_export_name_without_zip',''))
    prev_zip=str(manifest.get('previous_zip_name',''))
    prev_sha=str(manifest.get('previous_zip_sha256',''))
    add(rows,'META/Previous-Release-Fingerprint-current.json','previous_fingerprint','fingerprint_recorded_at_revision_matches_manifest',current_rev,fp.get('fingerprint_recorded_at_revision',''),'high','pass' if fp.get('fingerprint_recorded_at_revision','')==current_rev else 'fail','previous-release fingerprint must be recorded for the current package revision')
    for field,expected in [('baseline_revision',prev_rev),('baseline_export_name_without_zip',prev_export),('baseline_zip_name',prev_zip),('baseline_zip_sha256',prev_sha)]:
        observed=str(fp.get(field,''))
        add(rows,'META/Previous-Release-Fingerprint-current.json','previous_fingerprint',f'{field}_matches_manifest_previous',expected,observed,'high','pass' if expected and observed==expected else 'fail','previous-release JSON fingerprint must match manifest previous-release identity')
        md_status='pass' if observed and observed in fp_md else 'fail'
        add(rows,'META/Previous-Release-Fingerprint-current.md','previous_fingerprint_markdown',f'{field}_mirrored_from_json',observed,'present' if md_status=='pass' else 'missing_or_stale','high',md_status,'reviewer-facing previous-release fingerprint summary must mirror machine JSON, not stale older baselines')
    stable_count=str(fp.get('stable_file_count',''))
    add(rows,'META/Previous-Release-Fingerprint-current.md','previous_fingerprint_markdown','stable_file_count_mirrored_from_json',stable_count,'present' if stable_count and stable_count in fp_md else 'missing_or_stale','high','pass' if stable_count and stable_count in fp_md else 'fail','previous-release fingerprint Markdown summary must mirror JSON stable-file count')

    add(rows,'QA-REPORT-current.txt','qa_transcript','qa_current_report_deferred_to_final_qa','final QA transcript','excluded from freshness inputs','info','pass','QA-REPORT-current.txt is final-run evidence and is excluded from current-surface freshness gating to avoid a self-referential proof loop')


    if date:
        add(rows,'manifest.json','identity_json','manifest_date_current_release_day',date,date,'info','pass','release date recorded for human review; clock freshness is governed by filename/timestamp fields')
    return rows


def write_reports(root: Path, rows):
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Current-Surface-Freshness-Audit-current.csv',
        fields=FIELDS,
        rows=rows,
        title='Current Surface Freshness Audit',
        generated_by='tools/current_surface_freshness_audit.py',
        columns=['surface_path','check','severity','status','expected_value','observed_value','note'],
        intro_lines=[
            f"High failures: {sum(1 for r in rows if r.get('severity')=='high' and r.get('status')!='pass')}",
            'This audit targets the concrete failure class found in prior passes: stale current/proof surfaces that otherwise look gate-clean.',
        ],
    )


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} current surface freshness rows={len(rows)} high_fail={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r['surface_path']} {r['check']}: {r['observed_value']}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__ == '__main__': main()
