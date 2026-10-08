#!/usr/bin/env python3
"""Probe cohort selection (skeleton).

This script is intentionally minimal. It does NOT call external APIs by default.
It expects a local JSON/CSV of probe metadata (probe_id, country, asn, region tags).

Output: ProbeCohortPlan JSON with selected_probe_ids populated.

Usage:
  python probe_cohort_selector.py --input probes.csv --method quota_round_robin --target-n 200 --out plan.json
"""

import argparse
import csv
import json
import hashlib
from datetime import datetime, timezone


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_probes_csv(path: str):
    probes = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            probes.append({
                "probe_id": int(row["probe_id"]),
                "country": row.get("country", ""),
                "asn": int(row.get("asn", 0) or 0),
                "region": row.get("region", "")
            })
    return probes


def quota_round_robin(probes, target_n: int, max_per_country: int = 5, max_per_asn: int = 2):
    # Simple, explainable baseline.
    by_country = {}
    for p in probes:
        by_country.setdefault(p["country"], []).append(p)

    countries = sorted([c for c in by_country.keys() if c])
    selected = []
    counts_country = {}
    counts_asn = {}

    i = 0
    while len(selected) < target_n and countries:
        c = countries[i % len(countries)]
        i += 1
        bucket = by_country.get(c, [])
        if not bucket:
            continue

        # pop one candidate
        cand = bucket.pop(0)
        if counts_country.get(c, 0) >= max_per_country:
            continue
        if counts_asn.get(cand["asn"], 0) >= max_per_asn:
            continue

        selected.append(cand)
        counts_country[c] = counts_country.get(c, 0) + 1
        counts_asn[cand["asn"]] = counts_asn.get(cand["asn"], 0) + 1

        # prune exhausted
        if not bucket:
            by_country.pop(c, None)
            countries = sorted(by_country.keys())
            i = 0

    return [p["probe_id"] for p in selected]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--method", default="quota_round_robin")
    ap.add_argument("--target-n", type=int, required=True)
    ap.add_argument("--election-id", default="ELECTION")
    ap.add_argument("--max-per-country", type=int, default=5)
    ap.add_argument("--max-per-asn", type=int, default=2)
    args = ap.parse_args()

    probes = load_probes_csv(args.input)

    if args.method != "quota_round_robin":
        raise SystemExit("Only quota_round_robin implemented in skeleton")

    selected = quota_round_robin(
        probes,
        target_n=args.target_n,
        max_per_country=args.max_per_country,
        max_per_asn=args.max_per_asn,
    )

    plan = {
        "plan_id": f"cohort-{sha256_hex((''+str(datetime.now())).encode())[:12]}",
        "election_id": args.election_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target_n": args.target_n,
        "constraints": {
            "max_per_country": args.max_per_country,
            "max_per_asn": args.max_per_asn,
        },
        "selection_method": "quota_round_robin",
        "input_dataset": {
            "source": "local_csv",
            "dataset_hash": sha256_hex(open(args.input, 'rb').read()),
            "as_of": datetime.now(timezone.utc).isoformat(),
        },
        "selected_probe_ids": selected,
    }

    # commitment = hash of canonical JSON (sorted keys)
    canon = json.dumps(plan, sort_keys=True, separators=(",", ":")).encode("utf-8")
    plan_hash = sha256_hex(canon)
    plan["commitment"] = {
        "plan_hash": plan_hash,
        "signature": "TODO:sign(plan_hash)",
        "signing_key_id": "TODO"
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
