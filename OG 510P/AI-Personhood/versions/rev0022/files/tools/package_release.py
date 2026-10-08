import argparse
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--timestamp', required=True)
parser.add_argument('--slug', required=True)
args = parser.parse_args()

rev = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
bundle_name = f'AI-Personhood-{rev}-{args.timestamp}-{args.slug}.zip'
bundle_path = ROOT.parent / bundle_name

manifest = {
    'project': 'AI-Personhood',
    'revision': rev,
    'timestamp': args.timestamp,
    'slug': args.slug,
    'bundle': bundle_name
}
(ROOT / 'RELEASE-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(ROOT.rglob('*')):
        if path.is_dir():
            continue
        if '__pycache__' in path.parts:
            continue
        zf.write(path, path.relative_to(ROOT).as_posix())

print(bundle_path)
