#!/usr/bin/env python3
"""scripts/check_packet_verification_report_emit_packet.py

Drift firewall: ensure `tools/observer_verify_packet.py --emit-evidence-object`
actually emits a minimal verifier-report packet that:
- includes a publishable PacketVerificationReport payload with policy_profile_sha256
- repeats policy_profile_sha256 on the EvidenceEnvelope subject (digest-only)
- ships the policy profile bytes as a detached, content-addressed object when
  `--policy-profile <file>` is provided.

This catches a subtle but dangerous failure mode:
- schema/docs say the report packet should carry the policy profile object
- example packets may remain correct
- but the reference tool regresses and stops shipping the object.

No network access; stdlib-only + jsonschema (already used in other drift tests).
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema
from referencing import Registry, Resource
from jsonschema import FormatChecker

sys.path.insert(0, str((Path(__file__).resolve().parents[1]) / "tools"))
from jcs import dump_bytes as jcs_bytes


ROOT = Path(__file__).resolve().parents[1]
VERIFY_TOOL = ROOT / "tools" / "observer_verify_packet.py"
REPORT_SCHEMA = ROOT / "schemas" / "PacketVerificationReport.json"
ENVELOPE_SCHEMA = ROOT / "schemas" / "EvidenceEnvelope.json"
EXAMPLE_PACKET = ROOT / "artifacts" / "examples" / "evidence_packet_minimal"
POLICY_PROFILE = ROOT / "artifacts" / "templates" / "verifier-policy-profile.json"

SHA_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_registry() -> Registry:
    """Build a local $ref registry so validation never fetches network resources."""

    schemas_dir = ROOT / "schemas"
    reg = Registry()
    for sp in sorted(schemas_dir.glob("*.json")):
        try:
            sch = json.loads(sp.read_text(encoding="utf-8"))
        except Exception:
            continue
        res = Resource.from_contents(sch)
        sid = sch.get("$id")
        if isinstance(sid, str) and sid:
            reg = reg.with_resource(sid, res)
        reg = reg.with_resource(sp.name, res)
        reg = reg.with_resource(f"schemas/{sp.name}", res)
    return reg


def validate(obj: dict, schema_path: Path, registry: Registry) -> None:
    schema = load_schema(schema_path)
    v = jsonschema.validators.validator_for(schema)
    validator = v(schema, registry=registry, format_checker=FormatChecker())
    errs = sorted(validator.iter_errors(obj), key=lambda e: (list(e.path), e.message))
    if errs:
        fail("schema validation failed for " + str(schema_path.name) + ": " + "; ".join([f"{e.message} at {list(e.path)}" for e in errs[:5]]))


def find_report_envelope(packet_dir: Path) -> Path:
    env_dir = packet_dir / "envelopes"
    if not env_dir.exists():
        fail("emitted packet missing envelopes/")
    for p in sorted(env_dir.glob("*.json")):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get("kind") == "hfv.verifier.packet_verification_report":
            return p
    fail("could not find hfv.verifier.packet_verification_report envelope in emitted packet")


def load_payload_from_envelope(env: dict, packet_dir: Path) -> dict:
    if "payload_inline" in env:
        if isinstance(env["payload_inline"], dict):
            return env["payload_inline"]
        fail("payload_inline present but not an object")

    ptr = env.get("payload_pointer")
    if not isinstance(ptr, dict):
        fail("envelope missing payload_pointer")
    uri = ptr.get("uri", "")
    if not isinstance(uri, str) or not uri:
        fail("payload_pointer missing uri")
    rel = uri if uri.startswith("objects/") else f"objects/{uri}"
    p = (packet_dir / rel).resolve()
    if not p.exists():
        fail(f"payload object missing: {rel}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"could not parse payload object JSON: {e}")


def main() -> int:
    if not VERIFY_TOOL.exists():
        fail(f"missing verifier tool: {VERIFY_TOOL}")
    if not REPORT_SCHEMA.exists():
        fail(f"missing schema: {REPORT_SCHEMA}")
    if not ENVELOPE_SCHEMA.exists():
        fail(f"missing schema: {ENVELOPE_SCHEMA}")
    if not EXAMPLE_PACKET.exists():
        fail(f"missing example packet: {EXAMPLE_PACKET}")
    if not POLICY_PROFILE.exists():
        fail(f"missing policy profile template: {POLICY_PROFILE}")

    registry = build_registry()

    # Compute expected policy-profile digest (JCS canonical bytes).
    pp_obj = json.loads(POLICY_PROFILE.read_text(encoding="utf-8"))
    pp_bytes = jcs_bytes(pp_obj)
    expected_pp = "sha256:" + sha256_hex(pp_bytes)

    with tempfile.TemporaryDirectory(prefix="tes_emit_packet_") as td:
        out_dir = Path(td) / "out"
        cmd = [
            sys.executable,
            str(VERIFY_TOOL),
            str(EXAMPLE_PACKET),
            "--json",
            "--public",
            "--emit-evidence-object",
            str(out_dir),
            "--policy-profile",
            str(POLICY_PROFILE),
            "--issuer-id",
            "verifier:test",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            fail(f"observer_verify_packet emit failed (rc={proc.returncode}): {proc.stdout.strip()} {proc.stderr.strip()}")

        try:
            report = json.loads(proc.stdout)
        except Exception as e:
            fail(f"could not parse JSON report output: {e}")

        got_pp = report.get("policy_profile_sha256")
        if got_pp != expected_pp:
            fail(f"policy_profile_sha256 mismatch (got={got_pp!r}, want={expected_pp!r})")

        # The emitted packet must exist.
        if not out_dir.exists():
            fail("emit output directory not created")

        # The policy profile object must be shipped under objects/sha256-<hex>.json.
        hexpart = expected_pp.split(":", 1)[1]
        policy_obj = out_dir / "objects" / f"sha256-{hexpart}.json"
        if not policy_obj.exists():
            fail(f"missing shipped policy profile object: {policy_obj.relative_to(out_dir)}")
        if sha256_hex(policy_obj.read_bytes()).lower() != hexpart.lower():
            fail("shipped policy profile object hash does not match filename")

        # Locate the report envelope and validate subject pin.
        env_path = find_report_envelope(out_dir)
        env = json.loads(env_path.read_text(encoding="utf-8"))
        validate(env, ENVELOPE_SCHEMA, registry)

        subj = env.get("subject")
        if not isinstance(subj, dict):
            fail("envelope missing subject")
        subj_pp = subj.get("policy_profile_sha256")
        if subj_pp != expected_pp:
            fail(f"envelope subject policy_profile_sha256 mismatch (got={subj_pp!r}, want={expected_pp!r})")

        payload = load_payload_from_envelope(env, out_dir)
        validate(payload, REPORT_SCHEMA, registry)

        if payload.get("policy_profile_sha256") != expected_pp:
            fail("payload policy_profile_sha256 missing/mismatch")

        # Sanity: key digest pins should be well-formed when present.
        for k in (
            "manifest_sha256",
            "manifest_jcs_sha256",
            "attachment_requirements_sha256",
            "receipt_profiles_sha256",
        ):
            v = payload.get(k)
            if v is not None:
                if not (isinstance(v, str) and SHA_RE.match(v)):
                    fail(f"{k} present but not a sha256:<hex> (got {v!r})")

    print("PASS: emit-evidence-object ships policy profile object + subject pin + schema-valid payload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())