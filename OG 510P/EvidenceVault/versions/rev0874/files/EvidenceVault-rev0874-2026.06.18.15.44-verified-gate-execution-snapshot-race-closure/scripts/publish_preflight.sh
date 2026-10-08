#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 scripts/publication_rights_gate.py --context publish-preflight

fail() {
  echo "preflight: FAIL: $1" >&2
  exit 1
}

require_file() {
  [[ -f "$1" ]] || fail "missing file: $1"
}

require_dir() {
  [[ -d "$1" ]] || fail "missing directory: $1"
}

[[ "$(basename "$ROOT_DIR")" =~ ^EvidenceVault-rev[0-9]{4}$ ]] || fail "repo root must be named EvidenceVault-rev####"

for f in   README.md SERIES.md PAPER_SERIES_INDEX.md CATALOG.md CHANGELOG.md PUBLISHING.md START_HERE.md AGENTS.md Makefile MANIFEST.sha256 INDEX/files.json INDEX/files.csv DEDUPE_REPORT.md VALIDATION_INDEX.md VALIDATION_INDEX.json COMMAND_RUNNER_SEQUENCE.json COMMAND_RUNNER_SEQUENCE.md schemas/command_runner_sequence.schema.json CLAIM_OBLIGATION_MAP.md CLAIM_OBLIGATION_MAP.json PUBLIC_STATUS.md PUBLIC_STATUS.json RO_CRATE_PROFILE.md ro-crate-metadata.json TOOLCHAIN_LOCK.json TOOLCHAIN_LOCK.md SOURCE_INDEX.md SOURCE_INDEX.json CURRENT_FRONTIER.md CURRENT_FRONTIER.json CONTEXT_PACK.json schemas/context_pack.schema.json OPENING_CONTRACT.json OPENING_SURFACE_CONFORMANCE.json CONTROL_SURFACES.json LIFECYCLE_GATES.json ADR_INDEX.md ADR_INDEX.json RFC_INDEX.md RFC_INDEX.json ASSIMILATION_LEDGER.md ASSIMILATION_LEDGER.json REVISION_RECEIPT.json RELEASE_MANIFEST.json REVISION_ANCHORS.json ARCHIVE_INDEX.md ARCHIVE_INDEX.json AUDIT/HISTORICAL_ANOMALIES.json AUDIT/HISTORICAL_ANOMALIES.md artifacts/ARTIFACTS_INDEX.json artifacts/ARTIFACTS_INDEX.csv certs/CERTS_INDEX.json certs/CERTS_INDEX.csv rfcs/README.md rfcs/RFC-0000-template.md rfcs/RFC-0001-structured-review-ledger-lane.md   papers/EXTRACTION_MAP.json   publishing/OPERATOR_STARTUP.md publishing/CANONICAL_POLICY.json   publishing/templates/release_decision.md publishing/templates/public_release.md publishing/templates/release_queue_item.md   published/PUBLIC_SURFACE.json published/README.md published/index.md published/reader_guide.md published/artifact_request.md   published/releases/README.md published/releases/RELEASE_INDEX.json published/releases/LATEST.json   published/releases/2026-03-20-public-surface-bootstrap.md published/releases/2026-03-20-public-surface-bootstrap.json   published/releases/artifacts/README.md published/releases/artifacts/ARTIFACT_INDEX.json published/releases/snapshots/README.md published/releases/snapshots/EV-PUB-2026-03-20-public-surface-bootstrap.surface.json   release_queue/QUEUE_INDEX.json   release_queue/decisions/2026-03-20-public-surface-bootstrap.md release_queue/decisions/2026-03-20-public-surface-bootstrap.json   release_queue/decisions/2026-03-20-full-archive-mirror-not-public.md release_queue/decisions/2026-03-20-full-archive-mirror-not-public.json   release_queue/hold/2026-03-20-full-archive-mirror-not-public.md release_queue/hold/2026-03-20-full-archive-mirror-not-public.json   schemas/release_decision.schema.json schemas/public_surface_manifest.schema.json schemas/public_release.schema.json schemas/release_ledger.schema.json   schemas/release_queue_item.schema.json schemas/release_queue_index.schema.json schemas/public_release_bundle.schema.json schemas/public_release_artifact_index.schema.json schemas/public_surface_snapshot.schema.json schemas/opening_contract.schema.json schemas/opening_surface_conformance.schema.json schemas/control_surfaces.schema.json schemas/lifecycle_gates.schema.json schemas/adr_index.schema.json schemas/rfc_index.schema.json schemas/current_frontier.schema.json schemas/assimilation_ledger.schema.json schemas/revision_receipt.schema.json schemas/release_manifest.schema.json schemas/archive_bundle_index.schema.json schemas/revision_anchors.schema.json schemas/validation_index.schema.json schemas/claim_obligation_map.schema.json schemas/public_status.schema.json schemas/ro_crate_metadata.schema.json schemas/toolchain_lock.schema.json schemas/source_index.schema.json schemas/historical_anomalies.schema.json   scripts/build_release_ledger.py scripts/build_release_queue_index.py scripts/materialize_public_release.py scripts/publish_preflight.sh scripts/publish_queue_item.py   scripts/scaffold_queue_item.py scripts/transition_queue_item.py scripts/gate.py scripts/publish_audit.py scripts/validate_publishing.py scripts/validate_opening_surface.py scripts/validate_context_pack.py scripts/validate_makefile_surface.py scripts/validate_source_index.py scripts/build_source_index.py scripts/validate_adrs.py scripts/validate_rfcs.py scripts/validate_current_frontier.py scripts/validate_assimilation_ledger.py scripts/validate_control_surfaces.py scripts/validate_archive_identity.py scripts/validate_revision_anchors.py scripts/validate_validation_index.py scripts/validate_claim_obligation_map.py scripts/validate_public_status.py scripts/validate_ro_crate_metadata.py scripts/validate_toolchain_lock.py scripts/package_release.py scripts/verify_release_artifact.py scripts/rebuild_indexes.py scripts/build_dedupe_report.py scripts/validate_dedupe_report.py scripts/validate_manifest_index.py scripts/validate_json_inventory.py scripts/validate_text_payloads.py scripts/validate_text_surface_policy.py scripts/validate_payload_formats.py scripts/validate_crypto_envelopes.py scripts/validate_provenance_ledgers.py scripts/validate_filesystem_policy.py scripts/build_asset_indexes.py scripts/validate_asset_indexes.py scripts/validate_paper_series.py scripts/validate_embedded_archives.py scripts/validate_changelog.py scripts/validate_archive_index.py scripts/validate_historical_anomalies.py scripts/validate_cross_references.py scripts/validate_audit_witnesses.py scripts/validate_command_runners.py
 do
  require_file "$f"
done

for d in adrs rfcs papers artifacts artifacts/curated certs certs/curated published published/releases published/releases/artifacts published/releases/snapshots publishing publishing/templates release_queue release_queue/candidates release_queue/hold release_queue/published_ready release_queue/decisions INDEX schemas scripts; do
  require_dir "$d"
done

shopt -s nullglob
tex_files=(papers/*.tex)
pdf_files=(papers/*.pdf)
(( ${#tex_files[@]} > 0 )) || fail "no canonical TeX papers found"
(( ${#pdf_files[@]} > 0 )) || fail "no compiled paper PDFs found"
for tex in "${tex_files[@]}"; do
  pdf="${tex%.tex}.pdf"
  [[ -f "$pdf" ]] || fail "missing compiled PDF for $tex"
done
shopt -u nullglob

python3 - <<'PY2'
import json
from pathlib import Path
for rel in [
    'papers/EXTRACTION_MAP.json',
    'OPENING_CONTRACT.json',
    'OPENING_SURFACE_CONFORMANCE.json',
    'CONTROL_SURFACES.json',
    'LIFECYCLE_GATES.json',
    'RFC_INDEX.json',
    'CURRENT_FRONTIER.json',
    'ADR_INDEX.json',
    'ASSIMILATION_LEDGER.json',
    'REVISION_RECEIPT.json',
    'VALIDATION_INDEX.json',
    'COMMAND_RUNNER_SEQUENCE.json',
    'schemas/command_runner_sequence.schema.json',
    'CLAIM_OBLIGATION_MAP.json',
    'PUBLIC_STATUS.json',
    'TOOLCHAIN_LOCK.json',
    'SOURCE_INDEX.json',
    'RELEASE_MANIFEST.json',
    'REVISION_ANCHORS.json',
    'ARCHIVE_INDEX.json',
    'AUDIT/HISTORICAL_ANOMALIES.json',
    'CONTEXT_PACK.json',
    'schemas/context_pack.schema.json',
    'publishing/CANONICAL_POLICY.json',
    'published/PUBLIC_SURFACE.json',
    'schemas/release_decision.schema.json',
    'schemas/public_surface_manifest.schema.json',
    'schemas/public_release.schema.json',
    'schemas/release_ledger.schema.json',
    'schemas/release_queue_item.schema.json',
    'schemas/release_queue_index.schema.json',
    'schemas/public_release_bundle.schema.json',
    'schemas/public_release_artifact_index.schema.json',
    'schemas/public_surface_snapshot.schema.json',
    'schemas/opening_contract.schema.json',
    'schemas/opening_surface_conformance.schema.json',
    'schemas/control_surfaces.schema.json',
    'schemas/lifecycle_gates.schema.json',
    'schemas/adr_index.schema.json',
    'schemas/current_frontier.schema.json',
    'schemas/revision_receipt.schema.json',
    'schemas/release_manifest.schema.json',
    'schemas/archive_bundle_index.schema.json',
    'schemas/revision_anchors.schema.json',
    'schemas/validation_index.schema.json',
    'schemas/claim_obligation_map.schema.json',
    'schemas/public_status.schema.json',
    'schemas/toolchain_lock.schema.json',
    'schemas/source_index.schema.json',
    'schemas/historical_anomalies.schema.json',
]:
    json.loads(Path(rel).read_text())
for rel in sorted(Path('schemas').glob('*.json')):
    json.loads(rel.read_text())
PY2

python3 scripts/gate.py

python3 - <<'PY3'
from pathlib import Path
import fnmatch
import sys

root = Path('.')
for path in root.rglob('*'):
    parts = path.parts
    if path.name == '__pycache__' or path.suffix == '.pyc':
        print(f'preflight: FAIL: transient Python bytecode present: {path}', file=sys.stderr)
        sys.exit(1)

skip_roots = {'sources', 'artifacts', 'certs'}
patterns = ['_renders*', 'render_check*', '_render*', '*.aux', '*.log', '*.out', '*.toc', '*.bbl', '*.blg']
for path in root.rglob('*'):
    parts = path.parts
    if len(parts) > 1 and parts[0] in skip_roots:
        continue
    name = path.name
    if any(fnmatch.fnmatch(name, pattern) for pattern in patterns):
        print(f'preflight: FAIL: transient build/review artifact present: {path}', file=sys.stderr)
        sys.exit(1)
PY3

sha256sum -c MANIFEST.sha256 >/dev/null

echo "preflight: OK"
