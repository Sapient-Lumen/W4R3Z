#!/usr/bin/env python3
"""Build EvidenceVault rights-readiness and component license triage surfaces.

This builder does not grant a license.  It makes the current release blocker
machine-checkable so a mechanically valid archive cannot be mistaken for a
publication-ready or redistributable archive. It also consumes the local
license-reference integrity audit so missing shipped LICENSE/NOTICE targets
remain a hard publication blocker rather than a prose footnote.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "RIGHTS" / "component_license_ledger.json"
MD_OUT = ROOT / "RIGHTS" / "component_license_ledger.md"
ROOT_LICENSE_NAMES = ("LICENSE", "LICENSE.md", "COPYING", "NOTICE")
LICENSE_REFERENCE_AUDIT = ROOT / "RIGHTS" / "license_reference_integrity_audit.json"
GENERATED_DIGEST_CYCLE_EXCLUSIONS = {
    # These generated identity surfaces change during release refresh and do
    # not alter rights conclusions. Counting their bytes in the rights ledger
    # made the ledger stale immediately after a normal release-manifest/index rebuild.
    "RELEASE_MANIFEST.json",
    "MANIFEST.sha256",
    "INDEX/files.json",
    "INDEX/files.csv",
}
TRANSIENT_RIGHTS_COUNT_EXCLUDED_PARTS = {"__pycache__"}
TRANSIENT_RIGHTS_COUNT_EXCLUDED_SUFFIXES = {".pyc"}

COMPONENTS: list[dict[str, Any]] = [
    {
        "component_id": "core_governance",
        "note": "EvidenceVault governance, opening, manifest, and inventory surfaces",
        "paths": ["README.md", "START_HERE.md", "RELEASE_MANIFEST.json", "REVISION_RECEIPT.json", "MANIFEST.sha256", "INDEX/"],
    },
    {
        "component_id": "papers",
        "note": "Canonical TeX/PDF paper payloads and root PDF mirrors",
        "paths": ["papers/", "ev_acceptability_kernel.pdf", "ev_interpretation_profiles.pdf", "ev_streamfold.pdf", "ev_zkrtp.pdf", "ev_pact_ocf.pdf"],
    },
    {
        "component_id": "ctg",
        "note": "Retained CTG source tree and curated CTG material",
        "paths": ["sources/ctg/", "artifacts/curated/ctg/"],
    },
    {
        "component_id": "docf",
        "note": "Retained dOCF source tree and render/material mirrors",
        "paths": ["sources/docf/", "artifacts/curated/docf/", "renders/legacy_pdfs/docf/"],
    },
    {
        "component_id": "pact",
        "note": "Retained PACT source tree and cert/artifact material",
        "paths": ["sources/pact/", "artifacts/curated/pact/", "certs/curated/pact/"],
    },
    {
        "component_id": "ocf_llm",
        "note": "Retained OCF LLM source tree and cert/render material",
        "paths": ["sources/ocf_llm/", "certs/curated/ocf_llm/", "renders/legacy_pdfs/ocf_llm/"],
    },
    {
        "component_id": "streamfold",
        "note": "StreamFold represented without retained sources/ root",
        "paths": ["artifacts/curated/streamfold/", "certs/curated/streamfold/", "renders/legacy_pdfs/streamfold/"],
    },
    {
        "component_id": "zkrtp",
        "note": "zk-RTP represented without retained sources/ root",
        "paths": ["artifacts/curated/zkrtp_v2/", "certs/curated/zkrtp_v2/", "renders/legacy_pdfs/zkrtp_v2/", "renders/legacy_pdfs/zkrtp_portfolio/"],
    },
    {
        "component_id": "validators_and_scripts",
        "note": "Archive validation, build, publication, and verification scripts",
        "paths": ["scripts/", "Makefile"],
    },
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_existing_files(paths: list[str]) -> set[Path]:
    files: set[Path] = set()
    for rel_s in paths:
        p = ROOT / rel_s.rstrip("/")
        if not p.exists():
            continue
        if p.is_dir():
            candidates = (child for child in p.rglob("*") if child.is_file())
        elif p.is_file():
            candidates = (p,)
        else:
            continue
        for child in candidates:
            child_rel = rel(child)
            if child_rel in GENERATED_DIGEST_CYCLE_EXCLUSIONS:
                continue
            if any(part in TRANSIENT_RIGHTS_COUNT_EXCLUDED_PARTS for part in child.relative_to(ROOT).parts):
                continue
            if child.suffix in TRANSIENT_RIGHTS_COUNT_EXCLUDED_SUFFIXES:
                continue
            files.add(child)
    return files


def load_license_reference_audit() -> dict[str, Any] | None:
    path = ROOT / "RIGHTS" / "license_reference_integrity_audit.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def load_ro_crate_license() -> str | None:
    try:
        crate = json.loads((ROOT / "ro-crate-metadata.json").read_text(encoding="utf-8"))
    except Exception:
        return None
    for entity in crate.get("@graph", []):
        if isinstance(entity, dict) and entity.get("@id") == "./":
            value = entity.get("license")
            return value if isinstance(value, str) else None
    return None


def build(root: Path = ROOT) -> dict[str, Any]:
    global ROOT
    old_root = ROOT
    ROOT = root
    try:
        root_license_files = [name for name in ROOT_LICENSE_NAMES if (ROOT / name).is_file()]
        root_license_present = bool(root_license_files)
        ro_license = load_ro_crate_license()
        license_reference_audit = load_license_reference_audit()
        missing_license_references = 0
        if license_reference_audit is not None:
            missing_license_references = int(license_reference_audit.get("local_references_missing", 0) or 0) + int(license_reference_audit.get("local_references_outside_archive", 0) or 0)
        components = []
        total_files = 0
        total_bytes = 0
        for cfg in COMPONENTS:
            files = iter_existing_files(cfg["paths"])
            byte_count = sum(p.stat().st_size for p in files)
            total_files += len(files)
            total_bytes += byte_count
            components.append({
                "component_id": cfg["component_id"],
                "paths": cfg["paths"],
                "observed_file_count_under_existing_paths": len(files),
                "observed_byte_count_under_existing_paths": byte_count,
                "license_declared": "NOASSERTION",
                "license_concluded": "NOASSERTION",
                "copyright_text": "NOASSERTION",
                "review_status": "blocked_pending_owner_or_upstream_license_decision",
                "note": cfg["note"],
            })

        blocking_findings = []
        if not root_license_present:
            blocking_findings.append({
                "id": "missing_root_license_or_notice",
                "severity": "blocker",
                "message": "No root LICENSE/COPYING/NOTICE file is present; archive-wide redistribution rights are not granted.",
                "repair": "Add root LICENSE and NOTICE, then update RO-Crate and component ledger license conclusions.",
            })
        if ro_license in {None, "", "See README.md"}:
            blocking_findings.append({
                "id": "ro_crate_license_unresolved",
                "severity": "blocker",
                "message": f"RO-Crate root dataset license is unresolved: {ro_license!r}.",
                "repair": "Use a concrete license reference, or use NOASSERTION only with an explicit blocker file.",
            })
        elif ro_license == "NOASSERTION" and not (ROOT / "RIGHTS" / "LICENSE_DECISION_BLOCKER.md").is_file():
            blocking_findings.append({
                "id": "ro_crate_noassertion_without_blocker",
                "severity": "blocker",
                "message": "RO-Crate uses NOASSERTION but the rights decision blocker file is missing.",
                "repair": "Add RIGHTS/LICENSE_DECISION_BLOCKER.md or resolve the license.",
            })
        if license_reference_audit is None:
            blocking_findings.append({
                "id": "license_reference_integrity_audit_missing",
                "severity": "blocker",
                "message": "RIGHTS/license_reference_integrity_audit.json is missing, so local LICENSE/NOTICE references have not been checked.",
                "repair": "Run python3 scripts/build_license_reference_integrity_audit.py before rights readiness.",
            })
        elif missing_license_references:
            blocking_findings.append({
                "id": "missing_local_license_reference_targets",
                "severity": "blocker",
                "message": f"{missing_license_references} shipped local LICENSE/COPYING/NOTICE reference target(s) are missing or outside the archive.",
                "repair": "Add the pinned upstream license/notice file(s), or remove/annotate the unresolved local reference after human rights review.",
            })

        return {
            "version": 4,
            "revision_context": "rev0833-session-patch-over-rev0832-over-rev0826",
            "status": "publication_blocked_pending_rights_decision" if blocking_findings else "rights_ready_for_owner_review",
            "decision_required_before_publication": bool(blocking_findings),
            "root_license_or_notice_file_present": root_license_present,
            "root_license_or_notice_files": root_license_files,
            "ro_crate_root_license_value": ro_license,
            "license_reference_integrity_status": license_reference_audit.get("status") if license_reference_audit else "missing",
            "missing_or_outside_local_license_reference_count": missing_license_references,
            "license_reference_integrity_audit": "RIGHTS/license_reference_integrity_audit.json",
            "blocking_findings": blocking_findings,
            "generated_digest_cycle_exclusions": sorted(GENERATED_DIGEST_CYCLE_EXCLUSIONS),
            "transient_rights_count_exclusions": {
                "parts": sorted(TRANSIENT_RIGHTS_COUNT_EXCLUDED_PARTS),
                "suffixes": sorted(TRANSIENT_RIGHTS_COUNT_EXCLUDED_SUFFIXES),
            },
            "recommended_minimum_canonical_files": [
                "LICENSE",
                "NOTICE",
                "RIGHTS/component_license_ledger.json",
                "RIGHTS/license_evidence_scan.json",
                "RIGHTS/license_reference_integrity_audit.json",
                "SBOM/EvidenceVault-file-inventory.spdx.json",
            ],
            "components_total_observed_files_under_listed_paths": total_files,
            "components_total_observed_bytes_under_listed_paths": total_bytes,
            "components": components,
            "builder": "scripts/build_rights_readiness.py",
            "validator": "scripts/validate_rights_readiness.py",
        }
    finally:
        ROOT = old_root


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Component license ledger and rights-readiness blocker",
        "",
        "This is a release-readiness surface, not a license grant. It makes the current rights gap explicit and mechanically checkable.",
        "",
        f"- Status: `{data['status']}`",
        f"- Decision required before publication: `{str(data['decision_required_before_publication']).lower()}`",
        f"- Root LICENSE/COPYING/NOTICE present: `{str(data['root_license_or_notice_file_present']).lower()}`",
        f"- Root rights files: {', '.join(f'`{x}`' for x in data['root_license_or_notice_files']) if data['root_license_or_notice_files'] else 'none'}",
        f"- RO-Crate root license value: `{data['ro_crate_root_license_value']}`",
        f"- License-reference integrity status: `{data.get('license_reference_integrity_status')}`",
        f"- Missing/outside local license references: **{data.get('missing_or_outside_local_license_reference_count', 0)}**",
        f"- Observed files under component paths: **{data['components_total_observed_files_under_listed_paths']}**",
        f"- Observed bytes under component paths: **{data['components_total_observed_bytes_under_listed_paths']}**",
        f"- Generated digest/index files excluded from rights byte counts: {', '.join(f'`{x}`' for x in data.get('generated_digest_cycle_exclusions', []))}",
        "",
        "## Blocking findings",
        "",
    ]
    if data["blocking_findings"]:
        for finding in data["blocking_findings"]:
            lines.extend([
                f"### `{finding['id']}` — `{finding['severity']}`",
                f"- Finding: {finding['message']}",
                f"- Repair: {finding['repair']}",
                "",
            ])
    else:
        lines.extend(["No blocking findings recorded by this readiness check.", ""])

    lines.extend([
        "## Component table",
        "",
        "| Component | Files | Bytes | License concluded | Status |",
        "| --- | ---: | ---: | --- | --- |",
    ])
    for row in data["components"]:
        lines.append(
            f"| `{row['component_id']}` | {row['observed_file_count_under_existing_paths']} | "
            f"{row['observed_byte_count_under_existing_paths']} | `{row['license_concluded']}` | `{row['review_status']}` |"
        )
    lines.extend([
        "",
        "## Minimum repair",
        "",
        "Choose an archive-level license policy, add root `LICENSE` and `NOTICE`, use `RIGHTS/license_evidence_scan.json` as an input to human review, replace unresolved RO-Crate license metadata with a concrete license reference, and update this ledger or the SPDX document with component-level conclusions.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    data = build(ROOT)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(data), encoding="utf-8")
    print(
        "rights-readiness-build: OK "
        f"({len(data['components'])} components, {len(data['blocking_findings'])} blockers)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
