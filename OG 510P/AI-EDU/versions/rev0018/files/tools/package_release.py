import argparse
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser()
parser.add_argument('--timestamp', required=True)
parser.add_argument('--slug', required=True)
args = parser.parse_args()

receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
rev = receipt['revision']
bundle_name = f'AI-EDU-{rev}-{args.timestamp}-{args.slug}.zip'
bundle_path = ROOT.parent / bundle_name

manifest = {
    'project': 'AI-EDU',
    'revision': rev,
    'timestamp': args.timestamp,
    'slug': args.slug,
    'bundle': bundle_name,
    'status': 'packaged'
}
(ROOT / 'RELEASE-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

exclude = {bundle_name, '__pycache__'}
with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for path in ROOT.rglob('*'):
        if any(part in exclude for part in path.parts):
            continue
        if path.is_dir():
            continue
        zf.write(path, path.relative_to(ROOT).as_posix())

print(bundle_path)
