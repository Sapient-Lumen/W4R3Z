#!/usr/bin/env python3
"""Build rev0834 audit for asset-index refresh coupling.

This audit closes a concrete release-refresh gap: asset indexes under
artifacts/ and certs/ are part of the archive identity fence, but rev0833's
refresh cycle refreshed other generated surfaces without first rebuilding
ARTIFACTS_INDEX.* and CERTS_INDEX.*.  A later payload edit could therefore
leave a stale recovery index while identity surfaces were otherwise fresh.

The audit intentionally avoids recording MANIFEST.sha256 / INDEX/files.*
currentness. Those files are emitted *after* material audit builders run, so the
validator performs final manifest/index currentness checks independently.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "AUDIT" / "RELEASE_REFRESH_ASSET_INDEX_REPAIR_REV0834.json"
MD_OUT = ROOT / "AUDIT" / "RELEASE_REFRESH_ASSET_INDEX_REPAIR_REV0834.md"
ASSET_INDEX_FILES = [
    "artifacts/ARTIFACTS_INDEX.json",
    "artifacts/ARTIFACTS_INDEX.csv",
    "certs/CERTS_INDEX.json",
    "certs/CERTS_INDEX.csv",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def current_asset_index_snapshot() -> dict[str, Any]:
    files = []
    ok = True
    for rel in ASSET_INDEX_FILES:
        path = ROOT / rel
        row = {
            "path": rel,
            "exists": path.is_file(),
            "bytes": path.stat().st_size if path.is_file() else None,
            "sha256": sha256_file(path) if path.is_file() else None,
        }
        if rel.endswith(".json") and path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                row["indexed_payload_rows"] = len(data) if isinstance(data, list) else None
                row["json_is_list"] = isinstance(data, list)
            except Exception as exc:  # pragma: no cover - recorded as audit evidence
                row["json_parse_error"] = str(exc)
                row["json_is_list"] = False
        if rel.endswith(".csv") and path.is_file():
            row["indexed_payload_rows"] = csv_row_count(path)
        ok = ok and bool(row["exists"] and row.get("indexed_payload_rows") is not None)
        files.append(row)
    return {"asset_index_files_present_and_parseable": ok, "files": files}


def refresh_order_status() -> dict[str, Any]:
    text = (ROOT / "scripts" / "rebuild_indexes.py").read_text(encoding="utf-8")
    main_match = re.search(r"def main\(\) -> None:(?P<body>.*?)(?:\nif __name__ ==|\Z)", text, re.S)
    main_body = main_match.group("body") if main_match else ""
    builders_match = re.search(r"builders\s*=\s*\[(?P<body>.*?)\n\s*\]", text, re.S)
    builders_body = builders_match.group("body") if builders_match else ""
    positions = {
        "refresh_cycle_safe_material_surfaces": main_body.find("refresh_cycle_safe_material_surfaces()"),
        "refresh_release_manifest_identity": main_body.find("refresh_release_manifest_identity()"),
        "refresh_ro_crate_metadata": main_body.find("refresh_ro_crate_metadata()"),
        "build_index_rows_comment": main_body.find("# Build INDEX rows."),
    }
    order_ok = (
        "build_asset_indexes" in builders_body
        and -1 not in positions.values()
        and positions["refresh_cycle_safe_material_surfaces"] < positions["refresh_release_manifest_identity"] < positions["refresh_ro_crate_metadata"] < positions["build_index_rows_comment"]
    )
    return {
        "rebuild_indexes_includes_build_asset_indexes": "build_asset_indexes" in builders_body,
        "main_call_positions": positions,
        "order_ok": order_ok,
        "required_order": [
            "refresh_cycle_safe_material_surfaces() including build_asset_indexes",
            "refresh_release_manifest_identity()",
            "refresh_ro_crate_metadata()",
            "final INDEX/files.* and MANIFEST.sha256 emission",
        ],
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    asset_snapshot = current_asset_index_snapshot()
    order_status = refresh_order_status()
    blockers = []
    if not asset_snapshot["asset_index_files_present_and_parseable"]:
        blockers.append("asset_index_files_missing_or_unparseable")
    if not order_status["order_ok"]:
        blockers.append("rebuild_indexes_asset_index_refresh_order_invalid")
    return {
        "version": 2,
        "revision_context": "rev0834-session-patch-over-rev0833-over-rev0826",
        "status": "asset_index_refresh_cycle_repaired" if not blockers else "asset_index_refresh_cycle_blocked",
        "blockers": blockers,
        "pre_repair_observation": {
            "rev0833_selected_validator_gap": "validate_asset_indexes.py was not part of the rev0833 selected release-refresh validation set.",
            "observed_failure_before_repair": "asset-index-validate failed on artifacts/curated/zkrtp_v2/policy_report.json after prior payload rewrites changed the file without refreshing artifacts/ARTIFACTS_INDEX.*.",
        },
        "asset_index_file_snapshot": asset_snapshot,
        "rebuild_indexes_refresh_order_status": order_status,
        "final_manifest_index_checks": {
            "why_not_embedded_in_audit": "MANIFEST.sha256 and INDEX/files.* are emitted after material audit builders run; embedding their currentness here would create a generated-surface ordering false positive.",
            "checked_by": "scripts/validate_release_refresh_asset_index_rev0834.py",
            "checks": [
                "validate_asset_indexes.py passes",
                "RELEASE_MANIFEST.json asset-index identity digests match current ARTIFACTS_INDEX.json and CERTS_INDEX.json",
                "MANIFEST.sha256 contains current asset-index file digests",
                "INDEX/files.json contains current asset-index file digests",
            ],
        },
        "repair": {
            "rebuilt_files": ASSET_INDEX_FILES,
            "script_changes": [
                "scripts/rebuild_indexes.py now runs build_asset_indexes.py inside refresh_cycle_safe_material_surfaces().",
                "The material-surface refresh now runs before RELEASE_MANIFEST.json identity digest refresh.",
            ],
            "validator": "scripts/validate_release_refresh_asset_index_rev0834.py",
        },
        "builder": "scripts/build_release_refresh_asset_index_audit_rev0834.py",
    }


def render_markdown(data: dict[str, Any]) -> str:
    files = data["asset_index_file_snapshot"]["files"]
    lines = [
        "# Release refresh asset-index repair audit rev0834",
        "",
        "This audit records and validates a concrete release-refresh repair: asset indexes are archive-identity inputs and must be rebuilt before `RELEASE_MANIFEST.json`, RO-Crate, `INDEX/files.*`, and `MANIFEST.sha256` are emitted.",
        "",
        f"- Status: `{data['status']}`",
        f"- Blockers: {', '.join(f'`{b}`' for b in data['blockers']) if data['blockers'] else 'none'}",
        "",
        "## Pre-repair observation",
        "",
        f"- {data['pre_repair_observation']['rev0833_selected_validator_gap']}",
        f"- {data['pre_repair_observation']['observed_failure_before_repair']}",
        "",
        "## Current asset-index file snapshot",
        "",
        "| File | Rows | Bytes | SHA-256 |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in files:
        lines.append(
            f"| `{row['path']}` | {row.get('indexed_payload_rows', '')} | "
            f"{row.get('bytes', '')} | `{row['sha256']}` |"
        )
    order = data["rebuild_indexes_refresh_order_status"]
    lines.extend([
        "",
        "## Refresh order",
        "",
        f"- `rebuild_indexes.py` includes `build_asset_indexes.py`: `{str(order['rebuild_indexes_includes_build_asset_indexes']).lower()}`",
        f"- Required order satisfied: `{str(order['order_ok']).lower()}`",
        "",
        "Required order:",
        "",
    ])
    for item in order["required_order"]:
        lines.append(f"1. {item}")
    lines.extend([
        "",
        "## Final manifest/index checks",
        "",
        data["final_manifest_index_checks"]["why_not_embedded_in_audit"],
        "",
        f"Checked by `{data['final_manifest_index_checks']['checked_by']}`.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    data = build(ROOT)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(data), encoding="utf-8")
    print(f"release-refresh-asset-index-audit: OK ({data['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
