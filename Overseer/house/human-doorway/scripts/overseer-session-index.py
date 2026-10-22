#!/usr/bin/env python3
import argparse
import datetime as dt
import glob
import json
import os
import sys
from typing import Any


def load_history(path: str) -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = {}
    if not os.path.isfile(path):
        return data

    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError:
                continue
            session_id = row.get("session_id")
            if not session_id:
                continue
            ts = int(row.get("ts", 0) or 0)
            text = " ".join(str(row.get("text", "")).split())
            current = data.get(session_id)
            if current is None or ts >= current["last_activity_ts"]:
                data[session_id] = {
                    "last_activity_ts": ts,
                    "last_text": text,
                }
    return data


def scope_rank(cwd: str, workspace: str, scope_dirs: list[str]) -> tuple[bool, int, str]:
    if cwd == workspace or cwd.startswith(workspace.rstrip("/") + "/"):
        return True, 0, "workspace"

    for idx, root in enumerate(scope_dirs, start=1):
        root = root.rstrip("/")
        if cwd == root or cwd.startswith(root + "/"):
            return True, idx, os.path.basename(root) or root

    return False, 99, "other"


def to_iso(ts: int, fallback: str) -> str:
    if ts > 0:
        return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    return fallback


def load_sessions(root: str, history: dict[str, dict[str, Any]], workspace: str, scope_dirs: list[str]) -> list[dict[str, Any]]:
    sessions: list[dict[str, Any]] = []
    pattern = os.path.join(root, "*", "*", "*", "*.jsonl")
    for path in sorted(glob.glob(pattern)):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                first_line = handle.readline()
        except OSError:
            continue

        if not first_line:
            continue

        try:
            row = json.loads(first_line)
        except json.JSONDecodeError:
            continue

        if row.get("type") != "session_meta":
            continue

        payload = row.get("payload", {})
        session_id = payload.get("id")
        cwd = payload.get("cwd", "")
        started_at = payload.get("timestamp", "")
        if not session_id or not cwd:
            continue

        history_row = history.get(session_id, {})
        last_activity_ts = int(history_row.get("last_activity_ts", 0) or 0)
        last_text = history_row.get("last_text", "")
        in_scope, rank, scope_label = scope_rank(cwd, workspace, scope_dirs)
        sessions.append(
            {
                "session_id": session_id,
                "session_file": path,
                "cwd": cwd,
                "started_at": started_at,
                "last_activity_ts": last_activity_ts,
                "last_activity_iso": to_iso(last_activity_ts, started_at),
                "last_text": last_text,
                "in_scope": in_scope,
                "scope_rank": rank,
                "scope_label": scope_label,
            }
        )

    sessions.sort(
        key=lambda item: (
            int(item["scope_rank"]),
            -int(item["last_activity_ts"]),
            item["started_at"],
            item["session_id"],
        )
    )
    return sessions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions-root", required=True)
    parser.add_argument("--history", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--scope-dir", action="append", default=[])
    args = parser.parse_args()

    history = load_history(args.history)
    rows = load_sessions(args.sessions_root, history, args.workspace, args.scope_dir)
    json.dump(rows, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
