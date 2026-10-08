#!/usr/bin/env python3
from pathlib import Path
import sys, re, yaml
PATH_RE=re.compile(r'(?<![A-Za-z0-9_./-])((?:docs|REGISTERS|RUNBOOKS|tools)/[A-Za-z0-9_.*/()\-]+\.(?:md|yml|py|sha256)|[A-Z][A-Z0-9_/-]*\.(?:yml|md|sha256)|VERSION)')
INTENTIONAL={'REGISTERS/NO_SUCH_ABUSE_EVIDENCE.yml','tools/MISSING_SECURITY_HARDENING_SENTINEL.py','REGISTERS/NO_SUCH_TRUST_BOUNDARY_EVIDENCE.yml','REGISTERS/NO_SUCH_STAKEHOLDER_EVIDENCE.yml','REGISTERS/NO_SUCH_HARM_EVIDENCE.yml','REGISTERS/NO_SUCH_REDRESS_EVIDENCE.yml','REGISTERS/NO_SUCH_APPEAL_EVIDENCE.yml','REGISTERS/NO_SUCH_CONTESTATION_EVIDENCE.yml','REGISTERS/NO_SUCH_ACCEPTANCE_EVIDENCE.yml','REGISTERS/NO_SUCH_CUBE_SOURCE.yml','tools/MISSING_REMEDIATION_SENTINEL.py','REGISTERS/NO_SUCH_PUBLIC_ATTESTATION_EVIDENCE.yml','REGISTERS/NO_SUCH_ACCOUNTABILITY_REVIEW_EVIDENCE.yml','REGISTERS/NO_SUCH_EVIDENCE_PACKET.yml','REGISTERS/NO_SUCH_GATE_REPORT.yml','NO_SUCH_BUILD_INPUT.yml','REGISTERS/NO_SUCH_AUDIT_SAMPLE.yml','REGISTERS/NO_SUCH_DELEGATION_EVIDENCE.yml','REGISTERS/NO_SUCH_CORRECTIVE_EVIDENCE.yml','tools/MISSING_OBSERVABILITY_SENTINEL.py','tools/MISSING_FIXTURE_SENTINEL.py','REGISTERS/NO_SUCH_PRIVACY_MINIMIZATION.yml','REGISTERS/NO_SUCH_SENSITIVE_CLASSIFICATION.yml'}
def scan(root,surfaces):
    refs=[]; missing=[]; excluded=[]
    for rel in surfaces:
        if rel == 'REFERENCE_MAP.yml': continue
        p=root/rel
        if not p.exists(): missing.append({'surface':rel,'target':rel,'status':'surface_missing'}); continue
        text=p.read_text(encoding='utf-8',errors='ignore')
        for m in PATH_RE.finditer(text):
            target=m.group(1).rstrip('.,:)')
            if '*' in target: excluded.append({'surface':rel,'target':target,'reason':'wildcard declared surface'}); continue
            if rel=='FIXTURE_CORPUS.yml' and target in INTENTIONAL: excluded.append({'surface':rel,'target':target,'reason':'intentional negative-fixture target'}); continue
            ok=(root/target).exists(); refs.append({'surface':rel,'target':target,'status':'ok' if ok else 'missing'})
            if not ok: missing.append({'surface':rel,'target':target,'status':'missing'})
    return refs,missing,excluded

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    version=(root/'VERSION').read_text(encoding='utf-8').strip()
    root_surfaces=['README.md','ARCHIVE_INDEX.md','docs/00-start-here.md']+[p.name for p in sorted(root.glob('*.yml'))]
    surfaces=list(dict.fromkeys(root_surfaces+[str(p.relative_to(root)) for p in sorted((root/'REGISTERS').glob(f'{version}-*.yml'))]))
    refs,missing,excluded=scan(root,surfaces)
    report={'reference_map_version':f'{version}-reference-map-v9','archive_version':version,'checked_surfaces':surfaces,'summary':{'checked_surfaces':len(surfaces),'references_checked':len(refs),'missing_references':len(missing),'excluded_patterns':len(excluded)},'references':refs,'missing_references':missing,'excluded_patterns':excluded}
    print(yaml.safe_dump(report,sort_keys=False,allow_unicode=True).rstrip()); return 1 if missing else 0
if __name__=='__main__': raise SystemExit(main())
