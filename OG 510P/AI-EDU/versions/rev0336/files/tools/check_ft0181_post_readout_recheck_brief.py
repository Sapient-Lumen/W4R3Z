#!/usr/bin/env python3
"""Smoke-test the FT-0181 post-readout recheck brief bridge."""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

from prepare_ft0181_post_readout_recheck_brief import build_post_readout_recheck_brief
from record_ft0181_live_window_readout import OPERATOR_CONFIRMATION as READOUT_CONFIRMATION, build_live_window_readout
from record_ft0181_post_readout_action import OPERATOR_CONFIRMATION as ACTION_CONFIRMATION, build_post_readout_action
from ft0181_field_guards import owner_post_readout_recheck_brief_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-post-readout-recheck-brief'
HELPER = ROOT / 'tools' / 'check_ft0181_live_window_readout_brief.py'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_card_builder():
    spec = importlib.util.spec_from_file_location('ft0181_readout_brief_check_for_recheck_brief', HELPER)
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
card = build_card('completed-no-closure', 'post-recheck-brief-source')
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
action_result = build_post_readout_action(
    readout=readout,
    dispatch_lane='continue-same-ceiling',
    source_truth_class='SRC2',
    allowed_action_count=1,
    prohibited_action_count=5,
    field_to_reask_count=0,
    field_to_drop_count=0,
    reviewer_role_count=2,
    unresolved_disagreement_count=0,
    due_or_recheck_date='2026-06-25',
    owner_action_class='continue-within-same-ceiling',
    next_evidence_ask_class='bounded-owner-recheck',
    public_language_action='frozen-example-only',
    no_expansion_confirmed=True,
    no_public_claim_upgrade=True,
    no_service_record_edit=True,
    no_lifecycle_change=True,
    no_closure_from_dispatch=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=ACTION_CONFIRMATION,
    output_dir=TMP / 'owner-post-readout-actions' / 'valid',
)
if not action_result.get('ok'):
    fail(errors, f'valid source action did not build: {action_result}')
action = TMP / 'owner-post-readout-actions' / 'valid' / 'post-readout-action.json'
result = build_post_readout_recheck_brief(
    action=action,
    as_of_date='2026-06-25',
    output_dir=TMP / 'owner-post-readout-recheck-briefs' / 'valid',
)
if result.get('outcome') != 'POST-READOUT-RECHECK-BRIEF-PREPARED':
    fail(errors, f'valid post-readout recheck brief should prepare: {result}')
brief_path = TMP / 'owner-post-readout-recheck-briefs' / 'valid' / 'post-readout-recheck-brief.json'
brief = load_json(brief_path)
err = owner_post_readout_recheck_brief_integrity_error(brief, archive_root=ROOT)
if err:
    fail(errors, f'valid post-readout recheck brief should pass guard: {err}')
commands = brief.get('post_readout_recheck_command_templates', {})
primary = commands.get('primary', '')
for token in [
    'make owner-post-readout-recheck',
    'RECHECK_OUTCOME=no-new-owner-context',
    'CHECK_DATE=2026-06-25',
    'CONFIRM=human-recorded-post-readout-recheck-no-closure',
    'NO_SERVICE_RECORD_EDIT=1',
    'NO_CLOSURE_FROM_RECHECK=1',
]:
    if token not in primary:
        fail(errors, f'primary recheck command missing {token}: {primary}')
new_context = commands.get('new_owner_context_available', '')
if 'RECHECK_OUTCOME=new-owner-context-available' not in new_context or 'NEW_OWNER_CONTEXT_HELD_OUTSIDE_ARCHIVE=1' not in new_context:
    fail(errors, f'new-context command should hold context outside archive: {new_context}')
for name, command in commands.items():
    for forbidden in ['make owner-post-readout-context-receipt', 'make owner-field-next', 'csv=', 'student id', '@example', 'raw lms telemetry']:
        if forbidden in command.lower():
            fail(errors, f'{name} command leaked or jumped ahead via {forbidden}: {command}')

try:
    build_post_readout_recheck_brief(action=action, as_of_date='2026-06-24', output_dir=TMP / 'owner-post-readout-recheck-briefs' / 'too-early')
    fail(errors, 'recheck brief should not prepare before the dispatch due date')
except ValueError as exc:
    if 'TOO-EARLY-BLOCKED' not in str(exc):
        fail(errors, f'too-early block should name due-date block: {exc}')

try:
    build_post_readout_recheck_brief(action=readout, as_of_date='2026-06-25', output_dir=TMP / 'owner-post-readout-recheck-briefs' / 'bad-readout')
    fail(errors, 'live-window readout path should not be accepted as a recheck brief source')
except ValueError as exc:
    if 'ACTION-BLOCKED' not in str(exc):
        fail(errors, f'wrong source path should name action block: {exc}')

tampered = dict(brief)
tampered['recheck_effect'] = 'records_post_readout_recheck'
err = owner_post_readout_recheck_brief_integrity_error(tampered, archive_root=ROOT)
if not err or 'recheck_effect' not in err:
    fail(errors, f'tampered brief should fail recheck-effect guard, got {err}')

tampered = json.loads(json.dumps(brief))
tampered['post_readout_recheck_command_templates']['new_owner_context_available'] = tampered['post_readout_recheck_command_templates']['new_owner_context_available'].replace('NEW_OWNER_CONTEXT_HELD_OUTSIDE_ARCHIVE=1 ', '')
err = owner_post_readout_recheck_brief_integrity_error(tampered, archive_root=ROOT)
if not err or 'NEW_OWNER_CONTEXT_HELD_OUTSIDE_ARCHIVE' not in err:
    fail(errors, f'new-context command without holdout flag should fail, got {err}')

text = brief_path.read_text(encoding='utf-8') + (TMP / 'owner-post-readout-recheck-briefs' / 'valid' / 'POST-READOUT-RECHECK-BRIEF.md').read_text(encoding='utf-8')
for forbidden in ['student id', 'learner name', '@example', 'chat transcript', 'raw lms telemetry']:
    if forbidden in text.lower():
        fail(errors, f'brief leaked forbidden/raw/contact/claim term: {forbidden}')

if errors:
    raise SystemExit('check_ft0181_post_readout_recheck_brief errors:\n' + '\n'.join(errors))
print('check_ft0181_post_readout_recheck_brief: OK')
