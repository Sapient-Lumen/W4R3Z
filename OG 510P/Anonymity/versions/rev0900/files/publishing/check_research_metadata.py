#!/usr/bin/env python3
"""Check research-object metadata and local provenance consistency."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

import update_release_provenance


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def cff_scalar(text: str, key: str) -> str:
    m = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    if not m:
        return ""
    value = m.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return value


def record(checks: list[dict[str, Any]], name: str, ok: bool, details: str) -> None:
    checks.append({"name": name, "status": "pass" if ok else "fail", "details": details})


def provenance_statements(path: pathlib.Path) -> list[dict[str, Any]]:
    statements = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            statements.append(json.loads(line))
    return statements




def digest_entries_failures(root: pathlib.Path, entries: list[dict[str, Any]], *, name_key: str = "name", uri_prefix: str | None = None) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for entry in entries:
        raw_name = entry.get(name_key)
        if raw_name is None and name_key == "name":
            raw_name = entry.get("uri")
        if raw_name is None:
            failures.append({"name": None, "reason": "missing name/uri"})
            continue
        name = str(raw_name)
        if uri_prefix and name.startswith(uri_prefix):
            name = name[len(uri_prefix):]
        expected_hash = entry.get("digest", {}).get("sha256")
        if not expected_hash:
            failures.append({"name": name, "reason": "missing sha256"})
            continue
        path = root / name
        if not path.exists():
            failures.append({"name": name, "reason": "missing file"})
            continue
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            failures.append({"name": name, "reason": "sha256 mismatch", "expected": expected_hash, "actual": actual_hash})
    return failures


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    revision = release["revision"]
    timestamp = release["timestamp"]
    date = timestamp[:10].replace(".", "-")
    canonical = load_json(root / "publishing" / "CANONICAL_POLICY.json")
    metadata_paths = canonical.get("research_object_metadata", {})
    checks: list[dict[str, Any]] = []

    required = {
        "citation_cff": "CITATION.cff",
        "codemeta": "codemeta.json",
        "ro_crate_metadata": "ro-crate-metadata.json",
        "license": "LICENSE",
        "notice": "NOTICE",
        "release_provenance": "release_provenance.intoto.jsonl",
    }
    missing_keys = sorted(key for key in required if metadata_paths.get(key) != required[key])
    missing_files = sorted(path for path in required.values() if not (root / path).exists())
    record(checks, "canonical_policy_metadata_paths", not missing_keys and not missing_files, f"missing_or_mismapped_keys={missing_keys} missing_files={missing_files}")

    citation_text = (root / "CITATION.cff").read_text(encoding="utf-8", errors="replace")
    cff_schema_version = cff_scalar(citation_text, "cff-version")
    cff_version = cff_scalar(citation_text, "version")
    cff_date = cff_scalar(citation_text, "date-released")
    record(checks, "citation_cff_schema_version", cff_schema_version == "1.2.0", f"cff-version={cff_schema_version} expected=1.2.0")
    record(checks, "citation_cff_revision_and_date", cff_version == revision and cff_date == date, f"version={cff_version} expected={revision} date={cff_date} expected_date={date}")

    codemeta = load_json(root / "codemeta.json")
    expected_name = f"Anonymity datacube {revision}"
    record(checks, "codemeta_revision_date_and_name", codemeta.get("version") == revision and codemeta.get("dateModified") == date and codemeta.get("name") == expected_name, f"name={codemeta.get('name')} expected_name={expected_name} version={codemeta.get('version')} dateModified={codemeta.get('dateModified')}")
    record(checks, "codemeta_identifier_matches_bundle", codemeta.get("identifier") == release["bundle"], f"identifier={codemeta.get('identifier')} expected_bundle={release['bundle']}")

    crate = load_json(root / "ro-crate-metadata.json")
    graph = crate.get("@graph", [])
    dataset = next((node for node in graph if isinstance(node, dict) and node.get("@id") == "./"), {})
    has_part = {part.get("@id") for part in dataset.get("hasPart", []) if isinstance(part, dict)}
    # Keep the RO-Crate coverage contract tied to the same subject builder that
    # emits release_provenance.intoto.jsonl.  Earlier revisions duplicated a long
    # hand-maintained path list here and in update_release_provenance.py; that
    # made every tooling/provenance addition a two-place edit and risked silent
    # metadata under-coverage.
    required_has_part = set(update_release_provenance.subject_paths(root))
    required_has_part.update(update_release_provenance.DEPENDENCIES)
    required_has_part.update(required.values())
    required_has_part.update({
        "ARCHIVE_INDEX.json",
        "ARCHIVE_INDEX.md",
        "MANIFEST.sha256",
        "MANIFEST.json",
        "release_provenance.intoto.jsonl",
    })

    record(checks, "ro_crate_revision_date_name_identifier_and_parts", dataset.get("version") == revision and dataset.get("dateModified") == date and dataset.get("name") == expected_name and dataset.get("identifier") == release["bundle"] and required_has_part.issubset(has_part), f"name={dataset.get('name')} expected_name={expected_name} version={dataset.get('version')} dateModified={dataset.get('dateModified')} identifier={dataset.get('identifier')} missing_parts={sorted(required_has_part - has_part)}")

    license_size = (root / "LICENSE").stat().st_size if (root / "LICENSE").exists() else 0
    notice_text = (root / "NOTICE").read_text(encoding="utf-8", errors="replace") if (root / "NOTICE").exists() else ""
    notice_size = len(notice_text.encode("utf-8"))
    record(checks, "license_notice_nonempty_and_revision_bound", license_size > 20 and notice_size > 20 and revision in notice_text, f"LICENSE_bytes={license_size} NOTICE_bytes={notice_size} notice_contains_revision={revision in notice_text}")

    statements = provenance_statements(root / "release_provenance.intoto.jsonl")
    record(checks, "provenance_statement_count", len(statements) == 1, f"statement_count={len(statements)}")
    statement_type_ok = False
    predicate_type_ok = False
    subject_failures: list[dict[str, Any]] = []
    dependency_failures: list[dict[str, Any]] = []
    external_parameters_ok = False
    expected_subject_names = set(update_release_provenance.subject_paths(root))
    actual_subject_names: set[str] = set()
    missing_provenance_subjects: list[str] = []
    extra_provenance_subjects: list[str] = []
    expected_dependency_uris = {"file:" + rel for rel in update_release_provenance.DEPENDENCIES}
    actual_dependency_uris: set[str] = set()
    missing_provenance_dependencies: list[str] = []
    extra_provenance_dependencies: list[str] = []
    dependency_count = 0
    if statements:
        statement = statements[0]
        statement_type_ok = statement.get("_type") == "https://in-toto.io/Statement/v1"
        predicate_type_ok = statement.get("predicateType") == "https://slsa.dev/provenance/v1"
        pred = statement.get("predicate", {})
        build_definition = pred.get("buildDefinition", {})
        ext = build_definition.get("externalParameters", {})
        external_parameters_ok = ext.get("revision") == revision and ext.get("timestamp") == timestamp and ext.get("bundle") == release["bundle"]
        subjects = statement.get("subject", [])
        actual_subject_names = {str(entry.get("name")) for entry in subjects if isinstance(entry, dict) and entry.get("name")}
        missing_provenance_subjects = sorted(expected_subject_names - actual_subject_names)
        extra_provenance_subjects = sorted(actual_subject_names - expected_subject_names)
        subject_failures = digest_entries_failures(root, subjects, name_key="name")
        dependencies = build_definition.get("resolvedDependencies", [])
        dependency_count = len(dependencies)
        actual_dependency_uris = {str(entry.get("uri")) for entry in dependencies if isinstance(entry, dict) and entry.get("uri")}
        missing_provenance_dependencies = sorted(expected_dependency_uris - actual_dependency_uris)
        extra_provenance_dependencies = sorted(actual_dependency_uris - expected_dependency_uris)
        dependency_failures = digest_entries_failures(root, dependencies, name_key="uri", uri_prefix="file:")
    record(checks, "provenance_statement_types", statement_type_ok and predicate_type_ok, f"statement_type_ok={statement_type_ok} predicate_type_ok={predicate_type_ok}")
    record(checks, "provenance_external_parameters", external_parameters_ok, "external parameters match release manifest" if external_parameters_ok else "external parameters do not match release manifest")
    record(checks, "provenance_subject_path_set", not missing_provenance_subjects and not extra_provenance_subjects, f"missing={missing_provenance_subjects[:10]} extra={extra_provenance_subjects[:10]} expected_count={len(expected_subject_names)} actual_count={len(actual_subject_names)}")
    record(checks, "provenance_dependency_path_set", not missing_provenance_dependencies and not extra_provenance_dependencies, f"missing={missing_provenance_dependencies[:10]} extra={extra_provenance_dependencies[:10]} expected_count={len(expected_dependency_uris)} actual_count={len(actual_dependency_uris)}")
    record(checks, "provenance_subject_hashes", not subject_failures, f"failures={subject_failures[:10]}")
    record(checks, "provenance_dependency_hashes", not dependency_failures, f"dependency_count={dependency_count} failures={dependency_failures[:10]}")

    failures = [check for check in checks if check["status"] != "pass"]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": revision,
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "checks": checks,
        "summary": {
            "checks_passed": len(checks) - len(failures),
            "checks_failed": len(failures),
            "metadata_file_count": len(required),
            "provenance_subject_count": len(statements[0].get("subject", [])) if statements else 0,
            "expected_provenance_subject_count": len(expected_subject_names),
            "provenance_dependency_count": dependency_count,
            "expected_provenance_dependency_count": len(expected_dependency_uris),
        },
        "fail_closed_rule": "If research-object metadata or provenance hashes drift, repair the metadata before presenting the archive as a coherent research object.",
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
