#!/usr/bin/env python3
"""scripts/check_packet_verification_report_linkage.py

Drift firewall: ensure the reference verifier tool actually emits
`PacketVerificationReport.verifier_report_tbs_digest` when requested.

This catches a common failure mode:
- schema + docs add an optional linkage field
- CLI flags are added
- but the emitted report payload forgets to include the field
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import jsonschema  # type: ignore
    from jsonschema import FormatChecker  # type: ignore
except Exception:  # pragma: no cover - exercised in dependency-light release environments
    jsonschema = None  # type: ignore
    FormatChecker = None  # type: ignore

from _cli_harness import run_python_cli


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
VERIFY_TOOL = ROOT / "tools" / "observer_verify_packet.py"
REPORT_SCHEMA = ROOT / "schemas" / "PacketVerificationReport.json"

EXAMPLE_PACKET = ROOT / "artifacts" / "examples" / "evidence_packet_minimal"

LINK_DIGEST = "sha256:" + ("0" * 64)
POLICY_DIGEST = "sha256:" + ("1" * 64)

SHA_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _stdlib_validate_object(obj: dict, schema: dict, label: str) -> None:
    """Small fallback for strict top-level object schemas.

    The release archive does not vendor jsonschema.  In environments where the
    optional dependency is absent, keep this drift firewall useful by enforcing
    the schema constraints this check depends on: required top-level fields,
    additionalProperties=false, and simple top-level JSON types.
    """

    if not isinstance(obj, dict):
        fail(f"{label}: expected object")
    props = schema.get("properties")
    if not isinstance(props, dict):
        return
    required = schema.get("required")
    if isinstance(required, list):
        for k in required:
            if isinstance(k, str) and k not in obj:
                fail(f"{label}: missing required field {k!r}")
    if schema.get("additionalProperties") is False:
        for k in obj:
            if k not in props:
                fail(f"{label}: unknown field {k!r}")
    type_map = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "object": dict,
        "array": list,
    }
    for k, v in obj.items():
        ps = props.get(k)
        if not isinstance(ps, dict):
            continue
        typ = ps.get("type")
        allowed = typ if isinstance(typ, list) else [typ]
        allowed = [x for x in allowed if isinstance(x, str)]
        if "null" in allowed and v is None:
            continue
        concrete = tuple(type_map[x] for x in allowed if x in type_map)
        if concrete and not isinstance(v, concrete):
            fail(f"{label}: field {k!r} has wrong type")


def validate_report_schema(report: dict) -> None:
    schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
    if jsonschema is None:
        _stdlib_validate_object(report, schema, "PacketVerificationReport")
        return
    v = jsonschema.validators.validator_for(schema)
    validator = v(schema, format_checker=FormatChecker())
    errs = sorted(validator.iter_errors(report), key=lambda e: (list(e.path), e.message))
    if errs:
        fail("schema validation failed: " + "; ".join([f"{e.message} at {list(e.path)}" for e in errs[:5]]))


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    if not VERIFY_TOOL.exists():
        fail(f"missing verifier tool: {VERIFY_TOOL}")
    if not REPORT_SCHEMA.exists():
        fail(f"missing schema: {REPORT_SCHEMA}")
    if not EXAMPLE_PACKET.exists():
        fail(f"missing example packet: {EXAMPLE_PACKET}")

    code, out, err = run_python_cli(
        VERIFY_TOOL,
        [
            EXAMPLE_PACKET,
            "--json",
            "--public",
            "--verifier-report-tbs-digest",
            LINK_DIGEST,
            "--policy-profile-sha256",
            POLICY_DIGEST,
        ],
        extra_sys_path=[TOOLS, ROOT],
        cwd=ROOT,
    )
    if code != 0:
        # For this drift test, the example packet should verify cleanly.
        fail(f"observer_verify_packet failed (rc={code}): {out.strip()} {err.strip()}")

    try:
        report = json.loads(out)
    except Exception as e:
        fail(f"could not parse JSON output: {e}")

    got = report.get("verifier_report_tbs_digest")
    if got != LINK_DIGEST:
        fail(f"missing/incorrect verifier_report_tbs_digest (got={got!r}, want={LINK_DIGEST!r})")

    pp = report.get("policy_profile_sha256")
    if pp != POLICY_DIGEST:
        fail(f"missing/incorrect policy_profile_sha256 (got={pp!r}, want={POLICY_DIGEST!r})")

    # Comparability pins should be emitted when the registry files exist.
    # This is a drift firewall: fields are optional in schema but required for
    # the reference tool when running from the repo.
    required_sha_fields = [
        "verifier_problem_codes_sha256",
        "verifier_profiles_sha256",
        "envelope_kinds_sha256",
        "attachment_requirements_sha256",
        "receipt_profiles_sha256",
        "manifest_sha256",
        "manifest_jcs_sha256",
    ]
    for f in required_sha_fields:
        v = report.get(f)
        if not (isinstance(v, str) and SHA_RE.match(v)):
            fail(f"missing/invalid {f} (got={v!r})")

    # Public mode should not leak paths.
    pkt = report.get("packet_dir", "")
    if isinstance(pkt, str) and ("/" in pkt or "\\" in pkt):
        fail(f"public report leaked a path in packet_dir: {pkt!r}")

    # Public mode should emit codes-only problems.
    probs = report.get("problems")
    if isinstance(probs, list):
        for p in probs:
            if isinstance(p, str) and ":" in p:
                fail(f"public report leaked contextual problem string: {p!r}")

    # Validate output against the schema when jsonschema is available; otherwise
    # enforce a strict top-level schema fallback.
    validate_report_schema(report)

    print("PASS: PacketVerificationReport optional linkage + policy-profile pins are emitted and schema-compatible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
