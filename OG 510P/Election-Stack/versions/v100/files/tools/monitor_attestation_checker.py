#!/usr/bin/env python3
"""monitor_attestation_checker.py

Minimal reference tool to parse MonitorAttestation JSON and summarize:
- scope, monitor_id
- latest checkpoint hashes observed
- inclusion sample stats (if present)

This tool does NOT verify signatures; it is a demo/debug utility.
"""

import argparse
import json
import sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="MonitorAttestation JSON; default stdin")
    args = ap.parse_args()

    fp = open(args.path, "r", encoding="utf-8") if args.path else sys.stdin
    obj = json.load(fp)

    if obj.get("type") != "MonitorAttestation":
        print("ERROR: not a MonitorAttestation", file=sys.stderr)
        sys.exit(2)

    out = {
        "monitor_id": obj.get("monitor_id"),
        "scope": obj.get("scope"),
        "window": obj.get("window"),
        "latest_checkpoint_hashes": (obj.get("observations", {}) or {}).get("latest_checkpoint_hashes", []),
    }

    inc = ((obj.get("checks", {}) or {}).get("inclusion_sample", {}) or {})
    if inc:
        out["inclusion_sample"] = {
            "strategy": inc.get("strategy"),
            "sample_size": inc.get("sample_size"),
            "failures": inc.get("failures"),
        }

    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
