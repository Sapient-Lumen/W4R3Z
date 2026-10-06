#!/usr/bin/env python3
"""Guard docs/current summaries against generated JSON drift.

The front-door current docs are the operator view.  This check binds their
version stamps and compact count blocks to the generated JSON examples so a
future schema/checkset/ledger refresh cannot leave stale prose green.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from cube_digest_lib import load_json

ROOT = Path(__file__).resolve().parents[1]


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def doc_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")


def generated_version(obj: dict[str, Any]) -> str:
    value = obj.get("generated_for_version")
    return value if isinstance(value, str) else ""


def require_version_and_counts(errors: list[str], *, example_rel: str, doc_rel: str, count_pairs: list[tuple[str, Any]]) -> None:
    obj = load_json(ROOT, example_rel)
    if not isinstance(obj, dict):
        errors.append(f"{example_rel} must be a JSON object")
        return
    text = doc_text(doc_rel)
    version = generated_version(obj)
    require(errors, version in text, f"{doc_rel} must mention generated_for_version {version!r}")
    require(errors, f"Last updated: {version}" in text, f"{doc_rel} Last updated must match {example_rel}")
    for key, value in count_pairs:
        require(errors, f"{key}: {value}" in text, f"{doc_rel} must bind {key}: {value} from {example_rel}")


def main() -> int:
    errors: list[str] = []
    audit = load_json(ROOT, "spec/examples/cube.schema.audit.report.json")
    if isinstance(audit, dict):
        counts = audit.get("counts", {}) if isinstance(audit.get("counts"), dict) else {}
        require_version_and_counts(
            errors,
            example_rel="spec/examples/cube.schema.audit.report.json",
            doc_rel="docs/current/cube-schema-audit.md",
            count_pairs=[
                ("schemas_total", counts.get("schemas_total")),
                ("examples_total", counts.get("examples_total")),
                ("root_kind_schema_count", counts.get("root_kind_schema_count")),
                ("schemas_with_canonical_example_count", counts.get("schemas_with_canonical_example_count")),
                ("schemas_without_canonical_example_count", counts.get("schemas_without_canonical_example_count")),
                ("const_heavy_schema_count", counts.get("const_heavy_schema_count")),
                ("runtime_contract_shaped_schema_count", counts.get("runtime_contract_shaped_schema_count")),
                ("exact_fixture_schema_count", counts.get("exact_fixture_schema_count")),
                ("dotted_kind_filename_mismatch_count", counts.get("dotted_kind_filename_mismatch_count")),
            ],
        )
    else:
        errors.append("spec/examples/cube.schema.audit.report.json must be an object")

    backlog = load_json(ROOT, "spec/examples/cube.schema.refactor.backlog.json")
    if isinstance(backlog, dict):
        counts = backlog.get("counts", {}) if isinstance(backlog.get("counts"), dict) else {}
        require_version_and_counts(
            errors,
            example_rel="spec/examples/cube.schema.refactor.backlog.json",
            doc_rel="docs/current/cube-schema-refactor-backlog.md",
            count_pairs=[
                ("items_total", counts.get("items_total")),
                ("open_items", counts.get("open_items")),
                ("completed_items", counts.get("completed_items")),
                ("post_detach_items", counts.get("post_detach_items")),
                ("highest_const_count", counts.get("highest_const_count")),
                ("audit_next_targets_count", counts.get("audit_next_targets_count")),
            ],
        )
    else:
        errors.append("spec/examples/cube.schema.refactor.backlog.json must be an object")

    checkset = load_json(ROOT, "spec/examples/cube.hygiene.checkset.manifest.json")
    if isinstance(checkset, dict):
        counts = checkset.get("counts", {}) if isinstance(checkset.get("counts"), dict) else {}
        require_version_and_counts(
            errors,
            example_rel="spec/examples/cube.hygiene.checkset.manifest.json",
            doc_rel="docs/current/cube-hygiene-checkset.md",
            count_pairs=[
                ("top_level_check_scripts", counts.get("top_level_check_scripts")),
                ("hygiene_referenced_check_scripts", counts.get("hygiene_referenced_check_scripts")),
                ("non_check_validators_in_hygiene", counts.get("non_check_validators_in_hygiene")),
                ("release_critical_count", counts.get("release_critical_count")),
                ("post_detach_focus_count", counts.get("post_detach_focus_count")),
                ("generated_surface_count", counts.get("generated_surface_count")),
                ("schema_cube_audit_count", counts.get("schema_cube_audit_count")),
                ("deep_contract_count", counts.get("deep_contract_count")),
                ("missing_from_hygiene_count", counts.get("missing_from_hygiene_count")),
                ("stale_hygiene_reference_count", counts.get("stale_hygiene_reference_count")),
                ("duplicates_count", counts.get("duplicates_count")),
                ("shards_total", counts.get("shards_total")),
            ],
        )
    else:
        errors.append("spec/examples/cube.hygiene.checkset.manifest.json must be an object")

    ledger = load_json(ROOT, "spec/examples/cube.hygiene.run.ledger.json")
    if isinstance(ledger, dict):
        ledger_doc = doc_text("docs/current/hygiene-run-ledger.md")
        version = generated_version(ledger)
        require(errors, version in ledger_doc, f"docs/current/hygiene-run-ledger.md must mention generated_for_version {version!r}")
        require(errors, "current checked-in example snapshot" in ledger_doc.lower(), "hygiene-run-ledger doc must expose a current checked-in snapshot block")
        if ledger.get("run_complete") is True:
            require_version_and_counts(
                errors,
                example_rel="spec/examples/cube.hygiene.run.ledger.json",
                doc_rel="docs/current/hygiene-run-ledger.md",
                count_pairs=[
                    ("selected_profile", ledger.get("selected_profile")),
                    ("checks_total", ledger.get("checks_total")),
                    ("checks_completed", ledger.get("checks_completed")),
                    ("passed", (ledger.get("counts", {}) if isinstance(ledger.get("counts"), dict) else {}).get("passed")),
                    ("failed", (ledger.get("counts", {}) if isinstance(ledger.get("counts"), dict) else {}).get("failed")),
                    ("timed_out", (ledger.get("counts", {}) if isinstance(ledger.get("counts"), dict) else {}).get("timed_out")),
                    ("run_complete", str(ledger.get("run_complete")).lower()),
                ],
            )
    else:
        errors.append("spec/examples/cube.hygiene.run.ledger.json must be an object")

    if errors:
        print("Current generated surface sync check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("Current generated surface sync check OK")
    print("docs/current generated summaries match their checked-in JSON examples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
