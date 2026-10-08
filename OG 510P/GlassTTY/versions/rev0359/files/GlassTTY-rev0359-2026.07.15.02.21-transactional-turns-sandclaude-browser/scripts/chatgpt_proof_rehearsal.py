#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_first_proof_evaluator import evaluate_payload
from chatgpt_first_proof_kit import EXPECTED_REPLY, PROBE_TEXT
from chatgpt_surface_report_audit import extract_json_object
from chatgpt_contract_paths import active_contract_path

try:
    from chatgpt_surface_contract import check_contract
except Exception:  # pragma: no cover - script import resilience
    check_contract = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTRACT = active_contract_path(ROOT)
DEFAULT_OUT = ROOT / 'validation' / 'latest' / 'chatgpt-proof-rehearsal.json'
DEFAULT_EVAL_OUT = ROOT / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evaluation'
ATTEMPT_ID = 'chatgpt-proof-rehearsal-001'
TAB_ID = 7331

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def read_json(path: Path) -> JsonDict:
    parsed = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(parsed, dict):
        raise ValueError(f'{path} is not a JSON object')
    return parsed




def display_path(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except Exception:
        return str(path)


def read_report(path: Path | None) -> JsonDict | None:
    if path is None:
        return None
    return extract_json_object(path.read_text(encoding='utf-8'))


def _path(value: JsonDict, dotted: str, default: Any = None) -> Any:
    current: Any = value
    for part in dotted.split('.'):
        if not isinstance(current, dict):
            return default
        current = current.get(part)
    return default if current is None else current


def _contract_prompt_selector(contract: JsonDict | None) -> str:
    if not isinstance(contract, dict):
        return '#prompt-textarea'
    value = _path(contract, 'required.prompt_selector')
    return value if isinstance(value, str) and value else '#prompt-textarea'


def _contract_send_selector(contract: JsonDict | None) -> str:
    if not isinstance(contract, dict):
        return '#composer-submit-button'
    value = _path(contract, 'required.strict_send.selector')
    return value if isinstance(value, str) and value else '#composer-submit-button'


def _contract_send_testid(contract: JsonDict | None) -> str:
    value = _path(contract or {}, 'required.strict_send.data_testid')
    return value if isinstance(value, str) and value else 'send-button'


def _contract_send_aria(contract: JsonDict | None) -> str:
    value = _path(contract or {}, 'required.strict_send.aria_label')
    return value if isinstance(value, str) and value else 'Send prompt'


def _contract_check(report: JsonDict | None, contract: JsonDict | None) -> JsonDict | None:
    if report is None or contract is None or check_contract is None:
        return None
    return check_contract(report, contract)


def assistant_witness(text: str = EXPECTED_REPLY) -> JsonDict:
    return {
        'text': text,
        'selector_hint': '[data-message-author-role="assistant"]',
        'selection_policy': 'latest-visible-assistant-like-node-in-dom-order',
        'assistant_like': True,
        'author_role': 'assistant',
        'author_role_source': 'self',
        'node_tag': 'div',
        'candidate_score': 0.91,
        'document_order_index': 120,
        'frame_depth': 0,
        'frame_path': 'top',
    }


def user_witness(text: str = PROBE_TEXT) -> JsonDict:
    return {
        'text': text,
        'selector_hint': '[data-message-author-role="user"]',
        'selection_policy': 'latest-visible-user-like-node-in-dom-order',
        'user_like': True,
        'author_role': 'user',
        'author_role_source': 'self',
        'node_tag': 'div',
        'candidate_score': 0.88,
        'document_order_index': 90,
        'frame_depth': 0,
        'frame_path': 'top',
    }


def action_policy(contract: JsonDict | None) -> JsonDict:
    return {
        'submit_method': 'button-click-only',
        'keyboard_submit_enabled': False,
        'route_posture_allows_submit': True,
        'prompt_present_for_submit': True,
        'submit_button_found': True,
        'submit_button_min_score': 0.45,
        'submit_button_requires_explicit_send_intent': True,
        'submit_button_rejects_non_send_composer_controls': True,
        'observed_live_send_selector': _contract_send_selector(contract),
        'observed_live_send_testid': _contract_send_testid(contract),
        'observed_live_send_aria_label': _contract_send_aria(contract),
        'submit_button_live_surface_lock': '#composer-submit-button[data-testid=send-button]',
        'empty_composer_missing_send_is_allowed': True,
    }


def build_rehearsal_payload(*, report: JsonDict | None = None, contract: JsonDict | None = None,
                            contract_path: Path | None = None, report_path: Path | None = None) -> JsonDict:
    checked = _contract_check(report, contract)
    prompt_selector = _contract_prompt_selector(contract)
    send_selector = _contract_send_selector(contract)
    send_testid = _contract_send_testid(contract)
    send_aria = _contract_send_aria(contract)
    generated_at = utcnow()
    return {
        'schema_version': 1,
        'tool': 'glasstty-chatgpt-proof-rehearsal',
        'generated_at': generated_at,
        'proof_mode': 'offline-rehearsal',
        'rehearsal_only': True,
        'live_proof': False,
        'support_claim_state': 'no-support-claim; synthetic harness rehearsal only',
        'surface_key': 'chatgpt',
        'attempt_id': ATTEMPT_ID,
        'source_inputs': {
            'surface_report_path': display_path(report_path),
            'surface_contract_path': display_path(contract_path),
            'surface_contract_verdict': checked.get('verdict') if isinstance(checked, dict) else None,
        },
        'surface_contract_check': checked,
        'privacy_redaction_review': {
            'review_required_before_publication': True,
            'publishable_without_redaction_review': False,
            'reviewer': 'offline-rehearsal-generator',
            'notes': [
                'This is synthetic local evidence for harness testing only.',
                'It must not be promoted as a live ChatGPT proof bundle.',
            ],
        },
        'captures': {
            'after_write': {
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/',
                'tab_id': TAB_ID,
                'prompt': PROBE_TEXT,
                'metadata': {
                    'route_posture': 'plain-chat',
                    'surface_route': '/',
                    'prompt_selector': prompt_selector,
                    'rehearsal_only': True,
                    'action_policy': action_policy(contract),
                },
            },
            'after_generation': {
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/c/rehearsal-checkpoint',
                'tab_id': TAB_ID,
                'latest_output': EXPECTED_REPLY,
                'latest_output_witness': assistant_witness(),
                'latest_user_turn_witness': user_witness(),
                'metadata': {
                    'route_posture': 'plain-chat',
                    'surface_route': '/c/rehearsal-checkpoint',
                    'generation_state': 'settled-or-idle',
                    'generation_stop_control_present': False,
                    'generation_continue_control_present': False,
                    'latest_turn_pair_same_frame': True,
                    'latest_turn_pair_user_before_assistant': True,
                    'submit_selector': send_selector,
                    'submit_signal_explicit': True,
                    'submit_signal_disqualified': False,
                    'rehearsal_only': True,
                    'action_policy': action_policy(contract),
                },
            },
        },
        'actions': [
            {
                'sequence_index': 0,
                'tab_id': TAB_ID,
                'type': 'prompt.write',
                'ok': True,
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/',
                'readback': PROBE_TEXT,
                'selector_hint': prompt_selector,
                'rehearsal_only': True,
            },
            {
                'sequence_index': 1,
                'tab_id': TAB_ID,
                'type': 'prompt.submit',
                'ok': True,
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/',
                'operator_submit_confirmed': True,
                'operator_action': 'sidepanel-chatgpt-first-proof-submit-button',
                'submit_method': 'sidepanel-operator-click',
                'proof_live_gate_verdict': 'proof-live-gate-ok',
                'proof_live_gate_ok': True,
                'proof_live_gate_checked_at': generated_at,
                'proof_live_gate_expected': {
                    'surface_key': 'chatgpt',
                    'route_posture': 'plain-chat',
                    'prompt_selector': prompt_selector,
                    'send_selector': send_selector,
                    'send_testid': send_testid,
                    'send_aria_label': send_aria,
                },
                'proof_live_gate_observed': {
                    'adapter': 'chatgpt',
                    'route_posture': 'plain-chat',
                    'prompt_selector': prompt_selector,
                    'prompt_text_matches_checkpoint': True,
                    'submit_selector': send_selector,
                    'submit_signal_intent': True,
                    'submit_signal_explicit': True,
                    'submit_signal_disqualified': False,
                    'action_policy_route_safe': True,
                    'action_policy_prompt_present': True,
                    'action_policy_button_found': True,
                },
                'composer_readback_before_submit': PROBE_TEXT,
                'prompt_before_submit': PROBE_TEXT,
                'submitted_prompt': PROBE_TEXT,
                'submit_selector': send_selector,
                'submit_data_testid': send_testid,
                'submit_aria_label': send_aria,
                'rehearsal_only': True,
            },
            {
                'sequence_index': 2,
                'tab_id': TAB_ID,
                'type': 'transcript.latest',
                'ok': True,
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/c/rehearsal-checkpoint',
                'payload': {
                    'text': EXPECTED_REPLY,
                    'latest_output_witness': assistant_witness(),
                    'latest_user_turn_witness': user_witness(),
                    'adapter': 'chatgpt',
                    'url': 'https://chatgpt.com/c/rehearsal-checkpoint',
                    'tab_id': TAB_ID,
                    'rehearsal_only': True,
                },
            },
            {
                'sequence_index': 3,
                'tab_id': TAB_ID,
                'type': 'fixture.capture',
                'ok': True,
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/c/rehearsal-checkpoint',
                'payload': {
                    'adapter': 'chatgpt',
                    'url': 'https://chatgpt.com/c/rehearsal-checkpoint',
                    'tab_id': TAB_ID,
                    'metadata': {
                        'route_posture': 'plain-chat',
                        'surface_route': '/c/rehearsal-checkpoint',
                        'generation_state': 'settled-or-idle',
                        'generation_stop_control_present': False,
                        'rehearsal_only': True,
                    },
                },
            },
        ],
        'artifacts': {
            'rehearsal_note': 'No screenshot, browser trace, or live bundle artifact is produced by this dry run.',
        },
    }


def run_rehearsal(*, surface_report: Path | None = None, contract_path: Path | None = DEFAULT_CONTRACT,
                  out: Path = DEFAULT_OUT, evaluation_out: Path = DEFAULT_EVAL_OUT,
                  strict_surface: bool = False) -> JsonDict:
    report = read_report(surface_report)
    contract = read_json(contract_path) if contract_path and contract_path.exists() else None
    payload = build_rehearsal_payload(report=report, contract=contract, contract_path=contract_path,
                                      report_path=surface_report)
    verdict = (payload.get('surface_contract_check') or {}).get('verdict') if isinstance(payload.get('surface_contract_check'), dict) else None
    if strict_surface and verdict and verdict != 'surface-contract-ok':
        payload['strict_surface_failure'] = True
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    evaluation = evaluate_payload(payload, root=ROOT, input_path=out)
    evaluation_out.mkdir(parents=True, exist_ok=True)
    (evaluation_out / 'chatgpt-proof-rehearsal-evaluation.json').write_text(
        json.dumps(evaluation, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    summary = {
        'schema_version': 1,
        'tool': 'glasstty-chatgpt-proof-rehearsal-runner',
        'generated_at': utcnow(),
        'ok': evaluation.get('verdict') == 'rehearsal-harness-ok-not-live' and not payload.get('strict_surface_failure'),
        'payload_path': display_path(out),
        'evaluation_path': display_path(evaluation_out / 'chatgpt-proof-rehearsal-evaluation.json'),
        'surface_contract_verdict': verdict,
        'strict_surface_failure': bool(payload.get('strict_surface_failure')),
        'evaluator_verdict': evaluation.get('verdict'),
        'evaluator_harness_ok': evaluation.get('harness_ok'),
        'evaluator_missing_required_checks': evaluation.get('missing_required_checks'),
        'proof_mode': evaluation.get('proof_mode'),
        'rehearsal_only': evaluation.get('rehearsal_only'),
    }
    (evaluation_out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Build and evaluate an offline ChatGPT proof rehearsal bundle.')
    parser.add_argument('--surface-report', type=Path, help='Optional GlassTTY surface report/capsule/drill JSON to check against the contract')
    parser.add_argument('--contract', type=Path, default=DEFAULT_CONTRACT, help='Surface contract JSON to embed/check')
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT, help='Output path for the rehearsal proof payload')
    parser.add_argument('--evaluation-out', type=Path, default=DEFAULT_EVAL_OUT, help='Output directory for rehearsal evaluation artifacts')
    parser.add_argument('--strict-surface', action='store_true', help='Mark rehearsal not-ok if supplied surface report does not satisfy the contract')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args(argv)
    summary = run_rehearsal(
        surface_report=args.surface_report,
        contract_path=args.contract,
        out=args.out,
        evaluation_out=args.evaluation_out,
        strict_surface=args.strict_surface,
    )
    print(json.dumps(summary, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if summary.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
