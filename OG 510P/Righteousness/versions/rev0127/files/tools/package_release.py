import argparse
import json
import pathlib
import subprocess
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--timestamp", required=True)
parser.add_argument("--slug", required=True)
args = parser.parse_args()

receipt = json.loads((ROOT / "REVISION_RECEIPT.json").read_text(encoding="utf-8"))
revision = receipt["revision"]
bundle = f"Righteousness-{revision}-{args.timestamp}-{args.slug}.zip"
manifest = {
    "project": "Righteousness",
    "revision": revision,
    "timestamp": args.timestamp,
    "slug": args.slug,
    "bundle": bundle,
}
(ROOT / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

status_path = ROOT / "SURFACE_STATUS.json"
status = json.loads(status_path.read_text(encoding="utf-8"))
status["citation_head"]["surface"] = bundle
status["status_lanes"]["execution_state"] = "packaged"
status["status_lanes"]["public_state"] = "frozen-citable"
status["state_class"] = "released"
status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

subprocess.run(["python", str(ROOT / "tools" / "gen_context_pack.py")], check=True)

base_dir = ROOT.parents[1] if ROOT.parent.name == "out" else ROOT.parent
out_dir = base_dir / "out"
out_dir.mkdir(exist_ok=True)
out = out_dir / bundle
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in ROOT.rglob("*"):
        if path.is_dir():
            continue
        if path.name == bundle:
            continue
        zf.write(path, path.relative_to(ROOT).as_posix())

print(out)
