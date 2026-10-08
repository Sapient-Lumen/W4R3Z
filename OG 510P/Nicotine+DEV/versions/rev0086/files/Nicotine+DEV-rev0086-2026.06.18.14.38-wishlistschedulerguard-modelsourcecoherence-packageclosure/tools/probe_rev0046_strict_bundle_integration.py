#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, pathlib, re, shutil, subprocess, sys, tempfile
LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")
TESTS = [
    ("U-123", "maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py", "unittest", "PYTHONPATH"),
    ("PB-01", "maintainer_artifacts/pb01/test_peer_connection_primary_election_fixed_regression.py", "pytest", "NICOTINE_SOURCE"),
    ("SEARCH-RESP-01A", "maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-01B-BUDDY", "maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-01C-ROOM", "maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-PARSE-BUDGET-A", "maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py", "pytest", "PYTHONPATH"),
    ("SEARCH-RESP-PARSE-BUDGET-B", "maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py", "pytest", "PYTHONPATH"),
]
def source_trees(path: pathlib.Path) -> pathlib.Path:
    return path / "source-trees" if (path / "source-trees").exists() else path
def copy_minimal(src: pathlib.Path, dst: pathlib.Path) -> None:
    dst.mkdir(parents=True)
    shutil.copytree(src / "pynicotine", dst / "pynicotine", ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"))
    for name in ("pyproject.toml", "setup.cfg", "setup.py", "README.md", "NEWS.md", "COPYING"):
        if (src / name).exists(): shutil.copy2(src / name, dst / name)
def run(args, cwd="/tmp", env=None):
    return subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=90)
def apply_stack(package: pathlib.Path, checkout: pathlib.Path):
    logs=[]
    for script in ("tools/apply_u123_collision_gate_patch_rev0046.py", "tools/apply_pb01_primary_guard_patch_rev0038.py", "tools/apply_search_resp_room_scope_patch_rev0043.py", "tools/apply_search_resp_result_budget_patch_rev0042.py"):
        proc=run([sys.executable, str(package/script), str(checkout)])
        logs.append({"script": script, "rc": proc.returncode, "output": proc.stdout.strip()[-500:]})
        if proc.returncode: raise RuntimeError(logs[-1])
    return logs
def run_test(package, checkout, packet, test_rel, runner, env_kind):
    env=os.environ.copy(); env["PYTHONDONTWRITEBYTECODE"]="1"; env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"]="1"
    if env_kind == "NICOTINE_SOURCE": env.pop("PYTHONPATH", None); env["NICOTINE_SOURCE"] = str(checkout)
    else: env["PYTHONPATH"] = str(checkout)
    cmd=[sys.executable, str(package/test_rel)] if runner == "unittest" else [sys.executable, "-m", "pytest", "-q", "--tb=short", str(package/test_rel)]
    proc=run(cmd, env=env)
    lines=[line.strip() for line in proc.stdout.splitlines() if line.strip()]
    summary=""
    for line in reversed(lines):
        if re.search(r"\d+ (failed|passed|errors?)|^OK$|^FAILED", line, re.I): summary=line; break
    if not summary and lines: summary=lines[-1]
    return {"lane": None, "packet": packet, "rc": proc.returncode, "passed": proc.returncode == 0, "summary": summary, "tail": lines[-8:]}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("source_root", type=pathlib.Path); ap.add_argument("--lane", choices=LANES, action="append")
    ns=ap.parse_args(); package=pathlib.Path(__file__).resolve().parents[1]; trees=source_trees(ns.source_root.resolve()); lanes=ns.lane or list(LANES)
    records=[]; patch_logs=[]
    with tempfile.TemporaryDirectory(prefix="rev0046-stack-") as td:
        td=pathlib.Path(td)
        for lane in lanes:
            checkout=td/lane; copy_minimal(trees/lane, checkout); patch_logs.extend(apply_stack(package, checkout))
            for spec in TESTS:
                rec=run_test(package, checkout, *spec); rec["lane"]=lane; records.append(rec); print(f"{lane} {rec['packet']}: rc={rec['rc']} {rec['summary']}", flush=True)
    ok=all(r["passed"] for r in records); print(json.dumps({"status": "ok" if ok else "failed", "patch_logs": patch_logs, "records": records}, indent=2)); return 0 if ok else 1
if __name__ == "__main__": raise SystemExit(main())
