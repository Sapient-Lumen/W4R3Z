#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys

sys.dont_write_bytecode = True

from pathlib import Path

from archive_meta import ARCHIVE, GENERATED, METADATA_DIR, NUMBERED_NOTE_FILENAME_RE, ROOT, SCHEMA_DIR, SOURCES_DIR, current_notes_from_index, current_revision, numbered_archive_paths
from schema_validation import validate_repository_json
from test_matrix_registry import COMMON_TEST_MATRICES
from fieldwork_lint_helpers import REQUIRED_FIELDWORK_GAPS, require_text_contains, validate_fieldwork_chain_links, validate_fieldwork_follow_on_links, validate_fieldwork_post_release_links, validate_fieldwork_post_correction_links, validate_fieldwork_post_redress_links, validate_fieldwork_post_closure_links, validate_archive_stewardship_handoff_control

CURRENT_REV = current_revision()
CURRENT_NOTES = current_notes_from_index()

REQUIRED_SOURCE_FILES = [
    "README.md",
    "MISSION.md",
    "CHANGELOG.md",
    "INDEX.md",
    "ARCHIVE_STRUCTURE.md",
    "Makefile",
    "sources/source_catalog.json",
    "sources/source_keys.json",
    "metadata/note_metadata.json",
    "metadata/case_packets.json",
    "metadata/claims.json",
    "metadata/defeat_tests.json",
    "metadata/handback_tests.json",
    "metadata/supplier_dependency_tests.json",
    "metadata/symbolic_authority_tests.json",
    "metadata/capacity_tests.json",
    "metadata/model_decision_tests.json",
    "metadata/generative_assistant_tests.json",
    "metadata/staff_copilot_tests.json",
    "metadata/transition_receipt_tests.json",
    "metadata/platform_migration_tests.json",
    "metadata/ecological_personhood_tests.json",
    "metadata/entitlement_continuity_tests.json",
    "metadata/payment_redress_tests.json",
    "metadata/credential_access_tests.json",
    "metadata/representative_access_tests.json",
    "metadata/disaster_assistance_tests.json",
    "metadata/unemployment_insurance_tests.json",
    "metadata/watchlist_border_tests.json",
    "metadata/public_ai_register_tests.json",
    "metadata/subnational_ai_tests.json",
    "metadata/source_health.json",
    "metadata/route_merge_packets.json",
    "metadata/route_redirect_ledger.json",
    "metadata/gap_ledger.json",
    "schema/note_metadata.schema.json",
    "schema/source_keys.schema.json",
    "schema/case_packets.schema.json",
    "schema/claims.schema.json",
    "schema/defeat_tests.schema.json",
    "schema/handback_tests.schema.json",
    "schema/supplier_dependency_tests.schema.json",
    "schema/symbolic_authority_tests.schema.json",
    "schema/capacity_tests.schema.json",
    "schema/model_decision_tests.schema.json",
    "schema/generative_assistant_tests.schema.json",
    "schema/staff_copilot_tests.schema.json",
    "schema/transition_receipt_tests.schema.json",
    "schema/platform_migration_tests.schema.json",
    "schema/ecological_personhood_tests.schema.json",
    "schema/entitlement_continuity_tests.schema.json",
    "schema/payment_redress_tests.schema.json",
    "schema/credential_access_tests.schema.json",
    "schema/representative_access_tests.schema.json",
    "schema/disaster_assistance_tests.schema.json",
    "schema/unemployment_insurance_tests.schema.json",
    "schema/watchlist_border_tests.schema.json",
    "schema/public_ai_register_tests.schema.json",
    "schema/subnational_ai_tests.schema.json",
    "schema/source_health.schema.json",
    "schema/gap_ledger.schema.json",
    "schema/route_redirect_ledger.schema.json",
    "schema/route_merge_packets.schema.json",
    "schema/source_catalog.schema.json",
    "schema/evidence_receipts.schema.json",
    "schema/source_claim_receipts.schema.json",
    "schema/outcome_tail_plans.schema.json",
    "schema/source_health_taxonomy.schema.json",
    "schema/tail_sampling_gates.schema.json",
    "schema/field_intake_controls.schema.json",
    "schema/fieldwork_authorization_gates.schema.json",
    "schema/fieldwork_execution_controls.schema.json",
    "schema/fieldwork_release_controls.schema.json",
    "schema/fieldwork_correction_controls.schema.json",
    "schema/fieldwork_redress_verification_controls.schema.json",
    "schema/fieldwork_closure_dossiers.schema.json",
    "schema/fieldwork_postclosure_monitoring_controls.schema.json",
    "schema/archive_stewardship_handoff_controls.schema.json",
    "metadata/evidence_receipts.json",
    "metadata/source_claim_receipts.json",
    "metadata/outcome_tail_plans.json",
    "metadata/source_health_taxonomy.json",
    "metadata/tail_sampling_gates.json",
    "metadata/field_intake_controls.json",
    "metadata/fieldwork_authorization_gates.json",
    "metadata/fieldwork_execution_controls.json",
    "metadata/fieldwork_release_controls.json",
    "metadata/fieldwork_correction_controls.json",
    "metadata/fieldwork_redress_verification_controls.json",
    "metadata/fieldwork_closure_dossiers.json",
    "metadata/fieldwork_postclosure_monitoring_controls.json",
    "metadata/archive_stewardship_handoff_controls.json",
    "tools/build_evidence_receipts.py",
    "tools/build_source_claim_receipts.py",
    "tools/build_outcome_tail_plans.py",
    "tools/build_tail_sampling_gates.py",
    "tools/build_field_intake_controls.py",
    "tools/build_fieldwork_authorization_gates.py",
    "tools/build_fieldwork_execution_controls.py",
    "tools/build_fieldwork_release_controls.py",
    "tools/build_fieldwork_correction_controls.py",
    "tools/build_fieldwork_redress_verification_controls.py",
    "tools/build_fieldwork_closure_dossiers.py",
    "tools/build_fieldwork_postclosure_monitoring_controls.py",
    "tools/build_archive_stewardship_handoff_controls.py",
    "tools/fieldwork_lint_helpers.py",
    "tools/metadata_surface.py",
    "tools/build_steps.py",
    "tools/schema_validation.py",
    "tools/check_reproducible_build.py",
]
REQUIRED_GENERATED_FILES = [
    "ARCHIVE_INDEX.json",
    "NOTE_STATUS.json",
    "CASE_PACKET_MATRIX.json",
    "CASE_PACKET_MATRIX.md",
    "CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json",
    "CROSS_BOUNDARY_CONSOLIDATION_AUDIT.md",
    "RETIREMENT_CANDIDATES.json",
    "RETIREMENT_CANDIDATES.md",
    "ROUTE_REDIRECT_LEDGER.json",
    "ROUTE_REDIRECT_LEDGER.md",
    "CANON_MAP.json",
    "THREADS.md",
    "THREAD_SUMMARY.json",
    "RELEASES.json",
    "SOURCES.md",
    "SOURCES.json",
    "CONTROL_SURFACES.json",
    "ASSURANCE_ARTIFACTS.json",
    "LIFECYCLE_GATES.json",
    "CLAIMS.json",
    "CLAIMS.md",
    "DEFEAT_TESTS.json",
    "DEFEAT_TESTS.md",
    "HANDBACK_TESTS.json",
    "HANDBACK_TESTS.md",
    "SUPPLIER_DEPENDENCY_TESTS.json",
    "SUPPLIER_DEPENDENCY_TESTS.md",
    "SYMBOLIC_AUTHORITY_TESTS.json",
    "SYMBOLIC_AUTHORITY_TESTS.md",
    "CAPACITY_TESTS.json",
    "CAPACITY_TESTS.md",
    "MODEL_DECISION_TESTS.json",
    "MODEL_DECISION_TESTS.md",
    "GENERATIVE_ASSISTANT_TESTS.json",
    "GENERATIVE_ASSISTANT_TESTS.md",
    "STAFF_COPILOT_TESTS.json",
    "STAFF_COPILOT_TESTS.md",
    "TRANSITION_RECEIPT_TESTS.json",
    "TRANSITION_RECEIPT_TESTS.md",
    "PLATFORM_MIGRATION_TESTS.json",
    "PLATFORM_MIGRATION_TESTS.md",
    "ECOLOGICAL_PERSONHOOD_TESTS.json",
    "ECOLOGICAL_PERSONHOOD_TESTS.md",
    "ENTITLEMENT_CONTINUITY_TESTS.json",
    "ENTITLEMENT_CONTINUITY_TESTS.md",
    "PAYMENT_REDRESS_TESTS.json",
    "PAYMENT_REDRESS_TESTS.md",
    "EVIDENCE_RECEIPTS.json",
    "EVIDENCE_RECEIPTS.md",
    "SOURCE_CLAIM_RECEIPTS.json",
    "SOURCE_CLAIM_RECEIPTS.md",
    "OUTCOME_TAIL_PLANS.json",
    "OUTCOME_TAIL_PLANS.md",
    "TAIL_SAMPLING_GATES.json",
    "TAIL_SAMPLING_GATES.md",
    "FIELD_INTAKE_CONTROLS.json",
    "FIELD_INTAKE_CONTROLS.md",
    "FIELDWORK_AUTHORIZATION_GATES.json",
    "FIELDWORK_AUTHORIZATION_GATES.md",
    "FIELDWORK_EXECUTION_CONTROLS.json",
    "FIELDWORK_EXECUTION_CONTROLS.md",
    "FIELDWORK_RELEASE_CONTROLS.json",
    "FIELDWORK_RELEASE_CONTROLS.md",
    "FIELDWORK_CORRECTION_CONTROLS.json",
    "FIELDWORK_CORRECTION_CONTROLS.md",
    "FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json",
    "FIELDWORK_REDRESS_VERIFICATION_CONTROLS.md",
    "FIELDWORK_CLOSURE_DOSSIERS.json",
    "FIELDWORK_CLOSURE_DOSSIERS.md",
    "FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json",
    "FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.md",
    "ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json",
    "ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.md",
    "CREDENTIAL_ACCESS_TESTS.json",
    "CREDENTIAL_ACCESS_TESTS.md",
    "REPRESENTATIVE_ACCESS_TESTS.json",
    "REPRESENTATIVE_ACCESS_TESTS.md",
    "DISASTER_ASSISTANCE_TESTS.json",
    "DISASTER_ASSISTANCE_TESTS.md",
    "UNEMPLOYMENT_INSURANCE_TESTS.json",
    "UNEMPLOYMENT_INSURANCE_TESTS.md",
    "WATCHLIST_BORDER_TESTS.json",
    "WATCHLIST_BORDER_TESTS.md",
    "PUBLIC_AI_REGISTER_TESTS.json",
    "PUBLIC_AI_REGISTER_TESTS.md",
    "SUBNATIONAL_AI_TESTS.json",
    "SUBNATIONAL_AI_TESTS.md",
    "SOURCE_HEALTH.json",
    "SOURCE_HEALTH.md",
    "GAP_LEDGER.json",
    "GAP_LEDGER.md",
    "GENERATED_SURFACE_AUDIT.json",
    "GENERATED_SURFACE_AUDIT.md",
    "MANIFEST.json",
]
LEGACY_TOP_LEVEL_GENERATED = [
    "ARCHIVE_INDEX.json", "NOTE_STATUS.json", "CASE_PACKET_MATRIX.json", "CASE_PACKET_MATRIX.md", "CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json", "CROSS_BOUNDARY_CONSOLIDATION_AUDIT.md", "ROUTE_REDIRECT_LEDGER.json", "ROUTE_REDIRECT_LEDGER.md", "CANON_MAP.json", "THREADS.md", "THREAD_SUMMARY.json", "RELEASES.json",
    "SOURCES.md", "SOURCES.json", "CONTROL_SURFACES.json", "ASSURANCE_ARTIFACTS.json",
    "LIFECYCLE_GATES.json", "CLAIMS.json",
    "CLAIMS.md",
    "DEFEAT_TESTS.json",
    "DEFEAT_TESTS.md",
    "HANDBACK_TESTS.json",
    "HANDBACK_TESTS.md",
    "SUPPLIER_DEPENDENCY_TESTS.json",
    "SUPPLIER_DEPENDENCY_TESTS.md",
    "SYMBOLIC_AUTHORITY_TESTS.json",
    "SYMBOLIC_AUTHORITY_TESTS.md",
    "CAPACITY_TESTS.json",
    "CAPACITY_TESTS.md",
    "MODEL_DECISION_TESTS.json",
    "MODEL_DECISION_TESTS.md",
    "GENERATIVE_ASSISTANT_TESTS.json",
    "GENERATIVE_ASSISTANT_TESTS.md",
    "STAFF_COPILOT_TESTS.json",
    "STAFF_COPILOT_TESTS.md",
    "TRANSITION_RECEIPT_TESTS.json",
    "TRANSITION_RECEIPT_TESTS.md",
    "PLATFORM_MIGRATION_TESTS.json",
    "PLATFORM_MIGRATION_TESTS.md",
    "ECOLOGICAL_PERSONHOOD_TESTS.json",
    "ECOLOGICAL_PERSONHOOD_TESTS.md",
    "ENTITLEMENT_CONTINUITY_TESTS.json",
    "ENTITLEMENT_CONTINUITY_TESTS.md",
    "PAYMENT_REDRESS_TESTS.json",
    "PAYMENT_REDRESS_TESTS.md",
    "EVIDENCE_RECEIPTS.json",
    "EVIDENCE_RECEIPTS.md",
    "SOURCE_CLAIM_RECEIPTS.json",
    "SOURCE_CLAIM_RECEIPTS.md",
    "OUTCOME_TAIL_PLANS.json",
    "OUTCOME_TAIL_PLANS.md",
    "TAIL_SAMPLING_GATES.json",
    "TAIL_SAMPLING_GATES.md",
    "FIELD_INTAKE_CONTROLS.json",
    "FIELD_INTAKE_CONTROLS.md",
    "FIELDWORK_AUTHORIZATION_GATES.json",
    "FIELDWORK_AUTHORIZATION_GATES.md",
    "FIELDWORK_EXECUTION_CONTROLS.json",
    "FIELDWORK_EXECUTION_CONTROLS.md",
    "FIELDWORK_RELEASE_CONTROLS.json",
    "FIELDWORK_RELEASE_CONTROLS.md",
    "FIELDWORK_CORRECTION_CONTROLS.json",
    "FIELDWORK_CORRECTION_CONTROLS.md",
    "FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json",
    "FIELDWORK_REDRESS_VERIFICATION_CONTROLS.md",
    "FIELDWORK_CLOSURE_DOSSIERS.json",
    "FIELDWORK_CLOSURE_DOSSIERS.md",
    "FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json",
    "FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.md",
    "ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json",
    "ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.md",
    "CREDENTIAL_ACCESS_TESTS.json",
    "CREDENTIAL_ACCESS_TESTS.md",
    "REPRESENTATIVE_ACCESS_TESTS.json",
    "REPRESENTATIVE_ACCESS_TESTS.md",
    "DISASTER_ASSISTANCE_TESTS.json",
    "DISASTER_ASSISTANCE_TESTS.md",
    "UNEMPLOYMENT_INSURANCE_TESTS.json",
    "UNEMPLOYMENT_INSURANCE_TESTS.md",
    "WATCHLIST_BORDER_TESTS.json",
    "WATCHLIST_BORDER_TESTS.md",
    "PUBLIC_AI_REGISTER_TESTS.json",
    "PUBLIC_AI_REGISTER_TESTS.md",
    "SUBNATIONAL_AI_TESTS.json",
    "SUBNATIONAL_AI_TESTS.md",
    "SOURCE_HEALTH.json",
    "SOURCE_HEALTH.md",
    "GAP_LEDGER.json",
    "GAP_LEDGER.md",
    "GENERATED_SURFACE_AUDIT.json",
    "GENERATED_SURFACE_AUDIT.md",
    "MANIFEST.json",
]
REQUIRED_EXACT = ["## Pattern pack"]
REQUIRED_ANY_OF = [
    ["## One-line thesis"],
    ["## Why this matters", "## Core claim", "## The problem"],
    ["## Failure modes", "## Anti-theater tests"],
]
GENERATED_READER_BUDGETS = {
    "THREADS.md": 500_000,
    "SOURCES.json": 800_000,
    "SOURCE_HEALTH.json": 800_000,
    "ARCHIVE_INDEX.json": 800_000,
    "CONTROL_SURFACES.json": 800_000,
    "LIFECYCLE_GATES.json": 800_000,
}
EXPECTED_THREAD_TAGS = [
    "operations", "monitoring", "data-governance", "regulatory-governance",
    "administrative-procedure-governance", "official-notice-governance", "base-registry-governance",
    "service-delivery-governance", "open-data-governance", "public-enterprise-governance",
    "budget-governance", "procurement-governance", "audit-governance", "legislature-governance",
    "civil-service-governance", "judiciary-governance", "prosecution-governance", "election-governance",
    "ombuds-governance", "human-rights-governance", "policing-governance", "corrections-governance",
    "public-defense-governance", "information-rights-governance", "statistics-governance",
    "districting-governance", "civil-registration-governance", "entity-registry-governance",
    "anti-corruption-governance", "land-administration-governance", "administrative-geography-governance",
    "public-records-governance", "quality-infrastructure-governance", "trust-services-governance",
]

# Keep recent common test-matrix files in lint from the same registry used by build_all,
# so adding a substantive case packet no longer requires duplicating four file lists.
for _spec in COMMON_TEST_MATRICES:
    _metadata_rel = f"metadata/{_spec['metadata_filename']}"
    _schema_rel = f"schema/{_spec['metadata_filename'].replace('.json', '.schema.json')}"
    _gen_json = f"{_spec['output_stem']}.json"
    _gen_md = f"{_spec['output_stem']}.md"
    if _metadata_rel not in REQUIRED_SOURCE_FILES:
        REQUIRED_SOURCE_FILES.append(_metadata_rel)
    if _schema_rel not in REQUIRED_SOURCE_FILES:
        REQUIRED_SOURCE_FILES.append(_schema_rel)
    for _generated in [_gen_json, _gen_md]:
        if _generated not in REQUIRED_GENERATED_FILES:
            REQUIRED_GENERATED_FILES.append(_generated)
        if _generated not in LEGACY_TOP_LEVEL_GENERATED:
            LEGACY_TOP_LEVEL_GENERATED.append(_generated)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_entries(entries: list[dict], label: str) -> None:
    for entry in entries:
        if not isinstance(entry.get("bytes"), int) or entry["bytes"] < 0:
            fail(f"{label} entry missing valid bytes field: {entry}")
        sha = entry.get("sha256", "")
        if not re.fullmatch(r"[0-9a-f]{64}", sha):
            fail(f"{label} entry missing valid sha256: {entry}")


def validate_source_groups(source_map: dict, rel: str, label: str) -> None:
    if rel not in source_map:
        fail(f"{label} missing source entry: {rel}")
    groups = source_map[rel].get("groups", [])
    if not groups:
        fail(f"{label} note entry has no source groups: {rel}")
    seen = set()
    for group in groups:
        for field in ["title", "publisher", "url"]:
            if not isinstance(group.get(field), str) or not group[field].strip():
                fail(f"{label} source group missing {field}: {rel}")
        if not group["url"].startswith("http"):
            fail(f"{label} source url does not start with http: {rel}")
        norm = group["url"].rstrip("/")
        if norm in seen:
            fail(f"{label} duplicate source url: {rel}")
        seen.add(norm)


def first_thesis(path: Path) -> str:
    capture = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "## One-line thesis":
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if capture and line.strip():
            return line.strip()
    return ""


def validate_test_matrix_pair(metadata_filename: str, schema_const: str, generated_filename: str, numbers: list[int]) -> dict:
    metadata_path = METADATA_DIR / metadata_filename
    matrix = load_json(metadata_path)
    if matrix.get("schema") != schema_const:
        fail(f"metadata/{metadata_filename} missing expected schema")
    if matrix.get("revision") != CURRENT_REV:
        fail(f"metadata/{metadata_filename} revision mismatch: expected {CURRENT_REV}")
    for note_number in matrix.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/{metadata_filename} source_notes references unknown note number {note_number}")
    for test_id, test in matrix.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/{metadata_filename} test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/{metadata_filename} test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/{metadata_filename} test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/{metadata_filename} test {test_id} references unknown case example {note_number}")
    generated = load_json(GENERATED / generated_filename)
    if generated.get("revision") != CURRENT_REV:
        fail(f"generated/{generated_filename} revision mismatch: expected {CURRENT_REV}")
    if generated.get("test_count") != len(matrix.get("tests", {})):
        fail(f"generated/{generated_filename} test count mismatch metadata/{metadata_filename}")
    generated_ids = {test.get("test_id") for test in generated.get("tests", [])}
    if generated_ids != set(matrix.get("tests", {})):
        fail(f"generated/{generated_filename} test ids mismatch metadata/{metadata_filename}")
    return matrix


def main() -> None:
    for rel in REQUIRED_SOURCE_FILES:
        if not (ROOT / rel).exists():
            fail(f"missing required source-layer file: {rel}")

    schema_errors, schema_stats = validate_repository_json(ROOT)
    if schema_errors:
        fail("JSON Schema validation failed:\n  " + "\n  ".join(schema_errors))

    # Common test-matrix schema files must agree with the registry that drives
    # build_all. This catches copy-forward schema identity drift without forcing
    # a broad schema migration.
    for spec in COMMON_TEST_MATRICES:
        schema_name = spec["metadata_filename"].replace(".json", ".schema.json")
        schema_doc = load_json(SCHEMA_DIR / schema_name)
        schema_id = schema_doc.get("$id", "")
        if not isinstance(schema_id, str) or not schema_id.endswith(f"/{schema_name}"):
            fail(f"common test-matrix schema $id does not end with /{schema_name}: {schema_id}")
        schema_const = schema_doc.get("properties", {}).get("schema", {}).get("const")
        if schema_const != spec["schema_const"]:
            fail(f"common test-matrix schema const mismatch for {schema_name}: {schema_const} != {spec['schema_const']}")
    runtime_detritus = []
    runtime_detritus.extend(str(path.relative_to(ROOT)) for path in ROOT.rglob("__pycache__") if path.is_dir())
    runtime_detritus.extend(str(path.relative_to(ROOT)) for path in ROOT.rglob("*.pyc") if path.is_file())
    if runtime_detritus:
        fail(f"runtime detritus present in package: {sorted(runtime_detritus)[:10]}")
    if not GENERATED.exists():
        fail("missing generated/ directory; run make lint to rebuild")
    for name in REQUIRED_GENERATED_FILES:
        if not (GENERATED / name).exists():
            fail(f"missing generated file: generated/{name}")
    for name in LEGACY_TOP_LEVEL_GENERATED:
        if (ROOT / name).exists():
            fail(f"legacy generated file remains at package root: {name}")

    files = numbered_archive_paths()
    if not files:
        fail("no numbered archive files found")
    expected_files = [str(p.relative_to(ROOT)) for p in files]

    numbers = []
    titles = []
    theses = []
    for path in files:
        m = NUMBERED_NOTE_FILENAME_RE.fullmatch(path.name)
        if not m:
            fail(f"bad numbered filename: {path.name}")
        num = int(m.group(1))
        numbers.append(num)
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        heading = lines[0].strip() if lines else ""
        expected_heading_prefix = f"# {m.group(1)} — "
        if not heading.startswith(expected_heading_prefix):
            fail(f"heading mismatch in {path.name}: expected prefix '{expected_heading_prefix}'")
        for fragment in REQUIRED_EXACT:
            if fragment not in text:
                fail(f"missing section '{fragment}' in {path.name}")
        for group in REQUIRED_ANY_OF:
            if not any(fragment in text for fragment in group):
                fail(f"missing one of {group} in {path.name}")
        if re.search(r"(?i)https?://\S+\.pdf(?:\?\S*)?", text):
            fail(f"raw PDF link found in archive note: {path.name}")
        quote_lines = [line for line in lines if line.lstrip().startswith(">")]
        if len(quote_lines) > 8:
            fail(f"too many quoted lines in archive note: {path.name}")
        titles.append((path.name, heading))
        theses.append((path.name, first_thesis(path)))

    if len(numbers) != len(set(numbers)):
        fail("duplicate archive numbers detected")
    if numbers != sorted(numbers):
        fail("archive numbering is not sorted")

    title_map = {}
    for fname, title in titles:
        title_map.setdefault(title, []).append(fname)
    dup_titles = {title: names for title, names in title_map.items() if len(names) > 1}
    if dup_titles:
        fail(f"duplicate archive titles detected: {dup_titles}")

    thesis_map = {}
    for fname, thesis in theses:
        if thesis:
            thesis_map.setdefault(thesis, []).append(fname)
    dup_theses = {thesis: names for thesis, names in thesis_map.items() if len(names) > 1}
    if dup_theses:
        fail(f"duplicate one-line theses detected: {dup_theses}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    index = (ROOT / "INDEX.md").read_text(encoding="utf-8")
    archive_structure = (ROOT / "ARCHIVE_STRUCTURE.md").read_text(encoding="utf-8")
    generated_sources_md = (GENERATED / "SOURCES.md").read_text(encoding="utf-8")
    for generated_name, max_bytes in GENERATED_READER_BUDGETS.items():
        generated_path = GENERATED / generated_name
        if generated_path.exists() and generated_path.stat().st_size > max_bytes:
            fail(
                f"generated/{generated_name} exceeds compact-reader budget: "
                f"{generated_path.stat().st_size} > {max_bytes} bytes"
            )
    threads_md = (GENERATED / "THREADS.md").read_text(encoding="utf-8")
    if "## Full-detail route" not in threads_md:
        fail("generated/THREADS.md is missing compact-reader full-detail route notice")
    if CURRENT_REV not in readme:
        fail(f"README does not mention current revision {CURRENT_REV}")
    if CURRENT_REV not in changelog:
        fail(f"CHANGELOG does not mention current revision {CURRENT_REV}")
    if CURRENT_REV not in archive_structure:
        fail(f"ARCHIVE_STRUCTURE does not mention current revision {CURRENT_REV}")
    if f"Sources used for {CURRENT_REV}" not in generated_sources_md:
        fail("generated/SOURCES.md does not mention current revision")
    latest_prefix = f"{max(numbers):03d}-"
    if latest_prefix not in index:
        fail(f"INDEX does not include latest archive addition {latest_prefix}")
    for required in CURRENT_NOTES:
        basename = Path(required).name
        if basename not in readme:
            fail(f"README does not list current note {basename}")
        if basename not in index:
            fail(f"INDEX does not list current note {basename}")
        if basename not in archive_structure:
            fail(f"ARCHIVE_STRUCTURE does not list current note {basename}")
        if basename not in generated_sources_md:
            fail(f"generated/SOURCES.md does not list current note {basename}")

    markdown_h1_rels = ["README.md", "CHANGELOG.md", "INDEX.md", "ARCHIVE_STRUCTURE.md", "generated/THREADS.md", "generated/SOURCES.md", "generated/CASE_PACKET_MATRIX.md", "generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.md", "generated/RETIREMENT_CANDIDATES.md", "generated/CLAIMS.md", "generated/DEFEAT_TESTS.md", "generated/HANDBACK_TESTS.md", "generated/SUPPLIER_DEPENDENCY_TESTS.md", "generated/SYMBOLIC_AUTHORITY_TESTS.md", "generated/CAPACITY_TESTS.md", "generated/MODEL_DECISION_TESTS.md", "generated/GENERATIVE_ASSISTANT_TESTS.md", "generated/STAFF_COPILOT_TESTS.md", "generated/TRANSITION_RECEIPT_TESTS.md", "generated/PLATFORM_MIGRATION_TESTS.md", "generated/ECOLOGICAL_PERSONHOOD_TESTS.md", "generated/ENTITLEMENT_CONTINUITY_TESTS.md", "generated/PAYMENT_REDRESS_TESTS.md", "generated/EVIDENCE_RECEIPTS.md", "generated/SOURCE_CLAIM_RECEIPTS.md", "generated/OUTCOME_TAIL_PLANS.md", "generated/TAIL_SAMPLING_GATES.md", "generated/FIELD_INTAKE_CONTROLS.md", "generated/FIELDWORK_AUTHORIZATION_GATES.md", "generated/FIELDWORK_EXECUTION_CONTROLS.md", "generated/FIELDWORK_RELEASE_CONTROLS.md", "generated/SOURCE_HEALTH.md", "generated/GAP_LEDGER.md", "generated/GENERATED_SURFACE_AUDIT.md"]
    for spec in COMMON_TEST_MATRICES:
        rel = f"generated/{spec['output_stem']}.md"
        if rel not in markdown_h1_rels:
            markdown_h1_rels.append(rel)
    for rel in markdown_h1_rels:
        text = (ROOT / rel).read_text(encoding="utf-8")
        h1s = re.findall(r"(?m)^# ", text)
        if len(h1s) != 1:
            fail(f"{rel} should contain exactly one H1 heading")

    meta_number_map: dict[str, list[str]] = {}
    for meta_path in sorted(ROOT.glob("meta-*.md")):
        m = re.match(r"^meta-(\d{4})-.*\.md$", meta_path.name)
        if not m:
            fail(f"bad meta note filename: {meta_path.name}")
        meta_number_map.setdefault(m.group(1), []).append(meta_path.name)
        meta_text = meta_path.read_text(encoding="utf-8")
        if len(re.findall(r"(?m)^# ", meta_text)) != 1:
            fail(f"{meta_path.name} should contain exactly one H1 heading")
    duplicate_meta_numbers = {num: names for num, names in meta_number_map.items() if len(names) > 1}
    if duplicate_meta_numbers:
        fail(f"duplicate meta note numbers detected: {duplicate_meta_numbers}")

    source_catalog = load_json(SOURCES_DIR / "source_catalog.json")
    if source_catalog.get("schema") != "radical-governance-source-catalog-v1":
        fail("sources/source_catalog.json missing expected schema")
    if source_catalog.get("revision") != CURRENT_REV:
        fail(f"sources/source_catalog.json revision mismatch: expected {CURRENT_REV}")
    source_notes = source_catalog.get("notes", {})
    if set(source_notes) != set(expected_files):
        fail("sources/source_catalog.json note keys do not exactly match archive directory")
    for rel in expected_files:
        validate_source_groups(source_notes, rel, "sources/source_catalog.json")

    source_keys = load_json(SOURCES_DIR / "source_keys.json")
    if source_keys.get("schema") != "radical-governance-source-keys-v1":
        fail("sources/source_keys.json missing expected schema")
    if source_keys.get("revision") != CURRENT_REV:
        fail(f"sources/source_keys.json revision mismatch: expected {CURRENT_REV}")
    source_key_registry = source_keys.get("keys", {})
    if not source_key_registry:
        fail("sources/source_keys.json has no source keys")
    for key, entry in source_key_registry.items():
        for field in ["title", "publisher", "url"]:
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                fail(f"sources/source_keys.json entry {key} missing {field}")
        if not entry["url"].startswith("http"):
            fail(f"sources/source_keys.json url does not start with http: {key}")
    source_key_urls: dict[str, list[str]] = {}
    for key, entry in source_key_registry.items():
        norm_url = entry.get("url", "").rstrip("/")
        source_key_urls.setdefault(norm_url, []).append(key)
    duplicate_source_key_urls = {url: keys for url, keys in source_key_urls.items() if len(keys) > 1}
    if duplicate_source_key_urls:
        fail(f"sources/source_keys.json duplicate URLs across source keys: {duplicate_source_key_urls}")
    for rel, payload in source_notes.items():
        for group in payload.get("groups", []):
            group_key = group.get("source_key")
            if group_key and group_key not in source_key_registry:
                fail(f"source_catalog group references unknown source_key {group_key}: {rel}")


    source_health = load_json(METADATA_DIR / "source_health.json")
    if source_health.get("schema") != "radical-governance-source-health-v1":
        fail("metadata/source_health.json missing expected schema")
    if source_health.get("revision") != CURRENT_REV:
        fail(f"metadata/source_health.json revision mismatch: expected {CURRENT_REV}")
    for key, entry in source_health.get("entries", {}).items():
        if key not in source_key_registry:
            fail(f"metadata/source_health.json references unknown source_key {key}")
        for field in ["source_class", "publisher_class", "jurisdiction", "expected_volatility", "health_status"]:
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                fail(f"metadata/source_health.json entry {key} missing {field}")
        for ref_field in ["supersedes", "superseded_by", "fallback_source_keys"]:
            for ref_key in entry.get(ref_field, []):
                if ref_key not in source_key_registry:
                    fail(f"metadata/source_health.json entry {key} {ref_field} unknown source_key {ref_key}")
    generated_source_health = load_json(GENERATED / "SOURCE_HEALTH.json")
    if generated_source_health.get("revision") != CURRENT_REV:
        fail(f"generated/SOURCE_HEALTH.json revision mismatch: expected {CURRENT_REV}")
    generated_health_keys = {row.get("source_key") for row in generated_source_health.get("sources", [])}
    if generated_health_keys != set(source_key_registry):
        fail("generated/SOURCE_HEALTH.json source keys mismatch sources/source_keys.json")
    if generated_source_health.get("source_key_count") != len(source_key_registry):
        fail("generated/SOURCE_HEALTH.json source_key_count mismatch sources/source_keys.json")
    if generated_source_health.get("manual_health_entry_count") != len(source_health.get("entries", {})):
        fail("generated/SOURCE_HEALTH.json manual health entry count mismatch metadata/source_health.json")
    normalized_status_counts = generated_source_health.get("normalized_health_status_counts")
    normalized_volatility_counts = generated_source_health.get("normalized_expected_volatility_counts")
    taxonomy_pressure = generated_source_health.get("taxonomy_pressure")
    if not isinstance(normalized_status_counts, dict) or not normalized_status_counts:
        fail("generated/SOURCE_HEALTH.json missing normalized_health_status_counts")
    if not isinstance(normalized_volatility_counts, dict) or not normalized_volatility_counts:
        fail("generated/SOURCE_HEALTH.json missing normalized_expected_volatility_counts")
    if not isinstance(taxonomy_pressure, list) or len(taxonomy_pressure) < 2:
        fail("generated/SOURCE_HEALTH.json missing taxonomy_pressure rows")
    generated_health_rows = generated_source_health.get("sources", [])
    for row in generated_health_rows:
        if "normalized_health_status" not in row or "normalized_expected_volatility" not in row:
            fail(f"generated/SOURCE_HEALTH.json source row missing normalized taxonomy fields: {row.get('source_key')}")
    source_health_taxonomy = load_json(METADATA_DIR / "source_health_taxonomy.json")
    if source_health_taxonomy.get("schema") != "radical-governance-source-health-taxonomy-v1":
        fail("metadata/source_health_taxonomy.json missing expected schema")
    if source_health_taxonomy.get("revision") != CURRENT_REV:
        fail(f"metadata/source_health_taxonomy.json revision mismatch: expected {CURRENT_REV}")
    taxonomy_fields = source_health_taxonomy.get("fields", {})
    for field in ["health_status", "expected_volatility"]:
        if field not in taxonomy_fields or not isinstance(taxonomy_fields[field], dict) or not taxonomy_fields[field]:
            fail(f"metadata/source_health_taxonomy.json missing taxonomy aliases for {field}")
    if generated_source_health.get("source_health_taxonomy_source") != "metadata/source_health_taxonomy.json":
        fail("generated/SOURCE_HEALTH.json must identify metadata/source_health_taxonomy.json")
    if sorted(taxonomy_fields) != generated_source_health.get("taxonomy_alias_fields"):
        fail("generated/SOURCE_HEALTH.json taxonomy_alias_fields mismatch metadata/source_health_taxonomy.json")

    evidence_receipts = load_json(METADATA_DIR / "evidence_receipts.json")
    if evidence_receipts.get("schema") != "radical-governance-evidence-receipts-v1":
        fail("metadata/evidence_receipts.json missing expected schema")
    if evidence_receipts.get("revision") != CURRENT_REV:
        fail(f"metadata/evidence_receipts.json revision mismatch: expected {CURRENT_REV}")
    receipt_ids = set(evidence_receipts.get("receipts", {}))
    if not receipt_ids:
        fail("metadata/evidence_receipts.json must contain at least one receipt")
    proof_floor_labels = evidence_receipts.get("proof_floor_labels", {})
    if not isinstance(proof_floor_labels, dict) or "field_validated_person_outcome" not in proof_floor_labels:
        fail("metadata/evidence_receipts.json must declare proof_floor_labels including field_validated_person_outcome")
    receipt_gap_ledger = load_json(METADATA_DIR / "gap_ledger.json")
    known_gap_ids = set(receipt_gap_ledger.get("gaps", {}))
    receipt_blocker_map: dict[str, list[str]] = {}
    proof_floor_counts: dict[str, int] = {}
    material_outcome_dimension_counts: dict[str, int] = {}
    source_receipt_level_counts: dict[str, int] = {}
    for receipt_id, receipt in evidence_receipts.get("receipts", {}).items():
        if not receipt_id.startswith("ER-"):
            fail(f"evidence receipt id should start with ER-: {receipt_id}")
        for note_number in receipt.get("archive_notes", []):
            if int(note_number) not in numbers:
                fail(f"evidence receipt {receipt_id} references unknown archive note {note_number}")
        for source_key in receipt.get("source_keys", []):
            if source_key not in source_key_registry:
                fail(f"evidence receipt {receipt_id} references unknown source key {source_key}")
        proof_status = receipt.get("proof_status", "")
        if proof_status.startswith("field_validated") or proof_status.startswith("validated") or proof_status == "complete":
            fail(f"evidence receipt {receipt_id} claims validation rather than pilot status: {proof_status}")
        if not receipt.get("affected_person_gap", "").strip():
            fail(f"evidence receipt {receipt_id} lacks affected_person_gap")
        for field in ["proof_floor", "denominator_gap", "closure_blocker_for", "can_close_gap", "closure_rule"]:
            if field not in receipt:
                fail(f"evidence receipt {receipt_id} missing closure-gate field {field}")
        for field in ["material_outcome_dimensions", "field_sample_requirement", "source_receipt_level"]:
            if field not in receipt:
                fail(f"evidence receipt {receipt_id} missing material/source receipt field {field}")
        if not isinstance(receipt.get("material_outcome_dimensions"), list) or not receipt["material_outcome_dimensions"]:
            fail(f"evidence receipt {receipt_id} must have non-empty material_outcome_dimensions")
        for dimension in receipt.get("material_outcome_dimensions", []):
            if not isinstance(dimension, str) or not dimension.strip():
                fail(f"evidence receipt {receipt_id} has invalid material_outcome_dimensions entry")
            material_outcome_dimension_counts[dimension] = material_outcome_dimension_counts.get(dimension, 0) + 1
        if not isinstance(receipt.get("field_sample_requirement"), str) or not receipt["field_sample_requirement"].strip():
            fail(f"evidence receipt {receipt_id} lacks field_sample_requirement")
        if not isinstance(receipt.get("source_receipt_level"), str) or not receipt["source_receipt_level"].strip():
            fail(f"evidence receipt {receipt_id} lacks source_receipt_level")
        source_receipt_level = receipt.get("source_receipt_level")
        source_receipt_level_counts[source_receipt_level] = source_receipt_level_counts.get(source_receipt_level, 0) + 1
        proof_floor = receipt.get("proof_floor")
        if proof_floor not in proof_floor_labels:
            fail(f"evidence receipt {receipt_id} has unknown proof_floor {proof_floor}")
        proof_floor_counts[proof_floor] = proof_floor_counts.get(proof_floor, 0) + 1
        if not isinstance(receipt.get("denominator_gap"), str) or not receipt["denominator_gap"].strip():
            fail(f"evidence receipt {receipt_id} lacks denominator_gap")
        blockers = receipt.get("closure_blocker_for")
        if not isinstance(blockers, list):
            fail(f"evidence receipt {receipt_id} closure_blocker_for is not a list")
        for gap_id in blockers:
            if gap_id not in known_gap_ids:
                fail(f"evidence receipt {receipt_id} blocks unknown gap {gap_id}")
            receipt_blocker_map.setdefault(gap_id, []).append(receipt_id)
        can_close_gap = receipt.get("can_close_gap")
        if not isinstance(can_close_gap, bool):
            fail(f"evidence receipt {receipt_id} can_close_gap must be boolean")
        if can_close_gap and proof_floor != "field_validated_person_outcome":
            fail(f"evidence receipt {receipt_id} claims closure below field_validated_person_outcome")
        if proof_floor != "field_validated_person_outcome" and not blockers:
            fail(f"evidence receipt {receipt_id} below field validation must block at least one live gap")
    for required_gap in ["GAP-029-affected-person-outcome-validation", "GAP-031-source-evidence-preservation-and-claim-capture"]:
        if required_gap not in receipt_blocker_map:
            fail(f"evidence receipts must include closure blockers for {required_gap}")
        if str(receipt_gap_ledger.get("gaps", {}).get(required_gap, {}).get("status", "")).startswith("repaired"):
            blocking_nonfield = [
                rid for rid in receipt_blocker_map[required_gap]
                if evidence_receipts["receipts"][rid].get("proof_floor") != "field_validated_person_outcome"
            ]
            if blocking_nonfield:
                fail(f"gap {required_gap} is repaired despite non-field closure blocker(s): {blocking_nonfield}")
    generated_evidence_receipts = load_json(GENERATED / "EVIDENCE_RECEIPTS.json")
    if generated_evidence_receipts.get("revision") != CURRENT_REV:
        fail("generated/EVIDENCE_RECEIPTS.json revision mismatch")
    if generated_evidence_receipts.get("receipt_count") != len(receipt_ids):
        fail("generated/EVIDENCE_RECEIPTS.json receipt count mismatch metadata/evidence_receipts.json")
    generated_receipt_ids = {row.get("receipt_id") for row in generated_evidence_receipts.get("receipts", [])}
    if generated_receipt_ids != receipt_ids:
        fail("generated/EVIDENCE_RECEIPTS.json receipt ids do not match metadata/evidence_receipts.json")
    if generated_evidence_receipts.get("proof_floor_counts") != dict(sorted(proof_floor_counts.items())):
        fail("generated/EVIDENCE_RECEIPTS.json proof_floor_counts mismatch metadata/evidence_receipts.json")
    if generated_evidence_receipts.get("material_outcome_dimension_counts") != dict(sorted(material_outcome_dimension_counts.items())):
        fail("generated/EVIDENCE_RECEIPTS.json material_outcome_dimension_counts mismatch metadata/evidence_receipts.json")
    if generated_evidence_receipts.get("source_receipt_level_counts") != dict(sorted(source_receipt_level_counts.items())):
        fail("generated/EVIDENCE_RECEIPTS.json source_receipt_level_counts mismatch metadata/evidence_receipts.json")
    expected_blocker_map = {gap: sorted(ids) for gap, ids in sorted(receipt_blocker_map.items())}
    actual_blocker_map = {gap: sorted(ids) for gap, ids in generated_evidence_receipts.get("closure_blocker_map", {}).items()}
    if actual_blocker_map != expected_blocker_map:
        fail("generated/EVIDENCE_RECEIPTS.json closure_blocker_map mismatch metadata/evidence_receipts.json")

    source_claim_receipts = load_json(METADATA_DIR / "source_claim_receipts.json")
    if source_claim_receipts.get("schema") != "radical-governance-source-claim-receipts-v1":
        fail("metadata/source_claim_receipts.json missing expected schema")
    if source_claim_receipts.get("revision") != CURRENT_REV:
        fail(f"metadata/source_claim_receipts.json revision mismatch: expected {CURRENT_REV}")
    source_claim_ids = set(source_claim_receipts.get("receipts", {}))
    if len(source_claim_ids) < 5:
        fail("metadata/source_claim_receipts.json must contain at least five claim-passage receipts")
    claim_level_counts: dict[str, int] = {}
    claim_preservation_counts: dict[str, int] = {}
    claim_blocker_map: dict[str, list[str]] = {}
    for receipt_id, receipt in source_claim_receipts.get("receipts", {}).items():
        if not receipt_id.startswith("SCR-"):
            fail(f"source-claim receipt id should start with SCR-: {receipt_id}")
        if receipt.get("source_key") not in source_key_registry:
            fail(f"source-claim receipt {receipt_id} references unknown source key {receipt.get('source_key')}")
        for note_number in receipt.get("archive_notes", []):
            if int(note_number) not in numbers:
                fail(f"source-claim receipt {receipt_id} references unknown archive note {note_number}")
        anchor = receipt.get("anchor_quote", "")
        if not isinstance(anchor, str) or not anchor.strip():
            fail(f"source-claim receipt {receipt_id} lacks short anchor quote")
        if len(anchor.split()) > 12:
            fail(f"source-claim receipt {receipt_id} anchor_quote is too long for copyright-light navigation")
        if not receipt.get("passage_summary", "").strip():
            fail(f"source-claim receipt {receipt_id} lacks passage_summary")
        if not receipt.get("evidence_limit", "").strip():
            fail(f"source-claim receipt {receipt_id} lacks evidence_limit")
        if not receipt.get("next_preservation_step", "").strip():
            fail(f"source-claim receipt {receipt_id} lacks next_preservation_step")
        level = receipt.get("source_receipt_level", "")
        preservation = receipt.get("preservation_status", "")
        if not level or not preservation:
            fail(f"source-claim receipt {receipt_id} missing source_receipt_level or preservation_status")
        claim_level_counts[level] = claim_level_counts.get(level, 0) + 1
        claim_preservation_counts[preservation] = claim_preservation_counts.get(preservation, 0) + 1
        if preservation in {"preserved", "preserved_complete", "snapshot_preserved", "fingerprinted"} and not any(token in level for token in ["snapshot", "fingerprint", "archival"]):
            fail(f"source-claim receipt {receipt_id} claims preservation without snapshot/fingerprint/archival level")
        blockers = receipt.get("closure_blocker_for", [])
        if not isinstance(blockers, list) or not blockers:
            fail(f"source-claim receipt {receipt_id} must block at least one live gap")
        for gap_id in blockers:
            if gap_id not in known_gap_ids:
                fail(f"source-claim receipt {receipt_id} blocks unknown gap {gap_id}")
            claim_blocker_map.setdefault(gap_id, []).append(receipt_id)
    for required_gap in ["GAP-031-source-evidence-preservation-and-claim-capture"]:
        if required_gap not in claim_blocker_map:
            fail(f"source-claim receipts must include closure blockers for {required_gap}")
    generated_source_claim_receipts = load_json(GENERATED / "SOURCE_CLAIM_RECEIPTS.json")
    if generated_source_claim_receipts.get("revision") != CURRENT_REV:
        fail("generated/SOURCE_CLAIM_RECEIPTS.json revision mismatch")
    if generated_source_claim_receipts.get("receipt_count") != len(source_claim_ids):
        fail("generated/SOURCE_CLAIM_RECEIPTS.json receipt count mismatch metadata/source_claim_receipts.json")
    if {row.get("receipt_id") for row in generated_source_claim_receipts.get("receipts", [])} != source_claim_ids:
        fail("generated/SOURCE_CLAIM_RECEIPTS.json receipt ids do not match metadata/source_claim_receipts.json")
    if generated_source_claim_receipts.get("source_receipt_level_counts") != dict(sorted(claim_level_counts.items())):
        fail("generated/SOURCE_CLAIM_RECEIPTS.json source_receipt_level_counts mismatch metadata/source_claim_receipts.json")
    if generated_source_claim_receipts.get("preservation_status_counts") != dict(sorted(claim_preservation_counts.items())):
        fail("generated/SOURCE_CLAIM_RECEIPTS.json preservation_status_counts mismatch metadata/source_claim_receipts.json")
    expected_claim_blocker_map = {gap: sorted(ids) for gap, ids in sorted(claim_blocker_map.items())}
    actual_claim_blocker_map = {gap: sorted(ids) for gap, ids in generated_source_claim_receipts.get("closure_blocker_map", {}).items()}
    if actual_claim_blocker_map != expected_claim_blocker_map:
        fail("generated/SOURCE_CLAIM_RECEIPTS.json closure_blocker_map mismatch metadata/source_claim_receipts.json")

    outcome_tail_plans = load_json(METADATA_DIR / "outcome_tail_plans.json")
    if outcome_tail_plans.get("schema") != "radical-governance-outcome-tail-plans-v1":
        fail("metadata/outcome_tail_plans.json missing expected schema")
    if outcome_tail_plans.get("revision") != CURRENT_REV:
        fail(f"metadata/outcome_tail_plans.json revision mismatch: expected {CURRENT_REV}")
    plan_ids = set(outcome_tail_plans.get("plans", {}))
    if len(plan_ids) < 2:
        fail("metadata/outcome_tail_plans.json must include at least UI and housing tail plans")
    plan_gap_map: dict[str, list[str]] = {}
    outcome_field_counts: dict[str, int] = {}
    cohort_count = 0
    for plan_id, plan in outcome_tail_plans.get("plans", {}).items():
        if not plan_id.startswith("OTP-"):
            fail(f"outcome-tail plan id should start with OTP-: {plan_id}")
        for gap_id in plan.get("linked_gaps", []):
            if gap_id not in known_gap_ids:
                fail(f"outcome-tail plan {plan_id} links unknown gap {gap_id}")
            plan_gap_map.setdefault(gap_id, []).append(plan_id)
        for rid in plan.get("linked_evidence_receipts", []):
            if rid not in receipt_ids:
                fail(f"outcome-tail plan {plan_id} links unknown evidence receipt {rid}")
        for scr_id in plan.get("linked_source_claim_receipts", []):
            if scr_id not in source_claim_ids:
                fail(f"outcome-tail plan {plan_id} links unknown source-claim receipt {scr_id}")
        for note_number in plan.get("archive_notes", []):
            if int(note_number) not in numbers:
                fail(f"outcome-tail plan {plan_id} references unknown archive note {note_number}")
        cohorts = plan.get("cohorts", [])
        if not isinstance(cohorts, list) or len(cohorts) < 4:
            fail(f"outcome-tail plan {plan_id} needs at least four denominator cohorts")
        cohort_count += len(cohorts)
        for cohort in cohorts:
            if not cohort.get("cohort_id") or not cohort.get("denominator_role") or not cohort.get("exclusion_risk"):
                fail(f"outcome-tail plan {plan_id} has incomplete cohort row")
        fields = plan.get("outcome_tail_fields", [])
        if not isinstance(fields, list) or len(fields) < 6:
            fail(f"outcome-tail plan {plan_id} needs at least six material outcome tail fields")
        for field in fields:
            outcome_field_counts[field] = outcome_field_counts.get(field, 0) + 1
        if not plan.get("not_allowed_to_store"):
            fail(f"outcome-tail plan {plan_id} must declare not_allowed_to_store privacy exclusions")
        if not plan.get("closure_floor") or not plan.get("closure_blocker"):
            fail(f"outcome-tail plan {plan_id} lacks closure floor/blocker text")
    for required_gap in ["GAP-029-affected-person-outcome-validation", "GAP-033-power-distribution-and-material-outcome-theory"]:
        if required_gap not in plan_gap_map:
            fail(f"outcome-tail plans must cover {required_gap}")
    generated_outcome_tail_plans = load_json(GENERATED / "OUTCOME_TAIL_PLANS.json")
    if generated_outcome_tail_plans.get("revision") != CURRENT_REV:
        fail("generated/OUTCOME_TAIL_PLANS.json revision mismatch")
    if generated_outcome_tail_plans.get("plan_count") != len(plan_ids):
        fail("generated/OUTCOME_TAIL_PLANS.json plan count mismatch metadata/outcome_tail_plans.json")
    if generated_outcome_tail_plans.get("cohort_count") != cohort_count:
        fail("generated/OUTCOME_TAIL_PLANS.json cohort count mismatch metadata/outcome_tail_plans.json")
    if generated_outcome_tail_plans.get("outcome_tail_field_counts") != dict(sorted(outcome_field_counts.items())):
        fail("generated/OUTCOME_TAIL_PLANS.json outcome_tail_field_counts mismatch metadata/outcome_tail_plans.json")

    tail_sampling_gates = load_json(METADATA_DIR / "tail_sampling_gates.json")
    if tail_sampling_gates.get("schema") != "radical-governance-tail-sampling-gates-v1":
        fail("metadata/tail_sampling_gates.json missing expected schema")
    if tail_sampling_gates.get("revision") != CURRENT_REV:
        fail(f"metadata/tail_sampling_gates.json revision mismatch: expected {CURRENT_REV}")
    gate_ids = set(tail_sampling_gates.get("gates", {}))
    if len(gate_ids) < 2:
        fail("metadata/tail_sampling_gates.json must include at least UI and housing sampling gates")
    gate_status_counts: dict[str, int] = {}
    gate_gap_map: dict[str, list[str]] = {}
    gate_plan_map: dict[str, list[str]] = {}
    gate_source_claim_counts: dict[str, int] = {}
    gate_material_field_counts: dict[str, int] = {}
    gate_cohort_count = 0
    privacy_forbidden_terms = {"name", "ssn", "address", "claim_number", "docket_number", "private_screenshot"}
    for gate_id, gate in tail_sampling_gates.get("gates", {}).items():
        if not gate_id.startswith("TSG-"):
            fail(f"tail sampling gate id should start with TSG-: {gate_id}")
        status = gate.get("gate_status", "")
        if any(token in status.lower() for token in ["complete", "validated", "repaired", "closed"]):
            fail(f"tail sampling gate {gate_id} claims closure-like status: {status}")
        gate_status_counts[status] = gate_status_counts.get(status, 0) + 1
        plan_id = gate.get("outcome_tail_plan")
        if plan_id not in plan_ids:
            fail(f"tail sampling gate {gate_id} links unknown outcome_tail_plan {plan_id}")
        gate_plan_map.setdefault(plan_id, []).append(gate_id)
        plan = outcome_tail_plans["plans"].get(plan_id, {})
        plan_cohorts = {cohort.get("cohort_id") for cohort in plan.get("cohorts", [])}
        gate_cohorts = {cohort.get("cohort_id") for cohort in gate.get("cohort_requirements", [])}
        if plan_cohorts - gate_cohorts:
            fail(f"tail sampling gate {gate_id} omits outcome-tail plan cohort(s): {sorted(plan_cohorts - gate_cohorts)}")
        gate_cohort_count += len(gate.get("cohort_requirements", []))
        material_fields = gate.get("material_fields", [])
        if not isinstance(material_fields, list) or not material_fields:
            fail(f"tail sampling gate {gate_id} missing material_fields")
        for field in material_fields:
            gate_material_field_counts[field] = gate_material_field_counts.get(field, 0) + 1
        missing_plan_fields = set(plan.get("outcome_tail_fields", [])) - set(material_fields)
        if missing_plan_fields:
            fail(f"tail sampling gate {gate_id} material_fields omit plan outcome_tail_fields: {sorted(missing_plan_fields)}")
        for gap_id in gate.get("linked_gaps", []):
            if gap_id not in known_gap_ids:
                fail(f"tail sampling gate {gate_id} links unknown gap {gap_id}")
            gate_gap_map.setdefault(gap_id, []).append(gate_id)
        for required_gap in ["GAP-029-affected-person-outcome-validation", "GAP-031-source-evidence-preservation-and-claim-capture", "GAP-033-power-distribution-and-material-outcome-theory"]:
            if required_gap not in gate.get("linked_gaps", []):
                fail(f"tail sampling gate {gate_id} must block {required_gap}")
        for rid in gate.get("linked_source_claim_receipts", []):
            if rid not in source_claim_ids:
                fail(f"tail sampling gate {gate_id} links unknown source-claim receipt {rid}")
            gate_source_claim_counts[rid] = gate_source_claim_counts.get(rid, 0) + 1
        if len(gate.get("linked_source_claim_receipts", [])) < 4:
            fail(f"tail sampling gate {gate_id} needs multiple method/source-claim dependencies")
        for field in ["target_population", "sampling_frame", "nonresponse_bias_plan", "closure_blocker", "next_action"]:
            if not isinstance(gate.get(field), str) or not gate[field].strip():
                fail(f"tail sampling gate {gate_id} missing {field}")
        for field in ["fieldwork_controls", "material_followup_windows", "privacy_controls", "source_preservation_controls", "cannot_store", "disqualifiers"]:
            if not isinstance(gate.get(field), list) or not gate[field]:
                fail(f"tail sampling gate {gate_id} missing non-empty {field}")
        cannot_store = {str(item).lower() for item in gate.get("cannot_store", [])}
        if not privacy_forbidden_terms.intersection(cannot_store):
            fail(f"tail sampling gate {gate_id} cannot_store lacks sensitive-record exclusions")
        for cohort in gate.get("cohort_requirements", []):
            for field in ["cohort_id", "minimum_observation_goal", "required_outcome_fields", "denominator_audit"]:
                if field not in cohort:
                    fail(f"tail sampling gate {gate_id} cohort row missing {field}")
            if not isinstance(cohort.get("required_outcome_fields"), list) or not cohort["required_outcome_fields"]:
                fail(f"tail sampling gate {gate_id} cohort {cohort.get('cohort_id')} missing required_outcome_fields")
    for required_gap in ["GAP-029-affected-person-outcome-validation", "GAP-031-source-evidence-preservation-and-claim-capture", "GAP-033-power-distribution-and-material-outcome-theory"]:
        if required_gap not in gate_gap_map:
            fail(f"tail sampling gates must include closure blockers for {required_gap}")
    generated_tail_sampling_gates = load_json(GENERATED / "TAIL_SAMPLING_GATES.json")
    if generated_tail_sampling_gates.get("revision") != CURRENT_REV:
        fail("generated/TAIL_SAMPLING_GATES.json revision mismatch")
    if generated_tail_sampling_gates.get("gate_count") != len(gate_ids):
        fail("generated/TAIL_SAMPLING_GATES.json gate count mismatch metadata/tail_sampling_gates.json")
    if generated_tail_sampling_gates.get("cohort_gate_count") != gate_cohort_count:
        fail("generated/TAIL_SAMPLING_GATES.json cohort count mismatch metadata/tail_sampling_gates.json")
    if {row.get("gate_id") for row in generated_tail_sampling_gates.get("gates", [])} != gate_ids:
        fail("generated/TAIL_SAMPLING_GATES.json gate ids do not match metadata/tail_sampling_gates.json")
    if generated_tail_sampling_gates.get("gate_status_counts") != dict(sorted(gate_status_counts.items())):
        fail("generated/TAIL_SAMPLING_GATES.json gate_status_counts mismatch metadata/tail_sampling_gates.json")
    if generated_tail_sampling_gates.get("source_claim_receipt_counts") != dict(sorted(gate_source_claim_counts.items())):
        fail("generated/TAIL_SAMPLING_GATES.json source_claim_receipt_counts mismatch metadata/tail_sampling_gates.json")
    if generated_tail_sampling_gates.get("material_field_counts") != dict(sorted(gate_material_field_counts.items())):
        fail("generated/TAIL_SAMPLING_GATES.json material_field_counts mismatch metadata/tail_sampling_gates.json")
    if generated_tail_sampling_gates.get("gap_gate_map") != {k: sorted(v) for k, v in sorted(gate_gap_map.items())}:
        fail("generated/TAIL_SAMPLING_GATES.json gap_gate_map mismatch metadata/tail_sampling_gates.json")
    if generated_tail_sampling_gates.get("plan_gate_map") != {k: sorted(v) for k, v in sorted(gate_plan_map.items())}:
        fail("generated/TAIL_SAMPLING_GATES.json plan_gate_map mismatch metadata/tail_sampling_gates.json")


    field_intake_controls = load_json(METADATA_DIR / "field_intake_controls.json")
    if field_intake_controls.get("schema") != "radical-governance-field-intake-controls-v1":
        fail("metadata/field_intake_controls.json missing expected schema")
    if field_intake_controls.get("revision") != CURRENT_REV:
        fail(f"metadata/field_intake_controls.json revision mismatch: expected {CURRENT_REV}")
    field_control_ids = set(field_intake_controls.get("controls", {}))
    if len(field_control_ids) < 2:
        fail("metadata/field_intake_controls.json must include at least UI and housing controls")
    required_method_receipts = {"SCR-HSR-001", "SCR-EXEMPT-001", "SCR-CONSENT-001", "SCR-CODED-001", "SCR-PII-001"}
    field_status_counts: dict[str, int] = {}
    field_gap_map: dict[str, list[str]] = {}
    field_sampling_gate_map: dict[str, list[str]] = {}
    field_outcome_plan_map: dict[str, list[str]] = {}
    field_source_claim_counts: dict[str, int] = {}
    prohibited_artifact_counts: dict[str, int] = {}
    required_prohibited = {"name", "address", "private_screenshot", "raw_audio", "raw_video", "contact_roster", "linkage_key", "partner_case_record"}
    for control_id, control in field_intake_controls.get("controls", {}).items():
        if not control_id.startswith("FIC-"):
            fail(f"field intake control id should start with FIC-: {control_id}")
        status = control.get("control_status", "")
        if "not_collected" not in status or any(token in status.lower() for token in ["complete", "validated", "repaired", "closed"]):
            fail(f"field intake control {control_id} must remain not_collected and non-closing: {status}")
        field_status_counts[status] = field_status_counts.get(status, 0) + 1
        gate_id = control.get("linked_sampling_gate")
        if gate_id not in gate_ids:
            fail(f"field intake control {control_id} links unknown sampling gate {gate_id}")
        field_sampling_gate_map.setdefault(gate_id, []).append(control_id)
        plan_id = control.get("linked_outcome_tail_plan")
        if plan_id not in plan_ids:
            fail(f"field intake control {control_id} links unknown outcome tail plan {plan_id}")
        field_outcome_plan_map.setdefault(plan_id, []).append(control_id)
        gate = tail_sampling_gates["gates"].get(gate_id, {})
        if gate.get("outcome_tail_plan") != plan_id:
            fail(f"field intake control {control_id} gate/plan mismatch: {gate_id} -> {gate.get('outcome_tail_plan')} vs {plan_id}")
        for gap_id in control.get("linked_gaps", []):
            if gap_id not in known_gap_ids:
                fail(f"field intake control {control_id} links unknown gap {gap_id}")
            field_gap_map.setdefault(gap_id, []).append(control_id)
        for required_gap in ["GAP-029-affected-person-outcome-validation", "GAP-031-source-evidence-preservation-and-claim-capture", "GAP-032-license-maintainer-contribution-governance", "GAP-033-power-distribution-and-material-outcome-theory"]:
            if required_gap not in control.get("linked_gaps", []):
                fail(f"field intake control {control_id} must block {required_gap}")
        linked_receipts = set(control.get("linked_source_claim_receipts", []))
        missing_receipts = required_method_receipts - linked_receipts
        if missing_receipts:
            fail(f"field intake control {control_id} missing method/privacy receipts: {sorted(missing_receipts)}")
        for rid in linked_receipts:
            if rid not in source_claim_ids:
                fail(f"field intake control {control_id} links unknown source-claim receipt {rid}")
            field_source_claim_counts[rid] = field_source_claim_counts.get(rid, 0) + 1
        for field in ["human_subjects_boundary", "closure_blocker", "next_action"]:
            if not isinstance(control.get(field), str) or not control[field].strip():
                fail(f"field intake control {control_id} missing {field}")
        for field in ["lawful_basis_floor", "consent_notice_floor", "recruitment_controls", "data_linkage_controls", "adverse_action_firewall", "permitted_cube_artifacts", "prohibited_cube_artifacts", "publication_controls", "stop_rules"]:
            if not isinstance(control.get(field), list) or not control[field]:
                fail(f"field intake control {control_id} missing non-empty {field}")
        lower_prohibited = {str(item).lower() for item in control.get("prohibited_cube_artifacts", [])}
        if len(required_prohibited - lower_prohibited) > 2:
            fail(f"field intake control {control_id} does not prohibit enough private/linkage artifacts: {sorted(required_prohibited - lower_prohibited)}")
        for item in lower_prohibited:
            prohibited_artifact_counts[item] = prohibited_artifact_counts.get(item, 0) + 1
        permitted_text = " ".join(control.get("permitted_cube_artifacts", [])).lower()
        if any(token in permitted_text for token in ["name", "address", "claim_number", "docket_number", "linkage_key", "contact_roster", "private_record"]):
            fail(f"field intake control {control_id} permitted artifacts appear to allow private identifiers")
        firewall_text = " ".join(control.get("adverse_action_firewall", [])).lower()
        if "refusal" not in firewall_text or not any(token in firewall_text for token in ["benefit", "services", "representation", "assistance"]):
            fail(f"field intake control {control_id} adverse_action_firewall lacks refusal/no-service-impact language")
        if "outside the cube" not in " ".join(control.get("data_linkage_controls", []) + [control.get("closure_blocker", "")]).lower():
            fail(f"field intake control {control_id} must keep linkage/key custody outside the cube")
    for required_gap in ["GAP-029-affected-person-outcome-validation", "GAP-031-source-evidence-preservation-and-claim-capture", "GAP-032-license-maintainer-contribution-governance", "GAP-033-power-distribution-and-material-outcome-theory"]:
        if required_gap not in field_gap_map:
            fail(f"field intake controls must include closure blockers for {required_gap}")
    generated_field_intake_controls = load_json(GENERATED / "FIELD_INTAKE_CONTROLS.json")
    if generated_field_intake_controls.get("revision") != CURRENT_REV:
        fail("generated/FIELD_INTAKE_CONTROLS.json revision mismatch")
    if generated_field_intake_controls.get("control_count") != len(field_control_ids):
        fail("generated/FIELD_INTAKE_CONTROLS.json control count mismatch metadata/field_intake_controls.json")
    if {row.get("control_id") for row in generated_field_intake_controls.get("controls", [])} != field_control_ids:
        fail("generated/FIELD_INTAKE_CONTROLS.json control ids do not match metadata/field_intake_controls.json")
    if generated_field_intake_controls.get("control_status_counts") != dict(sorted(field_status_counts.items())):
        fail("generated/FIELD_INTAKE_CONTROLS.json control_status_counts mismatch metadata/field_intake_controls.json")
    if generated_field_intake_controls.get("source_claim_receipt_counts") != dict(sorted(field_source_claim_counts.items())):
        fail("generated/FIELD_INTAKE_CONTROLS.json source_claim_receipt_counts mismatch metadata/field_intake_controls.json")
    if generated_field_intake_controls.get("prohibited_artifact_counts") != dict(sorted(prohibited_artifact_counts.items())):
        fail("generated/FIELD_INTAKE_CONTROLS.json prohibited_artifact_counts mismatch metadata/field_intake_controls.json")
    if generated_field_intake_controls.get("gap_control_map") != {k: sorted(v) for k, v in sorted(field_gap_map.items())}:
        fail("generated/FIELD_INTAKE_CONTROLS.json gap_control_map mismatch metadata/field_intake_controls.json")
    if generated_field_intake_controls.get("sampling_gate_control_map") != {k: sorted(v) for k, v in sorted(field_sampling_gate_map.items())}:
        fail("generated/FIELD_INTAKE_CONTROLS.json sampling_gate_control_map mismatch metadata/field_intake_controls.json")
    if generated_field_intake_controls.get("outcome_plan_control_map") != {k: sorted(v) for k, v in sorted(field_outcome_plan_map.items())}:
        fail("generated/FIELD_INTAKE_CONTROLS.json outcome_plan_control_map mismatch metadata/field_intake_controls.json")

    fieldwork_authorization_gates = load_json(METADATA_DIR / "fieldwork_authorization_gates.json")
    if fieldwork_authorization_gates.get("schema") != "radical-governance-fieldwork-authorization-gates-v1":
        fail("metadata/fieldwork_authorization_gates.json missing expected schema")
    if fieldwork_authorization_gates.get("revision") != CURRENT_REV:
        fail(f"metadata/fieldwork_authorization_gates.json revision mismatch: expected {CURRENT_REV}")
    authorization_gate_ids = set(fieldwork_authorization_gates.get("gates", {}))
    if len(authorization_gate_ids) < 2:
        fail("metadata/fieldwork_authorization_gates.json must include at least UI and housing authorization gates")
    required_authorization_receipts = {"SCR-A108-001", "SCR-ADMINDATA-001", "SCR-DATASHARE-001", "SCR-CIPSEA-001", "SCR-SAP-001", "SCR-80053-001"}
    required_authorizer_terms = ["owner", "legal", "privacy", "ethics", "custodian", "security"]
    authorization_status_counts: dict[str, int] = {}
    authorization_gap_map: dict[str, list[str]] = {}
    authorization_field_intake_map: dict[str, list[str]] = {}
    authorization_sampling_gate_map: dict[str, list[str]] = {}
    authorization_outcome_plan_map: dict[str, list[str]] = {}
    authorization_source_claim_counts: dict[str, int] = {}
    authorization_prohibited_counts: dict[str, int] = {}
    authorization_authorizer_counts: dict[str, int] = {}
    required_authorization_prohibited = {"name", "address", "contact_roster", "linkage_key", "raw_transcript", "raw_audio", "raw_video", "private_screenshot", "partner_case_record", "secure_environment_export_before_disclosure_review"}
    for auth_id, gate in fieldwork_authorization_gates.get("gates", {}).items():
        if not auth_id.startswith("FWAG-"):
            fail(f"fieldwork authorization gate id should start with FWAG-: {auth_id}")
        status = gate.get("authorization_status", "")
        if "not_authorized" not in status or any(token in status.lower() for token in ["authorized", "complete", "validated", "repaired", "closed"] if token != "authorized"):
            fail(f"fieldwork authorization gate {auth_id} must remain not_authorized and non-closing: {status}")
        if status.startswith("authorized") or status in {"complete", "closed", "validated"}:
            fail(f"fieldwork authorization gate {auth_id} claims authorization/closure: {status}")
        authorization_status_counts[status] = authorization_status_counts.get(status, 0) + 1
        control_id = gate.get("linked_field_intake_control")
        if control_id not in field_control_ids:
            fail(f"fieldwork authorization gate {auth_id} links unknown field-intake control {control_id}")
        authorization_field_intake_map.setdefault(control_id, []).append(auth_id)
        sampling_gate_id = gate.get("linked_sampling_gate")
        if sampling_gate_id not in gate_ids:
            fail(f"fieldwork authorization gate {auth_id} links unknown sampling gate {sampling_gate_id}")
        authorization_sampling_gate_map.setdefault(sampling_gate_id, []).append(auth_id)
        plan_id = gate.get("linked_outcome_tail_plan")
        if plan_id not in plan_ids:
            fail(f"fieldwork authorization gate {auth_id} links unknown outcome tail plan {plan_id}")
        authorization_outcome_plan_map.setdefault(plan_id, []).append(auth_id)
        linked_control = field_intake_controls.get("controls", {}).get(control_id, {})
        if linked_control.get("linked_sampling_gate") != sampling_gate_id or linked_control.get("linked_outcome_tail_plan") != plan_id:
            fail(f"fieldwork authorization gate {auth_id} control/gate/plan mismatch")
        for required_gap in ["GAP-029-affected-person-outcome-validation", "GAP-031-source-evidence-preservation-and-claim-capture", "GAP-032-license-maintainer-contribution-governance", "GAP-033-power-distribution-and-material-outcome-theory"]:
            if required_gap not in gate.get("linked_gaps", []):
                fail(f"fieldwork authorization gate {auth_id} must block {required_gap}")
        for gap_id in gate.get("linked_gaps", []):
            if gap_id not in known_gap_ids:
                fail(f"fieldwork authorization gate {auth_id} links unknown gap {gap_id}")
            authorization_gap_map.setdefault(gap_id, []).append(auth_id)
        linked_receipts = set(gate.get("linked_source_claim_receipts", []))
        missing_receipts = required_authorization_receipts - linked_receipts
        if missing_receipts:
            fail(f"fieldwork authorization gate {auth_id} missing authorization source receipts: {sorted(missing_receipts)}")
        for rid in linked_receipts:
            if rid not in source_claim_ids:
                fail(f"fieldwork authorization gate {auth_id} links unknown source-claim receipt {rid}")
            authorization_source_claim_counts[rid] = authorization_source_claim_counts.get(rid, 0) + 1
        for field in ["required_authorizers", "authorization_artifacts", "custody_handoff_controls", "minimum_necessary_fields", "prohibited_cube_artifacts", "disclosure_review_controls", "stop_conditions"]:
            if not isinstance(gate.get(field), list) or not gate[field]:
                fail(f"fieldwork authorization gate {auth_id} missing non-empty {field}")
        authorizer_text = " ".join(gate.get("required_authorizers", [])).lower()
        for term in required_authorizer_terms:
            if term not in authorizer_text:
                fail(f"fieldwork authorization gate {auth_id} required_authorizers lacks {term!r} role")
        for item in gate.get("required_authorizers", []):
            authorization_authorizer_counts[item] = authorization_authorizer_counts.get(item, 0) + 1
        prohibited_lower = {str(item).lower() for item in gate.get("prohibited_cube_artifacts", [])}
        if len(required_authorization_prohibited - prohibited_lower) > 2:
            fail(f"fieldwork authorization gate {auth_id} does not prohibit enough private/custody artifacts: {sorted(required_authorization_prohibited - prohibited_lower)}")
        for item in prohibited_lower:
            authorization_prohibited_counts[item] = authorization_prohibited_counts.get(item, 0) + 1
        custody_text = " ".join(gate.get("custody_handoff_controls", []) + [gate.get("handoff_boundary", "")]).lower()
        if "outside the cube" not in custody_text or "secure environment" not in custody_text:
            fail(f"fieldwork authorization gate {auth_id} must keep custody outside the cube and name secure environment controls")
        disclosure_text = " ".join(gate.get("disclosure_review_controls", [])).lower()
        if "disclosure" not in disclosure_text or not any(token in disclosure_text for token in ["suppression", "small-cell", "small cell"]):
            fail(f"fieldwork authorization gate {auth_id} disclosure controls must include disclosure review and suppression language")
        stop_text = " ".join(gate.get("stop_conditions", [])).lower()
        for token in ["owner", "privacy", "secure environment", "linkage key"]:
            if token not in stop_text:
                fail(f"fieldwork authorization gate {auth_id} stop_conditions lack {token!r}")
        for field in ["handoff_boundary", "closure_blocker", "next_action"]:
            if not isinstance(gate.get(field), str) or not gate[field].strip():
                fail(f"fieldwork authorization gate {auth_id} missing {field}")
        if any(token in (gate.get("closure_blocker", "") + gate.get("next_action", "")).lower() for token in ["gap closed", "field validation complete", "authorized to collect"]):
            fail(f"fieldwork authorization gate {auth_id} uses closure/authorization language in blocker or next_action")
    for required_gap in ["GAP-029-affected-person-outcome-validation", "GAP-031-source-evidence-preservation-and-claim-capture", "GAP-032-license-maintainer-contribution-governance", "GAP-033-power-distribution-and-material-outcome-theory"]:
        if required_gap not in authorization_gap_map:
            fail(f"fieldwork authorization gates must include closure blockers for {required_gap}")
    generated_fieldwork_authorization_gates = load_json(GENERATED / "FIELDWORK_AUTHORIZATION_GATES.json")
    if generated_fieldwork_authorization_gates.get("revision") != CURRENT_REV:
        fail("generated/FIELDWORK_AUTHORIZATION_GATES.json revision mismatch")
    if generated_fieldwork_authorization_gates.get("gate_count") != len(authorization_gate_ids):
        fail("generated/FIELDWORK_AUTHORIZATION_GATES.json gate count mismatch metadata/fieldwork_authorization_gates.json")
    if {row.get("gate_id") for row in generated_fieldwork_authorization_gates.get("gates", [])} != authorization_gate_ids:
        fail("generated/FIELDWORK_AUTHORIZATION_GATES.json gate ids do not match metadata/fieldwork_authorization_gates.json")
    if generated_fieldwork_authorization_gates.get("authorization_status_counts") != dict(sorted(authorization_status_counts.items())):
        fail("generated/FIELDWORK_AUTHORIZATION_GATES.json authorization_status_counts mismatch metadata/fieldwork_authorization_gates.json")
    if generated_fieldwork_authorization_gates.get("source_claim_receipt_counts") != dict(sorted(authorization_source_claim_counts.items())):
        fail("generated/FIELDWORK_AUTHORIZATION_GATES.json source_claim_receipt_counts mismatch metadata/fieldwork_authorization_gates.json")
    if generated_fieldwork_authorization_gates.get("prohibited_artifact_counts") != dict(sorted(authorization_prohibited_counts.items())):
        fail("generated/FIELDWORK_AUTHORIZATION_GATES.json prohibited_artifact_counts mismatch metadata/fieldwork_authorization_gates.json")
    if generated_fieldwork_authorization_gates.get("required_authorizer_counts") != dict(sorted(authorization_authorizer_counts.items())):
        fail("generated/FIELDWORK_AUTHORIZATION_GATES.json required_authorizer_counts mismatch metadata/fieldwork_authorization_gates.json")
    if generated_fieldwork_authorization_gates.get("gap_gate_map") != {k: sorted(v) for k, v in sorted(authorization_gap_map.items())}:
        fail("generated/FIELDWORK_AUTHORIZATION_GATES.json gap_gate_map mismatch metadata/fieldwork_authorization_gates.json")
    if generated_fieldwork_authorization_gates.get("field_intake_gate_map") != {k: sorted(v) for k, v in sorted(authorization_field_intake_map.items())}:
        fail("generated/FIELDWORK_AUTHORIZATION_GATES.json field_intake_gate_map mismatch metadata/fieldwork_authorization_gates.json")
    if generated_fieldwork_authorization_gates.get("sampling_gate_map") != {k: sorted(v) for k, v in sorted(authorization_sampling_gate_map.items())}:
        fail("generated/FIELDWORK_AUTHORIZATION_GATES.json sampling_gate_map mismatch metadata/fieldwork_authorization_gates.json")
    if generated_fieldwork_authorization_gates.get("outcome_plan_map") != {k: sorted(v) for k, v in sorted(authorization_outcome_plan_map.items())}:
        fail("generated/FIELDWORK_AUTHORIZATION_GATES.json outcome_plan_map mismatch metadata/fieldwork_authorization_gates.json")

    fieldwork_execution_controls = load_json(METADATA_DIR / "fieldwork_execution_controls.json")
    if fieldwork_execution_controls.get("schema") != "radical-governance-fieldwork-execution-controls-v1":
        fail("metadata/fieldwork_execution_controls.json missing expected schema")
    if fieldwork_execution_controls.get("revision") != CURRENT_REV:
        fail(f"metadata/fieldwork_execution_controls.json revision mismatch: expected {CURRENT_REV}")
    execution_control_ids = set(fieldwork_execution_controls.get("controls", {}))
    if len(execution_control_ids) < 2:
        fail("metadata/fieldwork_execution_controls.json must include at least UI and housing execution controls")
    required_execution_receipts = {
        "SCR-OHRP-UP-001",
        "SCR-OHRP-INCIDENT-001",
        "SCR-IRB-CONTINUING-001",
        "SCR-PII-BREACH-001",
        "SCR-80053-AU-001",
        "SCR-NARA-SCHEDULE-001",
    }
    execution_status_counts: dict[str, int] = {}
    execution_gap_map: dict[str, list[str]] = {}
    execution_authorization_gate_map: dict[str, list[str]] = {}
    execution_field_intake_map: dict[str, list[str]] = {}
    execution_sampling_gate_map: dict[str, list[str]] = {}
    execution_outcome_plan_map: dict[str, list[str]] = {}
    execution_source_claim_counts: dict[str, int] = {}
    execution_prohibited_counts: dict[str, int] = {}
    execution_pause_counts: dict[str, int] = {}
    required_execution_prohibited = {
        "contact_roster",
        "linkage_key",
        "raw_transcript",
        "raw_audio",
        "raw_video",
        "private_screenshot",
        "partner_case_record",
        "incident_report_detail",
        "breach_detail",
        "audit_log",
        "secure_environment_raw_output",
    }
    required_execution_terms = {
        "participant_safety_controls": ["withdraw", "adverse action"],
        "incident_response_controls": ["incident", "unanticipated", "corrective"],
        "breach_response_controls": ["breach", "pause", "outside the cube"],
        "audit_controls": ["audit", "failure", "pause"],
        "retention_destruction_controls": ["destruction", "schedule", "hold"],
        "publication_release_controls": ["disclosure", "review"],
    }
    for execution_id, control in fieldwork_execution_controls.get("controls", {}).items():
        if not execution_id.startswith("FEC-"):
            fail(f"fieldwork execution control id should start with FEC-: {execution_id}")
        status = control.get("execution_status", "")
        if "not_executed" not in status or any(token in status.lower() for token in ["complete", "validated", "repaired", "closed"]):
            fail(f"fieldwork execution control {execution_id} must remain not_executed and non-closing: {status}")
        execution_status_counts[status] = execution_status_counts.get(status, 0) + 1
        ids = validate_fieldwork_chain_links(
            surface_kind="fieldwork execution control",
            surface_id=execution_id,
            row=control,
            known_gap_ids=known_gap_ids,
            source_claim_ids=source_claim_ids,
            authorization_gate_ids=authorization_gate_ids,
            field_control_ids=field_control_ids,
            sampling_gate_ids=gate_ids,
            plan_ids=plan_ids,
            authorization_gates=fieldwork_authorization_gates.get("gates", {}),
            field_intake_controls=field_intake_controls.get("controls", {}),
            fail=fail,
        )
        execution_authorization_gate_map.setdefault(ids["authorization_gate"], []).append(execution_id)
        execution_field_intake_map.setdefault(ids["field_intake_control"], []).append(execution_id)
        execution_sampling_gate_map.setdefault(ids["sampling_gate"], []).append(execution_id)
        execution_outcome_plan_map.setdefault(ids["outcome_tail_plan"], []).append(execution_id)
        linked_receipts = set(control.get("linked_source_claim_receipts", []))
        missing_execution_receipts = required_execution_receipts - linked_receipts
        if missing_execution_receipts:
            fail(f"fieldwork execution control {execution_id} missing execution source receipts: {sorted(missing_execution_receipts)}")
        for rid in linked_receipts:
            execution_source_claim_counts[rid] = execution_source_claim_counts.get(rid, 0) + 1
        for gap_id in control.get("linked_gaps", []):
            execution_gap_map.setdefault(gap_id, []).append(execution_id)
        for field in ["execution_artifacts_required", "operating_log_floor", "participant_safety_controls", "incident_response_controls", "breach_response_controls", "audit_controls", "retention_destruction_controls", "publication_release_controls", "prohibited_cube_artifacts", "pause_stop_conditions"]:
            if not isinstance(control.get(field), list) or not control[field]:
                fail(f"fieldwork execution control {execution_id} missing non-empty {field}")
        for field, tokens in required_execution_terms.items():
            require_text_contains(execution_id, field, " ".join(control.get(field, [])), tokens, fail)
        prohibited_lower = {str(item).lower() for item in control.get("prohibited_cube_artifacts", [])}
        if len(required_execution_prohibited - prohibited_lower) > 1:
            fail(f"fieldwork execution control {execution_id} does not prohibit enough private execution artifacts: {sorted(required_execution_prohibited - prohibited_lower)}")
        for item in prohibited_lower:
            execution_prohibited_counts[item] = execution_prohibited_counts.get(item, 0) + 1
        pause_text = " ".join(control.get("pause_stop_conditions", [])).lower()
        for token in ["withdrawal", "breach", "audit", "linkage key", "retention", "disclosure"]:
            if token not in pause_text:
                fail(f"fieldwork execution control {execution_id} pause_stop_conditions lack {token!r}")
        for item in control.get("pause_stop_conditions", []):
            execution_pause_counts[item] = execution_pause_counts.get(item, 0) + 1
        boundary_text = " ".join(
            control.get("operating_log_floor", [])
            + control.get("incident_response_controls", [])
            + control.get("breach_response_controls", [])
            + control.get("audit_controls", [])
            + [control.get("closure_blocker", ""), fieldwork_execution_controls.get("privacy_posture", "")]
        ).lower()
        if "outside the cube" not in boundary_text:
            fail(f"fieldwork execution control {execution_id} must keep private operating evidence outside the cube")
        if any(token in (control.get("closure_blocker", "") + control.get("next_action", "")).lower() for token in ["gap closed", "field validation complete", "outcome proven", "executed fieldwork"]):
            fail(f"fieldwork execution control {execution_id} uses closure/execution language in blocker or next_action")
    for required_gap in REQUIRED_FIELDWORK_GAPS:
        if required_gap not in execution_gap_map:
            fail(f"fieldwork execution controls must include closure blockers for {required_gap}")
    generated_fieldwork_execution_controls = load_json(GENERATED / "FIELDWORK_EXECUTION_CONTROLS.json")
    if generated_fieldwork_execution_controls.get("revision") != CURRENT_REV:
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json revision mismatch")
    if generated_fieldwork_execution_controls.get("control_count") != len(execution_control_ids):
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json control count mismatch metadata/fieldwork_execution_controls.json")
    if {row.get("control_id") for row in generated_fieldwork_execution_controls.get("controls", [])} != execution_control_ids:
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json control ids do not match metadata/fieldwork_execution_controls.json")
    if generated_fieldwork_execution_controls.get("execution_status_counts") != dict(sorted(execution_status_counts.items())):
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json execution_status_counts mismatch metadata/fieldwork_execution_controls.json")
    if generated_fieldwork_execution_controls.get("source_claim_receipt_counts") != dict(sorted(execution_source_claim_counts.items())):
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json source_claim_receipt_counts mismatch metadata/fieldwork_execution_controls.json")
    if generated_fieldwork_execution_controls.get("prohibited_artifact_counts") != dict(sorted(execution_prohibited_counts.items())):
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json prohibited_artifact_counts mismatch metadata/fieldwork_execution_controls.json")
    if generated_fieldwork_execution_controls.get("pause_condition_counts") != dict(sorted(execution_pause_counts.items())):
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json pause_condition_counts mismatch metadata/fieldwork_execution_controls.json")
    if generated_fieldwork_execution_controls.get("gap_control_map") != {k: sorted(v) for k, v in sorted(execution_gap_map.items())}:
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json gap_control_map mismatch metadata/fieldwork_execution_controls.json")
    if generated_fieldwork_execution_controls.get("authorization_gate_control_map") != {k: sorted(v) for k, v in sorted(execution_authorization_gate_map.items())}:
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json authorization_gate_control_map mismatch metadata/fieldwork_execution_controls.json")
    if generated_fieldwork_execution_controls.get("field_intake_control_map") != {k: sorted(v) for k, v in sorted(execution_field_intake_map.items())}:
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json field_intake_control_map mismatch metadata/fieldwork_execution_controls.json")
    if generated_fieldwork_execution_controls.get("sampling_gate_control_map") != {k: sorted(v) for k, v in sorted(execution_sampling_gate_map.items())}:
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json sampling_gate_control_map mismatch metadata/fieldwork_execution_controls.json")
    if generated_fieldwork_execution_controls.get("outcome_plan_control_map") != {k: sorted(v) for k, v in sorted(execution_outcome_plan_map.items())}:
        fail("generated/FIELDWORK_EXECUTION_CONTROLS.json outcome_plan_control_map mismatch metadata/fieldwork_execution_controls.json")


    fieldwork_release_controls = load_json(METADATA_DIR / "fieldwork_release_controls.json")
    if fieldwork_release_controls.get("schema") != "radical-governance-fieldwork-release-controls-v1":
        fail("metadata/fieldwork_release_controls.json missing expected schema")
    if fieldwork_release_controls.get("revision") != CURRENT_REV:
        fail(f"metadata/fieldwork_release_controls.json revision mismatch: expected {CURRENT_REV}")
    release_control_ids = set(fieldwork_release_controls.get("controls", {}))
    if len(release_control_ids) < 2:
        fail("metadata/fieldwork_release_controls.json must include at least UI and housing release controls")
    required_release_receipts = {
        "SCR-SPD4-001",
        "SCR-NIST800188-001",
        "SCR-NIST8053-001",
        "SCR-STRUDL-SDC-001",
        "SCR-FCSM-SDL-001",
        "SCR-CENSUS-DA-001",
    }
    release_status_counts: dict[str, int] = {}
    release_gap_map: dict[str, list[str]] = {}
    release_execution_map: dict[str, list[str]] = {}
    release_authorization_map: dict[str, list[str]] = {}
    release_field_intake_map: dict[str, list[str]] = {}
    release_sampling_map: dict[str, list[str]] = {}
    release_outcome_plan_map: dict[str, list[str]] = {}
    release_source_claim_counts: dict[str, int] = {}
    release_prohibited_counts: dict[str, int] = {}
    release_pause_counts: dict[str, int] = {}
    required_release_prohibited = {
        "name", "address", "contact_roster", "linkage_key", "raw_transcript", "raw_audio", "raw_video",
        "private_screenshot", "incident_report_detail", "breach_detail", "audit_log", "secure_environment_raw_output",
        "reviewer_workpaper", "small_cell", "rare_cohort_narrative",
    }
    required_release_terms = {
        "disclosure_limitation_controls": ["disclosure", "suppression", "small-cell"],
        "deidentification_controls": ["de-identification", "re-identification"],
        "public_narrative_controls": ["quote", "rare"],
        "quality_integrity_controls": ["nonresponse", "denominator", "uncertainty"],
        "participant_community_review_controls": ["harm", "review"],
        "errata_retraction_controls": ["errata", "withdraw"],
    }
    for release_id, control in fieldwork_release_controls.get("controls", {}).items():
        if not release_id.startswith("FRC-"):
            fail(f"fieldwork release control id should start with FRC-: {release_id}")
        status = control.get("release_status", "")
        if "not_released" not in status or any(token in status.lower() for token in ["complete", "validated", "repaired", "closed"]):
            fail(f"fieldwork release control {release_id} must remain not_released and non-closing: {status}")
        if status.startswith("released"):
            fail(f"fieldwork release control {release_id} claims release: {status}")
        release_status_counts[status] = release_status_counts.get(status, 0) + 1
        ids = validate_fieldwork_follow_on_links(
            surface_kind="fieldwork release control",
            surface_id=release_id,
            row=control,
            execution_control_ids=execution_control_ids,
            execution_controls=fieldwork_execution_controls.get("controls", {}),
            known_gap_ids=known_gap_ids,
            source_claim_ids=source_claim_ids,
            authorization_gate_ids=authorization_gate_ids,
            field_control_ids=field_control_ids,
            sampling_gate_ids=gate_ids,
            plan_ids=plan_ids,
            authorization_gates=fieldwork_authorization_gates.get("gates", {}),
            field_intake_controls=field_intake_controls.get("controls", {}),
            fail=fail,
        )
        release_execution_map.setdefault(ids["fieldwork_execution_control"], []).append(release_id)
        release_authorization_map.setdefault(ids["authorization_gate"], []).append(release_id)
        release_field_intake_map.setdefault(ids["field_intake_control"], []).append(release_id)
        release_sampling_map.setdefault(ids["sampling_gate"], []).append(release_id)
        release_outcome_plan_map.setdefault(ids["outcome_tail_plan"], []).append(release_id)
        linked_receipts = set(control.get("linked_source_claim_receipts", []))
        missing_release_receipts = required_release_receipts - linked_receipts
        if missing_release_receipts:
            fail(f"fieldwork release control {release_id} missing release source receipts: {sorted(missing_release_receipts)}")
        for rid in linked_receipts:
            if rid not in source_claim_ids:
                fail(f"fieldwork release control {release_id} links unknown source-claim receipt {rid}")
            release_source_claim_counts[rid] = release_source_claim_counts.get(rid, 0) + 1
        for gap_id in control.get("linked_gaps", []):
            release_gap_map.setdefault(gap_id, []).append(release_id)
        for field in ["release_artifacts_required", "disclosure_limitation_controls", "deidentification_controls", "public_narrative_controls", "quality_integrity_controls", "participant_community_review_controls", "errata_retraction_controls", "allowed_cube_artifacts", "prohibited_public_outputs", "pause_stop_conditions"]:
            if not isinstance(control.get(field), list) or not control[field]:
                fail(f"fieldwork release control {release_id} missing non-empty {field}")
        for field, tokens in required_release_terms.items():
            require_text_contains(release_id, field, " ".join(control.get(field, [])), tokens, fail)
        prohibited_lower = {str(item).lower() for item in control.get("prohibited_public_outputs", [])}
        if len(required_release_prohibited - prohibited_lower) > 2:
            fail(f"fieldwork release control {release_id} does not prohibit enough public/private artifacts: {sorted(required_release_prohibited - prohibited_lower)}")
        for item in prohibited_lower:
            release_prohibited_counts[item] = release_prohibited_counts.get(item, 0) + 1
        allowed_text = " ".join(control.get("allowed_cube_artifacts", [])).lower()
        if any(token in allowed_text for token in ["name", "address", "claim_number", "docket_number", "linkage_key", "raw", "audit_log", "reviewer_workpaper"]):
            fail(f"fieldwork release control {release_id} allowed artifacts appear to allow private or raw release material")
        pause_text = " ".join(control.get("pause_stop_conditions", [])).lower()
        for token in ["disclosure", "suppression", "small-cell", "re-identification", "withdrawal", "errata"]:
            if token not in pause_text:
                fail(f"fieldwork release control {release_id} pause_stop_conditions lack {token!r}")
        for item in control.get("pause_stop_conditions", []):
            release_pause_counts[item] = release_pause_counts.get(item, 0) + 1
        boundary_text = " ".join(
            control.get("release_artifacts_required", [])
            + control.get("disclosure_limitation_controls", [])
            + control.get("deidentification_controls", [])
            + control.get("public_narrative_controls", [])
            + [control.get("closure_blocker", ""), fieldwork_release_controls.get("privacy_posture", "")]
        ).lower()
        if "outside the cube" not in boundary_text:
            fail(f"fieldwork release control {release_id} must keep private release evidence outside the cube")
        if any(token in (control.get("closure_blocker", "") + control.get("next_action", "")).lower() for token in ["gap closed", "field validation complete", "outcome proven", "released output proves"]):
            fail(f"fieldwork release control {release_id} uses closure/release-as-proof language in blocker or next_action")
    for required_gap in REQUIRED_FIELDWORK_GAPS:
        if required_gap not in release_gap_map:
            fail(f"fieldwork release controls must include closure blockers for {required_gap}")
    generated_fieldwork_release_controls = load_json(GENERATED / "FIELDWORK_RELEASE_CONTROLS.json")
    if generated_fieldwork_release_controls.get("revision") != CURRENT_REV:
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json revision mismatch")
    if generated_fieldwork_release_controls.get("control_count") != len(release_control_ids):
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json control count mismatch metadata/fieldwork_release_controls.json")
    if {row.get("control_id") for row in generated_fieldwork_release_controls.get("controls", [])} != release_control_ids:
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json control ids do not match metadata/fieldwork_release_controls.json")
    if generated_fieldwork_release_controls.get("release_status_counts") != dict(sorted(release_status_counts.items())):
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json release_status_counts mismatch metadata/fieldwork_release_controls.json")
    if generated_fieldwork_release_controls.get("source_claim_receipt_counts") != dict(sorted(release_source_claim_counts.items())):
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json source_claim_receipt_counts mismatch metadata/fieldwork_release_controls.json")
    if generated_fieldwork_release_controls.get("prohibited_public_output_counts") != dict(sorted(release_prohibited_counts.items())):
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json prohibited_public_output_counts mismatch metadata/fieldwork_release_controls.json")
    if generated_fieldwork_release_controls.get("pause_condition_counts") != dict(sorted(release_pause_counts.items())):
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json pause_condition_counts mismatch metadata/fieldwork_release_controls.json")
    if generated_fieldwork_release_controls.get("gap_control_map") != {k: sorted(v) for k, v in sorted(release_gap_map.items())}:
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json gap_control_map mismatch metadata/fieldwork_release_controls.json")
    if generated_fieldwork_release_controls.get("execution_control_map") != {k: sorted(v) for k, v in sorted(release_execution_map.items())}:
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json execution_control_map mismatch metadata/fieldwork_release_controls.json")
    if generated_fieldwork_release_controls.get("authorization_gate_control_map") != {k: sorted(v) for k, v in sorted(release_authorization_map.items())}:
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json authorization_gate_control_map mismatch metadata/fieldwork_release_controls.json")
    if generated_fieldwork_release_controls.get("field_intake_control_map") != {k: sorted(v) for k, v in sorted(release_field_intake_map.items())}:
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json field_intake_control_map mismatch metadata/fieldwork_release_controls.json")
    if generated_fieldwork_release_controls.get("sampling_gate_control_map") != {k: sorted(v) for k, v in sorted(release_sampling_map.items())}:
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json sampling_gate_control_map mismatch metadata/fieldwork_release_controls.json")
    if generated_fieldwork_release_controls.get("outcome_plan_control_map") != {k: sorted(v) for k, v in sorted(release_outcome_plan_map.items())}:
        fail("generated/FIELDWORK_RELEASE_CONTROLS.json outcome_plan_control_map mismatch metadata/fieldwork_release_controls.json")

    fieldwork_correction_controls = load_json(METADATA_DIR / "fieldwork_correction_controls.json")
    if fieldwork_correction_controls.get("schema") != "radical-governance-fieldwork-correction-controls-v1":
        fail("metadata/fieldwork_correction_controls.json missing expected schema")
    if fieldwork_correction_controls.get("revision") != CURRENT_REV:
        fail(f"metadata/fieldwork_correction_controls.json revision mismatch: expected {CURRENT_REV}")
    correction_control_ids = set(fieldwork_correction_controls.get("controls", {}))
    if len(correction_control_ids) < 2:
        fail("metadata/fieldwork_correction_controls.json must include at least UI and housing correction controls")
    required_correction_receipts = {
        "SCR-IQA-2002-001",
        "SCR-IQA-M1915-001",
        "SCR-IQA-FAQ-001",
        "SCR-DOL-IQ-001",
        "SCR-SPD4-SELFREVIEW-001",
    }
    correction_status_counts: dict[str, int] = {}
    correction_gap_map: dict[str, list[str]] = {}
    correction_release_map: dict[str, list[str]] = {}
    correction_execution_map: dict[str, list[str]] = {}
    correction_authorization_map: dict[str, list[str]] = {}
    correction_field_intake_map: dict[str, list[str]] = {}
    correction_sampling_map: dict[str, list[str]] = {}
    correction_outcome_plan_map: dict[str, list[str]] = {}
    correction_source_claim_counts: dict[str, int] = {}
    correction_prohibited_counts: dict[str, int] = {}
    correction_pause_counts: dict[str, int] = {}
    required_correction_prohibited = {
        "name", "address", "claim_number", "docket_number", "contact_roster", "linkage_key",
        "raw_transcript", "raw_audio", "raw_video", "private_screenshot", "partner_case_record",
        "incident_report_detail", "breach_detail", "audit_log", "reviewer_workpaper",
        "secure_environment_raw_output", "private_correction_request", "redress_case_file",
    }
    required_correction_terms = {
        "defect_detection_controls": ["error", "denominator", "disclosure"],
        "correction_request_controls": ["affected", "correction", "request"],
        "withdrawal_retraction_controls": ["withdraw", "retract"],
        "notification_redress_controls": ["notify", "redress"],
        "versioning_citation_controls": ["version", "citation", "superseded"],
        "harm_review_controls": ["harm", "review"],
    }
    for correction_id, control in fieldwork_correction_controls.get("controls", {}).items():
        if not correction_id.startswith("FCC-"):
            fail(f"fieldwork correction control id should start with FCC-: {correction_id}")
        status = control.get("correction_status", "")
        if "not_activated" not in status or any(token in status.lower() for token in ["complete", "validated", "repaired", "closed"]):
            fail(f"fieldwork correction control {correction_id} must remain not_activated and non-closing: {status}")
        if status.startswith("corrected") or status.startswith("withdrawn") or status.startswith("retracted"):
            fail(f"fieldwork correction control {correction_id} claims correction/retraction status: {status}")
        correction_status_counts[status] = correction_status_counts.get(status, 0) + 1
        ids = validate_fieldwork_post_release_links(
            surface_kind="fieldwork correction control",
            surface_id=correction_id,
            row=control,
            release_control_ids=release_control_ids,
            release_controls=fieldwork_release_controls.get("controls", {}),
            execution_control_ids=execution_control_ids,
            execution_controls=fieldwork_execution_controls.get("controls", {}),
            known_gap_ids=known_gap_ids,
            source_claim_ids=source_claim_ids,
            authorization_gate_ids=authorization_gate_ids,
            field_control_ids=field_control_ids,
            sampling_gate_ids=gate_ids,
            plan_ids=plan_ids,
            authorization_gates=fieldwork_authorization_gates.get("gates", {}),
            field_intake_controls=field_intake_controls.get("controls", {}),
            fail=fail,
        )
        correction_release_map.setdefault(ids["fieldwork_release_control"], []).append(correction_id)
        correction_execution_map.setdefault(ids["fieldwork_execution_control"], []).append(correction_id)
        correction_authorization_map.setdefault(ids["authorization_gate"], []).append(correction_id)
        correction_field_intake_map.setdefault(ids["field_intake_control"], []).append(correction_id)
        correction_sampling_map.setdefault(ids["sampling_gate"], []).append(correction_id)
        correction_outcome_plan_map.setdefault(ids["outcome_tail_plan"], []).append(correction_id)
        linked_receipts = set(control.get("linked_source_claim_receipts", []))
        missing_correction_receipts = required_correction_receipts - linked_receipts
        if missing_correction_receipts:
            fail(f"fieldwork correction control {correction_id} missing correction source receipts: {sorted(missing_correction_receipts)}")
        for rid in linked_receipts:
            if rid not in source_claim_ids:
                fail(f"fieldwork correction control {correction_id} links unknown source-claim receipt {rid}")
            correction_source_claim_counts[rid] = correction_source_claim_counts.get(rid, 0) + 1
        for gap_id in control.get("linked_gaps", []):
            correction_gap_map.setdefault(gap_id, []).append(correction_id)
        for field in ["correction_artifacts_required", "defect_detection_controls", "correction_request_controls", "withdrawal_retraction_controls", "notification_redress_controls", "versioning_citation_controls", "harm_review_controls", "allowed_cube_artifacts", "prohibited_cube_artifacts", "pause_stop_conditions"]:
            if not isinstance(control.get(field), list) or not control[field]:
                fail(f"fieldwork correction control {correction_id} missing non-empty {field}")
        for field, tokens in required_correction_terms.items():
            require_text_contains(correction_id, field, " ".join(control.get(field, [])), tokens, fail)
        prohibited_lower = {str(item).lower() for item in control.get("prohibited_cube_artifacts", [])}
        if len(required_correction_prohibited - prohibited_lower) > 2:
            fail(f"fieldwork correction control {correction_id} does not prohibit enough private correction artifacts: {sorted(required_correction_prohibited - prohibited_lower)}")
        for item in prohibited_lower:
            correction_prohibited_counts[item] = correction_prohibited_counts.get(item, 0) + 1
        allowed_text = " ".join(control.get("allowed_cube_artifacts", [])).lower()
        if any(token in allowed_text for token in ["name", "address", "claim_number", "docket_number", "linkage_key", "raw", "audit_log", "redress_case_file", "private"]):
            fail(f"fieldwork correction control {correction_id} allowed artifacts appear to allow private correction material")
        pause_text = " ".join(control.get("pause_stop_conditions", [])).lower()
        for token in ["information-quality", "disclosure", "withdrawal", "retraction", "redress", "citation"]:
            if token not in pause_text:
                fail(f"fieldwork correction control {correction_id} pause_stop_conditions lack {token!r}")
        for item in control.get("pause_stop_conditions", []):
            correction_pause_counts[item] = correction_pause_counts.get(item, 0) + 1
        boundary_text = " ".join(
            control.get("correction_artifacts_required", [])
            + control.get("correction_request_controls", [])
            + control.get("notification_redress_controls", [])
            + control.get("allowed_cube_artifacts", [])
            + [control.get("closure_blocker", ""), fieldwork_correction_controls.get("privacy_posture", "")]
        ).lower()
        if "outside the cube" not in boundary_text:
            fail(f"fieldwork correction control {correction_id} must keep private correction evidence outside the cube")
        if any(token in (control.get("closure_blocker", "") + control.get("next_action", "")).lower() for token in ["gap closed", "field validation complete", "outcome proven", "corrected output proves", "correction proves"]):
            fail(f"fieldwork correction control {correction_id} uses closure/correction-as-proof language in blocker or next_action")
    for required_gap in REQUIRED_FIELDWORK_GAPS:
        if required_gap not in correction_gap_map:
            fail(f"fieldwork correction controls must include closure blockers for {required_gap}")
    generated_fieldwork_correction_controls = load_json(GENERATED / "FIELDWORK_CORRECTION_CONTROLS.json")
    if generated_fieldwork_correction_controls.get("revision") != CURRENT_REV:
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json revision mismatch")
    if generated_fieldwork_correction_controls.get("control_count") != len(correction_control_ids):
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json control count mismatch metadata/fieldwork_correction_controls.json")
    if {row.get("control_id") for row in generated_fieldwork_correction_controls.get("controls", [])} != correction_control_ids:
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json control ids do not match metadata/fieldwork_correction_controls.json")
    if generated_fieldwork_correction_controls.get("correction_status_counts") != dict(sorted(correction_status_counts.items())):
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json correction_status_counts mismatch metadata/fieldwork_correction_controls.json")
    if generated_fieldwork_correction_controls.get("source_claim_receipt_counts") != dict(sorted(correction_source_claim_counts.items())):
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json source_claim_receipt_counts mismatch metadata/fieldwork_correction_controls.json")
    if generated_fieldwork_correction_controls.get("prohibited_artifact_counts") != dict(sorted(correction_prohibited_counts.items())):
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json prohibited_artifact_counts mismatch metadata/fieldwork_correction_controls.json")
    if generated_fieldwork_correction_controls.get("pause_condition_counts") != dict(sorted(correction_pause_counts.items())):
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json pause_condition_counts mismatch metadata/fieldwork_correction_controls.json")
    if generated_fieldwork_correction_controls.get("gap_control_map") != {k: sorted(v) for k, v in sorted(correction_gap_map.items())}:
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json gap_control_map mismatch metadata/fieldwork_correction_controls.json")
    if generated_fieldwork_correction_controls.get("release_control_map") != {k: sorted(v) for k, v in sorted(correction_release_map.items())}:
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json release_control_map mismatch metadata/fieldwork_correction_controls.json")
    if generated_fieldwork_correction_controls.get("execution_control_map") != {k: sorted(v) for k, v in sorted(correction_execution_map.items())}:
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json execution_control_map mismatch metadata/fieldwork_correction_controls.json")
    if generated_fieldwork_correction_controls.get("authorization_gate_control_map") != {k: sorted(v) for k, v in sorted(correction_authorization_map.items())}:
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json authorization_gate_control_map mismatch metadata/fieldwork_correction_controls.json")
    if generated_fieldwork_correction_controls.get("field_intake_control_map") != {k: sorted(v) for k, v in sorted(correction_field_intake_map.items())}:
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json field_intake_control_map mismatch metadata/fieldwork_correction_controls.json")
    if generated_fieldwork_correction_controls.get("sampling_gate_control_map") != {k: sorted(v) for k, v in sorted(correction_sampling_map.items())}:
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json sampling_gate_control_map mismatch metadata/fieldwork_correction_controls.json")
    if generated_fieldwork_correction_controls.get("outcome_plan_control_map") != {k: sorted(v) for k, v in sorted(correction_outcome_plan_map.items())}:
        fail("generated/FIELDWORK_CORRECTION_CONTROLS.json outcome_plan_control_map mismatch metadata/fieldwork_correction_controls.json")


    fieldwork_redress_verification_controls = load_json(METADATA_DIR / "fieldwork_redress_verification_controls.json")
    if fieldwork_redress_verification_controls.get("schema") != "radical-governance-fieldwork-redress-verification-controls-v1":
        fail("metadata/fieldwork_redress_verification_controls.json missing expected schema")
    if fieldwork_redress_verification_controls.get("revision") != CURRENT_REV:
        fail(f"metadata/fieldwork_redress_verification_controls.json revision mismatch: expected {CURRENT_REV}")
    redress_control_ids = set(fieldwork_redress_verification_controls.get("controls", {}))
    if len(redress_control_ids) < 2:
        fail("metadata/fieldwork_redress_verification_controls.json must include at least UI and housing redress verification controls")
    required_redress_receipts = {
        "SCR-A123-2026-001",
        "SCR-GAO-GREENBOOK-2025-001",
    }
    redress_status_counts: dict[str, int] = {}
    redress_gap_map: dict[str, list[str]] = {}
    redress_correction_map: dict[str, list[str]] = {}
    redress_release_map: dict[str, list[str]] = {}
    redress_execution_map: dict[str, list[str]] = {}
    redress_authorization_map: dict[str, list[str]] = {}
    redress_field_intake_map: dict[str, list[str]] = {}
    redress_sampling_map: dict[str, list[str]] = {}
    redress_outcome_plan_map: dict[str, list[str]] = {}
    redress_source_claim_counts: dict[str, int] = {}
    redress_prohibited_counts: dict[str, int] = {}
    redress_pause_counts: dict[str, int] = {}
    redress_material_counts: dict[str, int] = {}
    required_redress_prohibited = {
        "name", "address", "claim_number", "docket_number", "contact_roster", "linkage_key",
        "administrative_extract", "payment_record", "court_file", "appeal_record", "redress_case_file",
        "raw_transcript", "raw_audio", "private_screenshot", "partner_case_record", "audit_log",
        "household_composition",
    }
    required_redress_terms = {
        "verification_artifacts_required": ["outside-cube", "verification", "exception"],
        "remedy_verification_controls": ["verify", "actual"],
        "exception_followup_controls": ["unresolved", "nonresponse"],
        "escalation_controls": ["corrective-action", "validation"],
    }
    for redress_id, control in fieldwork_redress_verification_controls.get("controls", {}).items():
        if not redress_id.startswith("FRV-"):
            fail(f"fieldwork redress verification control id should start with FRV-: {redress_id}")
        status = control.get("verification_status", "")
        if "not_verified" not in status or any(token in status.lower() for token in ["complete", "validated", "repaired", "closed"]):
            fail(f"fieldwork redress verification control {redress_id} must remain not_verified and non-closing: {status}")
        if status.startswith("verified") or status.startswith("remedied") or status.startswith("paid") or status.startswith("housed"):
            fail(f"fieldwork redress verification control {redress_id} claims verification/remedy status: {status}")
        redress_status_counts[status] = redress_status_counts.get(status, 0) + 1
        ids = validate_fieldwork_post_correction_links(
            surface_kind="fieldwork redress verification control",
            surface_id=redress_id,
            row=control,
            correction_control_ids=correction_control_ids,
            correction_controls=fieldwork_correction_controls.get("controls", {}),
            release_control_ids=release_control_ids,
            release_controls=fieldwork_release_controls.get("controls", {}),
            execution_control_ids=execution_control_ids,
            execution_controls=fieldwork_execution_controls.get("controls", {}),
            known_gap_ids=known_gap_ids,
            source_claim_ids=source_claim_ids,
            authorization_gate_ids=authorization_gate_ids,
            field_control_ids=field_control_ids,
            sampling_gate_ids=gate_ids,
            plan_ids=plan_ids,
            authorization_gates=fieldwork_authorization_gates.get("gates", {}),
            field_intake_controls=field_intake_controls.get("controls", {}),
            fail=fail,
        )
        redress_correction_map.setdefault(ids["fieldwork_correction_control"], []).append(redress_id)
        redress_release_map.setdefault(ids["fieldwork_release_control"], []).append(redress_id)
        redress_execution_map.setdefault(ids["fieldwork_execution_control"], []).append(redress_id)
        redress_authorization_map.setdefault(ids["authorization_gate"], []).append(redress_id)
        redress_field_intake_map.setdefault(ids["field_intake_control"], []).append(redress_id)
        redress_sampling_map.setdefault(ids["sampling_gate"], []).append(redress_id)
        redress_outcome_plan_map.setdefault(ids["outcome_tail_plan"], []).append(redress_id)
        linked_receipts = set(control.get("linked_source_claim_receipts", []))
        missing_redress_receipts = required_redress_receipts - linked_receipts
        if missing_redress_receipts:
            fail(f"fieldwork redress verification control {redress_id} missing redress source receipts: {sorted(missing_redress_receipts)}")
        for rid in linked_receipts:
            if rid not in source_claim_ids:
                fail(f"fieldwork redress verification control {redress_id} links unknown source-claim receipt {rid}")
            redress_source_claim_counts[rid] = redress_source_claim_counts.get(rid, 0) + 1
        for gap_id in control.get("linked_gaps", []):
            redress_gap_map.setdefault(gap_id, []).append(redress_id)
        for field in ["verification_artifacts_required", "remedy_verification_controls", "exception_followup_controls", "material_outcome_verification_fields", "escalation_controls", "allowed_cube_artifacts", "prohibited_cube_artifacts", "pause_stop_conditions"]:
            if not isinstance(control.get(field), list) or not control[field]:
                fail(f"fieldwork redress verification control {redress_id} missing non-empty {field}")
        for field, tokens in required_redress_terms.items():
            require_text_contains(redress_id, field, " ".join(control.get(field, [])), tokens, fail)
        material_fields = control.get("material_outcome_verification_fields", [])
        if len(material_fields) < 5:
            fail(f"fieldwork redress verification control {redress_id} needs at least five material outcome fields")
        for item in material_fields:
            redress_material_counts[item] = redress_material_counts.get(item, 0) + 1
        remedy_text = " ".join(control.get("remedy_verification_controls", []) + material_fields).lower()
        if redress_id.startswith("FRV-UI"):
            for token in ["payment", "hold", "overpayment", "appeal", "burden"]:
                if token not in remedy_text:
                    fail(f"fieldwork redress verification control {redress_id} lacks UI remedy token {token!r}")
        if redress_id.startswith("FRV-HC"):
            for token in ["possession", "lockout", "rehousing", "screening", "stability"]:
                if token not in remedy_text:
                    fail(f"fieldwork redress verification control {redress_id} lacks housing remedy token {token!r}")
        prohibited_lower = {str(item).lower() for item in control.get("prohibited_cube_artifacts", [])}
        if len(required_redress_prohibited - prohibited_lower) > 3:
            fail(f"fieldwork redress verification control {redress_id} does not prohibit enough private redress artifacts: {sorted(required_redress_prohibited - prohibited_lower)}")
        for item in prohibited_lower:
            redress_prohibited_counts[item] = redress_prohibited_counts.get(item, 0) + 1
        allowed_text = " ".join(control.get("allowed_cube_artifacts", [])).lower()
        if any(token in allowed_text for token in ["name", "address", "claim_number", "docket_number", "linkage_key", "raw", "audit_log", "redress_case_file", "payment_record", "private"]):
            fail(f"fieldwork redress verification control {redress_id} allowed artifacts appear to allow private remedy material")
        pause_text = " ".join(control.get("pause_stop_conditions", [])).lower()
        for token in ["pause", "verification", "unresolved", "nonresponse", "corrected output"]:
            if token not in pause_text:
                fail(f"fieldwork redress verification control {redress_id} pause_stop_conditions lack {token!r}")
        for item in control.get("pause_stop_conditions", []):
            redress_pause_counts[item] = redress_pause_counts.get(item, 0) + 1
        boundary_text = " ".join(
            control.get("verification_artifacts_required", [])
            + control.get("exception_followup_controls", [])
            + control.get("allowed_cube_artifacts", [])
            + [control.get("closure_blocker", ""), fieldwork_redress_verification_controls.get("privacy_posture", "")]
        ).lower()
        if "outside the cube" not in boundary_text:
            fail(f"fieldwork redress verification control {redress_id} must keep private redress evidence outside the cube")
        if any(token in (control.get("closure_blocker", "") + control.get("next_action", "")).lower() for token in ["gap closed", "field validation complete", "outcome proven", "redress route proves", "ledger proves"]):
            fail(f"fieldwork redress verification control {redress_id} uses closure/redress-as-proof language in blocker or next_action")
    for required_gap in REQUIRED_FIELDWORK_GAPS:
        if required_gap not in redress_gap_map:
            fail(f"fieldwork redress verification controls must include closure blockers for {required_gap}")
    generated_fieldwork_redress_verification_controls = load_json(GENERATED / "FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json")
    if generated_fieldwork_redress_verification_controls.get("revision") != CURRENT_REV:
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json revision mismatch")
    if generated_fieldwork_redress_verification_controls.get("control_count") != len(redress_control_ids):
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json control count mismatch metadata/fieldwork_redress_verification_controls.json")
    if {row.get("control_id") for row in generated_fieldwork_redress_verification_controls.get("controls", [])} != redress_control_ids:
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json control ids do not match metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("verification_status_counts") != dict(sorted(redress_status_counts.items())):
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json verification_status_counts mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("source_claim_receipt_counts") != dict(sorted(redress_source_claim_counts.items())):
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json source_claim_receipt_counts mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("prohibited_artifact_counts") != dict(sorted(redress_prohibited_counts.items())):
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json prohibited_artifact_counts mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("pause_condition_counts") != dict(sorted(redress_pause_counts.items())):
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json pause_condition_counts mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("material_field_counts") != dict(sorted(redress_material_counts.items())):
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json material_field_counts mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("gap_control_map") != {k: sorted(v) for k, v in sorted(redress_gap_map.items())}:
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json gap_control_map mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("correction_control_map") != {k: sorted(v) for k, v in sorted(redress_correction_map.items())}:
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json correction_control_map mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("release_control_map") != {k: sorted(v) for k, v in sorted(redress_release_map.items())}:
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json release_control_map mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("execution_control_map") != {k: sorted(v) for k, v in sorted(redress_execution_map.items())}:
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json execution_control_map mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("authorization_gate_control_map") != {k: sorted(v) for k, v in sorted(redress_authorization_map.items())}:
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json authorization_gate_control_map mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("field_intake_control_map") != {k: sorted(v) for k, v in sorted(redress_field_intake_map.items())}:
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json field_intake_control_map mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("sampling_gate_control_map") != {k: sorted(v) for k, v in sorted(redress_sampling_map.items())}:
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json sampling_gate_control_map mismatch metadata/fieldwork_redress_verification_controls.json")
    if generated_fieldwork_redress_verification_controls.get("outcome_plan_control_map") != {k: sorted(v) for k, v in sorted(redress_outcome_plan_map.items())}:
        fail("generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.json outcome_plan_control_map mismatch metadata/fieldwork_redress_verification_controls.json")


    fieldwork_closure_dossiers = load_json(METADATA_DIR / "fieldwork_closure_dossiers.json")
    if fieldwork_closure_dossiers.get("schema") != "radical-governance-fieldwork-closure-dossiers-v1":
        fail("metadata/fieldwork_closure_dossiers.json missing expected schema")
    if fieldwork_closure_dossiers.get("revision") != CURRENT_REV:
        fail(f"metadata/fieldwork_closure_dossiers.json revision mismatch: expected {CURRENT_REV}")
    closure_dossier_ids = set(fieldwork_closure_dossiers.get("controls", {}))
    if len(closure_dossier_ids) < 2:
        fail("metadata/fieldwork_closure_dossiers.json must include at least UI and housing closure dossiers")
    required_closure_receipts = {
        "SCR-A11-S290-001",
        "SCR-M20-12-EVAL-001",
        "SCR-M21-27-EVIDENCE-001",
        "SCR-GAO-EVIDENCE-001",
    }
    closure_status_counts: dict[str, int] = {}
    closure_gap_map: dict[str, list[str]] = {}
    closure_redress_map: dict[str, list[str]] = {}
    closure_correction_map: dict[str, list[str]] = {}
    closure_release_map: dict[str, list[str]] = {}
    closure_execution_map: dict[str, list[str]] = {}
    closure_authorization_map: dict[str, list[str]] = {}
    closure_field_intake_map: dict[str, list[str]] = {}
    closure_sampling_map: dict[str, list[str]] = {}
    closure_outcome_plan_map: dict[str, list[str]] = {}
    closure_source_claim_counts: dict[str, int] = {}
    closure_prohibited_counts: dict[str, int] = {}
    closure_unresolved_counts: dict[str, int] = {}
    closure_reopen_counts: dict[str, int] = {}
    closure_material_counts: dict[str, int] = {}
    required_closure_prohibited = {
        "contact_roster", "linkage_key", "raw_transcript", "raw_audio",
        "private_screenshot", "partner_case_record", "redress_case_file",
    }
    required_closure_terms = {
        "closure_evidence_required": ["outside-cube", "verification"],
        "attestation_requirements": ["attest", "review"],
        "reopen_triggers": ["later", "source"],
        "closure_blocker": ["outside-cube", "attestation", "not the outcome"],
    }
    for dossier_id, control in fieldwork_closure_dossiers.get("controls", {}).items():
        if not dossier_id.startswith("FCD-"):
            fail(f"fieldwork closure dossier id should start with FCD-: {dossier_id}")
        status = control.get("closure_readiness_status", "")
        if "not_ready" not in status or any(token in status.lower() for token in ["closed", "approved", "complete", "validated", "repaired"]):
            fail(f"fieldwork closure dossier {dossier_id} must remain not_ready and non-closing: {status}")
        closure_status_counts[status] = closure_status_counts.get(status, 0) + 1
        ids = validate_fieldwork_post_redress_links(
            surface_kind="fieldwork closure dossier",
            surface_id=dossier_id,
            row=control,
            redress_control_ids=redress_control_ids,
            redress_controls=fieldwork_redress_verification_controls.get("controls", {}),
            correction_control_ids=correction_control_ids,
            correction_controls=fieldwork_correction_controls.get("controls", {}),
            release_control_ids=release_control_ids,
            release_controls=fieldwork_release_controls.get("controls", {}),
            execution_control_ids=execution_control_ids,
            execution_controls=fieldwork_execution_controls.get("controls", {}),
            known_gap_ids=known_gap_ids,
            source_claim_ids=source_claim_ids,
            authorization_gate_ids=authorization_gate_ids,
            field_control_ids=field_control_ids,
            sampling_gate_ids=gate_ids,
            plan_ids=plan_ids,
            authorization_gates=fieldwork_authorization_gates.get("gates", {}),
            field_intake_controls=field_intake_controls.get("controls", {}),
            fail=fail,
        )
        closure_redress_map.setdefault(ids["fieldwork_redress_verification_control"], []).append(dossier_id)
        closure_correction_map.setdefault(ids["fieldwork_correction_control"], []).append(dossier_id)
        closure_release_map.setdefault(ids["fieldwork_release_control"], []).append(dossier_id)
        closure_execution_map.setdefault(ids["fieldwork_execution_control"], []).append(dossier_id)
        closure_authorization_map.setdefault(ids["authorization_gate"], []).append(dossier_id)
        closure_field_intake_map.setdefault(ids["field_intake_control"], []).append(dossier_id)
        closure_sampling_map.setdefault(ids["sampling_gate"], []).append(dossier_id)
        closure_outcome_plan_map.setdefault(ids["outcome_tail_plan"], []).append(dossier_id)
        for gap_id in control.get("linked_gaps", []):
            if gap_id not in known_gap_ids:
                fail(f"fieldwork closure dossier {dossier_id} links unknown gap {gap_id}")
            closure_gap_map.setdefault(gap_id, []).append(dossier_id)
        for required_gap in REQUIRED_FIELDWORK_GAPS:
            if required_gap not in control.get("linked_gaps", []):
                fail(f"fieldwork closure dossier {dossier_id} must block {required_gap}")
        missing_receipts = required_closure_receipts - set(control.get("linked_source_claim_receipts", []))
        if missing_receipts:
            fail(f"fieldwork closure dossier {dossier_id} missing closure source receipts: {sorted(missing_receipts)}")
        for rid in control.get("linked_source_claim_receipts", []):
            if rid not in source_claim_ids:
                fail(f"fieldwork closure dossier {dossier_id} links unknown source-claim receipt {rid}")
            closure_source_claim_counts[rid] = closure_source_claim_counts.get(rid, 0) + 1
        for field in ["closure_evidence_required", "material_outcome_fields", "attestation_requirements", "unresolved_exception_classes", "reopen_triggers", "allowed_cube_artifacts", "prohibited_cube_artifacts"]:
            values = control.get(field, [])
            if not isinstance(values, list) or not values:
                fail(f"fieldwork closure dossier {dossier_id} missing non-empty {field}")
        for field, terms in required_closure_terms.items():
            require_text_contains(dossier_id, field, " ".join(control.get(field, [])) if isinstance(control.get(field, []), list) else str(control.get(field, "")), terms, fail)
        if len(control.get("material_outcome_fields", [])) < 5:
            fail(f"fieldwork closure dossier {dossier_id} has too few material outcome fields")
        material_text = " ".join(control.get("closure_evidence_required", []) + control.get("material_outcome_fields", [])).lower()
        if dossier_id.startswith("FCD-UI"):
            for token in ["payment", "hold", "waiver", "appeal", "burden"]:
                if token not in material_text:
                    fail(f"fieldwork closure dossier {dossier_id} lacks UI material token {token!r}")
        if dossier_id.startswith("FCD-HC"):
            for token in ["possession", "lockout", "rehousing", "screening", "stability"]:
                if token not in material_text:
                    fail(f"fieldwork closure dossier {dossier_id} lacks housing material token {token!r}")
        prohibited_lower = {str(item).lower() for item in control.get("prohibited_cube_artifacts", [])}
        missing_prohibited = required_closure_prohibited - prohibited_lower
        if missing_prohibited:
            fail(f"fieldwork closure dossier {dossier_id} does not prohibit required private closure artifacts: {sorted(missing_prohibited)}")
        for item in prohibited_lower:
            closure_prohibited_counts[item] = closure_prohibited_counts.get(item, 0) + 1
        allowed_text = " ".join(control.get("allowed_cube_artifacts", [])).lower()
        if any(token in allowed_text for token in ["social_security", "address", "docket_number", "linkage_key", "raw_audio", "raw_transcript", "payment_record", "court_file", "partner_case_record"]):
            fail(f"fieldwork closure dossier {dossier_id} allowed artifacts appear to allow private closure material")
        boundary_text = " ".join(
            control.get("closure_evidence_required", [])
            + control.get("allowed_cube_artifacts", [])
            + [control.get("privacy_posture", ""), fieldwork_closure_dossiers.get("privacy_posture", ""), control.get("closure_blocker", "")]
        ).lower()
        if "outside-cube" not in boundary_text:
            fail(f"fieldwork closure dossier {dossier_id} must keep private verification evidence outside-cube")
        if any(token in (control.get("closure_blocker", "") + control.get("next_action", "")).lower() for token in ["gap closed", "field validation complete", "outcome proven", "attestation proves", "dossier proves"]):
            fail(f"fieldwork closure dossier {dossier_id} uses attestation/dossier-as-proof language in blocker or next_action")
        for item in control.get("unresolved_exception_classes", []):
            closure_unresolved_counts[item] = closure_unresolved_counts.get(item, 0) + 1
        for item in control.get("reopen_triggers", []):
            closure_reopen_counts[item] = closure_reopen_counts.get(item, 0) + 1
        for item in control.get("material_outcome_fields", []):
            closure_material_counts[item] = closure_material_counts.get(item, 0) + 1
    for required_gap in REQUIRED_FIELDWORK_GAPS:
        if required_gap not in closure_gap_map:
            fail(f"fieldwork closure dossiers must include closure blockers for {required_gap}")
    generated_fieldwork_closure_dossiers = load_json(GENERATED / "FIELDWORK_CLOSURE_DOSSIERS.json")
    if generated_fieldwork_closure_dossiers.get("revision") != CURRENT_REV:
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json revision mismatch")
    if generated_fieldwork_closure_dossiers.get("control_count") != len(closure_dossier_ids):
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json control count mismatch metadata/fieldwork_closure_dossiers.json")
    if {row.get("control_id") for row in generated_fieldwork_closure_dossiers.get("controls", [])} != closure_dossier_ids:
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json control ids do not match metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("closure_readiness_status_counts") != dict(sorted(closure_status_counts.items())):
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json closure_readiness_status_counts mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("source_claim_receipt_counts") != dict(sorted(closure_source_claim_counts.items())):
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json source_claim_receipt_counts mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("prohibited_artifact_counts") != dict(sorted(closure_prohibited_counts.items())):
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json prohibited_artifact_counts mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("unresolved_exception_counts") != dict(sorted(closure_unresolved_counts.items())):
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json unresolved_exception_counts mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("reopen_trigger_counts") != dict(sorted(closure_reopen_counts.items())):
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json reopen_trigger_counts mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("material_field_counts") != dict(sorted(closure_material_counts.items())):
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json material_field_counts mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("gap_control_map") != {k: sorted(v) for k, v in sorted(closure_gap_map.items())}:
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json gap_control_map mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("redress_control_map") != {k: sorted(v) for k, v in sorted(closure_redress_map.items())}:
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json redress_control_map mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("correction_control_map") != {k: sorted(v) for k, v in sorted(closure_correction_map.items())}:
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json correction_control_map mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("release_control_map") != {k: sorted(v) for k, v in sorted(closure_release_map.items())}:
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json release_control_map mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("execution_control_map") != {k: sorted(v) for k, v in sorted(closure_execution_map.items())}:
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json execution_control_map mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("authorization_gate_control_map") != {k: sorted(v) for k, v in sorted(closure_authorization_map.items())}:
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json authorization_gate_control_map mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("field_intake_control_map") != {k: sorted(v) for k, v in sorted(closure_field_intake_map.items())}:
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json field_intake_control_map mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("sampling_gate_control_map") != {k: sorted(v) for k, v in sorted(closure_sampling_map.items())}:
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json sampling_gate_control_map mismatch metadata/fieldwork_closure_dossiers.json")
    if generated_fieldwork_closure_dossiers.get("outcome_plan_control_map") != {k: sorted(v) for k, v in sorted(closure_outcome_plan_map.items())}:
        fail("generated/FIELDWORK_CLOSURE_DOSSIERS.json outcome_plan_control_map mismatch metadata/fieldwork_closure_dossiers.json")


    fieldwork_postclosure_monitoring_controls = load_json(METADATA_DIR / "fieldwork_postclosure_monitoring_controls.json")
    if fieldwork_postclosure_monitoring_controls.get("schema") != "radical-governance-fieldwork-postclosure-monitoring-controls-v1":
        fail("metadata/fieldwork_postclosure_monitoring_controls.json missing expected schema")
    if fieldwork_postclosure_monitoring_controls.get("revision") != CURRENT_REV:
        fail(f"metadata/fieldwork_postclosure_monitoring_controls.json revision mismatch: expected {CURRENT_REV}")
    postclosure_control_ids = set(fieldwork_postclosure_monitoring_controls.get("controls", {}))
    if len(postclosure_control_ids) < 2:
        fail("metadata/fieldwork_postclosure_monitoring_controls.json must include at least UI and housing post-closure monitoring controls")
    required_postclosure_receipts = {
        "SCR-A123-2026-MONITORING-001",
        "SCR-GAO-GREENBOOK-MONITORING-001",
        "SCR-GAO-EVIDENCE-CI-001",
        "SCR-A11-S290-LEARNING-001",
    }
    if not required_postclosure_receipts.issubset(source_claim_ids):
        fail(f"post-closure monitoring receipts missing from metadata/source_claim_receipts.json: {sorted(required_postclosure_receipts - source_claim_ids)}")
    required_postclosure_prohibited = {"linkage_key", "raw_monitoring_log", "private_screenshot", "partner_case_record", "redress_case_file"}
    postclosure_status_counts: dict[str, int] = {}
    postclosure_source_claim_counts: dict[str, int] = {}
    postclosure_prohibited_counts: dict[str, int] = {}
    postclosure_drift_counts: dict[str, int] = {}
    postclosure_cadence_counts: dict[str, int] = {}
    postclosure_reopen_rule_counts: dict[str, int] = {}
    postclosure_gap_map: dict[str, list[str]] = {}
    postclosure_closure_map: dict[str, list[str]] = {}
    postclosure_redress_map: dict[str, list[str]] = {}
    postclosure_correction_map: dict[str, list[str]] = {}
    postclosure_release_map: dict[str, list[str]] = {}
    postclosure_execution_map: dict[str, list[str]] = {}
    postclosure_authorization_map: dict[str, list[str]] = {}
    postclosure_field_intake_map: dict[str, list[str]] = {}
    postclosure_sampling_map: dict[str, list[str]] = {}
    postclosure_outcome_plan_map: dict[str, list[str]] = {}
    for control_id, control in fieldwork_postclosure_monitoring_controls.get("controls", {}).items():
        if not control_id.startswith("PCM-"):
            fail(f"fieldwork post-closure monitoring control id should start with PCM-: {control_id}")
        status = control.get("monitoring_status", "")
        if any(token in status.lower() for token in ["active", "approved", "complete", "validated", "closed"]):
            fail(f"fieldwork post-closure monitoring control {control_id} claims active/closure-like status: {status}")
        postclosure_status_counts[status] = postclosure_status_counts.get(status, 0) + 1
        ids = validate_fieldwork_post_closure_links(
            surface_kind="fieldwork post-closure monitoring control",
            surface_id=control_id,
            row=control,
            closure_dossier_ids=closure_dossier_ids,
            closure_dossiers=fieldwork_closure_dossiers.get("controls", {}),
            redress_control_ids=redress_control_ids,
            redress_controls=fieldwork_redress_verification_controls.get("controls", {}),
            correction_control_ids=correction_control_ids,
            correction_controls=fieldwork_correction_controls.get("controls", {}),
            release_control_ids=release_control_ids,
            release_controls=fieldwork_release_controls.get("controls", {}),
            execution_control_ids=execution_control_ids,
            execution_controls=fieldwork_execution_controls.get("controls", {}),
            known_gap_ids=known_gap_ids,
            source_claim_ids=source_claim_ids,
            authorization_gate_ids=authorization_gate_ids,
            field_control_ids=field_control_ids,
            sampling_gate_ids=gate_ids,
            plan_ids=plan_ids,
            authorization_gates=fieldwork_authorization_gates.get("gates", {}),
            field_intake_controls=field_intake_controls.get("controls", {}),
            fail=fail,
        )
        postclosure_closure_map.setdefault(ids["fieldwork_closure_dossier"], []).append(control_id)
        postclosure_redress_map.setdefault(ids["fieldwork_redress_verification_control"], []).append(control_id)
        postclosure_correction_map.setdefault(ids["fieldwork_correction_control"], []).append(control_id)
        postclosure_release_map.setdefault(ids["fieldwork_release_control"], []).append(control_id)
        postclosure_execution_map.setdefault(ids["fieldwork_execution_control"], []).append(control_id)
        postclosure_authorization_map.setdefault(ids["authorization_gate"], []).append(control_id)
        postclosure_field_intake_map.setdefault(ids["field_intake_control"], []).append(control_id)
        postclosure_sampling_map.setdefault(ids["sampling_gate"], []).append(control_id)
        postclosure_outcome_plan_map.setdefault(ids["outcome_tail_plan"], []).append(control_id)
        for field in ["monitoring_cadence_classes", "drift_triggers", "recheck_evidence_required", "allowed_cube_artifacts", "prohibited_cube_artifacts", "gap_reopen_rules"]:
            if not isinstance(control.get(field), list) or not control[field]:
                fail(f"fieldwork post-closure monitoring control {control_id} missing non-empty {field}")
        for rid in control.get("linked_source_claim_receipts", []):
            if rid not in source_claim_ids:
                fail(f"fieldwork post-closure monitoring control {control_id} links unknown source-claim receipt {rid}")
            postclosure_source_claim_counts[rid] = postclosure_source_claim_counts.get(rid, 0) + 1
        if len(set(control.get("linked_source_claim_receipts", [])) & required_postclosure_receipts) < 3:
            fail(f"fieldwork post-closure monitoring control {control_id} needs multiple monitoring/evidence receipts")
        for gap_id in control.get("linked_gaps", []):
            if gap_id not in known_gap_ids:
                fail(f"fieldwork post-closure monitoring control {control_id} links unknown gap {gap_id}")
            postclosure_gap_map.setdefault(gap_id, []).append(control_id)
        for required_gap in REQUIRED_FIELDWORK_GAPS:
            if required_gap not in control.get("linked_gaps", []):
                fail(f"fieldwork post-closure monitoring control {control_id} must block {required_gap}")
        drift_text = " ".join(control.get("drift_triggers", []) + control.get("gap_reopen_rules", []) + [control.get("monitoring_blocker", "")]).lower()
        for token in ["reopen", "recurrence", "source", "privacy"]:
            if token not in drift_text:
                fail(f"fieldwork post-closure monitoring control {control_id} lacks drift/reopen token {token!r}")
        if control_id.startswith("PCM-UI"):
            for token in ["payment", "hold", "appeal", "debt", "burden"]:
                if token not in drift_text:
                    fail(f"fieldwork post-closure monitoring control {control_id} lacks UI drift token {token!r}")
        if control_id.startswith("PCM-HC"):
            for token in ["possession", "lockout", "rehousing", "screening", "stability"]:
                if token not in drift_text:
                    fail(f"fieldwork post-closure monitoring control {control_id} lacks housing drift token {token!r}")
        for item in control.get("drift_triggers", []):
            postclosure_drift_counts[item] = postclosure_drift_counts.get(item, 0) + 1
        for item in control.get("monitoring_cadence_classes", []):
            postclosure_cadence_counts[item] = postclosure_cadence_counts.get(item, 0) + 1
        for item in control.get("gap_reopen_rules", []):
            postclosure_reopen_rule_counts[item] = postclosure_reopen_rule_counts.get(item, 0) + 1
        prohibited_lower = {str(item).lower() for item in control.get("prohibited_cube_artifacts", [])}
        if not required_postclosure_prohibited.issubset(prohibited_lower):
            fail(f"fieldwork post-closure monitoring control {control_id} does not prohibit required private monitoring artifacts: {sorted(required_postclosure_prohibited - prohibited_lower)}")
        for item in prohibited_lower:
            postclosure_prohibited_counts[item] = postclosure_prohibited_counts.get(item, 0) + 1
        allowed_text = " ".join(control.get("allowed_cube_artifacts", [])).lower()
        if any(token in allowed_text for token in ["name", "address", "claim_number", "docket_number", "linkage_key", "raw", "payment_record", "court_file", "partner_case_record"]):
            fail(f"fieldwork post-closure monitoring control {control_id} allowed artifacts appear to allow private monitoring material")
        boundary_text = " ".join(control.get("recheck_evidence_required", []) + control.get("allowed_cube_artifacts", []) + [control.get("monitoring_blocker", ""), fieldwork_postclosure_monitoring_controls.get("privacy_posture", "")]).lower()
        if "outside-cube" not in boundary_text:
            fail(f"fieldwork post-closure monitoring control {control_id} must keep private monitoring evidence outside-cube")
        if any(token in (control.get("monitoring_blocker", "") + control.get("next_action", "")).lower() for token in ["closure forever", "monitoring proves", "gap remains closed", "outcome proven", "field validation complete"]):
            fail(f"fieldwork post-closure monitoring control {control_id} uses monitoring/finality-as-proof language in blocker or next_action")
    for required_gap in REQUIRED_FIELDWORK_GAPS:
        if required_gap not in postclosure_gap_map:
            fail(f"fieldwork post-closure monitoring controls must include blockers for {required_gap}")
    generated_fieldwork_postclosure_monitoring_controls = load_json(GENERATED / "FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("revision") != CURRENT_REV:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json revision mismatch")
    if generated_fieldwork_postclosure_monitoring_controls.get("control_count") != len(postclosure_control_ids):
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json control count mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if {row.get("control_id") for row in generated_fieldwork_postclosure_monitoring_controls.get("controls", [])} != postclosure_control_ids:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json control ids do not match metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("monitoring_status_counts") != dict(sorted(postclosure_status_counts.items())):
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json monitoring_status_counts mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("source_claim_receipt_counts") != dict(sorted(postclosure_source_claim_counts.items())):
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json source_claim_receipt_counts mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("prohibited_artifact_counts") != dict(sorted(postclosure_prohibited_counts.items())):
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json prohibited_artifact_counts mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("drift_trigger_counts") != dict(sorted(postclosure_drift_counts.items())):
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json drift_trigger_counts mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("cadence_class_counts") != dict(sorted(postclosure_cadence_counts.items())):
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json cadence_class_counts mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("gap_reopen_rule_counts") != dict(sorted(postclosure_reopen_rule_counts.items())):
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json gap_reopen_rule_counts mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("gap_control_map") != {k: sorted(v) for k, v in sorted(postclosure_gap_map.items())}:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json gap_control_map mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("closure_dossier_map") != {k: sorted(v) for k, v in sorted(postclosure_closure_map.items())}:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json closure_dossier_map mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("redress_control_map") != {k: sorted(v) for k, v in sorted(postclosure_redress_map.items())}:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json redress_control_map mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("correction_control_map") != {k: sorted(v) for k, v in sorted(postclosure_correction_map.items())}:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json correction_control_map mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("release_control_map") != {k: sorted(v) for k, v in sorted(postclosure_release_map.items())}:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json release_control_map mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("execution_control_map") != {k: sorted(v) for k, v in sorted(postclosure_execution_map.items())}:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json execution_control_map mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("authorization_gate_control_map") != {k: sorted(v) for k, v in sorted(postclosure_authorization_map.items())}:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json authorization_gate_control_map mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("field_intake_control_map") != {k: sorted(v) for k, v in sorted(postclosure_field_intake_map.items())}:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json field_intake_control_map mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("sampling_gate_control_map") != {k: sorted(v) for k, v in sorted(postclosure_sampling_map.items())}:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json sampling_gate_control_map mismatch metadata/fieldwork_postclosure_monitoring_controls.json")
    if generated_fieldwork_postclosure_monitoring_controls.get("outcome_plan_control_map") != {k: sorted(v) for k, v in sorted(postclosure_outcome_plan_map.items())}:
        fail("generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json outcome_plan_control_map mismatch metadata/fieldwork_postclosure_monitoring_controls.json")



    archive_stewardship_handoff_controls = load_json(METADATA_DIR / "archive_stewardship_handoff_controls.json")
    if archive_stewardship_handoff_controls.get("schema") != "radical-governance-archive-stewardship-handoff-controls-v1":
        fail("metadata/archive_stewardship_handoff_controls.json missing expected schema")
    if archive_stewardship_handoff_controls.get("revision") != CURRENT_REV:
        fail(f"metadata/archive_stewardship_handoff_controls.json revision mismatch: expected {CURRENT_REV}")
    stewardship_control_ids = set(archive_stewardship_handoff_controls.get("controls", {}))
    if len(stewardship_control_ids) < 3:
        fail("metadata/archive_stewardship_handoff_controls.json must include archive, security, and succession handoff controls")
    required_stewardship_receipts = {
        "SCR-M16-21-OPEN-CODE-001",
        "SCR-GSA-OSS-POLICY-001",
        "SCR-CISA-VDP-001",
        "SCR-CISA-VDP-TEMPLATE-001",
        "SCR-REUSE-LICENSE-001",
        "SCR-CC-LICENSE-CONSIDERATIONS-001",
        "SCR-OSS-GOVERNANCE-ROLES-001",
    }
    if not required_stewardship_receipts.issubset(source_claim_ids):
        fail(f"archive stewardship receipts missing from metadata/source_claim_receipts.json: {sorted(required_stewardship_receipts - source_claim_ids)}")
    stewardship_status_counts: dict[str, int] = {}
    stewardship_source_claim_counts: dict[str, int] = {}
    stewardship_public_doc_counts: dict[str, int] = {}
    stewardship_role_counts: dict[str, int] = {}
    stewardship_owner_decision_counts: dict[str, int] = {}
    stewardship_clock_counts: dict[str, int] = {}
    stewardship_prohibited_counts: dict[str, int] = {}
    stewardship_gap_map: dict[str, list[str]] = {}
    required_public_docs = {"LICENSE_or_RIGHTS.md", "GOVERNANCE.md", "MAINTAINERS.md", "CONTRIBUTING.md", "SECURITY.md", "SUCCESSION.md"}
    required_roles = {"security_contact", "release_manager", "source_preservation_steward", "route_retirement_steward", "succession_backup"}
    for control_id, control in archive_stewardship_handoff_controls.get("controls", {}).items():
        validate_archive_stewardship_handoff_control(
            control_id=control_id,
            row=control,
            known_gap_ids=known_gap_ids,
            source_claim_ids=source_claim_ids,
            fail=fail,
        )
        status = control.get("handoff_status", "")
        stewardship_status_counts[status] = stewardship_status_counts.get(status, 0) + 1
        for rid in control.get("linked_source_claim_receipts", []):
            stewardship_source_claim_counts[rid] = stewardship_source_claim_counts.get(rid, 0) + 1
        for gap_id in control.get("linked_gaps", []):
            stewardship_gap_map.setdefault(gap_id, []).append(control_id)
        for item in control.get("required_public_documents", []):
            stewardship_public_doc_counts[item] = stewardship_public_doc_counts.get(item, 0) + 1
        for item in control.get("role_classes_required", []):
            stewardship_role_counts[item] = stewardship_role_counts.get(item, 0) + 1
        for item in control.get("required_owner_decisions", []):
            stewardship_owner_decision_counts[item] = stewardship_owner_decision_counts.get(item, 0) + 1
        for item in control.get("handoff_clocks", []):
            stewardship_clock_counts[item] = stewardship_clock_counts.get(item, 0) + 1
        for item in control.get("prohibited_cube_artifacts", []):
            stewardship_prohibited_counts[item] = stewardship_prohibited_counts.get(item, 0) + 1
    if "GAP-032-license-maintainer-contribution-governance" not in stewardship_gap_map:
        fail("archive stewardship handoff controls must block GAP-032")
    if not required_public_docs.issubset(stewardship_public_doc_counts):
        fail(f"archive stewardship handoff controls are missing required public document classes: {sorted(required_public_docs - set(stewardship_public_doc_counts))}")
    if not required_roles.issubset(stewardship_role_counts):
        fail(f"archive stewardship handoff controls are missing required role classes: {sorted(required_roles - set(stewardship_role_counts))}")
    generated_archive_stewardship_handoff_controls = load_json(GENERATED / "ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json")
    if generated_archive_stewardship_handoff_controls.get("revision") != CURRENT_REV:
        fail("generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json revision mismatch")
    if generated_archive_stewardship_handoff_controls.get("control_count") != len(stewardship_control_ids):
        fail("generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json control count mismatch metadata/archive_stewardship_handoff_controls.json")
    if {row.get("control_id") for row in generated_archive_stewardship_handoff_controls.get("controls", [])} != stewardship_control_ids:
        fail("generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json control ids do not match metadata/archive_stewardship_handoff_controls.json")
    if generated_archive_stewardship_handoff_controls.get("handoff_status_counts") != dict(sorted(stewardship_status_counts.items())):
        fail("generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json handoff_status_counts mismatch metadata/archive_stewardship_handoff_controls.json")
    if generated_archive_stewardship_handoff_controls.get("source_claim_receipt_counts") != dict(sorted(stewardship_source_claim_counts.items())):
        fail("generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json source_claim_receipt_counts mismatch metadata/archive_stewardship_handoff_controls.json")
    if generated_archive_stewardship_handoff_controls.get("public_document_counts") != dict(sorted(stewardship_public_doc_counts.items())):
        fail("generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json public_document_counts mismatch metadata/archive_stewardship_handoff_controls.json")
    if generated_archive_stewardship_handoff_controls.get("role_class_counts") != dict(sorted(stewardship_role_counts.items())):
        fail("generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json role_class_counts mismatch metadata/archive_stewardship_handoff_controls.json")
    if generated_archive_stewardship_handoff_controls.get("owner_decision_counts") != dict(sorted(stewardship_owner_decision_counts.items())):
        fail("generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json owner_decision_counts mismatch metadata/archive_stewardship_handoff_controls.json")
    if generated_archive_stewardship_handoff_controls.get("handoff_clock_counts") != dict(sorted(stewardship_clock_counts.items())):
        fail("generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json handoff_clock_counts mismatch metadata/archive_stewardship_handoff_controls.json")
    if generated_archive_stewardship_handoff_controls.get("prohibited_artifact_counts") != dict(sorted(stewardship_prohibited_counts.items())):
        fail("generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json prohibited_artifact_counts mismatch metadata/archive_stewardship_handoff_controls.json")
    if generated_archive_stewardship_handoff_controls.get("gap_control_map") != {k: sorted(v) for k, v in sorted(stewardship_gap_map.items())}:
        fail("generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json gap_control_map mismatch metadata/archive_stewardship_handoff_controls.json")

    route_metadata = load_json(METADATA_DIR / "note_metadata.json")
    route_metadata_notes = route_metadata.get("notes", {})
    service_home_tests = load_json(METADATA_DIR / "service_home_tests.json")
    service_home_test_ids = set(service_home_tests.get("tests", {}).keys())
    route_redirect_ledger = load_json(METADATA_DIR / "route_redirect_ledger.json")
    if route_redirect_ledger.get("schema") != "route_redirect_ledger.v1":
        fail("metadata/route_redirect_ledger.json missing expected schema")
    if route_redirect_ledger.get("revision") != CURRENT_REV:
        fail(f"metadata/route_redirect_ledger.json revision mismatch: expected {CURRENT_REV}")
    redirect_ledgers = route_redirect_ledger.get("ledgers", {})
    if not isinstance(redirect_ledgers, dict):
        fail("metadata/route_redirect_ledger.json ledgers must be an object")
    for ledger_id, ledger in redirect_ledgers.items():
        source_file = ledger.get("source_file")
        successor_file = ledger.get("successor_file")
        ledger_file = ledger.get("ledger_file")
        source_note = ledger.get("source_note")
        successor_note = ledger.get("successor_note")
        ledger_note = ledger.get("ledger_note")
        for file_field, file_value in [("source_file", source_file), ("successor_file", successor_file), ("ledger_file", ledger_file)]:
            if not isinstance(file_value, str) or not (ROOT / file_value).exists():
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} missing {file_field}: {file_value}")
        for note_field, note_value in [("source_note", source_note), ("successor_note", successor_note), ("ledger_note", ledger_note)]:
            if note_value not in numbers:
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} references unknown {note_field} {note_value}")
        if route_metadata_notes.get(source_file, {}).get("number") != source_note:
            fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} source file/note mismatch")
        if route_metadata_notes.get(successor_file, {}).get("number") != successor_note:
            fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} successor file/note mismatch")
        if route_metadata_notes.get(ledger_file, {}).get("number") != ledger_note:
            fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} ledger file/note mismatch")
        if ledger.get("deletion_authorization") is not False:
            fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} must not authorize deletion in this archive posture")
        reader_status = ledger.get("reader_redirect_status")
        reader_surfaces = ledger.get("reader_redirect_surfaces", [])
        if reader_status == "reader_redirect_visible_keep_active":
            if not isinstance(reader_surfaces, list) or not reader_surfaces:
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} claims reader-visible status without reader_redirect_surfaces")
            reader_file = ledger.get("reader_redirect_file")
            reader_note = ledger.get("reader_redirect_note")
            if not isinstance(reader_file, str) or not (ROOT / reader_file).exists():
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} reader_redirect_file missing: {reader_file}")
            if reader_note not in numbers:
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} reader_redirect_note unknown: {reader_note}")
            reader_meta = route_metadata_notes.get(reader_file, {})
            if reader_meta.get("number") != reader_note:
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} reader redirect file/note mismatch")
            for surface in reader_surfaces:
                if isinstance(surface, dict):
                    surface_path = surface.get("surface")
                    purpose = surface.get("purpose")
                    if not isinstance(purpose, str) or not purpose.strip():
                        fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} reader surface missing purpose: {surface}")
                else:
                    surface_path = surface
                if not isinstance(surface_path, str) or not (ROOT / surface_path).exists():
                    fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} reader surface missing: {surface_path}")
        final_review_file = ledger.get("final_preservation_review_file")
        final_review_note = ledger.get("final_preservation_review_note")
        if (final_review_file is None) != (final_review_note is None):
            fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} final preservation review must include both file and note")
        if final_review_file is not None:
            if not isinstance(final_review_file, str) or not (ROOT / final_review_file).exists():
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} final_preservation_review_file missing: {final_review_file}")
            if final_review_note not in numbers:
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} final_preservation_review_note unknown: {final_review_note}")
            final_meta = route_metadata_notes.get(final_review_file, {})
            if final_meta.get("number") != final_review_note:
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} final preservation review file/note mismatch")
            if not isinstance(ledger.get("final_preservation_review_status"), str) or not ledger["final_preservation_review_status"].strip():
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} final preservation review missing status")
        rows = ledger.get("redirect_rows")
        if not isinstance(rows, list) or not rows:
            fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} missing redirect_rows")
        for row in rows:
            for field in ["element_id", "protected_element", "source_note_element", "successor_section", "status", "limits"]:
                if not isinstance(row.get(field), str) or not row[field].strip():
                    fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} row missing {field}: {row}")
            if row.get("successor_note") != successor_note:
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} row successor_note mismatch: {row}")
            if not isinstance(row.get("test_ids"), list) or not row["test_ids"]:
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} row missing test_ids: {row}")
            for test_id in row.get("test_ids", []):
                if test_id not in service_home_test_ids:
                    fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} row unknown service-home test_id {test_id}")
            if not isinstance(row.get("source_keys"), list) or not row["source_keys"]:
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} row missing source_keys: {row}")
            for source_key in row.get("source_keys", []):
                if source_key not in source_key_registry:
                    fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} row unknown source_key {source_key}")
            if not isinstance(row.get("applied_examples"), list) or not row["applied_examples"]:
                fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} row missing applied_examples: {row}")
            for note in row.get("applied_examples", []):
                if note not in numbers:
                    fail(f"metadata/route_redirect_ledger.json ledger {ledger_id} row unknown applied_example note {note}")

    route_merge_packets = load_json(METADATA_DIR / "route_merge_packets.json")
    if route_merge_packets.get("schema") != "route_merge_packets.v1":
        fail("metadata/route_merge_packets.json missing expected schema")
    if route_merge_packets.get("revision") != CURRENT_REV:
        fail(f"metadata/route_merge_packets.json revision mismatch: expected {CURRENT_REV}")
    for packet_id, packet in route_merge_packets.get("packets", {}).items():
        source_file = packet.get("source_file")
        if not isinstance(source_file, str) or not (ROOT / source_file).exists():
            fail(f"metadata/route_merge_packets.json packet {packet_id} has missing source_file: {source_file}")
        source_note = packet.get("source_note")
        if source_note not in numbers:
            fail(f"metadata/route_merge_packets.json packet {packet_id} references unknown source_note {source_note}")
        source_meta = route_metadata_notes.get(source_file, {})
        if source_meta.get("number") != source_note:
            fail(f"metadata/route_merge_packets.json packet {packet_id} source_file/source_note mismatch")
        if not isinstance(packet.get("target_files"), list) or not packet.get("target_files"):
            fail(f"metadata/route_merge_packets.json packet {packet_id} missing target_files")
        if not isinstance(packet.get("target_notes"), list) or not packet.get("target_notes"):
            fail(f"metadata/route_merge_packets.json packet {packet_id} missing target_notes")
        for target_file in packet.get("target_files", []):
            if not isinstance(target_file, str) or not (ROOT / target_file).exists():
                fail(f"metadata/route_merge_packets.json packet {packet_id} target_file missing: {target_file}")
        for target_note in packet.get("target_notes", []):
            if target_note not in numbers:
                fail(f"metadata/route_merge_packets.json packet {packet_id} references unknown target_note {target_note}")
        if not isinstance(packet.get("candidate_status"), str) or not packet["candidate_status"].strip():
            fail(f"metadata/route_merge_packets.json packet {packet_id} missing candidate_status")
        if not isinstance(packet.get("protected_elements"), list) or not packet["protected_elements"]:
            fail(f"metadata/route_merge_packets.json packet {packet_id} missing protected_elements")
        if not isinstance(packet.get("preservation_findings"), list) or not packet["preservation_findings"]:
            fail(f"metadata/route_merge_packets.json packet {packet_id} missing preservation_findings")
        if not isinstance(packet.get("absorption_requirements"), list) or not packet["absorption_requirements"]:
            fail(f"metadata/route_merge_packets.json packet {packet_id} missing absorption_requirements")
        if not isinstance(packet.get("next_action"), str) or not packet["next_action"].strip():
            fail(f"metadata/route_merge_packets.json packet {packet_id} missing next_action")
        review_packet_file = packet.get("review_packet_file")
        review_packet_note = packet.get("review_packet_note")
        if (review_packet_file is None) != (review_packet_note is None):
            fail(f"metadata/route_merge_packets.json packet {packet_id} review packet must include both file and note")
        if review_packet_file is not None:
            if not isinstance(review_packet_file, str) or not (ROOT / review_packet_file).exists():
                fail(f"metadata/route_merge_packets.json packet {packet_id} review_packet_file missing: {review_packet_file}")
            if review_packet_note not in numbers:
                fail(f"metadata/route_merge_packets.json packet {packet_id} references unknown review_packet_note {review_packet_note}")
            review_meta = route_metadata_notes.get(review_packet_file, {})
            if review_meta.get("number") != review_packet_note:
                fail(f"metadata/route_merge_packets.json packet {packet_id} review packet file/note mismatch")
        patch_file = packet.get("partial_absorption_patch_file")
        patch_note = packet.get("partial_absorption_patch_note")
        if (patch_file is None) != (patch_note is None):
            fail(f"metadata/route_merge_packets.json packet {packet_id} partial absorption patch must include both file and note")
        if patch_file is not None:
            if not isinstance(patch_file, str) or not (ROOT / patch_file).exists():
                fail(f"metadata/route_merge_packets.json packet {packet_id} partial_absorption_patch_file missing: {patch_file}")
            if patch_note not in numbers:
                fail(f"metadata/route_merge_packets.json packet {packet_id} references unknown partial_absorption_patch_note {patch_note}")
            patch_meta = route_metadata_notes.get(patch_file, {})
            if patch_meta.get("number") != patch_note:
                fail(f"metadata/route_merge_packets.json packet {packet_id} partial absorption patch file/note mismatch")
            progress = packet.get("absorption_progress", [])
            if not isinstance(progress, list) or not progress:
                fail(f"metadata/route_merge_packets.json packet {packet_id} partial absorption patch missing absorption_progress")
            for item in progress:
                if not isinstance(item, str) or not item.strip():
                    fail(f"metadata/route_merge_packets.json packet {packet_id} invalid absorption_progress item")
        successor_file = packet.get("successor_route_file")
        successor_note = packet.get("successor_route_note")
        if (successor_file is None) != (successor_note is None):
            fail(f"metadata/route_merge_packets.json packet {packet_id} successor route must include both file and note")
        if successor_file is not None:
            if not isinstance(successor_file, str) or not (ROOT / successor_file).exists():
                fail(f"metadata/route_merge_packets.json packet {packet_id} successor_route_file missing: {successor_file}")
            if successor_note not in numbers:
                fail(f"metadata/route_merge_packets.json packet {packet_id} references unknown successor_route_note {successor_note}")
            successor_meta = route_metadata_notes.get(successor_file, {})
            if successor_meta.get("number") != successor_note:
                fail(f"metadata/route_merge_packets.json packet {packet_id} successor route file/note mismatch")
            if successor_file not in packet.get("target_files", []):
                fail(f"metadata/route_merge_packets.json packet {packet_id} successor route must also appear in target_files")
            if successor_note not in packet.get("target_notes", []):
                fail(f"metadata/route_merge_packets.json packet {packet_id} successor route must also appear in target_notes")
            parity_keys = packet.get("successor_source_parity_keys", [])
            if not isinstance(parity_keys, list) or not parity_keys:
                fail(f"metadata/route_merge_packets.json packet {packet_id} successor route missing source parity keys")
            for source_key in parity_keys:
                if source_key not in source_key_registry:
                    fail(f"metadata/route_merge_packets.json packet {packet_id} successor route unknown source parity key {source_key}")
        service_matrix = packet.get("service_home_test_matrix")
        if service_matrix is not None and not (METADATA_DIR / service_matrix.replace("metadata/", "")).exists():
            fail(f"metadata/route_merge_packets.json packet {packet_id} service_home_test_matrix missing: {service_matrix}")
        redirect_ledger_file = packet.get("redirect_ledger_file")
        redirect_ledger_id = packet.get("redirect_ledger_id")
        if (redirect_ledger_file is None) != (redirect_ledger_id is None):
            fail(f"metadata/route_merge_packets.json packet {packet_id} redirect ledger must include both file and id")
        if redirect_ledger_id is not None:
            if redirect_ledger_file != "metadata/route_redirect_ledger.json":
                fail(f"metadata/route_merge_packets.json packet {packet_id} unexpected redirect_ledger_file: {redirect_ledger_file}")
            ledger = redirect_ledgers.get(redirect_ledger_id)
            if ledger is None:
                fail(f"metadata/route_merge_packets.json packet {packet_id} unknown redirect_ledger_id {redirect_ledger_id}")
            if ledger.get("source_note") != source_note:
                fail(f"metadata/route_merge_packets.json packet {packet_id} redirect ledger source_note mismatch")
            if successor_note is not None and ledger.get("successor_note") != successor_note:
                fail(f"metadata/route_merge_packets.json packet {packet_id} redirect ledger successor_note mismatch")
            if len(ledger.get("redirect_rows", [])) < len(packet.get("protected_elements", [])):
                fail(f"metadata/route_merge_packets.json packet {packet_id} redirect ledger has fewer rows than protected elements")
            if ledger.get("deletion_authorization") is not False:
                fail(f"metadata/route_merge_packets.json packet {packet_id} redirect ledger cannot authorize deletion")
            if not isinstance(packet.get("redirect_ledger_status"), str) or not packet["redirect_ledger_status"].strip():
                fail(f"metadata/route_merge_packets.json packet {packet_id} missing redirect_ledger_status")
            if packet.get("reader_redirect_status") == "reader_redirect_visible_keep_active":
                if ledger.get("reader_redirect_status") != "reader_redirect_visible_keep_active":
                    fail(f"metadata/route_merge_packets.json packet {packet_id} reader redirect status not reflected in ledger")
                packet_surfaces = packet.get("reader_redirect_surfaces", [])
                if not isinstance(packet_surfaces, list) or not packet_surfaces:
                    fail(f"metadata/route_merge_packets.json packet {packet_id} missing reader_redirect_surfaces")
                ledger_surfaces = [s.get("surface") if isinstance(s, dict) else s for s in ledger.get("reader_redirect_surfaces", [])]
                if set(packet_surfaces) != set(ledger_surfaces):
                    fail(f"metadata/route_merge_packets.json packet {packet_id} reader_redirect_surfaces differ from ledger")
        final_review_file = packet.get("final_preservation_review_file")
        final_review_note = packet.get("final_preservation_review_note")
        if (final_review_file is None) != (final_review_note is None):
            fail(f"metadata/route_merge_packets.json packet {packet_id} final preservation review must include both file and note")
        if final_review_file is not None:
            if not isinstance(final_review_file, str) or not (ROOT / final_review_file).exists():
                fail(f"metadata/route_merge_packets.json packet {packet_id} final_preservation_review_file missing: {final_review_file}")
            if final_review_note not in numbers:
                fail(f"metadata/route_merge_packets.json packet {packet_id} references unknown final_preservation_review_note {final_review_note}")
            final_meta = route_metadata_notes.get(final_review_file, {})
            if final_meta.get("number") != final_review_note:
                fail(f"metadata/route_merge_packets.json packet {packet_id} final preservation review file/note mismatch")
            if not isinstance(packet.get("final_preservation_review_status"), str) or not packet["final_preservation_review_status"].strip():
                fail(f"metadata/route_merge_packets.json packet {packet_id} final preservation review missing status")
            if not isinstance(packet.get("retirement_blockers"), list) or not packet["retirement_blockers"]:
                fail(f"metadata/route_merge_packets.json packet {packet_id} final preservation review missing retirement_blockers")

    gap_ledger = load_json(METADATA_DIR / "gap_ledger.json")
    if gap_ledger.get("schema") != "radical-governance-gap-ledger-v1":
        fail("metadata/gap_ledger.json missing expected schema")
    if gap_ledger.get("revision") != CURRENT_REV:
        fail(f"metadata/gap_ledger.json revision mismatch: expected {CURRENT_REV}")
    for gap_id, gap in gap_ledger.get("gaps", {}).items():
        for field in ["status", "severity", "missing_domain", "why_it_matters", "next_artifact", "why_not_now"]:
            if not isinstance(gap.get(field), str) or not gap[field].strip():
                fail(f"metadata/gap_ledger.json gap {gap_id} missing {field}")
        if not isinstance(gap.get("affected_parties"), list) or not gap["affected_parties"]:
            fail(f"metadata/gap_ledger.json gap {gap_id} missing non-empty affected_parties")
        for party in gap.get("affected_parties", []):
            if not isinstance(party, str) or not party.strip():
                fail(f"metadata/gap_ledger.json gap {gap_id} has invalid affected_parties entry")
        for note_number in gap.get("nearest_notes", []):
            if note_number not in numbers:
                fail(f"metadata/gap_ledger.json gap {gap_id} references unknown nearest note {note_number}")
        for key in gap.get("source_keys", []):
            if key not in source_key_registry:
                fail(f"metadata/gap_ledger.json gap {gap_id} references unknown source_key {key}")
    live_gap_ids = [
        gap_id
        for gap_id, gap in gap_ledger.get("gaps", {}).items()
        if not str(gap.get("status", "")).startswith("repaired")
    ]
    if not live_gap_ids:
        fail("metadata/gap_ledger.json contains no live gaps; an all-repaired ledger is not a credible backlog")
    generated_gap_ledger = load_json(GENERATED / "GAP_LEDGER.json")
    if generated_gap_ledger.get("revision") != CURRENT_REV:
        fail(f"generated/GAP_LEDGER.json revision mismatch: expected {CURRENT_REV}")
    if generated_gap_ledger.get("gap_count") != len(gap_ledger.get("gaps", {})):
        fail("generated/GAP_LEDGER.json gap count mismatch metadata/gap_ledger.json")
    generated_gap_ids = {gap.get("gap_id") for gap in generated_gap_ledger.get("gaps", [])}
    if generated_gap_ids != set(gap_ledger.get("gaps", {})):
        fail("generated/GAP_LEDGER.json gap ids mismatch metadata/gap_ledger.json")

    source_tool = (ROOT / "tools" / "build_sources_index.py").read_text(encoding="utf-8")
    if "NEW_NOTE_SOURCES" in source_tool:
        fail("tools/build_sources_index.py still contains embedded NEW_NOTE_SOURCES data")

    metadata = load_json(METADATA_DIR / "note_metadata.json")
    if metadata.get("schema") != "radical-governance-note-metadata-v1":
        fail("metadata/note_metadata.json missing expected schema")
    if metadata.get("revision") != CURRENT_REV:
        fail(f"metadata/note_metadata.json revision mismatch: expected {CURRENT_REV}")
    status_label_set = set(metadata.get("status_labels", {}))
    if not status_label_set:
        fail("metadata/note_metadata.json missing status_labels")
    metadata_notes = metadata.get("notes", {})
    if set(metadata_notes) != set(expected_files):
        fail("metadata/note_metadata.json note keys do not exactly match archive directory")
    for rel in expected_files:
        if rel not in metadata_notes:
            fail(f"metadata/note_metadata.json missing note entry: {rel}")
        meta = metadata_notes[rel]
        for field in ["number", "revision", "note_class", "status", "canon_role", "tags"]:
            if field not in meta:
                fail(f"metadata/note_metadata.json entry missing {field}: {rel}")
        if meta.get("status") not in status_label_set:
            fail(f"metadata/note_metadata.json entry has unknown status {meta.get('status')}: {rel}")
        if not isinstance(meta.get("tags"), list) or not meta["tags"]:
            fail(f"metadata/note_metadata.json entry missing non-empty tags: {rel}")
        for key in meta.get("source_keys", []):
            if key not in source_key_registry:
                fail(f"metadata/note_metadata.json references unknown source_key {key}: {rel}")
        for dep in meta.get("depends_on", []) + meta.get("reserved_notes", []):
            if dep not in numbers:
                fail(f"metadata/note_metadata.json references unknown note number {dep}: {rel}")
        dispatcher = meta.get("dispatcher")
        if dispatcher is not None and dispatcher not in numbers:
            fail(f"metadata/note_metadata.json references unknown dispatcher {dispatcher}: {rel}")

    # Current-revision source catalogs must match note-metadata source keys.
    # This catches fresh packet drift without forcing a historical backfill.
    for current_file in CURRENT_NOTES:
        metadata_keys = set(metadata_notes.get(current_file, {}).get("source_keys", []))
        catalog_groups = source_notes.get(current_file, {}).get("groups", [])
        catalog_keys = {group.get("source_key") for group in catalog_groups if group.get("source_key")}
        if metadata_keys != catalog_keys:
            fail(
                f"current note source-key mismatch between note_metadata and source_catalog for {current_file}: "
                f"metadata_only={sorted(metadata_keys - catalog_keys)} catalog_only={sorted(catalog_keys - metadata_keys)}"
            )

    # Current-revision source-catalog groups must match the source-key registry values,
    # not just the key names. This catches fresh packet drift where a copied group
    # silently points a source key at a different title, publisher, or URL.
    for current_file in CURRENT_NOTES:
        for group in source_notes.get(current_file, {}).get("groups", []):
            key = group.get("source_key")
            if not key:
                continue
            registry_entry = source_key_registry.get(key, {})
            for field in ["title", "publisher", "url"]:
                if group.get(field) != registry_entry.get(field):
                    fail(
                        f"current note source-catalog group disagrees with source_keys registry for {current_file} key {key} field {field}"
                    )

    # Current-revision source keys must carry explicit health/currentness posture.
    # This preserves forward momentum without forcing a full historical backfill.
    current_revision_source_keys = {
        key
        for current_file in CURRENT_NOTES
        for key in metadata_notes.get(current_file, {}).get("source_keys", [])
    }
    missing_current_source_health = sorted(current_revision_source_keys - set(source_health.get("entries", {})))
    if missing_current_source_health:
        fail(f"current revision source key missing manual source-health entry: {missing_current_source_health}")

    # Current source keys that first appear in this revision must carry explicit provenance.
    # This catches fresh-source copy-forward mistakes without forcing historical source-health backfill.
    previous_note_source_keys = {
        key
        for file, meta in metadata_notes.items()
        if file not in CURRENT_NOTES
        for key in meta.get("source_keys", [])
    }
    for key in sorted(current_revision_source_keys - previous_note_source_keys):
        entry = source_health.get("entries", {}).get(key, {})
        if entry.get("first_added_revision") != CURRENT_REV:
            fail(
                f"current source-health entry first_added_revision should be {CURRENT_REV} for first-use source key {key}, "
                f"got {entry.get('first_added_revision')}"
            )

    # Current substantive packets must also have a registered test matrix.
    # This blocks fresh doctrine/case packets from shipping without operational tests,
    # while allowing maintenance-only revisions to repair tooling, metadata, or source posture
    # without inventing a fake operational matrix relationship.
    current_substantive_numbers = {
        metadata_notes[current_file].get("number")
        for current_file in CURRENT_NOTES
        if metadata_notes.get(current_file, {}).get("note_class") in {"policy_docket", "applied_case_packet"}
    }
    current_substantive_numbers.discard(None)
    current_matrix_matches = []
    if current_substantive_numbers:
        for spec in COMMON_TEST_MATRICES:
            matrix_path = METADATA_DIR / spec["metadata_filename"]
            if not matrix_path.exists():
                continue
            matrix_payload = load_json(matrix_path)
            matrix_notes = set(matrix_payload.get("source_notes", []))
            if current_substantive_numbers.issubset(matrix_notes):
                current_matrix_matches.append(spec["metadata_filename"])
        if not current_matrix_matches:
            fail(
                f"current substantive revision notes lack a registered operational test matrix covering "
                f"note numbers {sorted(current_substantive_numbers)}"
            )
    current_applied_numbers = {
        metadata_notes[current_file].get("number")
        for current_file in CURRENT_NOTES
        if metadata_notes.get(current_file, {}).get("note_class") == "applied_case_packet"
    }
    current_applied_numbers.discard(None)
    if current_applied_numbers:
        for matrix_filename in current_matrix_matches:
            matrix_payload = load_json(METADATA_DIR / matrix_filename)
            for test_id, test in matrix_payload.get("tests", {}).items():
                examples = set(test.get("case_examples", []))
                missing_examples = sorted(current_applied_numbers - examples)
                if missing_examples:
                    fail(
                        f"current revision test matrix {matrix_filename} test {test_id} "
                        f"does not cite current applied case example(s): {missing_examples}"
                    )

    generated_sources = load_json(GENERATED / "SOURCES.json")
    if generated_sources.get("revision") != CURRENT_REV:
        fail(f"generated/SOURCES.json revision mismatch: expected {CURRENT_REV}")
    if generated_sources.get("source_catalog") != "sources/source_catalog.json":
        fail("generated/SOURCES.json does not identify canonical source catalog")
    if generated_sources.get("source_key_registry") != "sources/source_keys.json":
        fail("generated/SOURCES.json does not identify canonical source key registry")
    if set(generated_sources.get("source_keys", {})) != set(source_key_registry):
        fail("generated/SOURCES.json source key registry mismatch")
    if generated_sources.get("source_scope") != "current_revision_route_and_registry_snapshot":
        fail("generated/SOURCES.json must stay scoped to the current revision route and source-key registry snapshot")
    counts = generated_sources.get("counts", {})
    if counts.get("source_key_registry_keys") != len(source_key_registry):
        fail("generated/SOURCES.json source-key count does not match registry")
    if counts.get("historical_notes_with_source_rows") != len(source_notes):
        fail("generated/SOURCES.json historical source-row count does not match canonical catalog")
    if counts.get("current_revision_notes") != len(CURRENT_NOTES):
        fail("generated/SOURCES.json current revision note count mismatch")
    for hash_field in ["catalog_sha256", "source_key_registry_sha256"]:
        hash_value = generated_sources.get(hash_field)
        if not isinstance(hash_value, str) or not re.fullmatch(r"[0-9a-f]{64}", hash_value):
            fail(f"generated/SOURCES.json missing valid {hash_field}")
    current_generated_notes = generated_sources.get("notes", {})
    if set(current_generated_notes) != set(CURRENT_NOTES):
        fail("generated/SOURCES.json notes must contain exactly the current revision route")
    if generated_sources.get("current_notes") != CURRENT_NOTES:
        fail("generated/SOURCES.json current_notes does not match INDEX current revision notes")
    for rel in CURRENT_NOTES:
        validate_source_groups(current_generated_notes, rel, "generated/SOURCES.json")

    archive_index = load_json(GENERATED / "ARCHIVE_INDEX.json")
    if archive_index.get("revision") != CURRENT_REV:
        fail(f"generated/ARCHIVE_INDEX.json revision mismatch: expected {CURRENT_REV}")
    indexed_files = [entry.get("file") for entry in archive_index.get("notes", [])]
    if indexed_files != expected_files:
        fail("generated/ARCHIVE_INDEX.json note list does not match archive directory order")
    archive_by_file = {entry.get("file"): entry for entry in archive_index.get("notes", [])}
    for required in CURRENT_NOTES:
        entry = archive_by_file.get(required)
        if not entry:
            fail(f"generated/ARCHIVE_INDEX.json missing current note entry: {required}")
        for field in ["thesis", "tags", "note_class", "status", "canon_role"]:
            if not entry.get(field):
                fail(f"generated/ARCHIVE_INDEX.json current note missing {field}: {required}")

    note_status = load_json(GENERATED / "NOTE_STATUS.json")
    if note_status.get("revision") != CURRENT_REV:
        fail(f"generated/NOTE_STATUS.json revision mismatch: expected {CURRENT_REV}")
    for front_key, front_target in note_status.get("front_door", {}).items():
        if not isinstance(front_target, str) or not front_target.strip():
            fail(f"generated/NOTE_STATUS.json front_door has invalid target for {front_key}")
        if not (ROOT / front_target).exists():
            fail(f"generated/NOTE_STATUS.json front-door target missing for {front_key}: {front_target}")

    for front_key in ["pocket_answer", "long_answer", "operating_canon", "cross_boundary_dispatcher", "applied_thick_case", "applied_thin_case", "applied_middle_case", "applied_asset_case", "applied_contract_case", "applied_regulatory_case", "applied_treaty_global_case", "waist_capture_lens", "claim_ledger_policy", "applied_procedural_digital_case", "supplier_dependency_lens", "cross_boundary_manual", "negative_control_policy", "applied_soft_law_case", "applied_database_alert_case", "plural_order_lens", "applied_plural_order_case", "applied_supplier_dependency_case", "supplier_dependency_review_policy", "municipal_distress_handback_policy", "applied_municipal_handback_case", "symbolic_authority_policy", "applied_symbolic_authority_case", "capacity_floor_policy", "applied_fragile_capacity_case", "model_decision_policy", "applied_model_decision_case", "generative_assistant_policy", "applied_generative_assistant_mycity_case", "applied_generative_assistant_govuk_chat_case", "staff_copilot_policy", "applied_staff_copilot_redbox_case", "applied_staff_copilot_dfe_correspondence_case", "applied_staff_copilot_ico_ice360_case", "applied_staff_triage_dwp_whitemail_case", "transition_receipt_policy", "applied_transition_receipt_arrivecan_case", "applied_transition_receipt_mycity_case", "platform_migration_policy", "applied_platform_migration_phoenix_dayforce_case", "applied_platform_migration_evisa_case", "ecological_personhood_policy", "applied_ecological_personhood_atrato_case", "applied_ecological_personhood_mar_menor_case", "applied_ecological_personhood_ganga_yamuna_case", "entitlement_continuity_policy", "applied_entitlement_continuity_medicaid_case", "applied_entitlement_continuity_universal_credit_case", "payment_redress_policy", "applied_payment_redress_postoffice_horizon_case", "applied_payment_redress_infected_blood_case", "applied_payment_refund_erc_case", "credential_access_policy", "applied_credential_access_logingov_case", "applied_credential_access_irs_idme_case", "applied_credential_access_onelogin_case", "representative_access_policy", "applied_representative_access_ssa_payee_case", "applied_representative_access_uk_appointee_case", "applied_representative_access_irs_taxpro_case", "applied_representative_access_health_appeal_case", "cloudtainer_source_health_policy", "disaster_assistance_policy", "applied_disaster_assistance_fema_ia_case", "unemployment_insurance_integrity_access_policy", "applied_unemployment_insurance_pandemic_ui_case", "watchlist_border_automation_policy", "applied_watchlist_border_us_case", "public_ai_register_policy", "applied_public_ai_register_case", "subnational_ai_policy", "applied_subnational_ai_case", "global_south_source_policy", "applied_global_south_source_case", "transition_receipt_tests", "platform_migration_tests", "ecological_personhood_tests", "entitlement_continuity_tests", "payment_redress_tests", "credential_access_tests", "representative_access_tests", "disaster_assistance_tests", "unemployment_insurance_tests", "watchlist_border_tests", "public_ai_register_tests", "subnational_ai_tests", "global_south_source_tests", "source_health", "gap_ledger", "generated_surface_audit", "symbolic_authority_tests", "capacity_tests", "model_decision_tests", "generative_assistant_tests", "staff_copilot_tests", "case_packet_matrix", "retirement_candidates", "claim_ledger", "defeat_tests", "handback_tests", "supplier_dependency_tests", "cross_boundary_consolidation_audit"]:
        if not note_status.get("front_door", {}).get(front_key):
            fail(f"generated/NOTE_STATUS.json front_door missing {front_key}")
    for required in CURRENT_NOTES:
        if required not in note_status.get("notes", {}):
            fail(f"generated/NOTE_STATUS.json missing current note entry: {required}")
        current_status = note_status["notes"][required]
        for field in ["note_class", "status", "canon_role"]:
            if not current_status.get(field):
                fail(f"generated/NOTE_STATUS.json current note missing {field}: {required}")

    front_targets = set(note_status.get("front_door", {}).values())
    reverse_metadata_refs: dict[int, list[str]] = {}
    for ref_file, ref_meta in metadata_notes.items():
        for ref_number in ref_meta.get("depends_on", []) + ref_meta.get("reserved_notes", []):
            reverse_metadata_refs.setdefault(ref_number, []).append(ref_file)
        dispatcher_number = ref_meta.get("dispatcher")
        if dispatcher_number is not None:
            reverse_metadata_refs.setdefault(dispatcher_number, []).append(ref_file)
    for file, meta in metadata_notes.items():
        if meta.get("status") != "historical_preserved":
            continue
        note_number = meta.get("number")
        if file in CURRENT_NOTES:
            fail(f"historical_preserved note cannot be a current revision note: {file}")
        if meta.get("first_citation"):
            fail(f"historical_preserved note cannot remain first_citation: {file}")
        if file in front_targets:
            fail(f"historical_preserved note cannot remain a front-door target: {file}")
        if note_number in reverse_metadata_refs:
            fail(f"historical_preserved note still has active metadata references: {file} <- {reverse_metadata_refs[note_number]}")
        review = meta.get("retirement_review")
        if not isinstance(review, dict):
            fail(f"historical_preserved note missing retirement_review: {file}")
        for field in ["revision", "review_note", "review_status", "reason", "preservation_policy", "successor_or_supporting_routes", "rollback_condition"]:
            if field not in review or review[field] in (None, "", []):
                fail(f"historical_preserved note {file} retirement_review missing {field}")
        if review.get("revision") != CURRENT_REV:
            fail(f"historical_preserved note {file} retirement_review revision should be {CURRENT_REV}")
        if review.get("review_note") not in numbers:
            fail(f"historical_preserved note {file} review_note unknown: {review.get('review_note')}")
        for supporting_note in review.get("successor_or_supporting_routes", []):
            if supporting_note not in numbers:
                fail(f"historical_preserved note {file} successor/supporting route unknown: {supporting_note}")
        status_entry = note_status.get("notes", {}).get(file, {})
        if status_entry.get("status") != "historical_preserved":
            fail(f"generated/NOTE_STATUS.json did not preserve historical_preserved status for {file}")

    # Current-revision policy and applied-case canon roles must be routable from the front-door map.
    # This catches a real drift mode: a new substantive packet can otherwise pass lint while NOTE_STATUS lacks its canonical entry.
    for current_file in CURRENT_NOTES:
        current_meta = metadata_notes.get(current_file, {})
        if current_meta.get("note_class") in {"policy_docket", "applied_case_packet"}:
            role = current_meta.get("canon_role")
            if not isinstance(role, str) or not role.strip():
                fail(f"current note missing canon_role for front-door check: {current_file}")
            actual_front = note_status.get("front_door", {}).get(role)
            if actual_front != current_file:
                fail(f"generated/NOTE_STATUS.json front_door for current canon_role {role} should be {current_file}, got {actual_front}")

    # Current-revision substantive packets must not pass with only note metadata.
    # Policy dockets need claim-ledger coverage; applied case packets also need case-matrix coverage.
    current_substantive_files = {
        file
        for file in CURRENT_NOTES
        if metadata_notes.get(file, {}).get("note_class") in {"policy_docket", "applied_case_packet"}
    }
    current_claim_files = {claim.get("note_file") for claim in load_json(METADATA_DIR / "claims.json").get("claims", {}).values()}
    missing_current_claims = sorted(current_substantive_files - current_claim_files)
    if missing_current_claims:
        fail(f"current substantive note missing claim-ledger entry: {missing_current_claims}")

    claims_header_current = set(load_json(METADATA_DIR / "claims.json").get("current_note_files", []))
    if claims_header_current != current_substantive_files:
        fail(
            f"metadata/claims.json current_note_files should exactly match current substantive notes: "
            f"metadata_only={sorted(claims_header_current - current_substantive_files)} "
            f"missing={sorted(current_substantive_files - claims_header_current)}"
        )

    case_packets = load_json(METADATA_DIR / "case_packets.json")
    if case_packets.get("schema") != "radical-governance-case-packets-v1":
        fail("metadata/case_packets.json missing expected schema")
    if case_packets.get("revision") != CURRENT_REV:
        fail(f"metadata/case_packets.json revision mismatch: expected {CURRENT_REV}")
    case_files = []
    for case_id, case in case_packets.get("cases", {}).items():
        file = case.get("file")
        if file not in expected_files:
            fail(f"metadata/case_packets.json case file missing from archive: {case_id} {file}")
        if file not in metadata_notes:
            fail(f"metadata/case_packets.json case file missing metadata: {file}")
        case_files.append(file)
        for field in ["case_label", "form_verdict", "form_family", "thickness", "live_chain_notes", "reserved_notes", "repair_surfaces", "source_keys"]:
            if not case.get(field):
                fail(f"metadata/case_packets.json case {case_id} missing {field}")
        for note_number in case.get("live_chain_notes", []) + case.get("reserved_notes", []):
            if note_number not in numbers:
                fail(f"metadata/case_packets.json case {case_id} references unknown chain note {note_number}")
        for key in case.get("source_keys", []):
            if key not in source_key_registry:
                fail(f"metadata/case_packets.json case {case_id} references unknown source_key {key}")
    current_applied_case_files = {
        file
        for file in CURRENT_NOTES
        if metadata_notes.get(file, {}).get("note_class") == "applied_case_packet"
    }
    missing_current_case_files = sorted(current_applied_case_files - set(case_files))
    if missing_current_case_files:
        fail(f"metadata/case_packets.json missing current applied-case note(s): {missing_current_case_files}")

    claims_meta = load_json(METADATA_DIR / "claims.json")
    if claims_meta.get("schema") != "radical-governance-claims-v1":
        fail("metadata/claims.json missing expected schema")
    if claims_meta.get("revision") != CURRENT_REV:
        fail(f"metadata/claims.json revision mismatch: expected {CURRENT_REV}")
    claim_status_labels = set(claims_meta.get("status_labels", {}))
    claim_currentness_labels = set(claims_meta.get("currentness_labels", {}))
    if not claim_status_labels or not claim_currentness_labels:
        fail("metadata/claims.json missing status or currentness labels")
    for current_file in claims_meta.get("current_note_files", []):
        if current_file not in expected_files:
            fail(f"metadata/claims.json current_note_files references unknown archive file: {current_file}")
    for claim_id, claim in claims_meta.get("claims", {}).items():
        note_file = claim.get("note_file")
        if note_file not in expected_files:
            fail(f"metadata/claims.json claim {claim_id} references unknown archive file: {note_file}")
        if claim.get("claim_status") not in claim_status_labels:
            fail(f"metadata/claims.json claim {claim_id} has unknown claim_status: {claim.get('claim_status')}")
        if claim.get("currentness") not in claim_currentness_labels:
            fail(f"metadata/claims.json claim {claim_id} has unknown currentness: {claim.get('currentness')}")
        for field in ["claim_text", "evidence_type", "opposition_brief", "falsifier", "review_clock"]:
            if not isinstance(claim.get(field), str) or not claim[field].strip():
                fail(f"metadata/claims.json claim {claim_id} missing {field}")
        for field in ["affected_parties", "capture_channels", "source_keys"]:
            if not isinstance(claim.get(field), list):
                fail(f"metadata/claims.json claim {claim_id} field {field} is not a list")
        for key in claim.get("source_keys", []):
            if key not in source_key_registry:
                fail(f"metadata/claims.json claim {claim_id} references unknown source_key {key}")

    # Current-revision claim and case-packet rows must use the same source-key set as
    # current note metadata. This catches fresh-packet drift where a copied claim or
    # case row silently carries stale source keys even though note metadata and the
    # source catalog are correct.
    for current_file in current_substantive_files:
        expected_source_keys = set(metadata_notes.get(current_file, {}).get("source_keys", []))
        matching_claims = [
            (claim_id, claim)
            for claim_id, claim in claims_meta.get("claims", {}).items()
            if claim.get("note_file") == current_file
        ]
        for claim_id, claim in matching_claims:
            actual_source_keys = set(claim.get("source_keys", []))
            if actual_source_keys != expected_source_keys:
                fail(
                    f"metadata/claims.json claim {claim_id} source keys do not match note metadata for {current_file}: "
                    f"metadata_only={sorted(expected_source_keys - actual_source_keys)} "
                    f"claim_only={sorted(actual_source_keys - expected_source_keys)}"
                )
    for case_id, case in case_packets.get("cases", {}).items():
        file = case.get("file")
        if file in current_applied_case_files:
            expected_source_keys = set(metadata_notes.get(file, {}).get("source_keys", []))
            actual_source_keys = set(case.get("source_keys", []))
            if actual_source_keys != expected_source_keys:
                fail(
                    f"metadata/case_packets.json case {case_id} source keys do not match note metadata for {file}: "
                    f"metadata_only={sorted(expected_source_keys - actual_source_keys)} "
                    f"case_only={sorted(actual_source_keys - expected_source_keys)}"
                )

    generated_claims = load_json(GENERATED / "CLAIMS.json")
    if generated_claims.get("revision") != CURRENT_REV:
        fail(f"generated/CLAIMS.json revision mismatch: expected {CURRENT_REV}")
    if generated_claims.get("claim_count") != len(claims_meta.get("claims", {})):
        fail("generated/CLAIMS.json claim count mismatch metadata/claims.json")
    generated_claim_ids = {claim.get("claim_id") for claim in generated_claims.get("claims", [])}
    if generated_claim_ids != set(claims_meta.get("claims", {})):
        fail("generated/CLAIMS.json claim ids mismatch metadata/claims.json")

    defeat_tests = load_json(METADATA_DIR / "defeat_tests.json")
    if defeat_tests.get("schema") != "radical-governance-defeat-tests-v1":
        fail("metadata/defeat_tests.json missing expected schema")
    if defeat_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/defeat_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in defeat_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/defeat_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in defeat_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/defeat_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/defeat_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/defeat_tests.json test {test_id} references unknown related note {note_number}")
    generated_defeat_tests = load_json(GENERATED / "DEFEAT_TESTS.json")
    if generated_defeat_tests.get("revision") != CURRENT_REV:
        fail(f"generated/DEFEAT_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_defeat_tests.get("test_count") != len(defeat_tests.get("tests", {})):
        fail("generated/DEFEAT_TESTS.json test count mismatch metadata/defeat_tests.json")
    generated_defeat_ids = {test.get("test_id") for test in generated_defeat_tests.get("tests", [])}
    if generated_defeat_ids != set(defeat_tests.get("tests", {})):
        fail("generated/DEFEAT_TESTS.json test ids mismatch metadata/defeat_tests.json")

    handback_tests = load_json(METADATA_DIR / "handback_tests.json")
    if handback_tests.get("schema") != "radical-governance-handback-tests-v1":
        fail("metadata/handback_tests.json missing expected schema")
    if handback_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/handback_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in handback_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/handback_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in handback_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/handback_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/handback_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/handback_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/handback_tests.json test {test_id} references unknown case example {note_number}")
    generated_handback_tests = load_json(GENERATED / "HANDBACK_TESTS.json")
    if generated_handback_tests.get("revision") != CURRENT_REV:
        fail(f"generated/HANDBACK_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_handback_tests.get("test_count") != len(handback_tests.get("tests", {})):
        fail("generated/HANDBACK_TESTS.json test count mismatch metadata/handback_tests.json")
    generated_handback_ids = {test.get("test_id") for test in generated_handback_tests.get("tests", [])}
    if generated_handback_ids != set(handback_tests.get("tests", {})):
        fail("generated/HANDBACK_TESTS.json test ids mismatch metadata/handback_tests.json")

    supplier_dependency_tests = load_json(METADATA_DIR / "supplier_dependency_tests.json")
    if supplier_dependency_tests.get("schema") != "radical-governance-supplier-dependency-tests-v1":
        fail("metadata/supplier_dependency_tests.json missing expected schema")
    if supplier_dependency_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/supplier_dependency_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in supplier_dependency_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/supplier_dependency_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in supplier_dependency_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/supplier_dependency_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/supplier_dependency_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/supplier_dependency_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/supplier_dependency_tests.json test {test_id} references unknown case example {note_number}")
    generated_supplier_dependency_tests = load_json(GENERATED / "SUPPLIER_DEPENDENCY_TESTS.json")
    if generated_supplier_dependency_tests.get("revision") != CURRENT_REV:
        fail(f"generated/SUPPLIER_DEPENDENCY_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_supplier_dependency_tests.get("test_count") != len(supplier_dependency_tests.get("tests", {})):
        fail("generated/SUPPLIER_DEPENDENCY_TESTS.json test count mismatch metadata/supplier_dependency_tests.json")
    generated_supplier_dependency_ids = {test.get("test_id") for test in generated_supplier_dependency_tests.get("tests", [])}
    if generated_supplier_dependency_ids != set(supplier_dependency_tests.get("tests", {})):
        fail("generated/SUPPLIER_DEPENDENCY_TESTS.json test ids mismatch metadata/supplier_dependency_tests.json")

    symbolic_authority_tests = load_json(METADATA_DIR / "symbolic_authority_tests.json")
    if symbolic_authority_tests.get("schema") != "radical-governance-symbolic-authority-tests-v1":
        fail("metadata/symbolic_authority_tests.json missing expected schema")
    if symbolic_authority_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/symbolic_authority_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in symbolic_authority_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/symbolic_authority_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in symbolic_authority_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/symbolic_authority_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/symbolic_authority_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/symbolic_authority_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/symbolic_authority_tests.json test {test_id} references unknown case example {note_number}")
    generated_symbolic_authority_tests = load_json(GENERATED / "SYMBOLIC_AUTHORITY_TESTS.json")
    if generated_symbolic_authority_tests.get("revision") != CURRENT_REV:
        fail(f"generated/SYMBOLIC_AUTHORITY_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_symbolic_authority_tests.get("test_count") != len(symbolic_authority_tests.get("tests", {})):
        fail("generated/SYMBOLIC_AUTHORITY_TESTS.json test count mismatch metadata/symbolic_authority_tests.json")
    generated_symbolic_authority_ids = {test.get("test_id") for test in generated_symbolic_authority_tests.get("tests", [])}
    if generated_symbolic_authority_ids != set(symbolic_authority_tests.get("tests", {})):
        fail("generated/SYMBOLIC_AUTHORITY_TESTS.json test ids mismatch metadata/symbolic_authority_tests.json")

    capacity_tests = load_json(METADATA_DIR / "capacity_tests.json")
    if capacity_tests.get("schema") != "radical-governance-capacity-tests-v1":
        fail("metadata/capacity_tests.json missing expected schema")
    if capacity_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/capacity_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in capacity_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/capacity_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in capacity_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/capacity_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/capacity_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/capacity_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/capacity_tests.json test {test_id} references unknown case example {note_number}")
    generated_capacity_tests = load_json(GENERATED / "CAPACITY_TESTS.json")
    if generated_capacity_tests.get("revision") != CURRENT_REV:
        fail(f"generated/CAPACITY_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_capacity_tests.get("test_count") != len(capacity_tests.get("tests", {})):
        fail("generated/CAPACITY_TESTS.json test count mismatch metadata/capacity_tests.json")
    generated_capacity_ids = {test.get("test_id") for test in generated_capacity_tests.get("tests", [])}
    if generated_capacity_ids != set(capacity_tests.get("tests", {})):
        fail("generated/CAPACITY_TESTS.json test ids mismatch metadata/capacity_tests.json")

    model_decision_tests = load_json(METADATA_DIR / "model_decision_tests.json")
    if model_decision_tests.get("schema") != "radical-governance-model-decision-tests-v1":
        fail("metadata/model_decision_tests.json missing expected schema")
    if model_decision_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/model_decision_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in model_decision_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/model_decision_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in model_decision_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/model_decision_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/model_decision_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/model_decision_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/model_decision_tests.json test {test_id} references unknown case example {note_number}")
    generated_model_decision_tests = load_json(GENERATED / "MODEL_DECISION_TESTS.json")
    if generated_model_decision_tests.get("revision") != CURRENT_REV:
        fail(f"generated/MODEL_DECISION_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_model_decision_tests.get("test_count") != len(model_decision_tests.get("tests", {})):
        fail("generated/MODEL_DECISION_TESTS.json test count mismatch metadata/model_decision_tests.json")
    generated_model_decision_ids = {test.get("test_id") for test in generated_model_decision_tests.get("tests", [])}
    if generated_model_decision_ids != set(model_decision_tests.get("tests", {})):
        fail("generated/MODEL_DECISION_TESTS.json test ids mismatch metadata/model_decision_tests.json")

    generative_assistant_tests = load_json(METADATA_DIR / "generative_assistant_tests.json")
    if generative_assistant_tests.get("schema") != "radical-governance-generative-assistant-tests-v1":
        fail("metadata/generative_assistant_tests.json missing expected schema")
    if generative_assistant_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/generative_assistant_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in generative_assistant_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/generative_assistant_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in generative_assistant_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/generative_assistant_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/generative_assistant_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/generative_assistant_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/generative_assistant_tests.json test {test_id} references unknown case example {note_number}")
    generated_generative_assistant_tests = load_json(GENERATED / "GENERATIVE_ASSISTANT_TESTS.json")
    if generated_generative_assistant_tests.get("revision") != CURRENT_REV:
        fail(f"generated/GENERATIVE_ASSISTANT_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_generative_assistant_tests.get("test_count") != len(generative_assistant_tests.get("tests", {})):
        fail("generated/GENERATIVE_ASSISTANT_TESTS.json test count mismatch metadata/generative_assistant_tests.json")
    generated_generative_assistant_ids = {test.get("test_id") for test in generated_generative_assistant_tests.get("tests", [])}
    if generated_generative_assistant_ids != set(generative_assistant_tests.get("tests", {})):
        fail("generated/GENERATIVE_ASSISTANT_TESTS.json test ids mismatch metadata/generative_assistant_tests.json")

    staff_copilot_tests = load_json(METADATA_DIR / "staff_copilot_tests.json")
    if staff_copilot_tests.get("schema") != "radical-governance-staff-copilot-tests-v1":
        fail("metadata/staff_copilot_tests.json missing expected schema")
    if staff_copilot_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/staff_copilot_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in staff_copilot_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/staff_copilot_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in staff_copilot_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/staff_copilot_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/staff_copilot_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/staff_copilot_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/staff_copilot_tests.json test {test_id} references unknown case example {note_number}")
    generated_staff_copilot_tests = load_json(GENERATED / "STAFF_COPILOT_TESTS.json")
    if generated_staff_copilot_tests.get("revision") != CURRENT_REV:
        fail(f"generated/STAFF_COPILOT_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_staff_copilot_tests.get("test_count") != len(staff_copilot_tests.get("tests", {})):
        fail("generated/STAFF_COPILOT_TESTS.json test count mismatch metadata/staff_copilot_tests.json")
    generated_staff_copilot_ids = {test.get("test_id") for test in generated_staff_copilot_tests.get("tests", [])}
    if generated_staff_copilot_ids != set(staff_copilot_tests.get("tests", {})):
        fail("generated/STAFF_COPILOT_TESTS.json test ids mismatch metadata/staff_copilot_tests.json")

    transition_receipt_tests = load_json(METADATA_DIR / "transition_receipt_tests.json")
    if transition_receipt_tests.get("schema") != "radical-governance-transition-receipt-tests-v1":
        fail("metadata/transition_receipt_tests.json missing expected schema")
    if transition_receipt_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/transition_receipt_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in transition_receipt_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/transition_receipt_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in transition_receipt_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/transition_receipt_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/transition_receipt_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/transition_receipt_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/transition_receipt_tests.json test {test_id} references unknown case example {note_number}")
    generated_transition_receipt_tests = load_json(GENERATED / "TRANSITION_RECEIPT_TESTS.json")
    if generated_transition_receipt_tests.get("revision") != CURRENT_REV:
        fail(f"generated/TRANSITION_RECEIPT_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_transition_receipt_tests.get("test_count") != len(transition_receipt_tests.get("tests", {})):
        fail("generated/TRANSITION_RECEIPT_TESTS.json test count mismatch metadata/transition_receipt_tests.json")
    generated_transition_receipt_ids = {test.get("test_id") for test in generated_transition_receipt_tests.get("tests", [])}
    if generated_transition_receipt_ids != set(transition_receipt_tests.get("tests", {})):
        fail("generated/TRANSITION_RECEIPT_TESTS.json test ids mismatch metadata/transition_receipt_tests.json")

    platform_migration_tests = load_json(METADATA_DIR / "platform_migration_tests.json")
    if platform_migration_tests.get("schema") != "radical-governance-platform-migration-tests-v1":
        fail("metadata/platform_migration_tests.json missing expected schema")
    if platform_migration_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/platform_migration_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in platform_migration_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/platform_migration_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in platform_migration_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/platform_migration_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/platform_migration_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/platform_migration_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/platform_migration_tests.json test {test_id} references unknown case example {note_number}")
    generated_platform_migration_tests = load_json(GENERATED / "PLATFORM_MIGRATION_TESTS.json")
    if generated_platform_migration_tests.get("revision") != CURRENT_REV:
        fail(f"generated/PLATFORM_MIGRATION_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_platform_migration_tests.get("test_count") != len(platform_migration_tests.get("tests", {})):
        fail("generated/PLATFORM_MIGRATION_TESTS.json test count mismatch metadata/platform_migration_tests.json")
    generated_platform_migration_ids = {test.get("test_id") for test in generated_platform_migration_tests.get("tests", [])}
    if generated_platform_migration_ids != set(platform_migration_tests.get("tests", {})):
        fail("generated/PLATFORM_MIGRATION_TESTS.json test ids mismatch metadata/platform_migration_tests.json")

    ecological_personhood_tests = load_json(METADATA_DIR / "ecological_personhood_tests.json")
    if ecological_personhood_tests.get("schema") != "radical-governance-ecological-personhood-tests-v1":
        fail("metadata/ecological_personhood_tests.json missing expected schema")
    if ecological_personhood_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/ecological_personhood_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in ecological_personhood_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/ecological_personhood_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in ecological_personhood_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/ecological_personhood_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/ecological_personhood_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/ecological_personhood_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/ecological_personhood_tests.json test {test_id} references unknown case example {note_number}")
    generated_ecological_personhood_tests = load_json(GENERATED / "ECOLOGICAL_PERSONHOOD_TESTS.json")
    if generated_ecological_personhood_tests.get("revision") != CURRENT_REV:
        fail(f"generated/ECOLOGICAL_PERSONHOOD_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_ecological_personhood_tests.get("test_count") != len(ecological_personhood_tests.get("tests", {})):
        fail("generated/ECOLOGICAL_PERSONHOOD_TESTS.json test count mismatch metadata/ecological_personhood_tests.json")
    generated_ecological_personhood_ids = {test.get("test_id") for test in generated_ecological_personhood_tests.get("tests", [])}
    if generated_ecological_personhood_ids != set(ecological_personhood_tests.get("tests", {})):
        fail("generated/ECOLOGICAL_PERSONHOOD_TESTS.json test ids mismatch metadata/ecological_personhood_tests.json")

    entitlement_continuity_tests = load_json(METADATA_DIR / "entitlement_continuity_tests.json")
    if entitlement_continuity_tests.get("schema") != "radical-governance-entitlement-continuity-tests-v1":
        fail("metadata/entitlement_continuity_tests.json missing expected schema")
    if entitlement_continuity_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/entitlement_continuity_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in entitlement_continuity_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/entitlement_continuity_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in entitlement_continuity_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/entitlement_continuity_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/entitlement_continuity_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/entitlement_continuity_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/entitlement_continuity_tests.json test {test_id} references unknown case example {note_number}")
    generated_entitlement_continuity_tests = load_json(GENERATED / "ENTITLEMENT_CONTINUITY_TESTS.json")
    if generated_entitlement_continuity_tests.get("revision") != CURRENT_REV:
        fail(f"generated/ENTITLEMENT_CONTINUITY_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_entitlement_continuity_tests.get("test_count") != len(entitlement_continuity_tests.get("tests", {})):
        fail("generated/ENTITLEMENT_CONTINUITY_TESTS.json test count mismatch metadata/entitlement_continuity_tests.json")
    generated_entitlement_continuity_ids = {test.get("test_id") for test in generated_entitlement_continuity_tests.get("tests", [])}
    if generated_entitlement_continuity_ids != set(entitlement_continuity_tests.get("tests", {})):
        fail("generated/ENTITLEMENT_CONTINUITY_TESTS.json test ids mismatch metadata/entitlement_continuity_tests.json")


    payment_redress_tests = load_json(METADATA_DIR / "payment_redress_tests.json")
    if payment_redress_tests.get("schema") != "radical-governance-payment-redress-tests-v1":
        fail("metadata/payment_redress_tests.json missing expected schema")
    if payment_redress_tests.get("revision") != CURRENT_REV:
        fail(f"metadata/payment_redress_tests.json revision mismatch: expected {CURRENT_REV}")
    for note_number in payment_redress_tests.get("source_notes", []):
        if note_number not in numbers:
            fail(f"metadata/payment_redress_tests.json source_notes references unknown note number {note_number}")
    for test_id, test in payment_redress_tests.get("tests", {}).items():
        for field in ["label", "question", "fail_or_repair"]:
            if not isinstance(test.get(field), str) or not test[field].strip():
                fail(f"metadata/payment_redress_tests.json test {test_id} missing {field}")
        for field in ["pass_evidence", "activated_by", "related_notes"]:
            if not isinstance(test.get(field), list) or not test[field]:
                fail(f"metadata/payment_redress_tests.json test {test_id} missing non-empty {field}")
        for note_number in test.get("related_notes", []):
            if note_number not in numbers:
                fail(f"metadata/payment_redress_tests.json test {test_id} references unknown related note {note_number}")
        for note_number in test.get("case_examples", []):
            if note_number not in numbers:
                fail(f"metadata/payment_redress_tests.json test {test_id} references unknown case example {note_number}")
    generated_payment_redress_tests = load_json(GENERATED / "PAYMENT_REDRESS_TESTS.json")
    if generated_payment_redress_tests.get("revision") != CURRENT_REV:
        fail(f"generated/PAYMENT_REDRESS_TESTS.json revision mismatch: expected {CURRENT_REV}")
    if generated_payment_redress_tests.get("test_count") != len(payment_redress_tests.get("tests", {})):
        fail("generated/PAYMENT_REDRESS_TESTS.json test count mismatch metadata/payment_redress_tests.json")
    generated_payment_redress_ids = {test.get("test_id") for test in generated_payment_redress_tests.get("tests", [])}
    if generated_payment_redress_ids != set(payment_redress_tests.get("tests", {})):
        fail("generated/PAYMENT_REDRESS_TESTS.json test ids mismatch metadata/payment_redress_tests.json")


    for spec in COMMON_TEST_MATRICES:
        validate_test_matrix_pair(
            spec["metadata_filename"],
            spec["schema_const"],
            f"{spec['output_stem']}.json",
            numbers,
        )

    case_matrix = load_json(GENERATED / "CASE_PACKET_MATRIX.json")
    if case_matrix.get("revision") != CURRENT_REV:
        fail(f"generated/CASE_PACKET_MATRIX.json revision mismatch: expected {CURRENT_REV}")
    if case_matrix.get("case_count") != len(case_packets.get("cases", {})):
        fail("generated/CASE_PACKET_MATRIX.json case count mismatch")
    matrix_files = [case.get("file") for case in case_matrix.get("cases", [])]
    if set(matrix_files) != set(case_files):
        fail("generated/CASE_PACKET_MATRIX.json case files mismatch metadata/case_packets.json")
    if not case_matrix.get("merge_guidance", {}).get("next_needed_tests"):
        fail("generated/CASE_PACKET_MATRIX.json missing next-needed merge guidance")


    consolidation_audit = load_json(GENERATED / "CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json")
    if consolidation_audit.get("revision") != CURRENT_REV:
        fail(f"generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json revision mismatch: expected {CURRENT_REV}")
    if consolidation_audit.get("case_count") != case_matrix.get("case_count"):
        fail("generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json case count mismatch with case matrix")
    if not consolidation_audit.get("chain_fields") or not consolidation_audit.get("consolidation_map"):
        fail("generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json missing chain fields or consolidation map")

    canon_map = load_json(GENERATED / "CANON_MAP.json")
    if canon_map.get("revision") != CURRENT_REV:
        fail(f"generated/CANON_MAP.json revision mismatch: expected {CURRENT_REV}")
    if canon_map.get("front_door", {}) != note_status.get("front_door", {}):
        fail("generated/CANON_MAP.json front door mismatch with NOTE_STATUS")
    for spec in COMMON_TEST_MATRICES:
        if not note_status.get("front_door", {}).get(spec["front_door_key"]):
            fail(f"generated/NOTE_STATUS.json front door missing common matrix key: {spec['front_door_key']}")
    if not canon_map.get("dispatcher_graph", {}).get("applied_cases"):
        fail("generated/CANON_MAP.json missing applied case graph")

    threads = (GENERATED / "THREADS.md").read_text(encoding="utf-8")
    for required in [
        "archive/448-governance-state-honesty-request-review-approval-and-live-separation.md",
        "archive/450-contemporaneous-decision-witnesses-what-was-shown-and-dispute-reconstruction.md",
    ]:
        if required not in archive_by_file:
            fail(f"archive metadata is missing rev0418 addition {required}")
    for required in CURRENT_NOTES:
        if Path(required).name not in threads:
            fail(f"generated/THREADS.md does not list current note {Path(required).name}")

    thread_summary = load_json(GENERATED / "THREAD_SUMMARY.json")
    if thread_summary.get("revision") != CURRENT_REV:
        fail(f"generated/THREAD_SUMMARY.json revision mismatch: expected {CURRENT_REV}")
    for tag in EXPECTED_THREAD_TAGS:
        if tag not in thread_summary.get("tags", {}):
            fail(f"generated/THREAD_SUMMARY.json missing expected tag: {tag}")
    for required in CURRENT_NOTES:
        entry = archive_by_file.get(required)
        tags = entry.get("tags", []) if entry else []
        if not any(thread_summary.get("tags", {}).get(tag, {}).get("latest_file") == required for tag in tags):
            fail(f"generated/THREAD_SUMMARY.json does not expose current note as latest_file for any of its tags: {required}")

    for filename, key, expected in [
        ("CONTROL_SURFACES.json", "surfaces", ["boundary-setting", "predeployment-evidence", "live-operations", "user-interaction", "evidence-and-redress", "supplier-and-ecosystem"]),
        ("ASSURANCE_ARTIFACTS.json", "artifacts", ["register", "notice", "log", "schedule", "waiver"]),
        ("LIFECYCLE_GATES.json", "gates", ["scoping-and-authority", "prelaunch-and-approval", "live-operation", "change-and-release", "redress-and-review", "retirement-and-continuity"]),
    ]:
        data = load_json(GENERATED / filename)
        if data.get("revision") != CURRENT_REV:
            fail(f"generated/{filename} revision mismatch: expected {CURRENT_REV}")
        for item in expected:
            if item not in data.get(key, {}):
                fail(f"generated/{filename} missing expected {key[:-1]}: {item}")


    surface_audit = load_json(GENERATED / "GENERATED_SURFACE_AUDIT.json")
    if surface_audit.get("revision") != CURRENT_REV:
        fail(f"generated/GENERATED_SURFACE_AUDIT.json revision mismatch: expected {CURRENT_REV}")
    surface_files = {entry.get("file") for entry in surface_audit.get("files", [])}
    if "generated/THREADS.md" not in surface_files:
        fail("generated/GENERATED_SURFACE_AUDIT.json does not include generated/THREADS.md")
    if surface_audit.get("generated_file_count", 0) < 1:
        fail("generated/GENERATED_SURFACE_AUDIT.json has no scanned files")

    releases = load_json(GENERATED / "RELEASES.json")
    if releases.get("revision") != CURRENT_REV:
        fail(f"generated/RELEASES.json revision mismatch: expected {CURRENT_REV}")
    rev_entry = next((item for item in releases.get("releases", []) if item.get("revision") == CURRENT_REV), None)
    if not rev_entry:
        fail("generated/RELEASES.json missing current revision entry")
    if sorted(rev_entry.get("notes", [])) != sorted(CURRENT_NOTES):
        fail("generated/RELEASES.json current revision note list mismatch")

    release_by_revision = {item.get("revision"): item for item in releases.get("releases", [])}

    def revision_number(revision: str) -> int:
        m = re.fullmatch(r"rev(\d{4})", revision or "")
        return int(m.group(1)) if m else -1

    recent_release_lineage_min_revision = 740
    archive_revisions = {
        entry.get("revision")
        for entry in archive_index.get("notes", [])
        if isinstance(entry.get("revision"), str)
        and revision_number(entry.get("revision")) >= recent_release_lineage_min_revision
    }
    release_revisions = {rev for rev in release_by_revision if isinstance(rev, str) and rev}
    missing_release_revisions = sorted(archive_revisions - release_revisions)
    if missing_release_revisions:
        fail(f"generated/RELEASES.json missing recent archive revision(s): {missing_release_revisions}")
    for revision in sorted(archive_revisions):
        expected_revision_notes = sorted(
            entry.get("file")
            for entry in archive_index.get("notes", [])
            if entry.get("revision") == revision
        )
        actual_revision_notes = sorted(release_by_revision.get(revision, {}).get("notes", []))
        if actual_revision_notes != expected_revision_notes:
            fail(
                f"generated/RELEASES.json note list mismatch for recent revision {revision}: "
                f"expected={expected_revision_notes} actual={actual_revision_notes}"
            )

    manifest = load_json(GENERATED / "MANIFEST.json")
    if manifest.get("revision") != CURRENT_REV:
        fail(f"generated/MANIFEST.json revision mismatch: expected {CURRENT_REV}")
    manifest_files = [entry["file"].split("/", 1)[-1] for entry in manifest.get("archive_notes", [])]
    if sorted(manifest_files) != [p.name for p in files]:
        fail("generated/MANIFEST.json archive note list does not match archive directory")
    for label in ["top_level_files", "source_files", "metadata_files", "schema_files", "generated_files", "archive_notes", "meta_notes", "tool_scripts"]:
        check_entries(manifest.get(label, []), label)
    top_names = {entry.get("file") for entry in manifest.get("top_level_files", [])}
    meta_names = {entry.get("file") for entry in manifest.get("meta_notes", [])}
    if top_names & meta_names:
        fail(f"generated/MANIFEST.json double-categorizes meta notes: {sorted(top_names & meta_names)}")
    if "MISSION.md" not in top_names:
        fail("generated/MANIFEST.json missing MISSION.md from top_level_files")
    manifest_section_files = {section: {entry.get("file") for entry in manifest.get(section, [])} for section in ["source_files", "metadata_files", "schema_files", "generated_files"]}
    for expected_file, section in [
        ("sources/source_catalog.json", "source_files"),
        ("sources/source_keys.json", "source_files"),
        ("metadata/note_metadata.json", "metadata_files"),
        ("metadata/case_packets.json", "metadata_files"),
        ("metadata/claims.json", "metadata_files"),
        ("metadata/defeat_tests.json", "metadata_files"),
        ("metadata/handback_tests.json", "metadata_files"),
        ("metadata/supplier_dependency_tests.json", "metadata_files"),
        ("metadata/symbolic_authority_tests.json", "metadata_files"),
        ("metadata/capacity_tests.json", "metadata_files"),
        ("metadata/model_decision_tests.json", "metadata_files"),
        ("metadata/generative_assistant_tests.json", "metadata_files"),
        ("metadata/staff_copilot_tests.json", "metadata_files"),
        ("metadata/transition_receipt_tests.json", "metadata_files"),
        ("metadata/platform_migration_tests.json", "metadata_files"),
        ("metadata/ecological_personhood_tests.json", "metadata_files"),
        ("metadata/entitlement_continuity_tests.json", "metadata_files"),
        ("metadata/payment_redress_tests.json", "metadata_files"),
        ("metadata/credential_access_tests.json", "metadata_files"),
        ("metadata/representative_access_tests.json", "metadata_files"),
        ("metadata/disaster_assistance_tests.json", "metadata_files"),
        ("metadata/unemployment_insurance_tests.json", "metadata_files"),
        ("metadata/watchlist_border_tests.json", "metadata_files"),
        ("metadata/public_ai_register_tests.json", "metadata_files"),
        ("metadata/subnational_ai_tests.json", "metadata_files"),
        ("metadata/source_health.json", "metadata_files"),
        ("metadata/gap_ledger.json", "metadata_files"),
        ("metadata/evidence_receipts.json", "metadata_files"),
        ("metadata/route_merge_packets.json", "metadata_files"),
        ("metadata/route_redirect_ledger.json", "metadata_files"),
        ("schema/note_metadata.schema.json", "schema_files"),
        ("schema/source_keys.schema.json", "schema_files"),
        ("schema/case_packets.schema.json", "schema_files"),
        ("schema/claims.schema.json", "schema_files"),
        ("schema/defeat_tests.schema.json", "schema_files"),
        ("schema/handback_tests.schema.json", "schema_files"),
        ("schema/supplier_dependency_tests.schema.json", "schema_files"),
        ("schema/symbolic_authority_tests.schema.json", "schema_files"),
        ("schema/capacity_tests.schema.json", "schema_files"),
        ("schema/model_decision_tests.schema.json", "schema_files"),
        ("schema/generative_assistant_tests.schema.json", "schema_files"),
        ("schema/staff_copilot_tests.schema.json", "schema_files"),
        ("schema/transition_receipt_tests.schema.json", "schema_files"),
        ("schema/platform_migration_tests.schema.json", "schema_files"),
        ("schema/ecological_personhood_tests.schema.json", "schema_files"),
        ("schema/entitlement_continuity_tests.schema.json", "schema_files"),
        ("schema/payment_redress_tests.schema.json", "schema_files"),
        ("schema/credential_access_tests.schema.json", "schema_files"),
        ("schema/representative_access_tests.schema.json", "schema_files"),
        ("schema/disaster_assistance_tests.schema.json", "schema_files"),
        ("schema/unemployment_insurance_tests.schema.json", "schema_files"),
        ("schema/watchlist_border_tests.schema.json", "schema_files"),
        ("schema/public_ai_register_tests.schema.json", "schema_files"),
        ("schema/subnational_ai_tests.schema.json", "schema_files"),
        ("schema/source_health.schema.json", "schema_files"),
        ("schema/gap_ledger.schema.json", "schema_files"),
        ("schema/route_redirect_ledger.schema.json", "schema_files"),
        ("schema/route_merge_packets.schema.json", "schema_files"),
        ("schema/source_catalog.schema.json", "schema_files"),
        ("schema/evidence_receipts.schema.json", "schema_files"),
        ("generated/NOTE_STATUS.json", "generated_files"),
        ("generated/CASE_PACKET_MATRIX.json", "generated_files"),
        ("generated/CASE_PACKET_MATRIX.md", "generated_files"),
        ("generated/CANON_MAP.json", "generated_files"),
        ("generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json", "generated_files"),
        ("generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.md", "generated_files"),
        ("generated/CLAIMS.json", "generated_files"),
        ("generated/CLAIMS.md", "generated_files"),
        ("generated/DEFEAT_TESTS.json", "generated_files"),
        ("generated/DEFEAT_TESTS.md", "generated_files"),
        ("generated/HANDBACK_TESTS.json", "generated_files"),
        ("generated/HANDBACK_TESTS.md", "generated_files"),
        ("generated/SUPPLIER_DEPENDENCY_TESTS.json", "generated_files"),
        ("generated/SUPPLIER_DEPENDENCY_TESTS.md", "generated_files"),
        ("generated/SYMBOLIC_AUTHORITY_TESTS.json", "generated_files"),
        ("generated/SYMBOLIC_AUTHORITY_TESTS.md", "generated_files"),
        ("generated/CAPACITY_TESTS.json", "generated_files"),
        ("generated/CAPACITY_TESTS.md", "generated_files"),
        ("generated/MODEL_DECISION_TESTS.json", "generated_files"),
        ("generated/MODEL_DECISION_TESTS.md", "generated_files"),
        ("generated/GENERATIVE_ASSISTANT_TESTS.json", "generated_files"),
        ("generated/GENERATIVE_ASSISTANT_TESTS.md", "generated_files"),
        ("generated/STAFF_COPILOT_TESTS.json", "generated_files"),
        ("generated/STAFF_COPILOT_TESTS.md", "generated_files"),
        ("generated/TRANSITION_RECEIPT_TESTS.json", "generated_files"),
        ("generated/TRANSITION_RECEIPT_TESTS.md", "generated_files"),
        ("generated/PLATFORM_MIGRATION_TESTS.json", "generated_files"),
        ("generated/PLATFORM_MIGRATION_TESTS.md", "generated_files"),
        ("generated/ECOLOGICAL_PERSONHOOD_TESTS.json", "generated_files"),
        ("generated/ECOLOGICAL_PERSONHOOD_TESTS.md", "generated_files"),
        ("generated/ENTITLEMENT_CONTINUITY_TESTS.json", "generated_files"),
        ("generated/ENTITLEMENT_CONTINUITY_TESTS.md", "generated_files"),
        ("generated/PAYMENT_REDRESS_TESTS.json", "generated_files"),
        ("generated/PAYMENT_REDRESS_TESTS.md", "generated_files"),
        ("generated/EVIDENCE_RECEIPTS.json", "generated_files"),
        ("generated/EVIDENCE_RECEIPTS.md", "generated_files"),
        ("generated/CREDENTIAL_ACCESS_TESTS.json", "generated_files"),
        ("generated/CREDENTIAL_ACCESS_TESTS.md", "generated_files"),
        ("generated/REPRESENTATIVE_ACCESS_TESTS.json", "generated_files"),
        ("generated/REPRESENTATIVE_ACCESS_TESTS.md", "generated_files"),
        ("generated/DISASTER_ASSISTANCE_TESTS.json", "generated_files"),
        ("generated/DISASTER_ASSISTANCE_TESTS.md", "generated_files"),
        ("generated/UNEMPLOYMENT_INSURANCE_TESTS.json", "generated_files"),
        ("generated/UNEMPLOYMENT_INSURANCE_TESTS.md", "generated_files"),
        ("generated/WATCHLIST_BORDER_TESTS.json", "generated_files"),
        ("generated/WATCHLIST_BORDER_TESTS.md", "generated_files"),
        ("generated/PUBLIC_AI_REGISTER_TESTS.json", "generated_files"),
        ("generated/PUBLIC_AI_REGISTER_TESTS.md", "generated_files"),
        ("generated/SUBNATIONAL_AI_TESTS.json", "generated_files"),
        ("generated/SUBNATIONAL_AI_TESTS.md", "generated_files"),
        ("generated/GLOBAL_SOUTH_SOURCE_TESTS.json", "generated_files"),
        ("generated/GLOBAL_SOUTH_SOURCE_TESTS.md", "generated_files"),
        ("generated/SOURCE_HEALTH.json", "generated_files"),
        ("generated/SOURCE_HEALTH.md", "generated_files"),
        ("generated/GAP_LEDGER.json", "generated_files"),
        ("generated/GAP_LEDGER.md", "generated_files"),
        ("generated/GENERATED_SURFACE_AUDIT.json", "generated_files"),
        ("generated/GENERATED_SURFACE_AUDIT.md", "generated_files"),
    ]:
        if expected_file not in manifest_section_files.get(section, set()):
            fail(f"generated/MANIFEST.json missing {expected_file} in {section}")
    for spec in COMMON_TEST_MATRICES:
        for expected_file, section in [
            (f"metadata/{spec['metadata_filename']}", "metadata_files"),
            (f"schema/{spec['metadata_filename'].replace('.json', '.schema.json')}", "schema_files"),
            (f"generated/{spec['output_stem']}.json", "generated_files"),
            (f"generated/{spec['output_stem']}.md", "generated_files"),
        ]:
            if expected_file not in manifest_section_files.get(section, set()):
                fail(f"generated/MANIFEST.json missing common matrix {expected_file} in {section}")

    print("OK: archive lint passed")
    print(f"Validated {schema_stats['validated_files']} canonical JSON files against {schema_stats['schema_files']} schemas")
    print(f"Found {len(live_gap_ids)} live gaps")
    print(f"Checked {len(files)} numbered archive files in {ARCHIVE}")


if __name__ == "__main__":
    main()
