from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import uuid
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .overflow_artifacts import apply_overflow_prune, plan_overflow_prune, summarize_overflow_inventory

JsonDict = dict[str, Any]
DEFAULT_TIMEOUT = 15.0


def default_home() -> Path:
    return Path(os.environ.get("GLASSTTY_HOME", Path.home() / ".local" / "share" / "glasstty"))


def socket_path() -> Path:
    return default_home() / "run" / "daemon.sock"


def fixtures_dir() -> Path:
    return default_home() / "fixtures"


def state_root() -> Path:
    return default_home() / "state"


def latest_dir() -> Path:
    return state_root() / "latest"


def read_json_file(path: Path) -> JsonDict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def latest_oversized_host_message() -> JsonDict | None:
    return read_json_file(latest_dir() / "oversized-host-outbound.json")


def _json_excerpt(value: object, *, limit: int = 600) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if len(raw) <= limit:
        return raw
    keep = max(0, limit - 3)
    return raw[:keep] + '...'


def build_overflow_report(*, artifact: str | None = None, include_message: bool = False) -> JsonDict:
    latest = latest_oversized_host_message()
    inventory = summarize_overflow_inventory(default_home())
    selected_path = Path(artifact).expanduser() if artifact else None
    if selected_path is None and isinstance(latest, dict):
        artifact_path = latest.get('artifact_path')
        if isinstance(artifact_path, str) and artifact_path.strip():
            selected_path = Path(artifact_path).expanduser()
    report: JsonDict = {
        'state_root': str(state_root()),
        'latest_summary': latest,
        'artifact_path': str(selected_path) if selected_path else None,
        'artifact_exists': bool(selected_path and selected_path.exists()),
        'inventory': inventory,
    }
    if selected_path is None:
        return report
    artifact_payload = read_json_file(selected_path) if selected_path.exists() else None
    report['artifact_summary'] = {
        'path': str(selected_path),
        'exists': bool(selected_path.exists()),
        'selected_from_latest': bool(isinstance(latest, dict) and latest.get('artifact_path') == str(selected_path)),
    }
    if not isinstance(artifact_payload, dict):
        return report
    message = artifact_payload.get('message') if isinstance(artifact_payload.get('message'), dict) else {}
    payload = message.get('payload') if isinstance(message.get('payload'), dict) else None
    payload_keys = sorted(payload.keys()) if isinstance(payload, dict) else None
    report['artifact_summary'].update({
        'kind': artifact_payload.get('kind'),
        'captured_at': artifact_payload.get('captured_at'),
        'budget': artifact_payload.get('budget'),
        'message_type': message.get('type'),
        'request_id': message.get('request_id'),
        'tab_id': message.get('tab_id'),
        'message_keys': sorted(message.keys()),
        'payload_keys': payload_keys,
        'message_excerpt': _json_excerpt(message),
    })
    if include_message:
        report['artifact_message'] = message
    return report


def build_overflow_prune_report(*, keep: int = 10, max_age_days: float | None = None, max_disk_bytes: int | None = None, apply: bool = False) -> JsonDict:
    plan = plan_overflow_prune(home=default_home(), keep=keep, max_age_days=max_age_days, max_disk_bytes=max_disk_bytes)
    report: JsonDict = {'plan': plan}
    if apply:
        report['applied'] = apply_overflow_prune(plan)
        report['post_inventory'] = summarize_overflow_inventory(default_home())
    return report


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_envelope(message_type: str, payload: JsonDict, *, tab_id: int | None = None) -> JsonDict:
    envelope: JsonDict = {
        "version": "0.1",
        "request_id": str(uuid.uuid4()),
        "type": message_type,
        "timestamp": iso_now(),
        "payload": payload,
    }
    if tab_id is not None:
        envelope["tab_id"] = tab_id
    return envelope


class SocketClient:
    def __init__(self, path: Path, timeout: float | None = None):
        self.path = path
        self.timeout = timeout
        self.sock: socket.socket | None = None
        self.file = None

    def __enter__(self) -> "SocketClient":
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if self.timeout is not None:
            self.sock.settimeout(self.timeout)
        self.sock.connect(os.fspath(self.path))
        self.file = self.sock.makefile("r", encoding="utf-8")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.file is not None:
            self.file.close()
        if self.sock is not None:
            self.sock.close()

    def send(self, message: JsonDict) -> None:
        assert self.sock is not None
        self.sock.sendall((json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8"))

    def recv(self) -> JsonDict:
        assert self.file is not None
        try:
            line = self.file.readline()
        except TimeoutError as exc:
            raise RuntimeError(f"broker socket timed out after {self.timeout}s") from exc
        except OSError as exc:
            raise RuntimeError(f"broker socket error: {exc}") from exc
        if not line:
            raise RuntimeError("broker socket closed")
        return json.loads(line)


def require_socket() -> Path:
    path = socket_path()
    if not path.exists():
        raise SystemExit(f"broker socket not found at {path}; start Chromium with the GlassTTY extension and native host first")
    return path


def emit_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False))


def emit_json_stderr(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False), file=sys.stderr)


def extract_text_from_browser_event(message: JsonDict) -> str | None:
    payload = message.get("message", {}).get("payload")
    if not isinstance(payload, dict):
        return None
    text = payload.get("text")
    return text if isinstance(text, str) else None


def bridge_payload_from_browser_event(message: JsonDict) -> JsonDict:
    payload = message.get("message", {}).get("payload")
    return payload if isinstance(payload, dict) else {}


def extract_supported_tabs_from_browser_event(message: JsonDict) -> list[JsonDict]:
    payload = bridge_payload_from_browser_event(message)
    tabs = payload.get("supportedTabs")
    if isinstance(tabs, list):
        return [tab for tab in tabs if isinstance(tab, dict)]
    return []


def extract_target_tab_from_browser_event(message: JsonDict, tab_id: int | None = None) -> JsonDict | None:
    tabs = extract_supported_tabs_from_browser_event(message)
    if tab_id is not None:
        for tab in tabs:
            if tab.get("tabId") == tab_id:
                return tab
        return None
    payload = bridge_payload_from_browser_event(message)
    selected_id = payload.get("selectedTargetTabId")
    if isinstance(selected_id, int):
        for tab in tabs:
            if tab.get("tabId") == selected_id:
                return tab
    target_tab = payload.get("targetTab")
    if isinstance(target_tab, dict):
        return target_tab
    if len(tabs) == 1:
        return tabs[0]
    return None


def extract_receivers_from_browser_event(message: JsonDict, tab_id: int | None = None) -> list[JsonDict]:
    if tab_id is None:
        rows: list[JsonDict] = []
        for tab in extract_supported_tabs_from_browser_event(message):
            if not isinstance(tab, dict):
                continue
            receivers = tab.get("receivers")
            if not isinstance(receivers, list):
                continue
            for receiver in receivers:
                if isinstance(receiver, dict):
                    rows.append({"tabId": tab.get("tabId"), **receiver})
        return rows
    target = extract_target_tab_from_browser_event(message, tab_id)
    if not isinstance(target, dict):
        return []
    receivers = target.get("receivers")
    if not isinstance(receivers, list):
        return []
    rows = []
    for receiver in receivers:
        if isinstance(receiver, dict):
            rows.append({"tabId": target.get("tabId"), **receiver})
    return rows


def receiver_key(receiver: JsonDict) -> str:
    document_id = receiver.get("documentId")
    if isinstance(document_id, str) and document_id.strip():
        return f"doc:{document_id.strip()}"
    frame_id = receiver.get("frameId")
    if isinstance(frame_id, int):
        return f"frame:{frame_id}"
    return ""


def _url_hostname(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return urllib.parse.urlparse(value.strip()).hostname
    except Exception:
        return None


def receiver_frame_depth(receiver: JsonDict) -> int | None:
    depth = receiver.get('frameDepth')
    if isinstance(depth, int):
        return depth
    frame_path_frame_ids = receiver.get('framePathFrameIds')
    if isinstance(frame_path_frame_ids, list):
        normalized = [value for value in frame_path_frame_ids if isinstance(value, int)]
        if normalized:
            return max(0, len(normalized) - 1)
    return None


def receiver_document_lifecycle(receiver: JsonDict) -> str | None:
    lifecycle = receiver.get('documentLifecycle')
    if isinstance(lifecycle, str) and lifecycle.strip():
        return lifecycle.strip()
    return None


def receiver_last_seen_at(receiver: JsonDict) -> str | None:
    last_seen = receiver.get('lastSeenAt')
    if isinstance(last_seen, str) and last_seen.strip():
        return last_seen.strip()
    return None


def receiver_is_lifecycle_preferred(receiver: JsonDict) -> bool:
    lifecycle = receiver_document_lifecycle(receiver)
    return lifecycle in {None, 'active'}


def receiver_is_outermost(receiver: JsonDict) -> bool:
    frame_type = receiver.get('frameType')
    if isinstance(frame_type, str) and frame_type.strip() == 'outermost_frame':
        return True
    depth = receiver_frame_depth(receiver)
    if isinstance(depth, int):
        return depth <= 0
    frame_path_frame_ids = receiver.get('framePathFrameIds')
    if isinstance(frame_path_frame_ids, list):
        normalized = [value for value in frame_path_frame_ids if isinstance(value, int)]
        if normalized:
            return len(normalized) == 1
    parent_frame_id = receiver.get('parentFrameId')
    if isinstance(parent_frame_id, int):
        return parent_frame_id < 0
    frame_id = receiver.get('frameId')
    return isinstance(frame_id, int) and frame_id == 0


def receiver_is_active_outermost(receiver: JsonDict) -> bool:
    return receiver_is_outermost(receiver) and receiver_is_lifecycle_preferred(receiver)


def receiver_frame_path_label(receiver: JsonDict) -> str | None:
    explicit = receiver.get('framePathLabel')
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    frame_path_hosts = receiver.get('framePathHosts')
    if isinstance(frame_path_hosts, list):
        normalized = [value.strip() for value in frame_path_hosts if isinstance(value, str) and value.strip()]
        if normalized:
            return ' → '.join(normalized)
    host = _url_hostname(receiver.get('frameUrl')) or _url_hostname(receiver.get('frameOrigin'))
    frame_id = receiver.get('frameId')
    if host and not receiver_is_outermost(receiver):
        return f'top-frame → {host}'
    if host:
        return host
    if isinstance(frame_id, int):
        return 'top-frame' if receiver_is_outermost(receiver) else f'top-frame → frame:{frame_id}'
    return None


def receiver_label(receiver: JsonDict) -> str:
    parts: list[str] = []
    frame_id = receiver.get("frameId")
    if isinstance(frame_id, int):
        parts.append("top-frame" if receiver_is_outermost(receiver) else f"frame:{frame_id}")
    document_id = receiver.get("documentId")
    if isinstance(document_id, str) and document_id.strip():
        parts.append(f"doc:{document_id.strip()[:8]}")
    frame_type = receiver.get("frameType")
    if isinstance(frame_type, str) and frame_type.strip() and frame_type.strip() != 'outermost_frame':
        parts.append(frame_type.strip())
    host = _url_hostname(receiver.get('frameUrl')) or _url_hostname(receiver.get('frameOrigin'))
    if host:
        parts.append(host)
    frame_path_label = receiver_frame_path_label(receiver)
    if frame_path_label and frame_path_label not in parts and frame_path_label != 'top-frame':
        parts.append(frame_path_label)
    depth = receiver_frame_depth(receiver)
    if isinstance(depth, int) and depth > 0:
        parts.append(f'depth:{depth}')
    ready = receiver.get("receiverReady")
    if ready is True:
        parts.append("ready")
    elif ready is False:
        parts.append("observed")
    lifecycle = receiver.get("documentLifecycle")
    if isinstance(lifecycle, str) and lifecycle.strip():
        parts.append(lifecycle.strip())
    return " · ".join(parts) or "receiver"


def receiver_sort_key(receiver: JsonDict) -> tuple[int, int, int, int, int, str]:
    lifecycle_preferred = 1 if receiver_is_lifecycle_preferred(receiver) else 0
    outermost = 1 if receiver_is_outermost(receiver) else 0
    ready = 1 if receiver.get('receiverReady') is True else 0
    depth = receiver_frame_depth(receiver)
    normalized_depth = depth if isinstance(depth, int) else sys.maxsize
    last_seen = receiver_last_seen_at(receiver) or ''
    inverted_last_seen = ''.join(chr(0x10FFFF - ord(char)) for char in last_seen)
    missing_last_seen = 1 if not last_seen else 0
    return (-lifecycle_preferred, -outermost, -ready, normalized_depth, missing_last_seen, inverted_last_seen)


def sort_receivers(rows: list[JsonDict]) -> list[JsonDict]:
    return sorted(rows, key=receiver_sort_key)


def describe_receiver_resolution(receiver: JsonDict, *, rank: int | None = None) -> JsonDict:
    depth = receiver_frame_depth(receiver)
    lifecycle = receiver_document_lifecycle(receiver)
    ready = receiver.get('receiverReady') is True
    summary: JsonDict = {
        'receiverKey': receiver_key(receiver),
        'receiverLabel': receiver_label(receiver),
        'lifecyclePreferred': receiver_is_lifecycle_preferred(receiver),
        'activeOutermost': receiver_is_active_outermost(receiver),
        'outermost': receiver_is_outermost(receiver),
        'ready': ready,
        'frameDepth': depth,
        'lastSeenAt': receiver_last_seen_at(receiver),
        'documentLifecycle': lifecycle,
        'rankingVector': {
            'lifecyclePreferred': receiver_is_lifecycle_preferred(receiver),
            'outermost': receiver_is_outermost(receiver),
            'ready': ready,
            'frameDepth': depth,
            'lastSeenAt': receiver_last_seen_at(receiver),
        },
        'reasons': [
            'lifecycle=active_or_unknown' if receiver_is_lifecycle_preferred(receiver) else f'lifecycle={lifecycle or "unknown"}',
            'frame=outermost' if receiver_is_outermost(receiver) else 'frame=subframe',
            'receiver=ready' if ready else 'receiver=observed_only',
            f'frameDepth={depth}' if isinstance(depth, int) else 'frameDepth=unknown',
            f'lastSeenAt={receiver_last_seen_at(receiver)}' if receiver_last_seen_at(receiver) else 'lastSeenAt=unknown',
        ],
    }
    if rank is not None:
        summary['rank'] = rank
    return summary


def describe_matching_receivers(rows: list[JsonDict]) -> list[JsonDict]:
    return [describe_receiver_resolution(receiver, rank=index) for index, receiver in enumerate(sort_receivers(rows), start=1)]


def receiver_matches(
    receiver: JsonDict,
    *,
    receiver_key_filter: str | None = None,
    frame_id: int | None = None,
    document_id: str | None = None,
    url_contains: str | None = None,
    frame_type: str | None = None,
    frame_host_contains: str | None = None,
    frame_path_contains: str | None = None,
    frame_depth: int | None = None,
    top_frame: bool = False,
    active_outermost: bool = False,
    ready_only: bool = False,
    document_lifecycle: str | None = None,
) -> bool:
    if receiver_key_filter and receiver_key(receiver) != receiver_key_filter:
        return False
    if frame_id is not None and receiver.get('frameId') != frame_id:
        return False
    if document_id is not None and receiver.get('documentId') != document_id:
        return False
    if top_frame and not receiver_is_outermost(receiver):
        return False
    if active_outermost and not receiver_is_active_outermost(receiver):
        return False
    if ready_only and receiver.get('receiverReady') is not True:
        return False
    if document_lifecycle is not None and receiver_document_lifecycle(receiver) != document_lifecycle:
        return False
    if frame_type is not None and receiver.get('frameType') != frame_type:
        return False
    if frame_depth is not None and receiver_frame_depth(receiver) != frame_depth:
        return False
    if url_contains:
        frame_url = receiver.get('frameUrl')
        frame_path_urls = receiver.get('framePathUrls')
        haystacks: list[str] = []
        if isinstance(frame_url, str):
            haystacks.append(frame_url)
        if isinstance(frame_path_urls, list):
            haystacks.extend(value for value in frame_path_urls if isinstance(value, str))
        if not haystacks or all(url_contains.lower() not in value.lower() for value in haystacks):
            return False
    if frame_host_contains:
        needle = frame_host_contains.lower()
        host_values = [_url_hostname(receiver.get('frameUrl')), _url_hostname(receiver.get('frameOrigin'))]
        frame_path_hosts = receiver.get('framePathHosts')
        if isinstance(frame_path_hosts, list):
            host_values.extend(value for value in frame_path_hosts if isinstance(value, str))
        if all(not isinstance(value, str) or needle not in value.lower() for value in host_values):
            return False
    if frame_path_contains:
        needle = frame_path_contains.lower()
        frame_path_label = receiver_frame_path_label(receiver)
        frame_path_urls = receiver.get('framePathUrls')
        haystacks: list[str] = []
        if isinstance(frame_path_label, str):
            haystacks.append(frame_path_label)
        if isinstance(frame_path_urls, list):
            haystacks.extend(value for value in frame_path_urls if isinstance(value, str))
        if all(needle not in value.lower() for value in haystacks):
            return False
    return True


def select_matching_receivers(
    rows: list[JsonDict],
    *,
    receiver_key_filter: str | None = None,
    frame_id: int | None = None,
    document_id: str | None = None,
    url_contains: str | None = None,
    frame_type: str | None = None,
    frame_host_contains: str | None = None,
    frame_path_contains: str | None = None,
    frame_depth: int | None = None,
    top_frame: bool = False,
    active_outermost: bool = False,
    ready_only: bool = False,
    document_lifecycle: str | None = None,
) -> list[JsonDict]:
    return sort_receivers([
        row for row in rows
        if receiver_matches(
            row,
            receiver_key_filter=receiver_key_filter,
            frame_id=frame_id,
            document_id=document_id,
            url_contains=url_contains,
            frame_type=frame_type,
            frame_host_contains=frame_host_contains,
            frame_path_contains=frame_path_contains,
            frame_depth=frame_depth,
            top_frame=top_frame,
            active_outermost=active_outermost,
            ready_only=ready_only,
            document_lifecycle=document_lifecycle,
        )
    ])


def print_supported_tabs(message: JsonDict) -> None:
    tabs = extract_supported_tabs_from_browser_event(message)
    for tab in tabs:
        print(f"{tab.get('tabId')}\t{tab.get('adapter', '')}\t{tab.get('title', '')}\t{tab.get('url', '')}")


def print_receivers(message: JsonDict, *, tab_id: int | None = None) -> None:
    tabs = extract_supported_tabs_from_browser_event(message)
    wanted = {tab_id} if tab_id is not None else {tab.get('tabId') for tab in tabs if isinstance(tab.get('tabId'), int)}
    for tab in tabs:
        current_tab_id = tab.get('tabId')
        if current_tab_id not in wanted:
            continue
        selected_key = tab.get('selectedReceiverKey')
        override_key = tab.get('receiverOverrideKey')
        receivers = tab.get('receivers')
        if not isinstance(receivers, list):
            continue
        for receiver in receivers:
            if not isinstance(receiver, dict):
                continue
            key = receiver_key(receiver)
            print(
                f"{current_tab_id}\t{key}\t{receiver_label(receiver)}\t{receiver.get('adapter', '')}\t"
                f"{receiver.get('frameId', '')}\t{receiver.get('documentId', '')}\t{receiver.get('documentLifecycle', '')}\t"
                f"{receiver.get('frameType', '')}\t{receiver.get('parentFrameId', '')}\t{receiver.get('parentDocumentId', '')}\t"
                f"{receiver.get('frameOrigin', '')}\t{receiver.get('frameUrl', '')}\t"
                f"{receiver.get('receiverReady', '')}\t{receiver.get('lastSeenAt', '')}\t"
                f"{'selected' if key and key == selected_key else ''}\t{'override' if key and key == override_key else ''}"
            )


def slugify(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value.lower()).strip("-") or "fixture"


def fixture_path_from_response(message: JsonDict, output_dir: Path | None = None) -> Path:
    payload = message.get("message", {}).get("payload", {})
    adapter = slugify(str(payload.get("adapter") or "unknown"))
    title = slugify(str(payload.get("title") or "page"))[:40]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = output_dir or fixtures_dir()
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{timestamp}-{adapter}-{title}.json"


def cmd_ping(args: argparse.Namespace) -> int:
    path = require_socket()
    try:
        with SocketClient(path, timeout=args.timeout) as client:
            hello = client.recv()
            if hello.get("stream") != "server" or hello.get("type") != "hello":
                raise RuntimeError(f"expected broker hello, received {_json_excerpt(hello)}")

            client.send({"op": "ping"})
            pong = client.recv()
            if pong.get("stream") != "server" or pong.get("type") != "pong":
                raise RuntimeError(f"expected broker pong, received {_json_excerpt(pong)}")
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"broker ping failed at {path}: {exc}") from exc

    broker = pong.get("payload")
    if not isinstance(broker, dict) or broker.get("ok") is not True:
        raise SystemExit(f"broker ping returned an unhealthy status: {_json_excerpt(broker)}")

    emit_json({
        "ok": True,
        "tool": "glassttyd",
        "mode": "broker-round-trip",
        "socket_path": os.fspath(path),
        "broker": broker,
    })
    return 0


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _active_surface_contract_path() -> Path:
    latest = _project_root() / 'validation' / 'latest'
    paths = sorted(
        latest.glob('chatgpt-live-surface-contract-rev*-*.json'),
        key=lambda path: path.name,
        reverse=True,
    )
    return paths[0] if paths else latest / 'chatgpt-live-surface-contract-rev0338-2026.06.13.json'


def _load_script_module(module_name: str):
    scripts = _project_root() / 'scripts'
    if os.fspath(scripts) not in sys.path:
        sys.path.insert(0, os.fspath(scripts))
    return __import__(module_name)


def cmd_doctor(args: argparse.Namespace) -> int:
    root = _project_root()
    manifest = read_json_file(root / 'extension' / 'manifest.json') or {}
    package_json = read_json_file(root / 'extension' / 'package.json') or {}
    contract_path = _active_surface_contract_path()
    contract = read_json_file(contract_path)
    report: JsonDict = {
        'ok': True,
        'tool': 'glassttyd-doctor',
        'project_root': os.fspath(root),
        'home': os.fspath(default_home()),
        'socket_path': os.fspath(socket_path()),
        'socket_exists': socket_path().exists(),
        'chatgpt_only': manifest.get('host_permissions') == ['https://chatgpt.com/*'],
        'extension_version': package_json.get('version'),
        'host_permissions': manifest.get('host_permissions'),
        'required_files': {
            'extension_manifest': (root / 'extension' / 'manifest.json').exists(),
            'chatgpt_adapter': (root / 'extension' / 'src' / 'adapters' / 'chatgpt.ts').exists(),
            'surface_oracle_userscript': (root / 'tools' / 'chatgpt-surface-oracle.user.js').exists(),
            'surface_contract': isinstance(contract, dict),
            'native_host_template': (root / 'native-host' / 'com.glasstty.bridge.template.json').exists(),
        },
        'surface_contract': {
            'path': os.fspath(contract_path),
            'version': contract.get('contract_version') if isinstance(contract, dict) else None,
            'strict_send_selector': _get_contract_path(contract, 'required.strict_send.selector') if isinstance(contract, dict) else None,
            'prompt_selector': _get_contract_path(contract, 'required.prompt_selector') if isinstance(contract, dict) else None,
        },
    }
    report['ok'] = bool(
        report['chatgpt_only']
        and all(report['required_files'].values())
    )
    if args.pretty:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        emit_json(report)
    return 0 if report['ok'] else 1


def _get_contract_path(value: JsonDict, path: str) -> Any:
    current: Any = value
    for part in path.split('.'):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def cmd_surface_audit(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_surface_report_audit')
    payload = mod.extract_json_object(mod.read_input(args.input))
    audit = mod.audit_surface(payload)
    print(json.dumps(audit, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if audit.get('verdict') == 'adapter-ready-surface' else 2


def cmd_surface_contract_build(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_surface_contract')
    payload = mod.read_payload(args.report)
    contract = mod.build_contract(payload, source_path=None if args.report == '-' else args.report)
    if args.out:
        Path(args.out).write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(contract, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0


def cmd_surface_contract_check(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_surface_contract')
    payload = mod.read_payload(args.report)
    contract = mod.read_json(args.contract)
    result = mod.check_contract(payload, contract)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if result.get('verdict') == 'surface-contract-ok' else 2




def cmd_proof_extension_readiness(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_extension_readiness')
    report = mod.check_extension_readiness(
        _project_root(),
        require_build=args.require_build,
        summary_path=Path(args.summary_out) if args.summary_out else None,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2

def cmd_proof_rehearse(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_rehearsal')
    summary = mod.run_rehearsal(
        surface_report=Path(args.surface_report) if args.surface_report else None,
        contract_path=Path(args.contract) if args.contract else None,
        out=Path(args.out),
        evaluation_out=Path(args.evaluation_out),
        strict_surface=args.strict_surface,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if summary.get('ok') else 2


def cmd_proof_preflight(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_preflight')
    report = mod.run_preflight(
        surface_report=Path(args.surface_report) if args.surface_report else None,
        contract_path=Path(args.contract) if args.contract else None,
        fixture_path=Path(args.fixture) if args.fixture else None,
        out=Path(args.out),
        rehearsal_out=Path(args.rehearsal_out),
        evaluation_out=Path(args.evaluation_out),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2



def cmd_proof_export_pack(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_pack_exporter')
    summary = mod.export_pack(
        Path(args.input),
        Path(args.pack_dir),
        summary_path=Path(args.summary_out),
        clean=args.clean,
        allow_placeholder_screenshot=True if args.allow_placeholder_screenshot else (False if args.no_placeholder_screenshot else None),
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    if args.require_ok and not summary.get('ok'):
        return 1
    return 0





def cmd_proof_recovery_vault(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_recovery_vault')
    optional = lambda value: None if value is None or str(value) in {'', 'none', 'None', '-'} else Path(value)
    report = mod.analyze_recovery_vault(
        Path(args.input),
        out=optional(args.out),
        redacted_out=optional(args.redacted_out),
        summary_out=Path(args.summary_out),
        require_full_document=args.require_full_document,
        require_integrity_match=args.require_integrity_match,
        require_live_candidate=args.require_live_candidate,
        ingest=args.ingest,
        ingest_out=Path(args.ingest_out),
        ingest_redacted_out=optional(args.ingest_redacted_out),
        ingest_summary_out=Path(args.ingest_summary_out),
        finalize=args.finalize,
        pack_dir=Path(args.pack_dir),
        final_summary_path=Path(args.final_summary_out),
        export_summary_path=Path(args.export_summary_out),
        check_summary_path=Path(args.check_summary_out),
        clean=args.clean,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2




def cmd_proof_transfer_audit(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_transfer_audit')
    report = mod.audit_transfer(
        Path(args.input),
        summary_out=Path(args.summary_out),
        require_proof_capture=not args.no_require_proof_capture,
        require_ready_to_download=args.require_ready_to_download,
        require_full_screenshot=args.require_full_screenshot,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2

def cmd_proof_attempt_audit(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_attempt_audit')
    report = mod.audit_file(
        Path(args.input),
        summary_out=Path(args.summary_out),
        require_ready_to_download=args.require_ready_to_download,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2

def cmd_proof_ingest(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_ingest')
    redacted_out = None if not args.redacted_out or str(args.redacted_out) in {'', 'none', 'None', '-'} else Path(args.redacted_out)
    report = mod.ingest_capture(
        Path(args.input),
        out=Path(args.out),
        redacted_out=redacted_out,
        summary_out=Path(args.summary_out),
        require_live_candidate=args.require_live_candidate,
        finalize=args.finalize,
        pack_dir=Path(args.pack_dir),
        final_summary_path=Path(args.final_summary_out),
        export_summary_path=Path(args.export_summary_out),
        check_summary_path=Path(args.check_summary_out),
        clean=args.clean,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


def cmd_proof_finalize_pack(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_finalize_pack')
    report = mod.finalize_pack(
        Path(args.input),
        Path(args.pack_dir),
        final_summary_path=Path(args.summary_out),
        export_summary_path=Path(args.export_summary_out),
        check_summary_path=Path(args.check_summary_out),
        clean=args.clean,
        require_live=args.require_live,
        allow_placeholder_screenshot=True if args.allow_placeholder_screenshot else (False if args.no_placeholder_screenshot else None),
        require_privacy_pass=args.require_privacy_pass,
        privacy_reviewer=args.privacy_reviewer,
        privacy_decision=args.privacy_decision,
        privacy_attest_screenshot_reviewed=args.privacy_attest_screenshot_reviewed,
        privacy_attest_no_unrelated_content=args.privacy_attest_no_unrelated_content,
        privacy_attest_local_only=args.privacy_attest_local_only,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2

def cmd_proof_check_pack(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_pack_check')
    report = mod.check_pack(
        Path(args.pack_dir),
        summary_path=Path(args.summary_out),
        require_live=args.require_live,
        allow_rehearsal=not args.no_rehearsal,
        require_privacy_pass=args.require_privacy_pass,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


def cmd_proof_pack_integrity(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_pack_integrity')
    report = mod.build_pack_integrity(
        Path(args.pack_dir),
        summary_path=Path(args.summary_out),
        write_pack_file=args.write_pack_file,
        refresh_ledger=args.refresh_ledger,
        require_existing=args.require_existing,
        require_existing_match=args.require_existing_match,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if (not args.require_ok or report.get('ok')) else 2

def cmd_proof_privacy_review(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_privacy_review')
    report = mod.build_privacy_review(
        Path(args.pack_dir),
        json_out=Path(args.json_out),
        markdown_out=Path(args.markdown_out) if args.markdown_out else None,
        reviewer=args.reviewer,
        reviewer_contact=args.reviewer_contact,
        decision=args.decision,
        require_live=args.require_live,
        require_pass=args.require_pass,
        attest_screenshot_reviewed=args.attest_screenshot_reviewed,
        attest_no_unrelated_content=args.attest_no_unrelated_content,
        attest_local_only=args.attest_local_only,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


def cmd_proof_publish_bundle(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_publish_bundle')
    report = mod.publish_bundle(
        Path(args.pack_dir),
        Path(args.out),
        summary_path=Path(args.summary_out),
        require_live=not args.no_require_live,
        require_privacy_pass=not args.no_require_privacy_pass,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


def cmd_proof_publish_verify(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_publish_verify')
    report = mod.verify_publish_bundle(
        Path(args.bundle),
        summary_path=Path(args.summary_out),
        expected_sha256=args.expected_sha256,
        require_live=not args.no_require_live,
        require_privacy_pass=not args.no_require_privacy_pass,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2




def cmd_proof_autopilot(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_autopilot')
    report = mod.run_autopilot(
        summary_out=Path(args.summary_out),
        execute_safe=args.execute_safe,
        execute_live=args.execute_live,
        input_path=Path(args.input) if args.input else None,
        live_pack_dir=Path(args.live_pack_dir),
        publish_bundle=Path(args.publish_bundle),
        require_complete=args.require_complete,
        clean=args.clean,
        reviewer=args.reviewer,
        decision=args.decision,
        attest_screenshot_reviewed=args.attest_screenshot_reviewed,
        attest_no_unrelated_content=args.attest_no_unrelated_content,
        attest_local_only=args.attest_local_only,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2

def cmd_proof_status(args: argparse.Namespace) -> int:
    mod = _load_script_module('chatgpt_proof_status')
    report = mod.build_status(
        summary_path=Path(args.summary_out) if args.summary_out else None,
        live_pack_dir=Path(args.live_pack_dir),
        rehearsal_pack_dir=Path(args.rehearsal_pack_dir),
        publish_bundle_path=Path(args.publish_bundle),
        require_live=not args.no_require_live,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None,
                     sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2

def cmd_tail(args: argparse.Namespace) -> int:
    events_path = state_root() / "events.jsonl"
    if not events_path.exists():
        print("no event log found", flush=True)
        return 1

    lines = events_path.read_text(encoding="utf-8").splitlines()
    for line in lines[-args.lines :]:
        print(line)
    return 0


def cmd_overflow_report(args: argparse.Namespace) -> int:
    report = build_overflow_report(artifact=args.artifact, include_message=args.include_message)
    if not report.get('artifact_path') and not isinstance(report.get('latest_summary'), dict):
        print('no oversized host-outbound artifact recorded yet', file=sys.stderr)
        return 1
    if report.get('artifact_path') and report.get('artifact_exists') is False:
        emit_json(report)
        return 2
    emit_json(report)
    return 0


def cmd_overflow_prune(args: argparse.Namespace) -> int:
    emit_json(build_overflow_prune_report(keep=args.keep, max_age_days=args.max_age_days, max_disk_bytes=args.max_disk_bytes, apply=args.apply))
    return 0


def cmd_socket_status(args: argparse.Namespace) -> int:
    with SocketClient(require_socket(), timeout=args.timeout) as client:
        emit_json(client.recv())
        client.send({"op": "status"})
        emit_json(client.recv())
    return 0


def wait_for_request_id(client: SocketClient, request_id: str) -> JsonDict:
    while True:
        message = client.recv()
        if message.get("stream") == "browser_event" and message.get("message", {}).get("request_id") == request_id:
            return message
        emit_json_stderr(message)


def submit_browser_request(
    message_type: str,
    payload: JsonDict,
    *,
    wait: bool,
    timeout: float,
    tab_id: int | None = None,
    text_output: bool = False,
    tabs_output: bool = False,
    receivers_output: bool = False,
    receivers_tab_id: int | None = None,
    save_fixture: bool = False,
    fixture_output_dir: Path | None = None,
) -> int:
    request = make_envelope(message_type, payload, tab_id=tab_id)
    with SocketClient(require_socket(), timeout=timeout) as client:
        emit_json_stderr(client.recv())
        client.send({"op": "submit_browser_request", "message": request})
        emit_json_stderr(client.recv())
        if wait:
            response = wait_for_request_id(client, request["request_id"])
            if save_fixture:
                target = fixture_path_from_response(response, fixture_output_dir)
                target.write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                try:
                    from native_message_budget_lib import fixture_payload_budget
                    payload = response.get('message', {}).get('payload')
                    if isinstance(payload, dict):
                        budget = fixture_payload_budget(payload)
                        host_budget = budget['host_to_extension']
                        if host_budget.get('status') in {'warning', 'overflow'}:
                            print(
                                f"[glassttyd] fixture payload uses {host_budget['size_bytes']} / {host_budget['limit_bytes']} bytes of Chrome's host-to-extension native-messaging budget",
                                file=sys.stderr,
                            )
                except Exception:
                    pass
                print(target)
            elif tabs_output:
                print_supported_tabs(response)
            elif receivers_output:
                print_receivers(response, tab_id=receivers_tab_id)
            elif text_output:
                text = extract_text_from_browser_event(response)
                if text is None:
                    emit_json(response)
                else:
                    print(text)
            else:
                emit_json(response)
        else:
            emit_json(request)
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    with SocketClient(require_socket(), timeout=args.timeout) as client:
        emit_json(client.recv())
        client.send({"op": "watch"})
        while True:
            emit_json(client.recv())


def cmd_request(args: argparse.Namespace) -> int:
    payload = json.loads(args.payload) if args.payload else {}
    return submit_browser_request(args.type, payload, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id)


def cmd_bridge_status(args: argparse.Namespace) -> int:
    return submit_browser_request("bridge.status", {}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id)


def cmd_contexts(args: argparse.Namespace) -> int:
    return submit_browser_request("bridge.contexts", {"ensure_offscreen": args.ensure_offscreen}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id)


def cmd_trace(args: argparse.Namespace) -> int:
    return submit_browser_request("bridge.trace", {"limit": args.limit}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id)


def cmd_probe(args: argparse.Namespace) -> int:
    return submit_browser_request(
        "bridge.probe",
        {"limit": args.limit, "await_health_ms": args.await_health_ms, "ensure_offscreen": args.ensure_offscreen},
        wait=args.wait,
        timeout=args.timeout,
        tab_id=args.tab_id,
    )


def cmd_content_script_experiment(args: argparse.Namespace) -> int:
    return submit_browser_request(
        "bridge.content_script_experiment",
        {},
        wait=True,
        timeout=args.timeout,
        tab_id=args.tab_id,
    )


def cmd_set_content_script_experiment(args: argparse.Namespace) -> int:
    return submit_browser_request(
        "bridge.set_content_script_experiment",
        {"experiment_id": args.experiment_id},
        wait=args.wait,
        timeout=args.timeout,
        tab_id=args.tab_id,
    )


def cmd_clear_content_script_experiment(args: argparse.Namespace) -> int:
    return submit_browser_request(
        "bridge.clear_content_script_experiment",
        {},
        wait=args.wait,
        timeout=args.timeout,
        tab_id=args.tab_id,
    )


def read_text_input(path_or_dash: str) -> str:
    if path_or_dash == '-':
        return sys.stdin.read()
    return Path(path_or_dash).read_text(encoding='utf-8')


def cmd_offscreen_dom(args: argparse.Namespace) -> int:
    payload = {
        "html": read_text_input(args.html_file),
        "selectors": args.selector or [],
        "max_candidates": args.max_candidates,
        "base_url": args.base_url,
    }
    return submit_browser_request(
        "bridge.offscreen_dom",
        payload,
        wait=True,
        timeout=args.timeout,
        tab_id=args.tab_id,
    )


def cmd_offscreen_fixture(args: argparse.Namespace) -> int:
    payload = {
        "html": read_text_input(args.html_file),
        "selectors": args.selector or [],
        "max_candidates": args.max_candidates,
        "base_url": args.base_url,
    }
    return submit_browser_request(
        "bridge.offscreen_fixture",
        payload,
        wait=True,
        timeout=args.timeout,
        tab_id=args.tab_id,
    )


def cmd_list_tabs(args: argparse.Namespace) -> int:
    return submit_browser_request("bridge.status", {}, wait=True, timeout=args.timeout, tab_id=args.tab_id, tabs_output=True)


def cmd_list_receivers(args: argparse.Namespace) -> int:
    return submit_browser_request("bridge.status", {}, wait=True, timeout=args.timeout, tab_id=args.tab_id, receivers_output=True, receivers_tab_id=args.tab_id)


def cmd_select_tab(args: argparse.Namespace) -> int:
    return submit_browser_request("bridge.set_target_tab", {"tab_id": args.tab_id}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id)


def cmd_clear_target_tab(args: argparse.Namespace) -> int:
    return submit_browser_request("bridge.clear_target_tab", {}, wait=args.wait, timeout=args.timeout)


def cmd_select_receiver(args: argparse.Namespace) -> int:
    return submit_browser_request("bridge.set_receiver_override", {"tab_id": args.tab_id, "receiver_key": args.receiver_key}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id)


def cmd_clear_receiver_override(args: argparse.Namespace) -> int:
    return submit_browser_request("bridge.clear_receiver_override", {"tab_id": args.tab_id}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id)


def cmd_resolve_receiver(args: argparse.Namespace) -> int:
    request = make_envelope('bridge.status', {}, tab_id=args.tab_id)
    with SocketClient(require_socket(), timeout=args.timeout) as client:
        emit_json_stderr(client.recv())
        client.send({"op": "submit_browser_request", "message": request})
        emit_json_stderr(client.recv())
        response = wait_for_request_id(client, request['request_id'])
    rows = extract_receivers_from_browser_event(response, args.tab_id)
    matches = select_matching_receivers(
        rows,
        receiver_key_filter=args.receiver_key,
        frame_id=args.frame_id,
        document_id=args.document_id,
        url_contains=args.url_contains,
        frame_type=args.frame_type,
        frame_host_contains=args.frame_host_contains,
        frame_path_contains=args.frame_path_contains,
        frame_depth=args.frame_depth,
        top_frame=args.top_frame,
        active_outermost=args.active_outermost,
        ready_only=args.ready_only,
        document_lifecycle=args.document_lifecycle,
    )
    if not matches:
        raise SystemExit(f'no receivers matched tab {args.tab_id}')
    ranked_matches = describe_matching_receivers(matches)
    if len(matches) > 1 and not args.first:
        result: JsonDict = {
            'ok': False,
            'tabId': args.tab_id,
            'matchCount': len(matches),
            'error': 'multiple receivers matched; add a narrower filter or pass --first',
            'matches': matches,
        }
        if args.explain:
            result['resolverPolicy'] = ['lifecyclePreferred', 'outermost', 'ready', 'frameDepth', 'lastSeenAt']
            result['rankedMatches'] = ranked_matches
        emit_json(result)
        return 2
    chosen = matches[0]
    key = receiver_key(chosen)
    if not key:
        raise SystemExit('matched receiver has no selectable receiver key')
    result: JsonDict = {
        'ok': True,
        'tabId': args.tab_id,
        'receiverKey': key,
        'receiverLabel': receiver_label(chosen),
        'receiver': chosen,
        'matchCount': len(matches),
    }
    if args.explain:
        result['resolverPolicy'] = ['lifecyclePreferred', 'outermost', 'ready', 'frameDepth', 'lastSeenAt']
        result['receiverResolution'] = describe_receiver_resolution(chosen, rank=1)
        result['rankedMatches'] = ranked_matches
    if args.set_override:
        override_request = make_envelope('bridge.set_receiver_override', {'tab_id': args.tab_id, 'receiver_key': key}, tab_id=args.tab_id)
        with SocketClient(require_socket(), timeout=args.timeout) as client:
            emit_json_stderr(client.recv())
            client.send({"op": "submit_browser_request", "message": override_request})
            emit_json_stderr(client.recv())
            if args.wait:
                result['overrideResponse'] = wait_for_request_id(client, override_request['request_id'])
        result['overrideSet'] = True
    emit_json(result)
    return 0


def cmd_read_prompt(args: argparse.Namespace) -> int:
    return submit_browser_request("prompt.read", {}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id, text_output=args.text)


def cmd_read_latest(args: argparse.Namespace) -> int:
    return submit_browser_request("transcript.latest", {}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id, text_output=args.text)


def cmd_write_prompt(args: argparse.Namespace) -> int:
    return submit_browser_request("prompt.write", {"text": args.text}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id)


def cmd_submit_prompt(args: argparse.Namespace) -> int:
    return submit_browser_request("prompt.submit", {}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id)


def cmd_read_selection(args: argparse.Namespace) -> int:
    return submit_browser_request("selection.read", {}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id, text_output=args.text)


def cmd_state_snapshot(args: argparse.Namespace) -> int:
    return submit_browser_request("state.snapshot", {}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id)


def cmd_debug_candidates(args: argparse.Namespace) -> int:
    return submit_browser_request("debug.dom_candidates", {}, wait=args.wait, timeout=args.timeout, tab_id=args.tab_id)


def cmd_capture_fixture(args: argparse.Namespace) -> int:
    return submit_browser_request(
        "fixture.capture",
        {},
        wait=True,
        timeout=args.timeout,
        tab_id=args.tab_id,
        save_fixture=True,
        fixture_output_dir=Path(args.output_dir) if args.output_dir else None,
    )


# --------------------------------------------------------------------------- #
# Conversation commands (rev0353): ask / chat / run + mock-tab
#
# These are the "generalized commandline tool" layer. The primitives above
# (write-prompt / submit-prompt / state-snapshot / transcript-latest) are the
# building blocks; these commands turn them into an actual conversation loop.
# --------------------------------------------------------------------------- #
def _resolve_socket(args: argparse.Namespace) -> Path:
    override = getattr(args, "socket", None)
    return Path(override) if override else socket_path()


def _engine_config_from_args(args: argparse.Namespace):
    from .conversation import EngineConfig

    return EngineConfig(
        poll_interval=getattr(args, "poll_interval", 1.0),
        max_wait=getattr(args, "max_wait", 180.0),
        settle_polls=getattr(args, "settle_polls", 2),
        start_grace=getattr(args, "start_grace", 15.0),
        auto_continue=not getattr(args, "no_continue", False),
        max_continues=getattr(args, "max_continues", 12),
        require_readback=getattr(args, "require_readback", False),
        keep_snapshots=getattr(args, "debug_snapshots", False),
        attach_timeout=getattr(args, "attach_timeout", 180.0),
        chip_wait=getattr(args, "chip_wait", 30.0),
        require_attachment=not getattr(args, "no_require_attachment", False),
    )


def _make_engine(args: argparse.Namespace):
    from .conversation import BrokerClient, BrokerUnavailable, ConversationEngine

    client = BrokerClient(_resolve_socket(args), default_timeout=getattr(args, "request_timeout", 20.0))
    try:
        client.ensure_available()
    except BrokerUnavailable as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(3)
    return ConversationEngine(client, tab_id=getattr(args, "tab_id", None), config=_engine_config_from_args(args))


def _read_prompt_source(args: argparse.Namespace) -> str:
    if getattr(args, "prompt", None):
        return str(args.prompt)
    if getattr(args, "file", None):
        return Path(args.file).read_text(encoding="utf-8")
    if getattr(args, "stdin", False) or not sys.stdin.isatty():
        data = sys.stdin.read()
        if data.strip():
            return data
    raise SystemExit("no prompt provided; pass text, --file PATH, or pipe on stdin")


def _slugify(text: str, *, limit: int = 40) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in text.strip().lower())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned[:limit] or "prompt"


def _diagnose_failure(engine, result, args: argparse.Namespace) -> JsonDict | None:
    """Probe the surface at the moment of failure and explain what broke.

    This is the whole reason the surface wing exists. A failed turn used to be a
    dead end ("submit was blocked" — by what?). Now the failure itself triggers a
    live probe, a diff against the last known-good surface, and a correlation
    between the two: not "something changed" but "your submit did nothing because
    the send button is now button[data-testid=composer-send-v2]".
    """
    from .surface import SurfaceStore, build_snapshot, triage

    restore_prompt: str | None = None
    drafted = False
    probe: JsonDict | None = None
    try:
        restore_prompt = engine.read_prompt()
        if restore_prompt == "":
            write_ok, readback_ok = engine.write_prompt("glasstty diagnose probe (draft, not sent)")
            drafted = write_ok and readback_ok
        reply = engine.client.request("surface.probe", {}, tab_id=getattr(args, "tab_id", None),
                                      timeout=getattr(args, "request_timeout", 20.0))
        candidate = reply.payload.get("probe")
        if isinstance(candidate, dict):
            probe = candidate
    except Exception as exc:  # noqa: BLE001 - diagnosis must never mask the original failure
        print(f"[glassttyd] diagnose: probe failed: {exc}", file=sys.stderr)
    finally:
        if drafted and restore_prompt is not None:
            try:
                restore_ok, restore_readback_ok = engine.write_prompt(restore_prompt)
                if not (restore_ok and restore_readback_ok):
                    print("[glassttyd] diagnose: could not verify draft cleanup", file=sys.stderr)
            except Exception as exc:  # noqa: BLE001 - preserve the original failure report
                print(f"[glassttyd] diagnose: draft cleanup failed: {exc}", file=sys.stderr)
    if probe is None:
        print("[glassttyd] diagnose: the page returned no probe (extension older than rev0354?)", file=sys.stderr)
        return None

    store = SurfaceStore(Path(getattr(args, "store", None) or (default_home() / "surface")))
    snapshot = build_snapshot(probe, label="failure", source="diagnose")
    store.save(snapshot)
    report = triage(snapshot, baseline=store.baseline(), failure=result.to_json())

    print("", file=sys.stderr)
    print(f"[glassttyd] diagnosis: {report['verdict']}", file=sys.stderr)
    if report.get("likely_cause"):
        print(f"[glassttyd] likely cause: {report['likely_cause']}", file=sys.stderr)
    for finding in report["findings"]:
        if finding.get("severity") in ("critical", "degraded"):
            detail = finding.get("summary") or finding.get("why") or finding.get("kind")
            print(f"[glassttyd]   [{finding['severity']}] {finding.get('kind')}: {detail}", file=sys.stderr)
    for repair in report["repairs"]:
        if repair.get("suggested_selector"):
            mark = "confident" if repair.get("confident") else "unconfirmed"
            print(f"[glassttyd]   repair ({mark}): {repair['anchor']} -> {repair['suggested_selector']}", file=sys.stderr)
    for action in report["next_actions"]:
        print(f"[glassttyd]   next: {action}", file=sys.stderr)
    return report


def _attachments(args: argparse.Namespace) -> list[Path]:
    return [Path(item) for item in (getattr(args, "attach", None) or [])]


def cmd_ask(args: argparse.Namespace) -> int:
    engine = _make_engine(args)
    if getattr(args, "new_chat", False):
        engine.new_chat()
        time.sleep(1.5)
    prompt = _read_prompt_source(args)
    attach = _attachments(args)
    if attach and not getattr(args, "quiet", False):
        for item in attach:
            print(f"[glassttyd] attaching {item.name} ({item.stat().st_size if item.exists() else 0} bytes)…", file=sys.stderr)
    result = engine.send(prompt, submit=not getattr(args, "no_submit", False), attach=attach)
    for record in result.attachments:
        if not getattr(args, "quiet", False):
            state = "chip rendered" if record.get("chip_present") else "NO CHIP"
            print(f"[glassttyd] attachment: {record['name']} {record['bytes']}B "
                  f"sha256={record['sha256'][:12]} chunks={record['chunks']} · {state}", file=sys.stderr)

    if not getattr(args, "quiet", False):
        status = "settled" if result.ok else "did-not-settle"
        print(
            f"[glassttyd] {status} · {result.settle_reason} · {result.polls} polls · "
            f"{result.continues} continue(s) · {result.elapsed_s:.1f}s · via {result.detection}",
            file=sys.stderr,
        )
        for warning in result.warnings:
            print(f"[glassttyd] warning: {warning}", file=sys.stderr)
        if result.error:
            print(f"[glassttyd] error: {result.error}", file=sys.stderr)

    diagnosis = None
    if not result.ok and getattr(args, "diagnose", False):
        diagnosis = _diagnose_failure(engine, result, args)

    if getattr(args, "json", False):
        payload = result.to_json()
        if diagnosis is not None:
            payload["diagnosis"] = diagnosis
        emit_json(payload)
    elif result.text is not None:
        print(result.text)

    if getattr(args, "out", None):
        Path(args.out).write_text((result.text or "") + ("\n" if result.text else ""), encoding="utf-8")
        if not getattr(args, "quiet", False):
            print(f"[glassttyd] wrote response to {args.out}", file=sys.stderr)

    return 0 if result.ok else 1


def cmd_chat(args: argparse.Namespace) -> int:
    engine = _make_engine(args)
    transcript_path = Path(args.out) if getattr(args, "out", None) else None
    if transcript_path is not None:
        transcript_path.parent.mkdir(parents=True, exist_ok=True)

    print("[glassttyd] chat session. /exit to quit, /read for latest, /help for commands.", file=sys.stderr)
    turn = 0
    while True:
        try:
            line = input("you> ")
        except EOFError:
            print("", file=sys.stderr)
            break
        except KeyboardInterrupt:
            print("\n[glassttyd] interrupted", file=sys.stderr)
            break

        stripped = line.strip()
        if not stripped:
            continue
        if stripped in ("/exit", "/quit"):
            break
        if stripped == "/help":
            print("commands: /exit, /quit, /read (print latest assistant turn), /help", file=sys.stderr)
            continue
        if stripped == "/read":
            try:
                latest = engine.read_latest()
                text = latest.get("text")
                print(text if isinstance(text, str) and text else "[no assistant turn yet]")
            except Exception as exc:  # noqa: BLE001 - REPL should not crash
                print(f"[glassttyd] read failed: {exc}", file=sys.stderr)
            continue

        turn += 1
        result = engine.send(stripped)
        if result.text is not None:
            print(f"gpt> {result.text}")
        if not result.ok:
            print(f"[glassttyd] turn did not settle: {result.settle_reason} ({result.error or 'no detail'})", file=sys.stderr)
        if transcript_path is not None:
            with transcript_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"turn": turn, **result.to_json()}, ensure_ascii=False) + "\n")

    return 0


def _substitute_vars(text: str, variables: dict[str, str]) -> tuple[str, list[str]]:
    missing: list[str] = []
    out = text
    for key, value in variables.items():
        out = out.replace("{{" + key + "}}", value)
    # detect leftover placeholders
    import re as _re

    for match in _re.findall(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}", out):
        missing.append(match)
    return out, sorted(set(missing))


def _parse_queue_file(path: Path, fmt: str) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    resolved = fmt
    if fmt == "auto":
        resolved = "jsonl" if path.suffix.lower() in (".jsonl", ".ndjson") else "blocks"

    items: list[dict[str, Any]] = []
    if resolved == "jsonl":
        for line_no, line in enumerate(raw.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if isinstance(obj, str):
                items.append({"prompt": obj})
            elif isinstance(obj, dict) and isinstance(obj.get("prompt"), str):
                items.append(obj)
            else:
                raise SystemExit(f"{path}:{line_no}: each JSONL record must be a string or an object with a 'prompt' field")
    else:  # blocks: split on lines that are exactly '---' (optionally '--- name')
        current: list[str] = []
        name: str | None = None
        for line in raw.splitlines():
            if line.strip() == "---" or line.strip().startswith("--- "):
                if current:
                    items.append({"prompt": "\n".join(current).strip(), "name": name})
                    current = []
                name = line.strip()[4:].strip() or None if line.strip().startswith("--- ") else None
                continue
            current.append(line)
        if current and "\n".join(current).strip():
            items.append({"prompt": "\n".join(current).strip(), "name": name})
    return [item for item in items if item.get("prompt")]


QUEUE_INPUT_SCHEMA = "glasstty.queue-input/v1"
QUEUE_INFLIGHT_SCHEMA = "glasstty.queue-inflight/v1"


def _queue_input_fingerprint(payload: JsonDict) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _hash_queue_attachment(path: Path) -> JsonDict:
    path = Path(path)
    try:
        before = path.stat()
        if not path.is_file():
            raise SystemExit(f"cannot verify queue attachment for resume; not a regular file: {path}")
        digest = hashlib.sha256()
        total = 0
        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
                total += len(chunk)
        after = path.stat()
    except OSError as exc:
        raise SystemExit(f"cannot verify queue attachment for resume: {path}: {exc}") from exc
    if total != before.st_size or (
        before.st_ino, before.st_size, before.st_mtime_ns
    ) != (
        after.st_ino, after.st_size, after.st_mtime_ns
    ):
        raise SystemExit(f"cannot verify queue attachment for resume; file changed while hashing: {path}")
    return {
        "path": str(path),
        "name": path.name,
        "bytes": total,
        "sha256": digest.hexdigest(),
    }


def _current_queue_input(name: str, prompt: str, attachments: list[Path]) -> tuple[JsonDict, str]:
    payload: JsonDict = {
        "schema": QUEUE_INPUT_SCHEMA,
        "name": name,
        "prompt": prompt,
        "attachments": [_hash_queue_attachment(path) for path in attachments],
    }
    return payload, _queue_input_fingerprint(payload)


def _result_queue_input(
    name: str,
    prompt: str,
    requested: list[Path],
    attachments: list[JsonDict],
) -> tuple[JsonDict, str | None]:
    captured: list[JsonDict] = []
    complete = len(requested) == len(attachments)
    for index, path in enumerate(requested):
        record = attachments[index] if index < len(attachments) else {}
        sha256 = record.get("sha256")
        size = record.get("bytes")
        valid = (
            record.get("ok") is True
            and record.get("path") == str(path)
            and isinstance(size, int) and not isinstance(size, bool) and size > 0
            and isinstance(sha256, str) and len(sha256) == 64
        )
        complete = complete and valid
        captured.append({
            "path": str(path),
            "name": path.name,
            "bytes": size if isinstance(size, int) and not isinstance(size, bool) else None,
            "sha256": sha256 if isinstance(sha256, str) and len(sha256) == 64 else None,
        })
    payload: JsonDict = {
        "schema": QUEUE_INPUT_SCHEMA,
        "name": name,
        "prompt": prompt,
        "attachments": captured,
    }
    return payload, _queue_input_fingerprint(payload) if complete else None


def _submission_outcome(record: JsonDict) -> str:
    outcome = record.get("submission_outcome")
    if outcome in {"not-attempted", "submitted", "unknown"}:
        return str(outcome)
    return "submitted" if record.get("submitted") is True else "not-attempted"


def _fsync_directory(path: Path) -> None:
    directory_fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _write_json_atomic(path: Path, payload: JsonDict) -> None:
    _write_text_atomic(path, json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _unlink_durable(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    _fsync_directory(path.parent)


def cmd_run(args: argparse.Namespace) -> int:
    engine = _make_engine(args)
    queue_path = Path(args.queue)
    if not queue_path.exists():
        raise SystemExit(f"queue file not found: {queue_path}")

    global_vars: dict[str, str] = {}
    for pair in getattr(args, "var", []) or []:
        if "=" not in pair:
            raise SystemExit(f"--var expects key=value, got: {pair}")
        key, value = pair.split("=", 1)
        global_vars[key.strip()] = value

    items = _parse_queue_file(queue_path, args.format)
    if not items:
        raise SystemExit(f"no prompts found in {queue_path}")

    global_attach = _attachments(args)
    out_dir = Path(args.out_dir) if getattr(args, "out_dir", None) else None
    if getattr(args, "resume", False) and out_dir is None:
        raise SystemExit("--resume requires --out-dir")
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)

    # Resume is content-addressed, not index-only. A changed queue, template value,
    # or attachment must never inherit an unrelated turn's successful record.
    prior_records: dict[int, JsonDict] = {}
    transcript_path = (out_dir / "transcript.jsonl") if out_dir is not None else None
    inflight_path = (out_dir / ".glasstty-inflight.json") if out_dir is not None else None
    resuming = bool(getattr(args, "resume", False)) and transcript_path is not None and transcript_path.exists()
    if resuming:
        for line_no, line in enumerate(transcript_path.read_text(encoding="utf-8").splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"cannot safely resume: malformed {transcript_path}:{line_no}: {exc}") from exc
            index = record.get("index") if isinstance(record, dict) else None
            if not isinstance(index, int) or isinstance(index, bool) or index < 1:
                raise SystemExit(f"cannot safely resume: invalid turn index in {transcript_path}:{line_no}")
            prior_records[index] = record
        extra_indices = sorted(index for index in prior_records if index > len(items))
        if extra_indices:
            raise SystemExit(
                "cannot safely resume: the transcript contains turn indices outside the current queue "
                f"({', '.join(map(str, extra_indices))})"
            )

    if inflight_path is not None and inflight_path.exists():
        if not getattr(args, "resume", False):
            _unlink_durable(inflight_path)
        else:
            try:
                inflight = json.loads(inflight_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise SystemExit(f"cannot safely resume: invalid in-flight marker {inflight_path}: {exc}") from exc
            attempt_id = inflight.get("attempt_id") if isinstance(inflight, dict) else None
            index = inflight.get("index") if isinstance(inflight, dict) else None
            completed = (
                inflight.get("schema") == QUEUE_INFLIGHT_SCHEMA
                and isinstance(attempt_id, str)
                and isinstance(index, int) and not isinstance(index, bool)
                and prior_records.get(index, {}).get("attempt_id") == attempt_id
            )
            if completed:
                _unlink_durable(inflight_path)
            else:
                raise SystemExit(
                    f"cannot safely resume: turn {index!r} has an unresolved in-flight marker at "
                    f"{inflight_path}; its submission may have landed, so inspect the conversation and "
                    "start a fresh run without --resume to proceed explicitly"
                )

    min_delay = float(getattr(args, "min_delay", 0.0) or 0.0)
    max_delay = float(getattr(args, "max_delay", 0.0) or 0.0)
    if max_delay and max_delay < min_delay:
        raise SystemExit("--max-delay must be >= --min-delay")

    transcript_fh = None
    if transcript_path is not None:
        transcript_fh = transcript_path.open("a" if resuming else "w", encoding="utf-8")

    records: list[dict[str, Any]] = []
    ok_count = 0
    skipped = 0
    diagnosed = False
    try:
        for index, item in enumerate(items, start=1):
            item_vars = dict(global_vars)
            if isinstance(item.get("vars"), dict):
                item_vars.update({str(k): str(v) for k, v in item["vars"].items()})
            prompt, missing = _substitute_vars(str(item["prompt"]), item_vars)
            name = item.get("name") or f"prompt-{index:03d}"

            if not getattr(args, "quiet", False):
                print(f"[glassttyd] ({index}/{len(items)}) {name} …", file=sys.stderr)
            if missing:
                print(f"[glassttyd] warning: unresolved template vars in {name}: {', '.join(missing)}", file=sys.stderr)

            item_attach = list(global_attach)
            if isinstance(item.get("attach"), list):
                item_attach += [Path(str(a)) for a in item["attach"]]
            elif isinstance(item.get("attach"), str):
                item_attach.append(Path(item["attach"]))

            prior = prior_records.get(index)
            if prior is not None and prior.get("ok") is True:
                prior_fingerprint = prior.get("queue_input_fingerprint")
                if not isinstance(prior_fingerprint, str):
                    raise SystemExit(
                        f"cannot safely resume turn {index}: its successful transcript record predates "
                        "content-addressed queue inputs; start a fresh run without --resume"
                    )
                _current_input, current_fingerprint = _current_queue_input(name, prompt, item_attach)
                if current_fingerprint != prior_fingerprint:
                    raise SystemExit(
                        f"cannot safely resume turn {index}: the prompt, name, template values, or attachment "
                        "content changed since the successful transcript record"
                    )
                if out_dir is not None:
                    slug = _slugify(name if item.get("name") else prompt)
                    response_file = out_dir / f"{index:03d}-{slug}.md"
                    if not response_file.exists():
                        _write_text_atomic(response_file, (prior.get("text") or "") + "\n")
                skipped += 1
                continue
            if prior is not None and _submission_outcome(prior) in {"submitted", "unknown"}:
                raise SystemExit(
                    f"cannot safely resume turn {index}: the previous attempt's submission outcome is "
                    f"{_submission_outcome(prior)!r}; inspect the conversation and start a fresh run to "
                    "avoid a duplicate prompt"
                )

            attempt_id = uuid.uuid4().hex
            if inflight_path is not None:
                _write_json_atomic(inflight_path, {
                    "schema": QUEUE_INFLIGHT_SCHEMA,
                    "attempt_id": attempt_id,
                    "index": index,
                    "name": name,
                    "prompt": prompt,
                    "attachments": [str(path) for path in item_attach],
                    "started_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                })

            result = engine.send(prompt, attach=item_attach)
            if result.ok:
                ok_count += 1

            queue_input, queue_input_fingerprint = _result_queue_input(
                name, prompt, item_attach, result.attachments,
            )
            record = {
                "index": index,
                "name": name,
                "attempt_id": attempt_id,
                "queue_input": queue_input,
                "queue_input_fingerprint": queue_input_fingerprint,
                **result.to_json(),
            }
            records.append(record)
            if transcript_fh is not None:
                transcript_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                transcript_fh.flush()
                os.fsync(transcript_fh.fileno())
            if out_dir is not None:
                slug = _slugify(name if item.get("name") else prompt)
                response_file = out_dir / f"{index:03d}-{slug}.md"
                _write_text_atomic(response_file, (result.text or "") + "\n")
            if inflight_path is not None:
                _unlink_durable(inflight_path)

            if not result.ok:
                print(f"[glassttyd] turn {index} did not settle: {result.settle_reason} ({result.error or 'no detail'})", file=sys.stderr)
                if getattr(args, "diagnose", False) and not diagnosed:
                    # Diagnose once. A drifted UI fails every turn identically;
                    # printing the same diagnosis 200 times helps no one.
                    _diagnose_failure(engine, result, args)
                    diagnosed = True
                if getattr(args, "stop_on_error", False):
                    print("[glassttyd] stopping (--stop-on-error)", file=sys.stderr)
                    break

            # Pacing between turns. Rate limits are real; the userscript queuer
            # paced itself for exactly this reason. Only sleep if more work follows.
            if max_delay > 0 and index < len(items):
                import random

                delay = random.uniform(min_delay, max_delay)
                if delay > 0:
                    if not getattr(args, "quiet", False):
                        print(f"[glassttyd] pacing {delay:.1f}s before next prompt", file=sys.stderr)
                    time.sleep(delay)
    finally:
        if transcript_fh is not None:
            transcript_fh.close()

    summary = {
        "queue": str(queue_path),
        "total": len(items),
        "attempted": len(records),
        "skipped_resumed": skipped,
        "settled": ok_count,
        "failed": len(records) - ok_count,
        "out_dir": str(out_dir) if out_dir else None,
    }
    if getattr(args, "json", False):
        emit_json({"summary": summary, "records": records})
    else:
        print(
            f"[glassttyd] done: {ok_count}/{len(records)} settled"
            + (f", {skipped} skipped (resume)" if skipped else "")
            + (f", responses in {out_dir}" if out_dir else ""),
            file=sys.stderr,
        )
    return 0 if summary["failed"] == 0 and (summary["attempted"] + skipped) == summary["total"] else 1



# --------------------------------------------------------------------------- #
# Surface intelligence commands (rev0354)
#
# The conversation lane made GlassTTY usable. This lane keeps it usable as
# ChatGPT's UI moves underneath it: probe the live surface, keep a history,
# diff it, and turn a drift into a diagnosis with concrete repair candidates.
# --------------------------------------------------------------------------- #
def _surface_store(args: argparse.Namespace):
    from .surface import SurfaceStore

    root = Path(getattr(args, "store", None) or (default_home() / "surface"))
    return SurfaceStore(root)


DRAFT_PROBE_TEXT = "glasstty surface probe (draft, not sent)"


def _capture_probe(args: argparse.Namespace) -> JsonDict:
    """Ask the live tab (or mock) for a surface probe.

    With --probe-with-draft, stage a harmless draft in the composer first. This is
    not a nicety: ChatGPT does not render a send button until the composer has
    text, so probing an empty composer can never tell you whether send still works.
    The live 2026-07-11 surface capture shows exactly this — zero matches for
    #composer-submit-button on a completely healthy page, and a drift contract
    shouting "blocker" about it. The draft is never submitted; it is restored
    afterwards.
    """
    from .conversation import BridgeRequestError

    engine = _make_engine(args)
    restore: str | None = None
    if getattr(args, "probe_with_draft", False):
        restore = engine.read_prompt() or ""
        write_ok, readback_ok = engine.write_prompt(DRAFT_PROBE_TEXT)
        if not write_ok or not readback_ok:
            raise BridgeRequestError("could not stage and verify the surface-probe draft")
        time.sleep(0.4)

    try:
        reply = engine.client.request("surface.probe", {}, tab_id=getattr(args, "tab_id", None),
                                      timeout=getattr(args, "request_timeout", 20.0))
    finally:
        if restore is not None:
            restore_ok, restore_readback_ok = engine.write_prompt(restore)
            if not restore_ok or not restore_readback_ok:
                raise BridgeRequestError("could not restore and verify the composer after the surface probe")

    probe = reply.payload.get("probe")
    if not isinstance(probe, dict):
        raise BridgeRequestError(
            "the page returned no surface probe; the extension may be older than rev0354 "
            "(rebuild it with `npm --prefix extension run build`)"
        )
    return probe


def _emit(data: JsonDict, args: argparse.Namespace) -> None:
    if getattr(args, "pretty", False):
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        emit_json(data)


def cmd_surface_snapshot(args: argparse.Namespace) -> int:
    from .surface import build_snapshot

    store = _surface_store(args)
    probe = _capture_probe(args)
    snapshot = build_snapshot(probe, label=getattr(args, "label", None))
    path = store.save(snapshot)

    baseline = store.baseline()
    changed = baseline is None or baseline.get("fingerprint") != snapshot.get("fingerprint")

    if getattr(args, "promote", False):
        store.promote(snapshot)

    result = {
        "ok": True,
        "path": str(path),
        "fingerprint": snapshot["fingerprint"],
        "baseline_fingerprint": baseline.get("fingerprint") if baseline else None,
        "changed_since_baseline": changed,
        "promoted": bool(getattr(args, "promote", False)),
        "capabilities": snapshot["capabilities"],
        "oddities": len(snapshot["oddities"]),
    }
    _emit(result, args)
    return 0


def cmd_surface_diff(args: argparse.Namespace) -> int:
    from .surface import build_snapshot, diff_snapshots

    store = _surface_store(args)

    def _load(spec: str | None, fallback):
        if spec in (None, "baseline"):
            snap = store.baseline()
            if snap is None:
                raise SystemExit("no baseline recorded; run `glassttyd surface-snapshot --promote` first")
            return snap
        if spec == "latest":
            snap = store.latest()
            if snap is None:
                raise SystemExit("no snapshots recorded yet")
            return snap
        if spec == "live":
            return build_snapshot(_capture_probe(args))
        return json.loads(Path(spec).read_text(encoding="utf-8"))

    before = _load(getattr(args, "before", None) or "baseline", None)
    after = _load(getattr(args, "after", None) or "live", None)
    _emit(diff_snapshots(before, after), args)
    return 0


def cmd_surface_triage(args: argparse.Namespace) -> int:
    from .surface import build_snapshot, triage

    store = _surface_store(args)
    if getattr(args, "input", None):
        snapshot = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if snapshot.get("schema") != "glasstty-surface-snapshot/v1":
            snapshot = build_snapshot(snapshot)
    else:
        snapshot = build_snapshot(_capture_probe(args))
        if not getattr(args, "no_save", False):
            store.save(snapshot)

    baseline = None if getattr(args, "no_baseline", False) else store.baseline()
    report = triage(snapshot, baseline=baseline)
    _emit(report, args)

    if getattr(args, "require_ok", False) and report["verdict"] != "surface-ok":
        return 1
    return 0


def cmd_surface_history(args: argparse.Namespace) -> int:
    store = _surface_store(args)
    rows = store.timeline()
    if getattr(args, "json", False):
        _emit({"ok": True, "snapshots": len(rows), "timeline": rows}, args)
        return 0
    if not rows:
        print("no snapshots recorded yet", file=sys.stderr)
        return 0
    baseline = store.baseline()
    baseline_fp = baseline.get("fingerprint") if baseline else None
    for row in rows:
        marker = "CHANGED" if row["changed"] else "  same "
        star = " *baseline" if row["fingerprint"] == baseline_fp else ""
        lost = f" lost={','.join(row['capabilities_lost'])}" if row["capabilities_lost"] else ""
        print(f"{row['stored_at']}  {marker}  {row['fingerprint']}  oddities={row['oddities']}{lost}{star}")
    return 0


def cmd_surface_watch(args: argparse.Namespace) -> int:
    """Poll the live surface and report the moment it changes.

    This is the early-warning system: it catches a UI change *before* it
    silently breaks a long queue run.
    """
    from .surface import build_snapshot, triage

    store = _surface_store(args)
    baseline = store.baseline()
    last_fp = baseline.get("fingerprint") if baseline else None
    interval = float(getattr(args, "interval", 60.0))

    print(f"[glassttyd] watching the ChatGPT surface every {interval:.0f}s (Ctrl-C to stop)", file=sys.stderr)
    if last_fp:
        print(f"[glassttyd] baseline fingerprint: {last_fp}", file=sys.stderr)

    try:
        while True:
            try:
                snapshot = build_snapshot(_capture_probe(args))
            except Exception as exc:  # noqa: BLE001 - a watcher must not die on one bad poll
                print(f"[glassttyd] probe failed: {exc}", file=sys.stderr)
                time.sleep(interval)
                continue

            fp = snapshot["fingerprint"]
            if fp != last_fp:
                store.save(snapshot)
                report = triage(snapshot, baseline=baseline)
                print(f"[glassttyd] SURFACE CHANGED {last_fp} -> {fp}  verdict={report['verdict']}", file=sys.stderr)
                for action in report["next_actions"]:
                    print(f"[glassttyd]   - {action}", file=sys.stderr)
                if getattr(args, "json", False):
                    emit_json(report)
                last_fp = fp
                if getattr(args, "once", False):
                    return 1 if report["verdict"] != "surface-ok" else 0
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[glassttyd] stopped", file=sys.stderr)
    return 0


def cmd_surface_scenarios(args: argparse.Namespace) -> int:
    """List the drift scenarios the mock tab can rehearse."""
    from .mock_tab import DRIFT_SCENARIOS

    if getattr(args, "json", False):
        _emit({"scenarios": DRIFT_SCENARIOS}, args)
        return 0
    print("Drift scenarios (glassttyd mock-tab --drift <name>):\n")
    for name, description in DRIFT_SCENARIOS.items():
        print(f"  {name:<22} {description}")
    return 0


def cmd_surface_repair(args: argparse.Namespace) -> int:
    """Turn a confident diagnosis into a live fix.

    This is the point of the whole wing. A drift used to mean waiting for a new
    extension build. Now: probe -> triage -> apply -> the next `ask` works. The
    override is a *hint* to the adapter, never a bypass of its safety scoring, so
    a wrong repair degrades to the normal search rather than clicking the wrong
    control.
    """
    from .surface import SurfaceStore, build_snapshot, propose_repairs, triage

    engine = _make_engine(args)
    store = _surface_store(args)
    snapshot = build_snapshot(_capture_probe(args), label="repair", source="repair")
    proposals = propose_repairs(snapshot)

    overrides: JsonDict = {}
    accepted: list[JsonDict] = []
    rejected: list[JsonDict] = []
    for proposal in proposals:
        anchor = proposal["anchor"]
        selector = proposal.get("suggested_selector")
        if not selector:
            rejected.append({**proposal, "reason": "no candidate found"})
            continue
        if not proposal.get("confident") and not getattr(args, "force", False):
            rejected.append({**proposal, "reason": "candidate not confident enough (use --force to apply anyway)"})
            continue
        overrides[anchor] = selector
        accepted.append({"anchor": anchor, "selector": selector, "confidence": proposal["candidates"][0]["confidence"]})

    # Manual override wins over anything inferred.
    for pair in getattr(args, "set", []) or []:
        if "=" not in pair:
            raise SystemExit(f"--set expects anchor=selector, got: {pair}")
        anchor, selector = pair.split("=", 1)
        overrides[anchor.strip()] = selector.strip()
        accepted.append({"anchor": anchor.strip(), "selector": selector.strip(), "confidence": "manual"})

    result: JsonDict = {
        "ok": True,
        "applied": False,
        "overrides": overrides,
        "accepted": accepted,
        "rejected": rejected,
        "verdict": triage(snapshot, baseline=store.baseline())["verdict"],
    }

    if getattr(args, "clear", False):
        engine.client.request("surface.overrides.set", {"overrides": {}},
                              tab_id=getattr(args, "tab_id", None), timeout=getattr(args, "request_timeout", 20.0))
        result.update({"overrides": {}, "accepted": [], "applied": True, "cleared": True})
        _emit(result, args)
        return 0

    if getattr(args, "apply", False):
        if not overrides:
            print("[glassttyd] nothing to apply: no confident repair was found", file=sys.stderr)
            _emit(result, args)
            return 1
        reply = engine.client.request("surface.overrides.set", {"overrides": overrides},
                                      tab_id=getattr(args, "tab_id", None),
                                      timeout=getattr(args, "request_timeout", 20.0))
        result["applied"] = bool(reply.payload.get("ok"))
        result["live_overrides"] = reply.payload.get("overrides")
        if result["applied"] and not getattr(args, "quiet", False):
            for item in accepted:
                print(f"[glassttyd] applied: {item['anchor']} -> {item['selector']}", file=sys.stderr)
            print("[glassttyd] the adapter will use these immediately; re-run your command.", file=sys.stderr)
            print("[glassttyd] this is a live patch — fold it into the adapter when convenient.", file=sys.stderr)
    else:
        if not getattr(args, "quiet", False):
            if accepted:
                for item in accepted:
                    print(f"[glassttyd] would apply: {item['anchor']} -> {item['selector']}", file=sys.stderr)
                print("[glassttyd] re-run with --apply to patch the live adapter.", file=sys.stderr)
            else:
                print("[glassttyd] no confident repair available.", file=sys.stderr)

    _emit(result, args)
    return 0


def cmd_surface_overrides(args: argparse.Namespace) -> int:
    engine = _make_engine(args)
    reply = engine.client.request("surface.overrides.get", {}, tab_id=getattr(args, "tab_id", None),
                                  timeout=getattr(args, "request_timeout", 20.0))
    _emit({"ok": True, "overrides": reply.payload.get("overrides") or {}}, args)
    return 0


def _unknown_composer_controls_by_phase(
    phases: list[tuple[str, JsonDict]],
) -> list[JsonDict]:
    """Return each live unknown once, retaining every phase where it appeared."""
    found: dict[str, JsonDict] = {}
    for phase, snapshot in phases:
        controls = snapshot.get("controls") or {}
        values = controls.values() if isinstance(controls, dict) else controls
        for control in values:
            if not isinstance(control, dict):
                continue
            if not (
                control.get("classification") == "unknown"
                and control.get("visible")
                and control.get("region") == "composer"
            ):
                continue
            identity = str(control.get("key") or (
                control.get("selector_hint"),
                control.get("aria_label"),
                control.get("test_id"),
                control.get("text"),
            ))
            if identity not in found:
                found[identity] = {**control, "observed_in": [phase]}
            elif phase not in found[identity]["observed_in"]:
                found[identity]["observed_in"].append(phase)
    return list(found.values())


def _first_flight_ok(report: JsonDict, unknowns: list[str]) -> bool:
    return not unknowns and all(bool(item.get("ok")) for item in report.get("steps") or [])


def _first_flight_baseline_blocker(snapshot: JsonDict, triage_report: JsonDict) -> str | None:
    capabilities = snapshot.get("capabilities") or {}
    if capabilities.get("submit_prompt") is not True:
        return "send control is not available with a staged draft"

    authentication = snapshot.get("authentication") or {}
    if authentication.get("posture") == "anonymous":
        return "not promoted while ChatGPT is logged out; attachment capability is unavailable"
    if authentication.get("posture") != "authenticated":
        return "not promoted because ChatGPT authentication could not be verified"

    verdict = triage_report.get("verdict")
    if verdict not in ("surface-ok", "surface-drift-cosmetic"):
        return f"verdict={verdict} is not healthy enough to become a baseline"
    return None


def cmd_first_flight(args: argparse.Namespace) -> int:
    """First contact with a real ChatGPT tab.

    Everything in GlassTTY is verified against a mock, and a mock is a model of
    someone's assumptions. The live 2026-07-11 surface capture proved two of those
    assumptions wrong in a single sitting. So the first live run is not "does it
    work" — it is a *measurement*, and this command is the instrument.

    It is deliberately read-mostly. It never submits a prompt unless you ask it to.
    """
    from .surface import SurfaceStore, build_snapshot, triage, utcnow

    engine = _make_engine(args)
    store = _surface_store(args)
    report: JsonDict = {"schema": "glasstty-first-flight/v1", "generated_at": utcnow(), "steps": []}
    unknowns: list[str] = []

    def step(name: str, ok: bool, detail: Any = None) -> None:
        report["steps"].append({"step": name, "ok": ok, "detail": detail})
        mark = "ok  " if ok else "FAIL"
        print(f"[{mark}] {name}" + (f" — {detail}" if isinstance(detail, str) else ""), file=sys.stderr)

    # 1. Is anything there at all?
    try:
        snapshot_payload = engine.snapshot()
        step("bridge reachable", True, f"adapter={snapshot_payload.get('adapter')} url={snapshot_payload.get('url')}")
    except Exception as exc:  # noqa: BLE001
        step("bridge reachable", False, str(exc))
        _emit(report, args)
        return 3

    # 2. Idle probe. Expect: send absent, submit_prompt unknown. Anything else is news.
    idle = build_snapshot(_capture_probe(args), label="first-flight-idle")
    store.save(idle)
    idle_triage = triage(idle)
    report["idle"] = {
        "verdict": idle_triage["verdict"],
        "capabilities": idle["capabilities"],
        "authentication": idle.get("authentication") or {},
        "composer": idle.get("composer"),
        "oddities": [o.get("summary") for o in idle.get("oddities") or []],
    }
    step("idle probe", True, f"verdict={idle_triage['verdict']}")
    idle_composer = idle.get("composer") or {}
    composer_clean = (
        idle_composer.get("empty") is True
        and int(idle_composer.get("attached_file_count") or 0) == 0
    )
    step(
        "composer starts empty",
        composer_clean,
        "no draft or attachment will be overwritten"
        if composer_clean else "clear the draft and attachments before first-flight",
    )
    if not composer_clean:
        unknowns.append(
            "First-flight found a draft or attachment already in the composer and refused all live mutations. "
            "Clear it deliberately, then rerun."
        )
    if idle["capabilities"].get("submit_prompt") is not None:
        unknowns.append(
            "The idle probe could see `submit_prompt` — the live capture said send is NOT rendered "
            "on an empty composer. Either ChatGPT changed, or the composer was not actually empty."
        )

    # 3. Draft probe — the definitive read on send. Never overwrite an existing
    # draft, even temporarily: first-flight is a measuring instrument, not an
    # excuse to trust restoration code with operator state.
    if composer_clean:
        draft_args = argparse.Namespace(**{**vars(args), "probe_with_draft": True})
        drafted = build_snapshot(_capture_probe(draft_args), label="first-flight-draft")
        store.save(drafted)
        drafted_triage = triage(drafted)
        report["drafted"] = {
            "verdict": drafted_triage["verdict"],
            "capabilities": drafted["capabilities"],
            "findings": drafted_triage["findings"],
            "repairs": drafted_triage["repairs"],
        }
        draft_ok = drafted["capabilities"].get("submit_prompt") is True
        draft_detail = (
            f"submit_prompt={str(drafted['capabilities'].get('submit_prompt')).lower()}; "
            f"verdict={drafted_triage['verdict']}"
        )
        baseline_blocker = _first_flight_baseline_blocker(drafted, drafted_triage)
    else:
        drafted = {}
        drafted_triage = {}
        report["drafted"] = {"skipped": True, "reason": "composer was not empty"}
        draft_ok = False
        draft_detail = "blocked to preserve the existing composer"
        baseline_blocker = "composer was not empty; no drafted surface was measured"
    step("draft probe (send should be visible)", draft_ok, draft_detail)

    # 4. Unknown controls: the atlas only knows what it has been shown.
    phases = [("idle", idle)]
    if drafted:
        phases.append(("drafted", drafted))
    unknown_controls = _unknown_composer_controls_by_phase(phases)
    report["unknown_composer_controls"] = unknown_controls
    if unknown_controls:
        step("composer fully classified", False, f"{len(unknown_controls)} unrecognised control(s)")
        for control in unknown_controls:
            unknowns.append(
                f"Unclassified composer control: {control.get('selector_hint')} "
                f"(aria={control.get('aria_label')!r} testid={control.get('test_id')!r}; "
                f"observed_in={control.get('observed_in')}). "
                f"Add it to ROLE_ATLAS in extension/src/adapters/surface-probe.ts."
            )
    else:
        step("composer fully classified", True)

    if baseline_blocker is None and unknown_controls:
        baseline_blocker = "unclassified composer controls cannot become a known-good baseline"
    if baseline_blocker is None:
        store.promote(drafted)
        step("baseline promoted", True, "surface-watch and --diagnose now have a known-good reference")
    else:
        step("baseline promoted", False, baseline_blocker)

    surface_ready = composer_clean and draft_ok and baseline_blocker is None and not unknown_controls

    # 5. THE big unknown: what does an attachment chip actually look like?
    attachment_cleanup_ok = True
    if getattr(args, "learn_attachment", False):
        authentication = idle.get("authentication") or {}
        if authentication.get("posture") != "authenticated":
            error = (
                "ChatGPT is logged out; log in to ChatGPT in this browser profile before learning attachments"
                if authentication.get("posture") == "anonymous"
                else "ChatGPT authentication could not be verified; refusing attachment learning"
            )
            report["attachment"] = {"ok": False, "error": error, "authentication": authentication}
            step("attachment chip observed", False, error)
            unknowns.append(
                "Authenticate this browser profile, then rerun first-flight "
                "with --learn-attachment. Anonymous ChatGPT sessions cannot upload files."
            )
        elif not surface_ready:
            error = "attachment learning blocked because the measured surface is not a verified clean baseline"
            report["attachment"] = {"ok": False, "error": error}
            step("attachment chip observed", False, error)
        else:
            probe_file = Path(args.learn_attachment)
            result = engine.attach(probe_file)
            report["attachment"] = result.to_json()
            known_chips = [
                control for control in result.added_controls
                if control.get("classification") == "attachment-chip"
            ]
            unknown_candidates = [
                control for control in result.added_controls
                if control.get("classification") == "unknown"
            ]
            if result.ok and result.chip_present and known_chips:
                step("attachment chip observed", True, f"{len(known_chips)} known chip control(s)")
            elif result.ok and result.chip_present and unknown_candidates:
                step("attachment chip candidate observed", True, f"{len(unknown_candidates)} unclassified candidate(s)")
                print("", file=sys.stderr)
                print("[glassttyd] ATTACHMENT CHIP CANDIDATE — filename and control diff agree:", file=sys.stderr)
                for control in unknown_candidates:
                    print(f"[glassttyd]   selector : {control.get('selector_hint')}", file=sys.stderr)
                    print(f"[glassttyd]   testid   : {control.get('test_id')!r}", file=sys.stderr)
                    print(f"[glassttyd]   aria     : {control.get('aria_label')!r}", file=sys.stderr)
                    print(f"[glassttyd]   classes  : {control.get('class_tokens')}", file=sys.stderr)
                unknowns.append(
                    "Review the attachment-chip candidate above, then add it to ROLE_ATLAS as role 'attachment-chip' and to "
                    "mock_tab.build_mock_probe so the mock stops guessing at it."
                )
            elif result.ok:
                step(
                    "attachment chip observed",
                    False,
                    "the input accepted the file but no filename-backed or known chip witness appeared",
                )
            else:
                step("attachment chip observed", False, result.error or "attach failed")

            if result.composer_keys_before:
                cleanup = engine.clear_attachments(
                    result.composer_keys_before,
                    expected_name=result.name,
                    expected_name_visible_before=result.expected_name_visible_before,
                )
            else:
                cleanup = None
            attachment_cleanup_ok = bool(cleanup and cleanup.ok)
            report["attachment_cleanup"] = (
                cleanup.to_json() if cleanup else {
                    "ok": False,
                    "error": "the extension returned no pre-attachment composer witness; cleanup cannot be proved",
                }
            )
            step(
                "attachment cleanup verified",
                attachment_cleanup_ok,
                "file input and attachment controls returned to baseline"
                if attachment_cleanup_ok else report["attachment_cleanup"].get("error"),
            )
            if not attachment_cleanup_ok:
                unknowns.append(
                    "Attachment cleanup could not be proved. Do not submit from this composer until its file chip is visibly removed."
                )

    # 6. Optional live round trip.
    if getattr(args, "canary", False):
        canary_marker = "GLASSTTY-FIRST-FLIGHT-OK"
        if not surface_ready:
            report["canary"] = {"ok": False, "blocked": "surface preflight was not clean"}
            step("live round trip", False, "blocked because the surface preflight was not clean")
        elif not attachment_cleanup_ok:
            report["canary"] = {"ok": False, "blocked": "attachment cleanup was not verified"}
            step("live round trip", False, "blocked because a stale attachment may remain")
        else:
            turn = engine.send(f"Reply with exactly: {canary_marker}")
            report["canary"] = turn.to_json()
            exact = (turn.text or "").strip() == canary_marker
            report["canary_exact_match"] = exact
            step("live round trip", turn.ok and exact, turn.settle_reason)
            if turn.ok and not exact:
                unknowns.append("The turn settled but exact canary text did not match — check transcript selection.")

    report["unknowns"] = unknowns
    report["ok"] = _first_flight_ok(report, unknowns)
    report["failed_steps"] = [item["step"] for item in report["steps"] if not item["ok"]]
    print("", file=sys.stderr)
    if unknowns:
        print(f"[glassttyd] {len(unknowns)} thing(s) to resolve — hand these to Claude Code:", file=sys.stderr)
        for index, item in enumerate(unknowns, start=1):
            print(f"[glassttyd]   {index}. {item}", file=sys.stderr)
    else:
        print("[glassttyd] no unknowns. The mock and reality agree — which would be the first time.", file=sys.stderr)

    if getattr(args, "out", None):
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[glassttyd] wrote {args.out}", file=sys.stderr)

    _emit(report, args)
    return 0 if report["ok"] else 1


def cmd_stop(args: argparse.Namespace) -> int:
    """Abort a generation in progress. The adapter has always been able to find the
    stop control; until now nothing ever called it."""
    engine = _make_engine(args)
    ok = engine.stop()
    if not getattr(args, "quiet", False):
        print("[glassttyd] stopped generation" if ok else "[glassttyd] nothing was generating", file=sys.stderr)
    return 0 if ok else 1


def cmd_new_chat(args: argparse.Namespace) -> int:
    engine = _make_engine(args)
    ok = engine.new_chat()
    if not getattr(args, "quiet", False):
        print("[glassttyd] opened a new chat" if ok else "[glassttyd] could not find the new-chat control", file=sys.stderr)
    return 0 if ok else 1


def cmd_attach(args: argparse.Namespace) -> int:
    """Stage files in the composer without sending anything."""
    engine = _make_engine(args)
    results = []
    failed = False
    for path in _attachments(args):
        result = engine.attach(path)
        state = "chip rendered" if result.chip_present else "NO CHIP"
        accepted = result.ok and (result.chip_present or not engine.config.require_attachment)
        result_json = result.to_json()
        result_json["accepted"] = accepted
        results.append(result_json)
        marker = "ok" if accepted else "FAILED"
        print(f"[glassttyd] {marker}: {result.name} {result.bytes}B chunks={result.chunks} · {state}", file=sys.stderr)
        for warning in result.warnings:
            print(f"[glassttyd] warning: {warning}", file=sys.stderr)
        if result.error:
            print(f"[glassttyd] error: {result.error}", file=sys.stderr)
        if not accepted:
            failed = True
    _emit({"ok": not failed, "attachments": results}, args)
    return 1 if failed else 0


def cmd_mock_tab(args: argparse.Namespace) -> int:
    from .mock_tab import run_mock_tab

    target = _resolve_socket(args)
    if target.exists() and not getattr(args, "force", False):
        print(
            f"[glassttyd] a socket already exists at {target}. Another broker (real "
            f"browser or mock) may be running. Use --force to replace it.",
            file=sys.stderr,
        )
        return 3
    if target.exists():
        try:
            target.unlink()
        except OSError:
            pass
    return run_mock_tab(
        target,
        emit_generation=not getattr(args, "no_generation", False),
        drift=getattr(args, "drift", "none"),
        rules_path=Path(args.rules) if getattr(args, "rules", None) else None,
        verbose=not getattr(args, "quiet", False),
    )


def add_tab_target_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tab-id", type=int, help="Explicit browser tab id to target instead of the best supported tab")


def add_text_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text", action="store_true", help="When waiting, print only payload.text if available")


def add_timeout_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Seconds to wait on the broker socket before failing")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glassttyd")
    sub = parser.add_subparsers(dest="command", required=True)

    ping = sub.add_parser("ping", help="Verify a live local broker round trip")
    add_timeout_flag(ping)
    ping.set_defaults(func=cmd_ping)

    doctor = sub.add_parser("doctor", help="Inspect the local GlassTTY environment")
    doctor.add_argument('--pretty', action='store_true')
    doctor.set_defaults(func=cmd_doctor)

    surface_audit = sub.add_parser(
        "surface-audit",
        help="Audit a ChatGPT surface report/capsule/drill JSON from stdin or a file",
    )
    surface_audit.add_argument('input', nargs='?', default='-')
    surface_audit.add_argument('--pretty', action='store_true')
    surface_audit.set_defaults(func=cmd_surface_audit)

    surface_contract_build = sub.add_parser(
        "surface-contract-build",
        help="Build a ChatGPT UI drift contract from a known-good surface report",
    )
    surface_contract_build.add_argument('report')
    surface_contract_build.add_argument('--out')
    surface_contract_build.add_argument('--pretty', action='store_true')
    surface_contract_build.set_defaults(func=cmd_surface_contract_build)

    surface_contract_check = sub.add_parser(
        "surface-contract-check",
        help="Check a ChatGPT surface report against a saved UI drift contract",
    )
    surface_contract_check.add_argument('report')
    surface_contract_check.add_argument('--contract', required=True)
    surface_contract_check.add_argument('--pretty', action='store_true')
    surface_contract_check.set_defaults(func=cmd_surface_contract_check)

    proof_extension_readiness = sub.add_parser(
        "proof-extension-readiness",
        help="Check static extension/side-panel readiness for the ChatGPT live proof path",
    )
    proof_extension_readiness.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-extension-readiness.json'))
    proof_extension_readiness.add_argument('--require-build', action='store_true')
    proof_extension_readiness.add_argument('--pretty', action='store_true')
    proof_extension_readiness.set_defaults(func=cmd_proof_extension_readiness)

    proof_rehearse = sub.add_parser(
        "proof-rehearse",
        help="Build and evaluate an offline ChatGPT checkpoint proof rehearsal bundle",
    )
    proof_rehearse.add_argument('--surface-report')
    proof_rehearse.add_argument('--contract', default=os.fspath(_active_surface_contract_path()))
    proof_rehearse.add_argument('--out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal.json'))
    proof_rehearse.add_argument('--evaluation-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evaluation'))
    proof_rehearse.add_argument('--strict-surface', action='store_true')
    proof_rehearse.add_argument('--pretty', action='store_true')
    proof_rehearse.set_defaults(func=cmd_proof_rehearse)

    proof_preflight = sub.add_parser(
        "proof-preflight",
        help="Run static, drift-contract, and offline rehearsal gates before a live ChatGPT proof attempt",
    )
    proof_preflight.add_argument('--surface-report')
    proof_preflight.add_argument('--contract', default=os.fspath(_active_surface_contract_path()))
    proof_preflight.add_argument('--fixture')
    proof_preflight.add_argument('--out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-preflight.json'))
    proof_preflight.add_argument('--rehearsal-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal.json'))
    proof_preflight.add_argument('--evaluation-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evaluation'))
    proof_preflight.add_argument('--pretty', action='store_true')
    proof_preflight.set_defaults(func=cmd_proof_preflight)


    proof_export_pack = sub.add_parser(
        "proof-export-pack",
        help="Export a side-panel ChatGPT proof capture or rehearsal into the 30-slot evidence-pack layout",
    )
    proof_export_pack.add_argument('--input', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal.json'))
    proof_export_pack.add_argument('--pack-dir', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evidence-pack'))
    proof_export_pack.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-pack-export-summary.json'))
    proof_export_pack.add_argument('--clean', action='store_true')
    proof_export_pack.add_argument('--allow-placeholder-screenshot', action='store_true')
    proof_export_pack.add_argument('--no-placeholder-screenshot', action='store_true')
    proof_export_pack.add_argument('--require-ok', action='store_true')
    proof_export_pack.add_argument('--pretty', action='store_true')
    proof_export_pack.set_defaults(func=cmd_proof_export_pack)


    proof_recovery_vault = sub.add_parser(
        "proof-recovery-vault",
        help="Inspect, extract, and optionally ingest a side-panel recovery-vault JSON or proof JSON",
    )
    proof_recovery_vault.add_argument('--input', required=True)
    proof_recovery_vault.add_argument('--out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-first-proof-capture.from-recovery-vault.json'))
    proof_recovery_vault.add_argument('--redacted-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-first-proof-capture.from-recovery-vault.redacted.json'))
    proof_recovery_vault.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-recovery-vault-summary.json'))
    proof_recovery_vault.add_argument('--require-full-document', action='store_true')
    proof_recovery_vault.add_argument('--require-integrity-match', action='store_true')
    proof_recovery_vault.add_argument('--require-live-candidate', action='store_true')
    proof_recovery_vault.add_argument('--ingest', action='store_true')
    proof_recovery_vault.add_argument('--ingest-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-first-proof-capture.json'))
    proof_recovery_vault.add_argument('--ingest-redacted-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-first-proof-capture.redacted.json'))
    proof_recovery_vault.add_argument('--ingest-summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-ingest-summary.json'))
    proof_recovery_vault.add_argument('--finalize', action='store_true')
    proof_recovery_vault.add_argument('--pack-dir', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-recovery-vault-evidence-pack'))
    proof_recovery_vault.add_argument('--final-summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-finalize-summary.json'))
    proof_recovery_vault.add_argument('--export-summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-pack-export-summary.json'))
    proof_recovery_vault.add_argument('--check-summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-pack-check-summary.json'))
    proof_recovery_vault.add_argument('--clean', action='store_true')
    proof_recovery_vault.add_argument('--pretty', action='store_true')
    proof_recovery_vault.set_defaults(func=cmd_proof_recovery_vault)

    proof_transfer_audit = sub.add_parser(
        "proof-transfer-audit",
        help="Audit downloaded/recovered ChatGPT proof JSON transfer integrity before attempt audit/ingest",
    )
    proof_transfer_audit.add_argument('--input', required=True)
    proof_transfer_audit.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-transfer-audit.json'))
    proof_transfer_audit.add_argument('--no-require-proof-capture', action='store_true')
    proof_transfer_audit.add_argument('--require-ready-to-download', action='store_true')
    proof_transfer_audit.add_argument('--require-full-screenshot', action='store_true')
    proof_transfer_audit.add_argument('--pretty', action='store_true')
    proof_transfer_audit.set_defaults(func=cmd_proof_transfer_audit)

    proof_attempt_audit = sub.add_parser(
        "proof-attempt-audit",
        help="Audit ordered side-panel ChatGPT proof-attempt events before ingest/finalization",
    )
    proof_attempt_audit.add_argument('--input', required=True)
    proof_attempt_audit.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-attempt-audit.json'))
    proof_attempt_audit.add_argument('--require-ready-to-download', action='store_true')
    proof_attempt_audit.add_argument('--pretty', action='store_true')
    proof_attempt_audit.set_defaults(func=cmd_proof_attempt_audit)

    proof_ingest = sub.add_parser(
        "proof-ingest",
        help="Validate and normalize a downloaded side-panel ChatGPT proof JSON before finalization",
    )
    proof_ingest.add_argument('--input', required=True)
    proof_ingest.add_argument('--out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-first-proof-capture.json'))
    proof_ingest.add_argument('--redacted-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-first-proof-capture.redacted.json'))
    proof_ingest.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-ingest-summary.json'))
    proof_ingest.add_argument('--require-live-candidate', action='store_true')
    proof_ingest.add_argument('--finalize', action='store_true')
    proof_ingest.add_argument('--pack-dir', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-ingest-evidence-pack'))
    proof_ingest.add_argument('--final-summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-finalize-summary.json'))
    proof_ingest.add_argument('--export-summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-pack-export-summary.json'))
    proof_ingest.add_argument('--check-summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-pack-check-summary.json'))
    proof_ingest.add_argument('--clean', action='store_true')
    proof_ingest.add_argument('--pretty', action='store_true')
    proof_ingest.set_defaults(func=cmd_proof_ingest)

    proof_finalize_pack = sub.add_parser(
        "proof-finalize-pack",
        help="Export and check a ChatGPT proof capture as one operator-facing finalization gate",
    )
    proof_finalize_pack.add_argument('--input', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal.json'))
    proof_finalize_pack.add_argument('--pack-dir', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evidence-pack'))
    proof_finalize_pack.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-finalize-summary.json'))
    proof_finalize_pack.add_argument('--export-summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-pack-export-summary.json'))
    proof_finalize_pack.add_argument('--check-summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-pack-check-summary.json'))
    proof_finalize_pack.add_argument('--clean', action='store_true')
    proof_finalize_pack.add_argument('--require-live', action='store_true')
    proof_finalize_pack.add_argument('--allow-placeholder-screenshot', action='store_true')
    proof_finalize_pack.add_argument('--no-placeholder-screenshot', action='store_true')
    proof_finalize_pack.add_argument('--require-privacy-pass', action='store_true')
    proof_finalize_pack.add_argument('--privacy-reviewer')
    proof_finalize_pack.add_argument('--privacy-decision', choices=['pending', 'pass', 'fail'], default='pending')
    proof_finalize_pack.add_argument('--privacy-attest-screenshot-reviewed', action='store_true')
    proof_finalize_pack.add_argument('--privacy-attest-no-unrelated-content', action='store_true')
    proof_finalize_pack.add_argument('--privacy-attest-local-only', action='store_true')
    proof_finalize_pack.add_argument('--pretty', action='store_true')
    proof_finalize_pack.set_defaults(func=cmd_proof_finalize_pack)

    proof_check_pack = sub.add_parser(
        "proof-check-pack",
        help="Check a ChatGPT 30-slot evidence pack for completeness and live/rehearsal safety",
    )
    proof_check_pack.add_argument('--pack-dir', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evidence-pack'))
    proof_check_pack.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-pack-check-summary.json'))
    proof_check_pack.add_argument('--require-live', action='store_true')
    proof_check_pack.add_argument('--no-rehearsal', action='store_true')
    proof_check_pack.add_argument('--require-privacy-pass', action='store_true')
    proof_check_pack.add_argument('--pretty', action='store_true')
    proof_check_pack.set_defaults(func=cmd_proof_check_pack)

    proof_pack_integrity = sub.add_parser(
        "proof-pack-integrity",
        help="Create or verify an internal integrity manifest for a ChatGPT evidence pack",
    )
    proof_pack_integrity.add_argument('--pack-dir', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evidence-pack'))
    proof_pack_integrity.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-pack-integrity-summary.json'))
    proof_pack_integrity.add_argument('--write-pack-file', action='store_true')
    proof_pack_integrity.add_argument('--refresh-ledger', action='store_true')
    proof_pack_integrity.add_argument('--require-existing', action='store_true')
    proof_pack_integrity.add_argument('--require-existing-match', action='store_true')
    proof_pack_integrity.add_argument('--require-ok', action='store_true')
    proof_pack_integrity.add_argument('--pretty', action='store_true')
    proof_pack_integrity.set_defaults(func=cmd_proof_pack_integrity)

    proof_privacy_review = sub.add_parser(
        "proof-privacy-review",
        help="Build/check structured privacy-redaction review for a ChatGPT proof evidence pack",
    )
    proof_privacy_review.add_argument('--pack-dir', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evidence-pack'))
    proof_privacy_review.add_argument('--json-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-privacy-review.json'))
    proof_privacy_review.add_argument('--markdown-out')
    proof_privacy_review.add_argument('--reviewer')
    proof_privacy_review.add_argument('--reviewer-contact')
    proof_privacy_review.add_argument('--decision', choices=['pending', 'pass', 'fail'], default='pending')
    proof_privacy_review.add_argument('--require-live', action='store_true')
    proof_privacy_review.add_argument('--require-pass', action='store_true')
    proof_privacy_review.add_argument('--attest-screenshot-reviewed', action='store_true')
    proof_privacy_review.add_argument('--attest-no-unrelated-content', action='store_true')
    proof_privacy_review.add_argument('--attest-local-only', action='store_true')
    proof_privacy_review.add_argument('--pretty', action='store_true')
    proof_privacy_review.set_defaults(func=cmd_proof_privacy_review)

    proof_publish_bundle = sub.add_parser(
        "proof-publish-bundle",
        help="Create a support/publish zip only from a live, privacy-reviewed ChatGPT evidence pack",
    )
    proof_publish_bundle.add_argument('--pack-dir', default=os.fspath(_project_root() / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack'))
    proof_publish_bundle.add_argument('--out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-publish-bundle.zip'))
    proof_publish_bundle.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-publish-summary.json'))
    proof_publish_bundle.add_argument('--no-require-live', action='store_true')
    proof_publish_bundle.add_argument('--no-require-privacy-pass', action='store_true')
    proof_publish_bundle.add_argument('--pretty', action='store_true')
    proof_publish_bundle.set_defaults(func=cmd_proof_publish_bundle)

    proof_publish_verify = sub.add_parser(
        "proof-publish-verify",
        help="Verify a ChatGPT proof publish/support zip after transfer",
    )
    proof_publish_verify.add_argument('--bundle', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-publish-bundle.zip'))
    proof_publish_verify.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-publish-verify-summary.json'))
    proof_publish_verify.add_argument('--expected-sha256')
    proof_publish_verify.add_argument('--no-require-live', action='store_true')
    proof_publish_verify.add_argument('--no-require-privacy-pass', action='store_true')
    proof_publish_verify.add_argument('--pretty', action='store_true')
    proof_publish_verify.set_defaults(func=cmd_proof_publish_verify)


    proof_autopilot = sub.add_parser(
        "proof-autopilot",
        help="Run a guided ChatGPT proof pipeline autopilot that only advances safe/live-gated steps",
    )
    proof_autopilot.add_argument('--input')
    proof_autopilot.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-autopilot-summary.json'))
    proof_autopilot.add_argument('--live-pack-dir', default=os.fspath(_project_root() / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack'))
    proof_autopilot.add_argument('--publish-bundle', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-publish-bundle.zip'))
    proof_autopilot.add_argument('--execute-safe', action='store_true')
    proof_autopilot.add_argument('--execute-live', action='store_true')
    proof_autopilot.add_argument('--clean', action='store_true')
    proof_autopilot.add_argument('--require-complete', action='store_true')
    proof_autopilot.add_argument('--reviewer')
    proof_autopilot.add_argument('--decision', choices=['pending', 'pass', 'fail'], default='pending')
    proof_autopilot.add_argument('--attest-screenshot-reviewed', action='store_true')
    proof_autopilot.add_argument('--attest-no-unrelated-content', action='store_true')
    proof_autopilot.add_argument('--attest-local-only', action='store_true')
    proof_autopilot.add_argument('--pretty', action='store_true')
    proof_autopilot.set_defaults(func=cmd_proof_autopilot)


    proof_status = sub.add_parser(
        "proof-status",
        help="Report the resumable state of the ChatGPT proof pipeline and the exact next operator command",
    )
    proof_status.add_argument('--summary-out', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-operator-state.json'))
    proof_status.add_argument('--live-pack-dir', default=os.fspath(_project_root() / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack'))
    proof_status.add_argument('--rehearsal-pack-dir', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evidence-pack'))
    proof_status.add_argument('--publish-bundle', default=os.fspath(_project_root() / 'validation' / 'latest' / 'chatgpt-proof-publish-bundle.zip'))
    proof_status.add_argument('--no-require-live', action='store_true')
    proof_status.add_argument('--pretty', action='store_true')
    proof_status.set_defaults(func=cmd_proof_status)

    tail = sub.add_parser("tail-events", help="Print recent native-host events")
    tail.add_argument("--lines", type=int, default=20)
    tail.set_defaults(func=cmd_tail)

    socket_status = sub.add_parser("socket-status", help="Check the local broker socket")
    add_timeout_flag(socket_status)
    socket_status.set_defaults(func=cmd_socket_status)

    watch = sub.add_parser("watch", help="Watch broker and browser events as JSON lines")
    add_timeout_flag(watch)
    watch.set_defaults(func=cmd_watch)

    request = sub.add_parser("request", help="Send an arbitrary browser request")
    request.add_argument("type")
    request.add_argument("--payload", default="{}")
    request.add_argument("--wait", action="store_true")
    add_timeout_flag(request)
    add_tab_target_argument(request)
    request.set_defaults(func=cmd_request)

    bridge_status = sub.add_parser("bridge-status", help="Request bridge.status from the extension")
    bridge_status.add_argument("--wait", action="store_true")
    add_timeout_flag(bridge_status)
    add_tab_target_argument(bridge_status)
    bridge_status.set_defaults(func=cmd_bridge_status)

    contexts = sub.add_parser("contexts", help="Request bridge.contexts from the extension for MV3 context diagnostics")
    contexts.add_argument("--wait", action="store_true")
    contexts.add_argument("--ensure-offscreen", action="store_true", help="Ensure the hidden offscreen diagnostics document before reading contexts")
    add_timeout_flag(contexts)
    add_tab_target_argument(contexts)
    contexts.set_defaults(func=cmd_contexts)

    trace = sub.add_parser("trace", help="Request bridge.trace from the extension for recent background events")
    trace.add_argument("--wait", action="store_true")
    trace.add_argument("--limit", type=int, default=40)
    add_timeout_flag(trace)
    add_tab_target_argument(trace)
    trace.set_defaults(func=cmd_trace)

    probe = sub.add_parser("probe", help="Request bridge.probe for a combined live diagnostics snapshot")
    probe.add_argument("--wait", action="store_true")
    probe.add_argument("--limit", type=int, default=60)
    probe.add_argument("--await-health-ms", type=int, default=1500)
    probe.add_argument("--ensure-offscreen", action="store_true", help="Ensure the hidden offscreen diagnostics document before collecting the probe snapshot")
    add_timeout_flag(probe)
    add_tab_target_argument(probe)
    probe.set_defaults(func=cmd_probe)

    content_script_experiment = sub.add_parser("content-script-experiment", help="Read the active dynamic content-script experiment and effective coverage policy")
    add_timeout_flag(content_script_experiment)
    add_tab_target_argument(content_script_experiment)
    content_script_experiment.set_defaults(func=cmd_content_script_experiment)

    set_content_script_experiment = sub.add_parser("set-content-script-experiment", help="Register a non-persistent dynamic content-script experiment for frame-coverage proof")
    set_content_script_experiment.add_argument('experiment_id', choices=['manifest_all_frames', 'manifest_match_about_blank', 'manifest_match_origin_as_fallback'])
    set_content_script_experiment.add_argument("--wait", action="store_true")
    add_timeout_flag(set_content_script_experiment)
    add_tab_target_argument(set_content_script_experiment)
    set_content_script_experiment.set_defaults(func=cmd_set_content_script_experiment)

    clear_content_script_experiment = sub.add_parser("clear-content-script-experiment", help="Clear GlassTTY's non-persistent dynamic content-script experiment registrations")
    clear_content_script_experiment.add_argument("--wait", action="store_true")
    add_timeout_flag(clear_content_script_experiment)
    add_tab_target_argument(clear_content_script_experiment)
    clear_content_script_experiment.set_defaults(func=cmd_clear_content_script_experiment)

    offscreen_dom = sub.add_parser("offscreen-dom", help="Parse saved HTML through the hidden offscreen document for DOM-capable diagnostics")
    offscreen_dom.add_argument("html_file", help="HTML file to parse, or '-' to read HTML from stdin")
    offscreen_dom.add_argument("--selector", action="append", default=[], help="CSS selector to count in the parsed HTML (repeatable)")
    offscreen_dom.add_argument("--base-url", default=None, help="Optional base URL used to resolve relative links and forms in the parsed HTML")
    offscreen_dom.add_argument("--max-candidates", type=int, default=8, help="Maximum editable candidates/headings to include in the summary")
    add_timeout_flag(offscreen_dom)
    add_tab_target_argument(offscreen_dom)
    offscreen_dom.set_defaults(func=cmd_offscreen_dom)

    offscreen_fixture = sub.add_parser("offscreen-fixture", help="Build a generic fixture-like capture from saved HTML through the hidden offscreen document")
    offscreen_fixture.add_argument("html_file", help="HTML file to parse, or '-' to read HTML from stdin")
    offscreen_fixture.add_argument("--selector", action="append", default=[], help="Extra CSS selectors to count in the parsed HTML (repeatable)")
    offscreen_fixture.add_argument("--base-url", default=None, help="Optional base URL used to resolve relative links and forms in the parsed HTML")
    offscreen_fixture.add_argument("--max-candidates", type=int, default=8, help="Maximum input/output candidates to include in the fixture capture")
    add_timeout_flag(offscreen_fixture)
    add_tab_target_argument(offscreen_fixture)
    offscreen_fixture.set_defaults(func=cmd_offscreen_fixture)

    list_tabs = sub.add_parser("list-tabs", help="Print supported tabs from bridge.status as tab-separated rows")
    add_timeout_flag(list_tabs)
    add_tab_target_argument(list_tabs)
    list_tabs.set_defaults(func=cmd_list_tabs)

    list_receivers = sub.add_parser("list-receivers", help="Print observed receiver inventory from bridge.status as tab-separated rows")
    add_timeout_flag(list_receivers)
    add_tab_target_argument(list_receivers)
    list_receivers.set_defaults(func=cmd_list_receivers)

    select_tab = sub.add_parser("select-tab", help="Persistently target a supported tab inside the extension")
    select_tab.add_argument("tab_id", type=int)
    select_tab.add_argument("--wait", action="store_true")
    add_timeout_flag(select_tab)
    select_tab.set_defaults(func=cmd_select_tab)

    clear_target_tab = sub.add_parser("clear-target-tab", help="Clear the persistently selected target tab")
    clear_target_tab.add_argument("--wait", action="store_true")
    add_timeout_flag(clear_target_tab)
    clear_target_tab.set_defaults(func=cmd_clear_target_tab)

    select_receiver = sub.add_parser("select-receiver", help="Persistently override the selected receiver for a supported tab")
    select_receiver.add_argument("tab_id", type=int)
    select_receiver.add_argument("receiver_key")
    select_receiver.add_argument("--wait", action="store_true")
    add_timeout_flag(select_receiver)
    select_receiver.set_defaults(func=cmd_select_receiver)

    clear_receiver_override = sub.add_parser("clear-receiver-override", help="Clear the persisted receiver override for a supported tab")
    clear_receiver_override.add_argument("tab_id", type=int)
    clear_receiver_override.add_argument("--wait", action="store_true")
    add_timeout_flag(clear_receiver_override)
    clear_receiver_override.set_defaults(func=cmd_clear_receiver_override)

    resolve_receiver = sub.add_parser("resolve-receiver", help="Resolve a receiver key for a supported tab using human-facing frame filters")
    resolve_receiver.add_argument('tab_id', type=int)
    resolve_receiver.add_argument('--receiver-key')
    resolve_receiver.add_argument('--frame-id', type=int)
    resolve_receiver.add_argument('--document-id')
    resolve_receiver.add_argument('--url-contains')
    resolve_receiver.add_argument('--frame-type')
    resolve_receiver.add_argument('--frame-host-contains')
    resolve_receiver.add_argument('--frame-path-contains')
    resolve_receiver.add_argument('--frame-depth', type=int)
    resolve_receiver.add_argument('--top-frame', action='store_true', help='Match any outermost frame, including non-zero prerender/cached outermost frames')
    resolve_receiver.add_argument('--active-outermost', action='store_true', help='Match receivers whose frame is outermost and whose lifecycle is active or unknown')
    resolve_receiver.add_argument('--document-lifecycle', choices=['prerender', 'active', 'cached', 'pending_deletion'])
    resolve_receiver.add_argument('--ready-only', action='store_true')
    resolve_receiver.add_argument('--explain', action='store_true', help='Include resolver ranking details explaining why the chosen receiver won')
    resolve_receiver.add_argument('--first', action='store_true', help='Return the first ranked match even when multiple receivers match')
    resolve_receiver.add_argument('--set-override', action='store_true', help='Persist the resolved receiver as the active override for the tab')
    resolve_receiver.add_argument('--wait', action='store_true', help='When used with --set-override, wait for the override response event')
    add_timeout_flag(resolve_receiver)
    resolve_receiver.set_defaults(func=cmd_resolve_receiver)

    read_prompt = sub.add_parser("read-prompt", help="Request prompt.read from the active or selected supported tab")
    read_prompt.add_argument("--wait", action="store_true")
    add_text_flag(read_prompt)
    add_timeout_flag(read_prompt)
    add_tab_target_argument(read_prompt)
    read_prompt.set_defaults(func=cmd_read_prompt)

    read_latest = sub.add_parser("read-latest", help="Request transcript.latest from the active or selected supported tab")
    read_latest.add_argument("--wait", action="store_true")
    add_text_flag(read_latest)
    add_timeout_flag(read_latest)
    add_tab_target_argument(read_latest)
    read_latest.set_defaults(func=cmd_read_latest)

    write_prompt = sub.add_parser("write-prompt", help="Request prompt.write on the active or selected supported tab")
    write_prompt.add_argument("text")
    write_prompt.add_argument("--wait", action="store_true")
    add_timeout_flag(write_prompt)
    add_tab_target_argument(write_prompt)
    write_prompt.set_defaults(func=cmd_write_prompt)

    submit_prompt = sub.add_parser("submit-prompt", help="Request prompt.submit on the active or selected supported tab")
    submit_prompt.add_argument("--wait", action="store_true")
    add_timeout_flag(submit_prompt)
    add_tab_target_argument(submit_prompt)
    submit_prompt.set_defaults(func=cmd_submit_prompt)

    read_selection = sub.add_parser("read-selection", help="Request selection.read on the active or selected supported tab")
    read_selection.add_argument("--wait", action="store_true")
    add_text_flag(read_selection)
    add_timeout_flag(read_selection)
    add_tab_target_argument(read_selection)
    read_selection.set_defaults(func=cmd_read_selection)

    state_snapshot = sub.add_parser("state-snapshot", help="Request state.snapshot on the active or selected supported tab")
    state_snapshot.add_argument("--wait", action="store_true")
    add_timeout_flag(state_snapshot)
    add_tab_target_argument(state_snapshot)
    state_snapshot.set_defaults(func=cmd_state_snapshot)

    debug_candidates = sub.add_parser("debug-candidates", help="Request debug.dom_candidates from the active or selected supported tab")
    debug_candidates.add_argument("--wait", action="store_true")
    add_timeout_flag(debug_candidates)
    add_tab_target_argument(debug_candidates)
    debug_candidates.set_defaults(func=cmd_debug_candidates)

    capture_fixture = sub.add_parser("capture-fixture", help="Capture a rich fixture from the active or selected supported tab and save it to disk")
    capture_fixture.add_argument("--output-dir", help="Directory for saved fixture JSON files")
    add_timeout_flag(capture_fixture)
    add_tab_target_argument(capture_fixture)
    capture_fixture.set_defaults(func=cmd_capture_fixture)

    # -- rev0353 conversation commands ------------------------------------- #
    def add_engine_flags(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--tab-id", type=int, help="Target a specific supported tab instead of the active one")
        parser.add_argument("--socket", help="Override the broker socket path (defaults to the daemon socket)")
        parser.add_argument("--poll-interval", type=float, default=1.0, help="Seconds between generation-state polls")
        parser.add_argument("--max-wait", type=float, default=180.0, help="Hard ceiling in seconds for one answer to settle")
        parser.add_argument("--start-grace", type=float, default=15.0, help="Seconds to wait for generation to begin before giving up")
        parser.add_argument("--settle-polls", type=int, default=2, help="Consecutive stable+settled polls required to accept an answer")
        parser.add_argument("--no-continue", action="store_true", help="Do not auto-click 'Continue generating'")
        parser.add_argument("--max-continues", type=int, default=12, help="Safety cap on automatic continue clicks")
        parser.add_argument("--request-timeout", type=float, default=20.0, help="Per bridge-request timeout in seconds")
        parser.add_argument("--require-readback", action="store_true", help="Fail if the composer readback does not match the prompt exactly")
        parser.add_argument("--debug-snapshots", action="store_true", help="Attach raw poll snapshots to --json output")
        parser.add_argument("--attach-timeout", type=float, default=180.0, help="Per-file upload ceiling in seconds")
        parser.add_argument("--chip-wait", type=float, default=30.0, help="Seconds to wait for the attachment chip to render")
        parser.add_argument("--no-require-attachment", action="store_true", help="Submit even if an attachment could not be witnessed (risks a fileless prompt)")

    ask = sub.add_parser("ask", help="Send one prompt to ChatGPT and print the settled answer")
    ask.add_argument("prompt", nargs="?", help="Prompt text (or use --file / stdin)")
    ask.add_argument("--file", help="Read the prompt from a file")
    ask.add_argument("--stdin", action="store_true", help="Force reading the prompt from stdin")
    ask.add_argument("--out", help="Write the answer text to a file")
    ask.add_argument("--json", action="store_true", help="Print the full structured turn result as JSON")
    ask.add_argument("--no-submit", action="store_true", help="Stage the prompt in the composer without submitting")
    ask.add_argument("--quiet", action="store_true", help="Suppress the status line on stderr")
    ask.add_argument("--diagnose", action="store_true", help="On failure, probe the surface and explain what broke")
    ask.add_argument("--attach", action="append", metavar="PATH", help="Attach a file to the prompt (repeatable)")
    ask.add_argument("--new-chat", action="store_true", help="Start a fresh conversation before sending")
    add_engine_flags(ask)
    ask.set_defaults(func=cmd_ask)

    chat = sub.add_parser("chat", help="Interactive ChatGPT REPL over the commandline")
    chat.add_argument("--out", help="Append each turn to a JSONL transcript file")
    chat.add_argument("--json", action="store_true", help="(reserved) structured output")
    add_engine_flags(chat)
    chat.set_defaults(func=cmd_chat)

    run = sub.add_parser("run", help="Run a queue of prompts and capture each response to disk")
    run.add_argument("queue", help="Queue file: JSONL (one prompt/object per line) or blocks (prompts split by '---')")
    run.add_argument("--out-dir", help="Directory to write per-prompt responses and transcript.jsonl")
    run.add_argument("--format", choices=["auto", "jsonl", "blocks"], default="auto", help="Queue file format (default: auto by extension)")
    run.add_argument("--var", action="append", metavar="KEY=VALUE", help="Template variable for {{KEY}} substitution (repeatable)")
    run.add_argument("--stop-on-error", action="store_true", help="Stop at the first turn that does not settle")
    run.add_argument("--resume", action="store_true", help="Resume exact verified inputs; refuse changed or ambiguously submitted turns (requires --out-dir)")
    run.add_argument("--min-delay", type=float, default=0.0, help="Minimum seconds to pace between prompts")
    run.add_argument("--max-delay", type=float, default=0.0, help="Maximum seconds to pace between prompts (random in [min,max]); 0 disables pacing")
    run.add_argument("--json", action="store_true", help="Print a JSON summary + records instead of a status line")
    run.add_argument("--quiet", action="store_true", help="Suppress per-prompt progress on stderr")
    run.add_argument("--diagnose", action="store_true", help="On the first failure, probe the surface and explain what broke")
    run.add_argument("--attach", action="append", metavar="PATH", help="Attach a file to every prompt in the queue (repeatable; per-item `attach` in JSONL also works)")
    add_engine_flags(run)
    run.set_defaults(func=cmd_run)

    mock_tab = sub.add_parser("mock-tab", help="Run an offline mock ChatGPT tab so ask/chat/run work without a browser")
    mock_tab.add_argument("--socket", help="Broker socket path to bind (defaults to the daemon socket)")
    mock_tab.add_argument("--no-generation", action="store_true", help="Do not emit the generation lifecycle (exercises text-stability fallback)")
    mock_tab.add_argument("--drift", default="none", help="Simulate a ChatGPT UI drift scenario (see `glassttyd surface-scenarios`)")
    mock_tab.add_argument("--rules", help="JSON file of {contains, reply, stall, refuse} response rules")
    mock_tab.add_argument("--force", action="store_true", help="Replace an existing socket file if present")
    mock_tab.add_argument("--quiet", action="store_true", help="Suppress mock-tab log lines")
    mock_tab.set_defaults(func=cmd_mock_tab)

    # -- rev0354 surface intelligence -------------------------------------- #
    def add_surface_flags(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--store", help="Surface history directory (default: $GLASSTTY_HOME/surface)")
        parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    surface_snapshot = sub.add_parser("surface-snapshot", help="Capture the live ChatGPT surface into the history store")
    surface_snapshot.add_argument("--label", help="Human label for this snapshot")
    surface_snapshot.add_argument("--promote", action="store_true", help="Also promote this snapshot to the known-good baseline")
    surface_snapshot.add_argument("--probe-with-draft", action="store_true", help="Stage a harmless draft first so the send control is actually rendered (never submits)")
    add_surface_flags(surface_snapshot)
    add_engine_flags(surface_snapshot)
    surface_snapshot.set_defaults(func=cmd_surface_snapshot)

    surface_diff = sub.add_parser("surface-diff", help="Diff two surfaces (baseline | latest | live | a snapshot path)")
    surface_diff.add_argument("--before", default="baseline", help="baseline | latest | live | path (default: baseline)")
    surface_diff.add_argument("--after", default="live", help="baseline | latest | live | path (default: live)")
    add_surface_flags(surface_diff)
    add_engine_flags(surface_diff)
    surface_diff.set_defaults(func=cmd_surface_diff)

    surface_triage = sub.add_parser("surface-triage", help="Diagnose the live surface: what drifted, what it breaks, how to repair it")
    surface_triage.add_argument("--input", help="Triage a saved snapshot/probe instead of probing live")
    surface_triage.add_argument("--no-baseline", action="store_true", help="Do not compare against the recorded baseline")
    surface_triage.add_argument("--no-save", action="store_true", help="Do not store the captured snapshot")
    surface_triage.add_argument("--require-ok", action="store_true", help="Exit non-zero unless the verdict is surface-ok")
    surface_triage.add_argument("--probe-with-draft", action="store_true", help="Stage a harmless draft first so the send control is actually rendered (never submits)")
    add_surface_flags(surface_triage)
    add_engine_flags(surface_triage)
    surface_triage.set_defaults(func=cmd_surface_triage)

    surface_history = sub.add_parser("surface-history", help="Show how the ChatGPT surface has changed over time")
    surface_history.add_argument("--json", action="store_true", help="Emit the timeline as JSON")
    add_surface_flags(surface_history)
    surface_history.set_defaults(func=cmd_surface_history)

    surface_watch = sub.add_parser("surface-watch", help="Poll the live surface and alert the moment it drifts")
    surface_watch.add_argument("--interval", type=float, default=60.0, help="Seconds between probes")
    surface_watch.add_argument("--once", action="store_true", help="Exit after the first detected change")
    surface_watch.add_argument("--json", action="store_true", help="Emit the triage report as JSON on change")
    add_surface_flags(surface_watch)
    add_engine_flags(surface_watch)
    surface_watch.set_defaults(func=cmd_surface_watch)

    surface_repair = sub.add_parser("surface-repair", help="Apply a confident surface repair to the live adapter without rebuilding it")
    surface_repair.add_argument("--apply", action="store_true", help="Actually push the override to the extension (default: dry run)")
    surface_repair.add_argument("--force", action="store_true", help="Apply even low-confidence candidates")
    surface_repair.add_argument("--set", action="append", metavar="ANCHOR=SELECTOR", help="Set an override by hand (repeatable)")
    surface_repair.add_argument("--clear", action="store_true", help="Remove all runtime overrides")
    surface_repair.add_argument("--quiet", action="store_true", help="Suppress the stderr summary")
    add_surface_flags(surface_repair)
    add_engine_flags(surface_repair)
    surface_repair.set_defaults(func=cmd_surface_repair)

    surface_overrides = sub.add_parser("surface-overrides", help="Show the runtime selector overrides currently in force")
    add_surface_flags(surface_overrides)
    add_engine_flags(surface_overrides)
    surface_overrides.set_defaults(func=cmd_surface_overrides)

    first_flight = sub.add_parser("first-flight", help="Measure a real ChatGPT tab against GlassTTY's assumptions (read-mostly)")
    first_flight.add_argument("--learn-attachment", metavar="PATH", help="Attach this small file once to discover the attachment-chip selector, then clear it")
    first_flight.add_argument("--canary", action="store_true", help="Also send one real prompt and verify the round trip")
    first_flight.add_argument("--out", help="Write the full report to a JSON file")
    add_surface_flags(first_flight)
    add_engine_flags(first_flight)
    first_flight.set_defaults(func=cmd_first_flight)

    stop = sub.add_parser("stop", help="Abort a generation that is in progress")
    stop.add_argument("--quiet", action="store_true")
    add_engine_flags(stop)
    stop.set_defaults(func=cmd_stop)

    new_chat = sub.add_parser("new-chat", help="Open a fresh ChatGPT conversation")
    new_chat.add_argument("--quiet", action="store_true")
    add_engine_flags(new_chat)
    new_chat.set_defaults(func=cmd_new_chat)

    attach = sub.add_parser("attach", help="Stage files in the composer without sending")
    attach.add_argument("--attach", action="append", metavar="PATH", required=True, help="File to attach (repeatable)")
    add_surface_flags(attach)
    add_engine_flags(attach)
    attach.set_defaults(func=cmd_attach)

    surface_scenarios = sub.add_parser("surface-scenarios", help="List the drift scenarios the mock tab can rehearse")
    surface_scenarios.add_argument("--json", action="store_true", help="Emit as JSON")
    surface_scenarios.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    surface_scenarios.set_defaults(func=cmd_surface_scenarios)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
