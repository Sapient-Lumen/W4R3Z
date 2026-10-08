#!/usr/bin/env python3
"""scripts/check_signature_verifier_ed25519.py

Regression check for the bounded Ed25519 authentication mode in
`tools/observer_verify_packet.py --trust-keyset` (alias: --auth-keyring).

This is not a production key-management test.  It proves the reference verifier
has real forward/fail-closed behavior for the minimum dangerous cases:
- known-good Ed25519-JCS-TBS signature -> SIGNATURE_VERIFIED
- caller-pinned trust-keyset sha256 -> match required before SIGNATURE_VERIFIED
- external keyset, governance-bundle, governance-bundle publication receipt, trust-status snapshot, and status-snapshot publication receipt can be required before SIGNATURE_VERIFIED
- strict-local-trust-chain-v1 and strict-local-authorized-trust-chain-v1 reject weak flag combinations that would otherwise verify only bytes/signatures
- threshold-2 keyset requires two distinct key materials, not repeated signatures
- tampered signature or wrong public key -> SIGNATURE_FAILED
- packet-contained/self-supplied trust keyset -> SIGNATURE_FAILED
- revoked/expired/disallowed-scope key -> SIGNATURE_FAILED
- retired-but-valid historical key -> SIGNATURE_VERIFIED
- --require-authentication without a trust keyset -> SIGNATURE_FAILED
- payload tamper after signature -> packet FAIL and authentication downgrades
  to SIGNATURE_FAILED (a valid envelope signature cannot rescue bad objects)
"""

from __future__ import annotations

import base64
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from _cli_harness import run_python_cli

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
ARCHIVE_VERSION_NUM = ARCHIVE_VERSION.removeprefix("v").zfill(4)
TOOLS = ROOT / "tools"
VERIFY_TOOL = TOOLS / "observer_verify_packet.py"
FIXTURE = ROOT / "artifacts" / "examples" / "evidence_packet_ed25519_signed_minimal"
TRUST_KEYSETS = ROOT / "artifacts" / "examples" / "trust_keysets"
TRUST_POLICIES = ROOT / "artifacts" / "examples" / "trust_policies"
KEYRING = TRUST_KEYSETS / "trust-keyset-ed25519-demo.json"
ROTATED_RETIRED_KEYRING = TRUST_KEYSETS / "trust-keyset-ed25519-demo-rotated-retired.json"
PACKET_CONTAINED_KEYRING = FIXTURE / "trust-keyset-ed25519-demo.json"
THRESHOLD_FIXTURE = ROOT / "artifacts" / "examples" / "evidence_packet_ed25519_threshold2_minimal"
THRESHOLD_KEYRING = TRUST_KEYSETS / "trust-keyset-ed25519-threshold2-demo.json"
THRESHOLD_RECEIPT = TRUST_KEYSETS / "trust-keyset-ed25519-threshold2-demo.publication-receipt.json"
GOVERNANCE_BUNDLE = TRUST_KEYSETS / "trust-key-governance-bundle-ed25519-threshold2-rev0845.json"
GOVERNANCE_BUNDLE_RECEIPT = TRUST_KEYSETS / "trust-key-governance-bundle-ed25519-threshold2-rev0845.publication-receipt.json"
STATUS_SNAPSHOT = TRUST_KEYSETS / "trust-status-snapshot-ed25519-threshold2-rev0847.json"
STATUS_SNAPSHOT_RECEIPT = TRUST_KEYSETS / "trust-status-snapshot-ed25519-threshold2-rev0852.publication-receipt.json"
SIGNER_AUTHORIZATION_ROSTER = TRUST_KEYSETS / "signer-authorization-roster-ed25519-threshold2-rev0852.json"
SIGNER_AUTHORIZATION_ROSTER_RECEIPT = TRUST_KEYSETS / "signer-authorization-roster-ed25519-threshold2-rev0852.publication-receipt.json"
VERIFICATION_POLICY_LOCKFILE = TRUST_POLICIES / f"verification-policy-lockfile-ed25519-authorized-threshold2-rev{ARCHIVE_VERSION_NUM}.json"
VERIFICATION_POLICY_LOCKFILE_RECEIPT = TRUST_POLICIES / f"verification-policy-lockfile-ed25519-authorized-threshold2-rev{ARCHIVE_VERSION_NUM}.publication-receipt.json"
FIXED_VERIFICATION_TIME = "2026-06-05T05:15:00Z"


def observer_report_version() -> str:
    text = VERIFY_TOOL.read_text(encoding="utf-8")
    import re
    m = re.search(r'^REPORT_VERSION\s*=\s*["\']([^"\']+)["\']', text, re.M)
    if not m:
        fail("could not read observer REPORT_VERSION")
    return m.group(1)


def public_fingerprint_profile_version() -> str:
    text = (TOOLS / "public_fingerprint_report.py").read_text(encoding="utf-8")
    import re
    m = re.search(r'^REPORT_FORMAT_VERSION\s*=\s*["\']([^"\']+)["\']', text, re.M)
    if not m:
        fail("could not read public fingerprint REPORT_FORMAT_VERSION")
    return m.group(1)


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_report(
    packet_dir: Path,
    keyring: Path,
    keyring_sha256: str = "",
    receipt: Path | None = None,
    require_receipt: bool = False,
    governance: Path | None = None,
    require_governance: bool = False,
    governance_sha256: str = "",
    governance_receipt: Path | None = None,
    require_governance_receipt: bool = False,
    governance_receipt_sha256: str = "",
    status_snapshot: Path | None = None,
    require_status_snapshot: bool = False,
    status_snapshot_sha256: str = "",
    status_snapshot_receipt: Path | None = None,
    require_status_snapshot_receipt: bool = False,
    status_snapshot_receipt_sha256: str = "",
    signer_authorization_roster: Path | None = None,
    require_signer_authorization_roster: bool = False,
    signer_authorization_roster_sha256: str = "",
    signer_authorization_roster_receipt: Path | None = None,
    require_signer_authorization_roster_receipt: bool = False,
    signer_authorization_roster_receipt_sha256: str = "",
    keyset_receipt_sha256: str = "",
    verification_time: str = FIXED_VERIFICATION_TIME,
    auth_profile: str = "",
) -> dict:
    args = [str(packet_dir), "--json", "--public", "--trust-keyset", str(keyring)]
    if keyring_sha256:
        args.extend(["--trust-keyset-sha256", keyring_sha256])
    if receipt is not None:
        args.extend(["--trust-keyset-receipt", str(receipt)])
    if keyset_receipt_sha256:
        args.extend(["--trust-keyset-receipt-sha256", keyset_receipt_sha256])
    if require_receipt:
        args.append("--require-trust-keyset-receipt")
    if governance is not None:
        args.extend(["--trust-governance-bundle", str(governance)])
    if governance_sha256:
        args.extend(["--trust-governance-bundle-sha256", governance_sha256])
    if require_governance:
        args.append("--require-trust-governance-bundle")
    if governance_receipt is not None:
        args.extend(["--trust-governance-bundle-receipt", str(governance_receipt)])
    if governance_receipt_sha256:
        args.extend(["--trust-governance-bundle-receipt-sha256", governance_receipt_sha256])
    if require_governance_receipt:
        args.append("--require-trust-governance-bundle-receipt")
    if status_snapshot is not None:
        args.extend(["--trust-status-snapshot", str(status_snapshot)])
    if status_snapshot_sha256:
        args.extend(["--trust-status-snapshot-sha256", status_snapshot_sha256])
    if require_status_snapshot:
        args.append("--require-trust-status-snapshot")
    if status_snapshot_receipt is not None:
        args.extend(["--trust-status-snapshot-receipt", str(status_snapshot_receipt)])
    if status_snapshot_receipt_sha256:
        args.extend(["--trust-status-snapshot-receipt-sha256", status_snapshot_receipt_sha256])
    if require_status_snapshot_receipt:
        args.append("--require-trust-status-snapshot-receipt")
    if signer_authorization_roster is not None:
        args.extend(["--signer-authorization-roster", str(signer_authorization_roster)])
    if signer_authorization_roster_sha256:
        args.extend(["--signer-authorization-roster-sha256", signer_authorization_roster_sha256])
    if require_signer_authorization_roster:
        args.append("--require-signer-authorization-roster")
    if signer_authorization_roster_receipt is not None:
        args.extend(["--signer-authorization-roster-receipt", str(signer_authorization_roster_receipt)])
    if signer_authorization_roster_receipt_sha256:
        args.extend(["--signer-authorization-roster-receipt-sha256", signer_authorization_roster_receipt_sha256])
    if require_signer_authorization_roster_receipt:
        args.append("--require-signer-authorization-roster-receipt")
    if verification_time:
        args.extend(["--verification-time", verification_time])
    if auth_profile:
        args.extend(["--auth-profile", auth_profile])
    code, out, err = run_python_cli(
        VERIFY_TOOL,
        args,
        extra_sys_path=[TOOLS, ROOT],
        cwd=ROOT,
    )
    try:
        obj = json.loads(out)
    except Exception as e:
        fail(f"could not parse verifier JSON (rc={code}): {e}; stdout={out!r}; stderr={err!r}")
    return obj


def require_code(report: dict, code: str) -> None:
    problems = [str(p).split(":", 1)[0] for p in report.get("problems", [])]
    if code not in problems:
        import inspect
        caller = inspect.stack()[1]
        fail(f"expected problem code {code!r} at line {caller.lineno}; got {report.get('problems')!r}")


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def mutate_receipt_remove_first_channel_digest(src: Path, dst: Path, field_names: tuple[str, ...]) -> None:
    """Remove per-channel digest observations while preserving top-level receipt digest.

    A receipt channel must carry the digest it observed. This negative control catches
    validators that silently inherit the receipt-level digest and treat an unbound
    channel as independent publication evidence.
    """

    obj = json.loads(src.read_text(encoding="utf-8"))
    for ch in obj.get("publication_channels", []):
        if isinstance(ch, dict):
            for field_name in field_names:
                ch.pop(field_name, None)
            break
    write_json(dst, obj)


def mutate_keyring_wrong_key(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    key = obj["keys"][0]
    raw = base64.urlsafe_b64decode(key["public_key"] + "=")
    mutated = bytes([raw[0] ^ 1]) + raw[1:]
    key["public_key"] = base64.urlsafe_b64encode(mutated).decode("ascii").rstrip("=")
    write_json(dst, obj)


def mutate_keyring_revoked(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["keys"][0]["status"] = "revoked"
    write_json(dst, obj)


def mutate_keyring_expired(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["keys"][0]["valid_to"] = "2026-02-20T23:59:59Z"
    write_json(dst, obj)


def mutate_keyring_disallowed_kind(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["keys"][0]["allowed_kinds"] = ["hfv.other.kind"]
    write_json(dst, obj)


def mutate_keyring_retired_after_issued_at(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["keys"][0]["status"] = "retired"
    obj["keys"][0]["retired_at"] = "2026-03-01T00:00:00Z"
    write_json(dst, obj)


def mutate_packet_signature(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst)
    env_path = dst / "envelopes" / "coverage_report_signed.envelope.json"
    env = json.loads(env_path.read_text(encoding="utf-8"))
    sig = env["signatures"][0]["sig"]
    env["signatures"][0]["sig"] = ("A" if sig[0] != "A" else "B") + sig[1:]
    write_json(env_path, env)


def run_require_auth_without_keyset(packet_dir: Path) -> dict:
    code, out, err = run_python_cli(
        VERIFY_TOOL,
        [str(packet_dir), "--json", "--public", "--require-authentication"],
        extra_sys_path=[TOOLS, ROOT],
        cwd=ROOT,
    )
    try:
        return json.loads(out)
    except Exception as e:
        fail(f"could not parse require-auth verifier JSON (rc={code}): {e}; stdout={out!r}; stderr={err!r}")


def run_policy_lockfile_report(
    packet_dir: Path,
    policy_lockfile: Path,
    policy_lockfile_sha256: str = "",
    policy_lockfile_receipt: Path | None = None,
    policy_lockfile_receipt_sha256: str = "",
    require_policy_lockfile_receipt: bool = False,
    extra_args: list[str] | None = None,
    verification_time: str = FIXED_VERIFICATION_TIME,
) -> dict:
    args = [
        str(packet_dir),
        "--json",
        "--public",
        "--verification-policy-lockfile",
        str(policy_lockfile),
    ]
    if policy_lockfile_sha256:
        args.extend(["--verification-policy-lockfile-sha256", policy_lockfile_sha256])
    if policy_lockfile_receipt is not None:
        args.extend(["--verification-policy-lockfile-receipt", str(policy_lockfile_receipt)])
    if policy_lockfile_receipt_sha256:
        args.extend(["--verification-policy-lockfile-receipt-sha256", policy_lockfile_receipt_sha256])
    if require_policy_lockfile_receipt:
        args.append("--require-verification-policy-lockfile-receipt")
    if verification_time:
        args.extend(["--verification-time", verification_time])
    if extra_args:
        args.extend(extra_args)
    code, out, err = run_python_cli(
        VERIFY_TOOL,
        args,
        extra_sys_path=[TOOLS, ROOT],
        cwd=ROOT,
    )
    try:
        return json.loads(out)
    except Exception as e:
        fail(f"could not parse policy-lockfile verifier JSON (rc={code}): {e}; stdout={out!r}; stderr={err!r}")


def mutate_packet_payload(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst)
    objects = sorted((dst / "objects").glob("sha256-*.json"))
    if not objects:
        fail("fixture has no payload object to tamper")
    # Keep the filename the same but alter bytes.  This must trip object/payload
    # integrity and must also prevent authentication_status=SIGNATURE_VERIFIED.
    obj_path = objects[0]
    payload = json.loads(obj_path.read_text(encoding="utf-8"))
    payload["notes"] = "tampered-after-signature"
    write_json(obj_path, payload)


def mutate_threshold_packet_single_signature(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst)
    env_path = dst / "envelopes" / "coverage_report_threshold2.envelope.json"
    env = json.loads(env_path.read_text(encoding="utf-8"))
    env["signatures"] = [env["signatures"][0], dict(env["signatures"][0])]
    # Repeating the same key/signature must not satisfy a distinct-key-material threshold.
    write_json(env_path, env)


def mutate_receipt_digest(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["trust_keyset_sha256"] = "sha256:" + ("0" * 64)
    for ch in obj.get("publication_channels", []):
        if isinstance(ch, dict):
            ch["observed_trust_keyset_sha256"] = obj["trust_keyset_sha256"]
    write_json(dst, obj)


def mutate_receipt_single_channel(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["publication_channels"] = obj.get("publication_channels", [])[:1]
    write_json(dst, obj)


def mutate_receipt_same_channel_type(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    channels = obj.get("publication_channels", [])
    if len(channels) < 2 or not all(isinstance(ch, dict) for ch in channels[:2]):
        fail(f"receipt fixture lacks two publication channels: {src}")
    first_type = str(channels[0].get("channel_type") or "same_type_channel").strip() or "same_type_channel"
    channels[1]["channel_type"] = first_type
    channels[1]["channel_id"] = str(channels[1].get("channel_id") or "channel-2") + "-same-type"
    # Keep the route different so this exercises type diversity, not duplicate-route detection.
    if "locator_ref" in channels[1]:
        channels[1]["locator_ref"] = str(channels[1].get("locator_ref") or "synthetic://same-type") + "/same-type"
    write_json(dst, obj)


def mutate_receipt_duplicate_route(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    channels = obj.get("publication_channels", [])
    if len(channels) < 2 or not all(isinstance(ch, dict) for ch in channels[:2]):
        fail(f"receipt fixture lacks two publication channels: {src}")
    channels[1]["channel_id"] = str(channels[1].get("channel_id") or "channel-2") + "-duplicate-route"
    channels[1]["locator_ref"] = str(channels[0].get("locator_ref") or "synthetic://duplicate-route")
    write_json(dst, obj)


def mutate_governance_bundle_receipt_digest(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["trust_governance_bundle_sha256"] = "sha256:" + ("5" * 64)
    for ch in obj.get("publication_channels", []):
        if isinstance(ch, dict):
            ch["observed_trust_governance_bundle_sha256"] = obj["trust_governance_bundle_sha256"]
    write_json(dst, obj)


def mutate_governance_bundle_receipt_single_channel(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["publication_channels"] = obj.get("publication_channels", [])[:1]
    write_json(dst, obj)


def mutate_governance_keyset_digest(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["trust_keyset_sha256"] = "sha256:" + ("2" * 64)
    write_json(dst, obj)


def mutate_governance_receipt_digest(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["publication_receipt_sha256"] = "sha256:" + ("3" * 64)
    write_json(dst, obj)


def mutate_governance_single_witness(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj.setdefault("key_ceremony", {})["witnesses"] = obj.get("key_ceremony", {}).get("witnesses", [])[:1]
    write_json(dst, obj)


def mutate_governance_stale(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["status"] = "superseded"
    obj["superseded_by"] = "SYNTH-GOV-BUNDLE-0844-THRESHOLD2-002"
    write_json(dst, obj)


def mutate_governance_remove_activation_event(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["key_events"] = [e for e in obj.get("key_events", []) if e.get("kid") != "example-ed25519-q1"]
    write_json(dst, obj)


def mutate_governance_remove_rotation_event(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["key_events"] = [e for e in obj.get("key_events", []) if str(e.get("event_type") or "").lower() not in {"revoked", "retired", "rotated", "rotation", "revocation", "replaced"}]
    write_json(dst, obj)


def mutate_status_snapshot_keyset_digest(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["trust_keyset_sha256"] = "sha256:" + ("7" * 64)
    write_json(dst, obj)


def mutate_status_snapshot_governance_digest(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["trust_governance_bundle_sha256"] = "sha256:" + ("8" * 64)
    write_json(dst, obj)


def mutate_status_snapshot_stale(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["next_update"] = "2026-06-04T11:00:00Z"
    write_json(dst, obj)


def mutate_status_snapshot_revoke_active_key(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    for row in obj.get("key_statuses", []):
        if isinstance(row, dict) and row.get("kid") == "example-ed25519-q1":
            row["status"] = "revoked"
            row["status_reason"] = "negative-control active signer revoked"
    write_json(dst, obj)


def mutate_status_snapshot_remove_key(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["key_statuses"] = [row for row in obj.get("key_statuses", []) if not (isinstance(row, dict) and row.get("kid") == "example-ed25519-q2")]
    write_json(dst, obj)


def mutate_status_snapshot_single_authority(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["status_authorities"] = obj.get("status_authorities", [])[:1]
    write_json(dst, obj)


def mutate_status_snapshot_receipt_digest(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["trust_status_snapshot_sha256"] = "sha256:" + ("7" * 64)
    for ch in obj.get("publication_channels", []):
        if isinstance(ch, dict):
            ch["observed_trust_status_snapshot_sha256"] = obj["trust_status_snapshot_sha256"]
    write_json(dst, obj)


def mutate_status_snapshot_receipt_single_channel(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["publication_channels"] = obj.get("publication_channels", [])[:1]
    obj["minimum_independent_channels"] = 2
    write_json(dst, obj)


def mutate_status_snapshot_receipt_validity(src: Path, dst: Path, *, valid_from: str | None = None, valid_until: str | None = None, remove: bool = False) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    if remove:
        obj.pop("valid_from", None)
        obj.pop("valid_until", None)
    if valid_from is not None:
        obj["valid_from"] = valid_from
    if valid_until is not None:
        obj["valid_until"] = valid_until
    write_json(dst, obj)


def mutate_status_snapshot_receipt_predates_snapshot(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["issued_at"] = "2026-06-04T12:39:30Z"
    for offset, ch in enumerate(obj.get("publication_channels", [])):
        if isinstance(ch, dict):
            ch["published_at"] = f"2026-06-04T12:3{8 + offset}:00Z"
            ch["observed_at"] = ch["published_at"]
    write_json(dst, obj)


def mutate_status_snapshot_receipt_issued_before_latest_channel(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["issued_at"] = "2026-06-04T12:45:30Z"
    channels = obj.get("publication_channels", [])
    if len(channels) >= 2 and isinstance(channels[1], dict):
        channels[1]["published_at"] = "2026-06-04T12:46:00Z"
        channels[1]["observed_at"] = channels[1]["published_at"]
    write_json(dst, obj)


def mutate_status_snapshot_receipt_future_channel(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    for ch in obj.get("publication_channels", []):
        if isinstance(ch, dict):
            ch["published_at"] = "2026-06-05T06:00:00Z"
            ch["observed_at"] = ch["published_at"]
            break
    write_json(dst, obj)


def mutate_policy_lockfile_receipt_digest(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["verification_policy_lockfile_sha256"] = "sha256:" + ("7" * 64)
    for ch in obj.get("publication_channels", []):
        if isinstance(ch, dict):
            ch["observed_verification_policy_lockfile_sha256"] = obj["verification_policy_lockfile_sha256"]
    write_json(dst, obj)


def mutate_policy_lockfile_receipt_policy_id(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["verification_policy_lockfile_id"] = "SYNTH-OTHER-POLICY-ID"
    write_json(dst, obj)


def mutate_policy_lockfile_receipt_selector(src: Path, dst: Path, **changes: str) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    selector = obj.setdefault("packet_selector", {})
    for key, value in changes.items():
        if value == "__DELETE__":
            selector.pop(key, None)
        else:
            selector[key] = value
    write_json(dst, obj)


def mutate_policy_lockfile_receipt_single_channel(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["publication_channels"] = obj.get("publication_channels", [])[:1]
    obj["minimum_independent_channels"] = 2
    write_json(dst, obj)


def mutate_policy_lockfile_receipt_validity(src: Path, dst: Path, *, valid_from: str | None = None, valid_until: str | None = None, remove: bool = False) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    if remove:
        obj.pop("valid_from", None)
        obj.pop("valid_until", None)
    if valid_from is not None:
        obj["valid_from"] = valid_from
    if valid_until is not None:
        obj["valid_until"] = valid_until
    write_json(dst, obj)


def mutate_policy_lockfile_receipt_future_channel(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    for ch in obj.get("publication_channels", []):
        if isinstance(ch, dict):
            ch["published_at"] = "2026-06-12T00:00:00Z"
            ch["observed_at"] = ch["published_at"]
            break
    write_json(dst, obj)


def mutate_policy_lockfile_receipt_predates_policy(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["issued_at"] = "2026-06-04T20:39:00Z"
    for offset, ch in enumerate(obj.get("publication_channels", [])):
        if isinstance(ch, dict):
            ch["published_at"] = f"2026-06-04T20:3{7 + offset}:00Z"
            ch["observed_at"] = ch["published_at"]
    write_json(dst, obj)


def mutate_policy_lockfile_receipt_issued_before_latest_channel(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["issued_at"] = "2026-06-04T20:42:30Z"
    channels = obj.get("publication_channels", [])
    if len(channels) >= 2 and isinstance(channels[1], dict):
        channels[1]["published_at"] = "2026-06-04T20:44:00Z"
        channels[1]["observed_at"] = channels[1]["published_at"]
    write_json(dst, obj)


def mutate_signer_authorization_keyset_digest(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["trust_keyset_sha256"] = "sha256:" + ("a" * 64)
    write_json(dst, obj)


def mutate_signer_authorization_status_digest(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["trust_status_snapshot_sha256"] = "sha256:" + ("b" * 64)
    write_json(dst, obj)


def mutate_signer_authorization_single_authority(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["authorities"] = obj.get("authorities", [])[:1]
    obj["minimum_authorities"] = 2
    write_json(dst, obj)


def mutate_signer_authorization_remove_key(src: Path, dst: Path, kid: str = "example-ed25519-q2") -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["authorizations"] = [row for row in obj.get("authorizations", []) if not (isinstance(row, dict) and row.get("kid") == kid)]
    write_json(dst, obj)


def mutate_signer_authorization_disallowed_kind(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    for row in obj.get("authorizations", []):
        if isinstance(row, dict) and row.get("kid") == "example-ed25519-q1":
            row["authorized_kinds"] = ["hfv.other.kind"]
    write_json(dst, obj)


def mutate_signer_authorization_expired(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    for row in obj.get("authorizations", []):
        if isinstance(row, dict) and row.get("kid") == "example-ed25519-q1":
            row["authorized_until"] = "2026-02-20T23:59:59Z"
    write_json(dst, obj)


def mutate_signer_authorization_public_key(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    for row in obj.get("authorizations", []):
        if isinstance(row, dict) and row.get("kid") == "example-ed25519-q1":
            row["public_key_sha256"] = "sha256:" + ("c" * 64)
    write_json(dst, obj)


def mutate_signer_authorization_remove_roster_window(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj.pop("valid_from", None)
    obj.pop("valid_until", None)
    write_json(dst, obj)


def mutate_signer_authorization_future_roster(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["issued_at"] = "2026-06-05T06:00:00Z"
    write_json(dst, obj)


def mutate_signer_authorization_expired_roster_window(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["valid_until"] = "2026-06-04T20:49:00Z"
    write_json(dst, obj)


def mutate_signer_authorization_future_authority_observation(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    for auth in obj.get("authorities", []):
        if isinstance(auth, dict):
            auth["observed_at"] = "2026-06-04T20:41:30Z"
            break
    write_json(dst, obj)


def mutate_signer_authorization_remove_row_window(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    for row in obj.get("authorizations", []):
        if isinstance(row, dict) and row.get("kid") == "example-ed25519-q1":
            row.pop("authorized_from", None)
            row.pop("authorized_until", None)
            break
    write_json(dst, obj)


def mutate_signer_authorization_roster_receipt_digest(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["signer_authorization_roster_sha256"] = "sha256:" + ("4" * 64)
    for ch in obj.get("publication_channels", []):
        if isinstance(ch, dict):
            ch["observed_signer_authorization_roster_sha256"] = obj["signer_authorization_roster_sha256"]
    write_json(dst, obj)


def mutate_signer_authorization_roster_receipt_single_channel(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["publication_channels"] = obj.get("publication_channels", [])[:1]
    obj["minimum_independent_channels"] = 2
    write_json(dst, obj)

def mutate_signer_authorization_roster_receipt_roster_id(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["signer_authorization_roster_id"] = "WRONG-ROSTER-ID"
    write_json(dst, obj)


def mutate_signer_authorization_roster_receipt_roster_issued_at(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["signer_authorization_roster_issued_at"] = "2026-06-04T19:41:00Z"
    write_json(dst, obj)


def mutate_signer_authorization_roster_receipt_predates_roster(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["issued_at"] = "2026-06-04T20:39:00Z"
    for offset, ch in enumerate(obj.get("publication_channels", [])):
        if isinstance(ch, dict):
            ch["published_at"] = f"2026-06-04T20:3{7 + offset}:00Z"
            ch["observed_at"] = ch["published_at"]
    write_json(dst, obj)


def mutate_signer_authorization_roster_receipt_issued_before_latest_channel(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["issued_at"] = "2026-06-04T20:45:30Z"
    channels = obj.get("publication_channels", [])
    if len(channels) >= 2 and isinstance(channels[1], dict):
        channels[1]["published_at"] = "2026-06-04T20:47:00Z"
        channels[1]["observed_at"] = channels[1]["published_at"]
    write_json(dst, obj)


def mutate_signer_authorization_roster_receipt_expired_window(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj["valid_until"] = "2026-06-05T01:00:00Z"
    write_json(dst, obj)


def mutate_signer_authorization_roster_receipt_future_channel(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    for ch in obj.get("publication_channels", []):
        if isinstance(ch, dict):
            ch["published_at"] = "2026-06-05T06:00:00Z"
            ch["observed_at"] = ch["published_at"]
            break
    write_json(dst, obj)


def write_matching_signer_authorization_roster_receipt(base_receipt: Path, roster_path: Path, dst: Path) -> None:
    obj = json.loads(base_receipt.read_text(encoding="utf-8"))
    digest = "sha256:" + sha256_file(roster_path)
    obj["signer_authorization_roster_sha256"] = digest
    for ch in obj.get("publication_channels", []):
        if isinstance(ch, dict):
            ch["observed_signer_authorization_roster_sha256"] = digest
    write_json(dst, obj)


def write_matching_policy_lockfile_receipt(base_receipt: Path, policy_path: Path, dst: Path) -> None:
    obj = json.loads(base_receipt.read_text(encoding="utf-8"))
    policy_obj = json.loads(policy_path.read_text(encoding="utf-8"))
    digest = "sha256:" + sha256_file(policy_path)
    obj["verification_policy_lockfile_sha256"] = digest
    obj["verification_policy_lockfile_id"] = str(policy_obj.get("policy_id") or "")
    if isinstance(policy_obj.get("packet_selector"), dict):
        obj["packet_selector"] = dict(policy_obj["packet_selector"])
    if policy_obj.get("packet_public_fingerprint_sha256"):
        obj["packet_public_fingerprint_sha256"] = str(policy_obj.get("packet_public_fingerprint_sha256"))
    if policy_obj.get("packet_public_fingerprint_profile"):
        obj["packet_public_fingerprint_profile"] = str(policy_obj.get("packet_public_fingerprint_profile"))
    # Keep receipt time after the default policy issue time unless a test mutates the receipt itself.
    obj["issued_at"] = "2026-06-05T02:43:30Z"
    obj["valid_from"] = "2026-06-05T02:00:00Z"
    obj["valid_until"] = "2026-06-12T23:59:59Z"
    for i, ch in enumerate(obj.get("publication_channels", [])):
        if isinstance(ch, dict):
            ch["observed_verification_policy_lockfile_sha256"] = digest
            ch["published_at"] = "2026-06-05T02:41:00Z" if i == 0 else "2026-06-05T02:42:00Z"
            ch["observed_at"] = ch["published_at"]
    write_json(dst, obj)


def mutate_policy_lockfile_input_path(src: Path, dst: Path, input_name: str, replacement_path: str) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj.setdefault("trust_inputs", {}).setdefault(input_name, {})["path"] = replacement_path
    write_json(dst, obj)


def mutate_policy_lockfile_remove_base_dir(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj.pop("trust_input_base_dir", None)
    write_json(dst, obj)


def mutate_policy_lockfile_add_unknown_trust_input(src: Path, dst: Path) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    obj.setdefault("trust_inputs", {})["trust_keyset_shadow_route"] = {
        "path": "trust-keyset-ed25519-threshold2-demo.json",
        "sha256": "sha256:" + ("1" * 64),
        "required": True,
    }
    write_json(dst, obj)


def mutate_policy_lockfile_verifier_requirements(
    src: Path,
    dst: Path,
    *,
    archive_version: str | None = None,
    report_version: str | None = None,
    auth_profile: str | None = None,
    remove: bool = False,
) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    if remove:
        obj.pop("verifier_requirements", None)
    else:
        req = obj.setdefault("verifier_requirements", {})
        if archive_version is not None:
            req["archive_version"] = archive_version
        if report_version is not None:
            req["packet_verification_report_version"] = report_version
        if auth_profile is not None:
            req["auth_profile"] = auth_profile
    write_json(dst, obj)


def mutate_policy_lockfile_validity(src: Path, dst: Path, *, valid_from: str | None = None, valid_until: str | None = None, verification_time: str | None = None, remove: bool = False) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    if remove:
        obj.pop("valid_from", None)
        obj.pop("valid_until", None)
    if valid_from is not None:
        obj["valid_from"] = valid_from
    if valid_until is not None:
        obj["valid_until"] = valid_until
    if verification_time is not None:
        obj["verification_time"] = verification_time
    write_json(dst, obj)


def mutate_policy_lockfile_selector(src: Path, dst: Path, **changes: str) -> None:
    obj = json.loads(src.read_text(encoding="utf-8"))
    selector = obj.setdefault("packet_selector", {})
    for key, value in changes.items():
        if value == "__DELETE__":
            selector.pop(key, None)
        else:
            selector[key] = value
    write_json(dst, obj)


def mutate_packet_manifest_scope(src_packet: Path, dst_packet: Path, *, election_id: str | None = None, jurisdiction: str | None = None, ambiguous: bool = False) -> None:
    shutil.copytree(src_packet, dst_packet)
    mpath = dst_packet / "manifest.json"
    obj = json.loads(mpath.read_text(encoding="utf-8"))
    if election_id is not None:
        if ambiguous:
            obj.setdefault("scope", {})["election_id"] = election_id
        else:
            obj["election_id"] = election_id
    if jurisdiction is not None:
        if ambiguous:
            obj.setdefault("scope", {})["jurisdiction"] = jurisdiction
        else:
            obj["jurisdiction"] = jurisdiction
    write_json(mpath, obj)


def main() -> int:
    if not VERIFY_TOOL.exists():
        fail(f"missing verifier tool: {VERIFY_TOOL}")
    if not FIXTURE.exists():
        fail(f"missing signed fixture packet: {FIXTURE}")
    if not KEYRING.exists():
        fail(f"missing external signed fixture keyring: {KEYRING}")
    if not PACKET_CONTAINED_KEYRING.exists():
        fail(f"missing packet-contained negative-control keyring: {PACKET_CONTAINED_KEYRING}")
    if not THRESHOLD_FIXTURE.exists():
        fail(f"missing threshold fixture packet: {THRESHOLD_FIXTURE}")
    if not THRESHOLD_KEYRING.exists():
        fail(f"missing threshold fixture keyring: {THRESHOLD_KEYRING}")
    if not THRESHOLD_RECEIPT.exists():
        fail(f"missing threshold fixture receipt: {THRESHOLD_RECEIPT}")
    if not GOVERNANCE_BUNDLE.exists():
        fail(f"missing threshold fixture governance bundle: {GOVERNANCE_BUNDLE}")
    if not GOVERNANCE_BUNDLE_RECEIPT.exists():
        fail(f"missing threshold fixture governance-bundle publication receipt: {GOVERNANCE_BUNDLE_RECEIPT}")
    if not STATUS_SNAPSHOT.exists():
        fail(f"missing threshold fixture trust-status snapshot: {STATUS_SNAPSHOT}")
    if not STATUS_SNAPSHOT_RECEIPT.exists():
        fail(f"missing threshold fixture trust-status snapshot publication receipt: {STATUS_SNAPSHOT_RECEIPT}")
    if not SIGNER_AUTHORIZATION_ROSTER.exists():
        fail(f"missing threshold fixture signer-authorization roster: {SIGNER_AUTHORIZATION_ROSTER}")
    if not SIGNER_AUTHORIZATION_ROSTER_RECEIPT.exists():
        fail(f"missing threshold fixture signer-authorization roster publication receipt: {SIGNER_AUTHORIZATION_ROSTER_RECEIPT}")
    if not VERIFICATION_POLICY_LOCKFILE.exists():
        fail(f"missing threshold fixture verification policy lockfile: {VERIFICATION_POLICY_LOCKFILE}")
    if not VERIFICATION_POLICY_LOCKFILE_RECEIPT.exists():
        fail(f"missing threshold fixture verification policy lockfile receipt: {VERIFICATION_POLICY_LOCKFILE_RECEIPT}")

    self_supplied = run_report(FIXTURE, PACKET_CONTAINED_KEYRING)
    if self_supplied.get("authentication_status") != "SIGNATURE_FAILED":
        fail(f"packet-contained keyset should fail; got {self_supplied.get('authentication_status')!r}")
    require_code(self_supplied, "signature_trust_keyset_untrusted_location")
    sv_self = self_supplied.get("signature_verification")
    if not isinstance(sv_self, dict) or sv_self.get("trust_keyset_location") != "packet_contained_rejected":
        fail("packet-contained keyset failure did not publish trust_keyset_location=packet_contained_rejected")

    positive = run_report(FIXTURE, KEYRING)
    if positive.get("status") != "PASS":
        fail(f"positive fixture status mismatch: {positive.get('status')!r}; problems={positive.get('problems')!r}")
    if positive.get("authentication_status") != "SIGNATURE_VERIFIED":
        fail(f"positive fixture authn mismatch: {positive.get('authentication_status')!r}")
    sv = positive.get("signature_verification")
    if not isinstance(sv, dict) or int(sv.get("trusted_signatures_valid") or 0) < 1:
        fail("positive fixture missing valid signature summary")
    if positive.get("signature_envelopes_checked") != 1 or positive.get("signature_envelopes_verified") != 1:
        fail("positive fixture missing envelope authentication counters")
    if positive.get("trusted_signatures_checked") != 1 or positive.get("trusted_signatures_valid") != 1:
        fail("positive fixture missing trusted-signature counters")
    if not str(positive.get("trust_keyset_sha256") or "").startswith("sha256:"):
        fail("positive fixture missing trust_keyset_sha256")
    if positive.get("signature_verification", {}).get("trust_keyset_location") != "external_to_packet":
        fail("positive fixture did not record trust_keyset_location=external_to_packet")

    expected_keyring_pin = "sha256:" + sha256_file(KEYRING)
    pinned_positive = run_report(FIXTURE, KEYRING, expected_keyring_pin)
    if pinned_positive.get("authentication_status") != "SIGNATURE_VERIFIED":
        fail(f"pinned positive fixture authn mismatch: {pinned_positive.get('authentication_status')!r}; problems={pinned_positive.get('problems')!r}")
    pinned_sv = pinned_positive.get("signature_verification", {})
    if pinned_sv.get("trust_keyset_pin_status") != "matched":
        fail(f"expected matched trust-keyset pin; got {pinned_sv.get('trust_keyset_pin_status')!r}")
    if pinned_sv.get("trust_keyset_pin_sha256") != expected_keyring_pin:
        fail("pinned positive fixture did not echo expected trust-keyset pin")

    expected_threshold_pin = "sha256:" + sha256_file(THRESHOLD_KEYRING)
    expected_keyset_receipt_pin = "sha256:" + sha256_file(THRESHOLD_RECEIPT)
    expected_governance_pin = "sha256:" + sha256_file(GOVERNANCE_BUNDLE)
    expected_governance_receipt_pin = "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT)
    expected_status_snapshot_pin = "sha256:" + sha256_file(STATUS_SNAPSHOT)
    expected_status_snapshot_receipt_pin = "sha256:" + sha256_file(STATUS_SNAPSHOT_RECEIPT)
    expected_signer_authorization_roster_pin = "sha256:" + sha256_file(SIGNER_AUTHORIZATION_ROSTER)
    expected_signer_authorization_roster_receipt_pin = "sha256:" + sha256_file(SIGNER_AUTHORIZATION_ROSTER_RECEIPT)
    expected_verification_policy_lockfile_pin = "sha256:" + sha256_file(VERIFICATION_POLICY_LOCKFILE)
    expected_verification_policy_lockfile_receipt_pin = "sha256:" + sha256_file(VERIFICATION_POLICY_LOCKFILE_RECEIPT)

    def run_strict_authorized(
        roster: Path | None = SIGNER_AUTHORIZATION_ROSTER,
        roster_pin: str = expected_signer_authorization_roster_pin,
        roster_receipt: Path | None = SIGNER_AUTHORIZATION_ROSTER_RECEIPT,
        roster_receipt_pin: str = expected_signer_authorization_roster_receipt_pin,
        auth_profile: str = "strict-local-authorized-trust-chain-v1",
        packet_dir: Path = THRESHOLD_FIXTURE,
    ) -> dict:
        return run_report(
            packet_dir,
            THRESHOLD_KEYRING,
            expected_threshold_pin,
            THRESHOLD_RECEIPT,
            False,
            GOVERNANCE_BUNDLE,
            False,
            expected_governance_pin,
            GOVERNANCE_BUNDLE_RECEIPT,
            False,
            expected_governance_receipt_pin,
            STATUS_SNAPSHOT,
            False,
            expected_status_snapshot_pin,
            STATUS_SNAPSHOT_RECEIPT,
            False,
            expected_status_snapshot_receipt_pin,
            keyset_receipt_sha256=expected_keyset_receipt_pin,
            auth_profile=auth_profile,
            signer_authorization_roster=roster,
            signer_authorization_roster_sha256=roster_pin,
            signer_authorization_roster_receipt=roster_receipt,
            signer_authorization_roster_receipt_sha256=roster_receipt_pin,
        )

    def run_roster_temporal_check(
        roster: Path,
        roster_pin: str,
        packet_dir: Path = THRESHOLD_FIXTURE,
    ) -> dict:
        # Isolate signer-authorization roster temporal validation from the
        # separate roster-publication-receipt digest gate. Strict profile tests
        # below still prove the receipt gate; this helper ensures stale/future
        # roster evidence fails for its own reason.
        return run_report(
            packet_dir,
            THRESHOLD_KEYRING,
            expected_threshold_pin,
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            expected_governance_pin,
            GOVERNANCE_BUNDLE_RECEIPT,
            True,
            expected_governance_receipt_pin,
            STATUS_SNAPSHOT,
            True,
            expected_status_snapshot_pin,
            STATUS_SNAPSHOT_RECEIPT,
            True,
            expected_status_snapshot_receipt_pin,
            keyset_receipt_sha256=expected_keyset_receipt_pin,
            signer_authorization_roster=roster,
            require_signer_authorization_roster=True,
            signer_authorization_roster_sha256=roster_pin,
        )

    threshold_positive = run_report(
        THRESHOLD_FIXTURE,
        THRESHOLD_KEYRING,
        expected_threshold_pin,
        THRESHOLD_RECEIPT,
        True,
        GOVERNANCE_BUNDLE,
        True,
        expected_governance_pin,
        GOVERNANCE_BUNDLE_RECEIPT,
        True,
        expected_governance_receipt_pin,
        STATUS_SNAPSHOT,
        True,
        expected_status_snapshot_pin,
        STATUS_SNAPSHOT_RECEIPT,
        True,
        expected_status_snapshot_receipt_pin,
        keyset_receipt_sha256=expected_keyset_receipt_pin,
    )
    if threshold_positive.get("status") != "PASS" or threshold_positive.get("authentication_status") != "SIGNATURE_VERIFIED":
        fail(f"threshold positive fixture failed: status={threshold_positive.get('status')!r}; auth={threshold_positive.get('authentication_status')!r}; problems={threshold_positive.get('problems')!r}")
    threshold_sv = threshold_positive.get("signature_verification", {})
    if threshold_positive.get("signature_threshold") != 2:
        fail(f"threshold fixture did not publish signature_threshold=2: {threshold_positive.get('signature_threshold')!r}")
    if threshold_sv.get("trust_keyset_receipt_status") != "matched":
        fail(f"threshold fixture receipt did not match: {threshold_sv.get('trust_keyset_receipt_status')!r}")
    if threshold_sv.get("trust_governance_bundle_status") != "matched":
        fail(f"threshold fixture governance bundle did not match: {threshold_sv.get('trust_governance_bundle_status')!r}; problems={threshold_positive.get('problems')!r}")
    if threshold_sv.get("trust_governance_bundle_pin_status") != "matched":
        fail("threshold fixture governance-bundle pin did not match")
    if threshold_sv.get("trust_governance_bundle_receipt_status") != "matched":
        fail(f"threshold fixture governance-bundle publication receipt did not match: {threshold_sv.get('trust_governance_bundle_receipt_status')!r}; problems={threshold_positive.get('problems')!r}")
    if threshold_sv.get("trust_governance_bundle_receipt_pin_status") != "matched":
        fail("threshold fixture governance-bundle receipt pin did not match")
    if int(threshold_sv.get("trust_governance_bundle_receipt_independent_channel_count") or 0) < 2:
        fail("threshold fixture governance-bundle receipt did not publish independent_channel_count>=2")
    if threshold_sv.get("trust_status_snapshot_status") != "matched":
        fail(f"threshold fixture trust-status snapshot did not match: {threshold_sv.get('trust_status_snapshot_status')!r}; problems={threshold_positive.get('problems')!r}")
    if threshold_sv.get("trust_status_snapshot_pin_status") != "matched":
        fail("threshold fixture trust-status snapshot pin did not match")
    if int(threshold_sv.get("trust_status_snapshot_authority_count") or 0) < 2:
        fail("threshold fixture trust-status snapshot did not publish authority_count>=2")
    if int(threshold_sv.get("trust_status_snapshot_key_status_count") or 0) < 2:
        fail("threshold fixture trust-status snapshot did not publish key_status_count>=2")
    if threshold_sv.get("trust_status_snapshot_receipt_status") != "matched":
        fail(f"threshold fixture trust-status snapshot publication receipt did not match: {threshold_sv.get('trust_status_snapshot_receipt_status')!r}; problems={threshold_positive.get('problems')!r}")
    if threshold_sv.get("trust_status_snapshot_receipt_pin_status") != "matched":
        fail("threshold fixture trust-status snapshot publication-receipt pin did not match")
    if int(threshold_sv.get("trust_status_snapshot_receipt_independent_channel_count") or 0) < 2:
        fail("threshold fixture trust-status snapshot publication receipt did not publish independent_channel_count>=2")
    if threshold_sv.get("trust_status_snapshot_receipt_validity_status") != "within_window":
        fail(f"trust-status snapshot publication receipt validity window did not match: {threshold_sv!r}")
    if threshold_sv.get("trust_status_snapshot_receipt_channel_time_status") != "within_window":
        fail(f"trust-status snapshot publication receipt channel times did not match: {threshold_sv!r}")
    if threshold_sv.get("trust_status_snapshot_receipt_temporal_status") != "coherent":
        fail(f"trust-status snapshot publication receipt temporal order did not cohere: {threshold_sv!r}")

    missing_status_time = run_report(
        THRESHOLD_FIXTURE,
        THRESHOLD_KEYRING,
        expected_threshold_pin,
        THRESHOLD_RECEIPT,
        True,
        GOVERNANCE_BUNDLE,
        True,
        expected_governance_pin,
        GOVERNANCE_BUNDLE_RECEIPT,
        True,
        expected_governance_receipt_pin,
        STATUS_SNAPSHOT,
        True,
        expected_status_snapshot_pin,
        STATUS_SNAPSHOT_RECEIPT,
        True,
        expected_status_snapshot_receipt_pin,
        keyset_receipt_sha256=expected_keyset_receipt_pin,
        verification_time="",
    )
    if missing_status_time.get("authentication_status") != "SIGNATURE_FAILED":
        fail("trust-status snapshot without explicit verification time should fail")
    missing_status_time_sv = missing_status_time.get("signature_verification", {})
    if missing_status_time_sv.get("failure_reason") != "trust_status_snapshot_verification_time_required":
        fail(f"trust-status snapshot without verification time should expose deterministic failure_reason; got {missing_status_time_sv.get('failure_reason')!r}")
    require_code(missing_status_time, "signature_trust_status_snapshot_invalid")

    if int(threshold_sv.get("trust_governance_witness_count") or 0) < 3:
        fail("threshold fixture governance bundle did not publish witness_count>=3")
    if int(threshold_sv.get("trust_governance_rotation_or_revocation_event_count") or 0) < 1:
        fail("threshold fixture governance bundle did not publish a rotation/revocation event count")
    envs = threshold_sv.get("envelopes") or []
    if not envs or envs[0].get("distinct_valid_key_count") != 2:
        fail(f"threshold fixture did not publish distinct_valid_key_count=2: {envs!r}")

    strict_positive = run_report(
        THRESHOLD_FIXTURE,
        THRESHOLD_KEYRING,
        expected_threshold_pin,
        THRESHOLD_RECEIPT,
        False,
        GOVERNANCE_BUNDLE,
        False,
        expected_governance_pin,
        GOVERNANCE_BUNDLE_RECEIPT,
        False,
        expected_governance_receipt_pin,
        STATUS_SNAPSHOT,
        False,
        expected_status_snapshot_pin,
        STATUS_SNAPSHOT_RECEIPT,
        False,
        expected_status_snapshot_receipt_pin,
        keyset_receipt_sha256=expected_keyset_receipt_pin,
        auth_profile="strict-local-trust-chain-v1",
    )
    if strict_positive.get("authentication_status") != "SIGNATURE_VERIFIED":
        fail(f"strict auth profile positive path failed: {strict_positive.get('problems')!r}")
    strict_sv = strict_positive.get("signature_verification", {})
    if strict_sv.get("auth_profile_status") != "requirements_met":
        fail(f"strict auth profile did not publish requirements_met: {strict_sv!r}")

    strict_authorized_positive = run_report(
        THRESHOLD_FIXTURE,
        THRESHOLD_KEYRING,
        expected_threshold_pin,
        THRESHOLD_RECEIPT,
        False,
        GOVERNANCE_BUNDLE,
        False,
        expected_governance_pin,
        GOVERNANCE_BUNDLE_RECEIPT,
        False,
        expected_governance_receipt_pin,
        STATUS_SNAPSHOT,
        False,
        expected_status_snapshot_pin,
        STATUS_SNAPSHOT_RECEIPT,
        False,
        expected_status_snapshot_receipt_pin,
        keyset_receipt_sha256=expected_keyset_receipt_pin,
        auth_profile="strict-local-authorized-trust-chain-v1",
        signer_authorization_roster=SIGNER_AUTHORIZATION_ROSTER,
        require_signer_authorization_roster=False,
        signer_authorization_roster_sha256=expected_signer_authorization_roster_pin,
        signer_authorization_roster_receipt=SIGNER_AUTHORIZATION_ROSTER_RECEIPT,
        signer_authorization_roster_receipt_sha256=expected_signer_authorization_roster_receipt_pin,
    )
    if strict_authorized_positive.get("authentication_status") != "SIGNATURE_VERIFIED":
        fail(f"strict authorized auth profile positive path failed: {strict_authorized_positive.get('problems')!r}")
    strict_auth_sv = strict_authorized_positive.get("signature_verification", {})
    if strict_auth_sv.get("auth_profile_status") != "requirements_met":
        fail(f"strict authorized auth profile did not publish requirements_met: {strict_auth_sv!r}")
    if strict_auth_sv.get("signer_authorization_roster_status") != "matched":
        fail(f"signer-authorization roster did not match: {strict_auth_sv.get('signer_authorization_roster_status')!r}")
    if strict_auth_sv.get("signer_authorization_roster_pin_status") != "matched":
        fail("signer-authorization roster pin did not match")
    if strict_auth_sv.get("signer_authorization_roster_receipt_status") != "matched":
        fail(f"signer-authorization roster publication receipt did not match: {strict_auth_sv!r}")
    if strict_auth_sv.get("signer_authorization_roster_receipt_pin_status") != "matched":
        fail("signer-authorization roster receipt pin did not match")
    if strict_auth_sv.get("signer_authorization_roster_receipt_roster_id_status") != "matched":
        fail(f"signer-authorization roster receipt roster-id binding did not match: {strict_auth_sv!r}")
    if strict_auth_sv.get("signer_authorization_roster_receipt_roster_issued_at_status") != "matched":
        fail(f"signer-authorization roster receipt roster-issued-at binding did not match: {strict_auth_sv!r}")
    if strict_auth_sv.get("signer_authorization_roster_receipt_validity_status") != "within_window":
        fail(f"signer-authorization roster receipt validity window did not match: {strict_auth_sv!r}")
    if strict_auth_sv.get("signer_authorization_roster_receipt_channel_time_status") != "within_window":
        fail(f"signer-authorization roster receipt channel times did not match: {strict_auth_sv!r}")
    if strict_auth_sv.get("signer_authorization_roster_receipt_temporal_status") != "coherent":
        fail(f"signer-authorization roster receipt temporal order did not cohere: {strict_auth_sv!r}")
    if int(strict_auth_sv.get("signer_authorization_roster_receipt_independent_channel_count") or 0) < 2:
        fail("signer-authorization roster receipt did not publish independent_channel_count>=2")
    if int(strict_auth_sv.get("signer_authorization_authority_count") or 0) < 2:
        fail("signer-authorization roster did not publish authority_count>=2")
    if int(strict_auth_sv.get("signer_authorization_active_entry_count") or 0) < 2:
        fail("signer-authorization roster did not publish active_entry_count>=2")
    if strict_auth_sv.get("signer_authorization_roster_temporal_status") != "within_window":
        fail(f"signer-authorization roster temporal status did not pass: {strict_auth_sv!r}")
    if strict_auth_sv.get("signer_authorization_authority_observed_at_status") != "coherent":
        fail(f"signer-authorization authority observation status did not pass: {strict_auth_sv!r}")
    if strict_auth_sv.get("signer_authorization_row_validity_status") != "coherent":
        fail(f"signer-authorization row validity status did not pass: {strict_auth_sv!r}")

    with tempfile.TemporaryDirectory(prefix="receipt-channel-digest-") as receipt_digest_td:
        receipt_digest_td_path = Path(receipt_digest_td)

        missing_keyset_channel_digest = receipt_digest_td_path / "missing-keyset-channel-digest.json"
        mutate_receipt_remove_first_channel_digest(
            THRESHOLD_RECEIPT,
            missing_keyset_channel_digest,
            ("observed_trust_keyset_sha256", "trust_keyset_sha256"),
        )
        missing_keyset_channel_report = run_report(
            THRESHOLD_FIXTURE,
            THRESHOLD_KEYRING,
            expected_threshold_pin,
            missing_keyset_channel_digest,
            True,
            keyset_receipt_sha256="sha256:" + sha256_file(missing_keyset_channel_digest),
        )
        if missing_keyset_channel_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-keyset receipt channel without observed digest should fail")
        require_code(missing_keyset_channel_report, "signature_trust_keyset_receipt_digest_mismatch")

        missing_governance_channel_digest = receipt_digest_td_path / "missing-governance-channel-digest.json"
        mutate_receipt_remove_first_channel_digest(
            GOVERNANCE_BUNDLE_RECEIPT,
            missing_governance_channel_digest,
            ("observed_trust_governance_bundle_sha256", "trust_governance_bundle_sha256", "governance_bundle_sha256"),
        )
        missing_governance_channel_report = run_report(
            THRESHOLD_FIXTURE,
            THRESHOLD_KEYRING,
            expected_threshold_pin,
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            expected_governance_pin,
            missing_governance_channel_digest,
            True,
            "sha256:" + sha256_file(missing_governance_channel_digest),
            keyset_receipt_sha256=expected_keyset_receipt_pin,
        )
        if missing_governance_channel_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("governance-bundle receipt channel without observed digest should fail")
        require_code(missing_governance_channel_report, "signature_trust_governance_bundle_receipt_digest_mismatch")

        missing_status_channel_digest = receipt_digest_td_path / "missing-status-channel-digest.json"
        mutate_receipt_remove_first_channel_digest(
            STATUS_SNAPSHOT_RECEIPT,
            missing_status_channel_digest,
            (
                "observed_trust_status_snapshot_sha256",
                "observed_status_snapshot_sha256",
                "trust_status_snapshot_sha256",
                "status_snapshot_sha256",
            ),
        )
        missing_status_channel_report = run_report(
            THRESHOLD_FIXTURE,
            THRESHOLD_KEYRING,
            expected_threshold_pin,
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            expected_governance_pin,
            GOVERNANCE_BUNDLE_RECEIPT,
            True,
            expected_governance_receipt_pin,
            STATUS_SNAPSHOT,
            True,
            expected_status_snapshot_pin,
            missing_status_channel_digest,
            True,
            "sha256:" + sha256_file(missing_status_channel_digest),
            keyset_receipt_sha256=expected_keyset_receipt_pin,
        )
        if missing_status_channel_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot receipt channel without observed digest should fail")
        require_code(missing_status_channel_report, "signature_trust_status_snapshot_receipt_digest_mismatch")

        missing_authorization_channel_digest = receipt_digest_td_path / "missing-authorization-channel-digest.json"
        mutate_receipt_remove_first_channel_digest(
            SIGNER_AUTHORIZATION_ROSTER_RECEIPT,
            missing_authorization_channel_digest,
            (
                "observed_signer_authorization_roster_sha256",
                "signer_authorization_roster_sha256",
                "authorization_roster_sha256",
                "roster_sha256",
            ),
        )
        missing_authorization_channel_report = run_report(
            THRESHOLD_FIXTURE,
            THRESHOLD_KEYRING,
            expected_threshold_pin,
            THRESHOLD_RECEIPT,
            False,
            GOVERNANCE_BUNDLE,
            False,
            expected_governance_pin,
            GOVERNANCE_BUNDLE_RECEIPT,
            False,
            expected_governance_receipt_pin,
            STATUS_SNAPSHOT,
            False,
            expected_status_snapshot_pin,
            STATUS_SNAPSHOT_RECEIPT,
            False,
            expected_status_snapshot_receipt_pin,
            keyset_receipt_sha256=expected_keyset_receipt_pin,
            auth_profile="strict-local-authorized-trust-chain-v1",
            signer_authorization_roster=SIGNER_AUTHORIZATION_ROSTER,
            signer_authorization_roster_sha256=expected_signer_authorization_roster_pin,
            signer_authorization_roster_receipt=missing_authorization_channel_digest,
            signer_authorization_roster_receipt_sha256="sha256:" + sha256_file(missing_authorization_channel_digest),
        )
        if missing_authorization_channel_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster receipt channel without observed digest should fail")
        require_code(missing_authorization_channel_report, "signature_signer_authorization_roster_receipt_digest_mismatch")

    missing_roster_receipt = run_report(
        THRESHOLD_FIXTURE,
        THRESHOLD_KEYRING,
        expected_threshold_pin,
        THRESHOLD_RECEIPT,
        False,
        GOVERNANCE_BUNDLE,
        False,
        expected_governance_pin,
        GOVERNANCE_BUNDLE_RECEIPT,
        False,
        expected_governance_receipt_pin,
        STATUS_SNAPSHOT,
        False,
        expected_status_snapshot_pin,
        STATUS_SNAPSHOT_RECEIPT,
        False,
        expected_status_snapshot_receipt_pin,
        keyset_receipt_sha256=expected_keyset_receipt_pin,
        auth_profile="strict-local-authorized-trust-chain-v1",
        signer_authorization_roster=SIGNER_AUTHORIZATION_ROSTER,
        signer_authorization_roster_sha256=expected_signer_authorization_roster_pin,
    )
    if missing_roster_receipt.get("authentication_status") != "SIGNATURE_FAILED":
        fail("strict authorized auth profile without signer-authorization roster receipt should fail")
    require_code(missing_roster_receipt, "signature_signer_authorization_roster_receipt_invalid")

    with tempfile.TemporaryDirectory() as roster_receipt_td:
        roster_receipt_td_path = Path(roster_receipt_td)
        bad_roster_receipt_digest = roster_receipt_td_path / "bad-roster-receipt-digest.json"
        mutate_signer_authorization_roster_receipt_digest(SIGNER_AUTHORIZATION_ROSTER_RECEIPT, bad_roster_receipt_digest)
        bad_roster_receipt_digest_report = run_strict_authorized(
            roster_receipt=bad_roster_receipt_digest,
            roster_receipt_pin="sha256:" + sha256_file(bad_roster_receipt_digest),
        )
        if bad_roster_receipt_digest_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster receipt digest mismatch should fail")
        require_code(bad_roster_receipt_digest_report, "signature_signer_authorization_roster_receipt_digest_mismatch")

        weak_roster_receipt = roster_receipt_td_path / "weak-roster-receipt.json"
        mutate_signer_authorization_roster_receipt_single_channel(SIGNER_AUTHORIZATION_ROSTER_RECEIPT, weak_roster_receipt)
        weak_roster_receipt_report = run_strict_authorized(
            roster_receipt=weak_roster_receipt,
            roster_receipt_pin="sha256:" + sha256_file(weak_roster_receipt),
        )
        if weak_roster_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster receipt channel quorum failure should fail")
        require_code(weak_roster_receipt_report, "signature_signer_authorization_roster_receipt_channel_quorum_not_met")

        same_type_roster_receipt = roster_receipt_td_path / "same-type-roster-receipt.json"
        mutate_receipt_same_channel_type(SIGNER_AUTHORIZATION_ROSTER_RECEIPT, same_type_roster_receipt)
        same_type_roster_receipt_report = run_strict_authorized(
            roster_receipt=same_type_roster_receipt,
            roster_receipt_pin="sha256:" + sha256_file(same_type_roster_receipt),
        )
        if same_type_roster_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("same-type signer-authorization roster receipt quorum should fail channel diversity")
        require_code(same_type_roster_receipt_report, "signature_signer_authorization_roster_receipt_channel_diversity_not_met")

        bad_roster_receipt_id = roster_receipt_td_path / "bad-roster-receipt-id.json"
        mutate_signer_authorization_roster_receipt_roster_id(SIGNER_AUTHORIZATION_ROSTER_RECEIPT, bad_roster_receipt_id)
        bad_roster_receipt_id_report = run_strict_authorized(
            roster_receipt=bad_roster_receipt_id,
            roster_receipt_pin="sha256:" + sha256_file(bad_roster_receipt_id),
        )
        if bad_roster_receipt_id_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster receipt roster-id mismatch should fail")
        require_code(bad_roster_receipt_id_report, "signature_signer_authorization_roster_receipt_identity_mismatch")

        bad_roster_receipt_issued = roster_receipt_td_path / "bad-roster-receipt-issued-at.json"
        mutate_signer_authorization_roster_receipt_roster_issued_at(SIGNER_AUTHORIZATION_ROSTER_RECEIPT, bad_roster_receipt_issued)
        bad_roster_receipt_issued_report = run_strict_authorized(
            roster_receipt=bad_roster_receipt_issued,
            roster_receipt_pin="sha256:" + sha256_file(bad_roster_receipt_issued),
        )
        if bad_roster_receipt_issued_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster receipt roster-issued-at mismatch should fail")
        require_code(bad_roster_receipt_issued_report, "signature_signer_authorization_roster_receipt_identity_mismatch")

        predating_roster_receipt = roster_receipt_td_path / "predating-roster-receipt.json"
        mutate_signer_authorization_roster_receipt_predates_roster(SIGNER_AUTHORIZATION_ROSTER_RECEIPT, predating_roster_receipt)
        predating_roster_receipt_report = run_strict_authorized(
            roster_receipt=predating_roster_receipt,
            roster_receipt_pin="sha256:" + sha256_file(predating_roster_receipt),
        )
        if predating_roster_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster receipt predating roster should fail")
        require_code(predating_roster_receipt_report, "signature_signer_authorization_roster_receipt_temporal_invalid")

        issued_before_channel_receipt = roster_receipt_td_path / "issued-before-channel-roster-receipt.json"
        mutate_signer_authorization_roster_receipt_issued_before_latest_channel(SIGNER_AUTHORIZATION_ROSTER_RECEIPT, issued_before_channel_receipt)
        issued_before_channel_receipt_report = run_strict_authorized(
            roster_receipt=issued_before_channel_receipt,
            roster_receipt_pin="sha256:" + sha256_file(issued_before_channel_receipt),
        )
        if issued_before_channel_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster receipt issued before latest channel should fail")
        require_code(issued_before_channel_receipt_report, "signature_signer_authorization_roster_receipt_temporal_invalid")

        expired_roster_receipt = roster_receipt_td_path / "expired-roster-receipt.json"
        mutate_signer_authorization_roster_receipt_expired_window(SIGNER_AUTHORIZATION_ROSTER_RECEIPT, expired_roster_receipt)
        expired_roster_receipt_report = run_strict_authorized(
            roster_receipt=expired_roster_receipt,
            roster_receipt_pin="sha256:" + sha256_file(expired_roster_receipt),
        )
        if expired_roster_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster receipt expired window should fail")
        require_code(expired_roster_receipt_report, "signature_signer_authorization_roster_receipt_temporal_invalid")

        future_roster_receipt = roster_receipt_td_path / "future-channel-roster-receipt.json"
        mutate_signer_authorization_roster_receipt_future_channel(SIGNER_AUTHORIZATION_ROSTER_RECEIPT, future_roster_receipt)
        future_roster_receipt_report = run_strict_authorized(
            roster_receipt=future_roster_receipt,
            roster_receipt_pin="sha256:" + sha256_file(future_roster_receipt),
        )
        if future_roster_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster receipt future channel should fail")
        require_code(future_roster_receipt_report, "signature_signer_authorization_roster_receipt_temporal_invalid")

    bad_roster_receipt_pin = run_strict_authorized(roster_receipt_pin="sha256:" + ("d" * 64))
    if bad_roster_receipt_pin.get("authentication_status") != "SIGNATURE_FAILED":
        fail("signer-authorization roster receipt pin mismatch should fail")
    require_code(bad_roster_receipt_pin, "signature_signer_authorization_roster_receipt_pin_mismatch")

    with tempfile.TemporaryDirectory() as packet_receipt_td:
        packet_receipt_td_path = Path(packet_receipt_td)
        packet_receipt_packet = packet_receipt_td_path / "packet-contained-signer-authorization-roster-receipt"
        shutil.copytree(THRESHOLD_FIXTURE, packet_receipt_packet)
        packet_receipt = packet_receipt_packet / "signer-authorization-roster-receipt.json"
        shutil.copy2(SIGNER_AUTHORIZATION_ROSTER_RECEIPT, packet_receipt)
        packet_receipt_report = run_strict_authorized(packet_dir=packet_receipt_packet, roster_receipt=packet_receipt)
        if packet_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("packet-contained signer-authorization roster receipt should fail")
        require_code(packet_receipt_report, "signature_signer_authorization_roster_receipt_untrusted_location")

    policy_lockfile_positive = run_policy_lockfile_report(
        THRESHOLD_FIXTURE,
        VERIFICATION_POLICY_LOCKFILE,
        expected_verification_policy_lockfile_pin,
        VERIFICATION_POLICY_LOCKFILE_RECEIPT,
        expected_verification_policy_lockfile_receipt_pin,
        True,
    )
    if policy_lockfile_positive.get("authentication_status") != "SIGNATURE_VERIFIED":
        fail(f"verification policy lockfile positive path failed: {policy_lockfile_positive.get('problems')!r}")
    policy_sv = policy_lockfile_positive.get("signature_verification", {})
    if policy_sv.get("verification_policy_lockfile_status") != "matched":
        fail(f"verification policy lockfile did not match: {policy_sv.get('verification_policy_lockfile_status')!r}")
    if policy_sv.get("verification_policy_lockfile_pin_status") != "matched":
        fail("verification policy lockfile pin did not match")
    if policy_sv.get("verification_policy_lockfile_receipt_status") != "matched":
        fail(f"verification policy lockfile receipt did not match: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_receipt_pin_status") != "matched":
        fail("verification policy lockfile receipt pin did not match")
    if int(policy_sv.get("verification_policy_lockfile_receipt_independent_channel_count") or 0) < 2:
        fail("verification policy lockfile receipt did not publish independent_channel_count>=2")
    if policy_sv.get("verification_policy_lockfile_receipt_validity_status") != "within_window":
        fail(f"verification policy lockfile receipt validity window did not match: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_receipt_channel_time_status") != "within_window":
        fail(f"verification policy lockfile receipt channel times did not match: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_receipt_temporal_status") != "coherent":
        fail(f"verification policy lockfile receipt temporal order did not cohere: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_auth_profile") != "strict-local-authorized-trust-chain-v1":
        fail(f"verification policy lockfile did not set the authorized strict profile: {policy_sv.get('verification_policy_lockfile_auth_profile')!r}")
    if policy_sv.get("verification_policy_lockfile_verifier_requirements_status") != "matched":
        fail(f"verification policy lockfile verifier requirements did not match: {policy_sv!r}")
    expected_report_version = observer_report_version()
    expected_public_fp_profile = public_fingerprint_profile_version()
    if policy_sv.get("verification_policy_lockfile_actual_archive_version") != ARCHIVE_VERSION:
        fail(f"policy lockfile did not bind to {ARCHIVE_VERSION} archive version: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_actual_report_version") != expected_report_version:
        fail(f"policy lockfile did not bind to PacketVerificationReport {expected_report_version}: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_required_auth_profile_status") != "matched":
        fail(f"policy lockfile auth-profile requirement did not match: {policy_sv!r}")
    if policy_sv.get("auth_profile_status") != "requirements_met":
        fail(f"policy lockfile did not satisfy strict authorized auth profile: {policy_sv!r}")
    if policy_sv.get("signer_authorization_roster_status") != "matched":
        fail("policy lockfile positive path did not load signer-authorization roster")
    if policy_sv.get("signer_authorization_roster_receipt_status") != "matched":
        fail("policy lockfile positive path did not load signer-authorization roster publication receipt")

    if policy_sv.get("verification_policy_lockfile_validity_status") != "within_window":
        fail(f"policy lockfile validity window did not match: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_temporal_context_status") != "external_time_supplied":
        fail(f"policy lockfile did not require/use external temporal context: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_embedded_verification_time_present") is not False:
        fail(f"policy lockfile should not embed verification_time: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_packet_selector_status") != "matched":
        fail(f"policy lockfile packet selector did not match: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_packet_selector_actual_packet_id") != "evidence_packet_ed25519_threshold2_minimal":
        fail(f"policy lockfile actual packet id drift: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_packet_public_fingerprint_status") != "matched":
        fail(f"policy lockfile packet public fingerprint did not match: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_packet_public_fingerprint_profile_status") != "matched":
        fail(f"policy lockfile packet public fingerprint profile did not match: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_packet_public_fingerprint_profile") != expected_public_fp_profile:
        fail(f"policy lockfile public fingerprint actual profile drift: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_packet_public_fingerprint_expected_profile") != expected_public_fp_profile:
        fail(f"policy lockfile public fingerprint expected profile drift: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_receipt_packet_public_fingerprint_status") != "matched":
        fail(f"policy lockfile receipt packet public fingerprint did not match: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_receipt_packet_public_fingerprint_profile_status") != "matched":
        fail(f"policy lockfile receipt packet public fingerprint profile did not match: {policy_sv!r}")
    if not str(policy_sv.get("verification_policy_lockfile_packet_public_fingerprint_actual_sha256") or "").startswith("sha256:"):
        fail(f"policy lockfile packet public fingerprint digest missing: {policy_sv!r}")
    if int(policy_sv.get("verification_policy_lockfile_packet_public_fingerprint_warn_count") or 0) != 0:
        fail(f"policy lockfile packet public fingerprint emitted warnings: {policy_sv!r}")
    if policy_sv.get("verification_policy_lockfile_trust_closure_status") != "computed":
        fail(f"policy lockfile trust-closure digest was not computed: {policy_sv!r}")
    if int(policy_sv.get("verification_policy_lockfile_trust_closure_input_count") or 0) != 8:
        fail(f"policy lockfile trust-closure input count drift: {policy_sv!r}")
    closure_sha = str(policy_sv.get("verification_policy_lockfile_trust_closure_sha256") or "")
    if not closure_sha.startswith("sha256:") or len(closure_sha) != 71:
        fail(f"policy lockfile trust-closure digest missing/malformed: {policy_sv!r}")

    with tempfile.TemporaryDirectory() as policy_fp_td:
        policy_fp_dir = Path(policy_fp_td)
        wrong_fp_policy = policy_fp_dir / "wrong-packet-fingerprint-policy.json"
        wrong_fp_receipt = policy_fp_dir / "wrong-packet-fingerprint-policy-receipt.json"
        obj = json.loads(VERIFICATION_POLICY_LOCKFILE.read_text(encoding="utf-8"))
        obj["packet_public_fingerprint_sha256"] = "sha256:" + ("0" * 64)
        write_json(wrong_fp_policy, obj)
        write_matching_policy_lockfile_receipt(VERIFICATION_POLICY_LOCKFILE_RECEIPT, wrong_fp_policy, wrong_fp_receipt)
        rec = json.loads(wrong_fp_receipt.read_text(encoding="utf-8"))
        rec["packet_public_fingerprint_sha256"] = obj["packet_public_fingerprint_sha256"]
        write_json(wrong_fp_receipt, rec)
        wrong_fp_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            wrong_fp_policy,
            "sha256:" + sha256_file(wrong_fp_policy),
            wrong_fp_receipt,
            "sha256:" + sha256_file(wrong_fp_receipt),
            True,
        )
        if wrong_fp_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("wrong packet public fingerprint should fail")
        require_code(wrong_fp_report, "signature_verification_policy_lockfile_packet_fingerprint_mismatch")

        missing_fp_policy = policy_fp_dir / "missing-packet-fingerprint-policy.json"
        missing_fp_receipt = policy_fp_dir / "missing-packet-fingerprint-policy-receipt.json"
        obj = json.loads(VERIFICATION_POLICY_LOCKFILE.read_text(encoding="utf-8"))
        obj.pop("packet_public_fingerprint_sha256", None)
        write_json(missing_fp_policy, obj)
        write_matching_policy_lockfile_receipt(VERIFICATION_POLICY_LOCKFILE_RECEIPT, missing_fp_policy, missing_fp_receipt)
        missing_fp_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            missing_fp_policy,
            "sha256:" + sha256_file(missing_fp_policy),
            missing_fp_receipt,
            "sha256:" + sha256_file(missing_fp_receipt),
            True,
        )
        if missing_fp_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("missing packet public fingerprint should fail")
        require_code(missing_fp_report, "signature_verification_policy_lockfile_packet_fingerprint_invalid")

        missing_fp_profile_policy = policy_fp_dir / "missing-packet-fingerprint-profile-policy.json"
        missing_fp_profile_receipt = policy_fp_dir / "missing-packet-fingerprint-profile-policy-receipt.json"
        obj = json.loads(VERIFICATION_POLICY_LOCKFILE.read_text(encoding="utf-8"))
        obj.pop("packet_public_fingerprint_profile", None)
        write_json(missing_fp_profile_policy, obj)
        write_matching_policy_lockfile_receipt(VERIFICATION_POLICY_LOCKFILE_RECEIPT, missing_fp_profile_policy, missing_fp_profile_receipt)
        missing_fp_profile_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            missing_fp_profile_policy,
            "sha256:" + sha256_file(missing_fp_profile_policy),
            missing_fp_profile_receipt,
            "sha256:" + sha256_file(missing_fp_profile_receipt),
            True,
        )
        if missing_fp_profile_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("missing packet public fingerprint profile should fail")
        require_code(missing_fp_profile_report, "signature_verification_policy_lockfile_packet_fingerprint_profile_mismatch")

        wrong_fp_profile_policy = policy_fp_dir / "wrong-packet-fingerprint-profile-policy.json"
        wrong_fp_profile_receipt = policy_fp_dir / "wrong-packet-fingerprint-profile-policy-receipt.json"
        obj = json.loads(VERIFICATION_POLICY_LOCKFILE.read_text(encoding="utf-8"))
        obj["packet_public_fingerprint_profile"] = "0.9"
        write_json(wrong_fp_profile_policy, obj)
        write_matching_policy_lockfile_receipt(VERIFICATION_POLICY_LOCKFILE_RECEIPT, wrong_fp_profile_policy, wrong_fp_profile_receipt)
        wrong_fp_profile_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            wrong_fp_profile_policy,
            "sha256:" + sha256_file(wrong_fp_profile_policy),
            wrong_fp_profile_receipt,
            "sha256:" + sha256_file(wrong_fp_profile_receipt),
            True,
        )
        if wrong_fp_profile_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("wrong packet public fingerprint profile should fail")
        require_code(wrong_fp_profile_report, "signature_verification_policy_lockfile_packet_fingerprint_profile_mismatch")

        receipt_profile_mismatch = policy_fp_dir / "policy-receipt-fingerprint-profile-mismatch.json"
        rec = json.loads(VERIFICATION_POLICY_LOCKFILE_RECEIPT.read_text(encoding="utf-8"))
        rec["packet_public_fingerprint_profile"] = "0.9"
        write_json(receipt_profile_mismatch, rec)
        receipt_profile_mismatch_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            receipt_profile_mismatch,
            "sha256:" + sha256_file(receipt_profile_mismatch),
            True,
        )
        if receipt_profile_mismatch_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("policy receipt packet public fingerprint profile mismatch should fail")
        require_code(receipt_profile_mismatch_report, "signature_verification_policy_lockfile_receipt_identity_mismatch")

        mut_packet = policy_fp_dir / "evidence_packet_ed25519_threshold2_minimal"
        shutil.copytree(THRESHOLD_FIXTURE, mut_packet)
        readme = mut_packet / "README.txt"
        readme.write_text(readme.read_text(encoding="utf-8") + "\npacket-public-fingerprint-negative-control\n", encoding="utf-8")
        mut_packet_report = run_policy_lockfile_report(
            mut_packet,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            VERIFICATION_POLICY_LOCKFILE_RECEIPT,
            expected_verification_policy_lockfile_receipt_pin,
            True,
        )
        if mut_packet_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("same-selector different-public-byte packet should fail")
        require_code(mut_packet_report, "signature_verification_policy_lockfile_packet_fingerprint_mismatch")

        symlink_parent = policy_fp_dir / "symlink-public-fingerprint-case"
        symlink_parent.mkdir()
        symlink_packet = symlink_parent / "evidence_packet_ed25519_threshold2_minimal"
        shutil.copytree(THRESHOLD_FIXTURE, symlink_packet)
        link = symlink_packet / "README.txt"
        link.unlink()
        try:
            link.symlink_to(THRESHOLD_FIXTURE / "README.txt")
        except (OSError, NotImplementedError):
            symlink_packet = None
        if symlink_packet is not None:
            symlink_packet_report = run_policy_lockfile_report(
                symlink_packet,
                VERIFICATION_POLICY_LOCKFILE,
                expected_verification_policy_lockfile_pin,
                VERIFICATION_POLICY_LOCKFILE_RECEIPT,
                expected_verification_policy_lockfile_receipt_pin,
                True,
            )
            if symlink_packet_report.get("authentication_status") != "SIGNATURE_FAILED":
                fail("same-selector symlinked public-fingerprint surface should fail")
            require_code(symlink_packet_report, "signature_verification_policy_lockfile_packet_fingerprint_invalid")
            sv = symlink_packet_report.get("signature_verification") or {}
            if int(sv.get("verification_policy_lockfile_packet_public_fingerprint_warn_count") or 0) < 1:
                fail(f"symlinked public-fingerprint surface should emit a warning count: {sv!r}")

        oversized_packet = policy_fp_dir / "oversized-public-fingerprint-case" / "evidence_packet_ed25519_threshold2_minimal"
        shutil.copytree(THRESHOLD_FIXTURE, oversized_packet)
        (oversized_packet / "README.txt").write_bytes(b"A" * (512 * 1024 + 1))
        oversized_packet_report = run_policy_lockfile_report(
            oversized_packet,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            VERIFICATION_POLICY_LOCKFILE_RECEIPT,
            expected_verification_policy_lockfile_receipt_pin,
            True,
        )
        if oversized_packet_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("same-selector oversized public-fingerprint surface should fail")
        require_code(oversized_packet_report, "signature_verification_policy_lockfile_packet_fingerprint_invalid")
        sv = oversized_packet_report.get("signature_verification") or {}
        if int(sv.get("verification_policy_lockfile_packet_public_fingerprint_warn_count") or 0) < 1:
            fail(f"oversized public-fingerprint surface should emit a warning count: {sv!r}")

    bad_policy_pin = run_policy_lockfile_report(
        THRESHOLD_FIXTURE,
        VERIFICATION_POLICY_LOCKFILE,
        "sha256:" + ("e" * 64),
    )
    if bad_policy_pin.get("authentication_status") != "SIGNATURE_FAILED":
        fail("verification policy lockfile pin mismatch should fail")
    require_code(bad_policy_pin, "signature_verification_policy_lockfile_pin_mismatch")

    missing_policy_pin = run_policy_lockfile_report(
        THRESHOLD_FIXTURE,
        VERIFICATION_POLICY_LOCKFILE,
        "",
    )
    if missing_policy_pin.get("authentication_status") != "SIGNATURE_FAILED":
        fail("strict verification policy lockfile without caller-side pin should fail")
    require_code(missing_policy_pin, "signature_verification_policy_lockfile_pin_required")

    missing_policy_receipt = run_policy_lockfile_report(
        THRESHOLD_FIXTURE,
        VERIFICATION_POLICY_LOCKFILE,
        expected_verification_policy_lockfile_pin,
        None,
        "",
        False,
    )
    if missing_policy_receipt.get("authentication_status") != "SIGNATURE_FAILED":
        fail("strict verification policy lockfile should auto-require its external publication receipt")
    require_code(missing_policy_receipt, "signature_verification_policy_lockfile_receipt_invalid")

    missing_policy_receipt_pin = run_policy_lockfile_report(
        THRESHOLD_FIXTURE,
        VERIFICATION_POLICY_LOCKFILE,
        expected_verification_policy_lockfile_pin,
        VERIFICATION_POLICY_LOCKFILE_RECEIPT,
        "",
        False,
    )
    if missing_policy_receipt_pin.get("authentication_status") != "SIGNATURE_FAILED":
        fail("strict verification policy lockfile receipt without caller-side receipt pin should fail")
    require_code(missing_policy_receipt_pin, "signature_verification_policy_lockfile_receipt_pin_required")

    bad_policy_receipt_pin = run_policy_lockfile_report(
        THRESHOLD_FIXTURE,
        VERIFICATION_POLICY_LOCKFILE,
        expected_verification_policy_lockfile_pin,
        VERIFICATION_POLICY_LOCKFILE_RECEIPT,
        "sha256:" + ("d" * 64),
        True,
    )
    if bad_policy_receipt_pin.get("authentication_status") != "SIGNATURE_FAILED":
        fail("verification policy lockfile receipt pin mismatch should fail")
    require_code(bad_policy_receipt_pin, "signature_verification_policy_lockfile_receipt_pin_mismatch")

    with tempfile.TemporaryDirectory() as policy_receipt_td:
        policy_receipt_td_path = Path(policy_receipt_td)
        bad_policy_receipt_digest = policy_receipt_td_path / "bad-policy-receipt-digest.json"
        mutate_policy_lockfile_receipt_digest(VERIFICATION_POLICY_LOCKFILE_RECEIPT, bad_policy_receipt_digest)
        bad_policy_receipt_digest_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            bad_policy_receipt_digest,
            "sha256:" + sha256_file(bad_policy_receipt_digest),
            True,
        )
        if bad_policy_receipt_digest_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile receipt digest mismatch should fail")
        require_code(bad_policy_receipt_digest_report, "signature_verification_policy_lockfile_receipt_digest_mismatch")

        wrong_policy_id_receipt = policy_receipt_td_path / "wrong-policy-id-policy-receipt.json"
        mutate_policy_lockfile_receipt_policy_id(VERIFICATION_POLICY_LOCKFILE_RECEIPT, wrong_policy_id_receipt)
        wrong_policy_id_receipt_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            wrong_policy_id_receipt,
            "sha256:" + sha256_file(wrong_policy_id_receipt),
            True,
        )
        if wrong_policy_id_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile receipt with wrong policy id should fail")
        require_code(wrong_policy_id_receipt_report, "signature_verification_policy_lockfile_receipt_identity_mismatch")

        wrong_selector_receipt = policy_receipt_td_path / "wrong-selector-policy-receipt.json"
        mutate_policy_lockfile_receipt_selector(VERIFICATION_POLICY_LOCKFILE_RECEIPT, wrong_selector_receipt, election_id="OTHER-ELECTION")
        wrong_selector_receipt_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            wrong_selector_receipt,
            "sha256:" + sha256_file(wrong_selector_receipt),
            True,
        )
        if wrong_selector_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile receipt with wrong packet selector should fail")
        require_code(wrong_selector_receipt_report, "signature_verification_policy_lockfile_receipt_identity_mismatch")

        missing_selector_receipt = policy_receipt_td_path / "missing-selector-policy-receipt.json"
        mutate_policy_lockfile_receipt_selector(VERIFICATION_POLICY_LOCKFILE_RECEIPT, missing_selector_receipt, jurisdiction="__DELETE__")
        missing_selector_receipt_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            missing_selector_receipt,
            "sha256:" + sha256_file(missing_selector_receipt),
            True,
        )
        if missing_selector_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile receipt with missing packet selector field should fail")
        require_code(missing_selector_receipt_report, "signature_verification_policy_lockfile_receipt_identity_mismatch")

        weak_policy_receipt = policy_receipt_td_path / "weak-policy-receipt-single-channel.json"
        mutate_policy_lockfile_receipt_single_channel(VERIFICATION_POLICY_LOCKFILE_RECEIPT, weak_policy_receipt)
        weak_policy_receipt_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            weak_policy_receipt,
            "sha256:" + sha256_file(weak_policy_receipt),
            True,
        )
        if weak_policy_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile receipt weak channel quorum should fail")
        require_code(weak_policy_receipt_report, "signature_verification_policy_lockfile_receipt_channel_quorum_not_met")

        same_type_policy_receipt = policy_receipt_td_path / "same-type-policy-receipt.json"
        mutate_receipt_same_channel_type(VERIFICATION_POLICY_LOCKFILE_RECEIPT, same_type_policy_receipt)
        same_type_policy_receipt_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            same_type_policy_receipt,
            "sha256:" + sha256_file(same_type_policy_receipt),
            True,
        )
        if same_type_policy_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("same-type verification-policy receipt quorum should fail channel diversity")
        require_code(same_type_policy_receipt_report, "signature_verification_policy_lockfile_receipt_channel_diversity_not_met")

        predating_policy_receipt = policy_receipt_td_path / "predating-policy-receipt.json"
        mutate_policy_lockfile_receipt_predates_policy(VERIFICATION_POLICY_LOCKFILE_RECEIPT, predating_policy_receipt)
        predating_policy_receipt_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            predating_policy_receipt,
            "sha256:" + sha256_file(predating_policy_receipt),
            True,
        )
        if predating_policy_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile receipt predating policy issuance should fail")
        require_code(predating_policy_receipt_report, "signature_verification_policy_lockfile_receipt_temporal_invalid")

        receipt_before_channel = policy_receipt_td_path / "receipt-issued-before-latest-channel.json"
        mutate_policy_lockfile_receipt_issued_before_latest_channel(VERIFICATION_POLICY_LOCKFILE_RECEIPT, receipt_before_channel)
        receipt_before_channel_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            receipt_before_channel,
            "sha256:" + sha256_file(receipt_before_channel),
            True,
        )
        if receipt_before_channel_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile receipt issued before latest channel observation should fail")
        require_code(receipt_before_channel_report, "signature_verification_policy_lockfile_receipt_temporal_invalid")

        expired_policy_receipt = policy_receipt_td_path / "expired-policy-receipt.json"
        mutate_policy_lockfile_receipt_validity(VERIFICATION_POLICY_LOCKFILE_RECEIPT, expired_policy_receipt, valid_until="2026-06-04T20:10:00Z")
        expired_policy_receipt_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            expired_policy_receipt,
            "sha256:" + sha256_file(expired_policy_receipt),
            True,
        )
        if expired_policy_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile receipt expired temporal window should fail")
        require_code(expired_policy_receipt_report, "signature_verification_policy_lockfile_receipt_temporal_invalid")

        missing_window_policy_receipt = policy_receipt_td_path / "missing-window-policy-receipt.json"
        mutate_policy_lockfile_receipt_validity(VERIFICATION_POLICY_LOCKFILE_RECEIPT, missing_window_policy_receipt, remove=True)
        missing_window_policy_receipt_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            missing_window_policy_receipt,
            "sha256:" + sha256_file(missing_window_policy_receipt),
            True,
        )
        if missing_window_policy_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile receipt missing temporal window should fail")
        require_code(missing_window_policy_receipt_report, "signature_verification_policy_lockfile_receipt_temporal_invalid")

        future_channel_policy_receipt = policy_receipt_td_path / "future-channel-policy-receipt.json"
        mutate_policy_lockfile_receipt_future_channel(VERIFICATION_POLICY_LOCKFILE_RECEIPT, future_channel_policy_receipt)
        future_channel_policy_receipt_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            future_channel_policy_receipt,
            "sha256:" + sha256_file(future_channel_policy_receipt),
            True,
        )
        if future_channel_policy_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile receipt future publication time should fail")
        require_code(future_channel_policy_receipt_report, "signature_verification_policy_lockfile_receipt_temporal_invalid")

        missing_policy_channel_digest = policy_receipt_td_path / "missing-policy-channel-digest.json"
        mutate_receipt_remove_first_channel_digest(
            VERIFICATION_POLICY_LOCKFILE_RECEIPT,
            missing_policy_channel_digest,
            (
                "observed_verification_policy_lockfile_sha256",
                "observed_policy_lockfile_sha256",
                "verification_policy_lockfile_sha256",
                "policy_lockfile_sha256",
            ),
        )
        missing_policy_channel_digest_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
            missing_policy_channel_digest,
            "sha256:" + sha256_file(missing_policy_channel_digest),
            True,
        )
        if missing_policy_channel_digest_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile receipt channel without observed digest should fail")
        require_code(missing_policy_channel_digest_report, "signature_verification_policy_lockfile_receipt_digest_mismatch")


    missing_external_time_policy = run_policy_lockfile_report(
        THRESHOLD_FIXTURE,
        VERIFICATION_POLICY_LOCKFILE,
        expected_verification_policy_lockfile_pin,
        verification_time="",
    )
    if missing_external_time_policy.get("authentication_status") != "SIGNATURE_FAILED":
        fail("strict verification policy lockfile without caller-supplied verification time should fail")
    require_code(missing_external_time_policy, "signature_verification_policy_lockfile_temporal_context_invalid")

    with tempfile.TemporaryDirectory() as time_td:
        time_policy = Path(time_td) / "bad-policy-embedded-verification-time.json"
        mutate_policy_lockfile_validity(VERIFICATION_POLICY_LOCKFILE, time_policy, verification_time=FIXED_VERIFICATION_TIME)
        embedded_time_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            time_policy,
            "sha256:" + sha256_file(time_policy),
        )
        if embedded_time_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("strict verification policy lockfile with embedded verification_time should fail")
        require_code(embedded_time_report, "signature_verification_policy_lockfile_temporal_context_invalid")

    with tempfile.TemporaryDirectory() as verifier_req_td:
        verifier_req_td_path = Path(verifier_req_td)
        verifier_req_cases = [
            ("missing-requirements", {"remove": True}),
            ("wrong-archive", {"archive_version": "v852"}),
            ("wrong-report", {"report_version": "1.19.0"}),
            ("wrong-auth-profile", {"auth_profile": "strict-local-trust-chain-v1"}),
        ]
        for label, kwargs in verifier_req_cases:
            bad_policy = verifier_req_td_path / f"bad-policy-verifier-requirements-{label}.json"
            mutate_policy_lockfile_verifier_requirements(VERIFICATION_POLICY_LOCKFILE, bad_policy, **kwargs)
            matching_policy_receipt = verifier_req_td_path / f"bad-policy-{label}-matching-receipt.json"
            write_matching_policy_lockfile_receipt(VERIFICATION_POLICY_LOCKFILE_RECEIPT, bad_policy, matching_policy_receipt)
            bad_policy_report = run_policy_lockfile_report(
                THRESHOLD_FIXTURE,
                bad_policy,
                "sha256:" + sha256_file(bad_policy),
                matching_policy_receipt,
                "sha256:" + sha256_file(matching_policy_receipt),
                True,
            )
            if bad_policy_report.get("authentication_status") != "SIGNATURE_FAILED":
                fail(f"verification policy lockfile with {label} verifier requirements should fail")
            require_code(bad_policy_report, "signature_verification_policy_lockfile_verifier_requirement_mismatch")
            bad_policy_sv = bad_policy_report.get("signature_verification", {})
            if bad_policy_sv.get("verification_policy_lockfile_verifier_requirements_status") not in {"missing", "mismatched", "invalid"}:
                fail(f"bad verifier requirements did not publish failure status: {bad_policy_sv!r}")

    policy_conflict = run_policy_lockfile_report(
        THRESHOLD_FIXTURE,
        VERIFICATION_POLICY_LOCKFILE,
        expected_verification_policy_lockfile_pin,
        extra_args=["--trust-keyset", str(THRESHOLD_KEYRING)],
    )
    if policy_conflict.get("authentication_status") != "SIGNATURE_FAILED":
        fail("verification policy lockfile mixed with manual trust flags should fail")
    require_code(policy_conflict, "signature_verification_policy_lockfile_conflict")

    with tempfile.TemporaryDirectory() as policy_td:
        policy_td_path = Path(policy_td)
        path_scope_cases = [
            ("absolute", "/tmp/trust-keyset-ed25519-threshold2-demo.json"),
            ("url", "https://example.invalid/trust-keyset-ed25519-threshold2-demo.json"),
            ("parent", "../trust-keysets/trust-keyset-ed25519-threshold2-demo.json"),
        ]
        for label, replacement_path in path_scope_cases:
            bad_policy = policy_td_path / f"bad-policy-{label}.json"
            mutate_policy_lockfile_input_path(VERIFICATION_POLICY_LOCKFILE, bad_policy, "trust_keyset", replacement_path)
            matching_policy_receipt = policy_td_path / f"bad-policy-{label}-matching-receipt.json"
            write_matching_policy_lockfile_receipt(VERIFICATION_POLICY_LOCKFILE_RECEIPT, bad_policy, matching_policy_receipt)
            bad_policy_report = run_policy_lockfile_report(
                THRESHOLD_FIXTURE,
                bad_policy,
                "sha256:" + sha256_file(bad_policy),
                matching_policy_receipt,
                "sha256:" + sha256_file(matching_policy_receipt),
                True,
            )
            if bad_policy_report.get("authentication_status") != "SIGNATURE_FAILED":
                fail(f"verification policy lockfile with {label} trust input path should fail")
            require_code(bad_policy_report, "signature_verification_policy_lockfile_path_scope_violation")
            sv_bad_policy = bad_policy_report.get("signature_verification", {})
            if sv_bad_policy.get("verification_policy_lockfile_path_policy_status") != "violated":
                fail(f"bad policy {label} did not publish path_policy_status=violated: {sv_bad_policy!r}")

        missing_base_policy = policy_td_path / "bad-policy-missing-base.json"
        mutate_policy_lockfile_remove_base_dir(VERIFICATION_POLICY_LOCKFILE, missing_base_policy)
        missing_base_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            missing_base_policy,
            "sha256:" + sha256_file(missing_base_policy),
        )
        if missing_base_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("strict verification policy lockfile without trust_input_base_dir should fail")
        require_code(missing_base_report, "signature_verification_policy_lockfile_path_scope_violation")

        unknown_input_policy = policy_td_path / "unknown-input-policy.json"
        mutate_policy_lockfile_add_unknown_trust_input(VERIFICATION_POLICY_LOCKFILE, unknown_input_policy)
        unknown_input_report = run_policy_lockfile_report(
            THRESHOLD_FIXTURE,
            unknown_input_policy,
            "sha256:" + sha256_file(unknown_input_policy),
        )
        if unknown_input_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("strict verification policy lockfile with unknown trust_inputs key should fail")
        require_code(unknown_input_report, "signature_verification_policy_lockfile_unknown_trust_input")

        validity_cases = [
            ("missing-validity", {"remove": True}),
            ("expired", {"valid_until": "2026-06-03T23:59:59Z"}),
            ("not-yet-valid", {"valid_from": "2026-06-06T00:00:00Z"}),
            ("reversed", {"valid_from": "2026-06-12T00:00:00Z", "valid_until": "2026-06-11T00:00:00Z"}),
        ]
        for label, kwargs in validity_cases:
            bad_policy = policy_td_path / f"bad-policy-{label}.json"
            mutate_policy_lockfile_validity(VERIFICATION_POLICY_LOCKFILE, bad_policy, **kwargs)
            matching_policy_receipt = policy_td_path / f"bad-policy-{label}-matching-receipt.json"
            write_matching_policy_lockfile_receipt(VERIFICATION_POLICY_LOCKFILE_RECEIPT, bad_policy, matching_policy_receipt)
            bad_policy_report = run_policy_lockfile_report(
                THRESHOLD_FIXTURE,
                bad_policy,
                "sha256:" + sha256_file(bad_policy),
                matching_policy_receipt,
                "sha256:" + sha256_file(matching_policy_receipt),
                True,
            )
            if bad_policy_report.get("authentication_status") != "SIGNATURE_FAILED":
                fail(f"verification policy lockfile with {label} validity should fail")
            require_code(bad_policy_report, "signature_verification_policy_lockfile_validity_invalid")

        selector_cases = [
            ("wrong-packet", {"packet_id": "other_packet"}),
            ("wrong-election", {"election_id": "OTHER-ELECTION"}),
            ("wrong-jurisdiction", {"jurisdiction": "OTHER-JURISDICTION"}),
            ("missing-packet", {"packet_id": "__DELETE__"}),
        ]
        for label, changes in selector_cases:
            bad_policy = policy_td_path / f"bad-policy-{label}.json"
            mutate_policy_lockfile_selector(VERIFICATION_POLICY_LOCKFILE, bad_policy, **changes)
            matching_policy_receipt = policy_td_path / f"bad-policy-{label}-matching-receipt.json"
            write_matching_policy_lockfile_receipt(VERIFICATION_POLICY_LOCKFILE_RECEIPT, bad_policy, matching_policy_receipt)
            bad_policy_report = run_policy_lockfile_report(
                THRESHOLD_FIXTURE,
                bad_policy,
                "sha256:" + sha256_file(bad_policy),
                matching_policy_receipt,
                "sha256:" + sha256_file(matching_policy_receipt),
                True,
            )
            if bad_policy_report.get("authentication_status") != "SIGNATURE_FAILED":
                fail(f"verification policy lockfile with {label} selector should fail")
            require_code(bad_policy_report, "signature_verification_policy_lockfile_packet_selector_mismatch")

        mixed_scope_packet = policy_td_path / THRESHOLD_FIXTURE.name
        mutate_packet_manifest_scope(THRESHOLD_FIXTURE, mixed_scope_packet, election_id="OTHER-ELECTION", jurisdiction="OTHER-JURISDICTION", ambiguous=True)
        mixed_scope_report = run_policy_lockfile_report(
            mixed_scope_packet,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
        )
        if mixed_scope_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile should reject ambiguous mixed-scope packet metadata")
        mixed_scope_sv = mixed_scope_report.get("signature_verification", {})
        if mixed_scope_sv.get("verification_policy_lockfile_packet_selector_scope_consistency_status") != "ambiguous_or_mismatched":
            fail(f"mixed-scope packet did not publish ambiguous selector status: {mixed_scope_sv!r}")
        require_code(mixed_scope_report, "signature_verification_policy_lockfile_packet_selector_mismatch")

        mixed_packet_id_dir = policy_td_path / "mixed-packet-id"
        shutil.copytree(THRESHOLD_FIXTURE, mixed_packet_id_dir)
        mpath = mixed_packet_id_dir / "manifest.json"
        mobj = json.loads(mpath.read_text(encoding="utf-8"))
        mobj["packet_id"] = THRESHOLD_FIXTURE.name
        write_json(mpath, mobj)
        mixed_packet_id_report = run_policy_lockfile_report(
            mixed_packet_id_dir,
            VERIFICATION_POLICY_LOCKFILE,
            expected_verification_policy_lockfile_pin,
        )
        if mixed_packet_id_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("verification policy lockfile should reject packet directory/name ambiguity")
        require_code(mixed_packet_id_report, "signature_verification_policy_lockfile_packet_selector_mismatch")

    strict_weak_keyset_only = run_report(
        FIXTURE,
        KEYRING,
        "",
        auth_profile="strict-local-trust-chain-v1",
    )
    if strict_weak_keyset_only.get("authentication_status") != "SIGNATURE_FAILED":
        fail("strict auth profile should reject keyset-only verification")
    require_code(strict_weak_keyset_only, "signature_trust_keyset_receipt_invalid")

    strict_missing_pin = run_report(
        THRESHOLD_FIXTURE,
        THRESHOLD_KEYRING,
        "",
        THRESHOLD_RECEIPT,
        False,
        GOVERNANCE_BUNDLE,
        False,
        expected_governance_pin,
        GOVERNANCE_BUNDLE_RECEIPT,
        False,
        expected_governance_receipt_pin,
        STATUS_SNAPSHOT,
        False,
        expected_status_snapshot_pin,
        STATUS_SNAPSHOT_RECEIPT,
        False,
        expected_status_snapshot_receipt_pin,
        keyset_receipt_sha256=expected_keyset_receipt_pin,
        auth_profile="strict-local-trust-chain-v1",
    )
    if strict_missing_pin.get("authentication_status") != "SIGNATURE_FAILED":
        fail("strict auth profile should reject missing trust-keyset pin")
    require_code(strict_missing_pin, "signature_auth_profile_not_met")

    missing_receipt = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, expected_threshold_pin, None, True)
    if missing_receipt.get("authentication_status") != "SIGNATURE_FAILED":
        fail("require-trust-keyset-receipt without receipt should fail")
    require_code(missing_receipt, "signature_trust_keyset_receipt_invalid")

    missing_governance_receipt = run_report(
        THRESHOLD_FIXTURE,
        THRESHOLD_KEYRING,
        expected_threshold_pin,
        THRESHOLD_RECEIPT,
        True,
        GOVERNANCE_BUNDLE,
        True,
        expected_governance_pin,
        None,
        True,
    )
    if missing_governance_receipt.get("authentication_status") != "SIGNATURE_FAILED":
        fail("require-trust-governance-bundle-receipt without receipt should fail")
    require_code(missing_governance_receipt, "signature_trust_governance_bundle_receipt_invalid")

    missing_status_snapshot = run_report(
        THRESHOLD_FIXTURE,
        THRESHOLD_KEYRING,
        expected_threshold_pin,
        THRESHOLD_RECEIPT,
        True,
        GOVERNANCE_BUNDLE,
        True,
        expected_governance_pin,
        GOVERNANCE_BUNDLE_RECEIPT,
        True,
        expected_governance_receipt_pin,
        None,
        True,
    )
    if missing_status_snapshot.get("authentication_status") != "SIGNATURE_FAILED":
        fail("require-trust-status-snapshot without snapshot should fail")
    require_code(missing_status_snapshot, "signature_trust_status_snapshot_invalid")

    missing_status_receipt = run_report(
        THRESHOLD_FIXTURE,
        THRESHOLD_KEYRING,
        expected_threshold_pin,
        THRESHOLD_RECEIPT,
        True,
        GOVERNANCE_BUNDLE,
        True,
        expected_governance_pin,
        GOVERNANCE_BUNDLE_RECEIPT,
        True,
        expected_governance_receipt_pin,
        STATUS_SNAPSHOT,
        True,
        expected_status_snapshot_pin,
        None,
        True,
    )
    if missing_status_receipt.get("authentication_status") != "SIGNATURE_FAILED":
        fail("require-trust-status-snapshot-receipt without receipt should fail")
    require_code(missing_status_receipt, "signature_trust_status_snapshot_receipt_invalid")

    bad_governance_receipt_pin = run_report(
        THRESHOLD_FIXTURE,
        THRESHOLD_KEYRING,
        expected_threshold_pin,
        THRESHOLD_RECEIPT,
        True,
        GOVERNANCE_BUNDLE,
        True,
        expected_governance_pin,
        GOVERNANCE_BUNDLE_RECEIPT,
        True,
        "sha256:" + ("6" * 64),
    )
    if bad_governance_receipt_pin.get("authentication_status") != "SIGNATURE_FAILED":
        fail("governance-bundle publication-receipt pin mismatch should fail")
    require_code(bad_governance_receipt_pin, "signature_trust_governance_bundle_receipt_pin_mismatch")

    rotated = run_report(FIXTURE, ROTATED_RETIRED_KEYRING)
    if rotated.get("authentication_status") != "SIGNATURE_VERIFIED":
        fail(f"retired historical key should still verify old envelope; got {rotated.get('authentication_status')!r}; problems={rotated.get('problems')!r}")

    with tempfile.TemporaryDirectory(prefix="tes_sig_verify_") as td:
        tdpath = Path(td)

        mismatched_pin = "sha256:" + ("0" * 64)
        mismatch_report = run_report(FIXTURE, KEYRING, mismatched_pin)
        if mismatch_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail(f"pin-mismatch authn should fail; got {mismatch_report.get('authentication_status')!r}")
        require_code(mismatch_report, "signature_trust_keyset_pin_mismatch")
        mismatch_sv = mismatch_report.get("signature_verification", {})
        if mismatch_sv.get("trust_keyset_pin_status") != "mismatched":
            fail("pin-mismatch report did not publish trust_keyset_pin_status=mismatched")

        invalid_pin_report = run_report(FIXTURE, KEYRING, "sha256:not-a-valid-pin")
        if invalid_pin_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail(f"invalid-pin authn should fail; got {invalid_pin_report.get('authentication_status')!r}")
        require_code(invalid_pin_report, "signature_trust_keyset_pin_invalid")

        repeated_signature_packet = tdpath / "threshold-repeated-signature-packet"
        mutate_threshold_packet_single_signature(THRESHOLD_FIXTURE, repeated_signature_packet)
        repeated_report = run_report(repeated_signature_packet, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True)
        if repeated_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("repeating one key/signature should not satisfy threshold=2")
        require_code(repeated_report, "signature_threshold_not_met")

        bad_receipt = tdpath / "bad-receipt.json"
        mutate_receipt_digest(THRESHOLD_RECEIPT, bad_receipt)
        bad_receipt_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), bad_receipt, True)
        if bad_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("receipt/keyset digest mismatch should fail")
        require_code(bad_receipt_report, "signature_trust_keyset_receipt_digest_mismatch")

        weak_receipt = tdpath / "weak-receipt.json"
        mutate_receipt_single_channel(THRESHOLD_RECEIPT, weak_receipt)
        weak_receipt_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), weak_receipt, True)
        if weak_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("single-channel receipt should fail channel quorum")
        require_code(weak_receipt_report, "signature_trust_keyset_receipt_channel_quorum_not_met")

        same_type_receipt = tdpath / "same-type-trust-keyset-receipt.json"
        mutate_receipt_same_channel_type(THRESHOLD_RECEIPT, same_type_receipt)
        same_type_receipt_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), same_type_receipt, True)
        if same_type_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("same-type trust-keyset receipt quorum should fail channel diversity")
        require_code(same_type_receipt_report, "signature_trust_keyset_receipt_channel_diversity_not_met")

        packet_receipt_packet = tdpath / "packet-contained-receipt-packet"
        shutil.copytree(THRESHOLD_FIXTURE, packet_receipt_packet)
        packet_receipt = packet_receipt_packet / "trust-keyset-receipt.json"
        shutil.copy2(THRESHOLD_RECEIPT, packet_receipt)
        packet_receipt_report = run_report(packet_receipt_packet, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), packet_receipt, True)
        if packet_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("packet-contained receipt should fail")
        require_code(packet_receipt_report, "signature_trust_keyset_receipt_untrusted_location")

        bad_governance_bundle_receipt = tdpath / "bad-governance-bundle-receipt.json"
        mutate_governance_bundle_receipt_digest(GOVERNANCE_BUNDLE_RECEIPT, bad_governance_bundle_receipt)
        bad_governance_bundle_receipt_report = run_report(
            THRESHOLD_FIXTURE,
            THRESHOLD_KEYRING,
            "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            bad_governance_bundle_receipt,
            True,
        )
        if bad_governance_bundle_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("governance-bundle publication receipt digest mismatch should fail")
        require_code(bad_governance_bundle_receipt_report, "signature_trust_governance_bundle_receipt_digest_mismatch")

        weak_governance_bundle_receipt = tdpath / "weak-governance-bundle-receipt.json"
        mutate_governance_bundle_receipt_single_channel(GOVERNANCE_BUNDLE_RECEIPT, weak_governance_bundle_receipt)
        weak_governance_bundle_receipt_report = run_report(
            THRESHOLD_FIXTURE,
            THRESHOLD_KEYRING,
            "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            weak_governance_bundle_receipt,
            True,
        )
        if weak_governance_bundle_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("governance-bundle publication receipt single-channel quorum should fail")
        require_code(weak_governance_bundle_receipt_report, "signature_trust_governance_bundle_receipt_channel_quorum_not_met")

        same_type_governance_bundle_receipt = tdpath / "same-type-governance-bundle-receipt.json"
        mutate_receipt_same_channel_type(GOVERNANCE_BUNDLE_RECEIPT, same_type_governance_bundle_receipt)
        same_type_governance_bundle_receipt_report = run_report(
            THRESHOLD_FIXTURE,
            THRESHOLD_KEYRING,
            "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            same_type_governance_bundle_receipt,
            True,
        )
        if same_type_governance_bundle_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("same-type governance-bundle receipt quorum should fail channel diversity")
        require_code(same_type_governance_bundle_receipt_report, "signature_trust_governance_bundle_receipt_channel_diversity_not_met")

        packet_governance_receipt_packet = tdpath / "packet-contained-governance-receipt-packet"
        shutil.copytree(THRESHOLD_FIXTURE, packet_governance_receipt_packet)
        packet_governance_receipt = packet_governance_receipt_packet / "trust-governance-bundle-receipt.json"
        shutil.copy2(GOVERNANCE_BUNDLE_RECEIPT, packet_governance_receipt)
        packet_governance_receipt_report = run_report(
            packet_governance_receipt_packet,
            THRESHOLD_KEYRING,
            "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            packet_governance_receipt,
            True,
        )
        if packet_governance_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("packet-contained governance-bundle publication receipt should fail")
        require_code(packet_governance_receipt_report, "signature_trust_governance_bundle_receipt_untrusted_location")

        bad_status_pin = run_report(
            THRESHOLD_FIXTURE,
            THRESHOLD_KEYRING,
            "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT,
            True,
            "sha256:" + ("9" * 64),
        )
        if bad_status_pin.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot pin mismatch should fail")
        require_code(bad_status_pin, "signature_trust_status_snapshot_pin_mismatch")

        packet_status_snapshot_packet = tdpath / "packet-contained-status-snapshot-packet"
        shutil.copytree(THRESHOLD_FIXTURE, packet_status_snapshot_packet)
        packet_status_snapshot = packet_status_snapshot_packet / "trust-status-snapshot.json"
        shutil.copy2(STATUS_SNAPSHOT, packet_status_snapshot)
        packet_status_report = run_report(
            packet_status_snapshot_packet,
            THRESHOLD_KEYRING,
            "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            packet_status_snapshot,
            True,
        )
        if packet_status_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("packet-contained trust-status snapshot should fail")
        require_code(packet_status_report, "signature_trust_status_snapshot_untrusted_location")

        bad_status_receipt_pin = run_report(
            THRESHOLD_FIXTURE,
            THRESHOLD_KEYRING,
            "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT,
            True,
            "sha256:" + sha256_file(STATUS_SNAPSHOT),
            STATUS_SNAPSHOT_RECEIPT,
            True,
            "sha256:" + ("8" * 64),
        )
        if bad_status_receipt_pin.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot publication-receipt pin mismatch should fail")
        require_code(bad_status_receipt_pin, "signature_trust_status_snapshot_receipt_pin_mismatch")

        bad_status_receipt = tdpath / "bad-status-snapshot-receipt.json"
        mutate_status_snapshot_receipt_digest(STATUS_SNAPSHOT_RECEIPT, bad_status_receipt)
        bad_status_receipt_report = run_report(
            THRESHOLD_FIXTURE,
            THRESHOLD_KEYRING,
            "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT,
            True,
            "sha256:" + sha256_file(STATUS_SNAPSHOT),
            bad_status_receipt,
            True,
        )
        if bad_status_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot publication receipt digest mismatch should fail")
        require_code(bad_status_receipt_report, "signature_trust_status_snapshot_receipt_digest_mismatch")

        weak_status_receipt = tdpath / "weak-status-snapshot-receipt.json"
        mutate_status_snapshot_receipt_single_channel(STATUS_SNAPSHOT_RECEIPT, weak_status_receipt)
        weak_status_receipt_report = run_report(
            THRESHOLD_FIXTURE,
            THRESHOLD_KEYRING,
            "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT,
            True,
            "sha256:" + sha256_file(STATUS_SNAPSHOT),
            weak_status_receipt,
            True,
        )
        if weak_status_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot publication receipt single-channel quorum should fail")
        require_code(weak_status_receipt_report, "signature_trust_status_snapshot_receipt_channel_quorum_not_met")

        same_type_status_receipt = tdpath / "same-type-status-snapshot-receipt.json"
        mutate_receipt_same_channel_type(STATUS_SNAPSHOT_RECEIPT, same_type_status_receipt)
        same_type_status_receipt_report = run_report(
            THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT, True, "sha256:" + sha256_file(STATUS_SNAPSHOT),
            same_type_status_receipt, True, "sha256:" + sha256_file(same_type_status_receipt),
        )
        if same_type_status_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("same-type status-snapshot receipt quorum should fail channel diversity")
        require_code(same_type_status_receipt_report, "signature_trust_status_snapshot_receipt_channel_diversity_not_met")

        duplicate_route_status_receipt = tdpath / "duplicate-route-status-snapshot-receipt.json"
        mutate_receipt_duplicate_route(STATUS_SNAPSHOT_RECEIPT, duplicate_route_status_receipt)
        duplicate_route_status_receipt_report = run_report(
            THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT, True, "sha256:" + sha256_file(STATUS_SNAPSHOT),
            duplicate_route_status_receipt, True, "sha256:" + sha256_file(duplicate_route_status_receipt),
        )
        if duplicate_route_status_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("duplicate-route status-snapshot receipt quorum should fail channel diversity")
        require_code(duplicate_route_status_receipt_report, "signature_trust_status_snapshot_receipt_channel_diversity_not_met")

        missing_status_receipt_window = tdpath / "missing-status-receipt-window.json"
        mutate_status_snapshot_receipt_validity(STATUS_SNAPSHOT_RECEIPT, missing_status_receipt_window, remove=True)
        missing_status_receipt_window_report = run_report(
            THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT, True, "sha256:" + sha256_file(STATUS_SNAPSHOT),
            missing_status_receipt_window, True, "sha256:" + sha256_file(missing_status_receipt_window),
        )
        if missing_status_receipt_window_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot publication receipt without validity window should fail")
        require_code(missing_status_receipt_window_report, "signature_trust_status_snapshot_receipt_temporal_invalid")

        expired_status_receipt = tdpath / "expired-status-receipt.json"
        mutate_status_snapshot_receipt_validity(STATUS_SNAPSHOT_RECEIPT, expired_status_receipt, valid_until="2026-06-05T02:00:00Z")
        expired_status_receipt_report = run_report(
            THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT, True, "sha256:" + sha256_file(STATUS_SNAPSHOT),
            expired_status_receipt, True, "sha256:" + sha256_file(expired_status_receipt),
        )
        if expired_status_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("expired trust-status snapshot publication receipt should fail")
        require_code(expired_status_receipt_report, "signature_trust_status_snapshot_receipt_temporal_invalid")

        predating_status_receipt = tdpath / "predating-status-receipt.json"
        mutate_status_snapshot_receipt_predates_snapshot(STATUS_SNAPSHOT_RECEIPT, predating_status_receipt)
        predating_status_receipt_report = run_report(
            THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT, True, "sha256:" + sha256_file(STATUS_SNAPSHOT),
            predating_status_receipt, True, "sha256:" + sha256_file(predating_status_receipt),
        )
        if predating_status_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot publication receipt predating snapshot update should fail")
        require_code(predating_status_receipt_report, "signature_trust_status_snapshot_receipt_temporal_invalid")

        status_receipt_before_channel = tdpath / "status-receipt-issued-before-latest-channel.json"
        mutate_status_snapshot_receipt_issued_before_latest_channel(STATUS_SNAPSHOT_RECEIPT, status_receipt_before_channel)
        status_receipt_before_channel_report = run_report(
            THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT, True, "sha256:" + sha256_file(STATUS_SNAPSHOT),
            status_receipt_before_channel, True, "sha256:" + sha256_file(status_receipt_before_channel),
        )
        if status_receipt_before_channel_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot publication receipt issued before latest channel should fail")
        require_code(status_receipt_before_channel_report, "signature_trust_status_snapshot_receipt_temporal_invalid")

        future_status_receipt_channel = tdpath / "future-status-receipt-channel.json"
        mutate_status_snapshot_receipt_future_channel(STATUS_SNAPSHOT_RECEIPT, future_status_receipt_channel)
        future_status_receipt_channel_report = run_report(
            THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT, True, "sha256:" + sha256_file(STATUS_SNAPSHOT),
            future_status_receipt_channel, True, "sha256:" + sha256_file(future_status_receipt_channel),
        )
        if future_status_receipt_channel_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("future-dated trust-status snapshot publication channel should fail")
        require_code(future_status_receipt_channel_report, "signature_trust_status_snapshot_receipt_temporal_invalid")

        packet_status_receipt_packet = tdpath / "packet-contained-status-receipt-packet"
        shutil.copytree(THRESHOLD_FIXTURE, packet_status_receipt_packet)
        packet_status_receipt = packet_status_receipt_packet / "trust-status-snapshot-receipt.json"
        shutil.copy2(STATUS_SNAPSHOT_RECEIPT, packet_status_receipt)
        packet_status_receipt_report = run_report(
            packet_status_receipt_packet,
            THRESHOLD_KEYRING,
            "sha256:" + sha256_file(THRESHOLD_KEYRING),
            THRESHOLD_RECEIPT,
            True,
            GOVERNANCE_BUNDLE,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE),
            GOVERNANCE_BUNDLE_RECEIPT,
            True,
            "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT),
            STATUS_SNAPSHOT,
            True,
            "sha256:" + sha256_file(STATUS_SNAPSHOT),
            packet_status_receipt,
            True,
        )
        if packet_status_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("packet-contained trust-status snapshot publication receipt should fail")
        require_code(packet_status_receipt_report, "signature_trust_status_snapshot_receipt_untrusted_location")

        missing_signer_roster = run_strict_authorized(roster=None, roster_pin="")
        if missing_signer_roster.get("authentication_status") != "SIGNATURE_FAILED":
            fail("strict authorized profile without signer-authorization roster should fail")
        require_code(missing_signer_roster, "signature_signer_authorization_roster_invalid")

        bad_signer_roster_pin = run_strict_authorized(
            roster=SIGNER_AUTHORIZATION_ROSTER,
            roster_pin="sha256:" + ("d" * 64),
        )
        if bad_signer_roster_pin.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster pin mismatch should fail")
        require_code(bad_signer_roster_pin, "signature_signer_authorization_roster_pin_mismatch")

        packet_signer_roster_packet = tdpath / "packet-contained-signer-authorization-packet"
        shutil.copytree(THRESHOLD_FIXTURE, packet_signer_roster_packet)
        packet_signer_roster = packet_signer_roster_packet / "signer-authorization-roster.json"
        shutil.copy2(SIGNER_AUTHORIZATION_ROSTER, packet_signer_roster)
        packet_signer_roster_report = run_strict_authorized(
            roster=packet_signer_roster,
            roster_pin=expected_signer_authorization_roster_pin,
            packet_dir=packet_signer_roster_packet,
        )
        if packet_signer_roster_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("packet-contained signer-authorization roster should fail")
        require_code(packet_signer_roster_report, "signature_signer_authorization_roster_untrusted_location")

        missing_roster_window = tdpath / "missing-signer-authorization-roster-window.json"
        mutate_signer_authorization_remove_roster_window(SIGNER_AUTHORIZATION_ROSTER, missing_roster_window)
        missing_roster_window_report = run_roster_temporal_check(roster=missing_roster_window, roster_pin="sha256:" + sha256_file(missing_roster_window))
        if missing_roster_window_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster without a validity window should fail")
        require_code(missing_roster_window_report, "signature_signer_authorization_roster_temporal_invalid")

        future_roster = tdpath / "future-signer-authorization-roster.json"
        mutate_signer_authorization_future_roster(SIGNER_AUTHORIZATION_ROSTER, future_roster)
        future_roster_report = run_roster_temporal_check(roster=future_roster, roster_pin="sha256:" + sha256_file(future_roster))
        if future_roster_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("future-dated signer-authorization roster should fail")
        require_code(future_roster_report, "signature_signer_authorization_roster_temporal_invalid")

        expired_roster_window = tdpath / "expired-signer-authorization-roster-window.json"
        mutate_signer_authorization_expired_roster_window(SIGNER_AUTHORIZATION_ROSTER, expired_roster_window)
        expired_roster_window_report = run_roster_temporal_check(roster=expired_roster_window, roster_pin="sha256:" + sha256_file(expired_roster_window))
        if expired_roster_window_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster outside verifier time should fail")
        require_code(expired_roster_window_report, "signature_signer_authorization_roster_temporal_invalid")

        future_authority_observation = tdpath / "future-signer-authorization-authority-observation.json"
        mutate_signer_authorization_future_authority_observation(SIGNER_AUTHORIZATION_ROSTER, future_authority_observation)
        future_authority_observation_report = run_roster_temporal_check(roster=future_authority_observation, roster_pin="sha256:" + sha256_file(future_authority_observation))
        if future_authority_observation_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization authority observation after roster issuance should fail")
        require_code(future_authority_observation_report, "signature_signer_authorization_roster_temporal_invalid")

        missing_row_window = tdpath / "missing-signer-authorization-row-window.json"
        mutate_signer_authorization_remove_row_window(SIGNER_AUTHORIZATION_ROSTER, missing_row_window)
        missing_row_window_report = run_roster_temporal_check(roster=missing_row_window, roster_pin="sha256:" + sha256_file(missing_row_window))
        if missing_row_window_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization row without a bounded authorization window should fail")
        require_code(missing_row_window_report, "signature_signer_authorization_time_invalid")

        packet_policy_packet = tdpath / "packet-contained-verification-policy-packet"
        shutil.copytree(THRESHOLD_FIXTURE, packet_policy_packet)
        packet_policy = packet_policy_packet / "verification-policy-lockfile.json"
        shutil.copy2(VERIFICATION_POLICY_LOCKFILE, packet_policy)
        packet_policy_report = run_policy_lockfile_report(
            packet_policy_packet,
            packet_policy,
            expected_verification_policy_lockfile_pin,
        )
        if packet_policy_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("packet-contained verification policy lockfile should fail")
        require_code(packet_policy_report, "signature_verification_policy_lockfile_untrusted_location")

        bad_signer_keyset = tdpath / "bad-signer-authorization-keyset-digest.json"
        mutate_signer_authorization_keyset_digest(SIGNER_AUTHORIZATION_ROSTER, bad_signer_keyset)
        bad_signer_keyset_report = run_roster_temporal_check(bad_signer_keyset, "sha256:" + sha256_file(bad_signer_keyset))
        if bad_signer_keyset_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster with wrong trust-keyset digest should fail")
        require_code(bad_signer_keyset_report, "signature_signer_authorization_key_mismatch")

        bad_signer_status = tdpath / "bad-signer-authorization-status-digest.json"
        mutate_signer_authorization_status_digest(SIGNER_AUTHORIZATION_ROSTER, bad_signer_status)
        bad_signer_status_report = run_roster_temporal_check(bad_signer_status, "sha256:" + sha256_file(bad_signer_status))
        if bad_signer_status_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster with wrong status-snapshot digest should fail")
        require_code(bad_signer_status_report, "signature_signer_authorization_key_mismatch")

        weak_signer_authority = tdpath / "weak-signer-authorization-authority.json"
        mutate_signer_authorization_single_authority(SIGNER_AUTHORIZATION_ROSTER, weak_signer_authority)
        weak_signer_authority_report = run_roster_temporal_check(weak_signer_authority, "sha256:" + sha256_file(weak_signer_authority))
        if weak_signer_authority_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster with weak authority quorum should fail")
        require_code(weak_signer_authority_report, "signature_signer_authorization_authority_quorum_not_met")

        missing_signer_key = tdpath / "missing-signer-authorization-key.json"
        mutate_signer_authorization_remove_key(SIGNER_AUTHORIZATION_ROSTER, missing_signer_key)
        missing_signer_key_report = run_roster_temporal_check(missing_signer_key, "sha256:" + sha256_file(missing_signer_key))
        if missing_signer_key_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster missing an active signing key should fail")
        require_code(missing_signer_key_report, "signature_signer_authorization_missing")

        disallowed_signer_kind = tdpath / "disallowed-signer-authorization-kind.json"
        mutate_signer_authorization_disallowed_kind(SIGNER_AUTHORIZATION_ROSTER, disallowed_signer_kind)
        disallowed_signer_kind_report = run_roster_temporal_check(disallowed_signer_kind, "sha256:" + sha256_file(disallowed_signer_kind))
        if disallowed_signer_kind_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster that disallows the envelope kind should fail")
        require_code(disallowed_signer_kind_report, "signature_signer_authorization_kind_not_allowed")

        expired_signer = tdpath / "expired-signer-authorization.json"
        mutate_signer_authorization_expired(SIGNER_AUTHORIZATION_ROSTER, expired_signer)
        expired_signer_report = run_roster_temporal_check(expired_signer, "sha256:" + sha256_file(expired_signer))
        if expired_signer_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster with expired authorization should fail")
        require_code(expired_signer_report, "signature_signer_authorization_time_invalid")

        bad_signer_pk = tdpath / "bad-signer-authorization-public-key.json"
        mutate_signer_authorization_public_key(SIGNER_AUTHORIZATION_ROSTER, bad_signer_pk)
        bad_signer_pk_report = run_roster_temporal_check(bad_signer_pk, "sha256:" + sha256_file(bad_signer_pk))
        if bad_signer_pk_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("signer-authorization roster with wrong public-key digest should fail")
        require_code(bad_signer_pk_report, "signature_signer_authorization_key_mismatch")

        stale_status = tdpath / "stale-status-snapshot.json"
        mutate_status_snapshot_stale(STATUS_SNAPSHOT, stale_status)
        stale_status_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE), GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT), stale_status, True)
        if stale_status_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("stale trust-status snapshot should fail")
        require_code(stale_status_report, "signature_trust_status_snapshot_stale")

        revoked_status = tdpath / "revoked-status-snapshot.json"
        mutate_status_snapshot_revoke_active_key(STATUS_SNAPSHOT, revoked_status)
        revoked_status_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE), GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT), revoked_status, True)
        if revoked_status_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot that revokes an active signer should fail")
        require_code(revoked_status_report, "signature_trust_status_snapshot_key_revoked")

        missing_status_key = tdpath / "missing-key-status-snapshot.json"
        mutate_status_snapshot_remove_key(STATUS_SNAPSHOT, missing_status_key)
        missing_status_key_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE), GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT), missing_status_key, True)
        if missing_status_key_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot missing an active key status should fail")
        require_code(missing_status_key_report, "signature_trust_status_snapshot_key_missing")

        wrong_status_keyset = tdpath / "wrong-keyset-status-snapshot.json"
        mutate_status_snapshot_keyset_digest(STATUS_SNAPSHOT, wrong_status_keyset)
        wrong_status_keyset_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE), GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT), wrong_status_keyset, True)
        if wrong_status_keyset_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot with wrong keyset digest should fail")
        require_code(wrong_status_keyset_report, "signature_trust_status_snapshot_keyset_mismatch")

        wrong_status_governance = tdpath / "wrong-governance-status-snapshot.json"
        mutate_status_snapshot_governance_digest(STATUS_SNAPSHOT, wrong_status_governance)
        wrong_status_governance_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE), GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT), wrong_status_governance, True)
        if wrong_status_governance_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot with wrong governance digest should fail")
        require_code(wrong_status_governance_report, "signature_trust_status_snapshot_governance_mismatch")

        weak_status_authority = tdpath / "weak-status-authority-snapshot.json"
        mutate_status_snapshot_single_authority(STATUS_SNAPSHOT, weak_status_authority)
        weak_status_authority_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE), GOVERNANCE_BUNDLE_RECEIPT, True, "sha256:" + sha256_file(GOVERNANCE_BUNDLE_RECEIPT), weak_status_authority, True)
        if weak_status_authority_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("trust-status snapshot with weak authority quorum should fail")
        require_code(weak_status_authority_report, "signature_trust_status_snapshot_authority_quorum_not_met")

        missing_governance = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, None, True)
        if missing_governance.get("authentication_status") != "SIGNATURE_FAILED":
            fail("require-trust-governance-bundle without bundle should fail")
        require_code(missing_governance, "signature_trust_governance_bundle_invalid")

        bad_governance_pin = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, GOVERNANCE_BUNDLE, True, "sha256:" + ("4" * 64))
        if bad_governance_pin.get("authentication_status") != "SIGNATURE_FAILED":
            fail("governance-bundle pin mismatch should fail")
        require_code(bad_governance_pin, "signature_trust_governance_bundle_pin_mismatch")

        packet_governance_packet = tdpath / "packet-contained-governance-packet"
        shutil.copytree(THRESHOLD_FIXTURE, packet_governance_packet)
        packet_governance = packet_governance_packet / "trust-governance-bundle.json"
        shutil.copy2(GOVERNANCE_BUNDLE, packet_governance)
        packet_governance_report = run_report(packet_governance_packet, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, packet_governance, True)
        if packet_governance_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("packet-contained governance bundle should fail")
        require_code(packet_governance_report, "signature_trust_governance_bundle_untrusted_location")

        wrong_governance_keyset = tdpath / "wrong-governance-keyset.json"
        mutate_governance_keyset_digest(GOVERNANCE_BUNDLE, wrong_governance_keyset)
        wrong_governance_keyset_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, wrong_governance_keyset, True)
        if wrong_governance_keyset_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("governance bundle with wrong keyset digest should fail")
        require_code(wrong_governance_keyset_report, "signature_trust_governance_bundle_keyset_mismatch")

        wrong_governance_receipt = tdpath / "wrong-governance-receipt.json"
        mutate_governance_receipt_digest(GOVERNANCE_BUNDLE, wrong_governance_receipt)
        wrong_governance_receipt_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, wrong_governance_receipt, True)
        if wrong_governance_receipt_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("governance bundle with wrong receipt digest should fail")
        require_code(wrong_governance_receipt_report, "signature_trust_governance_bundle_receipt_mismatch")

        weak_governance = tdpath / "weak-governance.json"
        mutate_governance_single_witness(GOVERNANCE_BUNDLE, weak_governance)
        weak_governance_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, weak_governance, True)
        if weak_governance_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("governance bundle with weak witness quorum should fail")
        require_code(weak_governance_report, "signature_trust_governance_bundle_witness_quorum_not_met")

        stale_governance = tdpath / "stale-governance.json"
        mutate_governance_stale(GOVERNANCE_BUNDLE, stale_governance)
        stale_governance_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, stale_governance, True)
        if stale_governance_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("superseded governance bundle should fail")
        require_code(stale_governance_report, "signature_trust_governance_bundle_stale")

        missing_activation = tdpath / "missing-activation-governance.json"
        mutate_governance_remove_activation_event(GOVERNANCE_BUNDLE, missing_activation)
        missing_activation_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, missing_activation, True)
        if missing_activation_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("governance bundle missing active-key activation event should fail")
        require_code(missing_activation_report, "signature_trust_governance_bundle_event_missing")

        missing_rotation = tdpath / "missing-rotation-governance.json"
        mutate_governance_remove_rotation_event(GOVERNANCE_BUNDLE, missing_rotation)
        missing_rotation_report = run_report(THRESHOLD_FIXTURE, THRESHOLD_KEYRING, "sha256:" + sha256_file(THRESHOLD_KEYRING), THRESHOLD_RECEIPT, True, missing_rotation, True)
        if missing_rotation_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail("governance bundle missing rotation/revocation event should fail")
        require_code(missing_rotation_report, "signature_trust_governance_bundle_event_missing")

        tampered_signature = tdpath / "tampered-signature-packet"
        mutate_packet_signature(FIXTURE, tampered_signature)
        tampered_sig_report = run_report(tampered_signature, KEYRING)
        if tampered_sig_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail(f"tampered-signature authn should fail; got {tampered_sig_report.get('authentication_status')!r}")
        require_code(tampered_sig_report, "signature_invalid")
        require_code(tampered_sig_report, "signature_threshold_not_met")

        wrong_key = tdpath / "wrong-keyring.json"
        mutate_keyring_wrong_key(KEYRING, wrong_key)
        wrong_report = run_report(FIXTURE, wrong_key)
        if wrong_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail(f"wrong-key authn should fail; got {wrong_report.get('authentication_status')!r}")
        require_code(wrong_report, "signature_invalid")
        require_code(wrong_report, "signature_threshold_not_met")

        revoked = tdpath / "revoked-keyring.json"
        mutate_keyring_revoked(KEYRING, revoked)
        revoked_report = run_report(FIXTURE, revoked)
        if revoked_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail(f"revoked-key authn should fail; got {revoked_report.get('authentication_status')!r}")
        require_code(revoked_report, "signature_key_revoked")
        require_code(revoked_report, "signature_threshold_not_met")

        expired = tdpath / "expired-keyring.json"
        mutate_keyring_expired(KEYRING, expired)
        expired_report = run_report(FIXTURE, expired)
        if expired_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail(f"expired-key authn should fail; got {expired_report.get('authentication_status')!r}")
        require_code(expired_report, "signature_key_expired")
        require_code(expired_report, "signature_threshold_not_met")

        disallowed = tdpath / "disallowed-kind-keyring.json"
        mutate_keyring_disallowed_kind(KEYRING, disallowed)
        disallowed_report = run_report(FIXTURE, disallowed)
        if disallowed_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail(f"disallowed-kind authn should fail; got {disallowed_report.get('authentication_status')!r}")
        require_code(disallowed_report, "signature_kind_not_allowed")
        require_code(disallowed_report, "signature_threshold_not_met")

        require_report = run_require_auth_without_keyset(FIXTURE)
        if require_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail(f"require-auth without keyset should fail; got {require_report.get('authentication_status')!r}")
        require_code(require_report, "signature_trust_keyset_invalid")

        tampered_packet = tdpath / "tampered-packet"
        mutate_packet_payload(FIXTURE, tampered_packet)
        tampered_report = run_report(tampered_packet, KEYRING)
        if tampered_report.get("status") != "FAIL":
            fail(f"tampered packet should FAIL; got {tampered_report.get('status')!r}")
        if tampered_report.get("authentication_status") != "SIGNATURE_FAILED":
            fail(
                "tampered packet must not report SIGNATURE_VERIFIED; "
                f"got {tampered_report.get('authentication_status')!r}"
            )
        require_code(tampered_report, "object_hash_mismatch")

    print("PASS: Ed25519 trust-keyset verifier positive, trust-keyset pinning, external receipts, threshold quorum, synthetic governance bundle, trust-status snapshot freshness/revocation, status-snapshot publication receipt, signer-authorization roster/receipt temporal and authority-observation gating, exact-scope selector-bound and packet-public-fingerprint-bound, policy-receipt-auto-required/pin-gated, trust-closure-digest-reporting, policy-issued-order-bound and policy-id/selector-bound policy-receipt, verifier/report/profile-bound policy lockfiles, and bounded-validity policy-lockfile paths, self-supplied trust-root/governance/status/authorization, lifecycle, and tamper negative controls")
    return 0


if __name__ == "__main__":
    import os as _os
    import sys as _sys

    _loader = (
        "import importlib.util, os, pathlib, sys; "
        "p=pathlib.Path(sys.argv[1]).resolve(); "
        "sys.path.insert(0, str(p.parent)); "
        "spec=importlib.util.spec_from_file_location('_ed25519_check_impl', p); "
        "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); "
        "rc=int(m.main() or 0); sys.stdout.flush(); sys.stderr.flush(); os._exit(rc)"
    )
    _os.execv(_sys.executable, [_sys.executable, "-u", "-c", _loader, __file__])
