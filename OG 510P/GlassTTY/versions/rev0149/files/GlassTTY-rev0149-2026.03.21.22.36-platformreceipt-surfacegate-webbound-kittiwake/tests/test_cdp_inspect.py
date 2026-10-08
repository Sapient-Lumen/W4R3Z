from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('glasstty_cdp_inspect_testshim', ROOT / 'scripts' / 'cdp_inspect.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)
choose_target = MODULE.choose_target
extension_url_prefix = MODULE.extension_url_prefix
inspect_cdp = MODULE.inspect_cdp
watch_browser_targets = MODULE.watch_browser_targets
attach_browser_targets = MODULE.attach_browser_targets


def test_inspect_cdp_reports_unavailable_port() -> None:
    report = inspect_cdp(port=9, extension_id='abc', timeout=0.05, wait=0.1)
    assert report['available'] is False
    assert report['port'] == 9
    assert report['extension_id'] == 'abc'
    assert 'last_error' in report


def test_choose_target_filters_by_type_and_prefix() -> None:
    targets = [
        {'type': 'page', 'url': 'https://example.com/', 'title': 'Example'},
        {'type': 'page', 'url': 'chrome-extension://abc/probe/index.html', 'title': 'chrome-extension://abc/probe/index.html'},
        {'type': 'service_worker', 'url': 'chrome-extension://abc/background.js', 'title': 'Service Worker'},
    ]
    target = choose_target(targets, target_type='page', url_prefix=extension_url_prefix('abc'))
    assert target is not None
    assert target['url'].endswith('/probe/index.html')


class _FakeWebSocket:
    def __init__(self, messages: list[dict[str, object]]) -> None:
        self._messages = [json.dumps(message) for message in messages]
        self.sent: list[dict[str, object]] = []
        self.closed = False
        self.timeout_values: list[float] = []

    def send(self, payload: str) -> None:
        self.sent.append(json.loads(payload))

    def recv(self) -> str:
        if self._messages:
            return self._messages.pop(0)
        raise TimeoutError('no more fake websocket messages')

    def settimeout(self, value: float) -> None:
        self.timeout_values.append(value)

    def close(self) -> None:
        self.closed = True


def test_watch_browser_targets_collects_extension_service_worker(monkeypatch) -> None:
    fake_ws = _FakeWebSocket([
        {'id': 1, 'result': {}},
        {
            'method': 'Target.targetCreated',
            'params': {
                'targetInfo': {
                    'targetId': 'worker-1',
                    'type': 'service_worker',
                    'title': 'Service Worker chrome-extension://abc/dist/background/main.js',
                    'url': 'chrome-extension://abc/dist/background/main.js',
                    'attached': False,
                    'browserContextId': 'context-1',
                },
            },
        },
        {
            'method': 'Target.targetInfoChanged',
            'params': {
                'targetInfo': {
                    'targetId': 'page-1',
                    'type': 'page',
                    'title': 'chrome-extension://abc/probe/index.html',
                    'url': 'chrome-extension://abc/probe/index.html',
                    'attached': False,
                    'browserContextId': 'context-1',
                },
            },
        },
        {'id': 2, 'result': {}},
    ])

    monkeypatch.setattr(MODULE, 'create_connection', lambda *args, **kwargs: fake_ws)

    report = watch_browser_targets('ws://127.0.0.1:9222/devtools/browser/test', extension_id='abc', duration=0.01, timeout=0.05)
    assert report['event_count'] >= 2
    assert report['service_worker_seen'] is True
    assert any(item['type'] == 'service_worker' for item in report['extension_targets'])
    assert any(item['type'] == 'page' for item in report['extension_pages'])
    assert fake_ws.closed is True
    assert fake_ws.sent[0]['method'] == 'Target.setDiscoverTargets'
    assert fake_ws.sent[-1]['method'] == 'Target.setDiscoverTargets'
    assert fake_ws.sent[-1]['params'] == {'discover': False}



def test_inspect_cdp_merges_browser_target_snapshot(monkeypatch) -> None:
    version_payload = {
        'Browser': 'Chromium/145.0.0.0',
        'webSocketDebuggerUrl': 'ws://127.0.0.1:9222/devtools/browser/test',
    }
    list_payload = [
        {'id': 'page-1', 'type': 'page', 'url': 'https://example.com/', 'title': 'Example'},
    ]

    def fake_fetch_json(url: str, timeout: float):
        assert timeout == 0.25
        if url.endswith('/json/version'):
            return version_payload
        if url.endswith('/json/list'):
            return list_payload
        raise AssertionError(url)

    def fake_fetch_browser_targets(websocket_url: str, *, timeout: float = 3.0):
        assert websocket_url == version_payload['webSocketDebuggerUrl']
        assert timeout == 0.25
        return [
            {
                'id': 'worker-1',
                'type': 'service_worker',
                'title': 'Service Worker',
                'url': 'chrome-extension://abc/dist/background/main.js',
                'webSocketDebuggerUrl': None,
                'attached': False,
                'browserContextId': 'context-1',
                'subtype': None,
            },
        ]

    monkeypatch.setattr(MODULE, 'fetch_json', fake_fetch_json)
    monkeypatch.setattr(MODULE, 'fetch_browser_targets', fake_fetch_browser_targets)

    report = inspect_cdp(port=9222, extension_id='abc', timeout=0.25, wait=0.25)
    assert report['available'] is True
    assert report['browser_websocket_url'] == version_payload['webSocketDebuggerUrl']
    assert report['target_count'] == 1
    assert report['browser_target_count'] == 1
    assert report['service_worker_seen'] is False
    assert report['browser_service_worker_seen'] is True
    assert report['extension_visible'] is True
    assert report['browser_extension_targets'][0]['url'].startswith('chrome-extension://abc/')



def test_inspect_cdp_merges_browser_target_watch(monkeypatch) -> None:
    version_payload = {
        'Browser': 'Chromium/145.0.0.0',
        'webSocketDebuggerUrl': 'ws://127.0.0.1:9222/devtools/browser/test',
    }
    list_payload = [
        {'id': 'page-1', 'type': 'page', 'url': 'https://example.com/', 'title': 'Example'},
    ]

    def fake_fetch_json(url: str, timeout: float):
        if url.endswith('/json/version'):
            return version_payload
        if url.endswith('/json/list'):
            return list_payload
        raise AssertionError(url)

    monkeypatch.setattr(MODULE, 'fetch_json', fake_fetch_json)
    monkeypatch.setattr(MODULE, 'fetch_browser_targets', lambda websocket_url, timeout=3.0: [])
    monkeypatch.setattr(
        MODULE,
        'watch_browser_targets',
        lambda websocket_url, extension_id, duration, timeout=3.0: {
            'requested_seconds': duration,
            'events': [{'method': 'Target.targetCreated'}],
            'event_count': 1,
            'observed_targets': [
                {
                    'id': 'worker-1',
                    'type': 'service_worker',
                    'title': 'Service Worker',
                    'url': 'chrome-extension://abc/dist/background/main.js',
                    'webSocketDebuggerUrl': None,
                    'attached': False,
                    'browserContextId': 'context-1',
                    'subtype': None,
                },
            ],
            'observed_target_count': 1,
            'destroyed_target_ids': [],
            'extension_targets': [
                {
                    'id': 'worker-1',
                    'type': 'service_worker',
                    'title': 'Service Worker',
                    'url': 'chrome-extension://abc/dist/background/main.js',
                    'webSocketDebuggerUrl': None,
                    'attached': False,
                    'browserContextId': 'context-1',
                    'subtype': None,
                },
            ],
            'extension_pages': [],
            'service_worker_seen': True,
        },
    )

    report = inspect_cdp(port=9222, extension_id='abc', timeout=0.25, wait=0.25, watch=0.5)
    assert report['browser_target_watch']['event_count'] == 1
    assert report['browser_watch_service_worker_seen'] is True
    assert report['browser_service_worker_seen'] is False
    assert report['extension_visible'] is True


def test_attach_browser_targets_collects_runtime_id(monkeypatch) -> None:
    fake_ws = _FakeWebSocket([
        {'id': 1, 'result': {}},
        {
            'method': 'Target.attachedToTarget',
            'params': {
                'sessionId': 'session-1',
                'waitingForDebugger': False,
                'targetInfo': {
                    'targetId': 'page-1',
                    'type': 'page',
                    'title': 'chrome-extension://abc/probe/index.html',
                    'url': 'chrome-extension://abc/probe/index.html',
                    'attached': True,
                    'browserContextId': 'context-1',
                },
            },
        },
        {
            'id': 2,
            'result': {
                'result': {
                    'type': 'object',
                    'value': {
                        'href': 'chrome-extension://abc/probe/index.html',
                        'title': 'probe',
                        'runtimeId': 'abc',
                        'hasChromeRuntime': True,
                        'userAgent': 'fake-agent',
                    },
                },
            },
        },
        {'id': 3, 'result': {}},
    ])

    monkeypatch.setattr(MODULE, 'create_connection', lambda *args, **kwargs: fake_ws)

    report = attach_browser_targets('ws://127.0.0.1:9222/devtools/browser/test', extension_id='abc', duration=0.01, timeout=0.05)
    assert report['event_count'] >= 1
    assert report['attached_target_count'] == 1
    assert report['session_evaluation_count'] == 1
    assert report['runtime_ids'] == ['abc']
    assert report['runtime_id_matches_extension'] is True
    assert report['service_worker_seen'] is False
    assert fake_ws.sent[0]['method'] == 'Target.setAutoAttach'
    assert fake_ws.sent[1]['method'] == 'Runtime.evaluate'
    assert fake_ws.sent[1]['sessionId'] == 'session-1'
    assert fake_ws.sent[-1]['method'] == 'Target.setAutoAttach'
    assert fake_ws.sent[-1]['params']['autoAttach'] is False


def test_inspect_cdp_merges_browser_target_attach(monkeypatch) -> None:
    version_payload = {
        'Browser': 'Chromium/145.0.0.0',
        'webSocketDebuggerUrl': 'ws://127.0.0.1:9222/devtools/browser/test',
    }
    list_payload = [
        {'id': 'page-1', 'type': 'page', 'url': 'https://example.com/', 'title': 'Example'},
    ]

    def fake_fetch_json(url: str, timeout: float):
        if url.endswith('/json/version'):
            return version_payload
        if url.endswith('/json/list'):
            return list_payload
        raise AssertionError(url)

    monkeypatch.setattr(MODULE, 'fetch_json', fake_fetch_json)
    monkeypatch.setattr(MODULE, 'fetch_browser_targets', lambda websocket_url, timeout=3.0: [])
    monkeypatch.setattr(MODULE, 'watch_browser_targets', lambda websocket_url, extension_id, duration, timeout=3.0: {'requested_seconds': duration, 'events': [], 'event_count': 0, 'observed_targets': [], 'observed_target_count': 0, 'destroyed_target_ids': [], 'extension_targets': [], 'extension_pages': [], 'service_worker_seen': False})
    monkeypatch.setattr(
        MODULE,
        'attach_browser_targets',
        lambda websocket_url, extension_id, duration, timeout=3.0: {
            'requested_seconds': duration,
            'events': [{'method': 'Target.attachedToTarget'}],
            'event_count': 1,
            'attached_targets': [
                {
                    'id': 'page-1',
                    'type': 'page',
                    'title': 'chrome-extension://abc/probe/index.html',
                    'url': 'chrome-extension://abc/probe/index.html',
                    'webSocketDebuggerUrl': None,
                    'attached': True,
                    'browserContextId': 'context-1',
                    'subtype': None,
                    'sessionId': 'session-1',
                    'waitingForDebugger': False,
                },
            ],
            'attached_target_count': 1,
            'detached_session_ids': [],
            'extension_targets': [
                {
                    'id': 'page-1',
                    'type': 'page',
                    'title': 'chrome-extension://abc/probe/index.html',
                    'url': 'chrome-extension://abc/probe/index.html',
                    'webSocketDebuggerUrl': None,
                    'attached': True,
                    'browserContextId': 'context-1',
                    'subtype': None,
                    'sessionId': 'session-1',
                    'waitingForDebugger': False,
                },
            ],
            'extension_pages': [
                {
                    'id': 'page-1',
                    'type': 'page',
                    'title': 'chrome-extension://abc/probe/index.html',
                    'url': 'chrome-extension://abc/probe/index.html',
                    'webSocketDebuggerUrl': None,
                    'attached': True,
                    'browserContextId': 'context-1',
                    'subtype': None,
                    'sessionId': 'session-1',
                    'waitingForDebugger': False,
                },
            ],
            'service_worker_seen': False,
            'session_evaluations': [
                {
                    'sessionId': 'session-1',
                    'target': {'id': 'page-1', 'type': 'page', 'url': 'chrome-extension://abc/probe/index.html'},
                    'result': {'runtimeId': 'abc'},
                },
            ],
            'session_evaluation_count': 1,
            'runtime_ids': ['abc'],
            'runtime_id_matches_extension': True,
            'errors': [],
        },
    )

    report = inspect_cdp(port=9222, extension_id='abc', timeout=0.25, wait=0.25, watch=0.5, attach=0.5)
    assert report['browser_target_attach']['event_count'] == 1
    assert report['browser_attach_runtime_id_matches_extension'] is True
    assert report['browser_attach_runtime_ids'] == ['abc']
    assert report['extension_visible'] is True
