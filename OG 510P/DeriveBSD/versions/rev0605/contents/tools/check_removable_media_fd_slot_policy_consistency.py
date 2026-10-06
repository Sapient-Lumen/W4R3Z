#!/usr/bin/env python3
"""Keep removable-media fixed-fd launcher policy evidence in sync.

The fd-slot launcher is small but authority-sensitive: it decides how broker
fds 3/4/5 are saved, cleared, delegated to the child, and restored in the
parent.  rev0518 guards against a real drift class where implementation and
examples used different policy strings, letting generated evidence and schemas
speak past the code.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import removable_media_fd_slot_launcher as fd_slots  # noqa: E402

POLICY = fd_slots.POLICY
OLD_POLICY = "save-and-clear-target-fds-before-opening-delegated-files"
EXPECTED_POLICY = "duplicate-target-fds-above-delegated-range-before-clearing-slots"
VERSION = "2026-06-05r554"

JSON_PATHS = [
    "spec/removable.media.capsicum.worker.bridge.schema.json",
    "spec/removable.media.local.freebsd.backend.run.receipt.schema.json",
    "spec/examples/removable.media.capsicum.worker.bridge.json",
    "spec/examples/removable.media.local.freebsd.backend.run.receipt.json",
    "validation/removable-media-capsicum-worker-bridge.receipt.json",
    "validation/removable-media-local-freebsd-backend-run.receipt.json",
]

DOC_PATHS = [
    "README.md",
    "docs/00-index.md",
    "docs/99-llm-runbook.md",
    "docs/current/removable-media-capsicum-worker-bridge.md",
    "docs/current/removable-media-freebsd-host-smoke.md",
]


def load_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def find_values(node: Any, key: str) -> list[Any]:
    values: list[Any] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key:
                values.append(v)
            values.extend(find_values(v, key))
    elif isinstance(node, list):
        for item in node:
            values.extend(find_values(item, key))
    return values


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    require(errors, POLICY == EXPECTED_POLICY, f"fd_slots.POLICY drifted: {POLICY!r}")

    for rel in JSON_PATHS:
        path = ROOT / rel
        require(errors, path.exists(), f"missing {rel}")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        require(errors, OLD_POLICY not in text, f"{rel} still contains obsolete fd-slot policy {OLD_POLICY!r}")
        require(errors, POLICY in text, f"{rel} missing current fd-slot policy {POLICY!r}")
        obj = json.loads(text)
        for key in ("launcher_fd_slot_policy", "policy"):
            for value in find_values(obj, key):
                if isinstance(value, str) and ("fd" in key or "delegated" in value or "target" in value):
                    require(errors, value == POLICY, f"{rel} has {key}={value!r}, expected {POLICY!r}")
        for value in find_values(obj, "generated_for_version"):
            if isinstance(value, str) and rel.startswith("spec/examples/"):
                require(errors, value == VERSION, f"{rel} generated_for_version={value!r}, expected {VERSION!r}")

    bridge = load_json("spec/examples/removable.media.capsicum.worker.bridge.json")
    backend = load_json("spec/examples/removable.media.local.freebsd.backend.run.receipt.json")
    require(errors, bridge.get("backend_integration", {}).get("launcher_fd_slot_policy") == POLICY, "bridge backend_integration must bind fd_slots.POLICY")
    require(errors, backend.get("worker_bridge", {}).get("launcher_fd_slot_policy") == POLICY, "backend receipt worker_bridge must bind fd_slots.POLICY")

    for rel in DOC_PATHS:
        path = ROOT / rel
        require(errors, path.exists(), f"missing {rel}")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        require(errors, OLD_POLICY not in text, f"{rel} still documents obsolete fd-slot policy")
        require(errors, POLICY in text, f"{rel} missing current fd-slot policy")

    if errors:
        print("removable-media fd-slot policy consistency check FAILED.")
        for err in errors:
            print("-", err)
        return 1
    print("removable-media fd-slot policy consistency check OK")
    print(f"Policy: {POLICY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
