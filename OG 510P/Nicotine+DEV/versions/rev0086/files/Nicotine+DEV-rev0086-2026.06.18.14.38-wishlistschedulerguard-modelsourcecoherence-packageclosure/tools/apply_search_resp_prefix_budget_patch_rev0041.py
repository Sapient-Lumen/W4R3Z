#!/usr/bin/env python3
"""Apply the rev0041 SEARCH-RESP-PARSE-BUDGET-A prefix guard prototype.

Usage:
    python apply_search_resp_prefix_budget_patch_rev0041.py /path/to/nicotine-plus-checkout

The patch is intentionally narrow: a FileSearchResponse whose compressed
pre-token search-username field advertises an implausibly large length is
rejected before that prefix is decompressed. The cap is conservative for a
username/search-owner field and is meant to be replaced by a project constant
if maintainers already have a canonical username-length bound.
"""
from __future__ import annotations

import sys
from pathlib import Path

CONSTANT = 'MAX_SEARCH_RESPONSE_USERNAME_LENGTH'
CAP = 255


def _insert_constant(text: str) -> str:
    if CONSTANT in text:
        return text
    if 'SEARCH_TOKENS_ALLOWED = set()\n' in text:
        return text.replace(
            'SEARCH_TOKENS_ALLOWED = set()\n',
            f'SEARCH_TOKENS_ALLOWED = set()\n{CONSTANT} = {CAP}\n',
            1,
        )
    if 'ZLIB_COMPRESSION_LEVEL = 4\n' in text:
        return text.replace(
            'ZLIB_COMPRESSION_LEVEL = 4\n',
            f'ZLIB_COMPRESSION_LEVEL = 4\n{CONSTANT} = {CAP}\n',
            1,
        )
    raise SystemExit('could not find a stable constant insertion point')


def _patch_legacy(text: str) -> str:
    old = (
        '        _pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))\n'
        '        _pos, self.token = self.unpack_uint32(\n'
        '            decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)\n'
    )
    new = (
        '        _pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))\n'
        f'\n        if username_len > {CONSTANT}:\n'
        '            # Reject implausible pre-token prefixes before materializing them.\n'
        '            self.token = None\n'
        '            self.list = []\n'
        '            return\n'
        '\n'
        '        _pos, self.token = self.unpack_uint32(\n'
        '            decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)\n'
    )
    if old in text:
        return text.replace(old, new, 1)
    return text


def _patch_master(text: str) -> str:
    old = (
        '        self._offset = username_len = self.unpack_uint32()\n'
        '        self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, username_len + 4))\n'
    )
    new = (
        '        self._offset = username_len = self.unpack_uint32()\n'
        f'\n        if username_len > {CONSTANT}:\n'
        '            # Reject implausible pre-token prefixes before materializing them.\n'
        '            self.token = None\n'
        '            return\n'
        '\n'
        '        self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, username_len + 4))\n'
    )
    if old in text:
        return text.replace(old, new, 1)
    return text


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: apply_search_resp_prefix_budget_patch_rev0041.py /path/to/source-tree')
        return 2
    target = Path(sys.argv[1]).resolve() / 'pynicotine' / 'slskmessages.py'
    text = target.read_text(encoding='utf-8')
    patched = _insert_constant(text)
    patched = _patch_legacy(patched)
    patched = _patch_master(patched)
    if patched == text or f'if username_len > {CONSTANT}:' not in patched:
        raise SystemExit('FileSearchResponse prefix parse block not patched')
    target.write_text(patched, encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
