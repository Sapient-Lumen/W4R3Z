#!/usr/bin/env python3
"""Standalone clean-room replay runner for the rev0062 strict/front kit.

The script is intentionally self-contained. It needs only:
  * this cleanroom-kit directory, and
  * the external Nicotine-source zip that contains the archived source lanes.

It extracts clean lanes to a temporary directory, applies the exported split
bundle patches from the kit, and runs the copied fixed-behavior regressions from
this kit rather than importing tests from the full cube.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

sys.dont_write_bytecode = True
EXPECTED_SOURCE_SHA256 = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
SOURCE_PREFIX = "Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/"
LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")
PATCH_ORDER = (
    "u-123-rev0059.patch",
    "pb-01-rev0059.patch",
    "search-resp-source-admission-rev0059.patch",
    "search-resp-parser-budget-rev0059.patch",
)
AFFECTED = (
    "pynicotine/downloads.py",
    "pynicotine/transfers.py",
    "pynicotine/slskproto.py",
    "pynicotine/search.py",
    "pynicotine/slskmessages.py",
)
FIXED_TESTS: Tuple[Tuple[str, str, str, str], ...] = (
    ("U-123", "tests/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py", "unittest", "PYTHONPATH"),
    ("PB-01", "tests/pb01/test_peer_connection_primary_election_fixed_regression.py", "pytest", "NICOTINE_SOURCE"),
    ("SEARCH-RESP-01A", "tests/search-resp-01/test_search_response_user_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-01B-BUDDY", "tests/search-resp-01/test_search_response_buddy_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-01C-ROOM", "tests/search-resp-01/test_search_response_room_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-PARSE-BUDGET-A", "tests/search-resp-01/test_search_response_prefix_budget_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-PARSE-BUDGET-B", "tests/search-resp-01/test_search_response_result_budget_fixed_regression.py", "pytest", "PYTHONPATH"),
)


def sha_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: List[Dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fields))
        w.writeheader()
        for row in rows:
            w.writerow({field: row.get(field, "") for field in w.fieldnames})


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_identity(source_zip: Path) -> Dict[str, object]:
    info: Dict[str, object] = {"source_zip": str(source_zip), "exists": source_zip.exists()}
    if not source_zip.exists():
        return info
    info["sha256"] = sha_path(source_zip)
    lanes = set()
    entries = 0
    with zipfile.ZipFile(source_zip) as zf:
        for name in zf.namelist():
            entries += 1
            if name.startswith(SOURCE_PREFIX):
                rest = name[len(SOURCE_PREFIX):]
                lane = rest.split("/", 1)[0]
                if lane in LANES:
                    lanes.add(lane)
    info["entries"] = entries
    info["lanes"] = sorted(lanes)
    return info


def extract_lane(source_zip: Path, lane: str, dest: Path) -> int:
    prefix = SOURCE_PREFIX + lane + "/"
    count = 0
    with zipfile.ZipFile(source_zip) as zf:
        for zi in zf.infolist():
            name = zi.filename
            if not name.startswith(prefix) or name.endswith("/"):
                continue
            rel = name[len(prefix):]
            if not rel:
                continue
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(zi) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            count += 1
    return count


def patch_apply(cwd: Path, patch_path: Path, lane: str, patch_name: str) -> Dict[str, object]:
    cmd = ["patch", "--batch", "--forward", "-p0", "-i", str(patch_path)]
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return {
        "lane": lane,
        "patch": patch_name,
        "stage": "cleanroom-forward-apply",
        "expected_rc": "0",
        "observed_rc": str(proc.returncode),
        "status": "pass" if proc.returncode == 0 else "fail",
        "summary": " | ".join(lines[-8:]),
    }


def test_summary(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if re.search(r"\d+ (failed|passed|errors?|error)|^OK$|^FAILED", line, re.I):
            return line
    return lines[-1] if lines else ""


def run_fixed_test(kit_dir: Path, lane: str, source_dir: Path, packet: str, test_rel: str, runner: str, env_kind: str, out_dir: Path) -> Dict[str, object]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if env_kind == "NICOTINE_SOURCE":
        env.pop("PYTHONPATH", None)
        env["NICOTINE_SOURCE"] = str(source_dir)
    else:
        env["PYTHONPATH"] = str(source_dir)
    test_path = kit_dir / test_rel
    if runner == "unittest":
        cmd = [sys.executable, str(test_path)]
    else:
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=short", str(test_path)]
    out_dir.mkdir(parents=True, exist_ok=True)
    output_file = out_dir / f"{lane}__{packet}__cleanroom-fixed-regression.txt".replace("/", "_")
    with output_file.open("w", encoding="utf-8") as fh:
        proc = subprocess.Popen(cmd, cwd="/tmp", env=env, stdout=fh, stderr=subprocess.STDOUT, text=True, start_new_session=True)
        try:
            rc = proc.wait(timeout=120)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            rc = 124
    text = output_file.read_text(encoding="utf-8", errors="replace")
    return {
        "lane": lane,
        "packet": packet,
        "stage": "cleanroom-fixed-regression",
        "runner": runner,
        "env_kind": env_kind,
        "expected_rc": "0",
        "observed_rc": str(rc),
        "status": "pass" if rc == 0 else "fail",
        "summary": test_summary(text),
        "test": test_rel,
        "output_file": str(output_file.relative_to(out_dir.parent)),
    }


def cleanup_caches(path: Path) -> None:
    for cache in list(path.rglob("__pycache__")) + list(path.rglob(".pytest_cache")):
        shutil.rmtree(cache, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="run the rev0062 clean-room replay kit")
    ap.add_argument("--source-zip", required=True)
    ap.add_argument("--kit-dir", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--lanes", default=",".join(LANES), help="comma-separated lanes or 'all'")
    ns = ap.parse_args()
    source_zip = Path(ns.source_zip).resolve()
    kit_dir = Path(ns.kit_dir).resolve()
    out_dir = Path(ns.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    requested_lanes = LANES if ns.lanes == "all" else tuple(x for x in ns.lanes.split(",") if x)
    source_info = source_identity(source_zip)
    errors: List[str] = []
    if not source_info.get("exists") or source_info.get("sha256") != EXPECTED_SOURCE_SHA256:
        errors.append("source bundle identity mismatch")
    if set(source_info.get("lanes", [])) != set(LANES):
        errors.append("source bundle lane set mismatch")

    patch_rows: List[Dict[str, object]] = []
    hash_rows: List[Dict[str, object]] = []
    test_rows: List[Dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="rev0062-cleanroom-") as td:
        td_path = Path(td)
        for lane in requested_lanes:
            lane_src = td_path / "source" / lane
            count = extract_lane(source_zip, lane, lane_src)
            if count <= 0:
                errors.append(f"no files extracted for {lane}")
                continue
            for patch_name in PATCH_ORDER:
                patch_path = kit_dir / "patches" / lane / patch_name
                if not patch_path.exists():
                    row = {"lane": lane, "patch": patch_name, "stage": "cleanroom-forward-apply", "expected_rc": "0", "observed_rc": "missing", "status": "fail", "summary": "patch missing"}
                else:
                    row = patch_apply(lane_src, patch_path, lane, patch_name)
                patch_rows.append(row)
                if row["status"] != "pass":
                    errors.append(f"patch apply failed: {lane} {patch_name}")
                    break
            for rel in AFFECTED:
                fp = lane_src / rel
                hash_rows.append({"lane": lane, "file": rel, "exists": str(fp.exists()).lower(), "sha256": sha_path(fp) if fp.exists() else "", "status": "pass" if fp.exists() else "fail"})
                if not fp.exists():
                    errors.append(f"missing affected file after patch: {lane} {rel}")
            if any(r["status"] != "pass" for r in patch_rows if r.get("lane") == lane):
                continue
            for packet, test_rel, runner, env_kind in FIXED_TESTS:
                row = run_fixed_test(kit_dir, lane, lane_src, packet, test_rel, runner, env_kind, out_dir / "test-outputs")
                test_rows.append(row)
                if row["status"] != "pass":
                    errors.append(f"fixed regression failed: {lane} {packet}")
            cleanup_caches(lane_src)
    cleanup_caches(kit_dir)

    patch_fields = ["lane", "patch", "stage", "expected_rc", "observed_rc", "status", "summary"]
    hash_fields = ["lane", "file", "exists", "sha256", "status"]
    test_fields = ["lane", "packet", "stage", "runner", "env_kind", "expected_rc", "observed_rc", "status", "summary", "test", "output_file"]
    write_csv(out_dir / "cleanroom_patch_apply_matrix.csv", patch_rows, patch_fields)
    write_csv(out_dir / "cleanroom_patched_file_hashes.csv", hash_rows, hash_fields)
    write_csv(out_dir / "cleanroom_fixed_regression_matrix.csv", test_rows, test_fields)
    write_json(out_dir / "cleanroom_patch_apply_matrix.json", patch_rows)
    write_json(out_dir / "cleanroom_patched_file_hashes.json", hash_rows)
    write_json(out_dir / "cleanroom_fixed_regression_matrix.json", test_rows)

    summary = {
        "revision": "rev0062",
        "status": "pass" if not errors else "fail",
        "source": source_info,
        "lanes_requested": list(requested_lanes),
        "patch_apply_rows": len(patch_rows),
        "patch_apply_pass": sum(1 for r in patch_rows if r.get("status") == "pass"),
        "patched_file_hash_rows": len(hash_rows),
        "patched_file_hash_pass": sum(1 for r in hash_rows if r.get("status") == "pass"),
        "fixed_regression_rows": len(test_rows),
        "fixed_regression_pass": sum(1 for r in test_rows if r.get("status") == "pass"),
        "errors": errors,
    }
    write_json(out_dir / "cleanroom_replay_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
