#!/usr/bin/env python3
from pathlib import Path
import contextlib
import io
import json
import re
import sys

sys.dont_write_bytecode = True

from restart_mirror_family import load_state, render_generated_restart_mirror_block, replace_generated_restart_mirror_block
from authority_graph_codec import load_authority_graph, write_authority_graph
from frontier_source_freshness import write_frontier_source_freshness_audit as _write_frontier_source_freshness_audit
from forecast_credit_policy import write_forecast_credit_realization_audit as _write_forecast_credit_realization_audit
from familyc_subregion_state_policy import write_familyc_subregion_state_audit as _write_familyc_subregion_state_audit
from frontier_source_policy import write_frontier_source_custody_isolation_audit as _write_frontier_source_custody_isolation_audit
from graviton_source_role_policy import write_graviton_source_role_audit as _write_graviton_source_role_audit
from route_realization_policy import write_route_realization_status_audit as _write_route_realization_status_audit
from amplitudes_gravity_bootstrap_policy import write_amplitudes_gravity_bootstrap_audit as _write_amplitudes_gravity_bootstrap_audit
from asymptotic_safety_observable_policy import write_asymptotic_safety_observable_audit as _write_asymptotic_safety_observable_audit
from evidence_delta_handoff_policy import write_evidence_delta_handoff_audit as _write_evidence_delta_handoff_audit
from route_condition_ceiling_policy import write_route_condition_ceiling_audit as _write_route_condition_ceiling_audit
from learned_inverse_ood_policy import write_learned_inverse_ood_audit as _write_learned_inverse_ood_audit
from stringm_observed_sector_policy import write_stringm_observed_sector_audit as _write_stringm_observed_sector_audit
from gw_strongfield_public_test_policy import write_gw_strongfield_public_test_audit as _write_gw_strongfield_public_test_audit
from qrf_frame_transport_policy import write_qrf_frame_transport_audit as _write_qrf_frame_transport_audit
from route_pressure_mirror_policy import write_route_pressure_mirror_audit as _write_route_pressure_mirror_audit
from causal_set_matter_horizon_policy import write_causal_set_matter_horizon_audit as _write_causal_set_matter_horizon_audit
from familyb_thermo_entropy_policy import write_familyb_thermo_entropy_audit as _write_familyb_thermo_entropy_audit
from cmb_bmode_source_role_policy import write_cmb_bmode_source_role_audit as _write_cmb_bmode_source_role_audit
from cosmology_source_role_policy import write_cosmology_source_role_audit as _write_cosmology_source_role_audit
from familyc_finite_n_reconstruction_policy import write_familyc_finite_n_reconstruction_audit as _write_familyc_finite_n_reconstruction_audit
from lab_gie_bmv_source_role_policy import write_lab_gie_bmv_source_role_audit as _write_lab_gie_bmv_source_role_audit
from claim_language_current_boundary_policy import write_claim_language_current_boundary_audit as _write_claim_language_current_boundary_audit
from credit_allocation_current_boundary_policy import write_credit_allocation_current_boundary_audit as _write_credit_allocation_current_boundary_audit
from observed_sector_matter_policy import write_observed_sector_matter_audit as _write_observed_sector_matter_audit
from classical_gr_observed_sector_policy import write_classical_gr_observed_sector_audit as _write_classical_gr_observed_sector_audit
from dark_sector_constraint_policy import write_dark_sector_constraint_audit as _write_dark_sector_constraint_audit
from negative_control_route_overlap_policy import write_negative_control_route_overlap_audit as _write_negative_control_route_overlap_audit
from qm_qft_observed_sector_policy import write_qm_qft_observed_sector_audit as _write_qm_qft_observed_sector_audit
from source_role_credit_cap_policy import write_source_role_credit_cap_audit as _write_source_role_credit_cap_audit
from source_snapshot_manifest import write_source_snapshot_manifest_audit as _write_source_snapshot_manifest_audit


def write_archive_index(root: Path) -> None:
    paths = sorted(
        p for p in root.rglob('*')
        if p.is_file() and p.suffix in {'.md', '.json', '.py'} and '.zip' not in p.name
    )
    lines = ['# Filesystem index', '', f'Total tracked text surfaces: {len(paths)}', '']
    for p in paths:
        rel = p.relative_to(root).as_posix()
        lines.append(f'- `{rel}`')
    (root / 'ARCHIVE_INDEX.generated.md').write_text('\n'.join(lines) + '\n')
    print('wrote ARCHIVE_INDEX.generated.md')



def augment_authority_dependency_graph_with_computational_edges(root: Path) -> None:
    """Add computational-artifact edges after the base dependency graph is rendered."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    rows = graph.get('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id():
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key = (source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({
            'edge_id': next_edge_id(),
            'source_kind': source_kind,
            'source_id': source_id,
            'dependent_kind': dependent_kind,
            'dependent_id': dependent_id,
            'dependency_kind': dependency_kind,
            'required_for': required_for,
            'failure_effect': failure_effect,
            'max_credit_transmitted': max_credit,
        })
        existing.add(key)
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    credit_ledger = json.loads((root / 'CREDIT-ALLOCATION-LEDGER.json').read_text())
    evidence_ledger = json.loads((root / 'EVIDENCE-UNIT-LEDGER.json').read_text())
    ssc_ledger = json.loads((root / 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid = row.get('route_id', '')
        effect = row.get('promotion_ceiling', '') or row.get('authority_state', '')
        for cid in row.get('computational_reproducibility_ids', []):
            add('computational-reproducibility', cid, 'route', rid, 'computational-reproducibility-condition', 'route computational replay denominator', 'freeze code/workflow/container/replay credit when computational reproducibility fails', effect)
        for nid in row.get('numerical_stability_ids', []):
            add('numerical-stability', nid, 'route', rid, 'numerical-stability-condition', 'route numerical stability denominator', 'cap numerical/solver/tolerance support when stability fails', effect)
        for sid in row.get('software_supply_chain_ids', []):
            add('software-supply-chain', sid, 'route', rid, 'software-supply-chain-condition', 'route software provenance denominator', 'freeze software-backed support when supply-chain provenance fails', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'open-question' if target_id.startswith('OQ-') else 'claim'
        effect = binding.get('maximum_authority_effect', '') or 'bounded by binding row'
        for cid in binding.get('computational_reproducibility_ids', []):
            add('computational-reproducibility', cid, target_kind, target_id, 'computational-reproducibility-claim-condition', f'claim computational replay denominator under {binding.get("binding_id")}', 'freeze code/workflow/container/replay claim wording until the computational row is restored', effect)
        for nid in binding.get('numerical_stability_ids', []):
            add('numerical-stability', nid, target_kind, target_id, 'numerical-stability-claim-condition', f'claim numerical stability denominator under {binding.get("binding_id")}', 'freeze numerical/solver/tolerance claim wording until stability rows are restored', effect)
        for sid in binding.get('software_supply_chain_ids', []):
            add('software-supply-chain', sid, target_kind, target_id, 'software-supply-chain-claim-condition', f'claim software-provenance denominator under {binding.get("binding_id")}', 'freeze software-provenance or artifact-integrity claim wording until provenance is restored', effect)
    # Broad subordinate artifact conditions.
    ledgers = [
        ('evidence-unit', 'evidence_unit_id', evidence_ledger.get('evidence_units', []), 'evidence-unit computational artifact denominator'),
        ('credit-allocation', 'credit_id', credit_ledger.get('credit_rows', []), 'credit-row computational artifact denominator'),
    ]
    # Optional ledgers with common handle fields.
    optional = [
        ('empirical-delta', 'delta_id', 'EMPIRICAL-DELTA-LEDGER.json', 'empirical_deltas'),
        ('forecast', 'forecast_id', 'DISCRIMINATOR-FORECAST-LEDGER.json', 'forecast_rows'),
        ('decision-experiment', 'experiment_id', 'DECISION-EXPERIMENT-LEDGER.json', 'decision_experiments'),
        ('severity-test', 'severity_id', 'EVIDENCE-SEVERITY-LEDGER.json', 'severity_rows'),
        ('contrast-class', 'contrast_id', 'CONTRAST-CLASS-LEDGER.json', 'contrast_rows'),
        ('likelihood-update', 'update_id', 'LIKELIHOOD-UPDATE-LEDGER.json', 'update_rows'),
        ('prior-sensitivity', 'prior_id', 'PRIOR-SENSITIVITY-LEDGER.json', 'prior_rows'),
        ('measurement-model', 'measurement_model_id', 'MEASUREMENT-MODEL-LEDGER.json', 'measurement_model_rows'),
        ('systematic-uncertainty', 'systematic_id', 'SYSTEMATIC-UNCERTAINTY-LEDGER.json', 'systematic_rows'),
        ('calibration-traceability', 'calibration_id', 'CALIBRATION-TRACEABILITY-LEDGER.json', 'calibration_rows'),
        ('validity-domain', 'domain_id', 'DOMAIN-OF-VALIDITY-LEDGER.json', 'domain_rows'),
        ('transportability', 'transport_id', 'TRANSPORTABILITY-LEDGER.json', 'transport_rows'),
        ('extrapolation-fence', 'fence_id', 'EXTRAPOLATION-FENCE-LEDGER.json', 'fence_rows'),
        ('causal-mechanism', 'mechanism_id', 'CAUSAL-MECHANISM-LEDGER.json', 'mechanism_rows'),
        ('intervention-protocol', 'intervention_id', 'INTERVENTION-PROTOCOL-LEDGER.json', 'intervention_rows'),
        ('counterfactual-robustness', 'counterfactual_id', 'COUNTERFACTUAL-ROBUSTNESS-LEDGER.json', 'counterfactual_rows'),
        ('selection-function', 'selection_id', 'SELECTION-FUNCTION-LEDGER.json', 'selection_rows'),
        ('multiplicity-control', 'multiplicity_id', 'MULTIPLICITY-CONTROL-LEDGER.json', 'multiplicity_rows'),
        ('reporting-bias', 'bias_id', 'REPORTING-BIAS-LEDGER.json', 'bias_rows'),
        ('model-capacity', 'model_capacity_id', 'MODEL-CAPACITY-LEDGER.json', 'capacity_rows'),
        ('complexity-penalty', 'complexity_penalty_id', 'COMPLEXITY-PENALTY-LEDGER.json', 'complexity_rows'),
        ('generalization-validation', 'generalization_id', 'PREDICTIVE-GENERALIZATION-LEDGER.json', 'generalization_rows'),
        ('semantic-term', 'semantic_term_id', 'SEMANTIC-TERM-LEDGER.json', 'semantic_rows'),
        ('ontology-commitment', 'ontology_commitment_id', 'ONTOLOGY-COMMITMENT-LEDGER.json', 'commitment_rows'),
        ('claim-language-permission', 'language_permission_id', 'CLAIM-LANGUAGE-PERMISSION-LEDGER.json', 'permission_rows'),
        ('social-authority', 'social_authority_id', 'SOCIAL-AUTHORITY-LEDGER.json', 'social_rows'),
        ('review-replication', 'review_replication_id', 'REVIEW-REPLICATION-LEDGER.json', 'review_rows'),
        ('consensus-elicitation', 'consensus_elicitation_id', 'CONSENSUS-ELICITATION-LEDGER.json', 'consensus_rows'),
    ]
    for kind, id_key, file_name, rows_key in optional:
        path = root / file_name
        if path.exists():
            data = json.loads(path.read_text())
            ledgers.append((kind, id_key, data.get(rows_key, []), f'{kind} computational artifact denominator'))
    for dep_kind, id_key, item_rows, required_for in ledgers:
        for item in item_rows:
            item_id = item.get(id_key, '')
            effect = item.get('maximum_authority_effect') or item.get('maximum_credit') or item.get('current_maximum_credit') or item.get('route_state_effect') or 'bounded by owning row'
            for cid in item.get('computational_reproducibility_ids', []):
                add('computational-reproducibility', cid, dep_kind, item_id, 'computational-reproducibility-condition', required_for, 'remove replay-dependent credit when computational reproducibility fails', effect)
            for nid in item.get('numerical_stability_ids', []):
                add('numerical-stability', nid, dep_kind, item_id, 'numerical-stability-condition', required_for, 'cap numerical credit when solver, tolerance, seed, or platform stability fails', effect)
            for sid in item.get('software_supply_chain_ids', []):
                add('software-supply-chain', sid, dep_kind, item_id, 'software-supply-chain-condition', required_for, 'remove software-backed credit when provenance is missing or defeated', effect)
    for row in ssc_ledger.get('supply_chain_rows', []):
        sid = row.get('software_supply_chain_id', '')
        effect = row.get('maximum_authority_effect', '') or 'bounded by software-supply-chain row'
        for cid in row.get('computational_reproducibility_ids', []):
            add('computational-reproducibility', cid, 'software-supply-chain', sid, 'computational-reproducibility-condition', 'software supply-chain replay dependency', 'freeze software-chain credit when its replay artifact cannot be reproduced', effect)
    graph['edge_rows'] = rows
    graph.setdefault('generated_from', [])
    for rel in ['COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json', 'NUMERICAL-STABILITY-LEDGER.json', 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json']:
        if rel not in graph['generated_from']:
            graph['generated_from'].append(rel)
    graph['generation_rule'] = graph.get('generation_rule', '') + ' Computational-reproducibility, numerical-stability, and software-supply-chain edges are appended by augment_authority_dependency_graph_with_computational_edges.'
    write_authority_graph(graph_path, graph)
    print('augmented AUTHORITY-DEPENDENCY-GRAPH.json with computational-artifact edges')


def write_route_state_summary(root: Path) -> None:
    """Render a compact generated summary from executable route ledgers.

    rev0284 refactor: this summary is registry-driven, so later route-support
    families do not disappear from the compact route mirror when the archive adds
    new route handle fields.
    """
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    registry_path = root / 'LEDGER-FAMILY-REGISTRY.json'
    registry = json.loads(registry_path.read_text()) if registry_path.exists() else {'registry_rows': []}
    rows = route_ledger.get('route_rows', [])
    state_counts = {}
    for row in rows:
        state = row.get('authority_state', '<missing>')
        state_counts[state] = state_counts.get(state, 0) + 1

    def ledger_count(rel: str) -> int:
        p = root / rel
        if not p.exists():
            return 0
        try:
            obj = json.loads(p.read_text())
        except Exception:
            return 0
        # Count the first list-valued payload that is not route field metadata.
        preferred_keys = [
            'route_rows','controls','empirical_deltas','gate_rows','obligation_rows','forecast_rows','decision_rows','carrier_rows','protocol_rows','binding_rows','defeater_rows','rollback_rows','severity_rows','evidence_units','independence_rows','credit_rows','contrast_rows','update_rows','prior_rows','measurement_model_rows','systematic_rows','calibration_rows','domain_rows','transport_rows','fence_rows','mechanism_rows','intervention_rows','counterfactual_rows','selection_rows','multiplicity_rows','bias_rows','capacity_rows','complexity_rows','generalization_rows','semantic_rows','commitment_rows','permission_rows','authority_rows','review_rows','consensus_rows','reproducibility_rows','stability_rows','supply_chain_rows','proof_obligation_rows','assumption_discharge_rows','formalization_rows','idealization_rows','approximation_rows','limit_rows','boundary_rows','initial_data_rows','sector_rows','gauge_rows','constraint_rows','observable_rows','regularization_rows','flow_rows','matching_rows','composition_rows','interface_rows','global_rows','unitarity_rows','causality_rows','quantization_rows','classical_limit_rows','semiclassical_rows','information_rows','entropy_rows','no_go_rows','symmetry_rows','anomaly_rows','conservation_rows','topology_rows','dimension_rows','signature_rows','algebraic_rows','factorization_rows','edge_mode_rows','measure_rows','ensemble_rows','typicality_rows','particle_spectrum_rows','interaction_coupling_rows','mass_hierarchy_rows','background_rows','vacuum_energy_rows','thermal_history_rows','horizon_rows','thermodynamics_rows','evaporation_rows','registry_rows'
        ]
        for key in preferred_keys:
            val = obj.get(key)
            if isinstance(val, list):
                return len(val)
        # rev0337: later registry families introduced additional collection keys
        # (for example curvature_rows, asymptotic_state_rows, qec_code_rows).
        # Falling back to the first top-level row list keeps the route-state
        # mirror from reporting false zero coverage when the ledger itself is
        # populated. Registry entries point only to executable ledger files, so
        # a top-level list here is the row collection rather than prose metadata.
        for key, val in obj.items():
            if isinstance(val, list) and all(isinstance(item, dict) for item in val):
                return len(val)
        return 0

    lines = [
        '# Route-state summary (generated)',
        '',
        'Generated from `CANDIDATE-ROUTE-STATE-LEDGER.json` plus `LEDGER-FAMILY-REGISTRY.json`. Do not edit directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{route_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(rows)}`",
        f"- Registered route-layer families: `{len(registry.get('registry_rows', []))}`",
        f"- Measurement-model rows: `{ledger_count('MEASUREMENT-MODEL-LEDGER.json')}`",
        f"- Systematic-uncertainty rows: `{ledger_count('SYSTEMATIC-UNCERTAINTY-LEDGER.json')}`",
        f"- Calibration-traceability rows: `{ledger_count('CALIBRATION-TRACEABILITY-LEDGER.json')}`",
        f"- Validity-domain rows: `{ledger_count('DOMAIN-OF-VALIDITY-LEDGER.json')}`",
        f"- Transportability rows: `{ledger_count('TRANSPORTABILITY-LEDGER.json')}`",
        f"- Extrapolation-fence rows: `{ledger_count('EXTRAPOLATION-FENCE-LEDGER.json')}`",
        '',
        '## State counts',
        '',
    ]
    for state, count in sorted(state_counts.items()):
        lines.append(f"- `{state}`: `{count}`")

    lines += ['', '## Registered layer-family row counts', '', '| Family | OQ | Ledgers | Ledger rows | Route fields | Policy | Max cardinality |', '|---|---|---:|---:|---:|---|---:|']
    for fam in registry.get('registry_rows', []):
        ledger_total = sum(ledger_count(rel) for rel in fam.get('ledger_files', []))
        lines.append(f"| `{fam.get('family_id')}` | `{fam.get('open_question_id','')}` | `{len(fam.get('ledger_files', []))}` | `{ledger_total}` | `{len(fam.get('route_fields', []))}` | `{fam.get('cardinality_policy','')}` | `{fam.get('maximum_route_field_cardinality','')}` |")

    registry_rows = registry.get('registry_rows', [])
    route_family_summaries = []
    for row in rows:
        active = []
        nonzero_field_total = 0
        for fam in registry_rows:
            field_counts = []
            for field in fam.get('route_fields', []):
                val = row.get(field, [])
                count = len(val) if isinstance(val, list) else 0
                if count:
                    field_counts.append(f"`{field}` = `{count}`")
                    nonzero_field_total += 1
            if field_counts:
                active.append((fam.get('family_id'), field_counts))
        route_family_summaries.append({
            'row': row,
            'active': active,
            'nonzero_field_total': nonzero_field_total,
            'empty_family_count': max(0, len(registry_rows) - len(active)),
        })

    lines += [
        '',
        '## Route rows by registered layer family',
        '',
        'Only registered families with nonzero route-field handles are expanded below. Empty family counts are summarized so this generated restart surface does not become a row-by-row bureaucracy mirror.',
        '',
        '| Route | State | Ceiling | Active families | Nonzero route fields | Empty families | Earliest blocker |',
        '|---|---|---|---:|---:|---:|---|',
    ]
    for summary in route_family_summaries:
        row = summary['row']
        lines.append(
            f"| `{row.get('route_id')}` | `{row.get('authority_state')}` | `{row.get('promotion_ceiling')}` | `{len(summary['active'])}` | `{summary['nonzero_field_total']}` | `{summary['empty_family_count']}` | {row.get('earliest_blocker')} |"
        )

    lines += [
        '',
        '## Active route-family detail disposition',
        '',
        'Per-route active-family matrices are intentionally omitted from this generated restart surface. Every current route currently carries handles in every registered layer family, so expanding those matrices repeats the executable ledgers without adding decision value. Use the route table above for restart triage and inspect `CANDIDATE-ROUTE-STATE-LEDGER.json` plus family-specific ledgers for exact handle IDs.',
        '',
    ]

    lines += ['', '## Compression rule', '', 'The route-state summary is a restart surface, not a full route-field matrix. Complete per-field custody remains in `CANDIDATE-ROUTE-STATE-LEDGER.json`, `LEDGER-FAMILY-REGISTRY.json`, and the executable lint/replay checks. This surface expands only nonzero family handles and keeps zero-family coverage as counts.', '', '## Non-promotion rule', '', 'This generated surface is descriptive only. A route row may not spend higher authority because it appears in this table. Promotion still requires the state-machine entry conditions, public-record custody, observed-sector obligations, negative controls, empirical deltas, residual caps, and every route-support family declared in `LEDGER-FAMILY-REGISTRY.json`.', '']
    (root / 'docs/30-program/route-state-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/route-state-summary.generated.md')

def write_promotion_and_recovery_summary(root: Path) -> None:
    gate_ledger = json.loads((root / 'PROMOTION-GATE-LEDGER.json').read_text())
    osr_ledger = json.loads((root / 'OBSERVED-SECTOR-RECOVERY-LEDGER.json').read_text())
    forecast_ledger = json.loads((root / 'DISCRIMINATOR-FORECAST-LEDGER.json').read_text())
    gates = gate_ledger.get('gate_rows', [])
    obligations = osr_ledger.get('obligations', [])
    forecasts = forecast_ledger.get('forecast_rows', [])
    lines = [
        '# Promotion / recovery / forecast summary (generated)',
        '',
        'Generated from `PROMOTION-GATE-LEDGER.json`, `OBSERVED-SECTOR-RECOVERY-LEDGER.json`, and `DISCRIMINATOR-FORECAST-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{gate_ledger.get('revision', '<missing>')}`",
        f"- Promotion gates: `{len(gates)}`",
        f"- Observed-sector obligations: `{len(obligations)}`",
        f"- Forecast rows: `{len(forecasts)}`",
        f"- No current route S4/S5: `{gate_ledger.get('no_current_route_s4_or_s5')}`",
        f"- No obligation closed for S5: `{osr_ledger.get('no_obligation_closed_for_s5')}`",
        '',
        '## Promotion gates',
        '',
        '| Gate | From | To | Blocking if missing |',
        '|---|---:|---:|---|',
    ]
    for gate in gates:
        block = str(gate.get('blocking_if_missing', '')).replace('\n',' ')
        if len(block) > 100:
            block = block[:97] + '...'
        lines.append(f"| `{gate.get('gate_id')}` | `{gate.get('from_state')}` | `{gate.get('to_state')}` | {block} |")
    lines += ['', '## Observed-sector obligations', '', '| Obligation | Routes touching | Current state |', '|---|---:|---|']
    for row in obligations:
        state = str(row.get('current_archive_state','')).replace('\n',' ')
        if len(state) > 100:
            state = state[:97] + '...'
        lines.append(f"| `{row.get('obligation_id')}` | `{len(row.get('route_ids_touching', []))}` | {state} |")
    lines += ['', '## Forecast rows', '', '| Forecast | Route | Current max credit |', '|---|---|---:|']
    for row in forecasts:
        lines.append(f"| `{row.get('forecast_id')}` | `{row.get('route_id')}` | `{row.get('current_maximum_credit')}` |")
    lines += ['', '## Non-promotion rule', '', 'A forecasted artifact, observed-sector recovery slice, or gate-local gain may update a route row only through the executable ledgers. It cannot be imported as free-standing closure language.', '']
    out = root / 'docs/30-program/promotion-and-recovery-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/promotion-and-recovery-summary.generated.md')


def write_decision_experiment_summary(root: Path) -> None:
    decision_ledger = json.loads((root / 'DECISION-EXPERIMENT-LEDGER.json').read_text())
    experiments = decision_ledger.get('decision_experiments', [])
    route_counts = {}
    ceiling_counts = {}
    for exp in experiments:
        for rid in exp.get('route_ids', []):
            route_counts[rid] = route_counts.get(rid, 0) + 1
        for outcome in exp.get('outcome_effects', []):
            ceiling = outcome.get('promotion_ceiling', '<missing>')
            ceiling_counts[ceiling] = ceiling_counts.get(ceiling, 0) + 1
    lines = [
        '# Decision-experiment summary (generated)',
        '',
        'Generated from `DECISION-EXPERIMENT-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing decision-experiment rows.',
        '',
        f"- Revision: `{decision_ledger.get('revision', '<missing>')}`",
        f"- Decision experiments: `{len(experiments)}`",
        f"- Route rows touched: `{len(route_counts)}`",
        '',
        '## Outcome ceiling counts',
        '',
    ]
    for ceiling in sorted(ceiling_counts):
        lines.append(f'- `{ceiling}`: `{ceiling_counts[ceiling]}`')
    lines += ['', '## Experiments', '', '| Experiment | Stage | Routes | Controls | Delta hooks | Carriers | Protocols | Max outcome ceiling |', '|---|---|---:|---:|---:|---:|---:|---:|']
    state_order = {'S0':0,'S1':1,'S2':2,'S3':3,'S4':4,'S5':5}
    for exp in experiments:
        ceilings = [out.get('promotion_ceiling', '') for out in exp.get('outcome_effects', [])]
        max_ceiling = ''
        if ceilings:
            max_ceiling = max(ceilings, key=lambda c: state_order.get(c, -1))
        stage = str(exp.get('decision_stage', '')).replace('\n', ' ')
        if len(stage) > 80:
            stage = stage[:77] + '...'
        lines.append(f"| `{exp.get('experiment_id')}` | {stage} | `{len(exp.get('route_ids', []))}` | `{len(exp.get('negative_controls', []))}` | `{len(exp.get('empirical_delta_hooks', []))}` | `{len(exp.get('public_record_carrier_ids', []))}` | `{len(exp.get('acquisition_protocol_ids', []))}` | `{max_ceiling}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'A decision-experiment row describes possible outcome effects; it does not itself update route state. A realized outcome must still enter through the empirical-delta ledger, public-record carriers, acquisition protocols, claim bindings, negative controls, promotion gates, observed-sector obligations, and route-row residual caps.',
        '',
    ]
    out = root / 'docs/30-program/decision-experiment-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/decision-experiment-summary.generated.md')



def write_record_carrier_and_acquisition_summary(root: Path) -> None:
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    carrier_ledger = json.loads((root / 'PUBLIC-RECORD-CARRIER-LEDGER.json').read_text())
    protocol_ledger = json.loads((root / 'ACQUISITION-PROTOCOL-LEDGER.json').read_text())
    binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    carriers = carrier_ledger.get('carrier_rows', [])
    protocols = protocol_ledger.get('protocol_rows', [])
    bindings = binding_ledger.get('binding_rows', [])
    route_rows = route_ledger.get('route_rows', [])
    level_counts = {}
    for carrier in carriers:
        level = carrier.get('publicness_level', '<missing>')
        level_counts[level] = level_counts.get(level, 0) + 1
    protocol_counts_by_stage = {}
    for protocol in protocols:
        stage = protocol.get('acquisition_stage', '<missing>')
        protocol_counts_by_stage[stage] = protocol_counts_by_stage.get(stage, 0) + 1
    carrier_route_counts = {c.get('carrier_id', ''): len(c.get('route_ids', [])) for c in carriers}
    protocol_route_counts = {p.get('protocol_id', ''): len(p.get('route_ids', [])) for p in protocols}
    lines = [
        '# Public-record carrier / acquisition / binding summary (generated)',
        '',
        'Generated from `PUBLIC-RECORD-CARRIER-LEDGER.json`, `ACQUISITION-PROTOCOL-LEDGER.json`, `CLAIM-ROUTE-BINDING-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{carrier_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Public-record carriers: `{len(carriers)}`",
        f"- Acquisition protocols: `{len(protocols)}`",
        f"- Claim-route bindings: `{len(bindings)}`",
        '',
        '## Publicness level counts',
        '',
    ]
    for level in sorted(level_counts):
        lines.append(f'- `{level}`: `{level_counts[level]}`')
    lines += ['', '## Carrier rows', '', '| Carrier | Publicness | Routes | Max credit |', '|---|---|---:|---:|']
    for carrier in carriers:
        lines.append(f"| `{carrier.get('carrier_id')}` | `{carrier.get('publicness_level')}` | `{carrier_route_counts.get(carrier.get('carrier_id'), 0)}` | `{carrier.get('maximum_authority_credit')}` |")
    lines += ['', '## Acquisition protocols', '', '| Protocol | Stage | Routes | Max route effect |', '|---|---|---:|---:|']
    for protocol in protocols:
        stage = str(protocol.get('acquisition_stage','')).replace('\n',' ')
        if len(stage) > 80:
            stage = stage[:77] + '...'
        lines.append(f"| `{protocol.get('protocol_id')}` | {stage} | `{protocol_route_counts.get(protocol.get('protocol_id'), 0)}` | `{protocol.get('maximum_route_effect')}` |")
    lines += ['', '## Claim-route bindings', '', '| Binding | Claim/OQ | Routes | Carriers | Protocols |', '|---|---|---:|---:|---:|']
    for binding in bindings:
        lines.append(f"| `{binding.get('binding_id')}` | `{binding.get('claim_or_oq_id')}` | `{len(binding.get('route_ids', []))}` | `{len(binding.get('carrier_ids', []))}` | `{len(binding.get('protocol_ids', []))}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Carrier coverage and acquisition coverage are evidence-custody constraints. They do not promote a route unless the route row, empirical delta, negative controls, promotion gate, observed-sector obligations, and claim binding all allow the stronger wording.',
        '',
    ]
    out = root / 'docs/30-program/record-carrier-and-acquisition-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/record-carrier-and-acquisition-summary.generated.md')


def _claim_kind(identifier: str) -> str:
    if str(identifier).startswith('OQ-'):
        return 'open-question'
    if str(identifier).startswith('CL-'):
        return 'claim'
    return 'claim-or-open-question'


def write_authority_dependency_graph(root: Path) -> None:
    """Generate an explicit dependency graph for route authority and rollback propagation."""
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    carrier_ledger = json.loads((root / 'PUBLIC-RECORD-CARRIER-LEDGER.json').read_text())
    protocol_ledger = json.loads((root / 'ACQUISITION-PROTOCOL-LEDGER.json').read_text())
    binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    rollback_ledger = json.loads((root / 'ROLLBACK-PROPAGATION-LEDGER.json').read_text())
    evidence_ledger_path = root / 'EVIDENCE-UNIT-LEDGER.json'
    independence_ledger_path = root / 'INDEPENDENCE-ASSUMPTION-LEDGER.json'
    credit_ledger_path = root / 'CREDIT-ALLOCATION-LEDGER.json'
    contrast_ledger_path = root / 'CONTRAST-CLASS-LEDGER.json'
    update_ledger_path = root / 'LIKELIHOOD-UPDATE-LEDGER.json'
    prior_ledger_path = root / 'PRIOR-SENSITIVITY-LEDGER.json'
    measurement_ledger_path = root / 'MEASUREMENT-MODEL-LEDGER.json'
    systematic_ledger_path = root / 'SYSTEMATIC-UNCERTAINTY-LEDGER.json'
    calibration_ledger_path = root / 'CALIBRATION-TRACEABILITY-LEDGER.json'
    causal_mechanism_ledger_path = root / 'CAUSAL-MECHANISM-LEDGER.json'
    intervention_protocol_ledger_path = root / 'INTERVENTION-PROTOCOL-LEDGER.json'
    counterfactual_robustness_ledger_path = root / 'COUNTERFACTUAL-ROBUSTNESS-LEDGER.json'
    selection_ledger_path = root / 'SELECTION-FUNCTION-LEDGER.json'
    multiplicity_ledger_path = root / 'MULTIPLICITY-CONTROL-LEDGER.json'
    reporting_bias_ledger_path = root / 'REPORTING-BIAS-LEDGER.json'
    model_capacity_ledger_path = root / 'MODEL-CAPACITY-LEDGER.json'
    complexity_penalty_ledger_path = root / 'COMPLEXITY-PENALTY-LEDGER.json'
    predictive_generalization_ledger_path = root / 'PREDICTIVE-GENERALIZATION-LEDGER.json'
    semantic_term_ledger_path = root / 'SEMANTIC-TERM-LEDGER.json'
    ontology_commitment_ledger_path = root / 'ONTOLOGY-COMMITMENT-LEDGER.json'
    claim_language_permission_ledger_path = root / 'CLAIM-LANGUAGE-PERMISSION-LEDGER.json'
    social_authority_ledger_path = root / 'SOCIAL-AUTHORITY-LEDGER.json'
    review_replication_ledger_path = root / 'REVIEW-REPLICATION-LEDGER.json'
    consensus_elicitation_ledger_path = root / 'CONSENSUS-ELICITATION-LEDGER.json'
    computational_reproducibility_ledger_path = root / 'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json'
    numerical_stability_ledger_path = root / 'NUMERICAL-STABILITY-LEDGER.json'
    software_supply_chain_ledger_path = root / 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json'
    forecast_ledger_path = root / 'DISCRIMINATOR-FORECAST-LEDGER.json'
    decision_ledger_path = root / 'DECISION-EXPERIMENT-LEDGER.json'
    empirical_delta_ledger_path = root / 'EMPIRICAL-DELTA-LEDGER.json'
    evidence_ledger = json.loads(evidence_ledger_path.read_text()) if evidence_ledger_path.exists() else {'evidence_units': []}
    independence_ledger = json.loads(independence_ledger_path.read_text()) if independence_ledger_path.exists() else {'independence_rows': []}
    credit_ledger = json.loads(credit_ledger_path.read_text()) if credit_ledger_path.exists() else {'credit_rows': []}
    contrast_ledger = json.loads(contrast_ledger_path.read_text()) if contrast_ledger_path.exists() else {'contrast_rows': []}
    update_ledger = json.loads(update_ledger_path.read_text()) if update_ledger_path.exists() else {'update_rows': []}
    prior_ledger = json.loads(prior_ledger_path.read_text()) if prior_ledger_path.exists() else {'prior_rows': []}
    measurement_ledger = json.loads(measurement_ledger_path.read_text()) if measurement_ledger_path.exists() else {'measurement_model_rows': []}
    systematic_ledger = json.loads(systematic_ledger_path.read_text()) if systematic_ledger_path.exists() else {'systematic_rows': []}
    calibration_ledger = json.loads(calibration_ledger_path.read_text()) if calibration_ledger_path.exists() else {'calibration_rows': []}
    causal_mechanism_ledger = json.loads(causal_mechanism_ledger_path.read_text()) if causal_mechanism_ledger_path.exists() else {'mechanism_rows': []}
    intervention_protocol_ledger = json.loads(intervention_protocol_ledger_path.read_text()) if intervention_protocol_ledger_path.exists() else {'intervention_rows': []}
    counterfactual_robustness_ledger = json.loads(counterfactual_robustness_ledger_path.read_text()) if counterfactual_robustness_ledger_path.exists() else {'counterfactual_rows': []}
    selection_ledger = json.loads(selection_ledger_path.read_text()) if selection_ledger_path.exists() else {'selection_rows': []}
    multiplicity_ledger = json.loads(multiplicity_ledger_path.read_text()) if multiplicity_ledger_path.exists() else {'multiplicity_rows': []}
    reporting_bias_ledger = json.loads(reporting_bias_ledger_path.read_text()) if reporting_bias_ledger_path.exists() else {'bias_rows': []}
    model_capacity_ledger = json.loads(model_capacity_ledger_path.read_text()) if model_capacity_ledger_path.exists() else {'capacity_rows': []}
    complexity_penalty_ledger = json.loads(complexity_penalty_ledger_path.read_text()) if complexity_penalty_ledger_path.exists() else {'complexity_rows': []}
    predictive_generalization_ledger = json.loads(predictive_generalization_ledger_path.read_text()) if predictive_generalization_ledger_path.exists() else {'generalization_rows': []}
    semantic_term_ledger = json.loads(semantic_term_ledger_path.read_text()) if semantic_term_ledger_path.exists() else {'semantic_rows': []}
    ontology_commitment_ledger = json.loads(ontology_commitment_ledger_path.read_text()) if ontology_commitment_ledger_path.exists() else {'commitment_rows': []}
    claim_language_permission_ledger = json.loads(claim_language_permission_ledger_path.read_text()) if claim_language_permission_ledger_path.exists() else {'permission_rows': []}
    social_authority_ledger = json.loads(social_authority_ledger_path.read_text()) if social_authority_ledger_path.exists() else {'social_rows': []}
    review_replication_ledger = json.loads(review_replication_ledger_path.read_text()) if review_replication_ledger_path.exists() else {'review_rows': []}
    consensus_elicitation_ledger = json.loads(consensus_elicitation_ledger_path.read_text()) if consensus_elicitation_ledger_path.exists() else {'consensus_rows': []}
    computational_reproducibility_ledger = json.loads(computational_reproducibility_ledger_path.read_text()) if computational_reproducibility_ledger_path.exists() else {'reproducibility_rows': []}
    numerical_stability_ledger = json.loads(numerical_stability_ledger_path.read_text()) if numerical_stability_ledger_path.exists() else {'stability_rows': []}
    software_supply_chain_ledger = json.loads(software_supply_chain_ledger_path.read_text()) if software_supply_chain_ledger_path.exists() else {'supply_chain_rows': []}
    forecast_ledger = json.loads(forecast_ledger_path.read_text()) if forecast_ledger_path.exists() else {'forecast_rows': []}
    decision_ledger = json.loads(decision_ledger_path.read_text()) if decision_ledger_path.exists() else {'decision_experiments': []}
    empirical_delta_ledger = json.loads(empirical_delta_ledger_path.read_text()) if empirical_delta_ledger_path.exists() else {'empirical_deltas': []}

    rows = []
    route_credit_by_id = {
        row.get('route_id', ''): row.get('promotion_ceiling') or row.get('authority_state', '')
        for row in route_ledger.get('route_rows', [])
    }
    evidence_unit_by_id = {
        row.get('evidence_unit_id', ''): row
        for row in evidence_ledger.get('evidence_units', [])
    }
    state_order = {'S0': 0, 'S1': 1, 'S2': 2, 'S3': 3, 'S4': 4, 'S5': 5}

    def max_state(states: list[str]) -> str:
        present = [state for state in states if state]
        if not present:
            return ''
        return max(present, key=lambda state: state_order.get(state, -1))

    def min_state(states: list[str]) -> str:
        present = [state for state in states if state]
        if not present:
            return ''
        return min(present, key=lambda state: state_order.get(state, 999))

    def add(source_kind: str, source_id: str, dependent_kind: str, dependent_id: str,
            dependency_kind: str, required_for: str, failure_effect: str,
            max_credit_transmitted: str) -> None:
        if not source_id or not dependent_id:
            return
        rows.append({
            'edge_id': f'AD-{len(rows) + 1:04d}',
            'source_kind': source_kind,
            'source_id': source_id,
            'dependent_kind': dependent_kind,
            'dependent_id': dependent_id,
            'dependency_kind': dependency_kind,
            'required_for': required_for,
            'failure_effect': failure_effect,
            'max_credit_transmitted': max_credit_transmitted,
        })

    for route in route_ledger.get('route_rows', []):
        rid = route.get('route_id', '')
        ceiling = route.get('promotion_ceiling', '')
        for carrier_id in route.get('public_record_carrier_ids', []):
            add('carrier', carrier_id, 'route', rid, 'record-carrier-requirement',
                'public-record credit and route evidence custody',
                'freeze carrier-dependent authority and run associated rollback rows', ceiling)
        for protocol_id in route.get('acquisition_protocol_ids', []):
            add('protocol', protocol_id, 'route', rid, 'acquisition-protocol-requirement',
                'record acquisition, replay, and transformation credit',
                'downgrade route to the most restrictive surviving replay-backed state', ceiling)
        for control_id in route.get('adversarial_countermodels', []):
            add('negative-control', control_id, 'route', rid, 'negative-control-condition',
                'state-machine promotion and residual-cap spending',
                'block promotion or roll back to the state before the failed negative control', ceiling)
        for gate_id in route.get('promotion_gate_ids', []):
            add('promotion-gate', gate_id, 'route', rid, 'promotion-gate-condition',
                'route-state entry or retention condition',
                'forbid compensatory promotion and recompute route state', ceiling)
        for obligation_id in route.get('observed_sector_obligations', []):
            add('observed-sector-obligation', obligation_id, 'route', rid, 'observed-sector-condition',
                'observed-sector recovery and ToE-scope wording',
                'cap route below closure until recovery burden is repaired', ceiling)
        for defeater_id in route.get('defeater_ids', []):
            add('defeater', defeater_id, 'route', rid, 'defeater-attack',
                'loss-of-authority detection and nonmonotonic revision',
                'activate rollback rule and remove defeated authority wording', ceiling)
        for severity_id in route.get('severity_test_ids', []):
            add('severity-test', severity_id, 'route', rid, 'severity-test-condition',
                'claim that positive evidence survived a severe test rather than a friendly fit',
                'convert the result to weak support or invoke declared rollback on failure', ceiling)
        for evidence_unit_id in route.get('evidence_unit_ids', []):
            evidence_unit = evidence_unit_by_id.get(evidence_unit_id, {})
            evidence_effect = min_state([ceiling, evidence_unit.get('maximum_credit', '')]) or ceiling
            add('evidence-unit', evidence_unit_id, 'route', rid, 'evidence-unit-support',
                'accounted support atom for route credit without double-counting',
                'remove or merge correlated support when the evidence unit is defeated or already counted', evidence_effect)
        for independence_id in route.get('independence_assumption_ids', []):
            add('independence-assumption', independence_id, 'route', rid, 'independence-assumption-condition',
                'whether multiple evidence units may aggregate as independent support',
                'treat support as correlated and cap aggregation until the assumption stress test passes', ceiling)
        for credit_id in route.get('credit_allocation_ids', []):
            add('credit-allocation', credit_id, 'route', rid, 'credit-allocation-rule',
                'route-local no-double-counting and no-compensation credit accounting',
                'recompute route support using the most restrictive surviving credit allocation', ceiling)
        for contrast_id in route.get('contrast_class_ids', []):
            add('contrast-class', contrast_id, 'route', rid, 'contrast-class-condition',
                'declared rival/null/decoy set and quotient policy for route support',
                'freeze or narrow update wording until the contrast denominator is restored', ceiling)
        for update_id in route.get('likelihood_update_ids', []):
            add('likelihood-update', update_id, 'route', rid, 'likelihood-update-rule',
                'route-local likelihood, benchmark, proof-survival, or qualitative update object',
                'remove or cap route update language when the update object is underdeclared or defeated', ceiling)
        for prior_id in route.get('prior_sensitivity_ids', []):
            add('prior-sensitivity', prior_id, 'route', rid, 'prior-sensitivity-condition',
                'prior, nuisance, quotient, regulator, detector, or model-class sensitivity stress test',
                'cap, merge, or roll back support when plausible prior variations change the result', ceiling)
        for measurement_id in route.get('measurement_model_ids', []):
            add('measurement-model', measurement_id, 'route', rid, 'measurement-model-condition',
                'declared measurand/recoverand and raw-record-to-observable transformation',
                'freeze update/support wording until the measurement model is restored or replaced', ceiling)
        for systematic_id in route.get('systematic_uncertainty_ids', []):
            add('systematic-uncertainty', systematic_id, 'route', rid, 'systematic-uncertainty-condition',
                'systematic-error budget, nuisance stress test, and residual cap for route support',
                'cap, merge, or roll back support when the systematic budget fails', ceiling)
        for calibration_id in route.get('calibration_traceability_ids', []):
            add('calibration-traceability', calibration_id, 'route', rid, 'calibration-traceability-condition',
                'calibration/proof/benchmark/catalog traceability chain for public update language',
                'freeze calibration-dependent update language and invoke rollback until traceability is repaired', ceiling)
        for domain_id in route.get('validity_domain_ids', []):
            add('validity-domain', domain_id, 'route', rid, 'validity-domain-condition',
                'declared source/target domain and preserved-invariant boundary for support language',
                'freeze generalized support until source-domain and target-domain limits are restored', ceiling)
        for transport_id in route.get('transportability_ids', []):
            add('transportability', transport_id, 'route', rid, 'transportability-condition',
                'source-to-target support transfer and domain-shift stress testing',
                'treat evidence as source-domain-only until transport is restored', ceiling)
        for fence_id in route.get('extrapolation_fence_ids', []):
            add('extrapolation-fence', fence_id, 'route', rid, 'extrapolation-fence-condition',
                'forbidden-inference and escalation-condition control for local-to-global claims',
                'quarantine or roll back extrapolated support wording when the fence is violated', ceiling)
        for mechanism_id in route.get('causal_mechanism_ids', []):
            add('causal-mechanism', mechanism_id, 'route', rid, 'causal-mechanism-condition',
                'declared causal question, mechanism structure, confounding controls, and invariance test',
                'freeze mechanism/cause wording until the causal-mechanism row is restored', ceiling)
        for intervention_id in route.get('intervention_protocol_ids', []):
            add('intervention-protocol', intervention_id, 'route', rid, 'intervention-protocol-condition',
                'declared intervention, perturbation, ablation, natural-experiment, or custody status',
                'downgrade intervention-backed wording to the declared noninterventional status', ceiling)
        for counterfactual_id in route.get('counterfactual_robustness_ids', []):
            add('counterfactual-robustness', counterfactual_id, 'route', rid, 'counterfactual-robustness-condition',
                'declared counterfactual query, alternative worlds, invariance requirement, and failure modes',
                'cap or roll back counterfactual robustness wording when the row fails', ceiling)
        for selection_id in route.get('selection_function_ids', []):
            add('selection-function', selection_id, 'route', rid, 'selection-function-condition',
                'declared search frame, inclusion/exclusion rule, missingness, and selection freeze for selected-positive language',
                'freeze discovery/surprise language until the selection denominator is restored', ceiling)
        for multiplicity_id in route.get('multiplicity_control_ids', []):
            add('multiplicity-control', multiplicity_id, 'route', rid, 'multiplicity-control-condition',
                'effective trial/search family and look-elsewhere or forking-paths control',
                'downgrade local positives to multiplicity-capped support until global control is restored', ceiling)
        for bias_id in route.get('reporting_bias_ids', []):
            add('reporting-bias', bias_id, 'route', rid, 'reporting-bias-condition',
                'file-drawer, survivorship, positive-result, null-visibility, and missing-record risk',
                'cap or roll back support language when missing nulls or failed attempts change the denominator', ceiling)
        for cap_id in route.get('model_capacity_ids', []):
            add('model-capacity', cap_id, 'route', rid, 'model-capacity-condition',
                'declared hypothesis-family flexibility, effective degrees of freedom, and capacity diagnostic for fit language',
                'freeze fit/simplicity support until model capacity is declared or capped', ceiling)
        for cpx_id in route.get('complexity_penalty_ids', []):
            add('complexity-penalty', cpx_id, 'route', rid, 'complexity-penalty-condition',
                'fit term charged against description length, Occam factor, information criterion, regularizer, or explicit capacity cap',
                'downgrade best-fit or parsimony language until the complexity penalty is restored', ceiling)
        for gen_id in route.get('generalization_validation_ids', []):
            add('generalization-validation', gen_id, 'route', rid, 'generalization-validation-condition',
                'holdout, forecast, transfer, or out-of-domain validation for predictive/generalization language',
                'demote predictive/generalization wording to retrospective fit when validation fails', ceiling)
        for sem_id in route.get('semantic_term_ids', []):
            add('semantic-term', sem_id, 'route', rid, 'semantic-term-condition',
                'controlled-term meaning, public-vs-native vocabulary, and semantic-stability test for route wording',
                'freeze semantic / equivalence / native-language wording until the term row is restored', ceiling)
        for ont_id in route.get('ontology_commitment_ids', []):
            add('ontology-commitment', ont_id, 'route', rid, 'ontology-commitment-condition',
                'declared structural, operational, package-local, effective, or custody-only ontology commitment',
                'downgrade ontology/realism/identity wording to the weakest surviving commitment row', ceiling)
        for perm_id in route.get('claim_language_permission_ids', []):
            add('claim-language-permission', perm_id, 'route', rid, 'claim-language-permission-condition',
                'allowed and forbidden claim language for route-local support, identity, equivalence, ontology, and closure wording',
                'remove unlicensed claim language and invoke the declared rollback handle', ceiling)
        for social_id in route.get('social_authority_ids', []):
            add('social-authority', social_id, 'route', rid, 'social-authority-condition',
                'peer-review, expert-testimony, institutional, citation, and field-uptake denominator for route wording',
                'remove social-authority-backed wording until review/testimony denominator is restored', ceiling)
        for review_id in route.get('review_replication_ids', []):
            add('review-replication', review_id, 'route', rid, 'review-replication-condition',
                'publication review, independent reanalysis, registered-report status, or replication target for route wording',
                'downgrade review/replication language to the strongest surviving target-local status', ceiling)
        for consensus_id in route.get('consensus_elicitation_ids', []):
            add('consensus-elicitation', consensus_id, 'route', rid, 'consensus-elicitation-condition',
                'declared expert/community denominator, dissent visibility, and aggregation rule for consensus wording',
                'freeze consensus or field-acceptance language until elicitation denominator is restored', ceiling)
        for crp_id in route.get('computational_reproducibility_ids', []):
            add('computational-reproducibility', crp_id, 'route', rid, 'computational-reproducibility-condition',
                'code, workflow, container, solver, proof-replay, or generated-artifact replay denominator for route wording',
                'freeze computational-artifact-backed wording until replay and environment controls are restored', ceiling)
        for nst_id in route.get('numerical_stability_ids', []):
            add('numerical-stability', nst_id, 'route', rid, 'numerical-stability-condition',
                'declared tolerance, solver, seed, floating-point, and platform-stability denominator for route wording',
                'cap numerical or pipeline-backed support when stability checks fail', ceiling)
        for ssc_id in route.get('software_supply_chain_ids', []):
            add('software-supply-chain', ssc_id, 'route', rid, 'software-supply-chain-condition',
                'source, dependency, build, container, workflow, and artifact-provenance denominator for route wording',
                'remove software-backed support until provenance or build integrity is restored', ceiling)

    for forecast in forecast_ledger.get('forecast_rows', []):
        fid = forecast.get('forecast_id', '')
        rid = forecast.get('route_id', '')
        add('forecast', fid, 'route', rid, 'forecast-route-condition',
            'route-facing discriminator forecast and prospective artifact target',
            'freeze forecast-backed route-update wording until the forecast row is restored or superseded',
            forecast.get('current_maximum_credit') or route_credit_by_id.get(rid, ''))

    for experiment in decision_ledger.get('decision_experiments', []):
        eid = experiment.get('experiment_id', '')
        outcome_ceiling = max_state([
            outcome.get('promotion_ceiling', '')
            for outcome in experiment.get('outcome_effects', [])
        ])
        for rid in experiment.get('route_ids', []):
            add('decision-experiment', eid, 'route', rid, 'decision-experiment-route-condition',
                'route-facing decision experiment and outcome-effect map',
                'freeze decision-experiment route-update wording until the experiment row and outcome map are restored',
                outcome_ceiling or route_credit_by_id.get(rid, ''))

    for delta in empirical_delta_ledger.get('empirical_deltas', []):
        did = delta.get('delta_id', '')
        effect = delta.get('promotion_ceiling', '') or route_credit_by_id.get(delta.get('route_id', ''), '')
        for rid in delta.get('route_ids', []):
            add('empirical-delta', did, 'route', rid, 'empirical-delta-route-condition',
                'route-facing realized/source-pressure delta for state, rollback, and candidate-native wording',
                'freeze or downgrade route support affected by the empirical-delta row until its public/source-pressure record is repaired',
                effect or route_credit_by_id.get(rid, ''))


    for binding in binding_ledger.get('binding_rows', []):
        target_id = binding.get('claim_or_oq_id', '')
        target_kind = _claim_kind(target_id)
        effect = binding.get('maximum_authority_effect', '') or 'bounded by binding row' or 'bounded by binding row'
        for rid in binding.get('route_ids', []):
            add('route', rid, target_kind, target_id, 'claim-route-support',
                f'claim or open-question authority under {binding.get("binding_id")}',
                'remove or restate dependent claim wording when route authority is lost', effect)
        for carrier_id in binding.get('carrier_ids', []):
            add('carrier', carrier_id, target_kind, target_id, 'claim-carrier-support',
                f'claim/public-record custody under {binding.get("binding_id")}',
                'freeze public-record closure wording until carrier custody is repaired', effect)
        for protocol_id in binding.get('protocol_ids', []):
            add('protocol', protocol_id, target_kind, target_id, 'claim-protocol-support',
                f'claim/acquisition replay under {binding.get("binding_id")}',
                'freeze replay-dependent claim wording until protocol pass is restored', effect)
        for domain_id in binding.get('validity_domain_ids', []):
            add('validity-domain', domain_id, target_kind, target_id, 'validity-domain-claim-condition',
                f'claim validity-domain ceiling under {binding.get("binding_id")}',
                'freeze generalized claim wording until domain bounds are restored', effect)
        for transport_id in binding.get('transportability_ids', []):
            add('transportability', transport_id, target_kind, target_id, 'transportability-claim-condition',
                f'claim transportability ceiling under {binding.get("binding_id")}',
                'remove transported claim wording until source-to-target map is restored', effect)
        for fence_id in binding.get('extrapolation_fence_ids', []):
            add('extrapolation-fence', fence_id, target_kind, target_id, 'extrapolation-fence-claim-condition',
                f'claim extrapolation fence under {binding.get("binding_id")}',
                'quarantine claim wording that violates forbidden-inference rows', effect)
        for mechanism_id in binding.get('causal_mechanism_ids', []):
            add('causal-mechanism', mechanism_id, target_kind, target_id, 'causal-mechanism-claim-condition',
                f'claim causal-mechanism denominator under {binding.get("binding_id")}',
                'freeze mechanism/cause claim wording until the causal denominator is restored', effect)
        for intervention_id in binding.get('intervention_protocol_ids', []):
            add('intervention-protocol', intervention_id, target_kind, target_id, 'intervention-protocol-claim-condition',
                f'claim intervention-status denominator under {binding.get("binding_id")}',
                'freeze intervention/natural-experiment/ablation wording until the intervention row is restored', effect)
        for counterfactual_id in binding.get('counterfactual_robustness_ids', []):
            add('counterfactual-robustness', counterfactual_id, target_kind, target_id, 'counterfactual-robustness-claim-condition',
                f'claim counterfactual-robustness denominator under {binding.get("binding_id")}',
                'freeze counterfactual robustness wording until the counterfactual row is restored', effect)
        for selection_id in binding.get('selection_function_ids', []):
            add('selection-function', selection_id, target_kind, target_id, 'selection-function-claim-condition',
                f'claim selection-function denominator under {binding.get("binding_id")}',
                'freeze selected-positive or discovery claim wording until the selection denominator is restored', effect)
        for multiplicity_id in binding.get('multiplicity_control_ids', []):
            add('multiplicity-control', multiplicity_id, target_kind, target_id, 'multiplicity-control-claim-condition',
                f'claim multiplicity-control denominator under {binding.get("binding_id")}',
                'freeze surprise/anomaly/global-significance wording until multiplicity control is restored', effect)
        for bias_id in binding.get('reporting_bias_ids', []):
            add('reporting-bias', bias_id, target_kind, target_id, 'reporting-bias-claim-condition',
                f'claim reporting-bias denominator under {binding.get("binding_id")}',
                'freeze file-drawer-insensitive or convergence wording until reporting-bias audit is restored', effect)
        for cap_id in binding.get('model_capacity_ids', []):
            add('model-capacity', cap_id, target_kind, target_id, 'model-capacity-claim-condition',
                f'claim model-capacity denominator under {binding.get("binding_id")}',
                'freeze fit/simplicity/parsimony claim wording until capacity debt is restored', effect)
        for cpx_id in binding.get('complexity_penalty_ids', []):
            add('complexity-penalty', cpx_id, target_kind, target_id, 'complexity-penalty-claim-condition',
                f'claim complexity-penalty denominator under {binding.get("binding_id")}',
                'freeze best-fit / Occam / compression claim wording until penalty row is restored', effect)
        for gen_id in binding.get('generalization_validation_ids', []):
            add('generalization-validation', gen_id, target_kind, target_id, 'generalization-validation-claim-condition',
                f'claim predictive-generalization denominator under {binding.get("binding_id")}',
                'freeze prediction/generalization claim wording until validation row is restored', effect)
        for sem_id in binding.get('semantic_term_ids', []):
            add('semantic-term', sem_id, target_kind, target_id, 'semantic-term-claim-condition',
                f'claim semantic-term denominator under {binding.get("binding_id")}',
                'freeze term-equivalence or native-language claim wording until semantic binding is restored', effect)
        for ont_id in binding.get('ontology_commitment_ids', []):
            add('ontology-commitment', ont_id, target_kind, target_id, 'ontology-commitment-claim-condition',
                f'claim ontology-commitment denominator under {binding.get("binding_id")}',
                'freeze ontology / realism / identity wording until the commitment row is restored', effect)
        for perm_id in binding.get('claim_language_permission_ids', []):
            add('claim-language-permission', perm_id, target_kind, target_id, 'claim-language-permission-claim-condition',
                f'claim-language permission under {binding.get("binding_id")}',
                'remove forbidden wording or downgrade to the strongest explicitly allowed language', effect)
        for social_id in binding.get('social_authority_ids', []):
            add('social-authority', social_id, target_kind, target_id, 'social-authority-claim-condition',
                f'claim social-authority denominator under {binding.get("binding_id")}',
                'freeze peer-review, expert, prestige, or institutional wording until social-authority row is restored', effect)
        for review_id in binding.get('review_replication_ids', []):
            add('review-replication', review_id, target_kind, target_id, 'review-replication-claim-condition',
                f'claim review/replication denominator under {binding.get("binding_id")}',
                'freeze peer-reviewed / replicated / registered-report wording until review target is restored', effect)
        for consensus_id in binding.get('consensus_elicitation_ids', []):
            add('consensus-elicitation', consensus_id, target_kind, target_id, 'consensus-elicitation-claim-condition',
                f'claim consensus/elicitation denominator under {binding.get("binding_id")}',
                'freeze consensus or field-accepted wording until elicitation denominator and dissent visibility are restored', effect)
        for crp_id in binding.get('computational_reproducibility_ids', []):
            add('computational-reproducibility', crp_id, target_kind, target_id, 'computational-reproducibility-claim-condition',
                f'claim computational-reproducibility denominator under {binding.get("binding_id")}',
                'freeze code/workflow/container/replay claim wording until the computational row is restored', effect)
        for nst_id in binding.get('numerical_stability_ids', []):
            add('numerical-stability', nst_id, target_kind, target_id, 'numerical-stability-claim-condition',
                f'claim numerical-stability denominator under {binding.get("binding_id")}',
                'freeze numerical/solver/tolerance claim wording until stability rows are restored', effect)
        for ssc_id in binding.get('software_supply_chain_ids', []):
            add('software-supply-chain', ssc_id, target_kind, target_id, 'software-supply-chain-claim-condition',
                f'claim software-supply-chain denominator under {binding.get("binding_id")}',
                'freeze software-provenance or artifact-integrity claim wording until provenance is restored', effect)

    for credit in credit_ledger.get('credit_rows', []):
        effect = credit.get('maximum_authority_effect', '') or 'bounded by credit row'
        for target_id in credit.get('claim_or_oq_ids', []):
            add('credit-allocation', credit.get('credit_id', ''), _claim_kind(target_id), target_id, 'credit-allocation-claim-rule',
                'claim/open-question aggregation wording under no-double-counting credit allocation',
                'downgrade aggregate support language when credit allocation is missing or defeated', effect)
        for evidence_unit_id in credit.get('evidence_unit_ids', []):
            evidence_unit = evidence_unit_by_id.get(evidence_unit_id, {})
            evidence_effect = min_state([effect, evidence_unit.get('maximum_credit', '')]) or effect
            add('evidence-unit', evidence_unit_id, 'credit-allocation', credit.get('credit_id', ''), 'evidence-unit-support',
                'credit-row accounting for a support atom',
                'remove this unit from route aggregation if defeated or already counted', evidence_effect)
        for independence_id in credit.get('independence_assumption_ids', []):
            add('independence-assumption', independence_id, 'credit-allocation', credit.get('credit_id', ''), 'independence-assumption-condition',
                'credit-row aggregation permission or correlation cap',
                'collapse apparent independent support into one correlated cluster unless the stress test passes', effect)
        for contrast_id in credit.get('contrast_class_ids', []):
            add('contrast-class', contrast_id, 'credit-allocation', credit.get('credit_id', ''), 'contrast-class-condition',
                'credit-row contrast denominator and claim grain',
                'downgrade credit when the support denominator or quotient policy is underdeclared', effect)
        for update_id in credit.get('likelihood_update_ids', []):
            add('likelihood-update', update_id, 'credit-allocation', credit.get('credit_id', ''), 'likelihood-update-rule',
                'credit-row update object and maximum authority effect',
                'remove update-derived credit if the likelihood/benchmark/proof object is not replayable or contrastive', effect)
        for prior_id in credit.get('prior_sensitivity_ids', []):
            add('prior-sensitivity', prior_id, 'credit-allocation', credit.get('credit_id', ''), 'prior-sensitivity-condition',
                'credit-row prior sensitivity and nuisance-stack cap',
                'merge or cap credit when plausible prior variations change the result', effect)
        for measurement_id in credit.get('measurement_model_ids', []):
            add('measurement-model', measurement_id, 'credit-allocation', credit.get('credit_id', ''), 'measurement-model-condition',
                'credit-row measurand and transformation denominator',
                'remove or cap credit when the measurement model is missing or defeated', effect)
        for systematic_id in credit.get('systematic_uncertainty_ids', []):
            add('systematic-uncertainty', systematic_id, 'credit-allocation', credit.get('credit_id', ''), 'systematic-uncertainty-condition',
                'credit-row systematic uncertainty and residual cap',
                'merge, cap, or roll back credit when systematic risk survives', effect)
        for calibration_id in credit.get('calibration_traceability_ids', []):
            add('calibration-traceability', calibration_id, 'credit-allocation', credit.get('credit_id', ''), 'calibration-traceability-condition',
                'credit-row calibration/traceability chain',
                'remove calibration-dependent credit until traceability is repaired', effect)
        for domain_id in credit.get('validity_domain_ids', []):
            add('validity-domain', domain_id, 'credit-allocation', credit.get('credit_id', ''), 'validity-domain-condition',
                'credit-row source/target domain boundary',
                'remove generalized credit when domain bounds are missing or violated', effect)
        for transport_id in credit.get('transportability_ids', []):
            add('transportability', transport_id, 'credit-allocation', credit.get('credit_id', ''), 'transportability-condition',
                'credit-row source-to-target transfer condition',
                'treat credit as source-domain only when transportability fails', effect)
        for fence_id in credit.get('extrapolation_fence_ids', []):
            add('extrapolation-fence', fence_id, 'credit-allocation', credit.get('credit_id', ''), 'extrapolation-fence-condition',
                'credit-row forbidden-inference control',
                'remove or quarantine credit that violates an extrapolation fence', effect)
        for mechanism_id in credit.get('causal_mechanism_ids', []):
            add('causal-mechanism', mechanism_id, 'credit-allocation', credit.get('credit_id', ''), 'causal-mechanism-condition',
                'credit-row causal-mechanism denominator',
                'remove mechanism-derived credit when causal structure is missing or defeated', effect)
        for intervention_id in credit.get('intervention_protocol_ids', []):
            add('intervention-protocol', intervention_id, 'credit-allocation', credit.get('credit_id', ''), 'intervention-protocol-condition',
                'credit-row intervention-status denominator',
                'downgrade credit when direct intervention, perturbation, ablation, or natural-experiment status is overclaimed', effect)
        for counterfactual_id in credit.get('counterfactual_robustness_ids', []):
            add('counterfactual-robustness', counterfactual_id, 'credit-allocation', credit.get('credit_id', ''), 'counterfactual-robustness-condition',
                'credit-row counterfactual robustness denominator',
                'cap or remove credit when counterfactual invariance fails', effect)
        for selection_id in credit.get('selection_function_ids', []):
            add('selection-function', selection_id, 'credit-allocation', credit.get('credit_id', ''), 'selection-function-condition',
                'credit-row selection denominator and missingness cap',
                'remove discovery/surprise credit when the support was selected post hoc or denominator is missing', effect)
        for multiplicity_id in credit.get('multiplicity_control_ids', []):
            add('multiplicity-control', multiplicity_id, 'credit-allocation', credit.get('credit_id', ''), 'multiplicity-control-condition',
                'credit-row multiplicity or look-elsewhere adjustment',
                'downgrade local positive credit when global search control is missing or fails', effect)
        for bias_id in credit.get('reporting_bias_ids', []):
            add('reporting-bias', bias_id, 'credit-allocation', credit.get('credit_id', ''), 'reporting-bias-condition',
                'credit-row file-drawer and survivorship audit',
                'collapse visible-positive credit when missing nulls or failed attempts alter the denominator', effect)
        for cap_id in credit.get('model_capacity_ids', []):
            add('model-capacity', cap_id, 'credit-allocation', credit.get('credit_id', ''), 'model-capacity-condition',
                'credit-row model-capacity debt for fit and simplicity language',
                'remove capacity-dependent credit when flexible fit is unaccounted', effect)
        for cpx_id in credit.get('complexity_penalty_ids', []):
            add('complexity-penalty', cpx_id, 'credit-allocation', credit.get('credit_id', ''), 'complexity-penalty-condition',
                'credit-row complexity penalty for best-fit / parsimony language',
                'cap credit when penalty is missing or defeated', effect)
        for gen_id in credit.get('generalization_validation_ids', []):
            add('generalization-validation', gen_id, 'credit-allocation', credit.get('credit_id', ''), 'generalization-validation-condition',
                'credit-row holdout / forecast / transfer validation condition',
                'demote predictive credit to retrospective fit when validation fails', effect)
        for crp_id in credit.get('computational_reproducibility_ids', []):
            add('computational-reproducibility', crp_id, 'credit-allocation', credit.get('credit_id', ''), 'computational-reproducibility-condition',
                'credit-row computational artifact replay condition',
                'remove replay-dependent credit when computational reproducibility fails', effect)
        for nst_id in credit.get('numerical_stability_ids', []):
            add('numerical-stability', nst_id, 'credit-allocation', credit.get('credit_id', ''), 'numerical-stability-condition',
                'credit-row numerical stability condition',
                'cap numerical credit when solver or platform stability fails', effect)
        for ssc_id in credit.get('software_supply_chain_ids', []):
            add('software-supply-chain', ssc_id, 'credit-allocation', credit.get('credit_id', ''), 'software-supply-chain-condition',
                'credit-row software provenance and artifact integrity condition',
                'remove software-backed credit when provenance is missing or defeated', effect)

    for unit in evidence_ledger.get('evidence_units', []):
        for independence_id in unit.get('independence_assumption_ids', []):
            add('independence-assumption', independence_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'independence-assumption-condition',
                'evidence-unit independence and double-counting status',
                'mark the unit correlated or unspendable as independent support', unit.get('maximum_credit', ''))
        for contrast_id in unit.get('contrast_class_ids', []):
            add('contrast-class', contrast_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'contrast-class-condition',
                'evidence-unit support denominator and rival-set exposure',
                'downgrade the unit to noncontrastive background if rival set or quotient policy fails', unit.get('maximum_credit', ''))
        for update_id in unit.get('likelihood_update_ids', []):
            add('likelihood-update', update_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'likelihood-update-rule',
                'evidence-unit update object binding',
                'mark the unit as non-updating if the update object is only custody, metadata, or a generated wrapper', unit.get('maximum_credit', ''))
        for prior_id in unit.get('prior_sensitivity_ids', []):
            add('prior-sensitivity', prior_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'prior-sensitivity-condition',
                'evidence-unit prior and nuisance sensitivity',
                'cap or merge the unit if plausible prior variations alter support', unit.get('maximum_credit', ''))
        for measurement_id in unit.get('measurement_model_ids', []):
            add('measurement-model', measurement_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'measurement-model-condition',
                'evidence-unit measurand/recoverand and raw-to-observable binding',
                'mark the unit non-spendable if measurement model is missing or defeated', unit.get('maximum_credit', ''))
        for systematic_id in unit.get('systematic_uncertainty_ids', []):
            add('systematic-uncertainty', systematic_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'systematic-uncertainty-condition',
                'evidence-unit systematic uncertainty and residual cap',
                'cap or roll back the unit if systematic uncertainty is unbounded', unit.get('maximum_credit', ''))
        for calibration_id in unit.get('calibration_traceability_ids', []):
            add('calibration-traceability', calibration_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'calibration-traceability-condition',
                'evidence-unit calibration/traceability chain',
                'freeze calibration-dependent support if traceability breaks', unit.get('maximum_credit', ''))
        for domain_id in unit.get('validity_domain_ids', []):
            add('validity-domain', domain_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'validity-domain-condition',
                'evidence-unit source/target validity boundary',
                'mark the unit source-domain only when domain conditions fail', unit.get('maximum_credit', ''))
        for transport_id in unit.get('transportability_ids', []):
            add('transportability', transport_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'transportability-condition',
                'evidence-unit source-to-target transfer permission',
                'remove transported support when the transfer stress test fails', unit.get('maximum_credit', ''))
        for fence_id in unit.get('extrapolation_fence_ids', []):
            add('extrapolation-fence', fence_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'extrapolation-fence-condition',
                'evidence-unit forbidden-inference control',
                'quarantine extrapolated readings of this unit', unit.get('maximum_credit', ''))
        for mechanism_id in unit.get('causal_mechanism_ids', []):
            add('causal-mechanism', mechanism_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'causal-mechanism-condition',
                'evidence-unit causal/mechanistic denominator',
                'mark the unit noncausal or mechanism-capped when causal structure is missing or defeated', unit.get('maximum_credit', ''))
        for intervention_id in unit.get('intervention_protocol_ids', []):
            add('intervention-protocol', intervention_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'intervention-protocol-condition',
                'evidence-unit intervention/perturbation/ablation/natural-experiment status',
                'downgrade intervention-backed readings to the declared status', unit.get('maximum_credit', ''))
        for counterfactual_id in unit.get('counterfactual_robustness_ids', []):
            add('counterfactual-robustness', counterfactual_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'counterfactual-robustness-condition',
                'evidence-unit counterfactual query and invariance requirement',
                'cap or roll back counterfactual readings when robustness fails', unit.get('maximum_credit', ''))
        for selection_id in unit.get('selection_function_ids', []):
            add('selection-function', selection_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'selection-function-condition',
                'evidence-unit search/selection denominator',
                'mark the unit selected-positive or custody-only until selection denominator is restored', unit.get('maximum_credit', ''))
        for multiplicity_id in unit.get('multiplicity_control_ids', []):
            add('multiplicity-control', multiplicity_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'multiplicity-control-condition',
                'evidence-unit multiplicity adjustment or no-discovery cap',
                'remove surprise/discovery readings when global search control is missing', unit.get('maximum_credit', ''))
        for bias_id in unit.get('reporting_bias_ids', []):
            add('reporting-bias', bias_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'reporting-bias-condition',
                'evidence-unit reporting-bias and null-visibility audit',
                'cap support when missing nulls or failed variants alter the visible evidence population', unit.get('maximum_credit', ''))
        for cap_id in unit.get('model_capacity_ids', []):
            add('model-capacity', cap_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'model-capacity-condition',
                'evidence-unit model-capacity denominator for fit language',
                'mark the unit as flexible-fit only when capacity is missing', unit.get('maximum_credit', ''))
        for cpx_id in unit.get('complexity_penalty_ids', []):
            add('complexity-penalty', cpx_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'complexity-penalty-condition',
                'evidence-unit complexity penalty denominator',
                'remove best-fit / parsimony readings when penalty fails', unit.get('maximum_credit', ''))
        for gen_id in unit.get('generalization_validation_ids', []):
            add('generalization-validation', gen_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'generalization-validation-condition',
                'evidence-unit holdout / forecast / transfer validation denominator',
                'demote generalization readings when validation is absent or failed', unit.get('maximum_credit', ''))
        for crp_id in unit.get('computational_reproducibility_ids', []):
            add('computational-reproducibility', crp_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'computational-reproducibility-condition',
                'evidence-unit computational replay denominator',
                'mark the unit noncomputational or custody-only when replay fails', unit.get('maximum_credit', ''))
        for nst_id in unit.get('numerical_stability_ids', []):
            add('numerical-stability', nst_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'numerical-stability-condition',
                'evidence-unit numerical stability denominator',
                'cap the unit when solver, tolerance, seed, or platform sensitivity is unbounded', unit.get('maximum_credit', ''))
        for ssc_id in unit.get('software_supply_chain_ids', []):
            add('software-supply-chain', ssc_id, 'evidence-unit', unit.get('evidence_unit_id', ''), 'software-supply-chain-condition',
                'evidence-unit software provenance denominator',
                'mark software-backed support nonspendable when artifact provenance fails', unit.get('maximum_credit', ''))

    for row in rollback_ledger.get('rollback_rows', []):
        rb_id = row.get('rollback_id', '')
        target_floor = row.get('target_floor', '')
        for rid in row.get('affected_route_ids', []):
            add('rollback-rule', rb_id, 'route', rid, 'rollback-action',
                'authority loss propagation after a live defeater fires',
                f'roll route toward `{target_floor}` or the most restrictive surviving state', target_floor)
        for target_id in row.get('affected_claim_or_oq_ids', []):
            add('rollback-rule', rb_id, _claim_kind(target_id), target_id, 'rollback-action',
                'claim/open-question wording repair after a live defeater fires',
                'freeze, restate, or retire defeated claim wording', target_floor)
        for carrier_id in row.get('affected_carrier_ids', []):
            add('rollback-rule', rb_id, 'carrier', carrier_id, 'rollback-action',
                'public-record carrier repair after a live defeater fires',
                'remove carrier-backed authority until custody/replay is repaired', target_floor)
        for protocol_id in row.get('affected_protocol_ids', []):
            add('rollback-rule', rb_id, 'protocol', protocol_id, 'rollback-action',
                'acquisition protocol repair after a live defeater fires',
                'remove protocol-backed authority until replay is repaired', target_floor)

    graph = {
        'project': route_ledger.get('project', 'Theory-of-Everything'),
        'revision': route_ledger.get('revision'),
        'schema_version': '1.0',
        'generated_from': [
            'CANDIDATE-ROUTE-STATE-LEDGER.json',
            'PUBLIC-RECORD-CARRIER-LEDGER.json',
            'ACQUISITION-PROTOCOL-LEDGER.json',
            'CLAIM-ROUTE-BINDING-LEDGER.json',
            'ROLLBACK-PROPAGATION-LEDGER.json',
            'EVIDENCE-UNIT-LEDGER.json',
            'INDEPENDENCE-ASSUMPTION-LEDGER.json',
            'CREDIT-ALLOCATION-LEDGER.json',
            'CONTRAST-CLASS-LEDGER.json',
            'LIKELIHOOD-UPDATE-LEDGER.json',
            'PRIOR-SENSITIVITY-LEDGER.json',
            'MEASUREMENT-MODEL-LEDGER.json',
            'SYSTEMATIC-UNCERTAINTY-LEDGER.json',
            'CALIBRATION-TRACEABILITY-LEDGER.json',
            'DOMAIN-OF-VALIDITY-LEDGER.json',
            'TRANSPORTABILITY-LEDGER.json',
            'EXTRAPOLATION-FENCE-LEDGER.json',
            'CAUSAL-MECHANISM-LEDGER.json',
            'INTERVENTION-PROTOCOL-LEDGER.json',
            'COUNTERFACTUAL-ROBUSTNESS-LEDGER.json',
            'SELECTION-FUNCTION-LEDGER.json',
            'MULTIPLICITY-CONTROL-LEDGER.json',
            'REPORTING-BIAS-LEDGER.json',
            'MODEL-CAPACITY-LEDGER.json',
            'COMPLEXITY-PENALTY-LEDGER.json',
            'PREDICTIVE-GENERALIZATION-LEDGER.json',
            'SEMANTIC-TERM-LEDGER.json',
            'ONTOLOGY-COMMITMENT-LEDGER.json',
            'CLAIM-LANGUAGE-PERMISSION-LEDGER.json',
            'SOCIAL-AUTHORITY-LEDGER.json',
            'REVIEW-REPLICATION-LEDGER.json',
            'CONSENSUS-ELICITATION-LEDGER.json',
            'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json',
            'NUMERICAL-STABILITY-LEDGER.json',
            'SOFTWARE-SUPPLY-CHAIN-LEDGER.json',
            'PROMOTION-GATE-LEDGER.json',
            'OBSERVED-SECTOR-RECOVERY-LEDGER.json',
            'DISCRIMINATOR-FORECAST-LEDGER.json',
            'DECISION-EXPERIMENT-LEDGER.json',
            'EMPIRICAL-DELTA-LEDGER.json',
        ],
        'generation_rule': 'Edges are generated from route carrier/protocol/control/gate/OSR/defeater/severity/evidence-unit/independence/credit/contrast/update/prior/measurement/systematic/calibration/domain/transport/fence/causal-mechanism/intervention/counterfactual/selection/multiplicity/reporting-bias/model-capacity/complexity-penalty/generalization-validation/semantic-term/ontology-commitment/claim-language-permission/social-authority/review-replication/consensus-elicitation/computational-reproducibility/numerical-stability/software-supply-chain dependencies, route-facing forecast, decision-experiment, and empirical-delta rows, claim-route bindings, credit-claim bindings, and rollback propagation rows. Do not edit manually; run make index.',
        'edge_rows': rows,
    }
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json')


def write_defeat_rollback_summary(root: Path) -> None:
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    defeater_ledger = json.loads((root / 'EPISTEMIC-DEFEATER-LEDGER.json').read_text())
    rollback_ledger = json.loads((root / 'ROLLBACK-PROPAGATION-LEDGER.json').read_text())
    severity_ledger = json.loads((root / 'EVIDENCE-SEVERITY-LEDGER.json').read_text())
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    route_rows = route_ledger.get('route_rows', [])
    defeaters = defeater_ledger.get('defeater_rows', [])
    rollbacks = rollback_ledger.get('rollback_rows', [])
    severity_rows = severity_ledger.get('severity_rows', [])
    edge_rows = graph.get('edge_rows', [])
    type_counts = {}
    for row in defeaters:
        dtype = row.get('defeater_type', '<missing>')
        type_counts[dtype] = type_counts.get(dtype, 0) + 1
    handled_routes = [r for r in route_rows if r.get('defeater_ids') and r.get('rollback_rule_ids') and r.get('severity_test_ids')]
    lines = [
        '# Defeat / rollback / severity summary (generated)',
        '',
        'Generated from `EPISTEMIC-DEFEATER-LEDGER.json`, `ROLLBACK-PROPAGATION-LEDGER.json`, `EVIDENCE-SEVERITY-LEDGER.json`, `AUTHORITY-DEPENDENCY-GRAPH.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{route_ledger.get('revision', '<missing>')}`",
        f"- Defeaters: `{len(defeaters)}`",
        f"- Rollback rules: `{len(rollbacks)}`",
        f"- Severity tests: `{len(severity_rows)}`",
        f"- Dependency edges: `{len(edge_rows)}`",
        f"- Route rows with defeater/rollback/severity handles: `{len(handled_routes)}` of `{len(route_rows)}`",
        '',
        '## Defeater type counts',
        '',
    ]
    for dtype in sorted(type_counts):
        lines.append(f'- `{dtype}`: `{type_counts[dtype]}`')
    lines += ['', '## Route loss handles', '', '| Route | Defeaters | Rollbacks | Severity tests |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('defeater_ids', []))}` | `{len(row.get('rollback_rule_ids', []))}` | `{len(row.get('severity_test_ids', []))}` |")
    lines += ['', '## Rollback rows', '', '| Rollback | Defeaters | Routes | Claims/OQs | Target floor |', '|---|---:|---:|---:|---:|']
    for row in rollbacks:
        lines.append(f"| `{row.get('rollback_id')}` | `{len(row.get('defeater_ids', []))}` | `{len(row.get('affected_route_ids', []))}` | `{len(row.get('affected_claim_or_oq_ids', []))}` | `{row.get('target_floor')}` |")
    lines += ['', '## Severity rows', '', '| Severity test | Routes | Decisions | Max credit if passed | Defeat if failed |', '|---|---:|---:|---:|---|']
    for row in severity_rows:
        defeat = str(row.get('defeat_if_failed', '')).replace('\n', ' ')
        if len(defeat) > 100:
            defeat = defeat[:97] + '...'
        lines.append(f"| `{row.get('severity_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('decision_experiment_ids', []))}` | `{row.get('maximum_credit_if_passed')}` | {defeat} |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Surviving a defeater audit, passing a rollback repair condition, or appearing in the dependency graph only preserves or restores the maximum authority already allowed elsewhere. It does not itself promote a route to S4 or S5.',
        '',
    ]
    out = root / 'docs/30-program/defeat-rollback-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/defeat-rollback-summary.generated.md')


def write_evidence_credit_summary(root: Path) -> None:
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    evidence_ledger = json.loads((root / 'EVIDENCE-UNIT-LEDGER.json').read_text())
    independence_ledger = json.loads((root / 'INDEPENDENCE-ASSUMPTION-LEDGER.json').read_text())
    credit_ledger = json.loads((root / 'CREDIT-ALLOCATION-LEDGER.json').read_text())
    units = evidence_ledger.get('evidence_units', [])
    independence_rows = independence_ledger.get('independence_rows', [])
    credit_rows = credit_ledger.get('credit_rows', [])
    route_rows = route_ledger.get('route_rows', [])

    role_counts = {}
    cluster_counts = {}
    for unit in units:
        role = unit.get('credit_role', '<missing>')
        role_counts[role] = role_counts.get(role, 0) + 1
        cluster = unit.get('shared_support_cluster', '<missing>')
        cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1

    lines = [
        '# Evidence-credit / independence / no-double-counting summary (generated)',
        '',
        'Generated from `EVIDENCE-UNIT-LEDGER.json`, `INDEPENDENCE-ASSUMPTION-LEDGER.json`, `CREDIT-ALLOCATION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{evidence_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Evidence units: `{len(units)}`",
        f"- Independence assumptions: `{len(independence_rows)}`",
        f"- Credit-allocation rows: `{len(credit_rows)}`",
        '',
        '## Credit-role counts',
        '',
    ]
    for role in sorted(role_counts):
        lines.append(f'- `{role}`: `{role_counts[role]}`')
    lines += ['', '## Shared-support clusters', '']
    for cluster in sorted(cluster_counts):
        lines.append(f'- `{cluster}`: `{cluster_counts[cluster]}`')
    lines += ['', '## Evidence units', '', '| Evidence unit | Routes | Role | Max credit | Cluster | Carriers | Protocols | Deltas | Severity |', '|---|---:|---|---:|---|---:|---:|---:|---:|']
    for unit in units:
        lines.append(f"| `{unit.get('evidence_unit_id')}` | `{len(unit.get('route_ids', []))}` | `{unit.get('credit_role')}` | `{unit.get('maximum_credit')}` | `{unit.get('shared_support_cluster')}` | `{len(unit.get('carrier_ids', []))}` | `{len(unit.get('protocol_ids', []))}` | `{len(unit.get('empirical_delta_ids', []))}` | `{len(unit.get('severity_test_ids', []))}` |")
    lines += ['', '## Independence assumptions', '', '| Assumption | Type | Units | Routes | Stress test |', '|---|---|---:|---:|---|']
    for row in independence_rows:
        stress = str(row.get('stress_test','')).replace('\n',' ')
        if len(stress) > 100:
            stress = stress[:97] + '...'
        lines.append(f"| `{row.get('independence_id')}` | `{row.get('assumption_type')}` | `{len(row.get('evidence_unit_ids', []))}` | `{len(row.get('route_ids', []))}` | {stress} |")
    lines += ['', '## Credit-allocation rows', '', '| Credit row | Route | Units | Independence assumptions | Max effect |', '|---|---|---:|---:|---:|']
    for row in credit_rows:
        lines.append(f"| `{row.get('credit_id')}` | `{row.get('route_id')}` | `{len(row.get('evidence_unit_ids', []))}` | `{len(row.get('independence_assumption_ids', []))}` | `{row.get('maximum_authority_effect')}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Evidence-credit coverage prevents double-counting and can lower or cap support. It does not promote a route; route-state changes still require empirical deltas, promotion gates, observed-sector obligations, public-record carriers, acquisition protocols, negative controls, defeater handling, severity tests, and residual caps.',
        '',
    ]
    out = root / 'docs/30-program/evidence-credit-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/evidence-credit-summary.generated.md')


def write_contrast_update_summary(root: Path) -> None:
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    contrast_ledger = json.loads((root / 'CONTRAST-CLASS-LEDGER.json').read_text())
    update_ledger = json.loads((root / 'LIKELIHOOD-UPDATE-LEDGER.json').read_text())
    prior_ledger = json.loads((root / 'PRIOR-SENSITIVITY-LEDGER.json').read_text())
    contrast_rows = contrast_ledger.get('contrast_rows', [])
    update_rows = update_ledger.get('update_rows', [])
    prior_rows = prior_ledger.get('prior_rows', [])
    route_rows = route_ledger.get('route_rows', [])

    ceiling_counts = {}
    for row in contrast_rows:
        ceiling = row.get('current_update_ceiling', '<missing>')
        ceiling_counts[ceiling] = ceiling_counts.get(ceiling, 0) + 1
    update_mode_counts = {}
    for row in update_rows:
        mode = row.get('update_mode', '<missing>')
        update_mode_counts[mode] = update_mode_counts.get(mode, 0) + 1

    lines = [
        '# Contrast / likelihood-update / prior-sensitivity summary (generated)',
        '',
        'Generated from `CONTRAST-CLASS-LEDGER.json`, `LIKELIHOOD-UPDATE-LEDGER.json`, `PRIOR-SENSITIVITY-LEDGER.json`, `MEASUREMENT-MODEL-LEDGER.json`, `SYSTEMATIC-UNCERTAINTY-LEDGER.json`, `CALIBRATION-TRACEABILITY-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{contrast_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Contrast classes: `{len(contrast_rows)}`",
        f"- Likelihood/update rows: `{len(update_rows)}`",
        f"- Prior-sensitivity rows: `{len(prior_rows)}`",
        '',
        '## Contrast ceiling counts',
        '',
    ]
    for ceiling in sorted(ceiling_counts):
        lines.append(f'- `{ceiling}`: `{ceiling_counts[ceiling]}`')
    lines += ['', '## Update-mode counts', '']
    for mode in sorted(update_mode_counts):
        lines.append(f'- `{mode}`: `{update_mode_counts[mode]}`')
    lines += ['', '## Route handles', '', '| Route | Contrasts | Updates | Priors |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('contrast_class_ids', []))}` | `{len(row.get('likelihood_update_ids', []))}` | `{len(row.get('prior_sensitivity_ids', []))}` |")
    lines += ['', '## Contrast classes', '', '| Contrast class | Routes | Evidence units | Ceiling | Completeness |', '|---|---:|---:|---:|---|']
    for row in contrast_rows:
        status = str(row.get('contrast_completeness_status','')).replace('\n',' ')
        if len(status) > 80:
            status = status[:77] + '...'
        lines.append(f"| `{row.get('contrast_class_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('evidence_unit_ids', []))}` | `{row.get('current_update_ceiling')}` | {status} |")
    lines += ['', '## Likelihood/update rows', '', '| Update row | Route | Contrast | Max effect | Mode |', '|---|---|---|---:|---|']
    for row in update_rows:
        lines.append(f"| `{row.get('likelihood_update_id')}` | `{row.get('route_id')}` | `{row.get('contrast_class_id')}` | `{row.get('maximum_authority_effect')}` | `{row.get('update_mode')}` |")
    lines += ['', '## Prior-sensitivity rows', '', '| Prior row | Routes | Contrasts | Max effect |', '|---|---:|---:|---:|']
    for row in prior_rows:
        lines.append(f"| `{row.get('prior_sensitivity_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('contrast_class_ids', []))}` | `{row.get('maximum_authority_effect')}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Contrast classes, likelihood/update rows, and prior-sensitivity rows make support denominators explicit. They can cap, split, merge, or roll back support, but they do not promote a route beyond its state-machine, promotion-gate, observed-sector, public-record, evidence-credit, and residual-cap limits.',
        '',
    ]
    out = root / 'docs/30-program/contrast-update-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/contrast-update-summary.generated.md')


def write_measurement_systematics_summary(root: Path) -> None:
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    measurement_ledger = json.loads((root / 'MEASUREMENT-MODEL-LEDGER.json').read_text())
    systematic_ledger = json.loads((root / 'SYSTEMATIC-UNCERTAINTY-LEDGER.json').read_text())
    calibration_ledger = json.loads((root / 'CALIBRATION-TRACEABILITY-LEDGER.json').read_text())
    measurement_rows = measurement_ledger.get('measurement_model_rows', [])
    systematic_rows = systematic_ledger.get('systematic_rows', [])
    calibration_rows = calibration_ledger.get('calibration_rows', [])
    route_rows = route_ledger.get('route_rows', [])
    model_class_counts = {}
    for row in measurement_rows:
        model_class_counts[row.get('model_class','<missing>')] = model_class_counts.get(row.get('model_class','<missing>'), 0) + 1
    systematic_class_counts = {}
    for row in systematic_rows:
        systematic_class_counts[row.get('systematic_class','<missing>')] = systematic_class_counts.get(row.get('systematic_class','<missing>'), 0) + 1
    traceability_class_counts = {}
    for row in calibration_rows:
        traceability_class_counts[row.get('traceability_class','<missing>')] = traceability_class_counts.get(row.get('traceability_class','<missing>'), 0) + 1

    lines = [
        '# Measurement-model / systematic-uncertainty / calibration-traceability summary (generated)',
        '',
        'Generated from `MEASUREMENT-MODEL-LEDGER.json`, `SYSTEMATIC-UNCERTAINTY-LEDGER.json`, `CALIBRATION-TRACEABILITY-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{measurement_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Measurement-model rows: `{len(measurement_rows)}`",
        f"- Systematic-uncertainty rows: `{len(systematic_rows)}`",
        f"- Calibration-traceability rows: `{len(calibration_rows)}`",
        '',
        '## Measurement model class counts',
        '',
    ]
    for klass in sorted(model_class_counts):
        lines.append(f'- `{klass}`: `{model_class_counts[klass]}`')
    lines += ['', '## Systematic class counts', '']
    for klass in sorted(systematic_class_counts):
        lines.append(f'- `{klass}`: `{systematic_class_counts[klass]}`')
    lines += ['', '## Traceability class counts', '']
    for klass in sorted(traceability_class_counts):
        lines.append(f'- `{klass}`: `{traceability_class_counts[klass]}`')
    lines += ['', '## Route handles', '', '| Route | Measurement models | Systematics | Calibration/traceability |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('measurement_model_ids', []))}` | `{len(row.get('systematic_uncertainty_ids', []))}` | `{len(row.get('calibration_traceability_ids', []))}` |")
    lines += ['', '## Measurement models', '', '| Measurement model | Routes | Evidence units | Max effect | Model class |', '|---|---:|---:|---:|---|']
    for row in measurement_rows:
        lines.append(f"| `{row.get('measurement_model_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('evidence_unit_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('model_class')}` |")
    lines += ['', '## Systematic rows', '', '| Systematic | Routes | Measurement models | Max effect | Class |', '|---|---:|---:|---:|---|']
    for row in systematic_rows:
        lines.append(f"| `{row.get('systematic_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('measurement_model_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('systematic_class')}` |")
    lines += ['', '## Calibration / traceability rows', '', '| Calibration row | Routes | Measurement models | Systematics | Max effect | Class |', '|---|---:|---:|---:|---:|---|']
    for row in calibration_rows:
        lines.append(f"| `{row.get('calibration_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('measurement_model_ids', []))}` | `{len(row.get('systematic_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('traceability_class')}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Measurement-model, systematic-uncertainty, and calibration/traceability rows make raw-record-to-observable conversion auditable. They can cap, freeze, or roll back support, but they do not promote a route beyond its state-machine, contrast/update, credit-allocation, public-record, observed-sector, or residual-cap limits.',
        '',
    ]
    out = root / 'docs/30-program/measurement-systematics-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/measurement-systematics-summary.generated.md')


def write_validity_transport_summary(root: Path) -> None:
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    domain_ledger = json.loads((root / 'DOMAIN-OF-VALIDITY-LEDGER.json').read_text())
    transport_ledger = json.loads((root / 'TRANSPORTABILITY-LEDGER.json').read_text())
    fence_ledger = json.loads((root / 'EXTRAPOLATION-FENCE-LEDGER.json').read_text())
    domain_rows = domain_ledger.get('domain_rows', [])
    transport_rows = transport_ledger.get('transport_rows', [])
    fence_rows = fence_ledger.get('fence_rows', [])
    route_rows = route_ledger.get('route_rows', [])
    domain_counts = {}
    for row in domain_rows:
        domain_counts[row.get('domain_class','<missing>')] = domain_counts.get(row.get('domain_class','<missing>'), 0) + 1
    transport_counts = {}
    for row in transport_rows:
        transport_counts[row.get('transport_status','<missing>')] = transport_counts.get(row.get('transport_status','<missing>'), 0) + 1
    fence_counts = {}
    for row in fence_rows:
        fence_counts[row.get('fence_class','<missing>')] = fence_counts.get(row.get('fence_class','<missing>'), 0) + 1

    lines = [
        '# Validity-domain / transportability / extrapolation-fence summary (generated)',
        '',
        'Generated from `DOMAIN-OF-VALIDITY-LEDGER.json`, `TRANSPORTABILITY-LEDGER.json`, `EXTRAPOLATION-FENCE-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{domain_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Validity-domain rows: `{len(domain_rows)}`",
        f"- Transportability rows: `{len(transport_rows)}`",
        f"- Extrapolation-fence rows: `{len(fence_rows)}`",
        '',
        '## Domain class counts',
        '',
    ]
    for klass in sorted(domain_counts):
        lines.append(f'- `{klass}`: `{domain_counts[klass]}`')
    lines += ['', '## Transport status counts', '']
    for status in sorted(transport_counts):
        lines.append(f'- `{status}`: `{transport_counts[status]}`')
    lines += ['', '## Fence class counts', '']
    for klass in sorted(fence_counts):
        lines.append(f'- `{klass}`: `{fence_counts[klass]}`')
    lines += ['', '## Route handles', '', '| Route | Domains | Transport | Fences |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('validity_domain_ids', []))}` | `{len(row.get('transportability_ids', []))}` | `{len(row.get('extrapolation_fence_ids', []))}` |")
    lines += ['', '## Validity domains', '', '| Domain | Routes | Evidence units | Max effect | Class |', '|---|---:|---:|---:|---|']
    for row in domain_rows:
        lines.append(f"| `{row.get('domain_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('evidence_unit_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('domain_class')}` |")
    lines += ['', '## Transportability rows', '', '| Transport row | Routes | Domains | Max effect | Status |', '|---|---:|---:|---:|---|']
    for row in transport_rows:
        lines.append(f"| `{row.get('transport_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('domain_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('transport_status')}` |")
    lines += ['', '## Extrapolation fences', '', '| Fence | Routes | Domains | Transport | Max effect | Class |', '|---|---:|---:|---:|---:|---|']
    for row in fence_rows:
        lines.append(f"| `{row.get('fence_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('domain_ids', []))}` | `{len(row.get('transport_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('fence_class')}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Validity-domain, transportability, and extrapolation-fence rows make source-to-target generalization auditable. They can cap, freeze, split, quarantine, or roll back support, but they do not promote a route beyond its state-machine, observed-sector, public-record, evidence-credit, contrast/update, measurement/systematics, or residual-cap limits.',
        '',
    ]
    out = root / 'docs/30-program/validity-transport-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/validity-transport-summary.generated.md')


def write_causal_mechanism_summary(root: Path) -> None:
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    mechanism_ledger = json.loads((root / 'CAUSAL-MECHANISM-LEDGER.json').read_text())
    intervention_ledger = json.loads((root / 'INTERVENTION-PROTOCOL-LEDGER.json').read_text())
    counterfactual_ledger = json.loads((root / 'COUNTERFACTUAL-ROBUSTNESS-LEDGER.json').read_text())
    route_rows = route_ledger.get('route_rows', [])
    mechanism_rows = mechanism_ledger.get('mechanism_rows', [])
    intervention_rows = intervention_ledger.get('intervention_rows', [])
    counterfactual_rows = counterfactual_ledger.get('counterfactual_rows', [])
    class_counts = {}
    for row in mechanism_rows:
        klass = row.get('mechanism_class', '<missing>')
        class_counts[klass] = class_counts.get(klass, 0) + 1
    status_counts = {}
    for row in intervention_rows:
        status = row.get('intervention_status', '<missing>')
        status_counts[status] = status_counts.get(status, 0) + 1
    cf_counts = {}
    for row in counterfactual_rows:
        klass = row.get('counterfactual_class', '<missing>')
        cf_counts[klass] = cf_counts.get(klass, 0) + 1
    lines = [
        '# Causal mechanism / intervention / counterfactual summary (generated)',
        '',
        'Generated from `CAUSAL-MECHANISM-LEDGER.json`, `INTERVENTION-PROTOCOL-LEDGER.json`, `COUNTERFACTUAL-ROBUSTNESS-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{mechanism_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Causal-mechanism rows: `{len(mechanism_rows)}`",
        f"- Intervention-protocol rows: `{len(intervention_rows)}`",
        f"- Counterfactual-robustness rows: `{len(counterfactual_rows)}`",
        '',
        '## Mechanism class counts',
        '',
    ]
    for klass in sorted(class_counts):
        lines.append(f'- `{klass}`: `{class_counts[klass]}`')
    lines += ['', '## Intervention status counts', '']
    for status in sorted(status_counts):
        lines.append(f'- `{status}`: `{status_counts[status]}`')
    lines += ['', '## Counterfactual class counts', '']
    for klass in sorted(cf_counts):
        lines.append(f'- `{klass}`: `{cf_counts[klass]}`')
    lines += ['', '## Route handles', '', '| Route | Mechanisms | Interventions | Counterfactuals |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('causal_mechanism_ids', []))}` | `{len(row.get('intervention_protocol_ids', []))}` | `{len(row.get('counterfactual_robustness_ids', []))}` |")
    lines += ['', '## Causal mechanisms', '', '| Mechanism | Routes | Evidence units | Max effect | Class |', '|---|---:|---:|---:|---|']
    for row in mechanism_rows:
        lines.append(f"| `{row.get('mechanism_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('evidence_unit_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('mechanism_class')}` |")
    lines += ['', '## Intervention protocols', '', '| Intervention | Routes | Mechanisms | Max effect | Status |', '|---|---:|---:|---:|---|']
    for row in intervention_rows:
        lines.append(f"| `{row.get('intervention_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('mechanism_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('intervention_status')}` |")
    lines += ['', '## Counterfactual robustness rows', '', '| Counterfactual | Routes | Mechanisms | Interventions | Max effect | Class |', '|---|---:|---:|---:|---:|---|']
    for row in counterfactual_rows:
        lines.append(f"| `{row.get('counterfactual_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('mechanism_ids', []))}` | `{len(row.get('intervention_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('counterfactual_class')}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Causal-mechanism, intervention-protocol, and counterfactual-robustness rows make mechanism language auditable. They can cap, split, freeze, or roll back cause/intervention/counterfactual wording, but they do not promote a route beyond its state-machine, observed-sector, public-record, evidence-credit, contrast/update, measurement/systematics, validity/transport, or residual-cap limits.',
        '',
    ]
    out = root / 'docs/30-program/causal-mechanism-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/causal-mechanism-summary.generated.md')


def write_selection_bias_summary(root: Path) -> None:
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    selection_ledger = json.loads((root / 'SELECTION-FUNCTION-LEDGER.json').read_text())
    multiplicity_ledger = json.loads((root / 'MULTIPLICITY-CONTROL-LEDGER.json').read_text())
    reporting_bias_ledger = json.loads((root / 'REPORTING-BIAS-LEDGER.json').read_text())
    route_rows = route_ledger.get('route_rows', [])
    selection_rows = selection_ledger.get('selection_rows', [])
    multiplicity_rows = multiplicity_ledger.get('multiplicity_rows', [])
    bias_rows = reporting_bias_ledger.get('bias_rows', [])
    sel_counts = {}
    for row in selection_rows:
        klass = row.get('selection_class', '<missing>')
        sel_counts[klass] = sel_counts.get(klass, 0) + 1
    mult_counts = {}
    for row in multiplicity_rows:
        klass = row.get('control_class', '<missing>')
        mult_counts[klass] = mult_counts.get(klass, 0) + 1
    bias_counts = {}
    for row in bias_rows:
        klass = row.get('bias_class', '<missing>')
        bias_counts[klass] = bias_counts.get(klass, 0) + 1
    lines = [
        '# Selection / multiplicity / reporting-bias summary (generated)',
        '',
        'Generated from `SELECTION-FUNCTION-LEDGER.json`, `MULTIPLICITY-CONTROL-LEDGER.json`, `REPORTING-BIAS-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{selection_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Selection-function rows: `{len(selection_rows)}`",
        f"- Multiplicity-control rows: `{len(multiplicity_rows)}`",
        f"- Reporting-bias rows: `{len(bias_rows)}`",
        '',
        '## Selection class counts',
        '',
    ]
    for klass in sorted(sel_counts):
        lines.append(f'- `{klass}`: `{sel_counts[klass]}`')
    lines += ['', '## Multiplicity control counts', '']
    for klass in sorted(mult_counts):
        lines.append(f'- `{klass}`: `{mult_counts[klass]}`')
    lines += ['', '## Reporting-bias counts', '']
    for klass in sorted(bias_counts):
        lines.append(f'- `{klass}`: `{bias_counts[klass]}`')
    lines += ['', '## Route handles', '', '| Route | Selection | Multiplicity | Reporting bias |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('selection_function_ids', []))}` | `{len(row.get('multiplicity_control_ids', []))}` | `{len(row.get('reporting_bias_ids', []))}` |")
    lines += ['', '## Selection functions', '', '| Selection function | Routes | Evidence units | Max effect | Class |', '|---|---:|---:|---:|---|']
    for row in selection_rows:
        lines.append(f"| `{row.get('selection_function_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('evidence_unit_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('selection_class')}` |")
    lines += ['', '## Multiplicity controls', '', '| Multiplicity control | Routes | Evidence units | Max effect | Discovery language? |', '|---|---:|---:|---:|---:|']
    for row in multiplicity_rows:
        lines.append(f"| `{row.get('multiplicity_control_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('evidence_unit_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('discovery_language_allowed')}` |")
    lines += ['', '## Reporting-bias audits', '', '| Reporting-bias audit | Routes | Evidence units | Max effect | Class |', '|---|---:|---:|---:|---|']
    for row in bias_rows:
        lines.append(f"| `{row.get('reporting_bias_id')}` | `{len(row.get('route_ids', []))}` | `{len(row.get('evidence_unit_ids', []))}` | `{row.get('maximum_authority_effect')}` | `{row.get('bias_class')}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Selection-function, multiplicity-control, and reporting-bias rows make selected-positive and look-elsewhere language auditable. They can cap, split, freeze, or roll back surprise/discovery/anomaly/benchmark-win wording, but they do not promote a route beyond its state-machine, observed-sector, public-record, evidence-credit, contrast/update, measurement/systematics, validity/transport, causal, or residual-cap limits.',
        '',
    ]
    out = root / 'docs/30-program/selection-bias-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/selection-bias-summary.generated.md')

def write_model_capacity_summary(root: Path) -> None:
    """Render generated summary for model capacity / complexity / generalization ledgers."""
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    cap_ledger = json.loads((root / 'MODEL-CAPACITY-LEDGER.json').read_text())
    cpx_ledger = json.loads((root / 'COMPLEXITY-PENALTY-LEDGER.json').read_text())
    gen_ledger = json.loads((root / 'PREDICTIVE-GENERALIZATION-LEDGER.json').read_text())
    route_rows = route_ledger.get('route_rows', [])
    cap_rows = cap_ledger.get('capacity_rows', [])
    cpx_rows = cpx_ledger.get('complexity_rows', [])
    gen_rows = gen_ledger.get('generalization_rows', [])
    cap_counts = {}
    for row in cap_rows:
        cap_counts[row.get('capacity_class','<missing>')] = cap_counts.get(row.get('capacity_class','<missing>'),0)+1
    cpx_counts = {}
    for row in cpx_rows:
        cpx_counts[row.get('penalty_class','<missing>')] = cpx_counts.get(row.get('penalty_class','<missing>'),0)+1
    gen_counts = {}
    for row in gen_rows:
        gen_counts[row.get('validation_class','<missing>')] = gen_counts.get(row.get('validation_class','<missing>'),0)+1
    lines = [
        '# Model-capacity / complexity / generalization summary (generated)',
        '',
        'Generated from `MODEL-CAPACITY-LEDGER.json`, `COMPLEXITY-PENALTY-LEDGER.json`, `PREDICTIVE-GENERALIZATION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{cap_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Model-capacity rows: `{len(cap_rows)}`",
        f"- Complexity-penalty rows: `{len(cpx_rows)}`",
        f"- Predictive-generalization rows: `{len(gen_rows)}`",
        '',
        '## Capacity class counts',
        '',
    ]
    for k in sorted(cap_counts): lines.append(f'- `{k}`: `{cap_counts[k]}`')
    lines += ['', '## Complexity penalty counts', '']
    for k in sorted(cpx_counts): lines.append(f'- `{k}`: `{cpx_counts[k]}`')
    lines += ['', '## Generalization validation counts', '']
    for k in sorted(gen_counts): lines.append(f'- `{k}`: `{gen_counts[k]}`')
    lines += ['', '## Route handles', '', '| Route | Capacity | Complexity | Generalization |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('model_capacity_ids', []))}` | `{len(row.get('complexity_penalty_ids', []))}` | `{len(row.get('generalization_validation_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Capacity, complexity, and generalization rows make fit, simplicity, parsimony, compression, Occam, and prediction language auditable. They can cap, split, freeze, or roll back apparent adequacy, but they do not promote a route beyond its state-machine, public-record, evidence-credit, contrast/update, measurement/systematics, validity/transport, causal, selection, or residual-cap limits.', '']
    out = root / 'docs/30-program/model-capacity-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/model-capacity-summary.generated.md')


def write_semantic_binding_summary(root: Path) -> None:
    """Render generated summary for semantic binding / ontology / language-permission ledgers."""
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    semantic_ledger = json.loads((root / 'SEMANTIC-TERM-LEDGER.json').read_text())
    ontology_ledger = json.loads((root / 'ONTOLOGY-COMMITMENT-LEDGER.json').read_text())
    permission_ledger = json.loads((root / 'CLAIM-LANGUAGE-PERMISSION-LEDGER.json').read_text())
    route_rows = route_ledger.get('route_rows', [])
    semantic_rows = semantic_ledger.get('semantic_rows', [])
    commitment_rows = ontology_ledger.get('commitment_rows', [])
    permission_rows = permission_ledger.get('permission_rows', [])
    def counts(rows, key):
        out = {}
        for row in rows:
            value = row.get(key, '<missing>')
            out[value] = out.get(value, 0) + 1
        return out
    term_counts = counts(semantic_rows, 'term_class')
    commitment_counts = counts(commitment_rows, 'commitment_class')
    permission_counts = counts(permission_rows, 'permission_class')
    lines = [
        '# Semantic binding / ontology / claim-language summary (generated)',
        '',
        'Generated from `SEMANTIC-TERM-LEDGER.json`, `ONTOLOGY-COMMITMENT-LEDGER.json`, `CLAIM-LANGUAGE-PERMISSION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{semantic_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Semantic-term rows: `{len(semantic_rows)}`",
        f"- Ontology-commitment rows: `{len(commitment_rows)}`",
        f"- Claim-language-permission rows: `{len(permission_rows)}`",
        '',
        '## Semantic-term class counts',
        '',
    ]
    for key in sorted(term_counts):
        lines.append(f'- `{key}`: `{term_counts[key]}`')
    lines += ['', '## Ontology-commitment class counts', '']
    for key in sorted(commitment_counts):
        lines.append(f'- `{key}`: `{commitment_counts[key]}`')
    lines += ['', '## Claim-language permission class counts', '']
    for key in sorted(permission_counts):
        lines.append(f'- `{key}`: `{permission_counts[key]}`')
    lines += ['', '## Route handles', '', '| Route | Semantic terms | Ontology commitments | Language permissions |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('semantic_term_ids', []))}` | `{len(row.get('ontology_commitment_ids', []))}` | `{len(row.get('claim_language_permission_ids', []))}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Semantic, ontology, and language-permission rows make wording auditable. They can cap, split, freeze, or roll back terminology, identity, equivalence, realism, native-observable, and closure language, but they do not promote a route beyond its state-machine, public-record, evidence-credit, contrast/update, measurement/systematics, validity/transport, causal, selection, capacity, or residual-cap limits.',
        '',
    ]
    out = root / 'docs/30-program/semantic-binding-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/semantic-binding-summary.generated.md')


def write_social_authority_summary(root: Path) -> None:
    """Render generated summary for social-authority / review-replication / consensus ledgers."""
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    social_ledger = json.loads((root / 'SOCIAL-AUTHORITY-LEDGER.json').read_text())
    review_ledger = json.loads((root / 'REVIEW-REPLICATION-LEDGER.json').read_text())
    consensus_ledger = json.loads((root / 'CONSENSUS-ELICITATION-LEDGER.json').read_text())
    route_rows = route_ledger.get('route_rows', [])
    social_rows = social_ledger.get('social_rows', [])
    review_rows = review_ledger.get('review_rows', [])
    consensus_rows = consensus_ledger.get('consensus_rows', [])
    def counts(rows, key):
        out = {}
        for row in rows:
            val = row.get(key, '<missing>')
            out[val] = out.get(val, 0) + 1
        return out
    social_counts = counts(social_rows, 'social_authority_class')
    review_counts = counts(review_rows, 'review_replication_class')
    consensus_counts = counts(consensus_rows, 'consensus_class')
    lines = [
        '# Social authority / review / consensus summary (generated)',
        '',
        'Generated from `SOCIAL-AUTHORITY-LEDGER.json`, `REVIEW-REPLICATION-LEDGER.json`, `CONSENSUS-ELICITATION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{social_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Social-authority rows: `{len(social_rows)}`",
        f"- Review/replication rows: `{len(review_rows)}`",
        f"- Consensus/elicitation rows: `{len(consensus_rows)}`",
        '',
        '## Social-authority class counts',
        '',
    ]
    for key in sorted(social_counts):
        lines.append(f'- `{key}`: `{social_counts[key]}`')
    lines += ['', '## Review/replication class counts', '']
    for key in sorted(review_counts):
        lines.append(f'- `{key}`: `{review_counts[key]}`')
    lines += ['', '## Consensus/elicitation class counts', '']
    for key in sorted(consensus_counts):
        lines.append(f'- `{key}`: `{consensus_counts[key]}`')
    lines += ['', '## Route handles', '', '| Route | Social authority | Review/replication | Consensus/elicitation |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('social_authority_ids', []))}` | `{len(row.get('review_replication_ids', []))}` | `{len(row.get('consensus_elicitation_ids', []))}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Social authority, review status, replication status, and consensus elicitation are testimony and scrutiny controls. They can cap, split, freeze, or contextualize wording, but they do not promote a route beyond its route-state, evidence, measurement, validity, causal, selection, capacity, semantic, ontology, or rollback limits.',
        '',
    ]
    out = root / 'docs/30-program/social-authority-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/social-authority-summary.generated.md')


def write_computational_reproducibility_summary(root: Path) -> None:
    """Render generated summary for computational reproducibility / numerical stability / software provenance ledgers."""
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    crp_ledger = json.loads((root / 'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json').read_text())
    nst_ledger = json.loads((root / 'NUMERICAL-STABILITY-LEDGER.json').read_text())
    ssc_ledger = json.loads((root / 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json').read_text())
    route_rows = route_ledger.get('route_rows', [])
    crp_rows = crp_ledger.get('reproducibility_rows', [])
    nst_rows = nst_ledger.get('stability_rows', [])
    ssc_rows = ssc_ledger.get('supply_chain_rows', [])
    def counts(rows, key):
        out = {}
        for row in rows:
            value = row.get(key, '<missing>')
            out[value] = out.get(value, 0) + 1
        return out
    crp_counts = counts(crp_rows, 'reproducibility_class')
    nst_counts = counts(nst_rows, 'stability_class')
    ssc_counts = counts(ssc_rows, 'supply_chain_class')
    lines = [
        '# Computational reproducibility / numerical stability / software provenance summary (generated)',
        '',
        'Generated from `COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json`, `NUMERICAL-STABILITY-LEDGER.json`, `SOFTWARE-SUPPLY-CHAIN-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{crp_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Computational-reproducibility rows: `{len(crp_rows)}`",
        f"- Numerical-stability rows: `{len(nst_rows)}`",
        f"- Software-supply-chain rows: `{len(ssc_rows)}`",
        '',
        '## Computational-reproducibility class counts',
        '',
    ]
    for key in sorted(crp_counts):
        lines.append(f'- `{key}`: `{crp_counts[key]}`')
    lines += ['', '## Numerical-stability class counts', '']
    for key in sorted(nst_counts):
        lines.append(f'- `{key}`: `{nst_counts[key]}`')
    lines += ['', '## Software-supply-chain class counts', '']
    for key in sorted(ssc_counts):
        lines.append(f'- `{key}`: `{ssc_counts[key]}`')
    lines += ['', '## Route handles', '', '| Route | Computational replay | Numerical stability | Software chain |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('computational_reproducibility_ids', []))}` | `{len(row.get('numerical_stability_ids', []))}` | `{len(row.get('software_supply_chain_ids', []))}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Computational replay, numerical stability, and software provenance make computational artifacts auditable. They can cap, freeze, demote, or roll back code, workflow, solver, simulation, benchmark, proof-replay, container, and generated-summary language, but they do not promote a route beyond its state-machine, public-record, evidence-credit, contrast/update, measurement/systematics, validity/transport, causal, selection, capacity, semantic, ontology, social-authority, or residual-cap limits.',
        '',
    ]
    out = root / 'docs/30-program/computational-reproducibility-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/computational-reproducibility-summary.generated.md')


def augment_authority_dependency_graph_with_formal_proof_edges(root: Path) -> None:
    """Add formal-proof / assumption-discharge / formalization-coverage edges after the base graph is rendered."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    rows = graph.get('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id():
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key = (source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({
            'edge_id': next_edge_id(),
            'source_kind': source_kind,
            'source_id': source_id,
            'dependent_kind': dependent_kind,
            'dependent_id': dependent_id,
            'dependency_kind': dependency_kind,
            'required_for': required_for,
            'failure_effect': failure_effect,
            'max_credit_transmitted': max_credit,
        })
        existing.add(key)
    if 'PROOF-OBLIGATION-LEDGER.json' not in graph.get('generated_from', []):
        graph.setdefault('generated_from', []).extend(['PROOF-OBLIGATION-LEDGER.json','ASSUMPTION-DISCHARGE-LEDGER.json','FORMALIZATION-COVERAGE-LEDGER.json'])
    graph['generation_rule'] = graph.get('generation_rule','') + ' Formal proof obligation / assumption discharge / formalization coverage edges are appended by the rev0275 augmentation pass.'
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid = row.get('route_id', '')
        effect = row.get('promotion_ceiling', '') or row.get('authority_state', '')
        for pid in row.get('proof_obligation_ids', []):
            add('proof-obligation', pid, 'route', rid, 'proof-obligation-condition', 'route proof/theorem/derivation denominator', 'freeze proof or derivation language when the proof obligation fails or changes statement', effect)
        for aid in row.get('assumption_discharge_ids', []):
            add('assumption-discharge', aid, 'route', rid, 'assumption-discharge-condition', 'route assumption-discharge denominator', 'cap theorem/derivation support when assumptions remain live or hidden', effect)
        for fid in row.get('formalization_coverage_ids', []):
            add('formalization-coverage', fid, 'route', rid, 'formalization-coverage-condition', 'route formalized-fragment coverage denominator', 'cap mechanized/formalization support when coverage is fragmentary or nonportable', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'open-question' if str(target_id).startswith('OQ-') else 'claim'
        effect = binding.get('maximum_authority_effect', '') or 'bounded by binding row'
        for pid in binding.get('proof_obligation_ids', []):
            add('proof-obligation', pid, target_kind, target_id, 'proof-obligation-claim-condition', f'claim proof-obligation denominator under {binding.get("binding_id")}', 'freeze proof/theorem/derivation claim wording until proof obligations are restored', effect)
        for aid in binding.get('assumption_discharge_ids', []):
            add('assumption-discharge', aid, target_kind, target_id, 'assumption-discharge-claim-condition', f'claim assumption-discharge denominator under {binding.get("binding_id")}', 'freeze assumption-discharge claim wording until assumptions are inventoried and discharged', effect)
        for fid in binding.get('formalization_coverage_ids', []):
            add('formalization-coverage', fid, target_kind, target_id, 'formalization-coverage-claim-condition', f'claim formalization-coverage denominator under {binding.get("binding_id")}', 'freeze formalization/mechanized-proof claim wording until coverage rows are restored', effect)
    optional = [
        ('evidence-unit', 'evidence_unit_id', 'EVIDENCE-UNIT-LEDGER.json', 'evidence_units'),
        ('credit-allocation', 'credit_id', 'CREDIT-ALLOCATION-LEDGER.json', 'credit_rows'),
        ('empirical-delta', 'delta_id', 'EMPIRICAL-DELTA-LEDGER.json', 'empirical_deltas'),
        ('forecast', 'forecast_id', 'DISCRIMINATOR-FORECAST-LEDGER.json', 'forecast_rows'),
        ('decision-experiment', 'experiment_id', 'DECISION-EXPERIMENT-LEDGER.json', 'decision_experiments'),
        ('severity-test', 'severity_id', 'EVIDENCE-SEVERITY-LEDGER.json', 'severity_rows'),
        ('contrast-class', 'contrast_id', 'CONTRAST-CLASS-LEDGER.json', 'contrast_rows'),
        ('likelihood-update', 'update_id', 'LIKELIHOOD-UPDATE-LEDGER.json', 'update_rows'),
        ('prior-sensitivity', 'prior_id', 'PRIOR-SENSITIVITY-LEDGER.json', 'prior_rows'),
        ('measurement-model', 'measurement_model_id', 'MEASUREMENT-MODEL-LEDGER.json', 'measurement_model_rows'),
        ('systematic-uncertainty', 'systematic_id', 'SYSTEMATIC-UNCERTAINTY-LEDGER.json', 'systematic_rows'),
        ('calibration-traceability', 'calibration_id', 'CALIBRATION-TRACEABILITY-LEDGER.json', 'calibration_rows'),
        ('validity-domain', 'domain_id', 'DOMAIN-OF-VALIDITY-LEDGER.json', 'domain_rows'),
        ('transportability', 'transport_id', 'TRANSPORTABILITY-LEDGER.json', 'transport_rows'),
        ('extrapolation-fence', 'fence_id', 'EXTRAPOLATION-FENCE-LEDGER.json', 'fence_rows'),
        ('causal-mechanism', 'mechanism_id', 'CAUSAL-MECHANISM-LEDGER.json', 'mechanism_rows'),
        ('intervention-protocol', 'intervention_id', 'INTERVENTION-PROTOCOL-LEDGER.json', 'intervention_rows'),
        ('counterfactual-robustness', 'counterfactual_id', 'COUNTERFACTUAL-ROBUSTNESS-LEDGER.json', 'counterfactual_rows'),
        ('selection-function', 'selection_id', 'SELECTION-FUNCTION-LEDGER.json', 'selection_rows'),
        ('multiplicity-control', 'multiplicity_id', 'MULTIPLICITY-CONTROL-LEDGER.json', 'multiplicity_rows'),
        ('reporting-bias', 'bias_id', 'REPORTING-BIAS-LEDGER.json', 'bias_rows'),
        ('model-capacity', 'model_capacity_id', 'MODEL-CAPACITY-LEDGER.json', 'capacity_rows'),
        ('complexity-penalty', 'complexity_penalty_id', 'COMPLEXITY-PENALTY-LEDGER.json', 'complexity_rows'),
        ('generalization-validation', 'generalization_id', 'PREDICTIVE-GENERALIZATION-LEDGER.json', 'generalization_rows'),
        ('semantic-term', 'semantic_term_id', 'SEMANTIC-TERM-LEDGER.json', 'semantic_rows'),
        ('ontology-commitment', 'ontology_commitment_id', 'ONTOLOGY-COMMITMENT-LEDGER.json', 'commitment_rows'),
        ('claim-language-permission', 'language_permission_id', 'CLAIM-LANGUAGE-PERMISSION-LEDGER.json', 'permission_rows'),
        ('social-authority', 'social_authority_id', 'SOCIAL-AUTHORITY-LEDGER.json', 'social_rows'),
        ('review-replication', 'review_replication_id', 'REVIEW-REPLICATION-LEDGER.json', 'review_rows'),
        ('consensus-elicitation', 'consensus_elicitation_id', 'CONSENSUS-ELICITATION-LEDGER.json', 'consensus_rows'),
        ('computational-reproducibility', 'computational_reproducibility_id', 'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json', 'reproducibility_rows'),
        ('numerical-stability', 'numerical_stability_id', 'NUMERICAL-STABILITY-LEDGER.json', 'stability_rows'),
        ('software-supply-chain', 'software_supply_chain_id', 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json', 'supply_chain_rows'),
    ]
    for dep_kind, id_key, file_name, rows_key in optional:
        path = root / file_name
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for item in data.get(rows_key, []):
            item_id = item.get(id_key, '')
            effect = item.get('maximum_authority_effect') or item.get('maximum_credit') or item.get('current_maximum_credit') or item.get('route_state_effect') or 'bounded by owning row'
            for pid in item.get('proof_obligation_ids', []):
                add('proof-obligation', pid, dep_kind, item_id, 'proof-obligation-condition', f'{dep_kind} proof-obligation denominator', 'remove proof-dependent credit when proof obligation fails', effect)
            for aid in item.get('assumption_discharge_ids', []):
                add('assumption-discharge', aid, dep_kind, item_id, 'assumption-discharge-condition', f'{dep_kind} assumption-discharge denominator', 'cap proof or derivation credit when assumptions remain live', effect)
            for fid in item.get('formalization_coverage_ids', []):
                add('formalization-coverage', fid, dep_kind, item_id, 'formalization-coverage-condition', f'{dep_kind} formalization-coverage denominator', 'cap mechanized/formal credit when coverage is fragmentary', effect)
    graph['edge_rows'] = rows
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json formal-proof edges')


def write_formal_proof_summary(root: Path) -> None:
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    proof_ledger = json.loads((root / 'PROOF-OBLIGATION-LEDGER.json').read_text())
    assumption_ledger = json.loads((root / 'ASSUMPTION-DISCHARGE-LEDGER.json').read_text())
    formal_ledger = json.loads((root / 'FORMALIZATION-COVERAGE-LEDGER.json').read_text())
    route_rows = route_ledger.get('route_rows', [])
    proof_rows = proof_ledger.get('proof_obligation_rows', [])
    assumption_rows = assumption_ledger.get('assumption_discharge_rows', [])
    formal_rows = formal_ledger.get('formalization_rows', [])
    def counts(rows, key):
        out = {}
        for row in rows:
            value = row.get(key, '<missing>')
            out[value] = out.get(value, 0) + 1
        return out
    lines = [
        '# Formal proof / assumption discharge / formalization coverage summary (generated)',
        '',
        'Generated from `PROOF-OBLIGATION-LEDGER.json`, `ASSUMPTION-DISCHARGE-LEDGER.json`, `FORMALIZATION-COVERAGE-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{proof_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Proof-obligation rows: `{len(proof_rows)}`",
        f"- Assumption-discharge rows: `{len(assumption_rows)}`",
        f"- Formalization-coverage rows: `{len(formal_rows)}`",
        '',
        '## Proof-obligation class counts',
        '',
    ]
    for key in sorted(counts(proof_rows, 'proof_obligation_class')):
        lines.append(f"- `{key}`: `{counts(proof_rows, 'proof_obligation_class')[key]}`")
    lines += ['', '## Assumption-discharge class counts', '']
    for key in sorted(counts(assumption_rows, 'assumption_class')):
        lines.append(f"- `{key}`: `{counts(assumption_rows, 'assumption_class')[key]}`")
    lines += ['', '## Formalization-coverage class counts', '']
    for key in sorted(counts(formal_rows, 'coverage_class')):
        lines.append(f"- `{key}`: `{counts(formal_rows, 'coverage_class')[key]}`")
    lines += ['', '## Route handles', '', '| Route | Proof obligations | Assumption discharge | Formalization coverage |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('proof_obligation_ids', []))}` | `{len(row.get('assumption_discharge_ids', []))}` | `{len(row.get('formalization_coverage_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Proof obligations, assumption-discharge rows, and formalization coverage make proof and derivation language auditable. They can cap, freeze, demote, or roll back theorem, no-go, uniqueness, consistency, formal-verification, proof-assistant, proof-certificate, and assumption-discharge language, but they do not promote a route beyond its state-machine, public-record, evidence-credit, contrast/update, measurement/systematics, validity/transport, causal, selection, capacity, semantic, social-authority, computational, or residual-cap limits.', '']
    out = root / 'docs/30-program/formal-proof-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/formal-proof-summary.generated.md')



def augment_authority_dependency_graph_with_idealization_edges(root: Path) -> None:
    """Add idealization / approximation-error / limit-interchange edges after the base graph is rendered."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    rows = graph.get('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id():
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key = (source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({
            'edge_id': next_edge_id(),
            'source_kind': source_kind,
            'source_id': source_id,
            'dependent_kind': dependent_kind,
            'dependent_id': dependent_id,
            'dependency_kind': dependency_kind,
            'required_for': required_for,
            'failure_effect': failure_effect,
            'max_credit_transmitted': max_credit,
        })
        existing.add(key)
    if 'IDEALIZATION-LEDGER.json' not in graph.get('generated_from', []):
        graph.setdefault('generated_from', []).extend(['IDEALIZATION-LEDGER.json','APPROXIMATION-ERROR-LEDGER.json','LIMIT-INTERCHANGE-LEDGER.json'])
    graph['generation_rule'] = graph.get('generation_rule','') + ' Idealization / approximation-error / limit-interchange edges are appended by the rev0276 augmentation pass.'
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid = row.get('route_id', '')
        effect = row.get('promotion_ceiling', '') or row.get('authority_state', '')
        for iid in row.get('idealization_ids', []):
            add('idealization', iid, 'route', rid, 'idealization-condition', 'route idealized-target denominator', 'cap ideal-model support when the simplified target differs from the claimed target', effect)
        for aid in row.get('approximation_error_ids', []):
            add('approximation-error', aid, 'route', rid, 'approximation-error-condition', 'route approximation-error denominator', 'cap approximate support when error budgets or residual propagation fail', effect)
        for lid in row.get('limit_interchange_ids', []):
            add('limit-interchange', lid, 'route', rid, 'limit-interchange-condition', 'route limit-sequence / finite-recovery denominator', 'cap exact-limit support when limits do not commute, are singular, or lack finite-regime recovery', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'open-question' if str(target_id).startswith('OQ-') else 'claim'
        effect = binding.get('maximum_authority_effect', '') or 'bounded by binding row'
        for iid in binding.get('idealization_ids', []):
            add('idealization', iid, target_kind, target_id, 'idealization-claim-condition', f'claim idealization denominator under {binding.get("binding_id")}', 'freeze ideal-model claim wording until idealization rows are restored', effect)
        for aid in binding.get('approximation_error_ids', []):
            add('approximation-error', aid, target_kind, target_id, 'approximation-error-claim-condition', f'claim approximation-error denominator under {binding.get("binding_id")}', 'freeze approximation/deidealization claim wording until error rows are restored', effect)
        for lid in binding.get('limit_interchange_ids', []):
            add('limit-interchange', lid, target_kind, target_id, 'limit-interchange-claim-condition', f'claim limit-interchange denominator under {binding.get("binding_id")}', 'freeze exact-limit / finite-target claim wording until limit rows are restored', effect)
    optional = [
        ('evidence-unit', 'evidence_unit_id', 'EVIDENCE-UNIT-LEDGER.json', 'evidence_units'),
        ('credit-allocation', 'credit_id', 'CREDIT-ALLOCATION-LEDGER.json', 'credit_rows'),
        ('empirical-delta', 'delta_id', 'EMPIRICAL-DELTA-LEDGER.json', 'empirical_deltas'),
        ('forecast', 'forecast_id', 'DISCRIMINATOR-FORECAST-LEDGER.json', 'forecast_rows'),
        ('decision-experiment', 'experiment_id', 'DECISION-EXPERIMENT-LEDGER.json', 'decision_experiments'),
        ('severity-test', 'severity_id', 'EVIDENCE-SEVERITY-LEDGER.json', 'severity_rows'),
        ('contrast-class', 'contrast_id', 'CONTRAST-CLASS-LEDGER.json', 'contrast_rows'),
        ('likelihood-update', 'update_id', 'LIKELIHOOD-UPDATE-LEDGER.json', 'update_rows'),
        ('prior-sensitivity', 'prior_id', 'PRIOR-SENSITIVITY-LEDGER.json', 'prior_rows'),
        ('measurement-model', 'measurement_model_id', 'MEASUREMENT-MODEL-LEDGER.json', 'measurement_model_rows'),
        ('systematic-uncertainty', 'systematic_id', 'SYSTEMATIC-UNCERTAINTY-LEDGER.json', 'systematic_rows'),
        ('calibration-traceability', 'calibration_id', 'CALIBRATION-TRACEABILITY-LEDGER.json', 'calibration_rows'),
        ('validity-domain', 'domain_id', 'DOMAIN-OF-VALIDITY-LEDGER.json', 'domain_rows'),
        ('transportability', 'transport_id', 'TRANSPORTABILITY-LEDGER.json', 'transport_rows'),
        ('extrapolation-fence', 'fence_id', 'EXTRAPOLATION-FENCE-LEDGER.json', 'fence_rows'),
        ('causal-mechanism', 'mechanism_id', 'CAUSAL-MECHANISM-LEDGER.json', 'mechanism_rows'),
        ('intervention-protocol', 'intervention_id', 'INTERVENTION-PROTOCOL-LEDGER.json', 'intervention_rows'),
        ('counterfactual-robustness', 'counterfactual_id', 'COUNTERFACTUAL-ROBUSTNESS-LEDGER.json', 'counterfactual_rows'),
        ('selection-function', 'selection_id', 'SELECTION-FUNCTION-LEDGER.json', 'selection_rows'),
        ('multiplicity-control', 'multiplicity_id', 'MULTIPLICITY-CONTROL-LEDGER.json', 'multiplicity_rows'),
        ('reporting-bias', 'bias_id', 'REPORTING-BIAS-LEDGER.json', 'bias_rows'),
        ('model-capacity', 'model_capacity_id', 'MODEL-CAPACITY-LEDGER.json', 'capacity_rows'),
        ('complexity-penalty', 'complexity_penalty_id', 'COMPLEXITY-PENALTY-LEDGER.json', 'complexity_rows'),
        ('generalization-validation', 'generalization_id', 'PREDICTIVE-GENERALIZATION-LEDGER.json', 'generalization_rows'),
        ('semantic-term', 'semantic_term_id', 'SEMANTIC-TERM-LEDGER.json', 'semantic_rows'),
        ('ontology-commitment', 'ontology_commitment_id', 'ONTOLOGY-COMMITMENT-LEDGER.json', 'commitment_rows'),
        ('claim-language-permission', 'language_permission_id', 'CLAIM-LANGUAGE-PERMISSION-LEDGER.json', 'permission_rows'),
        ('social-authority', 'social_authority_id', 'SOCIAL-AUTHORITY-LEDGER.json', 'social_rows'),
        ('review-replication', 'review_replication_id', 'REVIEW-REPLICATION-LEDGER.json', 'review_rows'),
        ('consensus-elicitation', 'consensus_elicitation_id', 'CONSENSUS-ELICITATION-LEDGER.json', 'consensus_rows'),
        ('computational-reproducibility', 'computational_reproducibility_id', 'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json', 'reproducibility_rows'),
        ('numerical-stability', 'numerical_stability_id', 'NUMERICAL-STABILITY-LEDGER.json', 'stability_rows'),
        ('software-supply-chain', 'software_supply_chain_id', 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json', 'supply_chain_rows'),
        ('proof-obligation', 'proof_obligation_id', 'PROOF-OBLIGATION-LEDGER.json', 'proof_obligation_rows'),
        ('assumption-discharge', 'assumption_discharge_id', 'ASSUMPTION-DISCHARGE-LEDGER.json', 'assumption_discharge_rows'),
        ('formalization-coverage', 'formalization_coverage_id', 'FORMALIZATION-COVERAGE-LEDGER.json', 'formalization_rows'),
    ]
    for dep_kind, id_key, file_name, rows_key in optional:
        path = root / file_name
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for item in data.get(rows_key, []):
            item_id = item.get(id_key, '')
            effect = item.get('maximum_authority_effect') or item.get('maximum_credit') or item.get('current_maximum_credit') or item.get('route_state_effect') or 'bounded by owning row'
            for iid in item.get('idealization_ids', []):
                add('idealization', iid, dep_kind, item_id, 'idealization-condition', f'{dep_kind} idealization denominator', 'remove ideal-model readings when idealization control fails', effect)
            for aid in item.get('approximation_error_ids', []):
                add('approximation-error', aid, dep_kind, item_id, 'approximation-error-condition', f'{dep_kind} approximation-error denominator', 'cap approximate readings when error budgets fail', effect)
            for lid in item.get('limit_interchange_ids', []):
                add('limit-interchange', lid, dep_kind, item_id, 'limit-interchange-condition', f'{dep_kind} limit-interchange denominator', 'cap exact-limit readings when limit safety or finite recovery fails', effect)
    graph['edge_rows'] = rows
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json idealization-limit edges')


def write_idealization_limit_summary(root: Path) -> None:
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    ideal_ledger = json.loads((root / 'IDEALIZATION-LEDGER.json').read_text())
    approx_ledger = json.loads((root / 'APPROXIMATION-ERROR-LEDGER.json').read_text())
    limit_ledger = json.loads((root / 'LIMIT-INTERCHANGE-LEDGER.json').read_text())
    route_rows = route_ledger.get('route_rows', [])
    ideal_rows = ideal_ledger.get('idealization_rows', [])
    approx_rows = approx_ledger.get('approximation_rows', [])
    limit_rows = limit_ledger.get('limit_rows', [])
    def counts(rows, key):
        out = {}
        for row in rows:
            value = row.get(key, '<missing>')
            out[value] = out.get(value, 0) + 1
        return out
    lines = [
        '# Idealization / approximation-error / limit-interchange summary (generated)',
        '',
        'Generated from `IDEALIZATION-LEDGER.json`, `APPROXIMATION-ERROR-LEDGER.json`, `LIMIT-INTERCHANGE-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{ideal_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Idealization rows: `{len(ideal_rows)}`",
        f"- Approximation-error rows: `{len(approx_rows)}`",
        f"- Limit-interchange rows: `{len(limit_rows)}`",
        '',
        '## Idealization class counts',
        '',
    ]
    for key in sorted(counts(ideal_rows, 'idealization_class')):
        lines.append(f"- `{key}`: `{counts(ideal_rows, 'idealization_class')[key]}`")
    lines += ['', '## Approximation-error class counts', '']
    for key in sorted(counts(approx_rows, 'approximation_error_class')):
        lines.append(f"- `{key}`: `{counts(approx_rows, 'approximation_error_class')[key]}`")
    lines += ['', '## Limit-interchange class counts', '']
    for key in sorted(counts(limit_rows, 'limit_interchange_class')):
        lines.append(f"- `{key}`: `{counts(limit_rows, 'limit_interchange_class')[key]}`")
    lines += ['', '## Route handles', '', '| Route | Idealizations | Approximation errors | Limit interchanges |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('idealization_ids', []))}` | `{len(row.get('approximation_error_ids', []))}` | `{len(row.get('limit_interchange_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Idealization rows, approximation-error rows, and limit-interchange rows make ideal-model and exact-limit language auditable. They can cap, freeze, demote, or roll back continuum, asymptotic, large-N, semiclassical, thermodynamic, regulator-removal, zero-noise, exact-limit, deidealized, and finite-target support language, but they do not promote a route beyond state-machine, public-record, evidence-credit, contrast/update, measurement/systematics, validity/transport, causal, selection, capacity, semantic, social-authority, computational, formal-proof, or residual-cap limits.', '']
    out = root / 'docs/30-program/idealization-limit-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/idealization-limit-summary.generated.md')


def augment_authority_dependency_graph_with_boundary_sector_edges(root: Path) -> None:
    """Add boundary-condition / initial-data / sector-selection edges after the base graph is rendered."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    rows = graph.get('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id():
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key = (source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({
            'edge_id': next_edge_id(),
            'source_kind': source_kind,
            'source_id': source_id,
            'dependent_kind': dependent_kind,
            'dependent_id': dependent_id,
            'dependency_kind': dependency_kind,
            'required_for': required_for,
            'failure_effect': failure_effect,
            'max_credit_transmitted': max_credit,
        })
        existing.add(key)
    for rel in ['BOUNDARY-CONDITION-LEDGER.json','INITIAL-DATA-LEDGER.json','SECTOR-SELECTION-LEDGER.json']:
        if rel not in graph.get('generated_from', []):
            graph.setdefault('generated_from', []).append(rel)
    graph['generation_rule'] = graph.get('generation_rule','') + ' Boundary-condition / initial-data / sector-selection edges are appended by the rev0277 augmentation pass.'
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid = row.get('route_id', '')
        effect = row.get('promotion_ceiling', '') or row.get('authority_state', '')
        for bid in row.get('boundary_condition_ids', []):
            add('boundary-condition', bid, 'route', rid, 'boundary-condition-condition', 'route boundary-condition denominator', 'cap boundary-conditioned support when boundary choices fail or change', effect)
        for iid in row.get('initial_data_ids', []):
            add('initial-data', iid, 'route', rid, 'initial-data-condition', 'route initial/preparation-data denominator', 'cap state-preparation or initial-condition support when initial data fail robustness tests', effect)
        for sid in row.get('sector_selection_ids', []):
            add('sector-selection', sid, 'route', rid, 'sector-selection-condition', 'route solution-sector denominator', 'cap selected-branch, selected-vacuum, selected-gauge, or selected-pipeline support when sector choice fails', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'open-question' if str(target_id).startswith('OQ-') else 'claim'
        effect = binding.get('maximum_authority_effect', '') or 'bounded by binding row'
        for bid in binding.get('boundary_condition_ids', []):
            add('boundary-condition', bid, target_kind, target_id, 'boundary-condition-claim-condition', f'claim boundary-condition denominator under {binding.get("binding_id")}', 'freeze boundary or background-independence claim wording until boundary rows are restored', effect)
        for iid in binding.get('initial_data_ids', []):
            add('initial-data', iid, target_kind, target_id, 'initial-data-claim-condition', f'claim initial-data denominator under {binding.get("binding_id")}', 'freeze initial-condition, preparation, ensemble, or vacuum wording until initial-data rows are restored', effect)
        for sid in binding.get('sector_selection_ids', []):
            add('sector-selection', sid, target_kind, target_id, 'sector-selection-claim-condition', f'claim sector-selection denominator under {binding.get("binding_id")}', 'freeze sector, branch, gauge, vacuum, regulator, apparatus, survey, or map-pipeline wording until sector rows are restored', effect)
    optional = [
        ('evidence-unit', 'evidence_unit_id', 'EVIDENCE-UNIT-LEDGER.json', 'evidence_units'),
        ('credit-allocation', 'credit_id', 'CREDIT-ALLOCATION-LEDGER.json', 'credit_rows'),
        ('empirical-delta', 'delta_id', 'EMPIRICAL-DELTA-LEDGER.json', 'empirical_deltas'),
        ('forecast', 'forecast_id', 'DISCRIMINATOR-FORECAST-LEDGER.json', 'forecast_rows'),
        ('decision-experiment', 'experiment_id', 'DECISION-EXPERIMENT-LEDGER.json', 'decision_experiments'),
        ('severity-test', 'severity_id', 'EVIDENCE-SEVERITY-LEDGER.json', 'severity_rows'),
        ('contrast-class', 'contrast_id', 'CONTRAST-CLASS-LEDGER.json', 'contrast_rows'),
        ('likelihood-update', 'update_id', 'LIKELIHOOD-UPDATE-LEDGER.json', 'update_rows'),
        ('prior-sensitivity', 'prior_id', 'PRIOR-SENSITIVITY-LEDGER.json', 'prior_rows'),
        ('measurement-model', 'measurement_model_id', 'MEASUREMENT-MODEL-LEDGER.json', 'measurement_model_rows'),
        ('systematic-uncertainty', 'systematic_id', 'SYSTEMATIC-UNCERTAINTY-LEDGER.json', 'systematic_rows'),
        ('calibration-traceability', 'calibration_id', 'CALIBRATION-TRACEABILITY-LEDGER.json', 'calibration_rows'),
        ('validity-domain', 'domain_id', 'DOMAIN-OF-VALIDITY-LEDGER.json', 'domain_rows'),
        ('transportability', 'transport_id', 'TRANSPORTABILITY-LEDGER.json', 'transport_rows'),
        ('extrapolation-fence', 'fence_id', 'EXTRAPOLATION-FENCE-LEDGER.json', 'fence_rows'),
        ('causal-mechanism', 'mechanism_id', 'CAUSAL-MECHANISM-LEDGER.json', 'mechanism_rows'),
        ('intervention-protocol', 'intervention_id', 'INTERVENTION-PROTOCOL-LEDGER.json', 'intervention_rows'),
        ('counterfactual-robustness', 'counterfactual_id', 'COUNTERFACTUAL-ROBUSTNESS-LEDGER.json', 'counterfactual_rows'),
        ('selection-function', 'selection_id', 'SELECTION-FUNCTION-LEDGER.json', 'selection_rows'),
        ('multiplicity-control', 'multiplicity_id', 'MULTIPLICITY-CONTROL-LEDGER.json', 'multiplicity_rows'),
        ('reporting-bias', 'bias_id', 'REPORTING-BIAS-LEDGER.json', 'bias_rows'),
        ('model-capacity', 'model_capacity_id', 'MODEL-CAPACITY-LEDGER.json', 'capacity_rows'),
        ('complexity-penalty', 'complexity_penalty_id', 'COMPLEXITY-PENALTY-LEDGER.json', 'complexity_rows'),
        ('generalization-validation', 'generalization_id', 'PREDICTIVE-GENERALIZATION-LEDGER.json', 'generalization_rows'),
        ('semantic-term', 'semantic_term_id', 'SEMANTIC-TERM-LEDGER.json', 'semantic_rows'),
        ('ontology-commitment', 'ontology_commitment_id', 'ONTOLOGY-COMMITMENT-LEDGER.json', 'commitment_rows'),
        ('claim-language-permission', 'language_permission_id', 'CLAIM-LANGUAGE-PERMISSION-LEDGER.json', 'permission_rows'),
        ('social-authority', 'social_authority_id', 'SOCIAL-AUTHORITY-LEDGER.json', 'social_rows'),
        ('review-replication', 'review_replication_id', 'REVIEW-REPLICATION-LEDGER.json', 'review_rows'),
        ('consensus-elicitation', 'consensus_elicitation_id', 'CONSENSUS-ELICITATION-LEDGER.json', 'consensus_rows'),
        ('computational-reproducibility', 'computational_reproducibility_id', 'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json', 'reproducibility_rows'),
        ('numerical-stability', 'numerical_stability_id', 'NUMERICAL-STABILITY-LEDGER.json', 'stability_rows'),
        ('software-supply-chain', 'software_supply_chain_id', 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json', 'supply_chain_rows'),
        ('proof-obligation', 'proof_obligation_id', 'PROOF-OBLIGATION-LEDGER.json', 'proof_obligation_rows'),
        ('assumption-discharge', 'assumption_discharge_id', 'ASSUMPTION-DISCHARGE-LEDGER.json', 'assumption_discharge_rows'),
        ('formalization-coverage', 'formalization_coverage_id', 'FORMALIZATION-COVERAGE-LEDGER.json', 'formalization_rows'),
        ('idealization', 'idealization_id', 'IDEALIZATION-LEDGER.json', 'idealization_rows'),
        ('approximation-error', 'approximation_error_id', 'APPROXIMATION-ERROR-LEDGER.json', 'approximation_rows'),
        ('limit-interchange', 'limit_interchange_id', 'LIMIT-INTERCHANGE-LEDGER.json', 'limit_rows'),
    ]
    for dep_kind, id_key, file_name, rows_key in optional:
        path = root / file_name
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for item in data.get(rows_key, []):
            item_id = item.get(id_key, '')
            effect = item.get('maximum_authority_effect') or item.get('maximum_credit') or item.get('current_maximum_credit') or item.get('route_state_effect') or 'bounded by owning row'
            for bid in item.get('boundary_condition_ids', []):
                add('boundary-condition', bid, dep_kind, item_id, 'boundary-condition-condition', f'{dep_kind} boundary-condition denominator', 'remove boundary-conditioned readings when boundary control fails', effect)
            for iid in item.get('initial_data_ids', []):
                add('initial-data', iid, dep_kind, item_id, 'initial-data-condition', f'{dep_kind} initial-data denominator', 'cap initial-condition or preparation readings when initial data control fails', effect)
            for sid in item.get('sector_selection_ids', []):
                add('sector-selection', sid, dep_kind, item_id, 'sector-selection-condition', f'{dep_kind} sector-selection denominator', 'cap selected-sector readings when branch, vacuum, gauge, regulator, apparatus, survey, or map-pipeline control fails', effect)
    graph['edge_rows'] = rows
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json boundary-sector edges')


def write_boundary_sector_summary(root: Path) -> None:
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    boundary_ledger = json.loads((root / 'BOUNDARY-CONDITION-LEDGER.json').read_text())
    initial_ledger = json.loads((root / 'INITIAL-DATA-LEDGER.json').read_text())
    sector_ledger = json.loads((root / 'SECTOR-SELECTION-LEDGER.json').read_text())
    route_rows = route_ledger.get('route_rows', [])
    boundary_rows = boundary_ledger.get('boundary_rows', [])
    initial_rows = initial_ledger.get('initial_data_rows', [])
    sector_rows = sector_ledger.get('sector_rows', [])
    def counts(rows, key):
        out = {}
        for row in rows:
            value = row.get(key, '<missing>')
            out[value] = out.get(value, 0) + 1
        return out
    lines = [
        '# Boundary-condition / initial-data / sector-selection summary (generated)',
        '',
        'Generated from `BOUNDARY-CONDITION-LEDGER.json`, `INITIAL-DATA-LEDGER.json`, `SECTOR-SELECTION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`.',
        'Do not edit this file directly; run `make index` after changing executable ledgers.',
        '',
        f"- Revision: `{boundary_ledger.get('revision', '<missing>')}`",
        f"- Route rows: `{len(route_rows)}`",
        f"- Boundary-condition rows: `{len(boundary_rows)}`",
        f"- Initial-data rows: `{len(initial_rows)}`",
        f"- Sector-selection rows: `{len(sector_rows)}`",
        '',
        '## Boundary-condition class counts',
        '',
    ]
    for key in sorted(counts(boundary_rows, 'boundary_class')):
        lines.append(f"- `{key}`: `{counts(boundary_rows, 'boundary_class')[key]}`")
    lines += ['', '## Initial-data class counts', '']
    for key in sorted(counts(initial_rows, 'initial_data_class')):
        lines.append(f"- `{key}`: `{counts(initial_rows, 'initial_data_class')[key]}`")
    lines += ['', '## Sector-selection class counts', '']
    for key in sorted(counts(sector_rows, 'sector_selection_class')):
        lines.append(f"- `{key}`: `{counts(sector_rows, 'sector_selection_class')[key]}`")
    lines += ['', '## Route handles', '', '| Route | Boundary conditions | Initial data | Sector selection |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('boundary_condition_ids', []))}` | `{len(row.get('initial_data_ids', []))}` | `{len(row.get('sector_selection_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Boundary-condition rows, initial-data rows, and sector-selection rows make background, boundary, preparation, ensemble, vacuum, gauge, regulator, apparatus, survey-window, map-pipeline, and solution-branch language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, evidence-credit, contrast/update, measurement/systematics, validity/transport, causal, selection, capacity, semantic, social-authority, computational, formal-proof, idealization, or residual-cap limits.', '']
    out = root / 'docs/30-program/boundary-sector-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/boundary-sector-summary.generated.md')


def augment_authority_dependency_graph_with_gauge_constraint_edges(root: Path) -> None:
    """Add gauge-symmetry / constraint-closure / observable-quotient edges after boundary/sector edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    rows = graph.get('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id():
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key = (source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({
            'edge_id': next_edge_id(),
            'source_kind': source_kind,
            'source_id': source_id,
            'dependent_kind': dependent_kind,
            'dependent_id': dependent_id,
            'dependency_kind': dependency_kind,
            'required_for': required_for,
            'failure_effect': failure_effect,
            'max_credit_transmitted': max_credit,
        })
        existing.add(key)
    for rel in ['GAUGE-SYMMETRY-LEDGER.json','CONSTRAINT-CLOSURE-LEDGER.json','OBSERVABLE-QUOTIENT-LEDGER.json']:
        if rel not in graph.get('generated_from', []):
            graph.setdefault('generated_from', []).append(rel)
    graph['generation_rule'] = graph.get('generation_rule','') + ' Gauge-symmetry / constraint-closure / observable-quotient edges are appended by the rev0278 augmentation pass.'
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid = row.get('route_id', '')
        effect = row.get('promotion_ceiling', '') or row.get('authority_state', '')
        for gid in row.get('gauge_symmetry_ids', []):
            add('gauge-symmetry', gid, 'route', rid, 'gauge-symmetry-condition', 'route gauge/redundancy denominator', 'cap gauge-invariant or representative-independent support when gauge/redundancy control fails', effect)
        for cid in row.get('constraint_closure_ids', []):
            add('constraint-closure', cid, 'route', rid, 'constraint-closure-condition', 'route constraint-closure denominator', 'cap anomaly-free, first-class, BRST/BV, Ward-identity, or reduction claims when closure fails', effect)
        for oid in row.get('observable_quotient_ids', []):
            add('observable-quotient', oid, 'route', rid, 'observable-quotient-condition', 'route observable-quotient denominator', 'cap physical-observable or candidate-native record wording when quotient/invariant test fails', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'open-question' if str(target_id).startswith('OQ-') else 'claim'
        effect = binding.get('maximum_authority_effect', '') or 'bounded by binding row'
        for gid in binding.get('gauge_symmetry_ids', []):
            add('gauge-symmetry', gid, target_kind, target_id, 'gauge-symmetry-claim-condition', f'claim gauge-symmetry denominator under {binding.get("binding_id")}', 'freeze gauge-invariant or representative-independent wording until gauge rows are restored', effect)
        for cid in binding.get('constraint_closure_ids', []):
            add('constraint-closure', cid, target_kind, target_id, 'constraint-closure-claim-condition', f'claim constraint-closure denominator under {binding.get("binding_id")}', 'freeze constraint-closed, anomaly-free, BRST/BV, Ward-identity, or reduced wording until constraint rows are restored', effect)
        for oid in binding.get('observable_quotient_ids', []):
            add('observable-quotient', oid, target_kind, target_id, 'observable-quotient-claim-condition', f'claim observable-quotient denominator under {binding.get("binding_id")}', 'freeze physical-observable, Dirac-observable, cohomology, or candidate-native record wording until quotient rows are restored', effect)
    # Also connect route-support rows that explicitly carry the new handles.
    optional = [
        ('evidence-unit', 'evidence_unit_id', 'EVIDENCE-UNIT-LEDGER.json', 'evidence_units'),
        ('credit-allocation', 'credit_id', 'CREDIT-ALLOCATION-LEDGER.json', 'credit_rows'),
        ('empirical-delta', 'delta_id', 'EMPIRICAL-DELTA-LEDGER.json', 'empirical_deltas'),
        ('forecast', 'forecast_id', 'DISCRIMINATOR-FORECAST-LEDGER.json', 'forecast_rows'),
        ('decision-experiment', 'experiment_id', 'DECISION-EXPERIMENT-LEDGER.json', 'decision_experiments'),
        ('severity-test', 'severity_id', 'EVIDENCE-SEVERITY-LEDGER.json', 'severity_rows'),
        ('contrast-class', 'contrast_id', 'CONTRAST-CLASS-LEDGER.json', 'contrast_rows'),
        ('likelihood-update', 'update_id', 'LIKELIHOOD-UPDATE-LEDGER.json', 'update_rows'),
        ('prior-sensitivity', 'prior_id', 'PRIOR-SENSITIVITY-LEDGER.json', 'prior_rows'),
        ('measurement-model', 'measurement_model_id', 'MEASUREMENT-MODEL-LEDGER.json', 'measurement_model_rows'),
        ('systematic-uncertainty', 'systematic_id', 'SYSTEMATIC-UNCERTAINTY-LEDGER.json', 'systematic_rows'),
        ('calibration-traceability', 'calibration_id', 'CALIBRATION-TRACEABILITY-LEDGER.json', 'calibration_rows'),
        ('validity-domain', 'domain_id', 'DOMAIN-OF-VALIDITY-LEDGER.json', 'domain_rows'),
        ('transportability', 'transport_id', 'TRANSPORTABILITY-LEDGER.json', 'transport_rows'),
        ('extrapolation-fence', 'fence_id', 'EXTRAPOLATION-FENCE-LEDGER.json', 'fence_rows'),
        ('causal-mechanism', 'mechanism_id', 'CAUSAL-MECHANISM-LEDGER.json', 'mechanism_rows'),
        ('intervention-protocol', 'intervention_id', 'INTERVENTION-PROTOCOL-LEDGER.json', 'intervention_rows'),
        ('counterfactual-robustness', 'counterfactual_id', 'COUNTERFACTUAL-ROBUSTNESS-LEDGER.json', 'counterfactual_rows'),
        ('selection-function', 'selection_id', 'SELECTION-FUNCTION-LEDGER.json', 'selection_rows'),
        ('multiplicity-control', 'multiplicity_id', 'MULTIPLICITY-CONTROL-LEDGER.json', 'multiplicity_rows'),
        ('reporting-bias', 'bias_id', 'REPORTING-BIAS-LEDGER.json', 'bias_rows'),
        ('model-capacity', 'model_capacity_id', 'MODEL-CAPACITY-LEDGER.json', 'capacity_rows'),
        ('complexity-penalty', 'complexity_penalty_id', 'COMPLEXITY-PENALTY-LEDGER.json', 'complexity_rows'),
        ('generalization-validation', 'generalization_id', 'PREDICTIVE-GENERALIZATION-LEDGER.json', 'generalization_rows'),
        ('semantic-term', 'semantic_term_id', 'SEMANTIC-TERM-LEDGER.json', 'semantic_rows'),
        ('ontology-commitment', 'ontology_commitment_id', 'ONTOLOGY-COMMITMENT-LEDGER.json', 'commitment_rows'),
        ('claim-language-permission', 'language_permission_id', 'CLAIM-LANGUAGE-PERMISSION-LEDGER.json', 'permission_rows'),
        ('social-authority', 'social_authority_id', 'SOCIAL-AUTHORITY-LEDGER.json', 'social_rows'),
        ('review-replication', 'review_replication_id', 'REVIEW-REPLICATION-LEDGER.json', 'review_rows'),
        ('consensus-elicitation', 'consensus_elicitation_id', 'CONSENSUS-ELICITATION-LEDGER.json', 'consensus_rows'),
        ('computational-reproducibility', 'computational_reproducibility_id', 'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json', 'reproducibility_rows'),
        ('numerical-stability', 'numerical_stability_id', 'NUMERICAL-STABILITY-LEDGER.json', 'stability_rows'),
        ('software-supply-chain', 'software_supply_chain_id', 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json', 'supply_chain_rows'),
        ('proof-obligation', 'proof_obligation_id', 'PROOF-OBLIGATION-LEDGER.json', 'proof_obligation_rows'),
        ('assumption-discharge', 'assumption_discharge_id', 'ASSUMPTION-DISCHARGE-LEDGER.json', 'assumption_discharge_rows'),
        ('formalization-coverage', 'formalization_coverage_id', 'FORMALIZATION-COVERAGE-LEDGER.json', 'formalization_rows'),
        ('idealization', 'idealization_id', 'IDEALIZATION-LEDGER.json', 'idealization_rows'),
        ('approximation-error', 'approximation_error_id', 'APPROXIMATION-ERROR-LEDGER.json', 'approximation_rows'),
        ('limit-interchange', 'limit_interchange_id', 'LIMIT-INTERCHANGE-LEDGER.json', 'limit_rows'),
        ('boundary-condition', 'boundary_condition_id', 'BOUNDARY-CONDITION-LEDGER.json', 'boundary_rows'),
        ('initial-data', 'initial_data_id', 'INITIAL-DATA-LEDGER.json', 'initial_data_rows'),
        ('sector-selection', 'sector_selection_id', 'SECTOR-SELECTION-LEDGER.json', 'sector_rows'),
    ]
    for dep_kind, id_key, file_name, rows_key in optional:
        path = root / file_name
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for item in data.get(rows_key, []):
            item_id = item.get(id_key, '')
            effect = item.get('maximum_authority_effect') or item.get('maximum_credit') or item.get('current_maximum_credit') or item.get('route_state_effect') or 'bounded by owning row'
            for gid in item.get('gauge_symmetry_ids', []):
                add('gauge-symmetry', gid, dep_kind, item_id, 'gauge-symmetry-condition', f'{dep_kind} gauge-symmetry denominator', 'remove gauge-invariant readings when gauge control fails', effect)
            for cid in item.get('constraint_closure_ids', []):
                add('constraint-closure', cid, dep_kind, item_id, 'constraint-closure-condition', f'{dep_kind} constraint-closure denominator', 'remove constraint-closed readings when closure/anomaly control fails', effect)
            for oid in item.get('observable_quotient_ids', []):
                add('observable-quotient', oid, dep_kind, item_id, 'observable-quotient-condition', f'{dep_kind} observable-quotient denominator', 'remove physical-observable readings when quotient/invariant control fails', effect)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json gauge/constraint/observable edges')


def write_gauge_constraint_summary(root: Path) -> None:
    gauge_ledger = json.loads((root / 'GAUGE-SYMMETRY-LEDGER.json').read_text())
    constraint_ledger = json.loads((root / 'CONSTRAINT-CLOSURE-LEDGER.json').read_text())
    observable_ledger = json.loads((root / 'OBSERVABLE-QUOTIENT-LEDGER.json').read_text())
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    gauge_rows = gauge_ledger.get('gauge_rows', [])
    constraint_rows = constraint_ledger.get('constraint_rows', [])
    observable_rows = observable_ledger.get('observable_rows', [])
    route_rows = route_ledger.get('route_rows', [])
    def counts(rows, key):
        out = {}
        for row in rows:
            out[row.get(key,'<missing>')] = out.get(row.get(key,'<missing>'), 0) + 1
        return out
    lines = [
        '# Gauge / constraint / observable-quotient summary (generated)', '',
        'Generated by `tools/sync_generated_surfaces.py`. Do not edit by hand.', '',
        f"- Revision: `{gauge_ledger.get('revision', '<missing>')}`",
        f"- Gauge-symmetry rows: `{len(gauge_rows)}`",
        f"- Constraint-closure rows: `{len(constraint_rows)}`",
        f"- Observable-quotient rows: `{len(observable_rows)}`",
        '', '## Gauge-symmetry class counts', ''
    ]
    for key in sorted(counts(gauge_rows, 'gauge_symmetry_class')):
        lines.append(f"- `{key}`: `{counts(gauge_rows, 'gauge_symmetry_class')[key]}`")
    lines += ['', '## Constraint-closure class counts', '']
    for key in sorted(counts(constraint_rows, 'constraint_closure_class')):
        lines.append(f"- `{key}`: `{counts(constraint_rows, 'constraint_closure_class')[key]}`")
    lines += ['', '## Observable-quotient class counts', '']
    for key in sorted(counts(observable_rows, 'observable_quotient_class')):
        lines.append(f"- `{key}`: `{counts(observable_rows, 'observable_quotient_class')[key]}`")
    lines += ['', '## Route handles', '', '| Route | Gauge rows | Constraint rows | Observable quotient rows |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('gauge_symmetry_ids', []))}` | `{len(row.get('constraint_closure_ids', []))}` | `{len(row.get('observable_quotient_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Gauge-symmetry rows, constraint-closure rows, and observable-quotient rows make gauge-invariant, representative-independent, physical-observable, Dirac-observable, BRST/cohomology, anomaly-free, reduced, and constraint-closed language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, evidence-credit, contrast/update, measurement/systematics, validity/transport, causal, selection, capacity, semantic, social-authority, computational, formal-proof, idealization, boundary/sector, or residual-cap limits.', '']
    out = root / 'docs/30-program/gauge-constraint-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/gauge-constraint-summary.generated.md')


def augment_authority_dependency_graph_with_renormalization_matching_edges(root: Path) -> None:
    """Add regularization-scheme / renormalization-flow / matching-condition edges after gauge/observable edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    rows = graph.get('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id():
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key = (source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({
            'edge_id': next_edge_id(),
            'source_kind': source_kind,
            'source_id': source_id,
            'dependent_kind': dependent_kind,
            'dependent_id': dependent_id,
            'dependency_kind': dependency_kind,
            'required_for': required_for,
            'failure_effect': failure_effect,
            'max_credit_transmitted': max_credit,
        })
        existing.add(key)
    for rel in ['REGULARIZATION-SCHEME-LEDGER.json','RENORMALIZATION-FLOW-LEDGER.json','MATCHING-CONDITION-LEDGER.json']:
        if rel not in graph.get('generated_from', []):
            graph.setdefault('generated_from', []).append(rel)
    graph['generation_rule'] = graph.get('generation_rule','') + ' Regularization-scheme / renormalization-flow / matching-condition edges are appended by the rev0279 augmentation pass.'
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid = row.get('route_id', '')
        effect = row.get('promotion_ceiling', '') or row.get('authority_state', '')
        for sid in row.get('regularization_scheme_ids', []):
            add('regularization-scheme', sid, 'route', rid, 'regularization-scheme-condition', 'route regulator/scheme denominator', 'cap regulator-independent or scheme-independent support when scheme control fails', effect)
        for fid in row.get('renormalization_flow_ids', []):
            add('renormalization-flow', fid, 'route', rid, 'renormalization-flow-condition', 'route RG-flow / running / fixed-point denominator', 'cap RG-invariant, fixed-point, running-parameter, or universality wording when flow control fails', effect)
        for mid in row.get('matching_condition_ids', []):
            add('matching-condition', mid, 'route', rid, 'matching-condition-condition', 'route scale/EFT/threshold matching denominator', 'cap source-to-target scale transfer when matching residuals fail', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'open-question' if str(target_id).startswith('OQ-') else 'claim'
        effect = binding.get('maximum_authority_effect', '') or 'bounded by binding row'
        for sid in binding.get('regularization_scheme_ids', []):
            add('regularization-scheme', sid, target_kind, target_id, 'regularization-scheme-claim-condition', f'claim regularization-scheme denominator under {binding.get("binding_id")}', 'freeze regulator-independent or scheme-independent wording until scheme rows are restored', effect)
        for fid in binding.get('renormalization_flow_ids', []):
            add('renormalization-flow', fid, target_kind, target_id, 'renormalization-flow-claim-condition', f'claim renormalization-flow denominator under {binding.get("binding_id")}', 'freeze RG-flow, running-parameter, fixed-point, or universality wording until flow rows are restored', effect)
        for mid in binding.get('matching_condition_ids', []):
            add('matching-condition', mid, target_kind, target_id, 'matching-condition-claim-condition', f'claim matching-condition denominator under {binding.get("binding_id")}', 'freeze threshold/EFT/counterterm/scale-matching wording until matching rows are restored', effect)
    optional = [
        ('evidence-unit', 'evidence_unit_id', 'EVIDENCE-UNIT-LEDGER.json', 'evidence_units'),
        ('credit-allocation', 'credit_id', 'CREDIT-ALLOCATION-LEDGER.json', 'credit_rows'),
        ('empirical-delta', 'delta_id', 'EMPIRICAL-DELTA-LEDGER.json', 'empirical_deltas'),
        ('forecast', 'forecast_id', 'DISCRIMINATOR-FORECAST-LEDGER.json', 'forecast_rows'),
        ('decision-experiment', 'experiment_id', 'DECISION-EXPERIMENT-LEDGER.json', 'decision_experiments'),
        ('severity-test', 'severity_id', 'EVIDENCE-SEVERITY-LEDGER.json', 'severity_rows'),
        ('contrast-class', 'contrast_id', 'CONTRAST-CLASS-LEDGER.json', 'contrast_rows'),
        ('likelihood-update', 'update_id', 'LIKELIHOOD-UPDATE-LEDGER.json', 'update_rows'),
        ('prior-sensitivity', 'prior_id', 'PRIOR-SENSITIVITY-LEDGER.json', 'prior_rows'),
        ('measurement-model', 'measurement_model_id', 'MEASUREMENT-MODEL-LEDGER.json', 'measurement_model_rows'),
        ('systematic-uncertainty', 'systematic_id', 'SYSTEMATIC-UNCERTAINTY-LEDGER.json', 'systematic_rows'),
        ('calibration-traceability', 'calibration_id', 'CALIBRATION-TRACEABILITY-LEDGER.json', 'calibration_rows'),
        ('validity-domain', 'domain_id', 'DOMAIN-OF-VALIDITY-LEDGER.json', 'domain_rows'),
        ('transportability', 'transport_id', 'TRANSPORTABILITY-LEDGER.json', 'transport_rows'),
        ('extrapolation-fence', 'fence_id', 'EXTRAPOLATION-FENCE-LEDGER.json', 'fence_rows'),
        ('causal-mechanism', 'mechanism_id', 'CAUSAL-MECHANISM-LEDGER.json', 'mechanism_rows'),
        ('intervention-protocol', 'intervention_id', 'INTERVENTION-PROTOCOL-LEDGER.json', 'intervention_rows'),
        ('counterfactual-robustness', 'counterfactual_id', 'COUNTERFACTUAL-ROBUSTNESS-LEDGER.json', 'counterfactual_rows'),
        ('selection-function', 'selection_id', 'SELECTION-FUNCTION-LEDGER.json', 'selection_rows'),
        ('multiplicity-control', 'multiplicity_id', 'MULTIPLICITY-CONTROL-LEDGER.json', 'multiplicity_rows'),
        ('reporting-bias', 'bias_id', 'REPORTING-BIAS-LEDGER.json', 'bias_rows'),
        ('model-capacity', 'model_capacity_id', 'MODEL-CAPACITY-LEDGER.json', 'capacity_rows'),
        ('complexity-penalty', 'complexity_penalty_id', 'COMPLEXITY-PENALTY-LEDGER.json', 'complexity_rows'),
        ('generalization-validation', 'generalization_id', 'PREDICTIVE-GENERALIZATION-LEDGER.json', 'generalization_rows'),
        ('semantic-term', 'semantic_term_id', 'SEMANTIC-TERM-LEDGER.json', 'semantic_rows'),
        ('ontology-commitment', 'ontology_commitment_id', 'ONTOLOGY-COMMITMENT-LEDGER.json', 'commitment_rows'),
        ('claim-language-permission', 'language_permission_id', 'CLAIM-LANGUAGE-PERMISSION-LEDGER.json', 'permission_rows'),
        ('social-authority', 'social_authority_id', 'SOCIAL-AUTHORITY-LEDGER.json', 'social_rows'),
        ('review-replication', 'review_replication_id', 'REVIEW-REPLICATION-LEDGER.json', 'review_rows'),
        ('consensus-elicitation', 'consensus_elicitation_id', 'CONSENSUS-ELICITATION-LEDGER.json', 'consensus_rows'),
        ('computational-reproducibility', 'computational_reproducibility_id', 'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json', 'reproducibility_rows'),
        ('numerical-stability', 'numerical_stability_id', 'NUMERICAL-STABILITY-LEDGER.json', 'stability_rows'),
        ('software-supply-chain', 'software_supply_chain_id', 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json', 'supply_chain_rows'),
        ('proof-obligation', 'proof_obligation_id', 'PROOF-OBLIGATION-LEDGER.json', 'proof_obligation_rows'),
        ('assumption-discharge', 'assumption_discharge_id', 'ASSUMPTION-DISCHARGE-LEDGER.json', 'assumption_discharge_rows'),
        ('formalization-coverage', 'formalization_coverage_id', 'FORMALIZATION-COVERAGE-LEDGER.json', 'formalization_rows'),
        ('idealization', 'idealization_id', 'IDEALIZATION-LEDGER.json', 'idealization_rows'),
        ('approximation-error', 'approximation_error_id', 'APPROXIMATION-ERROR-LEDGER.json', 'approximation_rows'),
        ('limit-interchange', 'limit_interchange_id', 'LIMIT-INTERCHANGE-LEDGER.json', 'limit_rows'),
        ('boundary-condition', 'boundary_condition_id', 'BOUNDARY-CONDITION-LEDGER.json', 'boundary_rows'),
        ('initial-data', 'initial_data_id', 'INITIAL-DATA-LEDGER.json', 'initial_data_rows'),
        ('sector-selection', 'sector_selection_id', 'SECTOR-SELECTION-LEDGER.json', 'sector_rows'),
        ('gauge-symmetry', 'gauge_symmetry_id', 'GAUGE-SYMMETRY-LEDGER.json', 'gauge_rows'),
        ('constraint-closure', 'constraint_closure_id', 'CONSTRAINT-CLOSURE-LEDGER.json', 'constraint_rows'),
        ('observable-quotient', 'observable_quotient_id', 'OBSERVABLE-QUOTIENT-LEDGER.json', 'observable_rows'),
    ]
    for dep_kind, id_key, file_name, rows_key in optional:
        path = root / file_name
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for item in data.get(rows_key, []):
            item_id = item.get(id_key, '')
            effect = item.get('maximum_authority_effect') or item.get('maximum_credit') or item.get('current_maximum_credit') or item.get('route_state_effect') or 'bounded by owning row'
            for sid in item.get('regularization_scheme_ids', []):
                add('regularization-scheme', sid, dep_kind, item_id, 'regularization-scheme-condition', f'{dep_kind} regularization-scheme denominator', 'remove scheme-independent readings when regularization/scheme control fails', effect)
            for fid in item.get('renormalization_flow_ids', []):
                add('renormalization-flow', fid, dep_kind, item_id, 'renormalization-flow-condition', f'{dep_kind} renormalization-flow denominator', 'remove RG-invariant, fixed-point, running, or universality readings when flow control fails', effect)
            for mid in item.get('matching_condition_ids', []):
                add('matching-condition', mid, dep_kind, item_id, 'matching-condition-condition', f'{dep_kind} matching-condition denominator', 'remove scale-transfer, EFT-matching, or threshold-matching readings when matching control fails', effect)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json regularization/renormalization/matching edges')


def write_renormalization_matching_summary(root: Path) -> None:
    reg_ledger = json.loads((root / 'REGULARIZATION-SCHEME-LEDGER.json').read_text())
    rgf_ledger = json.loads((root / 'RENORMALIZATION-FLOW-LEDGER.json').read_text())
    mat_ledger = json.loads((root / 'MATCHING-CONDITION-LEDGER.json').read_text())
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    reg_rows = reg_ledger.get('regularization_rows', [])
    rgf_rows = rgf_ledger.get('flow_rows', [])
    mat_rows = mat_ledger.get('matching_rows', [])
    route_rows = route_ledger.get('route_rows', [])
    def counts(rows, key):
        out = {}
        for row in rows:
            out[row.get(key,'<missing>')] = out.get(row.get(key,'<missing>'), 0) + 1
        return out
    lines = [
        '# Regularization / renormalization / matching summary (generated)', '',
        'Generated by `tools/sync_generated_surfaces.py`. Do not edit by hand.', '',
        f"- Revision: `{reg_ledger.get('revision', '<missing>')}`",
        f"- Regularization-scheme rows: `{len(reg_rows)}`",
        f"- Renormalization-flow rows: `{len(rgf_rows)}`",
        f"- Matching-condition rows: `{len(mat_rows)}`",
        '', '## Regularization-scheme class counts', ''
    ]
    for key in sorted(counts(reg_rows, 'regularization_scheme_class')):
        lines.append(f"- `{key}`: `{counts(reg_rows, 'regularization_scheme_class')[key]}`")
    lines += ['', '## Renormalization-flow class counts', '']
    for key in sorted(counts(rgf_rows, 'renormalization_flow_class')):
        lines.append(f"- `{key}`: `{counts(rgf_rows, 'renormalization_flow_class')[key]}`")
    lines += ['', '## Matching-condition class counts', '']
    for key in sorted(counts(mat_rows, 'matching_condition_class')):
        lines.append(f"- `{key}`: `{counts(mat_rows, 'matching_condition_class')[key]}`")
    lines += ['', '## Route handles', '', '| Route | Regularization rows | RG-flow rows | Matching rows |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('regularization_scheme_ids', []))}` | `{len(row.get('renormalization_flow_ids', []))}` | `{len(row.get('matching_condition_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Regularization-scheme rows, renormalization-flow rows, and matching-condition rows make regulator-independent, scheme-independent, RG-invariant, fixed-point, running-coupling, universal, naturalness, counterterm, threshold-matched, EFT-matched, and scale-bridged language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, evidence-credit, contrast/update, measurement/systematics, validity/transport, causal, selection, capacity, semantic, social-authority, computational, formal-proof, idealization, boundary/sector, gauge/observable, or residual-cap limits.', '']
    out = root / 'docs/30-program/renormalization-matching-summary.generated.md'
    out.write_text('\n'.join(lines))
    print('wrote docs/30-program/renormalization-matching-summary.generated.md')


def augment_authority_dependency_graph_with_composition_edges(root: Path) -> None:
    """Add composition-law / interface-compatibility / global-consistency edges after matching edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    rows = graph.get('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id():
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key = (source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id': next_edge_id(), 'source_kind': source_kind, 'source_id': source_id, 'dependent_kind': dependent_kind, 'dependent_id': dependent_id, 'dependency_kind': dependency_kind, 'required_for': required_for, 'failure_effect': failure_effect, 'max_credit_transmitted': max_credit})
        existing.add(key)
    for rel in ['COMPOSITION-LAW-LEDGER.json','INTERFACE-COMPATIBILITY-LEDGER.json','GLOBAL-CONSISTENCY-LEDGER.json']:
        if rel not in graph.get('generated_from', []):
            graph.setdefault('generated_from', []).append(rel)
    graph['generation_rule'] = graph.get('generation_rule','') + ' Composition-law / interface-compatibility / global-consistency edges are appended by the rev0280 augmentation pass.'
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid = row.get('route_id','')
        effect = row.get('promotion_ceiling','') or row.get('authority_state','')
        for cid in row.get('composition_law_ids', []):
            add('composition-law', cid, 'route', rid, 'composition-law-condition', 'route composition-law denominator', 'cap modular, factorized, gluing, or compositional support when the composition law fails', effect)
        for iid in row.get('interface_compatibility_ids', []):
            add('interface-compatibility', iid, 'route', rid, 'interface-compatibility-condition', 'route interface-compatibility denominator', 'cap interface-compatible or sector-gluing support when overlap/descent/interface checks fail', effect)
        for gid in row.get('global_consistency_ids', []):
            add('global-consistency', gid, 'route', rid, 'global-consistency-condition', 'route global-consistency denominator', 'cap unification, all-sector, or local-to-global support when global obstruction/integrability checks fail', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'open-question' if str(target_id).startswith('OQ-') else 'claim'
        effect = binding.get('maximum_authority_effect','') or 'bounded by binding row'
        for cid in binding.get('composition_law_ids', []):
            add('composition-law', cid, target_kind, target_id, 'composition-law-claim-condition', f'claim composition-law denominator under {binding.get("binding_id")}', 'freeze modular/compositional/gluing wording until composition rows are restored', effect)
        for iid in binding.get('interface_compatibility_ids', []):
            add('interface-compatibility', iid, target_kind, target_id, 'interface-compatibility-claim-condition', f'claim interface-compatibility denominator under {binding.get("binding_id")}', 'freeze interface-compatible or sector-gluing wording until interface rows are restored', effect)
        for gid in binding.get('global_consistency_ids', []):
            add('global-consistency', gid, target_kind, target_id, 'global-consistency-claim-condition', f'claim global-consistency denominator under {binding.get("binding_id")}', 'freeze unification/all-sector/local-to-global wording until global-consistency rows are restored', effect)
    optional = [
        ('evidence-unit','evidence_unit_id','EVIDENCE-UNIT-LEDGER.json','evidence_units'),
        ('credit-allocation','credit_id','CREDIT-ALLOCATION-LEDGER.json','credit_rows'),
        ('empirical-delta','delta_id','EMPIRICAL-DELTA-LEDGER.json','empirical_deltas'),
        ('forecast','forecast_id','DISCRIMINATOR-FORECAST-LEDGER.json','forecast_rows'),
        ('decision-experiment','experiment_id','DECISION-EXPERIMENT-LEDGER.json','decision_experiments'),
        ('severity-test','severity_id','EVIDENCE-SEVERITY-LEDGER.json','severity_rows'),
        ('contrast-class','contrast_id','CONTRAST-CLASS-LEDGER.json','contrast_rows'),
        ('likelihood-update','update_id','LIKELIHOOD-UPDATE-LEDGER.json','update_rows'),
        ('prior-sensitivity','prior_id','PRIOR-SENSITIVITY-LEDGER.json','prior_rows'),
        ('measurement-model','measurement_model_id','MEASUREMENT-MODEL-LEDGER.json','measurement_model_rows'),
        ('systematic-uncertainty','systematic_id','SYSTEMATIC-UNCERTAINTY-LEDGER.json','systematic_rows'),
        ('calibration-traceability','calibration_id','CALIBRATION-TRACEABILITY-LEDGER.json','calibration_rows'),
        ('validity-domain','domain_id','DOMAIN-OF-VALIDITY-LEDGER.json','domain_rows'),
        ('transportability','transport_id','TRANSPORTABILITY-LEDGER.json','transport_rows'),
        ('extrapolation-fence','fence_id','EXTRAPOLATION-FENCE-LEDGER.json','fence_rows'),
        ('causal-mechanism','mechanism_id','CAUSAL-MECHANISM-LEDGER.json','mechanism_rows'),
        ('intervention-protocol','intervention_id','INTERVENTION-PROTOCOL-LEDGER.json','intervention_rows'),
        ('counterfactual-robustness','counterfactual_id','COUNTERFACTUAL-ROBUSTNESS-LEDGER.json','counterfactual_rows'),
        ('selection-function','selection_id','SELECTION-FUNCTION-LEDGER.json','selection_rows'),
        ('multiplicity-control','multiplicity_id','MULTIPLICITY-CONTROL-LEDGER.json','multiplicity_rows'),
        ('reporting-bias','bias_id','REPORTING-BIAS-LEDGER.json','bias_rows'),
        ('model-capacity','model_capacity_id','MODEL-CAPACITY-LEDGER.json','capacity_rows'),
        ('complexity-penalty','complexity_penalty_id','COMPLEXITY-PENALTY-LEDGER.json','complexity_rows'),
        ('generalization-validation','generalization_id','PREDICTIVE-GENERALIZATION-LEDGER.json','generalization_rows'),
        ('semantic-term','semantic_term_id','SEMANTIC-TERM-LEDGER.json','semantic_rows'),
        ('ontology-commitment','ontology_commitment_id','ONTOLOGY-COMMITMENT-LEDGER.json','commitment_rows'),
        ('claim-language-permission','language_permission_id','CLAIM-LANGUAGE-PERMISSION-LEDGER.json','permission_rows'),
        ('social-authority','social_authority_id','SOCIAL-AUTHORITY-LEDGER.json','social_rows'),
        ('review-replication','review_replication_id','REVIEW-REPLICATION-LEDGER.json','review_rows'),
        ('consensus-elicitation','consensus_elicitation_id','CONSENSUS-ELICITATION-LEDGER.json','consensus_rows'),
        ('computational-reproducibility','computational_reproducibility_id','COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json','reproducibility_rows'),
        ('numerical-stability','numerical_stability_id','NUMERICAL-STABILITY-LEDGER.json','stability_rows'),
        ('software-supply-chain','software_supply_chain_id','SOFTWARE-SUPPLY-CHAIN-LEDGER.json','supply_chain_rows'),
        ('proof-obligation','proof_obligation_id','PROOF-OBLIGATION-LEDGER.json','proof_rows'),
        ('assumption-discharge','assumption_discharge_id','ASSUMPTION-DISCHARGE-LEDGER.json','assumption_rows'),
        ('formalization-coverage','formalization_coverage_id','FORMALIZATION-COVERAGE-LEDGER.json','formalization_rows'),
        ('idealization','idealization_id','IDEALIZATION-LEDGER.json','idealization_rows'),
        ('approximation-error','approximation_error_id','APPROXIMATION-ERROR-LEDGER.json','approximation_rows'),
        ('limit-interchange','limit_interchange_id','LIMIT-INTERCHANGE-LEDGER.json','limit_rows'),
        ('boundary-condition','boundary_condition_id','BOUNDARY-CONDITION-LEDGER.json','boundary_rows'),
        ('initial-data','initial_data_id','INITIAL-DATA-LEDGER.json','initial_data_rows'),
        ('sector-selection','sector_selection_id','SECTOR-SELECTION-LEDGER.json','sector_rows'),
        ('gauge-symmetry','gauge_symmetry_id','GAUGE-SYMMETRY-LEDGER.json','gauge_rows'),
        ('constraint-closure','constraint_closure_id','CONSTRAINT-CLOSURE-LEDGER.json','constraint_rows'),
        ('observable-quotient','observable_quotient_id','OBSERVABLE-QUOTIENT-LEDGER.json','observable_rows'),
        ('regularization-scheme','regularization_scheme_id','REGULARIZATION-SCHEME-LEDGER.json','regularization_rows'),
        ('renormalization-flow','renormalization_flow_id','RENORMALIZATION-FLOW-LEDGER.json','flow_rows'),
        ('matching-condition','matching_condition_id','MATCHING-CONDITION-LEDGER.json','matching_rows'),
    ]
    for dep_kind, id_key, file_name, rows_key in optional:
        path = root / file_name
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for item in data.get(rows_key, []):
            item_id = item.get(id_key,'')
            effect = item.get('maximum_authority_effect') or item.get('maximum_credit') or item.get('current_maximum_credit') or item.get('route_state_effect') or 'bounded by owning row'
            for cid in item.get('composition_law_ids', []):
                add('composition-law', cid, dep_kind, item_id, 'composition-law-condition', f'{dep_kind} composition-law denominator', 'remove local-to-global readings when composition-law control fails', effect)
            for iid in item.get('interface_compatibility_ids', []):
                add('interface-compatibility', iid, dep_kind, item_id, 'interface-compatibility-condition', f'{dep_kind} interface-compatibility denominator', 'remove interface/gluing readings when compatibility control fails', effect)
            for gid in item.get('global_consistency_ids', []):
                add('global-consistency', gid, dep_kind, item_id, 'global-consistency-condition', f'{dep_kind} global-consistency denominator', 'remove unification/all-sector readings when global-consistency control fails', effect)
    graph['edge_rows'] = rows
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json composition/interface/global-consistency edges')


def write_composition_consistency_summary(root: Path) -> None:
    comp = json.loads((root / 'COMPOSITION-LAW-LEDGER.json').read_text())
    iface = json.loads((root / 'INTERFACE-COMPATIBILITY-LEDGER.json').read_text())
    glob = json.loads((root / 'GLOBAL-CONSISTENCY-LEDGER.json').read_text())
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    comp_rows = comp.get('composition_rows', [])
    iface_rows = iface.get('interface_rows', [])
    global_rows = glob.get('global_rows', [])
    route_rows = route_ledger.get('route_rows', [])
    def counts(rows, key):
        out = {}
        for row in rows:
            out[row.get(key,'<missing>')] = out.get(row.get(key,'<missing>'), 0) + 1
        return out
    lines = ['# Composition / interface / global-consistency summary (generated)', '', 'Generated by `tools/sync_generated_surfaces.py`. Do not edit by hand.', '', f"- Revision: `{comp.get('revision','<missing>')}`", f"- Composition-law rows: `{len(comp_rows)}`", f"- Interface-compatibility rows: `{len(iface_rows)}`", f"- Global-consistency rows: `{len(global_rows)}`", '', '## Composition-law class counts', '']
    for key in sorted(counts(comp_rows, 'composition_law_class')):
        lines.append(f"- `{key}`: `{counts(comp_rows, 'composition_law_class')[key]}`")
    lines += ['', '## Interface-compatibility class counts', '']
    for key in sorted(counts(iface_rows, 'interface_compatibility_class')):
        lines.append(f"- `{key}`: `{counts(iface_rows, 'interface_compatibility_class')[key]}`")
    lines += ['', '## Global-consistency class counts', '']
    for key in sorted(counts(global_rows, 'global_consistency_class')):
        lines.append(f"- `{key}`: `{counts(global_rows, 'global_consistency_class')[key]}`")
    lines += ['', '## Route handles', '', '| Route | Composition rows | Interface rows | Global rows |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('composition_law_ids', []))}` | `{len(row.get('interface_compatibility_ids', []))}` | `{len(row.get('global_consistency_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Composition-law rows, interface-compatibility rows, and global-consistency rows make modular, compositional, gluing, factorized, interface-compatible, local-to-global, all-sector, unified, and globally consistent language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, evidence-credit, observed-sector, gauge/observable, regularization/matching, or residual-cap limits.', '']
    (root / 'docs/30-program/composition-consistency-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/composition-consistency-summary.generated.md')


def augment_authority_dependency_graph_with_viability_edges(root: Path) -> None:
    """Add unitarity-check / causality-cone / stability-positivity edges after composition edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    rows = graph.get('edge_rows', [])
    graph['generation_rule'] = graph.get('generation_rule','') + ' Unitarity-check / causality-cone / stability-positivity edges are appended by the rev0281 viability augmentation pass.'
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id():
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_ledger=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid=row.get('route_id','')
        effect=row.get('promotion_ceiling') or row.get('authority_state') or 'bounded by route'
        for uid in row.get('unitarity_check_ids', []):
            add('unitarity-check', uid, 'route', rid, 'unitarity-check-condition', 'route unitarity/probability denominator', 'cap physical-viability or unitarity language when probability, norm, S-matrix, or reflection/spectral positivity fails', effect)
        for cid in row.get('causality_cone_ids', []):
            add('causality-cone', cid, 'route', rid, 'causality-cone-condition', 'route causal/analyticity denominator', 'cap causal, local, analytic, retarded, or hyperbolic language when cone/order/analyticity control fails', effect)
        for sid in row.get('stability_positivity_ids', []):
            add('stability-positivity', sid, 'route', rid, 'stability-positivity-condition', 'route stability/positivity denominator', 'cap healthy-degree-of-freedom, positive-energy, ghost-free, tachyon-free, or stable-vacuum language when stability fails', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id=binding.get('claim_or_oq_id','')
        target_kind='open-question' if target_id.startswith('OQ-') else 'claim'
        effect=binding.get('maximum_authority_effect') or 'bounded by binding row'
        for uid in binding.get('unitarity_check_ids', []):
            add('unitarity-check', uid, target_kind, target_id, 'unitarity-check-claim-condition', f'claim unitarity denominator under {binding.get("binding_id")}', 'freeze unitarity/probability/viability wording until unitarity rows are restored', effect)
        for cid in binding.get('causality_cone_ids', []):
            add('causality-cone', cid, target_kind, target_id, 'causality-cone-claim-condition', f'claim causality denominator under {binding.get("binding_id")}', 'freeze causality/analyticity/locality wording until causality rows are restored', effect)
        for sid in binding.get('stability_positivity_ids', []):
            add('stability-positivity', sid, target_kind, target_id, 'stability-positivity-claim-condition', f'claim stability denominator under {binding.get("binding_id")}', 'freeze stability/positivity/healthy-degree-of-freedom wording until stability rows are restored', effect)
    optional=[
        ('evidence-unit','evidence_unit_id','EVIDENCE-UNIT-LEDGER.json','evidence_units'),
        ('credit-allocation','credit_id','CREDIT-ALLOCATION-LEDGER.json','credit_rows'),
        ('empirical-delta','delta_id','EMPIRICAL-DELTA-LEDGER.json','empirical_deltas'),
        ('forecast','forecast_id','DISCRIMINATOR-FORECAST-LEDGER.json','forecast_rows'),
        ('decision-experiment','experiment_id','DECISION-EXPERIMENT-LEDGER.json','decision_experiments'),
        ('severity-test','severity_id','EVIDENCE-SEVERITY-LEDGER.json','severity_rows'),
        ('contrast-class','contrast_id','CONTRAST-CLASS-LEDGER.json','contrast_rows'),
        ('likelihood-update','update_id','LIKELIHOOD-UPDATE-LEDGER.json','update_rows'),
        ('prior-sensitivity','prior_id','PRIOR-SENSITIVITY-LEDGER.json','prior_rows'),
        ('measurement-model','measurement_model_id','MEASUREMENT-MODEL-LEDGER.json','measurement_model_rows'),
        ('systematic-uncertainty','systematic_id','SYSTEMATIC-UNCERTAINTY-LEDGER.json','systematic_rows'),
        ('calibration-traceability','calibration_id','CALIBRATION-TRACEABILITY-LEDGER.json','calibration_rows'),
        ('validity-domain','domain_id','DOMAIN-OF-VALIDITY-LEDGER.json','domain_rows'),
        ('transportability','transport_id','TRANSPORTABILITY-LEDGER.json','transport_rows'),
        ('extrapolation-fence','fence_id','EXTRAPOLATION-FENCE-LEDGER.json','fence_rows'),
        ('causal-mechanism','mechanism_id','CAUSAL-MECHANISM-LEDGER.json','mechanism_rows'),
        ('intervention-protocol','intervention_id','INTERVENTION-PROTOCOL-LEDGER.json','intervention_rows'),
        ('counterfactual-robustness','counterfactual_id','COUNTERFACTUAL-ROBUSTNESS-LEDGER.json','counterfactual_rows'),
        ('selection-function','selection_id','SELECTION-FUNCTION-LEDGER.json','selection_rows'),
        ('multiplicity-control','multiplicity_id','MULTIPLICITY-CONTROL-LEDGER.json','multiplicity_rows'),
        ('reporting-bias','bias_id','REPORTING-BIAS-LEDGER.json','bias_rows'),
        ('model-capacity','model_capacity_id','MODEL-CAPACITY-LEDGER.json','capacity_rows'),
        ('complexity-penalty','complexity_penalty_id','COMPLEXITY-PENALTY-LEDGER.json','complexity_rows'),
        ('generalization-validation','generalization_id','PREDICTIVE-GENERALIZATION-LEDGER.json','generalization_rows'),
        ('semantic-term','semantic_term_id','SEMANTIC-TERM-LEDGER.json','semantic_rows'),
        ('ontology-commitment','ontology_commitment_id','ONTOLOGY-COMMITMENT-LEDGER.json','commitment_rows'),
        ('claim-language-permission','language_permission_id','CLAIM-LANGUAGE-PERMISSION-LEDGER.json','permission_rows'),
        ('social-authority','social_authority_id','SOCIAL-AUTHORITY-LEDGER.json','social_rows'),
        ('review-replication','review_replication_id','REVIEW-REPLICATION-LEDGER.json','review_rows'),
        ('consensus-elicitation','consensus_elicitation_id','CONSENSUS-ELICITATION-LEDGER.json','consensus_rows'),
        ('computational-reproducibility','computational_reproducibility_id','COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json','reproducibility_rows'),
        ('numerical-stability','numerical_stability_id','NUMERICAL-STABILITY-LEDGER.json','stability_rows'),
        ('software-supply-chain','software_supply_chain_id','SOFTWARE-SUPPLY-CHAIN-LEDGER.json','supply_chain_rows'),
        ('proof-obligation','proof_obligation_id','PROOF-OBLIGATION-LEDGER.json','proof_obligation_rows'),
        ('assumption-discharge','assumption_discharge_id','ASSUMPTION-DISCHARGE-LEDGER.json','assumption_discharge_rows'),
        ('formalization-coverage','formalization_coverage_id','FORMALIZATION-COVERAGE-LEDGER.json','formalization_rows'),
        ('idealization','idealization_id','IDEALIZATION-LEDGER.json','idealization_rows'),
        ('approximation-error','approximation_error_id','APPROXIMATION-ERROR-LEDGER.json','approximation_rows'),
        ('limit-interchange','limit_interchange_id','LIMIT-INTERCHANGE-LEDGER.json','limit_rows'),
        ('boundary-condition','boundary_condition_id','BOUNDARY-CONDITION-LEDGER.json','boundary_rows'),
        ('initial-data','initial_data_id','INITIAL-DATA-LEDGER.json','initial_data_rows'),
        ('sector-selection','sector_selection_id','SECTOR-SELECTION-LEDGER.json','sector_rows'),
        ('gauge-symmetry','gauge_symmetry_id','GAUGE-SYMMETRY-LEDGER.json','gauge_rows'),
        ('constraint-closure','constraint_closure_id','CONSTRAINT-CLOSURE-LEDGER.json','constraint_rows'),
        ('observable-quotient','observable_quotient_id','OBSERVABLE-QUOTIENT-LEDGER.json','observable_rows'),
        ('regularization-scheme','regularization_scheme_id','REGULARIZATION-SCHEME-LEDGER.json','regularization_rows'),
        ('renormalization-flow','renormalization_flow_id','RENORMALIZATION-FLOW-LEDGER.json','flow_rows'),
        ('matching-condition','matching_condition_id','MATCHING-CONDITION-LEDGER.json','matching_rows'),
        ('composition-law','composition_law_id','COMPOSITION-LAW-LEDGER.json','composition_rows'),
        ('interface-compatibility','interface_compatibility_id','INTERFACE-COMPATIBILITY-LEDGER.json','interface_rows'),
        ('global-consistency','global_consistency_id','GLOBAL-CONSISTENCY-LEDGER.json','global_rows'),
    ]
    for dep_kind, id_key, file_name, rows_key in optional:
        path=root/file_name
        if not path.exists():
            continue
        data=json.loads(path.read_text())
        for item in data.get(rows_key, []):
            item_id=item.get(id_key,'')
            effect=item.get('maximum_authority_effect') or item.get('maximum_credit') or item.get('current_maximum_credit') or item.get('route_state_effect') or 'bounded by owning row'
            for uid in item.get('unitarity_check_ids', []):
                add('unitarity-check', uid, dep_kind, item_id, 'unitarity-check-condition', f'{dep_kind} unitarity/probability denominator', 'remove physical-viability or unitarity readings when unitarity control fails', effect)
            for cid in item.get('causality_cone_ids', []):
                add('causality-cone', cid, dep_kind, item_id, 'causality-cone-condition', f'{dep_kind} causality/analyticity denominator', 'remove causal/local/analytic readings when causality control fails', effect)
            for sid in item.get('stability_positivity_ids', []):
                add('stability-positivity', sid, dep_kind, item_id, 'stability-positivity-condition', f'{dep_kind} stability/positivity denominator', 'remove healthy/stable/positive-energy readings when stability control fails', effect)
    graph['edge_rows']=rows
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json unitarity/causality/stability edges')


def write_unitarity_causality_stability_summary(root: Path) -> None:
    unit=json.loads((root/'UNITARITY-CHECK-LEDGER.json').read_text())
    caus=json.loads((root/'CAUSALITY-CONE-LEDGER.json').read_text())
    stab=json.loads((root/'STABILITY-POSITIVITY-LEDGER.json').read_text())
    route_ledger=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    unit_rows=unit.get('unitarity_rows', [])
    caus_rows=caus.get('causality_rows', [])
    stab_rows=stab.get('stability_rows', [])
    route_rows=route_ledger.get('route_rows', [])
    def counts(rows, key):
        out={}
        for r in rows:
            out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Unitarity / causality / stability summary (generated)', '', 'Generated by `tools/sync_generated_surfaces.py`. Do not edit by hand.', '', f"- Revision: `{unit.get('revision','<missing>')}`", f"- Unitarity-check rows: `{len(unit_rows)}`", f"- Causality-cone rows: `{len(caus_rows)}`", f"- Stability/positivity rows: `{len(stab_rows)}`", '', '## Unitarity-check class counts', '']
    for key,val in sorted(counts(unit_rows,'unitarity_check_class').items()):
        lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## Causality-cone class counts', '']
    for key,val in sorted(counts(caus_rows,'causality_cone_class').items()):
        lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## Stability/positivity class counts', '']
    for key,val in sorted(counts(stab_rows,'stability_positivity_class').items()):
        lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## Route handles', '', '| Route | Unitarity rows | Causality rows | Stability rows |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('unitarity_check_ids', []))}` | `{len(row.get('causality_cone_ids', []))}` | `{len(row.get('stability_positivity_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Unitarity-check, causality-cone, and stability/positivity rows make physical-viability, probability-conservation, microcausal, analytic, positive-energy, ghost-free, tachyon-free, and healthy-degree-of-freedom language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, evidence-credit, observed-sector, gauge/observable, regularization/matching, composition/global-consistency, or residual-cap limits.', '']
    (root/'docs/30-program/unitarity-causality-stability-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/unitarity-causality-stability-summary.generated.md')



def augment_authority_dependency_graph_with_quantization_correspondence_edges(root: Path) -> None:
    """Add quantization-map / classical-limit / semiclassical-correspondence edges after viability edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    rows = graph.get('edge_rows', [])
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())

    def add(source_kind: str, source_id: str, dependent_kind: str, dependent_id: str,
            dependency_kind: str, required_for: str, failure_effect: str,
            max_credit_transmitted: str) -> None:
        if not source_id or not dependent_id:
            return
        rows.append({
            'edge_id': f'AD-{len(rows) + 1:04d}',
            'source_kind': source_kind,
            'source_id': source_id,
            'dependent_kind': dependent_kind,
            'dependent_id': dependent_id,
            'dependency_kind': dependency_kind,
            'required_for': required_for,
            'failure_effect': failure_effect,
            'max_credit_transmitted': max_credit_transmitted,
        })

    for row in route_ledger.get('route_rows', []):
        rid = row.get('route_id', '')
        effect = row.get('promotion_ceiling') or row.get('authority_state') or 'bounded by route row'
        for qid in row.get('quantization_map_ids', []):
            add('quantization-map', qid, 'route', rid, 'quantization-map-condition', 'route quantization-map denominator', 'cap quantized-gravity, quantum-completion, or candidate-native quantum language when the quantization map fails', effect)
        for cid in row.get('classical_limit_ids', []):
            add('classical-limit', cid, 'route', rid, 'classical-limit-condition', 'route classical-limit denominator', 'cap classical-recovery, observed-sector, or finite-target language when the classical limit fails', effect)
        for sid in row.get('semiclassical_correspondence_ids', []):
            add('semiclassical-correspondence', sid, 'route', rid, 'semiclassical-correspondence-condition', 'route semiclassical-correspondence denominator', 'cap WKB, decoherence, backreaction, clock-recovery, or quantum-classical bridge language when correspondence fails', effect)

    for binding in binding_ledger.get('binding_rows', []):
        target_id = binding.get('claim_or_oq_id', '')
        target_kind = 'open-question' if target_id.startswith('OQ-') else 'claim'
        effect = binding.get('maximum_authority_effect') or 'bounded by claim-route binding'
        for qid in binding.get('quantization_map_ids', []):
            add('quantization-map', qid, target_kind, target_id, 'quantization-map-claim-condition', f'claim quantization-map denominator under {binding.get("binding_id")}', 'freeze quantization / quantum-completion wording until quantization rows are repaired', effect)
        for cid in binding.get('classical_limit_ids', []):
            add('classical-limit', cid, target_kind, target_id, 'classical-limit-claim-condition', f'claim classical-limit denominator under {binding.get("binding_id")}', 'freeze classical-limit / classical-recovery wording until classical-limit rows are repaired', effect)
        for sid in binding.get('semiclassical_correspondence_ids', []):
            add('semiclassical-correspondence', sid, target_kind, target_id, 'semiclassical-correspondence-claim-condition', f'claim semiclassical-correspondence denominator under {binding.get("binding_id")}', 'freeze WKB / decoherence / clock-recovery / semiclassical bridge wording until correspondence rows are repaired', effect)

    graph['edge_rows'] = rows
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json quantization/classical-limit/semiclassical-correspondence edges')


def write_quantization_correspondence_summary(root: Path) -> None:
    qmap = json.loads((root / 'QUANTIZATION-MAP-LEDGER.json').read_text())
    clim = json.loads((root / 'CLASSICAL-LIMIT-LEDGER.json').read_text())
    scor = json.loads((root / 'SEMICLASSICAL-CORRESPONDENCE-LEDGER.json').read_text())
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    qrows = qmap.get('quantization_rows', [])
    crows = clim.get('classical_limit_rows', [])
    srows = scor.get('semiclassical_rows', [])
    route_rows = route_ledger.get('route_rows', [])

    def counts(rows, key):
        out = {}
        for r in rows:
            out[r.get(key, '<missing>')] = out.get(r.get(key, '<missing>'), 0) + 1
        return out

    lines = [
        '# Quantization / classical-limit / semiclassical-correspondence summary (generated)',
        '',
        'Generated by `tools/sync_generated_surfaces.py`. Do not edit by hand.',
        '',
        f"- Revision: `{qmap.get('revision','<missing>')}`",
        f"- Quantization-map rows: `{len(qrows)}`",
        f"- Classical-limit rows: `{len(crows)}`",
        f"- Semiclassical-correspondence rows: `{len(srows)}`",
        '',
        '## Quantization-map class counts',
        '',
    ]
    for key, val in sorted(counts(qrows, 'quantization_map_class').items()):
        lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## Classical-limit class counts', '']
    for key, val in sorted(counts(crows, 'classical_limit_class').items()):
        lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## Semiclassical-correspondence class counts', '']
    for key, val in sorted(counts(srows, 'semiclassical_correspondence_class').items()):
        lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## Route handles', '', '| Route | Quantization-map rows | Classical-limit rows | Semiclassical rows |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('quantization_map_ids', []))}` | `{len(row.get('classical_limit_ids', []))}` | `{len(row.get('semiclassical_correspondence_ids', []))}` |")
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'Quantization-map, classical-limit, and semiclassical-correspondence rows make quantum-completion, quantized-gravity, WKB, decoherence, backreaction, clock-recovery, classical-recovery, and quantum-classical bridge language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, observed-sector, gauge/observable, matching, composition/global-consistency, viability, or residual-cap limits.',
        '',
    ]
    (root / 'docs/30-program/quantization-correspondence-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/quantization-correspondence-summary.generated.md')



def augment_authority_dependency_graph_with_information_entropy_edges(root: Path) -> None:
    """Add information-flow / entropy-accounting / no-go-compliance edges after quantization/correspondence edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['generation_rule'] = graph.get('generation_rule','') + ' Information-flow / entropy-accounting / no-go-compliance edges are appended by the rev0283 information-theory augmentation pass.'
    rows = graph.get('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id():
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_ledger=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid=row.get('route_id','')
        effect=row.get('promotion_ceiling','') or row.get('authority_state','')
        for iid in row.get('information_flow_ids', []):
            add('information-flow', iid, 'route', rid, 'information-flow-condition', 'route information-flow denominator', 'cap information-preservation/recovery language when information channel, leakage, duplication, or recovery residual fails', effect)
        for eid in row.get('entropy_accounting_ids', []):
            add('entropy-accounting', eid, 'route', rid, 'entropy-accounting-condition', 'route entropy-accounting denominator', 'cap entropy, generalized-entropy, mutual-information, Page-curve, or entropy-cone language when accounting fails', effect)
        for nid in row.get('no_go_compliance_ids', []):
            add('no-go-compliance', nid, 'route', rid, 'no-go-compliance-condition', 'route no-go theorem denominator', 'freeze no-cloning, no-signalling, data-processing, and recovery-map language when compliance fails', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id=binding.get('claim_or_oq_id','')
        target_kind='open-question' if target_id.startswith('OQ-') else 'claim'
        effect=binding.get('maximum_authority_effect','') or 'bounded by binding row'
        for iid in binding.get('information_flow_ids', []):
            add('information-flow', iid, target_kind, target_id, 'information-flow-claim-condition', f'claim information-flow denominator under {binding.get("binding_id")}', 'freeze information-flow claim wording until row is restored', effect)
        for eid in binding.get('entropy_accounting_ids', []):
            add('entropy-accounting', eid, target_kind, target_id, 'entropy-accounting-claim-condition', f'claim entropy-accounting denominator under {binding.get("binding_id")}', 'freeze entropy-accounting claim wording until row is restored', effect)
        for nid in binding.get('no_go_compliance_ids', []):
            add('no-go-compliance', nid, target_kind, target_id, 'no-go-compliance-claim-condition', f'claim no-go-compliance denominator under {binding.get("binding_id")}', 'freeze no-go, no-cloning, no-signalling, data-processing, and recovery wording until row is restored', effect)
    graph['edge_rows']=rows
    graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json information/entropy/no-go edges')


def write_information_entropy_summary(root: Path) -> None:
    info=json.loads((root/'INFORMATION-FLOW-LEDGER.json').read_text())
    ent=json.loads((root/'ENTROPY-ACCOUNTING-LEDGER.json').read_text())
    ngc=json.loads((root/'NO-GO-COMPLIANCE-LEDGER.json').read_text())
    route_ledger=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    info_rows=info.get('information_rows', [])
    ent_rows=ent.get('entropy_rows', [])
    ngc_rows=ngc.get('no_go_rows', [])
    route_rows=route_ledger.get('route_rows', [])
    def counts(rows,key):
        out={}
        for r in rows:
            out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Information / entropy / no-go summary (generated)', '', 'Generated by `tools/sync_generated_surfaces.py`. Do not edit by hand.', '', f"- Revision: `{info.get('revision','<missing>')}`", f"- Information-flow rows: `{len(info_rows)}`", f"- Entropy-accounting rows: `{len(ent_rows)}`", f"- No-go-compliance rows: `{len(ngc_rows)}`", '', '## Information-flow class counts', '']
    for key,val in sorted(counts(info_rows,'information_flow_class').items()):
        lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## Entropy-accounting class counts', '']
    for key,val in sorted(counts(ent_rows,'entropy_accounting_class').items()):
        lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## No-go-compliance class counts', '']
    for key,val in sorted(counts(ngc_rows,'no_go_compliance_class').items()):
        lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## Route handles', '', '| Route | Information rows | Entropy rows | No-go rows |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('information_flow_ids', []))}` | `{len(row.get('entropy_accounting_ids', []))}` | `{len(row.get('no_go_compliance_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Information-flow, entropy-accounting, and no-go-compliance rows make information-preservation, information-recovery, entropy, generalized-entropy, Page-curve, no-cloning, no-signalling, data-processing, and recovery-map language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, observed-sector, viability, quantization, or residual-cap limits.', '']
    (root/'docs/30-program/information-entropy-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/information-entropy-summary.generated.md')


def augment_authority_dependency_graph_with_symmetry_anomaly_edges(root: Path) -> None:
    """Add symmetry-realization / anomaly-matching / conservation-law edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['generation_rule'] = graph.get('generation_rule','') + ' Symmetry / anomaly / conservation edges are appended by the rev0284 augmentation pass.'
    rows = graph.get('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id():
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_ledger=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid=row.get('route_id','')
        effect=row.get('promotion_ceiling','') or row.get('authority_state','')
        for sid in row.get('symmetry_realization_ids', []):
            add('symmetry-realization', sid, 'route', rid, 'symmetry-realization-condition', 'route symmetry denominator', 'cap exact/global/generalized symmetry and duality-symmetry language when symmetry realization fails', effect)
        for aid in row.get('anomaly_matching_ids', []):
            add('anomaly-matching', aid, 'route', rid, 'anomaly-matching-condition', 'route anomaly denominator', 'freeze anomaly-free, anomaly-matched, inflow, and no-global-symmetry wording when anomaly control fails', effect)
        for cid in row.get('conservation_law_ids', []):
            add('conservation-law', cid, 'route', rid, 'conservation-law-condition', 'route conservation-law denominator', 'cap Ward-identity, conserved-current, charge-conservation, and flux-balance language when conservation budget fails', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id=binding.get('claim_or_oq_id','')
        target_kind='open-question' if target_id.startswith('OQ-') else 'claim'
        effect=binding.get('maximum_authority_effect','') or 'bounded by binding row'
        for sid in binding.get('symmetry_realization_ids', []):
            add('symmetry-realization', sid, target_kind, target_id, 'symmetry-realization-claim-condition', f'claim symmetry denominator under {binding.get("binding_id")}', 'freeze symmetry claim wording until row is restored', effect)
        for aid in binding.get('anomaly_matching_ids', []):
            add('anomaly-matching', aid, target_kind, target_id, 'anomaly-matching-claim-condition', f'claim anomaly denominator under {binding.get("binding_id")}', 'freeze anomaly/no-global-symmetry claim wording until row is restored', effect)
        for cid in binding.get('conservation_law_ids', []):
            add('conservation-law', cid, target_kind, target_id, 'conservation-law-claim-condition', f'claim conservation denominator under {binding.get("binding_id")}', 'freeze conservation/Ward claim wording until row is restored', effect)
    graph['edge_rows']=rows
    graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json symmetry/anomaly/conservation edges')


def write_symmetry_anomaly_summary(root: Path) -> None:
    sym=json.loads((root/'SYMMETRY-REALIZATION-LEDGER.json').read_text())
    anm=json.loads((root/'ANOMALY-MATCHING-LEDGER.json').read_text())
    con=json.loads((root/'CONSERVATION-LAW-LEDGER.json').read_text())
    route_ledger=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    sym_rows=sym.get('symmetry_rows', [])
    anm_rows=anm.get('anomaly_rows', [])
    con_rows=con.get('conservation_rows', [])
    def counts(rows,key):
        out={}
        for r in rows:
            out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Symmetry / anomaly / conservation summary (generated)', '', 'Generated by `tools/sync_generated_surfaces.py`. Do not edit by hand.', '', f"- Revision: `{sym.get('revision','<missing>')}`", f"- Symmetry-realization rows: `{len(sym_rows)}`", f"- Anomaly-matching rows: `{len(anm_rows)}`", f"- Conservation-law rows: `{len(con_rows)}`", '', '## Symmetry-realization class counts', '']
    for key,val in sorted(counts(sym_rows,'symmetry_realization_class').items()): lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## Anomaly-matching class counts', '']
    for key,val in sorted(counts(anm_rows,'anomaly_matching_class').items()): lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## Conservation-law class counts', '']
    for key,val in sorted(counts(con_rows,'conservation_law_class').items()): lines.append(f"- `{key}`: `{val}`")
    lines += ['', '## Route handles', '', '| Route | Symmetry rows | Anomaly rows | Conservation rows |', '|---|---:|---:|---:|']
    for row in route_ledger.get('route_rows', []):
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('symmetry_realization_ids', []))}` | `{len(row.get('anomaly_matching_ids', []))}` | `{len(row.get('conservation_law_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Symmetry, anomaly, and conservation rows make exact/global/generalized symmetry, no-global-symmetry, anomaly-free, anomaly-matched, Ward-identity, conserved-current, charge-conservation, and symmetry-protected language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, observed-sector, viability, quantization, information, or residual-cap limits.', '']
    (root/'docs/30-program/symmetry-anomaly-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/symmetry-anomaly-summary.generated.md')


def augment_authority_dependency_graph_with_subsystem_algebra_edges(root: Path) -> None:
    """Add algebraic-locality / subsystem-factorization / edge-mode-center edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Algebraic-locality / subsystem-factorization / edge-mode-center edges are appended by the rev0286 subsystem-algebra augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows = json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings = json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','') or row.get('authority_state','')
        for aid in row.get('algebraic_locality_ids', []):
            add('algebraic-locality', aid, 'route', rid, 'algebraic-locality-condition', 'route algebraic-locality denominator', 'cap local-algebra, observer-algebra, type-II/type-III, and candidate-native observable wording when algebraic locality fails', effect)
        for fid in row.get('subsystem_factorization_ids', []):
            add('subsystem-factorization', fid, 'route', rid, 'subsystem-factorization-condition', 'route subsystem-factorization denominator', 'freeze tensor-factor, split-property, independent-subsystem, detector/source split, and local-entropy wording when factorization fails', effect)
        for eid in row.get('edge_mode_center_ids', []):
            add('edge-mode-center', eid, 'route', rid, 'edge-mode-center-condition', 'route edge-mode/center denominator', 'cap edge-mode, center-choice, soft-charge, threshold, binning, entropy-readout, and observer-energy wording when edge/center control fails', effect)
    for binding in bindings:
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'claim' if target_id.startswith('CL-') else 'open-question'
        effect = binding.get('maximum_authority_effect','') or 'bounded by binding row'
        for aid in binding.get('algebraic_locality_ids', []):
            add('algebraic-locality', aid, target_kind, target_id, 'algebraic-locality-claim-condition', f'claim algebraic-locality denominator under {binding.get("binding_id")}', 'freeze local-algebra or observer-algebra claim wording until algebraic-locality row is restored', effect)
        for fid in binding.get('subsystem_factorization_ids', []):
            add('subsystem-factorization', fid, target_kind, target_id, 'subsystem-factorization-claim-condition', f'claim subsystem-factorization denominator under {binding.get("binding_id")}', 'freeze tensor-factor, split-property, or independent-subsystem claim wording until factorization row is restored', effect)
        for eid in binding.get('edge_mode_center_ids', []):
            add('edge-mode-center', eid, target_kind, target_id, 'edge-mode-center-claim-condition', f'claim edge-mode/center denominator under {binding.get("binding_id")}', 'freeze edge-mode, center-choice, threshold, binning, and entropy-readout claim wording until edge/center row is restored', effect)
    graph['edge_count'] = len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json subsystem/algebra/edge-center edges')


def write_subsystem_algebra_summary(root: Path) -> None:
    alg=json.loads((root/'ALGEBRAIC-LOCALITY-LEDGER.json').read_text())
    fac=json.loads((root/'SUBSYSTEM-FACTORIZATION-LEDGER.json').read_text())
    edg=json.loads((root/'EDGE-MODE-CENTER-LEDGER.json').read_text())
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    alg_rows=alg.get('algebraic_rows', []); fac_rows=fac.get('factorization_rows', []); edg_rows=edg.get('edge_mode_rows', [])
    def counts(rows, key):
        out={}
        for row in rows:
            val=row.get(key,'<missing>')
            out[val]=out.get(val,0)+1
        return out
    lines=['# Subsystem algebra / factorization / edge-mode-center summary (generated)', '', 'Generated from `ALGEBRAIC-LOCALITY-LEDGER.json`, `SUBSYSTEM-FACTORIZATION-LEDGER.json`, and `EDGE-MODE-CENTER-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{alg.get('revision','<missing>')}`", f"- Algebraic-locality rows: `{len(alg_rows)}`", f"- Subsystem-factorization rows: `{len(fac_rows)}`", f"- Edge-mode/center rows: `{len(edg_rows)}`", f"- Route rows: `{len(route_rows)}`", f"- S4/S5 routes: `{sum(1 for r in route_rows if r.get('authority_state') in ['S4','S5'])}`", '', '## Algebraic-locality class counts', '']
    for k,v in sorted(counts(alg_rows,'algebraic_locality_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Subsystem-factorization class counts', '']
    for k,v in sorted(counts(fac_rows,'subsystem_factorization_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Edge-mode/center class counts', '']
    for k,v in sorted(counts(edg_rows,'edge_mode_center_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Route handle counts', '', '| Route | Algebraic locality | Factorization | Edge/center |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('algebraic_locality_ids', []))}` | `{len(row.get('subsystem_factorization_ids', []))}` | `{len(row.get('edge_mode_center_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Algebraic-locality, subsystem-factorization, and edge-mode/center rows make local-algebra, observer-algebra, tensor-factor, split-property, local-entropy, type-II/type-III, center-choice, and edge-mode language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, observed-sector, gauge, topology, quantization, information, symmetry, viability, or residual-cap limits.', '']
    (root/'docs/30-program/subsystem-algebra-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/subsystem-algebra-summary.generated.md')


def write_ledger_family_surface_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    rows=registry.get('registry_rows', [])
    missing=[]
    def expected_schema(rel: str) -> str:
        return 'schemas/' + rel.lower().replace('_','-').replace('.json','.schema.json')
    lines=['# Ledger-family surface/schema audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json`. Do not edit directly; run `make index` after changing registered ledger families.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(rows)}`", '', '| Family | Ledgers present | Schemas present | Summary present | Route fields | Policy |', '|---|---:|---:|---:|---:|---|']
    for fam in rows:
        ledgers=fam.get('ledger_files', [])
        ledger_present=sum(1 for rel in ledgers if (root/rel).exists())
        schema_present=sum(1 for rel in ledgers if (root/expected_schema(rel)).exists())
        summary=fam.get('generated_summary','')
        summary_present=1 if summary and (root/summary).exists() else 0
        if ledger_present != len(ledgers): missing.append((fam.get('family_id'), 'ledger'))
        if schema_present != len(ledgers): missing.append((fam.get('family_id'), 'schema'))
        if summary and not summary_present: missing.append((fam.get('family_id'), 'summary'))
        lines.append(f"| `{fam.get('family_id')}` | `{ledger_present}/{len(ledgers)}` | `{schema_present}/{len(ledgers)}` | `{summary_present}` | `{len(fam.get('route_fields', []))}` | `{fam.get('cardinality_policy','')}` |")
    lines += ['', f"- Missing surface cells: `{len(missing)}`", '', '## Audit rule', '', 'Every registered route-support family should expose its ledger files, schemas, generated summary, route fields, open-question gate, and cardinality policy in one place. This audit is intentionally shallow but broad: it catches registry drift before a family can lose a schema, generated mirror, or route-field coverage silently.', '']
    if missing:
        lines += ['## Missing cells', '']
        for fid,kind in missing:
            lines.append(f"- `{fid}` missing `{kind}` coverage")
    (root/'docs/30-program/ledger-family-surface-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/ledger-family-surface-audit.generated.md')

def write_route_layer_coverage_audit(root: Path) -> None:
    registry = json.loads((root / 'LEDGER-FAMILY-REGISTRY.json').read_text())
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    route_rows = route_ledger.get('route_rows', [])
    lines = [
        '# Route-layer coverage audit (generated)',
        '',
        'Generated by `tools/sync_generated_surfaces.py`. Do not edit by hand.',
        '',
        f"- Revision: `{registry.get('revision','<missing>')}`",
        f"- Registered layer families: `{len(registry.get('registry_rows', []))}`",
        f"- Route rows audited: `{len(route_rows)}`",
        '',
        '## Family coverage',
        '',
        '| Family | OQ | Policy | Declared max route-field cardinality | Ledgers | Route fields | Empty route-field cells | Observed max route-field cardinality |',
        '|---|---|---|---:|---:|---:|---:|---:|',
    ]
    for fam in registry.get('registry_rows', []):
        fields = fam.get('route_fields', [])
        empty = 0
        max_card = 0
        for row in route_rows:
            for field in fields:
                val = row.get(field, [])
                if not val:
                    empty += 1
                if isinstance(val, list):
                    max_card = max(max_card, len(val))
        lines.append(f"| `{fam.get('family_id')}` | `{fam.get('open_question_id')}` | `{fam.get('cardinality_policy')}` | `{fam.get('maximum_route_field_cardinality','')}` | `{len(fam.get('ledger_files', []))}` | `{len(fields)}` | `{empty}` | `{max_card}` |")
    lines += [
        '',
        '## rev0282–rev0284 refactor note',
        '',
        'The audit exists because route-support layers can accidentally inflate by binding route-local rows to every route. rev0282 fixed composition/interface/global route-row overbinding. rev0283 tightened registry cardinality for mature route-local-plus-wrapper families. rev0284 refactored the route-state summary to read from this registry dynamically, so registered support families are not lost from the compact mirror. rev0286 adds a surface/schema audit so registered ledger families cannot silently lose ledgers, schemas, or summaries.',
        '',
    ]
    (root / 'docs/30-program/route-layer-coverage-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/route-layer-coverage-audit.generated.md')

def sync_start_here(root: Path) -> None:
    state = load_state(root)
    start_here_path = root / 'START_HERE.md'
    rendered = render_generated_restart_mirror_block(state)
    updated = replace_generated_restart_mirror_block(start_here_path.read_text(), rendered)
    start_here_path.write_text(updated)
    print('synced START_HERE.md restart mirror family block')



def augment_authority_dependency_graph_with_topology_dimension_signature_edges(root: Path) -> None:
    """Add spacetime-topology / dimension-realization / signature-structure edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Spacetime-topology / dimension-realization / signature-structure edges are appended by the rev0285 topology/dimension/signature augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows = json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings = json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3')
        for tid in row.get('spacetime_topology_ids', []):
            add('spacetime-topology', tid, 'route', rid, 'spacetime-topology-condition', 'route topology denominator', 'cap topology-independent, topology-change, manifoldlike, compactification, or background-independent language when topology control fails', effect)
        for did in row.get('dimension_realization_ids', []):
            add('dimension-realization', did, 'route', rid, 'dimension-realization-condition', 'route dimension denominator', 'cap dimension, spectral-dimension, dimensional-reduction, critical-dimension, or 3+1-recovery language when dimension control fails', effect)
        for sid in row.get('signature_structure_ids', []):
            add('signature-structure', sid, 'route', rid, 'signature-structure-condition', 'route signature denominator', 'cap Lorentzian, Euclidean, Wick-rotation, complex-contour, causal-order, or signature-independent language when signature control fails', effect)
    for binding in bindings:
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'claim' if target_id.startswith('CL-') else 'open-question'
        effect='S3'
        for tid in binding.get('spacetime_topology_ids', []):
            add('spacetime-topology', tid, target_kind, target_id, 'spacetime-topology-claim-condition', f'claim topology denominator under {binding.get("binding_id")}', 'freeze topology/spacetime-recovery claim wording until topology row is restored', effect)
        for did in binding.get('dimension_realization_ids', []):
            add('dimension-realization', did, target_kind, target_id, 'dimension-realization-claim-condition', f'claim dimension denominator under {binding.get("binding_id")}', 'freeze dimension/dimensional-reduction claim wording until dimension row is restored', effect)
        for sid in binding.get('signature_structure_ids', []):
            add('signature-structure', sid, target_kind, target_id, 'signature-structure-claim-condition', f'claim signature denominator under {binding.get("binding_id")}', 'freeze Lorentzian/Wick-rotation/signature claim wording until signature row is restored', effect)
    graph['edge_count'] = len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json topology/dimension/signature edges')


def write_topology_dimension_signature_summary(root: Path) -> None:
    top=json.loads((root/'SPACETIME-TOPOLOGY-LEDGER.json').read_text())
    dim=json.loads((root/'DIMENSION-REALIZATION-LEDGER.json').read_text())
    sig=json.loads((root/'SIGNATURE-STRUCTURE-LEDGER.json').read_text())
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    top_rows=top.get('topology_rows', []); dim_rows=dim.get('dimension_rows', []); sig_rows=sig.get('signature_rows', [])
    def counts(rows, key):
        out={}
        for row in rows:
            val=row.get(key,'<missing>')
            out[val]=out.get(val,0)+1
        return out
    lines=['# Topology / dimension / signature summary (generated)','', 'Generated from `SPACETIME-TOPOLOGY-LEDGER.json`, `DIMENSION-REALIZATION-LEDGER.json`, and `SIGNATURE-STRUCTURE-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.','', f"- Revision: `{top.get('revision','<missing>')}`", f"- Spacetime-topology rows: `{len(top_rows)}`", f"- Dimension-realization rows: `{len(dim_rows)}`", f"- Signature-structure rows: `{len(sig_rows)}`", f"- Route rows: `{len(route_rows)}`", f"- S4/S5 routes: `{sum(1 for r in route_rows if r.get('authority_state') in ['S4','S5'])}`", '', '## Topology class counts', '']
    for k,v in sorted(counts(top_rows,'topology_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Dimension class counts', '']
    for k,v in sorted(counts(dim_rows,'dimension_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Signature class counts', '']
    for k,v in sorted(counts(sig_rows,'signature_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Route handle counts', '', '| Route | Topology | Dimension | Signature |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('spacetime_topology_ids', []))}` | `{len(row.get('dimension_realization_ids', []))}` | `{len(row.get('signature_structure_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Topology, dimension, and signature rows make topology-independent, topology-change, manifold-recovered, dimensional-reduction, Lorentzian, Euclidean, Wick-rotation, complex-contour, causal-order, and signature-independent language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, observed-sector, viability, quantization, information, symmetry, or residual-cap limits.', '']
    (root/'docs/30-program/topology-dimension-signature-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/topology-dimension-signature-summary.generated.md')


def write_claim_route_binding_field_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    fields=[]
    for fam in registry.get('registry_rows', []):
        for field in fam.get('route_fields', []):
            if field not in fields:
                fields.append(field)
    missing=[]
    for row in bindings:
        for field in fields:
            if field not in row:
                missing.append((row.get('binding_id','<missing>'), field))
    lines=['# Claim-route binding field audit (generated)','', 'Generated from `CLAIM-ROUTE-BINDING-LEDGER.json` plus `LEDGER-FAMILY-REGISTRY.json`. Do not edit directly; run `make index` after changing route-layer families or bindings.','', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- Registered route fields: `{len(fields)}`", f"- Claim-route binding rows: `{len(bindings)}`", f"- Missing binding-field cells: `{len(missing)}`", '', '## Registered fields', '']
    for field in fields:
        lines.append(f"- `{field}`")
    if missing:
        lines += ['', '## Missing cells', '']
        for bid, field in missing[:200]:
            lines.append(f"- `{bid}` missing `{field}`")
    lines += ['', '## Normalization rule', '', 'Every binding row must expose every registered route-layer field. Empty lists are allowed when a binding does not spend that layer, but missing fields are no longer allowed because they hide late-added route-support families from authority propagation review.', '']
    (root/'docs/30-program/claim-route-binding-field-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/claim-route-binding-field-audit.generated.md')



def augment_authority_dependency_graph_with_measure_ensemble_typicality_edges(root: Path) -> None:
    """Add measure-definition / ensemble-sampling / typicality-weighting edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    rows = graph.get('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':f"EDGE-{len(rows)+1:05d}",'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_ledger=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','') or row.get('authority_state','')
        for mid in row.get('measure_definition_ids', []):
            add('measure-definition', mid, 'route', rid, 'measure-definition-condition', 'route measure/probability denominator', 'freeze probability, cutoff, path-integral-measure, landscape-measure, or naturalness wording when measure control fails', effect)
        for eid in row.get('ensemble_sampling_ids', []):
            add('ensemble-sampling', eid, 'route', rid, 'ensemble-sampling-condition', 'route ensemble/sample denominator', 'freeze ensemble-average, sample-member, source-population, or benchmark-distribution wording when ensemble control fails', effect)
        for tid in row.get('typicality_weighting_ids', []):
            add('typicality-weighting', tid, 'route', rid, 'typicality-weighting-condition', 'route typicality/reference-class denominator', 'freeze typicality, observer-weighting, anthropic, naturalness, rare-event, or prediction wording when typicality control fails', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id=binding.get('claim_or_oq_id',''); target_kind='open-question' if target_id.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','') or 'bounded by binding row'
        for mid in binding.get('measure_definition_ids', []):
            add('measure-definition', mid, target_kind, target_id, 'measure-definition-claim-condition', f'claim measure denominator under {binding.get("binding_id")}', 'freeze probability/measure claim wording until measure rows are restored', effect)
        for eid in binding.get('ensemble_sampling_ids', []):
            add('ensemble-sampling', eid, target_kind, target_id, 'ensemble-sampling-claim-condition', f'claim ensemble denominator under {binding.get("binding_id")}', 'freeze ensemble-average or sample-member claim wording until ensemble rows are restored', effect)
        for tid in binding.get('typicality_weighting_ids', []):
            add('typicality-weighting', tid, target_kind, target_id, 'typicality-weighting-claim-condition', f'claim typicality denominator under {binding.get("binding_id")}', 'freeze typicality/anthropic/observer-weighted claim wording until typicality rows are restored', effect)
    graph['edge_rows']=rows
    graph['edge_count']=len(rows)
    graph.setdefault('generated_from', [])
    for rel in ['MEASURE-DEFINITION-LEDGER.json','ENSEMBLE-SAMPLING-LEDGER.json','TYPICALITY-WEIGHTING-LEDGER.json']:
        if rel not in graph['generated_from']:
            graph['generated_from'].append(rel)
    graph['generation_rule']=graph.get('generation_rule','')+' Measure-definition / ensemble-sampling / typicality-weighting edges are appended by the rev0286 measure/ensemble/typicality augmentation pass.'
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json measure/ensemble/typicality edges')


def write_measure_ensemble_typicality_summary(root: Path) -> None:
    mea=json.loads((root/'MEASURE-DEFINITION-LEDGER.json').read_text())
    ens=json.loads((root/'ENSEMBLE-SAMPLING-LEDGER.json').read_text())
    typ=json.loads((root/'TYPICALITY-WEIGHTING-LEDGER.json').read_text())
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    mea_rows=mea.get('measure_rows', []); ens_rows=ens.get('ensemble_rows', []); typ_rows=typ.get('typicality_rows', [])
    def counts(rows, key):
        out={}
        for row in rows:
            val=row.get(key,'<missing>')
            out[val]=out.get(val,0)+1
        return out
    lines=['# Measure / ensemble / typicality summary (generated)','', 'Generated from `MEASURE-DEFINITION-LEDGER.json`, `ENSEMBLE-SAMPLING-LEDGER.json`, and `TYPICALITY-WEIGHTING-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.','', f"- Revision: `{mea.get('revision','<missing>')}`", f"- Measure-definition rows: `{len(mea_rows)}`", f"- Ensemble-sampling rows: `{len(ens_rows)}`", f"- Typicality-weighting rows: `{len(typ_rows)}`", f"- Route rows: `{len(route_rows)}`", f"- S4/S5 routes: `{sum(1 for r in route_rows if r.get('authority_state') in ['S4','S5'])}`", '', '## Measure class counts', '']
    for k,v in sorted(counts(mea_rows,'measure_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Ensemble class counts', '']
    for k,v in sorted(counts(ens_rows,'ensemble_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Typicality class counts', '']
    for k,v in sorted(counts(typ_rows,'typicality_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Route handle counts', '', '| Route | Measure | Ensemble | Typicality |', '|---|---:|---:|---:|']
    for row in route_rows:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('measure_definition_ids', []))}` | `{len(row.get('ensemble_sampling_ids', []))}` | `{len(row.get('typicality_weighting_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Measure, ensemble, and typicality rows make probability, path-integral measure, ensemble average, landscape count, naturalness, anthropic, observer-weighted, reference-class, and prediction language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, observed-sector, viability, quantization, information, symmetry, topology, or residual-cap limits.', '']
    (root/'docs/30-program/measure-ensemble-typicality-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/measure-ensemble-typicality-summary.generated.md')


def write_binding_control_ledger_coverage_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    missing=[]
    checked=0
    for binding in bindings:
        bid=binding.get('binding_id','<missing>')
        owns_oq=binding.get('claim_or_oq_id','')
        for fam in registry.get('registry_rows', []):
            fields=fam.get('route_fields', [])
            spends=any(binding.get(field) for field in fields)
            owns_family=(owns_oq == fam.get('open_question_id'))
            if not (spends or owns_family):
                continue
            checked += 1
            for rel in fam.get('ledger_files', []):
                if rel not in binding.get('controlling_ledgers', []):
                    missing.append((bid, fam.get('family_id','<missing>'), rel))
    lines=['# Binding control-ledger coverage audit (generated)','', 'Generated from `CLAIM-ROUTE-BINDING-LEDGER.json` plus `LEDGER-FAMILY-REGISTRY.json`. Do not edit directly; run `make index` after changing route-layer families or bindings.','', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- Claim-route binding rows: `{len(bindings)}`", f"- Binding/family pairs checked: `{checked}`", f"- Missing controlling-ledger cells: `{len(missing)}`", '', '## Rule', '', 'If a binding row spends any registered route-layer field, or if it owns that layer family OQ, then the binding must list the family ledgers in `controlling_ledgers`. Empty route-layer fields are allowed; hidden controlling-ledger omissions are not.', '']
    if missing:
        lines += ['## Missing cells', '']
        for bid, fam, rel in missing[:300]:
            lines.append(f"- `{bid}` / `{fam}` missing `{rel}`")
    (root/'docs/30-program/binding-control-ledger-coverage-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/binding-control-ledger-coverage-audit.generated.md')



def augment_authority_dependency_graph_with_matter_sector_edges(root: Path) -> None:
    """Add particle-spectrum / coupling / mass-hierarchy edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    rows = graph.get('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id():
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key = (source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id': next_edge_id(), 'source_kind': source_kind, 'source_id': source_id, 'dependent_kind': dependent_kind, 'dependent_id': dependent_id, 'dependency_kind': dependency_kind, 'required_for': required_for, 'failure_effect': failure_effect, 'max_credit_transmitted': max_credit})
        existing.add(key)
    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid = row.get('route_id','')
        effect = row.get('promotion_ceiling') or row.get('authority_state') or 'bounded by route row'
        for pid in row.get('particle_spectrum_ids', []):
            add('particle-spectrum', pid, 'route', rid, 'particle-spectrum-condition', 'route matter-spectrum denominator', 'freeze Standard Model or matter-spectrum wording when spectrum row fails', effect)
        for cid in row.get('interaction_coupling_ids', []):
            add('interaction-coupling', cid, 'route', rid, 'interaction-coupling-condition', 'route interaction/coupling denominator', 'freeze coupling, texture, or unification wording when coupling row fails', effect)
        for mid in row.get('mass_hierarchy_ids', []):
            add('mass-hierarchy', mid, 'route', rid, 'mass-hierarchy-condition', 'route mass/hierarchy denominator', 'freeze Higgs/EWSB, flavor, neutrino, hierarchy, or naturalness wording when mass row fails', effect)
    for binding in binding_ledger.get('binding_rows', []):
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'open-question' if str(target_id).startswith('OQ-') else 'claim'
        effect = binding.get('maximum_authority_effect') or 'bounded by binding row'
        for pid in binding.get('particle_spectrum_ids', []):
            add('particle-spectrum', pid, target_kind, target_id, 'particle-spectrum-claim-condition', f'claim particle-spectrum denominator under {binding.get("binding_id")}', 'freeze matter-spectrum claim wording until spectrum rows are restored', effect)
        for cid in binding.get('interaction_coupling_ids', []):
            add('interaction-coupling', cid, target_kind, target_id, 'interaction-coupling-claim-condition', f'claim interaction/coupling denominator under {binding.get("binding_id")}', 'freeze coupling or unification claim wording until coupling rows are restored', effect)
        for mid in binding.get('mass_hierarchy_ids', []):
            add('mass-hierarchy', mid, target_kind, target_id, 'mass-hierarchy-claim-condition', f'claim mass/hierarchy denominator under {binding.get("binding_id")}', 'freeze mass, Higgs/EWSB, flavor, neutrino, or hierarchy claim wording until mass rows are restored', effect)
    graph['edge_rows'] = rows
    graph['edge_count'] = len(rows)
    write_authority_graph(graph_path, graph)
    print('augmented AUTHORITY-DEPENDENCY-GRAPH.json with matter-sector edges')


def write_matter_sector_summary(root: Path) -> None:
    p = json.loads((root / 'PARTICLE-SPECTRUM-LEDGER.json').read_text())
    c = json.loads((root / 'INTERACTION-COUPLING-LEDGER.json').read_text())
    m = json.loads((root / 'MASS-HIERARCHY-LEDGER.json').read_text())
    routes = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    prow = p.get('particle_spectrum_rows', [])
    crow = c.get('interaction_coupling_rows', [])
    mrow = m.get('mass_hierarchy_rows', [])
    def counts(rows, key):
        out={}
        for r in rows:
            out[r.get(key,'<missing>')] = out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Matter-sector spectrum / coupling / mass-hierarchy summary (generated)', '', 'Generated from `PARTICLE-SPECTRUM-LEDGER.json`, `INTERACTION-COUPLING-LEDGER.json`, and `MASS-HIERARCHY-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{p.get('revision','<missing>')}`", f"- Particle-spectrum rows: `{len(prow)}`", f"- Interaction-coupling rows: `{len(crow)}`", f"- Mass/hierarchy rows: `{len(mrow)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Particle-spectrum class counts', '']
    for k,v in sorted(counts(prow,'spectrum_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Interaction-coupling class counts', '']
    for k,v in sorted(counts(crow,'coupling_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Mass/hierarchy class counts', '']
    for k,v in sorted(counts(mrow,'mass_hierarchy_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Non-promotion rule', '', 'Matter-sector rows are cap/rollback rows. They do not promote a route beyond its state-machine ceiling and they do not substitute for observed-sector recovery, public records, gauge/observable quotients, renormalization/matching, topology/signature, quantization/correspondence, symmetry/anomaly, measure/typicality, or subsystem/factorization controls.', '']
    (root / 'docs/30-program/matter-sector-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/matter-sector-summary.generated.md')



def augment_authority_dependency_graph_with_cosmology_history_edges(root: Path) -> None:
    """Add cosmological-background / vacuum-energy / thermal-history edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Cosmological-background / vacuum-energy / thermal-history edges are appended by the rev0288 cosmology-history augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows = json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings = json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3')
        for cid in row.get('cosmological_background_ids', []):
            add('cosmological-background', cid, 'route', rid, 'cosmological-background-condition', 'route cosmological-background denominator', 'cap Lambda-CDM, expansion-history, background-recovery, or complete-cosmology language when cosmological-background control fails', effect)
        for vid in row.get('vacuum_energy_ids', []):
            add('vacuum-energy', vid, 'route', rid, 'vacuum-energy-condition', 'route vacuum-energy/dark-sector denominator', 'cap cosmological-constant, dark-energy, dark-matter, dark-sector, or naturalness language when vacuum/dark-sector control fails', effect)
        for tid in row.get('thermal_history_ids', []):
            add('thermal-history', tid, 'route', rid, 'thermal-history-condition', 'route thermal-history denominator', 'cap inflation, reheating, BBN, structure-formation, growth-history, or complete-cosmology language when thermal-history control fails', effect)
    for binding in bindings:
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'claim' if target_id.startswith('CL-') else 'open-question'
        effect='S3'
        for cid in binding.get('cosmological_background_ids', []):
            add('cosmological-background', cid, target_kind, target_id, 'cosmological-background-claim-condition', f'claim cosmological-background denominator under {binding.get("binding_id")}', 'freeze cosmological-background claim wording until background row is restored', effect)
        for vid in binding.get('vacuum_energy_ids', []):
            add('vacuum-energy', vid, target_kind, target_id, 'vacuum-energy-claim-condition', f'claim vacuum-energy denominator under {binding.get("binding_id")}', 'freeze vacuum/dark-sector claim wording until vacuum-energy row is restored', effect)
        for tid in binding.get('thermal_history_ids', []):
            add('thermal-history', tid, target_kind, target_id, 'thermal-history-claim-condition', f'claim thermal-history denominator under {binding.get("binding_id")}', 'freeze thermal-history claim wording until thermal-history row is restored', effect)
    graph['edge_count'] = len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json cosmology-history edges')


def write_cosmology_history_summary(root: Path) -> None:
    b = json.loads((root / 'COSMOLOGICAL-BACKGROUND-LEDGER.json').read_text())
    v = json.loads((root / 'VACUUM-ENERGY-LEDGER.json').read_text())
    h = json.loads((root / 'THERMAL-HISTORY-LEDGER.json').read_text())
    routes = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    brows = b.get('background_rows', [])
    vrows = v.get('vacuum_energy_rows', [])
    hrows = h.get('thermal_history_rows', [])
    def counts(rows, key):
        out={}
        for r in rows:
            out[r.get(key,'<missing>')] = out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Cosmological-background / vacuum-energy / thermal-history summary (generated)', '', 'Generated from `COSMOLOGICAL-BACKGROUND-LEDGER.json`, `VACUUM-ENERGY-LEDGER.json`, and `THERMAL-HISTORY-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{b.get('revision','<missing>')}`", f"- Cosmological-background rows: `{len(brows)}`", f"- Vacuum-energy rows: `{len(vrows)}`", f"- Thermal-history rows: `{len(hrows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Cosmological-background class counts', '']
    for k,vv in sorted(counts(brows,'background_class').items()): lines.append(f"- `{k}`: `{vv}`")
    lines += ['', '## Vacuum-energy class counts', '']
    for k,vv in sorted(counts(vrows,'vacuum_class').items()): lines.append(f"- `{k}`: `{vv}`")
    lines += ['', '## Thermal-history class counts', '']
    for k,vv in sorted(counts(hrows,'thermal_history_class').items()): lines.append(f"- `{k}`: `{vv}`")
    lines += ['', '## Non-promotion rule', '', 'Cosmology rows make expansion-history, Lambda/dark-sector, inflation/reheating/BBN, and structure-formation wording auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond observed-sector, matter-sector, topology/signature, quantization, viability, public-record, and residual-cap limits.', '']
    (root / 'docs/30-program/cosmology-history-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/cosmology-history-summary.generated.md')



def augment_authority_dependency_graph_with_black_hole_sector_edges(root: Path) -> None:
    """Add horizon-structure / black-hole-thermodynamics / evaporation-radiation edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Horizon-structure / black-hole-thermodynamics / evaporation-radiation edges are appended by the rev0289 black-hole-sector augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows = json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings = json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3')
        for hid in row.get('horizon_structure_ids', []):
            add('horizon-structure', hid, 'route', rid, 'horizon-structure-condition', 'route horizon-structure denominator', 'cap horizon, causal-boundary, area, surface-gravity, and black-hole-sector wording when horizon control fails', effect)
        for bid in row.get('black_hole_thermodynamics_ids', []):
            add('black-hole-thermodynamics', bid, 'route', rid, 'black-hole-thermodynamics-condition', 'route black-hole thermodynamics denominator', 'cap first-law, area-law, generalized-second-law, entropy, temperature, or microstate wording when thermodynamics control fails', effect)
        for eid in row.get('evaporation_radiation_ids', []):
            add('evaporation-radiation', eid, 'route', rid, 'evaporation-radiation-condition', 'route evaporation/radiation denominator', 'cap Hawking-radiation, greybody, backreaction, endpoint, Page-curve, and information-recovery wording when evaporation/radiation control fails', effect)
    for binding in bindings:
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'claim' if target_id.startswith('CL-') else 'open-question'
        effect='S3'
        for hid in binding.get('horizon_structure_ids', []):
            add('horizon-structure', hid, target_kind, target_id, 'horizon-structure-claim-condition', f'claim horizon-structure denominator under {binding.get("binding_id")}', 'freeze horizon or black-hole-sector claim wording until horizon row is restored', effect)
        for bid in binding.get('black_hole_thermodynamics_ids', []):
            add('black-hole-thermodynamics', bid, target_kind, target_id, 'black-hole-thermodynamics-claim-condition', f'claim black-hole thermodynamics denominator under {binding.get("binding_id")}', 'freeze entropy, microstate, first-law, or thermodynamics claim wording until thermodynamics row is restored', effect)
        for eid in binding.get('evaporation_radiation_ids', []):
            add('evaporation-radiation', eid, target_kind, target_id, 'evaporation-radiation-claim-condition', f'claim evaporation/radiation denominator under {binding.get("binding_id")}', 'freeze Hawking-radiation, evaporation, endpoint, Page-curve, or information-recovery claim wording until evaporation/radiation row is restored', effect)
    graph['edge_count'] = len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json black-hole-sector edges')


def write_black_hole_sector_summary(root: Path) -> None:
    h = json.loads((root / 'HORIZON-STRUCTURE-LEDGER.json').read_text())
    b = json.loads((root / 'BLACK-HOLE-THERMODYNAMICS-LEDGER.json').read_text())
    e = json.loads((root / 'EVAPORATION-RADIATION-LEDGER.json').read_text())
    routes = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    hrows = h.get('horizon_rows', [])
    brows = b.get('thermodynamics_rows', [])
    erows = e.get('evaporation_rows', [])
    def counts(rows, key):
        out={}
        for r in rows:
            out[r.get(key,'<missing>')] = out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Black-hole horizon / thermodynamics / evaporation summary (generated)', '', 'Generated from `HORIZON-STRUCTURE-LEDGER.json`, `BLACK-HOLE-THERMODYNAMICS-LEDGER.json`, and `EVAPORATION-RADIATION-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{h.get('revision','<missing>')}`", f"- Horizon-structure rows: `{len(hrows)}`", f"- Black-hole thermodynamics rows: `{len(brows)}`", f"- Evaporation/radiation rows: `{len(erows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Horizon class counts', '']
    for k,v in sorted(counts(hrows,'horizon_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Thermodynamics class counts', '']
    for k,v in sorted(counts(brows,'thermodynamics_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Evaporation/radiation class counts', '']
    for k,v in sorted(counts(erows,'evaporation_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Route handle counts', '', '| Route | Horizon | Thermodynamics | Evaporation |', '|---|---:|---:|---:|']
    for row in routes:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('horizon_structure_ids', []))}` | `{len(row.get('black_hole_thermodynamics_ids', []))}` | `{len(row.get('evaporation_radiation_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Black-hole-sector rows make horizon, thermodynamics, microstate, radiation, endpoint, Page-curve, and information-problem wording auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond public-record, subsystem, information/no-go, topology/signature, quantization, viability, matter-sector, cosmology, observed-sector, or residual-cap limits.', '']
    (root / 'docs/30-program/black-hole-sector-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/black-hole-sector-summary.generated.md')


def write_source_reference_usage_audit(root: Path) -> None:
    """Render a broad source-reference usage audit across executable JSON ledgers."""
    import re
    bib_path = root / 'docs/00-meta/bibliography.md'
    bib = bib_path.read_text()
    refs = []
    urls = []
    current = None
    for line in bib.splitlines():
        m = re.match(r'- `(REF-\d{4})`', line)
        if m:
            current = m.group(1)
            refs.append(current)
            continue
        if current and line.strip().startswith('- URL:'):
            urls.append((current, line.split('URL:', 1)[1].strip()))
    ref_set=set(refs)
    used=[]
    def walk(obj):
        if isinstance(obj, dict):
            for k,v in obj.items():
                if k == 'source_refs' and isinstance(v, list):
                    used.extend(x for x in v if isinstance(x, str) and x.startswith('REF-'))
                else:
                    walk(v)
        elif isinstance(obj, list):
            for x in obj: walk(x)
    for jp in sorted(root.glob('*.json')):
        if jp.name == 'AUTHORITY-DEPENDENCY-GRAPH.json':
            continue
        try:
            walk(json.loads(jp.read_text()))
        except Exception:
            pass
    unknown=sorted(set(used)-ref_set)
    by_url={}
    for ref,url in urls:
        by_url.setdefault(url, []).append(ref)
    dup_urls={url:rs for url,rs in by_url.items() if len(rs)>1}
    unused=sorted(ref_set-set(used))
    lines=['# Source-reference usage audit (generated)', '', 'Generated from `docs/00-meta/bibliography.md` and executable JSON `source_refs`. Do not edit directly; run `make index` after changing sources or ledgers.', '', f"- Bibliography REF ids: `{len(refs)}`", f"- JSON source_refs observed: `{len(used)}`", f"- Distinct JSON source_refs observed: `{len(set(used))}`", f"- Unknown source_refs: `{len(unknown)}`", f"- Duplicate bibliography URLs: `{len(dup_urls)}`", f"- Bibliography refs not used by JSON source_refs: `{len(unused)}`", '', '## Duplicate URL entries', '']
    if dup_urls:
        for url,rs in sorted(dup_urls.items()):
            lines.append(f"- `{url}` → {', '.join(f'`{r}`' for r in rs)}")
    else:
        lines.append('- none')
    lines += ['', '## Unknown JSON source_refs', '']
    if unknown:
        for ref in unknown: lines.append(f"- `{ref}`")
    else:
        lines.append('- none')
    lines += ['', '## Most-used JSON source_refs', '']
    counts={r:used.count(r) for r in set(used)}
    for ref,c in sorted(counts.items(), key=lambda kv:(-kv[1], kv[0]))[:40]:
        lines.append(f"- `{ref}`: `{c}`")
    lines += ['', '## Audit rule', '', 'This audit is citation hygiene only. It detects unknown source handles and duplicate bibliography URLs; it does not certify source quality or promote any route. Retired duplicate IDs may remain in the bibliography for continuity but should not receive new executable `source_refs`.', '']
    (root/'docs/30-program/source-reference-usage-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/source-reference-usage-audit.generated.md')

def write_open_question_gate_coverage_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    questions=(root/'docs/20-constitution/open-question-registry.md').read_text()
    binding_by_oq={b.get('claim_or_oq_id'): b for b in bindings}
    rows=registry.get('registry_rows', [])
    missing=[]
    lines=['# Open-question gate coverage audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json`, `CLAIM-ROUTE-BINDING-LEDGER.json`, and `docs/20-constitution/open-question-registry.md`. Do not edit directly; run `make index` after changing route-layer families or bindings.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(rows)}`", '', '| Family | OQ | OQ registered | Binding row | Controlling ledgers covered |', '|---|---|---:|---|---:|']
    for fam in rows:
        fid=fam.get('family_id','')
        oq=fam.get('open_question_id','')
        registered=(f'`{oq}`' in questions) if oq else False
        binding=binding_by_oq.get(oq)
        binding_id=binding.get('binding_id','') if binding else ''
        ledgers=fam.get('ledger_files', [])
        control_ok=bool(binding) and all(l in binding.get('controlling_ledgers', []) for l in ledgers)
        if not registered or not binding or not control_ok:
            missing.append({'family_id':fid,'open_question_id':oq,'oq_registered':registered,'binding_id':binding_id,'controlling_ledgers_covered':control_ok})
        lines.append(f"| `{fid}` | `{oq}` | `{str(registered).lower()}` | `{binding_id or '<missing>'}` | `{str(control_ok).lower()}` |")
    lines += ['', f"- Missing or incomplete OQ gates: `{len(missing)}`", '', '## Rule', '', 'Every registered route-support family must name an owning OQ. That OQ must be present in the open-question registry and must have a claim-route binding row whose `controlling_ledgers` include the family ledgers. This prevents late-added support layers from existing without an explicit stop rule and authority-propagation gate.', '']
    if missing:
        lines += ['## Missing / incomplete gates', '']
        for item in missing:
            lines.append(f"- `{item['family_id']}` → `{item['open_question_id']}` registered={item['oq_registered']} binding=`{item['binding_id'] or '<missing>'}` controlling-ledgers-covered={item['controlling_ledgers_covered']}")
    (root/'docs/30-program/open-question-gate-coverage-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/open-question-gate-coverage-audit.generated.md')

def write_program_id_namespace_audit(root: Path) -> None:
    specs=[('WS', root/'docs/30-program/workstreams.md'), ('BR', root/'docs/30-program/bridge-experiments.md'), ('RF', root/'docs/30-program/research-frontiers.md')]
    lines=['# Program ID namespace audit (generated)', '', 'Generated from workstream, bridge-experiment, and research-frontier surfaces. Do not edit directly; run `make index` after changing program surfaces.', '']
    total_dupes=0
    missing_total=0
    for prefix, path in specs:
        text=path.read_text() if path.exists() else ''
        ids=[]
        import re
        line_pattern = re.compile(rf'^\s*(?:#+\s+|-\s+)?`?({prefix}-\d+)`?\b')
        for line in text.splitlines():
            m = line_pattern.search(line)
            if m:
                ids.append(m.group(1))
        counts={}
        for ident in ids:
            counts[ident]=counts.get(ident,0)+1
        dupes=[ident for ident,c in counts.items() if c>1]
        nums=sorted(int(i.split('-')[1]) for i in counts)
        missing=[]
        if nums:
            missing=[n for n in range(min(nums), max(nums)+1) if n not in nums]
        total_dupes += len(dupes)
        missing_total += len(missing)
        lines += [f"## `{prefix}` namespace", '', f"- Source: `{path.relative_to(root).as_posix()}`", f"- Unique IDs: `{len(counts)}`", f"- Duplicate IDs: `{len(dupes)}`", f"- Missing IDs inside observed range: `{len(missing)}`", f"- Current max: `{prefix}-{max(nums):04d}`" if prefix in ['WS','BR'] and nums else (f"- Current max: `{prefix}-{max(nums):02d}`" if nums else f"- Current max: `<none>`"), '']
        if dupes:
            lines += ['Duplicate entries:', *[f"- `{d}` appears `{counts[d]}` times" for d in dupes], '']
        if missing:
            lines += ['Missing entries:', *[f"- `{prefix}-{n:04d}`" if prefix in ['WS','BR'] else f"- `{prefix}-{n:02d}`" for n in missing[:80]], '']
    lines += ['## Audit rule', '', 'Program IDs are lightweight routing handles, but they should be unique. Duplicate WS/BR/RF IDs hide which workstream or bridge owns an obligation. rev0287 repairs the duplicated rev0286 WS/BR IDs and stale RF pointer, and makes future drift visible.', '']
    (root/'docs/30-program/program-id-namespace-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/program-id-namespace-audit.generated.md')



def augment_authority_dependency_graph_with_singularity_censorship_edges(root: Path) -> None:
    """Add curvature-regime / singularity-resolution / censorship-hyperbolicity edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Curvature-regime / singularity-resolution / censorship-hyperbolicity edges are appended by the rev0290 singularity-censorship augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows = json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings = json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3')
        for cid in row.get('curvature_regime_ids', []):
            add('curvature-regime', cid, 'route', rid, 'curvature-regime-condition', 'route curvature-regime denominator', 'cap high-curvature, Planckian, strong-field, early-universe, or singularity-proximal wording when curvature-regime control fails', effect)
        for sid in row.get('singularity_resolution_ids', []):
            add('singularity-resolution', sid, 'route', rid, 'singularity-resolution-condition', 'route singularity-resolution denominator', 'cap singularity-resolution, bounce, geodesic-completeness, extension, or endpoint wording when singularity control fails', effect)
        for hid in row.get('censorship_hyperbolicity_ids', []):
            add('censorship-hyperbolicity', hid, 'route', rid, 'censorship-hyperbolicity-condition', 'route censorship/hyperbolicity denominator', 'cap weak/strong cosmic-censorship, Cauchy-development, global-hyperbolicity, and deterministic-evolution wording when censorship/hyperbolicity control fails', effect)
    for binding in bindings:
        target_id = binding.get('claim_or_oq_id','')
        target_kind = 'claim' if target_id.startswith('CL-') else 'open-question'
        effect='S3'
        for cid in binding.get('curvature_regime_ids', []):
            add('curvature-regime', cid, target_kind, target_id, 'curvature-regime-claim-condition', f'claim curvature-regime denominator under {binding.get("binding_id")}', 'freeze high-curvature or singularity-proximal claim wording until curvature-regime row is restored', effect)
        for sid in binding.get('singularity_resolution_ids', []):
            add('singularity-resolution', sid, target_kind, target_id, 'singularity-resolution-claim-condition', f'claim singularity-resolution denominator under {binding.get("binding_id")}', 'freeze singularity-resolution, bounce, geodesic-completeness, or endpoint claim wording until singularity row is restored', effect)
        for hid in binding.get('censorship_hyperbolicity_ids', []):
            add('censorship-hyperbolicity', hid, target_kind, target_id, 'censorship-hyperbolicity-claim-condition', f'claim censorship/hyperbolicity denominator under {binding.get("binding_id")}', 'freeze cosmic-censorship, Cauchy-development, global-hyperbolicity, or deterministic-evolution wording until censorship/hyperbolicity row is restored', effect)
    graph['edge_count'] = len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json singularity-censorship edges')


def write_singularity_censorship_summary(root: Path) -> None:
    c = json.loads((root / 'CURVATURE-REGIME-LEDGER.json').read_text())
    s = json.loads((root / 'SINGULARITY-RESOLUTION-LEDGER.json').read_text())
    h = json.loads((root / 'CENSORSHIP-HYPERBOLICITY-LEDGER.json').read_text())
    routes = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    crows = c.get('curvature_rows', [])
    srows = s.get('singularity_rows', [])
    hrows = h.get('censorship_rows', [])
    def counts(rows, key):
        out={}
        for r in rows:
            out[r.get(key,'<missing>')] = out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Singularity / censorship / hyperbolicity summary (generated)', '', 'Generated from `CURVATURE-REGIME-LEDGER.json`, `SINGULARITY-RESOLUTION-LEDGER.json`, and `CENSORSHIP-HYPERBOLICITY-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{c.get('revision','<missing>')}`", f"- Curvature-regime rows: `{len(crows)}`", f"- Singularity-resolution rows: `{len(srows)}`", f"- Censorship/hyperbolicity rows: `{len(hrows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Curvature-regime class counts', '']
    for k,v in sorted(counts(crows,'curvature_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Singularity-resolution class counts', '']
    for k,v in sorted(counts(srows,'singularity_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Censorship/hyperbolicity class counts', '']
    for k,v in sorted(counts(hrows,'censorship_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Non-promotion rule', '', 'Singularity/censorship rows make high-curvature, singularity-resolution, bounce, geodesic-completeness, weak/strong cosmic-censorship, Cauchy-development, global-hyperbolicity, and deterministic-evolution wording auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond observed-sector, black-hole, cosmology, topology/signature, boundary/sector, gauge, quantization, viability, public-record, and residual-cap limits.', '']
    (root / 'docs/30-program/singularity-censorship-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/singularity-censorship-summary.generated.md')


def write_constitutional_id_namespace_audit(root: Path) -> None:
    import re
    specs=[('CL', root/'docs/20-constitution/claim-registry.md'), ('OQ', root/'docs/20-constitution/open-question-registry.md')]
    lines=['# Constitutional ID namespace audit (generated)', '', 'Generated from `docs/20-constitution/claim-registry.md` and `docs/20-constitution/open-question-registry.md`. Do not edit directly; run `make index` after changing constitutional registries.', '']
    total_dupes=0; total_missing=0; total_nonmonotone=0
    for prefix, path in specs:
        text=path.read_text() if path.exists() else ''
        pattern=re.compile(rf'^- `({prefix}-\d{{4}})`', re.MULTILINE)
        ids=pattern.findall(text)
        nums=[int(x.split('-')[1]) for x in ids]
        counts={}
        for ident in ids: counts[ident]=counts.get(ident,0)+1
        dupes=[ident for ident,c in counts.items() if c>1]
        missing=[]
        if nums:
            missing=[n for n in range(min(nums), max(nums)+1) if n not in set(nums)]
        nonmonotone=sum(1 for a,b in zip(nums, nums[1:]) if b<a)
        total_dupes += len(dupes); total_missing += len(missing); total_nonmonotone += nonmonotone
        lines += [f"## `{prefix}` namespace", '', f"- Source: `{path.relative_to(root).as_posix()}`", f"- Entry count: `{len(ids)}`", f"- Unique IDs: `{len(counts)}`", f"- Duplicate IDs: `{len(dupes)}`", f"- Missing IDs inside observed range: `{len(missing)}`", f"- Nonmonotone adjacent transitions: `{nonmonotone}`", f"- Current max: `{prefix}-{max(nums):04d}`" if nums else f"- Current max: `<none>`", '']
        if dupes:
            lines += ['Duplicate entries:', *[f"- `{d}` appears `{counts[d]}` times" for d in dupes], '']
        if missing:
            lines += ['Missing entries:', *[f"- `{prefix}-{n:04d}`" for n in missing[:120]], '']
    lines += ['## Audit result', '', f"- Duplicate namespace IDs: `{total_dupes}`", f"- Missing namespace IDs: `{total_missing}`", f"- Nonmonotone adjacent transitions: `{total_nonmonotone}`", '', '## Audit rule', '', 'Constitutional IDs are not evidence, but they are authority handles. Duplicate or skipped `CL-####` / `OQ-####` entries make later route bindings ambiguous. This audit keeps registry growth visible and does not promote any scientific route.', '']
    (root/'docs/30-program/constitutional-id-namespace-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/constitutional-id-namespace-audit.generated.md')



def augment_authority_dependency_graph_with_stress_energy_backreaction_edges(root: Path) -> None:
    """Add stress-energy/source, semiclassical-backreaction, and energy-condition edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Stress-energy/source, semiclassical-backreaction, and energy-condition edges are appended by the rev0291 stress-energy/backreaction augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows = json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings = json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for sid in row.get('stress_energy_source_ids', []):
            add('stress-energy-source', sid, 'route', rid, 'stress-energy-source-condition', 'route stress-energy/source denominator', 'cap stress tensor, effective source, matter current, mediator source, detector/source stress, or cosmological fluid wording when source control fails', effect)
        for bid in row.get('backreaction_consistency_ids', []):
            add('semiclassical-backreaction', bid, 'route', rid, 'semiclassical-backreaction-condition', 'route backreaction denominator', 'cap semiclassical Einstein equation, expectation-value backreaction, stochastic/noise-kernel, metric-response, or feedback wording when backreaction control fails', effect)
        for eid in row.get('energy_condition_ids', []):
            add('energy-condition', eid, 'route', rid, 'energy-condition-condition', 'route energy-condition denominator', 'cap NEC/WEC/SEC/DEC, ANEC, QEI, QNEC/QFC-adjacent, positivity, exotic-matter, or singularity-theorem-assumption wording when condition control fails', effect)
    for binding in bindings:
        target_id=binding.get('claim_or_oq_id','')
        target_kind='claim' if target_id.startswith('CL-') else 'open-question'
        effect=binding.get('maximum_authority_effect','S3') or 'S3'
        for sid in binding.get('stress_energy_source_ids', []):
            add('stress-energy-source', sid, target_kind, target_id, 'stress-energy-source-claim-condition', f'claim stress-energy/source denominator under {binding.get("binding_id")}', 'freeze source/stress-tensor claim wording until source row is restored', effect)
        for bid in binding.get('backreaction_consistency_ids', []):
            add('semiclassical-backreaction', bid, target_kind, target_id, 'semiclassical-backreaction-claim-condition', f'claim backreaction denominator under {binding.get("binding_id")}', 'freeze backreaction/semiclassical-closure claim wording until backreaction row is restored', effect)
        for eid in binding.get('energy_condition_ids', []):
            add('energy-condition', eid, target_kind, target_id, 'energy-condition-claim-condition', f'claim energy-condition denominator under {binding.get("binding_id")}', 'freeze energy-condition/QNEC/QEI/exotic-matter claim wording until energy-condition row is restored', effect)
    graph['edge_count'] = len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json stress-energy/backreaction edges')


def write_stress_energy_backreaction_summary(root: Path) -> None:
    source=json.loads((root/'STRESS-ENERGY-SOURCE-LEDGER.json').read_text())
    back=json.loads((root/'SEMICLASSICAL-BACKREACTION-LEDGER.json').read_text())
    cond=json.loads((root/'ENERGY-CONDITION-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    srows=source.get('source_rows', []); brows=back.get('backreaction_rows', []); erows=cond.get('energy_condition_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Stress-energy / backreaction / energy-condition summary (generated)', '', 'Generated from `STRESS-ENERGY-SOURCE-LEDGER.json`, `SEMICLASSICAL-BACKREACTION-LEDGER.json`, `ENERGY-CONDITION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{source.get('revision','<missing>')}`", f"- Stress-energy/source rows: `{len(srows)}`", f"- Semiclassical-backreaction rows: `{len(brows)}`", f"- Energy-condition rows: `{len(erows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Stress-source class counts', '']
    for k,v in sorted(counts(srows,'stress_source_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Backreaction class counts', '']
    for k,v in sorted(counts(brows,'backreaction_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Energy-condition class counts', '']
    for k,v in sorted(counts(erows,'energy_condition_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Non-promotion rule', '', 'Stress-energy/source, backreaction, and energy-condition rows make stress tensor, effective source, semiclassical Einstein equation, stochastic/noise-kernel, QNEC/QEI, exotic-matter, and singularity-theorem-assumption wording auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond matter, cosmology, black-hole, singularity/censorship, viability, quantization, public-record, and residual-cap limits.', '']
    (root/'docs/30-program/stress-energy-backreaction-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/stress-energy-backreaction-summary.generated.md')


def write_ledger_summary_coverage_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    rows=registry.get('registry_rows', [])
    missing=[]; declared=0; present=0
    lines=['# Ledger summary coverage audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json`. Do not edit directly; run `make index` after changing registered route-support families.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(rows)}`", '', '| Family | Generated summary | Present |', '|---|---|---:|']
    for fam in rows:
        summary=fam.get('generated_summary','')
        ok=bool(summary and (root/summary).exists())
        if summary: declared += 1
        if ok: present += 1
        if summary and not ok: missing.append((fam.get('family_id'), summary))
        lines.append(f"| `{fam.get('family_id')}` | `{summary or '<not-declared>'}` | `{1 if ok else 0}` |")
    lines += ['', f"- Families with declared summaries: `{declared}`", f"- Declared summaries present: `{present}`", f"- Missing declared summaries: `{len(missing)}`", '', '## Audit rule', '', 'Generated summaries are restart surfaces, not evidence. A registered family with a generated summary must point to an existing generated file so compact mirrors cannot silently under-report the executable route stack.', '']
    if missing:
        lines += ['## Missing declared summaries', '']
        for fid, summary in missing:
            lines.append(f"- `{fid}` → `{summary}`")
    (root/'docs/30-program/ledger-summary-coverage-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/ledger-summary-coverage-audit.generated.md')



def augment_authority_dependency_graph_with_classical_gr_edges(root: Path) -> None:
    """Add equivalence-principle / weak-field-PPN / gravitational-radiation edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Classical-GR equivalence-principle, weak-field/PPN, and gravitational-radiation edges are appended by the rev0292 classical-GR augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str: return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id: return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing: return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for eid in row.get('equivalence_principle_ids', []):
            add('equivalence-principle', eid, 'route', rid, 'equivalence-principle-condition', 'route equivalence-principle denominator', 'cap WEP/EEP/SEP, metric-coupling, local Lorentz/local position invariance, clock, or geodesic-motion wording when equivalence control fails', effect)
        for pid in row.get('weak_field_ppn_ids', []):
            add('weak-field-ppn', pid, 'route', rid, 'weak-field-ppn-condition', 'route weak-field/PPN denominator', 'cap Newtonian-limit, PPN, solar-system, Shapiro-delay, light-deflection, frame-dragging, or metric-theory wording when weak-field control fails', effect)
        for gid in row.get('gravitational_radiation_ids', []):
            add('gravitational-radiation', gid, 'route', rid, 'gravitational-radiation-condition', 'route gravitational-radiation denominator', 'cap radiation-reaction, binary-pulsar, gravitational-wave, propagation, polarization, waveform, or tensor-mode wording when radiation control fails', effect)
    for binding in bindings:
        target_id=binding.get('claim_or_oq_id',''); target_kind='claim' if target_id.startswith('CL-') else 'open-question'; effect=binding.get('maximum_authority_effect','S3') or 'S3'
        for eid in binding.get('equivalence_principle_ids', []):
            add('equivalence-principle', eid, target_kind, target_id, 'equivalence-principle-claim-condition', f'claim equivalence-principle denominator under {binding.get("binding_id")}', 'freeze equivalence-principle or metric-coupling claim wording until equivalence row is restored', effect)
        for pid in binding.get('weak_field_ppn_ids', []):
            add('weak-field-ppn', pid, target_kind, target_id, 'weak-field-ppn-claim-condition', f'claim weak-field/PPN denominator under {binding.get("binding_id")}', 'freeze weak-field, solar-system, or PPN claim wording until weak-field row is restored', effect)
        for gid in binding.get('gravitational_radiation_ids', []):
            add('gravitational-radiation', gid, target_kind, target_id, 'gravitational-radiation-claim-condition', f'claim gravitational-radiation denominator under {binding.get("binding_id")}', 'freeze radiation-reaction, binary-pulsar, GW, waveform, or propagation claim wording until radiation row is restored', effect)
    graph['edge_count']=len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json classical-GR recovery edges')


def write_classical_gr_recovery_summary(root: Path) -> None:
    ep=json.loads((root/'EQUIVALENCE-PRINCIPLE-LEDGER.json').read_text())
    ppn=json.loads((root/'WEAK-FIELD-PPN-LEDGER.json').read_text())
    rad=json.loads((root/'GRAVITATIONAL-RADIATION-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    erows=ep.get('equivalence_principle_rows', []); prows=ppn.get('weak_field_ppn_rows', []); rrows=rad.get('radiation_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Classical GR recovery summary (generated)', '', 'Generated from `EQUIVALENCE-PRINCIPLE-LEDGER.json`, `WEAK-FIELD-PPN-LEDGER.json`, `GRAVITATIONAL-RADIATION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{ep.get('revision','<missing>')}`", f"- Equivalence-principle rows: `{len(erows)}`", f"- Weak-field/PPN rows: `{len(prows)}`", f"- Gravitational-radiation rows: `{len(rrows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Equivalence-principle class counts', '']
    for k,v in sorted(counts(erows,'equivalence_principle_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Weak-field/PPN class counts', '']
    for k,v in sorted(counts(prows,'weak_field_ppn_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Gravitational-radiation class counts', '']
    for k,v in sorted(counts(rrows,'gravitational_radiation_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Non-promotion rule', '', 'Equivalence-principle, weak-field/PPN, and gravitational-radiation rows make classical-GR recovery language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond matter, stress-energy/backreaction, black-hole, cosmology, singularity/censorship, viability, public-record, observed-sector, and residual-cap limits.', '']
    (root/'docs/30-program/classical-gr-recovery-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/classical-gr-recovery-summary.generated.md')



def augment_authority_dependency_graph_with_state_preparation_detector_decoherence_edges(root: Path) -> None:
    """Add state-preparation / detector-response / decoherence-pointer edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' State-preparation / detector-response / decoherence-pointer edges are appended by the rev0293 quantum-record augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id: return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing: return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for sid in row.get('state_preparation_ids', []):
            add('state-preparation', sid, 'route', rid, 'state-preparation-condition', 'route state-preparation denominator', 'cap prepared-state, source-state, vacuum/sector, benchmark-target, SPAM, or apparatus-state wording when state-preparation control fails', effect)
        for did in row.get('detector_response_ids', []):
            add('detector-response', did, 'route', rid, 'detector-response-condition', 'route detector-response denominator', 'cap detector, witness, POVM/instrument, response-function, backaction, threshold, or direct-observation wording when detector-response control fails', effect)
        for pid in row.get('decoherence_pointer_ids', []):
            add('decoherence-pointer', pid, 'route', rid, 'decoherence-pointer-condition', 'route decoherence/pointer-record denominator', 'cap decoherence, pointer-basis, objectivity, collapse-like, or public quantum-record wording when decoherence/pointer control fails', effect)
    for binding in bindings:
        target_id=binding.get('claim_or_oq_id',''); target_kind='claim' if target_id.startswith('CL-') else 'open-question'; effect=binding.get('maximum_authority_effect','S3') or 'S3'
        for sid in binding.get('state_preparation_ids', []):
            add('state-preparation', sid, target_kind, target_id, 'state-preparation-claim-condition', f'claim state-preparation denominator under {binding.get("binding_id")}', 'freeze prepared-state or SPAM claim wording until state-preparation rows are restored', effect)
        for did in binding.get('detector_response_ids', []):
            add('detector-response', did, target_kind, target_id, 'detector-response-claim-condition', f'claim detector-response denominator under {binding.get("binding_id")}', 'freeze detector, witness, response, or direct-observation claim wording until detector-response rows are restored', effect)
        for pid in binding.get('decoherence_pointer_ids', []):
            add('decoherence-pointer', pid, target_kind, target_id, 'decoherence-pointer-claim-condition', f'claim decoherence/pointer denominator under {binding.get("binding_id")}', 'freeze decoherence, objectivity, pointer-record, or public quantum-record wording until decoherence rows are restored', effect)
    graph['edge_count']=len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json state-preparation/detector/decoherence edges')


def write_state_preparation_detector_decoherence_summary(root: Path) -> None:
    sp=json.loads((root/'STATE-PREPARATION-LEDGER.json').read_text())
    dr=json.loads((root/'DETECTOR-RESPONSE-LEDGER.json').read_text())
    dc=json.loads((root/'DECOHERENCE-POINTER-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    srows=sp.get('state_preparation_rows', []); drows=dr.get('detector_response_rows', []); crows=dc.get('decoherence_pointer_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# State-preparation / detector-response / decoherence-pointer summary (generated)', '', 'Generated from `STATE-PREPARATION-LEDGER.json`, `DETECTOR-RESPONSE-LEDGER.json`, `DECOHERENCE-POINTER-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{sp.get('revision','<missing>')}`", f"- State-preparation rows: `{len(srows)}`", f"- Detector-response rows: `{len(drows)}`", f"- Decoherence/pointer rows: `{len(crows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## State-preparation class counts', '']
    for k,v in sorted(counts(srows,'state_preparation_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Detector-response class counts', '']
    for k,v in sorted(counts(drows,'detector_response_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Decoherence/pointer class counts', '']
    for k,v in sorted(counts(crows,'decoherence_pointer_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Non-promotion rule', '', 'State-preparation, detector-response, and decoherence/pointer rows make quantum-record wording auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond public-record custody, measurement/systematics, subsystem/factorization, information/no-go, quantization/correspondence, observed-sector, and residual-cap limits.', '']
    (root/'docs/30-program/state-preparation-detector-decoherence-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/state-preparation-detector-decoherence-summary.generated.md')


def write_schema_envelope_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    failures=[]
    lines=['# Schema-envelope audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json` and `schemas/*.schema.json`. Do not edit directly; run `make index` after changing registered ledger families or schemas.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", '', '| Family | Ledger | Schema | Row key | Envelope OK |', '|---|---|---|---|---:|']
    for fam in registry.get('registry_rows', []):
        for rel in fam.get('ledger_files', []):
            ledger_path=root/rel
            schema_rel='schemas/'+rel.lower().replace('_','-').replace('.json','.schema.json')
            schema_path=root/schema_rel
            row_key='<missing>'
            ok=True
            if not ledger_path.exists() or not schema_path.exists():
                ok=False
            else:
                data=json.loads(ledger_path.read_text())
                schema=json.loads(schema_path.read_text())
                for base in ['project','revision','schema_version','purpose']:
                    if base not in data or base not in schema.get('required', []): ok=False
                row_keys=[k for k,v in data.items() if isinstance(v,list) and (k.endswith('_rows') or k in ['source_rows','radiation_rows','controls','empirical_deltas','evidence_units'])]
                row_key=row_keys[0] if row_keys else '<missing>'
                if row_key == '<missing>' or row_key not in schema.get('required', []): ok=False
                if row_key not in schema.get('properties', {}): ok=False
            if not ok: failures.append((fam.get('family_id'), rel, schema_rel, row_key))
            lines.append(f"| `{fam.get('family_id')}` | `{rel}` | `{schema_rel}` | `{row_key}` | `{1 if ok else 0}` |")
    lines += ['', f"- Envelope failures: `{len(failures)}`", '', '## Audit rule', '', 'Every registered ledger family must expose ledgers whose basic JSON envelope is reflected in its schema: `project`, `revision`, `schema_version`, `purpose`, and the primary row array. This audit is not a scientific authority source; it prevents schema drift and restart confusion.', '']
    if failures:
        lines += ['## Failures', '']
        for fam, rel, schema_rel, row_key in failures:
            lines.append(f"- `{fam}` / `{rel}` / `{schema_rel}` row key `{row_key}`")
    (root/'docs/30-program/schema-envelope-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/schema-envelope-audit.generated.md')


def write_ledger_row_count_parity_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    route_count=len(json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', []))
    expected=route_count+1
    missing=[]
    def row_count_for(rel: str) -> int:
        data=json.loads((root/rel).read_text())
        for key,val in data.items():
            if key.endswith('_rows') or key in ['source_rows','radiation_rows']:
                if isinstance(val, list): return len(val)
        return 0
    lines=['# Ledger row-count parity audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json` and route-local ledgers. Do not edit directly; run `make index` after changing registered route-support families.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Route rows: `{route_count}`", f"- Expected route-local-plus-wrapper row count: `{expected}`", '', '| Family | Policy | Ledger | Rows | Expected | Pass |', '|---|---|---|---:|---:|---:|']
    for fam in registry.get('registry_rows', []):
        if fam.get('cardinality_policy')!='route-local-plus-wrapper':
            continue
        for rel in fam.get('ledger_files', []):
            count=row_count_for(rel) if (root/rel).exists() else 0
            ok=count==expected
            if not ok: missing.append((fam.get('family_id'), rel, count, expected))
            lines.append(f"| `{fam.get('family_id')}` | `{fam.get('cardinality_policy')}` | `{rel}` | `{count}` | `{expected}` | `{1 if ok else 0}` |")
    lines += ['', f"- Parity failures: `{len(missing)}`", '', '## Audit rule', '', 'Route-local-plus-wrapper ledger families should have one row per route plus one metadata/provenance wrapper row in each ledger. A parity failure does not change scientific authority by itself, but it signals a hidden route-row or wrapper omission that must be repaired before wording from that family can be trusted.', '']
    if missing:
        lines += ['## Failures', '']
        for fid, rel, count, exp in missing:
            lines.append(f"- `{fid}` / `{rel}` has `{count}` rows; expected `{exp}`")
    (root/'docs/30-program/ledger-row-count-parity-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/ledger-row-count-parity-audit.generated.md')


def augment_authority_dependency_graph_with_asymptotic_ir_scattering_edges(root: Path) -> None:
    """Add asymptotic-state / infrared-dressing / scattering-observable edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Asymptotic-state / infrared-dressing / scattering-observable edges are appended by the rev0294 asymptotic/IR/scattering augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for sid in row.get('asymptotic_state_ids', []):
            add('asymptotic-state', sid, 'route', rid, 'asymptotic-state-condition', 'route asymptotic-state denominator', 'cap S-matrix, in/out state, Fock-space, boundary-state, or asymptotic-completeness wording when asymptotic-state control fails', effect)
        for iid in row.get('infrared_dressing_ids', []):
            add('infrared-dressing', iid, 'route', rid, 'infrared-dressing-condition', 'route infrared/soft-sector denominator', 'cap IR-finite, soft-theorem, memory, BMS-charge, dressing, or inclusive-sum wording when IR control fails', effect)
        for oid in row.get('scattering_observable_ids', []):
            add('scattering-observable', oid, 'route', rid, 'scattering-observable-condition', 'route scattering/inclusive-observable denominator', 'cap amplitude, inclusive-rate, finite-time detector, memory-readout, or catalog-likelihood wording when observable control fails', effect)
    for binding in bindings:
        target_id=binding.get('claim_or_oq_id',''); target_kind='claim' if target_id.startswith('CL-') else 'open-question'; effect=binding.get('maximum_authority_effect','S3') or 'S3'
        for sid in binding.get('asymptotic_state_ids', []):
            add('asymptotic-state', sid, target_kind, target_id, 'asymptotic-state-claim-condition', f'claim asymptotic-state denominator under {binding.get("binding_id")}', 'freeze S-matrix or asymptotic-state claim wording until asymptotic rows are restored', effect)
        for iid in binding.get('infrared_dressing_ids', []):
            add('infrared-dressing', iid, target_kind, target_id, 'infrared-dressing-claim-condition', f'claim infrared-dressing denominator under {binding.get("binding_id")}', 'freeze IR-finite, soft-sector, memory, or inclusive-sum claim wording until IR rows are restored', effect)
        for oid in binding.get('scattering_observable_ids', []):
            add('scattering-observable', oid, target_kind, target_id, 'scattering-observable-claim-condition', f'claim scattering-observable denominator under {binding.get("binding_id")}', 'freeze scattering, inclusive-rate, finite-time detector, or catalog-likelihood wording until observable rows are restored', effect)
    graph['edge_count']=len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json asymptotic/IR/scattering edges')


def write_asymptotic_ir_scattering_summary(root: Path) -> None:
    asym=json.loads((root/'ASYMPTOTIC-STATE-LEDGER.json').read_text())
    ir=json.loads((root/'INFRARED-DRESSING-LEDGER.json').read_text())
    scat=json.loads((root/'SCATTERING-OBSERVABLE-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    arows=asym.get('asymptotic_state_rows', []); irows=ir.get('infrared_dressing_rows', []); srows=scat.get('scattering_observable_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Asymptotic / IR / scattering summary (generated)', '', 'Generated from `ASYMPTOTIC-STATE-LEDGER.json`, `INFRARED-DRESSING-LEDGER.json`, `SCATTERING-OBSERVABLE-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{asym.get('revision','<missing>')}`", f"- Asymptotic-state rows: `{len(arows)}`", f"- Infrared-dressing rows: `{len(irows)}`", f"- Scattering-observable rows: `{len(srows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Asymptotic-state class counts', '']
    for k,v in sorted(counts(arows,'asymptotic_state_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Infrared-dressing class counts', '']
    for k,v in sorted(counts(irows,'infrared_dressing_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Scattering-observable class counts', '']
    for k,v in sorted(counts(srows,'scattering_observable_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Non-promotion rule', '', 'Asymptotic-state, infrared-dressing, and scattering/inclusive-observable rows make S-matrix, soft-sector, memory, IR-finite, inclusive-rate, and finite-time scattering language auditable. They can cap, freeze, demote, or sharpen support, but they do not promote a route beyond public-record, detector-response, gauge/constraint, information/no-go, state-preparation, observed-sector, and residual-cap limits.', '']
    (root/'docs/30-program/asymptotic-ir-scattering-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/asymptotic-ir-scattering-summary.generated.md')


def write_candidate_route_schema_field_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    schema=json.loads((root/'schemas/candidate-route-state-ledger.schema.json').read_text())
    required=set(schema.get('properties',{}).get('route_rows',{}).get('items',{}).get('required',[]))
    missing=[]
    total=0
    for fam in registry.get('registry_rows', []):
        for field in fam.get('route_fields', []):
            total += 1
            if field not in required:
                missing.append((fam.get('family_id','<missing>'), field))
    lines=['# Candidate-route schema field audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json` and `schemas/candidate-route-state-ledger.schema.json`. Do not edit directly; run `make index` after changing route-layer families or the route schema.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- Registered route fields checked: `{total}`", f"- Missing schema-required route fields: `{len(missing)}`", '', '## Rule', '', 'Every registered route-support field should appear in the route-row `required` list of `schemas/candidate-route-state-ledger.schema.json`. Missing fields indicate schema drift: route authority handles may exist in prose or ledgers without being schema-required.', '']
    if missing:
        lines += ['## Missing fields', '']
        for fam, field in missing:
            lines.append(f"- `{fam}` / `{field}`")
    (root/'docs/30-program/candidate-route-schema-field-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/candidate-route-schema-field-audit.generated.md')



def augment_authority_dependency_graph_with_discretization_continuum_edges(root: Path) -> None:
    """Add discretization-regime / finite-volume-scaling / continuum-extrapolation edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Discretization-regime / finite-volume-scaling / continuum-extrapolation edges are appended by the rev0295 discretization/continuum augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for did in row.get('discretization_regime_ids', []):
            add('discretization-regime', did, 'route', rid, 'discretization-regime-condition', 'route discretization/regulator denominator', 'cap lattice, triangulation, simulator, grid, or regulator wording when discretization control fails', effect)
        for fid in row.get('finite_volume_scaling_ids', []):
            add('finite-volume-scaling', fid, 'route', rid, 'finite-volume-scaling-condition', 'route finite-volume/finite-size denominator', 'cap finite-volume, thermodynamic-limit, infinite-volume, finite-catalog, or scaling wording when size scaling fails', effect)
        for cid in row.get('continuum_extrapolation_ids', []):
            add('continuum-extrapolation', cid, 'route', rid, 'continuum-extrapolation-condition', 'route continuum-limit/nonperturbative denominator', 'cap continuum-limit, nonperturbative-definition, or continuum candidate wording when extrapolation control fails', effect)
    for binding in bindings:
        target_id=binding.get('claim_or_oq_id',''); target_kind='claim' if target_id.startswith('CL-') else 'open-question'; effect=binding.get('maximum_authority_effect','S3') or 'S3'
        for did in binding.get('discretization_regime_ids', []):
            add('discretization-regime', did, target_kind, target_id, 'discretization-regime-claim-condition', f'claim discretization denominator under {binding.get("binding_id")}', 'freeze lattice, triangulation, simulator, grid, or regulator claim wording until discretization rows are restored', effect)
        for fid in binding.get('finite_volume_scaling_ids', []):
            add('finite-volume-scaling', fid, target_kind, target_id, 'finite-volume-scaling-claim-condition', f'claim finite-volume/scaling denominator under {binding.get("binding_id")}', 'freeze finite-volume, thermodynamic-limit, infinite-volume, or scaling claim wording until finite-volume rows are restored', effect)
        for cid in binding.get('continuum_extrapolation_ids', []):
            add('continuum-extrapolation', cid, target_kind, target_id, 'continuum-extrapolation-claim-condition', f'claim continuum-extrapolation denominator under {binding.get("binding_id")}', 'freeze continuum-limit or nonperturbative-definition claim wording until continuum-extrapolation rows are restored', effect)
    graph['edge_count']=len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json discretization/continuum edges')


def write_discretization_continuum_summary(root: Path) -> None:
    disc=json.loads((root/'DISCRETIZATION-REGIME-LEDGER.json').read_text())
    finite=json.loads((root/'FINITE-VOLUME-SCALING-LEDGER.json').read_text())
    cont=json.loads((root/'CONTINUUM-EXTRAPOLATION-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    drows=disc.get('discretization_rows', []); frows=finite.get('finite_volume_rows', []); crows=cont.get('continuum_extrapolation_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Discretization / finite-volume / continuum summary (generated)', '', 'Generated from `DISCRETIZATION-REGIME-LEDGER.json`, `FINITE-VOLUME-SCALING-LEDGER.json`, `CONTINUUM-EXTRAPOLATION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{disc.get('revision','<missing>')}`", f"- Discretization-regime rows: `{len(drows)}`", f"- Finite-volume/scaling rows: `{len(frows)}`", f"- Continuum-extrapolation rows: `{len(crows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Discretization-regime class counts', '']
    for k,v in sorted(counts(drows,'discretization_regime_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Finite-volume/scaling class counts', '']
    for k,v in sorted(counts(frows,'finite_volume_scaling_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Continuum-extrapolation class counts', '']
    for k,v in sorted(counts(crows,'continuum_extrapolation_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Non-promotion rule', '', 'Discretization-regime, finite-volume/scaling, and continuum-extrapolation rows make lattice, triangulation, simulator, finite-volume, thermodynamic-limit, continuum-limit, and nonperturbative-definition language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond public-record, gauge/constraint, topology/signature, measure/ensemble, observed-sector, and residual-cap limits.', '']
    (root/'docs/30-program/discretization-continuum-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/discretization-continuum-summary.generated.md')


def write_ledger_row_id_uniqueness_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    seen={}; dups=[]; checked=0
    lines=['# Ledger row-ID uniqueness audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json` and registered JSON ledgers. Do not edit directly; run `make index` after changing registered ledgers.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", '', '| Ledger | Row key | ID field | Rows checked | Duplicate IDs |', '|---|---|---|---:|---:|']
    for fam in registry.get('registry_rows', []):
        for rel in fam.get('ledger_files', []):
            p=root/rel
            if not p.exists():
                lines.append(f"| `{rel}` | `<missing>` | `<missing>` | `0` | `0` |")
                continue
            data=json.loads(p.read_text())
            row_keys=[k for k,v in data.items() if isinstance(v,list) and (k.endswith('_rows') or k in ['source_rows','radiation_rows','controls','empirical_deltas','evidence_units'])]
            row_key=row_keys[0] if row_keys else '<missing>'
            rows=data.get(row_key, []) if row_key!='<missing>' else []
            id_candidates=[]
            for r in rows:
                ids=[k for k,v in r.items() if k.endswith('_id') and isinstance(v,str) and v]
                id_candidates.append(ids[0] if ids else '<missing>')
            local_dups=0
            for r,idfield in zip(rows,id_candidates):
                rid=r.get(idfield,'') if idfield!='<missing>' else ''
                checked += 1
                if not rid:
                    dups.append((rel,row_key,idfield,'<missing>','missing id'))
                    local_dups += 1
                    continue
                if rid in seen:
                    dups.append((rel,row_key,idfield,rid,seen[rid]))
                    local_dups += 1
                else:
                    seen[rid]=rel
            idfield=id_candidates[0] if id_candidates else '<missing>'
            lines.append(f"| `{rel}` | `{row_key}` | `{idfield}` | `{len(rows)}` | `{local_dups}` |")
    lines += ['', f"- Registered ledger rows checked: `{checked}`", f"- Duplicate or missing row IDs: `{len(dups)}`", '', '## Audit rule', '', 'Registered executable ledger row identifiers must be unique across the route-support stack. A duplicate ID can make dependency edges, claim bindings, and generated summaries point at the wrong authority object even when each individual ledger is schema-valid.', '']
    if dups:
        lines += ['## Failures', '']
        for rel,row_key,idfield,rid,prev in dups:
            lines.append(f"- `{rid}` in `{rel}` / `{row_key}` / `{idfield}` conflicts with `{prev}`")
    (root/'docs/30-program/ledger-row-id-uniqueness-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/ledger-row-id-uniqueness-audit.generated.md')



def augment_authority_dependency_graph_with_correlator_operator_bootstrap_edges(root: Path) -> None:
    """Add correlation-function / operator-insertion / bootstrap-data edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Correlation-function / operator-insertion / bootstrap-data edges are appended by the rev0296 correlator/operator/bootstrap augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for cid in row.get('correlation_function_ids', []):
            add('correlation-function', cid, 'route', rid, 'correlation-function-condition', 'route correlation-function denominator', 'cap correlator, n-point, response-function, catalog-correlation, or bulk-boundary-correlator wording when the correlation row fails', effect)
        for oid in row.get('operator_insertion_ids', []):
            add('operator-insertion', oid, 'route', rid, 'operator-insertion-condition', 'route operator-insertion/dictionary denominator', 'cap operator-label, source-term, smearing, decoder-feature, or dictionary wording when the operator row fails', effect)
        for bid in row.get('bootstrap_data_ids', []):
            add('bootstrap-data', bid, 'route', rid, 'bootstrap-data-condition', 'route OPE/CFT-data/bootstrap denominator', 'cap OPE, conformal-block, crossing, bootstrap-island, and CFT-data wording when bootstrap-data control fails', effect)
    for binding in bindings:
        target_id=binding.get('claim_or_oq_id',''); target_kind='claim' if target_id.startswith('CL-') else 'open-question'; effect=binding.get('maximum_authority_effect','S3') or 'S3'
        for cid in binding.get('correlation_function_ids', []):
            add('correlation-function', cid, target_kind, target_id, 'correlation-function-claim-condition', f'claim correlation-function denominator under {binding.get("binding_id")}', 'freeze correlator, n-point, generating-functional, and response-function claim wording until correlation-function rows are restored', effect)
        for oid in binding.get('operator_insertion_ids', []):
            add('operator-insertion', oid, target_kind, target_id, 'operator-insertion-claim-condition', f'claim operator-insertion denominator under {binding.get("binding_id")}', 'freeze operator-dictionary, source-term, vertex, decoder-feature, and physical-observable wording until operator-insertion rows are restored', effect)
        for bid in binding.get('bootstrap_data_ids', []):
            add('bootstrap-data', bid, target_kind, target_id, 'bootstrap-data-claim-condition', f'claim bootstrap-data denominator under {binding.get("binding_id")}', 'freeze OPE, conformal-block, crossing, numerical-bootstrap, CFT-data, and bootstrap-island wording until bootstrap-data rows are restored', effect)
    graph['edge_count']=len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json correlator/operator/bootstrap edges')


def write_correlator_operator_bootstrap_summary(root: Path) -> None:
    c=json.loads((root/'CORRELATION-FUNCTION-LEDGER.json').read_text())
    o=json.loads((root/'OPERATOR-INSERTION-LEDGER.json').read_text())
    b=json.loads((root/'BOOTSTRAP-DATA-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    crows=c.get('correlation_function_rows', []); orows=o.get('operator_insertion_rows', []); brows=b.get('bootstrap_data_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Correlator / operator / bootstrap summary (generated)', '', 'Generated from `CORRELATION-FUNCTION-LEDGER.json`, `OPERATOR-INSERTION-LEDGER.json`, `BOOTSTRAP-DATA-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{c.get('revision','<missing>')}`", f"- Correlation-function rows: `{len(crows)}`", f"- Operator-insertion rows: `{len(orows)}`", f"- Bootstrap/CFT-data rows: `{len(brows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Correlation-function class counts', '']
    for k,v in sorted(counts(crows,'correlation_function_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Operator-insertion class counts', '']
    for k,v in sorted(counts(orows,'operator_insertion_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Bootstrap/CFT-data class counts', '']
    for k,v in sorted(counts(brows,'bootstrap_data_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Non-promotion rule', '', 'Correlation-function, operator-insertion, and bootstrap/CFT-data rows make correlator, n-point, generating-functional, operator-dictionary, OPE, conformal-block, crossing, bootstrap-island, CFT-data, and bulk-boundary-correlator language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, observed-sector, observable-quotient, measurement, IR, discretization, and residual-cap limits.', '']
    (root/'docs/30-program/correlator-operator-bootstrap-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/correlator-operator-bootstrap-summary.generated.md')



def augment_authority_dependency_graph_with_phase_order_universality_edges(root: Path) -> None:
    """Add phase-structure / order-parameter / universality-class edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Phase-structure / order-parameter / universality-class edges are appended by the rev0297 phase/order/universality augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for pid in row.get('phase_structure_ids', []):
            add('phase-structure', pid, 'route', rid, 'phase-structure-condition', 'route phase-structure denominator', 'cap phase-diagram, branch, regime, vacuum-sector, or phase-transition wording when the phase row fails', effect)
        for oid in row.get('order_parameter_ids', []):
            add('order-parameter', oid, 'route', rid, 'order-parameter-condition', 'route order-parameter/diagnostic denominator', 'cap order-parameter, critical-exponent, diagnostic, benchmark, or catalog-statistic wording when the order row fails', effect)
        for uid in row.get('universality_class_ids', []):
            add('universality-class', uid, 'route', rid, 'universality-class-condition', 'route universality-class/scaling denominator', 'cap universality-class, scaling-collapse, critical-surface, fixed-point, and phase-equivalence wording when universality control fails', effect)
    for binding in bindings:
        target_id=binding.get('claim_or_oq_id',''); target_kind='claim' if target_id.startswith('CL-') else 'open-question'; effect=binding.get('maximum_authority_effect','S3') or 'S3'
        for pid in binding.get('phase_structure_ids', []):
            add('phase-structure', pid, target_kind, target_id, 'phase-structure-claim-condition', f'claim phase-structure denominator under {binding.get("binding_id")}', 'freeze phase-diagram, branch, vacuum, and phase-transition claim wording until phase rows are restored', effect)
        for oid in binding.get('order_parameter_ids', []):
            add('order-parameter', oid, target_kind, target_id, 'order-parameter-claim-condition', f'claim order-parameter denominator under {binding.get("binding_id")}', 'freeze order-parameter, critical-exponent, diagnostic, and data-collapse wording until order-parameter rows are restored', effect)
        for uid in binding.get('universality_class_ids', []):
            add('universality-class', uid, target_kind, target_id, 'universality-class-claim-condition', f'claim universality-class denominator under {binding.get("binding_id")}', 'freeze universality-class, fixed-point universality, critical-surface, and phase-equivalence wording until universality rows are restored', effect)
    graph['edge_count']=len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json phase/order/universality edges')



def augment_authority_dependency_graph_with_hilbert_representation_spectrum_edges(root: Path) -> None:
    graph=load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    rows=graph.get('edge_rows', [])
    existing={(r.get('source_kind'),r.get('source_id'),r.get('dependent_kind'),r.get('dependent_id'),r.get('dependency_kind')) for r in rows}
    def add(sk,sid,dk,did,dep,req,fail,effect):
        if not sid or not did: return
        key=(sk,sid,dk,did,dep)
        if key in existing: return
        rows.append({'edge_id':f"EDGE-{len(rows)+1:05d}",'source_kind':sk,'source_id':sid,'dependent_kind':dk,'dependent_id':did,'dependency_kind':dep,'required_for':req,'failure_effect':fail,'max_credit_transmitted':effect})
        existing.add(key)
    route_ledger=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    binding_ledger=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    for row in route_ledger.get('route_rows', []):
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','') or row.get('authority_state','')
        for hid in row.get('hilbert_space_ids', []):
            add('hilbert-space',hid,'route',rid,'hilbert-space-condition','route Hilbert/state-space denominator','freeze Hilbert-space, state-space, GNS, or Fock-sector wording when the Hilbert-space row fails',effect)
        for mid in row.get('representation_map_ids', []):
            add('representation-map',mid,'route',rid,'representation-map-condition','route representation-equivalence denominator','freeze representation-equivalence, uniqueness, or candidate-identity wording when the representation-map row fails',effect)
        for sid in row.get('spectral_reconstruction_ids', []):
            add('spectral-reconstruction',sid,'route',rid,'spectral-reconstruction-condition','route spectral-reconstruction denominator','freeze spectrum, spectral-density, spectral-geometry, and reconstruction wording when the spectral row fails',effect)
    for binding in binding_ledger.get('binding_rows', []):
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','') or 'bounded by binding row'
        for hid in binding.get('hilbert_space_ids', []):
            add('hilbert-space',hid,tk,tid,'hilbert-space-claim-condition',f'claim Hilbert/state-space denominator under {binding.get("binding_id")}', 'freeze Hilbert-space or state-space claim wording until Hilbert rows are restored', effect)
        for mid in binding.get('representation_map_ids', []):
            add('representation-map',mid,tk,tid,'representation-map-claim-condition',f'claim representation-map denominator under {binding.get("binding_id")}', 'freeze representation-equivalence or uniqueness claim wording until representation rows are restored', effect)
        for sid in binding.get('spectral_reconstruction_ids', []):
            add('spectral-reconstruction',sid,tk,tid,'spectral-reconstruction-claim-condition',f'claim spectral-reconstruction denominator under {binding.get("binding_id")}', 'freeze spectrum, spectral-density, spectral-geometry, or spectral-reconstruction claim wording until spectral rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json Hilbert/representation/spectrum edges')

def write_phase_order_universality_summary(root: Path) -> None:
    p=json.loads((root/'PHASE-STRUCTURE-LEDGER.json').read_text())
    o=json.loads((root/'ORDER-PARAMETER-LEDGER.json').read_text())
    u=json.loads((root/'UNIVERSALITY-CLASS-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    prows=p.get('phase_structure_rows', []); orows=o.get('order_parameter_rows', []); urows=u.get('universality_class_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Phase / order parameter / universality summary (generated)', '', 'Generated from `PHASE-STRUCTURE-LEDGER.json`, `ORDER-PARAMETER-LEDGER.json`, `UNIVERSALITY-CLASS-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{p.get('revision','<missing>')}`", f"- Phase-structure rows: `{len(prows)}`", f"- Order-parameter rows: `{len(orows)}`", f"- Universality-class rows: `{len(urows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Phase-structure class counts', '']
    for k,v in sorted(counts(prows,'phase_structure_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Order-parameter class counts', '']
    for k,v in sorted(counts(orows,'order_parameter_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Universality-class counts', '']
    for k,v in sorted(counts(urows,'universality_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Non-promotion rule', '', 'Phase-structure, order-parameter, and universality-class rows make phase diagram, phase transition, critical point, order parameter, critical exponent, scaling collapse, fixed point, critical surface, and universality-class language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond state-machine, public-record, observed-sector, continuum, gauge, matter, cosmology, and residual-cap limits.', '']
    (root/'docs/30-program/phase-order-universality-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/phase-order-universality-summary.generated.md')


def write_route_binding_schema_property_audit(root: Path) -> None:
    route_schema=json.loads((root/'schemas/candidate-route-state-ledger.schema.json').read_text())
    binding_schema=json.loads((root/'schemas/claim-route-binding-ledger.schema.json').read_text())
    route_item=route_schema.get('properties',{}).get('route_rows',{}).get('items',{})
    binding_item=binding_schema.get('properties',{}).get('binding_rows',{}).get('items',{})
    route_required=route_item.get('required', [])
    binding_required=binding_item.get('required', [])
    route_props=set(route_item.get('properties',{}))
    binding_props=set(binding_item.get('properties',{}))
    route_missing=[f for f in route_required if f not in route_props]
    binding_missing=[f for f in binding_required if f not in binding_props]
    lines=['# Route / binding schema property audit (generated)', '', 'Generated from `schemas/candidate-route-state-ledger.schema.json` and `schemas/claim-route-binding-ledger.schema.json`. Do not edit directly; run `make index` after changing route or binding schemas.', '', f"- Candidate-route required fields: `{len(route_required)}`", f"- Candidate-route required fields missing property declarations: `{len(route_missing)}`", f"- Claim-route binding required fields: `{len(binding_required)}`", f"- Claim-route binding required fields missing property declarations: `{len(binding_missing)}`", '', '## Rule', '', 'Required row fields should also have schema property declarations. Missing property declarations indicate that row shape is enforced only by name, leaving type and property-envelope drift harder to audit.', '']
    if route_missing:
        lines += ['## Candidate-route missing property declarations', '']
        for f in route_missing: lines.append(f'- `{f}`')
    if binding_missing:
        lines += ['## Claim-route binding missing property declarations', '']
        for f in binding_missing: lines.append(f'- `{f}`')
    (root/'docs/30-program/route-binding-schema-property-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/route-binding-schema-property-audit.generated.md')

def write_claim_route_binding_schema_field_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    schema=json.loads((root/'schemas/claim-route-binding-ledger.schema.json').read_text())
    required=set(schema.get('properties',{}).get('binding_rows',{}).get('items',{}).get('required',[]))
    fields=[]
    for fam in registry.get('registry_rows', []):
        for f in fam.get('route_fields', []):
            if f not in fields: fields.append(f)
    missing=[f for f in fields if f not in required]
    lines=['# Claim-route binding schema field audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json` and `schemas/claim-route-binding-ledger.schema.json`. Do not edit directly; run `make index` after changing route-layer families or the binding schema.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- Registered route fields checked: `{len(fields)}`", f"- Missing binding-schema required fields: `{len(missing)}`", '', '## Rule', '', 'Every registered route-support field should appear in the claim-route binding row `required` list. Missing fields indicate schema drift: claim-route binding rows may expose handles without requiring future rows to preserve them.', '']
    if missing:
        lines += ['## Missing fields', '']
        for f in missing: lines.append(f'- `{f}`')
    (root/'docs/30-program/claim-route-binding-schema-field-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/claim-route-binding-schema-field-audit.generated.md')


def write_hilbert_representation_spectrum_summary(root: Path) -> None:
    h=json.loads((root/'HILBERT-SPACE-LEDGER.json').read_text())
    r=json.loads((root/'REPRESENTATION-MAP-LEDGER.json').read_text())
    s=json.loads((root/'SPECTRAL-RECONSTRUCTION-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    hrows=h.get('hilbert_space_rows', []); rrows=r.get('representation_map_rows', []); srows=s.get('spectral_reconstruction_rows', [])
    def counts(rows,key):
        out={}
        for row in rows: out[row.get(key,'<missing>')]=out.get(row.get(key,'<missing>'),0)+1
        return out
    lines=['# Hilbert-space / representation-map / spectral-reconstruction summary (generated)', '', 'Generated from `HILBERT-SPACE-LEDGER.json`, `REPRESENTATION-MAP-LEDGER.json`, `SPECTRAL-RECONSTRUCTION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{h.get('revision','<missing>')}`", f"- Hilbert-space rows: `{len(hrows)}`", f"- Representation-map rows: `{len(rrows)}`", f"- Spectral-reconstruction rows: `{len(srows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for row in routes if row.get('authority_state') in ['S4','S5'])}`", '', '## Hilbert-space class counts', '']
    for k,v in sorted(counts(hrows,'hilbert_space_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Representation-map class counts', '']
    for k,v in sorted(counts(rrows,'representation_map_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Spectral-reconstruction class counts', '']
    for k,v in sorted(counts(srows,'spectral_reconstruction_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Non-promotion rule', '', 'Hilbert-space, representation-map, and spectral-reconstruction rows make state-space, GNS, Fock-sector, representation-equivalence, spectral-density, mass-spectrum, spectral-geometry, and spectral-reconstruction language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, public-record, observed-sector, quotient, detector, and residual-cap limits.', '']
    (root/'docs/30-program/hilbert-representation-spectrum-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/hilbert-representation-spectrum-summary.generated.md')


def write_registered_ledger_schema_property_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    failures=[]; checked=0
    lines=['# Registered-ledger schema property audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json` and registered ledger schemas. Do not edit directly; run `make index` after changing registered ledger schemas.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", '', '| Ledger | Row key | Required row fields | Missing property declarations |', '|---|---|---:|---:|']
    for fam in registry.get('registry_rows', []):
        for rel in fam.get('ledger_files', []):
            schema_rel='schemas/'+rel.lower().replace('_','-').replace('.json','.schema.json')
            p=root/schema_rel
            if not p.exists():
                failures.append((rel,'<missing-schema>','<all>'))
                lines.append(f"| `{rel}` | `<missing>` | `0` | `1` |")
                continue
            sch=json.loads(p.read_text())
            row_keys=[k for k,v in sch.get('properties',{}).items() if isinstance(v,dict) and v.get('type')=='array']
            rk=row_keys[0] if row_keys else '<missing>'
            item=sch.get('properties',{}).get(rk,{}).get('items',{}) if rk!='<missing>' else {}
            req=item.get('required', [])
            props=set(item.get('properties',{}))
            missing=[f for f in req if f not in props]
            checked += len(req)
            if missing:
                failures.append((rel,rk,','.join(missing)))
            lines.append(f"| `{rel}` | `{rk}` | `{len(req)}` | `{len(missing)}` |")
    lines += ['', f"- Registered row required fields checked: `{checked}`", f"- Missing registered row property declarations: `{len(failures)}`", '', '## Rule', '', 'Registered executable ledger row fields should not be required without schema property declarations. The audit is shape-control only; it does not create scientific support.', '']
    if failures:
        lines += ['## Failures', '']
        for rel,rk,miss in failures: lines.append(f'- `{rel}` / `{rk}` missing `{miss}`')
    (root/'docs/30-program/registered-ledger-schema-property-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/registered-ledger-schema-property-audit.generated.md')


def augment_authority_dependency_graph_with_defect_instanton_vacuum_decay_edges(root: Path) -> None:
    """Add topological-defect / instanton-saddle / vacuum-decay-tunneling edges."""
    graph_path=root/'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph=load_authority_graph(graph_path)
    graph['generation_rule']=graph.get('generation_rule','') + ' Defect / instanton / vacuum-decay edges are appended by the rev0299 nonperturbative-sector augmentation pass.'
    rows=graph.get('edge_rows', [])
    existing={(r.get('source_kind'),r.get('source_id'),r.get('dependent_kind'),r.get('dependent_id'),r.get('dependency_kind')) for r in rows}
    def next_edge_id(): return f"EDGE-{len(rows)+1:05d}"
    def add(sk,sid,dk,did,kind,req,fail,effect):
        if not sid or not did: return
        key=(sk,sid,dk,did,kind)
        if key in existing: return
        rows.append({'edge_id':next_edge_id(),'source_kind':sk,'source_id':sid,'dependent_kind':dk,'dependent_id':did,'dependency_kind':kind,'required_for':req,'failure_effect':fail,'max_credit_transmitted':effect})
        existing.add(key)
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in routes:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling') or row.get('authority_state','')
        for did in row.get('topological_defect_ids', []): add('topological-defect',did,'route',rid,'topological-defect-condition','route topological-defect/sector denominator','cap defect, soliton, brane, wall, string, flux, or topological-sector wording when defect control fails',effect)
        for sid in row.get('instanton_saddle_ids', []): add('instanton-saddle',sid,'route',rid,'instanton-saddle-condition','route instanton/saddle/nonperturbative denominator','cap instanton, Euclidean-saddle, replica-saddle, bounce, transseries, or nonperturbative-correction wording when saddle control fails',effect)
        for vid in row.get('vacuum_decay_tunneling_ids', []): add('vacuum-decay-tunneling',vid,'route',rid,'vacuum-decay-tunneling-condition','route vacuum-decay/tunneling/metastability denominator','cap vacuum-selection, false-vacuum, metastability, bounce-rate, and tunneling-channel wording when decay control fails',effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','') or 'bounded by binding row'
        for did in binding.get('topological_defect_ids', []): add('topological-defect',did,tk,tid,'topological-defect-claim-condition',f'claim topological-defect denominator under {binding.get("binding_id")}', 'freeze defect/soliton/brane/topological-sector claim wording until defect rows are restored', effect)
        for sid in binding.get('instanton_saddle_ids', []): add('instanton-saddle',sid,tk,tid,'instanton-saddle-claim-condition',f'claim instanton/saddle denominator under {binding.get("binding_id")}', 'freeze instanton/saddle/bounce/transseries claim wording until saddle rows are restored', effect)
        for vid in binding.get('vacuum_decay_tunneling_ids', []): add('vacuum-decay-tunneling',vid,tk,tid,'vacuum-decay-tunneling-claim-condition',f'claim vacuum-decay/tunneling denominator under {binding.get("binding_id")}', 'freeze vacuum-decay/metastability/tunneling-rate claim wording until decay rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json defect/instanton/vacuum-decay edges')

def write_defect_instanton_vacuum_decay_summary(root: Path) -> None:
    d=json.loads((root/'TOPOLOGICAL-DEFECT-LEDGER.json').read_text())
    i=json.loads((root/'INSTANTON-SADDLE-LEDGER.json').read_text())
    v=json.loads((root/'VACUUM-DECAY-TUNNELING-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    drows=d.get('topological_defect_rows', []); irows=i.get('instanton_saddle_rows', []); vrows=v.get('vacuum_decay_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Defect / instanton / vacuum-decay summary (generated)', '', 'Generated from `TOPOLOGICAL-DEFECT-LEDGER.json`, `INSTANTON-SADDLE-LEDGER.json`, `VACUUM-DECAY-TUNNELING-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{d.get('revision','<missing>')}`", f"- Topological-defect rows: `{len(drows)}`", f"- Instanton/saddle rows: `{len(irows)}`", f"- Vacuum-decay/tunneling rows: `{len(vrows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Topological-defect class counts', '']
    for k,val in sorted(counts(drows,'topological_defect_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Instanton/saddle class counts', '']
    for k,val in sorted(counts(irows,'instanton_saddle_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Vacuum-decay/tunneling class counts', '']
    for k,val in sorted(counts(vrows,'vacuum_decay_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Non-promotion rule', '', 'Topological-defect, instanton/saddle, and vacuum-decay/tunneling rows make defects, solitons, walls, cosmic strings, branes, fluxes, instantons, Euclidean saddles, bounces, transseries sectors, false-vacuum decay, metastability, and tunneling-rate language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, public-record, topology/signature, matter/cosmology, observed-sector, and residual-cap limits.', '']
    (root/'docs/30-program/defect-instanton-vacuum-decay-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/defect-instanton-vacuum-decay-summary.generated.md')


def augment_authority_dependency_graph_with_compactification_moduli_swampland_edges(root: Path) -> None:
    """Add compactification-geometry / moduli-stabilization / swampland-compatibility edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Compactification-geometry / moduli-stabilization / swampland-compatibility edges are appended by the rev0300 compactification/moduli/swampland augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id: return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing: return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for cid in row.get('compactification_geometry_ids', []): add('compactification-geometry',cid,'route',rid,'compactification-geometry-condition','route compactification/internal-geometry denominator','cap compactification, dimensional-reduction, internal-geometry, landscape, or observed-world-selection wording when compactification geometry control fails',effect)
        for mid in row.get('moduli_stabilization_ids', []): add('moduli-stabilization',mid,'route',rid,'moduli-stabilization-condition','route moduli/vacuum-parameter stabilization denominator','cap moduli-stabilized, vacuum-selected, parameter-fixed, de Sitter/uplift, or low-energy-prediction wording when stabilization control fails',effect)
        for sid in row.get('swampland_compatibility_ids', []): add('swampland-compatibility',sid,'route',rid,'swampland-compatibility-condition','route swampland/landscape compatibility denominator','cap swampland-safe, landscape-member, WGC/distance/tower/de Sitter/tadpole, or UV-completion wording when compatibility control fails',effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','S3')
        for cid in binding.get('compactification_geometry_ids', []): add('compactification-geometry',cid,tk,tid,'compactification-geometry-claim-condition',f'claim compactification-geometry denominator under {binding.get("binding_id")}', 'freeze compactification/dimensional-reduction/vacuum-geometry claim wording until geometry rows are restored', effect)
        for mid in binding.get('moduli_stabilization_ids', []): add('moduli-stabilization',mid,tk,tid,'moduli-stabilization-claim-condition',f'claim moduli-stabilization denominator under {binding.get("binding_id")}', 'freeze moduli-stabilized/vacuum-selected/de Sitter/uplift claim wording until stabilization rows are restored', effect)
        for sid in binding.get('swampland_compatibility_ids', []): add('swampland-compatibility',sid,tk,tid,'swampland-compatibility-claim-condition',f'claim swampland-compatibility denominator under {binding.get("binding_id")}', 'freeze swampland-safe/landscape-member/UV-completion claim wording until compatibility rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json compactification/moduli/swampland edges')


def write_compactification_moduli_swampland_summary(root: Path) -> None:
    c=json.loads((root/'COMPACTIFICATION-GEOMETRY-LEDGER.json').read_text())
    m=json.loads((root/'MODULI-STABILIZATION-LEDGER.json').read_text())
    s=json.loads((root/'SWAMPLAND-COMPATIBILITY-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    crows=c.get('compactification_geometry_rows', []); mrows=m.get('moduli_stabilization_rows', []); srows=s.get('swampland_compatibility_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Compactification / moduli / swampland summary (generated)', '', 'Generated from `COMPACTIFICATION-GEOMETRY-LEDGER.json`, `MODULI-STABILIZATION-LEDGER.json`, `SWAMPLAND-COMPATIBILITY-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{c.get('revision','<missing>')}`", f"- Compactification-geometry rows: `{len(crows)}`", f"- Moduli-stabilization rows: `{len(mrows)}`", f"- Swampland-compatibility rows: `{len(srows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Compactification class counts', '']
    for k,val in sorted(counts(crows,'compactification_geometry_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Moduli-stabilization class counts', '']
    for k,val in sorted(counts(mrows,'moduli_stabilization_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Swampland/landscape compatibility class counts', '']
    for k,val in sorted(counts(srows,'swampland_compatibility_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Non-promotion rule', '', 'Compactification-geometry, moduli-stabilization, and swampland/landscape compatibility rows make compactification, internal geometry, moduli, flux, de Sitter, distance/tower, WGC, tadpole, landscape, swampland, and vacuum-selection language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, public-record, matter/cosmology, observed-sector, and residual-cap limits.', '']
    (root/'docs/30-program/compactification-moduli-swampland-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/compactification-moduli-swampland-summary.generated.md')


def write_ledger_family_registry_schema_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    schema=json.loads((root/'schemas/ledger-family-registry.schema.json').read_text())
    item=schema.get('properties',{}).get('registry_rows',{}).get('items',{})
    required=set(item.get('required', [])); props=item.get('properties', {})
    required_envelope=['family_id','introduced_revision','ledger_files','schema_files','route_fields','open_question_id','cardinality_policy','maximum_route_field_cardinality','generated_summary','audit_note']
    failures=[]
    for field in required_envelope:
        if field not in required: failures.append(f'schema does not require `{field}`')
        if field not in props: failures.append(f'schema does not declare property `{field}`')
    for row in registry.get('registry_rows', []):
        fid=row.get('family_id','<missing>')
        for field in required_envelope:
            val=row.get(field)
            if val in (None, '', []): failures.append(f'`{fid}` missing or empty `{field}`')
        if row.get('cardinality_policy') == 'route-local-plus-wrapper' and row.get('maximum_route_field_cardinality') != 2:
            failures.append(f'`{fid}` route-local-plus-wrapper family must declare maximum_route_field_cardinality 2')
    lines=['# Ledger-family registry schema audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json` and `schemas/ledger-family-registry.schema.json`. Do not edit directly; run `make index` after changing registry fields.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- Registry envelope failures: `{len(failures)}`", '', '## Required registry-row envelope', '']
    for field in required_envelope: lines.append(f'- `{field}`')
    if failures:
        lines += ['', '## Failures', '']
        lines += [f'- {f}' for f in failures]
    lines += ['', '## Audit rule', '', 'The ledger-family registry owns the route-support stack. Every family row must expose ledgers, schemas, route fields, an OQ gate, cardinality policy, generated summary path, and audit note. Missing registry metadata can hide a support layer from summaries, bindings, gates, or cardinality checks even when individual ledgers are valid.', '']
    (root/'docs/30-program/ledger-family-registry-schema-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/ledger-family-registry-schema-audit.generated.md')


def write_route_binding_schema_array_type_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    route_schema=json.loads((root/'schemas/candidate-route-state-ledger.schema.json').read_text())
    binding_schema=json.loads((root/'schemas/claim-route-binding-ledger.schema.json').read_text())
    route_props=route_schema.get('properties',{}).get('route_rows',{}).get('items',{}).get('properties',{})
    binding_props=binding_schema.get('properties',{}).get('binding_rows',{}).get('items',{}).get('properties',{})
    fields=[]
    for fam in registry.get('registry_rows', []):
        for f in fam.get('route_fields', []):
            if f not in fields: fields.append(f)
    def ok(prop): return isinstance(prop,dict) and prop.get('type')=='array' and isinstance(prop.get('items'),dict) and prop['items'].get('type')=='string'
    failures=[]
    for f in fields:
        if not ok(route_props.get(f)): failures.append(('candidate-route',f))
        if not ok(binding_props.get(f)): failures.append(('claim-route-binding',f))
    lines=['# Route / binding schema array-type audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json`, `schemas/candidate-route-state-ledger.schema.json`, and `schemas/claim-route-binding-ledger.schema.json`. Do not edit directly; run `make index` after changing route-layer fields or schemas.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- Registered route fields checked: `{len(fields)}`", f"- Array-type property failures: `{len(failures)}`", '', '## Rule', '', 'Every registered route-support field must be a schema property with `type: array` and `items.type: string` in both candidate-route rows and claim-route binding rows. Route-layer handles are lists of stable IDs, not untyped JSON payloads.', '']
    if failures:
        lines += ['## Failures','']
        for surface,field in failures: lines.append(f'- `{surface}` / `{field}`')
    (root/'docs/30-program/route-binding-schema-array-type-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/route-binding-schema-array-type-audit.generated.md')


def augment_authority_dependency_graph_with_lorentz_cpt_spin_edges(root: Path) -> None:
    """Add Lorentz-covariance / spin-statistics / CPT-discrete-symmetry edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Lorentz-covariance / spin-statistics / CPT-discrete-symmetry edges are appended by the rev0301 Lorentz/CPT/spin-statistics augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for lid in row.get('lorentz_covariance_ids', []):
            add('lorentz-covariance', lid, 'route', rid, 'lorentz-covariance-condition', 'route Lorentz/Poincare/local-frame covariance denominator', 'cap Lorentz-covariant, Lorentz-violation, SME-compatible, dispersion, preferred-frame, or local-frame wording when Lorentz covariance control fails', effect)
        for sid in row.get('spin_statistics_ids', []):
            add('spin-statistics', sid, 'route', rid, 'spin-statistics-condition', 'route spin/statistics theorem-assumption denominator', 'cap spin, helicity, exchange, statistics, particle-statistics, and spin-statistics theorem wording when spin-statistics control fails', effect)
        for cid in row.get('cpt_discrete_symmetry_ids', []):
            add('cpt-discrete-symmetry', cid, 'route', rid, 'cpt-discrete-symmetry-condition', 'route CPT/discrete-symmetry denominator', 'cap CPT, CP/T/parity, antimatter, crossing-CPT, and discrete-symmetry wording when CPT/discrete-symmetry control fails', effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','S3')
        for lid in binding.get('lorentz_covariance_ids', []):
            add('lorentz-covariance', lid, tk, tid, 'lorentz-covariance-claim-condition', f'claim Lorentz-covariance denominator under {binding.get("binding_id")}', 'freeze Lorentz/Poincare/local-frame/SME claim wording until Lorentz rows are restored', effect)
        for sid in binding.get('spin_statistics_ids', []):
            add('spin-statistics', sid, tk, tid, 'spin-statistics-claim-condition', f'claim spin-statistics denominator under {binding.get("binding_id")}', 'freeze spin/helicity/statistics/spin-statistics claim wording until spin-statistics rows are restored', effect)
        for cid in binding.get('cpt_discrete_symmetry_ids', []):
            add('cpt-discrete-symmetry', cid, tk, tid, 'cpt-discrete-symmetry-claim-condition', f'claim CPT/discrete-symmetry denominator under {binding.get("binding_id")}', 'freeze CPT/CP/T/parity/antimatter/discrete-symmetry claim wording until CPT rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json Lorentz/CPT/spin-statistics edges')


def write_lorentz_cpt_spin_statistics_summary(root: Path) -> None:
    l=json.loads((root/'LORENTZ-COVARIANCE-LEDGER.json').read_text())
    s=json.loads((root/'SPIN-STATISTICS-LEDGER.json').read_text())
    c=json.loads((root/'CPT-DISCRETE-SYMMETRY-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    lrows=l.get('lorentz_covariance_rows', []); srows=s.get('spin_statistics_rows', []); crows=c.get('cpt_discrete_symmetry_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Lorentz / CPT / spin-statistics summary (generated)', '', 'Generated from `LORENTZ-COVARIANCE-LEDGER.json`, `SPIN-STATISTICS-LEDGER.json`, `CPT-DISCRETE-SYMMETRY-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{l.get('revision','<missing>')}`", f"- Lorentz-covariance rows: `{len(lrows)}`", f"- Spin-statistics rows: `{len(srows)}`", f"- CPT/discrete-symmetry rows: `{len(crows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Lorentz-covariance class counts', '']
    for k,val in sorted(counts(lrows,'lorentz_covariance_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Spin-statistics class counts', '']
    for k,val in sorted(counts(srows,'spin_statistics_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## CPT/discrete-symmetry class counts', '']
    for k,val in sorted(counts(crows,'cpt_discrete_symmetry_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Non-promotion rule', '', 'Lorentz-covariance, spin-statistics, and CPT/discrete-symmetry rows make Lorentz, Poincare, local-frame, dispersion, SME, spin, helicity, exchange, statistics, CPT, CP/T/parity, antimatter, and discrete-symmetry language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, public-record, matter/cosmology, classical-GR, viability, and observed-sector limits.', '']
    (root/'docs/30-program/lorentz-cpt-spin-statistics-summary.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/lorentz-cpt-spin-statistics-summary.generated.md')



def augment_authority_dependency_graph_with_locality_microcausality_cluster_edges(root: Path) -> None:
    """Add microcausality/locality, cluster-decomposition, and local-QFT recovery edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Microcausality/locality, cluster-decomposition, and local-QFT-recovery edges are appended by the rev0302 locality augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for mid in row.get('microcausality_locality_ids', []):
            add('microcausality-locality', mid, 'route', rid, 'microcausality-locality-condition', 'route locality/microcausality denominator', 'cap locality, local-commutativity, no-signalling, detector-locality, and local-algebra wording when microcausality/locality control fails', effect)
        for cid in row.get('cluster_decomposition_ids', []):
            add('cluster-decomposition', cid, 'route', rid, 'cluster-decomposition-condition', 'route cluster-decomposition/isolability denominator', 'cap cluster, isolability, factorization, and independent-experiment wording when cluster control fails', effect)
        for qid in row.get('local_qft_recovery_ids', []):
            add('local-qft-recovery', qid, 'route', rid, 'local-qft-recovery-condition', 'route local-QFT recovery denominator', 'cap local-QFT, AQFT/net, Wightman/OS/factorization, and relativistic-QFT recovery wording when local-QFT recovery control fails', effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','S3')
        for mid in binding.get('microcausality_locality_ids', []):
            add('microcausality-locality', mid, tk, tid, 'microcausality-locality-claim-condition', f'claim locality/microcausality denominator under {binding.get("binding_id")}', 'freeze locality/no-signalling/local-algebra claim wording until microcausality/locality rows are restored', effect)
        for cid in binding.get('cluster_decomposition_ids', []):
            add('cluster-decomposition', cid, tk, tid, 'cluster-decomposition-claim-condition', f'claim cluster-decomposition denominator under {binding.get("binding_id")}', 'freeze cluster/isolability/factorization claim wording until cluster rows are restored', effect)
        for qid in binding.get('local_qft_recovery_ids', []):
            add('local-qft-recovery', qid, tk, tid, 'local-qft-recovery-claim-condition', f'claim local-QFT recovery denominator under {binding.get("binding_id")}', 'freeze local-QFT recovery and candidate-native local-observable wording until local-QFT rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json locality/microcausality/cluster edges')


def write_locality_microcausality_cluster_summary(root: Path) -> None:
    m=json.loads((root/'MICROCAUSALITY-LOCALITY-LEDGER.json').read_text())
    c=json.loads((root/'CLUSTER-DECOMPOSITION-LEDGER.json').read_text())
    q=json.loads((root/'LOCAL-QFT-RECOVERY-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    mrows=m.get('microcausality_locality_rows', []); crows=c.get('cluster_decomposition_rows', []); qrows=q.get('local_qft_recovery_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Locality / microcausality / cluster-decomposition summary (generated)', '', 'Generated from `MICROCAUSALITY-LOCALITY-LEDGER.json`, `CLUSTER-DECOMPOSITION-LEDGER.json`, `LOCAL-QFT-RECOVERY-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{m.get('revision','<missing>')}`", f"- Microcausality/locality rows: `{len(mrows)}`", f"- Cluster-decomposition rows: `{len(crows)}`", f"- Local-QFT-recovery rows: `{len(qrows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Microcausality/locality class counts', '']
    for k,val in sorted(counts(mrows,'microcausality_locality_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Cluster-decomposition class counts', '']
    for k,val in sorted(counts(crows,'cluster_decomposition_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Local-QFT-recovery class counts', '']
    for k,val in sorted(counts(qrows,'local_qft_recovery_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Non-promotion rule', '', 'Microcausality/locality, cluster-decomposition, and local-QFT-recovery rows make local-commutativity, no-signalling, detector locality, local-algebra, cluster, isolability, factorization, AQFT/net, Wightman/OS, and local-QFT recovery language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, public-record, matter/cosmology, classical-GR, quantum-record, and observed-sector limits.', '']
    (root/'docs/30-program/locality-microcausality-cluster-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/locality-microcausality-cluster-summary.generated.md')



def augment_authority_dependency_graph_with_entanglement_modular_relative_entropy_edges(root: Path) -> None:
    """Add entanglement-structure, modular-flow, and relative-entropy/recovery edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Entanglement-structure / modular-flow / relative-entropy-recovery edges are appended by the rev0303 entanglement augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for eid in row.get('entanglement_structure_ids', []):
            add('entanglement-structure', eid, 'route', rid, 'entanglement-structure-condition', 'route entanglement / wedge / entropy denominator', 'cap entanglement, area-law, RT/HRT/QES, entanglement-wedge, and geometry-from-entanglement wording when entanglement-structure control fails', effect)
        for mid in row.get('modular_flow_ids', []):
            add('modular-flow', mid, 'route', rid, 'modular-flow-condition', 'route modular Hamiltonian / modular-flow denominator', 'cap modular Hamiltonian, modular flow, emergent-time, and algebraic-flow wording when modular-flow control fails', effect)
        for rid2 in row.get('relative_entropy_recovery_ids', []):
            add('relative-entropy-recovery', rid2, 'route', rid, 'relative-entropy-recovery-condition', 'route relative-entropy / recovery-map denominator', 'cap JLMS, relative-entropy equality, Petz/recovery, monotonicity, and entanglement-wedge reconstruction wording when recovery control fails', effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','S3')
        for eid in binding.get('entanglement_structure_ids', []):
            add('entanglement-structure', eid, tk, tid, 'entanglement-structure-claim-condition', f'claim entanglement denominator under {binding.get("binding_id")}', 'freeze entanglement, area-law, RT/HRT/QES, or geometry-from-entanglement claim wording until entanglement rows are restored', effect)
        for mid in binding.get('modular_flow_ids', []):
            add('modular-flow', mid, tk, tid, 'modular-flow-claim-condition', f'claim modular-flow denominator under {binding.get("binding_id")}', 'freeze modular-Hamiltonian, modular-flow, emergent-time, or algebraic-flow claim wording until modular rows are restored', effect)
        for rid2 in binding.get('relative_entropy_recovery_ids', []):
            add('relative-entropy-recovery', rid2, tk, tid, 'relative-entropy-recovery-claim-condition', f'claim relative-entropy/recovery denominator under {binding.get("binding_id")}', 'freeze JLMS, relative-entropy, recovery-map, and entanglement-wedge reconstruction claim wording until recovery rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json entanglement/modular/relative-entropy edges')


def write_entanglement_modular_relative_entropy_summary(root: Path) -> None:
    e=json.loads((root/'ENTANGLEMENT-STRUCTURE-LEDGER.json').read_text())
    m=json.loads((root/'MODULAR-FLOW-LEDGER.json').read_text())
    r=json.loads((root/'RELATIVE-ENTROPY-RECOVERY-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    erows=e.get('entanglement_structure_rows', []); mrows=m.get('modular_flow_rows', []); rrows=r.get('relative_entropy_recovery_rows', [])
    def counts(rows,key):
        out={}
        for row in rows: out[row.get(key,'<missing>')]=out.get(row.get(key,'<missing>'),0)+1
        return out
    lines=['# Entanglement / modular-flow / relative-entropy summary (generated)', '', 'Generated from `ENTANGLEMENT-STRUCTURE-LEDGER.json`, `MODULAR-FLOW-LEDGER.json`, `RELATIVE-ENTROPY-RECOVERY-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{e.get('revision','<missing>')}`", f"- Entanglement-structure rows: `{len(erows)}`", f"- Modular-flow rows: `{len(mrows)}`", f"- Relative-entropy/recovery rows: `{len(rrows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for row in routes if row.get('authority_state') in ['S4','S5'])}`", '', '## Entanglement-structure class counts', '']
    for k,val in sorted(counts(erows,'entanglement_structure_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Modular-flow class counts', '']
    for k,val in sorted(counts(mrows,'modular_flow_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Relative-entropy/recovery class counts', '']
    for k,val in sorted(counts(rrows,'relative_entropy_recovery_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Non-promotion rule', '', 'Entanglement-structure, modular-flow, and relative-entropy/recovery rows make entanglement-wedge, RT/HRT/QES, geometry-from-entanglement, modular-Hamiltonian, modular-flow, JLMS, Petz/recovery, and holographic-completeness language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, public-record, subsystem, information/no-go, black-hole, local-QFT, quantization, and observed-sector limits.', '']
    (root/'docs/30-program/entanglement-modular-relative-entropy-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/entanglement-modular-relative-entropy-summary.generated.md')



def augment_authority_dependency_graph_with_qec_logical_decoder_edges(root: Path) -> None:
    """Add QEC code-subspace, logical-operator reconstruction, and decoder-certification edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' QEC-code-subspace / logical-operator-reconstruction / decoder-certification edges are appended by the rev0304 QEC augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for qid in row.get('qec_code_subspace_ids', []):
            add('qec-code-subspace', qid, 'route', rid, 'qec-code-subspace-condition', 'route QEC code-subspace / correctable-region denominator', 'cap QEC, code-subspace, erasure-correction, and correctable-region wording when code-subspace control fails', effect)
        for lid in row.get('logical_operator_reconstruction_ids', []):
            add('logical-operator-reconstruction', lid, 'route', rid, 'logical-operator-reconstruction-condition', 'route logical-operator reconstruction denominator', 'cap logical-operator, encoded-observable, multi-region reconstruction, and dictionary wording when logical reconstruction control fails', effect)
        for did in row.get('decoder_certification_ids', []):
            add('decoder-certification', did, 'route', rid, 'decoder-certification-condition', 'route decoder / recovery-map certification denominator', 'cap decoder, recovery-map, fidelity, benchmark, and holographic-QEC wording when decoder certification fails', effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','S3')
        for qid in binding.get('qec_code_subspace_ids', []):
            add('qec-code-subspace', qid, tk, tid, 'qec-code-subspace-claim-condition', f'claim QEC code-subspace denominator under {binding.get("binding_id")}', 'freeze QEC/code-subspace claim wording until QEC rows are restored', effect)
        for lid in binding.get('logical_operator_reconstruction_ids', []):
            add('logical-operator-reconstruction', lid, tk, tid, 'logical-operator-reconstruction-claim-condition', f'claim logical-operator denominator under {binding.get("binding_id")}', 'freeze logical-operator/reconstruction claim wording until logical rows are restored', effect)
        for did in binding.get('decoder_certification_ids', []):
            add('decoder-certification', did, tk, tid, 'decoder-certification-claim-condition', f'claim decoder-certification denominator under {binding.get("binding_id")}', 'freeze decoder/recovery-map/fidelity claim wording until decoder rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json QEC/logical/decoder edges')


def write_qec_logical_decoder_summary(root: Path) -> None:
    q=json.loads((root/'QEC-CODE-SUBSPACE-LEDGER.json').read_text())
    l=json.loads((root/'LOGICAL-OPERATOR-RECONSTRUCTION-LEDGER.json').read_text())
    d=json.loads((root/'DECODER-CERTIFICATION-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    qrows=q.get('qec_code_subspace_rows', []); lrows=l.get('logical_operator_reconstruction_rows', []); drows=d.get('decoder_certification_rows', [])
    def counts(rows,key):
        out={}
        for row in rows: out[row.get(key,'<missing>')]=out.get(row.get(key,'<missing>'),0)+1
        return out
    lines=['# QEC / logical-operator / decoder summary (generated)', '', 'Generated from `QEC-CODE-SUBSPACE-LEDGER.json`, `LOGICAL-OPERATOR-RECONSTRUCTION-LEDGER.json`, `DECODER-CERTIFICATION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{q.get('revision','<missing>')}`", f"- QEC code-subspace rows: `{len(qrows)}`", f"- Logical-operator reconstruction rows: `{len(lrows)}`", f"- Decoder-certification rows: `{len(drows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for row in routes if row.get('authority_state') in ['S4','S5'])}`", '', '## QEC code-subspace class counts', '']
    for k,val in sorted(counts(qrows,'qec_code_subspace_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Logical-operator reconstruction class counts', '']
    for k,val in sorted(counts(lrows,'logical_operator_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Decoder-certification class counts', '']
    for k,val in sorted(counts(drows,'decoder_certification_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Non-promotion rule', '', 'QEC code-subspace, logical-operator reconstruction, and decoder-certification rows make code-subspace, correctable-region, erasure-correction, logical-operator, recovery-map, decoder, fidelity, benchmark, and holographic-QEC language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, public-record, subsystem, information/no-go, entanglement, black-hole, local-QFT, quantum-record, and observed-sector limits.', '']
    (root/'docs/30-program/qec-logical-decoder-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/qec-logical-decoder-summary.generated.md')




def augment_authority_dependency_graph_with_complexity_resource_edges(root: Path) -> None:
    """Add circuit-complexity, holographic-complexity, and computational-hardness edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Circuit-complexity / holographic-complexity / computational-hardness edges are appended by the rev0305 complexity-resource augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for cid in row.get('circuit_complexity_ids', []):
            add('circuit-complexity', cid, 'route', rid, 'circuit-complexity-condition', 'route circuit-complexity / cost-metric denominator', 'cap circuit-cost, complexity-growth, and resource-bound wording when circuit-complexity control fails', effect)
        for hid in row.get('holographic_complexity_ids', []):
            add('holographic-complexity', hid, 'route', rid, 'holographic-complexity-condition', 'route holographic-complexity / bulk functional denominator', 'cap complexity=volume/action, WDW-patch, and black-hole-interior wording when holographic-complexity control fails', effect)
        for did in row.get('computational_hardness_ids', []):
            add('computational-hardness', did, 'route', rid, 'computational-hardness-condition', 'route computational-hardness / verifier denominator', 'cap hardness, intractability, decoder-hardness, and observer-limitation wording when computational-hardness control fails', effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','S3')
        for cid in binding.get('circuit_complexity_ids', []):
            add('circuit-complexity', cid, tk, tid, 'circuit-complexity-claim-condition', f'claim circuit-complexity denominator under {binding.get("binding_id")}', 'freeze circuit-complexity claim wording until circuit rows are restored', effect)
        for hid in binding.get('holographic_complexity_ids', []):
            add('holographic-complexity', hid, tk, tid, 'holographic-complexity-claim-condition', f'claim holographic-complexity denominator under {binding.get("binding_id")}', 'freeze holographic-complexity claim wording until holographic rows are restored', effect)
        for did in binding.get('computational_hardness_ids', []):
            add('computational-hardness', did, tk, tid, 'computational-hardness-claim-condition', f'claim computational-hardness denominator under {binding.get("binding_id")}', 'freeze computational-hardness claim wording until hardness rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json complexity-resource edges')


def write_circuit_holographic_complexity_summary(root: Path) -> None:
    c=json.loads((root/'CIRCUIT-COMPLEXITY-LEDGER.json').read_text())
    h=json.loads((root/'HOLOGRAPHIC-COMPLEXITY-LEDGER.json').read_text())
    d=json.loads((root/'COMPUTATIONAL-HARDNESS-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    crows=c.get('circuit_complexity_rows', []); hrows=h.get('holographic_complexity_rows', []); drows=d.get('computational_hardness_rows', [])
    def counts(rows,key):
        out={}
        for row in rows: out[row.get(key,'<missing>')]=out.get(row.get(key,'<missing>'),0)+1
        return out
    lines=['# Circuit / holographic complexity / computational-hardness summary (generated)', '', 'Generated from `CIRCUIT-COMPLEXITY-LEDGER.json`, `HOLOGRAPHIC-COMPLEXITY-LEDGER.json`, `COMPUTATIONAL-HARDNESS-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{c.get('revision','<missing>')}`", f"- Circuit-complexity rows: `{len(crows)}`", f"- Holographic-complexity rows: `{len(hrows)}`", f"- Computational-hardness rows: `{len(drows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for row in routes if row.get('authority_state') in ['S4','S5'])}`", '', '## Circuit-complexity class counts', '']
    for k,val in sorted(counts(crows,'circuit_complexity_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Holographic-complexity class counts', '']
    for k,val in sorted(counts(hrows,'holographic_complexity_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Computational-hardness class counts', '']
    for k,val in sorted(counts(drows,'computational_hardness_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Non-promotion rule', '', 'Circuit-complexity, holographic-complexity, and computational-hardness rows make circuit-cost, cost-geometry, complexity growth, complexity=volume/action, WDW-patch, black-hole-interior, decoder-hardness, and intractability language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, public-record, QEC/logical/decoder, entanglement, black-hole, computational-artifact, and observed-sector limits.', '']
    (root/'docs/30-program/circuit-holographic-complexity-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/circuit-holographic-complexity-summary.generated.md')


def write_claim_route_controlling_ledger_order_audit(root: Path) -> None:
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    failures=[]; rows=[]
    for binding in bindings:
        bid=binding.get('binding_id','<missing>')
        ledgers=binding.get('controlling_ledgers', [])
        duplicates=sorted({x for x in ledgers if ledgers.count(x)>1})
        unknown=[x for x in ledgers if not (root/x).exists()]
        stable=list(dict.fromkeys(ledgers))==ledgers
        rows.append((bid,len(ledgers),len(duplicates),len(unknown),stable))
        if duplicates or unknown or not stable:
            failures.append((bid,duplicates,unknown,stable))
    lines=['# Claim-route controlling-ledger order audit (generated)', '', 'Generated from `CLAIM-ROUTE-BINDING-LEDGER.json`. Do not edit directly; run `make index` after changing binding rows.', '', f"- Claim-route binding rows: `{len(bindings)}`", f"- Duplicate controlling-ledger failures: `{sum(1 for _,_,d,_,_ in rows if d)}`", f"- Unknown controlling-ledger failures: `{sum(1 for _,_,_,u,_ in rows if u)}`", f"- Order-stability failures: `{sum(1 for *_,stable in rows if not stable)}`", f"- Total controlling-ledger audit failures: `{len(failures)}`", '', '| Binding | Controlling ledgers | Duplicate count | Unknown count | Stable order |', '|---|---:|---:|---:|---:|']
    for bid,count,dup,unk,stable in rows:
        lines.append(f"| `{bid}` | `{count}` | `{dup}` | `{unk}` | `{str(stable).lower()}` |")
    if failures:
        lines += ['', '## Failures', '']
        for bid,dups,unknown,stable in failures:
            lines.append(f"- `{bid}` duplicates={dups} unknown={unknown} stable={stable}")
    (root/'docs/30-program/claim-route-controlling-ledger-order-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/claim-route-controlling-ledger-order-audit.generated.md')

def write_registered_source_kind_coverage_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    graph=load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    source_kinds={edge.get('source_kind') for edge in graph.get('edge_rows', [])}
    def source_kind_from_ledger(rel: str) -> str:
        overrides={'DOMAIN-OF-VALIDITY-LEDGER.json':'validity-domain','PREDICTIVE-GENERALIZATION-LEDGER.json':'generalization-validation'}
        if rel in overrides: return overrides[rel]
        name=rel.replace('.json','').lower()
        if name.endswith('-ledger'): name=name[:-7]
        return name
    rows=[]; failures=[]
    for fam in registry.get('registry_rows', []):
        if fam.get('cardinality_policy') != 'route-local-plus-wrapper':
            continue
        for ledger in fam.get('ledger_files', []):
            kind=source_kind_from_ledger(ledger)
            present=kind in source_kinds
            rows.append((fam.get('family_id','<missing>'), ledger, kind, present))
            if not present:
                failures.append((fam.get('family_id','<missing>'), ledger, kind))
    lines=['# Registered source-kind coverage audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json` and `AUTHORITY-DEPENDENCY-GRAPH.json`. Do not edit directly; run `make index` after changing route-support families or graph generation.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Route-local-plus-wrapper families checked: `{len(set(f for f,_,_,_ in rows))}`", f"- Ledger source kinds checked: `{len(rows)}`", f"- Source-kind coverage failures: `{len(failures)}`", '', '| Family | Ledger | Expected source kind | Present in graph |', '|---|---|---|---:|']
    for fam, ledger, kind, present in rows:
        lines.append(f"| `{fam}` | `{ledger}` | `{kind}` | `{str(present).lower()}` |")
    if failures:
        lines += ['', '## Failures', '']
        for fam, ledger, kind in failures:
            lines.append(f"- `{fam}` / `{ledger}` expected source kind `{kind}`")
    (root/'docs/30-program/registered-source-kind-coverage-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/registered-source-kind-coverage-audit.generated.md')


def write_registered_dependency_edge_coverage_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    graph=load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    edges={(e.get('source_kind'), e.get('source_id'), e.get('dependent_kind'), e.get('dependent_id')) for e in graph.get('edge_rows', [])}
    failures=[]; checked=0
    def source_kind_from_ledger(rel: str) -> str:
        overrides={
            'DOMAIN-OF-VALIDITY-LEDGER.json':'validity-domain',
            'PREDICTIVE-GENERALIZATION-LEDGER.json':'generalization-validation',
        }
        if rel in overrides:
            return overrides[rel]
        name=rel.replace('.json','').lower()
        if name.endswith('-ledger'): name=name[:-7]
        return name
    for fam in registry.get('registry_rows', []):
        if fam.get('cardinality_policy') != 'route-local-plus-wrapper':
            continue
        fields=fam.get('route_fields', [])
        ledgers=fam.get('ledger_files', [])
        if len(fields) != len(ledgers):
            failures.append((fam.get('family_id','<missing>'), '<family>', 'field/ledger length mismatch', f'{len(fields)} fields / {len(ledgers)} ledgers'))
            continue
        for field, ledger_rel in zip(fields, ledgers):
            source_kind=source_kind_from_ledger(ledger_rel)
            for route in routes:
                rid=route.get('route_id','<missing>')
                for sid in route.get(field, []):
                    checked += 1
                    if (source_kind, sid, 'route', rid) not in edges:
                        failures.append((fam.get('family_id','<missing>'), field, sid, rid))
    lines=['# Registered dependency-edge coverage audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json`, `CANDIDATE-ROUTE-STATE-LEDGER.json`, and `AUTHORITY-DEPENDENCY-GRAPH.json`. Do not edit directly; run `make index` after changing route-support handles or dependency graph generation.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- Route rows: `{len(routes)}`", f"- Route-local handle edges checked: `{checked}`", f"- Dependency edge coverage failures: `{len(failures)}`", '', '## Rule', '', 'Every nonempty handle in every `route-local-plus-wrapper` route field must have a corresponding source-kind/source-id → route edge in `AUTHORITY-DEPENDENCY-GRAPH.json`. This keeps rollback and authority propagation attached to route handles instead of relying on schema presence alone.', '']
    if failures:
        lines += ['## Failures', '']
        for fam, field, sid, rid in failures[:500]:
            lines.append(f'- `{fam}` / `{field}` / `{sid}` -> `{rid}`')
    (root/'docs/30-program/registered-dependency-edge-coverage-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/registered-dependency-edge-coverage-audit.generated.md')

def write_route_field_prefix_collision_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    field_to_fams={}
    stem_to_fields={}
    for fam in registry.get('registry_rows', []):
        for field in fam.get('route_fields', []):
            field_to_fams.setdefault(field, []).append(fam.get('family_id','<missing>'))
            stem=field[:-4] if field.endswith('_ids') else field
            stem_to_fields.setdefault(stem, []).append(field)
    duplicate_fields={k:v for k,v in field_to_fams.items() if len(v)>1}
    duplicate_stems={k:v for k,v in stem_to_fields.items() if len(set(v))>1}
    prefix_collisions=[]
    fields=sorted(field_to_fams)
    for i,a in enumerate(fields):
        for b in fields[i+1:]:
            if a != b and (a.startswith(b) or b.startswith(a)):
                prefix_collisions.append((a,b))
    lines=['# Route-field prefix collision audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json`. Do not edit directly; run `make index` after changing route-support families.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- Registered route fields: `{len(fields)}`", f"- Duplicate route fields: `{len(duplicate_fields)}`", f"- Duplicate field stems: `{len(duplicate_stems)}`", f"- Prefix collisions: `{len(prefix_collisions)}`", '', '| Route field | Owning families |', '|---|---|']
    for field in fields:
        lines.append(f"| `{field}` | `{', '.join(field_to_fams[field])}` |")
    if duplicate_fields or duplicate_stems or prefix_collisions:
        lines += ['', '## Failures', '']
        for k,v in duplicate_fields.items(): lines.append(f"- duplicate field `{k}` in `{v}`")
        for k,v in duplicate_stems.items(): lines.append(f"- duplicate stem `{k}` maps fields `{v}`")
        for a,b in prefix_collisions: lines.append(f"- prefix collision `{a}` / `{b}`")
    (root/'docs/30-program/route-field-prefix-collision-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/route-field-prefix-collision-audit.generated.md')

def write_generated_summary_writer_coverage_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    script=(root/'tools/sync_generated_surfaces.py').read_text()
    failures=[]
    rows=[]
    for fam in registry.get('registry_rows', []):
        summary=fam.get('generated_summary','')
        if not summary:
            continue
        present=(root/summary).exists()
        referenced=summary in script
        if not present or not referenced:
            failures.append((fam.get('family_id','<missing>'), summary, present, referenced))
        rows.append((fam.get('family_id','<missing>'), summary, present, referenced))
    lines=['# Generated-summary writer coverage audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json` and `tools/sync_generated_surfaces.py`. Do not edit directly; run `make index` after changing registered summaries or generator wiring.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- Families with generated summaries: `{len(rows)}`", f"- Summary writer coverage failures: `{len(failures)}`", '', '| Family | Summary | File exists | Writer referenced |', '|---|---|---:|---:|']
    for fam, summary, present, referenced in rows:
        lines.append(f"| `{fam}` | `{summary}` | `{str(present).lower()}` | `{str(referenced).lower()}` |")
    if failures:
        lines += ['', '## Failures', '']
        for fam, summary, present, referenced in failures:
            lines.append(f"- `{fam}` / `{summary}` exists={present} referenced={referenced}")
    (root/'docs/30-program/generated-summary-writer-coverage-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/generated-summary-writer-coverage-audit.generated.md')


def augment_authority_dependency_graph_with_perturbative_loop_resummation_edges(root: Path) -> None:
    """Add perturbative-expansion, loop-order/counterterm, and resummation/Borel edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Perturbative-expansion / loop-order-counterterm / resummation-Borel edges are appended by the rev0307 perturbative-control augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for pid in row.get('perturbative_expansion_ids', []):
            add('perturbative-expansion', pid, 'route', rid, 'perturbative-expansion-condition', 'route perturbative-expansion / truncation denominator', 'cap perturbative, low-order, small-parameter, and expansion-control wording when perturbative-expansion control fails', effect)
        for lid in row.get('loop_order_counterterm_ids', []):
            add('loop-order-counterterm', lid, 'route', rid, 'loop-order-counterterm-condition', 'route loop-order / counterterm denominator', 'cap loop-order, beta-function, counterterm, all-order, and UV-completion wording when loop/counterterm control fails', effect)
        for sid in row.get('resummation_borel_ids', []):
            add('resummation-borel', sid, 'route', rid, 'resummation-borel-condition', 'route Borel / resurgence / resummation denominator', 'cap Borel, resurgence, renormalon, transseries, and resummation wording when resummation control fails', effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','S3')
        for pid in binding.get('perturbative_expansion_ids', []):
            add('perturbative-expansion', pid, tk, tid, 'perturbative-expansion-claim-condition', f'claim perturbative-expansion denominator under {binding.get("binding_id")}', 'freeze perturbative-expansion claim wording until perturbative rows are restored', effect)
        for lid in binding.get('loop_order_counterterm_ids', []):
            add('loop-order-counterterm', lid, tk, tid, 'loop-order-counterterm-claim-condition', f'claim loop-order/counterterm denominator under {binding.get("binding_id")}', 'freeze loop-order, counterterm, and all-order-control wording until loop/counterterm rows are restored', effect)
        for sid in binding.get('resummation_borel_ids', []):
            add('resummation-borel', sid, tk, tid, 'resummation-borel-claim-condition', f'claim resummation/Borel denominator under {binding.get("binding_id")}', 'freeze Borel, resurgence, renormalon, transseries, and resummation wording until resummation rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json perturbative/loop/resummation edges')


def write_perturbative_loop_resummation_summary(root: Path) -> None:
    p=json.loads((root/'PERTURBATIVE-EXPANSION-LEDGER.json').read_text())
    l=json.loads((root/'LOOP-ORDER-COUNTERTERM-LEDGER.json').read_text())
    r=json.loads((root/'RESUMMATION-BOREL-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    prows=p.get('perturbative_expansion_rows', []); lrows=l.get('loop_order_counterterm_rows', []); rrows=r.get('resummation_borel_rows', [])
    def counts(rows,key):
        out={}
        for row in rows: out[row.get(key,'<missing>')]=out.get(row.get(key,'<missing>'),0)+1
        return out
    lines=['# Perturbative / loop-order / resummation summary (generated)', '', 'Generated from `PERTURBATIVE-EXPANSION-LEDGER.json`, `LOOP-ORDER-COUNTERTERM-LEDGER.json`, `RESUMMATION-BOREL-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{p.get('revision','<missing>')}`", f"- Perturbative-expansion rows: `{len(prows)}`", f"- Loop-order/counterterm rows: `{len(lrows)}`", f"- Resummation/Borel rows: `{len(rrows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for row in routes if row.get('authority_state') in ['S4','S5'])}`", '', '## Perturbative-expansion class counts', '']
    for k,val in sorted(counts(prows,'perturbative_expansion_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Loop-order/counterterm class counts', '']
    for k,val in sorted(counts(lrows,'loop_order_counterterm_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Resummation/Borel class counts', '']
    for k,val in sorted(counts(rrows,'resummation_borel_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Non-promotion rule', '', 'Perturbative-expansion, loop-order/counterterm, and resummation/Borel rows make low-order agreement, finite loop calculations, counterterm cancellation, EFT corridors, Borel summability, resurgence, renormalons, transseries, and resummation language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, regularization/matching, nonperturbative-sector, Hilbert/spectrum, public-record, and observed-sector limits.', '']
    (root/'docs/30-program/perturbative-loop-resummation-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/perturbative-loop-resummation-summary.generated.md')


def write_ledger_family_namespace_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    fams=registry.get('registry_rows', [])
    def dups(seq):
        return sorted({x for x in seq if seq.count(x)>1})
    family_ids=[f.get('family_id','') for f in fams]
    ledger_files=[x for f in fams for x in f.get('ledger_files', [])]
    schema_files=[x for f in fams for x in f.get('schema_files', [])]
    summaries=[f.get('generated_summary','') for f in fams if f.get('generated_summary')]
    rev_nums=[]; nonmonotone=0
    for f in fams:
        m=re.match(r'rev(\d+)$', f.get('introduced_revision',''))
        rev_nums.append(int(m.group(1)) if m else -1)
    for a,b in zip(rev_nums, rev_nums[1:]):
        if b < a: nonmonotone += 1
    failures={
        'duplicate_family_ids':dups(family_ids),
        'duplicate_ledger_files':dups(ledger_files),
        'duplicate_schema_files':dups(schema_files),
        'duplicate_generated_summaries':dups(summaries),
        'nonmonotone_introduced_revision_edges':nonmonotone,
    }
    total=sum(len(v) if isinstance(v,list) else int(v) for v in failures.values())
    lines=['# Ledger-family namespace audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json`. Do not edit directly; run `make index` after changing registered layer families.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(fams)}`", f"- Duplicate family IDs: `{len(failures['duplicate_family_ids'])}`", f"- Duplicate ledger files: `{len(failures['duplicate_ledger_files'])}`", f"- Duplicate schema files: `{len(failures['duplicate_schema_files'])}`", f"- Duplicate generated summaries: `{len(failures['duplicate_generated_summaries'])}`", f"- Nonmonotone introduced-revision edges: `{nonmonotone}`", f"- Total namespace failures: `{total}`", '', '| Family | Introduced | Ledgers | Schemas | Summary |', '|---|---:|---:|---:|---|']
    for f in fams:
        lines.append(f"| `{f.get('family_id')}` | `{f.get('introduced_revision')}` | `{len(f.get('ledger_files', []))}` | `{len(f.get('schema_files', []))}` | `{f.get('generated_summary','')}` |")
    if total:
        lines += ['', '## Failures', '']
        for k,v in failures.items(): lines.append(f"- `{k}`: `{v}`")
    (root/'docs/30-program/ledger-family-namespace-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/ledger-family-namespace-audit.generated.md')



def augment_authority_dependency_graph_with_equation_transport_fluctuation_edges(root: Path) -> None:
    """Add equation-of-state, transport-coefficient, and fluctuation-dissipation edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Equation-of-state / transport-coefficient / fluctuation-dissipation edges are appended by the rev0306 hydrodynamic transport augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for eid in row.get('equation_of_state_ids', []):
            add('equation-of-state', eid, 'route', rid, 'equation-of-state-condition', 'route equation-of-state / effective-fluid denominator', 'cap hydrodynamic, thermodynamic, dark-fluid, and fluid/gravity wording when equation-of-state control fails', effect)
        for tid in row.get('transport_coefficient_ids', []):
            add('transport-coefficient', tid, 'route', rid, 'transport-coefficient-condition', 'route transport-coefficient / Kubo denominator', 'cap viscosity, conductivity, diffusion, damping, and membrane-transport wording when transport control fails', effect)
        for fid in row.get('fluctuation_dissipation_ids', []):
            add('fluctuation-dissipation', fid, 'route', rid, 'fluctuation-dissipation-condition', 'route fluctuation-dissipation / noise-response denominator', 'cap FDT, KMS, stochastic, Schwinger-Keldysh, and noise-response wording when fluctuation-dissipation control fails', effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','S3')
        for eid in binding.get('equation_of_state_ids', []):
            add('equation-of-state', eid, tk, tid, 'equation-of-state-claim-condition', f'claim equation-of-state denominator under {binding.get("binding_id")}', 'freeze equation-of-state and effective-fluid wording until equation-of-state rows are restored', effect)
        for tcid in binding.get('transport_coefficient_ids', []):
            add('transport-coefficient', tcid, tk, tid, 'transport-coefficient-claim-condition', f'claim transport-coefficient denominator under {binding.get("binding_id")}', 'freeze transport, Kubo, viscosity, conductivity, diffusion, and damping wording until transport rows are restored', effect)
        for fid in binding.get('fluctuation_dissipation_ids', []):
            add('fluctuation-dissipation', fid, tk, tid, 'fluctuation-dissipation-claim-condition', f'claim fluctuation-dissipation denominator under {binding.get("binding_id")}', 'freeze FDT, KMS, noise-response, and stochastic hydrodynamic wording until FDT rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json equation/transport/fluctuation edges')


def write_equation_transport_fluctuation_summary(root: Path) -> None:
    eos=json.loads((root/'EQUATION-OF-STATE-LEDGER.json').read_text())
    trc=json.loads((root/'TRANSPORT-COEFFICIENT-LEDGER.json').read_text())
    fdt=json.loads((root/'FLUCTUATION-DISSIPATION-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    erows=eos.get('equation_of_state_rows', []); trows=trc.get('transport_coefficient_rows', []); frows=fdt.get('fluctuation_dissipation_rows', [])
    def counts(rows,key):
        out={}
        for row in rows: out[row.get(key,'<missing>')]=out.get(row.get(key,'<missing>'),0)+1
        return out
    lines=['# Equation-of-state / transport-coefficient / fluctuation-dissipation summary (generated)', '', 'Generated from `EQUATION-OF-STATE-LEDGER.json`, `TRANSPORT-COEFFICIENT-LEDGER.json`, `FLUCTUATION-DISSIPATION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit by hand.', '', f"- Revision: `{eos.get('revision','<missing>')}`", f"- Equation-of-state rows: `{len(erows)}`", f"- Transport-coefficient rows: `{len(trows)}`", f"- Fluctuation-dissipation rows: `{len(frows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for row in routes if row.get('authority_state') in ['S4','S5'])}`", '', '## Equation-of-state class counts', '']
    for k,val in sorted(counts(erows,'equation_of_state_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Transport-coefficient class counts', '']
    for k,val in sorted(counts(trows,'transport_coefficient_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Fluctuation-dissipation class counts', '']
    for k,val in sorted(counts(frows,'fluctuation_dissipation_class').items()): lines.append(f"- `{k}`: `{val}`")
    lines += ['', '## Non-promotion rule', '', 'Equation-of-state, transport-coefficient, and fluctuation-dissipation rows make hydrodynamic, thermodynamic, effective-fluid, Kubo, viscosity, conductivity, diffusion, membrane-fluid, Schwinger-Keldysh, KMS, stochastic, and noise-response language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, public-record, stress-energy, black-hole, cosmology, detector, matter, and observed-sector limits.', '']
    (root/'docs/30-program/equation-transport-fluctuation-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/equation-transport-fluctuation-summary.generated.md')


def write_registered_ledger_revision_alignment_audit(root: Path) -> None:
    manifest=json.loads((root/'RELEASE-MANIFEST.json').read_text())
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    target=manifest.get('revision','<missing>')
    rows=[]; failures=[]
    seen=[]
    for fam in registry.get('registry_rows', []):
        for rel in fam.get('ledger_files', []):
            if rel in seen:
                continue
            seen.append(rel)
            path=root/rel
            present=path.exists()
            revision='<missing>'
            if present:
                try:
                    data=json.loads(path.read_text())
                    revision=data.get('revision','<missing>')
                except Exception:
                    revision='<parse-failure>'
            ok=present and revision==target
            rows.append((rel,present,revision,ok))
            if not ok:
                failures.append((rel,present,revision))
    lines=['# Registered-ledger revision alignment audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json` and `RELEASE-MANIFEST.json`. Do not edit directly; run `make index` after changing registered ledgers or release identity.', '', f"- Manifest revision: `{target}`", f"- Registered ledger files checked: `{len(rows)}`", f"- Revision alignment failures: `{len(failures)}`", '', '| Ledger | Present | Revision | Aligned |', '|---|---:|---|---:|']
    for rel,present,revision,ok in rows:
        lines.append(f"| `{rel}` | `{str(present).lower()}` | `{revision}` | `{str(ok).lower()}` |")
    if failures:
        lines += ['', '## Failures', '']
        for rel,present,revision in failures:
            lines.append(f"- `{rel}` present={present} revision={revision}")
    (root/'docs/30-program/registered-ledger-revision-alignment-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/registered-ledger-revision-alignment-audit.generated.md')


def write_ledger_family_order_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    rows=registry.get('registry_rows', [])
    failures=[]
    def revnum(rev):
        m=re.match(r'^rev(\d+)$', rev or '')
        return int(m.group(1)) if m else -1
    def oqnum(oq):
        m=re.match(r'^OQ-(\d+)$', oq or '')
        return int(m.group(1)) if m else -1
    last_rev=-1; last_oq=-1
    lines=['# Ledger-family order audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json`. Do not edit directly; run `make index` after changing the registry.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(rows)}`", '', '| Index | Family | Introduced revision | OQ | Revision order ok | OQ order ok |', '|---:|---|---|---|---:|---:|']
    for idx,fam in enumerate(rows,1):
        rv=revnum(fam.get('introduced_revision','')); oq=oqnum(fam.get('open_question_id',''))
        rv_ok=rv>=last_rev
        oq_ok=oq>=last_oq or fam.get('cardinality_policy') in {'cluster-local-plus-wrapper'}
        if not rv_ok or not oq_ok:
            failures.append((fam.get('family_id'),fam.get('introduced_revision'),fam.get('open_question_id'),rv_ok,oq_ok))
        last_rev=max(last_rev, rv); last_oq=max(last_oq, oq)
        lines.append(f"| `{idx}` | `{fam.get('family_id')}` | `{fam.get('introduced_revision')}` | `{fam.get('open_question_id')}` | `{str(rv_ok).lower()}` | `{str(oq_ok).lower()}` |")
    lines += ['', f"- Ledger-family order failures: `{len(failures)}`", '', '## Rule', '', 'The registry should read in chronological order. Introduced revisions should be monotone, and owning OQ gates should not move backwards except for explicitly cluster-level legacy families. This is an audit/refactor guard, not a scientific authority source.', '']
    if failures:
        lines += ['## Failures', '']
        for item in failures: lines.append(f"- `{item[0]}` revision={item[1]} oq={item[2]} revision_ok={item[3]} oq_ok={item[4]}")
    (root/'docs/30-program/ledger-family-order-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/ledger-family-order-audit.generated.md')



def augment_authority_dependency_graph_with_stochastic_estimator_convergence_edges(root: Path) -> None:
    """Add stochastic-sampler, estimator-variance, and convergence-diagnostic edges."""
    graph = load_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json')
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Stochastic-sampler / estimator-variance / convergence-diagnostic edges are appended by the rev0308 stochastic-computation augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows = json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings = json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3')
        for sid in row.get('stochastic_sampler_ids', []):
            add('stochastic-sampler', sid, 'route', rid, 'stochastic-sampler-condition', 'route stochastic-sampler / Monte Carlo denominator', 'cap Monte Carlo, MCMC, nested-sampling, HMC, stochastic-simulation, and sampler-representativeness wording when sampler control fails', effect)
        for eid in row.get('estimator_variance_ids', []):
            add('estimator-variance', eid, 'route', rid, 'estimator-variance-condition', 'route estimator variance / Monte Carlo error denominator', 'cap estimator precision, finite-sample uncertainty, posterior/evidence, and exact-likelihood wording when estimator control fails', effect)
        for cid in row.get('convergence_diagnostic_ids', []):
            add('convergence-diagnostic', cid, 'route', rid, 'convergence-diagnostic-condition', 'route convergence / mixing / stopping denominator', 'cap R-hat, ESS, mixing, stopping-rule, nested-sampling, HMC-diagnostic, and convergence wording when diagnostic control fails', effect)
    for binding in bindings:
        target_id=binding.get('claim_or_oq_id','')
        target_kind='open-question' if target_id.startswith('OQ-') else 'claim'
        effect=binding.get('maximum_authority_effect','no route promotion')
        for sid in binding.get('stochastic_sampler_ids', []):
            add('stochastic-sampler', sid, target_kind, target_id, 'stochastic-sampler-claim-condition', f'claim stochastic-sampler denominator under {binding.get("binding_id")}', 'freeze stochastic-sampling claim wording until sampler rows are restored', effect)
        for eid in binding.get('estimator_variance_ids', []):
            add('estimator-variance', eid, target_kind, target_id, 'estimator-variance-claim-condition', f'claim estimator-variance denominator under {binding.get("binding_id")}', 'freeze estimator-precision claim wording until estimator rows are restored', effect)
        for cid in binding.get('convergence_diagnostic_ids', []):
            add('convergence-diagnostic', cid, target_kind, target_id, 'convergence-diagnostic-claim-condition', f'claim convergence-diagnostic denominator under {binding.get("binding_id")}', 'freeze convergence-diagnostic claim wording until diagnostic rows are restored', effect)
    graph['edge_count']=len(rows)
    write_authority_graph(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json stochastic/estimator/convergence edges')


def write_stochastic_estimator_convergence_summary(root: Path) -> None:
    s=json.loads((root/'STOCHASTIC-SAMPLER-LEDGER.json').read_text())
    e=json.loads((root/'ESTIMATOR-VARIANCE-LEDGER.json').read_text())
    c=json.loads((root/'CONVERGENCE-DIAGNOSTIC-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    sr=s.get('stochastic_sampler_rows', []); er=e.get('estimator_variance_rows', []); cr=c.get('convergence_diagnostic_rows', [])
    def counts(rows,key):
        out={}
        for row in rows:
            val=row.get(key,'<missing>'); out[val]=out.get(val,0)+1
        return out
    lines=['# Stochastic sampling / estimator variance / convergence summary (generated)', '', 'Generated from `STOCHASTIC-SAMPLER-LEDGER.json`, `ESTIMATOR-VARIANCE-LEDGER.json`, and `CONVERGENCE-DIAGNOSTIC-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{s.get('revision','<missing>')}`", f"- Stochastic-sampler rows: `{len(sr)}`", f"- Estimator-variance rows: `{len(er)}`", f"- Convergence-diagnostic rows: `{len(cr)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Stochastic-sampler class counts', '']
    for k,v in sorted(counts(sr,'stochastic_sampler_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Estimator-variance class counts', '']
    for k,v in sorted(counts(er,'estimator_variance_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Convergence-diagnostic class counts', '']
    for k,v in sorted(counts(cr,'convergence_diagnostic_class').items()): lines.append(f"- `{k}`: `{v}`")
    lines += ['', '## Route handle counts', '', '| Route | Samplers | Estimators | Diagnostics |', '|---|---:|---:|---:|']
    for row in routes:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('stochastic_sampler_ids', []))}` | `{len(row.get('estimator_variance_ids', []))}` | `{len(row.get('convergence_diagnostic_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Stochastic-sampler, estimator-variance, and convergence-diagnostic rows make Monte Carlo, MCMC, nested-sampling, HMC, bootstrap, posterior/evidence, effective-sample-size, R-hat, convergence, and finite-sample precision language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, likelihood/prior, measurement, selection/multiplicity, public-record, observed-sector, and residual-control ledgers.', '']
    (root/'docs/30-program/stochastic-estimator-convergence-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/stochastic-estimator-convergence-summary.generated.md')


def write_registered_id_reference_integrity_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    known=set()
    # Core JSON ids from all top-level JSON surfaces.
    for path in root.glob('*.json'):
        try:
            data=json.loads(path.read_text())
        except Exception:
            continue
        def walk(obj):
            if isinstance(obj, dict):
                for k,v in obj.items():
                    if k.endswith('_id') and isinstance(v,str):
                        known.add(v)
                    walk(v)
            elif isinstance(obj, list):
                for item in obj: walk(item)
        walk(data)
    # Bibliography REF ids and constitutional ids are also legal references.
    bib=(root/'docs/00-meta/bibliography.md').read_text()
    known.update(re.findall(r'`(REF-\d{4})`', bib))
    for rel,pat in [('docs/20-constitution/claim-registry.md', r'`(CL-\d{4})`'), ('docs/20-constitution/open-question-registry.md', r'`(OQ-\d{4})`')]:
        known.update(re.findall(pat, (root/rel).read_text()))
    ref_pat=re.compile(r'^(?:[A-Z][A-Z0-9]+|R-OQ\d{4}|REF|CL|OQ)-\d{4}')
    failures=[]; checked=0
    for fam in registry.get('registry_rows', []):
        for ledger in fam.get('ledger_files', []):
            path=root/ledger
            if not path.exists():
                continue
            data=json.loads(path.read_text())
            arrays=[v for v in data.values() if isinstance(v,list)]
            for arr in arrays:
                for row in arr:
                    if not isinstance(row,dict):
                        continue
                    row_id=next((v for k,v in row.items() if k.endswith('_id') and isinstance(v,str)), '<row>')
                    for key,val in row.items():
                        if key.endswith('_ids') or key in ('source_refs','route_ids'):
                            if not isinstance(val,list):
                                continue
                            for item in val:
                                if isinstance(item,str) and ref_pat.match(item):
                                    checked += 1
                                    if item not in known:
                                        failures.append((ledger,row_id,key,item))
    lines=['# Registered ID-reference integrity audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json`, registered executable ledgers, bibliography, and constitutional registries. Do not edit directly; run `make index` after changing executable ledger references.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- ID-like references checked: `{checked}`", f"- Unknown ID references: `{len(failures)}`", '', '## Rule', '', 'Every ID-like value in registered ledger list fields must resolve to a known route-support row, core ledger row, bibliography REF id, claim id, or open-question id. This catches stale handles that schema shape alone cannot detect.', '']
    if failures:
        lines += ['## Failures', '']
        for ledger,row_id,key,item in failures[:500]:
            lines.append(f'- `{ledger}` row `{row_id}` field `{key}` references unknown id `{item}`')
    (root/'docs/30-program/registered-id-reference-integrity-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/registered-id-reference-integrity-audit.generated.md')



def augment_authority_dependency_graph_with_simulator_emulator_transfer_edges(root: Path) -> None:
    """Add simulator-fidelity / surrogate-emulator / sim-to-real transfer edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Simulator-fidelity / surrogate-emulator / sim-to-real transfer edges are appended by the rev0310 simulator-transfer augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for sid in row.get('simulator_fidelity_ids', []):
            add('simulator-fidelity', sid, 'route', rid, 'simulator-fidelity-condition', 'route simulator/model-discrepancy denominator', 'cap simulator, synthetic-data, model-calibration, and digital-twin wording when simulator fidelity or discrepancy control fails', effect)
        for eid in row.get('surrogate_emulator_ids', []):
            add('surrogate-emulator', eid, 'route', rid, 'surrogate-emulator-condition', 'route surrogate/emulator approximation denominator', 'cap emulator, surrogate, reduced-order-model, response-surface, and approximate-likelihood wording when emulator control fails', effect)
        for tid in row.get('sim_to_real_transfer_ids', []):
            add('sim-to-real-transfer', tid, 'route', rid, 'sim-to-real-transfer-condition', 'route simulation-to-public-record transfer denominator', 'cap sim-to-real, synthetic-to-real, calibrated digital-twin, and domain-gap wording when transfer control fails', effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','S3')
        for sid in binding.get('simulator_fidelity_ids', []):
            add('simulator-fidelity', sid, tk, tid, 'simulator-fidelity-claim-condition', f'claim simulator-fidelity denominator under {binding.get("binding_id")}', 'freeze simulator/synthetic-data/model-calibration claim wording until simulator-fidelity rows are restored', effect)
        for eid in binding.get('surrogate_emulator_ids', []):
            add('surrogate-emulator', eid, tk, tid, 'surrogate-emulator-claim-condition', f'claim surrogate-emulator denominator under {binding.get("binding_id")}', 'freeze emulator/surrogate/approximate-likelihood claim wording until emulator rows are restored', effect)
        for xtid in binding.get('sim_to_real_transfer_ids', []):
            add('sim-to-real-transfer', xtid, tk, tid, 'sim-to-real-transfer-claim-condition', f'claim sim-to-real transfer denominator under {binding.get("binding_id")}', 'freeze sim-to-real/domain-gap/digital-twin transfer claim wording until transfer rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json simulator/emulator/transfer edges')


def write_simulator_emulator_transfer_summary(root: Path) -> None:
    s=json.loads((root/'SIMULATOR-FIDELITY-LEDGER.json').read_text())
    e=json.loads((root/'SURROGATE-EMULATOR-LEDGER.json').read_text())
    t=json.loads((root/'SIM-TO-REAL-TRANSFER-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    srows=s.get('simulator_fidelity_rows', []); erows=e.get('surrogate_emulator_rows', []); trows=t.get('sim_to_real_transfer_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Simulator-fidelity / surrogate-emulator / sim-to-real transfer summary (generated)', '', 'Generated from `SIMULATOR-FIDELITY-LEDGER.json`, `SURROGATE-EMULATOR-LEDGER.json`, and `SIM-TO-REAL-TRANSFER-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{s.get('revision','<missing>')}`", f"- Simulator-fidelity rows: `{len(srows)}`", f"- Surrogate-emulator rows: `{len(erows)}`", f"- Sim-to-real transfer rows: `{len(trows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Simulator-fidelity class counts', '']
    for k,v in sorted(counts(srows,'simulator_fidelity_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Surrogate-emulator class counts', '']
    for k,v in sorted(counts(erows,'surrogate_emulator_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Sim-to-real transfer class counts', '']
    for k,v in sorted(counts(trows,'sim_to_real_transfer_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Route handle counts', '', '| Route | Simulator fidelity | Surrogate emulator | Sim-to-real transfer |', '|---|---:|---:|---:|']
    for row in routes:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('simulator_fidelity_ids', []))}` | `{len(row.get('surrogate_emulator_ids', []))}` | `{len(row.get('sim_to_real_transfer_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Simulator-fidelity, surrogate-emulator, and sim-to-real transfer rows make simulator, synthetic-data, digital-twin, model-calibration, emulator, response-surface, approximate-likelihood, and domain-gap wording auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond public-record, measurement, stochastic, compression, validity, observed-sector, or residual-cap limits.', '']
    (root/'docs/30-program/simulator-emulator-transfer-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/simulator-emulator-transfer-summary.generated.md')



def augment_authority_dependency_graph_with_benchmark_evaluation_edges(root: Path) -> None:
    """Add benchmark-suite / benchmark-metric / evaluation-protocol edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Benchmark-suite / benchmark-metric / evaluation-protocol edges are appended by the rev0311 benchmark-evaluation augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for bid in row.get('benchmark_suite_ids', []):
            add('benchmark-suite', bid, 'route', rid, 'benchmark-suite-condition', 'route benchmark/challenge denominator', 'cap benchmark, challenge, validation-suite, hidden-test, or public/private leaderboard wording when benchmark-suite control fails', effect)
        for mid in row.get('benchmark_metric_ids', []):
            add('benchmark-metric', mid, 'route', rid, 'benchmark-metric-condition', 'route benchmark metric / score denominator', 'cap score, SOTA, rank, residual, performance, or metric wording when benchmark-metric control fails', effect)
        for eid in row.get('evaluation_protocol_ids', []):
            add('evaluation-protocol', eid, 'route', rid, 'evaluation-protocol-condition', 'route evaluation protocol / adjudication denominator', 'cap benchmark protocol, blinded evaluation, independent evaluator, or heldout-test wording when evaluation-protocol control fails', effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','S3')
        for bid in binding.get('benchmark_suite_ids', []):
            add('benchmark-suite', bid, tk, tid, 'benchmark-suite-claim-condition', f'claim benchmark-suite denominator under {binding.get("binding_id")}', 'freeze benchmark/challenge/validation-suite claim wording until benchmark-suite rows are restored', effect)
        for mid in binding.get('benchmark_metric_ids', []):
            add('benchmark-metric', mid, tk, tid, 'benchmark-metric-claim-condition', f'claim benchmark-metric denominator under {binding.get("binding_id")}', 'freeze metric/score/SOTA/leaderboard claim wording until metric rows are restored', effect)
        for eid in binding.get('evaluation_protocol_ids', []):
            add('evaluation-protocol', eid, tk, tid, 'evaluation-protocol-claim-condition', f'claim evaluation-protocol denominator under {binding.get("binding_id")}', 'freeze heldout/blind/independent-evaluation claim wording until evaluation rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json benchmark/evaluation edges')


def write_benchmark_evaluation_summary(root: Path) -> None:
    b=json.loads((root/'BENCHMARK-SUITE-LEDGER.json').read_text())
    m=json.loads((root/'BENCHMARK-METRIC-LEDGER.json').read_text())
    e=json.loads((root/'EVALUATION-PROTOCOL-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    brows=b.get('benchmark_suite_rows', []); mrows=m.get('benchmark_metric_rows', []); erows=e.get('evaluation_protocol_rows', [])
    def counts(rows,key):
        out={}
        for row in rows: out[row.get(key,'<missing>')]=out.get(row.get(key,'<missing>'),0)+1
        return out
    lines=['# Benchmark suite / metric / evaluation protocol summary (generated)', '', 'Generated from `BENCHMARK-SUITE-LEDGER.json`, `BENCHMARK-METRIC-LEDGER.json`, `EVALUATION-PROTOCOL-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{b.get('revision','<missing>')}`", f"- Benchmark-suite rows: `{len(brows)}`", f"- Benchmark-metric rows: `{len(mrows)}`", f"- Evaluation-protocol rows: `{len(erows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for row in routes if row.get('authority_state') in ['S4','S5'])}`", '', '## Benchmark-suite class counts', '']
    for k,v in sorted(counts(brows,'benchmark_suite_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Benchmark-metric class counts', '']
    for k,v in sorted(counts(mrows,'benchmark_metric_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Evaluation-protocol class counts', '']
    for k,v in sorted(counts(erows,'evaluation_protocol_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Route handle counts', '', '| Route | Benchmark suite | Benchmark metric | Evaluation protocol |', '|---|---:|---:|---:|']
    for row in routes:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('benchmark_suite_ids', []))}` | `{len(row.get('benchmark_metric_ids', []))}` | `{len(row.get('evaluation_protocol_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Benchmark-suite, benchmark-metric, and evaluation-protocol rows make benchmark, challenge, hidden-test, validation-suite, SOTA, leaderboard, score, metric, public/private split, and independent-evaluation wording auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond public-record, measurement, selection, simulator, compression, stochastic, observed-sector, or residual-cap limits.', '']
    (root/'docs/30-program/benchmark-evaluation-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/benchmark-evaluation-summary.generated.md')


def write_context_pack_release_freshness_audit(root: Path) -> None:
    manifest=json.loads((root/'RELEASE-MANIFEST.json').read_text())
    receipt=json.loads((root/'REVISION-RECEIPT.json').read_text())
    context=json.loads((root/'context-pack.json').read_text())
    checks=[]
    def add(label, expected, actual):
        checks.append((label, expected, actual, expected==actual))
    bundle=manifest.get('bundle','')
    nozip=bundle[:-4] if bundle.endswith('.zip') else bundle
    add('context.revision', manifest.get('revision'), context.get('revision'))
    add('context.timestamp', manifest.get('timestamp'), context.get('timestamp'))
    add('context.bundle', bundle, context.get('bundle'))
    add('context.current_revision', manifest.get('revision'), context.get('current_revision'))
    add('context.current_release', nozip, context.get('current_release'))
    add('context.latest_bundle', nozip, context.get('latest_bundle'))
    add('context.recent_revision_bundle', nozip, context.get('recent_revision_bundle'))
    add('context.latest_revision_delta_has_revision', True, str(manifest.get('revision')) in str(context.get('latest_revision_delta','')))
    add('context.latest_revision_summary_has_revision', True, str(manifest.get('revision')) in str(context.get('latest_revision_summary','')))
    add('context.summary_has_revision', True, str(manifest.get('revision')) in str(context.get('summary','')))
    add('receipt.summary_has_revision_delta', True, str(receipt.get('summary',''))[:20] in str(context.get('summary','')) or str(manifest.get('revision')) in str(context.get('summary','')))
    failures=[c for c in checks if not c[3]]
    lines=['# Context-pack release freshness audit (generated)', '', 'Generated from `context-pack.json`, `RELEASE-MANIFEST.json`, and `REVISION-RECEIPT.json`. Do not edit directly; run `make index` after changing restart handoff or release identity surfaces.', '', f"- Manifest revision: `{manifest.get('revision','<missing>')}`", f"- Checks: `{len(checks)}`", f"- Freshness failures: `{len(failures)}`", '', '| Check | Expected | Actual | Pass |', '|---|---|---|---:|']
    for label, expected, actual, ok in checks:
        lines.append(f"| `{label}` | `{expected}` | `{actual}` | `{str(ok).lower()}` |")
    lines += ['', '## Rule', '', 'The context pack is a restart artifact. It must not lag behind the manifest or receipt while still passing ordinary generated-surface checks. A freshness pass does not create scientific support; it only prevents stale machine handoff fields from misleading continuation.', '']
    if failures:
        lines += ['## Failures', '']
        for label, expected, actual, _ in failures:
            lines.append(f'- `{label}` expected `{expected}` but found `{actual}`')
    (root/'docs/30-program/context-pack-release-freshness-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/context-pack-release-freshness-audit.generated.md')


def write_registered_generated_summary_revision_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    manifest=json.loads((root/'RELEASE-MANIFEST.json').read_text())
    rev=manifest.get('revision','<missing>')
    rows=[]; failures=[]
    for fam in registry.get('registry_rows', []):
        summary=fam.get('generated_summary','')
        if not summary:
            continue
        p=root/summary
        present=p.exists()
        contains=False
        if present:
            contains=rev in p.read_text(errors='replace')
        rows.append((fam.get('family_id','<missing>'), summary, present, contains))
        if not present or not contains:
            failures.append((fam.get('family_id','<missing>'), summary, present, contains))
    lines=['# Registered generated-summary revision freshness audit (generated)', '', 'Generated from `LEDGER-FAMILY-REGISTRY.json`, registered generated summaries, and `RELEASE-MANIFEST.json`. Do not edit directly; run `make index` after changing registered summaries or release identity.', '', f"- Manifest revision: `{rev}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- Registered summaries checked: `{len(rows)}`", f"- Summary revision freshness failures: `{len(failures)}`", '', '| Family | Summary | Present | Contains current revision |', '|---|---|---:|---:|']
    for fam, summary, present, contains in rows:
        lines.append(f"| `{fam}` | `{summary}` | `{str(present).lower()}` | `{str(contains).lower()}` |")
    if failures:
        lines += ['', '## Failures', '']
        for fam, summary, present, contains in failures:
            lines.append(f'- `{fam}` / `{summary}` present={present} contains-current-revision={contains}')
    lines += ['', '## Rule', '', 'Every generated summary declared in the ledger-family registry should be rebuilt against the current manifest revision. This audit catches stale generated restart surfaces that still exist and are writer-covered but were not refreshed after a release move.', '']
    (root/'docs/30-program/registered-generated-summary-revision-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/registered-generated-summary-revision-audit.generated.md')

def augment_authority_dependency_graph_with_data_reduction_feature_sufficiency_edges(root: Path) -> None:
    """Add data-reduction / feature-extraction / summary-statistic sufficiency edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Data-reduction / feature-extraction / summary-statistic sufficiency edges are appended by the rev0309 compression/sufficiency augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for did in row.get('data_reduction_ids', []):
            add('data-reduction', did, 'route', rid, 'data-reduction-condition', 'route compressed-record / data-reduction denominator', 'cap data-reduced, compressed, binned, projected, score-compressed, or likelihood-free compression wording when reduction/loss control fails', effect)
        for fid in row.get('feature_extraction_ids', []):
            add('feature-extraction', fid, 'route', rid, 'feature-extraction-condition', 'route feature / embedding / representation denominator', 'cap feature, embedding, latent representation, graph-summary, harmonic-feature, decoder-feature, or learned-summary wording when feature control fails', effect)
        for sid in row.get('summary_statistic_sufficiency_ids', []):
            add('summary-statistic-sufficiency', sid, 'route', rid, 'summary-statistic-sufficiency-condition', 'route summary-statistic sufficiency/loss denominator', 'cap sufficient-statistic, Fisher-preserving, likelihood-ratio-preserving, ABC/SBI summary, or exact-likelihood wording when sufficiency control fails', effect)
    for binding in bindings:
        tid=binding.get('claim_or_oq_id',''); tk='open-question' if tid.startswith('OQ-') else 'claim'; effect=binding.get('maximum_authority_effect','S3')
        for did in binding.get('data_reduction_ids', []):
            add('data-reduction', did, tk, tid, 'data-reduction-claim-condition', f'claim data-reduction denominator under {binding.get("binding_id")}', 'freeze compressed-record/data-reduction claim wording until reduction rows are restored', effect)
        for fid in binding.get('feature_extraction_ids', []):
            add('feature-extraction', fid, tk, tid, 'feature-extraction-claim-condition', f'claim feature-extraction denominator under {binding.get("binding_id")}', 'freeze feature/embedding/latent-representation claim wording until feature rows are restored', effect)
        for sid in binding.get('summary_statistic_sufficiency_ids', []):
            add('summary-statistic-sufficiency', sid, tk, tid, 'summary-statistic-sufficiency-claim-condition', f'claim summary-statistic sufficiency denominator under {binding.get("binding_id")}', 'freeze summary-statistic/sufficiency/likelihood-free-compression claim wording until sufficiency rows are restored', effect)
    graph['edge_rows']=rows; graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json data-reduction/feature/sufficiency edges')


def write_data_reduction_feature_sufficiency_summary(root: Path) -> None:
    d=json.loads((root/'DATA-REDUCTION-LEDGER.json').read_text())
    f=json.loads((root/'FEATURE-EXTRACTION-LEDGER.json').read_text())
    s=json.loads((root/'SUMMARY-STATISTIC-SUFFICIENCY-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    drows=d.get('data_reduction_rows', []); frows=f.get('feature_extraction_rows', []); srows=s.get('summary_statistic_rows', [])
    def counts(rows,key):
        out={}
        for r in rows: out[r.get(key,'<missing>')]=out.get(r.get(key,'<missing>'),0)+1
        return out
    lines=['# Data-reduction / feature-extraction / summary-statistic sufficiency summary (generated)', '', 'Generated from `DATA-REDUCTION-LEDGER.json`, `FEATURE-EXTRACTION-LEDGER.json`, and `SUMMARY-STATISTIC-SUFFICIENCY-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{d.get('revision','<missing>')}`", f"- Data-reduction rows: `{len(drows)}`", f"- Feature-extraction rows: `{len(frows)}`", f"- Summary-statistic sufficiency rows: `{len(srows)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Data-reduction class counts', '']
    for k,v in sorted(counts(drows,'data_reduction_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Feature-extraction class counts', '']
    for k,v in sorted(counts(frows,'feature_extraction_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Summary-statistic class counts', '']
    for k,v in sorted(counts(srows,'summary_statistic_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Route handle counts', '', '| Route | Data reduction | Feature extraction | Summary sufficiency |', '|---|---:|---:|---:|']
    for row in routes:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('data_reduction_ids', []))}` | `{len(row.get('feature_extraction_ids', []))}` | `{len(row.get('summary_statistic_sufficiency_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Data-reduction, feature-extraction, and summary-statistic sufficiency rows make compressed-record, feature, embedding, score-compression, MOPED, information-bottleneck, ABC/SBI, and likelihood-free compression wording auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond public-record, measurement, stochastic, prior, contrast, observed-sector, or residual-cap limits.', '']
    (root/'docs/30-program/data-reduction-feature-sufficiency-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/data-reduction-feature-sufficiency-summary.generated.md')


def write_registered_artifact_reference_integrity_audit(root: Path) -> None:
    registry=json.loads((root/'LEDGER-FAMILY-REGISTRY.json').read_text())
    keys={'owner_surface','state_machine_surface','record_schema','generated_audit','generated_binding_audit','generated_binding_control_audit','generated_surface_audit','generated_gate_audit','generated_schema_envelope_audit','generated_candidate_route_schema_audit','generated_row_id_uniqueness_audit','generated_binding_schema_audit','generated_route_binding_property_audit','generated_array_type_audit','generated_registry_schema_audit','generated_summary_writer_audit','generated_route_field_prefix_audit','generated_dependency_edge_audit','generated_source_kind_audit','generated_controlling_ledger_order_audit','generated_id_reference_audit','generated_artifact_reference_audit','generated_summary_revision_audit','generated_summary'}
    list_keys={'ledger_files','schema_files','controlling_ledgers'}
    checked=0; failures=[]
    for path in root.glob('*.json'):
        try:
            data=json.loads(path.read_text())
        except Exception:
            continue
        def walk(obj, surface):
            nonlocal checked
            if isinstance(obj, dict):
                for k,v in obj.items():
                    if k in keys and isinstance(v,str) and v and not v.startswith(('http://','https://')):
                        checked += 1
                        if not (root/v).exists(): failures.append((surface,k,v))
                    elif k in list_keys and isinstance(v,list):
                        for item in v:
                            if isinstance(item,str) and item and not item.startswith(('http://','https://')):
                                checked += 1
                                if not (root/item).exists(): failures.append((surface,k,item))
                    walk(v, surface)
            elif isinstance(obj, list):
                for item in obj: walk(item, surface)
        walk(data, path.name)
    lines=['# Registered artifact-reference integrity audit (generated)', '', 'Generated from path-like references in executable JSON surfaces. Do not edit directly; run `make index` after changing registered ledgers, schemas, generated summaries, owner surfaces, or controlling ledgers.', '', f"- Registry revision: `{registry.get('revision','<missing>')}`", f"- Registered layer families: `{len(registry.get('registry_rows', []))}`", f"- Artifact/path references checked: `{checked}`", f"- Unknown artifact/path references: `{len(failures)}`", '', '## Rule', '', 'Path-like archive references in registered ledger families, route rows, and claim-route bindings must resolve to actual files in the package. This catches stale ledger, schema, owner-surface, generated-summary, and controlling-ledger paths that ID audits cannot see.', '']
    if failures:
        lines += ['## Failures', '']
        for surface,key,val in failures[:500]: lines.append(f'- `{surface}` field `{key}` references missing artifact `{val}`')
    (root/'docs/30-program/registered-artifact-reference-integrity-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/registered-artifact-reference-integrity-audit.generated.md')


def augment_authority_dependency_graph_with_prospective_preregistration_blinding_edges(root: Path) -> None:
    """Add prospective-prediction / preregistration-protocol / blinding-deviation edges."""
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    graph['revision'] = json.loads((root / 'RELEASE-MANIFEST.json').read_text()).get('revision', graph.get('revision'))
    graph['generation_rule'] = graph.get('generation_rule','') + ' Prospective-prediction / preregistration-protocol / blinding-deviation edges are appended by the rev0312 prospective-preregistration augmentation pass.'
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(source_kind, source_id, dependent_kind, dependent_id, dependency_kind, required_for, failure_effect, max_credit):
        if not source_id or not dependent_id:
            return
        key=(source_kind, source_id, dependent_kind, dependent_id, dependency_kind)
        if key in existing:
            return
        rows.append({'edge_id':next_edge_id(),'source_kind':source_kind,'source_id':source_id,'dependent_kind':dependent_kind,'dependent_id':dependent_id,'dependency_kind':dependency_kind,'required_for':required_for,'failure_effect':failure_effect,'max_credit_transmitted':max_credit})
        existing.add(key)
    route_rows=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings=json.loads((root/'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    for row in route_rows:
        rid=row.get('route_id',''); effect=row.get('promotion_ceiling','S3') or row.get('authority_state','S3')
        for pid in row.get('prospective_prediction_ids', []):
            add('prospective-prediction', pid, 'route', rid, 'prospective-prediction-condition', 'route prospective prediction / temporal holdout denominator', 'cap predicted, forecast, temporal-holdout, severe-test, or prediction wording when timing/postdiction control fails', effect)
        for prid in row.get('preregistration_protocol_ids', []):
            add('preregistration-protocol', prid, 'route', rid, 'preregistration-protocol-condition', 'route preregistration / pre-analysis protocol denominator', 'cap preregistered, registered-report, pre-analysis-plan, and protocol wording when registration or adherence control fails', effect)
        for bid in row.get('blinding_deviation_ids', []):
            add('blinding-deviation', bid, 'route', rid, 'blinding-deviation-condition', 'route blinding / unblinding / protocol-deviation denominator', 'cap blind-analysis, unblinded, confirmatory, exploratory, severe-test, or deviation-disclosure wording when blinding/deviation control fails', effect)
    for binding in bindings:
        target_id=binding.get('claim_or_oq_id','')
        target_kind='open-question' if target_id.startswith('OQ-') else 'claim'
        effect=binding.get('maximum_authority_effect','no route promotion')
        for pid in binding.get('prospective_prediction_ids', []):
            add('prospective-prediction', pid, target_kind, target_id, 'prospective-prediction-claim-condition', f'claim prospective-prediction denominator under {binding.get("binding_id")}', 'freeze prediction/forecast claim wording until prospective-prediction rows are restored', effect)
        for prid in binding.get('preregistration_protocol_ids', []):
            add('preregistration-protocol', prid, target_kind, target_id, 'preregistration-protocol-claim-condition', f'claim preregistration-protocol denominator under {binding.get("binding_id")}', 'freeze preregistered/registered-report/protocol claim wording until preregistration rows are restored', effect)
        for bid in binding.get('blinding_deviation_ids', []):
            add('blinding-deviation', bid, target_kind, target_id, 'blinding-deviation-claim-condition', f'claim blinding-deviation denominator under {binding.get("binding_id")}', 'freeze blinding/unblinding/deviation claim wording until blinding-deviation rows are restored', effect)
    graph['edge_count']=len(rows)
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json prospective/preregistration/blinding edges')


def write_prospective_preregistration_blinding_summary(root: Path) -> None:
    p=json.loads((root/'PROSPECTIVE-PREDICTION-LEDGER.json').read_text())
    r=json.loads((root/'PREREGISTRATION-PROTOCOL-LEDGER.json').read_text())
    b=json.loads((root/'BLINDING-DEVIATION-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    prow=p.get('prospective_prediction_rows', []); rrow=r.get('preregistration_protocol_rows', []); brow=b.get('blinding_deviation_rows', [])
    def counts(rows,key):
        out={}
        for row in rows:
            val=row.get(key,'<missing>'); out[val]=out.get(val,0)+1
        return out
    lines=['# Prospective prediction / preregistration / blinding summary (generated)', '', 'Generated from `PROSPECTIVE-PREDICTION-LEDGER.json`, `PREREGISTRATION-PROTOCOL-LEDGER.json`, `BLINDING-DEVIATION-LEDGER.json`, and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{p.get('revision','<missing>')}`", f"- Prospective-prediction rows: `{len(prow)}`", f"- Preregistration-protocol rows: `{len(rrow)}`", f"- Blinding/deviation rows: `{len(brow)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for row in routes if row.get('authority_state') in ['S4','S5'])}`", '', '## Prospective-prediction class counts', '']
    for k,v in sorted(counts(prow,'prospective_prediction_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Preregistration-protocol class counts', '']
    for k,v in sorted(counts(rrow,'preregistration_protocol_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Blinding/deviation class counts', '']
    for k,v in sorted(counts(brow,'blinding_deviation_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Route handle counts', '', '| Route | Prospective | Preregistration | Blinding/deviation |', '|---|---:|---:|---:|']
    for row in routes:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('prospective_prediction_ids', []))}` | `{len(row.get('preregistration_protocol_ids', []))}` | `{len(row.get('blinding_deviation_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Prospective-prediction, preregistration-protocol, and blinding/deviation rows make prediction, forecast, preregistration, registered-report, blind-analysis, unblinding, confirmatory, severe-test, and protocol-deviation language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, benchmark/evaluation, selection/multiplicity, public-record, measurement, observed-sector, and residual-control ledgers.', '']
    (root/'docs/30-program/prospective-preregistration-blinding-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/prospective-preregistration-blinding-summary.generated.md')


def write_release_navigation_freshness_audit(root: Path) -> None:
    manifest=json.loads((root/'RELEASE-MANIFEST.json').read_text())
    receipt=json.loads((root/'REVISION-RECEIPT.json').read_text())
    rev=manifest.get('revision','<missing>')
    slug=manifest.get('slug','<missing>')
    bundle=manifest.get('bundle','<missing>')
    surfaces=['README.md','START_HERE.md','ARCHIVE_INDEX.md','CHANGELOG.md','SURFACE-STATUS.json','REVISION-RECEIPT.json','RELEASE-MANIFEST.json','context-pack.json','docs/00-meta/trajectory-map.md','docs/40-model/current-head-control-router.md']
    checks=[]
    for rel in surfaces:
        path=root/rel
        present=path.exists()
        text=path.read_text(errors='replace') if present else ''
        checks.append((rel, present, rev in text, slug in text or rel in {'SURFACE-STATUS.json','RELEASE-MANIFEST.json','REVISION-RECEIPT.json','context-pack.json'}, bundle in text or rel in {'README.md','START_HERE.md','context-pack.json','RELEASE-MANIFEST.json','REVISION-RECEIPT.json','SURFACE-STATUS.json'}))
    failures=[c for c in checks if not (c[1] and c[2] and c[3] and c[4])]
    lines=['# Release-navigation freshness audit (generated)', '', 'Generated from `RELEASE-MANIFEST.json`, `REVISION-RECEIPT.json`, and core navigation surfaces. Do not edit directly; run `make index` after changing release identity or navigation surfaces.', '', f"- Manifest revision: `{rev}`", f"- Manifest slug: `{slug}`", f"- Surfaces checked: `{len(checks)}`", f"- Navigation freshness failures: `{len(failures)}`", '', '| Surface | Present | Contains revision | Contains slug or exempt | Contains bundle where required |', '|---|---:|---:|---:|---:|']
    for rel,present,has_rev,has_slug,has_bundle in checks:
        lines.append(f"| `{rel}` | `{str(present).lower()}` | `{str(has_rev).lower()}` | `{str(has_slug).lower()}` | `{str(has_bundle).lower()}` |")
    if failures:
        lines += ['', '## Failures', '']
        for rel,present,has_rev,has_slug,has_bundle in failures:
            lines.append(f'- `{rel}` present={present} revision={has_rev} slug-or-exempt={has_slug} bundle-where-required={has_bundle}')
    lines += ['', '## Rule', '', 'Human and machine entry surfaces must not lag the manifest/receipt release identity. This audit creates no scientific support; it only prevents stale navigation from misrouting a restart.', '']
    (root/'docs/30-program/release-navigation-freshness-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/release-navigation-freshness-audit.generated.md')


def ensure_registered_route_binding_edges(root: Path) -> None:
    """Fast registry-driven edge repair for route-local-plus-wrapper handles.

    This replaces the need to replay every historical graph augmentation when a
    release only needs registered route/binding handle edges refreshed.
    """
    graph_path = root / 'AUTHORITY-DEPENDENCY-GRAPH.json'
    graph = load_authority_graph(graph_path)
    manifest = json.loads((root / 'RELEASE-MANIFEST.json').read_text())
    registry = json.loads((root / 'LEDGER-FAMILY-REGISTRY.json').read_text())
    routes = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    bindings = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text()).get('binding_rows', [])
    rows = graph.setdefault('edge_rows', [])
    existing = {(r.get('source_kind'), r.get('source_id'), r.get('dependent_kind'), r.get('dependent_id'), r.get('dependency_kind')) for r in rows}
    def source_kind_for_field(field: str) -> str:
        overrides={'backreaction_consistency_ids':'semiclassical-backreaction'}
        if field in overrides:
            return overrides[field]
        return field[:-4].replace('_','-') if field.endswith('_ids') else field.replace('_','-')
    def next_edge_id() -> str:
        return f"EDGE-{len(rows)+1:05d}"
    def add(sk, sid, dk, did, depkind, required_for, failure_effect, max_credit):
        if not sid or not did:
            return
        key = (sk, sid, dk, did, depkind)
        if key in existing:
            return
        rows.append({
            'edge_id': next_edge_id(),
            'source_kind': sk,
            'source_id': sid,
            'dependent_kind': dk,
            'dependent_id': did,
            'dependency_kind': depkind,
            'required_for': required_for,
            'failure_effect': failure_effect,
            'max_credit_transmitted': max_credit,
        })
        existing.add(key)
    for fam in registry.get('registry_rows', []):
        if fam.get('cardinality_policy') != 'route-local-plus-wrapper':
            continue
        for field in fam.get('route_fields', []):
            if not field.endswith('_ids'):
                continue
            sk = source_kind_for_field(field)
            for route in routes:
                rid = route.get('route_id','')
                effect = route.get('promotion_ceiling') or route.get('authority_state') or 'bounded by route row'
                for sid in route.get(field, []):
                    add(sk, sid, 'route', rid, f'{sk}-condition', f'route {sk} denominator via {fam.get("family_id")}', f'cap or freeze {sk} wording when the registered row fails', effect)
            for binding in bindings:
                tid = binding.get('claim_or_oq_id','')
                tk = 'open-question' if tid.startswith('OQ-') else 'claim'
                effect = binding.get('maximum_authority_effect','bounded by binding row')
                for sid in binding.get(field, []):
                    add(sk, sid, tk, tid, f'{sk}-claim-condition', f'claim {sk} denominator under {binding.get("binding_id")}', f'freeze {sk} claim wording until the registered row is restored', effect)
    graph['revision'] = manifest.get('revision', graph.get('revision'))
    graph['edge_count'] = len(rows)
    rule = graph.get('generation_rule','')
    marker = ' Registered route/binding handle edges are repaired by the rev0313 fast registry-driven edge pass.'
    if marker.strip() not in rule:
        graph['generation_rule'] = rule + marker
    write_authority_graph(graph_path, graph)
    print('wrote AUTHORITY-DEPENDENCY-GRAPH.json registered route/binding edges')



SUPERSEDED_AUTHORITY_GRAPH_AUGMENTS = {
    # The rev0312 prospective/preregistration/blinding pass is intentionally
    # superseded by the rev0313 registry-driven route/binding edge repair. The
    # registry pass covers the same route-local-plus-wrapper keys and also
    # handles the later unit/constant/scale and uncertainty/significance/coverage
    # families. Replaying both in the wrong order changes wording for identical
    # dependency keys without adding rollback coverage.
    'augment_authority_dependency_graph_with_prospective_preregistration_blinding_edges',
}


def _authority_graph_augmentation_functions() -> list[tuple[int, str, object]]:
    funcs = []
    for name, obj in globals().items():
        if not name.startswith('augment_authority_dependency_graph'):
            continue
        if name in SUPERSEDED_AUTHORITY_GRAPH_AUGMENTS:
            continue
        funcs.append((obj.__code__.co_firstlineno, name, obj))
    return sorted(funcs)


def replay_authority_dependency_graph(root: Path, *, write: bool = False, quiet: bool = False) -> dict:
    """Rebuild the authority graph from source ledgers in memory.

    The older augmentation functions were written as load/append/write passes,
    which made full replay slow because each pass re-serialized the large graph.
    This wrapper monkey-patches only this module's graph load/write functions
    during replay, keeps the graph in memory, runs the non-superseded historical
    augmenters in source order, then applies the registry-driven route/binding
    repair once. When ``write`` is true, one compact graph is emitted at the end.
    """

    def run() -> dict:
        graph_state: dict[str, dict] = {}
        original_write = globals()['write_authority_graph']
        original_load = globals()['load_authority_graph']

        def memory_write(path, graph, *args, **kwargs):  # noqa: ANN001 - local shim mirrors imported writer
            graph_state['graph'] = graph

        def memory_load(path):  # noqa: ANN001 - local shim mirrors imported loader
            if 'graph' not in graph_state:
                raise RuntimeError('authority graph replay attempted to load before base graph generation')
            return graph_state['graph']

        try:
            globals()['write_authority_graph'] = memory_write
            globals()['load_authority_graph'] = memory_load
            write_authority_dependency_graph(root)
            for _lineno, _name, func in _authority_graph_augmentation_functions():
                func(root)
            ensure_registered_route_binding_edges(root)
        finally:
            globals()['write_authority_graph'] = original_write
            globals()['load_authority_graph'] = original_load

        graph = graph_state.get('graph')
        if graph is None:
            raise RuntimeError('authority graph replay produced no graph')
        graph['edge_count'] = len(graph.get('edge_rows', []))
        # Keep generated_from honest: replay depends on the base graph sources,
        # the family registry, and every registered route-support ledger whose
        # handles can add route/binding edges through the registry repair.
        sources: list[str] = []
        def remember_source(rel: str) -> None:
            if rel and rel not in sources:
                sources.append(rel)
        for rel in graph.get('generated_from', []):
            remember_source(rel)
        remember_source('LEDGER-FAMILY-REGISTRY.json')
        for rel in [
            'PROMOTION-GATE-LEDGER.json',
            'OBSERVED-SECTOR-RECOVERY-LEDGER.json',
            'DISCRIMINATOR-FORECAST-LEDGER.json',
            'DECISION-EXPERIMENT-LEDGER.json',
            'EMPIRICAL-DELTA-LEDGER.json',
        ]:
            remember_source(rel)
        registry_path = root / 'LEDGER-FAMILY-REGISTRY.json'
        if registry_path.exists():
            registry = json.loads(registry_path.read_text())
            for fam in registry.get('registry_rows', []):
                for rel in fam.get('ledger_files', []):
                    remember_source(rel)
        graph['generated_from'] = sources
        graph.setdefault('generation_rule', '')
        replay_marker = ' Full authority graph replay is performed in memory by replay_authority_dependency_graph; compact JSON is written once after source-ledger reconstruction.'
        if replay_marker.strip() not in graph['generation_rule']:
            graph['generation_rule'] += replay_marker
        if write:
            original_write(root / 'AUTHORITY-DEPENDENCY-GRAPH.json', graph)
            print('rebuilt AUTHORITY-DEPENDENCY-GRAPH.json from source ledgers')
        return graph

    if quiet:
        with contextlib.redirect_stdout(io.StringIO()):
            return run()
    return run()

def write_unit_constant_scale_summary(root: Path) -> None:
    u=json.loads((root/'UNIT-CONVENTION-LEDGER.json').read_text())
    c=json.loads((root/'FUNDAMENTAL-CONSTANT-LEDGER.json').read_text())
    s=json.loads((root/'SCALE-SETTING-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    ur=u.get('unit_convention_rows', []); cr=c.get('fundamental_constant_rows', []); sr=s.get('scale_setting_rows', [])
    def counts(rows,key):
        out={}
        for row in rows:
            val=row.get(key,'<missing>'); out[val]=out.get(val,0)+1
        return out
    lines=['# Unit convention / fundamental constant / scale-setting summary (generated)', '', 'Generated from `UNIT-CONVENTION-LEDGER.json`, `FUNDAMENTAL-CONSTANT-LEDGER.json`, and `SCALE-SETTING-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{u.get('revision','<missing>')}`", f"- Unit-convention rows: `{len(ur)}`", f"- Fundamental-constant rows: `{len(cr)}`", f"- Scale-setting rows: `{len(sr)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Unit-convention class counts', '']
    for k,v in sorted(counts(ur,'unit_convention_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Fundamental-constant class counts', '']
    for k,v in sorted(counts(cr,'fundamental_constant_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Scale-setting class counts', '']
    for k,v in sorted(counts(sr,'scale_setting_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Route handle counts', '', '| Route | Unit conventions | Constants | Scale rows |', '|---|---:|---:|---:|']
    for row in routes:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('unit_convention_ids', []))}` | `{len(row.get('fundamental_constant_ids', []))}` | `{len(row.get('scale_setting_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Unit-convention, fundamental-constant, and scale-setting rows make natural-units, Planck-units, dimensional-analysis, defining-constant, dimensionless-ratio, CODATA/SI, constant-prediction, hierarchy, naturalness, and scale-setting language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, measurement, renormalization, matter, cosmology, public-record, observed-sector, and residual-control ledgers.', '']
    (root/'docs/30-program/unit-constant-scale-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/unit-constant-scale-summary.generated.md')



def write_decision_forecast_route_edge_audit(root: Path) -> None:
    routes = json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    forecasts = json.loads((root/'DISCRIMINATOR-FORECAST-LEDGER.json').read_text()).get('forecast_rows', [])
    decisions = json.loads((root/'DECISION-EXPERIMENT-LEDGER.json').read_text()).get('decision_experiments', [])
    graph = load_authority_graph(root/'AUTHORITY-DEPENDENCY-GRAPH.json')
    edges = {
        (edge.get('source_kind'), edge.get('source_id'), edge.get('dependent_kind'), edge.get('dependent_id'), edge.get('dependency_kind'))
        for edge in graph.get('edge_rows', [])
    }
    forecast_by_route: dict[str, list[str]] = {}
    decision_by_route: dict[str, list[str]] = {}
    failures: list[str] = []
    for row in forecasts:
        fid = row.get('forecast_id', '')
        rid = row.get('route_id', '')
        forecast_by_route.setdefault(rid, []).append(fid)
        key = ('forecast', fid, 'route', rid, 'forecast-route-condition')
        if key not in edges:
            failures.append(f'missing forecast route edge `{fid}` -> `{rid}`')
    for exp in decisions:
        eid = exp.get('experiment_id', '')
        for rid in exp.get('route_ids', []):
            decision_by_route.setdefault(rid, []).append(eid)
            key = ('decision-experiment', eid, 'route', rid, 'decision-experiment-route-condition')
            if key not in edges:
                failures.append(f'missing decision-experiment route edge `{eid}` -> `{rid}`')
    uncovered = []
    lacking_decision = []
    s2_plus_lacking_forecast = []
    for route in routes:
        rid = route.get('route_id', '')
        state = route.get('authority_state', '')
        has_forecast = bool(forecast_by_route.get(rid))
        has_decision = bool(decision_by_route.get(rid))
        if not has_forecast and not has_decision:
            uncovered.append(rid)
            failures.append(f'route `{rid}` has no route-facing forecast or decision-experiment row')
        if state in {'S2','S3','S4','S5'} and not has_forecast:
            s2_plus_lacking_forecast.append(rid)
            failures.append(f'route `{rid}` at `{state}` has no route-facing discriminator forecast row')
        if not has_decision:
            lacking_decision.append(rid)
            failures.append(f'route `{rid}` has no route-facing decision-experiment row')
    lines = [
        '# Decision / forecast route-edge audit (generated)',
        '',
        'Generated from `CANDIDATE-ROUTE-STATE-LEDGER.json`, `DISCRIMINATOR-FORECAST-LEDGER.json`, `DECISION-EXPERIMENT-LEDGER.json`, and `AUTHORITY-DEPENDENCY-GRAPH.json`. Do not edit directly; run `make index` after changing route-facing decision surfaces.',
        '',
        f'- Route rows: `{len(routes)}`',
        f'- Forecast rows: `{len(forecasts)}`',
        f'- Decision experiments: `{len(decisions)}`',
        f'- Routes lacking both route-facing forecast and decision rows: `{len(uncovered)}`',
        f'- S2-or-higher routes lacking route-facing forecast rows: `{len(s2_plus_lacking_forecast)}`',
        f'- Routes lacking route-facing decision-experiment rows: `{len(lacking_decision)}`',
        f'- Edge/audit failures: `{len(failures)}`',
        '',
        '| Route | Authority | Forecast rows | Decision experiments |',
        '|---|---:|---:|---:|',
    ]
    for route in routes:
        rid = route.get('route_id', '')
        lines.append(
            f"| `{rid}` | `{route.get('authority_state', '')}` | `{len(forecast_by_route.get(rid, []))}` | `{len(decision_by_route.get(rid, []))}` |"
        )
    if failures:
        lines += ['', '## Failures', '']
        for item in failures:
            lines.append(f'- {item}')
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'This audit forces route-facing decision and forecast pressure to remain connected to the authority graph. It does not promote a route; it prevents an S2-or-higher candidate lane from surviving as a decision-only or pure-narrative corridor after its forecast handles disappear.',
        '',
    ]
    (root/'docs/30-program/decision-forecast-route-edge-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/decision-forecast-route-edge-audit.generated.md')


def write_empirical_delta_route_edge_audit(root: Path) -> None:
    routes = json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    deltas = json.loads((root/'EMPIRICAL-DELTA-LEDGER.json').read_text()).get('empirical_deltas', [])
    graph = load_authority_graph(root/'AUTHORITY-DEPENDENCY-GRAPH.json')
    edges = {
        (edge.get('source_kind'), edge.get('source_id'), edge.get('dependent_kind'), edge.get('dependent_id'), edge.get('dependency_kind'))
        for edge in graph.get('edge_rows', [])
    }
    delta_by_route: dict[str, list[str]] = {row.get('route_id', ''): [] for row in routes}
    failures: list[str] = []
    for delta in deltas:
        did = delta.get('delta_id', '')
        for rid in delta.get('route_ids', []):
            delta_by_route.setdefault(rid, []).append(did)
            key = ('empirical-delta', did, 'route', rid, 'empirical-delta-route-condition')
            if key not in edges:
                failures.append(f'missing empirical-delta route edge `{did}` -> `{rid}`')
    s2_plus_uncovered = []
    any_uncovered = []
    for route in routes:
        rid = route.get('route_id', '')
        state = route.get('authority_state', '')
        if not delta_by_route.get(rid):
            any_uncovered.append(rid)
            if state in {'S2','S3','S4','S5'}:
                s2_plus_uncovered.append(rid)
                failures.append(f'route `{rid}` at `{state}` has no empirical-delta/source-pressure row')
    lines = [
        '# Empirical-delta route-edge audit (generated)',
        '',
        'Generated from `CANDIDATE-ROUTE-STATE-LEDGER.json`, `EMPIRICAL-DELTA-LEDGER.json`, and `AUTHORITY-DEPENDENCY-GRAPH.json`. Do not edit directly; run `make index` after changing empirical-delta or route ledgers.',
        '',
        f'- Route rows: `{len(routes)}`',
        f'- Empirical deltas: `{len(deltas)}`',
        f'- S2-or-higher routes lacking empirical-delta rows: `{len(s2_plus_uncovered)}`',
        f'- Routes lacking any empirical-delta row: `{len(any_uncovered)}`',
        f'- Edge/audit failures: `{len(failures)}`',
        '',
        '| Route | Authority | Empirical-delta rows |',
        '|---|---:|---:|',
    ]
    for route in routes:
        rid = route.get('route_id', '')
        lines.append(f"| `{rid}` | `{route.get('authority_state', '')}` | `{len(delta_by_route.get(rid, []))}` |")
    if failures:
        lines += ['', '## Failures', '']
        for item in failures:
            lines.append(f'- {item}')
    lines += [
        '',
        '## Non-promotion rule',
        '',
        'This audit forces empirical/source-pressure deltas to remain route-facing in the authority graph. It does not promote a route; it prevents S2+ lanes from surviving as forecast, method, or narrative corridors after their empirical-delta handles disappear.',
        '',
    ]
    (root/'docs/30-program/empirical-delta-route-edge-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/empirical-delta-route-edge-audit.generated.md')


def write_frontier_source_freshness_audit(root: Path) -> None:
    _write_frontier_source_freshness_audit(root)
    print('wrote docs/30-program/frontier-source-freshness-audit.generated.md')

def write_forecast_credit_realization_audit(root: Path) -> None:
    _write_forecast_credit_realization_audit(root)


def write_familyc_subregion_state_audit(root: Path) -> None:
    _write_familyc_subregion_state_audit(root)


def write_release_chronology_consistency_audit(root: Path) -> None:
    manifest=json.loads((root/'RELEASE-MANIFEST.json').read_text())
    receipt=json.loads((root/'REVISION-RECEIPT.json').read_text())
    changelog=(root/'CHANGELOG.md').read_text()
    rev=manifest.get('revision','<missing>')
    prev=manifest.get('previous_revision','<missing>')
    bundle=manifest.get('bundle','<missing>')
    checks=[]
    checks.append(('manifest-revision-present', rev.startswith('rev')))
    checks.append(('receipt-revision-matches', receipt.get('revision')==rev))
    checks.append(('receipt-previous-matches', receipt.get('previous_revision')==prev))
    checks.append(('manifest-bundle-contains-revision', rev in bundle))
    checks.append(('manifest-bundle-contains-slug', manifest.get('slug','') in bundle))
    checks.append(('changelog-has-current-entry', f'## {rev} ' in changelog or f'## {rev} —' in changelog))
    checks.append(('changelog-has-previous-entry', f'## {prev} ' in changelog or f'## {prev} —' in changelog))
    checks.append(('receipt-packaged-release-matches', receipt.get('packaged_release')==bundle))
    failures=[name for name,ok in checks if not ok]
    lines=['# Release chronology consistency audit (generated)', '', 'Generated from `RELEASE-MANIFEST.json`, `REVISION-RECEIPT.json`, and `CHANGELOG.md`. Do not edit directly; run `make index` after changing release chronology.', '', f'- Manifest revision: `{rev}`', f'- Previous revision: `{prev}`', f'- Bundle: `{bundle}`', f'- Chronology checks: `{len(checks)}`', f'- Chronology failures: `{len(failures)}`', '', '| Check | Passed |', '|---|---:|']
    for name,ok in checks:
        lines.append(f'| `{name}` | `{str(ok).lower()}` |')
    if failures:
        lines += ['', '## Failures', '']
        for f in failures: lines.append(f'- `{f}`')
    lines += ['', '## Rule', '', 'Release chronology must keep the manifest, receipt, changelog, and bundle identity aligned. This audit creates no scientific support; it prevents stale release-history handles.', '']
    (root/'docs/30-program/release-chronology-consistency-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/release-chronology-consistency-audit.generated.md')



def write_uncertainty_significance_coverage_summary(root: Path) -> None:
    u=json.loads((root/'UNCERTAINTY-INTERVAL-LEDGER.json').read_text())
    s=json.loads((root/'SIGNIFICANCE-THRESHOLD-LEDGER.json').read_text())
    c=json.loads((root/'COVERAGE-CALIBRATION-LEDGER.json').read_text())
    routes=json.loads((root/'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text()).get('route_rows', [])
    ur=u.get('uncertainty_interval_rows', []); sr=s.get('significance_threshold_rows', []); cr=c.get('coverage_calibration_rows', [])
    def counts(rows,key):
        out={}
        for row in rows:
            val=row.get(key,'<missing>'); out[val]=out.get(val,0)+1
        return out
    lines=['# Uncertainty interval / significance threshold / coverage calibration summary (generated)', '', 'Generated from `UNCERTAINTY-INTERVAL-LEDGER.json`, `SIGNIFICANCE-THRESHOLD-LEDGER.json`, and `COVERAGE-CALIBRATION-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.', '', f"- Revision: `{u.get('revision','<missing>')}`", f"- Uncertainty-interval rows: `{len(ur)}`", f"- Significance-threshold rows: `{len(sr)}`", f"- Coverage-calibration rows: `{len(cr)}`", f"- Route rows: `{len(routes)}`", f"- S4/S5 routes: `{sum(1 for r in routes if r.get('authority_state') in ['S4','S5'])}`", '', '## Uncertainty-interval class counts', '']
    for k,v in sorted(counts(ur,'uncertainty_interval_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Significance-threshold class counts', '']
    for k,v in sorted(counts(sr,'significance_threshold_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Coverage-calibration class counts', '']
    for k,v in sorted(counts(cr,'coverage_calibration_class').items()): lines.append(f'- `{k}`: `{v}`')
    lines += ['', '## Route handle counts', '', '| Route | Intervals | Significance | Coverage/calibration |', '|---|---:|---:|---:|']
    for row in routes:
        lines.append(f"| `{row.get('route_id')}` | `{len(row.get('uncertainty_interval_ids', []))}` | `{len(row.get('significance_threshold_ids', []))}` | `{len(row.get('coverage_calibration_ids', []))}` |")
    lines += ['', '## Non-promotion rule', '', 'Uncertainty-interval, significance-threshold, and coverage-calibration rows make error bars, contours, confidence/credible intervals, p-values, sigma thresholds, discovery/exclusion conventions, nominal coverage, posterior calibration, and reliability diagnostics auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, likelihood/prior, measurement, selection, multiplicity, benchmark, stochastic, public-record, observed-sector, or residual-control ledgers.', '']
    (root/'docs/30-program/uncertainty-significance-coverage-summary.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/uncertainty-significance-coverage-summary.generated.md')


def write_bibliography_reference_sequence_audit(root: Path) -> None:
    bib=(root/'docs/00-meta/bibliography.md').read_text()
    retired=(root/'docs/00-meta/ref-id-retirement-ledger.md').read_text() if (root/'docs/00-meta/ref-id-retirement-ledger.md').exists() else ''
    ids=[int(x) for x in re.findall(r'^- `REF-(\d{4})`', bib, flags=re.MULTILINE)]
    retired_ids={int(x) for x in re.findall(r'`REF-(\d{4})`', retired)}
    duplicates=sorted({i for i in ids if ids.count(i)>1})
    max_id=max(ids) if ids else 0
    present=set(ids)
    missing=[i for i in range(1,max_id+1) if i not in present]
    unaccounted=[i for i in missing if i not in retired_ids]
    lines=['# Bibliography reference sequence audit (generated)', '', 'Generated from `docs/00-meta/bibliography.md` and `docs/00-meta/ref-id-retirement-ledger.md`. Do not edit directly; run `make index` after bibliography changes.', '', f'- Bibliography REF ids observed: `{len(ids)}`', f'- Distinct bibliography REF ids: `{len(present)}`', f'- Max REF id: `REF-{max_id:04d}`', f'- Duplicate REF ids: `{len(duplicates)}`', f'- Missing REF ids up to max: `{len(missing)}`', f'- Missing REF ids accounted for in retirement ledger: `{sum(1 for i in missing if i in retired_ids)}`', f'- Unaccounted missing REF ids: `{len(unaccounted)}`', '', '## Rule', '', 'Bibliography identifiers should be monotone, non-duplicated, and gap-accounted. This audit creates no scientific support; it protects source custody and restart reliability.', '']
    if duplicates:
        lines += ['## Duplicate REF ids', '']
        for i in duplicates: lines.append(f'- `REF-{i:04d}`')
    if unaccounted:
        lines += ['', '## Unaccounted missing REF ids', '']
        for i in unaccounted: lines.append(f'- `REF-{i:04d}`')
    (root/'docs/30-program/bibliography-reference-sequence-audit.generated.md').write_text('\n'.join(lines)+'\n')
    print('wrote docs/30-program/bibliography-reference-sequence-audit.generated.md')



def write_release_package_path_audit(root: Path) -> None:
    """Render a compact audit of the executable release path."""
    makefile = (root / 'Makefile').read_text()
    package_release = (root / 'tools/package_release.py').read_text()
    smoke_path = root / 'tools/smoke_package_release.py'
    smoke = smoke_path.read_text() if smoke_path.exists() else ''

    def target_header(target: str) -> str:
        for line in makefile.splitlines():
            if re.match(rf'^{re.escape(target)}\s*:', line):
                return line.strip()
        return ''

    def target_body(target: str) -> list[str]:
        lines = makefile.splitlines()
        body: list[str] = []
        in_target = False
        for line in lines:
            if re.match(rf'^{re.escape(target)}\s*:', line):
                in_target = True
                continue
            if in_target:
                if line and not line.startswith(('\t', ' ')) and re.match(r'^[A-Za-z0-9_-]+\s*:', line):
                    break
                if line.strip():
                    body.append(line.strip())
        return body

    header = target_header('package')
    body = target_body('package')
    body_text = '\n'.join(body)
    deps = set(header.split(':', 1)[1].split()) if ':' in header else set()
    checks = [
        ('package-target-depends-on-index', 'index' in deps),
        ('package-target-depends-on-lint', 'lint' in deps),
        ('package-target-builds-zip', 'tools/package_release.py' in body_text),
        ('package-target-smokes-zip-after-build', 'tools/smoke_package_release.py' in body_text and body_text.find('tools/smoke_package_release.py') > body_text.find('tools/package_release.py')),
        ('package-excludes-nested-zips', '.zip' in package_release and 'TRANSIENT_FILE_SUFFIXES' in package_release),
        ('package-writes-sorted-path-order', 'sorted(' in package_release and 'relative_to(root).as_posix()' in package_release),
        ('package-fixes-zip-metadata', 'ZipInfo' in package_release and 'manifest_zip_date_time' in package_release),
        ('smoke-tool-present', smoke_path.exists()),
        ('smoke-extracts-and-lints-package', '["make", "lint"]' in smoke),
        ('smoke-rebuilds-package-from-extract', 'tools/package_release.py' in smoke and 'rebuilt_sha' in smoke),
        ('smoke-compares-package-sha256', 'sha256_file' in smoke and 'original_sha' in smoke),
    ]
    failures = [name for name, ok in checks if not ok]
    manifest = json.loads((root / 'RELEASE-MANIFEST.json').read_text())
    lines = [
        '# Release package path audit (generated)',
        '',
        'Generated from `Makefile`, `tools/package_release.py`, and `tools/smoke_package_release.py`. Do not edit directly; run `make index` after changing release tooling.',
        '',
        f"- Manifest revision: `{manifest.get('revision', '<missing>')}`",
        f'- Package-path checks: `{len(checks)}`',
        f'- Package-path failures: `{len(failures)}`',
        '',
        '| Check | Passed |',
        '|---|---:|',
    ]
    for name, ok in checks:
        lines.append(f'| `{name}` | `{str(ok).lower()}` |')
    if failures:
        lines += ['', '## Failures', '']
        for item in failures:
            lines.append(f'- `{item}`')
    lines += [
        '',
        '## Rule',
        '',
        '`make package` is a release boundary, not a convenience zip command. It must regenerate generated surfaces, lint the source tree, build deterministic archive bytes, extract the package, lint the extracted tree, and rebuild byte-identically from the extracted contents. This audit creates no scientific support; it prevents stale or non-replayable cube releases.',
        '',
    ]
    (root / 'docs/30-program/release-package-path-audit.generated.md').write_text('\n'.join(lines))
    print('wrote docs/30-program/release-package-path-audit.generated.md')


def write_frontier_source_custody_isolation_audit(root: Path) -> None:
    _write_frontier_source_custody_isolation_audit(root)


def write_graviton_source_role_audit(root: Path) -> None:
    _write_graviton_source_role_audit(root)


def write_route_realization_status_audit(root: Path) -> None:
    _write_route_realization_status_audit(root)


def write_amplitudes_gravity_bootstrap_audit(root: Path) -> None:
    _write_amplitudes_gravity_bootstrap_audit(root)


def write_asymptotic_safety_observable_audit(root: Path) -> None:
    _write_asymptotic_safety_observable_audit(root)


def write_evidence_delta_handoff_audit(root: Path) -> None:
    _write_evidence_delta_handoff_audit(root)

def write_learned_inverse_ood_audit(root: Path) -> None:
    _write_learned_inverse_ood_audit(root)
    print('wrote docs/30-program/learned-inverse-ood-audit.generated.md')

def write_stringm_observed_sector_audit(root: Path) -> None:
    _write_stringm_observed_sector_audit(root)
    print('wrote docs/30-program/stringm-observed-sector-atlas-audit.generated.md')

def write_route_condition_ceiling_audit(root: Path) -> None:
    _write_route_condition_ceiling_audit(root)
    print('wrote docs/30-program/route-condition-ceiling-audit.generated.md')


def write_gw_strongfield_public_test_audit(root: Path) -> None:
    _write_gw_strongfield_public_test_audit(root)
    print('wrote docs/30-program/gw-strongfield-public-test-source-role-audit.generated.md')

def write_qrf_frame_transport_audit(root: Path) -> None:
    _write_qrf_frame_transport_audit(root)
    print('wrote docs/30-program/qrf-frame-transport-source-role-audit.generated.md')



def write_causal_set_matter_horizon_audit(root: Path) -> None:
    _write_causal_set_matter_horizon_audit(root)
    print('wrote docs/30-program/causal-set-matter-horizon-source-role-audit.generated.md')

def write_familyb_thermo_entropy_audit(root: Path) -> None:
    _write_familyb_thermo_entropy_audit(root)
    print('wrote docs/30-program/familyb-thermo-entropy-source-role-audit.generated.md')

def write_cmb_bmode_source_role_audit(root: Path) -> None:
    _write_cmb_bmode_source_role_audit(root)
    print('wrote docs/30-program/cmb-bmode-source-role-audit.generated.md')



def write_cosmology_source_role_audit(root: Path) -> None:
    _write_cosmology_source_role_audit(root)


def write_familyc_finite_n_reconstruction_audit(root: Path) -> None:
    _write_familyc_finite_n_reconstruction_audit(root)
    print('wrote docs/30-program/familyc-finite-n-reconstruction-source-role-audit.generated.md')

def write_lab_gie_bmv_source_role_audit(root: Path) -> None:
    _write_lab_gie_bmv_source_role_audit(root)


def write_claim_language_current_boundary_audit(root: Path) -> None:
    _write_claim_language_current_boundary_audit(root)
    print('wrote docs/30-program/claim-language-current-boundary-audit.generated.md')

def write_credit_allocation_current_boundary_audit(root: Path) -> None:
    _write_credit_allocation_current_boundary_audit(root)
    print('wrote docs/30-program/credit-allocation-current-boundary-audit.generated.md')


def write_observed_sector_matter_audit(root: Path) -> None:
    _write_observed_sector_matter_audit(root)
    print('wrote docs/30-program/observed-sector-matter-source-role-audit.generated.md')


def write_classical_gr_observed_sector_audit(root: Path) -> None:
    _write_classical_gr_observed_sector_audit(root)
    print('wrote docs/30-program/classical-gr-observed-sector-source-role-audit.generated.md')

def write_route_pressure_mirror_audit(root: Path) -> None:
    _write_route_pressure_mirror_audit(root)
    print('wrote docs/30-program/route-pressure-mirror-audit.generated.md')


def write_dark_sector_constraint_audit(root: Path) -> None:
    _write_dark_sector_constraint_audit(root)
    print('wrote docs/30-program/dark-sector-constraint-source-role-audit.generated.md')

def write_negative_control_route_overlap_audit(root: Path) -> None:
    _write_negative_control_route_overlap_audit(root)
    print('wrote docs/30-program/negative-control-route-overlap-audit.generated.md')


def write_qm_qft_observed_sector_audit(root: Path) -> None:
    _write_qm_qft_observed_sector_audit(root)
    print('wrote docs/30-program/qm-qft-observed-sector-source-role-audit.generated.md')


def write_source_role_credit_cap_audit(root: Path) -> None:
    _write_source_role_credit_cap_audit(root)
    print('wrote docs/30-program/source-role-credit-cap-audit.generated.md')


def write_source_snapshot_manifest_audit(root: Path) -> None:
    _write_source_snapshot_manifest_audit(root)
    print('wrote docs/30-program/source-snapshot-manifest-audit.generated.md')


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sync_start_here(root)
    replay_authority_dependency_graph(root, write=True)
    # Run all registered summary writers after graph replay so route/claim support summaries see current edges.
    for name in sorted(n for n in globals() if n.startswith('write_') and n.endswith('_summary')):
        if name in {'write_archive_index'}:
            continue
        try:
            globals()[name](root)
        except FileNotFoundError:
            continue
    if (root / 'LEDGER-FAMILY-REGISTRY.json').exists():
        for name in sorted(n for n in globals() if n.startswith('write_') and n.endswith('_audit')):
            try:
                globals()[name](root)
            except FileNotFoundError:
                continue
    write_archive_index(root)


if __name__ == '__main__':
    main()
