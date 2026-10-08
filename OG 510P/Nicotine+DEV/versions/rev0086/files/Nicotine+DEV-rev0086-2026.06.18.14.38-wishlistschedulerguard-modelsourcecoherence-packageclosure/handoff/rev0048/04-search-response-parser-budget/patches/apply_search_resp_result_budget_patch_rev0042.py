#!/usr/bin/env python3
"""Apply rev0042 FileSearchResponse accepted result-count budget guard."""
from __future__ import annotations

import sys
from pathlib import Path

USERNAME_CONSTANT = "MAX_SEARCH_RESPONSE_USERNAME_LENGTH"
USERNAME_CAP = 255
RESULT_CONSTANT = "MAX_SEARCH_RESPONSE_RESULT_COUNT"
RESULT_CAP = 10000


def _insert_constants(text: str) -> str:
    if RESULT_CONSTANT in text and USERNAME_CONSTANT in text:
        return text
    if "SEARCH_TOKENS_ALLOWED = set()\n" in text:
        repl = "SEARCH_TOKENS_ALLOWED = set()\n"
        if USERNAME_CONSTANT not in text:
            repl += f"{USERNAME_CONSTANT} = {USERNAME_CAP}\n"
        if RESULT_CONSTANT not in text:
            repl += f"{RESULT_CONSTANT} = {RESULT_CAP}\n"
        return text.replace("SEARCH_TOKENS_ALLOWED = set()\n", repl, 1)
    if "ZLIB_COMPRESSION_LEVEL = 4\n" in text:
        repl = "ZLIB_COMPRESSION_LEVEL = 4\n"
        if USERNAME_CONSTANT not in text:
            repl += f"{USERNAME_CONSTANT} = {USERNAME_CAP}\n"
        if RESULT_CONSTANT not in text:
            repl += f"{RESULT_CONSTANT} = {RESULT_CAP}\n"
        return text.replace("ZLIB_COMPRESSION_LEVEL = 4\n", repl, 1)
    raise SystemExit("could not find constant insertion point")


def _ensure_prefix_guard_legacy(text: str) -> str:
    if f"if username_len > {USERNAME_CONSTANT}:" in text:
        return text
    old = (
        "        _pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))\n"
        "        _pos, self.token = self.unpack_uint32(\n"
        "            decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)\n"
    )
    new = (
        "        _pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))\n"
        f"\n        if username_len > {USERNAME_CONSTANT}:\n"
        "            self.token = None\n"
        "            self.list = []\n"
        "            return\n"
        "\n"
        "        _pos, self.token = self.unpack_uint32(\n"
        "            decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)\n"
    )
    return text.replace(old, new, 1) if old in text else text


def _ensure_prefix_guard_master(text: str) -> str:
    if f"if username_len > {USERNAME_CONSTANT}:" in text:
        return text
    old = (
        "        self._offset = username_len = self.unpack_uint32()\n"
        "        self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, username_len + 4))\n"
    )
    new = (
        "        self._offset = username_len = self.unpack_uint32()\n"
        f"\n        if username_len > {USERNAME_CONSTANT}:\n"
        "            self.token = None\n"
        "            self.list = []\n"
        "            return\n"
        "\n"
        "        self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, username_len + 4))\n"
    )
    return text.replace(old, new, 1) if old in text else text


def _patch_legacy_network_message(text: str) -> str:
    if "accepted_result_count_header = decompressor.decompress(decompressor.unconsumed_tail, 4)" in text:
        return text
    old_with_cap = (
        "        # Optimization: only decompress the rest of the message when needed\n"
        "        decompressed_message = decompressor.decompress(decompressor.unconsumed_tail, max_uncompressed_size)\n"
        "\n"
        "        if not decompressor.unconsumed_tail:\n"
        "            self._parse_remaining_network_message(memoryview(decompressed_message))\n"
    )
    new_with_cap = (
        "        # Optimization: only decompress the rest of the message when needed.\n"
        "        accepted_result_count_header = decompressor.decompress(decompressor.unconsumed_tail, 4)\n"
        "\n"
        "        if len(accepted_result_count_header) < 4:\n"
        "            self.token = None\n"
        "            self.list = []\n"
        "            return\n"
        "\n"
        "        _pos, accepted_result_count = self.unpack_uint32(accepted_result_count_header)\n"
        f"        if accepted_result_count > {RESULT_CONSTANT}:\n"
        "            self.token = None\n"
        "            self.list = []\n"
        "            self.privatelist = []\n"
        "            return\n"
        "\n"
        "        decompressed_message = accepted_result_count_header + decompressor.decompress(\n"
        "            decompressor.unconsumed_tail, max_uncompressed_size - len(accepted_result_count_header))\n"
        "\n"
        "        if not decompressor.unconsumed_tail:\n"
        "            self._parse_remaining_network_message(memoryview(decompressed_message))\n"
    )
    if old_with_cap in text:
        return text.replace(old_with_cap, new_with_cap, 1)
    old_no_cap = (
        "        # Optimization: only decompress the rest of the message when needed\n"
        "        self._parse_remaining_network_message(\n"
        "            memoryview(decompressor.decompress(decompressor.unconsumed_tail))\n"
        "        )\n"
    )
    new_no_cap = (
        "        # Optimization: only decompress the rest of the message when needed.\n"
        "        accepted_result_count_header = decompressor.decompress(decompressor.unconsumed_tail, 4)\n"
        "\n"
        "        if len(accepted_result_count_header) < 4:\n"
        "            self.token = None\n"
        "            self.list = []\n"
        "            return\n"
        "\n"
        "        _pos, accepted_result_count = self.unpack_uint32(accepted_result_count_header)\n"
        f"        if accepted_result_count > {RESULT_CONSTANT}:\n"
        "            self.token = None\n"
        "            self.list = []\n"
        "            self.privatelist = []\n"
        "            return\n"
        "\n"
        "        self._parse_remaining_network_message(\n"
        "            memoryview(accepted_result_count_header + decompressor.decompress(decompressor.unconsumed_tail))\n"
        "        )\n"
    )
    return text.replace(old_no_cap, new_no_cap, 1) if old_no_cap in text else text


def _patch_legacy_result_parser(text: str) -> str:
    if f"max_results={RESULT_CONSTANT}" in text:
        return text
    old = (
        "    def _parse_remaining_network_message(self, message):\n"
        "        pos, self.list = self._parse_result_list(message)\n"
        "        pos, self.freeulslots = self.unpack_bool(message, pos)\n"
        "        pos, self.ulspeed = self.unpack_uint32(message, pos)\n"
        "        pos, self.inqueue = self.unpack_uint32(message, pos)\n"
        "\n"
        "        if message[pos:]:\n"
        "            pos, self.unknown = self.unpack_uint32(message, pos)\n"
        "\n"
        "        if message[pos:]:\n"
        "            pos, self.privatelist = self._parse_result_list(message, pos)\n"
        "\n"
        "    def _parse_result_list(self, message, pos=0):\n"
        "        pos, nfiles = self.unpack_uint32(message, pos)\n"
        "\n"
        "        ext = None\n"
        "        results = []\n"
    )
    new = (
        "    def _parse_remaining_network_message(self, message):\n"
        f"        pos, results = self._parse_result_list(message, max_results={RESULT_CONSTANT})\n"
        "\n"
        "        if results is None:\n"
        "            self.token = None\n"
        "            self.list = []\n"
        "            self.privatelist = []\n"
        "            return\n"
        "\n"
        "        self.list = results\n"
        "        pos, self.freeulslots = self.unpack_bool(message, pos)\n"
        "        pos, self.ulspeed = self.unpack_uint32(message, pos)\n"
        "        pos, self.inqueue = self.unpack_uint32(message, pos)\n"
        "\n"
        "        if message[pos:]:\n"
        "            pos, self.unknown = self.unpack_uint32(message, pos)\n"
        "\n"
        "        if message[pos:]:\n"
        f"            remaining_results = {RESULT_CONSTANT} - len(self.list)\n"
        "            pos, private_results = self._parse_result_list(message, pos, max_results=remaining_results)\n"
        "\n"
        "            if private_results is None:\n"
        "                self.token = None\n"
        "                self.list = []\n"
        "                self.privatelist = []\n"
        "                return\n"
        "\n"
        "            self.privatelist = private_results\n"
        "\n"
        f"    def _parse_result_list(self, message, pos=0, max_results={RESULT_CONSTANT}):\n"
        "        pos, nfiles = self.unpack_uint32(message, pos)\n"
        "\n"
        "        if nfiles > max_results:\n"
        "            return pos, None\n"
        "\n"
        "        ext = None\n"
        "        results = []\n"
    )
    return text.replace(old, new, 1) if old in text else text


def _patch_master_network_message(text: str) -> str:
    if "accepted_result_count_header = decompressor.decompress(decompressor.unconsumed_tail, 4)" in text:
        return text
    old = (
        "        # Optimization: only decompress the rest of the message when needed\n"
        "        self._offset = 0\n"
        "        self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, max_uncompressed_size))\n"
        "\n"
        "        if not decompressor.unconsumed_tail:\n"
        "            self._parse_remaining_network_message()\n"
    )
    new = (
        "        # Optimization: only decompress the rest of the message when needed.\n"
        "        accepted_result_count_header = decompressor.decompress(decompressor.unconsumed_tail, 4)\n"
        "\n"
        "        if len(accepted_result_count_header) < 4:\n"
        "            self.token = None\n"
        "            self.list = []\n"
        "            return\n"
        "\n"
        "        self._offset = 0\n"
        "        self._message = memoryview(accepted_result_count_header)\n"
        "        accepted_result_count = self.unpack_uint32()\n"
        f"        if accepted_result_count > {RESULT_CONSTANT}:\n"
        "            self.token = None\n"
        "            self.list = []\n"
        "            self.privatelist = []\n"
        "            return\n"
        "\n"
        "        self._offset = 0\n"
        "        self._message = memoryview(\n"
        "            accepted_result_count_header + decompressor.decompress(\n"
        "                decompressor.unconsumed_tail, max_uncompressed_size - len(accepted_result_count_header)))\n"
        "\n"
        "        if not decompressor.unconsumed_tail:\n"
        "            self._parse_remaining_network_message()\n"
    )
    return text.replace(old, new, 1) if old in text else text


def _patch_master_result_parser(text: str) -> str:
    if f"max_results={RESULT_CONSTANT}" in text:
        return text
    old = (
        "    def _parse_remaining_network_message(self):\n"
        "        self.list = self._parse_result_list()\n"
        "        self.freeulslots = self.unpack_bool()\n"
        "        self.ulspeed = self.unpack_uint32()\n"
        "        self.inqueue = self.unpack_uint32()\n"
        "\n"
        "        if self.has_remaining_content():\n"
        "            self.unknown = self.unpack_uint32()\n"
        "\n"
        "        if self.has_remaining_content():\n"
        "            self.privatelist = self._parse_result_list()\n"
        "\n"
        "    def _parse_result_list(self):\n"
        "        nfiles = self.unpack_uint32()\n"
        "\n"
        "        ext = None\n"
        "        results = []\n"
    )
    new = (
        "    def _parse_remaining_network_message(self):\n"
        f"        results = self._parse_result_list(max_results={RESULT_CONSTANT})\n"
        "\n"
        "        if results is None:\n"
        "            self.token = None\n"
        "            self.list = []\n"
        "            self.privatelist = []\n"
        "            return\n"
        "\n"
        "        self.list = results\n"
        "        self.freeulslots = self.unpack_bool()\n"
        "        self.ulspeed = self.unpack_uint32()\n"
        "        self.inqueue = self.unpack_uint32()\n"
        "\n"
        "        if self.has_remaining_content():\n"
        "            self.unknown = self.unpack_uint32()\n"
        "\n"
        "        if self.has_remaining_content():\n"
        f"            remaining_results = {RESULT_CONSTANT} - len(self.list)\n"
        "            private_results = self._parse_result_list(max_results=remaining_results)\n"
        "\n"
        "            if private_results is None:\n"
        "                self.token = None\n"
        "                self.list = []\n"
        "                self.privatelist = []\n"
        "                return\n"
        "\n"
        "            self.privatelist = private_results\n"
        "\n"
        f"    def _parse_result_list(self, max_results={RESULT_CONSTANT}):\n"
        "        nfiles = self.unpack_uint32()\n"
        "\n"
        "        if nfiles > max_results:\n"
        "            return None\n"
        "\n"
        "        ext = None\n"
        "        results = []\n"
    )
    return text.replace(old, new, 1) if old in text else text


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    target = Path(argv[0]) / "pynicotine" / "slskmessages.py"
    text = target.read_text(encoding="utf-8")
    patched = _insert_constants(text)
    patched = _ensure_prefix_guard_legacy(patched)
    patched = _ensure_prefix_guard_master(patched)
    patched = _patch_legacy_network_message(patched)
    patched = _patch_legacy_result_parser(patched)
    patched = _patch_master_network_message(patched)
    patched = _patch_master_result_parser(patched)
    required = [RESULT_CONSTANT, "accepted_result_count_header", "max_results=MAX_SEARCH_RESPONSE_RESULT_COUNT"]
    missing = [x for x in required if x not in patched]
    if missing:
        raise SystemExit(f"patch markers missing: {missing}")
    target.write_text(patched, encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
