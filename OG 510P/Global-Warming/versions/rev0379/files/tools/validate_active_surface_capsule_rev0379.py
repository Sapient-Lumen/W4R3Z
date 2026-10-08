from pathlib import Path
import zipfile, csv, sys
ROOT=Path(__file__).resolve().parents[1]
cap=ROOT/'evidence-bags/bvps-dispatch-intake-capsule-rev0379.zip'
manifest=ROOT/'cube/bvps-dispatch-intake-capsule-manifest-rev0379.csv'
if not cap.exists():
    raise SystemExit('missing active surface capsule')
if not manifest.exists():
    raise SystemExit('missing active surface capsule manifest')
rows=list(csv.DictReader(manifest.open(encoding='utf-8')))
with zipfile.ZipFile(cap) as z:
    names=set(z.namelist())
missing=[r['path'] for r in rows if r['path'] not in names]
if missing:
    raise SystemExit('capsule missing manifest paths: '+','.join(missing[:10]))
if len(rows) < 40:
    raise SystemExit(f'capsule too small or manifest incomplete: {len(rows)}')
print(f'PASS active surface capsule: {len(rows)} entries')
