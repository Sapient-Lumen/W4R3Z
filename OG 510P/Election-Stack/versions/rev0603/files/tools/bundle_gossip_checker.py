#!/usr/bin/env python3
"""bundle_gossip_checker.py

Minimal reference tool to:
- parse BundleGossipMessage JSON (from stdin or file)
- summarize checkpoint hashes observed
- flag split-view conditions (multiple checkpoint hashes seen)

This tool does NOT verify signatures; it is a demo/debug utility.
"""

import argparse
import json
import sys
from collections import defaultdict


def iter_messages(fp):
    for line in fp:
        line = line.strip()
        if not line:
            continue
        yield json.loads(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="JSONL file of BundleGossipMessage; default stdin")
    ap.add_argument("--max", type=int, default=100000, help="Max messages to read")
    args = ap.parse_args()

    fp = open(args.path, "r", encoding="utf-8") if args.path else sys.stdin

    checkpoint_to_senders = defaultdict(set)
    manifests = set()
    priority = set()

    count = 0
    for msg in iter_messages(fp):
        count += 1
        if count > args.max:
            break
        if msg.get("type") != "DIGEST":
            continue
        sender = msg.get("sender_id", "?")
        payload = msg.get("payload", {})
        ch = payload.get("checkpoint_hash")
        if ch:
            checkpoint_to_senders[ch].add(sender)
        for h in payload.get("known_manifest_hashes", []) or []:
            manifests.add(h)
        for h in payload.get("priority_manifest_hashes", []) or []:
            priority.add(h)

    summary = {
        "messages_read": count,
        "unique_checkpoint_hashes": len(checkpoint_to_senders),
        "checkpoint_hashes": [
            {"checkpoint_hash": ch, "sender_count": len(senders), "senders": sorted(list(senders))[:50]}
            for ch, senders in sorted(checkpoint_to_senders.items(), key=lambda x: (-len(x[1]), x[0]))
        ],
        "unique_manifest_hashes": len(manifests),
        "unique_priority_manifest_hashes": len(priority),
        "split_view_suspected": len(checkpoint_to_senders) > 1,
    }

    json.dump(summary, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
