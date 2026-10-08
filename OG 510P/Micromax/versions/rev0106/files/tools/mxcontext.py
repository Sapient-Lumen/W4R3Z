#!/usr/bin/env python3
"""mxcontext.py

Emit a short, stable, text-only summary of the repo for humans and LLMs.

Usage:
  python tools/mxcontext.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = [
    "TODO.md",
    "docs/43-worklist.md",
    "docs/00-vision.md",
    "docs/01-llm-start-here.md",
    "docs/42-portability-ledger.md",
    "docs/23-data-model.md",
    "docs/22-two-tier-execution.md",
    "docs/24-bytecode-format.md",
    "docs/25-inline-caching.md",
    "docs/27-bytecode-serialization.md",
    "docs/31-host-api.md",
    "docs/50-editor-behaviors.md",
    "docs/57-editor-multicursor.md",
    "docs/61-editor-cursorstate.md",
    "docs/63-editor-jumplist.md",
    "docs/64-editor-prompt-completion.md",
    "docs/65-debugging-spans.md",
    "docs/66-editor-micromax-commands.md",
    "docs/67-editor-keybinding-provenance.md",
    "docs/68-hook-provenance.md",
    "docs/69-editor-statusline-model.md",
    "docs/73-hook-groups.md",
    "docs/74-editor-registration-groups.md",
    "docs/75-editor-keymap-modes.md",
    "docs/76-editor-transient-keymodes.md",
    "docs/77-editor-keymap-discovery.md",
    "docs/78-editor-binding-descriptions.md",
    "docs/79-editor-prefix-maps.md",
    "docs/80-editor-mode-prefix-maps.md",
    "docs/71-cookbook.md",
    "docs/72-hacking-by-hand.md",
]


def main() -> None:
    print("micromax repo context")
    print("====================")
    print()
    print("Key entrypoints:")
    for p in DOCS:
        print(f"  - {p}")
    print()
    print("Key code:")
    for p in [
        "src/micromax/vm.py",
        "src/micromax/core.py",
        "src/micromax/stdlib/core.mx",
        "src/micromax_editor/editor.py",
        "src/micromax_editor/micromax_bridge.py",
        "tools/mkrevzip.py",
    ]:
        print(f"  - {p}")
    print()
    print("Run tests:")
    print("  make test")
    print()
    print("Repo tree (top-level):")
    for p in sorted([x.name for x in ROOT.iterdir() if not x.name.startswith('.')]):
        print(f"  - {p}")


if __name__ == "__main__":
    main()
