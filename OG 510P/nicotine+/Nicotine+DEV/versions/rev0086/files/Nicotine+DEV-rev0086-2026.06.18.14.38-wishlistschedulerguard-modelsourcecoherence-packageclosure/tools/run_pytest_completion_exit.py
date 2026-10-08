#!/usr/bin/env python3
"""Run pytest, attest that ``pytest.main()`` returned, then exit immediately.

Nicotine+ unit tests can leave non-daemon runtime threads alive after pytest has
completed. Normal interpreter shutdown then waits indefinitely even though
pytest has returned, emitted its terminal summary, and finalized JUnit output.

This wrapper does *not* infer completion from progress text or a parseable XML
file. It writes an atomic marker only after ``pytest.main()`` itself returns,
flushes the terminal streams, and uses ``os._exit`` to bypass leaked-thread
shutdown. The parent lane runner verifies the marker and JUnit report.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

MARKER_ENV = "CUBE_PYTEST_COMPLETION_MARKER"
MARKER_VERSION = 1


def _write_marker(path: Path, exit_code: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": MARKER_VERSION,
        "pytest_main_returned": True,
        "exit_code": exit_code,
    }
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> None:
    exit_code = int(pytest.main(sys.argv[1:]))
    marker_value = os.environ.get(MARKER_ENV)
    if marker_value:
        _write_marker(Path(marker_value).resolve(), exit_code)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)


if __name__ == "__main__":
    main()
