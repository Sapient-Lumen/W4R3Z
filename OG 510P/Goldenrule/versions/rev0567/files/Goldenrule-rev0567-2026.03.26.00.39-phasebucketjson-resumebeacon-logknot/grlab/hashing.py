import json
from hashlib import sha256
from typing import Any


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def hash_obj(obj: Any) -> str:
    return sha256(canonical_json_bytes(obj)).hexdigest()

