from pathlib import Path
import csv, sys
ROOT=Path(__file__).resolve().parents[1]
def rows(p):
    return list(csv.DictReader((ROOT/p).open(encoding='utf-8')))
idx=rows('cube/index.csv'); file=rows('cube/file.csv'); ffv=rows('cube/file-field-value.csv'); tags=rows('cube/file-tag-edge-normalized.csv')
idx_ids={r['id'] for r in idx}
file_ids={r['id'] for r in file}
ffv_ids={r['file_id'] for r in ffv}
tag_ids={r['file_id'] for r in tags}
if idx_ids-file_ids:
    raise SystemExit('file.csv missing ids: '+','.join(sorted(idx_ids-file_ids)))
if idx_ids-ffv_ids:
    raise SystemExit('file-field-value missing ids: '+','.join(sorted(idx_ids-ffv_ids)))
if '586' not in file_ids or '586' not in ffv_ids or '586' not in tag_ids:
    raise SystemExit('rev0379 tail id 586 not fully covered')
print(f'PASS normalization sync: index={len(idx_ids)} file={len(file_ids)} field_ids={len(ffv_ids)}')
