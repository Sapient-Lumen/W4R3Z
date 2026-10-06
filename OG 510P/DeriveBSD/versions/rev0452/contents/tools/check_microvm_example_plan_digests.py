#!/usr/bin/env python3
"""Check that microVM example receipts bind the correct plan digest.

Why:
  - The microVM control plane is only spec-able if Plan→Receipt is a stable join key.
  - Example drift is a common amnesia source (docs say one thing; examples imply another).

Rule:
  - For microVM plan examples, compute: sha256( utf8( JCS(plan_json) ) )
  - Ensure corresponding receipt examples include that digest as `plan_digest`.
  - Keep example pairs internally consistent (plan_id + selected digests).

Notes:
  - This is a lightweight check intended for CI.
  - We implement a restricted RFC 8785-style canonicalizer sufficient for DeriveBSD examples:
      * sort object keys lexicographically
      * no whitespace
      * UTF-8 output
      * reject floats (I-JSON friendly)

Usage:
  python3 tools/check_microvm_example_plan_digests.py

Exit codes:
  0: ok
  1: at least one example is inconsistent
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "spec" / "examples"

HEX64 = re.compile(r"^sha256:[0-9a-f]{64}$")


def _read_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"{p}: failed to parse JSON: {e}")


def _reject_floats(x, path: str = "$") -> None:
    if isinstance(x, float):
        raise ValueError(f"{path}: floats are not allowed in JCS-hashable examples")
    if isinstance(x, dict):
        for k, v in x.items():
            if not isinstance(k, str):
                raise ValueError(f"{path}: non-string object key {k!r}")
            _reject_floats(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            _reject_floats(v, f"{path}[{i}]")


def _jcs_bytes(obj: dict) -> bytes:
    _reject_floats(obj)
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")


def _plan_digest(plan_obj: dict) -> str:
    h = hashlib.sha256(_jcs_bytes(plan_obj)).hexdigest()
    return f"sha256:{h}"


def _require_hex64(label: str, value: str, problems: list[str]) -> None:
    if not isinstance(value, str) or not HEX64.match(value):
        problems.append(f"{label}: expected sha256:<64hex>, got {value!r}")


def main() -> int:
    problems: list[str] = []

    launch_plan_p = EX / "microvm.launch.plan.json"
    launch_receipt_p = EX / "microvm.launch.receipt.json"
    stop_plan_p = EX / "microvm.stop.plan.json"
    stop_receipt_p = EX / "microvm.stop.receipt.json"

    launch_plan = _read_json(launch_plan_p)
    launch_receipt = _read_json(launch_receipt_p)
    stop_plan = _read_json(stop_plan_p)
    stop_receipt = _read_json(stop_receipt_p)

    if launch_plan.get("kind") != "microvm.launch.plan":
        problems.append(f"{launch_plan_p.name}: kind must be microvm.launch.plan")
    if launch_receipt.get("kind") != "microvm.launch.receipt":
        problems.append(f"{launch_receipt_p.name}: kind must be microvm.launch.receipt")
    if stop_plan.get("kind") != "microvm.stop.plan":
        problems.append(f"{stop_plan_p.name}: kind must be microvm.stop.plan")
    if stop_receipt.get("kind") != "microvm.stop.receipt":
        problems.append(f"{stop_receipt_p.name}: kind must be microvm.stop.receipt")

    launch_d = _plan_digest(launch_plan)
    stop_d = _plan_digest(stop_plan)

    # Launch pair
    if launch_receipt.get("plan_id") != launch_plan.get("plan_id"):
        problems.append(
            f"launch: receipt.plan_id {launch_receipt.get('plan_id')!r} != plan.plan_id {launch_plan.get('plan_id')!r}"
        )

    _require_hex64("launch: computed plan_digest", launch_d, problems)
    if launch_receipt.get("plan_digest") != launch_d:
        problems.append(
            f"launch: receipt.plan_digest {launch_receipt.get('plan_digest')!r} != computed {launch_d}"
        )

    for k in ("policy_digest", "runtime_manifest_digest", "artifact_digest"):
        if k in launch_plan and k in launch_receipt and launch_plan[k] != launch_receipt[k]:
            problems.append(f"launch: receipt.{k} != plan.{k}")

    # Stop pair
    if stop_receipt.get("plan_id") != stop_plan.get("plan_id"):
        problems.append(
            f"stop: receipt.plan_id {stop_receipt.get('plan_id')!r} != plan.plan_id {stop_plan.get('plan_id')!r}"
        )

    _require_hex64("stop: computed plan_digest", stop_d, problems)
    if stop_receipt.get("plan_digest") != stop_d:
        problems.append(f"stop: receipt.plan_digest {stop_receipt.get('plan_digest')!r} != computed {stop_d}")

    if "policy_digest" in stop_plan and "policy_digest" in stop_receipt and stop_plan["policy_digest"] != stop_receipt["policy_digest"]:
        problems.append("stop: receipt.policy_digest != plan.policy_digest")

    # Example consistency: stop refers to launch plan digest.
    exp = stop_plan.get("expect_running_plan_digest")
    if exp is not None:
        _require_hex64("stop: expect_running_plan_digest", exp, problems)
        if exp != launch_d:
            problems.append(f"stop: expect_running_plan_digest {exp!r} != launch plan digest {launch_d}")

    obs = (stop_receipt.get("observed") or {}).get("running_plan_digest")
    if obs is not None:
        _require_hex64("stop: observed.running_plan_digest", obs, problems)
        if obs != launch_d:
            problems.append(f"stop: observed.running_plan_digest {obs!r} != launch plan digest {launch_d}")

    if problems:
        print("microVM plan/receipt digest check FAILED")
        for p in problems:
            print("-", p)
        print("\nFix: update the example plan/receipt files so receipts bind the computed sha256(JCS(plan)).")
        return 1

    print("microVM plan/receipt digest check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
