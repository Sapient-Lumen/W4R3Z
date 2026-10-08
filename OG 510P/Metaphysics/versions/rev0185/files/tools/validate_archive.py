#!/usr/bin/env python3
from pathlib import Path
import sys, re, hashlib, subprocess, importlib.util, yaml

VERSION = 'rev0185'
FINAL_DOC = 191

SPECIAL_SCHEMAS = {
    'release-validation': 'validation-record-v1.yml',
    'release-workflow': 'workflow-run-record-v1.yml',
    'schema-conformance': 'schema-conformance-report-v1.yml',
}

REQUIRED_ROOTS = [
 'CONTROL_STACK.yml','CUBE_INDEX.yml','READER_JOURNEY_MAP.yml','STATUS_VOCABULARY.yml','REFERENCE_MAP.yml','QUERY_REGRESSION_SUITE.yml',
 'CLAIM_LANGUAGE_LEDGER.yml','PROVENANCE_LEDGER.yml','INVARIANT_CATALOG.yml','TRACEABILITY_MATRIX.yml','CHANGE_IMPACT_MATRIX.yml','MIGRATION_LEDGER.yml','FIXTURE_CORPUS.yml',
 'CLAIM_GRAPH.yml','EVIDENCE_PACKET_INDEX.yml','CONTRADICTION_LEDGER.yml','FRESHNESS_POLICY.yml','DEFEASANCE_PROPAGATION.yml',
 'RELEASE_GATE_POLICY.yml','ACCEPTANCE_CRITERIA_MATRIX.yml','RELEASE_DECISION_LEDGER.yml','WAIVER_EXCEPTION_LEDGER.yml','RISK_ACCEPTANCE_LEDGER.yml','ASSURANCE_CASE_SKELETON.yml',
 'BUILD_REPRODUCIBILITY_LEDGER.yml','ATTESTATION_BOUNDARY_LEDGER.yml','EVIDENCE_CHAIN_CUSTODY.yml','EXECUTION_LOG_LEDGER.yml','ROLLBACK_RETRACTION_PLAN.yml','PUBLIC_RELEASE_ATTESTATION.yml',
 'OBSERVABILITY_MONITORING_PLAN.yml','AUDIT_SAMPLING_PLAN.yml','FEEDBACK_INTAKE_LEDGER.yml','DOWNSTREAM_RELIANCE_LEDGER.yml','DRIFT_ANOMALY_LEDGER.yml','EXERCISE_INCIDENT_DRILL_LEDGER.yml',
 'REMEDIATION_TRIAGE_POLICY.yml','SEVERITY_CLASSIFICATION_MATRIX.yml','SERVICE_OBJECTIVE_LEDGER.yml','CORRECTIVE_ACTION_REGISTER.yml','COMMUNICATION_ESCALATION_LEDGER.yml','CLOSURE_VERIFICATION_LEDGER.yml',
 'ROLE_AUTHORITY_MATRIX.yml','ACCOUNTABILITY_ASSIGNMENT_LEDGER.yml','SEGREGATION_OF_DUTIES_POLICY.yml','DELEGATION_HANDOFF_LEDGER.yml','APPROVAL_CONSENT_LEDGER.yml','ACCOUNTABILITY_REVIEW_LEDGER.yml',
 'CONTESTATION_INTAKE_LEDGER.yml','APPEAL_REVIEW_POLICY.yml','DISSENT_MINORITY_REPORT_LEDGER.yml','HARM_IMPACT_REVIEW_LEDGER.yml','REDRESS_REVERSAL_LEDGER.yml','STAKEHOLDER_CHALLENGE_REGISTER.yml',
 'PRIVACY_MINIMIZATION_POLICY.yml','CONFIDENTIALITY_ACCESS_MATRIX.yml','DISCLOSURE_PUBLICATION_REVIEW.yml','RETENTION_DELETION_LEDGER.yml','SENSITIVE_DATA_CLASSIFICATION.yml','PRIVACY_RISK_REVIEW_LEDGER.yml',
 'SECURITY_THREAT_MODEL.yml','ABUSE_MISUSE_CASE_REGISTER.yml','VULNERABILITY_DISCLOSURE_INTAKE.yml','SECURITY_HARDENING_BASELINE.yml','TRUST_BOUNDARY_LEDGER.yml','SECRET_KEY_MATERIAL_POLICY.yml',
 'MAINTAINERSHIP_STEWARDSHIP_LEDGER.yml','DEPENDENCY_UPDATE_POLICY.yml','PRESERVATION_ARCHIVAL_PLAN.yml','PORTABILITY_INTEROPERABILITY_MATRIX.yml','SUCCESSION_CONTINUITY_PLAN.yml','SUNSET_END_OF_LIFE_LEDGER.yml',
 'LICENSE_REUSE_POLICY.yml','ATTRIBUTION_CITATION_LEDGER.yml','THIRD_PARTY_CONTENT_REGISTER.yml','CONTRIBUTOR_PROVENANCE_LEDGER.yml','DERIVATIVE_REDISTRIBUTION_POLICY.yml','COMPLIANCE_BOUNDARY_LEDGER.yml',
 'ETHICAL_IMPACT_ASSESSMENT.yml','PUBLIC_INTEREST_BALANCING_LEDGER.yml','AFFECTED_PARTY_ANALYSIS.yml','FAIRNESS_BIAS_REVIEW_LEDGER.yml','MISUSE_SENSITIVE_RELEASE_POLICY.yml','BENEFIT_HARM_REGISTER.yml',
 'ACCESSIBILITY_REVIEW_PLAN.yml','READABILITY_PLAIN_LANGUAGE_LEDGER.yml','DISCOVERABILITY_NAVIGATION_MAP.yml','LOCALIZATION_TRANSLATION_BOUNDARY.yml','USER_GUIDANCE_ONBOARDING_LEDGER.yml','INCLUSIVE_ACCESS_RISK_REGISTER.yml',
 'CURRENT_RELEASE.yml','SOURCE_ANCHOR_LEDGER.yml','SOURCE_REVIEW_LEDGER.yml','DEBT_TAXONOMY.yml','CONCEPT_CUBE.yml','DISCOVERY_BACKLOG.yml','ACCESSIBILITY_TEST_MATRIX.yml','COMPREHENSION_STUDY_PLAN.yml','READER_TASK_PROTOCOL.yml','GLOSSARY_USABILITY_LEDGER.yml','SCREEN_READER_SMOKE_TEST_LOG.yml','KEYBOARD_NAVIGATION_CHECK.yml','TRANSLATION_READINESS_LEDGER.yml','datapackage.json','ro-crate-metadata.json','CUBE/datasets.yml','CUBE/dimensions.yml','CUBE/measures.yml','CUBE/attributes.yml','CUBE/observations/artifacts.yml','CUBE/observations/claims.yml','CUBE/observations/debts.yml','CUBE/observations/controls.yml','CUBE/observations/sources.yml','CUBE/observations/access.yml','CUBE/observations/concepts.yml','CUBE/observations/cube_audit.yml','CUBE/observations/concept_relations.yml','CUBE_AUDIT_LEDGER.yml','CONCEPT_RELATION_MAP.yml','CONCEPT_FAMILY_MAP.yml','CUBE/observations/source_audit.yml','CUBE/observations/source_relations.yml','SOURCE_AUDIT_LEDGER.yml','SOURCE_RELATION_MAP.yml','SOURCE_FAMILY_MAP.yml','SOURCE_CITATION_INDEX.yml','SOURCE_CROSSWALK_NORMALIZED.yml','CLAIM_OBSERVATION_INDEX.yml','CLAIM_RELATION_MAP.yml','CLAIM_AUDIT_LEDGER.yml','CUBE/observations/claim_relations.yml','CUBE/observations/claim_audit.yml','DEBT_OBSERVATION_INDEX.yml','DEBT_LIFECYCLE_POLICY.yml','DEBT_RELATION_MAP.yml','DEBT_AUDIT_LEDGER.yml','CUBE/observations/debt_relations.yml','CUBE/observations/debt_audit.yml','tools/generate_claim_observations.py','tools/check_claim_cube_refactor.py','tools/check_claim_audit.py','tools/check_debt_cube_refactor.py','tools/check_debt_audit.py'
]

REQUIRED_REPORTS = [
 'schema-conformance-report','reference-integrity-report','status-vocabulary-report','query-regression-report','invariant-report','traceability-report','fixture-report',
 'claim-graph-report','evidence-packet-report','contradiction-report','freshness-report','defeasance-report',
 'release-gate-report','acceptance-criteria-report','release-decision-report','waiver-exception-report','risk-acceptance-report','assurance-case-report',
 'build-reproducibility-report','attestation-boundary-report','evidence-custody-report','execution-log-report','rollback-retraction-report','public-release-attestation-report',
 'observability-report','audit-sampling-report','feedback-intake-report','downstream-reliance-report','drift-anomaly-report','exercise-drill-report',
 'remediation-triage-report','severity-classification-report','service-objective-report','corrective-action-report','communication-escalation-report','closure-verification-report',
 'role-authority-report','accountability-assignment-report','segregation-duties-report','delegation-handoff-report','approval-consent-report','accountability-review-report',
 'contestation-intake-report','appeal-review-report','dissent-report','harm-impact-report','redress-reversal-report','stakeholder-challenge-report',
 'privacy-minimization-report','confidentiality-access-report','disclosure-publication-report','retention-deletion-report','sensitive-data-classification-report','privacy-risk-review-report',
 'security-threat-model-report','abuse-misuse-case-report','vulnerability-disclosure-report','security-hardening-report','trust-boundary-report','secret-key-material-report',
 'maintainership-stewardship-report','dependency-update-report','preservation-archival-report','portability-interoperability-report','succession-continuity-report','sunset-eol-report',
 'license-reuse-report','attribution-citation-report','third-party-content-report','contributor-provenance-report','derivative-redistribution-report','compliance-boundary-report',
 'ethical-impact-report','public-interest-balancing-report','affected-party-analysis-report','fairness-bias-review-report','misuse-sensitive-release-report','benefit-harm-report',
 'accessibility-review-report','readability-plain-language-report','discoverability-navigation-report','localization-translation-report','user-guidance-onboarding-report','inclusive-access-risk-report',
 'current-release-normalization-report','cube-observation-expansion-report','source-anchor-report','debt-taxonomy-report','access-evidence-report','concept-cube-report','discovery-backlog-report','packaging-metadata-report','stale-token-check-report','cube-audit-report','concept-cube-refactor-report','concept-relation-map-report','concept-family-map-report','source-crosswalk-normalization-report','source-citation-index-report','source-family-map-report','source-relation-map-report','source-audit-report','source-cube-refactor-report','claim-observation-index-report','claim-relation-map-report','claim-audit-report','claim-cube-refactor-report','debt-observation-index-report','debt-lifecycle-policy-report','debt-relation-map-report','debt-audit-report','debt-cube-refactor-report'
]

STATUS_REPORT_NEEDLES = {
 'REGISTERS/invariant-report-rev0185.yml': 'INV4',
 'REGISTERS/traceability-report-rev0185.yml': 'TRC4',
 'REGISTERS/claim-graph-report-rev0185.yml': 'CG5',
 'REGISTERS/evidence-packet-report-rev0185.yml': 'EVP5',
 'REGISTERS/release-gate-report-rev0185.yml': 'GTE4',
 'REGISTERS/build-reproducibility-report-rev0185.yml': 'BLD4',
 'REGISTERS/observability-report-rev0185.yml': 'OBS4',
 'REGISTERS/remediation-triage-report-rev0185.yml': 'REM4',
 'REGISTERS/role-authority-report-rev0185.yml': 'RAR4',
 'REGISTERS/accountability-assignment-report-rev0185.yml': 'AAS4',
 'REGISTERS/segregation-duties-report-rev0185.yml': 'SOD4',
 'REGISTERS/delegation-handoff-report-rev0185.yml': 'DLG4',
 'REGISTERS/approval-consent-report-rev0185.yml': 'APC4',
 'REGISTERS/accountability-review-report-rev0185.yml': 'ACR4',
 'REGISTERS/fixture-report-rev0185.yml': 'FX6',
 'REGISTERS/privacy-minimization-report-rev0185.yml': 'PMN4',
 'REGISTERS/confidentiality-access-report-rev0185.yml': 'CAF4',
 'REGISTERS/disclosure-publication-report-rev0185.yml': 'DSP4',
 'REGISTERS/retention-deletion-report-rev0185.yml': 'RTN4',
 'REGISTERS/sensitive-data-classification-report-rev0185.yml': 'SDC4',
 'REGISTERS/privacy-risk-review-report-rev0185.yml': 'PRR4',
 'REGISTERS/security-threat-model-report-rev0185.yml': 'THM4',
 'REGISTERS/abuse-misuse-case-report-rev0185.yml': 'ABU4',
 'REGISTERS/vulnerability-disclosure-report-rev0185.yml': 'VUL4',
 'REGISTERS/security-hardening-report-rev0185.yml': 'HRD4',
 'REGISTERS/trust-boundary-report-rev0185.yml': 'TRB4',
 'REGISTERS/secret-key-material-report-rev0185.yml': 'SKM4',
 'REGISTERS/maintainership-stewardship-report-rev0185.yml': 'MTN4',
 'REGISTERS/dependency-update-report-rev0185.yml': 'DUP4',
 'REGISTERS/preservation-archival-report-rev0185.yml': 'PRS4',
 'REGISTERS/portability-interoperability-report-rev0185.yml': 'POR4',
 'REGISTERS/succession-continuity-report-rev0185.yml': 'SUC4',
 'REGISTERS/sunset-eol-report-rev0185.yml': 'EOL4',
 'REGISTERS/license-reuse-report-rev0185.yml': 'LIC4',
 'REGISTERS/attribution-citation-report-rev0185.yml': 'ATB4',
 'REGISTERS/third-party-content-report-rev0185.yml': 'TPC4',
 'REGISTERS/contributor-provenance-report-rev0185.yml': 'CPN4',
 'REGISTERS/derivative-redistribution-report-rev0185.yml': 'DER4',
 'REGISTERS/compliance-boundary-report-rev0185.yml': 'CBL4',
 'REGISTERS/ethical-impact-report-rev0185.yml': 'EIA4',
 'REGISTERS/public-interest-balancing-report-rev0185.yml': 'PIB4',
 'REGISTERS/affected-party-analysis-report-rev0185.yml': 'APA4',
 'REGISTERS/fairness-bias-review-report-rev0185.yml': 'FBR4',
 'REGISTERS/misuse-sensitive-release-report-rev0185.yml': 'MSR4',
 'REGISTERS/benefit-harm-report-rev0185.yml': 'BHR4',
 'REGISTERS/accessibility-review-report-rev0185.yml': 'ACY4',
 'REGISTERS/readability-plain-language-report-rev0185.yml': 'RPL4',
 'REGISTERS/discoverability-navigation-report-rev0185.yml': 'DNM4',
 'REGISTERS/localization-translation-report-rev0185.yml': 'LTB4',
 'REGISTERS/user-guidance-onboarding-report-rev0185.yml': 'UGO4',
 'REGISTERS/inclusive-access-risk-report-rev0185.yml': 'IAR4',
 'REGISTERS/current-release-normalization-report-rev0185.yml': 'CRN4',
 'REGISTERS/cube-observation-expansion-report-rev0185.yml': 'DCE4',
 'REGISTERS/source-anchor-report-rev0185.yml': 'SRC4',
 'REGISTERS/debt-taxonomy-report-rev0185.yml': 'DBT4',
 'REGISTERS/access-evidence-report-rev0185.yml': 'ATE4',
 'REGISTERS/concept-cube-report-rev0185.yml': 'CNC4',
 'REGISTERS/discovery-backlog-report-rev0185.yml': 'DSB4',
 'REGISTERS/packaging-metadata-report-rev0185.yml': 'PKG4',
 'REGISTERS/stale-token-check-report-rev0185.yml': 'STR4',
 'REGISTERS/concept-family-map-report-rev0185.yml': 'CFM4',
 'REGISTERS/concept-relation-map-report-rev0185.yml': 'CRX4',
 'REGISTERS/concept-cube-refactor-report-rev0185.yml': 'CCR4',
 'REGISTERS/cube-audit-report-rev0185.yml': 'CDA4',
 'REGISTERS/source-crosswalk-normalization-report-rev0185.yml': 'SCN4',
 'REGISTERS/source-citation-index-report-rev0185.yml': 'SCI4',
 'REGISTERS/source-family-map-report-rev0185.yml': 'SCF4',
 'REGISTERS/source-relation-map-report-rev0185.yml': 'SRX4',
 'REGISTERS/source-audit-report-rev0185.yml': 'SDA4',
 'REGISTERS/source-cube-refactor-report-rev0185.yml': 'SCF4',
 'REGISTERS/claim-observation-index-report-rev0185.yml': 'CIO4',
 'REGISTERS/claim-relation-map-report-rev0185.yml': 'CLX4',
 'REGISTERS/claim-audit-report-rev0185.yml': 'CLA4',
 'REGISTERS/claim-cube-refactor-report-rev0185.yml': 'CCF4',
 'REGISTERS/debt-observation-index-report-rev0185.yml': 'DCI4',
 'REGISTERS/debt-lifecycle-policy-report-rev0185.yml': 'DLP4',
 'REGISTERS/debt-relation-map-report-rev0185.yml': 'DRM4',
 'REGISTERS/debt-audit-report-rev0185.yml': 'DBA4',
 'REGISTERS/debt-cube-refactor-report-rev0185.yml': 'DCF4',
}

def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def dump_yaml(obj):
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)

def sha(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def schema_path_for(root, family):
    name = SPECIAL_SCHEMAS.get(family, f'{family}-record-v1.yml')
    return root/'REGISTERS'/'schemas'/name

def schema_required(root, family):
    sp=schema_path_for(root, family)
    if not sp.exists():
        return None, [f'missing schema for {family}: {sp.relative_to(root)}']
    schema=load(sp)
    req=schema.get('required_fields') or []
    return req, []

def flatten_keys(obj, prefix=''):
    if isinstance(obj, dict):
        for k,v in obj.items():
            p=f'{prefix}.{k}' if prefix else str(k)
            yield p
            yield from flatten_keys(v,p)
    elif isinstance(obj, list):
        for i,v in enumerate(obj):
            yield from flatten_keys(v,f'{prefix}[{i}]')

def value_at(obj, dotted):
    cur=obj
    for part in dotted.split('.'):
        if isinstance(cur, dict) and part in cur:
            cur=cur[part]
        else:
            return None
    return cur

def validate_required_fields(root, failures):
    current=sorted((root/'REGISTERS').glob(f'{VERSION}-*.yml'))
    if not current:
        failures.append('no current records found')
    misses=[]
    for rec in current:
        family=rec.stem[len(VERSION)+1:]
        req, errs = schema_required(root, family)
        failures.extend(errs)
        if req is None: continue
        data=load(rec)
        missing=[]
        for field in req:
            v=value_at(data, field)
            if v is None or v == '':
                missing.append(field)
        if missing:
            misses.append({'record':str(rec.relative_to(root)), 'missing':missing})
    if misses:
        failures.append('required-field misses: '+dump_yaml(misses).strip())

def validate_status(root, failures):
    vocab=load(root/'STATUS_VOCABULARY.yml')
    allowed=set()
    for fam in (vocab.get('code_families') or vocab.get('families') or []):
        allowed.update((fam.get('codes') or {}).keys())
    if not allowed:
        failures.append('status vocabulary has no codes')
        return
    text='\n'.join(p.read_text('utf-8', errors='ignore') for p in sorted((root/'REGISTERS').glob(f'{VERSION}-*.yml')))
    tokens=set(re.findall(r'\b([A-Z]{2,5}\d+)(?:_[A-Za-z0-9_]+)?\b', text))
    bad=sorted(t for t in tokens if t not in allowed)
    if bad:
        failures.append('undefined current status tokens: '+', '.join(bad[:50]))

def validate_docs(root, failures):
    docs=list((root/'docs').glob('*.md'))
    nums=[]
    for p in docs:
        m=re.match(r'^(\d+)-', p.name)
        if m: nums.append(int(m.group(1)))
    nums=sorted(set(nums))
    if nums != list(range(0, FINAL_DOC+1)):
        failures.append(f'numbered docs not contiguous 00-{FINAL_DOC}: got {nums[:3]}...{nums[-5:] if nums else []}, count {len(nums)}')
    front=(root/'README.md').read_text('utf-8')+'\n'+(root/'ARCHIVE_INDEX.md').read_text('utf-8')
    for rel in REQUIRED_ROOTS:
        if not (root/rel).exists(): failures.append(f'missing required artifact: {rel}')
        if rel not in front: failures.append(f'front-door missing artifact: {rel}')
    for name in REQUIRED_REPORTS:
        rel=f'REGISTERS/{name}-{VERSION}.yml'
        if not (root/rel).exists(): failures.append(f'missing required report: {rel}')

def validate_control(root, failures):
    data=load(root/'CONTROL_STACK.yml')
    steps=data.get('steps',[]) or []
    by={s.get('step'):s for s in steps}
    for n in range(144, FINAL_DOC+1):
        if n not in by:
            failures.append(f'control step missing: {n}'); continue
        doc=by[n].get('file')
        if not doc or not (root/doc).exists(): failures.append(f'control step {n} missing doc: {doc}')
        exp=None if n==FINAL_DOC else n+1
        got=by[n].get('successor_step')
        if got != exp:
            failures.append(f'bad successor for control step {n}: {got} expected {exp}')

def validate_cube(root, failures):
    cube=load(root/'CUBE_INDEX.yml')
    obs=(cube.get('current_release_observations') or cube.get('observations') or [])
    if len(obs) < len(list((root/'REGISTERS').glob(f'{VERSION}-*.yml'))):
        failures.append(f'cube observations too few: {len(obs)}')
    for o in obs:
        for rel in o.get('source_artifacts',[]) or []:
            if not (root/rel).exists(): failures.append(f'cube source artifact missing: {rel}')

def validate_reference(root, failures):
    report=root/f'REGISTERS/reference-integrity-report-{VERSION}.yml'
    if report.exists():
        data=load(report)
        if data.get('missing_references') not in ([], None) or data.get('missing_reference_count',0) not in (0,None):
            failures.append('live reference integrity failed')

def validate_query(root, failures):
    # Run query regression in-process to avoid subprocess/fork overhead after large YAML loads.
    import hashlib, importlib.util
    suite=load(root/'QUERY_REGRESSION_SUITE.yml')
    spec=importlib.util.spec_from_file_location('query_cube_module', root/'tools/query_cube.py')
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    qfail=[]
    for q in suite.get('queries',[]):
        name=q['name']
        try:
            out=mod.render_query(root, name)
            err=''
        except Exception as e:
            out=''; err=repr(e)
        lines=[l for l in out.splitlines() if l.strip()]
        missing=[sub for sub in q.get('required_substrings',[]) if sub not in out]
        if err or len(lines)<q.get('min_lines',0) or missing:
            qfail.append({'query':name,'line_count':len(lines),'missing_substrings':missing,'error':err})
    if qfail:
        failures.append('query regression failed: '+dump_yaml({'failures':qfail[:20]}).strip())

def validate_reports(root, failures):
    for rel, needle in STATUS_REPORT_NEEDLES.items():
        p=root/rel
        if not p.exists():
            failures.append(f'missing status report: {rel}')
            continue
        text=p.read_text('utf-8', errors='ignore')
        if needle not in text:
            failures.append(f'report {rel} missing status token {needle}')

def validate_checkers(root, failures):
    # The integrated validator remains bounded: it checks checker presence and report-status
    # surfaces here. The individual semantic checkers are run as separate release evidence
    # and their outputs are required by validate_reports.
    for script in [
        'check_invariants.py','check_traceability.py','check_claim_evidence.py','check_release_gates.py','check_repro_attestation.py',
        'check_observability_feedback.py','check_remediation_closure.py','check_accountability_authority.py','check_contestability_redress.py','check_privacy_confidentiality.py','check_security_abuse.py','check_lifecycle_sustainability.py','check_legal_reuse.py','check_ethics_public_interest.py','check_accessibility_comprehension.py','check_current_release.py','check_stale_revision_tokens.py','generate_debt_observations.py','generate_concept_observations.py','generate_source_observations.py','check_concept_cube_refactor.py','check_cube_audit.py','check_source_cube_refactor.py','check_source_audit.py','generate_claim_observations.py','check_claim_cube_refactor.py','check_claim_audit.py','check_debt_cube_refactor.py','check_debt_audit.py']:
        if not (root/'tools'/script).exists():
            failures.append(f'missing checker tool: tools/{script}')

def validate_external(root, failures):
    x=load(root/'EXTERNAL_CROSSWALK.yml')
    anchors=x.get('anchors',[]) or []
    if len(anchors) < 80:
        failures.append(f'external-crosswalk anchors too few: {len(anchors)}')
    if 'not compliance' not in (str(x.get('claim_boundary','')).lower()) and 'compliance claims remain forbidden' not in (str(x.get('status','')).lower()):
        failures.append('external-crosswalk does not preserve not-compliance boundary')



def validate_current_release(root, failures):
    # Inline current-release checks; individual checker remains available as separate evidence.
    version=(root/'VERSION').read_text('utf-8').strip() if (root/'VERSION').exists() else None
    cr=load(root/'CURRENT_RELEASE.yml')
    if not cr:
        failures.append('missing CURRENT_RELEASE.yml'); return
    if cr.get('archive_version') != VERSION or version != VERSION:
        failures.append('CURRENT_RELEASE/VERSION archive_version mismatch')
    package=cr.get('package')
    if not package or VERSION not in package:
        failures.append('current package does not contain current version token')
    if cr.get('final_numbered_doc') != FINAL_DOC:
        failures.append('CURRENT_RELEASE final_numbered_doc mismatch')
    current_doc=(cr.get('current_layer') or {}).get('doc')
    if not current_doc or not (root/current_doc).exists():
        failures.append('current layer doc missing')
    elif not Path(current_doc).name.startswith(f'{FINAL_DOC}-'):
        failures.append('current layer doc does not match final doc')
    for rel in cr.get('front_door_artifacts',[]):
        if not (root/rel).exists(): failures.append(f'front-door artifact missing: {rel}')
    for rel in cr.get('validation_tools',[]):
        if not (root/rel).exists(): failures.append(f'validation tool missing: {rel}')
    for p in sorted(root.glob('*.yml')):
        if p.name == 'MANIFEST.sha256':
            continue
        data=load(p)
        if not isinstance(data,dict): continue
        if 'archive_version' in data and data['archive_version'] != VERSION:
            failures.append(f'{p.name}: archive_version={data["archive_version"]!r} expected {VERSION!r}')
        if 'package' in data and data['package'] != package:
            failures.append(f'{p.name}: package does not match CURRENT_RELEASE.yml')

def validate_cube_datasets(root, failures):
    datasets=load(root/'CUBE'/'datasets.yml')
    needed=['ArtifactCube','ClaimCube','ClaimRelationCube','ClaimAuditCube','DebtCube','DebtRelationCube','DebtAuditCube','ControlCube','SourceCube','SourceRelationCube','SourceAuditCube','AccessCube','ConceptCube','ConceptRelationCube','CubeAuditCube']
    got=[d.get('dataset_id') for d in datasets.get('datasets',[]) or []]
    for n in needed:
        if n not in got: failures.append(f'cube dataset missing: {n}')
    for d in datasets.get('datasets',[]) or []:
        p=root/d.get('path','')
        if not p.exists(): failures.append(f'cube dataset path missing: {d.get("path")}')
    for rel in ['CUBE/dimensions.yml','CUBE/measures.yml','CUBE/attributes.yml']:
        if not (root/rel).exists(): failures.append(f'cube component missing: {rel}')

def validate_json_metadata(root, failures):
    import json
    for rel in ['datapackage.json','ro-crate-metadata.json']:
        try:
            json.loads((root/rel).read_text('utf-8'))
        except Exception as e:
            failures.append(f'json metadata failed: {rel}: {e}')

def validate_python(root, failures):
    import py_compile
    for p in sorted((root/'tools').glob('*.py')):
        try:
            py_compile.compile(str(p), doraise=True)
        except Exception as e:
            failures.append(f'python syntax failed: {p.relative_to(root)}: {e}')

def validate_manifest(root, failures):
    mp=root/'MANIFEST.sha256'
    if not mp.exists(): failures.append('missing MANIFEST.sha256'); return
    expected={}
    for line in mp.read_text('utf-8').splitlines():
        if not line.strip(): continue
        try:
            digest, rel=line.split('  ',1)
        except ValueError:
            failures.append('malformed manifest line: '+line); continue
        expected[rel]=digest
    actual={}
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.name=='MANIFEST.sha256': continue
        rel=str(p.relative_to(root))
        if rel.startswith('.') or '__pycache__' in rel or rel.endswith('.pyc'): continue
        actual[rel]=sha(p)
    missing=sorted(set(expected)-set(actual)); extra=sorted(set(actual)-set(expected))
    mism=[rel for rel,d in expected.items() if rel in actual and actual[rel]!=d]
    if missing or extra or mism:
        failures.append('manifest mismatch: '+dump_yaml({'missing':missing[:20],'extra':extra[:20],'mismatched':mism[:20]}).strip())

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    failures=[]
    if not (root/'VERSION').exists() or (root/'VERSION').read_text('utf-8').strip()!=VERSION:
        failures.append('VERSION is not '+VERSION)
    for fn in [validate_query, validate_current_release, validate_docs, validate_required_fields, validate_status, validate_control, validate_cube, validate_cube_datasets, validate_json_metadata, validate_reference, validate_reports, validate_checkers, validate_external, validate_python, validate_manifest]:
        try:
            fn(root, failures)
        except Exception as e:
            failures.append(f'{fn.__name__} crashed: {e}')
    if failures:
        print('VALIDATION FAILED')
        for f in failures: print('-', f)
        return 1
    print('VALIDATION PASSED')
    print('version: rev0185')
    print('numbered_docs: 00-191 (192 files)')
    print('scope: package structure, numbered-doc continuity, front-door inclusion, current-record required fields, status vocabulary, reference-map summary, query regression, invariant/traceability reports, claim/evidence reports, release-gate reports, reproducibility/attestation reports, post-release observability reports, remediation/closure reports, accountability/authority reports, contestability/redress reports, privacy/confidentiality reports, security/abuse reports, lifecycle sustainability reports, legal/reuse boundary reports, ethics/public-interest reports, accessibility/comprehension reports, current-release/stale-token checks, expanded-cube checks, schema-constraint checks, fixture-report pass, claim-language ledger, provenance ledger, debt-cube refactor reports, control-stack continuity, cube source artifacts, external-crosswalk shape, Python tool syntax, and manifest integrity only')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
