#!/usr/bin/env python3
"""Smoke-test the FT-0181 post-readout action brief bridge."""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

from prepare_ft0181_post_readout_action_brief import build_post_readout_action_brief
from record_ft0181_live_window_readout import OPERATOR_CONFIRMATION as READOUT_CONFIRMATION, build_live_window_readout
from ft0181_field_guards import owner_post_readout_action_brief_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-post-readout-action-brief'
HELPER = ROOT / 'tools' / 'check_ft0181_live_window_readout_brief.py'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_card_builder():
    spec = importlib.util.spec_from_file_location('ft0181_readout_brief_check_for_action_brief', HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError('could not load live-window readout brief check helper')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_card


if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True, exist_ok=True)
errors: list[str] = []

build_card = load_card_builder()
card = build_card('completed-no-closure', 'post-action-brief-source')
readout_result = build_live_window_readout(
    card=card,
    window_disposition='continue-bounded',
    source_truth_class='SRC2',
    aggregate_evidence_read_count=3,
    claim_family_effect_count=2,
    decision_delta_count=1,
    field_trim_count=0,
    reviewer_role_count=2,
    unresolved_disagreement_count=0,
    public_claim_ceiling='example-only-no-outcome-claim',
    no_public_claim_upgrade=True,
    no_service_record_edit=True,
    no_lifecycle_change=True,
    no_closure_from_readout=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=READOUT_CONFIRMATION,
    output_dir=TMP / 'owner-live-window-readouts' / 'valid',
)
if not readout_result.get('ok'):
    fail(errors, f'valid source readout did not build: {readout_result}')
readout = TMP / 'owner-live-window-readouts' / 'valid' / 'live-window-readout.json'
result = build_post_readout_action_brief(
    readout=readout,
    as_of_date='2026-06-18',
    output_dir=TMP / 'owner-post-readout-action-briefs' / 'valid',
)
if result.get('outcome') != 'POST-READOUT-ACTION-BRIEF-PREPARED':
    fail(errors, f'valid post-readout action brief should prepare: {result}')
brief_path = TMP / 'owner-post-readout-action-briefs' / 'valid' / 'post-readout-action-brief.json'
brief = load_json(brief_path)
err = owner_post_readout_action_brief_integrity_error(brief, archive_root=ROOT)
if err:
    fail(errors, f'valid post-readout action brief should pass guard: {err}')
primary = brief.get('post_readout_action_command_templates', {}).get('primary', '')
for token in [
    'make owner-post-readout-action',
    'DISPATCH_LANE=continue-same-ceiling',
    'DUE_OR_RECHECK_DATE=2026-06-25',
    'CONFIRM=human-recorded-post-readout-action-no-closure',
    'NO_SERVICE_RECORD_EDIT=1',
    'NO_CLOSURE_FROM_DISPATCH=1',
]:
    if token not in primary:
        fail(errors, f'primary action command missing {token}: {primary}')
for forbidden in ['make owner-post-readout-recheck', 'make owner-post-readout-context-receipt', 'make owner-live-window-readout']:
    if forbidden in primary:
        fail(errors, f'action brief must not jump to later or earlier command: {forbidden}')
text = brief_path.read_text(encoding='utf-8') + (TMP / 'owner-post-readout-action-briefs' / 'valid' / 'POST-READOUT-ACTION-BRIEF.md').read_text(encoding='utf-8')
for forbidden in ['student id', 'learner name', '@example', 'chat transcript', 'raw lms telemetry']:
    if forbidden in text.lower():
        fail(errors, f'brief leaked forbidden/raw/contact/claim term: {forbidden}')

# Different readout dispositions should map to different dispatch lanes without widening.
for disposition, lane in [('stopped', 'stop'), ('rolled-back', 'rollback-confirmed'), ('quarantine', 'quarantine')]:
    state = {'stopped': 'paused', 'rolled-back': 'rolled-back', 'quarantine': 'quarantined'}[disposition]
    source_card = build_card(state, f'post-action-brief-{lane}')
    out = TMP / 'owner-live-window-readouts' / lane
    build_live_window_readout(
        card=source_card,
        window_disposition=disposition,
        source_truth_class='SRC2',
        aggregate_evidence_read_count=3,
        claim_family_effect_count=2,
        decision_delta_count=0,
        field_trim_count=0,
        reviewer_role_count=2,
        unresolved_disagreement_count=0,
        public_claim_ceiling='example-only-no-outcome-claim',
        no_public_claim_upgrade=True,
        no_service_record_edit=True,
        no_lifecycle_change=True,
        no_closure_from_readout=True,
        raw_learner_data_present=False,
        protected_facts_present=False,
        security_payloads_present=False,
        public_claim_upgrade_requested=False,
        operator_confirmation=READOUT_CONFIRMATION,
        output_dir=out,
    )
    brief_out = TMP / 'owner-post-readout-action-briefs' / lane
    build_post_readout_action_brief(readout=out / 'live-window-readout.json', as_of_date='2026-06-18', output_dir=brief_out)
    command = load_json(brief_out / 'post-readout-action-brief.json')['post_readout_action_command_templates']['primary']
    if f'DISPATCH_LANE={lane}' not in command:
        fail(errors, f'{disposition} should map to dispatch lane {lane}: {command}')

try:
    build_post_readout_action_brief(readout=card, as_of_date='2026-06-18', output_dir=TMP / 'owner-post-readout-action-briefs' / 'bad-card')
    fail(errors, 'live-window card path should not be accepted as a post-readout action brief source')
except ValueError as exc:
    if 'READOUT-BLOCKED' not in str(exc):
        fail(errors, f'wrong source path should name readout block: {exc}')

tampered = dict(brief)
tampered['action_effect'] = 'records_post_readout_action'
err = owner_post_readout_action_brief_integrity_error(tampered, archive_root=ROOT)
if not err or 'action_effect' not in err:
    fail(errors, f'tampered brief should fail action-effect guard, got {err}')

if errors:
    raise SystemExit('check_ft0181_post_readout_action_brief errors:\n' + '\n'.join(errors))
print('check_ft0181_post_readout_action_brief: OK')
