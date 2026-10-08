#!/usr/bin/env python3
"""tools/jcs.py

RFC 8785 JSON Canonicalization Scheme (JCS) implementation (stdlib-only).

Goal:
- Deterministic canonical bytes for hashing/signing (docs/176).
- Interop: numbers follow ECMAScript/JSON.stringify-style formatting where possible.

Notes:
- Disallows NaN/Infinity.
- Normalizes -0 to 0.
- Uses shortest-roundtrip representation for non-integer floats, and normalizes
  exponent formatting to match JSON.stringify (e.g., 1e-06 -> 1e-6).

This is intentionally small and auditable; it is not a general-purpose JSON library.
"""

from __future__ import annotations

import json
import math
import re
from typing import Any

_EXP_RE = re.compile(r"e([+-]?)(\d+)$")


def _json_string(s: str) -> str:
    # Delegate escaping rules to stdlib.
    return json.dumps(s, ensure_ascii=False, separators=(",", ":"))


def _float_to_jcs(x: float) -> str:
    if not math.isfinite(x):
        raise ValueError("JCS forbids NaN/Infinity")

    # Normalize -0.0 to 0.
    if x == 0.0:
        return "0"

    # RFC8785 number serialization follows ECMAScript's JSON.stringify(), which
    # uses either decimal or exponential form based on the base-10 exponent.
    #
    # We start from Python's shortest-roundtrip repr(float) and then:
    #   (a) normalize exponent formatting (no leading zeros; always include + for pos exp)
    #   (b) expand or keep scientific notation to match JSON.stringify thresholds:
    #         -6 <= exponent < 21  => decimal form
    #          otherwise          => scientific form
    # See RFC8785 Appendix B for boundary samples.

    s = repr(x).lower()

    # If repr produced a plain decimal with a trailing .0, strip it (JSON.stringify
    # would emit an integer).
    if "e" not in s and s.endswith(".0"):
        s = s[:-2]
        return "0" if s == "-0" else s

    if "e" not in s:
        return s

    # Parse scientific notation.
    m = _EXP_RE.search(s)
    if not m:
        return s
    exp_sign, exp_digits = m.group(1) or "+", m.group(2)
    exp = int(exp_digits)
    if exp_sign == "-":
        exp = -exp

    coeff = s.split("e", 1)[0]
    neg = coeff.startswith("-")
    if neg:
        coeff = coeff[1:]

    # Decide between decimal vs scientific form.
    if -6 <= exp < 21:
        # Convert coeff * 10**exp to decimal form.
        if "." in coeff:
            intpart, frac = coeff.split(".", 1)
            digits = intpart + frac
            dec_places = len(frac)
        else:
            digits = coeff
            dec_places = 0

        if digits.startswith("+"):
            digits = digits[1:]

        shift = exp - dec_places
        if shift >= 0:
            out = digits + ("0" * shift)
        else:
            cut = len(digits) + shift
            if cut > 0:
                out = digits[:cut] + "." + digits[cut:]
            else:
                out = "0." + ("0" * (-cut)) + digits
            out = out.rstrip("0").rstrip(".")

        if out.startswith("."):
            out = "0" + out
        if neg:
            out = "-" + out
        return "0" if out == "-0" else out

    # Scientific form: normalize exponent sign and strip leading zeros.
    exp_abs = str(abs(exp))
    exp_sign = "+" if exp >= 0 else "-"
    coeff_out = ("-" if neg else "") + coeff
    return f"{coeff_out}e{exp_sign}{exp_abs}"


def _num_to_jcs(n: Any) -> str:
    if isinstance(n, bool) or n is None:
        raise TypeError("not a number")
    if isinstance(n, int):
        return str(n)
    if isinstance(n, float):
        return _float_to_jcs(n)
    raise TypeError(f"unsupported number type: {type(n)}")


def dumps(obj: Any) -> str:
    """Return RFC8785-JCS canonical JSON text (UTF-8 safe)."""

    def ser(o: Any) -> str:
        if o is None:
            return "null"
        if o is True:
            return "true"
        if o is False:
            return "false"
        if isinstance(o, str):
            return _json_string(o)
        if isinstance(o, (int, float)) and not isinstance(o, bool):
            return _num_to_jcs(o)
        if isinstance(o, list):
            return "[" + ",".join(ser(v) for v in o) + "]"
        if isinstance(o, dict):
            # Object keys are strings; sort by codepoints.
            items = []
            for k in sorted(o.keys(), key=lambda x: str(x)):
                if not isinstance(k, str):
                    # Spec assumes JSON keys are strings.
                    k = str(k)
                items.append(_json_string(k) + ":" + ser(o[k]))
            return "{" + ",".join(items) + "}"
        raise TypeError(f"unsupported JSON type: {type(o)}")

    return ser(obj)


def dump_bytes(obj: Any) -> bytes:
    return dumps(obj).encode("utf-8")
