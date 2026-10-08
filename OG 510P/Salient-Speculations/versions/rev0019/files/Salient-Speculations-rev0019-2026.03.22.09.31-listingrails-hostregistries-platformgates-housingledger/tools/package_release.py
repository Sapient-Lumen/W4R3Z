#!/usr/bin/env python3
from pathlib import Path
import argparse, json, zipfile, hashlib

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--timestamp', required=True)
parser.add_argument('--slug', required=True)
args = parser.parse_args()

manifest = json.loads((root / 'MANIFEST.json').read_text(encoding='utf-8'))
rev = manifest['revision']
base = f'Salient-Speculations-{rev}-{args.timestamp}-{args.slug}'
out = root.parent / f'{base}.zip'
sha_path = root.parent / f'{base}.sha256'

release_manifest = {
    'bundle': out.name,
    'revision': rev,
    'timestamp': args.timestamp,
    'slug': args.slug
}
(root / 'RELEASE-MANIFEST.json').write_text(json.dumps(release_manifest, indent=2) + '\n', encoding='utf-8')

with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(root.rglob('*')):
        if path.is_dir():
            continue
        zf.write(path, arcname=f'{base}/{path.relative_to(root)}')

sha256 = hashlib.sha256(out.read_bytes()).hexdigest()
sha_path.write_text(f'{sha256}  {out.name}\n', encoding='utf-8')
print(out)
print('sha256:', sha256)
print('sha256_file:', sha_path)
