#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, hashlib, zipfile, tempfile, subprocess, shutil
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
LANES = {"github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"}
BAD = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}
AFFECTED = {"pynicotine/downloads.py", "pynicotine/transfers.py", "pynicotine/slskproto.py", "pynicotine/search.py", "pynicotine/slskmessages.py"}

def rows(rel: str) -> List[Dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def sha_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def extract_affected(source_zip: Path, out: Path) -> Dict[str, object]:
    info: Dict[str, object] = {"source_zip": str(source_zip), "exists": source_zip.exists()}
    if not source_zip.exists():
        return info
    info["sha256"] = sha_path(source_zip)
    entries = 0
    lanes = set()
    with zipfile.ZipFile(source_zip) as zf:
        for name in zf.namelist():
            entries += 1
            if "/source-trees/" not in name or name.endswith("/"):
                continue
            rest = name.split("/source-trees/", 1)[1]
            parts = rest.split("/", 1)
            if len(parts) < 2:
                continue
            lane, rel = parts
            if lane not in LANES:
                continue
            lanes.add(lane)
            if rel in AFFECTED:
                target = out / lane / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(name))
    info["entries"] = entries
    info["lanes"] = sorted(lanes)
    return info

def run_patch(checkout: Path, patch_file: Path) -> Dict[str, object]:
    proc = subprocess.run(["patch", "-p0", "-i", str(patch_file)], cwd=checkout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    return {"rc": proc.returncode, "tail": proc.stdout.strip().splitlines()[-20:]}

def manifest_check(rel: str) -> List[str]:
    errors: List[str] = []
    path = ROOT / rel
    if not path.exists():
        return [f"missing {rel}"]
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            want, r = line.split("  ", 1)
        except ValueError:
            errors.append(f"bad manifest line: {line!r}")
            continue
        p = ROOT / r
        if not p.exists():
            errors.append(f"missing {r}")
        elif sha_path(p) != want:
            errors.append(f"hash mismatch {r}")
    return errors

def hygiene() -> List[str]:
    bad: List[str] = []
    for p in ROOT.rglob("*"):
        parts = p.relative_to(ROOT).parts
        if any(part in BAD for part in parts):
            bad.append(str(p.relative_to(ROOT)))
    return bad

def main() -> int:
    ap = argparse.ArgumentParser(description="rev0057 source-bundle selected patch-queue gate")
    ap.add_argument("--source-zip", default="/mnt/data/Nicotine-source(1).zip")
    ns = ap.parse_args()
    source_zip = Path(ns.source_zip)
    checks: List[Dict[str, object]] = []
    errors: List[str] = []

    manifest_rows = rows("data/rev0057_patch_queue_manifest.csv")
    ok = len(manifest_rows) == 3 and {r["lane"] for r in manifest_rows} == LANES and all(r["status"].startswith("generated") for r in manifest_rows)
    checks.append({"check": "patch queue manifest shape", "status": "pass" if ok else "fail", "rows": len(manifest_rows)})
    if not ok:
        errors.append("patch queue manifest shape")

    for r in manifest_rows:
        p = ROOT / r["patch"]
        ok = p.exists() and sha_path(p) == r["sha256"] and set(r["files_changed"].split(";")) == AFFECTED
        checks.append({"check": f"patch file hash {r['lane']}", "status": "pass" if ok else "fail", "patch": r["patch"], "bytes": r.get("bytes")})
        if not ok:
            errors.append(f"patch file hash {r['lane']}")

    marker_rows = rows("data/rev0057_patch_queue_marker_audit.csv")
    ok = len(marker_rows) == 21 and all(r["status"] == "pass" for r in marker_rows)
    checks.append({"check": "marker audit", "status": "pass" if ok else "fail", "rows": len(marker_rows)})
    if not ok:
        errors.append("marker audit")

    expected_hashes = {(r["lane"], r["file"]): r["new_sha256"] for r in rows("data/rev0057_patch_queue_file_hashes.csv")}
    with tempfile.TemporaryDirectory(prefix="rev0057-patchqueue-") as td:
        td_path = Path(td)
        src_info = extract_affected(source_zip, td_path / "src")
        ok = src_info.get("exists") and src_info.get("sha256") == EXPECTED_SHA and set(src_info.get("lanes", [])) == LANES
        checks.append({"check": "external source zip identity", "status": "pass" if ok else "fail", **src_info})
        if not ok:
            errors.append("external source zip identity")
        if ok:
            for r in manifest_rows:
                lane = r["lane"]
                checkout = td_path / "work" / lane
                shutil.copytree(td_path / "src" / lane, checkout)
                patch_result = run_patch(checkout, ROOT / r["patch"])
                ok_patch = patch_result["rc"] == 0
                checks.append({"check": f"patch applies {lane}", "status": "pass" if ok_patch else "fail", **patch_result})
                if not ok_patch:
                    errors.append(f"patch applies {lane}")
                    continue
                for file_rel in sorted(AFFECTED):
                    want = expected_hashes.get((lane, file_rel))
                    got = sha_path(checkout / file_rel)
                    ok_hash = got == want
                    checks.append({"check": f"patched file hash {lane} {file_rel}", "status": "pass" if ok_hash else "fail", "sha256": got})
                    if not ok_hash:
                        errors.append(f"patched file hash {lane} {file_rel}")

    e = manifest_check("handoff/rev0057/MANIFEST.sha256")
    checks.append({"check": "rev0057 handoff manifest", "status": "pass" if not e else "fail", "errors": e[:5]})
    errors.extend(e)

    bad = hygiene()
    checks.append({"check": "package hygiene", "status": "pass" if not bad else "fail", "bad_count": len(bad), "examples": bad[:10]})
    errors.extend(f"hygiene:{x}" for x in bad)

    out = {"revision": "rev0057", "status": "pass" if not errors else "fail", "checks": checks, "errors": errors}
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
