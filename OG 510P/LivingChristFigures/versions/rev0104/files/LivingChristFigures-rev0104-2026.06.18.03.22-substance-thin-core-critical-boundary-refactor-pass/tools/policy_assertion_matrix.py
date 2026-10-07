#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

FIELDS=['assertion_id','policy_assertion','policy_surface','enforced_by_gates','enforced_by_tools','evidence_reports','status','note']

ASSERTIONS=[
    ('assertion_001','Public layer remains index/policy/template/manifest only; no public URL release.','PUBLIC/README-public-edition.md|SCHEMA/Package-Release-Contract-current.json','gate_009|gate_012|gate_013|gate_014|gate_064','tools/public_source_link_review.py|tools/public_index_parity.py|tools/public_index_semantic_audit.py|tools/governance_consistency_audit.py','META/Public-Source-Link-Review-current.csv|META/Public-Index-Parity-current.csv|META/Public-Index-Semantic-Audit-current.csv|META/Governance-Consistency-Audit-current.csv','public URL exposure is blocked unless reviewed through source-link and public-index gates'),
    ('assertion_002','No case detail, testimony, image, route, live referral, support path, or capacity claim is released.','CURRENT-SPINE.md|PUBLIC/README-public-edition.md|PUBLIC/Public-Redaction-Policy-current.md','gate_004|gate_005|gate_006|gate_007|gate_013|gate_064|gate_067','tools/public_release_lint.py|tools/redaction_scan.py|tools/rule46_scan.py|tools/sensitive_surface_inventory.py|tools/public_index_parity.py|tools/public_index_semantic_audit.py|tools/source_safety_nearmiss_audit.py','META/Public-Release-Lint-current.csv|META/Redaction-Risk-Open-Findings-current.csv|META/Rule46-Scan-current.csv|META/Sensitive-Surface-Inventory-current.csv|META/Public-Index-Parity-current.csv|META/Public-Index-Semantic-Audit-current.csv|META/Source-Safety-Nearmiss-Audit-current.csv','public-surface scanners, semantic parity, and source near-miss checks jointly enforce the non-release posture'),
    ('assertion_003','Candidate-level public export is eligibility-led and fail-closed.','GOVERNANCE/Public-Export-Eligibility-Protocol-current.md|META/Public-Export-Eligibility-current.csv','gate_008|gate_013|gate_014|gate_064','tools/public_export_eligibility.py|tools/render_public_safe_index.py|tools/public_index_parity.py|tools/public_index_semantic_audit.py|tools/governance_consistency_audit.py','META/Public-Export-Eligibility-current.csv|PUBLIC/Candidate-Index-public.csv|META/Public-Index-Parity-current.csv|META/Public-Index-Semantic-Audit-current.csv|META/Governance-Consistency-Audit-current.csv','renderer depends on eligibility ledger, shared semantic template policy, and parity/consistency checks'),
    ('assertion_004','Indigenous data-governance and takedown/reclassification remain required before expansion of MMIWG2S+ or Indigenous family-led material.','GOVERNANCE/Indigenous-Data-Governance-Protocol-current.md|GOVERNANCE/Takedown-and-Reclassification-Protocol-current.md|GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv','gate_014|gate_023','tools/governance_consistency_audit.py|tools/required_document_coverage.py','META/Governance-Consistency-Audit-current.csv|META/Required-Document-Coverage-current.csv','governance documents and ledgers must exist and remain consistent'),
    ('assertion_005','Current revision surfaces cannot silently drift from the manifest.','000-START-HERE.txt|CURRENT-SPINE.md|CUBE-MAP.md|CUBE-RULES.txt|manifest.json','gate_001|gate_010|gate_023','tools/revision_surface_audit.py|tools/required_document_coverage.py','META/Revision-Surface-Audit-current.csv|META/Required-Document-Coverage-current.csv','front-door and JSON revision fields are audited'),
    ('assertion_006','Generated reports are not trusted unless their generator, inputs, hashes, and rebuild readiness are recorded.','META/Generated-Artifact-Provenance-current.csv|META/Rebuild-Readiness-Audit-current.csv','gate_011|gate_025','tools/generated_artifact_provenance.py|tools/rebuild_readiness_audit.py','META/Generated-Artifact-Provenance-current.csv|META/Rebuild-Readiness-Audit-current.csv','provenance and rebuild-readiness reports gate generated artifacts'),
    ('assertion_007','Schemas, mirrors, and field definitions must remain explicit and zero-backlog.','SCHEMA/Ledger-Contract-current.json|SCHEMA/README-schema-current.md','gate_016|gate_017|gate_019','tools/csv_json_mirror_audit.py|tools/schema_coverage_audit.py|tools/field_schema_consistency.py','META/CSV-JSON-Mirror-Audit-current.csv|META/Schema-Coverage-Audit-current.csv|META/Field-Schema-Consistency-Audit-current.csv','mirror and schema backlogs are release-blocking'),
    ('assertion_008','Package tools and paths must be inventoried and traceable to release gates or explicit helper status.','tools/README.md|META/Package-Dependency-Graph-current.csv|META/Tool-Run-Matrix-current.csv','gate_015|gate_020|gate_021|gate_022','tools/package_dependency_graph.py|tools/path_reference_audit.py|tools/rule_gate_traceability.py|tools/tool_run_matrix.py','META/Package-Dependency-Graph-current.csv|META/Path-Reference-Audit-current.csv|META/Rule-Gate-Traceability-current.csv|META/Tool-Run-Matrix-current.csv','tool/path/rule traceability must pass'),
    ('assertion_009','Selected validators must prove they fail on known-bad temporary package copies.','META/Audit-Selftest-current.csv','gate_024','tools/audit_selftest.py','META/Audit-Selftest-current.csv','controlled mutation tests must all pass'),
    ('assertion_010','Package handoff identity is not trusted unless archive member paths, Unicode filenames, and root/manifest/refresh/checksum identity close.','manifest.json|META/Archive-Member-Manifest-current.csv|META/Unicode-Path-Audit-current.csv|META/Package-Identity-Audit-current.csv','gate_033|gate_034|gate_035','tools/archive_member_manifest.py|tools/unicode_path_audit.py|tools/package_identity_audit.py','META/Archive-Member-Manifest-current.csv|META/Unicode-Path-Audit-current.csv|META/Package-Identity-Audit-current.csv','archive-member namespace, Unicode path safety, and package identity closure must pass before handoff'),
    ('assertion_011','Handoff safety now requires explicit dependency-cycle clarity, use-limit notice visibility, and classification of every current CSV surface.','GOVERNANCE/Handoff-Use-Limits-and-Reviewer-Notice-current.md|META/Dependency-Cycle-Audit-current.csv|META/Handoff-Notice-Audit-current.csv|META/Current-Surface-Registry-current.csv','gate_040|gate_041|gate_042','tools/dependency_cycle_audit.py|tools/handoff_notice_audit.py|tools/current_surface_registry.py','META/Dependency-Cycle-Audit-current.csv|META/Handoff-Notice-Audit-current.csv|META/Current-Surface-Registry-current.csv','cycle, notice, and current-surface registry gates must pass before handoff'),
    ('assertion_012','Shared audit helper adoption is gated and report-shape continuity is checked before handoff.','tools/lib_cube.py|META/Helper-Adoption-Audit-current.csv','gate_046','tools/helper_adoption_audit.py|tools/lib_cube.py','META/Helper-Adoption-Audit-current.csv','helper adoption gate must pass before handoff'),
]

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def read_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None

def report_ok(root: Path, rel: str) -> bool:
    p=root/rel
    if not p.exists(): return False
    rows=read_csv(p) if p.suffix.lower()=='.csv' else []
    if rows:
        if rel.endswith('Sensitive-Surface-Inventory-current.csv'):
            # Internal/private findings may be high; public release is blocked only by high public-scope rows.
            if any(r.get('file_scope')=='public' and r.get('severity')=='high' for r in rows): return False
        elif any(r.get('severity')=='high' for r in rows):
            return False
        if any(r.get('status')=='fail' for r in rows): return False
        if any(r.get('trace_status') in {'missing_boundary_coverage','missing_trace_file'} for r in rows): return False
        if any(r.get('coverage_status')=='fail' for r in rows): return False
        if any(r.get('dependency_status')=='missing_dependency' for r in rows): return False
        if any(r.get('status')=='missing_dependency' for r in rows): return False
    return True

def run(root: Path):
    rows=[]
    for aid,assertion,surfaces,gates,tools,reports,note in ASSERTIONS:
        missing=[]
        for rel in [x for x in (surfaces+'|'+tools+'|'+reports).split('|') if x]:
            if not (root/rel).exists(): missing.append(rel)
        bad_reports=[rel for rel in reports.split('|') if rel and not report_ok(root, rel)]
        status='pass' if not missing and not bad_reports else 'fail'
        detail=note if status=='pass' else 'missing='+ '; '.join(missing[:6]) + ('; bad_reports='+ '; '.join(bad_reports[:6]) if bad_reports else '')
        rows.append({'assertion_id':aid,'policy_assertion':assertion,'policy_surface':surfaces,'enforced_by_gates':gates,'enforced_by_tools':tools,'evidence_reports':reports,'status':status,'note':detail})
    return rows

def write_reports(root: Path, rows):
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Policy-Assertion-Matrix-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Policy-Assertion-Matrix-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    bad=[r for r in rows if r.get('status')!='pass']
    lines=['# Policy Assertion Matrix — current','', 'Generated by `tools/policy_assertion_matrix.py`.', '', f'Assertions: {len(rows)}', f'Non-pass assertions: {len(bad)}', '', 'This report maps high-level release claims to policy surfaces, gates, tools, and evidence reports. It is not a substitute for the release gate; it prevents handoff prose from drifting away from executable evidence.', '', '| assertion_id | status | policy_assertion | evidence_reports |','|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['assertion_id']} | {r['status']} | {r['policy_assertion'].replace('|','/')} | `{r['evidence_reports']}` |")
    (out/'Policy-Assertion-Matrix-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-fail', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} policy assertion matrix assertions={len(rows)} nonpass={len(bad)}")
    if args.fail_on_fail and bad: sys.exit(1)
if __name__=='__main__': main()
