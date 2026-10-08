#!/usr/bin/env python3
"""Fail if example packets contain unsafe relative paths.

Why:
- Packet fields like payload_pointer.uri, attachment.uri, and manifest artifacts[].url
  are treated as *relative paths* inside a packet directory.
- A malicious or malformed packet could attempt path traversal (e.g., "../secrets").

Scope:
- Only scans shipped example packets under artifacts/examples/.
- This is a drift firewall: if examples stay safe, docs + tools are less likely to
  regress.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from path_safety import is_safe_relpath  # type: ignore
EXAMPLES = ROOT / "artifacts" / "examples"

BAD = []

def check_envelope(p: Path) -> None:
    try:
        env = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        BAD.append(f"unparseable_envelope:{p.relative_to(ROOT)}")
        return

    ptr = env.get("payload_pointer")
    if isinstance(ptr, dict):
        uri = ptr.get("uri")
        if uri is not None and not is_safe_relpath(str(uri)):
            BAD.append(f"unsafe_payload_pointer_uri:{p.relative_to(ROOT)}:{uri}")

    atts = env.get("attachments")
    if isinstance(atts, list):
        for i, a in enumerate(atts):
            if not isinstance(a, dict):
                continue
            uri = a.get("uri")
            if uri is not None and not is_safe_relpath(str(uri)):
                BAD.append(f"unsafe_attachment_uri:{p.relative_to(ROOT)}:{i}:{uri}")


def check_manifest(p: Path) -> None:
    try:
        m = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        BAD.append(f"unparseable_manifest:{p.relative_to(ROOT)}")
        return

    for i, a in enumerate(m.get("artifacts", []) if isinstance(m, dict) else []):
        if not isinstance(a, dict):
            continue
        url = a.get("url")
        if isinstance(url, str) and url and not is_safe_relpath(url):
            BAD.append(f"unsafe_manifest_url:{p.relative_to(ROOT)}:{i}:{url}")


def main() -> int:
    if not EXAMPLES.exists():
        print("PASS: no artifacts/examples directory")
        return 0

    for env in EXAMPLES.rglob("envelopes/*.json"):
        check_envelope(env)

    for mf in EXAMPLES.rglob("manifest.json"):
        check_manifest(mf)

    if BAD:
        print("FAIL: unsafe paths found in example packets")
        for s in BAD[:30]:
            print("  ", s)
        if len(BAD) > 30:
            print(f"  ... ({len(BAD) - 30} more)")
        return 2

    print("PASS: example packet paths are safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
