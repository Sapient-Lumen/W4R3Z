#!/usr/bin/env python3
"""Check the published/ boundary and fail closed on unguarded new releases."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import publication_target as pt  # noqa: E402

LEGACY_NEW_RELEASE_DIR_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2} - Anonymity: .+")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.relative_to(root).as_posix()


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    classification = load_json(root / "published" / "publication_classification.json")
    citation_heads = load_json(root / "published" / "citation_heads.json")
    public_surface = load_json(root / "published" / "PUBLIC_SURFACE.json")
    legacy = load_json(root / "published" / "legacy_published_links.json")

    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []

    legacy_paths = {item.get("path") for item in legacy.get("canonical_legacy_links", []) if isinstance(item, dict)}
    frozen_paths = {item.get("path") for item in classification.get("repo_frozen_noncanonical_entries", []) if isinstance(item, dict)}
    new_classified = {item.get("path") for item in classification.get("new_post_policy_anonymity_entries", []) if isinstance(item, dict)}
    new_citation_heads = {item.get("path") for item in citation_heads.get("new_post_policy_anonymity_heads", []) if isinstance(item, dict)}
    public_heads = set(public_surface.get("current_public_citation_heads", []))

    actual_tex_paths = sorted(rel(p, root) for p in (root / "published").rglob("*.tex"))
    known = legacy_paths | frozen_paths | new_classified
    unknown_tex = sorted(path for path in actual_tex_paths if path not in known)
    for path in unknown_tex:
        failures.append({"category": "published_tex_not_classified", "path": path})

    legacy_missing = sorted(path for path in legacy_paths if not (root / path).exists())
    frozen_missing = sorted(path for path in frozen_paths if not (root / path).exists())
    for path in legacy_missing:
        failures.append({"category": "legacy_public_head_missing", "path": path})
    for path in frozen_missing:
        failures.append({"category": "repo_frozen_noncanonical_missing", "path": path})

    def is_materialized_new_release_dir(directory: pathlib.Path) -> bool:
        if LEGACY_NEW_RELEASE_DIR_RE.match(directory.name):
            return True
        if not pt.is_portable_published_dirname(directory.name):
            return False
        canonical_rel = f"published/{directory.name}/paper.tex"
        has_receipt = (directory / "PUBLICATION_RECEIPT.json").exists()
        has_metadata = (directory / "METADATA.json").exists()
        return has_receipt or has_metadata or canonical_rel in new_classified or canonical_rel in new_citation_heads

    new_dirs = sorted(p for p in (root / "published").iterdir() if p.is_dir() and is_materialized_new_release_dir(p))
    new_dir_tex = set()
    for d in new_dirs:
        canonical_tex = d / ("paper.tex" if pt.is_portable_published_dirname(d.name) else f"{d.name}.tex")
        tex_rel = rel(canonical_tex, root)
        new_dir_tex.add(tex_rel)
        entry_failures: list[dict[str, Any]] = []
        metadata_path = d / "METADATA.json"
        source_md_path = d / "SOURCE.md"
        receipt_path = d / "PUBLICATION_RECEIPT.json"
        if not canonical_tex.exists():
            entry_failures.append({"category": "canonical_tex_missing", "path": tex_rel})
        metadata: dict[str, Any] = {}
        receipt: dict[str, Any] = {}
        if not metadata_path.exists():
            entry_failures.append({"category": "metadata_missing", "path": rel(metadata_path, root)})
        else:
            metadata = load_json(metadata_path)
        if not source_md_path.exists():
            entry_failures.append({"category": "source_note_missing", "path": rel(source_md_path, root)})
        if not receipt_path.exists():
            entry_failures.append({"category": "publication_receipt_missing", "path": rel(receipt_path, root)})
        else:
            receipt = load_json(receipt_path)

        if metadata:
            if metadata.get("public_label") != "Anonymity":
                entry_failures.append({"category": "metadata_public_label_not_anonymity", "value": metadata.get("public_label")})
            if metadata.get("published_name") != d.name:
                entry_failures.append({"category": "metadata_published_name_mismatch", "metadata": metadata.get("published_name"), "directory": d.name})
            expected_artifact = "paper.tex" if pt.is_portable_published_dirname(d.name) else f"{d.name}.tex"
            if metadata.get("canonical_artifact") != expected_artifact:
                entry_failures.append({"category": "metadata_canonical_artifact_mismatch", "value": metadata.get("canonical_artifact"), "expected": expected_artifact})
            if not metadata.get("source_sha256"):
                entry_failures.append({"category": "metadata_missing_source_sha256"})
            for key in ["decision_note", "evidence_pack_manifest", "freeze_compile_witness", "freeze_packet_manifest"]:
                if not metadata.get(key):
                    entry_failures.append({"category": "metadata_missing_required_binding", "key": key})
                elif not (root / str(metadata[key])).exists():
                    entry_failures.append({"category": "metadata_binding_missing_file", "key": key, "path": metadata[key]})

        if receipt:
            if receipt.get("publication_authorized") is not True:
                entry_failures.append({"category": "receipt_publication_authorized_not_true"})
            if receipt.get("published_tex") != tex_rel:
                entry_failures.append({"category": "receipt_published_tex_mismatch", "receipt": receipt.get("published_tex"), "expected": tex_rel})
            if receipt.get("source_sha256") != metadata.get("source_sha256"):
                entry_failures.append({"category": "receipt_metadata_source_sha256_mismatch"})
            if receipt.get("source_sha256") and canonical_tex.exists() and sha256_file(canonical_tex) != receipt.get("source_sha256"):
                entry_failures.append({"category": "published_tex_sha256_not_source_sha256", "actual": sha256_file(canonical_tex), "source_sha256": receipt.get("source_sha256")})

        if tex_rel not in new_classified:
            entry_failures.append({"category": "new_release_not_in_publication_classification", "path": tex_rel})
        if tex_rel not in new_citation_heads:
            entry_failures.append({"category": "new_release_not_in_citation_heads", "path": tex_rel})
        if tex_rel not in public_heads:
            entry_failures.append({"category": "new_release_not_in_public_surface_current_heads", "path": tex_rel})

        decision_note = metadata.get("decision_note") or receipt.get("decision_note") if (metadata or receipt) else ""
        if decision_note:
            note_path = root / str(decision_note)
            if note_path.exists():
                note = note_path.read_text(encoding="utf-8", errors="replace")
                if "Publication action: publish" not in note:
                    entry_failures.append({"category": "decision_note_missing_publish_action", "path": str(decision_note)})
                sha = str(metadata.get("source_sha256") or receipt.get("source_sha256") or "")
                if sha and sha not in note:
                    entry_failures.append({"category": "decision_note_missing_source_sha256", "path": str(decision_note), "source_sha256": sha})
            else:
                entry_failures.append({"category": "decision_note_missing", "path": str(decision_note)})

        entries.append({"published_dir": rel(d, root), "published_tex": tex_rel, "status": "pass" if not entry_failures else "fail", "failure_count": len(entry_failures), "failures": entry_failures})
        failures.extend({"entry": tex_rel, **f} for f in entry_failures)

    classified_new_without_dir = sorted(path for path in new_classified if path not in new_dir_tex)
    for path in classified_new_without_dir:
        failures.append({"category": "classified_new_release_without_matching_directory", "path": path})
    if new_classified != new_citation_heads:
        failures.append({"category": "classification_citation_new_head_mismatch", "classification_only": sorted(new_classified - new_citation_heads), "citation_only": sorted(new_citation_heads - new_classified)})

    legacy_public_surface_ok = set(public_surface.get("current_public_citation_heads", [])) >= legacy_paths
    if not legacy_public_surface_ok:
        failures.append({"category": "public_surface_missing_legacy_heads", "missing": sorted(legacy_paths - public_heads)})

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "entries": entries,
        "warnings": warnings,
        "summary": {
            "legacy_public_head_count": len(legacy_paths),
            "repo_frozen_noncanonical_entry_count": len(frozen_paths),
            "new_post_policy_anonymity_dir_count": len(new_dirs),
            "new_post_policy_anonymity_head_count": len(new_classified),
            "unknown_published_tex_count": len(unknown_tex),
            "checks_failed": len(failures),
        },
        "failures": failures[:80],
        "fail_closed_rule": "If the published boundary audit fails, do not trust new public citation heads until the classification, receipt, evidence, compile, and decision bindings are repaired.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
