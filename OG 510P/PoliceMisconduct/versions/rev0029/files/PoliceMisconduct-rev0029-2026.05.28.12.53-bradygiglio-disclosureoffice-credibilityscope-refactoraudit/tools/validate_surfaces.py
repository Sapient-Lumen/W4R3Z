#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'README.md', 'START_HERE.md', 'AGENTS.md', 'CHANGELOG.md', 'ARCHIVE_INDEX.md',
    'RELEASE-MANIFEST.json', 'REVISION-RECEIPT.json', 'SURFACE-STATUS.json', 'context-pack.json',
    'CLAIM-SURFACE.json', 'NONCLAIMS.json', 'EVIDENCE-LADDER.json', 'PUBLIC-RECORD-CARRIER-LEDGER.json',
    'ETHICS-GUARDRAIL-LEDGER.json', 'PRIVACY-CLASSIFICATION-LEDGER.json', 'ENTITY-RESOLUTION-LEDGER.json',
    'DATACUBE-TRANSFER-LEDGER.json', 'OPEN-QUESTION-REGISTRY.json', 'VISION-LADDER.json',
    'PRODUCT-SHAPE-LEDGER.json', 'PILOT-SELECTION-MATRIX.json', 'PILOT-DECISION-RECEIPT.json',
    'SOURCE-GRAPH-PILOT-LEDGER.json', 'ACQUISITION-PROTOCOL-LEDGER.json', 'DISPLAY-GATE-LEDGER.json',
    'STATUS-DRIFT-WATCHLIST.json', 'DOCUMENT-CLASS-TAXONOMY.json', 'CITATION-PINNING-LEDGER.json',
    'PUBLIC-VIEW-GATE-MATRIX.json', 'ROLE-ACCESS-MODEL-LEDGER.json', 'HARM-MODEL-LEDGER.json',
    'LEGAL-RISK-REGISTER.json', 'SOURCE-DOCUMENT-ADMISSION-RULES.json', 'STATUS-LABEL-POLICY.json',
    'CLAIM-PROMOTION-GATE-LEDGER.json', 'MISSINGNESS-LEDGER.json', 'JURISDICTION-EDGE-CASE-LEDGER.json',
    'OFFICIAL-NEWS-CARRIER-LEDGER.json', 'STATUS-CONFLICT-RESOLUTION-LEDGER.json', 'DOCKET-RECHECK-PROTOCOL.json',
    'EVENT-TAXONOMY.json', 'CURRENT-STATUS-CANDIDATE-GATE.json', 'COURT-ORDER-ACCESSION-LEDGER.json',
    'LOCAL-MONITOR-SOURCE-BRIDGE-LEDGER.json', 'CHILD-AGENCY-STATUS-SPLIT-LEDGER.json',
    'PUBLIC-STATUS-CARD-COPY-LEDGER.json', 'HISTORY-RETENTION-LEDGER.json', 'GHOST-CARRIER-CANDIDATE-LEDGER.json',
    'PDF-URL-ACCESSION-LEDGER.json', 'ORDER-PROOF-ATOM-LEDGER.json', 'DOCUMENT-EFFECT-NONCURRENT-CLAIM-GATE.json',
    'PERSON-NAME-FILTER-LEDGER.json', 'PUBLIC-TIMELINE-GATE-LEDGER.json',
    'data/source_graph/doj_sls_law_enforcement_agencies.seed.json',
    'data/source_graph/doj_sls_matter_objects.rev0004.json',
    'data/source_graph/doj_sls_document_census.rev0004.json',
    'data/source_graph/doj_sls_status_events.rev0004.json',
    'data/source_graph/doj_sls_official_news_events.rev0005.json',
    'data/source_graph/doj_sls_status_reconciliation_queue.rev0005.json',
    'data/source_graph/doj_sls_event_matter_crosswalk.rev0005.json',
    'data/source_graph/doj_sls_high_volatility_source_packets.rev0005.json',
    'data/source_graph/doj_sls_status_candidate_packets.rev0006.json',
    'data/source_graph/doj_sls_court_order_accession_candidates.rev0006.json',
    'data/source_graph/doj_sls_local_monitor_sources.rev0006.json',
    'data/source_graph/doj_sls_child_agency_status_splits.rev0006.json',
    'data/source_graph/doj_sls_public_status_cards.rev0006.json',
    'data/source_graph/doj_sls_history_retention_warnings.rev0006.json',
    'data/source_graph/doj_sls_ghost_carrier_candidates.rev0006.json',
    'data/source_graph/doj_sls_additional_official_news_events.rev0006.json',
    'data/source_graph/doj_sls_pdf_url_accessions.rev0007.json',
    'data/source_graph/doj_sls_order_proof_atoms.rev0007.json',
    'data/source_graph/doj_sls_status_timeline_events.rev0007.json',
    'data/source_graph/doj_sls_accession_gap_register.rev0007.json',
    'data/source_graph/doj_sls_public_status_line_candidates.rev0007.json',
    'schemas/pdf_url_accession.schema.json', 'schemas/order_proof_atom.schema.json',
    'schemas/status_timeline_event.schema.json', 'schemas/accession_gap.schema.json',
    'docs/50-pilot/rev0007-order-proof-atom-report.md', 'docs/50-pilot/pdf-url-accession-method.md',
    'docs/50-pilot/document-effect-versus-current-status.md', 'docs/50-pilot/person-name-filter-for-public-documents.md',
    'docs/60-display/status-timeline-card-wireframe-rev0007.md', 'docs/70-examples/rev0007-sample-nopd-status-timeline.md',

    'SIGNAL-FAMILY-TRIAGE-LEDGER.json', 'STATUS-PROOF-BUNDLE-LEDGER.json',
    'PUBLIC-DEPARTMENT-PAGE-PREFLIGHT-LEDGER.json', 'ROLLBACK-DEPENDENCY-GRAPH-LEDGER.json',
    'SOURCE-PAGE-RESNAPSHOT-LEDGER.json', 'DOCKET-HUNT-QUEUE-LEDGER.json', 'CLAIM-PROMOTION-TRIAGE-LEDGER.json',
    'data/source_graph/doj_sls_source_page_resnapshot.rev0008.json',
    'data/source_graph/doj_sls_official_news_signal_vectors.rev0008.json',
    'data/source_graph/doj_sls_source_family_signal_conflicts.rev0008.json',
    'data/source_graph/doj_sls_status_proof_bundles.rev0008.json',
    'data/source_graph/doj_sls_source_acquisition_queue.rev0008.json',
    'data/source_graph/doj_sls_public_department_page_preflight.rev0008.json',
    'data/source_graph/doj_sls_claim_promotion_triage.rev0008.json',
    'data/source_graph/doj_sls_rollback_dependency_edges.rev0008.json',
    'schemas/source_page_resnapshot_row.schema.json', 'schemas/official_news_signal_vector.schema.json',
    'schemas/status_proof_bundle.schema.json', 'schemas/source_acquisition_queue_ticket.schema.json',
    'schemas/public_department_page_preflight.schema.json', 'schemas/claim_promotion_triage_row.schema.json',
    'schemas/rollback_dependency_edge.schema.json', 'schemas/source_family_signal_conflict.schema.json',
    'docs/50-pilot/rev0008-status-proof-bundle-report.md', 'docs/50-pilot/source-family-signal-triage-rev0008.md',
    'docs/50-pilot/court-order-hunt-queue-method-rev0008.md', 'docs/60-display/public-department-page-preflight-rev0008.md',
    'docs/70-examples/rev0008-sample-public-page-nopd.md', 'docs/80-ops/rollback-dependency-graph-method-rev0008.md',
]


REQUIRED += [
    'DOCUMENT-ROLE-MATRIX-LEDGER.json', 'DEPARTMENT-SOURCE-INVENTORY-PAGE-SHELL-LEDGER.json',
    'MISSINGNESS-BANNER-LEDGER.json', 'PUBLIC-PAGE-MODULE-PERMISSION-LEDGER.json',
    'SOURCE-INVENTORY-REVIEW-QUEUE-LEDGER.json',
    'data/source_graph/doj_sls_document_role_matrix.rev0009.json',
    'data/source_graph/doj_sls_department_source_inventory_page_shells.rev0009.json',
    'data/source_graph/doj_sls_missingness_banners.rev0009.json',
    'data/source_graph/doj_sls_public_page_module_permissions.rev0009.json',
    'data/source_graph/doj_sls_public_page_copy_blocks.rev0009.json',
    'data/source_graph/doj_sls_source_inventory_review_queue.rev0009.json',
    'schemas/document_role_matrix_row.schema.json', 'schemas/department_source_inventory_page_shell.schema.json',
    'schemas/missingness_banner.schema.json', 'schemas/public_page_module_permission.schema.json',
    'schemas/claimless_public_page_copy_block.schema.json', 'schemas/source_inventory_review_queue_ticket.schema.json',
    'docs/50-pilot/rev0009-public-source-inventory-shells-report.md',
    'docs/50-pilot/document-role-matrix-method-rev0009.md',
    'docs/60-display/department-source-inventory-page-shell-rev0009.md',
    'docs/60-display/missingness-banner-copy-rule-rev0009.md',
    'docs/70-examples/rev0009-sample-public-page-baltimore.md',
    'docs/80-ops/review-queue-priority-method-rev0009.md',
]


REQUIRED += [
    'AGENCY-IDENTITY-SPINE-LEDGER.json', 'DENOMINATOR-SOURCE-BRIDGE-LEDGER.json',
    'AGENCY-EXTERNAL-ID-GATE.json', 'AGENCY-MERGE-BLOCKER-LEDGER.json',
    'JURISDICTION-SCAFFOLD-LEDGER.json', 'PUBLIC-AGENCY-PAGE-GATE-LEDGER.json',
    'OFFICIAL-SOURCE-OBSERVATION-LEDGER.json',
    'data/source_graph/doj_sls_agency_identity_candidates.rev0010.json',
    'data/source_graph/doj_sls_agency_alias_packets.rev0010.json',
    'data/source_graph/doj_sls_jurisdiction_scaffolds.rev0010.json',
    'data/source_graph/denominator_source_bridge.rev0010.json',
    'data/source_graph/agency_external_id_requirements.rev0010.json',
    'data/source_graph/doj_sls_agency_merge_blockers.rev0010.json',
    'data/source_graph/doj_sls_agency_denominator_bridge_queue.rev0010.json',
    'data/source_graph/public_agency_page_gates.rev0010.json',
    'data/source_graph/official_source_observations.rev0010.json',
    'schemas/agency_identity_candidate.schema.json', 'schemas/agency_alias_packet.schema.json',
    'schemas/jurisdiction_scaffold.schema.json', 'schemas/denominator_source_bridge.schema.json',
    'schemas/agency_external_identifier_requirement.schema.json', 'schemas/agency_merge_blocker.schema.json',
    'schemas/agency_denominator_bridge_queue_ticket.schema.json', 'schemas/public_agency_page_gate.schema.json',
    'schemas/official_source_observation.schema.json',
    'docs/50-pilot/rev0010-agency-identity-spine-report.md',
    'docs/50-pilot/agency-identity-candidate-method-rev0010.md',
    'docs/50-pilot/denominator-source-bridge-method-rev0010.md',
    'docs/50-pilot/external-identifier-gate-rev0010.md',
    'docs/50-pilot/subunit-parent-split-examples-rev0010.md',
    'docs/50-pilot/rev0010-official-source-check-notes.md',
    'docs/60-display/public-agency-page-gate-rev0010.md',
    'docs/70-examples/rev0010-sample-agency-identity-card-nopd.md',
    'docs/70-examples/rev0010-sample-orange-county-split-card.md',
    'docs/80-ops/agency-unmerge-receipt-method-rev0010.md',
]


REQUIRED += [
    'SOURCE-FREEZE-PROTOCOL-LEDGER.json', 'LINK-ROT-RISK-LEDGER.json',
    'CHECKSUM-FIXITY-GATE-LEDGER.json', 'SOURCE-MUTATION-WATCH-LEDGER.json',
    'PAYLOAD-PUBLICATION-GATE-LEDGER.json',
    'data/source_graph/doj_sls_document_freeze_queue.rev0011.json',
    'data/source_graph/doj_sls_link_target_resolution_queue.rev0011.json',
    'data/source_graph/doj_sls_matter_freeze_debt.rev0011.json',
    'data/source_graph/doj_sls_document_mutation_watch.rev0011.json',
    'data/source_graph/checksum_debt_register.rev0011.json',
    'data/source_graph/doj_sls_source_page_freeze_targets.rev0011.json',
    'data/source_graph/source_preservation_policy_matrix.rev0011.json',
    'schemas/document_freeze_queue_ticket.schema.json', 'schemas/link_target_resolution_ticket.schema.json',
    'schemas/matter_freeze_debt_summary.schema.json', 'schemas/checksum_debt_item.schema.json',
    'schemas/document_mutation_watch.schema.json', 'schemas/source_page_freeze_target.schema.json',
    'schemas/source_preservation_policy_row.schema.json',
    'docs/50-pilot/rev0011-source-freeze-report.md',
    'docs/50-pilot/source-freeze-protocol-rev0011.md',
    'docs/50-pilot/checksum-and-fixity-policy-rev0011.md',
    'docs/50-pilot/link-rot-and-source-mutation-playbook-rev0011.md',
    'docs/50-pilot/warc-wacz-preservation-note-rev0011.md',
    'docs/60-display/preserved-source-badge-wireframe-rev0011.md',
    'docs/70-examples/rev0011-sample-freeze-card-nopd.md',
    'docs/80-ops/rev0011-preservation-operator-runbook.md',
]



REQUIRED += [
    'LINK-TARGET-RESOLUTION-LEDGER.json', 'CAPTURE-MANIFEST-LEDGER.json',
    'FIXITY-STATE-MACHINE-LEDGER.json', 'SOURCE-RECHECK-TRIGGER-LEDGER.json',
    'PUBLIC-CITATION-BADGE-GATE.json',
    'data/source_graph/doj_sls_link_target_resolutions.rev0012.json',
    'data/source_graph/doj_sls_official_news_resnapshots.rev0012.json',
    'data/source_graph/source_capture_manifest.rev0012.json',
    'data/source_graph/fixity_state_machine.rev0012.json',
    'data/source_graph/source_recheck_triggers.rev0012.json',
    'data/source_graph/public_citation_badge_candidates.rev0012.json',
    'data/source_graph/resolution_debt_delta.rev0012.json',
    'schemas/resolved_link_target.schema.json', 'schemas/official_news_resnapshot.schema.json',
    'schemas/source_capture_manifest_target.schema.json', 'schemas/fixity_state_definition.schema.json',
    'schemas/source_recheck_trigger.schema.json', 'schemas/public_citation_badge_candidate.schema.json',
    'schemas/resolution_debt_delta.schema.json',
    'docs/50-pilot/rev0012-link-target-resolution-report.md',
    'docs/50-pilot/capture-manifest-method-rev0012.md',
    'docs/50-pilot/fixity-state-machine-rev0012.md',
    'docs/50-pilot/official-news-resnapshot-method-rev0012.md',
    'docs/60-display/public-citation-badge-wireframe-rev0012.md',
    'docs/70-examples/rev0012-sample-capture-card-seattle.md',
    'docs/80-ops/rev0012-fixity-operator-runbook.md',
]


REQUIRED += [
    'TELOS-CHARTER-LEDGER.json', 'DREAM-REGISTER.json', 'EARNED-CAPABILITY-LADDER.json',
    'FUTURE-SESSION-REENTRY-OFFICE.json', 'UNCONSTRAINED-THINKING-GUARDRAIL.json',
    'DESIGN-TENSION-LEDGER.json', 'OPEN-HORIZON-REGISTER.json', 'FOUNDATION-AUDIT-CHECKLIST.json',
    'data/program/rev0015_telos_cards.json', 'data/program/rev0015_future_session_briefing_cards.json',
    'data/program/rev0015_foundation_audit_questions.json', 'data/program/rev0015_capability_ladder_edges.json',
    'schemas/telos_statement.schema.json', 'schemas/dream_register_entry.schema.json',
    'schemas/earned_capability_rung.schema.json', 'schemas/design_tension.schema.json',
    'schemas/open_horizon_entry.schema.json', 'schemas/foundation_audit_question.schema.json',
    'schemas/future_session_briefing_card.schema.json',
    'docs/00-meta/rev0015-mile-high-telos-charter.md', 'docs/00-meta/future-session-reentry-office.md',
    'docs/00-meta/not-overly-constrained-design-note.md', 'docs/30-program/what-we-are-trying-to-earn.md',
    'docs/30-program/earned-capability-ladder-rev0015.md', 'docs/30-program/dreams-and-product-futures-rev0015.md',
    'docs/20-constitution/phase-bound-vs-permanent-constraints.md', 'docs/30-program/open-horizon-register-rev0015.md',
    'docs/80-ops/rev0015-mile-high-reentry-checklist.md',
]

errors = []
for rel in REQUIRED:
    if not (ROOT / rel).exists():
        errors.append(f'missing required file: {rel}')

json_data = {}
for p in ROOT.rglob('*.json'):
    try:
        json_data[str(p.relative_to(ROOT))] = json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        errors.append(f'JSON parse failure {p.relative_to(ROOT)}: {e}')

manifest = json_data.get('RELEASE-MANIFEST.json', {})
receipt = json_data.get('REVISION-RECEIPT.json', {})
status = json_data.get('SURFACE-STATUS.json', {})
context = json_data.get('context-pack.json', {})
claim = json_data.get('CLAIM-SURFACE.json', {})
revision = manifest.get('revision')

if not revision:
    errors.append('manifest revision missing')
for name, obj in [('receipt', receipt), ('status', status), ('context-pack', context)]:
    if obj.get('revision') != revision:
        errors.append(f'{name} revision does not match manifest')
if manifest.get('bundle') != receipt.get('packaged_bundle_filename'):
    errors.append('receipt packaged bundle filename does not match manifest bundle')
if not claim.get('active_claims'):
    errors.append('CLAIM-SURFACE.json has no active_claims')
if not claim.get('non_claims'):
    errors.append('CLAIM-SURFACE.json has no non_claims')

# Guard against accidental live-data directories.
if manifest.get('live_person_records') == 0:
    for forbidden in ['officers', 'persons', 'civilians']:
        if (ROOT / 'data' / forbidden).exists():
            errors.append(f'data/{forbidden} exists while live_person_records is 0')
if manifest.get('live_incident_records') == 0 and (ROOT / 'data' / 'incidents').exists() and revision not in {'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'}:
    errors.append('data/incidents exists while live_incident_records is 0')
for forbidden, field in [('lawsuits','live_lawsuit_records'), ('settlements','live_settlement_records')]:
    if (ROOT / 'data' / forbidden).exists() and manifest.get(field, 0) == 0:
        errors.append(f'data/{forbidden} exists while {field} is 0')

seed = json_data.get('data/source_graph/doj_sls_law_enforcement_agencies.seed.json', {})
rows = seed.get('rows', [])
if seed.get('row_count') != len(rows):
    errors.append('DOJ SLS seed row_count mismatch')
for r in rows:
    if r.get('person_level_claims_admitted') is not False:
        errors.append(f"source row {r.get('row_id')} admits person claims")
    if r.get('incident_level_claims_admitted') is not False:
        errors.append(f"source row {r.get('row_id')} admits incident claims")

matters = json_data.get('data/source_graph/doj_sls_matter_objects.rev0004.json', {})
mo = matters.get('matter_objects', [])
if matters.get('matter_object_count') != len(mo):
    errors.append('matter_object_count mismatch')
if len(mo) != len(rows):
    errors.append('matter object count does not match source row count')
for m in mo:
    if m.get('record_kind') != 'matter_object_not_claim_object':
        errors.append(f"matter {m.get('matter_id')} wrong record_kind")
    for key in ['claim_extraction_allowed', 'person_extraction_allowed', 'incident_extraction_allowed']:
        if m.get(key) is not False:
            errors.append(f"matter {m.get('matter_id')} has {key} not false")
    if m.get('current_status_assertion_state') != 'not_asserted_in_rev0004':
        errors.append(f"matter {m.get('matter_id')} asserts current status")

docset = json_data.get('data/source_graph/doj_sls_document_census.rev0004.json', {})
docs = docset.get('documents', [])
doc_ids = {d.get('source_document_id') for d in docs}
if docset.get('document_count') != len(docs):
    errors.append('document_count mismatch')
if len(docs) < 100:
    errors.append('document census unexpectedly small')
for d in docs:
    for key in ['claim_extraction_allowed', 'person_extraction_allowed', 'incident_extraction_allowed']:
        if d.get(key) is not False:
            errors.append(f"doc {d.get('source_document_id')} has {key} not false")
    if d.get('content_summary_state') != 'not_summarized':
        errors.append(f"doc {d.get('source_document_id')} appears summarized")

# Prior revision nonclaim checks.
for path, key, count_field in [
    ('data/source_graph/doj_sls_official_news_events.rev0005.json','events','event_count'),
    ('data/source_graph/doj_sls_additional_official_news_events.rev0006.json','events','event_count'),
    ('data/source_graph/doj_sls_status_reconciliation_queue.rev0005.json','tickets','ticket_count'),
    ('data/source_graph/doj_sls_status_candidate_packets.rev0006.json','candidates','candidate_count'),
    ('data/source_graph/doj_sls_court_order_accession_candidates.rev0006.json','candidates','candidate_count'),
    ('data/source_graph/doj_sls_local_monitor_sources.rev0006.json','sources','source_count'),
    ('data/source_graph/doj_sls_child_agency_status_splits.rev0006.json','child_status_objects','child_status_count'),
    ('data/source_graph/doj_sls_public_status_cards.rev0006.json','cards','card_count'),
    ('data/source_graph/doj_sls_history_retention_warnings.rev0006.json','warnings','warning_count'),
    ('data/source_graph/doj_sls_ghost_carrier_candidates.rev0006.json','candidates','candidate_count')
]:
    obj = json_data.get(path, {})
    arr = obj.get(key, [])
    if obj.get(count_field) != len(arr):
        errors.append(f'{path} {count_field} mismatch')

# Rev0007 PDF URL accession checks.
pdf = json_data.get('data/source_graph/doj_sls_pdf_url_accessions.rev0007.json', {})
accessions = pdf.get('accessions', [])
if pdf.get('accession_count') != len(accessions):
    errors.append('pdf accession_count mismatch')
if len(accessions) != 13:
    errors.append('expected 13 PDF URL accessions in rev0007')
accession_ids = {a.get('accession_id') for a in accessions}
accession_doc_ids = {a.get('source_document_id') for a in accessions}
for a in accessions:
    if a.get('record_kind') != 'pdf_url_accession_noncontent':
        errors.append(f"pdf accession {a.get('accession_id')} wrong record_kind")
    if a.get('source_document_id') not in doc_ids:
        errors.append(f"pdf accession {a.get('accession_id')} references unknown source_document_id")
    if 'justice.gov' not in (a.get('official_url') or ''):
        errors.append(f"pdf accession {a.get('accession_id')} official_url is not DOJ")
    if a.get('content_type_observed') != 'application/pdf':
        errors.append(f"pdf accession {a.get('accession_id')} not marked application/pdf")
    if a.get('content_storage_state') != 'not_bundled_not_hashed':
        errors.append(f"pdf accession {a.get('accession_id')} storage state not blocked")
    if a.get('content_summary_state') != 'not_summarized':
        errors.append(f"pdf accession {a.get('accession_id')} appears summarized")
    for key in ['person_extraction_allowed','incident_extraction_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed','current_status_claim_admitted']:
        if a.get(key) is not False:
            errors.append(f"pdf accession {a.get('accession_id')} has {key} not false")

# Rev0007 order proof atom checks.
atoms_obj = json_data.get('data/source_graph/doj_sls_order_proof_atoms.rev0007.json', {})
atoms = atoms_obj.get('proof_atoms', [])
if atoms_obj.get('proof_atom_count') != len(atoms):
    errors.append('proof_atom_count mismatch')
if len(atoms) != 11:
    errors.append('expected 11 proof atoms in rev0007')
allowed_kinds = {'court_order_proof_atom_noncurrent','motion_request_atom_noncurrent','official_closing_letter_effect_atom_noncurrent'}
for atom in atoms:
    if atom.get('record_kind') not in allowed_kinds:
        errors.append(f"proof atom {atom.get('proof_atom_id')} wrong record_kind")
    if atom.get('source_document_id') not in accession_doc_ids:
        errors.append(f"proof atom {atom.get('proof_atom_id')} references non-accessioned doc")
    if atom.get('accession_id') not in accession_ids:
        errors.append(f"proof atom {atom.get('proof_atom_id')} references unknown accession")
    for key in ['current_status_claim_admitted','public_current_status_claim_admitted','person_extraction_allowed','incident_extraction_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed']:
        if atom.get(key) is not False:
            errors.append(f"proof atom {atom.get('proof_atom_id')} has {key} not false")
    if not atom.get('rollback_trigger'):
        errors.append(f"proof atom {atom.get('proof_atom_id')} missing rollback trigger")
    if atom.get('display_state') == 'public_final':
        errors.append(f"proof atom {atom.get('proof_atom_id')} marked public_final")
    if not atom.get('document_effect_statement'):
        errors.append(f"proof atom {atom.get('proof_atom_id')} missing document_effect_statement")

# Rev0007 timeline events.
tl = json_data.get('data/source_graph/doj_sls_status_timeline_events.rev0007.json', {})
events = tl.get('events', [])
if tl.get('timeline_event_count') != len(events):
    errors.append('timeline_event_count mismatch')
if len(events) != len(accessions):
    errors.append('timeline events should match PDF accessions')
for ev in events:
    if ev.get('record_kind') != 'source_document_timeline_event_noncurrent':
        errors.append(f"timeline event {ev.get('timeline_event_id')} wrong record_kind")
    for key in ['current_status_claim_admitted','public_current_status_claim_admitted','person_extraction_allowed','incident_extraction_allowed']:
        if ev.get(key) is not False:
            errors.append(f"timeline event {ev.get('timeline_event_id')} has {key} not false")
    if ev.get('event_public_display_state') != 'candidate_not_public':
        errors.append(f"timeline event {ev.get('timeline_event_id')} display not blocked")

# Rev0007 gaps and public lines.
gaps_obj = json_data.get('data/source_graph/doj_sls_accession_gap_register.rev0007.json', {})
gaps = gaps_obj.get('gaps', [])
if gaps_obj.get('gap_count') != len(gaps):
    errors.append('gap_count mismatch')
if len(gaps) < 8:
    errors.append('too few rev0007 accession gaps')
for gap in gaps:
    if gap.get('record_kind') != 'accession_gap_nonclaim':
        errors.append(f"gap {gap.get('gap_id')} wrong record_kind")
    for key in ['current_status_claim_admitted','person_extraction_allowed','incident_extraction_allowed']:
        if gap.get(key) is not False:
            errors.append(f"gap {gap.get('gap_id')} has {key} not false")

lines_obj = json_data.get('data/source_graph/doj_sls_public_status_line_candidates.rev0007.json', {})
lines = lines_obj.get('lines', [])
if lines_obj.get('line_count') != len(lines):
    errors.append('public status line_count mismatch')
if lines_obj.get('public_status_claims_admitted') != 0:
    errors.append('public status lines admit claims')
for line in lines:
    if line.get('record_kind') != 'public_status_line_candidate_nonclaim':
        errors.append(f"line {line.get('line_id')} wrong record_kind")
    if line.get('public_current_status_claim_admitted') is not False:
        errors.append(f"line {line.get('line_id')} admits current status")
    if line.get('person_or_incident_display_allowed') is not False:
        errors.append(f"line {line.get('line_id')} allows person/incident display")



# Rev0008 signal-triage and status-proof bundle surfaces.
snap_obj = json_data.get('data/source_graph/doj_sls_source_page_resnapshot.rev0008.json', {})
snap_rows = snap_obj.get('rows', [])
if snap_obj.get('row_count') != len(snap_rows):
    errors.append('rev0008 source-page resnapshot row_count mismatch')
if len(snap_rows) != 11:
    errors.append('rev0008 should have 11 source-page resnapshot rows')
for row in snap_rows:
    if row.get('record_kind') != 'source_page_resnapshot_row_nonclaim':
        errors.append(f"resnapshot row {row.get('resnapshot_id')} wrong record_kind")
    for key in ['source_page_status_label_claim_admitted','current_legal_status_claim_admitted','person_extraction_allowed','incident_extraction_allowed']:
        if row.get(key) is not False:
            errors.append(f"resnapshot row {row.get('resnapshot_id')} has {key} not false")

newsvec_obj = json_data.get('data/source_graph/doj_sls_official_news_signal_vectors.rev0008.json', {})
newsvecs = newsvec_obj.get('vectors', [])
if newsvec_obj.get('vector_count') != len(newsvecs):
    errors.append('rev0008 news vector_count mismatch')
if len(newsvecs) != 7:
    errors.append('rev0008 should have 7 official news signal vectors')
for v in newsvecs:
    if v.get('record_kind') != 'official_news_signal_vector_nonclaim':
        errors.append(f"news vector {v.get('signal_vector_id')} wrong record_kind")
    for key in ['current_legal_status_claim_admitted','public_current_status_claim_admitted','person_extraction_allowed','incident_extraction_allowed']:
        if v.get(key) is not False:
            errors.append(f"news vector {v.get('signal_vector_id')} has {key} not false")

bund_obj = json_data.get('data/source_graph/doj_sls_status_proof_bundles.rev0008.json', {})
bundles = bund_obj.get('bundles', [])
if bund_obj.get('bundle_count') != len(bundles):
    errors.append('rev0008 status bundle_count mismatch')
if len(bundles) != 11:
    errors.append('rev0008 should have 11 status proof bundles')
for b in bundles:
    if b.get('record_kind') != 'status_proof_bundle_nonclaim':
        errors.append(f"status bundle {b.get('bundle_id')} wrong record_kind")
    if not b.get('blocking_conditions'):
        errors.append(f"status bundle {b.get('bundle_id')} missing blocking_conditions")
    for key in ['current_legal_status_claim_admitted','public_current_status_claim_admitted','person_extraction_allowed','incident_extraction_allowed']:
        if b.get(key) is not False:
            errors.append(f"status bundle {b.get('bundle_id')} has {key} not false")

conf_obj = json_data.get('data/source_graph/doj_sls_source_family_signal_conflicts.rev0008.json', {})
conflicts = conf_obj.get('conflicts', [])
if conf_obj.get('conflict_count') != len(conflicts):
    errors.append('rev0008 signal conflict_count mismatch')
if len(conflicts) != len(bundles):
    errors.append('rev0008 conflicts should match status bundles')
for c in conflicts:
    if c.get('record_kind') != 'source_family_signal_conflict_nonclaim':
        errors.append(f"signal conflict {c.get('conflict_id')} wrong record_kind")
    if c.get('public_current_status_claim_admitted') is not False:
        errors.append(f"signal conflict {c.get('conflict_id')} admits public current status")

queue_obj = json_data.get('data/source_graph/doj_sls_source_acquisition_queue.rev0008.json', {})
queue = queue_obj.get('tickets', [])
if queue_obj.get('ticket_count') != len(queue):
    errors.append('rev0008 acquisition queue ticket_count mismatch')
if len(queue) != 10:
    errors.append('rev0008 should have 10 source acquisition tickets')
for q in queue:
    if q.get('record_kind') != 'source_acquisition_queue_ticket_nonclaim':
        errors.append(f"queue ticket {q.get('ticket_id')} wrong record_kind")
    for key in ['current_legal_status_claim_admitted','public_current_status_claim_admitted','person_extraction_allowed','incident_extraction_allowed']:
        if q.get(key) is not False:
            errors.append(f"queue ticket {q.get('ticket_id')} has {key} not false")

pref_obj = json_data.get('data/source_graph/doj_sls_public_department_page_preflight.rev0008.json', {})
prefs = pref_obj.get('cards', [])
if pref_obj.get('preflight_count') != len(prefs):
    errors.append('rev0008 preflight_count mismatch')
if len(prefs) != len(bundles):
    errors.append('rev0008 preflight cards should match status bundles')
for p in prefs:
    if p.get('record_kind') != 'public_department_page_preflight_nonclaim':
        errors.append(f"preflight {p.get('preflight_id')} wrong record_kind")
    for key in ['person_or_incident_display_allowed','current_status_banner_allowed','public_current_status_claim_admitted']:
        if p.get(key) is not False:
            errors.append(f"preflight {p.get('preflight_id')} has {key} not false")

tri_obj = json_data.get('data/source_graph/doj_sls_claim_promotion_triage.rev0008.json', {})
triage = tri_obj.get('rows', [])
if tri_obj.get('triage_count') != len(triage):
    errors.append('rev0008 triage_count mismatch')
if tri_obj.get('claim_promotions_admitted') != 0:
    errors.append('rev0008 admits claim promotions')
if len(triage) != len(bundles):
    errors.append('rev0008 triage rows should match status bundles')
for t in triage:
    if t.get('record_kind') != 'claim_promotion_triage_row_nonclaim':
        errors.append(f"claim triage {t.get('triage_id')} wrong record_kind")
    for key in ['current_legal_status_claim_admitted','public_current_status_claim_admitted','person_extraction_allowed','incident_extraction_allowed']:
        if t.get(key) is not False:
            errors.append(f"claim triage {t.get('triage_id')} has {key} not false")

edge_obj = json_data.get('data/source_graph/doj_sls_rollback_dependency_edges.rev0008.json', {})
edges = edge_obj.get('edges', [])
if edge_obj.get('edge_count') != len(edges):
    errors.append('rev0008 rollback edge_count mismatch')
if len(edges) < 45:
    errors.append('rev0008 should have at least 45 rollback dependency edges')
for e in edges:
    if e.get('record_kind') != 'rollback_dependency_edge':
        errors.append(f"rollback edge {e.get('edge_id')} wrong record_kind")
    if e.get('public_claim_involved') is not False or e.get('person_or_incident_involved') is not False:
        errors.append(f"rollback edge {e.get('edge_id')} involves forbidden public/person state")

# Rev0008 manifest count checks.
count_pairs = [
    ('source_page_resnapshot_rows_admitted_rev0008', len(snap_rows)),
    ('official_news_signal_vectors_admitted_rev0008', len(newsvecs)),
    ('source_family_signal_conflict_rows_rev0008', len(conflicts)),
    ('status_proof_bundles_admitted_rev0008', len(bundles)),
    ('source_acquisition_queue_tickets_rev0008', len(queue)),
    ('public_department_page_preflight_cards_rev0008', len(prefs)),
    ('claim_promotion_triage_rows_rev0008', len(triage)),
    ('rollback_dependency_edges_rev0008', len(edges)),
]
for field, count in count_pairs:
    if manifest.get(field) != count:
        errors.append(f'manifest {field} mismatch')
if manifest.get('public_current_status_claims_admitted') != 0:
    errors.append('rev0008 manifest public_current_status_claims_admitted must be 0')

missing = json_data.get('MISSINGNESS-LEDGER.json', {})
summary = missing.get('summary', {})
for key in ['document_content_summaries_performed','person_records_created','current_status_claims_admitted','docket_order_accessions_performed']:
    if summary.get(key) != 0:
        errors.append(f'missingness ledger {key} expected 0')
if summary.get('official_pdf_url_accessions_performed_rev0007') != len(accessions):
    errors.append('missingness pdf accession count mismatch')
if summary.get('document_effect_atoms_admitted_rev0007') != len(atoms):
    errors.append('missingness proof atom count mismatch')

for field in ['current_legal_status_claims_admitted','public_current_status_claims_admitted','live_person_records','live_incident_records','live_lawsuit_records','live_settlement_records']:
    if manifest.get(field) != 0:
        errors.append(f'manifest {field} expected 0')
if manifest.get('official_pdf_url_accessions_admitted') != len(accessions):
    errors.append('manifest pdf accession count mismatch')
if manifest.get('order_proof_atoms_admitted') != len(atoms):
    errors.append('manifest proof atom count mismatch')
if manifest.get('pdfs_bundled') != 0:
    errors.append('manifest pdfs_bundled must be 0')
if manifest.get('full_document_summaries_admitted') != 0:
    errors.append('manifest full document summaries must be 0')


# Rev0009 page-shell and document-role surfaces.
roles_obj = json_data.get('data/source_graph/doj_sls_document_role_matrix.rev0009.json', {})
role_rows = roles_obj.get('rows', [])
if roles_obj.get('row_count') != len(role_rows):
    errors.append('rev0009 document role row_count mismatch')
if len(role_rows) != len(docs):
    errors.append('rev0009 document role rows should match rev0004 document census rows')
role_doc_ids = {r.get('source_document_id') for r in role_rows}
if role_doc_ids != doc_ids:
    errors.append('rev0009 document role matrix source_document_id set does not match document census')
for r in role_rows:
    if r.get('record_kind') != 'document_role_matrix_row_nonclaim':
        errors.append(f"document role {r.get('role_row_id')} wrong record_kind")
    for key in ['claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed','current_status_claim_admitted','public_current_status_claim_admitted','full_document_summary_admitted']:
        if r.get(key) is not False:
            errors.append(f"document role {r.get('role_row_id')} has {key} not false")
    if r.get('content_summary_state') != 'not_summarized':
        errors.append(f"document role {r.get('role_row_id')} appears summarized")
    if not r.get('document_role_family'):
        errors.append(f"document role {r.get('role_row_id')} missing document_role_family")
    if not r.get('required_before_claim_promotion'):
        errors.append(f"document role {r.get('role_row_id')} missing claim-promotion blockers")

shells_obj = json_data.get('data/source_graph/doj_sls_department_source_inventory_page_shells.rev0009.json', {})
shells = shells_obj.get('shells', [])
if shells_obj.get('shell_count') != len(shells):
    errors.append('rev0009 page shell_count mismatch')
if len(shells) != len(mo):
    errors.append('rev0009 page shells should match matter objects')
for sh in shells:
    if sh.get('record_kind') != 'department_source_inventory_page_shell_nonclaim':
        errors.append(f"page shell {sh.get('page_shell_id')} wrong record_kind")
    for key in ['current_legal_status_claim_admitted','public_current_status_claim_admitted','person_or_incident_display_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed','full_document_summary_admitted']:
        if sh.get(key) is not False:
            errors.append(f"page shell {sh.get('page_shell_id')} has {key} not false")
    if sh.get('page_shell_readiness') != 'internal_preflight_not_public_release':
        errors.append(f"page shell {sh.get('page_shell_id')} readiness not blocked")
    if not sh.get('public_modules_blocked'):
        errors.append(f"page shell {sh.get('page_shell_id')} missing blocked modules")

banners_obj = json_data.get('data/source_graph/doj_sls_missingness_banners.rev0009.json', {})
banners = banners_obj.get('banners', [])
if banners_obj.get('banner_count') != len(banners):
    errors.append('rev0009 missingness banner_count mismatch')
if len(banners) != len(mo):
    errors.append('rev0009 missingness banners should match matter objects')
if banners_obj.get('total_document_labels') != len(docs):
    errors.append('rev0009 total document labels in banners should equal document census count')
for b in banners:
    if b.get('record_kind') != 'source_inventory_missingness_banner_nonclaim':
        errors.append(f"missingness banner {b.get('banner_id')} wrong record_kind")
    for key in ['content_summaries_completed','privacy_scans_completed','person_records_created','incident_records_created','public_current_status_claims_admitted']:
        if b.get(key) != 0:
            errors.append(f"missingness banner {b.get('banner_id')} has {key} not 0")
    for key in ['claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','current_status_claim_admitted']:
        if b.get(key) is not False:
            errors.append(f"missingness banner {b.get('banner_id')} has {key} not false")

perms_obj = json_data.get('data/source_graph/doj_sls_public_page_module_permissions.rev0009.json', {})
perms = perms_obj.get('permissions', [])
if perms_obj.get('permission_count') != len(perms):
    errors.append('rev0009 module permission_count mismatch')
if len(perms) != len(mo) * perms_obj.get('module_count_per_matter', 0):
    errors.append('rev0009 module permissions should equal matter_count * module_count_per_matter')
if perms_obj.get('person_or_incident_display_allowed_count') != 0:
    errors.append('rev0009 module permission object admits person/incident display')
for perm in perms:
    if perm.get('record_kind') != 'public_page_module_permission_nonclaim':
        errors.append(f"module permission {perm.get('permission_id')} wrong record_kind")
    for key in ['current_status_claim_admitted','person_or_incident_display_allowed','full_document_summary_admitted']:
        if perm.get(key) is not False:
            errors.append(f"module permission {perm.get('permission_id')} has {key} not false")
    if perm.get('module_name') in {'current_legal_status_banner','officer_lookup_module','civilian_or_witness_display_module','incident_list_module','lawsuit_merits_module','settlement_amount_module'} and perm.get('permission_state') != 'blocked':
        errors.append(f"module permission {perm.get('permission_id')} should be blocked")

copy_obj = json_data.get('data/source_graph/doj_sls_public_page_copy_blocks.rev0009.json', {})
copy_blocks = copy_obj.get('blocks', [])
if copy_obj.get('copy_block_count') != len(copy_blocks):
    errors.append('rev0009 copy block count mismatch')
if len(copy_blocks) != len(mo):
    errors.append('rev0009 copy blocks should match matter objects')
for block in copy_blocks:
    if block.get('record_kind') != 'claimless_public_page_copy_block_nonclaim':
        errors.append(f"copy block {block.get('copy_block_id')} wrong record_kind")
    if block.get('person_or_incident_display_allowed') is not False:
        errors.append(f"copy block {block.get('copy_block_id')} allows person/incident display")
    if block.get('public_current_status_claim_admitted') is not False:
        errors.append(f"copy block {block.get('copy_block_id')} admits public current status")

review_obj = json_data.get('data/source_graph/doj_sls_source_inventory_review_queue.rev0009.json', {})
review_tickets = review_obj.get('tickets', [])
if review_obj.get('ticket_count') != len(review_tickets):
    errors.append('rev0009 review ticket_count mismatch')
if len(review_tickets) != len(mo):
    errors.append('rev0009 review tickets should match matter objects')
for ticket in review_tickets:
    if ticket.get('record_kind') != 'source_inventory_review_queue_ticket_nonclaim':
        errors.append(f"review ticket {ticket.get('ticket_id')} wrong record_kind")
    for key in ['claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','current_status_claim_admitted']:
        if ticket.get(key) is not False:
            errors.append(f"review ticket {ticket.get('ticket_id')} has {key} not false")
    if not ticket.get('blocked_until_done'):
        errors.append(f"review ticket {ticket.get('ticket_id')} missing blockers")

# Rev0009 manifest count checks.
rev0009_count_pairs = [
    ('document_role_matrix_rows_rev0009', len(role_rows)),
    ('department_source_inventory_page_shells_rev0009', len(shells)),
    ('missingness_banners_rev0009', len(banners)),
    ('public_page_module_permission_rows_rev0009', len(perms)),
    ('public_page_copy_blocks_rev0009', len(copy_blocks)),
    ('source_inventory_review_tickets_rev0009', len(review_tickets)),
]
for field, count in rev0009_count_pairs:
    if manifest.get(field) != count:
        errors.append(f'manifest {field} mismatch')



# Rev0010 agency identity spine checks.
aic_obj = json_data.get('data/source_graph/doj_sls_agency_identity_candidates.rev0010.json', {})
aics = aic_obj.get('candidates', [])
if aic_obj.get('candidate_count') != len(aics):
    errors.append('rev0010 agency identity candidate_count mismatch')
if len(aics) != 30:
    errors.append('rev0010 should have 30 agency identity candidates')
source_rows = {r.get('row_id') for r in rows}
for c in aics:
    if c.get('record_kind') != 'agency_identity_candidate_nonclaim':
        errors.append(f"agency candidate {c.get('agency_identity_candidate_id')} wrong record_kind")
    if c.get('source_row_id') not in source_rows:
        errors.append(f"agency candidate {c.get('agency_identity_candidate_id')} references unknown source row")
    for key in ['canonical_agency_record_created','merge_allowed','public_agency_page_allowed','current_status_banner_allowed','current_legal_status_claim_admitted','misconduct_claim_admitted','officer_entity_creation_allowed','civilian_entity_creation_allowed','person_extraction_allowed','incident_extraction_allowed','lawsuit_merits_extraction_allowed','settlement_amount_extraction_allowed']:
        if c.get(key) is not False:
            errors.append(f"agency candidate {c.get('agency_identity_candidate_id')} has {key} not false")
    if not c.get('required_before_canonical_agency_record'):
        errors.append(f"agency candidate {c.get('agency_identity_candidate_id')} missing promotion requirements")

aic_ids = {c.get('agency_identity_candidate_id') for c in aics}
alias_obj = json_data.get('data/source_graph/doj_sls_agency_alias_packets.rev0010.json', {})
aliases = alias_obj.get('packets', [])
if alias_obj.get('alias_packet_count') != len(aliases):
    errors.append('rev0010 alias_packet_count mismatch')
if len(aliases) != len(aics):
    errors.append('rev0010 alias packets should match agency candidates')
for a in aliases:
    if a.get('record_kind') != 'agency_alias_packet_nonclaim':
        errors.append(f"alias packet {a.get('alias_packet_id')} wrong record_kind")
    if a.get('agency_identity_candidate_id') not in aic_ids:
        errors.append(f"alias packet {a.get('alias_packet_id')} references unknown agency candidate")
    if a.get('alias_merge_allowed') is not False:
        errors.append(f"alias packet {a.get('alias_packet_id')} allows merge")

jsc_obj = json_data.get('data/source_graph/doj_sls_jurisdiction_scaffolds.rev0010.json', {})
jscs = jsc_obj.get('scaffolds', [])
if jsc_obj.get('scaffold_count') != len(jscs):
    errors.append('rev0010 jurisdiction scaffold_count mismatch')
if len(jscs) != len(aics):
    errors.append('rev0010 jurisdiction scaffolds should match agency candidates')
for j in jscs:
    if j.get('record_kind') != 'jurisdiction_scaffold_nonclaim':
        errors.append(f"jurisdiction scaffold {j.get('jurisdiction_scaffold_id')} wrong record_kind")
    if j.get('agency_identity_candidate_id') not in aic_ids:
        errors.append(f"jurisdiction scaffold {j.get('jurisdiction_scaffold_id')} references unknown agency candidate")
    for key in ['public_map_allowed','public_denominator_claim_allowed','current_status_claim_admitted','person_extraction_allowed','incident_extraction_allowed']:
        if j.get(key) is not False:
            errors.append(f"jurisdiction scaffold {j.get('jurisdiction_scaffold_id')} has {key} not false")

bridge_obj = json_data.get('data/source_graph/denominator_source_bridge.rev0010.json', {})
bridges = bridge_obj.get('bridges', [])
if bridge_obj.get('bridge_count') != len(bridges):
    errors.append('rev0010 denominator bridge_count mismatch')
if len(bridges) != 8:
    errors.append('rev0010 should have 8 denominator/source bridge rows')
for b in bridges:
    if b.get('record_kind') != 'denominator_source_bridge_nonclaim':
        errors.append(f"bridge {b.get('bridge_source_id')} wrong record_kind")
    if b.get('claim_admitted') is not False or b.get('person_extraction_allowed') is not False or b.get('incident_extraction_allowed') is not False:
        errors.append(f"bridge {b.get('bridge_source_id')} admits forbidden state")
    if not b.get('what_it_cannot_support'):
        errors.append(f"bridge {b.get('bridge_source_id')} missing cannot-support caveats")

req_obj = json_data.get('data/source_graph/agency_external_id_requirements.rev0010.json', {})
reqs = req_obj.get('requirements', [])
if req_obj.get('requirement_count') != len(reqs):
    errors.append('rev0010 external ID requirement_count mismatch')
if len(reqs) != 10:
    errors.append('rev0010 should have 10 external ID requirements')
for r in reqs:
    if r.get('record_kind') != 'agency_external_identifier_requirement_nonclaim':
        errors.append(f"external id requirement {r.get('requirement_id')} wrong record_kind")
    if r.get('sufficient_alone_for_merge') is not False:
        errors.append(f"external id requirement {r.get('requirement_id')} sufficient alone")

mb_obj = json_data.get('data/source_graph/doj_sls_agency_merge_blockers.rev0010.json', {})
mbs = mb_obj.get('blockers', [])
if mb_obj.get('blocker_count') != len(mbs):
    errors.append('rev0010 merge blocker_count mismatch')
if len(mbs) != 14:
    errors.append('rev0010 should have 14 merge blockers')
for mb in mbs:
    if mb.get('record_kind') != 'agency_merge_blocker_rule':
        errors.append(f"merge blocker {mb.get('merge_blocker_id')} wrong record_kind")

q_obj = json_data.get('data/source_graph/doj_sls_agency_denominator_bridge_queue.rev0010.json', {})
qs = q_obj.get('tickets', [])
if q_obj.get('ticket_count') != len(qs):
    errors.append('rev0010 bridge queue ticket_count mismatch')
if len(qs) != len(aics):
    errors.append('rev0010 bridge queue should match agency candidates')
for q in qs:
    if q.get('record_kind') != 'agency_denominator_bridge_queue_ticket_nonclaim':
        errors.append(f"agency bridge queue {q.get('bridge_ticket_id')} wrong record_kind")
    if q.get('agency_identity_candidate_id') not in aic_ids:
        errors.append(f"agency bridge queue {q.get('bridge_ticket_id')} references unknown agency candidate")
    for key in ['canonical_agency_record_created','public_department_page_allowed','person_extraction_allowed','incident_extraction_allowed','current_status_claim_admitted']:
        if q.get(key) is not False:
            errors.append(f"agency bridge queue {q.get('bridge_ticket_id')} has {key} not false")

pg_obj = json_data.get('data/source_graph/public_agency_page_gates.rev0010.json', {})
pgs = pg_obj.get('gates', [])
if pg_obj.get('gate_count') != len(pgs):
    errors.append('rev0010 public agency page gate_count mismatch')
if len(pgs) != len(aics):
    errors.append('rev0010 page gates should match agency candidates')
if pg_obj.get('public_agency_pages_opened') != 0 or pg_obj.get('public_current_status_claims_admitted') != 0:
    errors.append('rev0010 page gates admit public pages/status')
for g in pgs:
    if g.get('record_kind') != 'public_agency_page_gate_nonclaim':
        errors.append(f"public agency page gate {g.get('public_agency_page_gate_id')} wrong record_kind")
    for key in ['public_agency_page_allowed','current_status_banner_allowed','person_or_incident_display_allowed','denominator_claim_allowed','current_status_claim_admitted','person_extraction_allowed','incident_extraction_allowed']:
        if g.get(key) is not False:
            errors.append(f"public agency page gate {g.get('public_agency_page_gate_id')} has {key} not false")

obs_obj = json_data.get('data/source_graph/official_source_observations.rev0010.json', {})
obs = obs_obj.get('observations', [])
if obs_obj.get('observation_count') != len(obs):
    errors.append('rev0010 official source observation_count mismatch')
if len(obs) != 7:
    errors.append('rev0010 should have 7 official source observations')
for o in obs:
    if o.get('record_kind') != 'official_source_observation_nonclaim':
        errors.append(f"official observation {o.get('observation_id')} wrong record_kind")
    if o.get('claim_admitted') is not False:
        errors.append(f"official observation {o.get('observation_id')} admits claim")

rev0010_count_pairs = [
    ('agency_identity_candidates_rev0010', len(aics)),
    ('agency_alias_packets_rev0010', len(aliases)),
    ('jurisdiction_scaffolds_rev0010', len(jscs)),
    ('denominator_source_bridge_rows_rev0010', len(bridges)),
    ('agency_external_id_requirements_rev0010', len(reqs)),
    ('agency_merge_blocker_rules_rev0010', len(mbs)),
    ('agency_denominator_bridge_queue_tickets_rev0010', len(qs)),
    ('public_agency_page_gate_rows_rev0010', len(pgs)),
    ('official_source_observations_rev0010', len(obs)),
]
for field, count in rev0010_count_pairs:
    if manifest.get(field) != count:
        errors.append(f'manifest {field} mismatch')
for field in ['canonical_agency_records_created','public_denominator_claims_admitted','public_geography_claims_admitted']:
    if manifest.get(field) != 0:
        errors.append(f'manifest {field} expected 0')


# Rev0011 source-freeze and fixity-gate surfaces.
freeze_obj = json_data.get('data/source_graph/doj_sls_document_freeze_queue.rev0011.json', {})
freeze_tickets = freeze_obj.get('tickets', [])
if freeze_obj.get('queue_count') != len(freeze_tickets):
    errors.append('rev0011 document freeze queue_count mismatch')
if len(freeze_tickets) != len(role_rows):
    errors.append('rev0011 document freeze tickets should match rev0009 document role rows')
freeze_doc_ids = {t.get('source_document_id') for t in freeze_tickets}
if freeze_doc_ids != role_doc_ids:
    errors.append('rev0011 freeze ticket document IDs should match document role matrix')
for t in freeze_tickets:
    if t.get('record_kind') != 'document_freeze_queue_ticket_nonclaim':
        errors.append(f"freeze ticket {t.get('freeze_ticket_id')} wrong record_kind")
    if t.get('content_payload_bundled_in_rev0011') is not False:
        errors.append(f"freeze ticket {t.get('freeze_ticket_id')} bundles payload")
    for key in ['claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed','current_status_claim_admitted','public_current_status_claim_admitted','full_document_summary_admitted']:
        if t.get(key) is not False:
            errors.append(f"freeze ticket {t.get('freeze_ticket_id')} has {key} not false")
    if t.get('content_hash_state') != 'not_computed_rev0011_queue_only':
        errors.append(f"freeze ticket {t.get('freeze_ticket_id')} has unexpected hash state")

res_obj = json_data.get('data/source_graph/doj_sls_link_target_resolution_queue.rev0011.json', {})
res_tickets = res_obj.get('tickets', [])
if res_obj.get('ticket_count') != len(res_tickets):
    errors.append('rev0011 link target resolution ticket_count mismatch')
expected_unresolved = [r for r in role_rows if not r.get('official_url_frozen_or_accessioned')]
if len(res_tickets) != len(expected_unresolved):
    errors.append('rev0011 resolution tickets should match unresolved document role rows')
for t in res_tickets:
    if t.get('record_kind') != 'link_target_resolution_ticket_nonclaim':
        errors.append(f"resolution ticket {t.get('resolution_ticket_id')} wrong record_kind")
    for key in ['claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','current_status_claim_admitted']:
        if t.get(key) is not False:
            errors.append(f"resolution ticket {t.get('resolution_ticket_id')} has {key} not false")
    if t.get('target_url_state') != 'not_yet_resolved_from_source_page_link':
        errors.append(f"resolution ticket {t.get('resolution_ticket_id')} already resolved")

matfree_obj = json_data.get('data/source_graph/doj_sls_matter_freeze_debt.rev0011.json', {})
matfree = matfree_obj.get('summaries', [])
if matfree_obj.get('matter_count') != len(matfree):
    errors.append('rev0011 matter freeze debt count mismatch')
if len(matfree) != len(mo):
    errors.append('rev0011 matter freeze debt should match matter objects')
if matfree_obj.get('total_document_labels') != len(role_rows):
    errors.append('rev0011 matter freeze debt total document labels mismatch')
for m in matfree:
    if m.get('record_kind') != 'matter_freeze_debt_summary_nonclaim':
        errors.append(f"matter freeze {m.get('matter_freeze_debt_id')} wrong record_kind")
    if m.get('content_payloads_bundled_in_rev0011') != 0:
        errors.append(f"matter freeze {m.get('matter_freeze_debt_id')} bundles payloads")
    if m.get('public_current_status_claim_admitted') is not False:
        errors.append(f"matter freeze {m.get('matter_freeze_debt_id')} admits public status")

mut_obj = json_data.get('data/source_graph/doj_sls_document_mutation_watch.rev0011.json', {})
mut_rows = mut_obj.get('watches', [])
if mut_obj.get('watch_count') != len(mut_rows):
    errors.append('rev0011 mutation watch_count mismatch')
if len(mut_rows) < 35:
    errors.append('rev0011 mutation watch unexpectedly small')
for w in mut_rows:
    if w.get('record_kind') != 'document_mutation_watch_nonclaim':
        errors.append(f"mutation watch {w.get('mutation_watch_id')} wrong record_kind")
    if not w.get('watch_reasons'):
        errors.append(f"mutation watch {w.get('mutation_watch_id')} missing reasons")
    for key in ['public_current_status_claim_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed']:
        if w.get(key) is not False:
            errors.append(f"mutation watch {w.get('mutation_watch_id')} has {key} not false")

check_obj = json_data.get('data/source_graph/checksum_debt_register.rev0011.json', {})
check_items = check_obj.get('items', [])
if check_obj.get('item_count') != len(check_items):
    errors.append('rev0011 checksum debt item_count mismatch')
if len(check_items) != 29:
    errors.append('rev0011 checksum debt should have 29 items')
if check_obj.get('payload_hashes_computed') != 0 or check_obj.get('payloads_bundled') != 0:
    errors.append('rev0011 checksum debt object incorrectly computes/bundles payloads')
for item in check_items:
    if item.get('record_kind') != 'checksum_debt_item_nonclaim':
        errors.append(f"checksum debt {item.get('checksum_debt_id')} wrong record_kind")
    if item.get('payload_hash_state') != 'not_computed_rev0011_queue_only':
        errors.append(f"checksum debt {item.get('checksum_debt_id')} unexpected hash state")
    if item.get('payload_bundled_in_rev0011') is not False:
        errors.append(f"checksum debt {item.get('checksum_debt_id')} bundles payload")
    for key in ['claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','public_current_status_claim_admitted']:
        if item.get(key) is not False:
            errors.append(f"checksum debt {item.get('checksum_debt_id')} has {key} not false")

sp_obj = json_data.get('data/source_graph/doj_sls_source_page_freeze_targets.rev0011.json', {})
sp_targets = sp_obj.get('targets', [])
if sp_obj.get('target_count') != len(sp_targets):
    errors.append('rev0011 source page freeze target_count mismatch')
if len(sp_targets) != 6:
    errors.append('rev0011 should have 6 source page freeze targets')
for target in sp_targets:
    if target.get('record_kind') != 'source_page_freeze_target_nonclaim':
        errors.append(f"source page target {target.get('source_page_freeze_target_id')} wrong record_kind")
    if target.get('content_payload_bundled_in_rev0011') is not False:
        errors.append(f"source page target {target.get('source_page_freeze_target_id')} bundles payload")
    for key in ['claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','public_current_status_claim_admitted']:
        if target.get(key) is not False:
            errors.append(f"source page target {target.get('source_page_freeze_target_id')} has {key} not false")

pol_obj = json_data.get('data/source_graph/source_preservation_policy_matrix.rev0011.json', {})
policies = pol_obj.get('policies', [])
if pol_obj.get('policy_count') != len(policies):
    errors.append('rev0011 preservation policy_count mismatch')
if len(policies) != 9:
    errors.append('rev0011 should have 9 preservation policy rows')
for pol in policies:
    if pol.get('record_kind') != 'source_preservation_policy_row':
        errors.append(f"preservation policy {pol.get('policy_id')} wrong record_kind")
    for key in ['claim_extraction_allowed_by_policy_row','person_extraction_allowed_by_policy_row','incident_extraction_allowed_by_policy_row','public_current_status_claim_admitted_by_policy_row']:
        if pol.get(key) is not False:
            errors.append(f"preservation policy {pol.get('policy_id')} has {key} not false")

rev0011_count_pairs = [
    ('document_freeze_tickets_rev0011', len(freeze_tickets)),
    ('link_target_resolution_tickets_rev0011', len(res_tickets)),
    ('matter_freeze_debt_summaries_rev0011', len(matfree)),
    ('document_mutation_watch_rows_rev0011', len(mut_rows)),
    ('checksum_debt_items_rev0011', len(check_items)),
    ('source_page_freeze_targets_rev0011', len(sp_targets)),
    ('source_preservation_policy_rows_rev0011', len(policies)),
]
for field, count in rev0011_count_pairs:
    if manifest.get(field) != count:
        errors.append(f'manifest {field} mismatch')
for field in ['payloads_bundled_rev0011','payload_hashes_computed_rev0011','content_summaries_admitted_rev0011']:
    if manifest.get(field) != 0:
        errors.append(f'manifest {field} expected 0')



# Rev0012 link-target resolution, capture manifest, and fixity-state surfaces.
link_obj = json_data.get('data/source_graph/doj_sls_link_target_resolutions.rev0012.json', {})
link_rows = link_obj.get('resolutions', [])
if link_obj.get('resolution_count') != len(link_rows):
    errors.append('rev0012 link target resolution_count mismatch')
if len(link_rows) != 12:
    errors.append('rev0012 should have 12 link-target resolution rows')
new_res = [r for r in link_rows if r.get('resolution_state') == 'new_source_page_pdf_url_resolution_rev0012']
reconf = [r for r in link_rows if r.get('resolution_state') == 'reconfirmed_prior_rev0007_accession']
failed = [r for r in link_rows if 'fetch_failed' in (r.get('resolution_state') or '')]
if len(new_res) != 3:
    errors.append('rev0012 should have 3 new source-page PDF URL resolutions')
if len(reconf) != 8:
    errors.append('rev0012 should reconfirm 8 prior PDF accessions')
if len(failed) != 1:
    errors.append('rev0012 should have 1 fetch-anomaly row')
for r in link_rows:
    if r.get('record_kind') != 'resolved_link_target_nonclaim':
        errors.append(f"link resolution {r.get('resolution_id')} wrong record_kind")
    for key in ['payload_captured','payload_hash_computed','payload_bundled','content_summary_admitted','document_effect_claim_admitted','current_legal_status_claim_admitted','public_current_status_claim_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed','privacy_scan_completed']:
        if r.get(key) is not False:
            errors.append(f"link resolution {r.get('resolution_id')} has {key} not false")
    if r.get('source_document_id') and r.get('source_document_id') not in doc_ids:
        errors.append(f"link resolution {r.get('resolution_id')} references unknown source document")

news_obj = json_data.get('data/source_graph/doj_sls_official_news_resnapshots.rev0012.json', {})
news_rows = news_obj.get('resnapshots', [])
if news_obj.get('resnapshot_count') != len(news_rows):
    errors.append('rev0012 official news resnapshot_count mismatch')
if len(news_rows) != 7:
    errors.append('rev0012 should have 7 official news resnapshots')
for n in news_rows:
    if n.get('record_kind') != 'official_news_resnapshot_nonclaim':
        errors.append(f"news resnapshot {n.get('news_resnapshot_id')} wrong record_kind")
    for key in ['payload_captured','payload_hash_computed','content_summary_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','current_legal_status_claim_admitted','public_current_status_claim_admitted']:
        if n.get(key) is not False:
            errors.append(f"news resnapshot {n.get('news_resnapshot_id')} has {key} not false")

cap_obj = json_data.get('data/source_graph/source_capture_manifest.rev0012.json', {})
cap_targets = cap_obj.get('targets', [])
if cap_obj.get('target_count') != len(cap_targets):
    errors.append('rev0012 capture target_count mismatch')
if len(cap_targets) != 21:
    errors.append('rev0012 should have 21 capture manifest targets')
if cap_obj.get('payloads_captured') != 0 or cap_obj.get('payload_hashes_computed') != 0:
    errors.append('rev0012 capture manifest should not capture/hash payloads')
for c in cap_targets:
    if c.get('record_kind') != 'source_capture_manifest_target_nonclaim':
        errors.append(f"capture target {c.get('capture_manifest_id')} wrong record_kind")
    for key in ['payload_captured','payload_hash_computed','payload_bundled','privacy_scan_completed','content_summary_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','current_legal_status_claim_admitted','public_current_status_claim_admitted']:
        if c.get(key) is not False:
            errors.append(f"capture target {c.get('capture_manifest_id')} has {key} not false")

fix_obj = json_data.get('data/source_graph/fixity_state_machine.rev0012.json', {})
fix_states = fix_obj.get('states', [])
if fix_obj.get('state_count') != len(fix_states):
    errors.append('rev0012 fixity state_count mismatch')
if len(fix_states) != 10:
    errors.append('rev0012 should have 10 fixity states')
if fix_obj.get('payload_states_opened_rev0012') != 0 or fix_obj.get('claim_review_states_opened_rev0012') != 0:
    errors.append('rev0012 fixity state machine opens payload/claim states')
for s in fix_states:
    if s.get('record_kind') != 'fixity_state_definition':
        errors.append(f"fixity state {s.get('fixity_state_id')} wrong record_kind")
    if s.get('public_current_status_claim_admitted_at_this_state') is not False:
        errors.append(f"fixity state {s.get('fixity_state_id')} admits public status")
    if s.get('person_extraction_allowed_at_this_state') is not False or s.get('incident_extraction_allowed_at_this_state') is not False:
        errors.append(f"fixity state {s.get('fixity_state_id')} allows person/incident extraction")

trig_obj = json_data.get('data/source_graph/source_recheck_triggers.rev0012.json', {})
trigs = trig_obj.get('triggers', [])
if trig_obj.get('trigger_count') != len(trigs):
    errors.append('rev0012 trigger_count mismatch')
if len(trigs) != 10:
    errors.append('rev0012 should have 10 recheck triggers')
for t in trigs:
    if t.get('record_kind') != 'source_recheck_trigger_nonclaim':
        errors.append(f"trigger {t.get('trigger_id')} wrong record_kind")
    for key in ['claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','current_legal_status_claim_admitted','public_current_status_claim_admitted']:
        if t.get(key) is not False:
            errors.append(f"trigger {t.get('trigger_id')} has {key} not false")

badge_obj = json_data.get('data/source_graph/public_citation_badge_candidates.rev0012.json', {})
badges = badge_obj.get('badges', [])
if badge_obj.get('badge_count') != len(badges):
    errors.append('rev0012 badge_count mismatch')
if len(badges) != 8:
    errors.append('rev0012 should have 8 badge candidates')
for b in badges:
    if b.get('record_kind') != 'public_citation_badge_candidate_nonclaim':
        errors.append(f"badge {b.get('badge_id')} wrong record_kind")
    for key in ['claim_extraction_allowed','person_or_incident_display_allowed','current_status_banner_allowed','public_current_status_claim_admitted']:
        if b.get(key) is not False:
            errors.append(f"badge {b.get('badge_id')} has {key} not false")

delta = json_data.get('data/source_graph/resolution_debt_delta.rev0012.json', {})
if delta.get('record_kind') != 'resolution_debt_delta_nonclaim':
    errors.append('rev0012 resolution debt delta wrong record_kind')
if delta.get('new_source_page_document_urls_resolved_rev0012') != 3:
    errors.append('rev0012 resolution debt delta should record 3 new source-page urls')
for key in ['payloads_captured','payload_hashes_computed','payloads_bundled','content_summaries_admitted','public_current_status_claims_admitted','person_records_created','incident_records_created']:
    if delta.get(key) != 0:
        errors.append(f'rev0012 resolution debt delta {key} expected 0')

rev0012_count_pairs = [
    ('link_target_resolution_rows_rev0012', len(link_rows)),
    ('source_page_link_targets_observed_rev0012', link_obj.get('source_page_link_targets_observed')),
    ('new_source_page_pdf_url_resolutions_rev0012', len(new_res)),
    ('prior_pdf_accessions_reconfirmed_rev0012', len(reconf)),
    ('official_news_resnapshots_rev0012', len(news_rows)),
    ('capture_manifest_targets_rev0012', len(cap_targets)),
    ('fixity_state_definitions_rev0012', len(fix_states)),
    ('source_recheck_triggers_rev0012', len(trigs)),
    ('public_citation_badge_candidates_rev0012', len(badges)),
]
for field, count in rev0012_count_pairs:
    if manifest.get(field) != count:
        errors.append(f'manifest {field} mismatch')
for field in ['payloads_captured_rev0012','payload_hashes_computed_rev0012','payloads_bundled_rev0012','content_summaries_admitted_rev0012','person_records_created_rev0012','incident_records_created_rev0012','public_current_status_claims_admitted_rev0012']:
    if manifest.get(field) != 0:
        errors.append(f'manifest {field} expected 0')


# Rev0013 payload-intake, privacy preflight, and capture-batch gates.
REQUIRED += [
    'PAYLOAD-INTAKE-ENVELOPE-LEDGER.json', 'PRIVACY-PREFLIGHT-LEDGER.json',
    'CAPTURE-BATCH-LEDGER.json', 'EXTRACTIVE-ACTION-GATE-LEDGER.json',
    'CUSTODY-SIDECAR-TEMPLATE-LEDGER.json', 'RELEASE-REDACTION-MATRIX-LEDGER.json',
    'CAPTURE-FAILURE-MODE-LEDGER.json',
    'data/source_graph/payload_intake_envelopes.rev0013.json',
    'data/source_graph/privacy_preflight_queue.rev0013.json',
    'data/source_graph/capture_operator_batches.rev0013.json',
    'data/source_graph/source_capture_order.rev0013.json',
    'data/source_graph/extractive_action_gates.rev0013.json',
    'data/source_graph/custody_sidecar_templates.rev0013.json',
    'data/source_graph/release_redaction_matrix.rev0013.json',
    'data/source_graph/capture_failure_modes.rev0013.json',
    'schemas/payload_intake_envelope.schema.json', 'schemas/privacy_preflight_queue_row.schema.json',
    'schemas/capture_operator_batch.schema.json', 'schemas/extractive_action_gate.schema.json',
    'schemas/custody_sidecar_template.schema.json', 'schemas/source_capture_order_row.schema.json',
    'schemas/release_redaction_matrix_row.schema.json', 'schemas/capture_failure_mode.schema.json',
    'docs/50-pilot/rev0013-payload-intake-envelope-report.md',
    'docs/50-pilot/privacy-preflight-method-rev0013.md',
    'docs/50-pilot/capture-batch-plan-rev0013.md',
    'docs/50-pilot/extractive-action-gate-rev0013.md',
    'docs/50-pilot/custody-sidecar-template-rev0013.md',
    'docs/60-display/private-vs-public-source-custody-rev0013.md',
    'docs/70-examples/rev0013-sample-payload-envelope-nopd.md',
    'docs/80-ops/rev0013-capture-operator-runbook.md',
    'docs/80-ops/rev0013-redaction-operator-checklist.md',
]

# Late required-file check for rev0013 additions.
for rel in REQUIRED:
    if not (ROOT / rel).exists() and f'missing required file: {rel}' not in errors:
        errors.append(f'missing required file: {rel}')

cap_obj_0012 = json_data.get('data/source_graph/source_capture_manifest.rev0012.json', {})
cap_targets_0012 = cap_obj_0012.get('targets', [])
cap_ids_0012 = {c.get('capture_manifest_id') for c in cap_targets_0012}

env_obj = json_data.get('data/source_graph/payload_intake_envelopes.rev0013.json', {})
envs = env_obj.get('envelopes', [])
if env_obj.get('envelope_count') != len(envs):
    errors.append('rev0013 payload envelope_count mismatch')
if len(envs) != len(cap_targets_0012):
    errors.append('rev0013 payload envelopes should match capture manifest targets')
for e in envs:
    if e.get('record_kind') != 'payload_intake_envelope_nonclaim':
        errors.append(f"payload envelope {e.get('payload_envelope_id')} wrong record_kind")
    if e.get('capture_manifest_id') not in cap_ids_0012:
        errors.append(f"payload envelope {e.get('payload_envelope_id')} references unknown capture_manifest_id")
    for key in ['payload_captured','payload_hash_computed','payload_bundled','payload_publicly_displayable','privacy_scan_completed','content_summary_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed','current_legal_status_claim_admitted','public_current_status_claim_admitted']:
        if e.get(key) is not False:
            errors.append(f"payload envelope {e.get('payload_envelope_id')} has {key} not false")

pref_obj_13 = json_data.get('data/source_graph/privacy_preflight_queue.rev0013.json', {})
pref_rows_13 = pref_obj_13.get('queue', [])
if pref_obj_13.get('queue_count') != len(pref_rows_13):
    errors.append('rev0013 privacy preflight queue_count mismatch')
if len(pref_rows_13) != len(envs):
    errors.append('rev0013 privacy rows should match payload envelopes')
for p13 in pref_rows_13:
    if p13.get('record_kind') != 'privacy_preflight_queue_row_nonclaim':
        errors.append(f"privacy preflight {p13.get('privacy_preflight_id')} wrong record_kind")
    for key in ['automatic_publication_allowed','scan_completed','payload_captured','payload_hash_computed','content_summary_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed','current_legal_status_claim_admitted','public_current_status_claim_admitted']:
        if p13.get(key) is not False:
            errors.append(f"privacy preflight {p13.get('privacy_preflight_id')} has {key} not false")

batch_obj_13 = json_data.get('data/source_graph/capture_operator_batches.rev0013.json', {})
batches_13 = batch_obj_13.get('batches', [])
if batch_obj_13.get('batch_count') != len(batches_13):
    errors.append('rev0013 capture batch_count mismatch')
if len(batches_13) != 6:
    errors.append('rev0013 should have 6 capture operator batches')
if batch_obj_13.get('target_count_total') != len(cap_targets_0012):
    errors.append('rev0013 batch target_count_total should equal capture manifest targets')
for b13 in batches_13:
    if b13.get('record_kind') != 'capture_operator_batch_nonclaim':
        errors.append(f"capture batch {b13.get('batch_id')} wrong record_kind")
    for key in ['payloads_captured','payload_hashes_computed','payloads_bundled','content_summaries_admitted']:
        if b13.get(key) != 0:
            errors.append(f"capture batch {b13.get('batch_id')} has {key} not 0")
    for key in ['claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','current_legal_status_claim_admitted','public_current_status_claim_admitted']:
        if b13.get(key) is not False:
            errors.append(f"capture batch {b13.get('batch_id')} has {key} not false")

order_obj_13 = json_data.get('data/source_graph/source_capture_order.rev0013.json', {})
order_rows_13 = order_obj_13.get('rows', [])
if order_obj_13.get('order_row_count') != len(order_rows_13):
    errors.append('rev0013 source capture order count mismatch')
if len(order_rows_13) != len(cap_targets_0012):
    errors.append('rev0013 source capture order should cover all capture targets')
for o13 in order_rows_13:
    if o13.get('record_kind') != 'source_capture_order_row_nonclaim':
        errors.append(f"source capture order {o13.get('capture_order_id')} wrong record_kind")
    for key in ['payload_capture_completed','payload_hash_computed','payload_bundled','privacy_scan_completed','content_summary_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','current_legal_status_claim_admitted','public_current_status_claim_admitted']:
        if o13.get(key) is not False:
            errors.append(f"source capture order {o13.get('capture_order_id')} has {key} not false")

gate_obj_13 = json_data.get('data/source_graph/extractive_action_gates.rev0013.json', {})
gates_13 = gate_obj_13.get('gates', [])
if gate_obj_13.get('gate_count') != len(gates_13):
    errors.append('rev0013 extractive action gate_count mismatch')
if len(gates_13) != 13:
    errors.append('rev0013 should have 13 extractive action gates')
for g13 in gates_13:
    if g13.get('record_kind') != 'extractive_action_gate_nonclaim':
        errors.append(f"extractive gate {g13.get('gate_id')} wrong record_kind")
    for key in ['action_performed_rev0013','payload_captured','payload_hash_computed','payload_bundled','content_summary_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed','current_legal_status_claim_admitted','public_current_status_claim_admitted']:
        if g13.get(key) is not False:
            errors.append(f"extractive gate {g13.get('gate_id')} has {key} not false")

tmpl_obj_13 = json_data.get('data/source_graph/custody_sidecar_templates.rev0013.json', {})
tmpls_13 = tmpl_obj_13.get('templates', [])
if tmpl_obj_13.get('template_count') != len(tmpls_13):
    errors.append('rev0013 custody sidecar template_count mismatch')
if len(tmpls_13) != 7:
    errors.append('rev0013 should have 7 sidecar templates')
if tmpl_obj_13.get('instances_created_rev0013') != 0:
    errors.append('rev0013 should create no live sidecar instances')
for st13 in tmpls_13:
    if st13.get('record_kind') != 'custody_sidecar_template_nonclaim':
        errors.append(f"sidecar template {st13.get('sidecar_template_id')} wrong record_kind")
    for key in ['public_release_allowed_without_review','payload_captured','payload_hash_computed','payload_bundled','content_summary_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','current_legal_status_claim_admitted','public_current_status_claim_admitted']:
        if st13.get(key) is not False:
            errors.append(f"sidecar template {st13.get('sidecar_template_id')} has {key} not false")

red_obj_13 = json_data.get('data/source_graph/release_redaction_matrix.rev0013.json', {})
red_rows_13 = red_obj_13.get('rules', [])
if red_obj_13.get('rule_count') != len(red_rows_13):
    errors.append('rev0013 release redaction rule_count mismatch')
if len(red_rows_13) != 10:
    errors.append('rev0013 should have 10 release redaction rules')
for r13 in red_rows_13:
    if r13.get('record_kind') != 'release_redaction_matrix_row_nonclaim':
        errors.append(f"redaction rule {r13.get('redaction_rule_id')} wrong record_kind")
    for key in ['public_display_allowed_without_privacy_scan','payload_bundled','content_summary_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed','current_legal_status_claim_admitted','public_current_status_claim_admitted']:
        if r13.get(key) is not False:
            errors.append(f"redaction rule {r13.get('redaction_rule_id')} has {key} not false")

fm_obj_13 = json_data.get('data/source_graph/capture_failure_modes.rev0013.json', {})
fms_13 = fm_obj_13.get('failure_modes', [])
if fm_obj_13.get('failure_mode_count') != len(fms_13):
    errors.append('rev0013 failure mode count mismatch')
if len(fms_13) != 12:
    errors.append('rev0013 should have 12 capture failure modes')
for f13 in fms_13:
    if f13.get('record_kind') != 'capture_failure_mode_nonclaim':
        errors.append(f"failure mode {f13.get('failure_mode_id')} wrong record_kind")
    for key in ['claim_extraction_allowed_after_failure','person_extraction_allowed_after_failure','incident_extraction_allowed_after_failure','current_legal_status_claim_admitted_after_failure','public_current_status_claim_admitted_after_failure','payload_bundled','content_summary_admitted']:
        if f13.get(key) is not False:
            errors.append(f"failure mode {f13.get('failure_mode_id')} has {key} not false")

rev0013_count_pairs = [
    ('payload_intake_envelopes_rev0013', len(envs)),
    ('privacy_preflight_rows_rev0013', len(pref_rows_13)),
    ('capture_operator_batches_rev0013', len(batches_13)),
    ('source_capture_order_rows_rev0013', len(order_rows_13)),
    ('extractive_action_gates_rev0013', len(gates_13)),
    ('custody_sidecar_templates_rev0013', len(tmpls_13)),
    ('release_redaction_rules_rev0013', len(red_rows_13)),
    ('capture_failure_modes_rev0013', len(fms_13)),
]
for field, count in rev0013_count_pairs:
    if manifest.get(field) != count:
        errors.append(f'manifest {field} mismatch')
for field in ['payloads_captured_rev0013','payload_hashes_computed_rev0013','payloads_bundled_rev0013','content_summaries_admitted_rev0013','person_records_created_rev0013','incident_records_created_rev0013','public_current_status_claims_admitted_rev0013']:
    if manifest.get(field) != 0:
        errors.append(f'manifest {field} expected 0')


# Rev0014 source-page anchor, diff sentinel, document-link anchor, provenance and change-gate surfaces.
anchor_obj_14 = json_data.get('data/source_graph/doj_sls_source_page_anchor_observations.rev0014.json', {})
anchor_obs_14 = anchor_obj_14.get('observations', [])
if anchor_obj_14.get('anchor_observation_count') != len(anchor_obs_14):
    errors.append('rev0014 anchor observation count mismatch')
if len(anchor_obs_14) != len(mo):
    errors.append('rev0014 anchor observations should match matter objects')
for a14 in anchor_obs_14:
    if a14.get('record_kind') != 'source_page_anchor_observation_nonclaim':
        errors.append(f"rev0014 anchor {a14.get('anchor_observation_id')} wrong record_kind")
    if a14.get('source_row_id') not in source_rows:
        errors.append(f"rev0014 anchor {a14.get('anchor_observation_id')} references unknown source row")
    if not a14.get('source_page_line_span_observed_rev0014'):
        errors.append(f"rev0014 anchor {a14.get('anchor_observation_id')} missing line span")
    for key in ['payload_captured','payload_hash_computed','payload_bundled','content_summary_admitted','source_page_delta_claim_admitted','current_legal_status_claim_admitted','public_current_status_claim_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed','public_display_allowed']:
        if a14.get(key) is not False:
            errors.append(f"rev0014 anchor {a14.get('anchor_observation_id')} has {key} not false")

sent_obj_14 = json_data.get('data/source_graph/doj_sls_source_page_diff_sentinels.rev0014.json', {})
sentinels_14 = sent_obj_14.get('sentinels', [])
if sent_obj_14.get('sentinel_count') != len(sentinels_14):
    errors.append('rev0014 sentinel count mismatch')
if len(sentinels_14) != len(mo):
    errors.append('rev0014 diff sentinels should match matter objects')
if sent_obj_14.get('structural_deltas_observed_rev0014') != 0 or sent_obj_14.get('public_delta_notes_admitted_rev0014') != 0:
    errors.append('rev0014 admits structural deltas or public delta notes')
for s14 in sentinels_14:
    if s14.get('record_kind') != 'source_page_diff_sentinel_nonclaim':
        errors.append(f"rev0014 diff sentinel {s14.get('diff_sentinel_id')} wrong record_kind")
    if s14.get('structural_delta_observed_rev0014') is not False or s14.get('delta_assertion_allowed') is not False:
        errors.append(f"rev0014 diff sentinel {s14.get('diff_sentinel_id')} admits delta/claim")
    for key in ['payload_captured','payload_hash_computed','content_summary_admitted','current_legal_status_claim_admitted','public_current_status_claim_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','public_change_note_allowed']:
        if s14.get(key) is not False:
            errors.append(f"rev0014 diff sentinel {s14.get('diff_sentinel_id')} has {key} not false")

link_anchor_obj_14 = json_data.get('data/source_graph/doj_sls_document_link_anchor_map.rev0014.json', {})
link_anchors_14 = link_anchor_obj_14.get('anchors', [])
if link_anchor_obj_14.get('document_link_anchor_count') != len(link_anchors_14):
    errors.append('rev0014 document link anchor count mismatch')
if len(link_anchors_14) != len(docs):
    errors.append('rev0014 document link anchors should match document census')
link_anchor_doc_ids_14 = {la.get('source_document_id') for la in link_anchors_14}
if link_anchor_doc_ids_14 != doc_ids:
    errors.append('rev0014 link anchor document IDs should match document census')
for la14 in link_anchors_14:
    if la14.get('record_kind') != 'document_link_anchor_map_row_nonclaim':
        errors.append(f"rev0014 document link anchor {la14.get('document_link_anchor_id')} wrong record_kind")
    for key in ['payload_captured','payload_hash_computed','payload_bundled','privacy_scan_completed','content_summary_admitted','document_effect_claim_admitted','current_legal_status_claim_admitted','public_current_status_claim_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','officer_entity_creation_allowed','civilian_entity_creation_allowed','public_display_allowed']:
        if la14.get(key) is not False:
            errors.append(f"rev0014 document link anchor {la14.get('document_link_anchor_id')} has {key} not false")

fresh_obj_14 = json_data.get('data/source_graph/doj_sls_status_label_freshness_tiers.rev0014.json', {})
fresh_14 = fresh_obj_14.get('tiers', [])
if fresh_obj_14.get('tier_count') != len(fresh_14):
    errors.append('rev0014 freshness tier count mismatch')
if len(fresh_14) != len(mo):
    errors.append('rev0014 freshness tiers should match matter objects')
if fresh_obj_14.get('public_status_displays_allowed_rev0014') != 0 or fresh_obj_14.get('current_legal_status_claims_admitted') != 0:
    errors.append('rev0014 freshness tiers admit status display/claims')
for f14 in fresh_14:
    if f14.get('record_kind') != 'status_label_freshness_tier_nonclaim':
        errors.append(f"rev0014 freshness tier {f14.get('freshness_tier_id')} wrong record_kind")
    for key in ['current_legal_status_claim_admitted','public_current_status_claim_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','public_status_display_allowed']:
        if f14.get(key) is not False:
            errors.append(f"rev0014 freshness tier {f14.get('freshness_tier_id')} has {key} not false")

ready_obj_14 = json_data.get('data/source_graph/source_page_section_capture_readiness.rev0014.json', {})
readiness_14 = ready_obj_14.get('readiness', [])
if ready_obj_14.get('readiness_count') != len(readiness_14):
    errors.append('rev0014 capture readiness count mismatch')
if len(readiness_14) != 8:
    errors.append('rev0014 should have 8 capture readiness rows')
if ready_obj_14.get('payloads_captured') != 0 or ready_obj_14.get('payload_hashes_computed') != 0:
    errors.append('rev0014 capture readiness should not capture/hash payloads')
for cr14 in readiness_14:
    if cr14.get('record_kind') != 'source_page_section_capture_readiness_nonclaim':
        errors.append(f"rev0014 capture readiness {cr14.get('readiness_id')} wrong record_kind")
    if cr14.get('ready_for_public_display') is not False:
        errors.append(f"rev0014 capture readiness {cr14.get('readiness_id')} ready for public display")
    for key in ['payload_captured','payload_hash_computed','payload_bundled','content_summary_admitted','current_legal_status_claim_admitted','public_current_status_claim_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed']:
        if cr14.get(key) is not False:
            errors.append(f"rev0014 capture readiness {cr14.get('readiness_id')} has {key} not false")

change_obj_14 = json_data.get('data/source_graph/public_change_note_candidates.rev0014.json', {})
change_notes_14 = change_obj_14.get('candidates', [])
if change_obj_14.get('change_note_candidate_count') != len(change_notes_14):
    errors.append('rev0014 change-note count mismatch')
if len(change_notes_14) != 10:
    errors.append('rev0014 should have 10 change-note candidates')
if change_obj_14.get('public_change_notes_admitted_rev0014') != 0:
    errors.append('rev0014 admits public change notes')
for cn14 in change_notes_14:
    if cn14.get('record_kind') != 'public_change_note_candidate_nonclaim':
        errors.append(f"rev0014 change note {cn14.get('change_note_candidate_id')} wrong record_kind")
    if cn14.get('allowed_before_publication') is not False:
        errors.append(f"rev0014 change note {cn14.get('change_note_candidate_id')} allowed before publication")
    for key in ['content_summary_admitted','current_legal_status_claim_admitted','public_current_status_claim_admitted','person_or_incident_display_allowed','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed']:
        if cn14.get(key) is not False:
            errors.append(f"rev0014 change note {cn14.get('change_note_candidate_id')} has {key} not false")

gate_obj_14 = json_data.get('data/source_graph/source_page_delta_assertion_gates.rev0014.json', {})
delta_gates_14 = gate_obj_14.get('gates', [])
if gate_obj_14.get('gate_count') != len(delta_gates_14):
    errors.append('rev0014 delta gate count mismatch')
if len(delta_gates_14) != 12:
    errors.append('rev0014 should have 12 delta assertion gates')
if gate_obj_14.get('public_delta_claims_admitted_rev0014') != 0:
    errors.append('rev0014 admits public delta claims')
for dg14 in delta_gates_14:
    if dg14.get('record_kind') != 'source_page_delta_assertion_gate':
        errors.append(f"rev0014 delta gate {dg14.get('delta_gate_id')} wrong record_kind")
    for key in ['claim_extraction_allowed_by_gate','person_extraction_allowed_by_gate','incident_extraction_allowed_by_gate','current_legal_status_claim_admitted_by_gate','public_current_status_claim_admitted_by_gate']:
        if dg14.get(key) is not False:
            errors.append(f"rev0014 delta gate {dg14.get('delta_gate_id')} has {key} not false")

obs_obj_14 = json_data.get('data/provenance/source_observation_events.rev0014.json', {})
obs_events_14 = obs_obj_14.get('events', [])
if obs_obj_14.get('event_count') != len(obs_events_14):
    errors.append('rev0014 source observation event count mismatch')
if len(obs_events_14) != 6:
    errors.append('rev0014 should have 6 source observation events')
for so14 in obs_events_14:
    if so14.get('record_kind') != 'source_observation_event_nonclaim':
        errors.append(f"rev0014 source observation {so14.get('source_observation_event_id')} wrong record_kind")
    for key in ['payload_captured','payload_hash_computed','current_status_claim_admitted']:
        if so14.get(key) is not False:
            errors.append(f"rev0014 source observation {so14.get('source_observation_event_id')} has {key} not false")

prov_obj_14 = json_data.get('data/provenance/provenance_activity_templates.rev0014.json', {})
prov_templates_14 = prov_obj_14.get('templates', [])
if prov_obj_14.get('template_count') != len(prov_templates_14):
    errors.append('rev0014 provenance template count mismatch')
if len(prov_templates_14) != 9:
    errors.append('rev0014 should have 9 provenance activity templates')
if prov_obj_14.get('instances_created_rev0014') != 0:
    errors.append('rev0014 should instantiate no provenance activities')
for pt14 in prov_templates_14:
    if pt14.get('record_kind') != 'provenance_activity_template_nonclaim':
        errors.append(f"rev0014 provenance template {pt14.get('activity_template_id')} wrong record_kind")
    for key in ['payload_captured','payload_hash_computed','content_summary_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed','public_current_status_claim_admitted']:
        if pt14.get(key) is not False:
            errors.append(f"rev0014 provenance template {pt14.get('activity_template_id')} has {key} not false")

vw_obj_14 = json_data.get('data/source_graph/volatile_source_family_watch.rev0014.json', {})
vw_rows_14 = vw_obj_14.get('watches', [])
if vw_obj_14.get('watch_count') != len(vw_rows_14):
    errors.append('rev0014 volatile watch count mismatch')
if len(vw_rows_14) != 7:
    errors.append('rev0014 should have 7 volatile source-family watches')
for vw14 in vw_rows_14:
    if vw14.get('record_kind') != 'volatile_source_family_watch_nonclaim':
        errors.append(f"rev0014 volatile watch {vw14.get('volatile_watch_id')} wrong record_kind")
    for key in ['public_current_status_claim_admitted','claim_extraction_allowed','person_extraction_allowed','incident_extraction_allowed']:
        if vw14.get(key) is not False:
            errors.append(f"rev0014 volatile watch {vw14.get('volatile_watch_id')} has {key} not false")

rev0014_count_pairs = [
    ('source_page_anchor_observations_rev0014', len(anchor_obs_14)),
    ('source_page_diff_sentinels_rev0014', len(sentinels_14)),
    ('document_link_anchor_rows_rev0014', len(link_anchors_14)),
    ('status_label_freshness_tiers_rev0014', len(fresh_14)),
    ('source_page_section_capture_readiness_rows_rev0014', len(readiness_14)),
    ('public_change_note_candidates_rev0014', len(change_notes_14)),
    ('source_page_delta_assertion_gates_rev0014', len(delta_gates_14)),
    ('source_observation_events_rev0014', len(obs_events_14)),
    ('provenance_activity_templates_rev0014', len(prov_templates_14)),
    ('volatile_source_family_watches_rev0014', len(vw_rows_14)),
]
for field, count in rev0014_count_pairs:
    if manifest.get(field) != count:
        errors.append(f'manifest {field} mismatch')
for field in ['structural_deltas_observed_rev0014','public_delta_notes_admitted_rev0014','payloads_captured_rev0014','payload_hashes_computed_rev0014','payloads_bundled_rev0014','content_summaries_admitted_rev0014','person_records_created_rev0014','incident_records_created_rev0014','public_current_status_claims_admitted_rev0014']:
    if manifest.get(field) != 0:
        errors.append(f'manifest {field} expected 0')


# Rev0015 telos, dream, reentry-office, and open-horizon foundation surfaces.
telos_obj_15 = json_data.get('TELOS-CHARTER-LEDGER.json', {})
telos_rows_15 = telos_obj_15.get('statements', [])
if telos_obj_15.get('statement_count') != len(telos_rows_15):
    errors.append('rev0015 telos statement_count mismatch')
if len(telos_rows_15) < 10:
    errors.append('rev0015 should have at least 10 telos statements')
if telos_obj_15.get('public_claims_admitted_rev0015') != 0:
    errors.append('rev0015 telos admits public claims')
for t15 in telos_rows_15:
    if not t15.get('id') or not t15.get('statement'):
        errors.append('rev0015 telos statement missing id/statement')

dream_obj_15 = json_data.get('DREAM-REGISTER.json', {})
dream_rows_15 = dream_obj_15.get('dreams', [])
if dream_obj_15.get('dream_count') != len(dream_rows_15):
    errors.append('rev0015 dream_count mismatch')
if len(dream_rows_15) < 15:
    errors.append('rev0015 should have at least 15 dream entries')
if dream_obj_15.get('public_claims_admitted_rev0015') != 0:
    errors.append('rev0015 dreams admit public claims')
for d15 in dream_rows_15:
    if d15.get('record_kind') != 'dream_register_entry_not_commitment_not_claim':
        errors.append(f"rev0015 dream {d15.get('dream_id')} wrong record_kind")
    if d15.get('commitment_state') != 'open_horizon_not_implementation_commitment':
        errors.append(f"rev0015 dream {d15.get('dream_id')} not marked noncommitment")
    for key in ['public_claim_admitted','person_record_creation_allowed','incident_record_creation_allowed']:
        if d15.get(key) is not False:
            errors.append(f"rev0015 dream {d15.get('dream_id')} has {key} not false")

ladder_obj_15 = json_data.get('EARNED-CAPABILITY-LADDER.json', {})
rungs_15 = ladder_obj_15.get('rungs', [])
if ladder_obj_15.get('rung_count') != len(rungs_15):
    errors.append('rev0015 rung_count mismatch')
if len(rungs_15) < 12:
    errors.append('rev0015 should have at least 12 earned capability rungs')
for r15 in rungs_15:
    if r15.get('record_kind') != 'earned_capability_rung':
        errors.append(f"rev0015 rung {r15.get('rung_id')} wrong record_kind")
    if r15.get('public_claim_admitted_rev0015') is not False:
        errors.append(f"rev0015 rung {r15.get('rung_id')} admits public claim")

reentry_obj_15 = json_data.get('FUTURE-SESSION-REENTRY-OFFICE.json', {})
if reentry_obj_15.get('revision') != revision:
    errors.append('rev0015 future-session office revision mismatch')
if not reentry_obj_15.get('valid_next_modes'):
    errors.append('rev0015 future-session office lacks valid next modes')
if reentry_obj_15.get('public_claims_admitted_rev0015') != 0:
    errors.append('rev0015 future-session office admits public claims')

guard_obj_15 = json_data.get('UNCONSTRAINED-THINKING-GUARDRAIL.json', {})
permanent_15 = guard_obj_15.get('permanent_constraints', [])
phase_15 = guard_obj_15.get('phase_bound_constraints', [])
if guard_obj_15.get('permanent_constraint_count') != len(permanent_15):
    errors.append('rev0015 permanent constraint count mismatch')
if guard_obj_15.get('phase_bound_constraint_count') != len(phase_15):
    errors.append('rev0015 phase-bound constraint count mismatch')
if len(permanent_15) < 8 or len(phase_15) < 8:
    errors.append('rev0015 guardrail should contain permanent and phase-bound constraints')

tension_obj_15 = json_data.get('DESIGN-TENSION-LEDGER.json', {})
tensions_15 = tension_obj_15.get('tensions', [])
if tension_obj_15.get('tension_count') != len(tensions_15):
    errors.append('rev0015 tension_count mismatch')
if len(tensions_15) < 12:
    errors.append('rev0015 should have at least 12 design tensions')
for dt15 in tensions_15:
    if dt15.get('must_hold_both_sides') is not True:
        errors.append(f"rev0015 tension {dt15.get('tension_id')} not marked hold-both")

horizon_obj_15 = json_data.get('OPEN-HORIZON-REGISTER.json', {})
horizon_15 = horizon_obj_15.get('entries', [])
if horizon_obj_15.get('horizon_entry_count') != len(horizon_15):
    errors.append('rev0015 open horizon count mismatch')
if len(horizon_15) < 20:
    errors.append('rev0015 should have at least 20 open horizons')
if horizon_obj_15.get('implementation_commitments_rev0015') != 0:
    errors.append('rev0015 open horizon has implementation commitments')
for hz15 in horizon_15:
    if hz15.get('record_kind') != 'open_horizon_entry_speculative_not_commitment':
        errors.append(f"rev0015 horizon {hz15.get('horizon_id')} wrong record_kind")
    if hz15.get('implementation_commitment_rev0015') is not False or hz15.get('public_claim_admitted_rev0015') is not False:
        errors.append(f"rev0015 horizon {hz15.get('horizon_id')} admits commitment or public claim")

audit_obj_15 = json_data.get('FOUNDATION-AUDIT-CHECKLIST.json', {})
audit_15 = audit_obj_15.get('questions', [])
if audit_obj_15.get('question_count') != len(audit_15):
    errors.append('rev0015 foundation audit count mismatch')
if len(audit_15) < 20:
    errors.append('rev0015 should have at least 20 foundation audit questions')

brief_obj_15 = json_data.get('data/program/rev0015_future_session_briefing_cards.json', {})
brief_15 = brief_obj_15.get('cards', [])
if brief_obj_15.get('briefing_card_count') != len(brief_15):
    errors.append('rev0015 briefing card count mismatch')

rev0015_count_pairs = [
    ('telos_statements_rev0015', len(telos_rows_15)),
    ('dream_register_entries_rev0015', len(dream_rows_15)),
    ('earned_capability_rungs_rev0015', len(rungs_15)),
    ('design_tensions_rev0015', len(tensions_15)),
    ('open_horizon_entries_rev0015', len(horizon_15)),
    ('future_session_briefing_cards_rev0015', len(brief_15)),
    ('foundation_audit_questions_rev0015', len(audit_15)),
    ('permanent_constraints_rev0015', len(permanent_15)),
    ('phase_bound_constraints_rev0015', len(phase_15)),
]
for field, count in rev0015_count_pairs:
    if manifest.get(field) != count:
        errors.append(f'manifest {field} mismatch')
for field in ['public_claims_admitted_rev0015','payloads_captured_rev0015','payload_hashes_computed_rev0015','payloads_bundled_rev0015','content_summaries_admitted_rev0015','canonical_agency_records_created_rev0015','person_records_created_rev0015','incident_records_created_rev0015','public_current_status_claims_admitted_rev0015']:
    if manifest.get(field) != 0:
        errors.append(f'manifest {field} expected 0')


# Rev0016 audit/factor checks.
for rel in [
    'CUBE-FOUNDATION-AUDIT-LEDGER.json', 'CUBE-FACTOR-MAP-LEDGER.json', 'AUDIT-FINDINGS-LEDGER.json',
    'OVERCONSTRAINT-AUDIT-LEDGER.json', 'FOUNDATION-DEBT-LEDGER.json', 'LEDGER-CONSOLIDATION-MAP.json',
    'SCHEMA-COVERAGE-AUDIT.json', 'OFFICE-REENTRY-CANON.json', 'OPEN-ROUTE-REGISTER.json',
    'REFACTOR-BACKLOG-LEDGER.json', 'PILOT-SHAPE-AUDIT-LEDGER.json', 'RECORD-LIFECYCLE-FACTOR-LEDGER.json',
    'data/audit/rev0016_file_line_audit.json', 'data/audit/rev0016_line_digest_index.json',
    'data/audit/rev0016_json_inventory.json', 'data/audit/rev0016_factor_assignments.json',
    'data/audit/rev0016_schema_coverage_rows.json', 'data/program/rev0016_office_reentry_cards.json',
    'data/program/rev0016_open_route_candidates.json', 'data/program/rev0016_refactor_packages.json',
    'schemas/audit_file_record.schema.json', 'schemas/line_digest_record.schema.json', 'schemas/audit_finding.schema.json',
    'schemas/factor_module.schema.json', 'schemas/foundation_debt.schema.json', 'schemas/office_reentry_card.schema.json',
    'schemas/constraint_audit_row.schema.json', 'schemas/route_candidate.schema.json', 'schemas/schema_coverage_row.schema.json',
    'docs/90-audit/rev0016-foundation-audit-report.md', 'docs/90-audit/rev0016-factor-map.md',
    'docs/90-audit/rev0016-overconstraint-audit.md', 'docs/00-meta/rev0016-office-reentry-canon.md',
    'docs/30-program/rev0016-open-routes-after-audit.md'
]:
    if not (ROOT / rel).exists():
        errors.append(f'missing rev0016 audit/factor file: {rel}')

audit = json_data.get('CUBE-FOUNDATION-AUDIT-LEDGER.json', {})
fmap = json_data.get('CUBE-FACTOR-MAP-LEDGER.json', {})
findings = json_data.get('AUDIT-FINDINGS-LEDGER.json', {})
debt = json_data.get('FOUNDATION-DEBT-LEDGER.json', {})
reentry = json_data.get('OFFICE-REENTRY-CANON.json', {})
routes = json_data.get('OPEN-ROUTE-REGISTER.json', {})
line_audit = json_data.get('data/audit/rev0016_file_line_audit.json', {})
if audit.get('base_file_count') != 428:
    errors.append('rev0016 base_file_count mismatch')
if audit.get('json_parse_errors') != 0:
    errors.append('rev0016 audit has JSON parse errors')
if line_audit.get('file_count') != 428:
    errors.append('rev0016 file audit count mismatch')
if line_audit.get('total_text_line_count') != 82927:
    errors.append('rev0016 line audit total line count mismatch')
if fmap.get('module_count') != 15:
    errors.append('rev0016 factor module count mismatch')
if findings.get('finding_count') != 16:
    errors.append('rev0016 audit finding count mismatch')
if debt.get('debt_count') != 12:
    errors.append('rev0016 debt count mismatch')
if reentry.get('card_count') != 8:
    errors.append('rev0016 office reentry card count mismatch')
if routes.get('route_count') != 10:
    errors.append('rev0016 open route count mismatch')
for field in ['public_claims_admitted_rev0016','payloads_captured_rev0016','payload_hashes_computed_rev0016','content_summaries_admitted_rev0016','person_records_created_rev0016','incident_records_created_rev0016','public_current_status_claims_admitted_rev0016']:
    if manifest.get(field) != 0:
        errors.append(f'manifest {field} expected 0')


# Rev0017 lifecycle ontology checks.
for rel in [
    'CLAIM-LIFECYCLE-INDEX.json', 'CLAIM-LIFECYCLE-STATE-MACHINE.json', 'CLAIM-LIFECYCLE-CROSSWALK.json',
    'CLAIM-STATE-ANTI-COLLAPSE-LEDGER.json', 'EARNED-PROMOTION-RECEIPT-TEMPLATE.json', 'LIFECYCLE-VALIDATION-INDEX.json',
    'data/lifecycle/rev0017_route_selection_receipt.json', 'data/lifecycle/rev0017_lifecycle_states.json',
    'data/lifecycle/rev0017_lifecycle_transitions.json', 'data/lifecycle/rev0017_transition_gate_matrix.json',
    'data/lifecycle/rev0017_lifecycle_file_crosswalk.json', 'data/lifecycle/rev0017_record_kind_state_crosswalk.json',
    'data/lifecycle/rev0017_lifecycle_surface_inventory.json', 'data/lifecycle/rev0017_promotion_receipt_templates.json',
    'data/lifecycle/rev0017_forbidden_transition_tests.json',
    'schemas/lifecycle_state.schema.json', 'schemas/lifecycle_transition.schema.json', 'schemas/lifecycle_file_crosswalk_row.schema.json',
    'schemas/record_kind_state_crosswalk.schema.json', 'schemas/transition_gate_matrix_row.schema.json',
    'schemas/promotion_receipt_template.schema.json', 'schemas/forbidden_transition_test.schema.json',
    'schemas/lifecycle_surface_inventory.schema.json', 'schemas/route_selection_receipt.schema.json',
    'docs/00-meta/rev0017-route-selection-note.md', 'docs/40-model/rev0017-claim-lifecycle-ontology.md',
    'docs/40-model/claim-state-machine-rev0017.md', 'docs/40-model/nonclaim-to-claim-crosswalk-rev0017.md',
    'docs/80-ops/rev0017-lifecycle-validation-runbook.md', 'docs/70-examples/rev0017-sample-promotion-receipts.md',
    'docs/30-program/rev0017-what-the-lifecycle-earns.md'
]:
    if not (ROOT / rel).exists():
        errors.append(f'missing rev0017 lifecycle file: {rel}')

life_index = json_data.get('CLAIM-LIFECYCLE-INDEX.json', {})
life_states_obj = json_data.get('data/lifecycle/rev0017_lifecycle_states.json', {})
life_trans_obj = json_data.get('data/lifecycle/rev0017_lifecycle_transitions.json', {})
gate_obj_17 = json_data.get('data/lifecycle/rev0017_transition_gate_matrix.json', {})
file_cross_obj_17 = json_data.get('data/lifecycle/rev0017_lifecycle_file_crosswalk.json', {})
rk_cross_obj_17 = json_data.get('data/lifecycle/rev0017_record_kind_state_crosswalk.json', {})
surf_inv_obj_17 = json_data.get('data/lifecycle/rev0017_lifecycle_surface_inventory.json', {})
promo_obj_17 = json_data.get('data/lifecycle/rev0017_promotion_receipt_templates.json', {})
forbid_obj_17 = json_data.get('data/lifecycle/rev0017_forbidden_transition_tests.json', {})
route_obj_17 = json_data.get('data/lifecycle/rev0017_route_selection_receipt.json', {})

states_17 = life_states_obj.get('states', [])
state_ids_17 = {s.get('state_id') for s in states_17}
trans_17 = life_trans_obj.get('transitions', [])
gates_17 = gate_obj_17.get('rows', [])
file_rows_17 = file_cross_obj_17.get('rows', [])
rk_rows_17 = rk_cross_obj_17.get('rows', [])
surf_rows_17 = surf_inv_obj_17.get('rows', [])
promo_rows_17 = promo_obj_17.get('templates', [])
forbid_rows_17 = forbid_obj_17.get('tests', [])

if route_obj_17.get('selected_route_id') != 'ROUTE-REV0016-004':
    errors.append('rev0017 selected route mismatch')
if life_states_obj.get('state_count') != len(states_17):
    errors.append('rev0017 lifecycle state_count mismatch')
if len(states_17) < 25:
    errors.append('rev0017 should define at least 25 lifecycle/meta states')
for s17 in states_17:
    if s17.get('record_kind') != 'lifecycle_state_definition':
        errors.append(f"rev0017 state {s17.get('state_id')} wrong record_kind")
    if s17.get('default_person_or_incident_extraction_allowed') is not False:
        errors.append(f"rev0017 state {s17.get('state_id')} allows person/incident extraction by default")
    if s17.get('default_current_status_claim_allowed') is not False:
        errors.append(f"rev0017 state {s17.get('state_id')} allows current status by default")

if life_trans_obj.get('transition_count') != len(trans_17):
    errors.append('rev0017 lifecycle transition_count mismatch')
if len(trans_17) < 30:
    errors.append('rev0017 should define at least 30 allowed transitions')
transition_ids_17 = set()
for t17 in trans_17:
    transition_ids_17.add(t17.get('transition_id'))
    if t17.get('record_kind') != 'lifecycle_transition_definition':
        errors.append(f"rev0017 transition {t17.get('transition_id')} wrong record_kind")
    if t17.get('from_state') not in state_ids_17 or t17.get('to_state') not in state_ids_17:
        errors.append(f"rev0017 transition {t17.get('transition_id')} references unknown state")
    if t17.get('requires_explicit_receipt') is not True:
        errors.append(f"rev0017 transition {t17.get('transition_id')} lacks explicit receipt requirement")
    if t17.get('allows_public_claim_by_itself') is not False or t17.get('allows_person_or_incident_creation_by_itself') is not False:
        errors.append(f"rev0017 transition {t17.get('transition_id')} allows forbidden promotion by itself")

if gate_obj_17.get('row_count') != len(gates_17):
    errors.append('rev0017 transition gate row_count mismatch')
if len(gates_17) != len(trans_17):
    errors.append('rev0017 transition gates should match transition count')
for g17 in gates_17:
    if g17.get('record_kind') != 'transition_gate_matrix_row':
        errors.append(f"rev0017 gate {g17.get('gate_row_id')} wrong record_kind")
    if g17.get('transition_id') not in transition_ids_17:
        errors.append(f"rev0017 gate {g17.get('gate_row_id')} references unknown transition")
    if g17.get('automated_promotion_allowed') is not False or g17.get('public_claim_allowed_by_transition') is not False or g17.get('person_or_incident_creation_allowed_by_transition') is not False:
        errors.append(f"rev0017 gate {g17.get('gate_row_id')} allows forbidden automatic promotion")

if file_cross_obj_17.get('file_count') != len(file_rows_17):
    errors.append('rev0017 file crosswalk count mismatch')
if len(file_rows_17) < 300:
    errors.append('rev0017 file crosswalk unexpectedly small')
for row17 in file_rows_17:
    if row17.get('record_kind') != 'lifecycle_file_crosswalk_row':
        errors.append(f"rev0017 file crosswalk {row17.get('crosswalk_id')} wrong record_kind")
    if row17.get('dominant_lifecycle_state') not in state_ids_17:
        errors.append(f"rev0017 file crosswalk {row17.get('crosswalk_id')} unknown state")
    if row17.get('claim_promotion_allowed_by_crosswalk') is not False or row17.get('public_display_allowed_by_crosswalk') is not False:
        errors.append(f"rev0017 file crosswalk {row17.get('crosswalk_id')} allows promotion/display")

if rk_cross_obj_17.get('record_kind_count') != len(rk_rows_17):
    errors.append('rev0017 record-kind crosswalk count mismatch')
if len(rk_rows_17) < 80:
    errors.append('rev0017 record-kind crosswalk unexpectedly small')
for rk17 in rk_rows_17:
    if rk17.get('record_kind') != 'record_kind_state_crosswalk_row':
        errors.append(f"rev0017 record-kind crosswalk {rk17.get('record_kind_crosswalk_id')} wrong record_kind")
    if rk17.get('dominant_lifecycle_state') not in state_ids_17:
        errors.append(f"rev0017 record-kind crosswalk {rk17.get('record_kind_crosswalk_id')} unknown state")
    if rk17.get('promotion_allowed_by_record_kind_name') is not False:
        errors.append(f"rev0017 record-kind crosswalk {rk17.get('record_kind_crosswalk_id')} allows promotion by name")

if surf_inv_obj_17.get('row_count') != len(surf_rows_17):
    errors.append('rev0017 surface inventory row_count mismatch')
if len(surf_rows_17) != len(states_17):
    errors.append('rev0017 surface inventory should have one row per state')
for si17 in surf_rows_17:
    if si17.get('record_kind') != 'lifecycle_surface_inventory_row':
        errors.append(f"rev0017 surface inventory {si17.get('inventory_row_id')} wrong record_kind")
    if si17.get('state_id') not in state_ids_17:
        errors.append(f"rev0017 surface inventory {si17.get('inventory_row_id')} unknown state")
    if si17.get('has_live_claims_rev0017') is not False or si17.get('has_public_claims_rev0017') is not False:
        errors.append(f"rev0017 surface inventory {si17.get('inventory_row_id')} admits live/public claims")

if promo_obj_17.get('template_count') != len(promo_rows_17):
    errors.append('rev0017 promotion template count mismatch')
if len(promo_rows_17) < 10:
    errors.append('rev0017 should have at least 10 promotion templates')
if promo_obj_17.get('templates_used_rev0017') != 0:
    errors.append('rev0017 promotion templates should be unused')
for p17 in promo_rows_17:
    if p17.get('record_kind') != 'promotion_receipt_template':
        errors.append(f"rev0017 promotion template {p17.get('template_id')} wrong record_kind")
    if p17.get('from_state') not in state_ids_17 or p17.get('to_state') not in state_ids_17:
        errors.append(f"rev0017 promotion template {p17.get('template_id')} unknown state")
    if p17.get('automated_promotion_allowed') is not False or p17.get('public_claim_allowed_by_template_alone') is not False or p17.get('person_or_incident_creation_allowed_by_template_alone') is not False:
        errors.append(f"rev0017 promotion template {p17.get('template_id')} allows forbidden promotion by template alone")

if forbid_obj_17.get('test_count') != len(forbid_rows_17):
    errors.append('rev0017 forbidden transition count mismatch')
if len(forbid_rows_17) < 15:
    errors.append('rev0017 should have at least 15 forbidden transition tests')
for f17 in forbid_rows_17:
    if f17.get('record_kind') != 'forbidden_transition_test':
        errors.append(f"rev0017 forbidden transition {f17.get('forbidden_test_id')} wrong record_kind")
    if f17.get('from_state') not in state_ids_17 or f17.get('attempted_to_state') not in state_ids_17:
        errors.append(f"rev0017 forbidden transition {f17.get('forbidden_test_id')} unknown state")
    if f17.get('public_claim_allowed') is not False or f17.get('person_or_incident_creation_allowed') is not False:
        errors.append(f"rev0017 forbidden transition {f17.get('forbidden_test_id')} allows forbidden claim/person creation")

life_counts = life_index.get('counts', {})
for field, count in [
    ('lifecycle_states', len(states_17)), ('allowed_transitions', len(trans_17)), ('transition_gate_rows', len(gates_17)),
    ('file_crosswalk_rows', len(file_rows_17)), ('record_kind_crosswalk_rows', len(rk_rows_17)),
    ('surface_inventory_rows', len(surf_rows_17)), ('promotion_receipt_templates', len(promo_rows_17)),
    ('forbidden_transition_tests', len(forbid_rows_17))
]:
    if life_counts.get(field) != count:
        errors.append(f'rev0017 lifecycle index {field} mismatch')

rev0017_manifest_pairs = [
    ('lifecycle_states_rev0017', len(states_17)),
    ('lifecycle_transitions_rev0017', len(trans_17)),
    ('transition_gate_rows_rev0017', len(gates_17)),
    ('lifecycle_file_crosswalk_rows_rev0017', len(file_rows_17)),
    ('record_kind_crosswalk_rows_rev0017', len(rk_rows_17)),
    ('lifecycle_surface_inventory_rows_rev0017', len(surf_rows_17)),
    ('promotion_receipt_templates_rev0017', len(promo_rows_17)),
    ('forbidden_transition_tests_rev0017', len(forbid_rows_17)),
]
for field, count in rev0017_manifest_pairs:
    if manifest.get(field) != count:
        errors.append(f'manifest {field} mismatch')
for field in ['public_claims_admitted_rev0017','payloads_captured_rev0017','payload_hashes_computed_rev0017','payloads_bundled_rev0017','content_summaries_admitted_rev0017','canonical_agency_records_created_rev0017','person_records_created_rev0017','officer_records_created_rev0017','civilian_records_created_rev0017','incident_records_created_rev0017','lawsuit_merits_records_created_rev0017','settlement_amount_records_created_rev0017','public_current_status_claims_admitted_rev0017']:
    if manifest.get(field) != 0:
        errors.append(f'manifest {field} expected 0')



# Rev0018 evidence atom / claim candidate workbench checks
rev0018_required = [
    'EVIDENCE-ATOM-WORKBENCH.json', 'CLAIM-CANDIDATE-WORKBENCH.json', 'CLAIM-GRAMMAR-LEDGER.json',
    'DEFEATER-WORKBENCH-LEDGER.json', 'SOURCE-VOICE-ATTRIBUTION-LEDGER.json', 'ATOM-PROMOTION-RECEIPT-TEMPLATE.json',
    'ADVERSE-CLAIM-SEVERITY-MATRIX.json', 'PERSON-PRIVACY-INTERLOCK-LEDGER.json',
    'data/claim_workbench/rev0018_evidence_atom_types.json',
    'data/claim_workbench/rev0018_claim_candidate_templates.json',
    'data/claim_workbench/rev0018_source_voice_grammar.json',
    'data/claim_workbench/rev0018_claim_modality_matrix.json',
    'data/claim_workbench/rev0018_defeater_classes.json',
    'data/claim_workbench/rev0018_atom_promotion_requirements.json',
    'data/claim_workbench/rev0018_forbidden_wording_tests.json',
    'data/claim_workbench/rev0018_adverse_claim_severity_matrix.json',
    'data/claim_workbench/rev0018_person_privacy_interlock.json',
    'data/claim_workbench/rev0018_claim_review_queue_blueprints.json',
    'data/claim_workbench/rev0018_claim_candidate_fixture_blueprints.json',
    'data/claim_workbench/rev0018_evidence_atom_lifecycle_alignment.json',
    'data/claim_workbench/rev0018_claim_candidate_lifecycle_alignment.json',
    'data/claim_workbench/rev0018_claim_output_field_contract.json',
    'data/claim_workbench/rev0018_atom_bundle_recipe_matrix.json',
]
if revision in {'rev0018', 'rev0019', 'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'}:
    for rel in rev0018_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0018 required file: {rel}')

    atom_surface = json_data.get('data/claim_workbench/rev0018_evidence_atom_types.json', {})
    atom_defs_18 = atom_surface.get('evidence_atom_types', [])
    if atom_surface.get('atom_type_count') != len(atom_defs_18):
        errors.append('rev0018 atom_type_count mismatch')
    if len(atom_defs_18) != 46:
        errors.append(f'rev0018 expected 46 atom types, found {len(atom_defs_18)}')
    atom_ids = {a.get('atom_type_id') for a in atom_defs_18}
    for a in atom_defs_18:
        if a.get('record_kind') != 'evidence_atom_type_definition':
            errors.append(f"rev0018 atom {a.get('atom_type_id')} wrong record_kind")
        if a.get('public_display_allowed_by_itself') is not False:
            errors.append(f"rev0018 atom {a.get('atom_type_id')} allows public display by itself")
        if a.get('entity_link_allowed_by_itself') is not False:
            errors.append(f"rev0018 atom {a.get('atom_type_id')} allows entity link by itself")

    template_surface = json_data.get('data/claim_workbench/rev0018_claim_candidate_templates.json', {})
    templates = template_surface.get('claim_candidate_templates', [])
    if template_surface.get('claim_candidate_template_count') != len(templates):
        errors.append('rev0018 claim_candidate_template_count mismatch')
    if len(templates) != 35:
        errors.append(f'rev0018 expected 35 claim candidate templates, found {len(templates)}')
    for t in templates:
        if t.get('record_kind') != 'claim_candidate_template':
            errors.append(f"rev0018 template {t.get('claim_template_id')} wrong record_kind")
        if t.get('can_create_public_claim_rev0018') is not False:
            errors.append(f"rev0018 template {t.get('claim_template_id')} can create public claim")
        for ref in t.get('minimum_required_atom_types', []):
            if ref not in atom_ids:
                errors.append(f"rev0018 template {t.get('claim_template_id')} references unknown atom {ref}")

    voice_surface = json_data.get('data/claim_workbench/rev0018_source_voice_grammar.json', {})
    voices = voice_surface.get('source_voice_frames', [])
    if voice_surface.get('source_voice_frame_count') != len(voices) or len(voices) != 28:
        errors.append(f"rev0018 source voice count mismatch: {len(voices)}")
    for v in voices:
        if v.get('record_kind') != 'source_voice_frame':
            errors.append(f"rev0018 voice {v.get('voice_frame_id')} wrong record_kind")
        if v.get('public_display_allowed_rev0018') is not False:
            errors.append(f"rev0018 voice {v.get('voice_frame_id')} public display not blocked")

    modality_surface = json_data.get('data/claim_workbench/rev0018_claim_modality_matrix.json', {})
    modalities = modality_surface.get('modalities', [])
    if modality_surface.get('modality_count') != len(modalities) or len(modalities) != 20:
        errors.append(f"rev0018 modality count mismatch: {len(modalities)}")

    defeater_surface = json_data.get('data/claim_workbench/rev0018_defeater_classes.json', {})
    defeaters = defeater_surface.get('defeater_classes', [])
    if defeater_surface.get('defeater_class_count') != len(defeaters) or len(defeaters) != 30:
        errors.append(f"rev0018 defeater count mismatch: {len(defeaters)}")
    for d in defeaters:
        if d.get('public_display_allowed_while_unresolved') is not False:
            errors.append(f"rev0018 defeater {d.get('defeater_class_id')} allows public display while unresolved")

    promotion_surface = json_data.get('data/claim_workbench/rev0018_atom_promotion_requirements.json', {})
    promotions = promotion_surface.get('promotion_requirements', [])
    if promotion_surface.get('promotion_requirement_count') != len(promotions) or len(promotions) != 46:
        errors.append(f"rev0018 promotion requirement count mismatch: {len(promotions)}")
    for pr in promotions:
        if pr.get('atom_type_id') not in atom_ids:
            errors.append(f"rev0018 promotion references unknown atom {pr.get('atom_type_id')}")
        if pr.get('public_display_allowed_by_requirement') is not False:
            errors.append(f"rev0018 promotion {pr.get('requirement_id')} allows public display")
        if pr.get('person_or_incident_creation_allowed_by_requirement') is not False:
            errors.append(f"rev0018 promotion {pr.get('requirement_id')} allows person/incident creation")

    fwt_surface = json_data.get('data/claim_workbench/rev0018_forbidden_wording_tests.json', {})
    fwts = fwt_surface.get('forbidden_wording_tests', [])
    if fwt_surface.get('forbidden_wording_test_count') != len(fwts) or len(fwts) != 32:
        errors.append(f"rev0018 forbidden wording test count mismatch: {len(fwts)}")

    privacy_surface = json_data.get('data/claim_workbench/rev0018_person_privacy_interlock.json', {})
    privacy = privacy_surface.get('privacy_interlocks', [])
    if privacy_surface.get('privacy_interlock_count') != len(privacy) or len(privacy) != 20:
        errors.append(f"rev0018 privacy interlock count mismatch: {len(privacy)}")
    for p in privacy:
        if p.get('requires_human_review') is not True:
            errors.append(f"rev0018 privacy interlock {p.get('interlock_id')} missing human review")

    severity_surface = json_data.get('data/claim_workbench/rev0018_adverse_claim_severity_matrix.json', {})
    severity = severity_surface.get('severity_rows', [])
    if severity_surface.get('severity_row_count') != len(severity) or len(severity) != 13:
        errors.append(f"rev0018 adverse severity count mismatch: {len(severity)}")

    queue_surface = json_data.get('data/claim_workbench/rev0018_claim_review_queue_blueprints.json', {})
    queues = queue_surface.get('queue_blueprints', [])
    if queue_surface.get('queue_blueprint_count') != len(queues) or len(queues) != 12:
        errors.append(f"rev0018 queue blueprint count mismatch: {len(queues)}")

    fixture_surface = json_data.get('data/claim_workbench/rev0018_claim_candidate_fixture_blueprints.json', {})
    fixtures = fixture_surface.get('fixtures', [])
    if fixture_surface.get('fixture_count') != len(fixtures) or len(fixtures) != 10:
        errors.append(f"rev0018 fixture count mismatch: {len(fixtures)}")
    for fx in fixtures:
        if fx.get('uses_live_people_or_real_incidents') is not False:
            errors.append(f"rev0018 fixture {fx.get('fixture_id')} uses live people or real incidents")

    # No-live-data counters specific to rev0018.
    for key in ['live_evidence_atoms_created_rev0018', 'live_claim_candidates_created_rev0018', 'public_claims_admitted_rev0018', 'public_displays_admitted_rev0018']:
        if manifest.get(key, 0) != 0:
            errors.append(f'manifest {key} must be 0')



# Rev0019 source-family atlas and root-refactor surfaces.
families_19 = []
lanes_19 = []
root_rows_19 = []
if revision in {'rev0019', 'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'}:
    rev0019_required = [
        'SOURCE-FAMILY-ATLAS-LEDGER.json', 'SOURCE-FAMILY-READINESS-LADDER.json',
        'CORPUS-LANE-ROUTING-LEDGER.json', 'PILOT-DELOCK-LEDGER.json',
        'ROOT-SURFACE-REFACTOR-LEDGER.json', 'REVIEW-OFFICE-INDEX.json',
        'MODULE-SURFACE-REGISTRY.json', 'NAMESPACE-MIGRATION-PLAN.json',
        'INTEROPERABILITY-CONTRACT-LEDGER.json', 'REV0019-AUDIT-RECEIPT.json',
        'data/source_families/rev0019_source_family_atlas.json',
        'data/source_families/rev0019_source_family_readiness_ladder.json',
        'data/source_families/rev0019_source_family_intake_gates.json',
        'data/source_families/rev0019_corpus_lane_routes.json',
        'data/source_families/rev0019_pilot_candidate_routes.json',
        'data/source_families/rev0019_interoperability_contracts.json',
        'data/source_families/rev0019_source_family_review_queue.json',
        'data/refactor/rev0019_root_surface_inventory.json',
        'data/refactor/rev0019_root_to_office_crosswalk.json',
        'data/refactor/rev0019_consolidation_waves.json',
        'data/refactor/rev0019_review_office_cards.json',
        'data/refactor/rev0019_surface_registry_snapshot.json',
        'data/refactor/rev0019_validator_refactor_plan.json',
        'schemas/source_family.schema.json', 'schemas/source_family_intake_gate.schema.json',
        'schemas/corpus_lane_route.schema.json', 'schemas/pilot_candidate_route.schema.json',
        'schemas/interoperability_contract.schema.json', 'schemas/root_surface_inventory_row.schema.json',
        'schemas/root_to_office_crosswalk_row.schema.json', 'schemas/consolidation_wave.schema.json',
        'schemas/review_office_card.schema.json', 'schemas/validator_refactor_step.schema.json',
        'docs/30-program/rev0019-source-family-atlas.md',
        'docs/30-program/corpus-lane-routing-rev0019.md',
        'docs/30-program/pilot-delock-note-rev0019.md',
        'docs/40-model/interoperability-contracts-rev0019.md',
        'docs/80-ops/review-office-reentry-rev0019.md',
        'docs/90-audit/root-ledger-refactor-audit-rev0019.md',
        'docs/90-audit/validator-refactor-plan-rev0019.md',
        'docs/00-meta/rev0019-handoff.md',
    ]
    for rel in rev0019_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0019 required file: {rel}')

    sf_obj = json_data.get('data/source_families/rev0019_source_family_atlas.json', {})
    families_19 = sf_obj.get('source_families', [])
    if sf_obj.get('source_family_count') != len(families_19):
        errors.append('rev0019 source_family_count mismatch')
    if len(families_19) != 24:
        errors.append(f'rev0019 expected 24 source families, found {len(families_19)}')
    fam_ids = {f.get('source_family_id') for f in families_19}
    for fam in families_19:
        if fam.get('live_data_allowed_rev0019') is not False:
            errors.append(f"rev0019 source family {fam.get('source_family_id')} allows live data")
        if fam.get('public_claims_admitted_rev0019') != 0:
            errors.append(f"rev0019 source family {fam.get('source_family_id')} admits public claims")
        if not fam.get('required_gates'):
            errors.append(f"rev0019 source family {fam.get('source_family_id')} missing required gates")

    gates_obj = json_data.get('data/source_families/rev0019_source_family_intake_gates.json', {})
    gates_19 = gates_obj.get('gates', [])
    if gates_obj.get('gate_count') != len(gates_19) or len(gates_19) != 18:
        errors.append(f'rev0019 intake gate count mismatch: {len(gates_19)}')
    for g in gates_19:
        if g.get('blocks_live_data_by_itself') is not True:
            errors.append(f"rev0019 gate {g.get('gate_id')} must block live data by itself")

    lanes_obj = json_data.get('data/source_families/rev0019_corpus_lane_routes.json', {})
    lanes_19 = lanes_obj.get('lanes', [])
    if lanes_obj.get('lane_count') != len(lanes_19) or len(lanes_19) != 18:
        errors.append(f'rev0019 corpus lane count mismatch: {len(lanes_19)}')
    for lane in lanes_19:
        if lane.get('live_records_created_rev0019') != 0 or lane.get('public_claims_admitted_rev0019') != 0:
            errors.append(f"rev0019 lane {lane.get('lane_id')} admits live records or public claims")

    cand_obj = json_data.get('data/source_families/rev0019_pilot_candidate_routes.json', {})
    cands_19 = cand_obj.get('candidates', [])
    if cand_obj.get('candidate_count') != len(cands_19) or len(cands_19) != 18:
        errors.append(f'rev0019 pilot candidate count mismatch: {len(cands_19)}')
    if cand_obj.get('live_branch_selected_rev0019') is not False:
        errors.append('rev0019 must not select a live branch')
    for c in cands_19:
        if c.get('source_family_id') not in fam_ids:
            errors.append(f"rev0019 pilot candidate {c.get('candidate_id')} references unknown source family")
        if c.get('live_data_allowed_rev0019') is not False or c.get('public_claims_admitted_rev0019') != 0:
            errors.append(f"rev0019 pilot candidate {c.get('candidate_id')} admits live data or claims")

    interop_obj = json_data.get('data/source_families/rev0019_interoperability_contracts.json', {})
    interops_19 = interop_obj.get('contracts', [])
    if interop_obj.get('contract_count') != len(interops_19) or len(interops_19) != 12:
        errors.append(f'rev0019 interoperability contract count mismatch: {len(interops_19)}')

    root_obj = json_data.get('data/refactor/rev0019_root_surface_inventory.json', {})
    root_rows_19 = root_obj.get('rows', [])
    if root_obj.get('root_surface_count') != len(root_rows_19):
        errors.append('rev0019 root surface count mismatch')
    if len(root_rows_19) < 130:
        errors.append('rev0019 root inventory unexpectedly small')
    for row in root_rows_19:
        if row.get('destructive_move_allowed_rev0019') is not False:
            errors.append(f"rev0019 root row {row.get('path')} allows destructive move")

    cross_obj = json_data.get('data/refactor/rev0019_root_to_office_crosswalk.json', {})
    cross_19 = cross_obj.get('rows', [])
    if cross_obj.get('crosswalk_row_count') != len(cross_19) or len(cross_19) != len(root_rows_19):
        errors.append('rev0019 root-to-office crosswalk mismatch')
    for row in cross_19:
        if row.get('move_performed_rev0019') is not False:
            errors.append(f"rev0019 crosswalk {row.get('crosswalk_id')} performed move")

    office_obj = json_data.get('data/refactor/rev0019_review_office_cards.json', {})
    offices_19 = office_obj.get('offices', [])
    if office_obj.get('office_count') != len(offices_19) or len(offices_19) != 12:
        errors.append(f'rev0019 review office count mismatch: {len(offices_19)}')

    waves_obj = json_data.get('data/refactor/rev0019_consolidation_waves.json', {})
    waves_19 = waves_obj.get('waves', [])
    if waves_obj.get('wave_count') != len(waves_19) or len(waves_19) != 7:
        errors.append(f'rev0019 consolidation wave count mismatch: {len(waves_19)}')
    if any(w.get('status_rev0019') == 'performed' and w.get('wave_id') != 'ROOT-WAVE-0' for w in waves_19):
        errors.append('rev0019 performed a migration wave beyond shadow index')

    for key in ['live_source_rows_created_rev0019','live_evidence_atoms_created_rev0019','live_claim_candidates_created_rev0019','public_claims_admitted_rev0019','public_displays_admitted_rev0019','destructive_moves_performed_rev0019']:
        if manifest.get(key, 0) != 0:
            errors.append(f'manifest {key} must be 0')


# Rev0020 review-packet kernel and reentry/refactor surfaces.
packet_states_20 = []
packet_types_20 = []
risk_tiers_20 = []
if revision in {'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'}:
    rev0020_required = [
        'REVIEW-PACKET-KERNEL.json', 'REVIEW-PACKET-STATE-MACHINE.json',
        'DECISION-RECEIPT-GRAMMAR.json', 'REVIEW-ROLE-MATRIX.json',
        'RISK-TIER-ROUTING-MATRIX.json', 'SOURCE-FAMILY-TO-REVIEW-PACKET-CROSSWALK.json',
        'OPERATION-START-CHECKLIST.json', 'REVIEW-PACKET-ANTI-COLLAPSE-LEDGER.json',
        'ARCHIVE-HEAD-REPAIR-RECEIPT.json', 'VALIDATOR-FACET-REGISTRY.json',
        'REENTRY-SURFACE-STALENESS-AUDIT.json',
        'data/review_packets/rev0020_review_packet_states.json',
        'data/review_packets/rev0020_review_packet_types.json',
        'data/review_packets/rev0020_required_packet_sections.json',
        'data/review_packets/rev0020_reviewer_role_matrix.json',
        'data/review_packets/rev0020_risk_tier_routes.json',
        'data/review_packets/rev0020_decision_receipt_templates.json',
        'data/review_packets/rev0020_packet_transition_gates.json',
        'data/review_packets/rev0020_source_family_packet_crosswalk.json',
        'data/review_packets/rev0020_live_operation_start_checklist.json',
        'data/review_packets/rev0020_no_live_data_packet_fixtures.json',
        'data/review_packets/rev0020_review_packet_anti_collapse_rules.json',
        'data/refactor/rev0020_archive_head_audit.json',
        'data/refactor/rev0020_validator_facet_inventory.json',
        'data/refactor/rev0020_reentry_surface_staleness_audit.json',
        'data/refactor/rev0020_doc_index_repair_actions.json',
        'data/refactor/rev0020_validator_refactor_patch_receipt.json',
        'data/refactor/rev0020_review_office_delta.json',
        'schemas/review_packet_state.schema.json', 'schemas/review_packet_type.schema.json',
        'schemas/review_packet_required_section.schema.json', 'schemas/reviewer_role.schema.json',
        'schemas/review_packet_risk_tier.schema.json', 'schemas/decision_receipt_template.schema.json',
        'schemas/review_packet_transition_gate.schema.json', 'schemas/source_family_review_packet_crosswalk.schema.json',
        'schemas/operation_start_check.schema.json', 'schemas/review_packet_fixture_blueprint.schema.json',
        'schemas/review_packet_anti_collapse_rule.schema.json', 'schemas/validator_facet_inventory_row.schema.json',
        'schemas/archive_head_audit_row.schema.json',
        'tools/validators/__init__.py', 'tools/validators/rev0020_review_packet_checks.py',
        'docs/80-ops/rev0020-review-packet-kernel.md',
        'docs/80-ops/review-packet-state-machine-rev0020.md',
        'docs/80-ops/risk-tier-routing-rev0020.md',
        'docs/80-ops/decision-receipts-rev0020.md',
        'docs/90-audit/archive-head-repair-rev0020.md',
        'docs/90-audit/validator-facet-refactor-rev0020.md',
        'docs/00-meta/rev0020-handoff.md',
    ]
    for rel in rev0020_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0020 required file: {rel}')

    state_obj = json_data.get('data/review_packets/rev0020_review_packet_states.json', {})
    packet_states_20 = state_obj.get('states', [])
    if state_obj.get('state_count') != len(packet_states_20) or len(packet_states_20) != 24:
        errors.append(f'rev0020 packet state count mismatch: {len(packet_states_20)}')
    state_ids_20 = {s.get('state_id') for s in packet_states_20}
    for s in packet_states_20:
        if s.get('record_kind') != 'review_packet_state_definition':
            errors.append(f"rev0020 state {s.get('state_id')} wrong record_kind")
        if s.get('live_records_created_rev0020') != 0 or s.get('public_claims_admitted_rev0020') != 0:
            errors.append(f"rev0020 state {s.get('state_id')} admits live records or public claims")

    type_obj = json_data.get('data/review_packets/rev0020_review_packet_types.json', {})
    packet_types_20 = type_obj.get('packet_types', [])
    if type_obj.get('packet_type_count') != len(packet_types_20) or len(packet_types_20) != 20:
        errors.append(f'rev0020 packet type count mismatch: {len(packet_types_20)}')
    type_ids_20 = {t.get('packet_type_id') for t in packet_types_20}
    for t in packet_types_20:
        if t.get('can_create_live_records_by_definition_rev0020') is not False:
            errors.append(f"rev0020 packet type {t.get('packet_type_id')} allows live records")
        if t.get('can_create_public_claims_by_definition_rev0020') is not False:
            errors.append(f"rev0020 packet type {t.get('packet_type_id')} allows public claims")

    section_obj = json_data.get('data/review_packets/rev0020_required_packet_sections.json', {})
    sections_20 = section_obj.get('sections', [])
    if section_obj.get('section_count') != len(sections_20) or len(sections_20) != 26:
        errors.append(f'rev0020 packet section count mismatch: {len(sections_20)}')

    role_obj = json_data.get('data/review_packets/rev0020_reviewer_role_matrix.json', {})
    roles_20 = role_obj.get('roles', [])
    if role_obj.get('role_count') != len(roles_20) or len(roles_20) != 14:
        errors.append(f'rev0020 reviewer role count mismatch: {len(roles_20)}')
    role_keys_20 = {r.get('role_key') for r in roles_20}
    for r in roles_20:
        if r.get('role_can_override_gates_alone') is not False or r.get('role_can_create_public_claim_alone') is not False:
            errors.append(f"rev0020 role {r.get('role_key')} can override or create public claim")

    risk_obj = json_data.get('data/review_packets/rev0020_risk_tier_routes.json', {})
    risk_tiers_20 = risk_obj.get('risk_tiers', [])
    if risk_obj.get('risk_tier_count') != len(risk_tiers_20) or len(risk_tiers_20) != 10:
        errors.append(f'rev0020 risk tier count mismatch: {len(risk_tiers_20)}')
    risk_ids_20 = {r.get('risk_tier_id') for r in risk_tiers_20}
    for r in risk_tiers_20:
        for role in r.get('required_role_keys', []):
            if role not in role_keys_20:
                errors.append(f"rev0020 risk tier {r.get('risk_tier_id')} references unknown role {role}")
        if r.get('requires_human_review_before_public_claim') is not True:
            errors.append(f"rev0020 risk tier {r.get('risk_tier_id')} missing human review gate")

    decision_obj = json_data.get('data/review_packets/rev0020_decision_receipt_templates.json', {})
    decisions_20 = decision_obj.get('decision_templates', [])
    if decision_obj.get('decision_template_count') != len(decisions_20) or len(decisions_20) != 15:
        errors.append(f'rev0020 decision receipt template count mismatch: {len(decisions_20)}')
    for d in decisions_20:
        if d.get('public_claims_admitted_by_template_rev0020') != 0:
            errors.append(f"rev0020 decision {d.get('decision_template_id')} admits public claims")

    trans_obj = json_data.get('data/review_packets/rev0020_packet_transition_gates.json', {})
    trans_20 = trans_obj.get('transition_gates', [])
    if trans_obj.get('transition_gate_count') != len(trans_20) or len(trans_20) != 38:
        errors.append(f'rev0020 transition gate count mismatch: {len(trans_20)}')
    for tr in trans_20:
        if tr.get('from_state_id') not in state_ids_20 or tr.get('to_state_id') not in state_ids_20:
            errors.append(f"rev0020 transition {tr.get('transition_id')} references unknown state")
        if tr.get('requires_decision_receipt') is not True:
            errors.append(f"rev0020 transition {tr.get('transition_id')} missing decision receipt")
        if tr.get('blocks_public_claim_by_default') is not True:
            errors.append(f"rev0020 transition {tr.get('transition_id')} does not block public claim")

    cross_obj_20 = json_data.get('data/review_packets/rev0020_source_family_packet_crosswalk.json', {})
    cross_20 = cross_obj_20.get('rows', [])
    if cross_obj_20.get('crosswalk_row_count') != len(cross_20) or len(cross_20) != 24:
        errors.append(f'rev0020 source-family packet crosswalk count mismatch: {len(cross_20)}')
    fam_ids_19_check = {f.get('source_family_id') for f in families_19}
    for row in cross_20:
        if row.get('source_family_id') not in fam_ids_19_check:
            errors.append(f"rev0020 crosswalk {row.get('crosswalk_id')} references unknown source family")
        if row.get('recommended_packet_type_id') not in type_ids_20:
            errors.append(f"rev0020 crosswalk {row.get('crosswalk_id')} references unknown packet type")
        if row.get('default_risk_tier_id') not in risk_ids_20:
            errors.append(f"rev0020 crosswalk {row.get('crosswalk_id')} references unknown risk tier")
        if row.get('live_data_allowed_rev0020') is not False or row.get('public_claims_admitted_rev0020') != 0:
            errors.append(f"rev0020 crosswalk {row.get('crosswalk_id')} admits live data or public claims")

    checklist_obj = json_data.get('data/review_packets/rev0020_live_operation_start_checklist.json', {})
    checks_20 = checklist_obj.get('checks', [])
    if checklist_obj.get('check_count') != len(checks_20) or len(checks_20) != 22:
        errors.append(f'rev0020 operation checklist count mismatch: {len(checks_20)}')
    for c in checks_20:
        if c.get('required_before_live_data') is not True or c.get('required_before_public_claim') is not True:
            errors.append(f"rev0020 checklist {c.get('check_id')} missing before-live/public gate")

    fixture_obj = json_data.get('data/review_packets/rev0020_no_live_data_packet_fixtures.json', {})
    fixtures_20 = fixture_obj.get('fixtures', [])
    if fixture_obj.get('fixture_count') != len(fixtures_20) or len(fixtures_20) != 12:
        errors.append(f'rev0020 fixture count mismatch: {len(fixtures_20)}')
    for fx in fixtures_20:
        if fx.get('uses_live_people_or_real_incidents') is not False or fx.get('uses_live_source_payload') is not False:
            errors.append(f"rev0020 fixture {fx.get('fixture_id')} uses live data")

    anti_obj = json_data.get('data/review_packets/rev0020_review_packet_anti_collapse_rules.json', {})
    anti_20 = anti_obj.get('rules', [])
    if anti_obj.get('rule_count') != len(anti_20) or len(anti_20) != 18:
        errors.append(f'rev0020 anti-collapse rule count mismatch: {len(anti_20)}')

    facet_obj = json_data.get('data/refactor/rev0020_validator_facet_inventory.json', {})
    facets_20 = facet_obj.get('facets', [])
    if facet_obj.get('facet_count') != len(facets_20) or len(facets_20) != 13:
        errors.append(f'rev0020 validator facet count mismatch: {len(facets_20)}')

    audit_obj = json_data.get('data/refactor/rev0020_archive_head_audit.json', {})
    audit_20 = audit_obj.get('rows', [])
    if audit_obj.get('audit_row_count') != len(audit_20) or len(audit_20) != 7:
        errors.append(f'rev0020 archive audit count mismatch: {len(audit_20)}')

    for key in ['live_source_rows_created_rev0020','live_evidence_atoms_created_rev0020','live_claim_candidates_created_rev0020','live_review_packets_created_rev0020','public_claims_admitted_rev0020','public_displays_admitted_rev0020','destructive_moves_performed_rev0020']:
        if manifest.get(key, 0) != 0:
            errors.append(f'manifest {key} must be 0')


if revision in {'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'}:
    rev0021_required = [
        'RECORD-INGRESS-ROUTER.json', 'INGRESS-ARTIFACT-TYPE-REGISTRY.json',
        'SOURCE-FAMILY-INGRESS-CROSSWALK.json', 'INGRESS-GATE-MATRIX.json',
        'SYNTHETIC-FIRST-PROTOCOL.json', 'LIVE-DATA-TRIPWIRE-LEDGER.json',
        'FIRST-LIVE-CANDIDATE-LANE-LEDGER.json', 'DATA-SURFACE-SCHEMA-REGISTRY.json',
        'JSON-SURFACE-SHAPE-AUDIT.json', 'ROOT-ALIAS-READINESS-LEDGER.json',
        'VALIDATOR-FACET-PROGRESS-LEDGER.json', 'NAMESPACE-DEBT-DELTA-LEDGER.json',
        'REV0021-ROUTE-DECISION-RECEIPT.json', 'REV0021-AUDIT-RECEIPT.json',
        'data/ingress/rev0021_artifact_type_registry.json',
        'data/ingress/rev0021_record_kind_ingress_routes.json',
        'data/ingress/rev0021_source_family_ingress_crosswalk.json',
        'data/ingress/rev0021_ingress_gate_matrix.json',
        'data/ingress/rev0021_synthetic_first_fixture_queue.json',
        'data/ingress/rev0021_live_data_tripwires.json',
        'data/ingress/rev0021_first_live_candidate_lanes.json',
        'data/refactor/rev0021_json_surface_shape_audit.json',
        'data/refactor/rev0021_schema_registry_rows.json',
        'data/refactor/rev0021_root_alias_readiness.json',
        'data/refactor/rev0021_validator_facet_progress.json',
        'data/refactor/rev0021_namespace_debt_delta.json',
        'tools/validators/rev0021_ingress_router_checks.py',
        'docs/80-ops/rev0021-record-ingress-router.md',
        'docs/80-ops/synthetic-first-protocol-rev0021.md',
        'docs/80-ops/live-data-tripwires-rev0021.md',
        'docs/90-audit/schema-registry-audit-rev0021.md',
        'docs/90-audit/root-alias-readiness-rev0021.md',
        'docs/00-meta/rev0021-handoff.md',
    ]
    for rel in rev0021_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0021 required file: {rel}')

    art_obj_21 = json_data.get('data/ingress/rev0021_artifact_type_registry.json', {})
    artifacts_21 = art_obj_21.get('artifact_types', [])
    if art_obj_21.get('artifact_type_count') != len(artifacts_21) or len(artifacts_21) != 40:
        errors.append(f'rev0021 artifact type count mismatch: {len(artifacts_21)}')
    packet_type_ids_20 = {p.get('packet_type_id') for p in packet_types_20}
    risk_ids_20_check = {r.get('risk_tier_id') for r in risk_tiers_20}
    lifecycle_ids_17_check = {s.get('state_id') for s in states_17}
    artifact_kinds_21 = {a.get('artifact_kind') for a in artifacts_21}
    for a in artifacts_21:
        if a.get('record_kind') != 'ingress_artifact_type_definition':
            errors.append(f"rev0021 artifact {a.get('artifact_type_id')} wrong record_kind")
        if a.get('recommended_packet_type_id') not in packet_type_ids_20:
            errors.append(f"rev0021 artifact {a.get('artifact_type_id')} references unknown packet type")
        if a.get('default_risk_tier_id') not in risk_ids_20_check:
            errors.append(f"rev0021 artifact {a.get('artifact_type_id')} references unknown risk tier")
        if a.get('minimum_lifecycle_state_id') not in lifecycle_ids_17_check:
            errors.append(f"rev0021 artifact {a.get('artifact_type_id')} references unknown lifecycle state")
        if a.get('can_create_live_person_record_by_type_rev0021') is not False or a.get('can_create_public_claim_by_type_rev0021') is not False:
            errors.append(f"rev0021 artifact {a.get('artifact_type_id')} allows live person or public claim")

    route_obj_21 = json_data.get('data/ingress/rev0021_record_kind_ingress_routes.json', {})
    routes_21 = route_obj_21.get('routes', [])
    if route_obj_21.get('route_count') != len(routes_21) or len(routes_21) != 44:
        errors.append(f'rev0021 ingress route count mismatch: {len(routes_21)}')
    route_ids_21 = {r.get('ingress_route_id') for r in routes_21}
    route_kinds_21 = {r.get('future_record_kind') for r in routes_21}
    lane_ids_19_check = {l.get('lane_id') for l in lanes_19}
    fam_ids_19_check = {f.get('source_family_id') for f in families_19}
    for r in routes_21:
        if r.get('recommended_packet_type_id') not in packet_type_ids_20:
            errors.append(f"rev0021 route {r.get('ingress_route_id')} references unknown packet type")
        if r.get('default_risk_tier_id') not in risk_ids_20_check:
            errors.append(f"rev0021 route {r.get('ingress_route_id')} references unknown risk tier")
        if r.get('minimum_lifecycle_state_id') not in lifecycle_ids_17_check:
            errors.append(f"rev0021 route {r.get('ingress_route_id')} references unknown lifecycle state")
        if r.get('owning_lane_id') not in lane_ids_19_check:
            errors.append(f"rev0021 route {r.get('ingress_route_id')} references unknown lane")
        for fam in r.get('related_source_family_ids', []):
            if fam not in fam_ids_19_check:
                errors.append(f"rev0021 route {r.get('ingress_route_id')} references unknown source family")
        for art in r.get('allowed_input_artifact_kinds', []):
            if art not in artifact_kinds_21:
                errors.append(f"rev0021 route {r.get('ingress_route_id')} references unknown artifact kind {art}")
        if r.get('live_records_created_rev0021') != 0 or r.get('public_claims_admitted_rev0021') != 0:
            errors.append(f"rev0021 route {r.get('ingress_route_id')} admits live records or public claims")
        if r.get('public_display_allowed_by_route_rev0021') is not False:
            errors.append(f"rev0021 route {r.get('ingress_route_id')} allows public display")

    cross_obj_21 = json_data.get('data/ingress/rev0021_source_family_ingress_crosswalk.json', {})
    cross_21 = cross_obj_21.get('rows', [])
    if cross_obj_21.get('crosswalk_row_count') != len(cross_21) or len(cross_21) != 24:
        errors.append(f'rev0021 source-family ingress crosswalk count mismatch: {len(cross_21)}')
    for row in cross_21:
        if row.get('source_family_id') not in fam_ids_19_check:
            errors.append(f"rev0021 crosswalk {row.get('crosswalk_id')} references unknown source family")
        if row.get('first_recommended_ingress_route_id') not in route_ids_21:
            errors.append(f"rev0021 crosswalk {row.get('crosswalk_id')} references unknown ingress route")
        if row.get('live_person_records_allowed_rev0021') is not False or row.get('public_claims_admitted_rev0021') != 0:
            errors.append(f"rev0021 crosswalk {row.get('crosswalk_id')} allows live people or public claims")

    gates_obj_21 = json_data.get('data/ingress/rev0021_ingress_gate_matrix.json', {})
    gates_21 = gates_obj_21.get('gates', [])
    if gates_obj_21.get('gate_count') != len(gates_21) or len(gates_21) != 24:
        errors.append(f'rev0021 gate count mismatch: {len(gates_21)}')
    for g in gates_21:
        if g.get('required_before_public_claim_by_default') is not True:
            errors.append(f"rev0021 gate {g.get('gate_id')} does not require public-claim gate")
        if g.get('public_claims_admitted_rev0021') != 0:
            errors.append(f"rev0021 gate {g.get('gate_id')} admits public claims")

    fx_obj_21 = json_data.get('data/ingress/rev0021_synthetic_first_fixture_queue.json', {})
    fixtures_21 = fx_obj_21.get('fixtures', [])
    if fx_obj_21.get('fixture_count') != len(fixtures_21) or len(fixtures_21) != 18:
        errors.append(f'rev0021 fixture count mismatch: {len(fixtures_21)}')
    for fx in fixtures_21:
        if fx.get('uses_live_people_or_real_incidents') is not False or fx.get('uses_live_source_payload') is not False:
            errors.append(f"rev0021 fixture {fx.get('fixture_id')} uses live data")
        if fx.get('recommended_packet_type_id') not in packet_type_ids_20:
            errors.append(f"rev0021 fixture {fx.get('fixture_id')} references unknown packet type")

    tw_obj_21 = json_data.get('data/ingress/rev0021_live_data_tripwires.json', {})
    tw_21 = tw_obj_21.get('tripwires', [])
    if tw_obj_21.get('tripwire_count') != len(tw_21) or len(tw_21) != 25:
        errors.append(f'rev0021 tripwire count mismatch: {len(tw_21)}')
    for tw in tw_21:
        if tw.get('requires_decision_receipt_to_override') is not True:
            errors.append(f"rev0021 tripwire {tw.get('tripwire_id')} missing override receipt")
        if tw.get('public_claims_admitted_rev0021') != 0:
            errors.append(f"rev0021 tripwire {tw.get('tripwire_id')} admits public claims")

    cand_obj_21 = json_data.get('data/ingress/rev0021_first_live_candidate_lanes.json', {})
    cands_21 = cand_obj_21.get('candidate_lanes', [])
    if cand_obj_21.get('candidate_lane_count') != len(cands_21) or len(cands_21) != 12:
        errors.append(f'rev0021 first-live candidate lane count mismatch: {len(cands_21)}')
    if cand_obj_21.get('live_data_opened_rev0021') is not False:
        errors.append('rev0021 first-live candidate lanes opened live data')
    for c in cands_21:
        if c.get('recommended_ingress_route_id') not in route_ids_21:
            errors.append(f"rev0021 candidate {c.get('candidate_lane_id')} references unknown route")
        if c.get('live_data_opened_rev0021') is not False or c.get('public_claims_admitted_rev0021') != 0:
            errors.append(f"rev0021 candidate {c.get('candidate_lane_id')} opens live data or claims")

    schema_obj_21 = json_data.get('data/refactor/rev0021_schema_registry_rows.json', {})
    schema_rows_21 = schema_obj_21.get('rows', [])
    if schema_obj_21.get('schema_registry_row_count') != len(schema_rows_21):
        errors.append('rev0021 schema registry row_count mismatch')
    if schema_obj_21.get('machine_schema_enforcement_enabled_rev0021') is not False:
        errors.append('rev0021 should not claim universal schema enforcement')
    for sr in schema_rows_21:
        if sr.get('schema_candidate') and not (ROOT / sr.get('schema_candidate')).exists():
            errors.append(f"rev0021 schema registry row {sr.get('schema_registry_row_id')} points to missing schema")
        if sr.get('public_claims_admitted_rev0021') != 0:
            errors.append(f"rev0021 schema registry row {sr.get('schema_registry_row_id')} admits public claims")

    shape_obj_21 = json_data.get('data/refactor/rev0021_json_surface_shape_audit.json', {})
    shape_rows_21 = shape_obj_21.get('rows', [])
    if shape_obj_21.get('audited_json_surface_count') != len(shape_rows_21):
        errors.append('rev0021 json shape audit count mismatch')
    if shape_obj_21.get('json_parse_error_count') != 0:
        errors.append('rev0021 json shape audit has parse errors')

    alias_obj_21 = json_data.get('data/refactor/rev0021_root_alias_readiness.json', {})
    alias_rows_21 = alias_obj_21.get('rows', [])
    if alias_obj_21.get('root_surface_count') != len(alias_rows_21):
        errors.append('rev0021 root alias row_count mismatch')
    for ar in alias_rows_21:
        if ar.get('move_allowed_rev0021') is not False or ar.get('destructive_moves_performed_rev0021') != 0:
            errors.append(f"rev0021 alias {ar.get('alias_row_id')} allows move or destructive action")

    facet_obj_21 = json_data.get('data/refactor/rev0021_validator_facet_progress.json', {})
    facets_21 = facet_obj_21.get('facets', [])
    if facet_obj_21.get('facet_count') != len(facets_21) or len(facets_21) != 14:
        errors.append(f'rev0021 facet progress count mismatch: {len(facets_21)}')
    if not any(f.get('implemented_module') == 'tools/validators/rev0021_ingress_router_checks.py' for f in facets_21):
        errors.append('rev0021 ingress validator facet module not registered')

    for key in ['live_source_rows_created_rev0021','live_artifacts_created_rev0021','live_evidence_atoms_created_rev0021','live_claim_candidates_created_rev0021','live_review_packets_created_rev0021','person_records_created_rev0021','incident_records_created_rev0021','lawsuit_records_created_rev0021','settlement_records_created_rev0021','public_claims_admitted_rev0021','public_displays_admitted_rev0021','destructive_moves_performed_rev0021']:
        if manifest.get(key, 0) != 0:
            errors.append(f'manifest {key} must be 0')



if revision in {'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'}:
    rev0022_required = [
        'CORRECTION-RIGHT-OF-REPLY-KERNEL.json', 'CONTESTATION-ROUTER.json',
        'COUNTEREVIDENCE-PACKET-LEDGER.json', 'RIGHT-OF-REPLY-DISPLAY-GATE.json',
        'CORRECTION-STATE-MACHINE-LEDGER.json', 'ABUSE-AND-MANIPULATION-GUARDRAIL.json',
        'RETRACTION-AND-ROLLBACK-RECEIPT-GRAMMAR.json', 'PUBLIC-CORRECTION-DISPLAY-GATE-LEDGER.json',
        'SURFACE-LOCATOR-INDEX.json', 'NAMESPACE-COUPLING-AUDIT.json', 'SCHEMA-HOLE-QUEUE.json',
        'VALIDATOR-FACET-SMOKE-REPORT.json', 'REV0022-ROUTE-DECISION-RECEIPT.json', 'REV0022-AUDIT-RECEIPT.json',
        'data/corrections/rev0022_correction_request_types.json',
        'data/corrections/rev0022_correction_state_machine.json',
        'data/corrections/rev0022_correction_transition_gates.json',
        'data/corrections/rev0022_right_of_reply_routes.json',
        'data/corrections/rev0022_counterevidence_packet_templates.json',
        'data/corrections/rev0022_update_action_matrix.json',
        'data/corrections/rev0022_abuse_guardrail_patterns.json',
        'data/corrections/rev0022_public_correction_display_gates.json',
        'data/corrections/rev0022_rollback_receipt_templates.json',
        'data/corrections/rev0022_correction_risk_tiers.json',
        'data/corrections/rev0022_correction_review_roles.json',
        'data/corrections/rev0022_source_family_correction_crosswalk.json',
        'data/corrections/rev0022_synthetic_correction_fixtures.json',
        'data/refactor/rev0022_surface_locator_index.json',
        'data/refactor/rev0022_namespace_coupling_audit.json',
        'data/refactor/rev0022_schema_hole_queue.json',
        'data/refactor/rev0022_validator_facet_smoke_report.json',
        'tools/validators/rev0022_correction_office_checks.py',
        'docs/80-ops/rev0022-correction-right-of-reply-office.md',
        'docs/80-ops/right-of-reply-and-contestation-routes-rev0022.md',
        'docs/80-ops/counterevidence-packet-method-rev0022.md',
        'docs/80-ops/rollback-receipt-grammar-rev0022.md',
        'docs/90-audit/surface-locator-refactor-rev0022.md',
        'docs/90-audit/validator-facet-smoke-rev0022.md',
        'docs/90-audit/schema-hole-queue-rev0022.md',
        'docs/00-meta/rev0022-handoff.md',
    ]
    for rel in rev0022_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0022 required file: {rel}')

    req_obj_22 = json_data.get('data/corrections/rev0022_correction_request_types.json', {})
    req_22 = req_obj_22.get('request_types', [])
    if req_obj_22.get('request_type_count') != len(req_22) or len(req_22) != 18:
        errors.append(f'rev0022 correction request type count mismatch: {len(req_22)}')
    req_ids_22 = {r.get('correction_request_type_id') for r in req_22}
    for r in req_22:
        if r.get('record_kind') != 'correction_request_type_definition':
            errors.append(f"rev0022 request type {r.get('correction_request_type_id')} wrong record_kind")
        if r.get('can_directly_change_public_display_by_type_rev0022') is not False:
            errors.append(f"rev0022 request type {r.get('correction_request_type_id')} can directly change public display")
        if r.get('can_create_live_person_or_incident_record_rev0022') is not False:
            errors.append(f"rev0022 request type {r.get('correction_request_type_id')} creates live person/incident record")
        if r.get('public_claims_admitted_rev0022') != 0 or r.get('live_records_created_rev0022') != 0:
            errors.append(f"rev0022 request type {r.get('correction_request_type_id')} admits claims or live records")

    sm_obj_22 = json_data.get('data/corrections/rev0022_correction_state_machine.json', {})
    states_22 = sm_obj_22.get('states', [])
    trans_22 = sm_obj_22.get('transitions', [])
    if sm_obj_22.get('state_count') != len(states_22) or len(states_22) != 20:
        errors.append(f'rev0022 correction state count mismatch: {len(states_22)}')
    if sm_obj_22.get('transition_count') != len(trans_22) or len(trans_22) != 34:
        errors.append(f'rev0022 correction transition count mismatch: {len(trans_22)}')
    state_ids_22 = {s.get('correction_state_id') for s in states_22}
    for s in states_22:
        if s.get('can_create_public_claim_rev0022') is not False or s.get('can_create_live_person_record_rev0022') is not False:
            errors.append(f"rev0022 state {s.get('correction_state_id')} allows claim or live person")
    for t in trans_22:
        if t.get('from_state_id') not in state_ids_22 or t.get('to_state_id') not in state_ids_22:
            errors.append(f"rev0022 transition {t.get('transition_id')} references unknown state")
        if t.get('creates_public_claim_rev0022') is not False or t.get('creates_live_record_rev0022') is not False:
            errors.append(f"rev0022 transition {t.get('transition_id')} creates claim or live record")

    gates_obj_22 = json_data.get('data/corrections/rev0022_correction_transition_gates.json', {})
    gates_22 = gates_obj_22.get('gates', [])
    if gates_obj_22.get('gate_count') != len(gates_22) or len(gates_22) != 22:
        errors.append(f'rev0022 correction gate count mismatch: {len(gates_22)}')
    for g in gates_22:
        if g.get('required_before_public_update_by_default') is not True:
            errors.append(f"rev0022 gate {g.get('correction_gate_id')} missing public update requirement")
        if g.get('public_claims_admitted_rev0022') != 0 or g.get('live_records_created_rev0022') != 0:
            errors.append(f"rev0022 gate {g.get('correction_gate_id')} admits claim or live record")

    reply_obj_22 = json_data.get('data/corrections/rev0022_right_of_reply_routes.json', {})
    replies_22 = reply_obj_22.get('routes', [])
    if reply_obj_22.get('route_count') != len(replies_22) or len(replies_22) != 12:
        errors.append(f'rev0022 right-of-reply route count mismatch: {len(replies_22)}')
    for rr in replies_22:
        if rr.get('reply_text_public_by_default') is not False or rr.get('does_not_override_source_record') is not True:
            errors.append(f"rev0022 reply route {rr.get('right_of_reply_route_id')} has unsafe defaults")
        if rr.get('public_claims_admitted_rev0022') != 0:
            errors.append(f"rev0022 reply route {rr.get('right_of_reply_route_id')} admits public claims")

    for path, key, count_field, expected in [
        ('data/corrections/rev0022_counterevidence_packet_templates.json','templates','template_count',15),
        ('data/corrections/rev0022_update_action_matrix.json','actions','action_count',14),
        ('data/corrections/rev0022_abuse_guardrail_patterns.json','patterns','pattern_count',13),
        ('data/corrections/rev0022_public_correction_display_gates.json','gates','gate_count',12),
        ('data/corrections/rev0022_rollback_receipt_templates.json','templates','template_count',12),
        ('data/corrections/rev0022_correction_risk_tiers.json','risk_tiers','tier_count',8),
        ('data/corrections/rev0022_correction_review_roles.json','roles','role_count',10),
        ('data/corrections/rev0022_synthetic_correction_fixtures.json','fixtures','fixture_count',16),
    ]:
        obj = json_data.get(path, {})
        arr = obj.get(key, [])
        if obj.get(count_field) != len(arr) or len(arr) != expected:
            errors.append(f'rev0022 {path} count mismatch: {len(arr)} expected {expected}')
        for row in arr:
            if row.get('public_claims_admitted_rev0022', 0) != 0 or row.get('live_records_created_rev0022', 0) != 0:
                errors.append(f"rev0022 {path} row admits public claims or live records")
            if path.endswith('synthetic_correction_fixtures.json') and (row.get('uses_live_people_or_real_incidents') is not False or row.get('uses_live_source_payload') is not False):
                errors.append(f"rev0022 fixture {row.get('fixture_id')} uses live data")

    sf_cross_obj_22 = json_data.get('data/corrections/rev0022_source_family_correction_crosswalk.json', {})
    sf_cross_22 = sf_cross_obj_22.get('rows', [])
    if sf_cross_obj_22.get('crosswalk_row_count') != len(sf_cross_22) or len(sf_cross_22) != 24:
        errors.append(f'rev0022 source-family correction crosswalk count mismatch: {len(sf_cross_22)}')
    fam_ids_check_22 = {f.get('source_family_id') for f in families_19}
    for row in sf_cross_22:
        if row.get('source_family_id') not in fam_ids_check_22:
            errors.append(f"rev0022 source-family correction crosswalk {row.get('correction_crosswalk_id')} references unknown source family")
        if row.get('primary_correction_request_type_id') not in req_ids_22:
            errors.append(f"rev0022 source-family correction crosswalk {row.get('correction_crosswalk_id')} references unknown correction type")
        if row.get('live_data_allowed_rev0022') is not False or row.get('public_claims_admitted_rev0022') != 0:
            errors.append(f"rev0022 source-family correction crosswalk {row.get('correction_crosswalk_id')} opens live data or claims")

    loc_obj_22 = json_data.get('data/refactor/rev0022_surface_locator_index.json', {})
    loc_rows_22 = loc_obj_22.get('rows', [])
    if loc_obj_22.get('surface_count') != len(loc_rows_22):
        errors.append('rev0022 surface locator count mismatch')
    for row in loc_rows_22:
        if row.get('move_allowed_rev0022') is not False or row.get('destructive_move_performed_rev0022') != 0:
            errors.append(f"rev0022 surface locator {row.get('surface_locator_id')} allows/performs move")

    namespace_obj_22 = json_data.get('data/refactor/rev0022_namespace_coupling_audit.json', {})
    ns_rows_22 = namespace_obj_22.get('rows', [])
    if namespace_obj_22.get('coupling_row_count') != len(ns_rows_22):
        errors.append('rev0022 namespace coupling count mismatch')
    if namespace_obj_22.get('destructive_moves_performed_rev0022') != 0:
        errors.append('rev0022 namespace audit performed destructive moves')

    holes_obj_22 = json_data.get('data/refactor/rev0022_schema_hole_queue.json', {})
    holes_22 = holes_obj_22.get('rows', [])
    if holes_obj_22.get('schema_hole_count') != len(holes_22):
        errors.append('rev0022 schema hole queue count mismatch')
    if holes_obj_22.get('machine_schema_enforcement_enabled_rev0022') is not False:
        errors.append('rev0022 schema hole queue incorrectly enables universal schema enforcement')

    smoke_obj_22 = json_data.get('data/refactor/rev0022_validator_facet_smoke_report.json', {})
    smoke_rows_22 = smoke_obj_22.get('rows', [])
    if smoke_obj_22.get('smoke_row_count') != len(smoke_rows_22):
        errors.append('rev0022 validator smoke count mismatch')
    if not any(row.get('module_path') == 'tools/validators/rev0022_correction_office_checks.py' and row.get('has_validate_function') is True for row in smoke_rows_22):
        errors.append('rev0022 correction validator facet missing from smoke report')

    for key in ['live_correction_requests_created_rev0022','public_correction_notes_published_rev0022','live_source_rows_created_rev0022','live_artifacts_created_rev0022','live_evidence_atoms_created_rev0022','live_claim_candidates_created_rev0022','person_records_created_rev0022','incident_records_created_rev0022','lawsuit_records_created_rev0022','settlement_records_created_rev0022','public_claims_admitted_rev0022','public_displays_admitted_rev0022','destructive_moves_performed_rev0022']:
        if manifest.get(key, 0) != 0:
            errors.append(f'manifest {key} must be 0')



if revision in {'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'}:
    rev0023_required = [
        'ACCESS-PUBLICATION-KERNEL.json', 'AUDIENCE-ROLE-LEDGER.json', 'PUBLICATION-TIER-LEDGER.json',
        'ROLE-FEATURE-PERMISSION-MATRIX.json', 'MISUSE-THREAT-MODEL-LEDGER.json', 'DATA-MINIMIZATION-GATE-LEDGER.json',
        'BULK-EXPORT-GATE-LEDGER.json', 'SENSITIVE-MEDIA-HANDLING-LEDGER.json', 'LAW-ENFORCEMENT-ACCESS-BOUNDARY.json',
        'PUBLICATION-DENIAL-REASON-LEDGER.json', 'ACCESS-DECISION-RECEIPT-GRAMMAR.json', 'ACCESS-OFFICE-REENTRY-CARD.json',
        'ACCESS-SURFACE-COUPLING-AUDIT.json', 'ROOT-NAMESPACE-SHADOW-MANIFEST.json', 'SCHEMA-HOLE-CLOSURE-PLAN.json',
        'REV0023-ROUTE-DECISION-RECEIPT.json', 'REV0023-AUDIT-RECEIPT.json',
        'data/access/rev0023_audience_roles.json', 'data/access/rev0023_publication_tiers.json',
        'data/access/rev0023_source_family_access_routes.json', 'data/access/rev0023_role_feature_permission_matrix.json',
        'data/access/rev0023_data_minimization_gates.json', 'data/access/rev0023_misuse_threat_model.json',
        'data/access/rev0023_bulk_export_gates.json', 'data/access/rev0023_sensitive_media_rules.json',
        'data/access/rev0023_law_enforcement_access_boundaries.json', 'data/access/rev0023_publication_denial_reasons.json',
        'data/access/rev0023_access_decision_receipt_templates.json', 'data/access/rev0023_synthetic_access_fixtures.json',
        'data/refactor/rev0023_access_surface_coupling_audit.json', 'data/refactor/rev0023_root_namespace_shadow_manifest.json',
        'data/refactor/rev0023_schema_hole_closure_plan.json', 'data/refactor/rev0023_validator_facet_smoke_report.json',
        'tools/validators/rev0023_access_office_checks.py',
        'docs/80-ops/rev0023-access-publication-office.md', 'docs/80-ops/role-access-and-misuse-boundaries-rev0023.md',
        'docs/60-display/publication-tier-ladder-rev0023.md', 'docs/60-display/bulk-export-and-api-gates-rev0023.md',
        'docs/20-constitution/no-police-intelligence-product-rev0023.md', 'docs/90-audit/access-surface-refactor-audit-rev0023.md',
        'docs/90-audit/schema-hole-closure-plan-rev0023.md', 'docs/00-meta/rev0023-handoff.md',
        'schemas/audience_role.schema.json', 'schemas/publication_tier.schema.json', 'schemas/role_feature_permission.schema.json',
        'schemas/source_family_access_route.schema.json', 'schemas/data_minimization_gate.schema.json', 'schemas/misuse_threat.schema.json',
        'schemas/bulk_export_gate.schema.json', 'schemas/access_decision_receipt_template.schema.json',
    ]
    for rel in rev0023_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0023 required file: {rel}')

    roles_obj_23 = json_data.get('data/access/rev0023_audience_roles.json', {})
    roles_23 = roles_obj_23.get('roles', [])
    if roles_obj_23.get('role_count') != len(roles_23) or len(roles_23) != 18:
        errors.append(f'rev0023 audience role count mismatch: {len(roles_23)}')
    role_ids_23 = {r.get('audience_role_id') for r in roles_23}
    role_keys_23 = {r.get('role_key') for r in roles_23}
    for r in roles_23:
        if r.get('can_receive_raw_person_level_payloads_by_default_rev0023') is not False or r.get('can_create_public_claims_by_role_rev0023') is not False:
            errors.append(f"rev0023 role {r.get('audience_role_id')} has unsafe defaults")
        if r.get('public_claims_admitted_rev0023') != 0 or r.get('live_records_created_rev0023') != 0:
            errors.append(f"rev0023 role {r.get('audience_role_id')} admits claims/live records")
    for required_role in ['law_enforcement_agency_employer','commercial_data_broker','family_or_survivor','public_defender']:
        if required_role not in role_keys_23:
            errors.append(f'rev0023 missing required audience role {required_role}')

    tier_obj_23 = json_data.get('data/access/rev0023_publication_tiers.json', {})
    tiers_23 = tier_obj_23.get('publication_tiers', [])
    if tier_obj_23.get('publication_tier_count') != len(tiers_23) or len(tiers_23) != 14:
        errors.append(f'rev0023 publication tier count mismatch: {len(tiers_23)}')
    tier_keys_23 = {t.get('tier_key') for t in tiers_23}
    for t in tiers_23:
        if t.get('requires_decision_receipt_before_publication') is not True:
            errors.append(f"rev0023 tier {t.get('publication_tier_id')} lacks decision receipt")
        if t.get('live_data_enabled_rev0023') is not False or t.get('public_claims_admitted_rev0023') != 0:
            errors.append(f"rev0023 tier {t.get('publication_tier_id')} enables live data or claims")

    routes_obj_23 = json_data.get('data/access/rev0023_source_family_access_routes.json', {})
    routes_23 = routes_obj_23.get('routes', [])
    if routes_obj_23.get('route_count') != len(routes_23) or len(routes_23) != 24:
        errors.append(f'rev0023 source-family access route count mismatch: {len(routes_23)}')
    family_ids_23 = {f.get('source_family_id') for f in families_19}
    for row in routes_23:
        if row.get('source_family_id') not in family_ids_23:
            errors.append(f"rev0023 access route {row.get('source_family_access_route_id')} references unknown source family")
        if row.get('default_publication_tier_key') not in tier_keys_23:
            errors.append(f"rev0023 access route {row.get('source_family_access_route_id')} references unknown tier")
        if row.get('live_data_allowed_rev0023') is not False or row.get('public_claims_admitted_rev0023') != 0:
            errors.append(f"rev0023 access route {row.get('source_family_access_route_id')} opens live data/claims")

    perm_obj_23 = json_data.get('data/access/rev0023_role_feature_permission_matrix.json', {})
    perms_23 = perm_obj_23.get('rows', [])
    if perm_obj_23.get('permission_row_count') != len(perms_23) or len(perms_23) != 288:
        errors.append(f'rev0023 permission row count mismatch: {len(perms_23)}')
    for row in perms_23:
        if row.get('audience_role_id') not in role_ids_23:
            errors.append(f"rev0023 permission {row.get('permission_row_id')} references unknown role")
        if row.get('raw_payload_access_enabled_rev0023') is not False or row.get('sensitive_media_access_enabled_rev0023') is not False or row.get('live_data_access_enabled_rev0023') is not False:
            errors.append(f"rev0023 permission {row.get('permission_row_id')} enables access")
        if row.get('public_claims_admitted_rev0023') != 0:
            errors.append(f"rev0023 permission {row.get('permission_row_id')} admits public claims")

    for path, key, count_field, expected in [
        ('data/access/rev0023_data_minimization_gates.json','gates','gate_count',22),
        ('data/access/rev0023_misuse_threat_model.json','threats','threat_count',20),
        ('data/access/rev0023_bulk_export_gates.json','gates','gate_count',16),
        ('data/access/rev0023_sensitive_media_rules.json','rules','rule_count',14),
        ('data/access/rev0023_law_enforcement_access_boundaries.json','boundaries','boundary_count',14),
        ('data/access/rev0023_publication_denial_reasons.json','denial_reasons','denial_reason_count',16),
        ('data/access/rev0023_access_decision_receipt_templates.json','templates','template_count',12),
        ('data/access/rev0023_synthetic_access_fixtures.json','fixtures','fixture_count',15),
    ]:
        obj = json_data.get(path, {})
        arr = obj.get(key, [])
        if obj.get(count_field) != len(arr) or len(arr) != expected:
            errors.append(f'rev0023 {path} count mismatch: {len(arr)} expected {expected}')
        for row in arr:
            if row.get('public_claims_admitted_rev0023', 0) != 0 or row.get('live_records_created_rev0023', 0) != 0:
                errors.append(f'rev0023 {path} row admits claims/live records')
            if path.endswith('synthetic_access_fixtures.json') and (row.get('uses_live_people_or_real_incidents') is not False or row.get('uses_live_source_payload') is not False):
                errors.append(f"rev0023 fixture {row.get('fixture_id')} uses live data")
            if path.endswith('bulk_export_gates.json') and (row.get('can_release_person_level_adverse_data_rev0023') is not False or row.get('can_release_raw_payload_rev0023') is not False or row.get('can_release_sensitive_media_rev0023') is not False):
                errors.append('rev0023 bulk gate releases prohibited data')
            if path.endswith('sensitive_media_rules.json') and row.get('raw_payload_release_enabled_rev0023') is not False:
                errors.append('rev0023 media rule enables raw release')
            if path.endswith('law_enforcement_access_boundaries.json') and row.get('special_access_granted_rev0023') is not False:
                errors.append('rev0023 LE boundary grants special access')

    for path, key, count_field in [
        ('data/refactor/rev0023_access_surface_coupling_audit.json','rows','surface_count'),
        ('data/refactor/rev0023_root_namespace_shadow_manifest.json','rows','root_surface_count'),
        ('data/refactor/rev0023_schema_hole_closure_plan.json','rows','closure_row_count'),
        ('data/refactor/rev0023_validator_facet_smoke_report.json','rows','smoke_row_count'),
    ]:
        obj = json_data.get(path, {})
        arr = obj.get(key, [])
        if obj.get(count_field) != len(arr):
            errors.append(f'rev0023 {path} count mismatch')
        if obj.get('destructive_moves_performed_rev0023', 0) != 0:
            errors.append(f'rev0023 {path} performed destructive move')
    if json_data.get('data/refactor/rev0023_schema_hole_closure_plan.json', {}).get('machine_schema_enforcement_enabled_rev0023') is not False:
        errors.append('rev0023 schema hole closure incorrectly enables universal schema enforcement')
    if not any(row.get('module_path') == 'tools/validators/rev0023_access_office_checks.py' and row.get('has_validate_function') is True for row in json_data.get('data/refactor/rev0023_validator_facet_smoke_report.json', {}).get('rows', [])):
        errors.append('rev0023 access validator facet missing from smoke report')

    # Run the facet itself via filepath so `tools/` does not need to be a package.
    try:
        import importlib.util
        facet_path = ROOT / 'tools/validators/rev0023_access_office_checks.py'
        spec = importlib.util.spec_from_file_location('rev0023_access_office_checks', facet_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        errors.extend(module.validate(ROOT))
    except Exception as e:
        errors.append(f'rev0023 access validator facet failed to run: {e}')

    for key in ['live_access_requests_created_rev0023','live_source_rows_created_rev0023','live_artifacts_created_rev0023','live_evidence_atoms_created_rev0023','live_claim_candidates_created_rev0023','live_review_packets_created_rev0023','canonical_agency_records_created_rev0023','person_records_created_rev0023','officer_records_created_rev0023','civilian_records_created_rev0023','incident_records_created_rev0023','lawsuit_records_created_rev0023','settlement_records_created_rev0023','public_claims_admitted_rev0023','public_displays_admitted_rev0023','destructive_moves_performed_rev0023']:
        if manifest.get(key, 0) != 0:
            errors.append(f'manifest {key} must be 0')
    for key in ['role_gated_access_enabled_rev0023','bulk_exports_enabled_rev0023','raw_payload_release_enabled_rev0023','sensitive_media_release_enabled_rev0023','law_enforcement_special_access_granted_rev0023']:
        if manifest.get(key) is not False:
            errors.append(f'manifest {key} must be false')


if revision in {'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'}:
    rev0024_required = [
        'IDENTITY-RESOLUTION-KERNEL.json', 'IDENTITY-SIGNAL-TAXONOMY.json', 'MERGE-ABSTENTION-LEDGER.json',
        'UNMERGE-RECEIPT-GRAMMAR.json', 'IDENTITY-RISK-TIER-LEDGER.json', 'IDENTITY-PUBLIC-DISPLAY-GATE.json',
        'ALIAS-AND-IDENTIFIER-HANDLING-LEDGER.json', 'SOURCE-FAMILY-IDENTITY-ROUTING-LEDGER.json',
        'SYNTHETIC-IDENTITY-FIXTURE-LEDGER.json', 'IDENTITY-DECISION-RECEIPT-GRAMMAR.json',
        'IDENTITY-OFFICE-REENTRY-CARD.json', 'RECORD-KIND-COVERAGE-AUDIT.json', 'ID-FIELD-NORMALIZATION-AUDIT.json',
        'ROOT-JSON-CONSOLIDATION-CANDIDATES.json', 'VALIDATOR-FACADE-MAP.json', 'MANIFEST-TIMESTAMP-REPAIR-RECEIPT.json',
        'REV0024-ROUTE-DECISION-RECEIPT.json', 'REV0024-AUDIT-RECEIPT.json',
        'data/identity/rev0024_entity_classes.json', 'data/identity/rev0024_identifier_types.json',
        'data/identity/rev0024_identity_signal_taxonomy.json', 'data/identity/rev0024_merge_state_machine.json',
        'data/identity/rev0024_merge_abstention_rules.json', 'data/identity/rev0024_unmerge_receipt_templates.json',
        'data/identity/rev0024_identity_risk_tiers.json', 'data/identity/rev0024_source_family_identity_routes.json',
        'data/identity/rev0024_public_identity_display_gates.json', 'data/identity/rev0024_synthetic_identity_fixtures.json',
        'data/identity/rev0024_identity_decision_receipt_templates.json',
        'data/refactor/rev0024_record_kind_coverage_audit.json', 'data/refactor/rev0024_id_field_normalization_audit.json',
        'data/refactor/rev0024_root_json_consolidation_candidates.json', 'data/refactor/rev0024_validator_facade_map.json',
        'data/refactor/rev0024_manifest_timestamp_repair_receipt.json',
        'tools/validators/rev0024_identity_office_checks.py',
        'docs/40-model/rev0024-identity-resolution-office.md', 'docs/40-model/merge-abstention-and-unmerge-receipts-rev0024.md',
        'docs/20-constitution/identity-harm-and-public-display-rev0024.md', 'docs/80-ops/rev0024-identity-reviewer-playbook.md',
        'docs/90-audit/record-kind-id-field-audit-rev0024.md', 'docs/00-meta/rev0024-handoff.md',
    ]
    for rel in rev0024_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0024 required file: {rel}')
    try:
        import importlib.util
        facet_path = ROOT / 'tools/validators/rev0024_identity_office_checks.py'
        spec = importlib.util.spec_from_file_location('rev0024_identity_office_checks', facet_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        errors.extend(module.validate(ROOT))
    except Exception as e:
        errors.append(f'rev0024 identity validator facet failed to run: {e}')

    entity_24 = json_data.get('data/identity/rev0024_entity_classes.json', {}).get('entity_classes', [])
    identifier_24 = json_data.get('data/identity/rev0024_identifier_types.json', {}).get('identifier_types', [])
    signals_24 = json_data.get('data/identity/rev0024_identity_signal_taxonomy.json', {}).get('identity_signals', [])
    states_24 = json_data.get('data/identity/rev0024_merge_state_machine.json', {}).get('states', [])
    transitions_24 = json_data.get('data/identity/rev0024_merge_state_machine.json', {}).get('transitions', [])
    abstain_24 = json_data.get('data/identity/rev0024_merge_abstention_rules.json', {}).get('rules', [])
    unmerge_24 = json_data.get('data/identity/rev0024_unmerge_receipt_templates.json', {}).get('templates', [])
    public_gates_24 = json_data.get('data/identity/rev0024_public_identity_display_gates.json', {}).get('gates', [])
    routes_24 = json_data.get('data/identity/rev0024_source_family_identity_routes.json', {}).get('routes', [])
    fixtures_24 = json_data.get('data/identity/rev0024_synthetic_identity_fixtures.json', {}).get('fixtures', [])
    rk_cov_24 = json_data.get('data/refactor/rev0024_record_kind_coverage_audit.json', {}).get('rows', [])
    id_fields_24 = json_data.get('data/refactor/rev0024_id_field_normalization_audit.json', {}).get('rows', [])
    for field, expected in [
        ('identity_entity_classes_rev0024', len(entity_24)), ('identity_identifier_types_rev0024', len(identifier_24)),
        ('identity_signals_rev0024', len(signals_24)), ('identity_merge_states_rev0024', len(states_24)),
        ('identity_merge_transitions_rev0024', len(transitions_24)), ('merge_abstention_rules_rev0024', len(abstain_24)),
        ('unmerge_receipt_templates_rev0024', len(unmerge_24)), ('source_family_identity_routes_rev0024', len(routes_24)),
        ('identity_public_display_gates_rev0024', len(public_gates_24)), ('synthetic_identity_fixtures_rev0024', len(fixtures_24)),
        ('record_kind_coverage_surfaces_rev0024', len(rk_cov_24)), ('id_field_names_audited_rev0024', len(id_fields_24)),
    ]:
        if manifest.get(field) != expected:
            errors.append(f'manifest {field} mismatch')
else:
    entity_24 = identifier_24 = signals_24 = states_24 = transitions_24 = abstain_24 = unmerge_24 = public_gates_24 = routes_24 = fixtures_24 = rk_cov_24 = id_fields_24 = []



if revision in {'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'}:
    rev0025_required = [
        'REV0025-BRANCH-RECONCILIATION-LEDGER.json', 'BRANCH-COLLISION-REPAIR-RECEIPT.json',
        'FOUNDATION-BRANCH-MERGE-INDEX.json', 'INCIDENT-EVENT-SPINE-KERNEL.json',
        'INCIDENT-ROLE-TAXONOMY-LEDGER.json', 'FORCE-AND-CUSTODY-EVENT-TAXONOMY.json',
        'INCIDENT-LIFECYCLE-STATE-MACHINE.json', 'INCIDENT-SOURCE-FAMILY-CROSSWALK.json',
        'INCIDENT-PRIVACY-AND-DUE-PROCESS-GATE.json', 'INCIDENT-PUBLIC-DISPLAY-GATE.json',
        'INCIDENT-MINIMUM-SOURCE-BUNDLE-LEDGER.json', 'INCIDENT-TO-LAWSUIT-SETTLEMENT-BRIDGE.json',
        'SYNTHETIC-INCIDENT-FIXTURE-LEDGER.json', 'ROOT-SURFACE-OFFICE-SHADOW-MAP-REV0025.json',
        'VALIDATOR-BRANCH-MERGE-AUDIT.json', 'INCIDENT-SCHEMA-LINKAGE-AUDIT.json',
        'NAMESPACE-MIGRATION-WAVE1-PLAN-REV0025.json',
        'CIVILIAN-FAMILY-DIGNITY-KERNEL.json', 'IDENTITY-RESOLUTION-KERNEL.json',
        'data/incidents/rev0025_incident_event_types.json', 'data/incidents/rev0025_incident_roles.json',
        'data/incidents/rev0025_incident_lifecycle_state_machine.json',
        'data/incidents/rev0025_incident_process_link_types.json',
        'data/incidents/rev0025_incident_privacy_due_process_gates.json',
        'data/incidents/rev0025_incident_public_display_gates.json',
        'data/incidents/rev0025_incident_minimum_source_bundle_rules.json',
        'data/incidents/rev0025_incident_source_family_crosswalk.json',
        'data/incidents/rev0025_synthetic_incident_fixtures.json',
        'data/incidents/rev0025_incident_bridge_rules.json',
        'tools/validators/rev0025_incident_office_checks.py',
        'tools/validators/rev0024_civilian_family_dignity_checks.py',
    ]
    for rel in rev0025_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0025 required file: {rel}')
    try:
        import importlib.util
        for mod_name in ['rev0024_civilian_family_dignity_checks', 'rev0025_incident_office_checks']:
            facet_path = ROOT / 'tools/validators' / f'{mod_name}.py'
            spec = importlib.util.spec_from_file_location(mod_name, facet_path)
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
            errors.extend(module.validate(ROOT))
    except Exception as e:
        errors.append(f'rev0025 validator facet failed to run: {e}')

    event_25 = json_data.get('data/incidents/rev0025_incident_event_types.json', {}).get('event_types', [])
    roles_25 = json_data.get('data/incidents/rev0025_incident_roles.json', {}).get('roles', [])
    sm_25 = json_data.get('data/incidents/rev0025_incident_lifecycle_state_machine.json', {})
    states_25 = sm_25.get('states', [])
    transitions_25 = sm_25.get('transitions', [])
    cross_25 = json_data.get('data/incidents/rev0025_incident_source_family_crosswalk.json', {}).get('rows', [])
    fixtures_25 = json_data.get('data/incidents/rev0025_synthetic_incident_fixtures.json', {}).get('fixtures', [])
    for field, expected in [
        ('incident_event_types_rev0025', len(event_25)), ('incident_roles_rev0025', len(roles_25)),
        ('incident_lifecycle_states_rev0025', len(states_25)), ('incident_lifecycle_transitions_rev0025', len(transitions_25)),
        ('incident_source_family_crosswalk_rows_rev0025', len(cross_25)), ('synthetic_incident_fixtures_rev0025', len(fixtures_25)),
    ]:
        if manifest.get(field) != expected:
            errors.append(f'manifest {field} mismatch')
else:
    event_25 = roles_25 = states_25 = transitions_25 = cross_25 = fixtures_25 = []


if revision in {'rev0026', 'rev0027', 'rev0028', 'rev0029'}:
    rev0026_required = [
        'LITIGATION-SETTLEMENT-SPINE-KERNEL.json', 'LAWSUIT-RECORD-TAXONOMY-LEDGER.json',
        'CASE-PARTY-ROLE-TAXONOMY.json', 'CASE-LIFECYCLE-STATE-MACHINE.json',
        'LEGAL-CLAIM-TYPE-CROSSWALK-LEDGER.json', 'DISPOSITION-AND-RELIEF-TAXONOMY.json',
        'SETTLEMENT-FINANCE-GATE-LEDGER.json', 'SETTLEMENT-NO-ADMISSION-GUARDRAIL.json',
        'PLAINTIFF-PRIVACY-GATE-LEDGER.json', 'QUALIFIED-IMMUNITY-SIGNAL-GATE.json',
        'LITIGATION-INCIDENT-BRIDGE-GATE.json', 'LITIGATION-PUBLIC-DISPLAY-GATE.json',
        'LITIGATION-CORRECTION-ROUTE-LEDGER.json', 'SOURCE-FAMILY-LAWSUIT-SETTLEMENT-CROSSWALK.json',
        'SYNTHETIC-LITIGATION-FIXTURE-LEDGER.json', 'PACKAGE-HYGIENE-AUDIT-REV0026.json',
        'PYCACHE-EXCLUSION-RECEIPT-REV0026.json', 'LITIGATION-SCHEMA-LINKAGE-AUDIT.json',
        'ROOT-LITIGATION-SURFACE-SHADOW-MAP-REV0026.json', 'VALIDATOR-FACET-INVENTORY-REV0026.json',
        'NAMESPACE-MIGRATION-WAVE2-PLAN-REV0026.json', 'REV0026-AUDIT-RECEIPT.json',
        'LITIGATION-OFFICE-REENTRY-CARD.json', 'data/litigation/rev0026_case_artifact_types.json',
        'data/litigation/rev0026_case_party_roles.json', 'data/litigation/rev0026_case_lifecycle_state_machine.json',
        'data/litigation/rev0026_legal_claim_type_taxonomy.json', 'data/litigation/rev0026_disposition_relief_taxonomy.json',
        'data/litigation/rev0026_settlement_finance_field_contracts.json', 'data/litigation/rev0026_settlement_no_admission_guardrails.json',
        'data/litigation/rev0026_plaintiff_privacy_gates.json', 'data/litigation/rev0026_qualified_immunity_procedural_signal_gates.json',
        'data/litigation/rev0026_litigation_incident_bridge_gates.json', 'data/litigation/rev0026_litigation_public_display_gates.json',
        'data/litigation/rev0026_litigation_correction_routes.json', 'data/litigation/rev0026_source_family_litigation_routes.json',
        'data/litigation/rev0026_synthetic_litigation_fixtures.json', 'tools/validators/rev0026_litigation_office_checks.py',
        'docs/40-model/rev0026-litigation-settlement-spine.md', 'docs/40-model/settlement-no-admission-guardrails-rev0026.md',
        'docs/20-constitution/plaintiff-privacy-and-case-voice-rev0026.md', 'docs/80-ops/rev0026-litigation-reviewer-playbook.md',
        'docs/90-audit/package-hygiene-and-validator-audit-rev0026.md', 'docs/00-meta/rev0026-handoff.md',
    ]
    for rel in rev0026_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0026 required file: {rel}')
    try:
        import importlib.util
        facet_path = ROOT / 'tools/validators/rev0026_litigation_office_checks.py'
        spec = importlib.util.spec_from_file_location('rev0026_litigation_office_checks', facet_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        errors.extend(module.validate(ROOT))
    except Exception as e:
        errors.append(f'rev0026 litigation validator facet failed to run: {e}')

    case_artifacts_26 = json_data.get('data/litigation/rev0026_case_artifact_types.json', {}).get('case_artifact_types', [])
    party_roles_26 = json_data.get('data/litigation/rev0026_case_party_roles.json', {}).get('case_party_roles', [])
    sm_26 = json_data.get('data/litigation/rev0026_case_lifecycle_state_machine.json', {})
    case_states_26 = sm_26.get('states', [])
    case_transitions_26 = sm_26.get('transitions', [])
    legal_claim_types_26 = json_data.get('data/litigation/rev0026_legal_claim_type_taxonomy.json', {}).get('legal_claim_types', [])
    disposition_relief_26 = json_data.get('data/litigation/rev0026_disposition_relief_taxonomy.json', {}).get('disposition_relief_types', [])
    settlement_fields_26 = json_data.get('data/litigation/rev0026_settlement_finance_field_contracts.json', {}).get('settlement_finance_fields', [])
    no_admission_26 = json_data.get('data/litigation/rev0026_settlement_no_admission_guardrails.json', {}).get('guardrails', [])
    source_family_litigation_routes_26 = json_data.get('data/litigation/rev0026_source_family_litigation_routes.json', {}).get('routes', [])
    synthetic_litigation_fixtures_26 = json_data.get('data/litigation/rev0026_synthetic_litigation_fixtures.json', {}).get('fixtures', [])
else:
    case_artifacts_26 = party_roles_26 = case_states_26 = case_transitions_26 = legal_claim_types_26 = disposition_relief_26 = settlement_fields_26 = no_admission_26 = source_family_litigation_routes_26 = synthetic_litigation_fixtures_26 = []


if revision in {'rev0027', 'rev0028', 'rev0029'}:
    rev0027_required = [
        'DISCIPLINE-CERTIFICATION-MOBILITY-KERNEL.json', 'EMPLOYMENT-ARTIFACT-TAXONOMY-LEDGER.json',
        'EMPLOYMENT-ROLE-TAXONOMY-LEDGER.json', 'CERTIFICATION-DECERTIFICATION-STATE-MACHINE.json',
        'SEPARATION-REASON-GUARDRAIL.json', 'DISCIPLINE-OUTCOME-TAXONOMY-LEDGER.json',
        'RECORD-DESTRUCTION-CLAUSE-LEDGER.json', 'OFFICER-MOBILITY-INDICATOR-LEDGER.json',
        'POST-SOURCE-INTAKE-GATE.json', 'DECERTIFICATION-APPEAL-GATE-LEDGER.json',
        'WANDERING-DETECTION-GATE-LEDGER.json', 'ARBITRATION-REINSTATEMENT-BRIDGE-LEDGER.json',
        'EMPLOYMENT-IDENTITY-BRIDGE-GATE.json', 'EMPLOYMENT-PUBLIC-DISPLAY-GATE.json',
        'EMPLOYMENT-CORRECTION-ROUTE-LEDGER.json', 'SOURCE-FAMILY-EMPLOYMENT-CERTIFICATION-CROSSWALK.json',
        'EMPLOYMENT-DECISION-RECEIPT-GRAMMAR.json', 'PERSONLESS-MOBILITY-PATH-TEMPLATE-LEDGER.json',
        'SYNTHETIC-EMPLOYMENT-MOBILITY-FIXTURE-LEDGER.json', 'EMPLOYMENT-OFFICE-REENTRY-CARD.json',
        'data/employment/rev0027_employment_artifact_types.json', 'data/employment/rev0027_certification_state_machine.json',
        'data/employment/rev0027_source_family_employment_routes.json', 'tools/validators/rev0027_employment_office_checks.py',
        'docs/40-model/rev0027-discipline-certification-mobility-spine.md', 'docs/00-meta/rev0027-handoff.md',
    ]
    for rel in rev0027_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0027 required file: {rel}')
    try:
        import importlib.util
        facet_path = ROOT / 'tools/validators/rev0027_employment_office_checks.py'
        spec = importlib.util.spec_from_file_location('rev0027_employment_office_checks', facet_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        errors.extend(module.validate(ROOT))
    except Exception as e:
        errors.append(f'rev0027 employment validator facet failed to run: {e}')
    employment_artifacts_27 = json_data.get('data/employment/rev0027_employment_artifact_types.json', {}).get('employment_artifact_types', [])
    employment_roles_27 = json_data.get('data/employment/rev0027_employment_roles.json', {}).get('employment_roles', [])
    cert_sm_27 = json_data.get('data/employment/rev0027_certification_state_machine.json', {})
    cert_states_27 = cert_sm_27.get('states', [])
    cert_transitions_27 = cert_sm_27.get('transitions', [])
    sep_reasons_27 = json_data.get('data/employment/rev0027_separation_reason_taxonomy.json', {}).get('separation_reasons', [])
    discipline_outcomes_27 = json_data.get('data/employment/rev0027_discipline_outcome_taxonomy.json', {}).get('discipline_outcomes', [])
    mobility_indicators_27 = json_data.get('data/employment/rev0027_mobility_indicator_taxonomy.json', {}).get('mobility_indicators', [])
    wandering_gates_27 = json_data.get('data/employment/rev0027_wandering_detection_gates.json', {}).get('gates', [])
    employment_routes_27 = json_data.get('data/employment/rev0027_source_family_employment_routes.json', {}).get('routes', [])
    employment_fixtures_27 = json_data.get('data/employment/rev0027_synthetic_employment_fixtures.json', {}).get('fixtures', [])
else:
    employment_artifacts_27 = employment_roles_27 = cert_states_27 = cert_transitions_27 = sep_reasons_27 = discipline_outcomes_27 = mobility_indicators_27 = wandering_gates_27 = employment_routes_27 = employment_fixtures_27 = []


if revision in {'rev0028', 'rev0029'}:
    rev0028_required = [
        'POLICY-CONTRACT-GOVERNANCE-KERNEL.json', 'POLICY-ARTIFACT-TAXONOMY-LEDGER.json',
        'POLICY-PROVISION-TAXONOMY-LEDGER.json', 'UNION-CONTRACT-ACCOUNTABILITY-CLAUSE-LEDGER.json',
        'POLICY-VERSION-LIFECYCLE-STATE-MACHINE.json', 'POLICY-EFFECTIVE-DATE-GATE.json',
        'POLICY-INCIDENT-BRIDGE-GATE.json', 'POLICY-EMPLOYMENT-DISCIPLINE-BRIDGE-GATE.json',
        'POLICY-LITIGATION-BRIDGE-GATE.json', 'POLICY-PUBLIC-DISPLAY-GATE.json',
        'SOURCE-FAMILY-POLICY-CONTRACT-CROSSWALK.json', 'SYNTHETIC-POLICY-CONTRACT-FIXTURE-LEDGER.json',
        'ROOT-POLICY-SURFACE-SHADOW-MAP-REV0028.json', 'VALIDATOR-FACET-INVENTORY-REV0028.json',
        'data/policy/rev0028_policy_artifact_types.json', 'data/policy/rev0028_policy_version_state_machine.json',
        'data/policy/rev0028_source_family_policy_routes.json', 'tools/validators/rev0028_policy_contract_office_checks.py',
        'docs/40-model/rev0028-policy-contract-governance-spine.md', 'docs/00-meta/rev0028-handoff.md',
    ]
    for rel in rev0028_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0028 required file: {rel}')
    try:
        import importlib.util
        facet_path = ROOT / 'tools/validators/rev0028_policy_contract_office_checks.py'
        spec = importlib.util.spec_from_file_location('rev0028_policy_contract_office_checks', facet_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        errors.extend(module.validate(ROOT))
    except Exception as e:
        errors.append(f'rev0028 policy contract validator facet failed to run: {e}')
    policy_artifacts_28 = json_data.get('data/policy/rev0028_policy_artifact_types.json', {}).get('policy_artifact_types', [])
    policy_provisions_28 = json_data.get('data/policy/rev0028_policy_provision_taxonomy.json', {}).get('policy_provisions', [])
    union_clauses_28 = json_data.get('data/policy/rev0028_union_contract_accountability_clauses.json', {}).get('union_contract_clauses', [])
    policy_sm_28 = json_data.get('data/policy/rev0028_policy_version_state_machine.json', {})
    policy_states_28 = policy_sm_28.get('states', [])
    policy_transitions_28 = policy_sm_28.get('transitions', [])
    policy_effective_gates_28 = json_data.get('data/policy/rev0028_effective_date_gates.json', {}).get('gates', [])
    source_family_policy_routes_28 = json_data.get('data/policy/rev0028_source_family_policy_routes.json', {}).get('routes', [])
    synthetic_policy_fixtures_28 = json_data.get('data/policy/rev0028_synthetic_policy_fixtures.json', {}).get('fixtures', [])
else:
    policy_artifacts_28 = policy_provisions_28 = union_clauses_28 = policy_states_28 = policy_transitions_28 = policy_effective_gates_28 = source_family_policy_routes_28 = synthetic_policy_fixtures_28 = []


if revision == 'rev0029':
    rev0029_required = [
        'BRADY-GIGLIO-DISCLOSURE-KERNEL.json', 'DISCLOSURE-ARTIFACT-TAXONOMY-LEDGER.json',
        'DISCLOSURE-SIGNAL-TAXONOMY-LEDGER.json', 'CREDIBILITY-ISSUE-TAXONOMY-LEDGER.json',
        'DISCLOSURE-LIFECYCLE-STATE-MACHINE.json', 'BRADY-GIGLIO-SCOPE-GATE.json',
        'TESTIMONY-CASE-LINK-GATE.json', 'PROSECUTOR-OFFICE-BOUNDARY-GATE.json',
        'DEFENSE-WORKBENCH-ROUTE-LEDGER.json', 'BRADY-GIGLIO-PUBLIC-DISPLAY-GATE.json',
        'PROTECTIVE-ORDER-SEALING-GUARDRAIL.json', 'BRADY-GIGLIO-ACCESS-BOUNDARY-LEDGER.json',
        'SOURCE-FAMILY-BRADY-GIGLIO-CROSSWALK.json', 'BRADY-GIGLIO-DECISION-RECEIPT-GRAMMAR.json',
        'BRADY-GIGLIO-CORRECTION-ROUTE-LEDGER.json', 'SYNTHETIC-BRADY-GIGLIO-FIXTURE-LEDGER.json',
        'ROOT-BRADY-SURFACE-SHADOW-MAP-REV0029.json', 'VALIDATOR-FACET-INVENTORY-REV0029.json',
        'ARCHIVE-HEAD-REPAIR-RECEIPT-REV0029.json', 'data/brady_giglio/rev0029_disclosure_artifact_types.json',
        'data/brady_giglio/rev0029_disclosure_signal_taxonomy.json', 'data/brady_giglio/rev0029_credibility_issue_taxonomy.json',
        'data/brady_giglio/rev0029_disclosure_lifecycle_state_machine.json', 'data/brady_giglio/rev0029_scope_gates.json',
        'data/brady_giglio/rev0029_testimony_case_link_gates.json', 'data/brady_giglio/rev0029_source_family_brady_routes.json',
        'data/brady_giglio/rev0029_public_display_gates.json', 'data/brady_giglio/rev0029_synthetic_disclosure_fixtures.json',
        'tools/validators/rev0029_brady_giglio_office_checks.py', 'docs/40-model/rev0029-brady-giglio-disclosure-office.md',
        'docs/00-meta/rev0029-handoff.md',
    ]
    for rel in rev0029_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing rev0029 required file: {rel}')
    try:
        import importlib.util
        facet_path = ROOT / 'tools/validators/rev0029_brady_giglio_office_checks.py'
        spec = importlib.util.spec_from_file_location('rev0029_brady_giglio_office_checks', facet_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        errors.extend(module.validate(ROOT))
    except Exception as e:
        errors.append(f'rev0029 Brady/Giglio validator facet failed to run: {e}')
    brady_artifacts_29 = json_data.get('data/brady_giglio/rev0029_disclosure_artifact_types.json', {}).get('disclosure_artifact_types', [])
    brady_signals_29 = json_data.get('data/brady_giglio/rev0029_disclosure_signal_taxonomy.json', {}).get('signals', [])
    credibility_issues_29 = json_data.get('data/brady_giglio/rev0029_credibility_issue_taxonomy.json', {}).get('credibility_issues', [])
    sm_29 = json_data.get('data/brady_giglio/rev0029_disclosure_lifecycle_state_machine.json', {})
    brady_states_29 = sm_29.get('states', [])
    brady_transitions_29 = sm_29.get('transitions', [])
    brady_scope_gates_29 = json_data.get('data/brady_giglio/rev0029_scope_gates.json', {}).get('gates', [])
    brady_testimony_gates_29 = json_data.get('data/brady_giglio/rev0029_testimony_case_link_gates.json', {}).get('gates', [])
    brady_routes_29 = json_data.get('data/brady_giglio/rev0029_source_family_brady_routes.json', {}).get('routes', [])
    brady_fixtures_29 = json_data.get('data/brady_giglio/rev0029_synthetic_disclosure_fixtures.json', {}).get('fixtures', [])
else:
    brady_artifacts_29 = brady_signals_29 = credibility_issues_29 = brady_states_29 = brady_transitions_29 = brady_scope_gates_29 = brady_testimony_gates_29 = brady_routes_29 = brady_fixtures_29 = []

if errors:
    print('VALIDATION FAILED')
    for e in errors:
        print('-', e)
    sys.exit(1)
print(f'VALIDATION PASSED for {revision}: {len(json_data)} JSON files checked, {len(docs)} document labels, {len(mo)} matter objects, {len(accessions)} PDF URL accessions, {len(atoms)} rev0007 proof atoms, {len(gaps)} accession gaps, {len(bundles)} rev0008 status bundles, {len(queue)} acquisition tickets, {len(edges)} rollback edges, {len(role_rows)} rev0009 document roles, {len(shells)} page shells, {len(perms)} module gates, {len(aics)} rev0010 agency candidates, {len(bridges)} denominator/source bridges, {len(pgs)} public agency gates, {len(freeze_tickets)} rev0011 freeze tickets, {len(res_tickets)} link-resolution tickets, {len(check_items)} checksum debt items, {len(mut_rows)} mutation watches, {len(link_rows)} rev0012 link-target observations, {len(news_rows)} news resnapshots, {len(cap_targets)} capture targets, {len(fix_states)} fixity states, {len(envs)} rev0013 payload envelopes, {len(pref_rows_13)} privacy rows, {len(batches_13)} capture batches, {len(gates_13)} extractive gates, {len(anchor_obs_14)} rev0014 anchors, {len(sentinels_14)} rev0014 diff sentinels, {len(link_anchors_14)} rev0014 link anchors, {len(prov_templates_14)} provenance templates, {len(telos_rows_15)} rev0015 telos statements, {len(dream_rows_15)} dreams, {len(rungs_15)} capability rungs, {len(horizon_15)} open horizons, {len(states_17)} rev0017 lifecycle states, {len(trans_17)} lifecycle transitions, {len(file_rows_17)} lifecycle file crosswalk rows, {len(rk_rows_17)} record-kind crosswalk rows, {len(atom_defs_18) if revision in {'rev0018', 'rev0019', 'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} rev0018 atom types, {len(templates) if revision in {'rev0018', 'rev0019', 'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} claim templates, {len(defeaters) if revision in {'rev0018', 'rev0019', 'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} defeater classes, {len(families_19) if revision in {'rev0019', 'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} rev0019 source families, {len(lanes_19) if revision in {'rev0019', 'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} corpus lanes, {len(root_rows_19) if revision in {'rev0019', 'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} root inventory rows, {len(packet_states_20) if revision in {'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} rev0020 packet states, {len(packet_types_20) if revision in {'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} packet types, {len(risk_tiers_20) if revision in {'rev0020', 'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} risk tiers, {len(routes_21) if revision in {'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} rev0021 ingress routes, {len(artifacts_21) if revision in {'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} artifact types, {len(tw_21) if revision in {'rev0021', 'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} live-data tripwires, {len(req_22) if revision in {'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} rev0022 correction request types, {len(states_22) if revision in {'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} correction states, {len(sf_cross_22) if revision in {'rev0022', 'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} source-family correction crosswalk rows, {len(roles_23) if revision in {'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} rev0023 audience roles, {len(tiers_23) if revision in {'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} publication tiers, {len(perms_23) if revision in {'rev0023', 'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} role-feature permission rows, {len(entity_24) if revision in {'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} rev0024 entity classes, {len(signals_24) if revision in {'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} identity signals, {len(abstain_24) if revision in {'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} abstention rules, {len(routes_24) if revision in {'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} source-family identity routes, {len(rk_cov_24) if revision in {'rev0024', 'rev0025', 'rev0026', 'rev0027', 'rev0028', 'rev0029'} else 0} record-kind audit rows, {len(case_artifacts_26)} rev0026 case artifact types, {len(party_roles_26)} case party roles, {len(case_states_26)} case lifecycle states, {len(case_transitions_26)} case lifecycle transitions, {len(legal_claim_types_26)} legal claim types, {len(settlement_fields_26)} settlement finance fields, {len(no_admission_26)} no-admission guardrails, {len(source_family_litigation_routes_26)} litigation source-family routes, {len(employment_artifacts_27)} rev0027 employment artifact types, {len(employment_roles_27)} employment roles, {len(cert_states_27)} certification states, {len(cert_transitions_27)} certification transitions, {len(mobility_indicators_27)} mobility indicators, {len(wandering_gates_27)} wandering gates, {len(employment_routes_27)} employment source-family routes, {len(employment_fixtures_27)} synthetic employment fixtures, {len(policy_artifacts_28)} rev0028 policy artifact types, {len(policy_provisions_28)} policy provision types, {len(union_clauses_28)} union contract clauses, {len(policy_states_28)} policy version states, {len(policy_transitions_28)} policy version transitions, {len(policy_effective_gates_28)} effective-date gates, {len(source_family_policy_routes_28)} policy source-family routes, {len(synthetic_policy_fixtures_28)} synthetic policy fixtures, {len(brady_artifacts_29)} rev0029 disclosure artifact types, {len(brady_signals_29)} disclosure signals, {len(credibility_issues_29)} credibility issue categories, {len(brady_states_29)} disclosure lifecycle states, {len(brady_transitions_29)} disclosure lifecycle transitions, {len(brady_scope_gates_29)} scope gates, {len(brady_testimony_gates_29)} testimony/case-link gates, {len(brady_routes_29)} Brady/Giglio source-family routes, {len(brady_fixtures_29)} synthetic disclosure fixtures')
