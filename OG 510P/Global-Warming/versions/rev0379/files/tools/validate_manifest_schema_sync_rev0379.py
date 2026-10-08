from pathlib import Path
import filecmp, json, sys
ROOT=Path(__file__).resolve().parents[1]
for name in ['manifest.json','schema.json','validation-rules.json']:
    a=ROOT/name; b=ROOT/'cube'/name
    if not a.exists() or not b.exists():
        raise SystemExit(f'missing {name} mirror')
    if a.read_bytes()!=b.read_bytes():
        raise SystemExit(f'{name} differs between root and cube')
print('PASS manifest/schema/rules mirrors synced')
