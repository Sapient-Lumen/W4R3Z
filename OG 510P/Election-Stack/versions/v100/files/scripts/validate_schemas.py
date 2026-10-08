#!/usr/bin/env python3
"""scripts/validate_schemas.py

Schema + example validation drift firewall.

Goals:
- Ensure all JSON Schemas under `schemas/` are parseable.
- If the `jsonschema` library is available, validate each schema against its meta-schema.
- If `jsonschema` is available, validate a small set of "ship" examples (templates + packets)
  with format checking enabled.

Rationale:
This archive is intended to survive long-horizon edits (including by LLMs).
Parsing-only checks catch syntax errors; meta-schema + example validation catches
semantic drift (e.g., required fields removed, formats accidentally broken).

Policy:
We do not vendor schema-validation libraries into the archive. If `jsonschema` is not
installed, this script degrades to parse-only mode.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from _shared.registry import read_csv

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"
OFFICIAL_CHANNELS = ROOT / "artifacts" / "registries" / "official-channels.csv"


@dataclass(frozen=True)
class ExampleCase:
    name: str
    instance_path: Path
    schema_path: Path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_example_envelopes() -> Iterable[Path]:
    examples_root = ROOT / "artifacts" / "examples"
    if not examples_root.exists():
        return []
    return sorted(examples_root.glob("evidence_packet_*/envelopes/*.json"))


def load_official_channel_ids() -> set[str]:
    if not OFFICIAL_CHANNELS.exists():
        return set()
    try:
        tbl = read_csv(OFFICIAL_CHANNELS)
        return {r.get("channel_id", "").strip() for r in tbl.rows if r.get("channel_id")}
    except Exception:
        # The registry has its own dedicated drift firewall; keep this best-effort.
        return set()


def payload_from_example_envelope(env_path: Path, env: dict[str, Any]) -> dict[str, Any] | None:
    if isinstance(env.get("payload_inline"), dict):
        return env["payload_inline"]

    pp = env.get("payload_pointer")
    if not isinstance(pp, dict):
        return None
    uri = pp.get("uri")
    if not isinstance(uri, str) or not uri:
        return None

    # Example packets are under artifacts/examples/evidence_packet_*/
    packet_dir = env_path.parent.parent
    obj = (packet_dir / "objects" / uri)
    if not obj.exists():
        return None
    try:
        data = json.loads(obj.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def check_public_notice_channels(payload: Any, known: set[str], label: str, failures: list[str]) -> None:
    if not known:
        return
    if not isinstance(payload, dict):
        return
    ch = payload.get("channels")
    if ch is None:
        return
    if not isinstance(ch, list):
        failures.append(f"{label}: channels must be a list")
        return
    for x in ch:
        cid = str(x).strip()
        if not cid:
            continue
        if cid not in known:
            failures.append(f"{label}: unknown channel_id '{cid}' (not in official-channels.csv)")




def _parse_rfc3339(dt: str) -> datetime | None:
    """Parse an RFC3339-ish timestamp (accepts 'Z')."""

    if not isinstance(dt, str) or not dt.strip():
        return None
    t = dt.strip()
    if t.endswith('Z'):
        t = t[:-1] + '+00:00'
    try:
        out = datetime.fromisoformat(t)
        if out.tzinfo is None:
            # Treat naive timestamps as UTC for drift checks.
            out = out.replace(tzinfo=timezone.utc)
        return out
    except Exception:
        return None


def check_public_notice_next_update_at(payload: Any, label: str, failures: list[str]) -> None:
    """Lightweight sanity checks for next_update_at ordering."""

    if not isinstance(payload, dict):
        return
    nua = payload.get('next_update_at')
    if nua is None:
        return
    if not isinstance(nua, str):
        failures.append(f"{label}: next_update_at must be a string")
        return
    dt_nu = _parse_rfc3339(nua)
    if dt_nu is None:
        failures.append(f"{label}: next_update_at is not parseable RFC3339 date-time: {nua!r}")
        return
    issued = payload.get('issued_at')
    if isinstance(issued, str) and issued.strip():
        dt_issued = _parse_rfc3339(issued)
        if dt_issued is None:
            failures.append(f"{label}: issued_at is not parseable RFC3339 date-time: {issued!r}")
            return
        if dt_nu < dt_issued:
            failures.append(f"{label}: next_update_at precedes issued_at ({nua} < {issued})")


def main() -> int:
    # 1) Parse all schemas.
    schemas: dict[str, Any] = {}
    for p in sorted(SCHEMAS_DIR.glob("*.json")):
        try:
            schemas[p.name] = load_json(p)
        except Exception as e:
            print(f"ERROR: invalid JSON in schema {p.name}: {e}", file=sys.stderr)
            return 2

    print(f"Loaded {len(schemas)} schemas OK.")

    # 2) Lightweight cross-registry checks that should remain stdlib-only.
    channel_failures: list[str] = []
    known_channels = load_official_channel_ids()
    pn_tpl = ROOT / "artifacts" / "templates" / "public-notice-payload.json"
    if pn_tpl.exists():
        try:
            tpl_obj = load_json(pn_tpl)
            check_public_notice_channels(tpl_obj, known_channels, "PublicNotice payload template", channel_failures)
            check_public_notice_next_update_at(tpl_obj, "PublicNotice payload template", channel_failures)
        except Exception as e:
            channel_failures.append(f"PublicNotice payload template: invalid JSON ({e})")

    pn_corr_tpl = ROOT / "artifacts" / "templates" / "public-notice-correction-payload.json"
    if pn_corr_tpl.exists():
        try:
            tpl_obj = load_json(pn_corr_tpl)
            check_public_notice_channels(tpl_obj, known_channels, "PublicNotice correction payload template", channel_failures)
            check_public_notice_next_update_at(tpl_obj, "PublicNotice correction payload template", channel_failures)
        except Exception as e:
            channel_failures.append(f"PublicNotice correction payload template: invalid JSON ({e})")

    pn_rumor_tpl = ROOT / "artifacts" / "templates" / "public-notice-rumor-control-payload.json"
    if pn_rumor_tpl.exists():
        try:
            tpl_obj = load_json(pn_rumor_tpl)
            check_public_notice_channels(tpl_obj, known_channels, "PublicNotice rumor-control payload template", channel_failures)
            check_public_notice_next_update_at(tpl_obj, "PublicNotice rumor-control payload template", channel_failures)
        except Exception as e:
            channel_failures.append(f"PublicNotice rumor-control payload template: invalid JSON ({e})")


    pn_status_tpl = ROOT / "artifacts" / "templates" / "public-notice-status-update-payload.json"
    if pn_status_tpl.exists():
        try:
            tpl_obj = load_json(pn_status_tpl)
            check_public_notice_channels(tpl_obj, known_channels, "PublicNotice status-update payload template", channel_failures)
            check_public_notice_next_update_at(tpl_obj, "PublicNotice status-update payload template", channel_failures)
        except Exception as e:
            channel_failures.append(f"PublicNotice status-update payload template: invalid JSON ({e})")

    for ep in iter_example_envelopes():
        try:
            env = load_json(ep)
        except Exception:
            continue
        if env.get("kind") != "hfv.public.notice":
            continue
        payload = payload_from_example_envelope(ep, env)
        check_public_notice_channels(payload, known_channels, f"example PublicNotice payload ({ep.relative_to(ROOT)})", channel_failures)
        check_public_notice_next_update_at(payload, f"example PublicNotice payload ({ep.relative_to(ROOT)})", channel_failures)

    if channel_failures:
        for e in channel_failures:
            print("ERROR:", e, file=sys.stderr)
        return 2

    # 3) Optional: meta-schema + example validation.
    try:
        import jsonschema  # type: ignore
        from jsonschema import FormatChecker  # type: ignore
        from referencing import Registry, Resource  # type: ignore
    except Exception:
        # Parse-only mode is still useful for catching syntax errors.
        print("jsonschema not available; skipping meta-schema and example validation")
        return 0

    # Build a local registry for $ref resolution (by $id, filename, and repo-relative path).
    reg = Registry()
    for name, schema in schemas.items():
        res = Resource.from_contents(schema)
        sid = schema.get("$id")
        if isinstance(sid, str) and sid:
            reg = reg.with_resource(sid, res)
        reg = reg.with_resource(name, res)
        reg = reg.with_resource(f"schemas/{name}", res)

    # Meta-validate schemas.
    schema_errors: list[str] = []
    for name, schema in schemas.items():
        try:
            v = jsonschema.validators.validator_for(schema)
            v.check_schema(schema)
        except Exception as e:
            schema_errors.append(f"{name}: {e}")

    if schema_errors:
        for e in schema_errors:
            print("ERROR: schema meta-validation failed:", e, file=sys.stderr)
        return 2

    # Validate a small set of "ship" examples.
    fc = FormatChecker()

    cases: list[ExampleCase] = [
        ExampleCase(
            name="PublicNotice payload template",
            instance_path=ROOT / "artifacts" / "templates" / "public-notice-payload.json",
            schema_path=ROOT / "schemas" / "PublicNotice.json",
        ),
        ExampleCase(
            name="PublicNotice correction payload template",
            instance_path=ROOT / "artifacts" / "templates" / "public-notice-correction-payload.json",
            schema_path=ROOT / "schemas" / "PublicNotice.json",
        ),
        ExampleCase(
            name="PublicNotice rumor-control payload template",
            instance_path=ROOT / "artifacts" / "templates" / "public-notice-rumor-control-payload.json",
            schema_path=ROOT / "schemas" / "PublicNotice.json",
        ),
        ExampleCase(
            name="PublicNotice status-update payload template",
            instance_path=ROOT / "artifacts" / "templates" / "public-notice-status-update-payload.json",
            schema_path=ROOT / "schemas" / "PublicNotice.json",
        ),
        ExampleCase(
            name="COI disclosure template",
            instance_path=ROOT / "artifacts" / "templates" / "coi-disclosure-template.json",
            schema_path=ROOT / "schemas" / "COIDisclosure.json",
        ),
        ExampleCase(
            name="PacketVerificationReport example template",
            instance_path=ROOT / "artifacts" / "templates" / "packet-verification-report-example.json",
            schema_path=ROOT / "schemas" / "PacketVerificationReport.json",
        ),
        ExampleCase(
            name="VerifierReport payload template",
            instance_path=ROOT / "artifacts" / "templates" / "verifier-report-payload.json",
            schema_path=ROOT / "schemas" / "VerifierReport.json",
        ),
    ]


    example_failures: list[str] = []
    for c in cases:
        if not c.instance_path.exists():
            continue
        if not c.schema_path.exists():
            example_failures.append(f"{c.name}: missing schema {c.schema_path}")
            continue
        inst = load_json(c.instance_path)
        sch = load_json(c.schema_path)
        v = jsonschema.validators.validator_for(sch)
        validator = v(sch, registry=reg, format_checker=fc)
        errs = sorted(validator.iter_errors(inst), key=lambda e: (list(e.path), e.message))
        for e in errs:
            example_failures.append(f"{c.name}: {c.instance_path.relative_to(ROOT)}: {e.message} at {list(e.path)}")

    # Validate example envelopes (structural + format checking).
    env_schema_path = ROOT / "schemas" / "EvidenceEnvelope.json"
    if env_schema_path.exists():
        esch = load_json(env_schema_path)
        ev = jsonschema.validators.validator_for(esch)
        evalidator = ev(esch, registry=reg, format_checker=fc)

        for ep in iter_example_envelopes():
            env = load_json(ep)
            errs = sorted(evalidator.iter_errors(env), key=lambda e: (list(e.path), e.message))
            for e in errs:
                example_failures.append(
                    f"envelope: {ep.relative_to(ROOT)}: {e.message} at {list(e.path)}"
                )

            # Note: payload validation is intentionally not enforced here yet.
            # Payload schemas and example manifests are still evolving; envelope structural
            # validation catches most drift without forcing premature schema commitments.

    if example_failures:
        for e in example_failures:
            print("ERROR:", e, file=sys.stderr)
        return 2

    print("Schema meta-validation + example validation OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
