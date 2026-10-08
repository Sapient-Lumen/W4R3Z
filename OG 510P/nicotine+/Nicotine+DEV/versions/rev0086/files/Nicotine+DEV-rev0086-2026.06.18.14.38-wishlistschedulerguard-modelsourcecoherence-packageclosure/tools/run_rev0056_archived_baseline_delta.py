#!/usr/bin/env python3
"""Optional rerun harness for rev0056 archived-source baseline checks.

Recommended use is lane-by-lane, for example:
  python tools/run_rev0056_archived_baseline_delta.py --source-dir /path/to/extracted/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z --lane github-tag-3.3.10 --out /tmp/rev0056-baseline

The package includes recorded output under evidence/rev0056-baseline-delta-rerun/.
"""
from __future__ import annotations
import argparse, csv, json, os, pathlib, re, signal, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")
CURRENT = [
    ("U-123-current-witness", "maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_reproducer.py", "unittest", "PYTHONPATH", "U-123"),
    ("PB-01-current-witness", "maintainer_artifacts/pb01/test_peer_connection_primary_election_reproducer.py", "pytest", "NICOTINE_SOURCE", "PB-01"),
    ("SEARCH-RESP-current-witness", "maintainer_artifacts/search-resp-01/test_search_response_scope_and_parse_order_reproducer.py", "pytest", "PYTHONPATH", "SEARCH-RESP-SERIES"),
]
FIXED = [
    ("U-123", "maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py", "unittest", "PYTHONPATH"),
    ("PB-01", "maintainer_artifacts/pb01/test_peer_connection_primary_election_fixed_regression.py", "pytest", "NICOTINE_SOURCE"),
    ("SEARCH-RESP-01A", "maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-01B-BUDDY", "maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-01C-ROOM", "maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-PARSE-BUDGET-A", "maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-PARSE-BUDGET-B", "maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py", "pytest", "PYTHONPATH"),
]
FIELDS = ["lane", "packet", "check", "stage", "expected_rc", "observed_rc", "status", "summary", "test", "output_file"]

def source_trees(root: pathlib.Path) -> pathlib.Path:
    if (root / "source-trees").exists():
        return root / "source-trees"
    for child in root.iterdir():
        if (child / "source-trees").exists():
            return child / "source-trees"
    raise FileNotFoundError("could not locate source-trees")

def summary(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if re.search(r"\d+ (failed|passed|errors?|error)|^OK$|^FAILED", line, re.I):
            return line
    return lines[-1] if lines else ""

def run_one(lane: str, src: pathlib.Path, label: str, rel: str, runner: str, env_kind: str, packet: str, stage: str, expected_nonzero: bool, outdir: pathlib.Path) -> dict:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if env_kind == "NICOTINE_SOURCE":
        env.pop("PYTHONPATH", None)
        env["NICOTINE_SOURCE"] = str(src)
    else:
        env["PYTHONPATH"] = str(src)
    cmd = [sys.executable, str(ROOT / rel)] if runner == "unittest" else [sys.executable, "-m", "pytest", "-q", "--tb=short", str(ROOT / rel)]
    outfile = outdir / f"{lane}__{packet}__{stage}.txt".replace("/", "_")
    with outfile.open("w", encoding="utf-8") as fh:
        proc = subprocess.Popen(cmd, cwd="/tmp", env=env, stdout=fh, stderr=subprocess.STDOUT, text=True, start_new_session=True)
        try:
            rc = proc.wait(timeout=75)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            rc = 124
    text = outfile.read_text(encoding="utf-8", errors="replace")
    status = "pass" if ((rc != 0) if expected_nonzero else (rc == 0)) else "fail"
    return {
        "lane": lane,
        "packet": packet,
        "check": label,
        "stage": stage,
        "expected_rc": "nonzero" if expected_nonzero else "0",
        "observed_rc": str(rc),
        "status": status,
        "summary": summary(text),
        "test": rel,
        "output_file": outfile.name,
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", required=True, type=pathlib.Path, help="Extracted Nicotine-source root containing source-trees")
    ap.add_argument("--lane", action="append", choices=LANES, help="Lane(s) to run; defaults to all")
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ns = ap.parse_args()
    trees = source_trees(ns.source_dir.resolve())
    lanes = ns.lane or list(LANES)
    ns.out.mkdir(parents=True, exist_ok=True)
    records = []
    for lane in lanes:
        src = trees / lane
        for label, rel, runner, env_kind, packet in CURRENT:
            rec = run_one(lane, src, label, rel, runner, env_kind, packet, "archived-current-witness", False, ns.out)
            records.append(rec)
            print(f"{lane} {packet} {rec['stage']}: {rec['status']} {rec['summary']}", flush=True)
        for packet, rel, runner, env_kind in FIXED:
            rec = run_one(lane, src, f"{packet} fixed-regression on unpatched archived source", rel, runner, env_kind, packet, "archived-unpatched-fixed-regression", True, ns.out)
            records.append(rec)
            print(f"{lane} {packet} {rec['stage']}: {rec['status']} {rec['summary']}", flush=True)
    with (ns.out / "rev0056_baseline_delta_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(records)
    (ns.out / "rev0056_baseline_delta_matrix.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    status = "pass" if all(r["status"] == "pass" for r in records) else "fail"
    print(json.dumps({"status": status, "records": len(records)}, indent=2))
    return 0 if status == "pass" else 1

if __name__ == "__main__":
    raise SystemExit(main())
