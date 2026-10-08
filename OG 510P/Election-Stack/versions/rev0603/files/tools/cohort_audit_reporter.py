#!/usr/bin/env python3
"""
cohort_audit_reporter.py — reference skeleton

Purpose:
  Produce a CohortAuditReport for a given ProbeCohortPlan and (optional) ProbeReputationRecords.

Inputs:
  --cohort-plan <path>     JSON with fields at least: { "plan_id": ..., "probes": [ { "probe_id": ..., "asn": ..., "country": ... } ] }
  --reputations <path>     JSON array of ProbeReputationRecord objects (optional)
  --window-start/stop      ISO-8601
  --created-by             string

Outputs:
  CohortAuditReport JSON.
"""
import argparse, json, hashlib, datetime, pathlib, math, sys
from collections import Counter

def sha256_bytes(b: bytes) -> str:
    import hashlib
    return hashlib.sha256(b).hexdigest()

def file_sha256(path: pathlib.Path) -> str:
    return sha256_bytes(path.read_bytes())

def entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total <= 0:
        return 0.0
    ent = 0.0
    for c in counter.values():
        p = c / total
        ent -= p * math.log(p, 2)
    return ent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort-plan", required=True)
    ap.add_argument("--reputations", default=None)
    ap.add_argument("--window-start", required=True)
    ap.add_argument("--window-stop", required=True)
    ap.add_argument("--created-by", required=True)
    ap.add_argument("--out", default="-")
    args = ap.parse_args()

    plan_path = pathlib.Path(args.cohort_plan)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    reputations = {}
    rep_path = None
    if args.reputations:
        rep_path = pathlib.Path(args.reputations)
        rep_list = json.loads(rep_path.read_text(encoding="utf-8"))
        for r in rep_list:
            reputations[str(r.get("probe_id"))] = r

    probes = plan.get("probes", [])
    by_country = Counter()
    by_asn = Counter()
    by_nt = Counter()
    excluded = []

    for p in probes:
        pid = str(p.get("probe_id"))
        asn = p.get("asn")
        country = p.get("country")
        nt = p.get("network_type")
        if country:
            by_country[str(country)] += 1
        if asn is not None:
            by_asn[str(asn)] += 1
        if nt:
            by_nt[str(nt)] += 1

        rep = reputations.get(pid)
        if rep and rep.get("confidence") == "low":
            excluded.append({"probe_id": pid, "reason": "low_confidence", "details": "Excluded by policy (low confidence reputation)."})
        # Note: this skeleton does not remove excluded probes from distributions; a real implementation should.

    total = max(1, sum(by_asn.values()))
    max_as_share = max(by_asn.values()) / total if by_asn else 0.0

    inputs_blob = plan_path.read_bytes() + (rep_path.read_bytes() if rep_path else b"")
    inputs_hash = sha256_bytes(inputs_blob)
    code_hash = file_sha256(pathlib.Path(__file__))
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    report = {
        "schema_version": "1.0",
        "audit_id": plan.get("plan_id", "unknown") + ":" + now,
        "cohort_plan_hash": sha256_bytes(plan_path.read_bytes()),
        "window": {"start": args.window_start, "stop": args.window_stop},
        "distributions": {
            "by_country": dict(by_country),
            "by_asn": dict(by_asn),
            "by_network_type": dict(by_nt)
        },
        "metrics": {
            "max_asn_share": max_as_share,
            "num_unique_asn": len(by_asn),
            "num_unique_country": len(by_country),
            "entropy_asn": entropy(by_asn) if by_asn else None,
            "entropy_country": entropy(by_country) if by_country else None
        },
        "excluded_probes": excluded,
        "references": [],
        "created_at": now,
        "created_by": args.created_by,
        "hashes": {"inputs_hash": inputs_hash, "code_hash": code_hash},
        "signature": {"alg": "none", "value": ""}
    }

    out_json = json.dumps(report, indent=2, sort_keys=True)
    if args.out == "-":
        sys.stdout.write(out_json + "\n")
    else:
        pathlib.Path(args.out).write_text(out_json, encoding="utf-8")

if __name__ == "__main__":
    main()
