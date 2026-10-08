#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_first_proof_artifact_ledger import ARTIFACT_SLOTS
    from chatgpt_first_proof_evaluator import REQUIRED_CHECKS as EVALUATOR_REQUIRED_CHECKS
    from chatgpt_first_proof_evaluator import SCHEMA_VERSION as EVALUATOR_SCHEMA_VERSION
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load_module(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    _LEDGER = _load_module('chatgpt_first_proof_artifact_ledger', 'chatgpt_first_proof_artifact_ledger.py')
    _EVALUATOR = _load_module('chatgpt_first_proof_evaluator', 'chatgpt_first_proof_evaluator.py')
    ARTIFACT_SLOTS = _LEDGER.ARTIFACT_SLOTS
    EVALUATOR_REQUIRED_CHECKS = _EVALUATOR.REQUIRED_CHECKS
    EVALUATOR_SCHEMA_VERSION = _EVALUATOR.SCHEMA_VERSION

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-FIRST-PROOF-KIT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-kit'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-first-proof-kit-captures.json'
CANDIDATE_BUNDLE_REL = Path('validation/latest/chatgpt-routefirst-chromium-live-candidate.json')
PROBE_TEXT = 'Reply with exactly this text and nothing else: GLASSTTY-CHECKPOINT'
EXPECTED_REPLY = 'GLASSTTY-CHECKPOINT'
REPORT_COMMAND = 'python scripts/chatgpt-first-proof-kit.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-first-proof-kit.py capture --output-dir validation/latest/chatgpt-first-proof-kit --pretty'
HISTORY_COMMAND = 'python scripts/chatgpt-first-proof-kit.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-first-proof-kit.py write-root'
WRITE_BUNDLE_COMMAND = 'python scripts/chatgpt-first-proof-kit.py write-candidate-bundle'
ARTIFACT_LEDGER_COMMAND = 'python scripts/chatgpt-first-proof-artifact-ledger.py audit --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --output-dir validation/latest/chatgpt-first-proof-artifact-ledger --readiness-level evaluator-ready --pretty'
SCHEMA_VALIDATE_COMMAND = 'python scripts/chatgpt-first-proof-schema-validation.py validate --input validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/bundle-manifest.json --output-dir validation/latest/chatgpt-first-proof-schema-validation --pretty'
AUDIT_CAPTURE_COMMAND = 'python scripts/chatgpt-first-proof-bundle-audit.py audit --input validation/latest/chatgpt-first-proof-capture.json --output-dir validation/latest/chatgpt-first-proof-bundle-audit --pretty'
EVALUATE_CAPTURE_COMMAND = 'python scripts/chatgpt-first-proof-evaluator.py evaluate --input validation/latest/chatgpt-first-proof-capture.json --output-dir validation/latest/chatgpt-first-proof-evaluation --pretty'
REHEARSE_PROOF_COMMAND = 'python scripts/chatgpt-proof-rehearsal.py --pretty'
EXPORT_PROOF_PACK_COMMAND = 'python scripts/chatgpt-proof-pack-exporter.py --input validation/latest/chatgpt-proof-rehearsal.json --pack-dir validation/latest/chatgpt-proof-rehearsal-evidence-pack --clean --pretty'


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise ValueError(f'{path} is not a JSON object')
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _history_entries(path: Path) -> list[dict[str, Any]]:
    try:
        payload = _read_json(path)
    except Exception:
        return []
    entries = payload.get('entries') if isinstance(payload, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def _history_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'history_key': 'chatgpt-first-proof-kit-captures',
        'updated_at': utcnow(),
        'entry_count': len(entries),
        'entries': entries,
    }


def summarize_capture_history(path: Path | None = None) -> dict[str, Any]:
    history_path = path or DEFAULT_HISTORY_PATH
    entries = _history_entries(history_path)
    return {
        'path': str(history_path),
        'exists': history_path.exists(),
        'capture_count': len(entries),
        'latest_capture': entries[-1] if entries else None,
        'history': _read_json(history_path) if history_path.exists() else None,
    }


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current)
    return [key for key in sorted(set(previous) | set(current)) if previous.get(key) != current.get(key)]


def _chatgpt_reference_files(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob('CHATGPT-*.json')):
        rows.append({
            'path': path.name,
            'exists': True,
            'size': path.stat().st_size,
            'sha256': sha256_file(path),
        })
    return rows


def _summary_markdown(payload: dict[str, Any]) -> str:
    selected = payload['selected_surface']
    slots = payload['artifact_plan']['required_slots']
    missing = payload['state']['missing_live_proof']
    lines = [
        '# ChatGPT first-proof kit',
        '',
        f"- generated_at: `{payload['generated_at']}`",
        f"- surface_key: `{selected['surface_key']}`",
        f"- role: `{selected['role']}`",
        f"- route_hint: `{selected['primary_route_hint']}`",
        f"- expected_reply: `{payload['probe_prompt']['expected_exact_reply']}`",
        f"- artifact_slots: `{len(slots)}`",
        f"- evaluator_schema_version: `{payload['evaluator_contract']['schema_version']}`",
        f"- live_proof_missing: `{missing}`",
        '',
        '## Run sequence',
        '',
    ]
    for key, command in payload['commands'].items():
        lines.append(f'- `{key}`: `{command}`')
    lines.extend([
        '',
        '## Promotion rule',
        '',
        'This kit can prepare and evaluate a ChatGPT proof bundle, but it does not promote support claims. Promotion still needs one coherent live bundle, passing local checks, and a human privacy/redaction review.',
        '',
    ])
    return '\n'.join(lines)


def build_chatgpt_first_proof_kit(*, root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    slots = [slot._asdict() for slot in ARTIFACT_SLOTS]
    chatgpt_refs = _chatgpt_reference_files(root)
    payload: dict[str, Any] = {
        'schema_version': 2,
        'kit_key': 'chatgpt-first-proof-kit',
        'generated_at': utcnow(),
        'project': 'GlassTTY ChatGPT-only refactor',
        'state': {
            'provider_scope': 'chatgpt-only',
            'missing_live_proof': True,
            'support_claim_state': 'hold-no-support-claim-widening',
            'archive_policy': 'old multi-provider history intentionally removed from this working cube; preserved by upstream archives',
        },
        'selected_surface': {
            'surface_key': 'chatgpt',
            'adapter': 'chatgpt',
            'role': 'primary-and-only-provider',
            'primary_route_hint': 'https://chatgpt.com/',
            'required_host': 'chatgpt.com',
            'proof_lane': 'desktop-web Chromium, plain text chat, route-first checkpoint',
            'forbidden_branches_for_first_proof': [
                'Projects', 'GPT builder', 'Canvas', 'voice/audio modes', 'file upload', 'image generation',
                'data analysis/tool execution', 'search/deep research', 'agent/task automation', 'mobile/desktop app lanes',
            ],
        },
        'probe_prompt': {
            'text': PROBE_TEXT,
            'expected_exact_reply': EXPECTED_REPLY,
            'normalization': 'trim outer whitespace only; no paraphrase, markdown wrapper, or extra sentence is acceptable',
        },
        'commands': {
            'show_kit': REPORT_COMMAND,
            'capture_kit_snapshot': CAPTURE_COMMAND,
            'show_kit_history': HISTORY_COMMAND,
            'write_root_kit': WRITE_ROOT_COMMAND,
            'write_candidate_bundle': WRITE_BUNDLE_COMMAND,
            'audit_artifact_pack': ARTIFACT_LEDGER_COMMAND,
            'validate_bundle_schema': SCHEMA_VALIDATE_COMMAND,
            'audit_captured_proof_bundle': AUDIT_CAPTURE_COMMAND,
            'evaluate_captured_proof_bundle': EVALUATE_CAPTURE_COMMAND,
            'rehearse_proof_harness_offline': REHEARSE_PROOF_COMMAND,
            'export_rehearsal_evidence_pack': EXPORT_PROOF_PACK_COMMAND,
            'extension_typecheck': 'npm --prefix extension run typecheck',
            'extension_build': 'npm --prefix extension run build',
            'pytest_chatgpt_proof': 'python -m pytest tests/test_chatgpt_executable_adapter_policy.py tests/test_chatgpt_first_proof_artifact_ledger.py tests/test_chatgpt_first_proof_schema_validation.py tests/test_chatgpt_first_proof_bundle_audit.py tests/test_chatgpt_first_proof_evaluator.py tests/test_chatgpt_first_proof_kit.py',
        },
        'selector_contract': {
            'composer_candidates': [
                {'family': 'accessible-textbox', 'priority': 1, 'why': 'prefer user-facing editable controls'},
                {'family': 'textarea', 'priority': 2, 'why': 'stable native editable fallback'},
                {'family': 'contenteditable', 'priority': 3, 'why': 'accepted only with explicit actionability/readback evidence'},
            ],
            'submit_policy': {
                'manual_or_sidepanel_submit_only': True,
                'keyboard_submit_enabled': False,
                'route_posture_required': 'plain-chat',
                'prompt_readback_required_before_submit': True,
            },
            'priority_rules': [
                'Use one attempt_id and one explicit tab_id across prompt.write, prompt.submit, transcript.latest, and settled-generation witness rows.',
                'Require prompt.write/readback before prompt.submit before transcript.latest before settled-generation, with monotonic explicit sequence_index values.',
                'After submit, require a root/plain-chat to /c/<conversation> route transition and preserve the normalized /c/ route path.',
                'Require an operator-submit attestation from the side-panel/manual submit path; do not use autonomous keyboard submit for this proof.',
                'Require submit-time composer readback exactly equal the checkpoint prompt before any submit action is accepted.',
                'Require latest assistant text exactly equal the checkpoint reply and match latest_output_witness text.',
                'Require a leaf-like, non-aggregate assistant witness and a separate user-turn witness whose text exactly equals the checkpoint prompt.',
                'Require user-before-assistant document order and explicit same-frame context for the latest user/assistant turn pair.',
                'Require a settled-generation fixture/snapshot after transcript.latest, on the same tab and same /c/ conversation route path.',
            ],
        },
        'artifact_plan': {
            'pack_dir': 'validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack',
            'required_slots': slots,
            'capture_ready_files': [slot['filename'] for slot in slots if slot['required_for'] == 'capture-ready'],
            'evaluator_ready_files': [slot['filename'] for slot in slots if slot['required_for'] in {'capture-ready', 'evaluator-ready'}],
            'review_ready_files': [slot['filename'] for slot in slots if slot['required_for'] in {'capture-ready', 'evaluator-ready', 'review-ready'}],
            'bundle_schema': 'schemas/chatgpt-first-proof-bundle.schema.json',
            'privacy_review_file': 'privacy-redaction-review.md',
        },
        'evaluator_contract': {
            'schema_version': EVALUATOR_SCHEMA_VERSION,
            'required_checks': list(EVALUATOR_REQUIRED_CHECKS),
            'reviewable_verdict': 'reviewable-no-claim-widening',
            'blocked_verdict': 'blocked',
        },
        'ui_branching_hazards': [
            'A ChatGPT surface can silently move from plain chat into Canvas, Projects, GPT builder, Search, file upload, data analysis, image, voice, or agent lanes.',
            'A proof on a richer branch does not prove the baseline text-chat lane and should be stopped rather than normalized away.',
            'Route, adapter, URL, tab_id, frame context, latest assistant witness, and latest user witness must be captured as evidence, not inferred after the fact.',
        ],
        'reference_files': chatgpt_refs,
        'candidate_bundle_path': str(CANDIDATE_BUNDLE_REL),
        'stop_signs': [
            'No live route-first ChatGPT checkpoint bundle is present yet.',
            'Do not publish support language from screenshots alone.',
            'Do not reuse stale multi-provider validation history as ChatGPT proof.',
            'Do not claim non-Chromium, mobile, app, workspace, tool, file, image, voice, or agent coverage from the first plain-chat proof.',
        ],
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def build_candidate_bundle_manifest(*, root: Path = ROOT) -> dict[str, Any]:
    kit = build_chatgpt_first_proof_kit(root=root)
    refs = kit['reference_files']
    artifact_refs: list[dict[str, Any]] = [
        {
            'path': 'CHATGPT-FIRST-PROOF-KIT.json',
            'kind': 'proof-kit',
            'role': 'current ChatGPT-only run contract',
            'exists': (root / 'CHATGPT-FIRST-PROOF-KIT.json').exists(),
        },
        {
            'path': 'schemas/chatgpt-first-proof-bundle.schema.json',
            'kind': 'schema',
            'role': 'bundle-manifest structural contract',
            'exists': (root / 'schemas' / 'chatgpt-first-proof-bundle.schema.json').exists(),
        },
        {
            'path': 'validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/README.md',
            'kind': 'evidence-pack-placeholder',
            'role': 'artifact-slot instructions for the live proof pack',
            'exists': (root / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack' / 'README.md').exists(),
        },
    ]
    for item in refs:
        artifact_refs.append({
            'path': item['path'],
            'kind': 'chatgpt-reference-receipt',
            'role': 'minimal ChatGPT-only proof/reference artifact retained in the working cube',
            'sha256': item.get('sha256'),
            'exists': item.get('exists'),
        })
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in artifact_refs:
        path = item.get('path')
        if isinstance(path, str) and path not in seen:
            seen.add(path)
            deduped.append(item)
    return {
        'schema_version': 2,
        'bundle_key': 'chatgpt-routefirst-chromium-live-candidate',
        'bundle_status': 'candidate',
        'surface_key': 'chatgpt',
        'provider_scope': 'chatgpt-only',
        'created_at': kit['generated_at'],
        'claim_effect': 'none; candidate bundle only prepares evidence review',
        'missing_live_proof': True,
        'proof_prompt': kit['probe_prompt'],
        'required_artifact_slots': kit['artifact_plan']['required_slots'],
        'evaluator_required_checks': kit['evaluator_contract']['required_checks'],
        'artifact_refs': deduped,
        'next_actions': [
            'Run the side-panel ChatGPT first-proof flow on https://chatgpt.com/.',
            'Fill validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack with all evaluator-ready artifacts.',
            'Run artifact ledger, schema validation, bundle audit, evaluator, and privacy/redaction review.',
        ],
    }


def capture_chatgpt_first_proof_kit(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    payload = build_chatgpt_first_proof_kit(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / 'chatgpt-first-proof-kit.json'
    summary_path = output_dir / 'SUMMARY.md'
    _write_json(json_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')
    entries = _history_entries(history_path)
    previous = entries[-1] if entries else None
    current = {
        'captured_at': payload['generated_at'],
        'output_dir': str(output_dir),
        'json_path': str(json_path),
        'summary_path': str(summary_path),
        'surface_key': 'chatgpt',
        'provider_scope': 'chatgpt-only',
        'primary_route_hint': payload['selected_surface']['primary_route_hint'],
        'expected_exact_reply': payload['probe_prompt']['expected_exact_reply'],
        'artifact_slot_count': len(payload['artifact_plan']['required_slots']),
        'evaluator_required_check_count': len(payload['evaluator_contract']['required_checks']),
        'candidate_bundle_path': payload['candidate_bundle_path'],
    }
    current['changed_fields'] = _changed_fields(previous, current)
    entries.append(current)
    _write_json(history_path, _history_payload(entries))
    return {
        'kit': payload,
        'history_update': {
            'path': str(history_path),
            'capture_count_after_write': len(entries),
            'changed_fields_vs_previous': current['changed_fields'],
        },
    }


def write_root_chatgpt_first_proof_kit(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_chatgpt_first_proof_kit(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def write_candidate_bundle_manifest(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_candidate_bundle_manifest(root=root)
    _write_json(root / CANDIDATE_BUNDLE_REL, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build the ChatGPT-only first-proof kit and candidate bundle seed.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser = subparsers.add_parser('history')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')
    subparsers.add_parser('write-root')
    subparsers.add_parser('write-candidate-bundle')
    args = parser.parse_args()
    pretty = bool(getattr(args, 'pretty', False))
    if args.command == 'capture':
        payload = capture_chatgpt_first_proof_kit(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
    elif args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
    elif args.command == 'write-root':
        payload = write_root_chatgpt_first_proof_kit(root=ROOT)
    elif args.command == 'write-candidate-bundle':
        payload = write_candidate_bundle_manifest(root=ROOT)
    else:
        payload = build_chatgpt_first_proof_kit(root=ROOT)
    print(json.dumps(payload, indent=2 if pretty else None))


if __name__ == '__main__':
    main()
