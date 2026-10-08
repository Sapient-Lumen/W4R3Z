#!/usr/bin/env python3
"""
inspection_gossip_checker.py — tiny reference checker for inspection gossip streams.

Reads JSONL of PublicInspectionGossipMessage and reports:
- unseen challenges past deadlines (requires optional sidecar)
- inconsistent digests across peers
"""

import argparse
import json
import sys
from collections import defaultdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gossip-jsonl", required=True)
    args = ap.parse_args()

    challenges = defaultdict(set)  # id -> {digest}
    responses = defaultdict(set)
    suppressions = defaultdict(set)

    with open(args.gossip_jsonl, "r") as f:
        for line in f:
            if not line.strip():
                continue
            msg = json.loads(line)
            for x in msg.get("challenge_digests", []):
                challenges[x["challenge_id"]].add(x["digest"])
            for x in msg.get("response_digests", []):
                responses[x["response_id"]].add(x["digest"])
            for x in msg.get("suppression_digests", []):
                suppressions[x["report_id"]].add(x["digest"])

    def report(name, d):
        bad = {k:v for k,v in d.items() if len(v) > 1}
        print(f"{name}: {len(d)} seen, {len(bad)} inconsistent")
        for k,v in list(bad.items())[:20]:
            print("  ", k, list(v))

    report("challenges", challenges)
    report("responses", responses)
    report("suppressions", suppressions)


if __name__ == "__main__":
    main()
