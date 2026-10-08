#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, zipfile
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
LANES = {"github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"}
PACKETS = {"U-123", "PB-01", "SEARCH-RESP-01A", "SEARCH-RESP-01B-BUDDY", "SEARCH-RESP-01C-ROOM", "SEARCH-RESP-PARSE-BUDGET-A", "SEARCH-RESP-PARSE-BUDGET-B"}
BAD = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}

def rows(rel: str) -> List[Dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def sha_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def inspect_source_zip(path: Path) -> Dict[str, object]:
    info: Dict[str, object] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return info
    info["sha256"] = sha_path(path)
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        lanes = sorted({
            n.split("/source-trees/", 1)[1].split("/", 1)[0]
            for n in names
            if "/source-trees/" in n and n.split("/source-trees/", 1)[1].split("/", 1)[0]
        })
        info["entries"] = len(names)
        info["lanes"] = lanes
        info["has_expected_lanes"] = set(lanes) == LANES
    return info

def check_manifest(rel: str) -> List[str]:
    errors: List[str] = []
    p = ROOT / rel
    if not p.exists():
        return [f"missing {rel}"]
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            want, r = line.split("  ", 1)
        except ValueError:
            errors.append(f"bad manifest line: {line!r}")
            continue
        q = ROOT / r
        if not q.exists():
            errors.append(f"missing {r}")
        elif sha_path(q) != want:
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
    ap = argparse.ArgumentParser(description="rev0056 baseline-delta gate validator")
    ap.add_argument("--source-zip", default="/mnt/data/Nicotine-source(1).zip")
    ns = ap.parse_args()
    checks: List[Dict[str, object]] = []
    errors: List[str] = []

    baseline = rows("data/rev0056_baseline_delta_matrix.csv")
    current = [r for r in baseline if r["stage"] == "archived-current-witness"]
    fixed = [r for r in baseline if r["stage"] == "archived-unpatched-fixed-regression"]
    ok = len(baseline) == 30 and len(current) == 9 and len(fixed) == 21 and all(r["status"] == "pass" for r in baseline)
    checks.append({"check": "baseline delta matrix", "status": "pass" if ok else "fail", "rows": len(baseline), "current_rows": len(current), "fixed_rows": len(fixed)})
    if not ok:
        errors.append("baseline matrix shape/status")

    delta = rows("data/rev0056_before_after_delta_gate.csv")
    ok = len(delta) == 21 and {r["lane"] for r in delta} == LANES and {r["packet"] for r in delta} == PACKETS and all(r["delta_status"] == "pass" for r in delta)
    checks.append({"check": "before/after delta gate", "status": "pass" if ok else "fail", "rows": len(delta)})
    if not ok:
        errors.append("before/after delta gate")

    stack = rows("data/rev0055_source_bundle_stack_rerun_matrix.csv")
    ok = len(stack) == 21 and all(r["status"] == "pass" for r in stack)
    checks.append({"check": "inherited selected-stack after-state", "status": "pass" if ok else "fail", "rows": len(stack)})
    if not ok:
        errors.append("selected stack after-state")

    manifest_rows = rows("data/rev0056_baseline_replay_output_manifest.csv")
    ok = len(manifest_rows) == 30 and all((ROOT / r["path"]).exists() and sha_path(ROOT / r["path"]) == r["sha256"] for r in manifest_rows)
    checks.append({"check": "baseline output manifest", "status": "pass" if ok else "fail", "rows": len(manifest_rows)})
    if not ok:
        errors.append("baseline output manifest")

    src = inspect_source_zip(Path(ns.source_zip))
    ok = bool(src.get("exists")) and src.get("sha256") == EXPECTED_SHA and src.get("has_expected_lanes")
    checks.append({"check": "external source zip identity", "status": "pass" if ok else "fail", **src})
    if not ok:
        errors.append("external source zip identity")

    for rel in ("handoff/rev0056/MANIFEST.sha256",):
        e = check_manifest(rel)
        checks.append({"check": rel, "status": "pass" if not e else "fail", "errors": e[:5]})
        errors.extend(e)

    bad = hygiene()
    checks.append({"check": "package hygiene", "status": "pass" if not bad else "fail", "bad_count": len(bad), "examples": bad[:10]})
    errors.extend(f"hygiene:{x}" for x in bad)

    out = {"revision": "rev0056", "status": "pass" if not errors else "fail", "checks": checks, "errors": errors}
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
