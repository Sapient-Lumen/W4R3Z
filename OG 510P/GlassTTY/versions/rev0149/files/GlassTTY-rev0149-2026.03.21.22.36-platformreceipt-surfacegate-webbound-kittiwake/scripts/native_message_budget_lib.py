from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fixture_plan_lib import load_fixture

NATIVE_MESSAGE_HOST_MAX_BYTES = 1024 * 1024
NATIVE_MESSAGE_EXTENSION_MAX_BYTES = 64 * 1024 * 1024
ESTIMATED_CAPTURE_MESSAGE_TYPE = 'fixture.capture'
ESTIMATED_REQUEST_ID = '00000000-0000-4000-8000-000000000000'
ESTIMATED_TIMESTAMP = '1970-01-01T00:00:00+00:00'
ESTIMATED_TAB_ID = 999999

JsonDict = dict[str, Any]


def json_size_bytes(data: Any) -> int:
    return len(json.dumps(data, ensure_ascii=False).encode('utf-8'))



def classify_budget(size_bytes: int, *, limit_bytes: int = NATIVE_MESSAGE_HOST_MAX_BYTES) -> str:
    ratio = size_bytes / limit_bytes if limit_bytes else 0.0
    if size_bytes > limit_bytes:
        return 'overflow'
    if ratio >= 0.9:
        return 'warning'
    if ratio >= 0.75:
        return 'caution'
    return 'ok'



def budget_report_for_size(size_bytes: int, *, limit_bytes: int = NATIVE_MESSAGE_HOST_MAX_BYTES) -> JsonDict:
    remaining = limit_bytes - size_bytes
    ratio = size_bytes / limit_bytes if limit_bytes else 0.0
    return {
        'size_bytes': size_bytes,
        'limit_bytes': limit_bytes,
        'remaining_bytes': remaining,
        'usage_ratio': round(ratio, 6),
        'status': classify_budget(size_bytes, limit_bytes=limit_bytes),
        'fits': size_bytes <= limit_bytes,
    }



def estimated_native_fixture_envelope(payload: JsonDict, *, message_type: str = ESTIMATED_CAPTURE_MESSAGE_TYPE) -> JsonDict:
    return {
        'version': '0.1',
        'request_id': ESTIMATED_REQUEST_ID,
        'type': message_type,
        'timestamp': ESTIMATED_TIMESTAMP,
        'tab_id': ESTIMATED_TAB_ID,
        'payload': payload,
    }



def fixture_payload_budget(payload: JsonDict, *, message_type: str = ESTIMATED_CAPTURE_MESSAGE_TYPE) -> JsonDict:
    envelope = estimated_native_fixture_envelope(payload, message_type=message_type)
    payload_bytes = json_size_bytes(payload)
    envelope_bytes = json_size_bytes(envelope)
    return {
        'payload_bytes': payload_bytes,
        'envelope_bytes': envelope_bytes,
        'host_to_extension': budget_report_for_size(envelope_bytes),
        'extension_to_host': budget_report_for_size(envelope_bytes, limit_bytes=NATIVE_MESSAGE_EXTENSION_MAX_BYTES),
    }



def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))



def budget_report_for_path(path: Path) -> JsonDict:
    raw = load_json(path)
    report: JsonDict = {
        'path': str(path),
        'raw_json_bytes': json_size_bytes(raw),
    }
    try:
        payload = load_fixture(path)
    except Exception:
        payload = None
    if isinstance(payload, dict):
        report['fixture_payload'] = fixture_payload_budget(payload)
        report['adapter'] = payload.get('adapter')
        report['title'] = payload.get('title')
        report['url'] = payload.get('url')
    else:
        report['json_document'] = budget_report_for_size(report['raw_json_bytes'])
    return report
