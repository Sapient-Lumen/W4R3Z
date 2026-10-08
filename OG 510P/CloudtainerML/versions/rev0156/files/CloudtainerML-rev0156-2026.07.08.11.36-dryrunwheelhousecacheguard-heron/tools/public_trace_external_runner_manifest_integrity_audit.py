#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
MANIFEST = ROOT / "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json"
CONTRACT = "external_runner_manifest_integrity_fallback_v1"
SUBJECTS_EXCLUDE = {"PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json"}

RESEARCH_BASIS = [
    {
        "url": "https://huggingface.co/docs/huggingface_hub/en/guides/download",
        "observed_lines": "lines 117-125, 143-170, and 202-229 in current docs opened during REV0150",
        "fact": "snapshot_download downloads a repository at a specific revision, supports file filters/local folders, and the hf CLI exposes dry-run byte planning.",
        "implication": "The external runner is allowed to be a subset packet, but its own subject manifest has to be verifiable after extraction before a large snapshot/capture run.",
    },
    {
        "url": "https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables",
        "observed_lines": "lines 86-110 and 167-172 in current docs opened during REV0150",
        "fact": "Hub environment variables are read at import time and HF_HUB_OFFLINE prevents HTTP calls when only cached files should be used.",
        "implication": "Runner integrity verification has to happen locally and must not depend on a full source cube checksum file or network state.",
    },
    {
        "url": "https://huggingface.co/docs/huggingface_hub/en/guides/manage-cache",
        "observed_lines": "lines 81-95 and 127-145 in current docs opened during REV0150",
        "fact": "The Hub cache uses a central file/chunk cache with blobs, snapshots, and cached immutable tree metadata.",
        "implication": "A compact runner should verify its own runner files separately from generated cache/snapshot state instead of trying to reuse full-cube checksums.",
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_subjects_sha(subjects: list[dict[str, Any]]) -> str:
    return hashlib.sha256(json.dumps(subjects, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def audit(root: Path = ROOT, *, strict: bool = False) -> dict[str, Any]:
    manifest_path = root / "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json"
    errors: list[str] = []
    warnings: list[str] = []
    manifest = load_manifest(manifest_path)
    subject_reports: list[dict[str, Any]] = []
    executable_reports: list[dict[str, Any]] = []

    if manifest is None:
        errors.append("missing_external_runner_manifest")
        manifest_subjects: list[dict[str, Any]] = []
    else:
        manifest_subjects = manifest.get("subjects", [])
        if manifest.get("contract") != "public_trace_external_runner_packet_v1":
            errors.append("unexpected_manifest_contract:" + str(manifest.get("contract")))
        if manifest.get("revision") != REV:
            errors.append(f"manifest_revision_mismatch:{manifest.get('revision')}!={REV}")
        if "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json" in {s.get("path") for s in manifest_subjects if isinstance(s, dict)}:
            errors.append("manifest_subjects_self_reference_is_not_verifiable")
        if not isinstance(manifest_subjects, list) or not manifest_subjects:
            errors.append("manifest_subjects_missing_or_empty")
        else:
            clean_subjects = []
            seen: set[str] = set()
            for item in manifest_subjects:
                if not isinstance(item, dict):
                    errors.append("malformed_subject_not_object")
                    continue
                rel = str(item.get("path", ""))
                if not rel or rel.startswith("/") or ".." in Path(rel).parts:
                    errors.append("unsafe_or_empty_subject_path:" + rel)
                    continue
                if rel in seen:
                    errors.append("duplicate_manifest_subject:" + rel)
                    continue
                seen.add(rel)
                if rel in SUBJECTS_EXCLUDE:
                    errors.append("excluded_subject_listed:" + rel)
                    continue
                path = root / rel
                report = {"path": rel, "present": path.is_file()}
                if not path.is_file():
                    errors.append("missing_manifest_subject:" + rel)
                else:
                    size = path.stat().st_size
                    digest = sha256_file(path)
                    report.update({"bytes": size, "sha256": digest})
                    if item.get("bytes") != size:
                        errors.append(f"manifest_subject_size_mismatch:{rel}")
                    if item.get("sha256") != digest:
                        errors.append(f"manifest_subject_sha256_mismatch:{rel}")
                    if rel.endswith(".sh") and not os.access(path, os.X_OK):
                        errors.append(f"manifest_shell_subject_not_executable:{rel}")
                    clean_subjects.append({"path": rel, "bytes": size, "sha256": digest})
                subject_reports.append(report)
            if manifest.get("subject_count") != len(clean_subjects):
                errors.append(f"manifest_subject_count_mismatch:{manifest.get('subject_count')}!={len(clean_subjects)}")
            total_bytes = sum(int(s.get("bytes", 0)) for s in clean_subjects)
            if manifest.get("total_bytes") != total_bytes:
                errors.append(f"manifest_total_bytes_mismatch:{manifest.get('total_bytes')}!={total_bytes}")
            expected_subjects_sha = canonical_subjects_sha(clean_subjects)
            if manifest.get("subjects_sha256") != expected_subjects_sha:
                errors.append("manifest_subjects_sha256_mismatch")
        required = manifest.get("required_in_packet", []) if isinstance(manifest, dict) else []
        for rel in required:
            path = root / rel
            if not path.exists():
                errors.append("missing_required_packet_file:" + str(rel))
        for rel in ["RUN_PUBLIC_TRACE.sh", "PREPARE_SNAPSHOT.sh", "BOOTSTRAP_RUNTIME.sh", "RUN_FIRST_REAL_TRACE.sh"]:
            path = root / rel
            executable_reports.append({"path": rel, "present": path.is_file(), "executable": os.access(path, os.X_OK)})
            if not path.is_file():
                errors.append("missing_root_runner_script:" + rel)
            elif not os.access(path, os.X_OK):
                errors.append("root_runner_script_not_executable:" + rel)

    # Extras are allowed after a real run because trace/provenance/receipt files are generated fresh.
    present_subject_count = sum(1 for r in subject_reports if r.get("present"))
    audit_doc = {
        "revision": REV,
        "revision_number": int(str(META.get("revision_number", REV.replace("rev", "0")))),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Verifies the compact external runner against its own subject manifest. This is the fallback integrity contract used when the runner intentionally lacks the full-cube CHECKSUMS.sha256 file; it prevents a successful expensive capture from dying at the final smoke_validate step only because the packet is a subset.",
        "contract": CONTRACT,
        "manifest_path": "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json",
        "manifest_present": manifest is not None,
        "manifest_subject_count": len(manifest_subjects) if isinstance(manifest_subjects, list) else None,
        "present_subject_count": present_subject_count,
        "self_referential_manifest_subject_allowed": False,
        "generated_trace_outputs_allowed_as_extras": True,
        "subject_reports": subject_reports,
        "root_runner_executable_reports": executable_reports,
        "errors": errors,
        "warnings": warnings,
        "research_basis": RESEARCH_BASIS,
        "decision": "runner_manifest_integrity_ok" if not errors else "repair_runner_manifest_or_packet_before_expensive_trace_run",
    }
    return audit_doc


def write_outputs(audit_doc: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST_INTEGRITY_AUDIT.json").write_text(json.dumps(audit_doc, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace external runner manifest integrity audit — {REVUP}",
        "",
        f"Status: `{audit_doc['status']}`  ",
        "Promotion allowed: `false`",
        "",
        audit_doc.get("summary", ""),
        "",
        "## Contract",
        "",
        f"- contract: `{audit_doc.get('contract')}`",
        f"- manifest present: `{audit_doc.get('manifest_present')}`",
        f"- subject count: `{audit_doc.get('manifest_subject_count')}`",
        f"- present subjects: `{audit_doc.get('present_subject_count')}`",
        "- self-referential manifest subject allowed: `false`",
        "- generated trace outputs allowed as extras: `true`",
        "",
        "## Errors",
        "",
    ]
    md.extend([f"- `{e}`" for e in audit_doc.get("errors", [])] if audit_doc.get("errors") else ["- none"])
    md.extend(["", "## Decision", "", str(audit_doc.get("decision", ""))])
    (OUT / f"{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST_INTEGRITY_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a compact public-trace external runner against its own manifest.")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args()
    root = args.root.resolve()
    audit_doc = audit(root, strict=args.strict)
    write_outputs(audit_doc)
    print(json.dumps({"status": audit_doc["status"], "errors": audit_doc["errors"]}, indent=2))
    if args.strict and audit_doc["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
