import argparse
import json
import pathlib
import re
import zipfile

from release_hygiene_lib import should_skip_release_path

ROOT = pathlib.Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser()
parser.add_argument("--timestamp", required=True)
parser.add_argument("--slug", required=True)
args = parser.parse_args()

changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
m = re.search(r"(rev\d{4})", changelog)
if not m:
    raise SystemExit("CHANGELOG.md missing rev header")
rev = m.group(1)

bundle_name = f"DelayBasin-{rev}-{args.timestamp}-{args.slug}.zip"
bundle_path = ROOT.parent / bundle_name

manifest = {
    "project": "DelayBasin",
    "revision": rev,
    "timestamp": args.timestamp,
    "slug": args.slug,
    "bundle": bundle_name,
}
(ROOT / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in ROOT.rglob("*"):
        if should_skip_release_path(path, bundle_name):
            continue
        if path.is_dir():
            continue
        arcname = path.relative_to(ROOT)
        zf.write(path, arcname.as_posix())

print(bundle_path)
