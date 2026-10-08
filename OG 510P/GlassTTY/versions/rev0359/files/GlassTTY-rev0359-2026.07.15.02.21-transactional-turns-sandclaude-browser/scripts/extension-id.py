#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path

ALPHABET = 'abcdefghijklmnop'


def compute_extension_id_from_key(key_b64: str) -> str:
    digest = hashlib.sha256(base64.b64decode(key_b64)).hexdigest()[:32]
    return ''.join(ALPHABET[int(ch, 16)] for ch in digest)


def main() -> None:
    parser = argparse.ArgumentParser(description='Compute Chromium extension id from manifest.key')
    parser.add_argument('manifest', nargs='?', default='extension/manifest.json')
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    key = manifest.get('key')
    if not isinstance(key, str) or not key.strip():
        raise SystemExit(f'manifest.key missing in {manifest_path}')
    print(compute_extension_id_from_key(key.strip()))


if __name__ == '__main__':
    main()
