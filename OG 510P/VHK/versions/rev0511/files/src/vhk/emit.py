from __future__ import annotations

"""Fast bus event emitter.

Why this exists
--------------
The main `vhk` CLI imports Rich/Typer and (transitively) heavier parts of the
stack. For hotkey daemons and compositor keybinds, it can be helpful to have a
tiny emitter that:

- avoids loading the full VHK CLI
- emits a single UNIX datagram to a known bus socket

This module is intentionally stdlib-only + `vhk.system.event_bus`.
"""

import argparse
import json
import sys
from pathlib import Path

from vhk.system.event_bus import emit_bus_event, get_bus_socket_path


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="vhk-emit", add_help=True)
    p.add_argument("--socket", help="Bus socket path (preferred: avoids reading project.yaml)")
    p.add_argument("--project", help="Project directory to derive socket path from (uses default rules)")
    p.add_argument("event", help="Event name to emit")
    p.add_argument("--data", help="Optional JSON payload")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(argv)

    sock: Path | None = Path(ns.socket).expanduser() if ns.socket else None
    if sock is None:
        if not ns.project:
            sys.stderr.write("error: provide --socket or --project\n")
            return 2
        sock = get_bus_socket_path(Path(ns.project).expanduser().resolve(), configured=None)

    data = None
    if ns.data is not None:
        try:
            data = json.loads(ns.data)
        except Exception as exc:
            sys.stderr.write(f"error: --data must be valid JSON: {exc}\n")
            return 2

    try:
        emit_bus_event(sock, str(ns.event), data)
    except Exception as exc:
        sys.stderr.write(f"error: failed to emit event: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
