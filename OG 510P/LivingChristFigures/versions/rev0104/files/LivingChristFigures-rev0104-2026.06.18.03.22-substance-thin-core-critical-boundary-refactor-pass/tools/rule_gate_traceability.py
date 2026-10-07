#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path
FIELDS=['rule_number','rule_name','boundary_coverage_status','mapped_release_gates','mapped_tools','mapped_reports','qa_enforced','trace_status','note']

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def rule_map(rule:int):
    gates=[]; tools=[]; reports=[]; qa='policy_or_legacy'
    if rule in {19,24}: tools+=['tools/qa_cube.py']; qa='automated'
    if rule in {25,26}: tools+=['tools/redaction_scan.py','tools/public_release_lint.py']; reports+=['META/Redaction-Risk-Open-Findings-current.csv','META/Public-Release-Lint-current.csv']; gates+=['gate_004','gate_005']; qa='automated'
    if rule==27: tools+=['tools/schema_validate.py']; reports+=['SCHEMA/Schema-Validation-Report-current.csv']; gates+=['gate_002']; qa='automated'
    if rule in {28,32}: tools+=['tools/evidence_lifecycle.py']; reports+=['META/Claim-Evidence-Strength-current.csv','META/Refresh-Priority-Queue-current.csv','META/Public-Claim-Quarantine-current.csv']; gates+=['gate_003','gate_008']; qa='automated'
    if rule in {29,30,31,33,34,35,36,37,38,39,40,41,42,43,44,45}: tools+=['tools/qa_cube.py']; reports+=['META/Negative-Case-Ledger-current.csv','META/Source-Promotion-Decision-Ledger-current.csv','META/Source-Promotion-Transaction-Audit-current.csv']; qa='automated_or_ledger_gate'
    if rule==46: tools+=['tools/rule46_scan.py']; reports+=['META/Rule46-Scan-current.csv']; gates+=['gate_006']; qa='automated'
    if rule in {47,55}: tools+=['tools/revision_surface_audit.py','tools/public_contract_check.py']; reports+=['META/Revision-Surface-Audit-current.csv']; gates+=['gate_001','gate_010','gate_012']; qa='automated'
    if rule in {48,49,50,51,52,57,58}: tools+=['tools/public_export_eligibility.py','tools/public_source_link_review.py','tools/public_release_lint.py','tools/sensitive_surface_inventory.py','tools/candidate_governance_snapshot.py','tools/public_index_parity.py','tools/governance_consistency_audit.py']; reports+=['META/Public-Export-Eligibility-current.csv','META/Public-Source-Link-Review-current.csv','META/Public-Release-Lint-current.csv','META/Sensitive-Surface-Inventory-current.csv','META/Candidate-Governance-Snapshot-current.csv','META/Governance-Consistency-Audit-current.csv','META/Public-Index-Parity-current.csv']; gates+=['gate_004','gate_007','gate_008','gate_009','gate_013','gate_014']; qa='automated'
    if rule in {53}: tools+=['tools/row_validate.py']; reports+=['SCHEMA/Row-Validation-Report-current.csv']; gates+=['gate_003']; qa='automated'
    if rule in {54}: tools+=['tools/generated_artifact_provenance.py']; reports+=['META/Generated-Artifact-Provenance-current.csv']; gates+=['gate_011']; qa='automated'
    if rule in {56,60}: tools+=['tools/release_gate_attestation.py']; reports+=['META/Release-Gate-Attestation-current.csv']; gates+=['all gates']; qa='automated'
    if rule in {59}: tools+=['tools/package_dependency_graph.py']; reports+=['META/Package-Dependency-Graph-current.csv']; gates+=['gate_015']; qa='automated'
    if rule in {61}: tools+=['tools/csv_json_mirror_audit.py']; reports+=['META/CSV-JSON-Mirror-Audit-current.csv']; gates+=['gate_016']; qa='automated'
    if rule in {62,64}: tools+=['tools/schema_coverage_audit.py']; reports+=['META/Schema-Coverage-Audit-current.csv']; gates+=['gate_017']; qa='automated'
    if rule in {63}: tools+=['tools/package_file_inventory.py']; reports+=['META/Package-File-Inventory-current.csv']; gates+=['gate_018']; qa='automated'
    if rule in {65}: tools+=['tools/field_schema_consistency.py']; reports+=['META/Field-Schema-Consistency-Audit-current.csv']; gates+=['gate_019']; qa='automated'
    if rule in {66}: tools+=['tools/path_reference_audit.py']; reports+=['META/Path-Reference-Audit-current.csv']; gates+=['gate_020']; qa='automated'
    if rule in {67}: tools+=['tools/rule_gate_traceability.py']; reports+=['META/Rule-Gate-Traceability-current.csv']; gates+=['gate_021']; qa='automated'
    if rule in {68}: tools+=['tools/tool_run_matrix.py']; reports+=['META/Tool-Run-Matrix-current.csv']; gates+=['gate_022']; qa='automated'
    if rule in {69}: tools+=['tools/required_document_coverage.py']; reports+=['META/Required-Document-Coverage-current.csv']; gates+=['gate_023']; qa='automated'
    if rule in {70}: tools+=['tools/audit_selftest.py']; reports+=['META/Audit-Selftest-current.csv']; gates+=['gate_024']; qa='automated'
    if rule in {71}: tools+=['tools/rebuild_readiness_audit.py']; reports+=['META/Rebuild-Readiness-Audit-current.csv']; gates+=['gate_025']; qa='automated'
    if rule in {72}: tools+=['tools/policy_assertion_matrix.py']; reports+=['META/Policy-Assertion-Matrix-current.csv']; gates+=['gate_026']; qa='automated'
    if rule in {73}: tools+=['tools/regeneration_sequence_plan.py']; reports+=['META/Regeneration-Sequence-Plan-current.csv']; gates+=['gate_027']; qa='automated'
    if rule in {74}: tools+=['tools/archive_build_manifest.py']; reports+=['META/Archive-Build-Manifest-current.csv']; gates+=['gate_028']; qa='automated'
    if rule in {75}: tools+=['tools/selftest_coverage_matrix.py']; reports+=['META/Selftest-Coverage-Matrix-current.csv']; gates+=['gate_029']; qa='automated'
    if rule in {76}: tools+=['tools/checksum_scope_audit.py']; reports+=['META/Checksum-Scope-Audit-current.csv']; gates+=['gate_030']; qa='automated'
    if rule in {77}: tools+=['tools/public_negative_corpus.py','tools/public_release_lint.py']; reports+=['META/Public-Negative-Corpus-current.csv']; gates+=['gate_031']; qa='automated'
    if rule in {78}: tools+=['tools/release_evidence_closure.py']; reports+=['META/Release-Evidence-Closure-current.csv']; gates+=['gate_032']; qa='automated'
    if rule in {79}: tools+=['tools/archive_member_manifest.py']; reports+=['META/Archive-Member-Manifest-current.csv']; gates+=['gate_033']; qa='automated'
    if rule in {80}: tools+=['tools/unicode_path_audit.py']; reports+=['META/Unicode-Path-Audit-current.csv']; gates+=['gate_034']; qa='automated'
    if rule in {81}: tools+=['tools/package_identity_audit.py']; reports+=['META/Package-Identity-Audit-current.csv']; gates+=['gate_035']; qa='automated'
    if rule in {82}: tools+=['tools/version_lineage_audit.py']; reports+=['META/Version-Lineage-Audit-current.csv']; gates+=['gate_036']; qa='automated'
    if rule in {83}: tools+=['tools/package_delta_manifest.py']; reports+=['META/Package-Delta-Manifest-current.csv']; gates+=['gate_037']; qa='automated'
    if rule in {84}: tools+=['tools/cross_report_reference_audit.py']; reports+=['META/Cross-Report-Reference-Audit-current.csv']; gates+=['gate_038']; qa='automated'
    if rule in {85}: tools+=['tools/handoff_review_digest.py']; reports+=['META/Handoff-Review-Digest-current.csv']; gates+=['gate_039']; qa='automated'
    if rule in {86}: tools+=['tools/dependency_cycle_audit.py']; reports+=['META/Dependency-Cycle-Audit-current.csv']; gates+=['gate_040']; qa='automated'
    if rule in {87}: tools+=['tools/handoff_notice_audit.py']; reports+=['META/Handoff-Notice-Audit-current.csv']; gates+=['gate_041']; qa='automated'
    if rule in {88}: tools+=['tools/current_surface_registry.py']; reports+=['META/Current-Surface-Registry-current.csv']; gates+=['gate_042']; qa='automated'
    if rule in {89}: tools+=['tools/manifest_semantic_coherence_audit.py']; reports+=['META/Manifest-Semantic-Coherence-Audit-current.csv']; gates+=['gate_043']; qa='automated'
    if rule in {90}: tools+=['tools/json_key_uniqueness_audit.py']; reports+=['META/JSON-Key-Uniqueness-Audit-current.csv']; gates+=['gate_044']; qa='automated'
    if rule in {91}: tools+=['tools/review_role_boundary_audit.py']; reports+=['META/Review-Role-Boundary-Audit-current.csv','GOVERNANCE/Review-Role-and-Handoff-Boundaries-current.md']; gates+=['gate_045']; qa='automated'
    if rule in {92}: tools+=['tools/helper_adoption_audit.py','tools/lib_cube.py']; reports+=['META/Helper-Adoption-Audit-current.csv']; gates+=['gate_046']; qa='automated'

    if rule in {93}: tools+=['tools/archive_roundtrip_audit.py']; reports+=['META/Archive-Roundtrip-Audit-current.csv']; gates+=['gate_047']; qa='automated'
    if rule in {94}: tools+=['tools/current_pointer_coherence_audit.py']; reports+=['META/Current-Pointer-Coherence-Audit-current.csv']; gates+=['gate_048']; qa='automated'
    if rule in {95}: tools+=['tools/rev0065_governance_surfaces.py']; reports+=['META/Source-Freshness-Preservation-current.csv']; gates+=['gate_049']; qa='automated'
    if rule in {96}: tools+=['tools/rev0065_governance_surfaces.py']; reports+=['META/Evidence-Debt-Sprint-current.csv']; gates+=['gate_050']; qa='automated'
    if rule in {97}: tools+=['tools/rev0065_governance_surfaces.py']; reports+=['GOVERNANCE/Permission-State-Ledger-current.csv']; gates+=['gate_051']; qa='automated'
    if rule in {98}: tools+=['tools/rev0065_governance_surfaces.py']; reports+=['META/Office-Accountability-current.csv']; gates+=['gate_052']; qa='automated'
    if rule in {99}: tools+=['tools/rev0065_governance_surfaces.py']; reports+=['RIGHTS-AND-USE-LIMITS.md','META/Data-Card-current.md','datapackage.json']; gates+=['gate_053']; qa='automated'

    if rule in {101}: tools+=['tools/boundary_domain_map.py']; reports+=['META/Boundary-Domain-Registry-current.csv','META/Candidate-Boundary-Domain-Map-current.csv','META/Boundary-Domain-Coverage-Audit-current.csv']; gates+=['gate_059']; qa='automated'
    if rule in {102}: tools+=['tools/tool_executability_audit.py']; reports+=['META/Tool-Executability-Audit-current.csv']; gates+=['gate_058']; qa='automated'

    if rule in {100}: tools+=['tools/report_contract_registry.py']; reports+=['META/Report-Contract-Registry-current.csv','META/Report-Contract-Audit-current.csv']; gates+=['gate_057']; qa='automated'
    if rule in {103}: tools+=['tools/identifier_namespace_audit.py']; reports+=['META/Identifier-Registry-current.csv','META/Identifier-Convention-Audit-current.csv']; gates+=['gate_060']; qa='automated'
    if rule in {104}: tools+=['tools/claim_source_boundary_audit.py']; reports+=['META/Claim-Source-Boundary-Matrix-current.csv','META/Claim-Source-Boundary-Audit-current.csv']; gates+=['gate_061']; qa='automated'

    if rule in {106}: tools+=['tools/candidate_discovery_intake_audit.py']; reports+=['META/Candidate-Discovery-Log-current.csv','META/Candidate-Discovery-Intake-Audit-current.csv']; gates+=['gate_062']; qa='automated'
    if rule in {107}: tools+=['tools/candidate_source_diversity_audit.py']; reports+=['META/Candidate-Source-Diversity-Audit-current.csv']; gates+=['gate_063']; qa='automated'
    if rule in {108}: tools+=['tools/source_maintenance_priority.py','tools/source_preservation_status.py','tools/source_freshness_preservation.py']; reports+=['META/Source-Maintenance-Priority-current.csv','META/Source-Preservation-Status-current.csv','META/Source-Freshness-Preservation-current.csv']; gates+=['gate_065']; qa='automated'
    if rule in {109}: tools+=['tools/source_safety_nearmiss_audit.py','tools/source_metadata_backfill_log.py','tools/public_source_link_review.py']; reports+=['META/Source-Safety-Nearmiss-Audit-current.csv','META/Source-Metadata-Backfill-current.csv','META/Public-Source-Link-Review-current.csv']; gates+=['gate_066','gate_067']; qa='automated'
    if rule in {110}: tools+=['tools/source_url_integrity_audit.py']; reports+=['META/Source-URL-Integrity-Audit-current.csv']; gates+=['gate_068']; qa='automated'
    if rule in {111}: tools+=['tools/source_manual_preservation_decision.py','tools/source_maintenance_priority.py','tools/source_preservation_status.py']; reports+=['META/Source-Manual-Preservation-Decision-current.csv','META/Source-Maintenance-Priority-current.csv','META/Source-Preservation-Status-current.csv']; gates+=['gate_069']; qa='automated'
    if rule in {112}: tools+=['tools/source_freshness_preservation.py','tools/release_gate_attestation.py']; reports+=['META/Source-Freshness-Preservation-current.csv','META/Release-Gate-Attestation-current.csv']; gates+=['gate_070']; qa='automated'
    if rule in {113}: tools+=['tools/source_backfill_coverage_audit.py','tools/source_metadata_backfill_log.py']; reports+=['META/Source-Backfill-Coverage-Audit-current.csv','META/Source-Metadata-Backfill-current.csv']; gates+=['gate_071']; qa='automated'

    # Foundational legacy rules are still covered by prose/policy and selected QA.
    if not gates and rule>=15:
        reports+=['META/Boundary-Rule-Coverage-current.csv']
    return sorted(set(gates)), sorted(set(tools)), sorted(set(reports)), qa

def run(root: Path):
    cov=read_csv(root/'META/Boundary-Rule-Coverage-current.csv')
    cov_by={int(r.get('rule_number','0')):r for r in cov if (r.get('rule_number','0') or '0').isdigit()}
    max_rule=max([92]+list(cov_by))
    rows=[]
    for rn in range(15,max_rule+1):
        r=cov_by.get(rn)
        gates,tools,reports,qa=rule_map(rn)
        exists=[x for x in tools+reports if (root/x).exists()]
        missing=[x for x in tools+reports if not (root/x).exists()]
        if not r:
            status='missing_boundary_coverage'; note='rule missing from Boundary-Rule-Coverage-current.csv'
            name=''
        elif missing:
            status='missing_trace_file'; note='missing mapped path(s): '+ '; '.join(missing[:8])
            name=r.get('rule_name','')
        elif not (gates or tools or reports):
            status='policy_only'; note='legacy/policy rule tracked in boundary coverage; no dedicated generated gate yet'
            name=r.get('rule_name','')
        else:
            status='pass'; note='coverage row has rule-to-gate/tool/report traceability'
            name=r.get('rule_name','')
        rows.append({'rule_number':str(rn),'rule_name':name,'boundary_coverage_status':'present' if r else 'missing','mapped_release_gates':'|'.join(gates),'mapped_tools':'|'.join(tools),'mapped_reports':'|'.join(reports),'qa_enforced':qa,'trace_status':status,'note':note})
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Rule-Gate-Traceability-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Rule-Gate-Traceability-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    bad=[r for r in rows if r.get('trace_status') in {'missing_boundary_coverage','missing_trace_file'}]
    lines=['# Rule-Gate Traceability — current','', 'Generated by `tools/rule_gate_traceability.py`.', '', f'Rules traced: {len(rows)}', f'Blocking trace rows: {len(bad)}', '', 'This report does not claim every older rule is fully automated. It prevents rules from becoming unmoored from coverage rows, tools, reports, and release gates.', '', '| rule | rule_name | trace_status | gates | tools | reports |','|---:|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['rule_number']} | {r['rule_name'].replace('|','/')} | {r['trace_status']} | {r['mapped_release_gates']} | `{r['mapped_tools']}` | `{r['mapped_reports']}` |")
    (out/'Rule-Gate-Traceability-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-missing', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('trace_status') in {'missing_boundary_coverage','missing_trace_file'}]
    print(f"{'FAIL' if bad else 'PASS'} rule-gate traceability rules={len(rows)} blocking={len(bad)}")
    if args.fail_on_missing and bad: sys.exit(1)
if __name__=='__main__': main()
