#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC_LEDGER = ROOT / 'specs' / 'spec_ledger.yaml'
RISK_REGISTER = ROOT / 'specs' / 'risk_register.yaml'
CACHE_PLAN = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_cache_plan_snapshot_20260306.json'
ZERO_NOISE = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_zero_noise_rule_classifier_snapshot_20260306.json'
PLAN_SCHEMA = ROOT / 'schemas' / 'canonicalization_plan.schema.json'
ZERO_SCHEMA = ROOT / 'schemas' / 'zero_noise_rule_classifier.schema.json'
PLAN_VALIDATOR = ROOT / 'scripts' / 'test' / 'check_rematch_cache_plan_contract.py'
ZERO_VALIDATOR = ROOT / 'scripts' / 'test' / 'check_rematch_zero_noise_rule_contract.py'

ASSUMPTION_IDS = ['SA-004', 'SA-005', 'SA-006', 'SA-007', 'SA-009', 'SA-010']
QUESTION_IDS = ['SQ-003', 'SQ-004', 'SQ-005', 'SQ-006', 'SQ-007', 'SQ-008', 'SQ-009', 'SQ-010', 'SQ-011']
RISK_IDS = [f'RK-{index:03d}' for index in range(7, 16)]
RETAINED_PATHS = [
    CACHE_PLAN,
    ZERO_NOISE,
    PLAN_SCHEMA,
    ZERO_SCHEMA,
    PLAN_VALIDATOR,
    ZERO_VALIDATOR,
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def build_receipt() -> dict[str, Any]:
    spec_rows = {row['id']: row for row in load_yaml(SPEC_LEDGER)}
    risk_rows = {row['id']: row for row in load_yaml(RISK_REGISTER)}
    cache_plan = load_json(CACHE_PLAN)
    zero_noise = load_json(ZERO_NOISE)

    assumptions = [
        {
            'id': row['id'],
            'status': row['status'],
            'summary': row['summary'],
            'primary_evidence_link': row['evidence_links'][0],
            'target_resolution': row['target_resolution'],
        }
        for row in (spec_rows[item] for item in ASSUMPTION_IDS)
    ]
    questions = [
        {
            'id': row['id'],
            'status': row['status'],
            'summary': row['summary'],
            'primary_evidence_link': row['evidence_links'][0],
            'target_resolution': row['target_resolution'],
        }
        for row in (spec_rows[item] for item in QUESTION_IDS)
    ]
    risks = [
        {
            'id': row['id'],
            'status': row['status'],
            'severity': row['severity'],
            'likelihood': row['likelihood'],
            'summary': row['summary'],
            'primary_evidence_link': row['evidence_links'][0],
            'review_date': row['review_date'],
        }
        for row in (risk_rows[item] for item in RISK_IDS)
    ]

    planner_modes = [
        {
            'id': row['id'],
            'label': row['label'],
            'planner_kind': row['planner_kind'],
            'recommended_key_fields': row['recommended_key_fields'],
            'minimal_exact_horizon': row['minimal_exact_horizon'],
            'regime_count': row['regime_count'],
            'optimized_key_depth_slots': row['optimized_key_depth_slots'],
            'key_depth_reduction_factor': row['key_depth_reduction_factor'],
        }
        for row in cache_plan['mode_rows']
    ]

    retained_artifacts = [
        {
            'path': rel(path),
            'role': role,
            'bytes': path.stat().st_size,
            'sha256': sha256(path),
        }
        for path, role in [
            (CACHE_PLAN, 'mode-specific canonicalization planner source'),
            (ZERO_NOISE, 'ordered zero-noise dispatch source'),
            (PLAN_SCHEMA, 'planner manifest schema'),
            (ZERO_SCHEMA, 'ordered zero-noise classifier schema'),
            (PLAN_VALIDATOR, 'planner manifest contract validator'),
            (ZERO_VALIDATOR, 'ordered zero-noise classifier contract validator'),
        ]
    ]

    linked_open_item_count = len(assumptions) + len(questions) + len(risks)
    ordered_rule_count = len(zero_noise['rule_rows'])
    support_signature_count = zero_noise['world']['support_signature_count']

    return {
        'receipt_kind': 'rematch_world_canonicalization_bridge_receipt',
        'receipt_version': '2026-03-17.rematch_world_canonicalization_bridge_receipt.v1',
        'scope': {
            'gap_id': 'SG-003',
            'focus_layer': 'canonicalization_contract_first',
            'generated_on': '2026-03-17',
            'provisional_scope_note': 'Bridge the current proxy-local canonicalization findings into one tiny inheritor-facing packet until real rematch worlds expose native planner fields.',
            'linked_open_item_count': linked_open_item_count,
        },
        'linked_open_items': {
            'assumptions': assumptions,
            'questions': questions,
            'risks': risks,
        },
        'planner_contract': {
            'source_artifact': rel(CACHE_PLAN),
            'naive_cache_plan': cache_plan['world']['naive_cache_plan'],
            'mode_rows': planner_modes,
        },
        'zero_noise_classifier_contract': {
            'source_artifact': rel(ZERO_NOISE),
            'schema_path': rel(ZERO_SCHEMA),
            'validator_path': rel(ZERO_VALIDATOR),
            'ordered_rule_count': ordered_rule_count,
            'support_signature_count': support_signature_count,
            'dispatch_surface_reduction_factor': round(support_signature_count / ordered_rule_count, 6),
        },
        'retained_artifacts': retained_artifacts,
        'carry_forward_rules': [
            'Key rematch canonicalization on active noise topology first; only then use the smallest validated entrant discriminator for that mode.',
            'Carry exact proxy-local horizons by mode instead of the inherited global h=50 bound: none=3, opponent_tremble=2, focal_tremble=2, bilateral_tremble=1.',
            'Treat the zero-noise ordered wildcard classifier as the preferred interim dispatch surface instead of a flat 243-row signature table.',
            'Reuse the zero-noise cooperative-start cache only under deterministic no-noise semantics when newly admitted entrants remain initial-C-only.',
        ],
        'must_regenerate_when': [
            'entrant support changes enough to add new initial-D or later-state support patterns',
            'noise semantics or actor-side tremble topology changes',
            'outside-option timing or rematch semantics change reachability',
            'memory depth or state-space semantics change the exact canonicalization horizon',
        ],
        'do_not_carry_forward': [
            'Do not hard-code one universal full-signature cache key across all noise modes.',
            'Do not reuse the zero-noise planner under any nonzero tremble semantics.',
            'Do not keep the inherited h=50 canonicalization unroll as a default once a smaller validated exact horizon exists.',
            'Do not vendor a bulky flat support-signature table when the ordered rule classifier already captures the same zero-noise dispatch semantics.',
        ],
        'recommended_next_moves': [
            'Expose planner-manifest fields natively on the first endogenous rematch world so cache keys and exact horizons stop living only in report code.',
            'Make the engine regenerate and validate the ordered zero-noise classifier whenever world semantics change, rather than copying the current proxy artifact forward unchanged.',
            'Retire SQ-003 through SQ-011 in order by turning this bridge receipt into engine-owned conformance checks instead of widening the archive with more ad hoc benchmark tables.',
        ],
        'archive_posture': {
            'prefer_citation_over_recopy': True,
            'intended_retention_class': 'durable_handoff_receipt',
            'size_discipline_note': 'Keep the receipt tiny and citation-first: retain hashes and pointers to the planner/classifier contracts rather than reprinting the full zero-noise dispatch table or duplicating large reports.',
        },
    }


def main() -> int:
    receipt = build_receipt()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
