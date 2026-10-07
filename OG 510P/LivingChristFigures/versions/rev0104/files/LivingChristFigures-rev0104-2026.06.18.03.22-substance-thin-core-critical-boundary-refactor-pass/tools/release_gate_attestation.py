#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, subprocess, sys
from pathlib import Path

sys.dont_write_bytecode = True

FIELDS=['gate_id','gate_name','status','evidence_files','blocking_findings','note']

def read_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def severity_count_json(path: Path, severity: str) -> int:
    data=read_json(path)
    if not isinstance(data, list): return -1
    return sum(1 for r in data if r.get('severity')==severity)


def high_count_json(path: Path) -> int:
    data=read_json(path)
    if not isinstance(data, list): return -1
    return sum(1 for r in data if r.get('severity')=='high')

def schema_high_count_for_gate(path: Path) -> int:
    """Count schema highs while excluding this attestation's own bootstrap/self-reference checks."""
    data=read_json(path)
    if not isinstance(data, list): return -1
    self_checks={'release_gate_attestation_file_exists','release_gate_attestation_rows','release_gate_attestation_failures'}
    return sum(1 for r in data if r.get('severity')=='high' and r.get('check') not in self_checks)

def gate(gid, name, ok, evidence, note, block=''):
    return {'gate_id':gid,'gate_name':name,'status':'pass' if ok else 'fail','evidence_files':'|'.join(evidence),'blocking_findings':block,'note':note}

def run(root: Path):
    rows=[]
    manifest=read_json(root/'manifest.json') or {}
    pub=read_json(root/'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json') or {}
    contract=read_json(root/'SCHEMA/Package-Release-Contract-current.json') or {}
    cur=manifest.get('revision','')
    rows.append(gate('gate_001','manifest_revision_alignment', cur and pub.get('revision')==cur and pub.get('package_revision')==cur and contract.get('package_revision')==cur, ['manifest.json','PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json','SCHEMA/Package-Release-Contract-current.json'], 'manifest, public manifest, and package contract revisions align'))
    rows.append(gate('gate_002','schema_validation_zero_high', schema_high_count_for_gate(root/'SCHEMA/Schema-Validation-Report-current.json')==0, ['SCHEMA/Schema-Validation-Report-current.json'], 'schema validator has zero high findings outside release-gate self-reference'))
    rows.append(gate('gate_003','row_validation_zero_high', high_count_json(root/'SCHEMA/Row-Validation-Report-current.json')==0, ['SCHEMA/Row-Validation-Report-current.json'], 'row-level validation has zero high findings'))
    rows.append(gate('gate_004','public_release_lint_zero_high', high_count_json(root/'META/Public-Release-Lint-current.json')==0, ['META/Public-Release-Lint-current.json'], 'public release lint has zero high findings'))
    rows.append(gate('gate_005','redaction_open_high_zero', high_count_json(root/'META/Redaction-Risk-Open-Findings-current.json')==0, ['META/Redaction-Risk-Open-Findings-current.json'], 'open configured high-risk redaction findings are zero'))
    rows.append(gate('gate_006','rule46_high_zero', high_count_json(root/'META/Rule46-Scan-current.json') in {0}, ['META/Rule46-Scan-current.json'], 'MMIWG2S+ extraction scanner has zero high findings'))
    public_high=[r for r in read_csv(root/'META/Sensitive-Surface-Inventory-current.csv') if r.get('file_scope')=='public' and r.get('severity')=='high']
    rows.append(gate('gate_007','sensitive_public_high_zero', len(public_high)==0, ['META/Sensitive-Surface-Inventory-current.csv'], 'sensitive-surface inventory has no high-risk public rows', str(len(public_high))))
    cand_ids={r.get('candidate_id','') for r in read_csv(root/'Candidate-Ledger-current.csv')}
    elig_ids={r.get('candidate_id','') for r in read_csv(root/'META/Public-Export-Eligibility-current.csv')}
    snap_ids={r.get('candidate_id','') for r in read_csv(root/'META/Candidate-Governance-Snapshot-current.csv')}
    rows.append(gate('gate_008','candidate_governance_coverage', cand_ids==elig_ids==snap_ids and len(cand_ids)>0, ['Candidate-Ledger-current.csv','META/Public-Export-Eligibility-current.csv','META/Candidate-Governance-Snapshot-current.csv'], 'eligibility and governance snapshot cover every candidate'))
    source_ids={r.get('source_id','') for r in read_csv(root/'Source-Registry-current.csv')}
    link_ids={r.get('source_id','') for r in read_csv(root/'META/Public-Source-Link-Review-current.csv')}
    rows.append(gate('gate_009','source_link_review_coverage', source_ids==link_ids and len(source_ids)>0, ['Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv'], 'public source-link review covers every source'))
    rev_high=high_count_json(root/'META/Revision-Surface-Audit-current.json')
    rows.append(gate('gate_010','revision_surface_zero_high', rev_high==0, ['META/Revision-Surface-Audit-current.json'], 'front-door revision surface has zero high findings'))
    prov_rows=read_csv(root/'META/Generated-Artifact-Provenance-current.csv')
    prov_ok=prov_rows and all(r.get('status')=='pass' for r in prov_rows)
    rows.append(gate('gate_011','generated_artifact_provenance_pass', bool(prov_ok), ['META/Generated-Artifact-Provenance-current.csv'], 'tracked generated artifacts have present inputs and recorded hashes'))
    pub_files={str(p.relative_to(root)) for p in (root/'PUBLIC').glob('*') if p.is_file()}
    allowed=set(contract.get('allowed_public_layer_files',[]))
    rows.append(gate('gate_012','public_layer_contract_closed', bool(pub_files) and pub_files==allowed, ['PUBLIC/','SCHEMA/Package-Release-Contract-current.json'], 'PUBLIC/ file set equals allowlist'))
    rows.append(gate('gate_013','public_index_parity_zero_high', high_count_json(root/'META/Public-Index-Parity-current.json')==0, ['META/Public-Index-Parity-current.json'], 'public index CSV/JSON/Markdown, manifest count, eligibility fields, and sentinels agree'))
    rows.append(gate('gate_014','governance_consistency_zero_high', high_count_json(root/'META/Governance-Consistency-Audit-current.json')==0, ['META/Governance-Consistency-Audit-current.json'], 'eligibility, public index, snapshot, queue, consent, link review, and governance decisions agree under configured checks'))
    dep_rows=read_csv(root/'META/Package-Dependency-Graph-current.csv')
    dep_missing=[r.get('edge_id','') for r in dep_rows if r.get('status')=='missing_dependency']
    rows.append(gate('gate_015','package_dependency_graph_no_missing', bool(dep_rows) and not dep_missing, ['META/Package-Dependency-Graph-current.csv'], 'configured generator/input/public-contract/frontmatter/ledger-mirror dependency edges point to existing package paths', '; '.join(dep_missing[:8])))
    rows.append(gate('gate_016','csv_json_mirror_audit_zero_high', high_count_json(root/'META/CSV-JSON-Mirror-Audit-current.json')==0, ['META/CSV-JSON-Mirror-Audit-current.json'], 'exact CSV/JSON mirror audit has zero high findings'))
    rows.append(gate('gate_017','schema_coverage_audit_zero_backlog', high_count_json(root/'META/Schema-Coverage-Audit-current.json')==0 and severity_count_json(root/'META/Schema-Coverage-Audit-current.json','medium')==0, ['META/Schema-Coverage-Audit-current.json'], 'schema coverage audit has zero high findings and zero medium backlog rows'))
    inv_rows=read_csv(root/'META/Package-File-Inventory-current.csv')
    inv_public=[r for r in inv_rows if r.get('package_zone')=='public_layer']
    rows.append(gate('gate_018','package_file_inventory_present', bool(inv_rows) and bool(inv_public), ['META/Package-File-Inventory-current.csv'], 'package file inventory exists, classifies package zones, and includes public-layer rows'))
    rows.append(gate('gate_019','field_schema_consistency_zero_high', high_count_json(root/'META/Field-Schema-Consistency-Audit-current.json')==0, ['META/Field-Schema-Consistency-Audit-current.json'], 'field-schema consistency audit has zero high findings; exact field schemas match target headers'))

    rows.append(gate('gate_020','path_reference_audit_zero_high', high_count_json(root/'META/Path-Reference-Audit-current.json')==0, ['META/Path-Reference-Audit-current.json'], 'path-reference audit has zero high findings'))
    trace_rows=read_csv(root/'META/Rule-Gate-Traceability-current.csv')
    trace_bad=[r.get('rule_number','') for r in trace_rows if r.get('trace_status') in {'missing_boundary_coverage','missing_trace_file'}]
    rows.append(gate('gate_021','rule_gate_traceability_no_missing', bool(trace_rows) and not trace_bad, ['META/Rule-Gate-Traceability-current.csv'], 'rule-gate traceability has no missing coverage or missing trace-file rows', '; '.join(trace_bad[:8])))
    tool_rows=read_csv(root/'META/Tool-Run-Matrix-current.csv')
    tool_bad=[r.get('tool_path','') for r in tool_rows if r.get('status')!='pass']
    rows.append(gate('gate_022','tool_run_matrix_all_pass', bool(tool_rows) and not tool_bad, ['META/Tool-Run-Matrix-current.csv'], 'tool-run matrix has no non-pass rows', '; '.join(tool_bad[:8])))
    rows.append(gate('gate_023','required_document_coverage_zero_high', high_count_json(root/'META/Required-Document-Coverage-current.json')==0, ['META/Required-Document-Coverage-current.json'], 'required-document coverage has zero high findings'))
    selftest_rows=read_csv(root/'META/Audit-Selftest-current.csv')
    selftest_bad=[r.get('selftest_id','') for r in selftest_rows if r.get('status')!='pass']
    rows.append(gate('gate_024','audit_selftest_all_pass', bool(selftest_rows) and not selftest_bad, ['META/Audit-Selftest-current.csv'], 'controlled mutation self-tests all pass', '; '.join(selftest_bad[:8])))
    rows.append(gate('gate_025','rebuild_readiness_zero_high', high_count_json(root/'META/Rebuild-Readiness-Audit-current.json')==0, ['META/Rebuild-Readiness-Audit-current.json'], 'deterministic rebuild-readiness audit has zero high findings'))

    policy_rows=read_csv(root/'META/Policy-Assertion-Matrix-current.csv')
    policy_bad=[r.get('assertion_id','') for r in policy_rows if r.get('status')!='pass']
    rows.append(gate('gate_026','policy_assertion_matrix_all_pass', bool(policy_rows) and not policy_bad, ['META/Policy-Assertion-Matrix-current.csv'], 'policy assertions map to existing evidence reports and all pass', '; '.join(policy_bad[:8])))
    regen_rows=read_csv(root/'META/Regeneration-Sequence-Plan-current.csv')
    regen_bad=[r.get('step_id','') for r in regen_rows if r.get('dependency_status')!='pass']
    rows.append(gate('gate_027','regeneration_sequence_plan_no_missing', bool(regen_rows) and not regen_bad, ['META/Regeneration-Sequence-Plan-current.csv'], 'regeneration sequence plan has no missing dependency rows', '; '.join(regen_bad[:8])))
    archive_rows=read_csv(root/'META/Archive-Build-Manifest-current.csv')
    archive_bad=[r.get('build_check_id','') for r in archive_rows if r.get('status')!='pass']
    rows.append(gate('gate_028','archive_build_manifest_all_pass', bool(archive_rows) and not archive_bad, ['META/Archive-Build-Manifest-current.csv'], 'archive build manifest checks all pass', '; '.join(archive_bad[:8])))
    coverage_rows=read_csv(root/'META/Selftest-Coverage-Matrix-current.csv')
    coverage_bad=[r.get('coverage_id','') for r in coverage_rows if r.get('coverage_status')!='pass']
    rows.append(gate('gate_029','selftest_coverage_matrix_all_pass', bool(coverage_rows) and not coverage_bad, ['META/Selftest-Coverage-Matrix-current.csv'], 'critical release-gate selftest coverage rows all pass', '; '.join(coverage_bad[:8])))

    checksum_rows=read_csv(root/'META/Checksum-Scope-Audit-current.csv')
    checksum_bad=[r.get('scope_check_id','') for r in checksum_rows if r.get('severity')=='high' or r.get('status')=='fail']
    rows.append(gate('gate_030','checksum_scope_audit_all_pass', bool(checksum_rows) and not checksum_bad, ['META/Checksum-Scope-Audit-current.csv'], 'checksum scope covers stable package files with no high/fail rows', '; '.join(checksum_bad[:8])))
    neg_rows=read_csv(root/'META/Public-Negative-Corpus-current.csv')
    neg_bad=[r.get('test_id','') for r in neg_rows if r.get('status')!='pass']
    rows.append(gate('gate_031','public_negative_corpus_all_pass', bool(neg_rows) and not neg_bad, ['META/Public-Negative-Corpus-current.csv'], 'public negative-corpus fixtures are caught at expected severity', '; '.join(neg_bad[:8])))
    closure_rows=read_csv(root/'META/Release-Evidence-Closure-current.csv')
    closure_bad=[r.get('closure_check_id','') for r in closure_rows if r.get('severity')=='high' or r.get('status')=='fail']
    rows.append(gate('gate_032','release_evidence_closure_all_pass', bool(closure_rows) and not closure_bad, ['META/Release-Evidence-Closure-current.csv'], 'release gates, evidence paths, policy assertions, selftests, provenance, and inventory close', '; '.join(closure_bad[:8])))
    archive_member_rows=read_csv(root/'META/Archive-Member-Manifest-current.csv')
    archive_member_bad=[r.get('package_path','') for r in archive_member_rows if r.get('status')!='pass']
    rows.append(gate('gate_033','archive_member_manifest_all_pass', bool(archive_member_rows) and not archive_member_bad, ['META/Archive-Member-Manifest-current.csv'], 'archive-member manifest paths are root-prefixed and all rows pass', '; '.join(archive_member_bad[:8])))
    unicode_rows=read_csv(root/'META/Unicode-Path-Audit-current.csv')
    unicode_bad=[r.get('check','') for r in unicode_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_034','unicode_path_audit_zero_high_fail', bool(unicode_rows) and not unicode_bad, ['META/Unicode-Path-Audit-current.csv'], 'Unicode/path audit has zero high failures', '; '.join(unicode_bad[:8])))
    identity_rows=read_csv(root/'META/Package-Identity-Audit-current.csv')
    identity_bad=[r.get('identity_check_id','') for r in identity_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_035','package_identity_audit_zero_high_fail', bool(identity_rows) and not identity_bad, ['META/Package-Identity-Audit-current.csv'], 'package identity audit has zero high failures', '; '.join(identity_bad[:8])))

    lineage_rows=read_csv(root/'META/Version-Lineage-Audit-current.csv')
    lineage_bad=[r.get('lineage_check_id','') for r in lineage_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_036','version_lineage_audit_zero_high_fail', bool(lineage_rows) and not lineage_bad, ['META/Version-Lineage-Audit-current.csv'], 'version-lineage audit has zero high/fail rows', '; '.join(lineage_bad[:8])))
    delta_rows=read_csv(root/'META/Package-Delta-Manifest-current.csv')
    delta_removed=[r.get('path','') for r in delta_rows if r.get('change_type')=='removed' or r.get('status')=='fail']
    rows.append(gate('gate_037','package_delta_manifest_no_removed', bool(delta_rows) and not delta_removed, ['META/Package-Delta-Manifest-current.csv'], 'package-delta manifest has no removed stable-file rows', '; '.join(delta_removed[:8])))
    reference_rows=read_csv(root/'META/Cross-Report-Reference-Audit-current.csv')
    reference_bad=[r.get('reference_check_id','') for r in reference_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_038','cross_report_reference_audit_zero_high_fail', bool(reference_rows) and not reference_bad, ['META/Cross-Report-Reference-Audit-current.csv'], 'cross-report reference audit has zero high/fail rows', '; '.join(reference_bad[:8])))
    digest_rows=read_csv(root/'META/Handoff-Review-Digest-current.csv')
    digest_bad=[r.get('digest_id','') for r in digest_rows if r.get('status')!='pass']
    digest_topics={r.get('topic',''):r.get('value','') for r in digest_rows}
    digest_stale=[]
    if cur and digest_topics.get('revision')!=cur:
        digest_stale.append(f"revision={digest_topics.get('revision','')} expected {cur}")
    if manifest.get('export_name_without_zip','') and digest_topics.get('export_name_without_zip')!=manifest.get('export_name_without_zip',''):
        digest_stale.append('export_name_without_zip mismatch')
    rows.append(gate('gate_039','handoff_review_digest_all_pass_and_current', bool(digest_rows) and not digest_bad and not digest_stale, ['META/Handoff-Review-Digest-current.csv','manifest.json'], 'handoff review digest has no non-pass rows and matches manifest revision/export', '; '.join((digest_bad+digest_stale)[:8])))
    cycle_rows=read_csv(root/'META/Dependency-Cycle-Audit-current.csv')
    cycle_bad=[r.get('cycle_id','') for r in cycle_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_040','dependency_cycle_audit_zero_high_fail', bool(cycle_rows) and not cycle_bad, ['META/Dependency-Cycle-Audit-current.csv'], 'dependency-cycle audit has zero high/fail rows', '; '.join(cycle_bad[:8])))
    notice_rows=read_csv(root/'META/Handoff-Notice-Audit-current.csv')
    notice_bad=[r.get('notice_check_id','') for r in notice_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_041','handoff_notice_audit_zero_high_fail', bool(notice_rows) and not notice_bad, ['META/Handoff-Notice-Audit-current.csv'], 'handoff-notice audit has zero high/fail rows', '; '.join(notice_bad[:8])))
    surface_rows=read_csv(root/'META/Current-Surface-Registry-current.csv')
    surface_bad=[r.get('surface_path','') for r in surface_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_042','current_surface_registry_all_classified', bool(surface_rows) and not surface_bad, ['META/Current-Surface-Registry-current.csv'], 'current-surface registry has no unclassified/high-fail rows', '; '.join(surface_bad[:8])))

    manifest_semantic_rows=read_csv(root/'META/Manifest-Semantic-Coherence-Audit-current.csv')
    manifest_semantic_bad=[r.get('check_id','') for r in manifest_semantic_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_043','manifest_semantic_coherence_zero_high_fail', bool(manifest_semantic_rows) and not manifest_semantic_bad, ['META/Manifest-Semantic-Coherence-Audit-current.csv'], 'manifest semantic coherence audit has zero high/fail rows', '; '.join(manifest_semantic_bad[:8])))
    json_key_rows=read_csv(root/'META/JSON-Key-Uniqueness-Audit-current.csv')
    json_key_bad=[r.get('json_path','') for r in json_key_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_044','json_key_uniqueness_zero_high_fail', bool(json_key_rows) and not json_key_bad, ['META/JSON-Key-Uniqueness-Audit-current.csv'], 'JSON key uniqueness audit has zero high/fail rows', '; '.join(json_key_bad[:8])))
    review_role_rows=read_csv(root/'META/Review-Role-Boundary-Audit-current.csv')
    review_role_bad=[r.get('boundary_id','') for r in review_role_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_045','review_role_boundary_zero_high_fail', bool(review_role_rows) and not review_role_bad, ['META/Review-Role-Boundary-Audit-current.csv','GOVERNANCE/Review-Role-and-Handoff-Boundaries-current.md'], 'review-role boundary audit has zero high/fail rows', '; '.join(review_role_bad[:8])))

    helper_rows=read_csv(root/'META/Helper-Adoption-Audit-current.csv')
    helper_bad=[r.get('finding_id','') for r in helper_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_046','helper_adoption_audit_zero_high_fail', bool(helper_rows) and not helper_bad, ['META/Helper-Adoption-Audit-current.csv','tools/helper_adoption_audit.py','tools/lib_cube.py'], 'helper adoption/report-shape audit has zero high/fail rows', '; '.join(helper_bad[:8])))

    roundtrip_rows=read_csv(root/'META/Archive-Roundtrip-Audit-current.csv')
    roundtrip_bad=[r.get('roundtrip_check_id','') for r in roundtrip_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_047','archive_roundtrip_audit_zero_high_fail', bool(roundtrip_rows) and not roundtrip_bad, ['META/Archive-Roundtrip-Audit-current.csv','tools/archive_roundtrip_audit.py'], 'archive roundtrip/tree/compression audit has zero high/fail rows', '; '.join(roundtrip_bad[:8])))

    pointer_rows=read_csv(root/'META/Current-Pointer-Coherence-Audit-current.csv')
    pointer_bad=[r.get('finding_id','') or r.get('pointer_check_id','') or r.get('check','') for r in pointer_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_048','current_pointer_coherence_zero_high_fail', bool(pointer_rows) and not pointer_bad, ['META/Current-Pointer-Coherence-Audit-current.csv','tools/current_pointer_coherence_audit.py'], 'current-pointer coherence audit has zero high/fail rows', '; '.join(pointer_bad[:8])))

    pres_rows=read_csv(root/'META/Source-Freshness-Preservation-current.csv')
    pres_ids={r.get('source_id','') for r in pres_rows}
    pres_bad=[r.get('source_id','') for r in pres_rows if r.get('status')=='fail']
    rows.append(gate('gate_049','source_freshness_preservation_coverage', bool(pres_rows) and source_ids==pres_ids and not pres_bad, ['META/Source-Freshness-Preservation-current.csv','Source-Registry-current.csv'], 'source freshness/preservation report covers every source without fail rows', f'source_only={len(source_ids-pres_ids)} preservation_only={len(pres_ids-source_ids)} bad={len(pres_bad)}'))

    sprint_rows=read_csv(root/'META/Evidence-Debt-Sprint-current.csv')
    sprint_bad=[r.get('debt_id','') for r in sprint_rows if not (r.get('safe_research_mode') and r.get('do_not_research_mode'))]
    rows.append(gate('gate_050','evidence_debt_sprint_present', bool(sprint_rows) and not sprint_bad, ['META/Evidence-Debt-Sprint-current.csv','Evidence-Debt-current.csv'], 'evidence-debt sprint queue exists with safe and forbidden research modes', '; '.join(sprint_bad[:8])))

    perm_rows=read_csv(root/'GOVERNANCE/Permission-State-Ledger-current.csv')
    perm_ids={r.get('candidate_id','') for r in perm_rows}
    rows.append(gate('gate_051','permission_state_candidate_coverage', bool(perm_rows) and cand_ids==perm_ids, ['GOVERNANCE/Permission-State-Ledger-current.csv','Candidate-Ledger-current.csv'], 'permission-state ledger covers every candidate', f'candidate_only={len(cand_ids-perm_ids)} permission_only={len(perm_ids-cand_ids)}'))

    acct_rows=read_csv(root/'META/Office-Accountability-current.csv')
    required_pairs={(r.get('candidate_id',''),oid) for r in read_csv(root/'Candidate-Ledger-current.csv') for oid in (r.get('office_ids','') or '').split('|') if oid}
    acct_pairs={(r.get('candidate_id',''),r.get('office_id','')) for r in acct_rows}
    missing_pairs=required_pairs-acct_pairs
    rows.append(gate('gate_052','office_accountability_pair_coverage', bool(acct_rows) and not missing_pairs, ['META/Office-Accountability-current.csv','Candidate-Ledger-current.csv'], 'office-accountability ledger covers candidate/office pairs', f'missing_pairs={len(missing_pairs)}'))

    required_docs=['RIGHTS-AND-USE-LIMITS.md','META/Data-Card-current.md','DATA-CARD-current.md','datapackage.json','BUILD-PROVENANCE-current.json','SIGNATURE-READINESS-current.md','META/Controlled-Vocabulary-Normalization-current.csv','META/Helper-Adoption-Scope-current.csv']
    missing_docs=[rel for rel in required_docs if not (root/rel).exists()]
    rows.append(gate('gate_053','rights_data_card_descriptor_and_scope_docs_present', not missing_docs, required_docs, 'rights/data-card/descriptor/provenance/signature-readiness/helper-scope/normalization surfaces exist without public expansion', '; '.join(missing_docs[:8])))


    ctx_rows=read_csv(root/'META/Public-Lint-Allowed-Contexts-current.csv')
    ctx_bad=[r.get('context_id','') for r in ctx_rows if not ((r.get('context_code','') or r.get('allowed_context_code','')) and r.get('status')=='active')]
    rows.append(gate('gate_054','public_lint_allowed_contexts_present', bool(ctx_rows) and not ctx_bad, ['META/Public-Lint-Allowed-Contexts-current.csv'], 'public-lint allowed-context policy is present and active', '; '.join(ctx_bad[:8])))

    hg_rows=read_csv(root/'META/Helper-Golden-Output-Audit-current.csv')
    hg_bad=[r.get('finding_id','') for r in hg_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_055','helper_golden_output_zero_high_fail', bool(hg_rows) and not hg_bad, ['META/Helper-Golden-Output-Audit-current.csv','META/Helper-Adoption-Scope-current.csv'], 'helper golden-output audit has zero high/fail rows and keeps helper adoption selected-scope', '; '.join(hg_bad[:8])))

    sig_required=['SHA256SUMS.txt','SHA256SUMS.txt.sig','RELEASE-PUBLIC-KEY.asc','SIGNATURE-STATUS-current.md','BUILD-PROVENANCE-current.json']
    sig_missing=[rel for rel in sig_required if not (root/rel).exists()]
    rows.append(gate('gate_056','checksum_signature_status_and_build_provenance_present', not sig_missing, sig_required, 'checksum signature, public verification key, signature status, and build provenance are present', '; '.join(sig_missing[:8])))


    report_contract_rows=read_csv(root/'META/Report-Contract-Audit-current.csv')
    report_contract_bad=[r.get('audit_id','') for r in report_contract_rows if r.get('severity')=='high' and r.get('status')!='pass']
    registry_rows=read_csv(root/'META/Report-Contract-Registry-current.csv')
    registry_bad=[r.get('surface_path','') for r in registry_rows if r.get('status')!='pass']
    rows.append(gate('gate_057','report_contract_audit_zero_high_fail', bool(report_contract_rows) and bool(registry_rows) and not report_contract_bad and not registry_bad, ['META/Report-Contract-Registry-current.csv','META/Report-Contract-Audit-current.csv','tools/report_contract_registry.py'], 'report-contract registry/audit has zero high failures and no non-pass registry rows', '; '.join((report_contract_bad+registry_bad)[:8])))


    tool_exec_rows=read_csv(root/'META/Tool-Executability-Audit-current.csv')
    tool_exec_bad=[r.get('tool_path','')+': '+r.get('note','') for r in tool_exec_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_058','tool_executability_audit_zero_high_fail', bool(tool_exec_rows) and not tool_exec_bad, ['META/Tool-Executability-Audit-current.csv','tools/tool_executability_audit.py'], 'packaged tool syntax/static-entrypoint audit has zero high failures', '; '.join(tool_exec_bad[:8])))

    boundary_domain_rows=read_csv(root/'META/Boundary-Domain-Coverage-Audit-current.csv')
    boundary_domain_bad=[r.get('candidate_id','')+': '+r.get('detail','') for r in boundary_domain_rows if r.get('severity')=='high' and r.get('status')!='pass']
    boundary_map_rows=read_csv(root/'META/Candidate-Boundary-Domain-Map-current.csv')
    rows.append(gate('gate_059','boundary_domain_inheritance_zero_high_fail', bool(boundary_domain_rows) and bool(boundary_map_rows) and not boundary_domain_bad, ['META/Boundary-Domain-Registry-current.csv','META/Candidate-Boundary-Domain-Map-current.csv','META/Boundary-Domain-Coverage-Audit-current.csv','tools/boundary_domain_map.py'], 'candidate boundary-domain inheritance audit has zero high failures', '; '.join(boundary_domain_bad[:8])))

    identifier_registry_rows=read_csv(root/'META/Identifier-Registry-current.csv')
    identifier_registry_bad=[r.get('identifier','') for r in identifier_registry_rows if r.get('namespace_status')!='pass']
    identifier_audit_rows=read_csv(root/'META/Identifier-Convention-Audit-current.csv')
    identifier_audit_bad=[r.get('audit_id','') for r in identifier_audit_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_060','identifier_namespace_crosslink_zero_high_fail', bool(identifier_registry_rows) and bool(identifier_audit_rows) and not identifier_registry_bad and not identifier_audit_bad, ['META/Identifier-Registry-current.csv','META/Identifier-Convention-Audit-current.csv','tools/identifier_namespace_audit.py'], 'identifier namespace registry and crosslink audit have zero high failures and no non-pass namespace rows', '; '.join((identifier_registry_bad+identifier_audit_bad)[:8])))

    claim_source_matrix_rows=read_csv(root/'META/Claim-Source-Boundary-Matrix-current.csv')
    claim_source_matrix_bad=[r.get('matrix_id','') for r in claim_source_matrix_rows if r.get('status')!='pass']
    claim_source_audit_rows=read_csv(root/'META/Claim-Source-Boundary-Audit-current.csv')
    claim_source_audit_bad=[r.get('audit_id','') for r in claim_source_audit_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_061','claim_source_boundary_matrix_zero_high_fail', bool(claim_source_matrix_rows) and bool(claim_source_audit_rows) and not claim_source_matrix_bad and not claim_source_audit_bad, ['META/Claim-Source-Boundary-Matrix-current.csv','META/Claim-Source-Boundary-Audit-current.csv','tools/claim_source_boundary_audit.py'], 'claim-source boundary matrix/audit has zero high failures and no non-pass matrix rows', '; '.join((claim_source_matrix_bad+claim_source_audit_bad)[:8])))


    discovery_log_rows=read_csv(root/'META/Candidate-Discovery-Log-current.csv')
    discovery_audit_rows=read_csv(root/'META/Candidate-Discovery-Intake-Audit-current.csv')
    discovery_audit_bad=[r.get('audit_id','') for r in discovery_audit_rows if r.get('severity')=='high' and r.get('status')!='pass']
    promoted=[r.get('proposed_candidate_id','') for r in discovery_log_rows if r.get('discovery_status')=='promoted_to_candidate']
    rows.append(gate('gate_062','candidate_discovery_intake_zero_high_fail', bool(discovery_log_rows) and bool(discovery_audit_rows) and not discovery_audit_bad, ['META/Candidate-Discovery-Log-current.csv','META/Candidate-Discovery-Intake-Audit-current.csv','tools/candidate_discovery_intake_audit.py'], 'candidate-discovery log/intake audit has zero high failures and promoted candidates remain public-closed', '; '.join(discovery_audit_bad[:8]) or ('promoted='+'|'.join(promoted[:8]))))

    source_pack_rows=read_csv(root/'META/Candidate-Source-Diversity-Audit-current.csv')
    source_pack_bad=[r.get('audit_id','') for r in source_pack_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_063','candidate_source_diversity_zero_high_fail', bool(source_pack_rows) and not source_pack_bad, ['META/Candidate-Source-Diversity-Audit-current.csv','tools/candidate_source_diversity_audit.py'], 'promoted candidate source-pack diversity audit has zero high failures', '; '.join(source_pack_bad[:8])))

    semantic_rows=read_csv(root/'META/Public-Index-Semantic-Audit-current.csv')
    semantic_bad=[r.get('finding_id','')+': '+r.get('check','') for r in semantic_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_064','public_index_semantic_audit_zero_high_fail', bool(semantic_rows) and not semantic_bad, ['META/Public-Index-Semantic-Audit-current.csv','tools/public_index_semantic_audit.py','tools/public_template_policy.py'], 'public-index semantic audit has zero high failures; governance quarantine does not imply the MMIWG template', '; '.join(semantic_bad[:8])))

    maint_rows=read_csv(root/'META/Source-Maintenance-Priority-current.csv')
    maint_ids={r.get('source_id','') for r in maint_rows}
    maint_bad=[r.get('source_id','')+': '+r.get('maintenance_priority','') for r in maint_rows if r.get('status')=='fail']
    preserve_rows=read_csv(root/'META/Source-Preservation-Status-current.csv')
    preserve_ids={r.get('source_id','') for r in preserve_rows}
    preserve_bad=[r.get('source_id','') for r in preserve_rows if r.get('status')=='fail']
    freshness_bytes=(root/'META/Source-Freshness-Preservation-current.csv').read_bytes() if (root/'META/Source-Freshness-Preservation-current.csv').exists() else b''
    preservation_bytes=(root/'META/Source-Preservation-Status-current.csv').read_bytes() if (root/'META/Source-Preservation-Status-current.csv').exists() else b''
    not_duplicate=bool(freshness_bytes and preservation_bytes and freshness_bytes != preservation_bytes)
    rows.append(gate('gate_065','source_maintenance_priority_and_preservation_refactor', bool(maint_rows) and source_ids==maint_ids==preserve_ids and not maint_bad and not preserve_bad and not_duplicate, ['META/Source-Maintenance-Priority-current.csv','META/Source-Preservation-Status-current.csv','META/Source-Freshness-Preservation-current.csv','tools/source_maintenance_priority.py','tools/source_preservation_status.py','tools/source_freshness_preservation.py'], 'source maintenance queue covers every source, preservation status is distinct from freshness, and no automated crawl/preservation failure rows remain', f'maint_source_only={len(source_ids-maint_ids)} preserve_source_only={len(source_ids-preserve_ids)} maint_bad={len(maint_bad)} preserve_bad={len(preserve_bad)} duplicate={not not_duplicate}'))

    backfill_rows=read_csv(root/'META/Source-Metadata-Backfill-current.csv')
    backfill_bad=[r.get('source_id','')+': '+r.get('note','') for r in backfill_rows if r.get('status')!='pass']
    batch_revisions={r.get('batch_revision','') for r in backfill_rows}
    completed_p1=[r.get('source_id','') for r in backfill_rows if r.get('backfill_status','').startswith('completed') and r.get('maintenance_priority_after','').startswith('p1_public_context_metadata_repair')]
    blocked_visible=[r.get('source_id','') for r in backfill_rows if r.get('backfill_status')=='blocked_visible_recheck_needed' and r.get('maintenance_priority_after','').startswith('p1_public_context_metadata_repair')]
    blocked_any=[r.get('source_id','') for r in backfill_rows if r.get('backfill_status')=='blocked_visible_recheck_needed']
    safety_rows=[r for r in backfill_rows if r.get('backfill_status')=='safety_reclassified_no_public_url']
    decision_batch_rows=[r for r in backfill_rows if r.get('backfill_status')=='manual_sensitive_metadata_completed_no_public_archive']
    safety_not_manual=[r.get('source_id','') for r in safety_rows if not (r.get('maintenance_priority_after','').startswith('p1_manual_sensitive_preservation') or r.get('maintenance_priority_after','').startswith('p2_sensitive_preservation_decision_recorded'))]
    decision_not_p2=[r.get('source_id','') for r in decision_batch_rows if r.get('maintenance_priority_after')!='p2_sensitive_preservation_decision_recorded']
    rows.append(gate('gate_066','source_metadata_backfill_cumulative_safety_coherent', len(backfill_rows)>=380 and {'rev0077','rev0078','rev0079','rev0080','rev0081','rev0083','rev0084'}.issubset(batch_revisions) and not backfill_bad and not completed_p1 and bool(blocked_any) and len(safety_rows)>=60 and not safety_not_manual and len(decision_batch_rows)>=240 and not decision_not_p2, ['META/Source-Metadata-Backfill-current.csv','META/Source-Maintenance-Priority-current.csv','META/Public-Source-Link-Review-current.csv','Source-Registry-current.csv','tools/source_metadata_backfill_log.py'], 'cumulative source metadata/safety backfill has no failed rows; completed rows leave P1 metadata repair, blocked rows remain visible, contact/route/support/housing/shelter/service/directory surfaces move to internal-only manual preservation, and metadata-ready sensitive cohort rows move only to recorded no-public-archive P2 watch', f'rows={len(backfill_rows)} batches={"|".join(sorted(batch_revisions))} bad={len(backfill_bad)} completed_still_p1={len(completed_p1)} blocked_visible={len(blocked_visible)} blocked_any={len(blocked_any)} safety={len(safety_rows)} safety_not_manual={len(safety_not_manual)} decision_batch={len(decision_batch_rows)} decision_not_p2={len(decision_not_p2)}'))

    nearmiss_rows=read_csv(root/'META/Source-Safety-Nearmiss-Audit-current.csv')
    nearmiss_bad=[r.get('source_id','')+': '+r.get('hazard_family','') for r in nearmiss_rows if r.get('severity')=='high' and r.get('status')!='pass']
    contained=[r for r in nearmiss_rows if r.get('severity')=='info' and r.get('status')=='pass']
    rows.append(gate('gate_067','source_safety_nearmiss_zero_high_fail', bool(nearmiss_rows) and not nearmiss_bad and len(contained)>=60, ['META/Source-Safety-Nearmiss-Audit-current.csv','tools/source_safety_nearmiss_audit.py','Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv'], 'high-confidence source near-misses for support/contact/route/housing/shelter/service-location/forensic-directory/child-residential/memorial-case exposure are either internal-only/manual or fail the release gate', f'rows={len(nearmiss_rows)} high_fail={len(nearmiss_bad)} contained={len(contained)}'))

    url_rows=read_csv(root/'META/Source-URL-Integrity-Audit-current.csv')
    url_ids={r.get('source_id','') for r in url_rows}
    url_bad=[r.get('source_id','')+': '+r.get('status','') for r in url_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_068','source_url_integrity_zero_high_fail', bool(url_rows) and source_ids==url_ids and not url_bad, ['META/Source-URL-Integrity-Audit-current.csv','tools/source_url_integrity_audit.py','Source-Registry-current.csv'], 'every Source Registry URL is structurally parseable and no truncated/whitespace/scheme/parenthesis URL defects remain', f'rows={len(url_rows)} high_fail={len(url_bad)} source_only={len(source_ids-url_ids)} url_only={len(url_ids-source_ids)}'))

    decision_rows=read_csv(root/'META/Source-Manual-Preservation-Decision-current.csv')
    decision_bad=[r.get('source_id','')+': '+r.get('manual_preservation_tier','') for r in decision_rows if r.get('severity')=='high' and r.get('status')!='pass']
    decision_recorded=[r for r in decision_rows if r.get('manual_preservation_tier')=='p2_sensitive_preservation_decision_recorded']
    untriaged=[r for r in decision_rows if r.get('manual_preservation_tier')=='p0_metadata_ready_untriaged_sensitive_source']
    rows.append(gate('gate_069','manual_sensitive_preservation_decision_zero_high_fail', bool(decision_rows) and not decision_bad and not untriaged and len(decision_recorded)>=250, ['META/Source-Manual-Preservation-Decision-current.csv','tools/source_manual_preservation_decision.py','Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv'], 'metadata-ready near-harm sources must have an explicit no-public-archive/no-auto-crawl preservation decision instead of generic not_recorded archive debt', f'rows={len(decision_rows)} high_fail={len(decision_bad)} recorded={len(decision_recorded)} untriaged={len(untriaged)}'))


    freshness_rows=read_csv(root/'META/Source-Freshness-Preservation-current.csv')
    freshness_manual=[r for r in freshness_rows if r.get('status')=='manual_identity_review_recorded_no_live_http_status']
    registry_manual=[r for r in read_csv(root/'Source-Registry-current.csv') if (r.get('last_http_status','') or '').startswith('manual_metadata_review_no_direct_http_open_')]
    manual_bad=[r.get('source_id','') for r in freshness_manual if r.get('safe_to_recheck_automatically')!='do_not_auto_recheck' or r.get('archive_url_or_archive_id')]
    registry_manual_ids={r.get('source_id','') for r in registry_manual}
    freshness_manual_ids={r.get('source_id','') for r in freshness_manual}
    rows.append(gate('gate_070','manual_metadata_no_direct_crawl_freshness_classified', len(freshness_manual)>=180 and registry_manual_ids==freshness_manual_ids and not manual_bad, ['META/Source-Freshness-Preservation-current.csv','Source-Registry-current.csv','tools/source_freshness_preservation.py'], 'manual metadata review without direct HTTP crawl is classified separately from live link-health tracking and remains no-auto-crawl/no-public-archive', f'manual_freshness={len(freshness_manual)} registry_manual={len(registry_manual)} id_mismatch={len(registry_manual_ids ^ freshness_manual_ids)} manual_bad={len(manual_bad)}'))

    coverage_rows=read_csv(root/'META/Source-Backfill-Coverage-Audit-current.csv')
    coverage_ids={r.get('source_id','') for r in coverage_rows}
    coverage_bad=[r.get('source_id','')+': '+r.get('coverage_status','') for r in coverage_rows if r.get('status')!='pass']
    rows.append(gate('gate_071','source_backfill_coverage_complete', bool(coverage_rows) and source_ids==coverage_ids and not coverage_bad, ['META/Source-Backfill-Coverage-Audit-current.csv','META/Source-Metadata-Backfill-current.csv','Source-Registry-current.csv','tools/source_backfill_coverage_audit.py'], 'source-backfill coverage audit has one pass row for every Source Registry source_id; duplicate action history no longer obscures missing coverage', f'rows={len(coverage_rows)} source_only={len(source_ids-coverage_ids)} coverage_only={len(coverage_ids-source_ids)} bad={len(coverage_bad)}'))

    fp_rows=read_csv(root/'META/Family-Profile-Consent-Boundary-Audit-current.csv')
    fp_bad=[r.get('source_id','')+': '+r.get('risk_class','') for r in fp_rows if r.get('severity')=='high' and r.get('status')!='pass']
    fsis_blocked=[r for r in fp_rows if r.get('source_id')=='src_amnesty_ca_58860a31' and r.get('public_url_release_decision')=='block_public_url' and r.get('public_link_policy','').startswith('internal_only')]
    rows.append(gate('gate_072','family_profile_consent_boundary_zero_high_fail', bool(fp_rows) and not fp_bad and bool(fsis_blocked), ['META/Family-Profile-Consent-Boundary-Audit-current.csv','tools/family_profile_consent_audit.py','Source-Registry-current.csv','META/Public-Source-Link-Review-current.csv','GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv'], 'family-profile/interview/testimony-near sources must either block public URL release or carry explicit consent and boundary controls; the FSIS Amnesty profile is explicitly blocked as internal-only evidence', f'rows={len(fp_rows)} high_fail={len(fp_bad)} fsis_blocked={len(fsis_blocked)}'))

    br_rows=read_csv(root/'META/Border-Route-Referral-Boundary-Audit-current.csv')
    br_bad=[(r.get('claim_id','') or r.get('source_id',''))+': '+r.get('hazard_tokens','') for r in br_rows if r.get('severity')=='high' and r.get('status')!='pass']
    calais_fixed=[r for r in br_rows if r.get('claim_id')=='claim_0007' and 'quarantined_from_route_referral_contact_extraction' in r.get('claim_status','') and r.get('status')=='pass']
    claim_boundary=[r for r in br_rows if r.get('claim_id')=='claim_0285' and r.get('status')=='pass']
    rows.append(gate('gate_073','border_route_referral_boundary_zero_high_fail', bool(br_rows) and not br_bad and bool(calais_fixed) and bool(claim_boundary), ['META/Border-Route-Referral-Boundary-Audit-current.csv','tools/border_route_referral_audit.py','Claim-Ledger-current.csv','Source-Registry-current.csv','META/Public-Claim-Quarantine-current.csv','META/Public-Source-Link-Review-current.csv'], 'border-route/referral/camp/contact sensitive sources and claims must be quarantined from public route, contact, shelter/referral, live-aid, image, crossing-risk, site/timing, and current-capacity copy; Calais claim_0007 must be explicitly fixed and claim_0285 must exist', f'rows={len(br_rows)} high_fail={len(br_bad)} calais_claim_fixed={len(calais_fixed)} boundary_claim={len(claim_boundary)}'))

    pgbv_rows=read_csv(root/'META/Pacific-GBV-Service-Capacity-Boundary-Audit-current.csv')
    pgbv_bad=[(r.get('claim_id','') or r.get('source_id',''))+': '+r.get('hazard_tokens','') for r in pgbv_rows if r.get('severity')=='high' and r.get('status')!='pass']
    pgbv_claims=[r for r in pgbv_rows if r.get('finding_type')=='claim_boundary']
    palau_fixed=[r for r in pgbv_rows if r.get('claim_id')=='claim_0164' and 'quarantined_from_service_referral_capacity_extraction' in r.get('claim_status','') and r.get('status')=='pass']
    pgbv_boundary=[r for r in pgbv_rows if r.get('claim_id')=='claim_0286' and r.get('status')=='pass']
    rows.append(gate('gate_074','pacific_gbv_service_capacity_boundary_zero_high_fail', bool(pgbv_rows) and not pgbv_bad and len(pgbv_claims)>=24 and bool(palau_fixed) and bool(pgbv_boundary), ['META/Pacific-GBV-Service-Capacity-Boundary-Audit-current.csv','tools/pacific_gbv_service_capacity_audit.py','Claim-Ledger-current.csv','Candidate-Ledger-current.csv','Source-Registry-current.csv','META/Public-Claim-Quarantine-current.csv','META/Public-Source-Link-Review-current.csv'], 'Pacific GBV/survivor-service claims and sources must be quarantined from public service-directory, contact/helpline, shelter/refuge, legal-advice, protection-order-safety, referral/intake, current-capacity, case/client, staff/site, image, and route/support-path copy; claim_0164 and claim_0286 must be explicitly fixed', f'rows={len(pgbv_rows)} high_fail={len(pgbv_bad)} claim_rows={len(pgbv_claims)} palau_fixed={len(palau_fixed)} boundary_claim={len(pgbv_boundary)}'))

    sco_rows=read_csv(root/'META/Suicide-Crisis-Operational-Boundary-Audit-current.csv')
    sco_bad=[(r.get('claim_id','') or r.get('source_id','') or r.get('surface_path',''))+': '+r.get('hazard_tokens','') for r in sco_rows if r.get('severity')=='high' and r.get('status')!='pass']
    sco_claim_0128=[r for r in sco_rows if r.get('claim_id')=='claim_0128' and 'quarantined_from_suicide_crisis_referral_contact_capacity_extraction' in r.get('claim_status','') and r.get('status')=='pass']
    sco_boundary=[r for r in sco_rows if r.get('claim_id')=='claim_0287' and r.get('status')=='pass']
    rows.append(gate('gate_075','suicide_crisis_operational_boundary_zero_high_fail', bool(sco_rows) and not sco_bad and bool(sco_claim_0128) and bool(sco_boundary), ['META/Suicide-Crisis-Operational-Boundary-Audit-current.csv','tools/suicide_crisis_operational_boundary_audit.py','Claim-Ledger-current.csv','Candidate-Ledger-current.csv','Source-Registry-current.csv','META/Public-Claim-Quarantine-current.csv','META/Public-Source-Link-Review-current.csv'], 'suicide/crisis-line/postvention claims and sources must be quarantined from public hotline shortcode/contact digit, service-hours, call-volume/caller-category, method, triage, referral, current-capacity, case/caller, and operational support-path copy; claim_0128 and claim_0287 must be explicitly fixed', f'rows={len(sco_rows)} high_fail={len(sco_bad)} claim_0128_fixed={len(sco_claim_0128)} boundary_claim={len(sco_boundary)}'))


    fresh_rows=read_csv(root/'META/Current-Surface-Freshness-Audit-current.csv')
    fresh_bad=[r.get('freshness_id','')+': '+r.get('surface_path','')+' '+r.get('check','') for r in fresh_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_076','current_surface_freshness_zero_high_fail', bool(fresh_rows) and not fresh_bad, ['META/Current-Surface-Freshness-Audit-current.csv','tools/current_surface_freshness_audit.py'], 'current identity/proof surfaces have zero freshness failures; stale current claims cannot pass as current', '; '.join(fresh_bad[:8])))

    ptr_rows=read_csv(root/'META/Preservation-Transfer-Readiness-current.csv')
    ptr_bad=[r.get('readiness_id','')+': '+r.get('area','')+' '+r.get('check','') for r in ptr_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_077','preservation_transfer_readiness_zero_high_fail', bool(ptr_rows) and not ptr_bad, ['META/Preservation-Transfer-Readiness-current.csv','ro-crate-metadata.json','tools/make_bagit_transfer_copy.py'], 'closed preservation-transfer readiness has zero high failures; RO-Crate metadata and external BagIt helper are present without opening public/source surfaces', '; '.join(ptr_bad[:8])))


    regen_cov_rows=read_csv(root/'META/Regeneration-Coverage-Audit-current.csv')
    regen_cov_bad=[r.get('coverage_id','')+': '+r.get('surface_path','')+' '+r.get('coverage_class','') for r in regen_cov_rows if r.get('severity')=='high' and r.get('status')!='pass']
    rows.append(gate('gate_078','regeneration_coverage_zero_high_fail', bool(regen_cov_rows) and not regen_cov_bad, ['META/Regeneration-Coverage-Audit-current.csv','META/Regeneration-Sequence-Plan-current.csv','META/Generated-Artifact-Provenance-current.csv','META/Report-Contract-Registry-current.csv','tools/regeneration_coverage_audit.py'], 'every current CSV surface is classified as generated, curated seed, schema/governance, public index, or deliberate late-closure; no unowned current report surface may ship', '; '.join(regen_cov_bad[:8])))

    overlay_audit_rows=read_csv(root/'META/Normalized-Code-Overlay-Audit-current.csv')
    overlay_bad=[r.get('audit_id','')+': '+r.get('check','') for r in overlay_audit_rows if r.get('severity')=='high' and r.get('status')!='pass']
    overlay_rows=read_csv(root/'META/Normalized-Code-Overlay-current.csv')
    required_code_fields={'candidate_status_code','capacity_claim_code','community_authority_status','boundary_lift_authority','public_surface_code','source_harm_proximity_code','claim_evidence_status_code'}
    observed_code_fields={r.get('normalized_code_field','') for r in overlay_rows}
    rows.append(gate('gate_079','normalized_code_overlay_zero_high_fail', bool(overlay_rows) and bool(overlay_audit_rows) and not overlay_bad and required_code_fields.issubset(observed_code_fields), ['META/Normalized-Code-Overlay-current.csv','META/Normalized-Code-Overlay-Audit-current.csv','META/Controlled-Vocabulary-Normalization-current.csv','tools/ledger_code_overlay.py'], 'row-level companion code overlay covers candidates, claims, sources, permission states, and public tiers without changing core ledger headers or opening the public layer', '; '.join(overlay_bad[:8]) or f'overlay_rows={len(overlay_rows)} fields={len(observed_code_fields)}'))

    release_change_rows=read_csv(root/'META/Release-Change-Review-current.csv')
    release_change_bad=[r.get('review_id','')+': '+r.get('subject_path','')+' '+r.get('review_check','') for r in release_change_rows if r.get('severity')=='high' and r.get('status')!='pass']
    signature_rows=[r for r in release_change_rows if r.get('review_check')=='signature_doc_current_revision_and_key' and r.get('status')=='pass']
    rows.append(gate('gate_080','release_change_review_zero_high_fail', bool(release_change_rows) and not release_change_bad and len(signature_rows)>=2, ['META/Release-Change-Review-current.csv','META/Package-Delta-Manifest-current.csv','SIGNATURE-STATUS-current.md','SIGNATURE-READINESS-current.md','tools/release_change_review.py'], 'release-change review triages raw deltas and proves signature readiness/status text points to the current revision/key; core payload movement remains blocked', '; '.join(release_change_bad[:8]) or f'rows={len(release_change_rows)} signature_checks={len(signature_rows)}'))

    rel_rows=read_csv(root/'META/Ledger-Relationship-Audit-current.csv')
    rel_bad=[r.get('relationship_id','')+': '+r.get('relationship_family','')+' '+r.get('source_id','')+'->'+r.get('referenced_id','') for r in rel_rows if r.get('severity')=='high' and r.get('status')!='pass']
    summary_rows=[r for r in rel_rows if r.get('relationship_family')=='relationship_audit_summary' and r.get('status')=='pass']
    rows.append(gate('gate_081','ledger_relationship_audit_zero_high_fail', bool(rel_rows) and not rel_bad and bool(summary_rows), ['META/Ledger-Relationship-Audit-current.csv','SCHEMA/Ledger-Relationship-Audit-Fields-current.csv','tools/ledger_relationship_audit.py'], 'row-level cross-ledger joins, release/quarantine pointers, discovery/source references, refresh paths, and normalized-code overlay targets have zero high failures', '; '.join(rel_bad[:8]) or f'rows={len(rel_rows)}'))


    public_export_rows=read_csv(root/'META/Public-Export-Surface-Audit-current.csv')
    public_export_bad=[r.get('audit_id','')+': '+r.get('surface_path','')+' '+r.get('check','') for r in public_export_rows if r.get('severity')=='high' and r.get('status')!='pass']
    public_bundle_rows=[r for r in public_export_rows if r.get('check')=='public_payload_paths_are_public_only' and r.get('status')=='pass']
    rows.append(gate('gate_082','public_export_surface_audit_zero_high_fail', bool(public_export_rows) and not public_export_bad and bool(public_bundle_rows), ['META/Public-Export-Surface-Audit-current.csv','PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json','tools/public_export_surface_audit.py'], 'actual public bundle is PUBLIC-only and legacy included_files are partitioned into public payload vs reviewer-support evidence', '; '.join(public_export_bad[:8]) or f'rows={len(public_export_rows)}'))


    ede_rows=read_csv(root/'META/Evidence-Debt-Execution-Audit-current.csv')
    ede_bad=[r.get('audit_id','')+': '+r.get('check','')+' '+r.get('observed','') for r in ede_rows if r.get('severity')=='high' and r.get('status')!='pass']
    ede_queue=read_csv(root/'META/Evidence-Debt-Execution-Queue-current.csv')
    critical_high=[r for r in read_csv(root/'Evidence-Debt-current.csv') if r.get('priority') in {'critical','high'}]
    rows.append(gate('gate_083','evidence_debt_execution_queue_zero_high_fail', bool(ede_rows) and bool(ede_queue) and not ede_bad and len(ede_queue)==len(critical_high), ['META/Evidence-Debt-Execution-Queue-current.csv','META/Evidence-Debt-Execution-Audit-current.csv','tools/evidence_debt_execution_queue.py'], 'every critical/high evidence-debt row has a safe internal execution queue row with forbidden-mode boundaries and no public expansion permission', '; '.join(ede_bad[:8]) or f'queue_rows={len(ede_queue)} critical_high_debts={len(critical_high)}'))

    edp_rows=read_csv(root/'META/Evidence-Debt-Work-Packet-Audit-current.csv')
    edp_bad=[r.get('audit_id','')+': '+r.get('check','')+' '+r.get('observed','') for r in edp_rows if r.get('severity')=='high' and r.get('status')!='pass']
    edp_packets=read_csv(root/'META/Evidence-Debt-Work-Packet-current.csv')
    queue_exec_ids={r.get('execution_id','') for r in ede_queue if r.get('execution_id')}
    packet_exec_ids=set()
    for p in edp_packets:
        for eid in (p.get('execution_ids','') or '').split('|'):
            if eid: packet_exec_ids.add(eid)
    critical_packets=[p for p in edp_packets if p.get('priority_band')=='critical']
    rows.append(gate('gate_084','evidence_debt_work_packets_zero_high_fail', bool(edp_rows) and bool(edp_packets) and not edp_bad and queue_exec_ids==packet_exec_ids and bool(critical_packets), ['META/Evidence-Debt-Work-Packet-current.csv','META/Evidence-Debt-Work-Packet-Audit-current.csv','tools/evidence_debt_work_packets.py'], 'critical/high evidence-debt execution rows are grouped into reviewer-sized work packets with acceptance criteria, completion slots, and no-public-expansion boundaries', '; '.join(edp_bad[:8]) or f'packets={len(edp_packets)} queue_exec={len(queue_exec_ids)} packet_exec={len(packet_exec_ids)}'))

    cpo_audit=read_csv(root/'META/Evidence-Debt-Critical-Path-Audit-current.csv')
    cpo_bad=[r.get('audit_id','')+': '+r.get('check','')+' '+r.get('observed','') for r in cpo_audit if r.get('severity')=='high' and r.get('status')!='pass']
    cpo_orders=read_csv(root/'META/Evidence-Debt-Critical-Path-Work-Order-current.csv')
    cpo_trace=read_csv(root/'META/Evidence-Debt-Work-Packet-Trace-current.csv')
    traced_exec_ids={r.get('execution_id','') for r in cpo_trace if r.get('execution_id') and r.get('trace_status')=='pass'}
    ordered_packet_ids={r.get('packet_id','') for r in cpo_orders if r.get('packet_id')}
    rows.append(gate('gate_085','evidence_debt_critical_path_work_order_zero_high_fail', bool(cpo_audit) and bool(cpo_orders) and bool(cpo_trace) and not cpo_bad and traced_exec_ids==queue_exec_ids and ordered_packet_ids=={p.get('packet_id','') for p in edp_packets if p.get('packet_id')}, ['META/Evidence-Debt-Critical-Path-Work-Order-current.csv','META/Evidence-Debt-Work-Packet-Trace-current.csv','META/Evidence-Debt-Critical-Path-Audit-current.csv','tools/evidence_debt_critical_path_work_order.py'], 'work packets are converted into an executable critical-path work order with queue-row traceability, critical-first ordering, completion targets, and no URL/contact leakage', '; '.join(cpo_bad[:8]) or f'work_orders={len(cpo_orders)} trace_rows={len(cpo_trace)} traced_exec={len(traced_exec_ids)}'))

    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Release-Gate-Attestation-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Release-Gate-Attestation-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    fail=[r for r in rows if r.get('status')!='pass']
    lines=['# Release Gate Attestation — current','', 'Generated by `tools/release_gate_attestation.py`.', '', f'Gates: {len(rows)}', f'Failed gates: {len(fail)}', '', '| gate_id | gate_name | status | note |', '| --- | --- | --- | --- |']
    for r in rows:
        lines.append(f"| {r['gate_id']} | {r['gate_name']} | {r['status']} | {r['note']} |")
    (out/'Release-Gate-Attestation-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-fail', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    for r in rows: print(f"{r['status'].upper()} {r['gate_id']} {r['gate_name']}: {r['note']}")
    if args.fail_on_fail and any(r.get('status')!='pass' for r in rows): sys.exit(1)
if __name__=='__main__': main()
