import argparse
import hashlib
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser()
parser.add_argument('--timestamp', required=True)
parser.add_argument('--slug', required=True)
args = parser.parse_args()

receipt_path = ROOT / 'REVISION_RECEIPT.json'
receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
rev = receipt['revision']
bundle_name = f'AI-EDU-{rev}-{args.timestamp}-{args.slug}.zip'
bundle_path = ROOT.parent / bundle_name
manifest_path = ROOT / 'RELEASE-MANIFEST.json'

EXCLUDED_TOP_LEVEL = {'scratch'}
EXCLUDED_NAMES = {'__pycache__'}
EXCLUDED_RELATIVE = {'RELEASE-MANIFEST.json'}


def included_files() -> list[pathlib.Path]:
    files = []
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.as_posix() in EXCLUDED_RELATIVE:
            continue
        if rel.parts and rel.parts[0] in EXCLUDED_TOP_LEVEL:
            continue
        if any(part in EXCLUDED_NAMES or part.startswith('.') for part in rel.parts):
            continue
        if path.suffix.lower() == '.zip':
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix())


def file_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def tree_sha256(files: list[pathlib.Path]) -> str:
    h = hashlib.sha256()
    for path in files:
        rel = path.relative_to(ROOT).as_posix().encode('utf-8')
        h.update(rel)
        h.update(b'\0')
        with path.open('rb') as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b''):
                h.update(chunk)
        h.update(b'\0')
    return h.hexdigest()

files = included_files()
manifest = {
    'project': 'AI-EDU',
    'revision': rev,
    'previous_revision': receipt.get('previous_revision'),
    'timestamp': args.timestamp,
    'slug': args.slug,
    'bundle': bundle_name,
    'status': 'packaged',
    'source_commit': 'not_available_in_source_bundle',
    'tree_sha256_excluding_release_manifest': tree_sha256(files),
    'revision_receipt_sha256': file_sha256(receipt_path),
    'changelog_sha256': file_sha256(ROOT / 'CHANGELOG.md'),
    'tracked_file_count_excluding_release_manifest': len(files),
    'claims_bit_reproducible_zip': False,
    'packager': 'tools/package_release.py',
    'provenance_note': 'The source bundle did not contain a Git commit identifier. The tree digest covers sorted included file paths and bytes, excluding RELEASE-MANIFEST.json, scratch, dotfiles, __pycache__, and nested ZIPs. ZIP metadata is not claimed bit-reproducible.',
}
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

# Include the freshly written manifest as the final sorted member.
package_files = included_files() + [manifest_path]
package_files = sorted(package_files, key=lambda item: item.relative_to(ROOT).as_posix())
with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for path in package_files:
        zf.write(path, path.relative_to(ROOT).as_posix())

print(bundle_path)
