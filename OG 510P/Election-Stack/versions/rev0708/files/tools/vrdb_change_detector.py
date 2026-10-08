#!/usr/bin/env python3
"""
vrdb_change_detector.py
Toy reference tool: compares two JSON snapshot manifests and emits a VRDBChangeAlert skeleton.

This is NOT production code. It is meant to illustrate how a monitor could detect large deltas and
produce content-addressed evidence for publication.
"""
import json, sys, hashlib, datetime

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load(path):
    with open(path, "rb") as f:
        data = f.read()
    return json.loads(data), sha256(data)

def main(old_path, new_path):
    old, old_hash = load(old_path)
    new, new_hash = load(new_path)

    # naive metrics
    old_parts = {p.get("partition_id"): p.get("root_hash") for p in old.get("partitions", [])}
    new_parts = {p.get("partition_id"): p.get("root_hash") for p in new.get("partitions", [])}
    changed = [pid for pid in set(old_parts)|set(new_parts) if old_parts.get(pid)!=new_parts.get(pid)]

    alert = {
        "schema_version": "1.0",
        "alert_id": "alert-"+sha256((old_hash+new_hash).encode())[:16],
        "created_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
        "epoch_id": new.get("epoch_id"),
        "severity": "warning" if changed else "info",
        "summary": f"{len(changed)} partitions changed between snapshots",
        "metrics": {
            "old_snapshot_id": old.get("snapshot_id"),
            "new_snapshot_id": new.get("snapshot_id"),
            "old_hash": old_hash,
            "new_hash": new_hash,
            "changed_partitions": changed,
        },
        "evidence_refs": {
            "old_snapshot_manifest": old_path,
            "new_snapshot_manifest": new_path
        },
        "signature": {
            "key_id": "TODO",
            "sig_alg": "TODO",
            "signature": "TODO"
        }
    }
    print(json.dumps(alert, indent=2))

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print("Usage: vrdb_change_detector.py OLD.json NEW.json", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
