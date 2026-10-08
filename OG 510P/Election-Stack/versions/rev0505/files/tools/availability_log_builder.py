#!/usr/bin/env python3
"""availability_log_builder.py

Minimal helper to build an Availability Transparency Log (ATL) feed from probe results and attestations.

This is *not* a production implementation. It is an artifact to guide real tooling.
"""
import json
import hashlib
import sys
from datetime import datetime, timezone

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main():
    if len(sys.argv) < 2:
        print("Usage: availability_log_builder.py <input.jsonl>", file=sys.stderr)
        sys.exit(2)

    entries=[]
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        for line in f:
            obj=json.loads(line)
            raw=json.dumps(obj, separators=(',', ':'), sort_keys=True).encode('utf-8')
            entries.append({
                "entry_hash": sha256_hex(raw),
                "entry_type": obj.get("type","unknown"),
                "seen_at": datetime.now(timezone.utc).isoformat()
            })

    out={
        "schema_version":"0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries
    }
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
