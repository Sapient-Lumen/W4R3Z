#!/usr/bin/env python3
from __future__ import annotations
"""Semantic guardrail for the public-safe candidate index.

The parity audit proves that CSV/JSON/Markdown surfaces agree. This audit proves
that the public shape still means what it claims: governance-quarantined rows may
share a non-expansion tier, but they must not inherit the Bridget Tolley/MMIWG
Canada prose template unless they are actually in that domain.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report
from public_template_policy import CANDIDATE_TEMPLATE_OVERRIDES, public_boundary_overrides

FIELDS = ['finding_id','severity','status','check','candidate_id','expected','observed','detail','remediation']

CRITICAL_EXPECTATIONS = {
    'cand_bridget_tolley_fsis_mmiwg_canada': {
        'template': 'mmiwg_family_led_boundary',
        'location_required': ['Canada'],
        'location_forbidden': [],
        'note_required': ['MMIWG'],
        'note_forbidden': [],
    },
    'cand_abuelas_de_plaza_de_mayo_identity_restitution': {
        'template': 'identity_restitution_no_intake',
        'location_required': ['Argentina'],
        'location_forbidden': ['Canada', 'Indigenous-led', 'MMIWG', 'red-dress', 'Red Dress'],
        'note_required': ['Identity-restitution', 'DNA/testing intake guide'],
        'note_forbidden': ['MMIWG', 'red-dress', 'Red Dress'],
    },
    'cand_las_patronas_veracruz_migrant_train_food_water': {
        'template': 'migrant_threshold_no_route_contact',
        'location_required': ['Veracruz', 'Mexico'],
        'location_forbidden': ['Canada', 'Indigenous-led', 'MMIWG', 'red-dress', 'Red Dress'],
        'note_required': ['Migrant-threshold', 'route'],
        'note_forbidden': ['MMIWG', 'red-dress', 'Red Dress'],
    },
    'cand_eaaf_forensic_return_of_names_and_remains': {
        'template': 'forensic_return_no_case_dna',
        'location_required': ['Argentina'],
        'location_forbidden': ['Canada', 'Indigenous-led', 'MMIWG', 'red-dress', 'Red Dress'],
        'note_required': ['Forensic-return', 'DNA/sample route'],
        'note_forbidden': ['MMIWG', 'red-dress', 'Red Dress'],
    },
    'cand_mothers_srebrenica_zepa_truth_justice_remembrance': {
        'template': 'genocide_memory_no_testimony_case_map',
        'location_required': ['Bosnia', 'Srebrenica'],
        'location_forbidden': ['Canada', 'Indigenous-led', 'MMIWG', 'red-dress', 'Red Dress'],
        'note_required': ['Genocide-memory', 'testimony'],
        'note_forbidden': ['MMIWG', 'red-dress', 'Red Dress'],
    },
}

MMIWG_DOMAIN_RE = re.compile(r'(?i)\b(MMIWG|MMIWG2S|Families of Sisters in Spirit|Sisters in Spirit|Bridget Tolley|Red Dress)\b')
NON_MMIWG_FORBIDDEN_RE = re.compile(r'(?i)\b(Canada; translocal Indigenous-led|Indigenous-led family/search|MMIWG2S|red-dress|Red Dress)\b')

EXCLUSIVE_TEMPLATE_ALLOWED_CANDIDATES = {
    'mmiwg_family_led_boundary': {'cand_bridget_tolley_fsis_mmiwg_canada'},
    'identity_restitution_no_intake': {'cand_abuelas_de_plaza_de_mayo_identity_restitution'},
    'migrant_threshold_no_route_contact': {'cand_las_patronas_veracruz_migrant_train_food_water'},
    'forensic_return_no_case_dna': {'cand_eaaf_forensic_return_of_names_and_remains'},
    'genocide_memory_no_testimony_case_map': {'cand_mothers_srebrenica_zepa_truth_justice_remembrance'},
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def add(rows: list[dict[str, str]], severity: str, status: str, check: str, candidate_id: str, expected: str, observed: str, detail: str, remediation: str) -> None:
    rows.append({
        'finding_id': f'pisa_{len(rows)+1:04d}',
        'severity': severity,
        'status': status,
        'check': check,
        'candidate_id': candidate_id,
        'expected': expected,
        'observed': observed,
        'detail': detail,
        'remediation': remediation,
    })


def row_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r.get('candidate_id',''): r for r in rows if r.get('candidate_id','')}


def contains_all(text: str, needles: list[str]) -> bool:
    return all(n.lower() in (text or '').lower() for n in needles)


def contains_any(text: str, needles: list[str]) -> bool:
    low = (text or '').lower()
    return any(n.lower() in low for n in needles)


def run(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    candidate_rows = read_csv(root/'Candidate-Ledger-current.csv')
    eligibility_rows = read_csv(root/'META/Public-Export-Eligibility-current.csv')
    public_rows = read_csv(root/'PUBLIC/Candidate-Index-public.csv')
    if not candidate_rows:
        add(rows, 'high', 'fail', 'candidate_ledger_present', '.', 'Candidate-Ledger-current.csv rows', 'missing_or_empty', 'Candidate ledger is required for semantic context.', 'Restore or regenerate Candidate-Ledger-current.csv.')
    if not eligibility_rows:
        add(rows, 'high', 'fail', 'eligibility_present', '.', 'META/Public-Export-Eligibility-current.csv rows', 'missing_or_empty', 'Eligibility ledger is required for template parity.', 'Run tools/public_export_eligibility.py --write-report.')
    if not public_rows:
        add(rows, 'high', 'fail', 'public_index_present', '.', 'PUBLIC/Candidate-Index-public.csv rows', 'missing_or_empty', 'Public index is required for semantic guardrail checks.', 'Run tools/render_public_safe_index.py --write.')
    if rows:
        return rows

    candidates = row_by_id(candidate_rows)
    eligibility = row_by_id(eligibility_rows)
    public = row_by_id(public_rows)

    for cid, exp in CRITICAL_EXPECTATIONS.items():
        cand = candidates.get(cid, {})
        elig = eligibility.get(cid, {})
        pub = public.get(cid, {})
        if not cand or not elig or not pub:
            add(rows, 'high', 'fail', 'critical_candidate_present', cid, 'candidate, eligibility, and public rows all present', f'candidate={bool(cand)} eligibility={bool(elig)} public={bool(pub)}', 'Critical public-semantic sentinel row is missing from one or more surfaces.', 'Regenerate candidate ledger, eligibility, and public index before release.')
            continue
        expected_template = exp['template']
        if elig.get('public_shape_template') != expected_template:
            add(rows, 'high', 'fail', 'critical_template_expected', cid, expected_template, elig.get('public_shape_template',''), 'Eligibility assigned the wrong public template for a high-risk canary candidate.', 'Use tools/public_template_policy.py overrides; governance quarantine must not imply MMIWG.')
        else:
            add(rows, 'info', 'pass', 'critical_template_expected', cid, expected_template, elig.get('public_shape_template',''), 'Eligibility template matches candidate-domain expectation.', 'No action required.')
        if pub.get('public_shape_template') != expected_template:
            add(rows, 'high', 'fail', 'critical_template_rendered', cid, expected_template, pub.get('public_shape_template',''), 'Rendered public index template disagrees with expected candidate-domain template.', 'Regenerate PUBLIC/Candidate-Index-public.* from the eligibility ledger and shared template policy.')
        else:
            add(rows, 'info', 'pass', 'critical_template_rendered', cid, expected_template, pub.get('public_shape_template',''), 'Public index template matches candidate-domain expectation.', 'No action required.')
        loc = pub.get('location','')
        note = pub.get('public_use_note','')
        required_loc = exp.get('location_required', [])
        if not contains_any(loc, required_loc):
            add(rows, 'high', 'fail', 'critical_location_required', cid, 'one of: ' + '|'.join(required_loc), loc, 'Public location lost the broad correct domain context.', 'Apply template-specific public boundary overrides from tools/public_template_policy.py.')
        else:
            add(rows, 'info', 'pass', 'critical_location_required', cid, 'one of: ' + '|'.join(required_loc), loc, 'Public location retains the broad correct domain context.', 'No action required.')
        forbidden_loc = exp.get('location_forbidden', [])
        if contains_any(loc, forbidden_loc):
            add(rows, 'high', 'fail', 'critical_location_forbidden', cid, 'no: ' + '|'.join(forbidden_loc), loc, 'Public location inherited another domain/template language.', 'Remove hard-coded cross-domain location overrides; rerender with template-specific boundaries.')
        else:
            add(rows, 'info', 'pass', 'critical_location_forbidden', cid, 'no: ' + '|'.join(forbidden_loc), loc, 'Public location avoids forbidden inherited domain language.', 'No action required.')
        required_note = exp.get('note_required', [])
        if not contains_all(note, required_note):
            add(rows, 'medium', 'warn', 'critical_note_required', cid, 'all: ' + '|'.join(required_note), note, 'Public note does not name all expected boundary exclusions for this domain.', 'Review tools/public_template_policy.py template wording.')
        else:
            add(rows, 'info', 'pass', 'critical_note_required', cid, 'all: ' + '|'.join(required_note), note, 'Public note names the expected domain-specific exclusions.', 'No action required.')
        forbidden_note = exp.get('note_forbidden', [])
        if contains_any(note, forbidden_note):
            add(rows, 'high', 'fail', 'critical_note_forbidden', cid, 'no: ' + '|'.join(forbidden_note), note, 'Public note inherited another domain/template language.', 'Remove hard-coded cross-domain public-use note text and rerender.')
        else:
            add(rows, 'info', 'pass', 'critical_note_forbidden', cid, 'no: ' + '|'.join(forbidden_note), note, 'Public note avoids forbidden inherited domain language.', 'No action required.')

    for cid, elig in sorted(eligibility.items()):
        template = elig.get('public_shape_template','')
        cand = candidates.get(cid, {})
        text = ' '.join([cid, cand.get('name',''), cand.get('office',''), cand.get('work',''), cand.get('why',''), cand.get('sensitivity','')])
        if template == 'mmiwg_family_led_boundary' and not MMIWG_DOMAIN_RE.search(text):
            add(rows, 'high', 'fail', 'mmiwg_template_domain_exclusivity', cid, 'MMIWG/Bridget/FSIS domain text present', text[:240], 'A non-MMIWG candidate is using the MMIWG family-led boundary template.', 'Change template dispatch so only MMIWG-domain rows receive mmiwg_family_led_boundary.')

    for cid, pub in sorted(public.items()):
        template = pub.get('public_shape_template','')
        text = ' '.join([pub.get('location',''), pub.get('office',''), pub.get('public_use_note','')])
        if template != 'mmiwg_family_led_boundary' and NON_MMIWG_FORBIDDEN_RE.search(text):
            add(rows, 'high', 'fail', 'non_mmiwg_forbidden_language', cid, 'no Canada/MMIWG/red-dress inherited language for non-MMIWG templates', text[:240], 'A non-MMIWG public row still contains old MMIWG/Canada public shape language.', 'Rerender public index from tools/public_template_policy.py template-specific overrides.')
        allowed = EXCLUSIVE_TEMPLATE_ALLOWED_CANDIDATES.get(template)
        if allowed is not None and cid not in allowed:
            add(rows, 'high', 'fail', 'exclusive_template_candidate_scope', cid, 'allowed=' + '|'.join(sorted(allowed)), template, 'Domain-specific public templates with embedded jurisdiction/prose may only be used by their explicit candidate overrides.', 'Use a generic boundary template or add an explicit, reviewed candidate override.')

    expected_templates = set(CANDIDATE_TEMPLATE_OVERRIDES.values())
    rendered_templates = {r.get('public_shape_template','') for r in public_rows}
    missing_templates = sorted(expected_templates - rendered_templates)
    if missing_templates:
        add(rows, 'high', 'fail', 'critical_template_quorum', '.', 'templates present: ' + '|'.join(sorted(expected_templates)), 'missing: ' + '|'.join(missing_templates), 'The public index no longer exercises all high-risk template canaries.', 'Restore sentinel candidate rows or update this audit with equivalent canaries.')
    else:
        add(rows, 'info', 'pass', 'critical_template_quorum', '.', 'templates present: ' + '|'.join(sorted(expected_templates)), 'present: ' + '|'.join(sorted(expected_templates)), 'All high-risk public template canaries are represented in the rendered index.', 'No action required.')

    if not any(r.get('severity') == 'high' for r in rows):
        add(rows, 'info', 'pass', 'public_index_semantic_audit', '.', 'zero high findings', f'{len(public_rows)} public rows checked; {len(CRITICAL_EXPECTATIONS)} critical canaries', 'PASS public-index semantics match candidate domains and no MMIWG cross-template inheritance remains.', 'No action required.')
    return rows


def write_reports(root: Path, rows: list[dict[str, str]]) -> None:
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Public-Index-Semantic-Audit-current.csv',
        fields=FIELDS,
        rows=rows,
        title='Public Index Semantic Audit',
        generated_by='tools/public_index_semantic_audit.py',
        columns=['finding_id','severity','status','check','candidate_id','expected','observed','detail'],
        intro_lines=[
            'This audit checks that public-index template labels and broad public locations still mean the right thing.',
            'Governance quarantine is a release tier; it is not a domain template.',
            f'High findings: {sum(1 for r in rows if r.get("severity") == "high")}',
            f'Medium findings: {sum(1 for r in rows if r.get("severity") == "medium")}',
        ],
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--write-report', action='store_true')
    ap.add_argument('--fail-on-high', action='store_true')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    rows = run(root)
    if args.write_report:
        write_reports(root, rows)
    high = [r for r in rows if r.get('severity') == 'high']
    medium = [r for r in rows if r.get('severity') == 'medium']
    print(f"public_index_semantic_audit_rows={len(rows)} high={len(high)} medium={len(medium)}")
    for r in rows[:80]:
        print(f"{r.get('severity','?').upper()} {r.get('status')} {r.get('check')} {r.get('candidate_id')}: {r.get('detail')}")
    if len(rows) > 80:
        print(f'... {len(rows)-80} more rows')
    if args.fail_on_high and high:
        sys.exit(1)


if __name__ == '__main__':
    main()
