#!/usr/bin/env python3
"""Build and validate the r523 hygiene checkset shard manifest.

The archive's full hygiene wrapper has become too large for short interactive
release windows.  r523 keeps the all-check wrapper, but adds typed shard
metadata and a --profile flag so release-critical, post-detach, generated, and
schema-audit slices can be run deliberately without losing coverage of the full
checkset.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-05-30r533"
SCHEMA = "spec/cube.hygiene.checkset.manifest.schema.json"
EXAMPLE = "spec/examples/cube.hygiene.checkset.manifest.json"
CHECK_RE = re.compile(r"check_[A-Za-z0-9_]+\.py")
SCRIPT_RE = re.compile(r'"([A-Za-z0-9_]+\.py)"')

NON_CHECK_VALIDATORS = {"lint_spec_schemas.py", "validate_spec_examples.py"}
RELEASE_CRITICAL = {
    "check_consistency.py",
    "lint_spec_schemas.py",
    "check_schema_kind_matches_filename.py",
    "validate_spec_examples.py",
    "check_discovery.py",
    "check_meta_doc_discoverability.py",
    "check_changelog_format.py",
    "check_release_heading_uniqueness.py",
    "check_release_heading_order.py",
    "check_changelog_index_release_coverage.py",
    "check_index_front_matter_order.py",
    "check_doc_number_prefix_uniqueness.py",
    "check_markdown_h1_structure.py",
    "check_markdown_h2_heading_uniqueness.py",
    "check_markdown_inline_code_balance.py",
    "check_text_files_final_newline.py",
    "check_python_tool_executable_bits.py",
    "check_changelog_artifact_mentions.py",
    "check_hygiene_checkset_completeness.py",
    "check_release_last_updated.py",
    "check_generated_docs.py",
    "check_validation_logs_clean.py",
    "check_spec_example_coverage.py",
    "check_readme_latest_cut.py",
    "check_version.py",
}
GENERATED_SURFACE = {
    "check_generated_docs.py",
    "check_discovery.py",
    "check_meta_doc_discoverability.py",
    "check_doc_metadata.py",
    "check_doc_patterns.py",
    "check_changelog_index_release_coverage.py",
    "check_spec_example_coverage.py",
}
SCHEMA_CUBE_AUDIT = {
    "check_cube_schema_audit_report.py",
    "check_cube_hygiene_checkset_manifest.py",
    "check_schema_kind_matches_filename.py",
    "lint_spec_schemas.py",
    "validate_spec_examples.py",
}

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "cube.hygiene.checkset.manifest", "check_cube_hygiene_checkset_manifest.py"],
    "README.md": [VERSION, "hygiene-checkset", "tools/hygiene.py --profile release-critical"],
    "docs/00-index.md": [VERSION, "docs/current/cube-hygiene-checkset.md"],
    "docs/98-archive-hygiene.md": ["check_cube_hygiene_checkset_manifest.py", "tools/hygiene.py --profile release-critical"],
    "docs/99-llm-runbook.md": ["check_cube_hygiene_checkset_manifest.py", "tools/hygiene.py --profile post-detach"],
    "docs/current/cube-hygiene-checkset.md": ["cube.hygiene.checkset.manifest", "release-critical", "post-detach", "generated-surface"],
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def hygiene_text() -> str:
    return (ROOT / "tools" / "hygiene.py").read_text(encoding="utf-8", errors="replace")


def referenced_scripts() -> list[str]:
    text = hygiene_text()
    return sorted(set(m.group(1) for m in SCRIPT_RE.finditer(text) if m.group(1).endswith(".py")))


def referenced_checks_in_hygiene() -> list[str]:
    return CHECK_RE.findall(hygiene_text())


def top_level_checks() -> set[str]:
    return {p.name for p in (ROOT / "tools").glob("check_*.py") if p.is_file()}


def classify(name: str) -> tuple[str, str, bool]:
    if name in RELEASE_CRITICAL:
        return "release-critical", "front-door, schema, generated-doc, or release metadata guardrail", True
    if "post_detach" in name or "removable_media_local_fallback" in name:
        return "post-detach", "focused removable-media post-detach/fallback lifecycle guardrail", False
    if name in GENERATED_SURFACE or name.startswith("check_doc_") or name.startswith("check_markdown_"):
        return "generated-surface", "generated documentation or discoverability guardrail", False
    if name in SCHEMA_CUBE_AUDIT or name.startswith("check_cube_"):
        return "schema-cube-audit", "schema/audit/refactor surface guardrail", False
    return "deep-contract", "legacy or domain-specific contract guardrail retained in full hygiene", False


def build_manifest() -> dict[str, Any]:
    checks_expected = top_level_checks()
    ref_checks_list = referenced_checks_in_hygiene()
    ref_checks = set(ref_checks_list)
    counts = Counter(ref_checks_list)
    scripts = referenced_scripts()
    non_check = sorted(name for name in scripts if name in NON_CHECK_VALIDATORS)
    missing = sorted(checks_expected - ref_checks)
    stale = sorted(name for name in ref_checks - checks_expected)
    duplicates = sorted(name for name, count in counts.items() if count > 1)

    # Include the two non-check validators because they are first-class release
    # gates even though check_hygiene_checkset_completeness only watches check_*.py.
    tool_names = sorted(ref_checks | set(non_check))
    check_rows = []
    shard_counts = Counter()
    for name in tool_names:
        shard, reason, release_critical = classify(name)
        shard_counts[shard] += 1
        check_rows.append({
            "tool": name,
            "shard": shard,
            "release_critical": release_critical,
            "reason": reason,
        })

    shards = [
        {
            "shard_id": "release-critical",
            "profile_name": "release-critical",
            "purpose": "bounded front-door checks suitable for an interactive release cut",
            "run_command": "python3 tools/hygiene.py --profile release-critical",
            "check_count": shard_counts["release-critical"],
        },
        {
            "shard_id": "post-detach",
            "profile_name": "post-detach",
            "purpose": "focused removable-media fallback and post-detach lifecycle checks",
            "run_command": "python3 tools/hygiene.py --profile post-detach",
            "check_count": shard_counts["post-detach"],
        },
        {
            "shard_id": "generated-surface",
            "profile_name": "generated-surface",
            "purpose": "generated documentation, discoverability, and markdown surface checks",
            "run_command": "python3 tools/hygiene.py --profile generated-surface",
            "check_count": shard_counts["generated-surface"],
        },
        {
            "shard_id": "schema-cube-audit",
            "profile_name": "schema-cube-audit",
            "purpose": "schema validation, example validation, and cube audit checks",
            "run_command": "python3 tools/hygiene.py --profile schema-cube-audit",
            "check_count": shard_counts["schema-cube-audit"],
        },
        {
            "shard_id": "deep-contract",
            "profile_name": "deep-contract",
            "purpose": "remaining domain contract checks retained for full asynchronous CI style runs",
            "run_command": "python3 tools/hygiene.py --profile deep-contract",
            "check_count": shard_counts["deep-contract"],
        },
    ]

    return {
        "kind": "cube.hygiene.checkset.manifest",
        "schema_version": "1.0",
        "manifest_id": "cube-hygiene-checkset-20260530-r532",
        "generated_for_version": VERSION,
        "scope": {
            "source": "tools/hygiene.py plus top-level tools/check_*.py",
            "hygiene_wrapper": "tools/hygiene.py",
            "top_level_check_glob": "tools/check_*.py",
            "non_check_validators": non_check,
        },
        "counts": {
            "top_level_check_scripts": len(checks_expected),
            "hygiene_referenced_check_scripts": len(ref_checks),
            "non_check_validators_in_hygiene": len(non_check),
            "shards_total": 5,
            "release_critical_count": shard_counts["release-critical"],
            "post_detach_focus_count": shard_counts["post-detach"],
            "generated_surface_count": shard_counts["generated-surface"],
            "schema_cube_audit_count": shard_counts["schema-cube-audit"],
            "deep_contract_count": shard_counts["deep-contract"],
            "duplicates_count": len(duplicates),
            "missing_from_hygiene_count": len(missing),
            "stale_hygiene_reference_count": len(stale),
        },
        "shards": shards,
        "checks": check_rows,
        "profile_policy": {
            "hygiene_profile_argument": "--profile",
            "default_profile": "all",
            "release_cut_profile": "release-critical",
            "full_profile": "all",
        },
        "invariants": {
            "every_top_level_check_is_referenced_once": not missing and not duplicates,
            "every_referenced_check_exists": not stale,
            "every_check_has_one_shard": True,
            "release_critical_profile_is_bounded": 0 < shard_counts["release-critical"] < len(check_rows),
            "post_detach_focus_profile_exists": shard_counts["post-detach"] > 0,
            "generated_surface_profile_exists": shard_counts["generated-surface"] > 0,
            "schema_cube_audit_profile_exists": shard_counts["schema-cube-audit"] > 0,
        },
        "refactor_policy": {
            "problem": "flat-full-hygiene-wrapper-exceeds-interactive-release-window",
            "change": "profiled-hygiene-shards-are-typed-and-live-scanned",
            "next_refactor": "teach CI to run shards in parallel and report per-shard elapsed time",
        },
    }


def validation_errors(obj: dict[str, Any]) -> list[str]:
    schema = load_json(ROOT, SCHEMA)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def require_docs() -> None:
    for rel, tokens in REQUIRED_DOC_TOKENS.items():
        path = ROOT / rel
        if not path.exists():
            fail(f"missing required doc surface: {rel}")
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                fail(f"{rel} missing required token {token!r}")
    text = hygiene_text()
    for token in ["--profile", "release-critical", "post-detach", "generated-surface", "schema-cube-audit", "deep-contract"]:
        if token not in text:
            fail(f"tools/hygiene.py missing profile token {token!r}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write the live checkset manifest example")
    args = ap.parse_args()

    expected = build_manifest()
    if args.write:
        (ROOT / EXAMPLE).write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {EXAMPLE}")
        return 0

    observed = load_json(ROOT, EXAMPLE)
    errs = validation_errors(observed)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    if observed != expected:
        print("cube hygiene checkset manifest is stale; regenerate with:", file=sys.stderr)
        print("  python3 tools/check_cube_hygiene_checkset_manifest.py --write", file=sys.stderr)
        if observed.get("counts") != expected.get("counts"):
            print(f"observed counts: {observed.get('counts')}", file=sys.stderr)
            print(f"expected counts: {expected.get('counts')}", file=sys.stderr)
        raise SystemExit(1)
    for key, value in observed["invariants"].items():
        if value is not True:
            fail(f"invariant {key} must be true")
    require_docs()
    print("cube hygiene checkset manifest check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
