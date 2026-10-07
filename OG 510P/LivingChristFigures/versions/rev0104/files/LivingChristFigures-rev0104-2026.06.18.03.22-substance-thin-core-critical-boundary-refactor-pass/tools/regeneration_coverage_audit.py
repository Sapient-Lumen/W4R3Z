#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, importlib.util, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import current_csv_surfaces, package_rel, read_csv_rows, write_csv_json_md_report

FIELDS = [
    'coverage_id','surface_path','surface_kind','coverage_class','generator_or_owner',
    'in_generated_provenance','in_regeneration_plan','in_report_contract','severity','status','note'
]

SELF_REFERENTIAL_LATE_CLOSURE = {
    'META/Generated-Artifact-Provenance-current.csv',
    'META/Handoff-Review-Digest-current.csv',
    'META/Release-Evidence-Closure-current.csv',
    'META/Release-Gate-Attestation-current.csv',
    'SCHEMA/Schema-Validation-Report-current.csv',
}

CORE_STATIC_LEDGER_OR_SEED = {
    'Candidate-Ledger-current.csv',
    'Claim-Ledger-current.csv',
    'Source-Registry-current.csv',
    'Evidence-Debt-current.csv',
    'Office-Card-Index-current.csv',
    'Refresh-Index-current.csv',
    'Longform-Registry-current.csv',
    'META/Boundary-Rule-Coverage-current.csv',
    'META/Candidate-Discovery-Log-current.csv',
    'META/Claim-Type-Taxonomy-current.csv',
    'META/Clean-Extract-Archive-QA-current.csv',
    'META/Cloudtainer-Deep-Read-Audit-current.csv',
    'META/Evidence-Debt-Dashboard-current.csv',
    'META/Manifest-Audit-current.csv',
    'META/Negative-Case-Ledger-current.csv',
    'META/Online-Research-Intake-current.csv',
    'META/Operator-Dissent-Ledger-current.csv',
    'META/Operator-Update-Audit-current.csv',
    'META/Path-Rename-Ledger-current.csv',
    'META/Public-Claim-Quarantine-current.csv',
    'META/Public-Claim-Release-Ledger-current.csv',
    'META/Refresh-Sprint-Decision-Matrix-current.csv',
    'META/Source-Freshness-and-Provenance-Audit-current.csv',
    'META/Source-Promotion-Decision-Ledger-current.csv',
    'META/Source-Promotion-Transaction-Audit-current.csv',
    'GOVERNANCE/CARE-OCAP-UNDRIP-Crosswalk-current.csv',
    'GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv',
    'GOVERNANCE/Governance-Decision-Ledger-current.csv',
}

SCHEMA_STATIC_PATTERNS = (
    '-Fields-current.csv',
    'Controlled-Vocabulary-current.csv',
    'Public-Allowed-Claim-Shapes-current.csv',
    'Public-Link-Policy-current.csv',
    'Harm-Proximity-Controlled-Vocabulary-current.csv',
    'Normalized-Code-Overlay-current.csv',
)



def load_artifact_specs(root: Path) -> dict[str, str]:
    tool = root / 'tools/generated_artifact_provenance.py'
    out: dict[str, str] = {}
    try:
        spec = importlib.util.spec_from_file_location('gap_for_regen_coverage', tool)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        for artifact, generator, _inputs in getattr(mod, 'ARTIFACTS', []):
            out[str(artifact)] = str(generator)
    except Exception:
        for row in read_csv_rows(root / 'META/Generated-Artifact-Provenance-current.csv'):
            if row.get('artifact_path'):
                out[row.get('artifact_path','')] = row.get('generator','')
    return out


def regeneration_outputs(root: Path) -> set[str]:
    out: set[str] = set()
    for row in read_csv_rows(root / 'META/Regeneration-Sequence-Plan-current.csv'):
        for rel in (row.get('declared_outputs','') or '').split('|'):
            if rel:
                out.add(rel)
    return out


def report_contracts(root: Path) -> set[str]:
    out: set[str] = set()
    for row in read_csv_rows(root / 'META/Report-Contract-Registry-current.csv'):
        rel = row.get('csv_path') or row.get('surface_path')
        if rel:
            out.add(rel)
    return out


def surface_kind(rel: str) -> str:
    if rel.startswith('SCHEMA/'):
        return 'schema_current_csv'
    if rel.startswith('META/'):
        return 'meta_current_csv'
    if rel.startswith('GOVERNANCE/'):
        return 'governance_current_csv'
    if rel.startswith('PUBLIC/'):
        return 'public_current_csv'
    return 'root_current_csv'


def class_for(rel: str, genmap: dict[str,str], regen: set[str]) -> tuple[str,str,str,str]:
    """Return class, owner, severity, status."""
    if rel in genmap:
        if rel in regen:
            return 'tracked_generated_surface', genmap[rel], 'info', 'pass'
        return 'generated_but_missing_regeneration_plan', genmap[rel], 'high', 'fail'
    if rel in SELF_REFERENTIAL_LATE_CLOSURE:
        return 'self_referential_late_closure_surface', 'late_closure_bootstrap', 'info', 'pass'
    if rel in CORE_STATIC_LEDGER_OR_SEED:
        return 'curated_seed_or_core_ledger', 'manual_curated_or_ledger_contract', 'info', 'pass'
    if rel.startswith('SCHEMA/') and rel.endswith(SCHEMA_STATIC_PATTERNS):
        return 'schema_seed_or_field_contract', 'schema_layer_static_contract', 'info', 'pass'
    if rel.startswith('GOVERNANCE/'):
        return 'governance_curated_surface', 'governance_layer', 'info', 'pass'
    if rel.startswith('PUBLIC/') and rel == 'PUBLIC/Candidate-Index-public.csv':
        return 'public_generated_index', 'tools/render_public_safe_index.py', 'info', 'pass'
    return 'unmanaged_current_surface', '', 'high', 'fail'


def add(rows, rel, kind, cls, owner, prov, regen, contract, severity, status, note):
    rows.append({
        'coverage_id': f'regen_cov_{len(rows)+1:04d}',
        'surface_path': rel,
        'surface_kind': kind,
        'coverage_class': cls,
        'generator_or_owner': owner,
        'in_generated_provenance': 'yes' if prov else 'no',
        'in_regeneration_plan': 'yes' if regen else 'no',
        'in_report_contract': 'yes' if contract else 'no',
        'severity': severity,
        'status': status,
        'note': note,
    })


def run(root: Path):
    rows=[]
    genmap = load_artifact_specs(root)
    regen = regeneration_outputs(root)
    contracts = report_contracts(root)
    current_csvs = set(current_csv_surfaces(root))

    for rel in sorted(current_csvs):
        cls, owner, sev, status = class_for(rel, genmap, regen)
        in_contract = rel in contracts
        # Field schema surfaces are contract material themselves and are not required to be report-contract rows.
        contract_ok = in_contract or (rel.startswith('SCHEMA/') and rel.endswith(SCHEMA_STATIC_PATTERNS))
        if status == 'pass' and not contract_ok:
            sev, status = 'high', 'fail'
            note = 'current CSV is classified but absent from report contract registry or schema-static exception'
        elif status == 'pass' and cls == 'tracked_generated_surface':
            note = 'generated surface is tracked in provenance, included in regeneration plan, and contract-covered where required'
        elif status == 'pass' and cls == 'self_referential_late_closure_surface':
            note = 'late-closure surface is deliberately excluded from strict provenance fixed-point requirements and remains release-gated separately'
        elif status == 'pass':
            note = 'non-generated current surface has an explicit seed/schema/governance owner and contract coverage where required'
        else:
            note = 'current CSV lacks a safe owner/regeneration class or is missing from the regeneration plan'
        add(rows, rel, surface_kind(rel), cls, owner, rel in genmap, rel in regen, in_contract, sev, status, note)

    # Every primary generated artifact should also be present as a declared regeneration output; this catches drift in ARTIFACTS vs plan.
    for rel, owner in sorted(genmap.items()):
        if rel.endswith('.csv') and rel not in current_csvs:
            present = (root / rel).exists()
            ok = present and rel in regen
            add(rows, rel, 'generated_primary_artifact', 'tracked_generated_noncurrent_csv', owner, True, rel in regen, rel in contracts, 'info' if ok else 'high', 'pass' if ok else 'fail', 'generated primary CSV is not a *-current.csv report, but it is present and declared by the regeneration plan' if ok else 'generated provenance points to a CSV artifact that is missing or absent from the regeneration plan')
        elif rel not in regen:
            add(rows, rel, 'generated_primary_artifact', 'generated_artifact_missing_regeneration_step', owner, True, False, rel in contracts, 'high', 'fail', 'generated provenance artifact is not declared by the regeneration sequence plan')

    # Regeneration outputs that are current CSVs but not otherwise classified are high risk.
    for rel in sorted(regen):
        if rel.endswith('-current.csv') and rel not in current_csvs:
            add(rows, rel, 'regeneration_output', 'regeneration_output_missing_from_package', '', rel in genmap, True, rel in contracts, 'high', 'fail', 'regeneration plan declares a current CSV output that is absent from the package')

    bad = [r for r in rows if r['severity']=='high' and r['status']!='pass']
    add(rows, '.', 'package_summary', 'regeneration_coverage_summary', 'tools/regeneration_coverage_audit.py', False, False, False, 'info', 'pass' if not bad else 'fail', f'current_csv_surfaces={len(current_csvs)} generated_artifacts={len(genmap)} regeneration_outputs={len(regen)} report_contracts={len(contracts)} high_failures={len(bad)}')
    return rows


def write_reports(root: Path, rows):
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Regeneration-Coverage-Audit-current.csv',
        fields=FIELDS,
        rows=rows,
        title='Regeneration Coverage Audit',
        generated_by='tools/regeneration_coverage_audit.py',
        columns=['surface_path','coverage_class','generator_or_owner','in_generated_provenance','in_regeneration_plan','in_report_contract','severity','status','note'],
        intro_lines=[
            f'High failures: {sum(1 for r in rows if r.get("severity")=="high" and r.get("status")!="pass")}',
            'This audit prevents unowned current report surfaces from accumulating. It distinguishes generated/provenance surfaces, curated seed ledgers, schema contracts, governance ledgers, public generated index rows, and deliberate late-closure proof loops.',
        ],
        max_md_rows=360,
    )


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} regeneration coverage rows={len(rows)} high_fail={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r['surface_path']} {r['coverage_class']}: {r['note']}")
    if args.fail_on_high and bad: sys.exit(1)

if __name__ == '__main__': main()
