#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, re, hashlib, collections

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def dump(obj):
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=110).rstrip()

def norm(text):
    return re.sub(r'\s+', ' ', str(text).strip().lower())

def classify(text):
    t = norm(text)
    if any(w in t for w in ['accessibility','wcag','screen-reader','assistive','keyboard','disabled','plain-language','comprehension','reader','translation','localization']): return 'accessibility_or_comprehension_evidence_absent'
    if any(w in t for w in ['external','independent','audit','legal','compliance','certification','reviewer','red team']): return 'external_review_absent'
    if any(w in t for w in ['public support','helpdesk','public service','sla','slo','support queue']): return 'public_service_absent'
    if any(w in t for w in ['rdf','shacl','spdx','cyclonedx','oscal','slsa','export','endpoint','json-ld','ro-crate']): return 'publication_export_absent'
    if any(w in t for w in ['source','freshness','watch','url','bibliography','citation']): return 'source_watch_absent'
    if any(w in t for w in ['schema','typed','json schema','constraint','enum']): return 'schema_strength_absent'
    if any(w in t for w in ['semantic','philosophical','concept','hard case','ontology','truth']): return 'semantic_correctness_unproven'
    if any(w in t for w in ['owner','maintainer','assigned','capacity','staffing']): return 'ownership_or_capacity_absent'
    if any(w in t for w in ['closure','remediation','verified','corrective','redress']): return 'closure_evidence_absent'
    return 'general_local_only_debt'

def blocked_claim(family, text):
    table = {
      'accessibility_or_comprehension_evidence_absent':'accessibility/comprehension conformance claim',
      'external_review_absent':'external audit/review claim',
      'public_service_absent':'public support/service readiness claim',
      'publication_export_absent':'machine-readable export/publication claim',
      'source_watch_absent':'source-currentness/freshness claim',
      'schema_strength_absent':'strong machine-validation claim',
      'semantic_correctness_unproven':'semantic correctness/philosophical completeness claim',
      'ownership_or_capacity_absent':'assigned-owner/capacity-backed remediation claim',
      'closure_evidence_absent':'debt closure/remediation-complete claim',
      'general_local_only_debt':'stronger public/conformance upgrade claim'
    }
    return table.get(family,'stronger public/conformance upgrade claim')

def severity(family, text):
    t=norm(text)
    if family in {'accessibility_or_comprehension_evidence_absent','external_review_absent','source_watch_absent','public_service_absent','closure_evidence_absent'}: return 'high_when_claimed_else_visible'
    if family in {'publication_export_absent','schema_strength_absent','semantic_correctness_unproven','ownership_or_capacity_absent'}: return 'medium_when_claimed_else_visible'
    if any(w in t for w in ['no ', 'absent', 'missing', 'unassigned', 'not ']): return 'medium_when_claimed_else_visible'
    return 'advisory_visible'

def priority(sev, family):
    if sev.startswith('high'): return 'P1_blocks_upgrade_claim'
    if family in {'schema_strength_absent','publication_export_absent','semantic_correctness_unproven'}: return 'P2_blocks_strong_conformance_language'
    return 'P3_visible_backlog'

def lifecycle_status(text):
    t=norm(text)
    if any(w in t for w in ['closed', 'completed', 'verified']) and 'no ' not in t: return 'claimed_closed_requires_evidence_review'
    if any(w in t for w in ['planned', 'candidate', 'future']): return 'planned_or_candidate'
    return 'open_unassigned'

def closure_evidence_type(family):
    return {
      'accessibility_or_comprehension_evidence_absent':'test report, participant/proxy evidence, assistive-tech matrix, and bounded accessibility claim',
      'external_review_absent':'named independent review artifact, reviewer scope, findings, and closure decision',
      'public_service_absent':'support process, service objective, intake channel, owner, and evidence of operation',
      'publication_export_absent':'generated export, validator transcript, scope boundary, and no-overclaim note',
      'source_watch_absent':'source-watch policy, last-checked ledger, diff evidence, and freshness exception handling',
      'schema_strength_absent':'typed schema or shape validation transcript plus failing/passing fixtures',
      'semantic_correctness_unproven':'hard-case analysis, rival comparison, negative controls, and review boundary',
      'ownership_or_capacity_absent':'named owner or explicit declined-owner decision plus capacity review',
      'closure_evidence_absent':'closure verifier, evidence artifact, and re-open trigger',
      'general_local_only_debt':'specific evidence artifact matching the claim being upgraded'
    }.get(family, 'specific evidence artifact matching the claim being upgraded')

def iter_debt_fields(obj, prefix=''):
    if isinstance(obj, dict):
        for k,v in obj.items():
            path=f'{prefix}.{k}' if prefix else str(k)
            if k.startswith('open_') or k.endswith('_debt'):
                yield path, v
            # avoid exploding huge already-generated debt item lists in DEBT_TAXONOMY
            if k in {'debt_items','debt_observations','claim_observations','source_observations'}:
                continue
            yield from iter_debt_fields(v, path)
    elif isinstance(obj, list):
        for i,v in enumerate(obj):
            yield from iter_debt_fields(v, f'{prefix}[{i}]')

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    version = (root/'VERSION').read_text(encoding='utf-8').strip()
    package = load(root/'CURRENT_RELEASE.yml').get('package')
    sources = list(sorted(root.glob('*.yml'))) + list(sorted((root/'REGISTERS').glob(f'{version}-*.yml')))
    raw=[]
    for p in sources:
        if p.name == 'MANIFEST.sha256': continue
        data = load(p)
        if not isinstance(data, dict): continue
        for field, v in iter_debt_fields(data):
            vals = v if isinstance(v, list) else [v]
            for item in vals:
                if isinstance(item, dict): item = item.get('debt_text') or item.get('text') or str(item)
                text=str(item).strip()
                if not text or text in ('None','[]'): continue
                raw.append((str(p.relative_to(root)), field, text))
    recurrence=collections.Counter(norm(t) for _,_,t in raw)
    rows=[]
    for i,(artifact,field,text) in enumerate(raw,1):
        fam=classify(text); sev=severity(fam,text); pri=priority(sev,fam); life=lifecycle_status(text)
        key=hashlib.sha1(norm(text).encode()).hexdigest()[:12]
        rows.append({
            'debt_observation_id': f'DEBT-{version}-{i:04d}',
            'debt_key': f'DBTKEY-{key}',
            'source_artifact': artifact,
            'field': field,
            'debt_text': text,
            'debt_family': fam,
            'severity': sev,
            'priority_class': pri,
            'blocking_status': 'blocks_corresponding_upgrade_claim_until_closure_evidence_exists',
            'blocked_claim_class': blocked_claim(fam,text),
            'owner_status': 'unassigned_or_local_maintainer_only',
            'capacity_status': 'not_scheduled_unless_separately_assigned',
            'lifecycle_status': life,
            'closure_status': 'open' if life!='claimed_closed_requires_evidence_review' else 'requires_evidence_review',
            'closure_evidence_required': closure_evidence_type(fam),
            'recurrence_count': recurrence[norm(text)],
            'first_seen_revision': version,
            'last_seen_revision': version,
            'accepted_risk_status': 'not_accepted_for_public_or_conformance_upgrade',
            'public_use_effect': 'must remain visible in public-use and derivative-use warnings if relevant',
            'claim_boundary': 'local debt observation only; not closure, owner assignment, remediation, or external verification'
        })
    out = {'debt_observations_version': f'{version}-debt-observations-v2', 'archive_version': version, 'package': package, 'generated_by': 'tools/generate_debt_observations.py', 'observation_scope': 'top-level YAML open-debt fields plus current register open-debt fields; generated local structure only', 'debt_observations': rows}
    print(dump(out))
    return 0
if __name__ == '__main__': raise SystemExit(main())
