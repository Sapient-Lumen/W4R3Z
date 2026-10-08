#!/usr/bin/env python3
"""Launch several MTGSim C++ test shards and aggregate their reports.

This is a local/CI convenience wrapper around tools/run_cpp_tests.py. It is
useful when a future suite has thousands of cases and we want decomposition at
both levels: shards across machines or processes, and jobs within each shard.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import pathlib
import shlex
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from typing import Any

os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "harness" / "shards"


def rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def tail(text: str, limit: int = 4000) -> str:
    return text[-limit:] if len(text) > limit else text


def run_shard(index: int, args: argparse.Namespace, started: float) -> dict[str, Any]:
    report_path = REPORT_DIR / f"cpp_shard_{index:03d}.json"
    junit_path = REPORT_DIR / f"cpp_shard_{index:03d}.xml"
    cmd = [
        sys.executable,
        "tools/run_cpp_tests.py",
        "--mode", args.mode,
        "--jobs", args.jobs,
        "--repeat", str(args.repeat),
        "--case-timeout-sec", f"{args.case_timeout_sec:.3f}",
        "--shard-count", str(args.shards),
        "--shard-index", str(index),
        "--shard-strategy", args.shard_strategy,
        "--report", str(report_path),
        "--junit", str(junit_path),
        "--json",
    ]
    if args.filter:
        cmd.extend(["--filter", args.filter])
    for tag in args.tag:
        cmd.extend(["--tag", tag])
    for tag in args.exclude_tag:
        cmd.extend(["--exclude-tag", tag])
    for rule in args.rule:
        cmd.extend(["--rule", rule])
    if args.shuffle_seed is not None:
        cmd.extend(["--shuffle-seed", str(args.shuffle_seed + index)])
    if args.no_history_balance:
        cmd.append("--no-history-balance")
    if args.fail_fast:
        cmd.append("--fail-fast")
    if args.verbose:
        cmd.append("--verbose")
    remaining = None
    if args.budget_sec is not None:
        remaining = max(0.001, args.budget_sec - (time.perf_counter() - started))
        cmd.extend(["--budget-sec", f"{remaining:.3f}"])
    print(f"[shard {index}] + {' '.join(shlex.quote(part) for part in cmd)}", flush=True)
    begin = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=remaining)
        duration = time.perf_counter() - begin
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - begin
        return {
            "shard_index": index,
            "status": "failed",
            "returncode": 124,
            "duration_sec": duration,
            "command": cmd,
            "stdout_tail": tail(exc.stdout if isinstance(exc.stdout, str) else ""),
            "stderr_tail": tail(exc.stderr if isinstance(exc.stderr, str) else "") + f"\nTIMEOUT after {duration:.3f}s",
            "report_path": rel(report_path),
            "junit_path": rel(junit_path),
            "summary": {},
            "selection": {},
        }
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    report: dict[str, Any] = {}
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    return {
        "shard_index": index,
        "status": "passed" if proc.returncode == 0 else "failed",
        "returncode": proc.returncode,
        "duration_sec": duration,
        "command": cmd,
        "stdout_tail": tail(proc.stdout),
        "stderr_tail": tail(proc.stderr),
        "report_path": rel(report_path),
        "junit_path": rel(junit_path),
        "summary": report.get("summary", {}),
        "selection": report.get("selection", {}),
    }


def write_junit(path: pathlib.Path, shard_results: list[dict[str, Any]]) -> None:
    suite = ET.Element("testsuite", {
        "name": "mtgsim_cpp_shards",
        "tests": str(len(shard_results)),
        "failures": str(sum(1 for row in shard_results if row.get("status") != "passed")),
        "time": f"{sum(float(row.get('duration_sec') or 0.0) for row in shard_results):.6f}",
    })
    for row in shard_results:
        case = ET.SubElement(suite, "testcase", {
            "classname": "mtgsim.cpp.shards",
            "name": f"shard_{int(row.get('shard_index', 0)):03d}",
            "time": f"{float(row.get('duration_sec') or 0.0):.6f}",
        })
        if row.get("status") != "passed":
            failure = ET.SubElement(case, "failure", {"message": f"returncode={row.get('returncode')}"})
            failure.text = (str(row.get("stderr_tail") or row.get("stdout_tail") or ""))[:4000]
        if row.get("stdout_tail"):
            ET.SubElement(case, "system-out").text = str(row.get("stdout_tail"))
        if row.get("stderr_tail"):
            ET.SubElement(case, "system-err").text = str(row.get("stderr_tail"))
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["debug", "release", "sanitize", "profile"], default="release")
    parser.add_argument("--shards", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    parser.add_argument("--max-parallel-shards", type=int, default=None)
    parser.add_argument("--jobs", default="1", help="Jobs per shard. Keep low when many shards run locally.")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--filter", default="")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--exclude-tag", action="append", default=[])
    parser.add_argument("--rule", action="append", default=[])
    parser.add_argument("--shuffle-seed", type=int, default=None)
    parser.add_argument("--case-timeout-sec", type=float, default=5.0)
    parser.add_argument("--budget-sec", type=float, default=None)
    parser.add_argument("--shard-strategy", choices=["round-robin", "hash", "duration-greedy"], default="duration-greedy")
    parser.add_argument("--no-history-balance", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--report", type=pathlib.Path, default=ROOT / "reports" / "harness" / "cpp_shards_latest.json")
    parser.add_argument("--junit", type=pathlib.Path, default=ROOT / "reports" / "harness" / "cpp_shards_latest.xml")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.shards <= 0:
        raise SystemExit("--shards must be positive")
    if args.repeat <= 0:
        raise SystemExit("--repeat must be positive")
    max_workers = args.max_parallel_shards or min(args.shards, os.cpu_count() or 1)
    started = time.perf_counter()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    shard_results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, max_workers)) as executor:
        futures = {executor.submit(run_shard, index, args, started): index for index in range(args.shards)}
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            shard_results.append(row)
            print(f"[shard {row['shard_index']}] {row['status']} in {row['duration_sec']:.3f}s", flush=True)
            if args.fail_fast and row["status"] != "passed":
                for pending in futures:
                    pending.cancel()
                break
    shard_results.sort(key=lambda row: int(row["shard_index"]))
    duration = time.perf_counter() - started
    failures = sum(1 for row in shard_results if row.get("status") != "passed")
    aggregate = {
        "schema": "mtgsim.cpp_shards_report.v1",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "status": "passed" if failures == 0 and len(shard_results) == args.shards else "failed",
        "duration_sec": duration,
        "config": {
            "mode": args.mode,
            "shards": args.shards,
            "max_parallel_shards": max_workers,
            "jobs_per_shard": args.jobs,
            "repeat": args.repeat,
            "filter": args.filter,
            "tags": args.tag,
            "exclude_tags": args.exclude_tag,
            "rules": args.rule,
            "shard_strategy": args.shard_strategy,
            "history_balance": not args.no_history_balance,
            "budget_sec": args.budget_sec,
        },
        "summary": {
            "shards_completed": len(shard_results),
            "shards_failed": failures,
            "case_jobs": sum(int((row.get("summary") or {}).get("case_jobs") or 0) for row in shard_results),
            "passed": sum(int((row.get("summary") or {}).get("passed") or 0) for row in shard_results),
            "failed": sum(int((row.get("summary") or {}).get("failed") or 0) for row in shard_results),
            "timeouts": sum(int((row.get("summary") or {}).get("timeouts") or 0) for row in shard_results),
            "cases_selected_total": sum(int((row.get("selection") or {}).get("cases_selected_on_shard") or 0) for row in shard_results),
        },
        "shards": shard_results,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_junit(args.junit, shard_results)
    print(f"cpp shards {aggregate['status']} in {duration:.3f}s; report={rel(args.report)} junit={rel(args.junit)}")
    if args.json:
        print(json.dumps(aggregate, sort_keys=True))
    return 0 if aggregate["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
