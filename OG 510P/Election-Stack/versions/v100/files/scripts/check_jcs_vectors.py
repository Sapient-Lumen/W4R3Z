#!/usr/bin/env python3
"""Sanity-check our RFC8785-JCS implementation against tiny known-good vectors.

These vectors are deliberately small but high-leverage:
- The canonicalization sample used by the RFC8785 reference implementations.
- Boundary behaviors for JSON.stringify-style number formatting.

Why not a huge test corpus?
- We can't afford archive bloat; this is a drift tripwire, not a conformance suite.

References:
- RFC 8785 (JCS), Appendix B (number serialization samples)
- cyberphone/json-canonicalization "Sample Input" / "Expected Output" snippet
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from jcs import dumps as jcs_dumps  # noqa: E402


def f64_from_hexbits(hexbits: str) -> float:
    b = bytes.fromhex(hexbits)
    return struct.unpack(">d", b)[0]


def assert_eq(name: str, got: str, exp: str):
    if got != exp:
        print(f"FAIL {name}:")
        print("  expected:", exp)
        print("  got     :", got)
        raise SystemExit(2)


def main() -> int:
    # Vector 1: canonicalization sample.
    sample_json = r'''{
      "numbers": [333333333.33333329, 1E30, 4.50, 2e-3, 0.000000000000000000000000001],
      "string": "\u20ac$\u000F\u000aA'\u0042\u0022\u005c\\\"\/",
      "literals": [null, true, false]
    }'''
    obj = json.loads(sample_json)
    got = jcs_dumps(obj)
    expected = (
        "{\"literals\":[null,true,false],\"numbers\":[333333333.3333333,1e+30,4.5,0.002,1e-27],"
        "\"string\":\"€$\\u000f\\nA'B\\\"\\\\\\\\\\\"/\"}"
    )
    assert_eq("sample_object", got, expected)

    # Vector 2: number boundary samples (subset of RFC8785 Appendix B).
    cases = [
        ("0000000000000000", "0"),
        ("8000000000000000", "0"),  # minus zero
        ("0000000000000001", "5e-324"),
        ("44b52d02c7e14af6", "1e+23"),
        ("444b1ae4d6e2ef50", "1e+21"),
        ("3eb0c6f7a0b5ed8d", "0.000001"),
        ("44b52d02c7e14af5", "9.999999999999997e+22"),
        ("3eb0c6f7a0b5ed8c", "9.999999999999997e-7"),
    ]
    for hexbits, exp in cases:
        x = f64_from_hexbits(hexbits)
        got = jcs_dumps(x)
        assert_eq(f"num_{hexbits}", got, exp)

    # Vector 3: threshold behavior not in Appendix B table.
    assert_eq("num_1e20", jcs_dumps(1e20), "100000000000000000000")
    assert_eq("num_1e-7", jcs_dumps(1e-7), "1e-7")

    print("PASS: JCS vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
