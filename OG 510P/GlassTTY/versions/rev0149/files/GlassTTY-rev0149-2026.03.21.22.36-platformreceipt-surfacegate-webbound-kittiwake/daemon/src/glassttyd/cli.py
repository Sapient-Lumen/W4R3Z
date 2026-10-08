from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
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


def cmd_ping(_args: argparse.Namespace) -> int:
    emit_json({"ok": True, "tool": "glassttyd", "mode": "local-cli"})
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[3]
    script = root / 'scripts' / 'doctor.py'
    argv = [sys.executable, os.fspath(script)]
    if args.pretty:
        argv.append('--pretty')
    result = subprocess.run(argv, check=True, capture_output=True, text=True)
    print(result.stdout, end='')
    return 0


def cmd_index_fixtures(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[3]
    script = root / 'scripts' / 'index-fixtures.py'
    argv = [sys.executable, os.fspath(script), args.root]
    if args.pretty:
        argv.append('--pretty')
    result = subprocess.run(argv, check=True, capture_output=True, text=True)
    print(result.stdout, end='')
    return 0


def cmd_compare_fixtures(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[3]
    script = root / 'scripts' / 'compare-fixtures.py'
    argv = [sys.executable, os.fspath(script), args.left, args.right]
    if args.pretty:
        argv.append('--pretty')
    result = subprocess.run(argv, check=True, capture_output=True, text=True)
    print(result.stdout, end='')
    return 0


def cmd_seed_fixture_corpus(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[3]
    script = root / 'scripts' / 'seed-fixture-corpus.py'
    argv = [sys.executable, os.fspath(script), args.output_dir]
    if args.force:
        argv.append('--force')
    result = subprocess.run(argv, check=True, capture_output=True, text=True)
    print(result.stdout, end='')
    return 0


def cmd_plan_fixture(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[3]
    script = root / 'scripts' / 'plan-fixture.py'
    argv = [sys.executable, os.fspath(script), args.fixture]
    if args.pretty:
        argv.append('--pretty')
    result = subprocess.run(argv, check=True, capture_output=True, text=True)
    print(result.stdout, end='')
    return 0




def cmd_native_message_budget(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[3]
    script = root / 'scripts' / 'native-message-budget.py'
    argv = [sys.executable, os.fspath(script), *args.path]
    if args.pretty:
        argv.append('--pretty')
    result = subprocess.run(argv, check=True, capture_output=True, text=True)
    print(result.stdout, end='')
    return 0



def cmd_compare_coverage_experiments(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[3]
    script = root / 'scripts' / 'compare-coverage-experiments.py'
    argv = [sys.executable, os.fspath(script), args.baseline, args.candidate]
    if args.experiment_id:
        argv.extend(['--experiment-id', args.experiment_id])
    if args.pretty:
        argv.append('--pretty')
    result = subprocess.run(argv, check=True, capture_output=True, text=True)
    print(result.stdout, end='')
    return 0

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


def add_tab_target_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tab-id", type=int, help="Explicit browser tab id to target instead of the best supported tab")


def add_text_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text", action="store_true", help="When waiting, print only payload.text if available")


def add_timeout_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Seconds to wait on the broker socket before failing")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glassttyd")
    sub = parser.add_subparsers(dest="command", required=True)

    ping = sub.add_parser("ping", help="Local smoke test")
    ping.set_defaults(func=cmd_ping)

    doctor = sub.add_parser("doctor", help="Inspect the local GlassTTY environment")
    doctor.add_argument('--pretty', action='store_true')
    doctor.set_defaults(func=cmd_doctor)

    index_fixtures = sub.add_parser("index-fixtures", help="Summarize saved fixture JSON files")
    index_fixtures.add_argument('root', nargs='?', default='fixtures')
    index_fixtures.add_argument('--pretty', action='store_true')
    index_fixtures.set_defaults(func=cmd_index_fixtures)

    compare_fixtures = sub.add_parser("compare-fixtures", help="Compare two saved fixture JSON files")
    compare_fixtures.add_argument('left')
    compare_fixtures.add_argument('right')
    compare_fixtures.add_argument('--pretty', action='store_true')
    compare_fixtures.set_defaults(func=cmd_compare_fixtures)

    seed_fixture_corpus = sub.add_parser("seed-fixture-corpus", help="Write a deterministic sample fixture corpus")
    seed_fixture_corpus.add_argument('output_dir', nargs='?', default='fixtures/corpus')
    seed_fixture_corpus.add_argument('--force', action='store_true')
    seed_fixture_corpus.set_defaults(func=cmd_seed_fixture_corpus)

    plan_fixture = sub.add_parser("plan-fixture", help="Generate an interaction plan and user-facing locator hints from a saved fixture")
    plan_fixture.add_argument('fixture')
    plan_fixture.add_argument('--pretty', action='store_true')
    plan_fixture.set_defaults(func=cmd_plan_fixture)

    native_message_budget = sub.add_parser("native-message-budget", help="Estimate native-messaging size budget usage for saved JSON artifacts")
    native_message_budget.add_argument('path', nargs='+')
    native_message_budget.add_argument('--pretty', action='store_true')
    native_message_budget.set_defaults(func=cmd_native_message_budget)

    overflow_report = sub.add_parser("overflow-report", help="Summarize the latest oversized native-host outbound artifact without dumping the full payload")
    overflow_report.add_argument('--artifact', help='Optional explicit oversized-host-outbound artifact JSON path')
    overflow_report.add_argument('--include-message', action='store_true', help='Include the full preserved oversized message in the JSON output')
    overflow_report.set_defaults(func=cmd_overflow_report)

    overflow_prune = sub.add_parser("overflow-prune", help="Plan or apply retention for oversized native-host outbound artifacts")
    overflow_prune.add_argument('--keep', type=int, default=10, help='Retain at least this many newest oversized artifacts (default: 10)')
    overflow_prune.add_argument('--max-age-days', type=float, help='Also prune artifacts older than this many days')
    overflow_prune.add_argument('--max-disk-bytes', type=int, help='Also prune oldest artifacts until retained disk usage is at or below this byte budget')
    overflow_prune.add_argument('--apply', action='store_true', help='Delete the planned artifacts instead of only printing the retention plan')
    overflow_prune.set_defaults(func=cmd_overflow_prune)

    compare_coverage_experiments = sub.add_parser("compare-coverage-experiments", help="Compare before/after probe or fixture artifacts against the saved coverage experiment plan")
    compare_coverage_experiments.add_argument('baseline')
    compare_coverage_experiments.add_argument('candidate')
    compare_coverage_experiments.add_argument('--experiment-id', choices=['current_runtime_priming', 'manifest_all_frames', 'manifest_match_about_blank', 'manifest_match_origin_as_fallback'])
    compare_coverage_experiments.add_argument('--pretty', action='store_true')
    compare_coverage_experiments.set_defaults(func=cmd_compare_coverage_experiments)

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

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
