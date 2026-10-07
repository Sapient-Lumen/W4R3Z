#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['readiness_id','area','check','expected','observed','severity','status','next_action']


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))


def add(rows, area, check, expected, observed, severity, status, next_action):
    rows.append({'readiness_id':f'ptr_{len(rows)+1:04d}','area':area,'check':check,'expected':str(expected),'observed':str(observed),'severity':severity,'status':status,'next_action':next_action})


def exists(root: Path, rel: str) -> bool:
    return (root/rel).exists()


def zero_high(root: Path, rel: str) -> tuple[bool, int]:
    rows=read_csv(root/rel)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    return (bool(rows) and not bad, len(bad))


def run(root: Path):
    rows=[]
    manifest=read_json(root/'manifest.json') or {}
    export=manifest.get('export_name_without_zip','')
    rev=manifest.get('revision','')

    add(rows,'identity','root_export_alignment',export,root.name,'high','pass' if export and root.name==export else 'fail','Keep manifest/root/ZIP member namespace aligned before transfer.')

    required_fixity=['SHA256SUMS.txt','SHA256SUMS.txt.sig','RELEASE-PUBLIC-KEY.asc','SIGNATURE-STATUS-current.md','META/Archive-Member-Manifest-current.csv','META/Archive-Build-Manifest-current.csv','META/Archive-Roundtrip-Audit-current.csv']
    missing=[rel for rel in required_fixity if not exists(root,rel)]
    add(rows,'fixity','checksum_signature_archive_surfaces_present','all required fixity/signature/archive surfaces present','missing: '+ '|'.join(missing) if missing else 'all present','high','pass' if not missing else 'fail','Regenerate checksum/signature/archive surfaces after report closure.')
    amm_ok, amm_bad = zero_high(root,'META/Archive-Member-Manifest-current.csv')
    add(rows,'fixity','archive_member_manifest_zero_high','zero high/fail rows',amm_bad,'high','pass' if amm_ok else 'fail','Archive member manifest should remain the internal file-level transfer inventory.')

    crate=read_json(root/'ro-crate-metadata.json')
    graph=crate.get('@graph',[]) if isinstance(crate, dict) else []
    ids={node.get('@id') for node in graph if isinstance(node, dict)}
    required_ids={'./','manifest.json','Candidate-Ledger-current.csv','Claim-Ledger-current.csv','Source-Registry-current.csv','Evidence-Debt-current.csv','Refresh-Index-current.csv','META/Current-Surface-Freshness-Audit-current.csv','META/Preservation-Transfer-Readiness-current.csv'}
    add(rows,'ro_crate','ro_crate_metadata_present_and_core_entities_listed',sorted(required_ids),'missing: '+ '|'.join(sorted(required_ids-ids)) if crate else 'missing ro-crate-metadata.json','high','pass' if crate and required_ids.issubset(ids) else 'fail','Keep RO-Crate metadata as transfer metadata only; it does not open public URLs or source URLs.')

    helper='tools/make_bagit_transfer_copy.py'
    bag_root_files=['bagit.txt','bag-info.txt','manifest-sha256.txt','tagmanifest-sha256.txt']
    bag_in_root=[rel for rel in bag_root_files if exists(root,rel)]
    helper_ok=exists(root,helper) and not bag_in_root
    add(rows,'bagit','external_bagit_wrapper_ready_without_restructuring_root','helper present and no in-place BagIt tag files in package root',f'helper={exists(root,helper)} in_place_tags={"|".join(bag_in_root) if bag_in_root else "none"}','high','pass' if helper_ok else 'fail','Use the helper to create an external BagIt transfer copy when needed; do not move this datacube under data/ inside the linked ZIP.')

    premis_required={
        'objects':'manifest.json|META/Archive-Member-Manifest-current.csv|SHA256SUMS.txt',
        'events':'BUILD-PROVENANCE-current.json|META/Version-Lineage-Audit-current.csv|META/Package-Delta-Manifest-current.csv|META/Release-Gate-Attestation-current.csv',
        'rights':'RIGHTS-AND-USE-LIMITS.md|GOVERNANCE/Handoff-Use-Limits-and-Reviewer-Notice-current.md|SCHEMA/Package-Release-Contract-current.json',
        'agents':'BUILD-PROVENANCE-current.json|GOVERNANCE/Review-Role-and-Handoff-Boundaries-current.md|tools/README.md',
    }
    for area, rels in premis_required.items():
        rel_list=rels.split('|')
        missing=[rel for rel in rel_list if not exists(root,rel)]
        add(rows,'premis_lite',f'premis_{area}_evidence_surfaces_present',rels,'missing: '+ '|'.join(missing) if missing else 'all present','high','pass' if not missing else 'fail','This is a PREMIS-lite evidence crosswalk, not a full PREMIS XML serialization.')

    prov_required=['META/Generated-Artifact-Provenance-current.csv','META/Package-Dependency-Graph-current.csv','META/Regeneration-Sequence-Plan-current.csv']
    missing=[rel for rel in prov_required if not exists(root,rel)]
    add(rows,'prov','package_provenance_graph_surfaces_present','generated artifacts + dependency graph + regeneration order','missing: '+ '|'.join(missing) if missing else 'all present','high','pass' if not missing else 'fail','Retain generated-artifact provenance as the package-local PROV-style lineage surface.')

    fresh_ok, fresh_bad=zero_high(root,'META/Current-Surface-Freshness-Audit-current.csv')
    add(rows,'risk_gate','current_surface_freshness_zero_high','zero high failures',fresh_bad,'high','pass' if fresh_ok else 'fail','Freshness is now a transfer-readiness condition, not a reviewer memory task.')
    lint_ok, lint_bad=zero_high(root,'META/Public-Release-Lint-current.csv')
    add(rows,'public_boundary','public_release_lint_zero_high','zero high failures',lint_bad,'high','pass' if lint_ok else 'fail','Closed public layer remains binding during preservation transfer.')
    add(rows,'status','preservation_transfer_profile_scope',f'{rev} closed datacube transfer metadata','not public release / not source URL publication','info','pass','Use these surfaces to hand off the package safely without expanding public exposure.')
    return rows


def write_reports(root: Path, rows):
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Preservation-Transfer-Readiness-current.csv',
        fields=FIELDS,
        rows=rows,
        title='Preservation Transfer Readiness',
        generated_by='tools/preservation_transfer_readiness.py',
        columns=['area','check','severity','status','expected','observed','next_action'],
        intro_lines=[
            f"High failures: {sum(1 for r in rows if r.get('severity')=='high' and r.get('status')!='pass')}",
            'This report turns preservation standards into package-local checks without converting the linked ZIP into a public release or in-place BagIt bag.',
        ],
    )


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} preservation transfer readiness rows={len(rows)} high_fail={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r['area']} {r['check']}: {r['observed']}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__ == '__main__': main()
