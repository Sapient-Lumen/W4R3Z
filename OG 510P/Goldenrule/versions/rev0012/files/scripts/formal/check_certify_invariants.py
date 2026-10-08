#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grlab.certify import CertifyError, certify_memory_one_pair


def _memory_one(strategy_id: str, p_cc: float, p_cd: float, p_dc: float, p_dd: float) -> dict[str, object]:
    return {
        "family": "memory_one",
        "id": strategy_id,
        "p0": p_cc,
        "p_cc": p_cc,
        "p_cd": p_cd,
        "p_dc": p_dc,
        "p_dd": p_dd,
    }


def _approx(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def main() -> int:
    root = ROOT
    out = root / "artifacts" / "formal" / "certify_invariants.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    pairs = [
        {
            "id": "allc_vs_allc",
            "a": _memory_one("allc", 1.0, 1.0, 1.0, 1.0),
            "b": _memory_one("allc", 1.0, 1.0, 1.0, 1.0),
            "expected": {"avg_payoff_a": 3.0, "avg_payoff_b": 3.0, "state_idx": 0},
        },
        {
            "id": "alld_vs_alld",
            "a": _memory_one("alld", 0.0, 0.0, 0.0, 0.0),
            "b": _memory_one("alld", 0.0, 0.0, 0.0, 0.0),
            "expected": {"avg_payoff_a": 1.0, "avg_payoff_b": 1.0, "state_idx": 3},
        },
        {
            "id": "allc_vs_alld",
            "a": _memory_one("allc", 1.0, 1.0, 1.0, 1.0),
            "b": _memory_one("alld", 0.0, 0.0, 0.0, 0.0),
            "expected": {"avg_payoff_a": 0.0, "avg_payoff_b": 5.0, "state_idx": 1},
        },
        {
            "id": "tft_vs_tft",
            "a": _memory_one("tft", 1.0, 0.0, 1.0, 0.0),
            "b": _memory_one("tft", 1.0, 0.0, 1.0, 0.0),
            "expected_error": "singular",
        },
    ]

    checks: list[dict[str, object]] = []
    failed = False

    for pair in pairs:
        row: dict[str, object] = {"id": pair["id"], "ok": True}
        try:
            result = certify_memory_one_pair(pair["a"], pair["b"])
        except CertifyError as exc:
            expected_error = str(pair.get("expected_error", "")).strip().lower()
            got_error = str(exc)
            if expected_error and expected_error in got_error.lower():
                row["expected_error"] = expected_error
                row["error"] = got_error
                row["ok"] = True
            else:
                row["ok"] = False
                row["error"] = got_error
                failed = True
            checks.append(row)
            continue

        dist = result["steady_state_distribution"]
        total = sum(float(x) for x in dist)
        in_range = all(0.0 <= float(x) <= 1.0 for x in dist)
        payoff_range = 0.0 <= float(result["avg_payoff_a"]) <= 5.0 and 0.0 <= float(result["avg_payoff_b"]) <= 5.0
        symmetry = _approx(float(result["avg_payoff_a"]) - float(result["avg_payoff_b"]), 0.0) if pair["a"]["id"] == pair["b"]["id"] else True

        expected_match = True
        expected = pair.get("expected")
        if isinstance(expected, dict):
            expected_match = (
                _approx(float(result["avg_payoff_a"]), float(expected["avg_payoff_a"]))
                and _approx(float(result["avg_payoff_b"]), float(expected["avg_payoff_b"]))
                and _approx(float(dist[int(expected["state_idx"])]), 1.0)
            )

        row.update(
            {
                "sum_to_one": _approx(total, 1.0),
                "dist_in_range": in_range,
                "payoff_in_range": payoff_range,
                "symmetry_if_identical": symmetry,
                "expected_match": expected_match,
                "result": result,
            }
        )

        row_ok = bool(row["sum_to_one"] and row["dist_in_range"] and row["payoff_in_range"] and row["symmetry_if_identical"] and row["expected_match"])
        row["ok"] = row_ok
        if not row_ok:
            failed = True
        checks.append(row)

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "check": "certify_invariants",
        "cases": checks,
        "ok": not failed,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"formal: wrote {out}")

    if failed:
        print("formal: certify invariants failed", file=sys.stderr)
        return 1
    print(f"formal: certify invariants ok ({len(checks)} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
