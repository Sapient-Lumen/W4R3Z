#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_contract_paths import active_contract_path, active_fixture_path
from chatgpt_extension_readiness import check_extension_readiness
from chatgpt_proof_rehearsal import run_rehearsal
from chatgpt_surface_contract import check_contract, read_json as read_contract_json, read_payload
from chatgpt_surface_report_audit import audit_surface

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / 'validation' / 'latest' / 'chatgpt-proof-preflight.json'
DEFAULT_REHEARSAL_OUT = ROOT / 'validation' / 'latest' / 'chatgpt-proof-rehearsal.json'
DEFAULT_EVAL_OUT = ROOT / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evaluation'

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')




def display_path(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except Exception:
        return str(path)


def read_json(path: Path) -> JsonDict | None:
    if not path.exists():
        return None
    parsed = json.loads(path.read_text(encoding='utf-8'))
    return parsed if isinstance(parsed, dict) else None


def _path(value: JsonDict | None, dotted: str, default: Any = None) -> Any:
    current: Any = value
    for part in dotted.split('.'):
        if not isinstance(current, dict):
            return default
        current = current.get(part)
    return default if current is None else current


def _static_checks(root: Path) -> JsonDict:
    manifest = read_json(root / 'extension' / 'manifest.json') or {}
    package = read_json(root / 'extension' / 'package.json') or {}
    adapter_index = root / 'extension' / 'src' / 'adapters' / 'index.ts'
    adapter_index_text = adapter_index.read_text(encoding='utf-8') if adapter_index.exists() else ''
    adapter_path = root / 'extension' / 'src' / 'adapters' / 'chatgpt.ts'
    checks = {
        'chatgpt_only_host_permission': manifest.get('host_permissions') == ['https://chatgpt.com/*'],
        'chatgpt_adapter_exists': adapter_path.exists(),
        'adapter_registry_has_only_chatgpt': 'chatgptAdapter' in adapter_index_text and 'export const adapters' in adapter_index_text and 'claude' not in adapter_index_text.lower() and 'gemini' not in adapter_index_text.lower(),
        'surface_oracle_exists': (root / 'tools' / 'chatgpt-surface-oracle.user.js').exists(),
        'proof_rehearsal_exists': (root / 'scripts' / 'chatgpt_proof_rehearsal.py').exists(),
        'evaluator_exists': (root / 'scripts' / 'chatgpt_first_proof_evaluator.py').exists(),
        'native_host_template_exists': (root / 'native-host' / 'com.glasstty.bridge.template.json').exists(),
    }
    return {
        'ok': all(checks.values()),
        'checks': checks,
        'extension_version': package.get('version'),
        'host_permissions': manifest.get('host_permissions'),
    }


def _contract_summary(contract: JsonDict | None, contract_path: Path | None) -> JsonDict:
    return {
        'path': display_path(contract_path),
        'exists': bool(contract_path and contract_path.exists()),
        'contract_version': contract.get('contract_version') if isinstance(contract, dict) else None,
        'prompt_selector': _path(contract, 'required.prompt_selector'),
        'strict_send_selector': _path(contract, 'required.strict_send.selector'),
        'strict_send_testid': _path(contract, 'required.strict_send.data_testid'),
        'strict_send_aria_label': _path(contract, 'required.strict_send.aria_label'),
    }


def build_preflight(*, surface_report: Path | None = None, contract_path: Path | None = None,
                    fixture_path: Path | None = None, rehearsal_out: Path = DEFAULT_REHEARSAL_OUT,
                    evaluation_out: Path = DEFAULT_EVAL_OUT) -> JsonDict:
    contract_path = contract_path or active_contract_path(ROOT)
    fixture_path = fixture_path if fixture_path is not None else active_fixture_path(ROOT)
    contract = read_contract_json(contract_path) if contract_path and contract_path.exists() else None
    static = _static_checks(ROOT)
    extension_readiness = check_extension_readiness(ROOT, require_build=False)

    fixture_result: JsonDict | None = None
    if contract is not None and fixture_path and fixture_path.exists():
        fixture_payload = read_payload(str(fixture_path))
        fixture_result = check_contract(fixture_payload, contract)

    current_result: JsonDict | None = None
    current_audit: JsonDict | None = None
    if surface_report:
        current_payload = read_payload(str(surface_report))
        current_audit = audit_surface(current_payload)
        if contract is not None:
            current_result = check_contract(current_payload, contract)

    rehearsal = run_rehearsal(
        surface_report=surface_report or fixture_path,
        contract_path=contract_path,
        out=rehearsal_out,
        evaluation_out=evaluation_out,
        strict_surface=True,
    )

    gates = {
        'static_tree_ok': bool(static.get('ok')),
        'extension_readiness_ok': bool(extension_readiness.get('ok')),
        'contract_present': isinstance(contract, dict),
        'fixture_contract_ok': fixture_result is not None and fixture_result.get('verdict') == 'surface-contract-ok',
        'current_surface_ok_or_not_supplied': current_result is None or current_result.get('verdict') == 'surface-contract-ok',
        'rehearsal_harness_ok_not_live': bool(rehearsal.get('ok')) and rehearsal.get('evaluator_verdict') == 'rehearsal-harness-ok-not-live',
    }
    ok = all(gates.values())
    verdict = 'ready-for-live-operator-attempt-not-a-live-proof' if ok else 'blocked-before-live-attempt'
    blockers = [name for name, value in gates.items() if not value]
    next_actions = []
    if not gates['static_tree_ok']:
        next_actions.append('Fix missing static files or ChatGPT-only manifest/adapter registry checks.')
    if not gates['extension_readiness_ok']:
        next_actions.append('Run proof-extension-readiness and fix extension/side-panel blockers before opening ChatGPT.')
    if not gates['contract_present']:
        next_actions.append('Capture or restore an active ChatGPT surface contract in validation/latest/.')
    if not gates['fixture_contract_ok']:
        next_actions.append('Regenerate the known-good surface fixture or contract; the saved fixture no longer satisfies the active contract.')
    if current_result is not None and current_result.get('verdict') != 'surface-contract-ok':
        next_actions.extend(current_result.get('recommendations') or [])
    if not gates['rehearsal_harness_ok_not_live']:
        next_actions.append('Run proof-rehearse and inspect the evaluator output before attempting live proof.')
    if ok:
        next_actions.append('When live access is available, run surface drift check first, then the guarded ChatGPT checkpoint proof flow.')
    return {
        'schema_version': 1,
        'tool': 'glasstty-chatgpt-proof-preflight',
        'generated_at': utcnow(),
        'ok': ok,
        'verdict': verdict,
        'live_proof': False,
        'blockers': blockers,
        'gates': gates,
        'static': static,
        'extension_readiness': extension_readiness,
        'contract': _contract_summary(contract, contract_path),
        'fixture_contract_check': fixture_result,
        'current_surface_audit': current_audit,
        'current_surface_contract_check': current_result,
        'rehearsal': rehearsal,
        'next_actions': next_actions,
    }


def run_preflight(*, surface_report: Path | None = None, contract_path: Path | None = None,
                  fixture_path: Path | None = None, out: Path = DEFAULT_OUT,
                  rehearsal_out: Path = DEFAULT_REHEARSAL_OUT, evaluation_out: Path = DEFAULT_EVAL_OUT) -> JsonDict:
    report = build_preflight(
        surface_report=surface_report,
        contract_path=contract_path,
        fixture_path=fixture_path,
        rehearsal_out=rehearsal_out,
        evaluation_out=evaluation_out,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Run the offline ChatGPT proof preflight gates.')
    parser.add_argument('--surface-report', type=Path, help='Optional current surface report to check against the active contract')
    parser.add_argument('--contract', type=Path, help='Override surface contract path')
    parser.add_argument('--fixture', type=Path, help='Override known-good surface fixture path')
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT, help='Output path for the preflight summary')
    parser.add_argument('--rehearsal-out', type=Path, default=DEFAULT_REHEARSAL_OUT, help='Output path for the rehearsal payload')
    parser.add_argument('--evaluation-out', type=Path, default=DEFAULT_EVAL_OUT, help='Output directory for evaluator output')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args(argv)
    report = run_preflight(
        surface_report=args.surface_report,
        contract_path=args.contract,
        fixture_path=args.fixture,
        out=args.out,
        rehearsal_out=args.rehearsal_out,
        evaluation_out=args.evaluation_out,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
