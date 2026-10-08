from __future__ import annotations

import json
import socket
import time
import urllib.request
from typing import Any

from websocket import WebSocketTimeoutException, create_connection


EXTENSION_ATTACH_EVAL = """(() => ({
  href: globalThis.location?.href ?? null,
  title: globalThis.document?.title ?? null,
  runtimeId: globalThis.chrome?.runtime?.id ?? null,
  hasChromeRuntime: !!globalThis.chrome?.runtime,
  userAgent: globalThis.navigator?.userAgent ?? null,
}))()"""

ATTACH_FILTER = [
    {'type': 'page'},
    {'type': 'service_worker'},
]


def fetch_json(url: str, timeout: float) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def extension_url_prefix(extension_id: str | None) -> str | None:
    return f"chrome-extension://{extension_id}/" if extension_id else None


def choose_target(targets: list[dict[str, Any]], *, target_type: str | None = None, url_prefix: str | None = None, title_contains: str | None = None) -> dict[str, Any] | None:
    for item in targets:
        if target_type and item.get('type') != target_type:
            continue
        if url_prefix and not str(item.get('url') or '').startswith(url_prefix):
            continue
        if title_contains and title_contains not in str(item.get('title') or ''):
            continue
        return item
    return None


def _normalized_target(item: dict[str, Any]) -> dict[str, Any]:
    return {
        'id': item.get('id') or item.get('targetId'),
        'type': item.get('type'),
        'title': item.get('title'),
        'url': item.get('url'),
        'webSocketDebuggerUrl': item.get('webSocketDebuggerUrl'),
        'attached': item.get('attached'),
        'browserContextId': item.get('browserContextId'),
        'subtype': item.get('subtype'),
    }


def _extension_target_subset(targets: list[dict[str, Any]], extension_id: str | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    if not extension_id:
        return [], [], False
    prefix = extension_url_prefix(extension_id)
    extension_targets = [item for item in targets if isinstance(item.get('url'), str) and item['url'].startswith(prefix or '')]
    extension_pages = [item for item in extension_targets if item.get('type') == 'page']
    service_worker_seen = any(item.get('type') == 'service_worker' for item in extension_targets)
    return extension_targets, extension_pages, service_worker_seen


def _target_filter_default() -> list[dict[str, Any]]:
    return [
        {'type': 'browser', 'exclude': True},
        {'type': 'tab', 'exclude': True},
        {},
    ]


def _recv_matching_response(ws: Any, *, response_id: int, deadline: float, event_handler: Any | None = None) -> dict[str, Any]:
    while time.time() < deadline:
        remaining = max(0.05, deadline - time.time())
        try:
            ws.settimeout(remaining)
        except Exception:  # noqa: BLE001
            pass
        try:
            raw = ws.recv()
        except (TimeoutError, socket.timeout, WebSocketTimeoutException):
            continue
        message = json.loads(raw)
        if message.get('id') == response_id:
            if message.get('error'):
                raise RuntimeError(f"CDP command failed: {message['error']}")
            return message
        if event_handler is not None:
            event_handler(message)
    raise RuntimeError(f'timed out waiting for CDP response id={response_id}')


def _cdp_command(websocket_url: str, method: str, params: dict[str, Any] | None = None, *, timeout: float = 3.0) -> dict[str, Any]:
    session_timeout = max(float(timeout), 3.0)
    ws = create_connection(websocket_url, timeout=session_timeout, origin='http://127.0.0.1')
    try:
        ws.send(json.dumps({
            'id': 1,
            'method': method,
            'params': params or {},
        }))
        return _recv_matching_response(ws, response_id=1, deadline=time.time() + session_timeout)
    finally:
        ws.close()


def evaluate_target(websocket_url: str, expression: str, *, timeout: float = 3.0) -> dict[str, Any]:
    return _cdp_command(
        websocket_url,
        'Runtime.evaluate',
        {
            'expression': expression,
            'returnByValue': True,
            'awaitPromise': True,
        },
        timeout=timeout,
    )


def fetch_browser_targets(websocket_url: str, *, timeout: float = 3.0) -> list[dict[str, Any]]:
    response = _cdp_command(websocket_url, 'Target.getTargets', timeout=timeout)
    target_infos = (((response.get('result') or {}).get('targetInfos')) or [])
    return [_normalized_target(item) for item in target_infos if isinstance(item, dict)]


def watch_browser_targets(websocket_url: str, *, extension_id: str | None, duration: float, timeout: float = 3.0) -> dict[str, Any]:
    report: dict[str, Any] = {
        'requested_seconds': max(0.0, float(duration)),
        'events': [],
        'event_count': 0,
        'observed_targets': [],
        'observed_target_count': 0,
        'destroyed_target_ids': [],
        'extension_targets': [],
        'extension_pages': [],
        'service_worker_seen': False,
    }
    if duration <= 0:
        return report

    observed_by_id: dict[str, dict[str, Any]] = {}
    destroyed_ids: list[str] = []

    def record_event(message: dict[str, Any]) -> None:
        method = message.get('method')
        params = message.get('params') if isinstance(message.get('params'), dict) else {}
        target_info = None
        if method in {'Target.targetCreated', 'Target.targetInfoChanged', 'Target.attachedToTarget'}:
            payload = params.get('targetInfo')
            if isinstance(payload, dict):
                target_info = _normalized_target(payload)
                target_id = target_info.get('id')
                if isinstance(target_id, str) and target_id:
                    observed_by_id[target_id] = target_info
        elif method == 'Target.targetDestroyed':
            target_id = params.get('targetId')
            if isinstance(target_id, str) and target_id:
                destroyed_ids.append(target_id)
        event_entry: dict[str, Any] = {'method': method}
        if target_info is not None:
            event_entry['target'] = target_info
        elif method == 'Target.targetDestroyed':
            event_entry['targetId'] = params.get('targetId')
        report['events'].append(event_entry)

    session_timeout = max(float(timeout), 3.0)
    ws = create_connection(websocket_url, timeout=session_timeout, origin='http://127.0.0.1')
    try:
        enable_id = 1
        ws.send(json.dumps({
            'id': enable_id,
            'method': 'Target.setDiscoverTargets',
            'params': {
                'discover': True,
                'filter': _target_filter_default(),
            },
        }))
        deadline = time.time() + session_timeout
        _recv_matching_response(ws, response_id=enable_id, deadline=deadline, event_handler=record_event)

        watch_deadline = time.time() + duration
        while time.time() < watch_deadline:
            remaining = max(0.05, min(session_timeout, watch_deadline - time.time()))
            try:
                ws.settimeout(remaining)
            except Exception:  # noqa: BLE001
                pass
            try:
                raw = ws.recv()
            except (TimeoutError, socket.timeout, WebSocketTimeoutException):
                continue
            record_event(json.loads(raw))

        disable_id = 2
        ws.send(json.dumps({
            'id': disable_id,
            'method': 'Target.setDiscoverTargets',
            'params': {'discover': False},
        }))
        try:
            _recv_matching_response(ws, response_id=disable_id, deadline=time.time() + min(session_timeout, 1.5), event_handler=record_event)
        except Exception:  # noqa: BLE001
            pass
    finally:
        ws.close()

    report['event_count'] = len(report['events'])
    report['observed_targets'] = list(observed_by_id.values())
    report['observed_target_count'] = len(report['observed_targets'])
    report['destroyed_target_ids'] = destroyed_ids
    extension_targets, extension_pages, service_worker_seen = _extension_target_subset(report['observed_targets'], extension_id)
    report['extension_targets'] = extension_targets
    report['extension_pages'] = extension_pages
    report['service_worker_seen'] = service_worker_seen
    return report


def attach_browser_targets(websocket_url: str, *, extension_id: str | None, duration: float, timeout: float = 3.0) -> dict[str, Any]:
    report: dict[str, Any] = {
        'requested_seconds': max(0.0, float(duration)),
        'events': [],
        'event_count': 0,
        'attached_targets': [],
        'attached_target_count': 0,
        'detached_session_ids': [],
        'extension_targets': [],
        'extension_pages': [],
        'service_worker_seen': False,
        'session_evaluations': [],
        'session_evaluation_count': 0,
        'runtime_ids': [],
        'runtime_id_matches_extension': False,
        'errors': [],
    }
    if duration <= 0:
        return report

    attached_by_session: dict[str, dict[str, Any]] = {}
    detached_sessions: list[str] = []
    session_evaluations: list[dict[str, Any]] = []
    evaluated_sessions: set[str] = set()
    pending_sessions: list[str] = []
    next_id = 0

    def next_message_id() -> int:
        nonlocal next_id
        next_id += 1
        return next_id

    def record_event(message: dict[str, Any]) -> None:
        method = message.get('method')
        params = message.get('params') if isinstance(message.get('params'), dict) else {}
        event_entry: dict[str, Any] = {'method': method}
        if method == 'Target.attachedToTarget':
            payload = params.get('targetInfo')
            if isinstance(payload, dict):
                target = _normalized_target(payload)
                session_id = params.get('sessionId')
                if isinstance(session_id, str) and session_id:
                    target['sessionId'] = session_id
                    target['waitingForDebugger'] = bool(params.get('waitingForDebugger'))
                    attached_by_session[session_id] = target
                    pending_sessions.append(session_id)
                event_entry['target'] = target
        elif method in {'Target.targetCreated', 'Target.targetInfoChanged'}:
            payload = params.get('targetInfo')
            if isinstance(payload, dict):
                event_entry['target'] = _normalized_target(payload)
        elif method == 'Target.detachedFromTarget':
            session_id = params.get('sessionId')
            if isinstance(session_id, str) and session_id:
                detached_sessions.append(session_id)
            event_entry['sessionId'] = session_id
            if 'targetId' in params:
                event_entry['targetId'] = params.get('targetId')
        report['events'].append(event_entry)

    def send_command(ws: Any, method: str, params: dict[str, Any] | None = None, *, session_id: str | None = None, response_timeout: float | None = None) -> dict[str, Any]:
        message_id = next_message_id()
        payload: dict[str, Any] = {
            'id': message_id,
            'method': method,
            'params': params or {},
        }
        if session_id:
            payload['sessionId'] = session_id
        ws.send(json.dumps(payload))
        return _recv_matching_response(
            ws,
            response_id=message_id,
            deadline=time.time() + (response_timeout if response_timeout is not None else session_timeout),
            event_handler=record_event,
        )

    def evaluate_pending_sessions(ws: Any) -> None:
        while pending_sessions:
            session_id = pending_sessions.pop(0)
            if session_id in evaluated_sessions:
                continue
            target = attached_by_session.get(session_id) or {}
            if target.get('type') not in {'page', 'service_worker'}:
                continue
            try:
                response = send_command(
                    ws,
                    'Runtime.evaluate',
                    {
                        'expression': EXTENSION_ATTACH_EVAL,
                        'returnByValue': True,
                        'awaitPromise': True,
                    },
                    session_id=session_id,
                    response_timeout=max(1.5, min(session_timeout, 2.5)),
                )
                value = ((response.get('result') or {}).get('result') or {}).get('value')
                entry = {
                    'sessionId': session_id,
                    'target': target,
                    'result': value if isinstance(value, dict) else None,
                }
                session_evaluations.append(entry)
                evaluated_sessions.add(session_id)
            except Exception as exc:  # noqa: BLE001
                report['errors'].append(f'session {session_id} evaluate failed: {exc}')
                evaluated_sessions.add(session_id)

    session_timeout = max(float(timeout), 3.0)
    ws = create_connection(websocket_url, timeout=session_timeout, origin='http://127.0.0.1')
    try:
        send_command(
            ws,
            'Target.setAutoAttach',
            {
                'autoAttach': True,
                'waitForDebuggerOnStart': False,
                'flatten': True,
                'filter': ATTACH_FILTER,
            },
        )
        evaluate_pending_sessions(ws)

        watch_deadline = time.time() + duration
        while time.time() < watch_deadline:
            remaining = max(0.05, min(session_timeout, watch_deadline - time.time()))
            try:
                ws.settimeout(remaining)
            except Exception:  # noqa: BLE001
                pass
            try:
                raw = ws.recv()
            except (TimeoutError, socket.timeout, WebSocketTimeoutException):
                evaluate_pending_sessions(ws)
                continue
            record_event(json.loads(raw))
            evaluate_pending_sessions(ws)

        try:
            send_command(ws, 'Target.setAutoAttach', {'autoAttach': False, 'waitForDebuggerOnStart': False, 'flatten': True}, response_timeout=min(session_timeout, 1.5))
        except Exception as exc:  # noqa: BLE001
            report['errors'].append(f'failed to disable auto-attach: {exc}')
    finally:
        ws.close()

    report['event_count'] = len(report['events'])
    report['attached_targets'] = list(attached_by_session.values())
    report['attached_target_count'] = len(report['attached_targets'])
    report['detached_session_ids'] = detached_sessions
    extension_targets, extension_pages, service_worker_seen = _extension_target_subset(report['attached_targets'], extension_id)
    report['extension_targets'] = extension_targets
    report['extension_pages'] = extension_pages
    report['service_worker_seen'] = service_worker_seen
    report['session_evaluations'] = session_evaluations
    report['session_evaluation_count'] = len(session_evaluations)
    runtime_ids = sorted({entry.get('result', {}).get('runtimeId') for entry in session_evaluations if isinstance(entry.get('result'), dict) and isinstance(entry.get('result', {}).get('runtimeId'), str) and entry.get('result', {}).get('runtimeId')})
    report['runtime_ids'] = runtime_ids
    report['runtime_id_matches_extension'] = bool(extension_id) and extension_id in runtime_ids
    return report


def inspect_cdp(*, port: int, extension_id: str | None, timeout: float, wait: float, watch: float = 0.0, attach: float = 0.0) -> dict[str, Any]:
    report: dict[str, Any] = {
        'port': port,
        'available': False,
        'browser_version': None,
        'browser_websocket_url': None,
        'targets': [],
        'target_count': 0,
        'extension_id': extension_id,
        'extension_targets': [],
        'service_worker_seen': False,
        'page_targets': [],
        'extension_pages': [],
        'browser_targets': [],
        'browser_target_count': 0,
        'browser_extension_targets': [],
        'browser_extension_pages': [],
        'browser_service_worker_seen': False,
        'browser_target_watch': None,
        'browser_watch_extension_targets': [],
        'browser_watch_extension_pages': [],
        'browser_watch_service_worker_seen': False,
        'browser_target_attach': None,
        'browser_attach_extension_targets': [],
        'browser_attach_extension_pages': [],
        'browser_attach_service_worker_seen': False,
        'browser_attach_runtime_ids': [],
        'browser_attach_runtime_id_matches_extension': False,
        'browser_attach_session_evaluations': [],
        'extension_visible': False,
    }
    deadline = time.time() + wait
    while True:
        try:
            version = fetch_json(f'http://127.0.0.1:{port}/json/version', timeout)
            targets = fetch_json(f'http://127.0.0.1:{port}/json/list', timeout)
            report['available'] = True
            report['browser_version'] = version.get('Browser')
            report['browser_websocket_url'] = version.get('webSocketDebuggerUrl')
            report['targets'] = [_normalized_target(item) for item in targets if isinstance(item, dict)]
            report['target_count'] = len(report['targets'])
            report['page_targets'] = [item for item in report['targets'] if item.get('type') == 'page']
            extension_targets, extension_pages, service_worker_seen = _extension_target_subset(report['targets'], extension_id)
            report['extension_targets'] = extension_targets
            report['extension_pages'] = extension_pages
            report['service_worker_seen'] = service_worker_seen
            browser_ws = report.get('browser_websocket_url')
            if isinstance(browser_ws, str) and browser_ws:
                try:
                    report['browser_targets'] = fetch_browser_targets(browser_ws, timeout=timeout)
                    report['browser_target_count'] = len(report['browser_targets'])
                    browser_extension_targets, browser_extension_pages, browser_service_worker_seen = _extension_target_subset(report['browser_targets'], extension_id)
                    report['browser_extension_targets'] = browser_extension_targets
                    report['browser_extension_pages'] = browser_extension_pages
                    report['browser_service_worker_seen'] = browser_service_worker_seen
                    if watch > 0:
                        try:
                            watch_report = watch_browser_targets(browser_ws, extension_id=extension_id, duration=watch, timeout=timeout)
                            report['browser_target_watch'] = watch_report
                            report['browser_watch_extension_targets'] = watch_report.get('extension_targets') or []
                            report['browser_watch_extension_pages'] = watch_report.get('extension_pages') or []
                            report['browser_watch_service_worker_seen'] = bool(watch_report.get('service_worker_seen'))
                        except Exception as exc:  # noqa: BLE001
                            report['browser_target_watch'] = {'requested_seconds': watch, 'error': str(exc)}
                    if attach > 0:
                        try:
                            attach_report = attach_browser_targets(browser_ws, extension_id=extension_id, duration=attach, timeout=timeout)
                            report['browser_target_attach'] = attach_report
                            report['browser_attach_extension_targets'] = attach_report.get('extension_targets') or []
                            report['browser_attach_extension_pages'] = attach_report.get('extension_pages') or []
                            report['browser_attach_service_worker_seen'] = bool(attach_report.get('service_worker_seen'))
                            report['browser_attach_runtime_ids'] = attach_report.get('runtime_ids') or []
                            report['browser_attach_runtime_id_matches_extension'] = bool(attach_report.get('runtime_id_matches_extension'))
                            report['browser_attach_session_evaluations'] = attach_report.get('session_evaluations') or []
                        except Exception as exc:  # noqa: BLE001
                            report['browser_target_attach'] = {'requested_seconds': attach, 'error': str(exc)}
                except Exception as exc:  # noqa: BLE001
                    report['browser_target_error'] = str(exc)
            report['extension_visible'] = bool(
                report['extension_pages']
                or report['service_worker_seen']
                or report['browser_extension_pages']
                or report['browser_service_worker_seen']
                or report['browser_watch_extension_pages']
                or report['browser_watch_service_worker_seen']
                or report['browser_attach_extension_pages']
                or report['browser_attach_service_worker_seen']
            )
            return report
        except Exception as exc:  # noqa: BLE001
            report['last_error'] = str(exc)
            if time.time() >= deadline:
                return report
            time.sleep(0.2)
