#!/usr/bin/env python3
"""Rev0045 strict/front source-refresh gate runner.

Usage:
    python tools/probe_rev0045_strict_front_refresh.py /path/to/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z

This helper intentionally avoids embedding or modifying the source bundle. It
copies only each lane's pynicotine package into temporary patched checkouts,
runs one expected-failure fixed-regression smoke on current source, applies the
selected cube patch for each production-gated packet, then runs the fixed
regression on the patched temporary copy.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass

LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")


@dataclass(frozen=True)
class Packet:
    packet: str
    test: str
    runner: str  # pytest or unittest
    patcher: str | None = None
    current_env: str = "PYTHONPATH"  # PYTHONPATH or NICOTINE_SOURCE
    current_expect: str = "fail"      # fail or pass
    patched_expect: str = "pass"


PACKETS = (
    Packet("U-123", "maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py", "unittest", patcher="u123-inline"),
    Packet("PB-01", "maintainer_artifacts/pb01/test_peer_connection_primary_election_fixed_regression.py", "pytest", patcher="tools/apply_pb01_primary_guard_patch_rev0038.py", current_env="NICOTINE_SOURCE"),
    Packet("SEARCH-RESP-01A", "maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py", "pytest", patcher="tools/apply_search_resp_user_scope_patch_rev0039.py"),
    Packet("SEARCH-RESP-01B-BUDDY", "maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py", "pytest", patcher="tools/apply_search_resp_buddy_source_patch_rev0040.py"),
    Packet("SEARCH-RESP-PARSE-BUDGET-A", "maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py", "pytest", patcher="tools/apply_search_resp_prefix_budget_patch_rev0041.py"),
    Packet("SEARCH-RESP-PARSE-BUDGET-B", "maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py", "pytest", patcher="tools/apply_search_resp_result_budget_patch_rev0042.py"),
    Packet("SEARCH-RESP-01C-ROOM", "maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py", "pytest", patcher="tools/apply_search_resp_room_scope_patch_rev0043.py"),
)

U123_OLD_DEACTIVATE = '''    def _deactivate_transfer(self, transfer):\n\n        username = transfer.username\n        token = transfer.token\n\n        if token is None or token not in self.active_users.get(username, {}):\n            return False\n\n        del self.active_users[username][token]\n\n        if not self.active_users[username]:\n            del self.active_users[username]\n\n        if transfer.speed > 0:\n            self.total_bandwidth = max(0, self.total_bandwidth - transfer.speed)\n\n        if transfer.request_timer_id is not None:\n            events.cancel_scheduled(transfer.request_timer_id)\n            transfer.request_timer_id = None\n\n        transfer.speed = transfer.avg_speed\n        transfer.sock = None\n        transfer.token = None\n\n        return True\n'''
U123_NEW_DEACTIVATE = '''    def _deactivate_transfer(self, transfer):\n\n        username = transfer.username\n        token = transfer.token\n\n        if token is None:\n            return False\n\n        active_transfers = self.active_users.get(username, {})\n        active_transfer = active_transfers.get(token)\n        deactivated = False\n\n        if active_transfer is transfer:\n            del active_transfers[token]\n\n            if not active_transfers:\n                del self.active_users[username]\n\n            deactivated = True\n\n        if transfer.speed > 0:\n            self.total_bandwidth = max(0, self.total_bandwidth - transfer.speed)\n\n        if transfer.request_timer_id is not None:\n            events.cancel_scheduled(transfer.request_timer_id)\n            transfer.request_timer_id = None\n\n        transfer.speed = transfer.avg_speed\n        transfer.sock = None\n        transfer.token = None\n\n        return deactivated\n'''
U123_OLD_DOWNLOAD = '''        log.add_transfer("Received download request with token %s for file %s from user %s",\n                         (token, virtual_path, username))\n\n        download = (self.queued_users.get(username, {}).get(virtual_path)\n                    or self.failed_users.get(username, {}).get(virtual_path))\n'''
U123_NEW_DOWNLOAD = '''        log.add_transfer("Received download request with token %s for file %s from user %s",\n                         (token, virtual_path, username))\n\n        download = (self.queued_users.get(username, {}).get(virtual_path)\n                    or self.failed_users.get(username, {}).get(virtual_path))\n        active_download = self.active_users.get(username, {}).get(token)\n\n        if active_download is not None and active_download is not download:\n            log.add_transfer("Rejected duplicate download request with token %s for file %s from user %s; "\n                             "token is already bound to active file %s",\n                             (token, virtual_path, username, active_download.virtual_path))\n            reason = TransferRejectReason.QUEUED if download is not None else TransferRejectReason.CANCELLED\n            return TransferResponse(allowed=False, reason=reason, token=token)\n'''


def resolve_source_root(arg: pathlib.Path) -> pathlib.Path:
    if (arg / "source-trees").exists():
        return arg / "source-trees"
    return arg


def lane_root(source_root: pathlib.Path, lane: str) -> pathlib.Path:
    path = source_root / lane
    if not (path / "pynicotine").exists():
        raise FileNotFoundError(f"missing lane pynicotine package: {path}")
    return path


def copy_minimal_checkout(src: pathlib.Path, dst: pathlib.Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src / "pynicotine", dst / "pynicotine", ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"))
    for name in ("pyproject.toml", "setup.cfg", "setup.py", "README.md", "NEWS.md", "COPYING"):
        src_file = src / name
        if src_file.exists():
            shutil.copy2(src_file, dst / name)


def replace_once(path: pathlib.Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"patch anchor not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def apply_u123_patch(root: pathlib.Path) -> None:
    replace_once(root / "pynicotine" / "transfers.py", U123_OLD_DEACTIVATE, U123_NEW_DEACTIVATE)
    replace_once(root / "pynicotine" / "downloads.py", U123_OLD_DOWNLOAD, U123_NEW_DOWNLOAD)


def apply_packet_patch(package_root: pathlib.Path, packet: Packet, checkout: pathlib.Path) -> None:
    if packet.patcher == "u123-inline":
        apply_u123_patch(checkout)
        return
    assert packet.patcher is not None
    subprocess.run([sys.executable, str(package_root / packet.patcher), str(checkout)], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)


def run_test(package_root: pathlib.Path, source_tree: pathlib.Path, packet: Packet, *, expect_fail_fast: bool) -> dict:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if packet.current_env == "NICOTINE_SOURCE":
        env["NICOTINE_SOURCE"] = str(source_tree)
    else:
        env["PYTHONPATH"] = str(source_tree)

    test_path = package_root / packet.test
    if packet.runner == "unittest":
        cmd = [sys.executable, str(test_path)]
    else:
        cmd = [sys.executable, "-m", "pytest", "-q", "--tb=short"]
        if expect_fail_fast:
            cmd.append("--maxfail=1")
        cmd.append(str(test_path))

    proc = subprocess.run(cmd, cwd=str(package_root), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=90)
    output = proc.stdout
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    summary = ""
    for line in reversed(lines):
        if re.search(r"\d+ (failed|passed|error|errors)", line, re.I) or line in {"OK", "FAILED"}:
            summary = line
            break
    if not summary and lines:
        summary = lines[-1]
    return {"rc": proc.returncode, "passed": proc.returncode == 0, "summary": summary, "tail": lines[-8:]}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    package_root = pathlib.Path(__file__).resolve().parents[1]
    source_root = resolve_source_root(pathlib.Path(argv[1]).resolve())
    records = []
    ok = True

    with tempfile.TemporaryDirectory(prefix="rev0045-strict-refresh-") as tmp_name:
        tmp_root = pathlib.Path(tmp_name)
        for packet in PACKETS:
            for lane in LANES:
                current = lane_root(source_root, lane)
                current_run = run_test(package_root, current, packet, expect_fail_fast=(packet.current_expect == "fail"))
                patched = tmp_root / packet.packet.lower().replace("/", "-").replace(" ", "-") / lane
                copy_minimal_checkout(current, patched)
                apply_packet_patch(package_root, packet, patched)
                patched_run = run_test(package_root, patched, packet, expect_fail_fast=False)
                gate_ok = (not current_run["passed"]) and patched_run["passed"]
                ok = ok and gate_ok
                records.append({
                    "packet": packet.packet,
                    "lane": lane,
                    "current_fixed_regression": current_run,
                    "selected_patch_fixed_regression": patched_run,
                    "gate_ok": gate_ok,
                })
                print(f"{packet.packet} {lane}: current rc={current_run['rc']} {current_run['summary']} | patched rc={patched_run['rc']} {patched_run['summary']} | gate_ok={gate_ok}", flush=True)

    print(json.dumps({"status": "ok" if ok else "failed", "records": records}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
