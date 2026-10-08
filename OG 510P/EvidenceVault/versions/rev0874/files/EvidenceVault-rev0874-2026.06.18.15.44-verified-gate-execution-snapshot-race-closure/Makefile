SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help
PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: help build-papers asset-indexes dedupe-report rebuild-indexes opening-check context-check command-surface-check toolchain-check manifest-check dedupe-check json-check text-check text-surface-check payload-format-check crypto-check provenance-check filesystem-check asset-check paper-check archive-payload-check source-check adr-check rfc-check frontier-check assimilation-check revision-check control-check validation-check claim-obligation-check public-status-check ro-crate-check changelog-check archive-index-check historical-anomaly-check cross-reference-check audit-witness-check identity-check publishing-check runner-check release-ledgers preflight gate publish-audit package-release

help:
	@echo "EvidenceVault command surface"
	@echo "  make build-papers       # rebuild canonical paper PDFs"
	@echo "  make asset-indexes      # regenerate artifacts/ARTIFACTS_INDEX.* and certs/CERTS_INDEX.*"
	@echo "  make dedupe-report      # regenerate DEDUPE_REPORT.md duplicate-payload inventory"
	@echo "  make rebuild-indexes    # regenerate INDEX/files.* and MANIFEST.sha256"
	@echo "  make opening-check      # validate opening/resumption surfaces"
	@echo "  make context-check      # validate context-pack revision, schema, command hints, and key-machine paths"
	@echo "  make command-surface-check # validate Makefile phony/help/recipe and command-inventory coherence"
	@echo "  make toolchain-check # validate governed replay toolchain lock, required modules/commands, and ZIP policy constants"
	@echo "  make manifest-check     # validate full MANIFEST.sha256 and INDEX/files.* coverage"
	@echo "  make dedupe-check       # validate DEDUPE_REPORT.md mirrors current duplicate-payload inventory"
	@echo "  make json-check         # validate whole-archive JSON parseability and bundled schema registry"
	@echo "  make text-check         # validate YAML/JSONL/CSV/Python/UTF-8 text payload hygiene"
	@echo "  make text-surface-check # validate governed text surfaces use UTF-8, LF line endings, final newline, and no trailing whitespace"
	@echo "  make payload-format-check # validate PDF/PNG/JSON-LD/SD-JWT/residual payload formats"
	@echo "  make crypto-check       # validate PEM public keys, DSSE syntax, and indexed Ed25519 DSSE verification fixtures"
	@echo "  make provenance-check # validate upstream input, redaction, pruning, and omission ledgers"
	@echo "  make filesystem-check # validate safe paths, regular-file modes, and transient filesystem artifacts"
	@echo "  make asset-check        # validate artifacts/certs indexes and canonical-path pointers"
	@echo "  make paper-check        # validate canonical papers, root PDF mirrors, and extraction-map paths"
	@echo "  make archive-payload-check # validate embedded ZIP/tar payloads, public-bundle freshness, and repro-pack digests"
	@echo "  make source-check       # validate retained-source inventory and family representation map"
	@echo "  make adr-check          # validate standing architecture decision surfaces"
	@echo "  make rfc-check          # validate bounded unresolved RFC/proposal memory"
	@echo "  make frontier-check     # validate current priority/open-pressure resume surfaces"
	@echo "  make assimilation-check # validate outside-pattern assimilation memory"
	@echo "  make revision-check     # validate current revision-anchor coherence"
	@echo "  make control-check      # validate control-surface and lifecycle-gate crosswalks"
	@echo "  make validation-check   # validate assurance/command inventory coherence"
	@echo "  make claim-obligation-check # validate governed claim-obligation map"
	@echo "  make public-status-check # validate public/internal status bridge and no public-payload widening"
	@echo "  make ro-crate-check    # validate RO-Crate-style research-object metadata bridge"
	@echo "  make changelog-check    # validate current changelog/history-anchor coherence"
	@echo "  make archive-index-check # validate ARCHIVE_INDEX.md/JSON bundle-lineage mirror"
	@echo "  make historical-anomaly-check # validate governed carried-forward historical anomaly ledger"
	@echo "  make cross-reference-check # validate governed machine-readable path references"
	@echo "  make audit-witness-check # validate retained AUDIT inventory witness coverage and wiring"
	@echo "  make identity-check     # validate internal bundle identity and lineage"
	@echo "  make publishing-check   # validate queue/public-release state"
	@echo "  make runner-check       # validate composite command-runner sequences and bounded publish-audit wiring"
	@echo "  make release-ledgers    # rebuild queue ledger, release ledger, and public bundles"
	@echo "  make preflight          # strict shipping preflight including transient-artifact scan"
	@echo "  make gate               # opening + context pack + command surface + toolchain lock + asset indexes + dedupe report + archive indexes + manifest + JSON + text payloads + governed text surfaces + payload formats + crypto-envelope/key material + provenance/absence ledgers + filesystem policy + asset + paper + embedded archive/source freshness + source + ADR + RFC + frontier + assimilation + revision + control + validation + claim-obligation map + public-status bridge + RO-Crate metadata bridge + changelog/history-anchor + archive-index companion + historical-anomaly ledger + cross-reference + audit-witness + identity + publishing"
	@echo "  make publish-audit      # release-ledger rebuild plus index/JSON refresh and release-path checks"
	@echo "  make package-release    # run full package gate, emit the ZIP plus sidecar, and verify artifact bytes"

build-papers:
	bash scripts/build_papers.sh

asset-indexes:
	$(PYTHON) scripts/build_asset_indexes.py

dedupe-report:
	$(PYTHON) scripts/build_dedupe_report.py

rebuild-indexes:
	$(PYTHON) scripts/rebuild_indexes.py

opening-check:
	$(PYTHON) scripts/validate_opening_surface.py

context-check:
	$(PYTHON) scripts/validate_context_pack.py

command-surface-check:
	$(PYTHON) scripts/validate_makefile_surface.py

toolchain-check:
	$(PYTHON) scripts/validate_toolchain_lock.py

manifest-check:
	$(PYTHON) scripts/validate_manifest_index.py

dedupe-check:
	$(PYTHON) scripts/validate_dedupe_report.py

json-check:
	$(PYTHON) scripts/validate_json_inventory.py

text-check:
	$(PYTHON) scripts/validate_text_payloads.py

text-surface-check:
	$(PYTHON) scripts/validate_text_surface_policy.py

payload-format-check:
	$(PYTHON) scripts/validate_payload_formats.py

crypto-check:
	$(PYTHON) scripts/validate_crypto_envelopes.py

provenance-check:
	$(PYTHON) scripts/validate_provenance_ledgers.py

filesystem-check:
	$(PYTHON) scripts/validate_filesystem_policy.py

asset-check:
	$(PYTHON) scripts/validate_asset_indexes.py

paper-check:
	$(PYTHON) scripts/validate_paper_series.py

archive-payload-check:
	$(PYTHON) scripts/validate_embedded_archives.py

source-check:
	$(PYTHON) scripts/validate_source_index.py

adr-check:
	$(PYTHON) scripts/validate_adrs.py

rfc-check:
	$(PYTHON) scripts/validate_rfcs.py

frontier-check:
	$(PYTHON) scripts/validate_current_frontier.py

assimilation-check:
	$(PYTHON) scripts/validate_assimilation_ledger.py

revision-check:
	$(PYTHON) scripts/validate_revision_anchors.py

control-check:
	$(PYTHON) scripts/validate_control_surfaces.py

validation-check:
	$(PYTHON) scripts/validate_validation_index.py

claim-obligation-check:
	$(PYTHON) scripts/validate_claim_obligation_map.py

public-status-check:
	$(PYTHON) scripts/validate_public_status.py

ro-crate-check:
	$(PYTHON) scripts/validate_ro_crate_metadata.py

changelog-check:
	$(PYTHON) scripts/validate_changelog.py

archive-index-check:
	$(PYTHON) scripts/validate_archive_index.py

historical-anomaly-check:
	$(PYTHON) scripts/validate_historical_anomalies.py

cross-reference-check:
	$(PYTHON) scripts/validate_cross_references.py

audit-witness-check:
	$(PYTHON) scripts/validate_audit_witnesses.py

identity-check:
	$(PYTHON) scripts/validate_archive_identity.py

publishing-check:
	$(PYTHON) scripts/validate_publishing.py

runner-check:
	$(PYTHON) scripts/validate_command_runners.py

release-ledgers:
	$(PYTHON) scripts/publication_rights_gate.py --context release-ledgers
	$(PYTHON) scripts/build_release_queue_index.py
	$(PYTHON) scripts/build_release_ledger.py
	$(PYTHON) scripts/materialize_public_release.py

preflight:
	bash scripts/publish_preflight.sh

gate:
	$(PYTHON) scripts/gate.py

publish-audit:
	$(PYTHON) scripts/publish_audit.py

package-release:
	$(PYTHON) scripts/package_release.py
