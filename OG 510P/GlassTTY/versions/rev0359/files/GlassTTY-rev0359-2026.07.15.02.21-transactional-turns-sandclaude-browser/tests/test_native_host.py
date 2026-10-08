from __future__ import annotations

import io
import json
import socket
import sys
from pathlib import Path

from glassttyd.native_host import NativeBridge
from glassttyd.protocol import NATIVE_MESSAGE_HOST_MAX_BYTES, read_native_message
from glassttyd.state import StateStore


class _FakeStdout:
    def __init__(self) -> None:
        self.buffer = io.BytesIO()


def _bridge(tmp_path):
    return NativeBridge(StateStore(tmp_path / 'state'))


def _read_one_message(fake_stdout: _FakeStdout) -> dict[str, object]:
    payload = fake_stdout.buffer.getvalue()
    fake_stdin = type('FakeStdin', (), {'buffer': io.BytesIO(payload)})()
    message = read_native_message(fake_stdin)
    assert message is not None
    return message


def test_handle_browser_message_passthroughs_bridge_contexts(tmp_path):
    bridge = _bridge(tmp_path)
    response = bridge.handle_browser_message({
        'type': 'bridge.contexts',
        'request_id': 'req-1',
        'timestamp': 'now',
        'payload': {'openContexts': []},
    })
    assert response is None



def test_handle_browser_message_passthroughs_bridge_probe(tmp_path):
    bridge = _bridge(tmp_path)
    response = bridge.handle_browser_message({
        'type': 'bridge.probe',
        'request_id': 'req-2',
        'timestamp': 'now',
        'payload': {'status': {'nativeConnection': {'connected': True}}},
    })
    assert response is None



def test_handle_browser_message_passthroughs_bridge_offscreen_dom(tmp_path):
    bridge = _bridge(tmp_path)
    response = bridge.handle_browser_message({
        'type': 'bridge.offscreen_dom',
        'request_id': 'req-3',
        'timestamp': 'now',
        'payload': {'ok': True, 'summary': {'title': 'fixture'}},
    })
    assert response is None



def test_handle_browser_message_passthroughs_bridge_offscreen_fixture(tmp_path):
    bridge = _bridge(tmp_path)
    response = bridge.handle_browser_message({
        'type': 'bridge.offscreen_fixture',
        'request_id': 'req-4',
        'timestamp': 'now',
        'payload': {'ok': True, 'fixture': {'adapter': 'offscreen-html'}},
    })
    assert response is None









def test_bridge_status_one_shot_stays_secondary_without_owner(tmp_path):
    bridge = _bridge(tmp_path)
    response = bridge.handle_browser_message({
        'type': 'bridge.status',
        'request_id': 'req-status-secondary-only',
        'timestamp': '2026-03-17T12:10:00Z',
        'payload': {'broker_intent': 'secondary_only'},
    })
    assert response is not None
    payload = response['payload']
    assert payload['broker']['role'] == 'secondary'
    assert payload['broker']['socket_exists'] is False
    assert payload['broker']['owner_metadata'] is None
    assert bridge.broker_started is False
    assert bridge._broker is None
    assert not bridge.socket_path().exists()




def test_health_ping_one_shot_stays_secondary_without_owner(tmp_path):
    bridge = _bridge(tmp_path)
    response = bridge.handle_browser_message({
        'type': 'health.ping',
        'request_id': 'req-health-secondary-only',
        'timestamp': '2026-03-17T12:10:30Z',
        'payload': {'broker_intent': 'secondary_only'},
    })
    assert response is not None
    payload = response['payload']
    assert payload['broker']['role'] == 'secondary'
    assert payload['broker']['socket_exists'] is False
    assert bridge.broker_started is False
    assert bridge._broker is None
    assert not bridge.socket_path().exists()

def test_health_ping_owner_candidate_claims_broker_lazily(tmp_path):
    bridge = _bridge(tmp_path)
    response = bridge.handle_browser_message({
        'type': 'health.ping',
        'request_id': 'req-health-owner',
        'timestamp': '2026-03-17T12:11:00Z',
        'payload': {
            'broker_intent': 'owner_candidate',
            'requestId': 'health-correlation-owner',
            'trigger': 'bridge.probe',
        },
    })
    assert response is not None
    payload = response['payload']
    try:
        assert response['request_id'] == 'req-health-owner'
        assert payload['echo']['requestId'] == 'health-correlation-owner'
        assert payload['echo']['trigger'] == 'bridge.probe'
        assert payload['broker']['role'] == 'owner'
        assert payload['broker']['socket_exists'] is True
        assert payload['broker']['owner_metadata']['host_identity']['boot_id'] == bridge.boot_id
        assert bridge.broker_started is True
        assert bridge._broker is not None
        assert bridge.socket_path().exists()
    finally:
        bridge.stop_broker_if_owner()


def test_extension_correlates_native_health_echo_and_envelope() -> None:
    source = (
        Path(__file__).resolve().parents[1] / 'extension' / 'src' / 'background' / 'main.ts'
    ).read_text(encoding='utf-8')

    assert 'envelopeRequestId: healthRequest.request_id' in source
    assert "typeof echo.requestId === 'string'" in source
    assert 'pendingNativeHealth.envelopeRequestId === message.request_id' in source
    assert 'lastHealthOk: false' in source


def test_extension_reloads_a_stale_unpacked_worker_bundle() -> None:
    root = Path(__file__).resolve().parents[1]
    source = (root / 'extension' / 'src' / 'background' / 'main.ts').read_text(encoding='utf-8')
    build = (root / 'extension' / 'scripts' / 'build.mjs').read_text(encoding='utf-8')

    assert 'manifestMetadata.version !== buildVersion' in build
    assert '__GLASSTTY_BUNDLE_VERSION__: JSON.stringify(buildVersion)' in build
    assert 'MANIFEST_VERSION === __GLASSTTY_BUNDLE_VERSION__' in source
    assert "STALE_BUNDLE_RELOAD_KEY = 'staleBundleReloadAttempt'" in source
    assert 'is still stale for manifest' in source
    assert 'if (!BUNDLE_VERSION_IS_CURRENT) return;' in source
    assert "{ reload: () => void }).reload()" in source


def test_probe_page_preserves_explicit_stale_worker_errors() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / 'extension' / 'src' / 'probe' / 'main.ts'
    ).read_text(encoding='utf-8')

    assert 'function probePayload(envelope:' in source
    assert "throw new Error(`bridge.probe failed: ${error}`)" in source
    assert 'result.bridge = probePayload(bridge)' in source

def test_bridge_status_reports_host_identity_and_broker_role(tmp_path):
    bridge = _bridge(tmp_path)
    assert bridge.start_broker_if_owner() is True
    try:
        response = bridge.handle_browser_message({
            'type': 'bridge.status',
            'request_id': 'req-status-owner',
            'timestamp': '2026-03-17T11:40:00Z',
            'payload': {},
        })
        assert response is not None
        payload = response['payload']
        assert payload['host_identity']['boot_id'] == bridge.boot_id
        assert payload['host_identity']['message_count'] == 1
        assert payload['broker']['role'] == 'owner'
        assert payload['broker']['connected_clients'] == 0
        assert payload['broker']['owner_metadata']['host_identity']['boot_id'] == bridge.boot_id
    finally:
        bridge.stop_broker_if_owner()


def test_secondary_bridge_skips_broker_socket_takeover(tmp_path):
    owner = _bridge(tmp_path)
    secondary = _bridge(tmp_path)
    assert owner.start_broker_if_owner() is True
    assert secondary.start_broker_if_owner() is False
    try:
        response = secondary.handle_browser_message({
            'type': 'bridge.status',
            'request_id': 'req-status-secondary',
            'timestamp': '2026-03-17T11:41:00Z',
            'payload': {},
        })
        assert response is not None
        payload = response['payload']
        assert payload['broker']['role'] == 'secondary'
        assert payload['host_identity']['boot_id'] == secondary.boot_id
        assert payload['broker']['owner_metadata']['host_identity']['boot_id'] == owner.boot_id
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
            conn.connect(str(owner.socket_path()))
            hello = json.loads(conn.makefile('r', encoding='utf-8').readline())
        assert hello['stream'] == 'server'
        assert hello['payload']['broker']['role'] == 'owner'
        assert hello['payload']['host_identity']['boot_id'] == owner.boot_id
    finally:
        secondary.stop_broker_if_owner()
        owner.stop_broker_if_owner()

def test_bridge_status_reports_compact_overflow_inventory_when_empty(tmp_path):
    bridge = _bridge(tmp_path)
    response = bridge.handle_browser_message({
        'type': 'bridge.status',
        'request_id': 'req-status',
        'timestamp': '2026-03-17T11:20:00Z',
        'payload': {},
    })
    assert response is not None
    payload = response['payload']
    assert payload['overflow_inventory']['artifact_count'] == 0
    assert payload['overflow_inventory']['recent_artifacts'] == []
    assert 'artifacts' not in payload['overflow_inventory']

def test_emit_to_extension_spools_oversized_message_and_emits_notice(monkeypatch, tmp_path):
    bridge = _bridge(tmp_path)
    fake_stdout = _FakeStdout()
    monkeypatch.setattr(sys, 'stdout', fake_stdout)
    oversized_message = {
        'type': 'bridge.offscreen_fixture',
        'request_id': 'req-overflow',
        'timestamp': '2026-03-17T09:30:00Z',
        'payload': {'blob': 'x' * (NATIVE_MESSAGE_HOST_MAX_BYTES + 4096)},
    }

    bridge.emit_to_extension(oversized_message)

    outbound = _read_one_message(fake_stdout)
    assert outbound['type'] == 'error.report'
    payload = outbound['payload']
    assert payload['overflow'] is True
    assert payload['original_type'] == 'bridge.offscreen_fixture'
    assert payload['message_size_bytes'] > NATIVE_MESSAGE_HOST_MAX_BYTES
    artifact_path = tmp_path / 'state' / 'fixtures' / json.loads(json.dumps(payload['artifact_path'])).split('/')[-1]
    assert artifact_path.exists()
    artifact = json.loads(artifact_path.read_text(encoding='utf-8'))
    assert artifact['kind'] == 'oversized-host-outbound'
    assert artifact['message']['type'] == 'bridge.offscreen_fixture'
    latest = json.loads((tmp_path / 'state' / 'latest' / 'oversized-host-outbound.json').read_text(encoding='utf-8'))
    assert latest['artifact_path'] == str(artifact_path)
    status = bridge.status()
    assert status['last_oversized_host_message']['artifact_path'] == str(artifact_path)
    assert status['overflow_inventory']['artifact_count'] == 1
    assert status['overflow_inventory']['recent_artifacts'][0]['path'] == str(artifact_path)
    assert 'artifacts' not in status['overflow_inventory']
    events = (tmp_path / 'state' / 'events.jsonl').read_text(encoding='utf-8').splitlines()
    assert any('host_outbound_overflow' in line for line in events)
    assert not any('host_outbound"' in line and 'req-overflow' in line for line in events)



def test_emit_to_extension_keeps_regular_messages_inline(monkeypatch, tmp_path):
    bridge = _bridge(tmp_path)
    fake_stdout = _FakeStdout()
    monkeypatch.setattr(sys, 'stdout', fake_stdout)
    message = {
        'type': 'bridge.status',
        'request_id': 'req-ok',
        'timestamp': '2026-03-17T09:31:00Z',
        'payload': {'ok': True},
    }

    bridge.emit_to_extension(message)

    outbound = _read_one_message(fake_stdout)
    assert outbound == message
    latest_path = tmp_path / 'state' / 'latest' / 'oversized-host-outbound.json'
    assert not latest_path.exists()
    events = (tmp_path / 'state' / 'events.jsonl').read_text(encoding='utf-8').splitlines()
    assert any('host_outbound' in line and 'req-ok' in line for line in events)
