#!/usr/bin/env python3
"""mxcontext.py

Emit a short, stable repo-context snapshot for humans and LLMs.

Usage:
  python tools/mxcontext.py
  python tools/mxcontext.py --json
  python tools/mxcontext.py --check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
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
    "docs/146-keymenu.md",
    "docs/147-infobar.md",
    "docs/148-statusline-row-policy.md",
    "docs/149-constantshow.md",
    "docs/150-capture-prompts.md",
    "docs/151-capture-status-model.md",
    "docs/152-interaction-status-model.md",
    "docs/153-bottom-rows-model.md",
    "docs/154-statusline-layout-model.md",
    "docs/155-keymenu-infobar-models.md",
    "docs/156-interaction-row-model.md",
    "docs/157-screen-layout-model.md",
    "docs/158-edit-window-model.md",
    "docs/159-screen-model.md",
    "docs/160-prompt-panel-model.md",
    "docs/161-gutter-model.md",
    "docs/162-viewport-rows-model.md",
    "docs/163-screen-rows-model.md",
    "docs/164-search-rows-model.md",
    "docs/165-showchars-rows-model.md",
    "docs/166-display-rows-model.md",
    "docs/167-viewport-cues-model.md",
    "docs/168-docs-cues-model.md",
    "docs/169-headless-screen-dump-cli.md",
    "docs/170-context-cli-json.md",
    "docs/171-rust-vm-spike.md",
    "docs/176-docs-cues-link-metadata.md",
    "docs/177-docs-cues-image-metadata.md",
    "docs/178-docs-cues-code-metadata.md",
    "docs/179-docs-cues-inline-markup-metadata.md",
    "docs/180-docs-cues-literal-source-metadata.md",
    "docs/202-docs-cues-structure-metadata.md",
    "docs/203-docs-cues-table-metadata.md",
    "docs/204-docs-cues-heading-metadata.md",
    "docs/205-docs-cues-definition-metadata.md",
    "docs/206-docs-cues-block-metadata.md",
    "docs/207-docs-cues-section-metadata.md",
    "docs/208-helpoutline-section-groups.md",
    "docs/209-recentdirpick.md",
    "docs/210-helpnav-heading-breadcrumbs.md",
    "docs/211-help-breadcrumb-query-matching.md",
    "docs/212-helplink-heading-query-matching.md",
    "docs/213-help-heading-fragment-query-matching.md",
    "docs/214-helplink-target-title-query-matching.md",
    "docs/215-portability-cleanup-error-precedence.md",
    "docs/216-portability-try-handler-error-precedence.md",
    "docs/217-portability-stdlib-manifest-cli.md",
    "docs/218-portability-stdlib-source-inventory.md",
    "docs/219-portability-stdlib-dependency-inventory.md",
    "docs/220-portability-stdlib-closure-inventory.md",
    "docs/221-portability-stdlib-user-inventory.md",
    "docs/222-portability-stdlib-impact-map.md",
    "docs/223-portability-selected-retest-command.md",
    "docs/224-portability-impact-inventory.md",
    "docs/225-portability-impact-groups.md",
    "docs/226-portability-impact-group-retest-metadata.md",
    "docs/227-portability-impact-stages.md",
    "docs/228-portability-impact-slice-filters.md",
    "docs/229-portability-impact-case-filters.md",
    "docs/230-portability-impact-filter-options.md",
    "docs/231-portability-impact-semantic-filter-options.md",
    "docs/232-portability-impact-filter-suffixes.md",
    "docs/233-portability-impact-filter-commands.md",
    "docs/234-portability-impact-filter-family-modes.md",
    "docs/235-portability-impact-filter-previews.md",
    "docs/236-portability-impact-preview-effects.md",
    "docs/237-portability-impact-filter-recommendations.md",
    "docs/238-portability-impact-equivalent-cuts.md",
    "docs/239-portability-impact-distinct-recommendations.md",
    "docs/240-portability-impact-distinct-groups.md",
    "docs/241-portability-impact-representative-reasons.md",
    "docs/242-portability-impact-recommendation-ranks.md",
    "docs/243-portability-impact-primary-recommendation.md",
    "docs/181-portability-pick-roll-cases.md",
    "docs/182-portability-pick-roll-indexing.md",
    "docs/183-portability-pick-roll-four-item.md",
    "docs/184-portability-pick-roll-five-item.md",
    "docs/185-portability-pick-roll-errors.md",
    "docs/186-portability-qdup.md",
    "docs/187-portability-negate-abs-zero-less.md",
    "docs/188-portability-min-max.md",
    "docs/189-portability-oneplus-oneminus-zeropreds.md",
    "docs/190-portability-twostar-twoslash.md",
    "docs/191-portability-2over-2swap.md",
    "docs/192-portability-2rot.md",
    "docs/193-portability-2returnstack-pairs.md",
    "docs/194-portability-2nip-2tuck.md",
    "docs/195-portability-2rdrop.md",
    "docs/196-portability-not-equals.md",
    "docs/197-portability-basic-stack-pairs.md",
    "docs/198-portability-keep.md",
    "docs/199-portability-recovery-error-stacks.md",
    "docs/200-portability-assert.md",
    "docs/201-portability-stdlib-coverage-audit.md",
    "docs/71-cookbook.md",
    "docs/72-hacking-by-hand.md",
]

CODE = [
    "src/micromax/vm.py",
    "src/micromax/core.py",
    "src/micromax/stdlib/core.mx",
    "src/micromax_editor/editor.py",
    "src/micromax_editor/micromax_bridge.py",
    "src/micromax_editor/__main__.py",
    "tools/mkrevzip.py",
    "tools/mxcontext.py",
]

RUN_COMMANDS = [
    "make test",
    "make context",
    "make context-json",
    "make context-check",
    "python tools/mxcontext.py --json",
    "python tools/mxcontext.py --check",
    "python -m micromax_editor --help-doc docs/70-tutorial.md --dump-screen 24 80",
]



def _read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")



def infer_rev() -> int:
    todo = _read_text("TODO.md").splitlines()[:1]
    if todo:
        match = re.search(r"rev\s*(\d+)", todo[0], flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    readme = _read_text("README.md").splitlines()[:8]
    for line in readme:
        match = re.search(r"Rev\s*(\d+)\s+note:", line, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    raise SystemExit("could not infer rev from TODO.md or README.md")



def latest_note() -> str | None:
    for line in _read_text("README.md").splitlines():
        stripped = line.strip()
        if stripped.startswith("Rev") and " note:" in stripped:
            return stripped
    return None



def current_priorities() -> list[str]:
    lines = _read_text("TODO.md").splitlines()
    in_section = False
    priorities: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.lower() == "## next up (high leverage)":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if not in_section:
            continue
        match = re.match(r"\d+\.\s+(.*)$", stripped)
        if match:
            text = re.sub(r"\*\*", "", match.group(1)).strip()
            priorities.append(text)
    return priorities



def missing_paths() -> list[str]:
    missing: list[str] = []
    for rel in DOCS + CODE:
        if not (ROOT / rel).exists():
            missing.append(rel)
    return missing



def payload() -> dict[str, object]:
    return {
        "project": "micromax",
        "rev": infer_rev(),
        "latest_note": latest_note(),
        "current_priorities": current_priorities(),
        "docs": DOCS,
        "code": CODE,
        "run_commands": RUN_COMMANDS,
        "top_level": sorted(x.name for x in ROOT.iterdir() if not x.name.startswith('.')),
        "checks": {
            "missing_paths": missing_paths(),
            "ok": len(missing_paths()) == 0,
        },
    }



def print_human(data: dict[str, object]) -> None:
    print("micromax repo context")
    print("====================")
    print()
    print(f"Rev: {data['rev']}")
    note = data.get("latest_note")
    if isinstance(note, str) and note:
        print(f"Latest note: {note}")
        print()
    priorities = data.get("current_priorities")
    if isinstance(priorities, list) and priorities:
        print("Current priorities:")
        for i, item in enumerate(priorities, start=1):
            print(f"  {i}. {item}")
        print()
    print("Key entrypoints:")
    for p in data["docs"]:
        print(f"  - {p}")
    print()
    print("Key code:")
    for p in data["code"]:
        print(f"  - {p}")
    print()
    print("Useful commands:")
    for cmd in data["run_commands"]:
        print(f"  - {cmd}")
    print()
    print("Repo tree (top-level):")
    for p in data["top_level"]:
        print(f"  - {p}")



def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit machine-readable repo context JSON")
    ap.add_argument("--check", action="store_true", help="fail if referenced docs/code paths are missing")
    args = ap.parse_args(argv)

    data = payload()
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_human(data)

    if args.check:
        missing = list(data["checks"]["missing_paths"])
        if missing:
            if not args.json:
                print()
                print("Missing referenced paths:")
                for rel in missing:
                    print(f"  - {rel}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
