#!/usr/bin/env python3
"""
tools/observer_verify_packet.py

Offline integrity checks for an evidence packet directory.

Checks:
- content-addressed objects: sha256 matches filename (sha256-<hex>.*)
- envelopes: payload_digest and tbs_digest recompute cleanly (docs/176)
- attachments: referenced objects exist and hash-match; optional receipt profile validation
- manifest: referenced digests exist (best effort)

Signature verification is NOT performed (stdlib-only).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Tuple, List
import csv

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PROFILE_REGISTRY = ROOT / "artifacts" / "registries" / "receipt-profiles.csv"

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def jcs_dumps(obj: Any) -> str:
    # Stdlib approximation of RFC8785-JCS: sort keys, no whitespace.
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def load_receipt_profiles() -> set[str]:
    if not RECEIPT_PROFILE_REGISTRY.exists():
        return set()
    profiles=set()
    try:
        with RECEIPT_PROFILE_REGISTRY.open("r", encoding="utf-8", newline="") as f:
            r=csv.DictReader(f)
            for row in r:
                p=row.get("profile")
                if p:
                    profiles.add(p)
    except Exception:
        return set()
    return profiles

RECEIPT_PROFILES = load_receipt_profiles()

def build_tbs(env: Dict[str, Any]) -> Dict[str, Any]:
    t = {k: env[k] for k in [
        "envelope_version","kind","track","issued_at","issuer","subject",
        "payload_schema","payload_digest","canonicalization"
    ]}
    if "attachments" in env:
        t["attachments"] = env["attachments"]
    return t

def read_payload_bytes(env: Dict[str, Any], packet_dir: Path) -> Tuple[bytes, str]:
    if "payload_inline" in env:
        payload_bytes = jcs_dumps(env["payload_inline"]).encode("utf-8")
        return payload_bytes, "inline"
    ptr = env.get("payload_pointer")
    if not isinstance(ptr, dict):
        return b"", "missing_payload_pointer"
    uri = ptr.get("uri","")
    if not uri:
        return b"", "missing_uri"
    p = (packet_dir/"objects"/uri)
    if not p.exists():
        return b"", f"missing:{uri}"
    return p.read_bytes(), f"objects/{uri}"

def recompute_payload_digest(env: Dict[str, Any], packet_dir: Path) -> Tuple[str, str]:
    payload_bytes, where = read_payload_bytes(env, packet_dir)
    if not payload_bytes:
        return "sha256:" + ("0"*64), where
    return f"sha256:{sha256_bytes(payload_bytes)}", where

def verify_objects(objects_dir: Path) -> List[str]:
    problems=[]
    if not objects_dir.exists():
        return ["objects_dir_missing"]
    for p in objects_dir.iterdir():
        if not p.is_file():
            continue
        name=p.name
        if not name.startswith("sha256-"):
            continue
        hexpart=name[len("sha256-"):].split(".",1)[0]
        got=sha256_bytes(p.read_bytes())
        if got.lower()!=hexpart.lower():
            problems.append(f"object_hash_mismatch:{name}")
    return problems

def verify_attachments(env: Dict[str, Any], packet_dir: Path, env_name: str) -> List[str]:
    problems=[]
    atts = env.get("attachments")
    if not atts:
        return problems
    if not isinstance(atts, list):
        return [f"attachments_not_array:{env_name}"]
    for i, att in enumerate(atts):
        if not isinstance(att, dict):
            problems.append(f"attachment_not_object:{env_name}:{i}")
            continue
        d = att.get("digest")
        if not d or not isinstance(d, str) or not d.startswith("sha256:"):
            problems.append(f"attachment_missing_digest:{env_name}:{i}")
            continue
        uri = att.get("uri","")
        if not uri:
            problems.append(f"attachment_missing_uri:{env_name}:{i}:{d}")
            continue
        tgt = packet_dir/"objects"/uri
        if not tgt.exists():
            problems.append(f"attachment_missing_object:{env_name}:{i}:{d}")
            continue
        got = sha256_bytes(tgt.read_bytes())
        want = d.split(":",1)[1]
        if got.lower()!=want.lower():
            problems.append(f"attachment_hash_mismatch:{env_name}:{i}:{tgt.relative_to(packet_dir)}")
            continue

        # Optional: validate receipt profile identifiers (drift firewall)
        if att.get("rel") == "transparency_receipt" and tgt.suffix == ".json":
            try:
                robj = json.loads(tgt.read_text(encoding="utf-8"))
                prof = robj.get("profile")
                if not prof:
                    problems.append(f"receipt_profile_missing:{env_name}:{i}")
                elif RECEIPT_PROFILES and prof not in RECEIPT_PROFILES:
                    problems.append(f"receipt_profile_unknown:{env_name}:{i}:{prof}")
            except Exception:
                problems.append(f"receipt_unparseable:{env_name}:{i}")

    return problems

def verify_envelopes(env_dir: Path, packet_dir: Path) -> List[str]:
    problems=[]
    if not env_dir.exists():
        return ["envelopes_dir_missing"]
    for p in env_dir.iterdir():
        if not p.is_file() or not p.name.endswith(".json"):
            continue
        env=json.loads(p.read_text(encoding="utf-8"))
        problems += verify_attachments(env, packet_dir, p.name)

        recomputed, where = recompute_payload_digest(env, packet_dir)
        if recomputed != env.get("payload_digest"):
            problems.append(f"payload_digest_mismatch:{p.name}:{where}")

        tbs=build_tbs(env)
        tbs_bytes=jcs_dumps(tbs).encode("utf-8")
        tbs_digest=f"sha256:{sha256_bytes(tbs_bytes)}"
        if tbs_digest != env.get("tbs_digest"):
            problems.append(f"tbs_digest_mismatch:{p.name}")
    return problems

def verify_manifest(packet_dir: Path) -> List[str]:
    problems=[]
    mpath=packet_dir/"manifest.json"
    if not mpath.exists():
        return ["manifest_missing"]
    m=json.loads(mpath.read_text(encoding="utf-8"))
    arts=m.get("artifacts",[])
    for a in arts:
        d=a.get("digest") or (("sha256:"+a["sha256"]) if "sha256" in a else "")
        if not isinstance(d, str) or not d.startswith("sha256:"):
            continue
        hexv=d.split(":")[1]
        found=False
        for root in [packet_dir/"objects", packet_dir]:
            for ext in [".json",".bin",".txt",".md",".csv",".toml",""]:
                pp=root/f"sha256-{hexv}{ext}"
                if pp.exists():
                    found=True; break
            if found: break
        if not found:
            problems.append(f"missing_artifact_object:{a.get('name','?')}:{d}")
    return problems

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("packet_dir", help="Packet directory")
    args=ap.parse_args()
    packet_dir=Path(args.packet_dir)

    problems=[]
    problems += verify_objects(packet_dir/"objects")
    problems += verify_envelopes(packet_dir/"envelopes", packet_dir)
    problems += verify_manifest(packet_dir)

    if problems:
        for p in problems:
            print("PROBLEM", p)
        return 2
    print("OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
