#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

CAPS = [10, 20, 10000]
MATERIAL_ANCHOR = 'TTTMMMMMU'
STABILITY_ANCHOR = 'TTTMMMMUU'
TAU10 = Decimal('-0.000463764')
TAU10000 = Decimal('0.000033068')
TAU20 = Decimal('0.000313597')
THRESHOLDS = [
    ('tau(10)', 10, TAU10),
    ('tau(10000)', 10000, TAU10000),
    ('tau(20)', 20, TAU20),
]
BASELINE_EXPRESSION = (
    '0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife '
    '- 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties'
)


class OracleInputError(ValueError):
    pass


def _to_decimal(value: str | Decimal | None, name: str) -> Decimal:
    if value is None:
        raise OracleInputError(f'missing required value: {name}')
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise OracleInputError(f'invalid decimal for {name}: {value}') from exc


def baseline_nonhazard_surplus(weights: dict[str, str | Decimal]) -> Decimal:
    return (
        Decimal('0.00027') * _to_decimal(weights.get('w_width'), 'w_width')
        + Decimal('0.00013') * _to_decimal(weights.get('w_buffer'), 'w_buffer')
        + Decimal('0.000122') * _to_decimal(weights.get('w_knife'), 'w_knife')
        - Decimal('0.00142') * _to_decimal(weights.get('w_delta'), 'w_delta')
        - _to_decimal(weights.get('w_material'), 'w_material')
        - _to_decimal(weights.get('w_undecided'), 'w_undecided')
        - _to_decimal(weights.get('w_ties'), 'w_ties')
    )


def _winner_signature(label: str) -> list[str | None]:
    if label == 'MMM':
        return [MATERIAL_ANCHOR, MATERIAL_ANCHOR, MATERIAL_ANCHOR]
    if label == 'SMM':
        return [STABILITY_ANCHOR, MATERIAL_ANCHOR, MATERIAL_ANCHOR]
    if label == 'SMS':
        return [STABILITY_ANCHOR, MATERIAL_ANCHOR, STABILITY_ANCHOR]
    if label == 'SSS':
        return [STABILITY_ANCHOR, STABILITY_ANCHOR, STABILITY_ANCHOR]
    if label == 'TIE_tau10':
        return [None, MATERIAL_ANCHOR, MATERIAL_ANCHOR]
    if label == 'TIE_tau20':
        return [STABILITY_ANCHOR, None, STABILITY_ANCHOR]
    if label == 'TIE_tau10000':
        return [STABILITY_ANCHOR, MATERIAL_ANCHOR, None]
    if label == 'TIE_origin':
        return [None, None, None]
    raise OracleInputError(f'unsupported label for signature: {label}')


def classify_from_BH(B: Decimal, H: Decimal) -> dict[str, Any]:
    if H < 0:
        raise OracleInputError('classifier only defined here for nonnegative w_hazard')

    if H == 0:
        if B < 0:
            label = 'MMM'
            region = 'zero_hazard_axis_material_ray'
            robustness = 'material_robust_all_checked_caps'
            direct_rule = 'B < 0 on the zero-hazard axis'
        elif B > 0:
            label = 'SSS'
            region = 'zero_hazard_axis_stability_ray'
            robustness = 'stability_robust_all_checked_caps'
            direct_rule = 'B > 0 on the zero-hazard axis'
        else:
            label = 'TIE_origin'
            region = 'origin_all_cap_tie_point'
            robustness = 'exact_tie_all_checked_caps'
            direct_rule = 'B = 0 and H = 0'
    elif B < TAU10 * H:
        label = 'MMM'
        region = 'positive_hazard_material_cone'
        robustness = 'material_robust_all_checked_caps'
        direct_rule = 'B < tau(10) * H'
    elif B == TAU10 * H:
        label = 'TIE_tau10'
        region = 'tau10_boundary_ray'
        robustness = 'boundary_tie_at_cap_10'
        direct_rule = 'B = tau(10) * H'
    elif B < TAU10000 * H:
        label = 'SMM'
        region = 'positive_hazard_single_reversal_cone'
        robustness = 'cap_sensitive_across_checked_caps'
        direct_rule = 'tau(10) * H < B < tau(10000) * H'
    elif B == TAU10000 * H:
        label = 'TIE_tau10000'
        region = 'tau10000_boundary_ray'
        robustness = 'boundary_tie_at_cap_10000'
        direct_rule = 'B = tau(10000) * H'
    elif B < TAU20 * H:
        label = 'SMS'
        region = 'positive_hazard_double_reversal_cone'
        robustness = 'cap_sensitive_across_checked_caps'
        direct_rule = 'tau(10000) * H < B < tau(20) * H'
    elif B == TAU20 * H:
        label = 'TIE_tau20'
        region = 'tau20_boundary_ray'
        robustness = 'boundary_tie_at_cap_20'
        direct_rule = 'B = tau(20) * H'
    else:
        label = 'SSS'
        region = 'positive_hazard_stability_cone'
        robustness = 'stability_robust_all_checked_caps'
        direct_rule = 'B > tau(20) * H'

    winners = _winner_signature(label)
    cap_rows = []
    for cap, winner in zip(CAPS, winners):
        cap_rows.append(
            {
                'cap': cap,
                'outcome': 'tie' if winner is None else 'strict_winner',
                'winner': winner,
            }
        )

    rho = None if H == 0 else str(B / H)
    if label in {'MMM', 'SMM', 'SMS', 'SSS'}:
        strict_path_class = label
    else:
        strict_path_class = None

    if label == 'MMM':
        recommended_black_box_probe_contract = '[10,20] confirms robustness; [10,20,10000] records full strict path'
    elif label == 'SSS':
        recommended_black_box_probe_contract = '[10,20] confirms robustness; [10,20,10000] records full strict path'
    elif label in {'SMM', 'SMS'}:
        recommended_black_box_probe_contract = '[10,20,10000] or adaptive 10000 -> (10 after M, 20 after S)'
    else:
        recommended_black_box_probe_contract = 'use [10,20,10000] when a portable black-box record must expose the exact tie cap'

    return {
        'material_anchor': MATERIAL_ANCHOR,
        'stability_anchor': STABILITY_ANCHOR,
        'baseline_nonhazard_surplus': str(B),
        'w_hazard': str(H),
        'hazard_normalized_margin_rho_when_defined': rho,
        'classification_region': region,
        'strict_path_class': strict_path_class,
        'closure_label': label,
        'robustness_class': robustness,
        'direct_rule_triggered': direct_rule,
        'checked_cap_outcomes': cap_rows,
        'recommended_black_box_probe_contract': recommended_black_box_probe_contract,
    }


def classify_from_weights(weights: dict[str, str | Decimal]) -> dict[str, Any]:
    B = baseline_nonhazard_surplus(weights)
    H = _to_decimal(weights.get('w_hazard'), 'w_hazard')
    result = classify_from_BH(B, H)
    result['input_mode'] = 'weights'
    result['declared_weights'] = {key: str(_to_decimal(weights.get(key), key)) for key in [
        'w_width', 'w_buffer', 'w_knife', 'w_delta', 'w_material', 'w_undecided', 'w_ties', 'w_hazard'
    ]}
    result['baseline_nonhazard_surplus_expression'] = BASELINE_EXPRESSION
    return result


def classify_from_direct_coordinates(B: str | Decimal, H: str | Decimal) -> dict[str, Any]:
    result = classify_from_BH(_to_decimal(B, 'B'), _to_decimal(H, 'H'))
    result['input_mode'] = 'projective_coordinates'
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Executable family10 rematch-proxy delta decision oracle.')
    parser.add_argument('--B', help='baseline_nonhazard_surplus for direct cone classification')
    parser.add_argument('--H', help='w_hazard for direct cone classification')
    parser.add_argument('--w-width', dest='w_width')
    parser.add_argument('--w-buffer', dest='w_buffer')
    parser.add_argument('--w-knife', dest='w_knife')
    parser.add_argument('--w-delta', dest='w_delta')
    parser.add_argument('--w-material', dest='w_material')
    parser.add_argument('--w-undecided', dest='w_undecided')
    parser.add_argument('--w-ties', dest='w_ties')
    parser.add_argument('--w-hazard', dest='w_hazard')
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.B is not None or args.H is not None:
        if args.B is None or args.H is None:
            raise SystemExit('direct coordinate mode requires both --B and --H')
        result = classify_from_direct_coordinates(args.B, args.H)
    else:
        weight_keys = [
            'w_width', 'w_buffer', 'w_knife', 'w_delta',
            'w_material', 'w_undecided', 'w_ties', 'w_hazard',
        ]
        if any(getattr(args, key) is None for key in weight_keys):
            raise SystemExit('weight mode requires all eight weight arguments or use --B/--H')
        result = classify_from_weights({key: getattr(args, key) for key in weight_keys})
    payload = {
        'tool': str(Path(__file__).resolve()),
        'caps_checked': CAPS,
        'thresholds': [{ 'boundary_name': name, 'cap': cap, 'value': str(value)} for name, cap, value in THRESHOLDS],
        'result': result,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
