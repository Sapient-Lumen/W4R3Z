#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, hashlib, zipfile
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
BAD = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}
EXPECTED_SHA = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
EXPECTED_LANES = {"github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"}
EXPECTED_PACKETS = {"U-123", "PB-01", "SEARCH-RESP-01A", "SEARCH-RESP-01B-BUDDY", "SEARCH-RESP-01C-ROOM", "SEARCH-RESP-PARSE-BUDGET-A", "SEARCH-RESP-PARSE-BUDGET-B"}

def rows(rel: str) -> List[Dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def sha_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def manifest(rel: str) -> List[str]:
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

def inspect_source_zip(path: Path) -> Dict[str, object]:
    info: Dict[str, object] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return info
    info["sha256"] = sha_path(path)
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        lanes = sorted({n.split("/source-trees/", 1)[1].split("/", 1)[0] for n in names if "/source-trees/" in n and len(n.split("/source-trees/", 1)[1].split("/", 1)) > 1})
        info.update({
            "entries": len(names),
            "lanes": lanes,
            "has_required_lanes": set(lanes) == EXPECTED_LANES,
            "has_key_files": all(any(f"/source-trees/{lane}/pynicotine/" in n for n in names) for lane in EXPECTED_LANES),
        })
    return info

def main() -> int:
    ap = argparse.ArgumentParser(description="rev0055 source-bundle usage gate")
    ap.add_argument("--source-zip", default="/mnt/data/Nicotine-source(1).zip", help="uploaded Nicotine source bundle")
    ns = ap.parse_args()
    checks: List[Dict[str, object]] = []
    errors: List[str] = []

    usage = rows("data/rev0055_source_bundle_usage_gate.csv")
    ok = len(usage) == 8 and {r["status"] for r in usage} <= {"pass", "held"}
    checks.append({"check": "rev0055 usage gate rows", "status": "pass" if ok else "fail", "rows": len(usage)})
    if not ok:
        errors.append("usage gate shape")

    stack = rows("data/rev0055_source_bundle_stack_rerun_matrix.csv")
    ok = len(stack) == 21 and {r["lane"] for r in stack} == EXPECTED_LANES and {r["packet"] for r in stack} == EXPECTED_PACKETS and all(r["status"] == "pass" for r in stack)
    checks.append({"check": "rev0055 source-bundle stack matrix", "status": "pass" if ok else "fail", "rows": len(stack)})
    if not ok:
        errors.append("stack matrix")

    anchor = json.loads((ROOT / "evidence/rev0055-source-anchor-helper-rerun.json").read_text(encoding="utf-8"))
    ok = anchor.get("status") == "pass" and anchor.get("anchor_rows") == 126
    checks.append({"check": "rev0055 source-anchor helper rerun", "status": "pass" if ok else "fail", "anchor_rows": anchor.get("anchor_rows")})
    if not ok:
        errors.append("source anchor helper")

    gate = json.loads((ROOT / "evidence/rev0055-current-upstream-gate-sourcezip-rerun.json").read_text(encoding="utf-8"))
    summary = gate.get("source_zip_scan_summary") or {}
    ok = gate.get("status") == "pass" and summary.get("rows") == 21 and summary.get("total_markers_present") == 0 and summary.get("total_markers_missing") == 54
    checks.append({"check": "rev0055 source-zip marker scan rerun", "status": "pass" if ok else "fail", "summary": summary})
    if not ok:
        errors.append("source zip marker scan")

    sj = json.loads((ROOT / "evidence/rev0055-strict-stack-sourcebundle-rerun-matrix.json").read_text(encoding="utf-8"))
    ok = sj.get("status") == "pass" and len(sj.get("records", [])) == 21
    checks.append({"check": "rev0055 strict stack rerun evidence", "status": "pass" if ok else "fail", "records": len(sj.get("records", []))})
    if not ok:
        errors.append("strict stack rerun evidence")

    src = inspect_source_zip(Path(ns.source_zip))
    ok = bool(src.get("exists")) and src.get("sha256") == EXPECTED_SHA and src.get("has_required_lanes") and src.get("has_key_files")
    checks.append({"check": "external source zip identity", "status": "pass" if ok else "fail", **src})
    if not ok:
        errors.append("external source zip identity")

    e = manifest("handoff/rev0055/MANIFEST.sha256")
    checks.append({"check": "rev0055 handoff manifest", "status": "pass" if not e else "fail", "errors": e[:5]})
    errors.extend(e)

    bad = hygiene()
    checks.append({"check": "package hygiene", "status": "pass" if not bad else "fail", "bad_count": len(bad), "examples": bad[:10]})
    errors.extend(f"hygiene:{x}" for x in bad)

    out = {"revision": "rev0055", "status": "pass" if not errors else "fail", "checks": checks, "errors": errors}
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
