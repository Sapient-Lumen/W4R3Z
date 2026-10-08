#!/usr/bin/env python3
"""Parity monitor skeleton (v20)

This is intentionally a *skeleton* reference implementation.

Purpose:
- Fetch a pinned manifest / checkpoint from multiple perspectives
- Compare hashes and emit ParityProbeResult + ParityReport JSON objects

Integrations (optional):
- RIPE Atlas: create measurements and pull results via the Atlas REST API.
  Docs: https://atlas.ripe.net/docs/apis/ and status checks: https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/status-checks/
- OONI: query public interference signals via the OONI API.
  Docs: https://docs.ooni.org/data

Notes:
- Do NOT include voter data.
- Treat outputs as public artifacts: sign and anchor into the PBB.

Usage idea:
  python parity_monitor_skeleton.py --config config.json --out parity_report.json
"""

import argparse, json, hashlib, datetime
from urllib.request import urlopen, Request

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def fetch(url: str, user_agent: str | None = None, timeout: int = 10) -> tuple[int, dict, bytes]:
    req = Request(url)
    if user_agent:
        req.add_header("User-Agent", user_agent)
    with urlopen(req, timeout=timeout) as resp:
        status = getattr(resp, "status", 200)
        headers = dict(resp.headers.items())
        body = resp.read()
        return status, headers, body

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="JSON config with targets and expectations")
    ap.add_argument("--out", required=True, help="Output ParityReport JSON path")
    args = ap.parse_args()

    cfg = json.load(open(args.config, "r", encoding="utf-8"))
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    results = []
    for t in cfg.get("targets", []):
        url = t["url"]
        expected_hash = t.get("expected_manifest_hash")
        status, headers, body = fetch(url, user_agent=t.get("user_agent"))
        observed_hash = sha256_hex(body) if body else None
        st = "ok" if (expected_hash is None or observed_hash == expected_hash) else "mismatch"

        results.append({
            "schema_version": "1.0",
            "timestamp": now,
            "vantage": {"source": "internal", "id": cfg.get("monitor_id","local")},
            "target": {"url": url, "purpose": t.get("purpose")},
            "expected": {"manifest_hash": expected_hash},
            "observed": {"http_status": status, "response_hash": observed_hash, "notes": None},
            "status": st,
            "evidence_pointers": None
        })

    report = {
        "schema_version": "1.0",
        "report_id": cfg.get("report_id", f"parity-{now}"),
        "period_start": now,
        "period_end": now,
        "checkpoint_id": cfg.get("checkpoint_id", "UNKNOWN"),
        "targets": [t["url"] for t in cfg.get("targets",[])],
        "results": results,
        "summary": {
            "ok": sum(1 for r in results if r["status"]=="ok"),
            "mismatch": sum(1 for r in results if r["status"]=="mismatch"),
            "unreachable": 0,
            "error": 0
        },
        "signatures": []  # populate in production
    }

    json.dump(report, open(args.out, "w", encoding="utf-8"), indent=2)
    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
