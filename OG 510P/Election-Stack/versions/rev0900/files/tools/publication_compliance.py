#!/usr/bin/env python3
"""
tools/publication_compliance.py

Compute a toy-but-useful PublicationCoverageReport from an evidence packet directory.

Inputs:
- PublicationContract envelope (kind: hfv.publication.contract)
- PublicationTriggerEvent envelopes (kind: hfv.publication.trigger_event)
- Any evidence envelopes referenced by contract rules (by kind)

Output:
- PublicationCoverageReport JSON to stdout (or --out)

This is a reference tool: it treats issued_at timestamps as publication time
and checks for existence of at least one envelope of the expected kind in the
deadline window [occurred_at, occurred_at + max_delay_seconds].

It intentionally does NOT attempt deep semantic linkage (e.g., mapping a notice
to an incident via IDs). That linkage can be layered on later.
"""

from __future__ import annotations
from pathlib import Path
import argparse, json, sys
from datetime import datetime, timezone, timedelta

def parse_dt(s: str) -> datetime:
    # Accept Z suffix
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s).astimezone(timezone.utc)

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def load_payload(packet_dir: Path, env: dict) -> dict:
    if "payload_inline" in env:
        return env["payload_inline"]
    pp = env.get("payload_pointer") or {}
    uri = pp.get("uri")
    if not uri:
        raise ValueError("Envelope has no payload_inline or payload_pointer.uri")
    obj = packet_dir / "objects" / uri
    return load_json(obj)

def find_envelopes(packet_dir: Path) -> list[dict]:
    envs=[]
    env_dir = packet_dir / "envelopes"
    if not env_dir.exists():
        return envs
    for p in sorted(env_dir.glob("*.envelope.json")):
        try:
            envs.append(load_json(p))
        except Exception:
            continue
    return envs

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("packet_dir", help="Path to evidence packet directory (contains envelopes/, objects/, manifest.json)")
    ap.add_argument("--out", help="Write report JSON to this file instead of stdout")
    args = ap.parse_args()

    packet_dir = Path(args.packet_dir).resolve()
    envs = find_envelopes(packet_dir)

    # Load contract (first one wins)
    contract_env = next((e for e in envs if e.get("kind") == "hfv.publication.contract"), None)
    if not contract_env:
        print("ERROR: no hfv.publication.contract envelope found", file=sys.stderr)
        return 2
    contract = load_payload(packet_dir, contract_env)
    contract_id = contract.get("contract_id", "unknown")

    rules = []
    for r in contract.get("rules", []):
        kind = (r.get("kind") or "").strip()
        trig = (r.get("trigger") or "").strip()
        mds = int(r.get("max_delay_seconds") or 0)
        if kind and trig and mds >= 0:
            rules.append({"kind": kind, "trigger_id": trig, "max_delay_seconds": mds})

    if not rules:
        print("ERROR: contract has no usable rules", file=sys.stderr)
        return 2

    # Load trigger events
    trigger_envs = [e for e in envs if e.get("kind") == "hfv.publication.trigger_event"]
    events=[]
    for te in trigger_envs:
        try:
            payload = load_payload(packet_dir, te)
            events.append({
                "event_id": payload.get("event_id"),
                "trigger_id": payload.get("trigger_id"),
                "occurred_at": payload.get("occurred_at"),
                "trigger_event_reference": te.get("payload_digest") or "",
            })
        except Exception:
            continue

    # Index existing envelopes by kind
    by_kind: dict[str, list[datetime]] = {}
    for e in envs:
        k = e.get("kind")
        if not k:
            continue
        try:
            t = parse_dt(e.get("issued_at"))
        except Exception:
            continue
        by_kind.setdefault(k, []).append(t)
    for k in list(by_kind.keys()):
        by_kind[k].sort()

    missed=[]
    per_rule_counts={}
    total=0
    satisfied=0

    # Determine time window
    occ_times=[]
    for ev in events:
        try:
            occ_times.append(parse_dt(ev["occurred_at"]))
        except Exception:
            pass
    if occ_times:
        window_start=min(occ_times)
        window_end=max(occ_times)
    else:
        window_start=parse_dt(contract_env.get("issued_at"))
        window_end=window_start

    # Evaluate
    for ev in events:
        try:
            occ=parse_dt(ev["occurred_at"])
        except Exception:
            continue
        for rule in rules:
            if rule["trigger_id"] != ev["trigger_id"]:
                continue
            total += 1
            deadline = occ + timedelta(seconds=rule["max_delay_seconds"])
            # satisfied if any envelope of kind in [occ, deadline]
            ok=False
            for t in by_kind.get(rule["kind"], []):
                if t < occ:
                    continue
                if t <= deadline:
                    ok=True
                    break
                if t > deadline:
                    break
            if ok:
                satisfied += 1
            else:
                missed.append({
                    "event_id": ev.get("event_id") or "unknown",
                    "trigger_id": ev["trigger_id"],
                    "expected_kind": rule["kind"],
                    "deadline": deadline.isoformat().replace("+00:00","Z"),
                    "trigger_event_reference": ev.get("trigger_event_reference","")
                })
            key=(rule["kind"], rule["trigger_id"])
            c=per_rule_counts.get(key, {"events_total":0,"events_satisfied":0,"events_missed":0})
            c["events_total"] += 1
            if ok: c["events_satisfied"] += 1
            else: c["events_missed"] += 1
            per_rule_counts[key]=c

    missed_n=len(missed)
    miss_rate = (missed_n/total) if total>0 else 0.0
    per_rule=[]
    for (kind,trig),c in sorted(per_rule_counts.items()):
        mt=c["events_missed"]
        mr=(mt/c["events_total"]) if c["events_total"]>0 else 0.0
        per_rule.append({
            "kind":kind,
            "trigger_id":trig,
            "events_total":c["events_total"],
            "events_satisfied":c["events_satisfied"],
            "events_missed":c["events_missed"],
            "miss_rate":mr
        })

    report={
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "contract_id": contract_id,
        "window_start": window_start.isoformat().replace("+00:00","Z"),
        "window_end": window_end.isoformat().replace("+00:00","Z"),
        "events_total": total,
        "events_satisfied": satisfied,
        "events_missed": missed_n,
        "miss_rate": miss_rate,
        "per_rule": per_rule,
        "missed_events": missed
    }

    out_txt=json.dumps(report, indent=2)
    if args.out:
        Path(args.out).write_text(out_txt, encoding="utf-8")
    else:
        print(out_txt)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
