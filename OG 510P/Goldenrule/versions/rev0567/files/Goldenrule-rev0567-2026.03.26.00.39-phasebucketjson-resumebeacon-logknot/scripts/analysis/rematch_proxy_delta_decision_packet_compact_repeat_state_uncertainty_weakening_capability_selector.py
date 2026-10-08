#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form import (
    REGIME_BANDS,
    normalize_weakening_threshold,
)

ROOT = Path(__file__).resolve().parents[2]
REPRESENTATIVE_THRESHOLDS = [band['representative_threshold_unique_appends'] for band in REGIME_BANDS]


class WeakeningCapabilitySelectorError(ValueError):
    pass


def capability_profile_for_threshold(threshold: int) -> dict[str, Any]:
    regime = normalize_weakening_threshold(threshold)
    stronger_eventual = set(regime['eventual_relaxed_anchor_states_from_stronger_tiers'])
    stronger_direct = set(regime['direct_relaxed_anchor_states_from_stronger_tiers'])
    middle_band_release = set(regime['middle_band_neutral_release_states'])

    return {
        'threshold_band_label': regime['threshold_band_label'],
        'threshold_unique_appends': regime['normalized_threshold_unique_appends'],
        'regime_code': regime['regime_code'],
        'regime_label': regime['regime_label'],
        'operator_summary': regime['operator_summary'],
        'capabilities': {
            'admits_any_relaxed_release_from_stronger_tiers': bool(stronger_eventual),
            'forbids_relaxed_basin_growth_beyond_neutral_exit': stronger_eventual.issubset({18}),
            'admits_middle_band_precision_relief': 2 in middle_band_release,
            'admits_neutral_anchor_relaxed_release_eventually': 13 in stronger_eventual,
            'admits_entry_boundary_relaxed_release_eventually': 8 in stronger_eventual,
            'admits_direct_entry_boundary_relaxed_release': 8 in stronger_direct,
            'admits_direct_precision_relaxed_release': 2 in stronger_direct,
        },
        'support_sets': {
            'eventual_relaxed_anchor_states_from_stronger_tiers': regime['eventual_relaxed_anchor_states_from_stronger_tiers'],
            'direct_relaxed_anchor_states_from_stronger_tiers': regime['direct_relaxed_anchor_states_from_stronger_tiers'],
            'middle_band_neutral_release_states': regime['middle_band_neutral_release_states'],
        },
        'closure_summary': regime['closure_summary'],
        'forced_one_shot_weakening_cases': regime['forced_one_shot_weakening_cases'],
    }



def capability_profiles() -> list[dict[str, Any]]:
    return [capability_profile_for_threshold(threshold) for threshold in REPRESENTATIVE_THRESHOLDS]



def _requirements_dict(
    *,
    require_any_relaxed_release_from_stronger_tiers: bool,
    require_middle_band_precision_relief: bool,
    require_neutral_anchor_relaxed_release: bool,
    require_direct_entry_boundary_relaxed_release: bool,
    require_direct_precision_relaxed_release: bool,
    forbid_relaxed_basin_growth_beyond_neutral_exit: bool,
) -> dict[str, bool]:
    return {
        'require_any_relaxed_release_from_stronger_tiers': require_any_relaxed_release_from_stronger_tiers,
        'require_middle_band_precision_relief': require_middle_band_precision_relief,
        'require_neutral_anchor_relaxed_release': require_neutral_anchor_relaxed_release,
        'require_direct_entry_boundary_relaxed_release': require_direct_entry_boundary_relaxed_release,
        'require_direct_precision_relaxed_release': require_direct_precision_relaxed_release,
        'forbid_relaxed_basin_growth_beyond_neutral_exit': forbid_relaxed_basin_growth_beyond_neutral_exit,
    }



def _matches(profile: dict[str, Any], requirements: dict[str, bool]) -> bool:
    caps = profile['capabilities']
    if requirements['require_any_relaxed_release_from_stronger_tiers'] and not caps['admits_any_relaxed_release_from_stronger_tiers']:
        return False
    if requirements['require_middle_band_precision_relief'] and not caps['admits_middle_band_precision_relief']:
        return False
    if requirements['require_neutral_anchor_relaxed_release'] and not caps['admits_neutral_anchor_relaxed_release_eventually']:
        return False
    if requirements['require_direct_entry_boundary_relaxed_release'] and not caps['admits_direct_entry_boundary_relaxed_release']:
        return False
    if requirements['require_direct_precision_relaxed_release'] and not caps['admits_direct_precision_relaxed_release']:
        return False
    if requirements['forbid_relaxed_basin_growth_beyond_neutral_exit'] and not caps['forbids_relaxed_basin_growth_beyond_neutral_exit']:
        return False
    return True



def _incompatibility_notes(requirements: dict[str, bool]) -> list[str]:
    notes: list[str] = []
    if requirements['forbid_relaxed_basin_growth_beyond_neutral_exit'] and requirements['require_neutral_anchor_relaxed_release']:
        notes.append('neutral-anchor relaxed release first appears at threshold 12, which enlarges the relaxed-floor basin beyond neutral exit boundary 18')
    if requirements['forbid_relaxed_basin_growth_beyond_neutral_exit'] and requirements['require_direct_entry_boundary_relaxed_release']:
        notes.append('direct entry-boundary relaxed release first appears at threshold 17, which necessarily enlarges the relaxed-floor basin beyond neutral exit boundary 18')
    if requirements['forbid_relaxed_basin_growth_beyond_neutral_exit'] and requirements['require_direct_precision_relaxed_release']:
        notes.append('direct precision-anchor relaxed release first appears at threshold 23, which necessarily enlarges the relaxed-floor basin beyond neutral exit boundary 18')
    return notes



def select_weakening_regime_by_capabilities(
    *,
    require_any_relaxed_release_from_stronger_tiers: bool = False,
    require_middle_band_precision_relief: bool = False,
    require_neutral_anchor_relaxed_release: bool = False,
    require_direct_entry_boundary_relaxed_release: bool = False,
    require_direct_precision_relaxed_release: bool = False,
    forbid_relaxed_basin_growth_beyond_neutral_exit: bool = False,
) -> dict[str, Any]:
    requirements = _requirements_dict(
        require_any_relaxed_release_from_stronger_tiers=require_any_relaxed_release_from_stronger_tiers,
        require_middle_band_precision_relief=require_middle_band_precision_relief,
        require_neutral_anchor_relaxed_release=require_neutral_anchor_relaxed_release,
        require_direct_entry_boundary_relaxed_release=require_direct_entry_boundary_relaxed_release,
        require_direct_precision_relaxed_release=require_direct_precision_relaxed_release,
        forbid_relaxed_basin_growth_beyond_neutral_exit=forbid_relaxed_basin_growth_beyond_neutral_exit,
    )

    for profile in capability_profiles():
        if not _matches(profile, requirements):
            continue
        return {
            'tool': str(Path(__file__).resolve()),
            'status': 'selected_named_regime',
            'requirements': requirements,
            'selected_threshold_unique_appends': profile['threshold_unique_appends'],
            'selected_threshold_band_label': profile['threshold_band_label'],
            'selected_regime_code': profile['regime_code'],
            'selected_regime_label': profile['regime_label'],
            'selected_operator_summary': profile['operator_summary'],
            'selected_capabilities': profile['capabilities'],
            'selected_support_sets': profile['support_sets'],
            'selected_closure_summary': profile['closure_summary'],
            'selection_reason': 'pick the smallest named weakening regime whose capability profile satisfies the requested operator promises',
        }

    return {
        'tool': str(Path(__file__).resolve()),
        'status': 'no_named_regime_satisfies_promises',
        'requirements': requirements,
        'incompatibility_notes': _incompatibility_notes(requirements),
        'considered_threshold_bands': [profile['threshold_band_label'] for profile in capability_profiles()],
        'selection_reason': 'the requested promise bundle never appears in the current six-regime weakening menu',
    }



def build_weakening_capability_selector_snapshot() -> dict[str, Any]:
    profiles = capability_profiles()
    objectives = [
        {
            'objective_code': 'fully_sticky',
            'objective_label': 'Keep every optional weakening deferred',
            'requirements': {},
            'selector': select_weakening_regime_by_capabilities(),
        },
        {
            'objective_code': 'suffix_only_relaxed_release',
            'objective_label': 'Permit suffix-only relaxed release without enlarging the relaxed-floor basin',
            'requirements': {
                'require_any_relaxed_release_from_stronger_tiers': True,
                'forbid_relaxed_basin_growth_beyond_neutral_exit': True,
            },
            'selector': select_weakening_regime_by_capabilities(
                require_any_relaxed_release_from_stronger_tiers=True,
                forbid_relaxed_basin_growth_beyond_neutral_exit=True,
            ),
        },
        {
            'objective_code': 'middle_band_precision_relief_without_relaxed_growth',
            'objective_label': 'Allow precision→neutral relief in the middle band while keeping the relaxed-floor basin fixed',
            'requirements': {
                'require_middle_band_precision_relief': True,
                'forbid_relaxed_basin_growth_beyond_neutral_exit': True,
            },
            'selector': select_weakening_regime_by_capabilities(
                require_middle_band_precision_relief=True,
                forbid_relaxed_basin_growth_beyond_neutral_exit=True,
            ),
        },
        {
            'objective_code': 'staged_neutral_release_to_relaxed_anchor',
            'objective_label': 'Allow the neutral anchor to discharge to the relaxed anchor, even if entry boundary 8 still stages through 13',
            'requirements': {
                'require_neutral_anchor_relaxed_release': True,
            },
            'selector': select_weakening_regime_by_capabilities(
                require_neutral_anchor_relaxed_release=True,
            ),
        },
        {
            'objective_code': 'direct_entry_boundary_release',
            'objective_label': 'Allow direct relaxed release from neutral entry boundary 8',
            'requirements': {
                'require_direct_entry_boundary_relaxed_release': True,
            },
            'selector': select_weakening_regime_by_capabilities(
                require_direct_entry_boundary_relaxed_release=True,
            ),
        },
        {
            'objective_code': 'full_base_policy_recovery',
            'objective_label': 'Recover the base cheapest-tier weakening policy, including direct precision release under relaxed floors',
            'requirements': {
                'require_direct_precision_relaxed_release': True,
            },
            'selector': select_weakening_regime_by_capabilities(
                require_direct_precision_relaxed_release=True,
            ),
        },
    ]
    infeasible_objectives = [
        {
            'objective_code': 'impossible_neutral_release_without_relaxed_growth',
            'objective_label': 'Demand neutral-anchor relaxed release while forbidding any relaxed-basin growth beyond neutral exit boundary 18',
            'requirements': {
                'require_neutral_anchor_relaxed_release': True,
                'forbid_relaxed_basin_growth_beyond_neutral_exit': True,
            },
            'selector': select_weakening_regime_by_capabilities(
                require_neutral_anchor_relaxed_release=True,
                forbid_relaxed_basin_growth_beyond_neutral_exit=True,
            ),
        },
        {
            'objective_code': 'impossible_direct_precision_release_without_relaxed_growth',
            'objective_label': 'Demand direct precision-anchor relaxed release while forbidding any relaxed-basin growth beyond neutral exit boundary 18',
            'requirements': {
                'require_direct_precision_relaxed_release': True,
                'forbid_relaxed_basin_growth_beyond_neutral_exit': True,
            },
            'selector': select_weakening_regime_by_capabilities(
                require_direct_precision_relaxed_release=True,
                forbid_relaxed_basin_growth_beyond_neutral_exit=True,
            ),
        },
    ]

    capability_minima = {
        'any_relaxed_release_from_stronger_tiers': 7,
        'middle_band_precision_relief': 11,
        'neutral_anchor_relaxed_release_eventually': 12,
        'direct_entry_boundary_relaxed_release': 17,
        'direct_precision_relaxed_release': 23,
    }

    return {
        'focus': 'Turn the named weakening regimes into a compact capability selector so inheritors can pick the smallest threshold band that satisfies an operational promise bundle instead of reasoning from threshold numerology by hand.',
        'headline_findings': {
            'main_rule': 'The six weakening regimes already form an exact promise menu: choose the smallest regime whose capabilities satisfy the desired release promises, and mark bundles that demand relaxed-floor growth while forbidding basin expansion as genuinely infeasible.',
            'minimal_thresholds_by_capability_unique_appends': capability_minima,
            'only_relaxed_basin_preserving_middle_band_relief_threshold_unique_appends': 11,
            'first_threshold_that_enlarges_relaxed_basin_to_neutral_anchor_unique_appends': 12,
            'first_threshold_that_allows_direct_entry_boundary_release_unique_appends': 17,
            'first_threshold_that_recovers_direct_precision_release_unique_appends': 23,
        },
        'decision_rules': [
            'Express weakening policy as promised capabilities first, then choose the smallest threshold band that satisfies them.',
            'Treat `forbid_relaxed_basin_growth_beyond_neutral_exit` as a hard safety promise: once you demand neutral-anchor or precision-anchor relaxed release, that promise becomes incompatible with the current menu.',
            'Threshold `11` is the unique selector answer when middle-band precision relief is desired but relaxed-floor reach must stay fixed.',
            'Threshold `12` is enough for eventual neutral-anchor discharge to relaxed anchor `25`; threshold `17` is only needed when the direct `8→25` jump itself matters.',
            'Threshold `23` remains the first band that exactly recovers the base cheapest-tier weakening policy under relaxed floors.',
        ],
        'capability_profiles': profiles,
        'objective_catalog': objectives,
        'infeasible_objectives': infeasible_objectives,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure_snapshot_20260308.json',
        ],
    }



def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Select the smallest named weakening regime that satisfies a bundle of operator capability promises.')
    parser.add_argument('--require-any-relaxed-release-from-stronger-tiers', action='store_true')
    parser.add_argument('--require-middle-band-precision-relief', action='store_true')
    parser.add_argument('--require-neutral-anchor-relaxed-release', action='store_true')
    parser.add_argument('--require-direct-entry-boundary-relaxed-release', action='store_true')
    parser.add_argument('--require-direct-precision-relaxed-release', action='store_true')
    parser.add_argument('--forbid-relaxed-basin-growth-beyond-neutral-exit', action='store_true')
    return parser



def main() -> None:
    args = _parser().parse_args()
    print(
        json.dumps(
            select_weakening_regime_by_capabilities(
                require_any_relaxed_release_from_stronger_tiers=args.require_any_relaxed_release_from_stronger_tiers,
                require_middle_band_precision_relief=args.require_middle_band_precision_relief,
                require_neutral_anchor_relaxed_release=args.require_neutral_anchor_relaxed_release,
                require_direct_entry_boundary_relaxed_release=args.require_direct_entry_boundary_relaxed_release,
                require_direct_precision_relaxed_release=args.require_direct_precision_relaxed_release,
                forbid_relaxed_basin_growth_beyond_neutral_exit=args.forbid_relaxed_basin_growth_beyond_neutral_exit,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == '__main__':
    main()
