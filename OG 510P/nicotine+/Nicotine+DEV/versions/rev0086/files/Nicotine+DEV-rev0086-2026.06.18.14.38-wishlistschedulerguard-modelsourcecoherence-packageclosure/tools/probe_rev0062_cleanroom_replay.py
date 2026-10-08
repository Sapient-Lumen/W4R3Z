#!/usr/bin/env python3
"""rev0062 clean-room replay kit gate.

Validates that the reviewer-facing cleanroom kit can be copied out of the cube,
then applied and run against the uploaded archived source bundle without relying
on hidden cube paths for patches or tests.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "handoff" / "rev0062" / "cleanroom-kit"
EXPECTED_SOURCE_SHA256 = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
LANES = {"github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"}
PACKETS = {"U-123", "PB-01", "SEARCH-RESP-01A", "SEARCH-RESP-01B-BUDDY", "SEARCH-RESP-01C-ROOM", "SEARCH-RESP-PARSE-BUDGET-A", "SEARCH-RESP-PARSE-BUDGET-B"}
BAD_PARTS = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}


def sha_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))




def write_csv(path: Path, rows: List[Dict[str, object]], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def manifest_errors(rel: str) -> List[str]:
    path = ROOT / rel
    if not path.exists():
        return [f"missing manifest {rel}"]
    errors: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            want, file_rel = line.split(None, 1)
        except ValueError:
            errors.append(f"bad manifest line {line!r}")
            continue
        file_rel = file_rel.strip()
        fp = ROOT / file_rel
        if not fp.exists():
            errors.append(f"missing manifest target {file_rel}")
        elif sha_path(fp) != want:
            errors.append(f"hash mismatch {file_rel}")
    return errors


def package_hygiene() -> List[str]:
    for cache in list(ROOT.rglob("__pycache__")) + list(ROOT.rglob(".pytest_cache")):
        shutil.rmtree(cache, ignore_errors=True)
    bad: List[str] = []
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT)
        if any(part in BAD_PARTS for part in rel.parts):
            bad.append(rel.as_posix())
    return bad


def copy_kit_to_external_stage(stage: Path) -> Path:
    dst = stage / "external-cleanroom-kit"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(KIT, dst, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    return dst


def run_one_lane(source_zip: Path, kit_stage: Path, lane_out: Path, lane: str) -> Dict[str, object]:
    if lane_out.exists():
        shutil.rmtree(lane_out)
    lane_out.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(kit_stage / "run_cleanroom_replay.py"), "--source-zip", str(source_zip), "--kit-dir", str(kit_stage), "--out-dir", str(lane_out), "--lanes", lane]
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    proc = subprocess.run(cmd, cwd="/tmp", env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=420)
    (lane_out / "standalone-runner-stdout.txt").write_text(proc.stdout, encoding="utf-8")
    try:
        summary = json.loads((lane_out / "cleanroom_replay_summary.json").read_text(encoding="utf-8"))
    except Exception as exc:
        summary = {"status": "fail", "errors": [f"could not read standalone summary: {exc}"], "stdout": proc.stdout[-2000:]}
    summary["standalone_rc"] = proc.returncode
    summary["lane"] = lane
    return summary


def run_standalone(source_zip: Path, kit_stage: Path, out_dir: Path, lanes: str) -> Dict[str, object]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    lane_list = [x for x in ("github-tag-3.3.10,github-branch-3.3.x,github-branch-master" if lanes == "all" else lanes).split(",") if x]
    all_patch_rows: List[Dict[str, object]] = []
    all_test_rows: List[Dict[str, object]] = []
    all_hash_rows: List[Dict[str, object]] = []
    lane_summaries: List[Dict[str, object]] = []
    errors: List[str] = []
    lanes_root = out_dir / "lanes"
    for lane in lane_list:
        lane_out = lanes_root / lane
        summary = run_one_lane(source_zip, kit_stage, lane_out, lane)
        lane_summaries.append(summary)
        if summary.get("status") != "pass" or summary.get("standalone_rc") != 0:
            errors.append(f"lane {lane} cleanroom runner failed")
        all_patch_rows.extend(read_csv(lane_out / "cleanroom_patch_apply_matrix.csv"))
        all_test_rows.extend(read_csv(lane_out / "cleanroom_fixed_regression_matrix.csv"))
        all_hash_rows.extend(read_csv(lane_out / "cleanroom_patched_file_hashes.csv"))
    write_csv(out_dir / "cleanroom_patch_apply_matrix.csv", all_patch_rows, ["lane", "patch", "stage", "expected_rc", "observed_rc", "status", "summary"])
    write_csv(out_dir / "cleanroom_fixed_regression_matrix.csv", all_test_rows, ["lane", "packet", "stage", "runner", "env_kind", "expected_rc", "observed_rc", "status", "summary", "test", "output_file"])
    write_csv(out_dir / "cleanroom_patched_file_hashes.csv", all_hash_rows, ["lane", "file", "exists", "sha256", "status"])
    write_json(out_dir / "cleanroom_patch_apply_matrix.json", all_patch_rows)
    write_json(out_dir / "cleanroom_fixed_regression_matrix.json", all_test_rows)
    write_json(out_dir / "cleanroom_patched_file_hashes.json", all_hash_rows)
    source = lane_summaries[0].get("source", {}) if lane_summaries else {}
    summary = {
        "revision": "rev0062",
        "status": "pass" if not errors and all(r.get("status") == "pass" for r in all_patch_rows + all_test_rows + all_hash_rows) else "fail",
        "source": source,
        "lanes_requested": lane_list,
        "lane_summaries": lane_summaries,
        "patch_apply_rows": len(all_patch_rows),
        "patch_apply_pass": sum(1 for r in all_patch_rows if r.get("status") == "pass"),
        "patched_file_hash_rows": len(all_hash_rows),
        "patched_file_hash_pass": sum(1 for r in all_hash_rows if r.get("status") == "pass"),
        "fixed_regression_rows": len(all_test_rows),
        "fixed_regression_pass": sum(1 for r in all_test_rows if r.get("status") == "pass"),
        "errors": errors,
        "standalone_rc": 0 if lane_summaries and all(s.get("standalone_rc") == 0 for s in lane_summaries) else 1,
    }
    write_json(out_dir / "cleanroom_replay_summary.json", summary)
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="rev0062 clean-room replay gate")
    ap.add_argument("--source-zip", default="/mnt/data/Nicotine-source(1).zip")
    ap.add_argument("--out-dir", default=str(ROOT / "evidence" / "rev0062-cleanroom-replay-rerun"))
    ap.add_argument("--write-data", action="store_true", help="copy generated cleanroom matrices into data/rev0062_* files")
    ap.add_argument("--lanes", default="github-branch-master", help="comma-separated lanes or all; full evidence uses all, default is a one-lane package smoke")
    ns = ap.parse_args()
    source_zip = Path(ns.source_zip).resolve()
    out_dir = Path(ns.out_dir).resolve()
    checks: List[Dict[str, object]] = []
    errors: List[str] = []

    src_ok = source_zip.exists() and sha_path(source_zip) == EXPECTED_SOURCE_SHA256
    checks.append({"check": "uploaded source bundle sha256", "status": "pass" if src_ok else "fail", "source_zip": str(source_zip), "sha256": sha_path(source_zip) if source_zip.exists() else "missing"})
    if not src_ok:
        errors.append("source sha256")

    kit_required = [KIT / "run_cleanroom_replay.py"]
    for lane in LANES:
        for patch in ("u-123-rev0059.patch", "pb-01-rev0059.patch", "search-resp-source-admission-rev0059.patch", "search-resp-parser-budget-rev0059.patch"):
            kit_required.append(KIT / "patches" / lane / patch)
    for test in (
        "tests/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py",
        "tests/pb01/test_peer_connection_primary_election_fixed_regression.py",
        "tests/search-resp-01/test_search_response_user_scope_fixed_regression.py",
        "tests/search-resp-01/test_search_response_buddy_scope_fixed_regression.py",
        "tests/search-resp-01/test_search_response_room_scope_fixed_regression.py",
        "tests/search-resp-01/test_search_response_prefix_budget_fixed_regression.py",
        "tests/search-resp-01/test_search_response_result_budget_fixed_regression.py",
    ):
        kit_required.append(KIT / test)
    missing = [p.relative_to(ROOT).as_posix() for p in kit_required if not p.exists()]
    checks.append({"check": "cleanroom kit required files", "status": "pass" if not missing else "fail", "required_count": len(kit_required), "missing": missing})
    errors.extend(f"missing kit file {m}" for m in missing)

    with __import__("tempfile").TemporaryDirectory(prefix="rev0062-external-kit-stage-") as td:
        kit_stage = copy_kit_to_external_stage(Path(td))
        summary = run_standalone(source_zip, kit_stage, out_dir, ns.lanes)
    standalone_ok = summary.get("status") == "pass" and summary.get("standalone_rc") == 0
    checks.append({"check": "external copied kit standalone replay", "status": "pass" if standalone_ok else "fail", **{k: summary.get(k) for k in ("patch_apply_rows", "patch_apply_pass", "patched_file_hash_rows", "patched_file_hash_pass", "fixed_regression_rows", "fixed_regression_pass", "standalone_rc")}})
    if not standalone_ok:
        errors.append("standalone cleanroom replay")

    patch_rows = read_csv(out_dir / "cleanroom_patch_apply_matrix.csv")
    test_rows = read_csv(out_dir / "cleanroom_fixed_regression_matrix.csv")
    hash_rows = read_csv(out_dir / "cleanroom_patched_file_hashes.csv")
    lane_count = 3 if ns.lanes == "all" else len([x for x in ns.lanes.split(",") if x])
    expected_patch_rows = lane_count * 4
    expected_test_rows = lane_count * 7
    expected_hash_rows = lane_count * 5
    checks.append({"check": "cleanroom patch rows", "status": "pass" if len(patch_rows) == expected_patch_rows and all(r.get("status") == "pass" for r in patch_rows) else "fail", "rows": len(patch_rows), "expected_rows": expected_patch_rows, "pass_rows": sum(1 for r in patch_rows if r.get("status") == "pass")})
    checks.append({"check": "cleanroom regression rows", "status": "pass" if len(test_rows) == expected_test_rows and all(r.get("status") == "pass" for r in test_rows) and {r.get("packet") for r in test_rows} == PACKETS else "fail", "rows": len(test_rows), "expected_rows": expected_test_rows, "pass_rows": sum(1 for r in test_rows if r.get("status") == "pass"), "packets": sorted({r.get("packet") for r in test_rows})})
    checks.append({"check": "cleanroom patched file hashes", "status": "pass" if len(hash_rows) == expected_hash_rows and all(r.get("status") == "pass" for r in hash_rows) else "fail", "rows": len(hash_rows), "expected_rows": expected_hash_rows, "pass_rows": sum(1 for r in hash_rows if r.get("status") == "pass")})
    if not (len(patch_rows) == expected_patch_rows and all(r.get("status") == "pass" for r in patch_rows)):
        errors.append("patch rows")
    if not (len(test_rows) == expected_test_rows and all(r.get("status") == "pass" for r in test_rows)):
        errors.append("regression rows")
    if not (len(hash_rows) == expected_hash_rows and all(r.get("status") == "pass" for r in hash_rows)):
        errors.append("hash rows")

    manifest_errs = manifest_errors("handoff/rev0062/MANIFEST.sha256")
    checks.append({"check": "handoff rev0062 manifest", "status": "pass" if not manifest_errs else "fail", "errors": manifest_errs[:10]})
    errors.extend(manifest_errs)

    if ns.write_data and not errors:
        mapping = {
            "cleanroom_patch_apply_matrix.csv": "data/rev0062_cleanroom_patch_apply_matrix.csv",
            "cleanroom_patch_apply_matrix.json": "data/rev0062_cleanroom_patch_apply_matrix.json",
            "cleanroom_fixed_regression_matrix.csv": "data/rev0062_cleanroom_fixed_regression_matrix.csv",
            "cleanroom_fixed_regression_matrix.json": "data/rev0062_cleanroom_fixed_regression_matrix.json",
            "cleanroom_patched_file_hashes.csv": "data/rev0062_cleanroom_patched_file_hashes.csv",
            "cleanroom_patched_file_hashes.json": "data/rev0062_cleanroom_patched_file_hashes.json",
            "cleanroom_replay_summary.json": "data/rev0062_cleanroom_replay_summary.json",
        }
        for src_name, dst_rel in mapping.items():
            shutil.copy2(out_dir / src_name, ROOT / dst_rel)

    bad = package_hygiene()
    checks.append({"check": "package hygiene", "status": "pass" if not bad else "fail", "bad_count": len(bad), "examples": bad[:10]})
    errors.extend(f"hygiene:{x}" for x in bad)

    output = {"revision": "rev0062", "status": "pass" if not errors else "fail", "checks": checks, "errors": errors}
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
