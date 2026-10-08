#!/usr/bin/env python3
"""path_correlation_analyzer.py

Reference (non-production) tool to compute a PathCorrelationReport from traceroute-like inputs.

Inputs:
  - JSONL where each line is an object:
      { "probe_id": "...", "as_path": [64512, 3356, ...], "raw_hash": "..." }

Outputs:
  - PathCorrelationReport JSON (no signing; caller signs/canonicalizes)

This is intentionally small and auditable. Replace clustering/metrics with your preferred methods.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Tuple


def shannon_entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    ent = 0.0
    for c in counts.values():
        p = c / total
        ent -= p * math.log2(p)
    return ent


def jaccard(a: List[int], b: List[int]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / max(1, len(sa | sb))


def mean_pairwise_jaccard(paths: List[List[int]]) -> float:
    if len(paths) < 2:
        return 0.0
    s = 0.0
    n = 0
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            s += jaccard(paths[i], paths[j])
            n += 1
    return s / n


def simple_cluster(paths_by_probe: Dict[str, List[int]], threshold: float = 0.8):
    """Very simple clustering: probes belong to same cluster if Jaccard >= threshold."""
    probes = list(paths_by_probe.keys())
    assigned = set()
    clusters = []
    cluster_id = 0
    for p in probes:
        if p in assigned:
            continue
        cluster = [p]
        assigned.add(p)
        for q in probes:
            if q in assigned:
                continue
            if jaccard(paths_by_probe[p], paths_by_probe[q]) >= threshold:
                cluster.append(q)
                assigned.add(q)
        clusters.append((f"C{cluster_id}", cluster))
        cluster_id += 1
    return clusters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="JSONL path")
    ap.add_argument("--target-name", required=True)
    ap.add_argument("--target-url", required=True)
    ap.add_argument("--window-start", required=True, help="ISO8601")
    ap.add_argument("--window-stop", required=True, help="ISO8601")
    ap.add_argument("--cohort-plan-hash", required=True)
    ap.add_argument("--jaccard-collapse-threshold", type=float, default=0.75)
    ap.add_argument("--max-asn-share-threshold", type=float, default=0.20)
    ap.add_argument("--min-asn-entropy", type=float, default=3.0)
    args = ap.parse_args()

    paths_by_probe: Dict[str, List[int]] = {}
    raw_hashes: Dict[str, str] = {}

    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            pid = str(obj["probe_id"])
            paths_by_probe[pid] = [int(x) for x in obj.get("as_path", [])]
            raw_hashes[pid] = str(obj.get("raw_hash", ""))

    # ASN distribution (use first AS as a crude proxy for access ASN)
    access_asn = [p[0] for p in paths_by_probe.values() if p]
    asn_counts = Counter(access_asn)
    total = sum(asn_counts.values()) or 1
    max_asn_share = max(asn_counts.values(), default=0) / total
    asn_entropy = shannon_entropy(asn_counts)
    mean_j = mean_pairwise_jaccard(list(paths_by_probe.values()))

    clusters = simple_cluster(paths_by_probe, threshold=args.jaccard_collapse_threshold)

    collapse = (max_asn_share >= args.max_asn_share_threshold) or (asn_entropy <= args.min_asn_entropy) or (mean_j >= args.jaccard_collapse_threshold)

    report = {
        "schema_version": "1.0.0",
        "report_id": f"PCR-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "target": {"name": args.target_name, "url": args.target_url},
        "window": {"start": args.window_start, "stop": args.window_stop},
        "cohort_plan_hash": args.cohort_plan_hash,
        "paths": [
            {"probe_id": pid, "as_path": paths_by_probe[pid], "raw_hash": raw_hashes.get(pid, "")}
            for pid in sorted(paths_by_probe.keys())
        ],
        "metrics": {
            "asn_entropy": asn_entropy,
            "max_asn_share": max_asn_share,
            "mean_jaccard": mean_j,
            "collapse_detected": collapse,
            "clusters": [
                {
                    "cluster_id": cid,
                    "probe_ids": sorted(members),
                    "representative_path": paths_by_probe[members[0]] if members else [],
                }
                for cid, members in clusters
            ],
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "hashes": {"canonical_json_sha256": ""},
        "signature": {"alg": "", "value": ""},
    }

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
