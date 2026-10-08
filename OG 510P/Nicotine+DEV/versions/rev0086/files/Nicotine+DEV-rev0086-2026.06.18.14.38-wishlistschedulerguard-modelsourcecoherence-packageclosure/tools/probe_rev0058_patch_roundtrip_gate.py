#!/usr/bin/env python3
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

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_SHA256 = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
SOURCE_PREFIX = "Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/"
LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")
AFFECTED = (
    "pynicotine/downloads.py",
    "pynicotine/transfers.py",
    "pynicotine/slskproto.py",
    "pynicotine/search.py",
    "pynicotine/slskmessages.py",
)
BAD_PARTS = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}
FIXED_TESTS: Tuple[Tuple[str, str, str, str], ...] = (
    ("U-123", "maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py", "unittest", "PYTHONPATH"),
    ("PB-01", "maintainer_artifacts/pb01/test_peer_connection_primary_election_fixed_regression.py", "pytest", "NICOTINE_SOURCE"),
    ("SEARCH-RESP-01A", "maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-01B-BUDDY", "maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-01C-ROOM", "maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-PARSE-BUDGET-A", "maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-PARSE-BUDGET-B", "maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py", "pytest", "PYTHONPATH"),
)


def sha_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(rel: str) -> List[Dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fields))
        w.writeheader()
        for row in rows:
            w.writerow({field: row.get(field, "") for field in w.fieldnames})


def manifest_errors(rel: str) -> List[str]:
    path = ROOT / rel
    if not path.exists():
        return [f"missing manifest {rel}"]
    errors: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            want, file_rel = line.split("  ", 1)
        except ValueError:
            errors.append(f"bad manifest line {line!r}")
            continue
        file_path = ROOT / file_rel
        if not file_path.exists():
            errors.append(f"missing manifest target {file_rel}")
        else:
            got = sha_path(file_path)
            if got != want:
                errors.append(f"hash mismatch {file_rel}: got {got} expected {want}")
    return errors


def package_hygiene() -> List[str]:
    bad: List[str] = []
    for p in ROOT.rglob("*"):
        parts = p.relative_to(ROOT).parts
        if any(part in BAD_PARTS for part in parts):
            bad.append(str(p.relative_to(ROOT)))
    return bad


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


def patch_cmd(cwd: Path, patch_path: Path, stage: str) -> Dict[str, object]:
    if stage == "forward-dry-run":
        cmd = ["patch", "--batch", "--forward", "--dry-run", "-p0", "-i", str(patch_path)]
        expected = 0
    elif stage == "forward-apply":
        cmd = ["patch", "--batch", "--forward", "-p0", "-i", str(patch_path)]
        expected = 0
    elif stage == "reverse-dry-run-after-apply":
        cmd = ["patch", "--batch", "--reverse", "--dry-run", "-p0", "-i", str(patch_path)]
        expected = 0
    elif stage == "second-forward-dry-run-rejected":
        cmd = ["patch", "--batch", "--forward", "--dry-run", "-p0", "-i", str(patch_path)]
        expected = 1
    else:
        raise ValueError(stage)
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=45)
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return {
        "stage": stage,
        "command": " ".join(cmd[:5]) + " ...",
        "expected_rc": str(expected),
        "observed_rc": str(proc.returncode),
        "status": "pass" if proc.returncode == expected else "fail",
        "summary": " | ".join(lines[-8:]),
    }


def test_summary(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if re.search(r"\d+ (failed|passed|errors?|error)|^OK$|^FAILED", line, re.I):
            return line
    return lines[-1] if lines else ""


def run_fixed_test(lane: str, source_dir: Path, packet: str, test_rel: str, runner: str, env_kind: str, out_dir: Path) -> Dict[str, object]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if env_kind == "NICOTINE_SOURCE":
        env.pop("PYTHONPATH", None)
        env["NICOTINE_SOURCE"] = str(source_dir)
    else:
        env["PYTHONPATH"] = str(source_dir)
    if runner == "unittest":
        cmd = [sys.executable, str(ROOT / test_rel)]
    else:
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=short", str(ROOT / test_rel)]
    out_dir.mkdir(parents=True, exist_ok=True)
    output_file = out_dir / f"{lane}__{packet}__patch-file-roundtrip-fixed-regression.txt".replace("/", "_")
    with output_file.open("w", encoding="utf-8") as fh:
        proc = subprocess.Popen(cmd, cwd="/tmp", env=env, stdout=fh, stderr=subprocess.STDOUT, text=True, start_new_session=True)
        try:
            rc = proc.wait(timeout=90)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            rc = 124
    text = output_file.read_text(encoding="utf-8", errors="replace")
    return {
        "lane": lane,
        "packet": packet,
        "stage": "patch-file-roundtrip-fixed-regression",
        "runner": runner,
        "env_kind": env_kind,
        "expected_rc": "0",
        "observed_rc": str(rc),
        "status": "pass" if rc == 0 else "fail",
        "summary": test_summary(text),
        "test": test_rel,
        "output_file": output_file.name,
    }


def run_roundtrip(source_zip: Path, lanes: List[str], out_dir: Path) -> Dict[str, List[Dict[str, object]]]:
    manifest = {row["lane"]: row for row in read_csv("data/rev0057_patch_queue_manifest.csv")}
    expected_hashes = {(row["lane"], row["file"]): row["new_sha256"] for row in read_csv("data/rev0057_patch_queue_file_hashes.csv")}
    apply_rows: List[Dict[str, object]] = []
    hash_rows: List[Dict[str, object]] = []
    test_rows: List[Dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="rev0058-roundtrip-") as td:
        td_path = Path(td)
        for lane in lanes:
            lane_src = td_path / "source" / lane
            file_count = extract_lane(source_zip, lane, lane_src)
            patch_rel = manifest[lane]["patch"]
            patch_path = ROOT / patch_rel
            for stage in ("forward-dry-run", "forward-apply", "reverse-dry-run-after-apply", "second-forward-dry-run-rejected"):
                result = patch_cmd(lane_src, patch_path, stage)
                apply_rows.append({"lane": lane, "patch": patch_rel, "source_file_count": file_count, **result})
                if result["status"] != "pass" and stage in {"forward-dry-run", "forward-apply"}:
                    break
            for file_rel in AFFECTED:
                file_path = lane_src / file_rel
                got = sha_path(file_path) if file_path.exists() else "missing"
                want = expected_hashes.get((lane, file_rel), "")
                hash_rows.append({
                    "lane": lane,
                    "file": file_rel,
                    "expected_sha256": want,
                    "observed_sha256": got,
                    "status": "pass" if got == want else "fail",
                })
            for packet, test_rel, runner, env_kind in FIXED_TESTS:
                test_rows.append(run_fixed_test(lane, lane_src, packet, test_rel, runner, env_kind, out_dir))
    return {"apply_rows": apply_rows, "hash_rows": hash_rows, "test_rows": test_rows}


def load_recorded_counts() -> Dict[str, object]:
    counts: Dict[str, object] = {}
    for name, rel in (
        ("apply_rows", "data/rev0058_patch_roundtrip_apply_matrix.csv"),
        ("hash_rows", "data/rev0058_patch_roundtrip_file_hashes.csv"),
        ("test_rows", "data/rev0058_patch_roundtrip_fixed_regression_matrix.csv"),
    ):
        path = ROOT / rel
        if path.exists():
            rows = read_csv(rel)
            counts[name] = len(rows)
            counts[name + "_pass"] = sum(1 for r in rows if r.get("status") == "pass")
        else:
            counts[name] = 0
            counts[name + "_pass"] = 0
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description="rev0058 patch-file roundtrip and regression gate")
    ap.add_argument("--source-zip", default="/mnt/data/Nicotine-source(1).zip")
    ap.add_argument("--run-tests", action="store_true", help="apply rev0057 patch files to clean source lanes and run fixed regressions")
    ap.add_argument("--lane", action="append", choices=LANES, help="limit run-tests to one or more lanes")
    ap.add_argument("--out-dir", default="evidence/rev0058-patch-roundtrip-rerun", help="where raw test output is written when --run-tests is enabled")
    ap.add_argument("--write-data", action="store_true", help="write rev0058 data CSV/JSON files from a --run-tests execution")
    ns = ap.parse_args()

    source_zip = Path(ns.source_zip)
    checks: List[Dict[str, object]] = []
    errors: List[str] = []

    source_info = source_identity(source_zip)
    source_ok = bool(source_info.get("exists")) and source_info.get("sha256") == EXPECTED_SOURCE_SHA256 and set(source_info.get("lanes", [])) == set(LANES)
    checks.append({"check": "uploaded source bundle identity", "status": "pass" if source_ok else "fail", **source_info})
    if not source_ok:
        errors.append("uploaded source bundle identity")

    rev0057_manifest_rows = read_csv("data/rev0057_patch_queue_manifest.csv")
    manifest_ok = len(rev0057_manifest_rows) == 3 and {r["lane"] for r in rev0057_manifest_rows} == set(LANES)
    checks.append({"check": "inherited rev0057 patch manifest shape", "status": "pass" if manifest_ok else "fail", "rows": len(rev0057_manifest_rows)})
    if not manifest_ok:
        errors.append("inherited rev0057 patch manifest shape")

    for row in rev0057_manifest_rows:
        patch_path = ROOT / row["patch"]
        ok = patch_path.exists() and sha_path(patch_path) == row["sha256"]
        checks.append({"check": f"rev0057 patch hash {row['lane']}", "status": "pass" if ok else "fail", "patch": row["patch"]})
        if not ok:
            errors.append(f"rev0057 patch hash {row['lane']}")

    if ns.run_tests:
        if not source_ok:
            errors.append("run-tests blocked by source identity")
        else:
            lanes = ns.lane or list(LANES)
            run = run_roundtrip(source_zip, lanes, ROOT / ns.out_dir)
            apply_rows = run["apply_rows"]
            hash_rows = run["hash_rows"]
            test_rows = run["test_rows"]
            for label, data_rows in (("patch apply roundtrip", apply_rows), ("patched file hashes", hash_rows), ("fixed regressions after patch-file apply", test_rows)):
                ok = bool(data_rows) and all(r.get("status") == "pass" for r in data_rows)
                checks.append({"check": label, "status": "pass" if ok else "fail", "rows": len(data_rows), "pass_rows": sum(1 for r in data_rows if r.get("status") == "pass")})
                if not ok:
                    errors.append(label)
            if ns.write_data:
                write_csv(ROOT / "data/rev0058_patch_roundtrip_apply_matrix.csv", apply_rows, ["lane", "patch", "source_file_count", "stage", "command", "expected_rc", "observed_rc", "status", "summary"])
                (ROOT / "data/rev0058_patch_roundtrip_apply_matrix.json").write_text(json.dumps(apply_rows, indent=2), encoding="utf-8")
                write_csv(ROOT / "data/rev0058_patch_roundtrip_file_hashes.csv", hash_rows, ["lane", "file", "expected_sha256", "observed_sha256", "status"])
                (ROOT / "data/rev0058_patch_roundtrip_file_hashes.json").write_text(json.dumps(hash_rows, indent=2), encoding="utf-8")
                write_csv(ROOT / "data/rev0058_patch_roundtrip_fixed_regression_matrix.csv", test_rows, ["lane", "packet", "stage", "runner", "env_kind", "expected_rc", "observed_rc", "status", "summary", "test", "output_file"])
                (ROOT / "data/rev0058_patch_roundtrip_fixed_regression_matrix.json").write_text(json.dumps(test_rows, indent=2), encoding="utf-8")
                summary_rows = [
                    {"metric": "source_bundle_used", "value": "yes"},
                    {"metric": "source_zip_sha256", "value": EXPECTED_SOURCE_SHA256},
                    {"metric": "patch_apply_roundtrip_rows", "value": str(len(apply_rows))},
                    {"metric": "patch_apply_roundtrip_pass", "value": str(sum(1 for r in apply_rows if r.get("status") == "pass"))},
                    {"metric": "patched_file_hash_rows", "value": str(len(hash_rows))},
                    {"metric": "patched_file_hash_pass", "value": str(sum(1 for r in hash_rows if r.get("status") == "pass"))},
                    {"metric": "fixed_regression_rows_after_patch_file_apply", "value": str(len(test_rows))},
                    {"metric": "fixed_regression_pass_after_patch_file_apply", "value": str(sum(1 for r in test_rows if r.get("status") == "pass"))},
                    {"metric": "new_private_packets", "value": "0"},
                    {"metric": "fresh_current_checkout_completed", "value": "no"},
                ]
                write_csv(ROOT / "data/rev0058_patch_roundtrip_summary.csv", summary_rows, ["metric", "value"])
                (ROOT / "data/rev0058_patch_roundtrip_summary.json").write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")
    else:
        counts = load_recorded_counts()
        recorded_ok = counts.get("apply_rows") == 12 and counts.get("apply_rows_pass") == 12 and counts.get("hash_rows") == 15 and counts.get("hash_rows_pass") == 15 and counts.get("test_rows") == 21 and counts.get("test_rows_pass") == 21
        checks.append({"check": "recorded rev0058 roundtrip data", "status": "pass" if recorded_ok else "fail", **counts})
        if not recorded_ok:
            errors.append("recorded rev0058 roundtrip data")

    for rel in ("handoff/rev0057/MANIFEST.sha256", "handoff/rev0058/MANIFEST.sha256"):
        if (ROOT / rel).exists():
            e = manifest_errors(rel)
            checks.append({"check": f"manifest {rel}", "status": "pass" if not e else "fail", "errors": e[:5]})
            errors.extend(e)

    bad = package_hygiene()
    checks.append({"check": "package hygiene", "status": "pass" if not bad else "fail", "bad_count": len(bad), "examples": bad[:10]})
    errors.extend([f"hygiene:{x}" for x in bad])

    output = {"revision": "rev0058", "status": "pass" if not errors else "fail", "checks": checks, "errors": errors}
    print(json.dumps(output, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
