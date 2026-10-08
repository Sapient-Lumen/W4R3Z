#!/usr/bin/env python3
"""Validate the rev0832 regenerated OCF resolver trace."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from regenerate_ocf_trace_rev0832 import (  # noqa: E402
    ABOM_REL,
    AUDIT_JSON,
    AUDIT_MD,
    COMMAND,
    LEGACY_TIMESTAMP,
    TRACE_REL,
    build_audit,
    render_markdown,
)


def fail(msg: str) -> None:
    print(f"ocf-trace-regeneration-rev0832-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    expected = build_audit(ROOT)
    if expected["status"] != "trace_regenerated_and_replayable":
        fail(f"unexpected trace regeneration status: {expected['status']}")
    cur = expected["current"]
    if cur["timestamp"] != LEGACY_TIMESTAMP:
        fail("regenerated trace did not preserve legacy timestamp")
    if cur["abom_digest_in_trace"] != cur["abom_digest_recomputed"]:
        fail("trace abomDigest does not match the current ABOM")
    if cur["bad_pattern_total"] != 0:
        fail("regenerated trace still contains malformed locator/status/path bad patterns")
    if not AUDIT_JSON.is_file() or not AUDIT_MD.is_file():
        fail("missing OCF trace regeneration audit outputs")
    actual = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    if actual != expected:
        fail("OCF trace regeneration JSON audit is stale")
    if AUDIT_MD.read_text(encoding="utf-8") != render_markdown(expected):
        fail("OCF trace regeneration Markdown audit is stale")

    with tempfile.TemporaryDirectory(prefix="ev-ocf-trace-") as td:
        out = Path(td) / "trace.yaml"
        cmd = ["python3", "sources/ocf_llm/tools/ocf_resolver.py", "--out", str(out), ABOM_REL]
        env = os.environ.copy()
        env["OCF_TRACE_DATE"] = LEGACY_TIMESTAMP
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        cp = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=60)
        if cp.returncode != 0:
            fail(f"portable trace replay command failed with rc={cp.returncode}: {cp.stderr[:300]}")
        if cp.stderr.strip():
            fail(f"portable trace replay emitted stderr: {cp.stderr[:300]}")
        if out.read_bytes() != (ROOT / TRACE_REL).read_bytes():
            fail("portable trace replay output does not byte-match the checked-in regenerated trace")
    print("ocf-trace-regeneration-rev0832-validate: OK (byte-replay matched regenerated trace)")


if __name__ == "__main__":
    main()
