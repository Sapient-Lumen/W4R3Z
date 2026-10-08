from __future__ import annotations

import json
import struct
import sys
from typing import Any

JsonDict = dict[str, Any]


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
    encoded = json.dumps(message, ensure_ascii=False).encode('utf-8')
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
