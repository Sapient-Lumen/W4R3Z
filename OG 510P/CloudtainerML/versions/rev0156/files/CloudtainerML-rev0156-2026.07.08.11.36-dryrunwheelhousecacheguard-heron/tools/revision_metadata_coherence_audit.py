#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(str(REV).replace("rev", ""))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

CURRENT_JSON = [
    "CUBE-META.json",
    "REVISION-RECEIPT.json",
    "EVIDENCE-STATUS.json",
    "SURFACE-STATUS.json",
    "REENTRY-CONTRACT.json",
]

VERSION_KEYS = {
    "revision",
    "revision_number",
    "revision_int",
    "current_revision_int",
    "current_revision",
    "evidence_revision",
    "current_focus",
    "fresh_focus",
    "current_lineage_artifact",
    "current_primary_artifact",
    "current_scientific_artifact",
    "primary_artifact",
    "primary_lineage_artifact",
    "primary_scientific_artifact",
    "revision_name",
    "package_name",
    "archive_name",
    "title",
    "summary",
    "timestamp",
    "generated_at",
    "updated_at",
    "validated_at",
    "source_revision",
    "previous_revision",
}


def load(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    if not p.exists():
        return {"_missing": True}
    return json.loads(p.read_text(encoding="utf-8"))


def stale_current_value(value: Any) -> bool:
    text = str(value)
    # Current identity fields may mention only the current revision/package.
    # previous_revision/source_revision are skipped by the caller.
    stale_rev = [m.lower() for m in re.findall(r"(?i)rev\d{4}", text)]
    return any(item != REV for item in stale_rev) or any(bad in text for bad in ["bundlecompletegate-raven", "hardwareboundarymetafix-peregrine", "devicedtypetiminggate-harrier", "promptmanifestgate-oriole", "cachecontractgate-falcon", "relocationreceiptmetafix-owl", "evaluatorreceiptgate-merlin", "verdictgatemetafix-goshawk", "selectorreceiptreplayfix-lanner", "handoffarchivegate-osprey"])


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    package_name = str(META.get("package_name", ""))
    archive_name = str(META.get("archive_name", ""))
    expected_archive = package_name + ".zip"
    if archive_name != expected_archive:
        errors.append(f"archive_name must equal package_name + .zip: {archive_name!r} != {expected_archive!r}")

    # Directly validate current identity fields; rev0105 revealed that generic
    # revision/revision_number checks can miss stale `current_revision` labels.
    current_identity_expectations = {
        'current_revision': REV,
        'evidence_revision': REV,
        'current_lineage_artifact': f'MISSION-AUDIT-{REVUP}.md',
        'primary_lineage_artifact': f'MISSION-AUDIT-{REVUP}.md',
    }
    for key, expected in current_identity_expectations.items():
        if META.get(key) != expected:
            errors.append(f'CUBE-META.json: {key} {META.get(key)!r} != {expected!r}')

    per_file: dict[str, dict[str, Any]] = {}
    for rel in CURRENT_JSON:
        data = load(rel)
        per_file[rel] = {"present": not data.get("_missing", False), "errors": [], "warnings": []}
        if data.get("_missing"):
            errors.append(f"missing current metadata file: {rel}")
            continue
        if data.get("revision") != REV:
            msg = f"{rel}: revision {data.get('revision')!r} != {REV!r}"
            errors.append(msg); per_file[rel]["errors"].append(msg)
        if int(data.get("revision_number", -1)) != REVNO:
            msg = f"{rel}: revision_number {data.get('revision_number')!r} != {REVNO}"
            errors.append(msg); per_file[rel]["errors"].append(msg)
        for key in ["revision_int", "current_revision_int"]:
            if key in data and int(data.get(key, -1)) != REVNO:
                msg = f"{rel}: {key} {data.get(key)!r} != {REVNO}"
                errors.append(msg); per_file[rel]["errors"].append(msg)
        if data.get("package_name") and data.get("package_name") != package_name:
            msg = f"{rel}: package_name mismatch"
            errors.append(msg); per_file[rel]["errors"].append(msg)
        if data.get("archive_name") and data.get("archive_name") != archive_name:
            msg = f"{rel}: archive_name mismatch"
            errors.append(msg); per_file[rel]["errors"].append(msg)
        if data.get("revision_name") and data.get("revision_name") != package_name:
            msg = f"{rel}: revision_name should be current package name, not stale lineage label"
            errors.append(msg); per_file[rel]["errors"].append(msg)

        counts = data.get("counts")
        if isinstance(counts, dict) and counts.get("revision_number") is not None and int(counts.get("revision_number")) != REVNO:
            msg = f"{rel}: counts.revision_number {counts.get('revision_number')!r} != {REVNO}"
            errors.append(msg); per_file[rel]["errors"].append(msg)
        if data.get("source_revision") and data.get("source_revision") != data.get("previous_revision"):
            msg = f"{rel}: source_revision differs from previous_revision; allowed only with an explicit fork note"
            warnings.append(msg); per_file[rel]["warnings"].append(msg)
        for key in VERSION_KEYS:
            if key in {"previous_revision", "source_revision"}:
                continue
            if key in data and stale_current_value(data.get(key)):
                msg = f"{rel}: stale value in {key}: {data.get(key)!r}"
                errors.append(msg); per_file[rel]["errors"].append(msg)

    status = "pass" if not errors else "fail"
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": package_name,
        "archive_name": archive_name,
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Verifies that current top-level metadata cannot carry stale revision identity from the previous datacube turn.",
        "checked_files": per_file,
        "errors": errors,
        "warnings": warnings,
        "defect_prevented": "rev0105-style stale current_revision/current_artifact metadata surviving inside otherwise current package files",
    }
    (OUT / f"{REVUP}_REVISION_METADATA_COHERENCE_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Revision metadata coherence audit — {REVUP}",
        "",
        f"Status: `{status}`  ",
        "Promotion allowed: `false`",
        "",
        "This audit exists because a current package can pass ordinary smoke checks while still carrying stale title/summary/revision_int/source_revision fields from an older turn.",
        "",
        "## Errors",
    ]
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    md.extend(["", "## Warnings"])
    md.extend([f"- `{w}`" for w in warnings] if warnings else ["- none"])
    (OUT / f"{REVUP}_REVISION_METADATA_COHERENCE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
