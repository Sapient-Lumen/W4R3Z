#!/usr/bin/env python3
"""mxbytecode.py

Tiny helper to inspect tier-2 compilation artifacts.

Usage:
  python tools/mxbytecode.py path/to/file.mf
  python tools/mxbytecode.py path/to/file.mf --word foo
  python tools/mxbytecode.py path/to/file.mf --word foo --json

Notes:
- This is intentionally simple: it loads the file into a fresh VM.
- If --word is omitted, it prints the new words defined by the file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from micromax import VM, MicromaxError


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="micromax source file")
    ap.add_argument("--word", help="word name to disassemble / serialize")
    ap.add_argument("--json", action="store_true", help="print bytecode JSON instead of disasm")
    ns = ap.parse_args(argv)

    path = Path(ns.path)
    if not path.exists():
        print(f"mxbytecode: no such file: {path}", file=sys.stderr)
        return 2

    vm = VM()
    before = set(vm.all_words_view().keys())
    src = path.read_text(encoding="utf-8")
    try:
        vm.eval(src, filename=str(path))
    except MicromaxError as e:
        print(vm.format_error(e), file=sys.stderr)
        return 1

    if not ns.word:
        after = set(vm.all_words_view().keys())
        new = sorted(list(after - before))
        for n in new:
            print(n)
        return 0

    w = vm.find_word(ns.word)
    if w is None:
        print(f"mxbytecode: unknown word: {ns.word}", file=sys.stderr)
        return 1

    try:
        if ns.json:
            vm.stack.append(w)
            vm.eval("bytecode-json")
            print(vm.pop_str())
        else:
            vm.stack.append(w)
            vm.eval("disasm")
    except MicromaxError as e:
        print(vm.format_error(e), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
