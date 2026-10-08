#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from second_adapter_brief import build_second_adapter_brief
    from support_source_baseline import load_source_lock
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    _BRIEF_PATH = Path(__file__).resolve().parent / 'second_adapter_brief.py'
    _BRIEF_SPEC = importlib.util.spec_from_file_location('second_adapter_brief', _BRIEF_PATH)
    _BRIEF_MODULE = importlib.util.module_from_spec(_BRIEF_SPEC)
    assert _BRIEF_SPEC.loader is not None
    _BRIEF_SPEC.loader.exec_module(_BRIEF_MODULE)
    build_second_adapter_brief = _BRIEF_MODULE.build_second_adapter_brief

    _SOURCE_PATH = Path(__file__).resolve().parent / 'support_source_baseline.py'
    _SOURCE_SPEC = importlib.util.spec_from_file_location('support_source_baseline', _SOURCE_PATH)
    _SOURCE_MODULE = importlib.util.module_from_spec(_SOURCE_SPEC)
    assert _SOURCE_SPEC.loader is not None
    _SOURCE_SPEC.loader.exec_module(_SOURCE_MODULE)
    load_source_lock = _SOURCE_MODULE.load_source_lock

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-FIRST-PROOF-KIT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-kit'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-first-proof-kit-captures.json'
CANDIDATE_BUNDLE_REL = Path('docs/support-bundles/candidate/chatgpt-routefirst-chromium-live-candidate.json')
REPORT_COMMAND = 'python scripts/chatgpt-first-proof-kit.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-first-proof-kit.py capture --output-dir validation/latest/chatgpt-first-proof-kit'
HISTORY_COMMAND = 'python scripts/chatgpt-first-proof-kit.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-first-proof-kit.py write-root'
WRITE_BUNDLE_COMMAND = 'python scripts/chatgpt-first-proof-kit.py write-candidate-bundle'
CORE_BROWSER_SUBSTRATE_KEYS = {'shared-browser-substrate', 'shared', 'all-surfaces'}
PROBE_TEXT = 'Reply with exactly this text and nothing else: GLASSTTY-CHECKPOINT'


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise ValueError(f'{path} is not a JSON object')
    return payload


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


def _source_groups(*, lock: dict[str, Any], surface_key: str = 'chatgpt') -> dict[str, list[dict[str, Any]]]:
    product_sources: list[dict[str, Any]] = []
    shared_sources: list[dict[str, Any]] = []
    for source in lock.get('sources') or []:
        if not isinstance(source, dict):
            continue
        source_key = str(source.get('source_key') or '')
        surface_keys = {str(item) for item in source.get('surface_keys') or [] if str(item).strip()}
        if surface_key in surface_keys and source.get('tier') == 'first-party-product-surface':
            product_sources.append(source)
        if CORE_BROWSER_SUBSTRATE_KEYS.intersection(surface_keys) or source_key.startswith('chrome-') or source_key.startswith('mdn-'):
            shared_sources.append(source)
    product_sources.sort(key=lambda item: (not bool(item.get('required_for_publication')), str(item.get('source_key') or '')))
    shared_sources.sort(key=lambda item: str(item.get('source_key') or ''))
    return {
        'product_sources': product_sources,
        'shared_sources': shared_sources,
    }


def _primary_route_source(product_sources: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not product_sources:
        return None
    for source in product_sources:
        claim_uses = {str(item).strip().lower() for item in source.get('claim_uses') or [] if str(item).strip()}
        url = str(source.get('url') or '')
        if 'direct browser route' in claim_uses or 'pre-login baseline posture' in claim_uses or 'chatgpt.com' in url:
            return source
    return product_sources[0]


def _summary_markdown(payload: dict[str, Any]) -> str:
    hazards = payload.get('ui_branching_hazards') or []
    priorities = payload.get('selector_contract', {}).get('priority_rules') or []
    lines = [
        '# ChatGPT first proof kit',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- primary route hint: `{((payload.get('selected_surface') or {}).get('primary_route_hint'))}`",
        f"- probe prompt: `{((payload.get('probe_prompt') or {}).get('text'))}`",
        f"- candidate bundle path: `{payload.get('candidate_bundle_path')}`",
        '',
        '## Priority rules',
        '',
    ]
    for item in priorities:
        lines.append(f"- {item}")
    lines.extend(['', '## UI branching hazards', ''])
    for item in hazards:
        lines.append(f"- {item.get('hazard')}: {item.get('why_it_matters')}")
    return '\n'.join(lines) + '\n'


def build_chatgpt_first_proof_kit(*, root: Path = ROOT) -> dict[str, Any]:
    brief = build_second_adapter_brief(root=root, surface_key='chatgpt')
    lock = load_source_lock(root=root)
    groups = _source_groups(lock=lock)
    product_sources = groups['product_sources']
    shared_sources = groups['shared_sources']
    primary_route_source = _primary_route_source(product_sources)
    primary_route_hint = (primary_route_source or {}).get('url')

    product_source_keys = [str(item.get('source_key')) for item in product_sources if item.get('source_key')]
    shared_source_keys = [str(item.get('source_key')) for item in shared_sources if item.get('source_key')]
    source_keys = sorted(dict.fromkeys(product_source_keys + shared_source_keys))

    selector_contract = {
        'surface_key': 'chatgpt',
        'priority_rules': [
            'Prefer route-first proof on chatgpt.com before Projects, Canvas, GPT builder, or other richer workspaces.',
            'Prefer user-facing, accessible locators and main-region scoping before CSS or DOM-shape fallbacks.',
            'Preserve one failed candidate and one successful candidate for the composer and submit affordance so drift is reviewable.',
            'Treat submit proof, generation proof, and latest-turn proof as separate evidence moments even when one run provides all three.',
            'Require a composer witness receipt before submit proof so a merely discovered textbox cannot masquerade as a proved write path.',
            'Require a submit witness receipt before treating submit, generation, or latest-turn extraction as a proved workflow slice.',
            'Require a proof-bundle receipt before claiming a whole proof window is fit for held-bundle promotion.',
            'Require a promotion-stability receipt before using repeated proof windows to strengthen ChatGPT support language beyond one held bundle.',
            'Require a support-claim receipt before phrasing support language so repeated Chromium proof does not silently imply broader browser or workspace coverage.',
            'Require a capability-profile receipt before phrasing support language so a plain text-only baseline does not silently imply Search, uploads, data analysis, voice, image, or other tool modes.',
            'Require an auth-workspace receipt before phrasing support language so guest, personal, Business, Enterprise, or Edu session stories do not silently blur together.',
            'Require a plan-envelope receipt before phrasing support language so guest, Free, Plus, Pro, Business, Enterprise, or Edu subscription stories do not silently blur together.',
            'Require a browser-envelope receipt before phrasing support language so one explicit Chromium lane does not silently become broader browser support.',
            'Require a retention-envelope receipt before phrasing support language so standard saved-history chats, Temporary Chats, memory-off runs, and reused storage-state sessions do not silently blur together.',
            'Require a platform-envelope receipt before phrasing support language so desktop web proof does not silently become Windows app, macOS app, iOS, Android, or mobile-web support.',
        ],
        'route_anchor': {
            'expected_hosts': ['chatgpt.com'],
            'primary_route_hint': primary_route_hint,
            'supporting_source_keys': product_source_keys,
            'capture_requirements': ['url', 'page_title', 'auth_posture', 'surface_identity_text', 'screenshot'],
            'success_cues': [
                'ChatGPT-branded page on chatgpt.com',
                'visible prompt or login posture consistent with the home-page article',
            ],
        },
        'receiver_resolution': {
            'scope_rule': 'Search in the main app or conversation region first, then consider global overlays or modal takeovers.',
            'overlay_classes_to_record': [
                'login or sign-up gate',
                'consent or privacy wall',
                'tool mode overlay',
                'canvas split view',
            ],
        },
        'composer_candidates': [
            {
                'priority': 1,
                'family': 'accessible-textbox',
                'locator_guidance': 'Prefer a visible textbox-like control in the main chat region via role-based or label-based lookup.',
                'actionability_checks': ['visible', 'enabled', 'editable'],
                'why': 'Playwright recommends resilient user-facing locators and actionability checks before interaction.',
            },
            {
                'priority': 2,
                'family': 'textarea',
                'locator_guidance': 'Fallback to a visible textarea candidate after main-region scoping.',
                'actionability_checks': ['visible', 'enabled', 'editable'],
                'why': 'The home page explicitly says a prompt can be entered in the text box to get started.',
            },
            {
                'priority': 3,
                'family': 'contenteditable',
                'locator_guidance': 'Only after textbox and textarea candidates fail, inspect a visible contenteditable candidate and preserve the failure reason for higher-priority candidates.',
                'actionability_checks': ['visible', 'editable'],
                'why': 'Richer modes may swap editor implementations, but the first proof should still document the fallback rather than assume it.',
            },
        ],
        'submit_candidates': [
            {
                'priority': 1,
                'family': 'visible-submit-button',
                'locator_guidance': 'Look for a visible button in the composer area whose accessible name resembles send, submit, or equivalent.',
                'actionability_checks': ['visible', 'stable', 'receives-events', 'enabled'],
                'why': 'A direct button click is easier to debug than a keyboard-only submit path.',
            },
            {
                'priority': 2,
                'family': 'keyboard-submit',
                'locator_guidance': 'Use Enter-based submission only after composer writability is proven and the direct button path is documented as missing or blocked.',
                'actionability_checks': ['composer-focused', 'post-write-readback'],
                'why': 'Keyboard submit is a fallback, not the primary proof path.',
            },
        ],
        'latest_turn_readback': {
            'conversation_scope': 'main conversation region first',
            'assistant_turn_goal': 'latest visible assistant turn with text and completion posture',
            'supporting_cues': [
                'retry icon or response actions under the most recent response',
                'streaming or stop state separated from final stable readback',
            ],
        },
    }

    ui_branching_hazards = [
        {
            'hazard': 'logged-out single-thread posture',
            'why_it_matters': 'The current home-page article says logged-out use is available at chatgpt.com but limits you to one conversation and cannot preserve history after logout.',
            'source_key': 'chatgpt-home-page',
        },
        {
            'hazard': 'projects require login and introduce a richer workspace shell',
            'why_it_matters': 'Projects are a logged-in workspace with chats, files, instructions, and sharing, so they should stay out of the first generic chat-lane proof.',
            'source_key': 'chatgpt-projects',
        },
        {
            'hazard': 'canvas can open from prompts, slash command, composer toolbox, or longer generated content',
            'why_it_matters': 'Canvas is useful but it changes the UI shape and should be treated as a branch, not the baseline lane.',
            'source_key': 'chatgpt-canvas-feature',
        },
        {
            'hazard': 'web-only composer controls can appear for selected models',
            'why_it_matters': 'The web composer can expose model and thinking-time controls, so selector scope should stay anchored to the active composer rather than assume a fixed button neighborhood.',
            'source_key': 'chatgpt-models-and-tools',
        },
        {
            'hazard': 'built-in tools can change the same route without changing the host',
            'why_it_matters': 'Search, uploads, data analysis, images, voice, and other tools can all live on the same ChatGPT surface, so the first proof should preserve a capability profile instead of silently treating one text-only pass as tool-general support.',
            'source_key': 'chatgpt-capabilities-overview',
        },
    ]

    failure_taxonomy = [
        {'failure_class': 'route-mismatch', 'symptom': 'not on chatgpt.com or wrong surface shell', 'next_capture': 'route witness and screenshot'},
        {'failure_class': 'auth-gated', 'symptom': 'login or sign-up requirement blocks workflow', 'next_capture': 'gate text and auth posture note'},
        {'failure_class': 'receiver-ambiguous', 'symptom': 'multiple plausible editable targets', 'next_capture': 'candidate inventory with one rejected reason per candidate'},
        {'failure_class': 'composer-not-editable', 'symptom': 'candidate exists but fails enabled or editable checks', 'next_capture': 'before or after state plus actionability failure'},
        {'failure_class': 'submit-blocked', 'symptom': 'submit affordance missing, disabled, or intercepted by overlay', 'next_capture': 'button state or fallback attempt evidence'},
        {'failure_class': 'streaming-ambiguous', 'symptom': 'generation cues present but completion state unclear', 'next_capture': 'generation timeline plus final stable readback attempt'},
        {'failure_class': 'latest-turn-ambiguous', 'symptom': 'multiple plausible last assistant turns or partial grouping drift', 'next_capture': 'conversation-region snapshot with candidate notes'},
    ]

    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'selected_surface': {
            'surface_key': 'chatgpt',
            'primary_route_hint': primary_route_hint,
            'brief_generated_at': brief.get('generated_at'),
            'brief_path': 'SECOND-ADAPTER-BRIEF.json',
        },
        'probe_prompt': {
            'text': PROBE_TEXT,
            'why': 'Exact-match reply reduces ambiguity when validating compose, submit, generation, and latest-turn extraction.',
            'expected_exact_reply': 'GLASSTTY-CHECKPOINT',
        },
        'selector_contract': selector_contract,
        'ui_branching_hazards': ui_branching_hazards,
        'failure_taxonomy': failure_taxonomy,
        'artifact_plan': {
            'baseline': ['route-witness.json', 'surface-screenshot.png', 'receiver-posture.md'],
            'composer': ['composer-candidates.json', 'composer-before.txt', 'composer-after.txt', 'composer-witness-receipt.json'],
            'submit_readback': ['probe-prompt.txt', 'submit-evidence.json', 'generation-timeline.json', 'latest-turn.txt'],
            'bundle': ['bundle-manifest.json', 'promotion-notes.md', 'gate-results.json', 'repeatability-notes.md', 'locator-notes.md', 'retention-profile.json'],
        },
        'source_keys': source_keys,
        'candidate_bundle_path': str(CANDIDATE_BUNDLE_REL),
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'write_candidate_bundle': WRITE_BUNDLE_COMMAND,
            'second_adapter_brief': 'python scripts/second-adapter-brief.py --pretty',
        },
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def build_candidate_bundle_manifest(*, root: Path = ROOT) -> dict[str, Any]:
    kit = build_chatgpt_first_proof_kit(root=root)
    archive_name = root.name
    manifest_path = root / 'ARCHIVE_MANIFEST.json'
    if manifest_path.exists():
        try:
            archive_name = _read_json(manifest_path).get('archive_name') or archive_name
        except Exception:
            pass
    return {
        'bundle_key': 'chatgpt-routefirst-chromium-live-candidate',
        'bundle_status': 'candidate',
        'surface_key': 'chatgpt',
        'browser_lane': 'chromium-live',
        'captured_at': kit.get('generated_at'),
        'workflows_touched': [
            'surface-detect',
            'receiver-resolve',
            'composer-read',
            'composer-write',
            'turn-submit',
            'latest-turn-read',
            'support-capture',
        ],
        'support_record': 'docs/support-records/chatgpt.md',
        'revision_receipt': 'REVISION-RECEIPT.json',
        'claim_scope': {
            'tier_ceiling': 'investigated',
            'evidence_class': 'source-backed planning and selector-contract bundle only; no live official-surface ChatGPT capture yet',
            'publication_blockers': [
                'no live route or screenshot artifact from the current ChatGPT official surface',
                'no durable compose/submit/readback artifact bundle captured on chromium-live',
                'support truth still rests on current first-party anchors plus planning artifacts rather than a live named baseline run',
            ],
        },
        'artifact_refs': [
            {'path': 'docs/support-records/chatgpt.md', 'kind': 'support-record', 'role': 'living ChatGPT support record'},
            {'path': 'SECOND-ADAPTER-REPORT.json', 'kind': 'selection-report', 'role': 'scored second-adapter choice and supporting rationale'},
            {'path': 'SECOND-ADAPTER-BRIEF.json', 'kind': 'execution-brief', 'role': 'ordered phases and artifact targets for the first proof'},
            {'path': 'CHATGPT-FIRST-PROOF-KIT.json', 'kind': 'proof-kit', 'role': 'selector contract, probe prompt, hazards, and failure taxonomy for the first ChatGPT proof'},
            {'path': 'CHATGPT-POSTURE-MATRIX.json', 'kind': 'posture-matrix', 'role': 'route-first posture classifier for deciding whether a landed shell is baseline-safe or a richer branch'},
            {'path': 'CHATGPT-BRANCH-GUARD.json', 'kind': 'branch-guard', 'role': 'witness-driven continue-vs-stop classifier for the route-first ChatGPT baseline'},
            {'path': 'CHATGPT-ROUTE-WITNESS-RECEIPT.json', 'kind': 'witness-receipt', 'role': 'witness-quality and proof-readiness grader for the route-first ChatGPT baseline'},
            {'path': 'CHATGPT-COMPOSER-WITNESS-RECEIPT.json', 'kind': 'composer-witness-receipt', 'role': 'composer writability and readback grader for the route-first ChatGPT baseline'},
            {'path': 'CHATGPT-SUBMIT-WITNESS-RECEIPT.json', 'kind': 'submit-witness-receipt', 'role': 'submit dispatch, completion, and latest-turn proof grader for the route-first ChatGPT baseline'},
            {'path': 'CHATGPT-PROOF-BUNDLE-RECEIPT.json', 'kind': 'proof-bundle-receipt', 'role': 'bundle-level promotion gate for one whole ChatGPT proof window'},
            {'path': 'CHATGPT-PROMOTION-STABILITY-RECEIPT.json', 'kind': 'promotion-stability-receipt', 'role': 'repeatability and support-strength gate for multiple ChatGPT proof windows'},
            {'path': 'CHATGPT-SUPPORT-CLAIM-RECEIPT.json', 'kind': 'support-claim-receipt', 'role': 'lane-bound support-claim envelope so repeated proof does not silently imply broader browser or workspace support'},
            {'path': 'CHATGPT-CAPABILITY-PROFILE-RECEIPT.json', 'kind': 'capability-profile-receipt', 'role': 'text-only capability envelope so a plain route-first baseline does not silently imply Search, uploads, data analysis, or other tool-mode coverage'},
            {'path': 'CHATGPT-AUTH-WORKSPACE-RECEIPT.json', 'kind': 'auth-workspace-receipt', 'role': 'session-bound envelope so guest, personal, Business, Enterprise, or Edu proof does not silently blur together'},
            {'path': 'CHATGPT-PLAN-ENVELOPE-RECEIPT.json', 'kind': 'plan-envelope-receipt', 'role': 'subscription-bound envelope so guest, Free, Plus, Pro, Business, Enterprise, or Edu proof does not silently blur together'},
            {'path': 'CHATGPT-BROWSER-ENVELOPE-RECEIPT.json', 'kind': 'browser-envelope-receipt', 'role': 'browser-bound envelope so one explicit Chromium lane does not silently blur into Chrome, Edge, Firefox, WebKit, or mobile support'},
            {'path': 'CHATGPT-RETENTION-ENVELOPE-RECEIPT.json', 'kind': 'retention-envelope-receipt', 'role': 'conversation-retention envelope so standard saved-history chats, Temporary Chats, memory-off runs, and reused storage-state sessions do not silently blur together'},
            {'path': 'CHATGPT-PLATFORM-ENVELOPE-RECEIPT.json', 'kind': 'platform-envelope-receipt', 'role': 'platform-bound envelope so one desktop web proof lane does not silently blur into Windows app, macOS app, iOS, Android, or mobile-web support'},
            {'path': 'adapters/chatgpt/README.md', 'kind': 'adapter-note', 'role': 'surface-specific goals and known weakness summary'},
            {'path': 'adapters/chatgpt/selector-notes.md', 'kind': 'selector-note', 'role': 'human-readable selector posture for the ChatGPT adapter'},
            {'path': 'validation/latest/chatgpt-first-proof-kit/chatgpt-first-proof-kit.json', 'kind': 'proof-kit-capture', 'role': 'latest captured first-proof kit snapshot'},
            {'path': 'validation/latest/chatgpt-posture-matrix/chatgpt-posture-matrix.json', 'kind': 'posture-matrix-capture', 'role': 'latest captured route-first posture matrix snapshot'},
            {'path': 'validation/latest/chatgpt-branch-guard/chatgpt-branch-guard.json', 'kind': 'branch-guard-capture', 'role': 'latest captured witness-driven branch guard snapshot'},
            {'path': 'validation/latest/chatgpt-route-witness-receipt/chatgpt-route-witness-receipt.json', 'kind': 'witness-receipt-capture', 'role': 'latest captured witness-quality and proof-readiness snapshot'},
            {'path': 'validation/latest/chatgpt-composer-witness-receipt/chatgpt-composer-witness-receipt.json', 'kind': 'composer-witness-receipt-capture', 'role': 'latest captured composer writability and readback snapshot'},
            {'path': 'validation/latest/chatgpt-submit-witness-receipt/chatgpt-submit-witness-receipt.json', 'kind': 'submit-witness-receipt-capture', 'role': 'latest captured submit dispatch and latest-turn proof snapshot'},
            {'path': 'validation/latest/chatgpt-proof-bundle-receipt/chatgpt-proof-bundle-receipt.json', 'kind': 'proof-bundle-receipt-capture', 'role': 'latest captured bundle-level promotion gate snapshot'},
            {'path': 'validation/latest/chatgpt-promotion-stability-receipt/chatgpt-promotion-stability-receipt.json', 'kind': 'promotion-stability-receipt-capture', 'role': 'latest captured repeatability and support-strength gate snapshot'},
            {'path': 'validation/latest/chatgpt-support-claim-receipt/chatgpt-support-claim-receipt.json', 'kind': 'support-claim-receipt-capture', 'role': 'latest captured lane-bound support-claim envelope snapshot'},
            {'path': 'validation/latest/chatgpt-capability-profile-receipt/chatgpt-capability-profile-receipt.json', 'kind': 'capability-profile-receipt-capture', 'role': 'latest captured text-only capability envelope snapshot'},
            {'path': 'validation/latest/chatgpt-auth-workspace-receipt/chatgpt-auth-workspace-receipt.json', 'kind': 'auth-workspace-receipt-capture', 'role': 'latest captured session-bound auth/workspace envelope snapshot'},
            {'path': 'validation/latest/chatgpt-plan-envelope-receipt/chatgpt-plan-envelope-receipt.json', 'kind': 'plan-envelope-receipt-capture', 'role': 'latest captured subscription-plan envelope snapshot'},
            {'path': 'validation/latest/chatgpt-browser-envelope-receipt/chatgpt-browser-envelope-receipt.json', 'kind': 'browser-envelope-receipt-capture', 'role': 'latest captured browser/project-bound envelope snapshot'},
            {'path': 'validation/latest/chatgpt-retention-envelope-receipt/chatgpt-retention-envelope-receipt.json', 'kind': 'retention-envelope-receipt-capture', 'role': 'latest captured conversation-retention envelope snapshot'},
            {'path': 'validation/latest/chatgpt-platform-envelope-receipt/chatgpt-platform-envelope-receipt.json', 'kind': 'platform-envelope-receipt-capture', 'role': 'latest captured product-surface envelope snapshot'},
            {'path': 'validation/latest/second-adapter-brief/second-adapter-brief.json', 'kind': 'brief-capture', 'role': 'latest captured second-adapter brief snapshot'},
        ],
        'result_summary': {
            'worked': [
                'ChatGPT now has a machine-readable first-proof kit with route-first selector priorities and an exact-match benign probe',
                'the candidate bundle turns the seeded ChatGPT support story into one inspectable review object',
                'the new branch guard can classify a concrete route witness into continue, continue-with-caution, or stop before proof actions begin',
                'the new route-witness receipt can refuse proof continuation when the witness is too sparse for a durable handoff',
                'the new composer witness receipt can hold submit proof when a candidate exists but writability or readback evidence is still too weak',
                'the new submit witness receipt can hold completed-turn claims when dispatch, completion, or latest-turn proof is still too thin',
                'the new proof-bundle receipt can hold bundle promotion when one whole proof window is not coherent enough to attach to a stronger held bundle',
                'the new promotion-stability receipt can hold stronger support language until repeated proof windows preserve stable readback and replay materials',
                'the new support-claim receipt can hold wording that would otherwise overstate one Chromium route-first lane as broader ChatGPT coverage',
                'the new capability-profile receipt can hold wording that would otherwise overstate one plain text-only pass as Search, uploads, data analysis, voice, image, or other tool-mode support',
                'the new auth-workspace receipt can hold wording that would otherwise blur guest, personal, Business, Enterprise, or Edu session stories together',
                'the new plan-envelope receipt can hold wording that would otherwise blur guest, Free, Plus, Pro, Business, Enterprise, or Edu subscription stories together',
                'the new browser-envelope receipt can hold wording that would otherwise overstate one Chromium route-first lane as broader browser support',
                'the new retention-envelope receipt can hold wording that would otherwise blur standard saved-history chats, Temporary Chats, memory-off runs, or reused storage-state sessions together',
                'the new platform-envelope receipt can hold wording that would otherwise overstate one desktop web lane as Windows app, macOS app, iOS, Android, or mobile-web support',
            ],
            'held': [
                'the bundle remains planning-only until live route, composer, submit, and readback artifacts are captured',
                'stronger support language remains held until repeated proof windows clear the promotion-stability receipt',
                'support wording remains lane-bound until the support-claim receipt says the browser/auth/route envelope is explicit enough to phrase honestly',
                'support wording remains text-only until the capability-profile receipt says the model/tool/attachment envelope is explicit enough to phrase honestly',
                'support wording remains session-bound until the auth-workspace receipt says the guest/personal/workspace envelope is explicit enough to phrase honestly',
                'support wording remains plan-bound until the plan-envelope receipt says the subscription tier is explicit enough to phrase honestly',
                'support wording remains browser-bound until the browser-envelope receipt says the browser engine, brand, device class, and execution profile are explicit enough to phrase honestly',
                'support wording remains retention-bound until the retention-envelope receipt says history, memory, Temporary Chat, and context-persistence semantics are explicit enough to phrase honestly',
                'support wording remains platform-bound until the platform-envelope receipt says the product surface, runtime shell, and form factor are explicit enough to phrase honestly',
                'no publication claim beyond investigated support is justified yet',
            ],
            'unknown': [
                'the exact current live composer shape for the target account or auth posture',
                'whether the first successful proof will run logged out or logged in',
            ],
            'next_action': 'run the first route-first ChatGPT baseline, require the route, composer, submit, and proof-bundle receipts to pass honestly, then repeat that proof on a second distinct proof window, require the promotion-stability receipt, require the support-claim receipt, require the capability-profile receipt, require the auth-workspace receipt, require the plan-envelope receipt, require the browser-envelope receipt, require the retention-envelope receipt, and finally require the platform-envelope receipt before strengthening support language across tool, auth, workspace, subscription, browser, or conversation-retention modes, or product surfaces',
        },
        'publication_decision': {
            'decision': 'candidate',
            'why': [
                'the bundle is coherent enough to review and run from, but it does not yet contain live official-surface proof',
                'promotion would currently overclaim beyond the attached artifacts',
            ],
            'publish_when': [
                'a live route-first baseline exists on chromium-live with a screenshot and receiver posture note',
                'a named support bundle includes compose, submit, generation, and latest-turn artifacts from the same proof window',
                'repeated proof windows preserve the same benign probe/readback signature and clear the promotion-stability receipt',
                'the claimed support wording stays text-only until the capability-profile receipt says no richer tool or attachment mode is being implied',
                'the claimed support wording stays session-bound until the auth-workspace receipt says guest, personal, or workspace scope is explicit',
                'the claimed support wording stays plan-bound until the plan-envelope receipt says the subscription tier is explicit',
                'the claimed support wording stays browser-bound until the browser-envelope receipt says the engine, brand, device, and execution profile are explicit',
                'the claimed support wording stays retention-bound until the retention-envelope receipt says saved-history, Temporary Chat, memory, and context-persistence semantics are explicit',
                'the claimed support wording stays platform-bound until the platform-envelope receipt says desktop web, mobile web, Windows, macOS, iOS, or Android scope is explicit',
            ],
        },
        'lineage': {'created_in_archive': archive_name},
        'source_refs': list(kit.get('source_keys') or []),
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
        'captured_at': payload.get('generated_at'),
        'output_dir': str(output_dir),
        'json_path': str(json_path),
        'summary_path': str(summary_path),
        'primary_route_hint': ((payload.get('selected_surface') or {}).get('primary_route_hint')),
        'probe_prompt': ((payload.get('probe_prompt') or {}).get('expected_exact_reply')),
        'source_key_count': len(payload.get('source_keys') or []),
        'branch_hazard_count': len(payload.get('ui_branching_hazards') or []),
        'failure_class_count': len(payload.get('failure_taxonomy') or []),
        'candidate_bundle_path': payload.get('candidate_bundle_path'),
    }
    current['changed_fields'] = _changed_fields(previous, current)
    entries.append(current)
    _write_json(history_path, _history_payload(entries))
    return {'kit': payload, 'history_update': {'path': str(history_path), 'capture_count_after_write': len(entries), 'changed_fields_vs_previous': current['changed_fields']}}


def write_root_chatgpt_first_proof_kit(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_chatgpt_first_proof_kit(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def write_candidate_bundle_manifest(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_candidate_bundle_manifest(root=root)
    _write_json(root / CANDIDATE_BUNDLE_REL, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build the first proof kit and candidate bundle seed for the ChatGPT second adapter.')
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
    if args.command == 'capture':
        payload = capture_chatgpt_first_proof_kit(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        print(json.dumps(write_root_chatgpt_first_proof_kit(root=ROOT), indent=2 if args.pretty else None))
        return
    if args.command == 'write-candidate-bundle':
        print(json.dumps(write_candidate_bundle_manifest(root=ROOT), indent=2 if args.pretty else None))
        return
    print(json.dumps(build_chatgpt_first_proof_kit(root=ROOT), indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
