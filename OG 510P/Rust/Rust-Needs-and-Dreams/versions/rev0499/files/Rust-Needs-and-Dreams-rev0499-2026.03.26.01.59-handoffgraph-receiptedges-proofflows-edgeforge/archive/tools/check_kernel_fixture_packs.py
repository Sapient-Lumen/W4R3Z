#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / 'fixtures' / 'top-band-v0'
HYG = FIXTURE_DIR / 'fixture-pack-hygiene-checks.json'
REQUIRED_FILES = [
    ROOT / 'fixtures' / 'README.md',
    FIXTURE_DIR / 'README.md',
    HYG,
]
REQUIRED_FIELDS = [
    'schema_family', 'fixture_id', 'kernel_id', 'candidate_id', 'scenario_id',
    'fixture_family', 'substrate_lane', 'required_tools', 'input_assets',
    'command_recipe', 'expected_artifacts', 'expected_negative_states',
    'expected_checks', 'refused_claims', 'refresh_triggers',
    'related_contracts', 'related_witnesses'
]
REQUIRED_KERNELS = {
    'build-state-pack',
    'debug-acceptance-matrix',
    'package-intake-review-kit',
    'safety-critical-readiness-cards',
}

def non_empty_string(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ''

def non_empty_list(v: Any) -> bool:
    return isinstance(v, list) and len(v) > 0

def main() -> int:
    errors: list[str] = []
    for path in REQUIRED_FILES:
        if not path.exists():
            errors.append(f'missing required fixture asset: {path.relative_to(ROOT)}')
    if not HYG.exists():
        pass
    else:
        try:
            hyg = json.loads(HYG.read_text(encoding='utf-8'))
        except Exception as exc:  # noqa: BLE001
            errors.append(f'failed to parse hygiene checks: {exc}')
            hyg = {}
        if hyg.get('schema_family') != 'kernel-fixture-hygiene/v0':
            errors.append('fixture hygiene schema_family must be kernel-fixture-hygiene/v0')
    cards = sorted(FIXTURE_DIR.glob('*.fixture.json'))
    if len(cards) < 4:
        errors.append('fixture corpus must include at least four fixture cards')
    ids: set[str] = set()
    kernels: set[str] = set()
    has_experimental = False
    has_route_uncertainty = False
    has_stale = False
    for path in cards:
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:  # noqa: BLE001
            errors.append(f'failed to parse {path.relative_to(ROOT)}: {exc}')
            continue
        for field in REQUIRED_FIELDS:
            if field not in payload:
                errors.append(f'{path.name} missing required field {field}')
        fid = payload.get('fixture_id')
        if not non_empty_string(fid):
            errors.append(f'{path.name} fixture_id must be non-empty string')
        elif fid in ids:
            errors.append(f'duplicate fixture_id: {fid}')
        else:
            ids.add(fid)
        kid = payload.get('kernel_id')
        if not non_empty_string(kid):
            errors.append(f'{path.name} kernel_id must be non-empty string')
        else:
            kernels.add(kid)
        for key in [
            'required_tools', 'input_assets', 'command_recipe', 'expected_artifacts',
            'expected_negative_states', 'expected_checks', 'refused_claims',
            'refresh_triggers', 'related_contracts', 'related_witnesses'
        ]:
            if not non_empty_list(payload.get(key)):
                errors.append(f'{path.name} {key} must be non-empty list')
        lane = payload.get('substrate_lane')
        if lane == 'experimental_caveated':
            has_experimental = True
        if lane == 'route_specific_uncertainty':
            has_route_uncertainty = True
        if lane == 'stale_or_missing_evidence':
            has_stale = True
        for rel in payload.get('related_contracts', []):
            if not non_empty_string(rel):
                errors.append(f'{path.name} related_contracts entries must be non-empty strings')
                continue
            if not (ROOT / rel).exists():
                errors.append(f'{path.name} related contract does not exist: {rel}')
        for rel in payload.get('related_witnesses', []):
            if not non_empty_string(rel):
                errors.append(f'{path.name} related_witnesses entries must be non-empty strings')
                continue
            if not (ROOT / rel).exists():
                errors.append(f'{path.name} related witness does not exist: {rel}')
    missing_kernels = sorted(REQUIRED_KERNELS - kernels)
    if missing_kernels:
        errors.append('missing required kernel coverage: ' + ', '.join(missing_kernels))
    if not has_experimental:
        errors.append('missing experimental_caveated fixture lane')
    if not has_route_uncertainty:
        errors.append('missing route_specific_uncertainty fixture lane')
    if not has_stale:
        errors.append('missing stale_or_missing_evidence fixture lane')
    if errors:
        print('Kernel fixture pack check FAILED', file=sys.stderr)
        for err in errors:
            print(f'- {err}', file=sys.stderr)
        return 1
    print('Kernel fixture pack check passed')
    print(f'Validated {len(cards)} fixture cards with kernel coverage: {", ".join(sorted(kernels))}.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
