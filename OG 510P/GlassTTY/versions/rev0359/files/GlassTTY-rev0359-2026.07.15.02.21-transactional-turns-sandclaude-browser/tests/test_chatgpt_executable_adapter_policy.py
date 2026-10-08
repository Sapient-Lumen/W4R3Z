from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_chatgpt_adapter_submit_path_is_route_guarded_and_scoped() -> None:
    source = (ROOT / 'extension' / 'src' / 'adapters' / 'chatgpt.ts').read_text(encoding='utf-8')

    assert "function routePostureAllowsSubmit" in source
    assert "return posture === 'plain-chat'" in source
    assert "findComposerActionRoot" in source
    assert "findLikelySendButton(document, window, composer)" in source
    assert "keyboard_submit_enabled: false" in source
    assert "route_posture_allows_submit" in source
    assert "prompt_present_for_submit" in source


def test_chatgpt_manifest_coverage_stays_explicit() -> None:
    manifest = json.loads((ROOT / 'extension' / 'manifest.json').read_text(encoding='utf-8'))

    assert 'https://chatgpt.com/*' in manifest['host_permissions']
    assert manifest['host_permissions'] == ['https://chatgpt.com/*']
    content_matches = [match for script in manifest['content_scripts'] for match in script.get('matches', [])]
    assert 'https://chatgpt.com/*' in content_matches
    assert content_matches == ['https://chatgpt.com/*']



def test_content_runtime_preserves_attempt_id_for_proof_coherence() -> None:
    source = (ROOT / 'extension' / 'src' / 'content' / 'main.ts').read_text(encoding='utf-8')

    assert 'function attemptIdFromMessage' in source
    assert 'function withAttemptMetadata' in source
    assert "payload?.attempt_id" in source
    assert "payload?.run_id" in source
    assert "metadata: Record<string, unknown>" in source
    assert "replyTo(message, 'fixture.capture', withAttemptMetadata" in source
    assert "replyTo(message, 'prompt.submit', withAttemptMetadata" in source
    assert "replyTo(message, 'state.snapshot', withAttemptMetadata" in source
    assert "readback: activeAdapter.readPrompt(document), url: window.location.href" in source
    assert "adapter: activeAdapter.name, url: window.location.href" in source
    assert 'const latestWitness = activeAdapter.readLatestOutputWitness?.(document)' in source
    assert 'latest_output_witness: latestWitness' in source
    assert 'const latestUserTurnWitness = activeAdapter.readLatestUserTurnWitness?.(document)' in source
    assert 'latest_user_turn_witness: latestUserTurnWitness' in source


def test_chatgpt_route_classifier_prefers_path_and_composer_over_global_body_text() -> None:
    source = (ROOT / 'extension' / 'src' / 'adapters' / 'chatgpt.ts').read_text(encoding='utf-8')

    assert 'function classifyRouteDetails' in source
    assert 'plain-chat-path-and-composer' in source
    assert "pathname === '/' || pathname.startsWith('/c/')" in source
    assert 'activeShellText(document)' in source
    assert 'bodyText(document)' not in source
    assert "includesAny(text, ['project'" not in source
    assert 'route_evidence: route.evidence' in source
    assert 'route_prompt_present: route.prompt_present' in source


def test_chatgpt_latest_output_prefers_latest_assistant_like_dom_order() -> None:
    source = (ROOT / 'extension' / 'src' / 'adapters' / 'chatgpt.ts').read_text(encoding='utf-8')

    assert 'function outputDocumentOrder' in source
    assert 'function isAssistantOutputCandidate' in source
    assert 'function latestOutputWitness' in source
    assert 'readLatestOutputWitness(document: Document)' in source
    assert 'latest-visible-assistant-like-node-in-dom-order' in source
    assert 'function authorRoleElement' in source
    assert "closest('[data-message-author-role]')" in source
    assert "if (roleForTurn) return roleForTurn === 'assistant'" in source
    assert "if (roleForTurn === 'user') score -= 0.55" in source
    assert 'assistant_like: match.assistant_like' in source
    assert 'author_role: roleForTurn' in source
    assert 'author_role_source: authorRoleSource(node)' in source
    assert '.slice().sort(outputDocumentOrder)' in source


def test_chatgpt_latest_user_turn_witness_is_exposed() -> None:
    source = (ROOT / 'extension' / 'src' / 'adapters' / 'chatgpt.ts').read_text(encoding='utf-8')
    base = (ROOT / 'extension' / 'src' / 'adapters' / 'base.ts').read_text(encoding='utf-8')

    assert 'export interface UserTurnWitness' in base
    assert 'readLatestUserTurnWitness?(document: Document): UserTurnWitness' in base
    assert 'const USER_TURN_SELECTORS' in source
    assert 'function latestUserTurnWitness' in source
    assert 'latest-visible-user-like-node-in-dom-order' in source
    assert 'latest_user_turn_witness: userTurnWitness' in source
    assert 'document_order_index?: number' in base
    assert 'function documentOrderIndex' in source
    assert 'latest_output_document_order_index: outputWitness.document_order_index' in source
    assert 'latest_user_turn_document_order_index: userTurnWitness.document_order_index' in source
    assert 'latest_turn_pair_user_before_assistant' in source
    assert 'latest_user_turn_selector: userTurnWitness.selector_hint' in source


def test_chatgpt_fixture_records_generation_settled_witnesses() -> None:
    source = (ROOT / 'extension' / 'src' / 'adapters' / 'chatgpt.ts').read_text(encoding='utf-8')

    assert 'function generationState' in source
    assert 'GENERATION_STOP_TERMS' in source
    assert 'generation_state: generation.state' in source
    assert 'generation_stop_control_present: Boolean(generation.stop.node)' in source
    assert 'generation_continue_control_present: Boolean(generation.continue.node)' in source
    assert 'generation_stop_selector' in source


def test_sidepanel_has_manual_chatgpt_first_proof_capture_helper() -> None:
    html = (ROOT / 'extension' / 'sidepanel' / 'index.html').read_text(encoding='utf-8')
    source = (ROOT / 'extension' / 'src' / 'sidepanel' / 'main.ts').read_text(encoding='utf-8')

    assert 'ChatGPT first proof' in html
    assert 'proof-attempt-id' in html
    assert 'proof-write-capture' in html
    assert 'proof-submit' in html
    assert 'proof-read-latest' in html
    assert 'CHATGPT_FIRST_PROOF_PROMPT' in source
    assert 'proofCaptureDocument' in source
    assert "attempt_id: attemptId" in source
    assert "proofRequest('prompt.submit', {}, {" in source
    assert "operator_submit_confirmed: true" in source
    assert "submit_method: 'sidepanel-operator-click'" in source
    assert "proofRequest('transcript.latest')" in source
    assert 'chatgpt-first-proof-capture.json' in source
    assert 'sequence_index: index' in source
    assert 'url: payloadUrl' in source
    assert 'adapter: payloadAdapter' in source
    assert 'request_type: response.type' in source
    assert 'operator_action: payload.operator_action' in source
    assert 'latest_user_turn_witness_text: latestUserTurnWitnessText' in source
    assert 'latest_user_turn_witness_text_matches_probe: latestUserTurnWitnessTextMatchesProbe' in source
    assert 'latest_output_witness_document_order_index: latestOutputWitnessDocumentOrderIndex' in source
    assert 'latest_user_turn_witness_document_order_index: latestUserTurnWitnessDocumentOrderIndex' in source
    assert 'latest_turn_pair_same_frame: latestTurnPairSameFrame' in source
    assert 'latest_turn_pair_user_before_assistant: latestTurnPairUserBeforeAssistant' in source
    assert 'latest_output_witness_frame_depth: latestOutputWitnessFrameDepth' in source
    assert 'latest_user_turn_witness_frame_depth: latestUserTurnWitnessFrameDepth' in source
    assert 'explicit frame_depth/frame_path context' in source
    assert 'chatgptConversationRoutePath' in source
    assert 'same_conversation_route_after_latest' in source
    assert 'proof_chain_conversation_route_path' in source


def test_chatgpt_send_button_scoring_avoids_composer_tool_controls() -> None:
    source = (ROOT / 'extension' / 'src' / 'adapters' / 'chatgpt.ts').read_text(encoding='utf-8')

    assert '#composer-submit-button' in source
    assert 'button#composer-submit-button' in source
    assert 'observed_live_send_selector' in source
    assert 'observed_live_send_testid' in source
    assert 'observed_live_send_aria_label' in source
    assert 'form button[type="submit"]' in source
    assert 'contentEditableMode' in source
    assert '[contenteditable="plaintext-only"]' in source
    assert 'data-placeholder' in source
    assert "'model'" in source
    assert "'picker'" in source
    assert "'reasoning'" in source
    assert "'library'" in source
    assert "'canvas'" in source
    assert "'email'" in source
    assert "'tools'" in source
    assert 'NON_SEND_CONTROL_TERMS' in source
    assert 'function sendControlSignal' in source
    assert 'signal.intent' in source
    assert 'submit_signal_explicit' in source
    assert 'submit_signal_submit_type' in source
    assert 'signal.disqualified' in source
    assert 'score -= 1.0' in source
    assert "'add files and more'" in source
    assert "'composer-plus'" in source
    assert "'start dictation'" in source
    assert "'copy response'" in source
    assert "'extra high'" in source
    assert 'findBlockedComposerControl' in source
    assert 'blocked_composer_control_selector' in source
    assert 'submit_expected_live_selector: OBSERVED_LIVE_SEND_SELECTOR' in source
    assert "submit_button_live_surface_lock: '#composer-submit-button[data-testid=send-button]'" in source


def test_surface_megathing_is_paste_safe_and_csp_hostile_free() -> None:
    source = (ROOT / 'tools' / 'chatgpt-surface-megathing.js').read_text(encoding='utf-8')

    assert 'safe-wrapped-ascii' in source
    assert 'GLASSTTY_SURFACE_CAPSULE_JSON=' in source
    assert '__GLASSTTY_DOWNLOAD_SURFACE_REPORT__' in source
    assert 'no_eval' in source
    assert 'no_script_tag_injection' in source
    assert 'eval(' not in source
    assert 'new Function' not in source
    assert "createElement('script'" not in source
    assert 'createElement("script"' not in source
    assert '\u2028' not in source
    assert '\u2029' not in source
    assert max(len(line) for line in source.splitlines()) <= 88


def test_surface_capsule_tool_is_paste_safe_and_small_enough() -> None:
    source = (ROOT / 'tools' / 'chatgpt-surface-capsule.js').read_text(encoding='utf-8')

    assert 'capsule-safe-ascii' in source
    assert 'GLASSTTY_SURFACE_CAPSULE_JSON=' in source
    assert '__GLASSTTY_DOWNLOAD_SURFACE_CAPSULE__' in source
    assert 'send_readiness' in source
    assert 'blocked_send_control' in source
    assert 'eval(' not in source
    assert 'new Function' not in source
    assert "createElement('script'" not in source
    assert 'createElement("script"' not in source
    assert '\u2028' not in source
    assert '\u2029' not in source
    assert max(len(line) for line in source.splitlines()) <= 88
