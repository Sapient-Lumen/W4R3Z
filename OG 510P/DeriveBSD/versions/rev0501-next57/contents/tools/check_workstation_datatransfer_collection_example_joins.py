#!/usr/bin/env python3
"""Mechanically check the first ui.collection.handoff example stack.

Why:
  - The first richer reviewed finite-collection lane is now spec-shaped enough to
    implement. The example stack should therefore carry real computed joins rather
    than disconnected placeholder digests.
  - This prevents docs/spec drift where collection_digest or grant_digest stop
    meaning the exact portable joins they claim to be.

Rules:
  - manifest.collection_digest == sha256(utf8(JCS(authoritative_manifest)))
  - grant.collection_digest == manifest.collection_digest
  - receipt.collection_digest == manifest.collection_digest
  - receipt.grant_digest == sha256(utf8(JCS(grant_artifact)))
  - grant/receipt stay aligned on lease_id + subject + offer_source_subject
  - receipt.retrieved_at <= grant.effective_until
  - if grant.constraints.expires_at is present, effective_until <= expires_at
  - first-cut receipt keeps grant_exhausted = true
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "spec" / "examples"
HEX64 = re.compile(r"^sha256:[0-9a-f]{64}$")


def _read_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"{p}: failed to parse JSON: {exc}")


def _reject_floats(x, path: str = "$") -> None:
    if isinstance(x, float):
        raise ValueError(f"{path}: floats are not allowed in JCS-hashable examples")
    if isinstance(x, dict):
        for k, v in x.items():
            if not isinstance(k, str):
                raise ValueError(f"{path}: non-string object key {k!r}")
            _reject_floats(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            _reject_floats(v, f"{path}[{i}]")


def _jcs_bytes(obj: dict) -> bytes:
    _reject_floats(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256_jcs(obj: dict) -> str:
    return "sha256:" + hashlib.sha256(_jcs_bytes(obj)).hexdigest()


def _require_hex64(label: str, value: str, problems: list[str]) -> None:
    if not isinstance(value, str) or not HEX64.match(value):
        problems.append(f"{label}: expected sha256:<64hex>, got {value!r}")


def _parse_ts(value: str, label: str, problems: list[str]) -> datetime | None:
    if not isinstance(value, str):
        problems.append(f"{label}: expected ISO8601 string, got {value!r}")
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
    except ValueError:
        problems.append(f"{label}: invalid ISO8601 timestamp {value!r}")
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def main() -> int:
    problems: list[str] = []

    manifest_p = EX / "ui.collection.handoff.manifest.json"
    grant_p = EX / "ui.collection.handoff.grant.json"
    receipt_p = EX / "ui.collection.handoff.receipt.json"

    manifest = _read_json(manifest_p)
    grant = _read_json(grant_p)
    receipt = _read_json(receipt_p)

    if manifest.get("kind") != "ui.collection.handoff.manifest":
        problems.append(f"{manifest_p.name}: kind must be ui.collection.handoff.manifest")
    if grant.get("kind") != "ui.collection.handoff.grant":
        problems.append(f"{grant_p.name}: kind must be ui.collection.handoff.grant")
    if receipt.get("kind") != "ui.collection.handoff.receipt":
        problems.append(f"{receipt_p.name}: kind must be ui.collection.handoff.receipt")

    computed_collection_digest = _sha256_jcs(manifest.get("authoritative_manifest", {}))
    computed_grant_digest = _sha256_jcs(grant)

    _require_hex64("computed collection_digest", computed_collection_digest, problems)
    _require_hex64("computed grant_digest", computed_grant_digest, problems)

    if manifest.get("collection_digest") != computed_collection_digest:
        problems.append(
            f"manifest.collection_digest {manifest.get('collection_digest')!r} != computed {computed_collection_digest}"
        )
    if grant.get("collection_digest") != computed_collection_digest:
        problems.append(
            f"grant.collection_digest {grant.get('collection_digest')!r} != manifest/computed {computed_collection_digest}"
        )
    if receipt.get("collection_digest") != computed_collection_digest:
        problems.append(
            f"receipt.collection_digest {receipt.get('collection_digest')!r} != manifest/computed {computed_collection_digest}"
        )

    if receipt.get("grant_digest") != computed_grant_digest:
        problems.append(
            f"receipt.grant_digest {receipt.get('grant_digest')!r} != computed {computed_grant_digest}"
        )

    if grant.get("lease_id") != receipt.get("lease_id"):
        problems.append(f"lease_id mismatch: grant={grant.get('lease_id')!r} receipt={receipt.get('lease_id')!r}")
    if grant.get("subject") != receipt.get("subject"):
        problems.append("subject mismatch between grant and receipt")
    if grant.get("offer_source_subject") != receipt.get("offer_source_subject"):
        problems.append("offer_source_subject mismatch between grant and receipt")
    if receipt.get("grant_exhausted") is not True:
        problems.append("receipt.grant_exhausted must stay true for the first-cut single-retrieve-autostop lane")

    retrieved_at = _parse_ts(receipt.get("retrieved_at"), "receipt.retrieved_at", problems)
    effective_until = _parse_ts(grant.get("effective_until"), "grant.effective_until", problems)
    expires_at = _parse_ts((grant.get("constraints") or {}).get("expires_at"), "grant.constraints.expires_at", problems) if (grant.get("constraints") or {}).get("expires_at") is not None else None

    if retrieved_at and effective_until and retrieved_at > effective_until:
        problems.append(
            f"receipt.retrieved_at {receipt.get('retrieved_at')!r} must not be later than grant.effective_until {grant.get('effective_until')!r}"
        )
    if effective_until and expires_at and effective_until > expires_at:
        problems.append(
            f"grant.effective_until {grant.get('effective_until')!r} must not be later than constraints.expires_at {grant.get('constraints', {}).get('expires_at')!r}"
        )

    if problems:
        print("workstation transfer collection example joins FAILED")
        for problem in problems:
            print("-", problem)
        print("\nFix: update the ui.collection.handoff examples so collection_digest and grant_digest are real computed joins, not disconnected placeholders.")
        return 1

    print("Workstation transfer collection example joins: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
