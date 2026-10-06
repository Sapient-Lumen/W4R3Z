import json
import pathlib
import re
from typing import Any

from hot_current_supports_lib import (
    LANDING_SURFACES,
    HotCurrentSupportsError,
    latest_cue_items,
    validate_hot_current_supports,
)

PRIMARY_JSON_REVISION_SURFACES = [
    "REVISION-RECEIPT.json",
    "SURFACE-STATUS.json",
    "RELEASE-MANIFEST.json",
    "context-pack.json",
    "frontier-ticket.json",
    "innovation-packet.json",
    "replay-capsule.json",
    "compact-surface-bundle.json",
    "VALIDATION-INDEX.json",
    "VALIDATION-TOOLCHAIN-MANIFEST.json",
    "LINT-IDEMPOTENCE-AUDIT.json",
]
STATUS_REVISION_PATHS = [
    "revision",
    "current_revision",
    "current_head",
    "latest_revision",
    "operational_head.revision",
    "citation_head.revision",
    "status_lanes.revision",
]
STATUS_BUNDLE_PATHS = [
    "latest_bundle",
    "current_bundle",
    "latest_archive",
    "frozen_public_surface",
    "current_release_surface",
    "operational_head.surface",
    "citation_head.surface",
    "status_lanes.current_release_surface",
    "status_lanes.frozen_public_surface",
]


def load_json(root: pathlib.Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def get_path(obj: Any, dotted: str) -> Any:
    cur = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def status_value(observed: Any, expected: Any) -> str:
    return "pass" if observed == expected else "fail"


def build_landing_cues(root: pathlib.Path, receipt: dict[str, Any], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    expected = validate_hot_current_supports(root, receipt)
    expected_resolution = receipt.get("resolution_witness", {}).get("id")
    for rel in LANDING_SURFACES:
        path = root / rel
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        row: dict[str, Any] = {"surface": rel, "status": "fail"}
        try:
            match, observed = latest_cue_items(text, rel)
        except HotCurrentSupportsError as exc:
            row["error"] = str(exc)
            rows.append(row)
            continue
        missing = [item for item in expected if item not in observed]
        unexpected = [item for item in observed if item not in expected]
        row.update({
            "revision": match.group("revision"),
            "bundle": match.group("bundle"),
            "resolved_question": match.group("resolved"),
            "resolution_id": match.group("resolution"),
            "successor_question": match.group("successor"),
            "hot_current_supports_count": len(observed),
            "hot_current_supports_missing": missing,
            "hot_current_supports_unexpected": unexpected,
            "hot_current_supports_order_exact": observed == expected,
        })
        row["status"] = "pass" if (
            row["revision"] == receipt.get("revision")
            and row["bundle"] == manifest.get("bundle")
            and row["resolved_question"] == receipt.get("resolved_question")
            and row["resolution_id"] == expected_resolution
            and row["successor_question"] == receipt.get("next_open_question")
            and observed == expected
        ) else "fail"
        rows.append(row)
    return rows


def build_status_fields(status: dict[str, Any], receipt: dict[str, Any], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rev = receipt.get("revision")
    bundle = manifest.get("bundle")
    for dotted in STATUS_REVISION_PATHS:
        observed = get_path(status, dotted)
        rows.append({
            "surface": "SURFACE-STATUS.json",
            "path": dotted,
            "expected": rev,
            "observed": observed,
            "status": status_value(observed, rev),
        })
    for dotted in STATUS_BUNDLE_PATHS:
        observed = get_path(status, dotted)
        rows.append({
            "surface": "SURFACE-STATUS.json",
            "path": dotted,
            "expected": bundle,
            "observed": observed,
            "status": status_value(observed, bundle),
        })
    rows.append({
        "surface": "SURFACE-STATUS.json",
        "path": "previous_revision",
        "expected": receipt.get("previous_revision"),
        "observed": status.get("previous_revision"),
        "status": status_value(status.get("previous_revision"), receipt.get("previous_revision")),
    })
    return rows


def build_json_revision_cues(root: pathlib.Path, receipt: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rev = receipt.get("revision")
    for rel in PRIMARY_JSON_REVISION_SURFACES:
        path = root / rel
        if not path.exists():
            if rel == "CURRENTNESS-CUE-AUDIT.json":
                continue
            rows.append({"surface": rel, "path": "revision", "expected": rev, "observed": None, "status": "fail"})
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            rows.append({"surface": rel, "path": "revision", "expected": rev, "observed": f"json-error:{exc}", "status": "fail"})
            continue
        if "revision" in data:
            observed = data.get("revision")
            rows.append({"surface": rel, "path": "revision", "expected": rev, "observed": observed, "status": status_value(observed, rev)})
    return rows


def build_current_key_scan(root: pathlib.Path, receipt: dict[str, Any]) -> list[dict[str, Any]]:
    """Scan high-risk currentness names in primary root JSON surfaces.

    Historical or anchored fields are intentionally not scanned here; this is a terse-current-cue mesh,
    not a ban on historical revision identifiers in ledgers or receipts.
    """
    rows: list[dict[str, Any]] = []
    rev = receipt.get("revision")
    scan_names = {"current_revision", "latest_revision", "current_head", "head_revision"}
    for rel in ["SURFACE-STATUS.json", "REVISION-RECEIPT.json", "context-pack.json", "frontier-ticket.json", "innovation-packet.json", "replay-capsule.json", "compact-surface-bundle.json"]:
        path = root / rel
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        def walk(obj: Any, trail: str = "") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    child = f"{trail}.{key}" if trail else key
                    if key in scan_names and isinstance(value, str) and re.fullmatch(r"rev\d{4}", value):
                        rows.append({
                            "surface": rel,
                            "path": child,
                            "expected": rev,
                            "observed": value,
                            "status": status_value(value, rev),
                        })
                    walk(value, child)
            elif isinstance(obj, list):
                for idx, value in enumerate(obj):
                    walk(value, f"{trail}[{idx}]")
        walk(data)
    return rows


def build_currentness_cue_audit(root: pathlib.Path) -> dict[str, Any]:
    receipt = load_json(root, "REVISION-RECEIPT.json")
    manifest = load_json(root, "RELEASE-MANIFEST.json")
    status = load_json(root, "SURFACE-STATUS.json")
    revision = receipt.get("revision")
    bundle = manifest.get("bundle")
    status_fields = build_status_fields(status, receipt, manifest)
    landing_cues = build_landing_cues(root, receipt, manifest)
    json_revision_cues = build_json_revision_cues(root, receipt)
    current_key_scan = build_current_key_scan(root, receipt)
    all_rows = [*status_fields, *landing_cues, *json_revision_cues, *current_key_scan]
    failures = [row for row in all_rows if row.get("status") != "pass"]
    return {
        "project": "DelayBasin",
        "revision": revision,
        "surface": "CURRENTNESS-CUE-AUDIT.json",
        "guide_surface": "docs/00-meta/currentness-cue-audit.md",
        "state": "generated-currentness-cue-audit",
        "generated_from": ["REVISION-RECEIPT.json", "SURFACE-STATUS.json", "RELEASE-MANIFEST.json", *LANDING_SURFACES],
        "expected": {
            "revision": revision,
            "previous_revision": receipt.get("previous_revision"),
            "bundle": bundle,
            "stamp": manifest.get("timestamp"),
            "slug": manifest.get("slug"),
            "resolved_question": receipt.get("resolved_question"),
            "next_open_question": receipt.get("next_open_question"),
            "resolution_id": receipt.get("resolution_witness", {}).get("id"),
            "hot_current_supports": receipt.get("hot_current_supports"),
        },
        "non_claim": "currentness-cue-court, latest-head-tribunal, status-sovereign, bundle-revision-notary, recency-court, landing-cue-authority, green-lint-currentness-waiver, and current-key-senate are forbidden; this surface detects stale current cues but does not certify semantic truth or continuation authority.",
        "status_fields": status_fields,
        "landing_cues": landing_cues,
        "json_revision_cues": json_revision_cues,
        "current_key_scan": current_key_scan,
        "known_repaired_findings": [
            {
                "id": "rev0327-surface-status-current-revision-stale",
                "finding": "SURFACE-STATUS.json carried current_revision=rev0325 while the package head was rev0327; prior green lint did not catch that terse currentness key.",
                "repair": "rev0328 sets SURFACE-STATUS.current_revision to the current revision and adds generated currentness-cue auditing plus a direct status-field guard.",
                "evidence_surfaces": ["SURFACE-STATUS.json", "CURRENTNESS-CUE-AUDIT.json", "tools/check_currentness_cue_audit_contract.py", "tools/check_surface_status_current_key_coherence.py"],
                "status": "closed-by-rev0328",
            }
        ],
        "scan_policy": {
            "scope": "high-risk current/latest/head revision and bundle cues plus exact compact hot-current-support lists in root reentry surfaces",
            "historical_exclusions": ["previous_revision", "origin_revision", "anchor.expected_head", "anchor.observed_head", "historical_witness=true subtrees", "older ledger rows"],
            "repair": "fail closed on terse current-key drift; route semantic overclaim to the successor question instead of creating a currentness court",
        },
        "counts": {
            "status_fields": len(status_fields),
            "landing_cues": len(landing_cues),
            "json_revision_cues": len(json_revision_cues),
            "current_key_scan": len(current_key_scan),
            "failures": len(failures),
        },
        "failures": failures,
    }


def render_currentness_cue_audit_md(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Currentness cue audit")
    lines.append("")
    lines.append("This generated surface exposes high-risk current/latest/head cues so stale terse keys cannot hide behind a green lint count.")
    lines.append("")
    lines.append(f"- Revision: `{payload['revision']}`")
    lines.append(f"- Bundle: `{payload['expected']['bundle']}`")
    lines.append(f"- Resolved question: `{payload['expected']['resolved_question']}`")
    lines.append(f"- Live successor: `{payload['expected']['next_open_question']}`")
    lines.append(f"- Failures: `{payload['counts']['failures']}`")
    lines.append("")
    lines.append("## Non-claim")
    lines.append(payload["non_claim"])
    lines.append("")
    lines.append("## Status fields")
    for row in payload["status_fields"]:
        lines.append(f"- `{row['surface']}#{row['path']}` — expected `{row['expected']}`, observed `{row['observed']}`: `{row['status']}`")
    lines.append("")
    lines.append("## Landing cues")
    for row in payload["landing_cues"]:
        lines.append(f"- `{row['surface']}` — revision `{row.get('revision')}`, bundle `{row.get('bundle')}`, successor `{row.get('successor_question')}`: `{row['status']}`")
    lines.append("")
    lines.append("## Known repaired findings")
    for row in payload["known_repaired_findings"]:
        lines.append(f"- `{row['id']}` — {row['finding']} Repair: {row['repair']}")
    lines.append("")
    lines.append("## Scan policy")
    lines.append(f"- Scope: {payload['scan_policy']['scope']}")
    lines.append(f"- Historical exclusions: {', '.join(payload['scan_policy']['historical_exclusions'])}")
    lines.append(f"- Repair: {payload['scan_policy']['repair']}")
    return "\n".join(lines).rstrip() + "\n"
