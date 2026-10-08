#!/usr/bin/env python3
"""Validate the operator command surface.

The Makefile is the archive's lowest-friction command map.  A stale phony list,
help line, or target recipe can mislead cold-open/release operators even when the
underlying scripts still pass individually.  This validator keeps the declared
public targets, help output, recipes, validation inventory, context-pack command
hints, and canonical policy command-surface pointers aligned.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / 'Makefile'

EXPECTED_TARGETS = [
    'help',
    'build-papers',
    'asset-indexes',
    'dedupe-report',
    'rebuild-indexes',
    'opening-check',
    'context-check',
    'command-surface-check',
    'toolchain-check',
    'manifest-check',
    'dedupe-check',
    'json-check',
    'text-check',
    'text-surface-check',
    'payload-format-check',
    'crypto-check',
    'provenance-check',
    'filesystem-check',
    'asset-check',
    'paper-check',
    'archive-payload-check',
    'source-check',
    'adr-check',
    'rfc-check',
    'frontier-check',
    'assimilation-check',
    'revision-check',
    'control-check',
    'validation-check',
    'claim-obligation-check',
    'public-status-check',
    'ro-crate-check',
    'changelog-check',
    'archive-index-check',
    'historical-anomaly-check',
    'cross-reference-check',
    'audit-witness-check',
    'identity-check',
    'publishing-check',
    'runner-check',
    'release-ledgers',
    'preflight',
    'gate',
    'publish-audit',
    'package-release',
]

EXPECTED_RECIPES = {
    'build-papers': ['bash scripts/build_papers.sh'],
    'asset-indexes': ['$(PYTHON) scripts/build_asset_indexes.py'],
    'dedupe-report': ['$(PYTHON) scripts/build_dedupe_report.py'],
    'rebuild-indexes': ['$(PYTHON) scripts/rebuild_indexes.py'],
    'opening-check': ['$(PYTHON) scripts/validate_opening_surface.py'],
    'context-check': ['$(PYTHON) scripts/validate_context_pack.py'],
    'command-surface-check': ['$(PYTHON) scripts/validate_makefile_surface.py'],
    'toolchain-check': ['$(PYTHON) scripts/validate_toolchain_lock.py'],
    'manifest-check': ['$(PYTHON) scripts/validate_manifest_index.py'],
    'dedupe-check': ['$(PYTHON) scripts/validate_dedupe_report.py'],
    'json-check': ['$(PYTHON) scripts/validate_json_inventory.py'],
    'text-check': ['$(PYTHON) scripts/validate_text_payloads.py'],
    'text-surface-check': ['$(PYTHON) scripts/validate_text_surface_policy.py'],
    'payload-format-check': ['$(PYTHON) scripts/validate_payload_formats.py'],
    'crypto-check': ['$(PYTHON) scripts/validate_crypto_envelopes.py'],
    'provenance-check': ['$(PYTHON) scripts/validate_provenance_ledgers.py'],
    'filesystem-check': ['$(PYTHON) scripts/validate_filesystem_policy.py'],
    'asset-check': ['$(PYTHON) scripts/validate_asset_indexes.py'],
    'paper-check': ['$(PYTHON) scripts/validate_paper_series.py'],
    'archive-payload-check': ['$(PYTHON) scripts/validate_embedded_archives.py'],
    'source-check': ['$(PYTHON) scripts/validate_source_index.py'],
    'adr-check': ['$(PYTHON) scripts/validate_adrs.py'],
    'rfc-check': ['$(PYTHON) scripts/validate_rfcs.py'],
    'frontier-check': ['$(PYTHON) scripts/validate_current_frontier.py'],
    'assimilation-check': ['$(PYTHON) scripts/validate_assimilation_ledger.py'],
    'revision-check': ['$(PYTHON) scripts/validate_revision_anchors.py'],
    'control-check': ['$(PYTHON) scripts/validate_control_surfaces.py'],
    'validation-check': ['$(PYTHON) scripts/validate_validation_index.py'],
    'claim-obligation-check': ['$(PYTHON) scripts/validate_claim_obligation_map.py'],
    'public-status-check': ['$(PYTHON) scripts/validate_public_status.py'],
    'ro-crate-check': ['$(PYTHON) scripts/validate_ro_crate_metadata.py'],
    'changelog-check': ['$(PYTHON) scripts/validate_changelog.py'],
    'archive-index-check': ['$(PYTHON) scripts/validate_archive_index.py'],
    'historical-anomaly-check': ['$(PYTHON) scripts/validate_historical_anomalies.py'],
    'cross-reference-check': ['$(PYTHON) scripts/validate_cross_references.py'],
    'audit-witness-check': ['$(PYTHON) scripts/validate_audit_witnesses.py'],
    'identity-check': ['$(PYTHON) scripts/validate_archive_identity.py'],
    'publishing-check': ['$(PYTHON) scripts/validate_publishing.py'],
    'runner-check': ['$(PYTHON) scripts/validate_command_runners.py'],
    'release-ledgers': [
        '$(PYTHON) scripts/publication_rights_gate.py --context release-ledgers',
        '$(PYTHON) scripts/build_release_queue_index.py',
        '$(PYTHON) scripts/build_release_ledger.py',
        '$(PYTHON) scripts/materialize_public_release.py',
    ],
    'preflight': ['bash scripts/publish_preflight.sh'],
    'gate': ['$(PYTHON) scripts/gate.py'],
    'publish-audit': ['$(PYTHON) scripts/publish_audit.py'],
    'package-release': ['$(PYTHON) scripts/package_release.py'],
}

HELP_TARGETS = [target for target in EXPECTED_TARGETS if target != 'help']


def fail(msg: str) -> None:
    print(f'command-surface-validate: FAIL: {msg}', file=sys.stderr)
    sys.exit(1)


def load_json(rel: str):
    try:
        return json.loads((ROOT / rel).read_text(encoding='utf-8'))
    except Exception as exc:
        fail(f'invalid JSON in {rel}: {exc}')


def parse_target_recipes(text: str) -> dict[str, list[str]]:
    recipes: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        target_match = re.match(r'^([A-Za-z0-9_.-]+):\s*(?:#.*)?$', line)
        if target_match and not line.startswith('.'):
            current = target_match.group(1)
            recipes.setdefault(current, [])
            continue
        if current and line.startswith('\t'):
            recipes[current].append(line[1:].rstrip())
            continue
        if line and not line.startswith('\t') and not line.startswith('@echo'):
            # Assignment/comment/blank lines are allowed between targets; anything
            # non-recipe resets the current target unless it is another target line.
            if not line.startswith('#'):
                current = None
    return recipes


def parse_phony_targets(text: str) -> list[str]:
    match = re.search(r'(?m)^\.PHONY:\s*(.+)$', text)
    if not match:
        fail('Makefile missing .PHONY declaration')
    return match.group(1).split()


def require_script_from_recipe(recipe: str) -> None:
    script_match = re.search(r'(scripts/[A-Za-z0-9_.\-/]+)', recipe)
    if script_match and not (ROOT / script_match.group(1)).exists():
        fail(f'recipe references missing script: {script_match.group(1)}')


def validate_makefile_text(text: str) -> None:
    if not text.endswith('\n'):
        fail('Makefile must end with a newline')
    if '\r' in text:
        fail('Makefile must use LF line endings')
    if 'SHELL := /usr/bin/env bash' not in text.splitlines()[:8]:
        fail('Makefile must pin SHELL := /usr/bin/env bash near the top')
    if '.DEFAULT_GOAL := help' not in text.splitlines()[:8]:
        fail('Makefile must keep help as the default goal')
    if 'PYTHON ?= python3' not in text.splitlines()[:8]:
        fail('Makefile must expose PYTHON ?= python3')
    if 'export PYTHONDONTWRITEBYTECODE := 1' not in text.splitlines()[:8]:
        fail('Makefile must disable Python bytecode emission')

    phony_targets = parse_phony_targets(text)
    if phony_targets != EXPECTED_TARGETS:
        fail(f'.PHONY target drift; expected={EXPECTED_TARGETS!r}, actual={phony_targets!r}')

    recipes = parse_target_recipes(text)
    defined_targets = [target for target in recipes if target != '.PHONY']
    if defined_targets != EXPECTED_TARGETS:
        fail(f'Makefile target definition drift; expected={EXPECTED_TARGETS!r}, actual={defined_targets!r}')

    for target, expected in EXPECTED_RECIPES.items():
        actual = recipes.get(target)
        if actual != expected:
            fail(f'Makefile recipe drift for {target}: expected={expected!r}, actual={actual!r}')
        for recipe in actual:
            require_script_from_recipe(recipe)

    for target in HELP_TARGETS:
        if f'make {target}' not in text:
            fail(f'Makefile help text missing make {target}')
    help_section = text.split('help:', 1)[1].split('\nbuild-papers:', 1)[0]
    help_lines = [line for line in help_section.splitlines() if line.startswith('\t@echo "  make ')]
    help_targets = []
    for line in help_lines:
        match = re.search(r'make ([a-z0-9-]+)', line)
        if match:
            help_targets.append(match.group(1))
    if help_targets != HELP_TARGETS:
        fail(f'Makefile help target order/content drift; expected={HELP_TARGETS!r}, actual={help_targets!r}')


def validate_inventory_and_policy() -> None:
    validation = load_json('VALIDATION_INDEX.json')
    context = load_json('CONTEXT_PACK.json')
    policy = load_json('publishing/CANONICAL_POLICY.json')
    release = load_json('RELEASE_MANIFEST.json')

    check_targets = {check['make_target'] for check in validation.get('checks', [])}
    composite_targets = {target['make_target'] for target in validation.get('composite_targets', [])}
    expected_inventory_targets = set(EXPECTED_TARGETS) - {'help', 'build-papers'}
    actual_inventory_targets = check_targets | composite_targets
    missing = sorted(expected_inventory_targets - actual_inventory_targets)
    extra = sorted(actual_inventory_targets - expected_inventory_targets)
    if missing or extra:
        fail(f'VALIDATION_INDEX checked-target coverage drift; missing={missing}, extra={extra}')

    command_check = next((check for check in validation.get('checks', []) if check.get('id') == 'command-surface-check'), None)
    if command_check is None:
        fail('VALIDATION_INDEX.json missing command-surface-check')
    if command_check.get('scripts') != ['scripts/validate_makefile_surface.py']:
        fail('command-surface-check scripts mismatch')
    if not {'Makefile', 'CONTEXT_PACK.json', 'VALIDATION_INDEX.json', 'publishing/CANONICAL_POLICY.json', 'RELEASE_MANIFEST.json', 'scripts/validate_makefile_surface.py'}.issubset(set(command_check.get('validates', []))):
        fail('command-surface-check validates missing command-surface inventory surfaces')

    commands = set(context.get('checks', []))
    for target in expected_inventory_targets:
        if f'make {target}' not in commands:
            fail(f'CONTEXT_PACK.json checks missing make {target}')
    if 'python3 scripts/validate_makefile_surface.py' not in commands:
        fail('CONTEXT_PACK.json checks missing direct command-surface validator invocation')
    if context.get('key_machine_surfaces', {}).get('command_surface') != 'Makefile':
        fail('CONTEXT_PACK.json command_surface mismatch')
    if context.get('key_machine_surfaces', {}).get('command_surface_validator') != 'scripts/validate_makefile_surface.py':
        fail('CONTEXT_PACK.json command_surface_validator mismatch')

    if policy.get('operator_command_surface') != 'Makefile':
        fail('publishing/CANONICAL_POLICY.json operator_command_surface mismatch')
    if policy.get('command_surface_validator') != 'scripts/validate_makefile_surface.py':
        fail('publishing/CANONICAL_POLICY.json command_surface_validator mismatch')
    if release.get('command_surface') != 'Makefile':
        fail('RELEASE_MANIFEST.json command_surface mismatch')


def main() -> None:
    text = MAKEFILE.read_text(encoding='utf-8')
    validate_makefile_text(text)
    validate_inventory_and_policy()
    print(f'command-surface-validate: OK ({len(HELP_TARGETS)} public make targets, {len(EXPECTED_RECIPES)} recipes)')


if __name__ == '__main__':
    main()
