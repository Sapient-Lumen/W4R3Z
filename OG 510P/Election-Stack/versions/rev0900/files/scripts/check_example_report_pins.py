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
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "artifacts" / "examples"

KIND_PACKET_REPORT = "hfv.verifier.packet_verification_report"

REG_ENVELOPE_KINDS = ROOT / "artifacts" / "registries" / "envelope-kinds.csv"
REG_ATTACHMENT_REQS = ROOT / "artifacts" / "registries" / "envelope-attachment-requirements.csv"
REG_RECEIPT_PROFILES = ROOT / "artifacts" / "registries" / "receipt-profiles.csv"
REG_PROBLEM_CODES = ROOT / "artifacts" / "registries" / "verifier-problem-codes.csv"
REG_VERIFIER_PROFILES = ROOT / "artifacts" / "registries" / "verifier-profiles.csv"
POLICY_PROFILE_TEMPLATE = ROOT / "artifacts" / "templates" / "verifier-policy-profile.json"

# Import RFC8785-JCS helper from tools/ (stdlib-only; used for stable digest pins).
sys.path.insert(0, str(ROOT / "tools"))
from jcs import dump_bytes as jcs_bytes


def sha256_prefixed_bytes(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def policy_profile_digest(path: Path) -> str:
    """Compute sha256 pin for a VerifierPolicyProfile JSON (RFC8785-JCS canonical bytes)."""
    try:
        obj = load_json(path)
        return sha256_prefixed_bytes(jcs_bytes(obj))
    except Exception:
        # Fallback: raw bytes (best-effort).
        try:
            return sha256_prefixed_bytes(path.read_bytes())
        except Exception:
            return ""


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

    authn = str(payload.get("authentication_status") or "")
    if authn != "HASH_ONLY_NOT_AUTHENTICATED":
        failures.append(f"{env_path}: authentication_status drift (got {authn!r} want 'HASH_ONLY_NOT_AUTHENTICATED')")

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

    if "attachment_requirements_sha256" in payload and REG_ATTACHMENT_REQS.exists():
        want = sha256_prefixed_bytes(REG_ATTACHMENT_REQS.read_bytes())
        got = str(payload.get("attachment_requirements_sha256") or "")
        if got and got != want:
            failures.append(f"{env_path}: attachment_requirements_sha256 mismatch (got {got} want {want})")

    if "receipt_profiles_sha256" in payload and REG_RECEIPT_PROFILES.exists():
        want = sha256_prefixed_bytes(REG_RECEIPT_PROFILES.read_bytes())
        got = str(payload.get("receipt_profiles_sha256") or "")
        if got and got != want:
            failures.append(f"{env_path}: receipt_profiles_sha256 mismatch (got {got} want {want})")

    
    if "verifier_profiles_sha256" in payload and REG_VERIFIER_PROFILES.exists():
        want = sha256_prefixed_bytes(REG_VERIFIER_PROFILES.read_bytes())
        got = str(payload.get("verifier_profiles_sha256") or "")
        if got and got != want:
            failures.append(f"{env_path}: verifier_profiles_sha256 mismatch (got {got} want {want})")


    # Example comparability: policy profile digest pin (bytes published alongside verifier output).
    if packet_dir.name == "evidence_packet_packet_verification_report_minimal":
        want = policy_profile_digest(POLICY_PROFILE_TEMPLATE) if POLICY_PROFILE_TEMPLATE.exists() else ""
        got = str(payload.get("policy_profile_sha256") or "")
        if not got:
            failures.append(f"{env_path}: missing policy_profile_sha256 (required for this example packet)")
        elif want and got != want:
            failures.append(f"{env_path}: policy_profile_sha256 mismatch (got {got} want {want})")

        # The report envelope subject should also carry the policy pin for index-only scans.
        subj = env.get("subject")
        if isinstance(subj, dict):
            sp = str(subj.get("policy_profile_sha256") or "")
            if got and sp != got:
                failures.append(f"{env_path}: envelope subject missing/incorrect policy_profile_sha256 (got {sp!r} want {got!r})")
        else:
            failures.append(f"{env_path}: envelope subject missing for policy_profile_sha256 check")

        # Enforce that the minimal example packet actually ships the pinned policy profile bytes as an object
        # (content-addressed by the same sha256). This keeps the example fully offline-comparable.
        mpath = packet_dir / "manifest.json"
        if not mpath.exists():
            failures.append(f"{env_path}: missing manifest.json for policy-profile shipping check")
        else:
            try:
                man = load_json(mpath)
                arts = man.get("artifacts") if isinstance(man, dict) else None
                found = None
                if isinstance(arts, list):
                    for a in arts:
                        if isinstance(a, dict) and str(a.get("digest") or "") == got:
                            found = a
                            break
                if not found:
                    failures.append(f"{env_path}: manifest.json does not include policy profile artifact (digest {got})")
                else:
                    url = str(found.get("url") or "").strip()
                    if not url:
                        failures.append(f"{env_path}: policy profile artifact missing url in manifest.json")
                    else:
                        fpath = (packet_dir / url).resolve()
                        try:
                            fpath.relative_to(packet_dir.resolve())
                        except Exception:
                            failures.append(f"{env_path}: policy profile artifact url escapes packet: {url!r}")
                        else:
                            if not fpath.exists():
                                failures.append(f"{env_path}: policy profile object missing at {url!r}")
                            else:
                                want_hex = got.split(":", 1)[1]
                                have = sha256_prefixed_bytes(fpath.read_bytes())
                                have_hex = have.split(":", 1)[1]
                                if have_hex.lower() != want_hex.lower():
                                    failures.append(f"{env_path}: policy profile object hash mismatch (got {have} want {got})")
            except Exception as e:
                failures.append(f"{env_path}: could not validate policy profile artifact shipping: {e}")

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

                # Optional formatting-independent manifest digest (RFC8785-JCS canonical bytes).
                want_jcs = ''
                try:
                    obj = load_json(target_manifest)
                    want_jcs = sha256_prefixed_bytes(jcs_bytes(obj))
                except Exception:
                    want_jcs = ''

                if 'manifest_jcs_sha256' in payload:
                    got_jcs = str(payload.get('manifest_jcs_sha256') or '')
                    if want_jcs and got_jcs and got_jcs != want_jcs:
                        failures.append(f"{env_path}: manifest_jcs_sha256 mismatch (got {got_jcs} want {want_jcs})")
                elif packet_dir.name == 'evidence_packet_packet_verification_report_minimal' and want_jcs:
                    failures.append(f"{env_path}: missing manifest_jcs_sha256 (recommended for JSON-manifest comparability)")


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
