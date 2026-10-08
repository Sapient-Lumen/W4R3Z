#!/usr/bin/env python3
"""scripts/check_example_report_pins.py

Release-gate drift firewall for verifier-report examples.

Rationale:
- Example packets are used as regression vectors for operator tooling.
- Publishable verifier outputs may include registry sha256 pins for comparability.
  If those pins drift silently, published reports become ambiguous.

This check enforces that:
- any *_sha256 pins in PacketVerificationReport examples match this archive's canonical bytes
- PacketVerificationReport tool.version/tool.archive_version match the archive VERSION
- manifest_sha256 (when present) matches the example packet's manifest.json raw bytes
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "artifacts" / "examples"

KIND_PACKET_REPORT = "hfv.verifier.packet_verification_report"

REG_ENVELOPE_KINDS = ROOT / "artifacts" / "registries" / "envelope-kinds.csv"
REG_PROBLEM_CODES = ROOT / "artifacts" / "registries" / "verifier-problem-codes.csv"


def sha256_prefixed_bytes(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_payload_object(packet_dir: Path, env: Dict[str, Any]) -> Dict[str, Any] | None:
    ptr = env.get("payload_pointer")
    if not isinstance(ptr, dict):
        return None
    uri = (ptr.get("uri") or "").strip()
    if not uri:
        return None
    rel = uri if uri.startswith("objects/") else f"objects/{uri}"
    path = (packet_dir / rel).resolve()
    try:
        # Only allow payloads inside the packet.
        path.relative_to(packet_dir.resolve())
    except Exception:
        return None
    if not path.exists():
        return None
    obj = load_json(path)
    return obj if isinstance(obj, dict) else None


def check_packet_verification_report(packet_dir: Path, env_path: Path, env: Dict[str, Any], failures: List[str]) -> None:
    payload = read_payload_object(packet_dir, env)
    if not payload:
        failures.append(f"{env_path}: missing/invalid payload object")
        return

    # tool.version pins must match archive version for example packets.
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    tool = payload.get("tool")
    if not isinstance(tool, dict):
        failures.append(f"{env_path}: payload.tool missing")
    else:
        tv = str(tool.get("version") or "")
        tav = str(tool.get("archive_version") or "")
        if tv and tv != version:
            failures.append(f"{env_path}: tool.version drift (got {tv!r} want {version!r})")
        if tav and tav != version:
            failures.append(f"{env_path}: tool.archive_version drift (got {tav!r} want {version!r})")

    # Registry pins must match canonical bytes when present.
    if "envelope_kinds_sha256" in payload and REG_ENVELOPE_KINDS.exists():
        want = sha256_prefixed_bytes(REG_ENVELOPE_KINDS.read_bytes())
        got = str(payload.get("envelope_kinds_sha256") or "")
        if got and got != want:
            failures.append(f"{env_path}: envelope_kinds_sha256 mismatch (got {got} want {want})")

    if "verifier_problem_codes_sha256" in payload and REG_PROBLEM_CODES.exists():
        want = sha256_prefixed_bytes(REG_PROBLEM_CODES.read_bytes())
        got = str(payload.get("verifier_problem_codes_sha256") or "")
        if got and got != want:
            failures.append(f"{env_path}: verifier_problem_codes_sha256 mismatch (got {got} want {want})")

    # Manifest sha256 (when present) refers to the *verified* packet (not the report packet).
    # Best-effort: if payload.packet_dir points to a sibling example packet with a manifest,
    # enforce that it matches.
    if "manifest_sha256" in payload:
        target = str(payload.get("packet_dir") or "").strip()
        if target:
            target_manifest = EXAMPLES / target / "manifest.json"
            if target_manifest.exists():
                want = sha256_prefixed_bytes(target_manifest.read_bytes())
                got = str(payload.get("manifest_sha256") or "")
                if got and got != want:
                    failures.append(f"{env_path}: manifest_sha256 mismatch (got {got} want {want})")


def main() -> int:
    failures: List[str] = []
    if not EXAMPLES.exists():
        return 0

    for pkt in sorted(EXAMPLES.iterdir()):
        if not pkt.is_dir():
            continue
        env_dir = pkt / "envelopes"
        if not env_dir.exists():
            continue
        for env_path in sorted(env_dir.glob("*.json")):
            try:
                env = load_json(env_path)
            except Exception as e:
                failures.append(f"{env_path}: JSON parse failed: {e}")
                continue
            if not isinstance(env, dict):
                continue
            kind = env.get("kind")
            if kind == KIND_PACKET_REPORT:
                check_packet_verification_report(pkt, env_path, env, failures)

    if failures:
        for f in failures:
            print("ERROR:", f)
        return 2

    print("PASS: example report pins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
