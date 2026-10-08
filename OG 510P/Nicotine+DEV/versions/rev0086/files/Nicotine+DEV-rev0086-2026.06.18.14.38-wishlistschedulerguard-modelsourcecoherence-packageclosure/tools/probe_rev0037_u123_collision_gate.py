#!/usr/bin/env python3
'''Probe the rev0037 U-123 selected fix gate against archived source lanes.

Usage:
  python tools/probe_rev0037_u123_collision_gate.py /path/to/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z

The helper copies only each lane's pynicotine package into a temporary directory,
applies the selected prototype patch in-memory on the copy, and runs the rev0037
collision-rejection regression. It does not modify the supplied source tree.
'''

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")
OLD_DEACTIVATE = '''    def _deactivate_transfer(self, transfer):\n\n        username = transfer.username\n        token = transfer.token\n\n        if token is None or token not in self.active_users.get(username, {}):\n            return False\n\n        del self.active_users[username][token]\n\n        if not self.active_users[username]:\n            del self.active_users[username]\n\n        if transfer.speed > 0:\n            self.total_bandwidth = max(0, self.total_bandwidth - transfer.speed)\n\n        if transfer.request_timer_id is not None:\n            events.cancel_scheduled(transfer.request_timer_id)\n            transfer.request_timer_id = None\n\n        transfer.speed = transfer.avg_speed\n        transfer.sock = None\n        transfer.token = None\n\n        return True\n'''
NEW_DEACTIVATE = '''    def _deactivate_transfer(self, transfer):\n\n        username = transfer.username\n        token = transfer.token\n\n        if token is None:\n            return False\n\n        active_transfers = self.active_users.get(username, {})\n        active_transfer = active_transfers.get(token)\n        deactivated = False\n\n        if active_transfer is transfer:\n            del active_transfers[token]\n\n            if not active_transfers:\n                del self.active_users[username]\n\n            deactivated = True\n\n        if transfer.speed > 0:\n            self.total_bandwidth = max(0, self.total_bandwidth - transfer.speed)\n\n        if transfer.request_timer_id is not None:\n            events.cancel_scheduled(transfer.request_timer_id)\n            transfer.request_timer_id = None\n\n        transfer.speed = transfer.avg_speed\n        transfer.sock = None\n        transfer.token = None\n\n        return deactivated\n'''
OLD_DOWNLOAD = '''        log.add_transfer("Received download request with token %s for file %s from user %s",\n                         (token, virtual_path, username))\n\n        download = (self.queued_users.get(username, {}).get(virtual_path)\n                    or self.failed_users.get(username, {}).get(virtual_path))\n'''
NEW_DOWNLOAD = '''        log.add_transfer("Received download request with token %s for file %s from user %s",\n                         (token, virtual_path, username))\n\n        download = (self.queued_users.get(username, {}).get(virtual_path)\n                    or self.failed_users.get(username, {}).get(virtual_path))\n        active_download = self.active_users.get(username, {}).get(token)\n\n        if active_download is not None and active_download is not download:\n            log.add_transfer("Rejected duplicate download request with token %s for file %s from user %s; "\n                             "token is already bound to active file %s",\n                             (token, virtual_path, username, active_download.virtual_path))\n            reason = TransferRejectReason.QUEUED if download is not None else TransferRejectReason.CANCELLED\n            return TransferResponse(allowed=False, reason=reason, token=token)\n'''


def patch_file(path: pathlib.Path, old: str, new: str) -> None:
    text = path.read_text()
    if old not in text:
        raise RuntimeError(f"patch anchor not found in {path}")
    path.write_text(text.replace(old, new))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    source_root = pathlib.Path(argv[1]) / "source-trees"
    cube_root = pathlib.Path(__file__).resolve().parents[1]
    test_path = cube_root / "maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py"
    records = []

    with tempfile.TemporaryDirectory(prefix="nplus-u123-rev0037-") as tmp:
        tmp_path = pathlib.Path(tmp)
        for lane in LANES:
            lane_src = source_root / lane / "pynicotine"
            lane_dst = tmp_path / lane
            lane_dst.mkdir()
            shutil.copytree(lane_src, lane_dst / "pynicotine", ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
            patch_file(lane_dst / "pynicotine/transfers.py", OLD_DEACTIVATE, NEW_DEACTIVATE)
            patch_file(lane_dst / "pynicotine/downloads.py", OLD_DOWNLOAD, NEW_DOWNLOAD)
            env = os.environ.copy()
            env["PYTHONPATH"] = str(lane_dst)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            proc = subprocess.run([sys.executable, str(test_path)], cwd=str(tmp_path), env=env,
                                  text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
            records.append({
                "lane": lane,
                "test": "collision_rejection_regression_selected_patch",
                "exit": proc.returncode,
                "passed": proc.returncode == 0,
                "tail": proc.stdout[-1200:]
            })

    print(json.dumps(records, indent=2))
    return 0 if all(r["passed"] for r in records) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
