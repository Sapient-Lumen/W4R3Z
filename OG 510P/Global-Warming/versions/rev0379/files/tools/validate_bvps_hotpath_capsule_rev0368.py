#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAP=ROOT/'evidence-bags/bvps-hotpath-capsule-rev0368.zip'
MAN=ROOT/'cube/bvps-hotpath-capsule-manifest-rev0368.csv'
required={'575-nuclear-emergency-preparedness-sirenapproval-eofler-recordsqueue-refactor-compact-canon.md','cube/nuclear-emergency-bvps-ans-transition-admissibility-matrix-rev0368.csv','cube/nuclear-emergency-bvps-eof-ler-adams-watch-rev0368.csv','cube/nuclear-emergency-bvps-public-records-request-queue-rev0368.csv','cube/nuclear-emergency-bvps-closure-blocker-board-rev0368.csv','cube/datacube-rev0368-hotpath.sqlite'}
errors=[]
if not CAP.exists(): errors.append('missing_capsule_zip')
if not MAN.exists(): errors.append('missing_capsule_manifest')
if not errors:
    rows=list(csv.DictReader(MAN.open(newline='', encoding='utf-8')))
    m={r['inner_path']:r for r in rows}
    with zipfile.ZipFile(CAP) as z:
        names=[i.filename for i in z.infolist()]
        if len(names)!=len(set(names)): errors.append('duplicate_inner_paths')
        for req in required:
            if req not in names: errors.append('missing_required_inner:'+req)
        for info in z.infolist():
            data=z.read(info.filename)
            actual=hashlib.sha256(data).hexdigest()
            if info.filename not in m: errors.append('missing_manifest_row:'+info.filename)
            elif info.filename != 'cube/bvps-hotpath-capsule-manifest-rev0368.csv' and m[info.filename].get('sha256') != actual: errors.append('hash_mismatch:'+info.filename)
        if len(names)<25: errors.append('too_few_capsule_files')
if errors:
    print('FAIL hotpath_capsule_rev0368 ' + ';'.join(errors[:30])); sys.exit(1)
print(f'PASS hotpath_capsule_rev0368 files={len(names)} size_bytes={CAP.stat().st_size}')
