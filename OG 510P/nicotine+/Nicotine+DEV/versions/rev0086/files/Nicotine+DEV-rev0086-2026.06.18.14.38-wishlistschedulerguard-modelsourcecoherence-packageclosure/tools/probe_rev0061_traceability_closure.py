#!/usr/bin/env python3
"""rev0061 traceability closure gate.

Validates the archived-source evidence chain for the seven strict/front packets.
This helper intentionally does not run the expensive pytest matrix; it verifies
that the recorded source-bundle identity, closure data, manifests, inherited
helper rerun, and package hygiene all remain coherent.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Dict, List

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_SHA256 = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
LANES = {"github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"}
PACKETS = {"U-123", "PB-01", "SEARCH-RESP-01A", "SEARCH-RESP-01B-BUDDY", "SEARCH-RESP-01C-ROOM", "SEARCH-RESP-PARSE-BUDGET-A", "SEARCH-RESP-PARSE-BUDGET-B"}


def read_csv(rel: str) -> List[Dict[str, str]]:
    path = ROOT / rel
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_identity(path: Path) -> Dict[str, object]:
    out: Dict[str, object] = {"source_zip": str(path), "exists": path.exists()}
    if not path.exists():
        return out
    out["sha256"] = sha256(path)
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
    out["entries"] = len(names)
    lanes = sorted(lane for lane in LANES if any(f"source-trees/{lane}/" in n for n in names))
    out["lanes"] = lanes
    return out


def manifest_errors(rel: str) -> List[str]:
    path = ROOT / rel
    errors: List[str] = []
    if not path.exists():
        return [f"missing manifest {rel}"]
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, file_rel = line.split(None, 1)
        except ValueError:
            errors.append(f"bad manifest line: {line}")
            continue
        file_rel = file_rel.strip()
        fp = ROOT / file_rel
        if not fp.exists():
            errors.append(f"missing manifest file: {file_rel}")
            continue
        observed = sha256(fp)
        if observed != expected:
            errors.append(f"sha mismatch: {file_rel}")
    return errors


def package_hygiene() -> List[str]:
    bad: List[str] = []
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT).as_posix()
        parts = set(rel.split("/"))
        if "__pycache__" in parts or ".pytest_cache" in parts:
            bad.append(rel)
        if ".git" in parts or "source-trees" in parts or "git-full" in parts:
            # The compact cube should not embed upstream source trees.
            bad.append(rel)
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description="rev0061 traceability closure gate")
    ap.add_argument("--source-zip", default="/mnt/data/Nicotine-source(1).zip")
    ns = ap.parse_args()

    checks: List[Dict[str, object]] = []
    errors: List[str] = []

    src = source_identity(Path(ns.source_zip))
    source_ok = src.get("exists") and src.get("sha256") == EXPECTED_SOURCE_SHA256 and set(src.get("lanes", [])) == LANES
    checks.append({"check": "uploaded source bundle identity", "status": "pass" if source_ok else "fail", **src})
    if not source_ok:
        errors.append("uploaded source bundle identity")

    rows = read_csv("data/rev0061_traceability_closure_matrix.csv")
    row_ok = len(rows) == 21 and all(r.get("status") == "pass" for r in rows)
    packet_ok = {r.get("packet") for r in rows} == PACKETS
    lane_ok = {r.get("lane") for r in rows} == LANES
    checks.append({"check": "traceability closure matrix", "status": "pass" if row_ok and packet_ok and lane_ok else "fail", "rows": len(rows), "pass_rows": sum(1 for r in rows if r.get("status") == "pass"), "packets": sorted({r.get("packet") for r in rows}), "lanes": sorted({r.get("lane") for r in rows})})
    if not (row_ok and packet_ok and lane_ok):
        errors.append("traceability closure matrix")

    required_cols = [
        "artifact_paths_present", "lane_patch_present", "source_anchors_matched", "baseline_delta_pass", "roundtrip_fixed_regression_pass", "target_bundle_only_pass", "all_except_target_bundle_nonzero_pass", "canonical_order_regression_pass", "reverse_order_regression_pass"
    ]
    for col in required_cols:
        ok = len(rows) == 21 and all(r.get(col) == "pass" for r in rows)
        checks.append({"check": f"closure column {col}", "status": "pass" if ok else "fail", "pass_rows": sum(1 for r in rows if r.get(col) == "pass")})
        if not ok:
            errors.append(f"closure column {col}")

    packet_rows = read_csv("data/rev0061_packet_traceability_summary.csv")
    ok_packets = len(packet_rows) == 7 and all(r.get("status") == "pass" for r in packet_rows)
    checks.append({"check": "packet traceability summary", "status": "pass" if ok_packets else "fail", "rows": len(packet_rows), "pass_rows": sum(1 for r in packet_rows if r.get("status") == "pass")})
    if not ok_packets:
        errors.append("packet traceability summary")

    inherited = ROOT / "evidence/rev0061-inherited-rev0060-helper-rerun-after-hygiene-fix.json"
    try:
        inherited_data = json.loads(inherited.read_text(encoding="utf-8"))
        inherited_ok = inherited_data.get("status") == "pass"
    except Exception:
        inherited_ok = False
    checks.append({"check": "inherited rev0060 helper rerun after hygiene fix", "status": "pass" if inherited_ok else "fail", "path": str(inherited.relative_to(ROOT))})
    if not inherited_ok:
        errors.append("inherited rev0060 helper rerun")

    for rel in ("handoff/rev0061/MANIFEST.sha256",):
        errs = manifest_errors(rel)
        checks.append({"check": f"manifest {rel}", "status": "pass" if not errs else "fail", "errors": errs[:10]})
        errors.extend(errs)

    for cache in list(ROOT.rglob("__pycache__")) + list(ROOT.rglob(".pytest_cache")):
        shutil.rmtree(cache, ignore_errors=True)
    bad = package_hygiene()
    checks.append({"check": "package hygiene", "status": "pass" if not bad else "fail", "bad_count": len(bad), "examples": bad[:10]})
    errors.extend(f"hygiene:{x}" for x in bad)

    output = {"revision": "rev0061", "status": "pass" if not errors else "fail", "checks": checks, "errors": errors}
    print(json.dumps(output, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
