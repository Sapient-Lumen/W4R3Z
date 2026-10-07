#!/usr/bin/env python3
"""Create a DSSE envelope signature for the external package attestation.

The deterministic packager writes an unsigned in-toto/SLSA statement after the
zip is built.  This helper signs the exact statement bytes as a DSSE payload with
an operator-provided Ed25519 private key and records a key id derived from the
public key bytes.  The private key is never expected to be in the archive.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import Any

DSSE_PAYLOAD_TYPE = "application/vnd.in-toto+json"


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def default_artifact_paths(root: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    zip_path = (root.parent / release["bundle"]).resolve()
    attestation = zip_path.with_suffix(zip_path.suffix + ".package.intoto.jsonl")
    envelope = zip_path.with_suffix(zip_path.suffix + ".package.dsse.json")
    public_key_sidecar = zip_path.with_suffix(zip_path.suffix + ".package.dsse.pub.pem")
    return attestation, envelope, public_key_sidecar


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def public_key_id(public_key_path: pathlib.Path) -> str:
    return "sha256:" + sha256_bytes(public_key_path.read_bytes())


def dsse_preauth_encoding(payload_type: str, payload: bytes) -> bytes:
    payload_type_bytes = payload_type.encode("utf-8")
    return b"DSSEv1 " + str(len(payload_type_bytes)).encode("ascii") + b" " + payload_type_bytes + b" " + str(len(payload)).encode("ascii") + b" " + payload


def run_openssl(args: list[str], *, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, timeout=timeout)


def sign_bytes(private_key: pathlib.Path, preauth: bytes) -> bytes:
    with tempfile.TemporaryDirectory(prefix="anonymity_dsse_sign_") as tmp_s:
        tmp = pathlib.Path(tmp_s)
        msg = tmp / "preauth.bin"
        sig = tmp / "signature.bin"
        msg.write_bytes(preauth)
        proc = run_openssl(["openssl", "pkeyutl", "-sign", "-rawin", "-inkey", str(private_key), "-in", str(msg), "-out", str(sig)])
        if proc.returncode != 0:
            raise RuntimeError("openssl Ed25519 sign failed: " + (proc.stderr or proc.stdout)[-1000:])
        return sig.read_bytes()


def verify_signature(public_key: pathlib.Path, preauth: bytes, signature: bytes) -> None:
    with tempfile.TemporaryDirectory(prefix="anonymity_dsse_verify_") as tmp_s:
        tmp = pathlib.Path(tmp_s)
        msg = tmp / "preauth.bin"
        sig = tmp / "signature.bin"
        msg.write_bytes(preauth)
        sig.write_bytes(signature)
        proc = run_openssl(["openssl", "pkeyutl", "-verify", "-rawin", "-pubin", "-inkey", str(public_key), "-in", str(msg), "-sigfile", str(sig)])
        if proc.returncode != 0:
            raise RuntimeError("openssl Ed25519 verify failed after signing: " + (proc.stderr or proc.stdout)[-1000:])


def build_envelope(attestation_path: pathlib.Path, private_key_path: pathlib.Path, public_key_path: pathlib.Path, payload_type: str) -> dict[str, Any]:
    payload = attestation_path.read_bytes()
    preauth = dsse_preauth_encoding(payload_type, payload)
    signature = sign_bytes(private_key_path, preauth)
    verify_signature(public_key_path, preauth, signature)
    return {
        "payloadType": payload_type,
        "payload": base64.b64encode(payload).decode("ascii"),
        "signatures": [
            {
                "keyid": public_key_id(public_key_path),
                "sig": base64.b64encode(signature).decode("ascii"),
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--attestation", default="")
    parser.add_argument("--private-key", required=True)
    parser.add_argument("--public-key", default="signing/package_attestation_public_key.pem")
    parser.add_argument("--out", default="")
    parser.add_argument("--public-key-sidecar", default="")
    parser.add_argument("--payload-type", default=DSSE_PAYLOAD_TYPE)
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    default_attestation, default_out, default_public_key_sidecar = default_artifact_paths(root)
    attestation_path = pathlib.Path(args.attestation).resolve() if args.attestation else default_attestation
    private_key_path = pathlib.Path(args.private_key).resolve()
    public_key_path = pathlib.Path(args.public_key).resolve() if pathlib.Path(args.public_key).is_absolute() else (root / args.public_key).resolve()
    out_path = pathlib.Path(args.out).resolve() if args.out else default_out
    public_key_sidecar_path = pathlib.Path(args.public_key_sidecar).resolve() if args.public_key_sidecar else default_public_key_sidecar

    if not attestation_path.exists():
        raise SystemExit(f"package attestation not found: {attestation_path}")
    if not private_key_path.exists():
        raise SystemExit(f"private key not found: {private_key_path}")
    if not public_key_path.exists():
        raise SystemExit(f"public key not found: {public_key_path}")

    envelope = build_envelope(attestation_path, private_key_path, public_key_path, args.payload_type)
    out_path.write_text(json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    public_key_sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(public_key_path, public_key_sidecar_path)
    print(json.dumps({
        "status": "pass",
        "envelope": str(out_path),
        "attestation": str(attestation_path),
        "public_key": str(public_key_path),
        "public_key_sidecar": str(public_key_sidecar_path),
        "keyid": envelope["signatures"][0]["keyid"],
        "payload_type": envelope["payloadType"],
        "payload_sha256": sha256_bytes(attestation_path.read_bytes()),
        "public_key_sidecar_sha256": sha256_bytes(public_key_sidecar_path.read_bytes()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
