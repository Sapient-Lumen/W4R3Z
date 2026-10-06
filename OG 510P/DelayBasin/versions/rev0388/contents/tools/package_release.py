import argparse
import json
import pathlib

from generated_surface_lib import refresh_generated_surfaces
from package_preflight_lib import run_artifact_smoke, run_lint_preflight, write_deterministic_zip, write_verified_sha256_sidecar
from release_hygiene_lib import build_release_manifest, extract_revision_from_changelog

ROOT = pathlib.Path(__file__).resolve().parents[1]


parser = argparse.ArgumentParser()
parser.add_argument("--timestamp", required=True)
parser.add_argument("--slug", required=True)
args = parser.parse_args()

changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
rev = extract_revision_from_changelog(changelog)

manifest = build_release_manifest(rev, args.timestamp, args.slug)
bundle_name = manifest["bundle"]
bundle_path = ROOT.parent / bundle_name
(ROOT / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
receipt_path = ROOT / "REVISION-RECEIPT.json"
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
receipt["revision"] = rev
receipt["stamp"] = args.timestamp
receipt["slug"] = args.slug
receipt["bundle"] = bundle_name
receipt["packaged_bundle_filename"] = bundle_name
receipt["packaged_release"] = True
receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
refresh_generated_surfaces(ROOT, include_release_integrity=True)
run_lint_preflight(ROOT)
write_deterministic_zip(ROOT, bundle_path, bundle_name)
run_artifact_smoke(ROOT, bundle_path, bundle_name)
sidecar = ROOT.parent / f"{bundle_name}.sha256"
write_verified_sha256_sidecar(bundle_path, sidecar, bundle_name)
print(bundle_path)
print(sidecar)
