#!/usr/bin/env python3
"""Audit package waste signals after rev0365 intake/field-kit refactor."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib, json
ROOT = Path(__file__).resolve().parents[1]
risky={'.exe','.vbs','.ps1','.docm','.xlsm','.lnk','.eml','.msg','.7z'}
def sha256_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()
files=[p for p in ROOT.rglob('*') if p.is_file()]
ext_counts=Counter(p.suffix.lower() or '[no_ext]' for p in files)
by_hash=defaultdict(list)
for p in files:
    try: by_hash[(p.stat().st_size, sha256_file(p))].append(p)
    except OSError: pass
dups=[grp for grp in by_hash.values() if len(grp)>1]
wasted=sum((len(grp)-1)*grp[0].stat().st_size for grp in dups)
actual_risky=[str(p.relative_to(ROOT)) for p in files if p.suffix.lower() in risky and ('fixtures' in p.parts or 'quarantine' in p.parts)]
rev0365_fieldkit=ROOT/'field-kits/bvps-rev0365'
rev0365_fieldkit_files=[p for p in rev0365_fieldkit.rglob('*') if p.is_file()] if rev0365_fieldkit.exists() else []
print(json.dumps({
  'file_count': len(files),
  'extension_top10': ext_counts.most_common(10),
  'duplicate_content_groups': len(dups),
  'duplicate_content_files': sum(len(g) for g in dups),
  'duplicate_wasted_bytes': wasted,
  'actual_risky_fixture_paths': actual_risky,
  'rev0365_fieldkit_file_count': len(rev0365_fieldkit_files),
  'largest_files': [(str(p.relative_to(ROOT)), p.stat().st_size) for p in sorted(files, key=lambda x: x.stat().st_size, reverse=True)[:10]],
}, indent=2))
