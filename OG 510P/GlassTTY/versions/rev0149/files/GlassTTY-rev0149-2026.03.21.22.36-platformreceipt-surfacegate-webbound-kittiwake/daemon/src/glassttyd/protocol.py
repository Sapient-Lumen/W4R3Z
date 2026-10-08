from __future__ import annotations

import json
import struct
import sys
from typing import Any

JsonDict = dict[str, Any]
NATIVE_MESSAGE_HOST_MAX_BYTES = 1024 * 1024
NATIVE_MESSAGE_EXTENSION_MAX_BYTES = 64 * 1024 * 1024


def encode_native_message(message: JsonDict) -> bytes:
    return json.dumps(message, ensure_ascii=False).encode('utf-8')


def native_message_size(message: JsonDict) -> int:
    return len(encode_native_message(message))


def native_message_budget_report(message: JsonDict, *, limit_bytes: int = NATIVE_MESSAGE_HOST_MAX_BYTES) -> JsonDict:
    size = native_message_size(message)
    remaining = limit_bytes - size
    ratio = size / limit_bytes if limit_bytes else 0.0
    return {
        'size_bytes': size,
        'limit_bytes': limit_bytes,
        'remaining_bytes': remaining,
        'usage_ratio': ratio,
        'fits': size <= limit_bytes,
    }


def validate_native_host_message_size(message: JsonDict) -> int:
    size = native_message_size(message)
    if size > NATIVE_MESSAGE_HOST_MAX_BYTES:
        raise RuntimeError(
            f'native host message too large: {size} bytes exceeds Chrome host-to-extension limit of {NATIVE_MESSAGE_HOST_MAX_BYTES} bytes'
        )
    return size


def read_native_message(stdin) -> JsonDict | None:
    raw_length = stdin.buffer.read(4)
    if not raw_length:
        return None
    if len(raw_length) != 4:
        raise RuntimeError('incomplete native message length header')
    message_length = struct.unpack('<I', raw_length)[0]
    payload = stdin.buffer.read(message_length)
    if len(payload) != message_length:
        raise RuntimeError('incomplete native message body')
    return json.loads(payload.decode('utf-8'))


def write_native_message(stdout, message: JsonDict) -> None:
    encoded = encode_native_message(message)
    if len(encoded) > NATIVE_MESSAGE_HOST_MAX_BYTES:
        raise RuntimeError(
            f'native host message too large: {len(encoded)} bytes exceeds Chrome host-to-extension limit of {NATIVE_MESSAGE_HOST_MAX_BYTES} bytes'
        )
    stdout.buffer.write(struct.pack('<I', len(encoded)))
    stdout.buffer.write(encoded)
    stdout.buffer.flush()


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr, flush=True)


def make_envelope(message_type: str, payload: JsonDict, *, request_id: str | None = None, tab_id: int | None = None, timestamp: str | None = None) -> JsonDict:
    envelope: JsonDict = {
        'version': '0.1',
        'request_id': request_id,
        'type': message_type,
        'timestamp': timestamp,
        'payload': payload,
    }
    if tab_id is not None:
        envelope['tab_id'] = tab_id
    return envelope
