#!/usr/bin/env python3
"""Minimal Availability Witness Gossip checker.

Reads newline-delimited JSON AvailabilityGossipMessage objects and reports:
- latest checkpoint per sender
- conflicting checkpoints for same (sender_id, epoch)

This is intentionally minimal and NOT production code.
"""

import json
import sys
from collections import defaultdict


def main(path: str) -> int:
    by_sender_epoch = defaultdict(set)
    latest = {}

    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                print(f"Line {i}: invalid JSON", file=sys.stderr)
                continue

            sender = msg.get("sender_id", "?")
            ck = (msg.get("atl_checkpoint") or {})
            epoch = ck.get("epoch")
            chash = ck.get("checkpoint_hash")
            if epoch is None or not chash:
                print(f"Line {i}: missing checkpoint fields", file=sys.stderr)
                continue

            by_sender_epoch[(sender, epoch)].add(chash)
            latest[sender] = (epoch, chash)

    # Report conflicts
    conflicts = 0
    for (sender, epoch), hashes in sorted(by_sender_epoch.items(), key=lambda x: (x[0][0], x[0][1])):
        if len(hashes) > 1:
            conflicts += 1
            print(f"CONFLICT sender={sender} epoch={epoch} hashes={sorted(hashes)}")

    print("---")
    for sender, (epoch, chash) in sorted(latest.items()):
        print(f"latest sender={sender} epoch={epoch} checkpoint_hash={chash}")

    if conflicts:
        print(f"\nDetected {conflicts} sender/epoch conflicts.")
        return 2

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: availability_gossip_checker.py <awg_messages.jsonl>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
