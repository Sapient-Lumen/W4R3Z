#!/usr/bin/env python3
"""atlas_urp_generator.py — skeleton

Creates RIPE Atlas measurements (optional), fetches results for a time window, and emits:
- AtlasMeasurementReceipt.json
- UnreachabilityProof.json (referencing measurement IDs + reduction outputs)

NOTE: This is intentionally a *skeleton* (no network in this environment). It shows how to wire
the APIs safely and deterministically.

Docs:
- 117-automated-unreachability-proofs-ripe-atlas.md
- 118-measurement-ethics-guardrails.md
"""
from __future__ import annotations
import argparse, json, os, sys, time, hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

ATLAS_CREATE_URL = "https://atlas.ripe.net/api/v2/measurements/"
ATLAS_RESULTS_URL_TMPL = "https://atlas.ripe.net/api/v2/measurements/{mid}/results/"

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)

def create_measurement(api_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if requests is None:
        raise RuntimeError("requests not available")
    headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
    r = requests.post(ATLAS_CREATE_URL, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_results(mid: int, start_unix: int, stop_unix: int) -> Any:
    if requests is None:
        raise RuntimeError("requests not available")
    url = ATLAS_RESULTS_URL_TMPL.format(mid=mid)
    params = {"start": start_unix, "stop": stop_unix}
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, help="Path to AtlasMeasurementPlan JSON")
    ap.add_argument("--ethics", required=True, help="Path to EthicsGuardrailsPolicy JSON")
    ap.add_argument("--outdir", required=True, help="Output directory")
    ap.add_argument("--api-key-env", default="RIPE_ATLAS_API_KEY", help="Env var holding RIPE Atlas API key")
    ap.add_argument("--create", action="store_true", help="Actually create measurements via API")
    ap.add_argument("--start", type=int, required=True, help="Start UNIX timestamp for results window")
    ap.add_argument("--stop", type=int, required=True, help="Stop UNIX timestamp for results window")
    args = ap.parse_args()

    plan = load_json(args.plan)
    ethics = load_json(args.ethics)

    os.makedirs(args.outdir, exist_ok=True)

    # TODO: enforce ethics policy locally (rate caps, allowed targets, etc.)
    # This skeleton assumes operator enforcement.

    receipt = {
        "plan_id": plan.get("plan_id"),
        "created_measurement_ids": [],
        "api_endpoint": ATLAS_CREATE_URL,
        "created_at": utc_now_iso(),
        "raw_request_hash": None,
        "notes": "skeleton",
    }

    # Build RIPE Atlas create payload from plan (left as TODO — depends on measurement type mapping)
    create_payload = {
        "definitions": [],
        "probes": []
    }
    raw = json.dumps(create_payload, sort_keys=True).encode("utf-8")
    receipt["raw_request_hash"] = sha256_bytes(raw)

    if args.create:
        api_key = os.environ.get(args.api_key_env)
        if not api_key:
            print(f"Missing API key in env var {args.api_key_env}", file=sys.stderr)
            return 2
        resp = create_measurement(api_key, create_payload)
        # RIPE Atlas returns measurement IDs in response; exact field depends on request.
        mids = []
        if isinstance(resp, dict):
            if "measurements" in resp and isinstance(resp["measurements"], list):
                mids = [m.get("id") for m in resp["measurements"] if isinstance(m, dict) and "id" in m]
            elif "id" in resp:
                mids = [resp["id"]]
        receipt["created_measurement_ids"] = [int(x) for x in mids if x is not None]

    save_json(os.path.join(args.outdir, "AtlasMeasurementReceipt.json"), receipt)

    # Fetch + reduce results (if measurement IDs exist)
    # TODO: deterministic reduction + URP assembly (see doc 117)
    if receipt["created_measurement_ids"]:
        all_results = {}
        for mid in receipt["created_measurement_ids"]:
            all_results[str(mid)] = fetch_results(int(mid), args.start, args.stop)
        raw_results_path = os.path.join(args.outdir, "atlas_raw_results.json")
        save_json(raw_results_path, all_results)

    print("Done.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
