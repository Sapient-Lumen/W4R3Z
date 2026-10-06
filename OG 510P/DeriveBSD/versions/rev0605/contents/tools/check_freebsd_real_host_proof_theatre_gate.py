#!/usr/bin/env python3
"""Prevent checked-in FreeBSD proof theatre.

A checked-in object may not claim ``proof_status=real-host-proof`` unless it is a
FreeBSD removable-media host proof bundle that passes the strict default bundle
validator against its original receipt.  The Linux cloudtainer may keep only the
explicit checker-simulation non-proof bundle as release-critical evidence.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
FREEBSD_TOOLS = TOOLS / "freebsd"
for path in [TOOLS, FREEBSD_TOOLS]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from cube_digest_lib import CanonicalJsonError, load_json_strict_text  # noqa: E402
import validate_removable_media_local_fallback_host_proof_bundle as bundle_validator  # noqa: E402

BUNDLE_KIND = "removable.media.local.freebsd.host.proof.bundle"
SCAN_DIRS = ["spec", "validation", "session-reviews"]
CURRENT_EXAMPLE = "spec/examples/removable.media.local.freebsd.host.proof.bundle.json"


def iter_json_paths() -> list[Path]:
    paths: list[Path] = []
    for rel in SCAN_DIRS:
        base = ROOT / rel
        if base.exists():
            paths.extend(path for path in base.rglob("*.json") if path.is_file())
    return sorted(set(paths))


def walk_objects(obj: Any, pointer: str = "$"):
    if isinstance(obj, dict):
        yield pointer, obj
        for key, value in obj.items():
            safe_key = str(key).replace("/", "~1")
            yield from walk_objects(value, f"{pointer}/{safe_key}")
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            yield from walk_objects(value, f"{pointer}/{idx}")


def main() -> int:
    errors: list[str] = []
    real_checked = 0
    nonproof_bundles = 0
    example_nonproof_seen = False

    for path in iter_json_paths():
        rel = path.relative_to(ROOT).as_posix()
        try:
            obj = load_json_strict_text(path.read_text(encoding="utf-8"))
        except (OSError, CanonicalJsonError) as exc:
            errors.append(f"{rel}: strict JSON load failed: {exc}")
            continue
        for pointer, node in walk_objects(obj):
            status = node.get("proof_status")
            if status == "real-host-proof":
                real_checked += 1
                if node.get("kind") != BUNDLE_KIND:
                    errors.append(f"{rel} {pointer}: real-host-proof is only allowed on {BUNDLE_KIND}")
                    continue
                bundle_errors = bundle_validator.validate_bundle(
                    node,
                    path,
                    allow_checker_simulation=False,
                    allow_current_tool_drift=False,
                )
                for err in bundle_errors[:10]:
                    errors.append(f"{rel} {pointer}: claimed real-host-proof failed strict validation: {err}")
                if len(bundle_errors) > 10:
                    errors.append(f"{rel} {pointer}: claimed real-host-proof had {len(bundle_errors) - 10} additional strict validation errors")
            elif status == "checker-simulation-non-proof" and node.get("kind") == BUNDLE_KIND:
                nonproof_bundles += 1
                if rel == CURRENT_EXAMPLE and pointer == "$":
                    example_nonproof_seen = True
                allowed_errors = bundle_validator.validate_bundle(
                    node,
                    path,
                    allow_checker_simulation=True,
                    allow_current_tool_drift=True,
                )
                for err in allowed_errors[:10]:
                    errors.append(f"{rel} {pointer}: checker-simulation non-proof bundle failed allowed validation: {err}")
                strict_errors = bundle_validator.validate_bundle(
                    node,
                    path,
                    allow_checker_simulation=False,
                    allow_current_tool_drift=True,
                )
                if not any("default mode accepts only real-host-proof bundles" in err for err in strict_errors):
                    errors.append(f"{rel} {pointer}: checker-simulation non-proof bundle must be rejected by default real-proof mode")

    if not example_nonproof_seen:
        errors.append(f"{CURRENT_EXAMPLE}: expected checked-in checker-simulation-non-proof bundle was not observed")

    if errors:
        print("FreeBSD real-host proof theatre gate FAILED.", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "FreeBSD real-host proof theatre gate OK "
        f"(strict real-host bundles checked: {real_checked}; "
        f"checker non-proof bundles validated: {nonproof_bundles})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
