#!/usr/bin/env python3
"""ooni_corroborator.py — research/prototype utility, supplementary only.

Builds a schema-valid OONICorroboration object.  By default it performs no
network I/O and emits only the intended bounded query/pointer shape.  Operators
must pass --query-api to query OONI's public API; even then, the tool records
aggregate/count metadata and pointers, not raw measurement bodies.

Docs:
- 119-ooni-corroboration.md
- 118-measurement-ethics-guardrails.md
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

OONI_MEASUREMENTS_ENDPOINT = "https://api.ooni.io/api/v1/measurements"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso_utc(raw: str, label: str) -> str:
    if not raw:
        raise ValueError(f"--{label} is required")
    value = raw.replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError(f"--{label} must include timezone, preferably Z")
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_window(start: str, stop: str) -> dict[str, str]:
    s = parse_iso_utc(start, "from")
    e = parse_iso_utc(stop, "to")
    if datetime.fromisoformat(e.replace("Z", "+00:00")) <= datetime.fromisoformat(s.replace("Z", "+00:00")):
        raise ValueError("--to must be after --from")
    return {"start": s, "stop": e}


def build_params(args: argparse.Namespace, window: dict[str, str]) -> dict[str, str]:
    params: dict[str, str] = {
        "since": window["start"],
        "until": window["stop"],
        "test_name": args.test_name,
        "limit": str(args.limit),
    }
    if args.country:
        params["probe_cc"] = args.country.upper()
    if args.asn:
        asn = str(args.asn).upper().removeprefix("AS")
        if not asn.isdigit():
            raise ValueError("--asn must be numeric or AS-prefixed numeric")
        params["probe_asn"] = asn
    return params


def query_ooni(params: dict[str, str]) -> Any:
    if requests is None:
        raise RuntimeError("--query-api requires the requests package")
    r = requests.get(OONI_MEASUREMENTS_ENDPOINT, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def summarize_response(obj: Any) -> dict[str, Any]:
    # Avoid copying raw measurements into the corroboration object.  Different
    # OONI API versions have used list/dict wrappers, so preserve only bounded
    # counts and top-level shape metadata.
    if isinstance(obj, list):
        return {"status": "api_queried_summary_only", "measurement_count_returned": len(obj), "response_shape": "list"}
    if isinstance(obj, dict):
        results = obj.get("results")
        count = len(results) if isinstance(results, list) else None
        summary = {
            "status": "api_queried_summary_only",
            "response_shape": "object",
            "top_level_keys": sorted(str(k) for k in obj.keys())[:20],
        }
        if count is not None:
            summary["measurement_count_returned"] = count
        if isinstance(obj.get("metadata"), dict):
            summary["metadata_keys"] = sorted(str(k) for k in obj["metadata"].keys())[:20]
        return summary
    return {"status": "api_queried_summary_only", "response_shape": type(obj).__name__}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output JSON path")
    ap.add_argument("--country", default=None, help="ISO country code filter")
    ap.add_argument("--asn", default=None, help="ASN filter, numeric or AS-prefixed")
    ap.add_argument("--test-name", default="web_connectivity")
    ap.add_argument("--from", dest="time_from", required=True, help="ISO time lower bound")
    ap.add_argument("--to", dest="time_to", required=True, help="ISO time upper bound")
    ap.add_argument("--limit", type=int, default=100, help="bounded API result limit")
    ap.add_argument("--query-api", action="store_true", help="query OONI public API; default is dry-run/no-network")
    args = ap.parse_args()

    if args.limit < 1 or args.limit > 1000:
        print("--limit must be 1..1000", file=sys.stderr)
        return 2
    try:
        window = normalize_window(args.time_from, args.time_to)
        params = build_params(args, window)
    except Exception as exc:
        print(f"Invalid OONI corroboration request: {exc}", file=sys.stderr)
        return 2

    pointer = OONI_MEASUREMENTS_ENDPOINT + "?" + urlencode(params)
    summary: dict[str, Any] = {
        "status": "dry_run_no_api_query",
        "generated_at": utc_now_iso(),
        "supplementary_only": True,
        "raw_measurements_embedded": False,
    }
    if args.query_api:
        try:
            summary = summarize_response(query_ooni(params))
            summary["generated_at"] = utc_now_iso()
            summary["supplementary_only"] = True
            summary["raw_measurements_embedded"] = False
        except Exception as exc:
            print(f"OONI API query failed: {exc}", file=sys.stderr)
            return 3

    out = {
        "window": window,
        "filters": {
            "country_code": args.country.upper() if args.country else None,
            "asn": int(str(args.asn).upper().removeprefix("AS")) if args.asn else None,
            "test_name": args.test_name,
        },
        "summary": summary,
        "pointers": [pointer],
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
