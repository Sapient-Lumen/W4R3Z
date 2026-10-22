#!/usr/bin/env python3
"""Write or clear a bounded control note for a specific finite loop."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


ROOT = pathlib.Path("/home/overseer")
CONTROL_ROOT = pathlib.Path(
    os.environ.get("OVERSEER_LOOP_CONTROL_ROOT", str(ROOT / "state" / "loop-control"))
)
NOTES_ROOT = CONTROL_ROOT / "notes"
ACTION_CHOICES = {
    "inform",
    "focus-next-turn",
    "stop-after-turn",
    "hold-after-turn",
    "cancel-before-turn",
}
ROOM_REFRESH_SCRIPT = ROOT / "scripts" / "refresh_loop_room_briefs.py"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_write_text(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        pathlib.Path(tmp_name).replace(path)
    finally:
        tmp = pathlib.Path(tmp_name)
        if tmp.exists():
            tmp.unlink()


def note_paths(loop_id: str) -> tuple[pathlib.Path, pathlib.Path]:
    return NOTES_ROOT / f"{loop_id}.json", NOTES_ROOT / f"{loop_id}.md"


def render_markdown(payload: dict[str, object]) -> str:
    consumed_turn = payload.get("consumed_turn")
    lines = [
        "# Loop Control Note",
        "",
        f"- status: {payload.get('status') or 'unknown'}",
        f"- loop_id: {payload.get('loop_id') or '(none)'}",
        f"- updated_at: {payload.get('updated_at') or '(none)'}",
        f"- action: {payload.get('action') or '(none)'}",
        f"- priority: {payload.get('priority') or 'normal'}",
        f"- requested_by: {payload.get('requested_by') or 'interactive'}",
        f"- summary: {payload.get('summary') or '(none)'}",
        "",
    ]
    body = str(payload.get("body") or "").strip()
    if body:
        lines.extend(["## Body", "", body, ""])
    if payload.get("status") == "consumed":
        lines.extend(
            [
                "## Consumption",
                "",
                f"- consumed_at: {payload.get('consumed_at') or '(none)'}",
                f"- consumed_by: {payload.get('consumed_by') or '(none)'}",
                f"- consumed_reason: {payload.get('consumed_reason') or '(none)'}",
                f"- consumed_turn: {consumed_turn if consumed_turn is not None else '(none)'}",
                "",
            ]
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loop-id", required=True)
    parser.add_argument("--action", choices=sorted(ACTION_CHOICES))
    parser.add_argument("--summary")
    parser.add_argument("--body")
    parser.add_argument("--body-file")
    parser.add_argument("--priority", default="normal", choices=["low", "normal", "high", "urgent"])
    parser.add_argument("--requested-by", default="interactive")
    parser.add_argument("--clear", action="store_true")
    parser.add_argument("--no-refresh", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    json_path, md_path = note_paths(args.loop_id)

    if args.clear:
        payload: dict[str, object] = {
            "status": "cleared",
            "loop_id": args.loop_id,
            "updated_at": utc_now_iso(),
            "action": None,
            "priority": None,
            "requested_by": None,
            "summary": None,
            "body": None,
            "consumed_at": None,
            "consumed_by": None,
            "consumed_reason": None,
            "consumed_turn": None,
        }
    else:
        if not args.action:
            raise SystemExit("--action is required unless --clear is used")
        if not args.summary:
            raise SystemExit("--summary is required unless --clear is used")
        body = args.body or ""
        if args.body_file:
            body = pathlib.Path(args.body_file).read_text(encoding="utf-8")
        payload = {
            "status": "active",
            "loop_id": args.loop_id,
            "updated_at": utc_now_iso(),
            "action": args.action,
            "priority": args.priority,
            "requested_by": args.requested_by,
            "summary": args.summary,
            "body": body,
            "consumed_at": None,
            "consumed_by": None,
            "consumed_reason": None,
            "consumed_turn": None,
        }

    atomic_write_text(json_path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    atomic_write_text(md_path, render_markdown(payload) + "\n")
    if not args.no_refresh and ROOM_REFRESH_SCRIPT.exists():
        try:
            subprocess.run([sys.executable, str(ROOM_REFRESH_SCRIPT)], check=True)
        except subprocess.CalledProcessError as exc:
            print(
                f"WARN  loop room refresh failed after writing control note (rc={exc.returncode})",
                file=sys.stderr,
            )
    if args.stdout:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"OK   wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
