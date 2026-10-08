#!/usr/bin/env python3
"""
probe_reputation_scorer.py — reference skeleton

Purpose:
  Generate ProbeReputationRecord objects from probe telemetry (measurement summaries).
  This is NOT a full implementation; it provides a reproducible scaffolding:
    - deterministic inputs hash
    - deterministic code hash (hash of this file)
    - conservative scoring defaults

Inputs (expected):
  --input <path>   JSON or JSONL containing per-probe telemetry summaries:
                   { "probe_id": "...", "availability": 0..1, "jitter_ms": ..., "loss": 0..1, "peer_agreement": 0..1,
                     "interference": 0..1, "metadata": {...} }
  --window-start / --window-stop ISO-8601
  --created-by string
Outputs:
  JSON array of ProbeReputationRecord objects.
"""
import argparse, json, hashlib, datetime, pathlib, sys

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def file_sha256(path: pathlib.Path) -> str:
    return sha256_bytes(path.read_bytes())

def load_records(path: pathlib.Path):
    txt = path.read_text(encoding="utf-8")
    txt_strip = txt.strip()
    if not txt_strip:
        return []
    if txt_strip[0] == "[":
        return json.loads(txt_strip)
    # JSONL
    out = []
    for line in txt.splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out

def clamp01(x):
    try:
        x = float(x)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, x))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--window-start", required=True)
    ap.add_argument("--window-stop", required=True)
    ap.add_argument("--created-by", required=True)
    ap.add_argument("--out", default="-")
    args = ap.parse_args()

    in_path = pathlib.Path(args.input)
    telemetry = load_records(in_path)

    # Deterministic inputs hash
    inputs_hash = sha256_bytes(in_path.read_bytes())
    code_hash = file_sha256(pathlib.Path(__file__))

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    out = []
    for rec in telemetry:
        probe_id = rec.get("probe_id")
        if not probe_id:
            continue
        availability = clamp01(rec.get("availability", 0.0))
        stability = clamp01(rec.get("stability", rec.get("peer_jitter_score", 0.0)))
        consistency = clamp01(rec.get("peer_agreement", 0.0))
        interference = clamp01(rec.get("interference", 0.0))

        # Conservative confidence: require all four scores >= 0.8 for "high"
        scores = [availability, stability, consistency, 1.0 - interference]
        if min(scores) >= 0.8:
            confidence = "high"
        elif min(scores) >= 0.6:
            confidence = "medium"
        else:
            confidence = "low"

        out.append({
            "schema_version": "1.0",
            "probe_id": str(probe_id),
            "platform": rec.get("platform", "ripe_atlas"),
            "metadata": rec.get("metadata", {}),
            "window": {"start": args.window_start, "stop": args.window_stop},
            "scores": {
                "availability_score": availability,
                "stability_score": stability,
                "consistency_score": consistency,
                "interference_score": interference
            },
            "integrity_flags": rec.get("integrity_flags", []),
            "confidence": confidence,
            "created_at": now,
            "created_by": args.created_by,
            "hashes": {"inputs_hash": inputs_hash, "code_hash": code_hash},
            "signature": {"alg": "none", "value": ""}
        })

    out_json = json.dumps(out, indent=2, sort_keys=True)
    if args.out == "-":
        sys.stdout.write(out_json + "\n")
    else:
        pathlib.Path(args.out).write_text(out_json, encoding="utf-8")

if __name__ == "__main__":
    main()
