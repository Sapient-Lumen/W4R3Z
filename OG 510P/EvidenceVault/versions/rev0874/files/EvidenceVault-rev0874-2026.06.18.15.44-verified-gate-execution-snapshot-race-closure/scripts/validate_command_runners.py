#!/usr/bin/env python3
"""Validate governed composite command-runner coherence.

Composite runners are an operator-facing assurance surface.  This validator keeps
Makefile targets, shell preflight, runner scripts, package refresh/final gates,
and the exact command sequence contract aligned so a stale hard-coded list cannot
silently diverge from the sequence operators actually execute.  It also guards
the detached artifact verifier lane that replays the embedded command-runner
sequence contract from emitted ZIP bytes.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
SEQUENCE_JSON = 'COMMAND_RUNNER_SEQUENCE.json'
SEQUENCE_MD = 'COMMAND_RUNNER_SEQUENCE.md'
SEQUENCE_SCHEMA = 'schemas/command_runner_sequence.schema.json'
EXPECTED_SEQUENCE_IDS = ['gate', 'publish_audit', 'package_refresh', 'package_final_validators']
EXPECTED_TRANSIENT_SKIP_ROOTS = {'sources', 'artifacts', 'certs'}
EXPECTED_TRANSIENT_BUILD_PATTERNS = [
    '_renders*',
    'render_check*',
    '_render*',
    '*.aux',
    '*.log',
    '*.out',
    '*.toc',
    '*.bbl',
    '*.blg',
]
PREFLIGHT_REQUIRED_FILE_SENTINELS = {
    'README.md', 'START_HERE.md', 'PUBLISHING.md',
    'CONTROL_SURFACES.json', 'LIFECYCLE_GATES.json',
    'VALIDATION_INDEX.md', 'VALIDATION_INDEX.json',
    'COMMAND_RUNNER_SEQUENCE.json', 'COMMAND_RUNNER_SEQUENCE.md', 'schemas/command_runner_sequence.schema.json',
    'TOOLCHAIN_LOCK.json', 'TOOLCHAIN_LOCK.md', 'schemas/toolchain_lock.schema.json', 'scripts/validate_toolchain_lock.py',
    'CLAIM_OBLIGATION_MAP.json', 'CLAIM_OBLIGATION_MAP.md', 'schemas/claim_obligation_map.schema.json', 'scripts/validate_claim_obligation_map.py',
    'PUBLIC_STATUS.json', 'PUBLIC_STATUS.md', 'schemas/public_status.schema.json', 'scripts/validate_public_status.py',
    'ro-crate-metadata.json', 'RO_CRATE_PROFILE.md', 'schemas/ro_crate_metadata.schema.json', 'scripts/validate_ro_crate_metadata.py',
    'RELEASE_MANIFEST.json', 'REVISION_ANCHORS.json', 'ARCHIVE_INDEX.md', 'ARCHIVE_INDEX.json',
    'AUDIT/HISTORICAL_ANOMALIES.json', 'AUDIT/HISTORICAL_ANOMALIES.md', 'schemas/historical_anomalies.schema.json', 'scripts/validate_historical_anomalies.py',
    'MANIFEST.sha256', 'INDEX/files.json', 'INDEX/files.csv',
    'scripts/gate.py', 'scripts/publish_preflight.sh', 'scripts/publish_audit.py', 'scripts/package_release.py', 'scripts/verify_release_artifact.py',
    'scripts/validate_command_runners.py', 'scripts/validate_archive_identity.py', 'scripts/validate_publishing.py',
}
PREFLIGHT_REQUIRED_DIR_SENTINELS = {
    'INDEX', 'scripts', 'schemas',
    'published/releases/artifacts', 'published/releases/snapshots',
    'release_queue/candidates', 'release_queue/hold', 'release_queue/published_ready', 'release_queue/decisions',
}
CRITICAL_GATE_STEPS = {
    'validate_opening_surface.py', 'validate_context_pack.py', 'validate_makefile_surface.py', 'validate_toolchain_lock.py',
    'build_asset_indexes.py', 'build_dedupe_report.py', 'rebuild_indexes.py', 'validate_manifest_index.py',
    'validate_json_inventory.py', 'validate_text_payloads.py', 'validate_text_surface_policy.py', 'validate_payload_formats.py',
    'validate_crypto_envelopes.py', 'validate_provenance_ledgers.py', 'validate_filesystem_policy.py', 'validate_asset_indexes.py',
    'validate_paper_series.py', 'validate_embedded_archives.py', 'validate_source_index.py', 'validate_adrs.py', 'validate_rfcs.py',
    'validate_current_frontier.py', 'validate_assimilation_ledger.py', 'validate_revision_anchors.py', 'validate_control_surfaces.py',
    'validate_validation_index.py', 'validate_claim_obligation_map.py', 'validate_public_status.py', 'validate_ro_crate_metadata.py',
    'validate_changelog.py', 'validate_archive_index.py', 'validate_historical_anomalies.py', 'validate_cross_references.py',
    'validate_audit_witnesses.py', 'validate_command_runners.py', 'validate_archive_identity.py', 'validate_publishing.py',
}


def fail(msg: str) -> None:
    print(f'command-runner-validate: FAIL: {msg}', file=sys.stderr)
    sys.exit(1)


def require(rel: str) -> None:
    if not isinstance(rel, str) or not rel:
        fail(f'empty/non-string path reference: {rel!r}')
    if rel.startswith('/') or '\\' in rel or '..' in Path(rel).parts:
        fail(f'unsafe path reference: {rel}')
    if not (ROOT / rel).exists():
        fail(f'missing path: {rel}')


def load_json(rel: str) -> dict:
    try:
        data = json.loads((ROOT / rel).read_text(encoding='utf-8'))
    except Exception as exc:
        fail(f'invalid JSON in {rel}: {exc}')
    if not isinstance(data, dict):
        fail(f'{rel} must be a JSON object')
    return data


def literal_value(script_rel: str, variable: str):
    path = ROOT / script_rel
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=script_rel)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable:
                    try:
                        return ast.literal_eval(node.value)
                    except Exception as exc:
                        fail(f'{script_rel} {variable} is not a literal value: {exc}')
    fail(f'{script_rel} missing literal {variable}')


def render_markdown(contract: dict) -> str:
    lines = [
        '# Command-runner sequence contract',
        '',
        'This file is the exact human-facing companion to `COMMAND_RUNNER_SEQUENCE.json`.',
        'The JSON contract is the governed source of truth for composite runner order; `scripts/gate.py`, `scripts/publish_audit.py`, and `scripts/package_release.py` load it rather than carrying parallel literal validator lists.',
        '',
        f"- Format: `{contract['format']}`",
        f"- Revision: `{contract['revision']}`",
        f"- Previous revision: `{contract['previous_revision']}`",
        f"- Generated at: `{contract['generated_at_local']}`",
        f"- Validator: `{contract['policy']['validator']}`",
        f"- Schema: `{contract['policy']['schema']}`",
        f"- Package-final equals gate: `{str(contract['policy']['package_final_must_equal_gate']).lower()}`",
        f"- Publish-audit must not call gate: `{str(contract['policy']['publish_audit_must_not_call_gate']).lower()}`",
        '',
        '## Policy',
        '',
    ]
    for key in sorted(contract['policy']):
        value = contract['policy'][key]
        if isinstance(value, bool):
            value = str(value).lower()
        lines.append(f'- `{key}`: `{value}`')
    lines.extend(['', '## Sequences', ''])
    for sequence in contract['sequences']:
        lines.extend([
            f"### `{sequence['id']}` — `{sequence['owner_script']}`",
            '',
            f"- Make target: `{sequence['make_target']}`",
            f"- Kind: `{sequence['kind']}`",
            f"- Subprocess isolation: `{str(sequence['subprocess_isolation']).lower()}`",
            f"- Steps: `{len(sequence['steps'])}`",
            f"- Description: {sequence['description']}",
            '',
            '| # | Role | Script |',
            '| ---: | --- | --- |',
        ])
        for step in sequence['steps']:
            lines.append(f"| {step['order']} | `{step['role']}` | `scripts/{step['script']}` |")
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def sequence_by_id(contract: dict) -> dict[str, dict]:
    out = {}
    for sequence in contract.get('sequences', []):
        seq_id = sequence.get('id')
        if seq_id in out:
            fail(f'duplicate sequence id: {seq_id}')
        out[seq_id] = sequence
    return out


def scripts_for(contract: dict, seq_id: str) -> list[str]:
    sequences = sequence_by_id(contract)
    if seq_id not in sequences:
        fail(f'missing command-runner sequence: {seq_id}')
    return [step['script'] for step in sequences[seq_id]['steps']]


def validate_schema(contract: dict) -> None:
    schema = load_json(SEQUENCE_SCHEMA)
    errors = sorted(Draft202012Validator(schema).iter_errors(contract), key=lambda e: list(e.path))
    if errors:
        err = errors[0]
        where = '/'.join(str(p) for p in err.path) or '<root>'
        fail(f'{SEQUENCE_JSON} schema violation at {where}: {err.message}')


def validate_contract(contract: dict) -> None:
    receipt = load_json('REVISION_RECEIPT.json')
    if contract.get('revision') != receipt.get('revision'):
        fail('COMMAND_RUNNER_SEQUENCE.json revision must match REVISION_RECEIPT.json')
    if contract.get('previous_revision') != receipt.get('previous_revision'):
        fail('COMMAND_RUNNER_SEQUENCE.json previous_revision must match REVISION_RECEIPT.json')
    stamp = receipt.get('timestamp', '').split('.')
    if len(stamp) != 5:
        fail('REVISION_RECEIPT.json timestamp must use YYYY.MM.DD.HH.MM')
    expected_generated = f'{stamp[0]}-{stamp[1]}-{stamp[2]}T{stamp[3]}:{stamp[4]}:00-0400'
    if contract.get('generated_at_local') != expected_generated:
        fail('COMMAND_RUNNER_SEQUENCE.json generated_at_local must mirror receipt timestamp')
    policy = contract.get('policy', {})
    expected_policy = {
        'validator': 'scripts/validate_command_runners.py',
        'markdown_companion': SEQUENCE_MD,
        'schema': SEQUENCE_SCHEMA,
        'child_interpreter': 'sys.executable',
        'cwd': 'archive_root',
        'bytecode_policy': 'PYTHONDONTWRITEBYTECODE=1',
        'package_final_must_equal_gate': True,
        'publish_audit_must_not_call_gate': True,
        'package_refresh_is_builder_only': True,
    }
    for key, expected in expected_policy.items():
        if policy.get(key) != expected:
            fail(f'COMMAND_RUNNER_SEQUENCE.json policy.{key} mismatch')
    sequences = sequence_by_id(contract)
    if list(sequences) != EXPECTED_SEQUENCE_IDS:
        fail(f'command-runner sequence order must be {EXPECTED_SEQUENCE_IDS!r}')
    seen_owner_pairs = set()
    for seq_id, sequence in sequences.items():
        require(sequence['owner_script'])
        if not sequence.get('subprocess_isolation'):
            fail(f'{seq_id} must require subprocess isolation')
        scripts = []
        for expected_order, step in enumerate(sequence['steps'], start=1):
            if step.get('order') != expected_order:
                fail(f'{seq_id} step order must be contiguous starting at 1')
            if not step.get('required'):
                fail(f'{seq_id} step {expected_order} must be required')
            script_name = step['script']
            require(f'scripts/{script_name}')
            scripts.append(script_name)
            seen_owner_pairs.add((sequence['owner_script'], script_name))
            expected_role = 'validator' if script_name.startswith('validate_') else 'builder' if script_name.startswith('build_') or script_name == 'rebuild_indexes.py' else 'materializer' if script_name.startswith('materialize_') else 'runner'
            if step.get('role') != expected_role:
                fail(f'{seq_id} step {expected_order} role mismatch for {script_name}')
        if len(scripts) != len(set(scripts)):
            fail(f'{seq_id} must not contain duplicate scripts')
    gate = scripts_for(contract, 'gate')
    package_final = scripts_for(contract, 'package_final_validators')
    if package_final != gate:
        fail('package_final_validators sequence must exactly equal gate sequence')
    if not CRITICAL_GATE_STEPS.issubset(set(gate)):
        missing = sorted(CRITICAL_GATE_STEPS - set(gate))
        fail(f'gate sequence missing critical steps: {missing}')
    publish_audit = scripts_for(contract, 'publish_audit')
    if 'gate.py' in publish_audit or 'scripts/gate.py' in publish_audit:
        fail('publish_audit sequence must not call gate.py')
    if publish_audit[:3] != ['build_release_queue_index.py', 'build_release_ledger.py', 'materialize_public_release.py']:
        fail('publish_audit sequence must begin with queue index, release ledger, and materialization')
    if publish_audit[-2:] != ['validate_publishing.py', 'validate_archive_identity.py']:
        fail('publish_audit sequence must end with publishing and archive identity validators')
    refresh = scripts_for(contract, 'package_refresh')
    if refresh != ['build_asset_indexes.py', 'build_dedupe_report.py', 'rebuild_indexes.py']:
        fail('package_refresh sequence must contain only scoped builders')
    if (ROOT / SEQUENCE_MD).read_text(encoding='utf-8') != render_markdown(contract):
        fail(f'{SEQUENCE_MD} must exactly mirror {SEQUENCE_JSON}')
    return None


def validate_runner_consumption(contract: dict) -> None:
    text_gate = (ROOT / 'scripts/gate.py').read_text(encoding='utf-8')
    text_publish = (ROOT / 'scripts/publish_audit.py').read_text(encoding='utf-8')
    text_package = (ROOT / 'scripts/package_release.py').read_text(encoding='utf-8')
    for script_rel, text, seq_id in [
        ('scripts/gate.py', text_gate, 'gate'),
        ('scripts/publish_audit.py', text_publish, 'publish_audit'),
    ]:
        if SEQUENCE_JSON not in text:
            fail(f'{script_rel} must reference {SEQUENCE_JSON}')
        if f"load_sequence('{seq_id}')" not in text:
            fail(f'{script_rel} must load {seq_id} from the command-runner sequence contract')
        if re.search(r'\nSEQUENCE\s*=\s*\[', text):
            fail(f'{script_rel} must not carry a literal SEQUENCE list')
        validate_subprocess_isolation(script_rel, text)
    if SEQUENCE_JSON not in text_package:
        fail('scripts/package_release.py must reference COMMAND_RUNNER_SEQUENCE.json')
    for seq_id in ('package_refresh', 'package_final_validators'):
        if f"load_runner_sequence('{seq_id}')" not in text_package:
            fail(f'scripts/package_release.py must load {seq_id} from the command-runner sequence contract')
    for snippet in ['RELEASE_ARTIFACT_VERIFIER', 'verify_release_artifact.py', 'write_sha256_sidecar', 'run_release_artifact_verifier', '--require-sidecar']:
        if snippet not in text_package:
            fail(f'scripts/package_release.py missing release-artifact verifier/sidecar snippet: {snippet}')
    text_rights_helper = (ROOT / 'scripts/publication_rights_gate.py').read_text(encoding='utf-8')
    for snippet in ['RIGHTS/component_license_ledger.json', 'assert_publication_rights_ready', 'publication rights gate blocked', 'decision_required_before_publication', 'blocking_findings', 'root_license_or_notice_file_present', 'root_license_or_notice_file_absent', 'def main() -> int', '--context']:
        if snippet not in text_rights_helper:
            fail(f'scripts/publication_rights_gate.py missing publication-rights gate snippet: {snippet}')
    for script_rel, text, context, first_mutation in [
        ('scripts/publish_audit.py', text_publish, 'publish-audit', "\n    for script_name in load_sequence('publish_audit')"),
        ('scripts/package_release.py', text_package, 'package-release', '\n    run_package_refresh_sequence()'),
        ('scripts/materialize_public_release.py', (ROOT / 'scripts/materialize_public_release.py').read_text(encoding='utf-8'), 'materialize-public-release', 'records = []'),
        ('scripts/publish_queue_item.py', (ROOT / 'scripts/publish_queue_item.py').read_text(encoding='utf-8'), 'publish-queue-item', '\n    state, path = find_item(args.item)'),
        ('scripts/transition_queue_item.py', (ROOT / 'scripts/transition_queue_item.py').read_text(encoding='utf-8'), 'transition-queue-item', '\n    src_state, json_path = find_item(args.item)'),
    ]:
        if 'from publication_rights_gate import assert_publication_rights_ready' not in text:
            fail(f'{script_rel} must import shared publication rights gate helper')
        guard_call = text.find(f"assert_publication_rights_ready(ROOT, '{context}')")
        mutation_call = text.find(first_mutation)
        if guard_call < 0 or mutation_call < 0 or guard_call > mutation_call:
            fail(f'{script_rel} must run publication rights gate before first publication mutation marker')
    refresh_call = text_package.find('\n    run_package_refresh_sequence()')
    package_guard_call = text_package.find("\n    assert_publication_rights_ready(ROOT, 'package-release')")
    root_name_call = text_package.find('\n    assert_root_name()')
    if package_guard_call < 0 or refresh_call < 0 or package_guard_call > refresh_call:
        fail('scripts/package_release.py must run publication rights gate before package refresh')
    if root_name_call < 0 or package_guard_call > root_name_call:
        fail('scripts/package_release.py must run publication rights gate before root-name checks')

    text_verifier = (ROOT / 'scripts/verify_release_artifact.py').read_text(encoding='utf-8')
    for snippet in ['validate_embedded_index', 'validate_embedded_identity_digests', 'IDENTITY_DIGEST_TARGETS', 'INDEX_FIELDS', 'embedded INDEX/files.json', 'embedded INDEX/files.csv', 'validate_included_roots_coverage', 'included_roots', 'validate_embedded_ro_crate_metadata', 'RO_CRATE_REQUIRED_HAS_PARTS', 'RO_CRATE_DIGESTED_FILE_ENTITIES', 'embedded RO-Crate', 'RO_CRATE_PROFILE.md', 'validate_embedded_public_status', 'PUBLIC_STATUS.json', 'public_status_delta', 'latest_public_release', 'validate_embedded_claim_obligation_map', 'CLAIM_OBLIGATION_MAP.json', 'claim_obligations', 'claim_crosswalk', 'validate_embedded_revision_anchors', 'REVISION_ANCHORS.json', 'validator inventory mismatch', 'anchored_surfaces', 'validate_embedded_toolchain_lock', 'TOOLCHAIN_LOCK.json', 'TOOLCHAIN_LOCK.md', 'toolchain_packages', 'package_policy', 'validate_embedded_historical_anomalies', 'HISTORICAL_ANOMALIES.json', 'historical_anomalies', 'historical anomaly count drift', 'validate_embedded_command_runner_sequence', 'COMMAND_RUNNER_SEQUENCE.json', 'command_runner_sequences', 'package_final_validators', 'gate sequence does not mirror embedded VALIDATION_INDEX.json gate composite target', 'validate_embedded_crypto_fixtures', 'CRYPTO_FIXTURE_INDEX.json', 'Ed25519', 'expected Ed25519 DSSE verification']:
        if snippet not in text_verifier:
            fail(f'scripts/verify_release_artifact.py missing embedded index/identity/inclusion/public-status/historical-anomaly/revision-anchor/toolchain/RO-Crate/crypto verifier snippet: {snippet}')

    if re.search(r'PACKAGE_REFRESH_SEQUENCE\s*=\s*\[', text_package):
        fail('scripts/package_release.py must not carry a literal PACKAGE_REFRESH_SEQUENCE list')
    if re.search(r'for script_name in \[', text_package):
        fail('scripts/package_release.py must not carry a literal package-final validator list')
    validate_subprocess_isolation('scripts/package_release.py', text_package)


def validate_subprocess_isolation(script_rel: str, text: str | None = None) -> None:
    text = text if text is not None else (ROOT / script_rel).read_text(encoding='utf-8')
    required = [
        'import subprocess',
        'sys.dont_write_bytecode = True',
        "env['PYTHONDONTWRITEBYTECODE'] = '1'",
        'cwd=ROOT',
        'check=True',
    ]
    for snippet in required:
        if snippet not in text:
            fail(f'{script_rel} missing subprocess-isolation snippet: {snippet}')
    if script_rel == 'scripts/gate.py':
        command_ok = "subprocess.run([sys.executable, '-u', str(script)]" in text
        if "env['PYTHONUNBUFFERED'] = '1'" not in text:
            fail('scripts/gate.py must force unbuffered child output for diagnosable long gate runs')
    else:
        command_ok = 'subprocess.run([sys.executable, str(script)]' in text
    if not command_ok:
        fail(f'{script_rel} missing subprocess-isolation command invocation')


def validate_makefile(contract: dict) -> None:
    text = (ROOT / 'Makefile').read_text(encoding='utf-8')
    targets = {
        'gate': 'scripts/gate.py',
        'publish-audit': 'scripts/publish_audit.py',
        'package-release': 'scripts/package_release.py',
        'runner-check': 'scripts/validate_command_runners.py',
        'release-ledgers': 'scripts/publication_rights_gate.py --context release-ledgers',
    }
    for target, command in targets.items():
        if f'{target}:' not in text:
            fail(f'Makefile missing target {target}')
        if command not in text:
            fail(f'Makefile target {target} missing command {command}')


def validate_preflight_shell() -> None:
    path = ROOT / 'scripts/publish_preflight.sh'
    text = path.read_text(encoding='utf-8')
    for snippet in ['set -euo pipefail', 'python3 scripts/publication_rights_gate.py --context publish-preflight', 'python3 scripts/gate.py', 'sha256sum -c MANIFEST.sha256']:
        if snippet not in text:
            fail(f'publish_preflight.sh missing required snippet: {snippet}')
    for rel in PREFLIGHT_REQUIRED_FILE_SENTINELS:
        if rel not in text:
            fail(f'publish_preflight.sh missing required file sentinel: {rel}')
    for rel in PREFLIGHT_REQUIRED_DIR_SENTINELS:
        if rel not in text:
            fail(f'publish_preflight.sh missing required directory sentinel: {rel}')


def validate_transient_policy_constants() -> None:
    skip = literal_value('scripts/package_release.py', 'TRANSIENT_SKIP_ROOTS')
    patterns = literal_value('scripts/package_release.py', 'TRANSIENT_BUILD_PATTERNS')
    if set(skip) != EXPECTED_TRANSIENT_SKIP_ROOTS:
        fail('scripts/package_release.py transient skip roots drift')
    if patterns != EXPECTED_TRANSIENT_BUILD_PATTERNS:
        fail('scripts/package_release.py transient build patterns drift')
    preflight = (ROOT / 'scripts/publish_preflight.sh').read_text(encoding='utf-8')
    for root in sorted(EXPECTED_TRANSIENT_SKIP_ROOTS):
        if f'/{root}/' not in preflight and f'"{root}"' not in preflight and f"'{root}'" not in preflight:
            fail(f'publish_preflight.sh missing transient skip root {root}')
    for pattern in EXPECTED_TRANSIENT_BUILD_PATTERNS:
        if pattern not in preflight:
            fail(f'publish_preflight.sh missing transient build pattern {pattern}')


def validate_governed_wiring(contract: dict) -> None:
    policy = load_json('publishing/CANONICAL_POLICY.json')
    context = load_json('CONTEXT_PACK.json')
    validation = load_json('VALIDATION_INDEX.json')
    control = load_json('CONTROL_SURFACES.json')
    gates = load_json('LIFECYCLE_GATES.json')
    anchors = load_json('REVISION_ANCHORS.json')
    manifest = load_json('RELEASE_MANIFEST.json')
    registry = load_json('schemas/registry.json')
    for key, expected in {
        'command_runner_sequence_json': SEQUENCE_JSON,
        'command_runner_sequence_markdown': SEQUENCE_MD,
        'command_runner_sequence_schema': SEQUENCE_SCHEMA,
        'command_runner_validator': 'scripts/validate_command_runners.py',
        'release_artifact_verifier': 'scripts/verify_release_artifact.py',
        'release_artifact_verifier_validator': 'scripts/validate_command_runners.py',
    }.items():
        if policy.get(key) != expected:
            fail(f'publishing/CANONICAL_POLICY.json {key} mismatch')
    if 'explicit_command_runner_sequence_contract_validation' not in policy.get('principles', []):
        fail('publishing/CANONICAL_POLICY.json principles missing explicit_command_runner_sequence_contract_validation')
    kms = context.get('key_machine_surfaces', {})
    for key, expected in {
        'command_runner_sequence_json': SEQUENCE_JSON,
        'command_runner_sequence_markdown': SEQUENCE_MD,
        'command_runner_sequence_schema': SEQUENCE_SCHEMA,
        'command_runner_validator': 'scripts/validate_command_runners.py',
        'release_artifact_verifier': 'scripts/verify_release_artifact.py',
        'release_artifact_verifier_validator': 'scripts/validate_command_runners.py',
    }.items():
        if kms.get(key) != expected:
            fail(f'CONTEXT_PACK.json key_machine_surfaces.{key} mismatch')
    if 'python3 scripts/validate_command_runners.py' not in context.get('checks', []):
        fail('CONTEXT_PACK.json checks missing command-runner validator')
    checks = {check['id']: check for check in validation.get('checks', [])}
    runner = checks.get('runner-check')
    if runner is None:
        fail('VALIDATION_INDEX.json missing runner-check')
    if runner.get('scripts') != ['scripts/validate_command_runners.py']:
        fail('runner-check scripts mismatch')
    required_runner_validates = {
        SEQUENCE_JSON, SEQUENCE_MD, SEQUENCE_SCHEMA,
        'scripts/gate.py', 'scripts/publish_audit.py', 'scripts/package_release.py', 'scripts/verify_release_artifact.py', 'scripts/publish_preflight.sh',
        'Makefile', 'CONTEXT_PACK.json', 'CONTROL_SURFACES.json', 'LIFECYCLE_GATES.json',
        'VALIDATION_INDEX.json', 'publishing/CANONICAL_POLICY.json', 'REVISION_ANCHORS.json', 'RELEASE_MANIFEST.json', 'schemas/registry.json',
    }
    if not required_runner_validates.issubset(set(runner.get('validates', []))):
        missing = sorted(required_runner_validates - set(runner.get('validates', [])))
        fail(f'runner-check validates missing surfaces: {missing}')
    json_check = checks.get('json-check')
    if json_check and not {SEQUENCE_JSON, SEQUENCE_SCHEMA}.issubset(set(json_check.get('validates', []))):
        fail('json-check validates missing command-runner sequence surfaces')
    preflight = checks.get('preflight')
    if preflight and not {SEQUENCE_JSON, SEQUENCE_MD, SEQUENCE_SCHEMA}.issubset(set(preflight.get('validates', []))):
        fail('preflight validates missing command-runner sequence surfaces')
    validation_paths = {item['path'] for item in control.get('surfaces', {}).get('validation_and_packaging', [])}
    opening_paths = {item['path'] for item in control.get('surfaces', {}).get('opening_and_resumption', [])}
    for rel in (SEQUENCE_JSON, SEQUENCE_MD, SEQUENCE_SCHEMA, 'scripts/validate_command_runners.py', 'scripts/verify_release_artifact.py'):
        if rel not in validation_paths:
            fail(f'CONTROL_SURFACES.json validation_and_packaging missing {rel}')
    for rel in (SEQUENCE_JSON, SEQUENCE_MD):
        if rel not in opening_paths:
            fail(f'CONTROL_SURFACES.json opening_and_resumption missing {rel}')
    for gate_id in ('careful_revision_pass', 'publish_audit', 'named_bundle_packaging'):
        refs = set(gates['gates'][gate_id].get('authoritative_sequence', []) + gates['gates'][gate_id].get('required_surfaces', []) + gates['gates'][gate_id].get('checks', []))
        if 'scripts/validate_command_runners.py' not in refs:
            fail(f'LIFECYCLE_GATES.json {gate_id} missing command-runner validator')
    package_refs = set(gates['gates']['named_bundle_packaging'].get('required_surfaces', []))
    if SEQUENCE_JSON not in package_refs or SEQUENCE_MD not in package_refs:
        fail('LIFECYCLE_GATES.json named_bundle_packaging missing command-runner sequence contract surfaces')
    if 'scripts/verify_release_artifact.py' not in package_refs:
        fail('LIFECYCLE_GATES.json named_bundle_packaging missing release artifact verifier surface')
    anchored = {item['path']: item for item in anchors.get('anchored_surfaces', [])}
    if SEQUENCE_JSON not in anchored:
        fail('REVISION_ANCHORS.json missing COMMAND_RUNNER_SEQUENCE.json anchor')
    if 'scripts/validate_command_runners.py' not in set(anchors.get('validators', [])):
        fail('REVISION_ANCHORS.json validators missing command-runner validator')
    for rel in (SEQUENCE_JSON, SEQUENCE_MD):
        if rel not in manifest.get('included_roots', []):
            fail(f'RELEASE_MANIFEST.json included_roots missing {rel}')
    if manifest.get('identity_digests', {}).get('command_runner_sequence_json_sha256') is None:
        fail('RELEASE_MANIFEST.json identity_digests missing command_runner_sequence_json_sha256')
    if manifest.get('release_artifact_verifier') != 'scripts/verify_release_artifact.py':
        fail('RELEASE_MANIFEST.json release_artifact_verifier mismatch')
    if manifest.get('release_artifact_verifier_validator') != 'scripts/validate_command_runners.py':
        fail('RELEASE_MANIFEST.json release_artifact_verifier_validator mismatch')
    if manifest.get('identity_digests', {}).get('release_artifact_verifier_sha256') is None:
        fail('RELEASE_MANIFEST.json identity_digests missing release_artifact_verifier_sha256')
    if manifest.get('identity_digests', {}).get('release_artifact_verifier_validator_sha256') is None:
        fail('RELEASE_MANIFEST.json identity_digests missing release_artifact_verifier_validator_sha256')
    if registry.get(SEQUENCE_JSON) != 'command_runner_sequence.schema.json':
        fail('schemas/registry.json missing COMMAND_RUNNER_SEQUENCE.json schema entry')


def main() -> None:
    print('command-runner-validate: loading governed sequence contract', flush=True)
    for rel in (SEQUENCE_JSON, SEQUENCE_MD, SEQUENCE_SCHEMA):
        require(rel)
    contract = load_json(SEQUENCE_JSON)
    validate_schema(contract)
    validate_contract(contract)
    validate_runner_consumption(contract)
    validate_makefile(contract)
    validate_preflight_shell()
    validate_transient_policy_constants()
    validate_governed_wiring(contract)
    print(
        'command-runner-validate: OK '
        f"(gate={len(scripts_for(contract, 'gate'))}, "
        f"publish-audit={len(scripts_for(contract, 'publish_audit'))}, "
        f"package-refresh={len(scripts_for(contract, 'package_refresh'))}, "
        f"package-final={len(scripts_for(contract, 'package_final_validators'))}, "
        'sequence-contract=governed)'
    )


if __name__ == '__main__':
    main()
