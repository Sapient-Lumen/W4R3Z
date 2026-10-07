export PYTHONDONTWRITEBYTECODE=1

.PHONY: rebuild-surfaces verify-surfaces

rebuild-surfaces:
	python3 publishing/rebuild_archive_surfaces.py --root .

verify-surfaces:
	python3 publishing/render_transfer_sources.py --root .
	python3 publishing/build_decision_index.py --root .
	python3 publishing/render_queue_surfaces.py --root .
	python3 publishing/check_surface_schemas.py --root . --write-report reports/surface_schema_validation.json
	python3 publishing/check_archive_invariants.py --root . --write-report reports/archive_invariants.json
	python3 publishing/check_context_pack_contract.py --root . --write-report reports/context_pack_contract.json
	python3 publishing/check_context_pack_budget.py --root . --write-report reports/context_pack_budget.json
	python3 publishing/check_archive_budget.py --root . --write-report reports/archive_budget.json
	python3 publishing/check_transfer_source_receipt.py --root . --write-report reports/transfer_source_receipt.json
	python3 publishing/check_transient_surface.py --root . --write-report reports/transient_surface_audit.json
	python3 publishing/verify_manifest_sha256.py --root . --write-report reports/manifest_sha256_verification.json
	python3 publishing/check_manifest_coverage.py --root . --write-report reports/manifest_coverage_audit.json
	python3 publishing/build_lifecycle_gate_status.py --root . --write-report reports/lifecycle_gate_status.json
	python3 publishing/check_archive_coherence.py --root . --write-report reports/archive_surface_coherence.json
