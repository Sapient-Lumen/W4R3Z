from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]


def default_home() -> Path:
    return Path(os.environ.get("GLASSTTY_HOME", Path.home() / ".local" / "share" / "glasstty"))


def socket_path() -> Path:
    return default_home() / "run" / "daemon.sock"


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_envelope(message_type: str, payload: JsonDict, *, tab_id: int | None = None) -> JsonDict:
    envelope: JsonDict = {
        "version": "0.1",
        "request_id": str(uuid.uuid4()),
        "type": message_type,
        "timestamp": iso_now(),
        "payload": payload,
    }
    if tab_id is not None:
        envelope["tab_id"] = tab_id
    return envelope


class SocketClient:
    def __init__(self, path: Path):
        self.path = path
        self.sock: socket.socket | None = None
        self.file = None

    def __enter__(self) -> "SocketClient":
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(os.fspath(self.path))
        self.file = self.sock.makefile("r", encoding="utf-8")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.file is not None:
            self.file.close()
        if self.sock is not None:
            self.sock.close()

    def send(self, message: JsonDict) -> None:
        assert self.sock is not None
        self.sock.sendall((json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8"))

    def recv(self) -> JsonDict:
        assert self.file is not None
        line = self.file.readline()
        if not line:
            raise RuntimeError("broker socket closed")
        return json.loads(line)


def require_socket() -> Path:
    path = socket_path()
    if not path.exists():
        raise SystemExit(f"broker socket not found at {path}; start Chromium with the GlassTTY extension and native host first")
    return path


def cmd_ping(_args: argparse.Namespace) -> int:
    print(json.dumps({"ok": True, "tool": "glassttyd", "mode": "local-cli"}))
    return 0


def cmd_tail(args: argparse.Namespace) -> int:
    events_path = default_home() / "state" / "events.jsonl"
    if not events_path.exists():
        print("no event log found", flush=True)
        return 1

    lines = events_path.read_text(encoding="utf-8").splitlines()
    tail = lines[-args.lines:]
    for line in tail:
        print(line)
    return 0


def cmd_socket_status(_args: argparse.Namespace) -> int:
    with SocketClient(require_socket()) as client:
        print(json.dumps(client.recv(), ensure_ascii=False))
        client.send({"op": "status"})
        print(json.dumps(client.recv(), ensure_ascii=False))
    return 0


def wait_for_request_id(client: SocketClient, request_id: str) -> JsonDict:
    while True:
        message = client.recv()
        if message.get("stream") == "browser_event" and message.get("message", {}).get("request_id") == request_id:
            return message
        print(json.dumps(message, ensure_ascii=False), file=sys.stderr)


def submit_browser_request(message_type: str, payload: JsonDict, *, wait: bool) -> int:
    request = make_envelope(message_type, payload)
    with SocketClient(require_socket()) as client:
        print(json.dumps(client.recv(), ensure_ascii=False), file=sys.stderr)
        client.send({"op": "submit_browser_request", "message": request})
        ack = client.recv()
        print(json.dumps(ack, ensure_ascii=False), file=sys.stderr)
        if wait:
            print(json.dumps(wait_for_request_id(client, request["request_id"]), ensure_ascii=False))
        else:
            print(json.dumps(request, ensure_ascii=False))
    return 0


def cmd_watch(_args: argparse.Namespace) -> int:
    with SocketClient(require_socket()) as client:
        print(json.dumps(client.recv(), ensure_ascii=False))
        client.send({"op": "watch"})
        while True:
            print(json.dumps(client.recv(), ensure_ascii=False))


def cmd_request(args: argparse.Namespace) -> int:
    payload = json.loads(args.payload) if args.payload else {}
    return submit_browser_request(args.type, payload, wait=args.wait)


def cmd_read_prompt(args: argparse.Namespace) -> int:
    return submit_browser_request("prompt.read", {}, wait=args.wait)


def cmd_read_latest(args: argparse.Namespace) -> int:
    return submit_browser_request("transcript.latest", {}, wait=args.wait)


def cmd_write_prompt(args: argparse.Namespace) -> int:
    return submit_browser_request("prompt.write", {"text": args.text}, wait=args.wait)


def cmd_debug_candidates(args: argparse.Namespace) -> int:
    return submit_browser_request("debug.dom_candidates", {}, wait=args.wait)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glassttyd")
    sub = parser.add_subparsers(dest="command", required=True)

    ping = sub.add_parser("ping", help="Local smoke test")
    ping.set_defaults(func=cmd_ping)

    tail = sub.add_parser("tail-events", help="Print recent native-host events")
    tail.add_argument("--lines", type=int, default=20)
    tail.set_defaults(func=cmd_tail)

    socket_status = sub.add_parser("socket-status", help="Check the local broker socket")
    socket_status.set_defaults(func=cmd_socket_status)

    watch = sub.add_parser("watch", help="Watch broker and browser events as JSON lines")
    watch.set_defaults(func=cmd_watch)

    request = sub.add_parser("request", help="Send an arbitrary browser request")
    request.add_argument("type")
    request.add_argument("--payload", default="{}")
    request.add_argument("--wait", action="store_true")
    request.set_defaults(func=cmd_request)

    read_prompt = sub.add_parser("read-prompt", help="Request prompt.read from the active supported tab")
    read_prompt.add_argument("--wait", action="store_true")
    read_prompt.set_defaults(func=cmd_read_prompt)

    read_latest = sub.add_parser("read-latest", help="Request transcript.latest from the active supported tab")
    read_latest.add_argument("--wait", action="store_true")
    read_latest.set_defaults(func=cmd_read_latest)

    write_prompt = sub.add_parser("write-prompt", help="Request prompt.write on the active supported tab")
    write_prompt.add_argument("text")
    write_prompt.add_argument("--wait", action="store_true")
    write_prompt.set_defaults(func=cmd_write_prompt)

    debug_candidates = sub.add_parser("debug-candidates", help="Request debug.dom_candidates from the active supported tab")
    debug_candidates.add_argument("--wait", action="store_true")
    debug_candidates.set_defaults(func=cmd_debug_candidates)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
