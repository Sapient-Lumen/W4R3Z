#!/usr/bin/env python3
"""Check publication-receipt channel observed-digest enforcement.

This is a focused, fast regression gate for the current strict-policy verifier boundary:
receipt-level subject digests are not enough. Each independent publication channel
must carry its own observed subject digest, and removing those per-channel digest
observations must fail closed even when the caller supplies a matching byte pin
for the mutated receipt file.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Tuple

from _cli_harness import run_python_cli

ROOT = Path(__file__).resolve().parents[1]
PACKET = Path("artifacts/examples/evidence_packet_ed25519_threshold2_minimal")
def archive_version_num() -> str:
    raw = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    return raw.removeprefix("v").zfill(4)


VERSION_NUM = archive_version_num()
POLICY = Path(f"artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev{VERSION_NUM}.json")
POLICY_RECEIPT = Path(f"artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev{VERSION_NUM}.publication-receipt.json")
VERIFICATION_TIME = "2026-06-05T05:15:00Z"

MANUAL_FLAGS = {
    "trust_keyset": "--trust-keyset",
    "trust_keyset_receipt": "--trust-keyset-receipt",
    "trust_governance_bundle": "--trust-governance-bundle",
    "trust_governance_bundle_receipt": "--trust-governance-bundle-receipt",
    "trust_status_snapshot": "--trust-status-snapshot",
    "trust_status_snapshot_receipt": "--trust-status-snapshot-receipt",
    "signer_authorization_roster": "--signer-authorization-roster",
    "signer_authorization_roster_receipt": "--signer-authorization-roster-receipt",
}

RECEIPT_TARGETS = {
    "trust_keyset_receipt": "signature_trust_keyset_receipt_digest_mismatch",
    "trust_governance_bundle_receipt": "signature_trust_governance_bundle_receipt_digest_mismatch",
    "trust_status_snapshot_receipt": "signature_trust_status_snapshot_receipt_digest_mismatch",
    "signer_authorization_roster_receipt": "signature_signer_authorization_roster_receipt_digest_mismatch",
}

POLICY_RECEIPT_PROBLEM = "signature_verification_policy_lockfile_receipt_digest_mismatch"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_pin(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def fixture_paths() -> Mapping[str, Tuple[Path, str]]:
    policy = load_json(ROOT / POLICY)
    base = (ROOT / POLICY.parent / policy["trust_input_base_dir"]).resolve()
    out: Dict[str, Tuple[Path, str]] = {}
    for name, spec in policy["trust_inputs"].items():
        p = (base / spec["path"]).resolve()
        if not p.exists():
            fail(f"missing trust input {name}: {p}")
        actual = sha256_pin(p)
        if actual != spec["sha256"]:
            fail(f"trust input {name} pin mismatch: policy={spec['sha256']} actual={actual}")
        out[name] = (p, spec["sha256"])
    return out


def remove_channel_digest_fields(receipt: dict) -> dict:
    mutated = copy.deepcopy(receipt)
    channels = mutated.get("publication_channels")
    if not isinstance(channels, list) or not channels:
        fail("receipt has no publication_channels")
    removed = 0
    for channel in channels:
        if not isinstance(channel, dict):
            continue
        for key in list(channel.keys()):
            if key.startswith("observed_") and key.endswith("sha256"):
                channel.pop(key)
                removed += 1
    if removed == 0:
        fail("receipt mutation removed no per-channel observed digest fields")
    return mutated


def run_verifier(args: List[str]) -> dict:
    rc, out, err = run_python_cli(ROOT / "tools" / "observer_verify_packet.py", args, extra_sys_path=[ROOT / "tools", ROOT], cwd=ROOT)
    if not out.strip():
        fail(f"verifier produced no JSON output; rc={rc}; stderr={err[:500]}")
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        fail(f"verifier output was not JSON: {exc}; stdout={out[:500]}; stderr={err[:500]}")


def expect_failed_with(report: dict, problem_prefix: str) -> None:
    problems = report.get("problems") or []
    if report.get("authentication_status") != "SIGNATURE_FAILED":
        fail(f"expected SIGNATURE_FAILED, got {report.get('authentication_status')}; problems={problems[:6]}")
    if not any(str(p).startswith(problem_prefix) for p in problems):
        fail(f"expected {problem_prefix}, got {problems[:10]}")


def manual_args(inputs: Mapping[str, Tuple[Path, str]], override: Mapping[str, Tuple[Path, str]] | None = None) -> List[str]:
    merged = dict(inputs)
    if override:
        merged.update(override)
    args = [str(PACKET), "--json", "--public", "--verification-time", VERIFICATION_TIME]
    for name, flag in MANUAL_FLAGS.items():
        path, pin = merged[name]
        args.extend([flag, str(path), f"{flag}-sha256", pin])
    args.extend([
        "--require-authentication",
        "--require-trust-keyset-receipt",
        "--require-trust-governance-bundle",
        "--require-trust-governance-bundle-receipt",
        "--require-trust-status-snapshot",
        "--require-trust-status-snapshot-receipt",
        "--require-signer-authorization-roster",
        "--require-signer-authorization-roster-receipt",
    ])
    return args


def check_manual_receipt_family(inputs: Mapping[str, Tuple[Path, str]], receipt_name: str, problem_prefix: str, tempdir: Path) -> None:
    print(f"checking {receipt_name}...", flush=True)
    source, _pin = inputs[receipt_name]
    mutated = remove_channel_digest_fields(load_json(source))
    target = tempdir / f"{receipt_name}-missing-channel-digest.json"
    write_json(target, mutated)
    report = run_verifier(manual_args(inputs, {receipt_name: (target, sha256_pin(target))}))
    expect_failed_with(report, problem_prefix)


def check_policy_receipt(tempdir: Path) -> None:
    print("checking verification_policy_lockfile_receipt...", flush=True)
    mutated = remove_channel_digest_fields(load_json(ROOT / POLICY_RECEIPT))
    target = tempdir / "verification-policy-receipt-missing-channel-digest.json"
    write_json(target, mutated)
    report = run_verifier([
        str(PACKET),
        "--json",
        "--public",
        "--verification-policy-lockfile",
        str(POLICY),
        "--verification-policy-lockfile-sha256",
        sha256_pin(ROOT / POLICY),
        "--verification-policy-lockfile-receipt",
        str(target),
        "--verification-policy-lockfile-receipt-sha256",
        sha256_pin(target),
        "--require-verification-policy-lockfile-receipt",
        "--verification-time",
        VERIFICATION_TIME,
    ])
    expect_failed_with(report, POLICY_RECEIPT_PROBLEM)


def check_fixture_channels(inputs: Mapping[str, Tuple[Path, str]]) -> None:
    # Static fixture sanity: all checked receipt fixtures must carry explicit per-channel digest observations.
    all_receipts = list(RECEIPT_TARGETS) + ["verification_policy_lockfile_receipt"]
    for name in RECEIPT_TARGETS:
        path, _ = inputs[name]
        receipt = load_json(path)
        channels = receipt.get("publication_channels") or []
        if len(channels) < 2:
            fail(f"{name} has fewer than two publication channels")
        for idx, channel in enumerate(channels):
            digest_keys = [k for k in channel if k.startswith("observed_") and k.endswith("sha256")]
            if not digest_keys:
                fail(f"{name} channel {idx} has no explicit observed_*_sha256 field")
    policy_receipt = load_json(ROOT / POLICY_RECEIPT)
    top_digest_values = {str(policy_receipt.get(k) or "") for k in ("verification_policy_lockfile_sha256", "policy_lockfile_sha256", "policy_sha256") if str(policy_receipt.get(k) or "")}
    if len(top_digest_values) > 1:
        fail(f"policy receipt top-level digest aliases disagree: {sorted(top_digest_values)}")
    top_id_values = {str(policy_receipt.get(k) or "") for k in ("verification_policy_lockfile_id", "policy_lockfile_id", "policy_id") if str(policy_receipt.get(k) or "")}
    if len(top_id_values) > 1:
        fail(f"policy receipt top-level id aliases disagree: {sorted(top_id_values)}")
    for idx, channel in enumerate(policy_receipt.get("publication_channels") or []):
        digest_keys = [k for k in channel if k.startswith("observed_") and k.endswith("sha256")]
        if not digest_keys:
            fail(f"policy receipt channel {idx} has no explicit observed_*_sha256 field")
        digest_values = {str(channel.get(k) or "") for k in digest_keys if str(channel.get(k) or "")}
        if len(digest_values) > 1:
            fail(f"policy receipt channel {idx} observed digest aliases disagree: {sorted(digest_values)}")


def main() -> int:
    if not (ROOT / POLICY).exists() or not (ROOT / POLICY_RECEIPT).exists():
        fail(f"missing current rev{VERSION_NUM} policy or policy receipt fixture")
    inputs = fixture_paths()
    check_fixture_channels(inputs)
    print("checking positive manual path...", flush=True)
    positive = run_verifier(manual_args(inputs))
    if positive.get("status") != "PASS" or positive.get("authentication_status") != "SIGNATURE_VERIFIED":
        fail(f"manual positive trust-chain path failed: {positive.get('problems')}")
    with tempfile.TemporaryDirectory(prefix="tes-channel-digest-") as td:
        tempdir = Path(td)
        for receipt_name, problem_prefix in RECEIPT_TARGETS.items():
            check_manual_receipt_family(inputs, receipt_name, problem_prefix, tempdir)
        check_policy_receipt(tempdir)
    print("PASS: current publication receipt channel observed-digest fixtures, policy-receipt alias coherence, and fail-closed negative controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
