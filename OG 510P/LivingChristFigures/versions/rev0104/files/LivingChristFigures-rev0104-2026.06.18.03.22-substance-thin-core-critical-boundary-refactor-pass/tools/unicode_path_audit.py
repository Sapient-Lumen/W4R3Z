#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys, unicodedata
from collections import defaultdict
from pathlib import Path

FIELDS=['path_audit_id','check','severity','status','observed_count','affected_paths','detail']
MOJIBAKE_MARKERS=['Ã','Â','â€™','â€œ','â€�','â€“','â€”','�','├','║','┬','┤','─','╜','╖','╣']
MAC_JUNK={'.DS_Store','._.DS_Store'}


def rel_files(root: Path) -> list[str]:
    out=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file():
            continue
        rel=str(p.relative_to(root)).replace('\\','/')
        out.append(rel)
    return out


def add(rows, check, sev, status, affected, detail):
    rows.append({
        'path_audit_id': f'unicode_path_{len(rows)+1:03d}',
        'check': check,
        'severity': sev,
        'status': status,
        'observed_count': str(len(affected) if isinstance(affected, list) else affected),
        'affected_paths': '|'.join(affected[:24]) if isinstance(affected, list) else '',
        'detail': detail,
    })


def run(root: Path):
    rows=[]
    files=rel_files(root)
    non_nfc=[rel for rel in files if unicodedata.normalize('NFC', rel) != rel]
    add(rows,'paths_are_unicode_nfc','high' if non_nfc else 'info','fail' if non_nfc else 'pass',non_nfc,'All package-relative paths must be NFC-normalized to prevent ZIP/extraction drift' if non_nfc else 'All package-relative paths are NFC-normalized')

    moj=[rel for rel in files if any(marker in rel for marker in MOJIBAKE_MARKERS)]
    cp437=[]
    for rel in files:
        try:
            decoded=rel.encode('cp437').decode('utf-8')
            if decoded != rel and any(ord(ch)>127 for ch in decoded) and not any(marker in decoded for marker in MOJIBAKE_MARKERS):
                cp437.append(rel+' -> '+decoded)
        except Exception:
            pass
    if cp437:
        moj.extend([x.split(' -> ')[0] for x in cp437])
    add(rows,'paths_have_no_mojibake_or_replacement_chars','high' if moj else 'info','fail' if moj else 'pass',moj,'Mojibake/replacement-character markers or CP437/UTF-8 round-trip corruption risk found in package path(s)' if moj else 'No configured mojibake/replacement-character markers or CP437/UTF-8 round-trip risks appear in package paths')
    add(rows,'cp437_utf8_roundtrip_mojibake_detector','high' if cp437 else 'info','fail' if cp437 else 'pass',cp437,'Paths decode plausibly as CP437-misread UTF-8; rebuild archive or normalize path' if cp437 else 'No CP437/UTF-8 round-trip mojibake pattern detected')

    unsafe=[]
    controls=[]
    edge_space=[]
    mac=[]
    for rel in files:
        parts=rel.split('/')
        if rel.startswith('/') or '\\' in rel or '..' in parts or any(part=='' for part in parts):
            unsafe.append(rel)
        if any(any(ord(ch)<32 or ord(ch)==127 for ch in part) for part in parts):
            controls.append(rel)
        if any(part != part.strip() for part in parts):
            edge_space.append(rel)
        if any(part in MAC_JUNK or part.startswith('._') for part in parts):
            mac.append(rel)
    add(rows,'paths_are_package_relative_posix_safe','high' if unsafe else 'info','fail' if unsafe else 'pass',unsafe,'Unsafe absolute/traversal/backslash/empty path component detected' if unsafe else 'All paths are package-relative POSIX-style paths')
    add(rows,'paths_have_no_control_characters','high' if controls else 'info','fail' if controls else 'pass',controls,'Control characters detected in path(s)' if controls else 'No control characters detected in paths')
    add(rows,'path_components_have_no_edge_spaces','medium' if edge_space else 'info','review' if edge_space else 'pass',edge_space,'Leading/trailing spaces in path component(s)' if edge_space else 'No leading/trailing spaces in path components')
    add(rows,'no_mac_sidecar_artifacts','high' if mac else 'info','fail' if mac else 'pass',mac,'macOS sidecar/artifact files detected' if mac else 'No configured macOS sidecar artifacts detected')

    folded=defaultdict(list)
    for rel in files:
        folded[unicodedata.normalize('NFC', rel).casefold()].append(rel)
    dup=[]
    for vals in folded.values():
        if len(vals)>1:
            dup.extend(vals)
    add(rows,'no_casefold_or_normalized_duplicate_paths','high' if dup else 'info','fail' if dup else 'pass',sorted(dup),'Paths collide after NFC/casefold normalization' if dup else 'No path collisions after NFC/casefold normalization')

    # Preserve non-ASCII names, but count them so reviewers can see Unicode exposure intentionally.
    non_ascii=[rel for rel in files if any(ord(ch)>127 for ch in rel)]
    add(rows,'unicode_path_exposure_inventory','info','pass',non_ascii,f'{len(non_ascii)} file path(s) contain non-ASCII characters; exposure is inventoried and allowed when NFC/no-mojibake checks pass')
    return rows


def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Unicode-Path-Audit-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Unicode-Path-Audit-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    high=sum(1 for r in rows if r.get('severity')=='high'); nonpass=sum(1 for r in rows if r.get('status') not in {'pass'})
    lines=['# Unicode Path Audit — current','', 'Generated by `tools/unicode_path_audit.py`.', '', f'High findings: {high}', f'Non-pass rows: {nonpass}', '', 'This audit prevents a repeat of filename-encoding drift: package paths must be NFC-normalized, package-relative, free of configured mojibake markers, and non-colliding after Unicode/casefold normalization.', '', '| check | severity | status | count | detail |','|---|---|---|---:|---|']
    for r in rows:
        detail=(r.get('detail','') or '').replace('|','/').replace('\n',' ')
        lines.append(f"| {r['check']} | {r['severity']} | {r['status']} | {r['observed_count']} | {detail} |")
    (out/'Unicode-Path-Audit-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    high=[r for r in rows if r.get('severity')=='high']
    print(f"{'FAIL' if high else 'PASS'} unicode path audit checks={len(rows)} high={len(high)}")
    for r in high[:20]: print(f"HIGH {r['check']}: {r['affected_paths']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
