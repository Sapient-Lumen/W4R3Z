"""Offline verifier for the PACT replay pack demo.

Usage:
  python verify_replay_pack.py /path/to/PACT_workdir/replay_pack

This verifier intentionally mirrors the paper's "receipt-driven admission" story:
- recompute run root from manifest
- verify DSSE signature on PPP statement and check it binds to run root
- verify ABOM-view Merkle membership proof
- verify DSSE signature on policy decision receipt (PDR) and check it binds to run root

It is not a full PACT verifier.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def jcs(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def merkle_leaf(leaf_hash: bytes) -> bytes:
    return sha256(b"leaf:" + leaf_hash)


def merkle_parent(left: bytes, right: bytes) -> bytes:
    return sha256(b"node:" + left + right)


def merkle_verify(leaf_hash: bytes, proof: List[Tuple[str, str]], root: bytes) -> bool:
    h = merkle_leaf(leaf_hash)
    for side, sib_hex in proof:
        sib = bytes.fromhex(sib_hex)
        if side == "R":
            h = merkle_parent(h, sib)
        elif side == "L":
            h = merkle_parent(sib, h)
        else:
            raise ValueError(f"bad side: {side}")
    return h == root


def dsse_verify(env: Dict[str, Any], pk_by_keyid: Dict[str, Ed25519PublicKey]) -> bytes:
    payload_type = env["payloadType"]
    payload = b64d(env["payload"])
    sigs = env.get("signatures", [])
    if not sigs:
        raise ValueError("no signatures")

    to_verify = payload_type.encode("utf-8") + b"\x00" + payload
    for s in sigs:
        keyid = s["keyid"]
        pk = pk_by_keyid.get(keyid)
        if pk is None:
            continue
        sig = b64d(s["sig"])
        pk.verify(sig, to_verify)
        return payload
    raise ValueError("no acceptable signature")


def read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python verify_replay_pack.py /path/to/replay_pack", file=sys.stderr)
        raise SystemExit(2)

    d = Path(sys.argv[1]).resolve()
    keys = read_json(d / "keys.json")
    keyid = keys["run_root_signer"]["keyid"]
    pk_raw = b64d(keys["run_root_signer"]["public_key_raw_b64"])
    pk = Ed25519PublicKey.from_public_bytes(pk_raw)
    pk_map = {keyid: pk}

    manifest = read_json(d / "manifest.json")
    run_root = sha256_hex(jcs(manifest))

    # PPP (run anchor)
    env = read_json(d / "ppp_run_root.dsse.json")
    payload = dsse_verify(env, pk_map)
    stmt = json.loads(payload)
    assert stmt["predicateType"] == "https://pact.dev/predicate/run-root/v1"
    assert stmt["subject"][0]["digest"]["sha256"] == run_root

    pred = stmt["predicate"]
    assert pred["roots"]["storeRoot"]["sha256"] == manifest["store_merkle_root_sha256"]
    views_root = bytes.fromhex(pred["roots"]["viewsRoot"]["sha256"])

    # ABOM view
    view = read_json(d / "abom_view_one_object.json")
    assert view["run_root"]["sha256"] == run_root
    assert view["storeRoot"]["sha256"] == manifest["store_merkle_root_sha256"]
    root = bytes.fromhex(view["storeRoot"]["sha256"])
    leaf_hash = bytes.fromhex(view["disclosed"]["payload_sha256"])
    proof = [(x["side"], x["sibling_hex"]) for x in view["disclosed"]["merkle_proof"]]
    assert merkle_verify(leaf_hash, proof, root)

    view_leaf = bytes.fromhex(view["viewsLeafSha256"])
    view_proof = [(x["side"], x["sibling_hex"]) for x in view["viewsProof"]]
    assert merkle_verify(view_leaf, view_proof, views_root)

    # Policy decision
    pdr_env = read_json(d / "policy_decision.dsse.json")
    pdr_payload = dsse_verify(pdr_env, pk_map)
    pdr_stmt = json.loads(pdr_payload)
    assert pdr_stmt["predicateType"] == "https://pact.dev/predicate/policy-decision/v1"
    assert pdr_stmt["subject"][0]["digest"]["sha256"] == run_root
    assert pdr_stmt["predicate"]["decision"] == "pass"

    print("OK")
    print("run_root_sha256:", run_root)
    print("store_root_sha256:", view["storeRoot"]["sha256"])


if __name__ == "__main__":
    main()
