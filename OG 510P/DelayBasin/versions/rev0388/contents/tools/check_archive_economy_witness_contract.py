import json
import pathlib

from witness_vocabulary_lib import expect_family, load_families

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/archive-economy-audit-witnesses.md"
AUDIT = ROOT / "ARCHIVE-ECONOMY-AUDIT.json"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
for path in (DOC, AUDIT, RECEIPT):
    if not path.exists():
        raise SystemExit(f"missing archive economy witness surface: {path.relative_to(ROOT)}")

families = load_families()
expect_family(
    families,
    "archive_economy_state",
    allowed=[
        "unchecked-archive-economy",
        "inventory-only-archive-economy",
        "risk-flagged-archive-economy",
        "refactor-ready-archive-economy",
        "mixed-archive-economy",
    ],
    surfaces=["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", "docs/10-method/archive-economy-audit-witnesses.md"],
)
receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
witness = receipt.get("archive_economy_witness")
contract = receipt.get("archive_economy_contract")
if not isinstance(witness, dict) or not isinstance(contract, dict):
    raise SystemExit("receipt missing archive_economy_witness/archive_economy_contract")
expected_witness = {
    "witness_family": "archive_economy_state",
    "witness_family_handle": "WVF-0133",
    "selected_token": "refactor-ready-archive-economy",
    "witness_surface": "docs/10-method/archive-economy-audit-witnesses.md",
    "contract_surface": "tools/check_archive_economy_witness_contract.py",
}
for key, value in expected_witness.items():
    if witness.get(key) != value:
        raise SystemExit(f"archive economy witness {key} drifted: {witness.get(key)!r} != {value!r}")
for flag in [
    "release-hygiene-root-relative",
    "economy-audit-generated",
    "checker-sprawl-measured",
    "queue-sediment-measured",
    "checker-batch-consolidated",
    "queue-sediment-reduced",
    "shadow-batch-consolidated",
    "hot-surface-compacted",
    "markdown-risk-reduced",
    "self-reference-excluded",
    "source-roundtrip-verified",
    "gpustorming-late-search-batched",
    "stale-ledger-debt-reduced",
    "gpu-witness-batch-consolidated",
    "ledger-debt-nonreview-gate",
    "path-alias-batch-resolved",
    "gpustorming-standard-batched",
    "batch-alias-groups-verified",
    "batch-spec-reviewability-guard",
    "batch-specs-segmented",
    "gpustorming-standard-no-exec",
    "batch-spec-locality-checked",
    "method-doc-ratchet-batched",
    "segment-index-derived-from-parts",
    "batch-diagnostics-segment-local",
    "method-doc-semantic-boundary-guard",
    "core-method-batched",
    "core-method-source-bound",
    "core-method-negative-canaries",
    "external-metadata-date-guard",
    "executable-canary-runs",
    "risk-burn-bureaucracy-boundary",
    "generated-surface-drift-gated",
    "lint-generator-mutation-removed",
    "package-release-refreshes-all-generated-surfaces",
    "package-release-lint-preflight",
    "package-release-artifact-smoke",
    "zip-member-set-checked",
    "clean-extraction-lint-gated",
    "package-sidecar-after-smoke",
    "package-artifact-negative-canaries",
    "safe-extract-independent",
    "package-deterministic-writer-canaries",
    "zip-fixed-metadata-checked",
    "zip-rebuild-byte-canary",
    "release-identity-validated",
    "release-identity-canaries",
    "package-sidecar-verified",
    "package-sidecar-canaries",
    "sidecar-format-digest-checked",
    "release-integrity-helper-refactored",
    "release-integrity-negative-canaries",
    "manifest-hash-drift-checked",
    "checksum-format-checked",
    "provenance-command-checked",
    "tools/package_preflight_lib.py",
    "tools/check_package_release_preflight_contract.py",
    "package-release-lint-preflight",
]:
    if witness.get(flag) is not True:
        raise SystemExit(f"archive economy witness missing true flag: {flag}")
if contract.get("checker") != "tools/check_archive_economy_witness_contract.py":
    raise SystemExit("archive economy contract checker drifted")
if contract.get("doc") != "docs/10-method/archive-economy-audit-witnesses.md":
    raise SystemExit("archive economy contract doc drifted")
if contract.get("family") != "archive_economy_state":
    raise SystemExit("archive economy contract family drifted")
if contract.get("audit") != "ARCHIVE-ECONOMY-AUDIT.json" or contract.get("audit_checker") != "tools/check_archive_economy_audit_contract.py":
    raise SystemExit("archive economy contract audit pointers drifted")
if contract.get("shadow_batch_checker") != "tools/check_shadow_batch_contract.py":
    raise SystemExit("archive economy contract shadow batch checker drifted")
if contract.get("hot_surface_compaction") != "HOT-SURFACE-COMPACTION.json" or contract.get("hot_surface_compaction_checker") != "tools/check_hot_surface_compaction_contract.py":
    raise SystemExit("archive economy contract hot-surface compaction pointers drifted")
if contract.get("hot_surface_compaction_helper") != "tools/hot_surface_compaction_lib.py" or contract.get("hot_surface_source_roundtrip_checker") != "tools/check_hot_surface_source_roundtrip_contract.py":
    raise SystemExit("archive economy contract hot-surface roundtrip pointers drifted")
if contract.get("gpustorming_late_search_batch_checker") != "tools/check_gpustorming_late_search_family_batch_contract.py":
    raise SystemExit("archive economy contract late-search batch pointer drifted")
if contract.get("ledger_debt_surfaces") != ["ASSUMPTION-LEDGER.json", "OBLIGATION-LEDGER.json", "RETROSPECTIVE-QUEUE.json", "LEDGER-AUDIT.json"]:
    raise SystemExit("archive economy contract ledger-debt surfaces drifted")
if contract.get("gpu_witness_batch_checker") != "tools/check_gpu_witness_batch_contract.py" or contract.get("gpu_witness_batch_specs") != "tools/gpu_witness_contract_specs.py":
    raise SystemExit("archive economy contract GPU witness batch pointers drifted")
if contract.get("ledger_debt_gate") != "LEDGER-AUDIT.json#debt_pressure":
    raise SystemExit("archive economy contract debt-pressure gate pointer drifted")
if contract.get("gpustorming_standard_batch_checker") != "tools/check_gpustorming_standard_family_batch_contract.py" or contract.get("gpustorming_standard_batch_specs") != "tools/gpustorming_standard_contract_specs.py":
    raise SystemExit("archive economy contract standard GPustorming batch pointers drifted")
if contract.get("path_alias_batch_groups") != "PATH-ALIAS-LEDGER.json#batch_alias_groups":
    raise SystemExit("archive economy contract path-alias batch groups pointer drifted")
if contract.get("batch_spec_locality_question") != "docs/20-constitution/open-question-registry.md#OQ-0235":
    raise SystemExit("archive economy contract batch-spec locality question drifted")
if contract.get("batch_spec_locality_checker") != "tools/check_batch_spec_locality_contract.py":
    raise SystemExit("archive economy contract batch-spec locality checker drifted")

if contract.get("method_doc_ratchet_batch_checker") != "tools/check_method_doc_ratchet_batch_contract.py" or contract.get("method_doc_ratchet_batch_specs") != "tools/method_doc_ratchet_contract_specs.py":
    raise SystemExit("archive economy contract method-doc ratchet batch pointers drifted")
if contract.get("method_doc_ratchet_batch_spec_parts") != [
    "tools/method_doc_ratchet_contract_specs_part_1.py",
    "tools/method_doc_ratchet_contract_specs_part_2.py",
]:
    raise SystemExit("archive economy contract method-doc ratchet spec parts drifted")
if contract.get("core_method_batch_checker") != "tools/check_core_method_batch_contract.py" or contract.get("core_method_batch_specs") != "tools/core_method_contract_specs.py":
    raise SystemExit("archive economy contract core-method batch pointers drifted")
if contract.get("core_method_batch_spec_parts") != [
    "tools/core_method_contract_specs_part_1.py",
    "tools/core_method_contract_specs_part_2.py",
]:
    raise SystemExit("archive economy contract core-method spec parts drifted")
if contract.get("core_method_successor_question") != "docs/20-constitution/open-question-registry.md#OQ-0238":
    raise SystemExit("archive economy contract core-method successor question drifted")
if contract.get("batch_spec_successor_question") != "docs/20-constitution/open-question-registry.md#OQ-0238":
    raise SystemExit("archive economy contract batch-spec successor question drifted")
if contract.get("core_method_negative_canary_checker") != "tools/check_core_method_batch_negative_canaries.py":
    raise SystemExit("archive economy contract core-method negative canary checker drifted")
if contract.get("core_method_contract_lib") != "tools/core_method_contract_lib.py":
    raise SystemExit("archive economy contract core-method library pointer drifted")
if contract.get("canary_runs_surface") != "CANARY-RUNS.json" or contract.get("canary_runs_checker") != "tools/check_canary_runs_contract.py":
    raise SystemExit("archive economy contract canary-runs pointers drifted")
if contract.get("external_metadata_generator") != "tools/gen_external_metadata.py" or contract.get("external_metadata_contract") != "tools/check_external_metadata_contract.py":
    raise SystemExit("archive economy contract external metadata pointers drifted")
if contract.get("external_metadata_contract_lib") != "tools/external_metadata_contract_lib.py":
    raise SystemExit("archive economy contract external metadata lib pointer drifted")
if contract.get("batch_spec_segment_iterator_policy") != "aggregates and public part lists must derive from segment rows; segment indexes are diagnostics only, not authority":
    raise SystemExit("archive economy contract batch-spec segment iterator policy drifted")
if contract.get("package_release_tool") != "tools/package_release.py":
    raise SystemExit("archive economy contract package-release tool pointer drifted")
if contract.get("package_release_preflight_helper") != "tools/package_preflight_lib.py":
    raise SystemExit("archive economy contract package-release preflight helper pointer drifted")
if contract.get("package_release_preflight_checker") != "tools/check_package_release_preflight_contract.py":
    raise SystemExit("archive economy contract package-release preflight checker pointer drifted")
if contract.get("package_release_artifact_smoke_helper") != "tools/package_preflight_lib.py#run_artifact_smoke":
    raise SystemExit("archive economy contract package-release artifact smoke helper pointer drifted")
if contract.get("package_release_artifact_smoke_checker") != "tools/check_package_release_preflight_contract.py":
    raise SystemExit("archive economy contract package-release artifact smoke checker pointer drifted")
if contract.get("package_release_artifact_smoke_negative_canary_checker") != "tools/check_package_artifact_smoke_negative_canaries.py":
    raise SystemExit("archive economy contract package artifact smoke negative canary pointer drifted")
if contract.get("package_deterministic_zip_canary_checker") != "tools/check_package_deterministic_zip_canaries.py":
    raise SystemExit("archive economy contract package deterministic zip canary pointer drifted")
if contract.get("package_deterministic_zip_helper") != "tools/package_preflight_lib.py#write_deterministic_zip":
    raise SystemExit("archive economy contract package deterministic zip helper pointer drifted")
if contract.get("package_sha256_sidecar_helper") != "tools/package_preflight_lib.py#write_verified_sha256_sidecar":
    raise SystemExit("archive economy contract package SHA256 sidecar helper pointer drifted")
if contract.get("package_sha256_sidecar_checker") != "tools/check_package_sidecar_canaries.py":
    raise SystemExit("archive economy contract package SHA256 sidecar checker pointer drifted")
if contract.get("release_identity_helper") != "tools/release_hygiene_lib.py#validate_release_identity":
    raise SystemExit("archive economy contract release identity helper pointer drifted")
if contract.get("release_identity_checker") != "tools/check_release_identity_canaries.py":
    raise SystemExit("archive economy contract release identity checker pointer drifted")
if contract.get("release_integrity_helper") != "tools/release_integrity_contract_lib.py":
    raise SystemExit("archive economy contract release integrity helper pointer drifted")
if contract.get("release_integrity_checker") != "tools/check_release_integrity_contract.py":
    raise SystemExit("archive economy contract release integrity checker pointer drifted")
if contract.get("release_integrity_negative_canary_checker") != "tools/check_release_integrity_negative_canaries.py":
    raise SystemExit("archive economy contract release integrity negative canary checker pointer drifted")
if contract.get("release_integrity_successor_question") != "docs/20-constitution/open-question-registry.md#OQ-0245":
    raise SystemExit("archive economy contract release integrity successor question drifted")
if contract.get("package_release_artifact_smoke_successor_question") != "docs/20-constitution/open-question-registry.md#OQ-0242":
    raise SystemExit("archive economy contract package-release artifact smoke successor question drifted")
if contract.get("package_deterministic_zip_successor_question") != "docs/20-constitution/open-question-registry.md#OQ-0244":
    raise SystemExit("archive economy contract package deterministic zip successor question drifted")
if contract.get("generated_surface_drift_checker") != "tools/check_generated_surface_drift.py":
    raise SystemExit("archive economy contract generated-surface drift checker pointer drifted")
if contract.get("generated_surface_orchestrator") != "tools/gen_all_generated_surfaces.py":
    raise SystemExit("archive economy contract generated-surface orchestrator pointer drifted")
if contract.get("generated_surface_helper") != "tools/generated_surface_lib.py":
    raise SystemExit("archive economy contract generated-surface helper pointer drifted")
if contract.get("generated_surface_successor_question") != "docs/20-constitution/open-question-registry.md#OQ-0239":
    raise SystemExit("archive economy contract generated-surface successor question drifted")
if contract.get("gpu_witness_batch_spec_parts") != [
    "tools/gpu_witness_contract_specs_part_1.py",
    "tools/gpu_witness_contract_specs_part_2.py",
    "tools/gpu_witness_contract_specs_part_3.py",
    "tools/gpu_witness_contract_specs_part_4.py",
]:
    raise SystemExit("archive economy contract GPU spec parts drifted")
if contract.get("gpustorming_standard_batch_spec_parts") != [
    "tools/gpustorming_standard_contract_specs_part_1.py",
    "tools/gpustorming_standard_contract_specs_part_2.py",
    "tools/gpustorming_standard_contract_specs_part_3.py",
    "tools/gpustorming_standard_contract_specs_part_4.py",
]:
    raise SystemExit("archive economy contract standard GPustorming spec parts drifted")
if contract.get("receipt_slot_guard") != "tools/check_current_witness_receipt_slot.py":
    raise SystemExit("archive economy contract must name receipt-slot guard")
text = DOC.read_text(encoding="utf-8")
for needle in [
    "# Archive economy audit witnesses",
    "refactor-ready-archive-economy",
    "release-hygiene-root-relative",
    "checker-batch-consolidated",
    "shadow-batch-consolidated",
    "hot-surface-compacted",
    "source-roundtrip-verified",
    "gpustorming-late-search-batched",
    "stale-ledger-debt-reduced",
    "gpu-witness-batch-consolidated",
    "ledger-debt-nonreview-gate",
    "path-alias-batch-resolved",
    "gpustorming-standard-batched",
    "batch-alias-groups-verified",
    "wrapper-regrowth-by-alias",
    "batch-spec-reviewability-guard",
    "batch-specs-segmented",
    "gpustorming-standard-no-exec",
    "batch-spec-locality-checked",
    "method-doc-ratchet-batched",
    "segment-index-derived-from-parts",
    "batch-diagnostics-segment-local",
    "OQ-0236",
    "OQ-0237",
    "OQ-0238",
    "semantic-ratchet-substitution",
    "method-doc-semantic-boundary-guard",
    "core-method-batched",
    "core-method-source-bound",
    "core-method-negative-canaries",
    "external-metadata-date-guard",
    "executable-canary-runs",
    "risk-burn-bureaucracy-boundary",
    "generated-surface-drift-gated",
    "lint-generator-mutation-removed",
    "package-release-refreshes-all-generated-surfaces",
    "package-release-lint-preflight",
    "package-release-artifact-smoke",
    "zip-member-set-checked",
    "clean-extraction-lint-gated",
    "package-sidecar-after-smoke",
    "package-artifact-negative-canaries",
    "safe-extract-independent",
    "package-deterministic-writer-canaries",
    "zip-fixed-metadata-checked",
    "zip-rebuild-byte-canary",
    "release-identity-validated",
    "release-identity-canaries",
    "package-sidecar-verified",
    "package-sidecar-canaries",
    "sidecar-format-digest-checked",
    "release-integrity-helper-refactored",
    "release-integrity-negative-canaries",
    "manifest-hash-drift-checked",
    "checksum-format-checked",
    "provenance-command-checked",
    "tools/release_integrity_contract_lib.py",
    "tools/check_release_integrity_negative_canaries.py",
    "OQ-0245",
    "bundle-notary",
    "tools/package_preflight_lib.py",
    "tools/check_package_release_preflight_contract.py",
    "tools/check_generated_surface_drift.py",
    "tools/gen_all_generated_surfaces.py",
    "tools/generated_surface_lib.py",
    "OQ-0239",
    "source docs remain semantic surfaces",
    "package-release-audit-order-repaired",
    "tools/package_release.py",
    "markdown-risk-reduced",
    "queue-sediment-reduced",
    "not a deletion court",
]:
    if needle not in text:
        raise SystemExit(f"archive economy witness doc missing {needle}")
print("check_archive_economy_witness_contract: OK")
