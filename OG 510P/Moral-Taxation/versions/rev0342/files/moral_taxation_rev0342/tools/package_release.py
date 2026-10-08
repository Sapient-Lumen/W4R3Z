#!/usr/bin/env python3
import json, pathlib, re, sys, zipfile
sys.dont_write_bytecode = True

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
sys.path.insert(0, str(root / "tools"))
import release_lineage

version = (root / "VERSION").read_text(encoding="utf-8").strip()
releases = json.loads((root / "RELEASES.json").read_text(encoding="utf-8"))
receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
zip_name = releases.get("latest_zip", "")
errors, _lineage_details = release_lineage.collect_lineage_errors(root)

if releases.get("latest_revision") != version:
    errors.append("RELEASES.json latest_revision must match VERSION before packaging")
if receipt.get("revision") != version:
    errors.append("REVISION-RECEIPT.json revision must match VERSION before packaging")
if releases.get("latest_codename") != receipt.get("codename"):
    errors.append("RELEASES.json latest_codename must match REVISION-RECEIPT.json codename")
if version not in root.name:
    errors.append("archive root folder name must include VERSION before packaging")
if version not in zip_name or receipt.get("codename", "") not in zip_name:
    errors.append("latest_zip must include VERSION and codename")
if not re.match(r"^Moral-Taxation-rev\d{4}-\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}-[a-z0-9-]+\.zip$", zip_name):
    errors.append("latest_zip must follow Moral-Taxation-rev####-YYYY.MM.DD.HH.MM-codename.zip")
manifest = root / "MANIFEST.json"
if not manifest.exists():
    errors.append("MANIFEST.json missing; run make manifest first")

if errors:
    raise SystemExit("\n".join(errors))

out = root.parent / zip_name
if len(sys.argv) > 2:
    out = pathlib.Path(sys.argv[2]).resolve()
if out.exists():
    out.unlink()
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            zf.write(path, f"{root.name}/{rel}")
print(out)
