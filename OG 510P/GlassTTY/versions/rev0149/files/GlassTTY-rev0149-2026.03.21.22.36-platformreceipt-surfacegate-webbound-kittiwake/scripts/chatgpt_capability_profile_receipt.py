#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_support_claim_receipt import build_chatgpt_support_claim_receipt, evaluate_chatgpt_support_claim_receipt
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    _CLAIM = _load('chatgpt_support_claim_receipt', 'chatgpt_support_claim_receipt.py')
    build_chatgpt_support_claim_receipt = _CLAIM.build_chatgpt_support_claim_receipt
    evaluate_chatgpt_support_claim_receipt = _CLAIM.evaluate_chatgpt_support_claim_receipt

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-CAPABILITY-PROFILE-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-capability-profile-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-capability-profile-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-capability-profile-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-capability-profile-receipt.py capture --output-dir validation/latest/chatgpt-capability-profile-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-capability-profile-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-capability-profile-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-capability-profile-receipt.py evaluate --promotion path/to/promotion-window.json --pretty'

Payload = dict[str, Any]
TOOL_NEEDLES = {
    'search': ('search', 'web-search', 'web_search', 'browse', 'browsing'),
    'deep-research': ('deep research', 'deep-research', 'deep_research'),
    'file-uploads': ('upload', 'uploads', 'file-upload', 'file_upload', 'attachment', 'attachments'),
    'data-analysis': ('data-analysis', 'data analysis', 'advanced-data-analysis', 'python', 'code-interpreter', 'analysis'),
    'canvas': ('canvas',),
    'projects': ('project', 'projects'),
    'gpts-builder': ('gpt builder', 'gpts builder', 'gpt-builder', 'gpts-builder', 'custom gpt', 'custom-gpt'),
    'history-search': ('history-search', 'history search', 'sidebar-search', 'sidebar search'),
    'voice': ('voice', 'advanced voice', 'voice-mode'),
    'images': ('image', 'images', 'image-generation', 'image-input', 'image-editing'),
}
BASELINE_BLOCKERS = {'search', 'deep-research', 'file-uploads', 'data-analysis', 'canvas', 'projects', 'gpts-builder', 'history-search', 'voice', 'images'}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _history_entries(path: Path) -> list[dict[str, Any]]:
    try:
        payload = _read_json(path)
    except Exception:
        return []
    entries = payload.get('entries') if isinstance(payload, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def summarize_capture_history(path: Path | None = None) -> dict[str, Any]:
    history_path = path or DEFAULT_HISTORY_PATH
    entries = _history_entries(history_path)
    payload = _read_json(history_path) if history_path.exists() else None
    latest = entries[-1] if entries else None
    return {
        'path': str(history_path),
        'exists': history_path.exists(),
        'capture_count': len(entries),
        'latest_capture': latest,
        'history': payload,
    }


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current.keys())
    return [key for key in sorted(set(previous) | set(current)) if previous.get(key) != current.get(key)]


def _history_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'updated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'capture_count': len(entries),
        'entries': entries,
    }


def _normalize_keyish(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower().replace('_', '-').replace(' ', '-')
    return normalized or None


def _normalize_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = ' '.join(value.strip().lower().split())
    return normalized or None


def _reviewable_summaries(claim_eval: Payload) -> list[Payload]:
    promotion_eval = claim_eval.get('promotion_evaluation') if isinstance(claim_eval.get('promotion_evaluation'), dict) else {}
    raw = promotion_eval.get('window_summaries')
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict) and item.get('bundle_readiness') in {'ready-for-held', 'ready-with-caution'}]


def _window_payloads(promotion: Payload) -> list[Payload]:
    for key in ('proof_windows', 'windows', 'bundles', 'runs'):
        raw = promotion.get(key)
        if isinstance(raw, list):
            return [item for item in raw if isinstance(item, dict)]
    single = promotion.get('proof_window')
    if isinstance(single, dict):
        return [single]
    bundle = promotion.get('bundle')
    if isinstance(bundle, dict):
        return [bundle]
    return []


def _summary_lookup(claim_eval: Payload) -> dict[int, Payload]:
    by_index: dict[int, Payload] = {}
    for item in _reviewable_summaries(claim_eval):
        idx = item.get('window_index')
        if isinstance(idx, int):
            by_index[idx - 1] = item
    return by_index


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
        return out
    return []


def _tool_hits(strings: list[str]) -> list[str]:
    hits: list[str] = []
    normalized = [_normalize_text(item) or '' for item in strings]
    for tool, needles in TOOL_NEEDLES.items():
        for text in normalized:
            if any(needle in text for needle in needles):
                hits.append(tool)
                break
    return list(dict.fromkeys(hits))


def _artifact_rows(window: Payload) -> list[Payload]:
    rows: list[Payload] = []
    for key in ('artifact_refs', 'artifacts', 'bundle_artifacts'):
        raw = window.get(key)
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    rows.append(item)
    return rows


def _artifact_hints(rows: list[Payload]) -> list[str]:
    hints: list[str] = []
    for row in rows:
        for field in ('kind', 'path', 'role'):
            value = row.get(field)
            if isinstance(value, str) and value.strip():
                hints.append(value.strip())
    return hints


def _entry_mode(window: Payload, summary: Payload | None) -> str | None:
    for key in ('prompt_entry_mode', 'entry_mode', 'prompt_mode', 'composer_mode'):
        value = _normalize_keyish(window.get(key))
        if value:
            return value
    strings: list[str] = []
    if summary:
        strings.extend(_collect_strings(summary.get('matched_posture_key')))
    strings.extend(_collect_strings(window.get('used_tools')))
    strings.extend(_collect_strings(window.get('visible_tools')))
    strings.extend(_artifact_hints(_artifact_rows(window)))
    hits = _tool_hits(strings)
    if hits:
        return hits[0]
    route = window.get('route_witness') if isinstance(window.get('route_witness'), dict) else {}
    path = route.get('path')
    if isinstance(path, str) and path.startswith('/'):
        return 'text-only'
    return None


def _attachment_count(window: Payload) -> int | None:
    for key in ('uploaded_file_count', 'attachment_count', 'file_upload_count'):
        if key in window and window.get(key) is None:
            return None
    for key in ('uploaded_file_count', 'attachment_count', 'file_upload_count'):
        value = window.get(key)
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return max(0, value)
    for key in ('has_uploads', 'used_uploads'):
        value = window.get(key)
        if isinstance(value, bool):
            return 1 if value else 0
    rows = _artifact_rows(window)
    artifact_text = ' '.join(_artifact_hints(rows)).lower()
    if any(token in artifact_text for token in ('upload', 'attachment', 'analysis')):
        return 1
    return 0 if rows else None


def _tool_profile(window: Payload, summary: Payload | None) -> list[str]:
    strings: list[str] = []
    for key in ('used_tools', 'visible_tools', 'tool_profile', 'tool_modes', 'composer_tools', 'capability_profile'):
        strings.extend(_collect_strings(window.get(key)))
    strings.extend(_artifact_hints(_artifact_rows(window)))
    if summary:
        strings.extend(_collect_strings(summary.get('matched_posture_key')))
    entry_mode = _entry_mode(window, summary)
    if entry_mode:
        strings.append(entry_mode)
    attachments = _attachment_count(window)
    if attachments and attachments > 0:
        strings.append('file upload')
    hits = _tool_hits(strings)
    return [item for item in hits if item in BASELINE_BLOCKERS]


def _model_labels(window: Payload) -> list[str]:
    labels: list[str] = []
    for key in ('model_profile', 'model_label', 'model_family', 'model_slug', 'composer_model_label', 'selected_model'):
        value = _normalize_text(window.get(key))
        if value:
            labels.append(value)
    return list(dict.fromkeys(labels))


def _window_profile(index: int, window: Payload, summary: Payload | None) -> Payload:
    entry_mode = _entry_mode(window, summary)
    tools = _tool_profile(window, summary)
    attachment_count = _attachment_count(window)
    model_labels = _model_labels(window)
    return {
        'window_index': index,
        'proof_window_token': (summary or {}).get('proof_window_token'),
        'bundle_readiness': (summary or {}).get('bundle_readiness'),
        'auth_posture': (summary or {}).get('auth_posture'),
        'route_path': (summary or {}).get('route_path'),
        'matched_posture_key': (summary or {}).get('matched_posture_key'),
        'entry_mode': entry_mode,
        'active_tool_profile': tools,
        'attachment_count': attachment_count,
        'model_labels': model_labels,
        'prompt_is_text_only': entry_mode == 'text-only' and not tools and (attachment_count in {0, None}),
    }


def _profile_scorecard(window_profiles: list[Payload], claim_eval: Payload) -> list[Payload]:
    claim_state = str(claim_eval.get('claim_readiness') or '')
    entry_modes = [item.get('entry_mode') for item in window_profiles if isinstance(item.get('entry_mode'), str)]
    attachment_known = [item for item in window_profiles if item.get('attachment_count') is not None]
    blocker_windows = [item for item in window_profiles if item.get('active_tool_profile')]
    model_sets = [tuple(item.get('model_labels') or []) for item in window_profiles if item.get('model_labels')]
    return [
        {
            'check_key': 'lane_bound_claim_ready',
            'required': True,
            'present': claim_state in {'experimental-lane-bound', 'provisional-lane-bound'},
            'detail': 'the capability profile should only narrow an already lane-bound ChatGPT claim, not replace the route/browser/auth gate',
            'claim_readiness': claim_state,
        },
        {
            'check_key': 'profile_scope_explicit',
            'required': True,
            'present': bool(window_profiles) and len(entry_modes) == len(window_profiles),
            'detail': 'each reviewable proof window should preserve or at least infer a prompt-entry mode so model/tool scope does not become guesswork',
            'entry_modes': entry_modes,
        },
        {
            'check_key': 'plain_text_entry_only',
            'required': True,
            'present': bool(window_profiles) and all(item.get('entry_mode') == 'text-only' for item in window_profiles),
            'detail': 'the current baseline envelope is only for plain text entry on the route-first lane, not slash-search, uploads, voice, or richer tool invocations',
        },
        {
            'check_key': 'no_tool_branch_usage',
            'required': True,
            'present': bool(window_profiles) and not blocker_windows,
            'detail': 'a plain baseline claim should stop or hold when the same proof windows also exercise Search, uploads, data analysis, Canvas, Projects, GPT builder, voice, or image tools',
            'tool_windows': [
                {'window_index': item.get('window_index'), 'active_tool_profile': item.get('active_tool_profile')}
                for item in blocker_windows
            ],
        },
        {
            'check_key': 'attachment_state_explicit',
            'required': True,
            'present': bool(window_profiles) and len(attachment_known) == len(window_profiles),
            'detail': 'uploaded files and structured-data inputs change the interaction envelope, so attachment state should be explicit even when it is zero',
            'attachment_counts': [item.get('attachment_count') for item in window_profiles],
        },
        {
            'check_key': 'no_uploaded_inputs',
            'required': True,
            'present': bool(window_profiles) and all((item.get('attachment_count') or 0) == 0 for item in window_profiles),
            'detail': 'a plain text baseline should not inherit file-upload or structured-data claims from windows that attached files or analysis inputs',
        },
        {
            'check_key': 'model_profile_consistent',
            'required': False,
            'present': not model_sets or len(set(model_sets)) == 1,
            'detail': 'when model labels are preserved, they should be consistent across the repeated windows so later support wording can stay reviewable',
            'model_sets': [list(item) for item in model_sets],
        },
    ]


def _capability_scope(window_profiles: list[Payload]) -> Payload:
    return {
        'entry_modes': list(dict.fromkeys(item.get('entry_mode') for item in window_profiles if item.get('entry_mode'))),
        'auth_postures': list(dict.fromkeys(item.get('auth_posture') for item in window_profiles if item.get('auth_posture'))),
        'route_paths': list(dict.fromkeys(item.get('route_path') for item in window_profiles if item.get('route_path'))),
        'active_tool_profiles': [
            {'window_index': item.get('window_index'), 'active_tool_profile': item.get('active_tool_profile')}
            for item in window_profiles if item.get('active_tool_profile')
        ],
        'attachment_counts': [
            {'window_index': item.get('window_index'), 'attachment_count': item.get('attachment_count')}
            for item in window_profiles
        ],
        'model_labels': list(dict.fromkeys(label for item in window_profiles for label in (item.get('model_labels') or []))),
        'supported_capability_slice': 'plain text-only route-first chat baseline' if window_profiles else 'unknown',
    }


def _capability_envelope(scope: Payload, *, max_tier: str, caution_flags: list[str]) -> Payload:
    entry = ', '.join(scope.get('entry_modes') or []) or 'unspecified entry mode'
    auth = ', '.join(scope.get('auth_postures') or []) or 'unspecified auth posture'
    routes = ', '.join(scope.get('route_paths') or []) or 'unspecified route path'
    models = ', '.join(scope.get('model_labels') or []) if scope.get('model_labels') else 'unspecified/default model profile'
    supported_claims = [
        f'GlassTTY has evidence only for the plain text-only ChatGPT route-first baseline ({routes}), not for every ChatGPT tool or workspace mode.',
        f'The current capability envelope only covers the {auth} posture(s) and the `{entry}` entry mode preserved in the reviewable proof windows.',
        f'Any model wording must stay anchored to the preserved profile ({models}) and should not imply all ChatGPT model or tool combinations.',
    ]
    if max_tier == 'provisional':
        supported_claims.append('Repeated proof windows justify a provisional text-only capability profile, but not tool-expanded ChatGPT support.')
    elif max_tier == 'experimental':
        supported_claims.append('Current evidence can justify only an experimental text-only capability profile.')
    else:
        supported_claims.append('Current evidence does not justify a live capability claim beyond investigated planning artifacts.')
    excluded_claims = [
        'Do not claim Search, deep research, file uploads, data analysis, image generation, or voice support from the plain text-only baseline.',
        'Do not claim Projects, Canvas, GPT builder, or sidebar history-search support from the same proof windows.',
        'Do not treat one preserved or inferred model profile as proof for all ChatGPT model/tool combinations.',
    ]
    if caution_flags:
        excluded_claims.append('Keep caution flags attached so ambiguous model labels or missing profile capture do not turn into broad capability claims.')
    return {
        'tier_ceiling': max_tier,
        'entry_mode_scope': scope.get('entry_modes') or [],
        'auth_scope': scope.get('auth_postures') or [],
        'route_scope': scope.get('route_paths') or [],
        'model_profile_scope': scope.get('model_labels') or [],
        'excluded_tool_modes': sorted(BASELINE_BLOCKERS),
        'supported_claims': supported_claims,
        'excluded_claims': excluded_claims,
    }


def evaluate_chatgpt_capability_profile_receipt(promotion: Payload, *, root: Path = ROOT) -> Payload:
    spec = build_chatgpt_capability_profile_receipt(root=root)
    claim_eval = evaluate_chatgpt_support_claim_receipt(promotion, root=root)
    windows = _window_payloads(promotion)
    summary_by_index = _summary_lookup(claim_eval)
    window_profiles = [_window_profile(index + 1, window, summary_by_index.get(index)) for index, window in enumerate(windows) if summary_by_index.get(index)]
    scorecard = _profile_scorecard(window_profiles, claim_eval)
    present_checks = [item['check_key'] for item in scorecard if item.get('present')]
    missing_required = [item['check_key'] for item in scorecard if item.get('required') and not item.get('present')]
    missing_optional = [item['check_key'] for item in scorecard if not item.get('required') and not item.get('present')]
    scope = _capability_scope(window_profiles)

    caution_flags: list[str] = list(dict.fromkeys(str(item) for item in (claim_eval.get('caution_flags') or []) if isinstance(item, str)))
    if 'model_profile_consistent' in missing_optional:
        caution_flags.append('mixed-or-missing-model-profile')
    if 'attachment_state_explicit' in missing_required:
        caution_flags.append('attachment-state-not-explicit')

    blocker_tools = sorted({tool for item in window_profiles for tool in (item.get('active_tool_profile') or []) if tool in BASELINE_BLOCKERS})
    claim_state = str(claim_eval.get('claim_readiness') or '')
    recommended_tier = 'investigated'
    if blocker_tools:
        readiness = 'stop'
        reason = 'the proof windows already exercised richer ChatGPT tools or workspace modes, so they cannot be phrased as a plain text-only baseline capability claim'
    elif claim_state == 'planning-only':
        readiness = 'planning-only'
        reason = 'the receipt still describes capability-boundary discipline and does not yet have reviewable proof windows to narrow'
    elif claim_state == 'investigated-only':
        readiness = 'investigated-only'
        reason = 'some proof objects exist, but they are not yet reviewable enough to justify even a text-only capability envelope'
    elif missing_required:
        readiness = 'hold-for-profile-clarification'
        reason = 'the route-first proof is partly reviewable, but the prompt/tool/attachment profile is still too fuzzy to phrase an honest text-only capability claim'
    elif claim_state == 'provisional-lane-bound':
        readiness = 'provisional-text-profile'
        reason = 'repeated lane-bound proof windows are strong enough for a provisional text-only capability profile, but not for tool-expanded ChatGPT claims'
        recommended_tier = 'provisional'
    else:
        readiness = 'experimental-text-profile'
        reason = 'the evidence can justify an experimental text-only capability profile, but broader ChatGPT tool coverage still needs explicit proof'
        recommended_tier = 'experimental'

    if readiness == 'planning-only':
        next_action = 'capture one live route-first ChatGPT proof window before trying to phrase any capability profile'
    elif readiness == 'investigated-only':
        next_action = 'repair the upstream route/composer/submit/claim receipts until at least one reviewable proof window exists'
    elif readiness == 'hold-for-profile-clarification':
        next_action = 'preserve explicit entry mode, attachment state, and tool visibility/usage for each proof window before widening capability language'
    elif readiness == 'experimental-text-profile':
        next_action = 'keep the support wording explicitly text-only and gather the second repeated proof window with the same plain prompt profile'
    elif readiness == 'provisional-text-profile':
        next_action = 'promote only to a provisional text-only capability profile and keep search/uploads/data-analysis/voice/image/workspace claims explicitly out of scope'
    else:
        next_action = 'split richer tool or workspace runs into separate evidence lanes instead of treating them as plain text baseline proof'

    envelope = _capability_envelope(scope, max_tier=recommended_tier, caution_flags=caution_flags)
    return {
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'capability_evaluation_kind': 'chatgpt-routefirst-capability-profile-envelope',
        'claim_evaluation': claim_eval,
        'window_capability_profiles': window_profiles,
        'field_scorecard': scorecard,
        'present_check_keys': present_checks,
        'missing_required_check_keys': missing_required,
        'missing_optional_check_keys': missing_optional,
        'capability_readiness': readiness,
        'capability_readiness_reason': reason,
        'recommended_support_record_tier': recommended_tier,
        'caution_flags': caution_flags,
        'capability_envelope': envelope,
        'recommended_next_action': next_action,
        'source_keys': spec.get('source_keys') or [],
    }


def _summary_markdown(payload: Payload) -> str:
    axes = payload.get('capability_axes') or []
    states = payload.get('capability_readiness_states') or []
    lines = [
        '# ChatGPT capability profile receipt',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- target support tier: `{payload.get('target_support_tier')}`",
        '',
        '## Capability axes',
        '',
    ]
    for item in axes:
        lines.append(f"- {item.get('axis')}: {item.get('rule')}")
    lines.extend(['', '## Capability readiness states', ''])
    for item in states:
        lines.append(f"- {item.get('state')}: {item.get('rule')}")
    lines.append('')
    return '\n'.join(lines)


def build_chatgpt_capability_profile_receipt(*, root: Path = ROOT) -> Payload:
    claim_spec = build_chatgpt_support_claim_receipt(root=root)
    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'bound the strongest honest ChatGPT capability profile so repeated plain-text proof does not silently imply search, uploads, data analysis, voice, image, or richer workspace support',
        'target_support_tier': 'provisional',
        'design_principles': [
            'A route-first text-only proof should not silently imply ChatGPT Search, file uploads, data analysis, deep research, voice, or image workflows.',
            'Capability wording should preserve explicit entry-mode, tool-usage, attachment-state, and model-profile bounds instead of burying them in caveats.',
            'The capability envelope should describe both what the current evidence covers and what richer tool or workspace modes it explicitly does not cover.',
        ],
        'capability_axes': [
            {'axis': 'entry-mode', 'rule': 'plain text-only prompt entry should remain distinct from slash-search, uploads, voice, or richer tool invocations'},
            {'axis': 'tool-profile', 'rule': 'built-in tools such as Search, deep research, uploads, data analysis, images, or voice should not be inferred from a text-only baseline'},
            {'axis': 'attachment-state', 'rule': 'zero-upload proof should remain distinct from workflows that attach files or structured data'},
            {'axis': 'model-profile', 'rule': 'one preserved or inferred model profile should not be phrased as all-model support'},
            {'axis': 'workspace-branch', 'rule': 'Projects, Canvas, GPT builder, and sidebar history search remain separate branches even when the route host stays the same'},
        ],
        'capability_readiness_states': [
            {'state': 'provisional-text-profile', 'rule': 'repeated lane-bound proof windows justify only a provisional plain text-only capability profile'},
            {'state': 'experimental-text-profile', 'rule': 'current evidence can justify only an experimental plain text-only capability profile'},
            {'state': 'hold-for-profile-clarification', 'rule': 'proof exists, but entry mode, attachment state, or tool/model profile is still too fuzzy to phrase honestly'},
            {'state': 'investigated-only', 'rule': 'planning or thin proof artifacts exist, but they do not yet justify a live capability profile'},
            {'state': 'planning-only', 'rule': 'the receipt still describes capability-boundary discipline rather than current live evidence'},
            {'state': 'stop', 'rule': 'the proof windows exercised richer tools or workspace branches and should not be generalized into a plain baseline capability story'},
        ],
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'evaluate': EVALUATE_COMMAND,
            'support_claim_receipt': 'python scripts/chatgpt-support-claim-receipt.py --pretty',
        },
        'source_keys': sorted(dict.fromkeys((claim_spec.get('source_keys') or []) + ['chatgpt-data-analysis'])),
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_capability_profile_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> Payload:
    payload = build_chatgpt_capability_profile_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / 'chatgpt-capability-profile-receipt.json'
    summary_path = output_dir / 'SUMMARY.md'
    _write_json(json_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')
    entries = _history_entries(history_path)
    previous = entries[-1] if entries else None
    current = {
        'captured_at': payload.get('generated_at'),
        'path': str(json_path),
        'summary_path': str(summary_path),
        'source_keys': payload.get('source_keys') or [],
        'capability_readiness_states': [item.get('state') for item in payload.get('capability_readiness_states') or []],
    }
    changed_fields = _changed_fields(previous, current)
    current['changed_fields'] = changed_fields
    entries.append(current)
    _write_json(history_path, _history_payload(entries))
    return {
        'receipt': payload,
        'output_dir': str(output_dir),
        'json_path': str(json_path),
        'summary_path': str(summary_path),
        'history_update': {
            'history_path': str(history_path),
            'capture_count_after_write': len(entries),
            'changed_fields': changed_fields,
        },
    }


def write_root_chatgpt_capability_profile_receipt(*, root: Path = ROOT) -> Payload:
    payload = build_chatgpt_capability_profile_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build or evaluate the ChatGPT capability profile receipt.')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser = subparsers.add_parser('history')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    subparsers.add_parser('write-root')
    eval_parser = subparsers.add_parser('evaluate')
    eval_parser.add_argument('--promotion', required=True)
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    if args.command == 'capture':
        payload = capture_chatgpt_capability_profile_receipt(output_dir=Path(args.output_dir), history_path=Path(args.history_path))
    elif args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
    elif args.command == 'write-root':
        payload = write_root_chatgpt_capability_profile_receipt()
    elif args.command == 'evaluate':
        payload = evaluate_chatgpt_capability_profile_receipt(_read_json(Path(args.promotion)))
    else:
        payload = build_chatgpt_capability_profile_receipt()
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
