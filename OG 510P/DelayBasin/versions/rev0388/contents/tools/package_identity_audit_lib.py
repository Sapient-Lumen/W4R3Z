import json
import pathlib
import re
from typing import Any

from external_metadata_contract_lib import external_metadata_rows
from release_hygiene_lib import parse_bundle_name

EXTERNAL_METADATA_SURFACES = ["LICENSE", "CITATION.cff", "codemeta.json", "ro-crate-metadata.json", "SBOM.spdx.json"]
ROOT_JSON_SURFACES = [
    "REVISION-RECEIPT.json",
    "SURFACE-STATUS.json",
    "RELEASE-MANIFEST.json",
    "PATH-ALIAS-LEDGER.json",
    "ALIAS-RETENTION-POLICY.json",
    "CANARY-PROTOCOL.json",
    "CURRENTNESS-CUE-AUDIT.json",
    "VALIDATION-TOOLCHAIN-MANIFEST.json",
    "VALIDATION-INDEX.json",
    "LINT-IDEMPOTENCE-AUDIT.json",
    "FRONTIER-BACKLOG.json",
    "LEDGER-AUDIT.json",
    "LINK-INTEGRITY-POLICY.json",
    "SELF-SUFFICIENCY-LEDGER.json",
    "WITNESS-VOCABULARY.json",
    "WITNESS-FAMILY-HANDLES.json",
]
CURRENT_KEY_NAMES = {"current_revision", "latest_revision", "current_head", "head_revision"}
REV_RE = re.compile(r"rev\d{4}")
BUNDLE_RE = re.compile(r"DelayBasin-rev\d{4}-[^\s`\"']+?\.zip")


def load_json(root: pathlib.Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def status(observed: Any, expected: Any) -> str:
    return "pass" if observed == expected else "fail"


def walk_current_keys(obj: Any, rel: str, revision: str, path: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        historical = obj.get("historical_witness") is True
        for key, value in obj.items():
            child = f"{path}.{key}" if path else key
            if not historical and key in CURRENT_KEY_NAMES and isinstance(value, str) and REV_RE.fullmatch(value):
                rows.append({"surface": rel, "path": child, "expected": revision, "observed": value, "status": status(value, revision)})
            if not historical:
                rows.extend(walk_current_keys(value, rel, revision, child))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            rows.extend(walk_current_keys(value, rel, revision, f"{path}[{idx}]"))
    return rows


def build_json_identity_rows(root: pathlib.Path, revision: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    revision_rows: list[dict[str, Any]] = []
    current_rows: list[dict[str, Any]] = []
    for rel in ROOT_JSON_SURFACES:
        path = root / rel
        if not path.exists():
            revision_rows.append({"surface": rel, "path": "<file>", "expected": "present", "observed": "missing", "status": "fail"})
            continue
        data = load_json(root, rel)
        if "revision" in data:
            revision_rows.append({"surface": rel, "path": "revision", "expected": revision, "observed": data.get("revision"), "status": status(data.get("revision"), revision)})
        current_rows.extend(walk_current_keys(data, rel, revision))
    return revision_rows, current_rows


def build_external_metadata_rows(root: pathlib.Path, revision: str, bundle: str) -> list[dict[str, Any]]:
    # Keep package-identity auditing aligned with the executable external metadata contract,
    # including release-date and SBOM creation-time coherence. The revision/bundle
    # arguments remain in the signature for older callers, but the shared contract derives
    # expectations from RELEASE-MANIFEST.json and REVISION-RECEIPT.json.
    return external_metadata_rows(root)


def build_release_identity_rows(root: pathlib.Path, receipt: dict[str, Any], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    revision = receipt.get("revision")
    bundle = manifest.get("bundle")
    status_payload = load_json(root, "SURFACE-STATUS.json")
    try:
        parsed = parse_bundle_name(str(bundle))
        canonical_status = "pass" if parsed.get("revision") == revision and parsed.get("timestamp") == manifest.get("timestamp") and parsed.get("slug") == manifest.get("slug") else "fail"
        canonical_observed: Any = parsed
    except ValueError as exc:
        canonical_status = "fail"
        canonical_observed = str(exc)
    rows = [
        {"surface": "RELEASE-MANIFEST.json", "path": "revision", "expected": revision, "observed": manifest.get("revision"), "status": status(manifest.get("revision"), revision)},
        {"surface": "RELEASE-MANIFEST.json", "path": "bundle", "expected": receipt.get("packaged_bundle_filename"), "observed": bundle, "status": status(bundle, receipt.get("packaged_bundle_filename"))},
        {"surface": "RELEASE-MANIFEST.json", "path": "bundle_pattern", "expected": "DelayBasin-rev####-YYYY.MM.DD.HH.MM-lowercase-dash-slug.zip", "observed": canonical_observed, "status": canonical_status},
        {"surface": "SURFACE-STATUS.json", "path": "latest_bundle", "expected": bundle, "observed": status_payload.get("latest_bundle"), "status": status(status_payload.get("latest_bundle"), bundle)},
        {"surface": "REVISION-RECEIPT.json", "path": "packaged_bundle_filename", "expected": bundle, "observed": receipt.get("packaged_bundle_filename"), "status": status(receipt.get("packaged_bundle_filename"), bundle)},
    ]
    return rows


def build_package_identity_audit(root: pathlib.Path) -> dict[str, Any]:
    receipt = load_json(root, "REVISION-RECEIPT.json")
    manifest = load_json(root, "RELEASE-MANIFEST.json")
    revision = receipt.get("revision")
    bundle = manifest.get("bundle")
    json_rows, current_key_rows = build_json_identity_rows(root, revision)
    external_rows = build_external_metadata_rows(root, revision, bundle)
    release_rows = build_release_identity_rows(root, receipt, manifest)
    all_rows = [*json_rows, *current_key_rows, *external_rows, *release_rows]
    failures = [row for row in all_rows if row.get("status") != "pass"]
    return {
        "project": "DelayBasin",
        "revision": revision,
        "surface": "PACKAGE-IDENTITY-AUDIT.json",
        "guide_surface": "docs/00-meta/package-identity-audit.md",
        "state": "generated-package-identity-audit",
        "generated_from": ["REVISION-RECEIPT.json", "RELEASE-MANIFEST.json", "SURFACE-STATUS.json", *ROOT_JSON_SURFACES, *EXTERNAL_METADATA_SURFACES],
        "expected": {"revision": revision, "bundle": bundle, "resolved_question": receipt.get("resolved_question"), "next_open_question": receipt.get("next_open_question"), "resolution_id": receipt.get("resolution_witness", {}).get("id")},
        "non_claim": "package-identity-court, metadata-sovereign, release-name-tribunal, license-revision-notary, current-key-senate, checksum-authority, manifest-court, and identity-spillover-board are forbidden; this surface detects stale package identity spillover but does not certify semantic truth, license interpretation, or continuation authority.",
        "release_identity_rows": release_rows,
        "json_revision_rows": json_rows,
        "current_key_rows": current_key_rows,
        "external_metadata_rows": external_rows,
        "known_repaired_findings": [
            {"id": "rev0328-license-stale-release-line", "finding": "LICENSE began with 'DelayBasin research archive release rev0327' inside the rev0328 package while the weaker external metadata check still passed because rev0328 appeared elsewhere.", "repair": "rev0329 requires external metadata to contain only the current revision token and requires the LICENSE first line to name the current package revision.", "status": "closed-by-rev0329"},
            {"id": "rev0328-path-alias-current-revision-stale", "finding": "PATH-ALIAS-LEDGER.json carried current_revision=rev0327 while revision=rev0328; the prior currentness audit did not scan this root metadata spillover surface.", "repair": "rev0329 sets PATH-ALIAS-LEDGER.current_revision to the current revision and adds package-identity auditing over root JSON current-key spillover.", "status": "closed-by-rev0329"},
        ],
        "scan_policy": {
            "scope": "external metadata revision/bundle tokens, strict release bundle filename components, root JSON top-level revision fields, and current/head/latest revision keys outside ledger historical rows",
            "historical_exclusions": ["previous_revision", "origin_revision", "older ledger item revisions", "historical_witness=true subtrees", "anchor.expected_head", "anchor.observed_head"],
            "repair": "fail closed on package-identity spillover; repair metadata/current-key drift without treating identity freshness as semantic authority",
        },
        "counts": {"release_identity_rows": len(release_rows), "json_revision_rows": len(json_rows), "current_key_rows": len(current_key_rows), "external_metadata_rows": len(external_rows), "failures": len(failures)},
        "failures": failures,
    }


def render_package_identity_audit_md(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Package identity audit")
    lines.append("")
    lines.append("This generated surface exposes stale package-identity spillover that can hide outside the landing/currentness mesh.")
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
    lines.append("## Repaired findings")
    for row in payload["known_repaired_findings"]:
        lines.append(f"- `{row['id']}` — {row['finding']} Repair: {row['repair']}")
    lines.append("")
    lines.append("## Counts")
    for key, value in payload["counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Scan policy")
    lines.append(f"- Scope: {payload['scan_policy']['scope']}")
    lines.append(f"- Historical exclusions: {', '.join(payload['scan_policy']['historical_exclusions'])}")
    lines.append(f"- Repair: {payload['scan_policy']['repair']}")
    return "\n".join(lines).rstrip() + "\n"
