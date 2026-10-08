#!/usr/bin/env python3
"""Lightweight source probe helper for external Nicotine+ source lanes.

Set NICOTINE_DEV_SOURCE_TREES to the directory containing:
  github-tag-3.3.10/
  github-branch-3.3.x/
  github-branch-master/

Example:
  NICOTINE_DEV_SOURCE_TREES=/path/to/source-trees tools/source_probe_batch.py FileSearchResponse
"""
import argparse, os, pathlib, subprocess, sys

parser = argparse.ArgumentParser()
parser.add_argument('patterns', nargs='+')
parser.add_argument('--source-trees', default=os.environ.get('NICOTINE_DEV_SOURCE_TREES'))
args = parser.parse_args()
if not args.source_trees:
    raise SystemExit('Set --source-trees or NICOTINE_DEV_SOURCE_TREES')
base = pathlib.Path(args.source_trees)
lanes = ['github-tag-3.3.10','github-branch-3.3.x','github-branch-master']
for lane in lanes:
    root = base / lane
    print(f'## {lane}')
    if not root.exists():
        print('missing')
        continue
    for pat in args.patterns:
        print(f'### pattern: {pat}')
        try:
            out = subprocess.run(['rg','-n',pat,str(root/'pynicotine')], check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
            print(out.stdout[:8000] or '(no matches)')
        except Exception as exc:
            print(f'ERROR: {exc}')
