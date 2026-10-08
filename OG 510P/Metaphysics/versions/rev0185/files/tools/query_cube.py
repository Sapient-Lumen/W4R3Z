#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

_CACHE = {}
def load(p):
    p = Path(p)
    key = str(p.resolve())
    if key not in _CACHE:
        with open(p, 'r', encoding='utf-8') as f:
            _CACHE[key] = yaml.safe_load(f) or {}
    return _CACHE[key]

def ydump(x): return yaml.safe_dump(x, sort_keys=False, allow_unicode=True).rstrip()
def current_version(root): return (root/'VERSION').read_text(encoding='utf-8').strip()
def current_records(root): return sorted((root/'REGISTERS').glob(f"{current_version(root)}-*.yml"))
ROOT_QUERY_FILES = {'debtauditledger':'DEBT_AUDIT_LEDGER.yml', 'debtaudit':'CUBE/observations/debt_audit.yml', 'debtrelations':'CUBE/observations/debt_relations.yml', 'debtrelationmap':'DEBT_RELATION_MAP.yml', 'debtlifecycle':'DEBT_LIFECYCLE_POLICY.yml', 'debtobservationindex':'DEBT_OBSERVATION_INDEX.yml', 'claimauditledger':'CLAIM_AUDIT_LEDGER.yml', 'claimaudit':'CUBE/observations/claim_audit.yml', 'claimrelations':'CUBE/observations/claim_relations.yml', 'claimrelationmap':'CLAIM_RELATION_MAP.yml', 'claimobservationindex':'CLAIM_OBSERVATION_INDEX.yml', 'claims': 'CLAIM_LANGUAGE_LEDGER.yml', 'provenance': 'PROVENANCE_LEDGER.yml', 'regressions': 'QUERY_REGRESSION_SUITE.yml', 'invariants': 'INVARIANT_CATALOG.yml', 'traceability': 'TRACEABILITY_MATRIX.yml', 'impact': 'CHANGE_IMPACT_MATRIX.yml', 'migration': 'MIGRATION_LEDGER.yml', 'fixtures': 'FIXTURE_CORPUS.yml', 'claimgraph': 'CLAIM_GRAPH.yml', 'evidence': 'EVIDENCE_PACKET_INDEX.yml', 'contradictions': 'CONTRADICTION_LEDGER.yml', 'freshness': 'FRESHNESS_POLICY.yml', 'defeasance': 'DEFEASANCE_PROPAGATION.yml', 'gates': 'RELEASE_GATE_POLICY.yml', 'acceptance': 'ACCEPTANCE_CRITERIA_MATRIX.yml', 'decisions': 'RELEASE_DECISION_LEDGER.yml', 'waivers': 'WAIVER_EXCEPTION_LEDGER.yml', 'riskacceptance': 'RISK_ACCEPTANCE_LEDGER.yml', 'assurance': 'ASSURANCE_CASE_SKELETON.yml', 'build': 'BUILD_REPRODUCIBILITY_LEDGER.yml', 'attestation': 'ATTESTATION_BOUNDARY_LEDGER.yml', 'custody': 'EVIDENCE_CHAIN_CUSTODY.yml', 'execution': 'EXECUTION_LOG_LEDGER.yml', 'rollback': 'ROLLBACK_RETRACTION_PLAN.yml', 'publicattestation': 'PUBLIC_RELEASE_ATTESTATION.yml', 'observability': 'OBSERVABILITY_MONITORING_PLAN.yml', 'audit': 'AUDIT_SAMPLING_PLAN.yml', 'feedback': 'FEEDBACK_INTAKE_LEDGER.yml', 'reliance': 'DOWNSTREAM_RELIANCE_LEDGER.yml', 'drift': 'DRIFT_ANOMALY_LEDGER.yml', 'drills': 'EXERCISE_INCIDENT_DRILL_LEDGER.yml', 'remediation': 'REMEDIATION_TRIAGE_POLICY.yml', 'severity': 'SEVERITY_CLASSIFICATION_MATRIX.yml', 'objectives': 'SERVICE_OBJECTIVE_LEDGER.yml', 'corrective': 'CORRECTIVE_ACTION_REGISTER.yml', 'escalation': 'COMMUNICATION_ESCALATION_LEDGER.yml', 'closure': 'CLOSURE_VERIFICATION_LEDGER.yml', 'roleauthority': 'ROLE_AUTHORITY_MATRIX.yml', 'accountability': 'ACCOUNTABILITY_ASSIGNMENT_LEDGER.yml', 'dutysegregation': 'SEGREGATION_OF_DUTIES_POLICY.yml', 'delegation': 'DELEGATION_HANDOFF_LEDGER.yml', 'approval': 'APPROVAL_CONSENT_LEDGER.yml', 'accountabilityreview': 'ACCOUNTABILITY_REVIEW_LEDGER.yml', 'contestation': 'CONTESTATION_INTAKE_LEDGER.yml', 'appeals': 'APPEAL_REVIEW_POLICY.yml', 'dissent': 'DISSENT_MINORITY_REPORT_LEDGER.yml', 'harm': 'HARM_IMPACT_REVIEW_LEDGER.yml', 'redress': 'REDRESS_REVERSAL_LEDGER.yml', 'challenges': 'STAKEHOLDER_CHALLENGE_REGISTER.yml', 'privacyminimization': 'PRIVACY_MINIMIZATION_POLICY.yml', 'accessboundary': 'CONFIDENTIALITY_ACCESS_MATRIX.yml', 'disclosure': 'DISCLOSURE_PUBLICATION_REVIEW.yml', 'retention': 'RETENTION_DELETION_LEDGER.yml', 'sensitiveclassification': 'SENSITIVE_DATA_CLASSIFICATION.yml', 'privacyrisk': 'PRIVACY_RISK_REVIEW_LEDGER.yml', 'securitythreats': 'SECURITY_THREAT_MODEL.yml', 'abusecases': 'ABUSE_MISUSE_CASE_REGISTER.yml', 'vulnerabilityintake': 'VULNERABILITY_DISCLOSURE_INTAKE.yml', 'securityhardening': 'SECURITY_HARDENING_BASELINE.yml', 'trustboundaries': 'TRUST_BOUNDARY_LEDGER.yml', 'secrets': 'SECRET_KEY_MATERIAL_POLICY.yml', 'maintainership': 'MAINTAINERSHIP_STEWARDSHIP_LEDGER.yml', 'dependencies': 'DEPENDENCY_UPDATE_POLICY.yml', 'preservation': 'PRESERVATION_ARCHIVAL_PLAN.yml', 'portability': 'PORTABILITY_INTEROPERABILITY_MATRIX.yml', 'succession': 'SUCCESSION_CONTINUITY_PLAN.yml', 'sunset': 'SUNSET_END_OF_LIFE_LEDGER.yml', 'licensing': 'LICENSE_REUSE_POLICY.yml', 'attribution': 'ATTRIBUTION_CITATION_LEDGER.yml', 'thirdparty': 'THIRD_PARTY_CONTENT_REGISTER.yml', 'contributors': 'CONTRIBUTOR_PROVENANCE_LEDGER.yml', 'derivatives': 'DERIVATIVE_REDISTRIBUTION_POLICY.yml', 'complianceboundaries': 'COMPLIANCE_BOUNDARY_LEDGER.yml', 'ethicalimpact': 'ETHICAL_IMPACT_ASSESSMENT.yml', 'publicinterest': 'PUBLIC_INTEREST_BALANCING_LEDGER.yml', 'affectedparties': 'AFFECTED_PARTY_ANALYSIS.yml', 'fairnessbias': 'FAIRNESS_BIAS_REVIEW_LEDGER.yml', 'misuserelease': 'MISUSE_SENSITIVE_RELEASE_POLICY.yml', 'benefitharm': 'BENEFIT_HARM_REGISTER.yml', 'accessibility': 'ACCESSIBILITY_REVIEW_PLAN.yml', 'readability': 'READABILITY_PLAIN_LANGUAGE_LEDGER.yml', 'discoverability': 'DISCOVERABILITY_NAVIGATION_MAP.yml', 'localization': 'LOCALIZATION_TRANSLATION_BOUNDARY.yml', 'guidance': 'USER_GUIDANCE_ONBOARDING_LEDGER.yml', 'inclusiveaccess': 'INCLUSIVE_ACCESS_RISK_REGISTER.yml', 'currentrelease': 'CURRENT_RELEASE.yml', 'cubedatasets': 'CUBE/datasets.yml', 'cubedimensions': 'CUBE/dimensions.yml', 'cubemeasures': 'CUBE/measures.yml', 'cubeattributes': 'CUBE/attributes.yml', 'artifactobservations': 'CUBE/observations/artifacts.yml', 'claimobservations': 'CUBE/observations/claims.yml', 'debtobservations': 'CUBE/observations/debts.yml', 'sourceobservations': 'CUBE/observations/sources.yml', 'accessobservations': 'CUBE/observations/access.yml', 'conceptobservations': 'CUBE/observations/concepts.yml', 'sourceanchors': 'SOURCE_ANCHOR_LEDGER.yml', 'sourcereviews': 'SOURCE_REVIEW_LEDGER.yml', 'debttaxonomy': 'DEBT_TAXONOMY.yml', 'conceptfamilymap': 'CONCEPT_FAMILY_MAP.yml', 'conceptrelations': 'CUBE/observations/concept_relations.yml', 'conceptrelationmap': 'CONCEPT_RELATION_MAP.yml', 'cubeauditledger': 'CUBE_AUDIT_LEDGER.yml', 'cubeaudit': 'CUBE/observations/cube_audit.yml', 'conceptcube': 'CONCEPT_CUBE.yml', 'discoverybacklog': 'DISCOVERY_BACKLOG.yml', 'accessibilitytests': 'ACCESSIBILITY_TEST_MATRIX.yml', 'comprehensionplan': 'COMPREHENSION_STUDY_PLAN.yml', 'readertasks': 'READER_TASK_PROTOCOL.yml', 'glossaryusability': 'GLOSSARY_USABILITY_LEDGER.yml', 'screenreader': 'SCREEN_READER_SMOKE_TEST_LOG.yml', 'keyboardnav': 'KEYBOARD_NAVIGATION_CHECK.yml', 'translationreadiness': 'TRANSLATION_READINESS_LEDGER.yml', 'readerjourney': 'READER_JOURNEY_MAP.yml', 'accessmatrix': 'ACCESSIBILITY_TEST_MATRIX.yml', 'comprehension': 'COMPREHENSION_STUDY_PLAN.yml', 'glossary': 'GLOSSARY_USABILITY_LEDGER.yml', 'keyboard': 'KEYBOARD_NAVIGATION_CHECK.yml', 'translation': 'TRANSLATION_READINESS_LEDGER.yml', 'exportreadiness': 'EXPORT_READINESS_LEDGER.yml', 'discovery': 'DISCOVERY_BACKLOG.yml', 'cubeartifacts': 'CUBE/observations/artifacts.yml', 'cubeclaims': 'CUBE/observations/claims.yml', 'cubedebts': 'CUBE/observations/debts.yml', 'cubecontrols': 'CUBE/observations/controls.yml', 'cubesources': 'CUBE/observations/sources.yml', 'cubeaccess': 'CUBE/observations/access.yml', 'cubeconcepts': 'CUBE/observations/concepts.yml', 'sourcecrosswalknormalized': 'SOURCE_CROSSWALK_NORMALIZED.yml', 'sourcecitationindex': 'SOURCE_CITATION_INDEX.yml', 'sourcefamilymap': 'SOURCE_FAMILY_MAP.yml', 'sourcerelationmap': 'SOURCE_RELATION_MAP.yml', 'sourceauditledger': 'SOURCE_AUDIT_LEDGER.yml', 'sourcerelations': 'CUBE/observations/source_relations.yml', 'sourceaudit': 'CUBE/observations/source_audit.yml'}

def render_query(root, q):
    root=Path(root); cube=load(root/'CUBE_INDEX.yml'); version=current_version(root); out=[]
    if q=='observations':
        for o in cube.get('current_release_observations',[]): out.append(f"{o.get('observation_id')} | {o.get('family')} | {o.get('dimensions',{}).get('status')}")
    elif q=='schema':
        for o in cube.get('current_release_observations',[]):
            m=o.get('measures',{}); out.append(f"{o.get('dimensions',{}).get('artifact')}: expected={m.get('required_fields_expected')} present={m.get('required_fields_present')} missing={m.get('required_fields_missing')}")
    elif q=='control':
        cs=load(root/'CONTROL_STACK.yml'); out.append(f"final_step: {cs.get('final_step')}")
        for s in cs.get('steps',[]):
            if s.get('step',0)>=168: out.append(f"{s.get('step')}: {s.get('file')} -> {s.get('successor_step')}")
    elif q=='sources':
        seen=[]
        for o in cube.get('current_release_observations',[]):
            for s in o.get('source_artifacts',[]) or []:
                if s not in seen: seen.append(s)
        for p in sorted(list(root.glob('*.yml'))+[root/'README.md',root/'ARCHIVE_INDEX.md']+list((root/'RUNBOOKS').glob('*.md'))+list((root/'tools').glob('*.py'))+list(root.glob('*.json'))+list((root/'CUBE').glob('*.yml'))+list((root/'CUBE'/'observations').glob('*.yml'))):
            if p.exists():
                rel=str(p.relative_to(root))
                if rel not in seen and rel!='MANIFEST.sha256': seen.append(rel)
        out.extend(seen)
    elif q=='debts':
        for p in current_records(root)+sorted(root.glob('*.yml')):
            d=load(p)
            for k,v in d.items():
                if k.startswith('open_') or k.endswith('_debt'): out.append(f"{p.name}::{k}: {v}")
    elif q=='forbidden':
        for p in sorted(root.glob('*.yml'))+current_records(root):
            d=load(p)
            if 'forbidden_claim_language' in d: out.append(f"{p.name}: {d['forbidden_claim_language']}")
            if p.name=='CLAIM_LANGUAGE_LEDGER.yml': out.append(ydump(d.get('forbidden_claim_clusters',[])))
            if p.name=='PUBLIC_RELEASE_ATTESTATION.yml': out.append(ydump(d.get('negative_assertions',[])))
    elif q=='capacity':
        d=load(root/'REGISTERS'/f'{version}-capacity-allocation.yml')
        for k in ['capacity_status','backlog_admission_class','work_in_progress_class','deferral_class','open_capacity_debt']: out.append(f"{k}: {d.get(k)}")
    elif q=='vocab':
        d=load(root/'STATUS_VOCABULARY.yml')
        for f in d.get('code_families',[]): out.append(f"{f.get('family')}: {', '.join(list((f.get('codes') or {}).keys())[:25])}")
    elif q=='references':
        d=load(root/'REFERENCE_MAP.yml'); out.append('REFERENCE_MAP.yml'); out.append(f"missing_references: {d.get('summary',{}).get('missing_references',0)}")
        for r in d.get('references',[])[:200]: out.append(f"{r.get('surface')} -> {r.get('target')} [{r.get('status')}]")
    elif q in ROOT_QUERY_FILES:
        data=load(root/ROOT_QUERY_FILES[q])
        # Large observation surfaces are rendered as compact line summaries so query regression remains usable.
        list_key=None
        for k,v in data.items():
            if isinstance(v, list):
                list_key=k; break
        if list_key and len(data.get(list_key, [])) > 100:
            out.append(str(ROOT_QUERY_FILES[q]))
            for k,v in data.items():
                if k==list_key: continue
                if isinstance(v, (str,int,float,bool)) or v is None:
                    out.append(f"{k}: {v}")
                elif isinstance(v, list) and k != list_key and len(v) <= 50:
                    out.append(f"{k}: {', '.join(map(str, v))}")
            rows=data.get(list_key, [])
            out.append(f"{list_key}: {len(rows)}")
            fields=['claim_observation_id','claim_relation_observation_id','claim_audit_observation_id','artifact_observation_id','debt_observation_id','source_observation_id','source_relation_observation_id','source_audit_observation_id','concept_observation_id','concept_relation_observation_id','cube_audit_observation_id','artifact','source_artifact','source_artifacts','claim_polarity','origin','claim_text','debt_text','source_id','name','concept_id','relation_type','target_concept_id','dataset_id','audit_subject','finding','status','family','source_family','freshness_state','debt_family','blocking_status','closure_status','query_boundary','priority_class','lifecycle_status','blocked_claim_class','audit_subject','finding','claim_boundary']
            for r in rows:
                if isinstance(r, dict):
                    bits=[]
                    for f in fields:
                        if f in r:
                            val=r[f]
                            if isinstance(val, list): val=', '.join(map(str,val[:8]))
                            bits.append(f"{f}={str(val)[:240]}")
                    out.append(' | '.join(bits) if bits else str(r)[:500])
                else:
                    out.append(str(r)[:500])
        else:
            out.append(ydump(data))
    else:
        raise KeyError(q)
    return '\n'.join(out)+'\n'

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>2 else Path('.')
    q=sys.argv[2] if len(sys.argv)>2 else (sys.argv[1] if len(sys.argv)>1 else 'observations')
    try: sys.stdout.write(render_query(root,q))
    except KeyError:
        print('known queries: '+' '.join(['observations','schema','control','sources','debts','forbidden','capacity','vocab','references']+sorted(ROOT_QUERY_FILES)), file=sys.stderr); return 2
    return 0
if __name__=='__main__': raise SystemExit(main())
