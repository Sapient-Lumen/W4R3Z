#!/usr/bin/env python3
"""Audit cloudtainer/package waste signals for the extracted datacube."""
from pathlib import Path
from collections import Counter, defaultdict
import csv, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {'.git'}

def sha256_file(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

files = [p for p in ROOT.rglob('*') if p.is_file() and not any(part in EXCLUDE for part in p.parts)]
ext_counts = Counter(p.suffix.lower() or '[no_ext]' for p in files)
by_hash = defaultdict(list)
for p in files:
    try:
        by_hash[(p.stat().st_size, sha256_file(p))].append(p)
    except OSError:
        pass
dups = [grp for grp in by_hash.values() if len(grp) > 1]
wasted = sum((len(grp)-1)*grp[0].stat().st_size for grp in dups)
print(json.dumps({
    'file_count': len(files),
    'extension_top10': ext_counts.most_common(10),
    'duplicate_content_groups': len(dups),
    'duplicate_content_files': sum(len(g) for g in dups),
    'duplicate_wasted_bytes': wasted,
    'largest_files': [(str(p.relative_to(ROOT)), p.stat().st_size) for p in sorted(files, key=lambda x: x.stat().st_size, reverse=True)[:10]],
}, indent=2))
