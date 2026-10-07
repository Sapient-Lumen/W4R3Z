#!/usr/bin/env python3
import copy
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
RELEASE_ID = 'worked-example-draft-59'
NOTE_VERSION = '0.59'


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(name: str):
    path = ART / name
    data = path.read_bytes()
    return json.loads(data), sha256_bytes(data)


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return abs(a - b) <= tol


def attenuated_bits(raw_b: float, p: float) -> float:
    return math.log2((1.0 - p) + p * (2.0 ** raw_b))


def extract_paper_version(text: str):
    m = re.search(r'Unified archive note v([0-9]+\.[0-9]+)', text)
    return m.group(1) if m else None


def main() -> None:
    abom, abom_digest = load_json('example_abom.json')
    receipt, receipt_digest = load_json('example_receipt.json')
    release_receipt, release_receipt_digest = load_json('example_release_receipt.json')
    uvi, uvi_digest = load_json('example_uvi.json')
    verifier_report, verifier_report_digest = load_json('example_verifier_report.json')
    state_decl, state_decl_digest = load_json('example_state_decl.json')
    state_decl_registry, state_decl_registry_digest = load_json('example_state_decl_registry.json')
    primary_surface_manifest, primary_surface_digest = load_json('example_primary_surface_manifest.json')
    user_watch_policy, user_watch_policy_digest = load_json('example_user_watch_policy.json')
    change_control, change_control_digest = load_json('example_change_control.json')
    plan_catalog, plan_catalog_digest = load_json('example_replay_plans.json')
    profiling_evidence, profiling_evidence_digest = load_json('example_profiling_evidence.json')
    profiling_prefix_evidence = None
    profiling_prefix_evidence_digest = None
    variant_receipt = None
    variant_receipt_digest = None
    profiling_statecond_evidence = None
    profiling_statecond_evidence_digest = None
    statecond_variant_receipt = None
    statecond_variant_receipt_digest = None
    try:
        profiling_prefix_evidence, profiling_prefix_evidence_digest = load_json('example_profiling_evidence_prefixfetch.json')
        variant_receipt, variant_receipt_digest = load_json('example_receipt_prefixfetch_variant.json')
    except FileNotFoundError:
        pass
    try:
        profiling_statecond_evidence, profiling_statecond_evidence_digest = load_json('example_profiling_evidence_prefixfetch_statecond.json')
        statecond_variant_receipt, statecond_variant_receipt_digest = load_json('example_receipt_prefixfetch_statecond_variant.json')

    except FileNotFoundError:
        pass


    profiling_contact_coarsened_evidence = None
    profiling_contact_coarsened_evidence_digest = None
    contact_coarsened_variant_receipt = None
    contact_coarsened_variant_receipt_digest = None
    coarsening_map_contact = None
    coarsening_map_contact_digest = None
    try:
        profiling_contact_coarsened_evidence, profiling_contact_coarsened_evidence_digest = load_json('example_profiling_evidence_contact_coarsened.json')
        contact_coarsened_variant_receipt, contact_coarsened_variant_receipt_digest = load_json('example_receipt_contact_coarsened_variant.json')
        coarsening_map_contact, coarsening_map_contact_digest = load_json('example_coarsening_map_contact.json')
    except FileNotFoundError:
        pass

    support_bundle_map, support_bundle_map_digest = load_json('example_support_bundle_map.json')
    compare_profile, compare_profile_digest = load_json('example_compare_profile.json')
    compare_walkthrough, compare_walkthrough_digest = load_json('example_compare_walkthrough.json')
    compare_report, compare_report_digest = load_json('example_compare_report.json')
    drift_cases, drift_cases_digest = load_json('example_drift_cases.json')
    exposure_registry, exposure_registry_digest = load_json('example_exposure_nf_registry.json')
    tw_decl_obj, tw_decl_digest = load_json('example_tw_decl.json')
    artifact_inventory, artifact_inventory_digest = load_json('example_artifact_inventory.json')
    support_manifest, _ = load_json('support_manifest.json')
    existing_validation_report_path = ART / 'example_validation_report.json'
    existing_validation_report_digest = None
    if existing_validation_report_path.exists():
        existing_validation_report_digest = sha256_bytes(existing_validation_report_path.read_bytes())

    paper_text = (ROOT / 'paper.tex').read_text(encoding='utf-8')
    paper_version = extract_paper_version(paper_text)
    expected_paper_version = RELEASE_ID.replace('worked-example-draft-', '0.')

    checks = []
    warnings = []

    def record(name: str, ok: bool, detail: str):
        checks.append({'name': name, 'ok': ok, 'detail': detail})

    claim_id = receipt['claim_id']
    tw_id = receipt['tw_id']
    enf_by_label = {e['label']: e['exposure_nf_id'] for e in exposure_registry.get('entries', [])}
    record('claim_id consistency', all(obj['claim_id'] == claim_id for obj in [abom, state_decl, state_decl_registry, primary_surface_manifest, user_watch_policy, change_control, plan_catalog, support_bundle_map, compare_profile, compare_walkthrough, compare_report, drift_cases, verifier_report, artifact_inventory]), f'claim_id={claim_id}')
    record('profiling evidence claim_id consistency', profiling_evidence.get('evidence', {}).get('claim_id') == claim_id, f"evidence.claim_id={profiling_evidence.get('evidence', {}).get('claim_id')}")
    record('profiling evidence tw_id consistency', profiling_evidence.get('evidence', {}).get('tw_id') == tw_id, f"evidence.tw_id={profiling_evidence.get('evidence', {}).get('tw_id')}")
    record('tw_id consistency', state_decl['tw_id'] == tw_id == compare_profile['user_compare_surface']['tw_id'] == tw_decl_obj['tw_id'], f'tw_id={tw_id}')

    state_decl_id = state_decl.get('state_decl_id')
    record('state_decl_id presence', isinstance(state_decl_id, str) and state_decl_id.startswith('sha256:'), f'state_decl_id={state_decl_id}')
    record('state_decl_id consistency', receipt.get('state_decl_id') == state_decl_id == change_control['interface_guard'].get('state_decl_id') == compare_profile['user_compare_surface'].get('state_decl_id'), 'receipt, state declaration, change-control guard, and compare profile agree on state_decl_id')
    record('release label consistency', release_receipt['release_id'] == abom['release_label'] == compare_profile['release_id'] == change_control['release_id'] == drift_cases['base_release_id'] == compare_walkthrough['base_release_id'] == artifact_inventory['release_id'] == RELEASE_ID, f'release ids agree and are {RELEASE_ID}')
    record('paper version aligned with draft label', paper_version == expected_paper_version, f'paper.tex declares v{paper_version}; expected v{expected_paper_version} for {RELEASE_ID}')

    # receipt line item references
    line_items = {item['exposure_nf_id']: item for item in receipt['line_items']}

    # profiling/equalization evidence_id coherence
    if 'enf.profiling.retrybucket.v1' in enf_by_label:
        profiling_item = line_items.get(enf_by_label['enf.profiling.retrybucket.v1'])
        record('profiling evidence_id present', profiling_item is not None and isinstance(profiling_item.get('evidence_id'), str), f"evidence_id={profiling_item.get('evidence_id') if profiling_item else None}")
        record('profiling evidence_id coherence', profiling_item is not None and profiling_item.get('evidence_id') == profiling_evidence.get('evidence_id'), 'receipt line item evidence_id matches example_profiling_evidence.json evidence_id')
    else:
        record('profiling ENF label present', False, 'exposure registry missing enf.profiling.retrybucket.v1')

    primary_item = line_items[enf_by_label['enf.primary.linkability.v1']]
    rho = primary_item.get('obs_model', {}).get('rho_upper')
    record('primary rho_upper presence', isinstance(rho, (int, float)) and 0.0 <= float(rho) <= 1.0, f'rho_upper={rho}')
    rho_ok = (rho is not None and primary_surface_manifest.get('rho_upper') is not None and change_control['interface_guard'].get('primary_rho_upper') is not None and compare_profile['primary_compare_surface'].get('rho_upper') is not None)
    if rho_ok:
        rho_ok = float(rho) == float(primary_surface_manifest.get('rho_upper')) == float(change_control['interface_guard'].get('primary_rho_upper')) == float(compare_profile['primary_compare_surface'].get('rho_upper'))
    record('primary rho_upper coherence', rho_ok, 'rho_upper agrees across receipt obs_model, primary-surface manifest, change-control guard, and compare profile')
    record('tw_id per line item', all('tw_id' in item and item['tw_id'] == tw_id for item in receipt['line_items']), 'each line item carries tw_id matching the receipt-level tw_id')

    replay_hooks = [item['replay_hook'] for item in receipt['line_items']]
    plan_ids = {plan['plan_id'] for plan in plan_catalog['plans']}
    bundle_ids = {bundle['bundle_id'] for bundle in support_bundle_map['bundles']}
    plan_spec_ids = {plan['plan_id']: plan.get('plan_spec_id') for plan in plan_catalog.get('plans', [])}

    def canon_bytes(obj) -> bytes:
        return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def sha256_id(obj) -> str:
        return "sha256:" + sha256_bytes(canon_bytes(obj))

    recomputed_plan_spec_ids = {
        plan['plan_id']: sha256_id(plan.get('plan_spec', {}))
        for plan in plan_catalog.get('plans', [])
    }


    # state-declaration canonicalization
    def strip_state_decl_id(sd: dict) -> dict:
        sd2 = copy.deepcopy(sd)
        sd2.pop('state_decl_id', None)
        return sd2

    recomputed_state_decl_id = sha256_id(strip_state_decl_id(state_decl))
    record('state_decl_id canonicalization', state_decl_id == recomputed_state_decl_id, f'recomputed={recomputed_state_decl_id}')
    # registry binding
    reg_entries = state_decl_registry.get('entries', [])
    reg_ok = len(reg_entries) == 1 and reg_entries[0].get('state_contract_id') == state_decl.get('state_contract_id') and reg_entries[0].get('state_decl_id') == state_decl_id
    record('state decl registry binding', reg_ok, 'example_state_decl_registry.json binds state_contract_id to state_decl_id')
    record('replay plan coverage', all(h['plan_id'] in plan_ids for h in replay_hooks), f'plan_ids={sorted(plan_ids)}')
    record('plan spec ids present', all(plan_spec_ids.get(pid) for pid in plan_ids), 'every plan has a plan_spec_id')
    record('plan spec id canonicalization', all(plan_spec_ids.get(pid) == recomputed_plan_spec_ids.get(pid) for pid in plan_ids), 'plan_spec_id matches sha256(canon(plan_spec)) for each plan')
    record('receipt replay hooks carry plan_spec_id', all('plan_spec_id' in h for h in replay_hooks), 'each replay_hook includes a plan_spec_id')
    record('receipt plan_spec_id matches catalog', all(h.get('plan_spec_id') == plan_spec_ids.get(h.get('plan_id')) for h in replay_hooks), 'each replay_hook plan_spec_id matches the catalog entry for that plan_id')
    record('artifact bundle coverage', all(h['artifact_bundle'] in bundle_ids for h in replay_hooks), f'bundle_ids={sorted(bundle_ids)}')

    # math checks
    vector = line_items[enf_by_label['enf.fallback.vector.v1']]['obs_model']['vector']
    recomputed_tiers = [attenuated_bits(v['raw_b'], v['p']) for v in vector]
    fallback_summary = sum(recomputed_tiers)
    record('fallback vector arithmetic', close(fallback_summary, line_items[enf_by_label['enf.fallback.vector.v1']]['budget_value']), f'recomputed={fallback_summary:.16f}')

    cset = line_items[enf_by_label['enf.fallback.cct.v1']]
    cset_recomputed = attenuated_bits(cset['knobs']['raw_b'], cset['obs_model']['p_obs_upper'])
    record('fallback cset arithmetic', close(cset_recomputed, cset['budget_value']), f'recomputed={cset_recomputed:.16f}')

    pathselect = line_items[enf_by_label['enf.pathselect.fallbackbit.v1']]
    selection_tax = math.log2(pathselect['obs_model']['R_pi_upper'])
    record('selection tax arithmetic', close(selection_tax, pathselect['budget_value']), f'recomputed={selection_tax:.16f}')

    total_summary = math.log2(pathselect['obs_model']['fallback_rate_hat'] * (2.0 ** fallback_summary) + (1.0 - pathselect['obs_model']['fallback_rate_hat']) * (2.0 ** line_items[enf_by_label['enf.primary.linkability.v1']]['budget_value'])) + selection_tax
    record('ABOM fallback summary', close(abom['budget_summary']['fallback_summary'], fallback_summary), f"abom={abom['budget_summary']['fallback_summary']:.16f}")
    record('ABOM total summary', close(abom['budget_summary']['total_summary'], total_summary), f"abom={abom['budget_summary']['total_summary']:.16f}; recomputed={total_summary:.16f}")
    record('compare profile totals', close(compare_profile['user_compare_surface']['budget_value'], fallback_summary) and close(compare_profile['user_compare_surface']['selection_tax_bits'], selection_tax) and close(compare_profile['user_compare_surface']['total_summary_bits_per_lookup'], total_summary), 'compare profile matches recomputed summaries')
    record('verifier report totals', close(verifier_report['recomputed']['fallback_summary_bits_per_lookup'], fallback_summary) and close(verifier_report['recomputed']['selection_tax_bits'], selection_tax) and close(verifier_report['recomputed']['total_summary_bits_per_lookup'], total_summary), 'verifier report matches recomputed summaries')

    # digest link checks
    record('release receipt digests', release_receipt['abom_digest'] == abom_digest and release_receipt['receipt_digest'] == receipt_digest and release_receipt['plan_catalog_digest'] == plan_catalog_digest, 'release receipt references current ABOM/receipt/plan digests')
    record('adjunct digest links', release_receipt['adjunct_digests']['primary_surface_manifest'] == primary_surface_digest and release_receipt['adjunct_digests']['state_decl'] == state_decl_digest and release_receipt['adjunct_digests']['user_watch_policy'] == user_watch_policy_digest and release_receipt['adjunct_digests']['change_control'] == change_control_digest and release_receipt['adjunct_digests']['support_bundle_map'] == support_bundle_map_digest and release_receipt['adjunct_digests']['compare_profile'] == compare_profile_digest and release_receipt['adjunct_digests']['compare_walkthrough'] == compare_walkthrough_digest, 'release receipt adjunct digests match current files')
    record('UVI receipt digest', uvi['receipt_digest'] == receipt_digest, 'UVI points at current receipt digest')
    record('compare walkthrough base digest', compare_walkthrough['base_fields']['user_fast_diff']['receipt_digest'] == receipt_digest, 'compare walkthrough base receipt digest matches current receipt')

    # compare walkthrough successor arithmetic
    successor_p = 0.015
    successor_fallback = sum(attenuated_bits(v['raw_b'], successor_p) for v in vector)
    successor_total = math.log2(pathselect['obs_model']['fallback_rate_hat'] * (2.0 ** successor_fallback) + (1.0 - pathselect['obs_model']['fallback_rate_hat']) * (2.0 ** line_items[enf_by_label['enf.primary.linkability.v1']]['budget_value'])) + selection_tax
    successor_receipt = copy.deepcopy(receipt)
    for item in successor_receipt['line_items']:
        if item['exposure_nf_id'] == enf_by_label['enf.fallback.cct.v1']:
            item['budget_value'] = attenuated_bits(item['knobs']['raw_b'], successor_p)
            item['obs_model']['p_obs_upper'] = successor_p
        elif item['exposure_nf_id'] == enf_by_label['enf.fallback.vector.v1']:
            successor_vector = []
            for v in item['obs_model']['vector']:
                successor_vector.append({
                    'tier': v['tier'],
                    'p': successor_p,
                    'raw_b': v['raw_b'],
                    'effective_b': attenuated_bits(v['raw_b'], successor_p),
                    'status': v['status'],
                })
            item['budget_value'] = successor_fallback
            item['obs_model']['vector'] = successor_vector
    successor_receipt_digest = sha256_bytes(json.dumps(successor_receipt, indent=2, sort_keys=True).encode() + b'\n')
    record('compare walkthrough successor arithmetic', close(compare_walkthrough['successor_fields']['user_fast_diff']['budget_value'], successor_fallback) and close(compare_walkthrough['successor_fields']['user_fast_diff']['total_summary_bits_per_lookup'], successor_total), f'successor_fallback={successor_fallback:.16f}; successor_total={successor_total:.16f}')
    record('compare walkthrough successor digest', compare_walkthrough.get('successor_receipt_digest_basis') == 'synthetic_case_B_successor_receipt' and compare_walkthrough['successor_fields']['user_fast_diff']['receipt_digest'] == successor_receipt_digest, f'successor_receipt_digest={successor_receipt_digest}')
    successor_ids = [case['successor_release_id'] for case in drift_cases['cases']]
    expected_successors = [RELEASE_ID + suffix for suffix in ('a', 'b', 'c')]
    record('successor release-id coherence', drift_cases.get('base_release_id') == RELEASE_ID and compare_walkthrough.get('base_release_id') == RELEASE_ID and compare_walkthrough['successor_fields']['release_id'] == RELEASE_ID + 'b' and successor_ids == expected_successors, f"base={compare_walkthrough.get('base_release_id')}; successors={successor_ids}")

    # support manifest identity
    manifest_paths = {entry['path']: entry['sha256'] for entry in support_manifest['files']}
    record('support manifest identity', support_manifest.get('manifest_id') == 'worked-example-support-manifest-v1' and support_manifest.get('claim_id') == claim_id and support_manifest.get('release_id') == RELEASE_ID, f"manifest_id={support_manifest.get('manifest_id')}; release_id={support_manifest.get('release_id')}")
    record('manifest-inventory cross reference', support_manifest.get('artifact_inventory_id') == artifact_inventory.get('inventory_id') and artifact_inventory.get('support_manifest_id') == support_manifest.get('manifest_id'), f"support_manifest artifact_inventory_id={support_manifest.get('artifact_inventory_id')}; artifact_inventory support_manifest_id={artifact_inventory.get('support_manifest_id')}")
    record('maintenance report identity coherence', compare_report.get('release_id') == RELEASE_ID and compare_report.get('support_manifest_id') == support_manifest.get('manifest_id') and compare_report.get('artifact_inventory_id') == artifact_inventory.get('inventory_id') and compare_report.get('note_version') == NOTE_VERSION, f"compare_report release_id={compare_report.get('release_id')}; support_manifest_id={compare_report.get('support_manifest_id')}; artifact_inventory_id={compare_report.get('artifact_inventory_id')}; note_version={compare_report.get('note_version')}")
    record('support manifest compare report digest', manifest_paths.get('example_compare_report.json') == compare_report_digest, f"manifest compare-report digest={manifest_paths.get('example_compare_report.json')}; compare_report_digest={compare_report_digest}")
    if existing_validation_report_digest is not None and 'example_validation_report.json' in manifest_paths:
        record('support manifest validation report digest', manifest_paths.get('example_validation_report.json') == existing_validation_report_digest, 'persisted validation-report digest already matches the support manifest before refresh')
    elif existing_validation_report_digest is not None:
        warnings.append('support_manifest.json did not yet bind example_validation_report.json at validator start; this is normal on the first clean rebuild.')

    # support manifest coverage (do not require self-reference)
    expected = {
        'example_abom.json': abom_digest,
        'example_exposure_nf_registry.json': exposure_registry_digest,
        'example_tw_decl.json': tw_decl_digest,
        'example_receipt.json': receipt_digest,
        'example_release_receipt.json': release_receipt_digest,
        'example_primary_surface_manifest.json': primary_surface_digest,
        'example_replay_plans.json': plan_catalog_digest,
        'example_support_bundle_map.json': support_bundle_map_digest,
        'example_profiling_evidence.json': profiling_evidence_digest,
        'example_compare_profile.json': compare_profile_digest,
        'example_compare_walkthrough.json': compare_walkthrough_digest,
        'example_state_decl.json': state_decl_digest,
        'example_state_decl_registry.json': state_decl_registry_digest,
        'example_user_watch_policy.json': user_watch_policy_digest,
        'example_change_control.json': change_control_digest,
        'example_drift_cases.json': drift_cases_digest,
        'example_uvi.json': uvi_digest,
        'example_verifier_report.json': verifier_report_digest,
        'example_artifact_inventory.json': artifact_inventory_digest,
        '../README.md': sha256_bytes((ROOT / 'README.md').read_bytes()),
        '../paper.tex': sha256_bytes((ROOT / 'paper.tex').read_bytes()),
        '../tools/materialize_example.py': sha256_bytes((ROOT / 'tools' / 'materialize_example.py').read_bytes()),
        '../tools/emit_compare_report.py': sha256_bytes((ROOT / 'tools' / 'emit_compare_report.py').read_bytes()),
        '../tools/validate_example.py': sha256_bytes((ROOT / 'tools' / 'validate_example.py').read_bytes()),
        '../tools/rebuild_example.sh': sha256_bytes((ROOT / 'tools' / 'rebuild_example.sh').read_bytes()),
    }
    expected_with_optional = dict(expected)
    if variant_receipt_digest is not None:
        expected_with_optional['example_receipt_prefixfetch_variant.json'] = variant_receipt_digest
    if profiling_prefix_evidence_digest is not None:
        expected_with_optional['example_profiling_evidence_prefixfetch.json'] = profiling_prefix_evidence_digest
    if 'example_compare_report.json' in manifest_paths:
        expected_with_optional['example_compare_report.json'] = compare_report_digest
    if 'example_validation_report.json' in manifest_paths:
        expected_with_optional['example_validation_report.json'] = manifest_paths['example_validation_report.json']
    record('support manifest coverage', all(manifest_paths.get(p) == d for p, d in expected_with_optional.items()), 'support_manifest.json covers the current support artifacts, note source, and helper files, with compare/validator outputs bound on clean rebuilds')

    # artifact inventory checks
    inventory_paths = [entry['path'] for group in artifact_inventory['groups'] for entry in group['entries']]
    record('artifact inventory uniqueness', len(inventory_paths) == len(set(inventory_paths)), 'inventory paths are unique')
    artifact_json_paths = {p.name for p in ART.glob('*.json')}
    helper_paths = {
        'README.md',
        'paper.tex',
        'tools/materialize_example.py',
        'tools/emit_compare_report.py',
        'tools/validate_example.py',
        'tools/rebuild_example.sh',
    }
    expected_inventory_paths = sorted(artifact_json_paths | helper_paths)
    record('artifact inventory coverage', sorted(inventory_paths) == expected_inventory_paths, 'every JSON artifact plus the note source, README, and tiny helper scripts are inventory-listed exactly once')
    def inventory_path_exists(path: str) -> bool:
        return ((ART / path).exists() if '/' not in path and path.endswith('.json') else (ROOT / path).exists())

    record('artifact inventory existence', all(inventory_path_exists(path) for path in inventory_paths), 'inventory-listed artifacts and maintenance helpers exist at the declared paths')
    record('artifact inventory support manifest inclusion', 'example_artifact_inventory.json' in manifest_paths and manifest_paths['example_artifact_inventory.json'] == artifact_inventory_digest, 'support manifest binds the current artifact inventory digest')
    transient_paths = {'paper.pdf', 'paper.aux', 'paper.log', 'paper.out', 'pngcheck', 'pngcheck/contact_sheet.png', 'tools/__pycache__', 'tools/materialize_example.cpython-311.pyc'}
    record('transient outputs excluded from maintenance layer', all(path not in inventory_paths for path in transient_paths) and all(path not in manifest_paths for path in transient_paths), 'inventory/support manifest exclude local render/interpreter byproducts such as PDFs, aux/log/out files, PNG page checks, and Python bytecode caches')

    # coherence checks across adjuncts
    receipt_exposures = [item['exposure_nf_id'] for item in receipt['line_items']]
    record('user-facing surface coherence', uvi['exposure_nf_id'] == user_watch_policy['primary_user_surface_exposure_nf_id'] == compare_profile['user_compare_surface']['exposure_nf_id'], 'UVI, watch policy, and compare profile point to the same user-facing surface')
    record('change-control guard coherence', change_control['interface_guard']['required_exposures'] == receipt_exposures and change_control['interface_guard']['tw_id'] == tw_id and (change_control['interface_guard'].get('primary_rho_upper') is not None and primary_item.get('obs_model', {}).get('rho_upper') is not None and float(change_control['interface_guard'].get('primary_rho_upper')) == float(primary_item.get('obs_model', {}).get('rho_upper'))) and change_control['interface_guard'].get('state_decl_id') == state_decl.get('state_decl_id') and compare_profile['primary_compare_surface']['exposure_nf_id'] == receipt_exposures[0], 'guard fields align across receipt, primary rho_upper, state declaration id, and compare profile')
    record('bundle plan coherence', all(plan in plan_ids for bundle in support_bundle_map['bundles'] for plan in bundle['consumed_by']), 'every support bundle resolves to known replay plans')
    record('bundle artifact existence', all((ART / req).exists() for bundle in support_bundle_map['bundles'] for req in bundle['required_artifacts']), 'every required_artifact named by the support-bundle map exists in the artifacts directory')
    record('watch policy field set', user_watch_policy['compare_fields'] == compare_profile['source_fields']['uvi'], 'user watch policy fields match the UVI compare fields surfaced by the compare profile')
    record('compare report coherence', compare_report['compare_profile_id'] == compare_profile['compare_profile_id'] and compare_report['classification'] == compare_walkthrough['classification_result'] and compare_report['user_fast_diff']['base'] == compare_walkthrough['base_fields']['user_fast_diff'] and compare_report['user_fast_diff']['successor'] == compare_walkthrough['successor_fields']['user_fast_diff'] and compare_report['auditor_fast_diff']['base'] == compare_walkthrough['base_fields']['auditor_fast_diff'] and compare_report['auditor_fast_diff']['successor'] == compare_walkthrough['successor_fields']['auditor_fast_diff'], 'machine-readable compare report agrees with the compare profile and walk-through')


    # Optional prefix-fetch variant checks (if present).
    if variant_receipt is not None and profiling_prefix_evidence is not None:
        record('prefix-fetch variant claim_id consistency', variant_receipt.get('claim_id') == claim_id, 'variant receipt uses the same claim_id')
        record('prefix-fetch variant tw_id consistency', variant_receipt.get('tw_id') == tw_id, 'variant receipt uses the same tw_id')
        # evidence id must bind the prefix evidence object
        prefix_item = next((it for it in variant_receipt.get('line_items', []) if it.get('name') == 'profiling_equalization_prefixfetch'), None)
        record('prefix-fetch variant has profiling line item', prefix_item is not None, 'variant receipt includes profiling_equalization_prefixfetch line item')
        if prefix_item is not None:
            record('prefix-fetch evidence_id binds evidence object', prefix_item.get('evidence_id') == profiling_prefix_evidence.get('evidence_id'), 'variant line item evidence_id equals evidence object evidence_id')
            summary = profiling_prefix_evidence.get('evidence', {}).get('certificate_summary', {})
            expected_eta = float(summary.get('eta_bits'))
            expected_delta = float(summary.get('delta_slack'))
            bv = prefix_item.get('budget_value', {})
            record('prefix-fetch budget_value agrees with evidence summary', close(float(bv.get('eta_bits')), expected_eta) and close(float(bv.get('delta')), expected_delta), f'budget_value={{eta_bits:{bv.get("eta_bits")},delta:{bv.get("delta")}}} vs evidence={{eta_bits:{expected_eta},delta:{expected_delta}}}')


    # Optional state-conditioned prefix-fetch variant checks (if present).
    if statecond_variant_receipt is not None and profiling_statecond_evidence is not None:
        record('statecond prefix-fetch variant claim_id consistency', statecond_variant_receipt.get('claim_id') == claim_id, 'state-conditioned variant receipt uses the same claim_id')
        record('statecond prefix-fetch variant tw_id consistency', statecond_variant_receipt.get('tw_id') == tw_id, 'state-conditioned variant receipt uses the same tw_id')
        sc_item = next((it for it in statecond_variant_receipt.get('line_items', []) if it.get('name') == 'profiling_equalization_prefixfetch_statecond'), None)
        record('statecond variant has profiling line item', sc_item is not None, 'state-conditioned variant receipt includes profiling_equalization_prefixfetch_statecond line item')
        if sc_item is not None:
            record('statecond evidence_id binds evidence object', sc_item.get('evidence_id') == profiling_statecond_evidence.get('evidence_id'), 'state-conditioned variant line item evidence_id equals evidence object evidence_id')
            summary = profiling_statecond_evidence.get('evidence', {}).get('certificate_summary', {})
            expected_eta = float(summary.get('eta_bits'))
            expected_delta = float(summary.get('delta_slack'))
            bv = sc_item.get('budget_value', {})
            record('statecond budget_value agrees with evidence summary', close(float(bv.get('eta_bits')), expected_eta) and close(float(bv.get('delta')), expected_delta), f'budget_value={{eta_bits:{bv.get("eta_bits")},delta:{bv.get("delta")}}} vs evidence={{eta_bits:{expected_eta},delta:{expected_delta}}}')
    

    # Optional coarsened-contact variant checks (if present).
    if contact_coarsened_variant_receipt is not None and profiling_contact_coarsened_evidence is not None and coarsening_map_contact is not None:
        record('contact-coarsened variant claim_id consistency', contact_coarsened_variant_receipt.get('claim_id') == claim_id, 'coarsened-contact variant receipt uses the same claim_id')
        record('contact-coarsened variant tw_id consistency', contact_coarsened_variant_receipt.get('tw_id') == tw_id, 'coarsened-contact variant receipt uses the same tw_id')
        cc_item = next((it for it in contact_coarsened_variant_receipt.get('line_items', []) if it.get('name') == 'profiling_equalization_contact_coarsened'), None)
        record('contact-coarsened variant has profiling line item', cc_item is not None, 'coarsened-contact variant receipt includes profiling_equalization_contact_coarsened line item')
        if cc_item is not None:
            record('contact-coarsened evidence_id binds evidence object', cc_item.get('evidence_id') == profiling_contact_coarsened_evidence.get('evidence_id'), 'coarsened-contact variant line item evidence_id equals evidence object evidence_id')
            ev = profiling_contact_coarsened_evidence.get('evidence', {})
            record('contact-coarsened evidence binds coarsening_map_id', ev.get('coarsening_map_id') == coarsening_map_contact.get('coarsening_map_id'), 'evidence coarsening_map_id equals declared coarsening map id')
            summary = ev.get('certificate_summary', {})
            expected_eta = float(summary.get('eta_bits'))
            expected_delta = float(summary.get('delta_slack'))
            bv = cc_item.get('budget_value', {})
            record('contact-coarsened budget_value agrees with evidence summary', close(float(bv.get('eta_bits')), expected_eta) and close(float(bv.get('delta')), expected_delta), f'budget_value={{eta_bits:{bv.get("eta_bits")},delta:{bv.get("delta")}}} vs evidence={{eta_bits:{expected_eta},delta:{expected_delta}}}')

# policy warnings, not failures
    if primary_surface_manifest.get('status') == 'policy_declaration':
        warnings.append('Primary-path line item remains assumption-qualified under sep.nr1; validation checks internal consistency, not real-world truth of separation.')
    warnings.append('Validation is archive-internal and does not replace Evaluation 1-3 workflows or live deployment evidence.')

    overall_ok = all(c['ok'] for c in checks)
    report = {
        'report_id': 'worked-example-validation-report-v1',
        'claim_id': claim_id,
        'release_id': RELEASE_ID,
        'support_manifest_id': support_manifest.get('manifest_id'),
        'artifact_inventory_id': artifact_inventory.get('inventory_id'),
        'note_version': NOTE_VERSION,
        'overall_ok': overall_ok,
        'checks': checks,
        'warnings': warnings,
        'recomputed': {
            'fallback_contact_bits_per_lookup': cset_recomputed,
            'fallback_summary_bits_per_lookup': fallback_summary,
            'selection_tax_bits': selection_tax,
            'total_summary_bits_per_lookup': total_summary,
            'successor_case_B_fallback_summary_bits_per_lookup': successor_fallback,
            'successor_case_B_total_summary_bits_per_lookup': successor_total,
        },
    }
    report_path = ART / 'example_validation_report.json'
    data = json.dumps(report, indent=2, sort_keys=True).encode() + b'\n'
    report_path.write_bytes(data)
    report_digest = sha256_bytes(data)

    # Update support manifest to include the freshly written validation report.
    # The compare-report digest is expected to have been bound already by emit_compare_report.py.
    existing_paths = {entry['path'] for entry in support_manifest['files']}
    if 'example_validation_report.json' not in existing_paths:
        support_manifest['files'].append({'path': 'example_validation_report.json', 'sha256': report_digest})
    else:
        for entry in support_manifest['files']:
            if entry['path'] == 'example_validation_report.json':
                entry['sha256'] = report_digest
    support_manifest['files'] = sorted(support_manifest['files'], key=lambda x: x['path'])
    (ART / 'support_manifest.json').write_bytes(json.dumps(support_manifest, indent=2, sort_keys=True).encode() + b'\n')

    import sys
    print(json.dumps({'overall_ok': overall_ok, 'report_digest': report_digest}, indent=2))
    sys.exit(0 if overall_ok else 1)


if __name__ == '__main__':
    main()
