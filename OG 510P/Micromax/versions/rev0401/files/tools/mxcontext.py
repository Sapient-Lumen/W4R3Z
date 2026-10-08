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
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

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
    "docs/244-context-portability-snapshot.md",
    "docs/245-archive-context-manifest.md",
    "docs/246-docs-cues-task-metadata.md",
    "docs/247-docs-cues-blockquote-break-metadata.md",
    "docs/248-docs-cues-list-metadata.md",
    "docs/249-docs-cues-link-target-metadata.md",
    "docs/250-docs-cues-image-target-metadata.md",
    "docs/251-docs-cues-table-kind-metadata.md",
    "docs/252-docs-cues-block-kind-metadata.md",
    "docs/253-docs-cues-markup-kind-metadata.md",
    "docs/254-docs-cues-literal-kind-metadata.md",
    "docs/255-docs-cues-definition-kind-metadata.md",
    "docs/256-docs-cues-heading-kind-metadata.md",
    "docs/257-docs-cues-link-source-kind-metadata.md",
    "docs/258-docs-cues-image-source-kind-metadata.md",
    "docs/259-docs-cues-reference-form-metadata.md",
    "docs/260-docs-cues-markup-delimiter-metadata.md",
    "docs/261-docs-cues-code-delimiter-metadata.md",
    "docs/262-docs-cues-fenced-code-source-metadata.md",
    "docs/263-docs-cues-table-alignment-metadata.md",
    "docs/264-docs-cues-blockquote-alert-kind-metadata.md",
    "docs/265-docs-cues-heading-level-metadata.md",
    "docs/266-docs-cues-heading-fragment-source-metadata.md",
    "docs/267-docs-cues-task-list-kind-metadata.md",
    "docs/268-docs-cues-task-state-metadata.md",
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
    "docs/315-showcmd-showword-miss-feedback.md",
    "docs/316-keybinding-miss-feedback.md",
    "docs/317-core-introspection-miss-feedback.md",
    "docs/318-picker-fallback-section-labels.md",
    "docs/319-buffer-command-miss-feedback.md",
    "docs/320-showhook-not-hook-feedback.md",
    "docs/321-markjump-miss-feedback.md",
    "docs/322-unknown-command-feedback.md",
    "docs/323-headless-repl-unknown-command-feedback.md",
    "docs/324-help-miss-feedback.md",
    "docs/325-macro-subcommand-miss-feedback.md",
    "docs/326-macro-play-miss-feedback.md",
    "docs/327-unbind-success-feedback.md",
    "docs/328-bind-success-feedback.md",
    "docs/329-close-success-feedback.md",
    "docs/330-command-runtime-error-feedback.md",
    "docs/331-help-doc-navigation-miss-feedback.md",
    "docs/332-plugin-no-manager-feedback.md",
    "docs/333-bulk-close-error-feedback.md",
    "docs/334-mx-command-error-feedback.md",
    "docs/335-hook-runtime-error-feedback.md",
    "docs/336-binddoc-success-feedback.md",
    "docs/337-url-command-feedback.md",
    "docs/338-option-command-feedback.md",
    "docs/339-help-link-action-feedback.md",
    "docs/340-helpfollow-miss-feedback.md",
    "docs/341-helpback-feedback.md",
    "docs/342-helpdocs-open-feedback.md",
    "docs/343-helpjump-fragment-miss-feedback.md",
]

CODE = [
    "src/micromax/vm.py",
    "src/micromax/core.py",
    "src/micromax/portability_suite.py",
    "src/micromax/stdlib/core.mx",
    "src/micromax_editor/editor.py",
    "src/micromax_editor/micromax_bridge.py",
    "src/micromax_editor/__main__.py",
    "tools/mkrevzip.py",
    "tools/mxcontext.py",
    "portability/kernel_cases.json",
]

RUN_COMMANDS = [
    "make test",
    "make context",
    "make context-json",
    "make context-check",
    "python tools/mxcontext.py --json",
    "python tools/mxcontext.py --check",
    "python tools/mxportable.py --json",
    "python tools/mxportable.py --stdlib-manifest --json",
    "python tools/mxportable.py --stdlib-manifest --show-source --json",
    "python -m micromax_editor --help-doc docs/70-tutorial.md --dump-screen 24 80",
]



def _read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")



def _extract_rev(line: str) -> int | None:
    match = re.search(r"rev\s*(\d+)", line, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None



def _todo_heading_rev() -> int | None:
    for line in _read_text("TODO.md").splitlines():
        stripped = line.strip()
        if stripped.startswith("# TODO"):
            return _extract_rev(stripped)
    return None



def revision_sources() -> dict[str, Any]:
    todo_lines = _read_text("TODO.md").splitlines()
    todo_first_line = todo_lines[0].strip() if todo_lines else ""
    readme_note = latest_note() or ""
    todo_first_rev = _extract_rev(todo_first_line)
    todo_heading_rev = _todo_heading_rev()
    readme_latest_rev = _extract_rev(readme_note)
    revisions = [rev for rev in (todo_first_rev, todo_heading_rev, readme_latest_rev) if rev is not None]
    current_rev = max(revisions) if revisions else None
    warnings: list[str] = []
    if current_rev is None:
        warnings.append("could not infer current revision from TODO.md or README.md")
    if todo_first_rev is None:
        warnings.append("TODO.md first line is missing a revision note")
    if todo_heading_rev is None:
        warnings.append("TODO.md heading is missing a revision")
    if readme_latest_rev is None:
        warnings.append("README.md is missing a latest revision note")
    if current_rev is not None:
        if todo_first_rev is not None and todo_first_rev != current_rev:
            warnings.append(
                f"TODO.md first-line rev {todo_first_rev} does not match current rev {current_rev}"
            )
        if todo_heading_rev is not None and todo_heading_rev != current_rev:
            warnings.append(
                f"TODO.md heading rev {todo_heading_rev} does not match current rev {current_rev}"
            )
        if readme_latest_rev is not None and readme_latest_rev != current_rev:
            warnings.append(
                f"README.md latest note rev {readme_latest_rev} does not match current rev {current_rev}"
            )
    return {
        "current_rev": current_rev,
        "todo_first_line": todo_first_line,
        "todo_first_line_rev": todo_first_rev,
        "todo_heading_rev": todo_heading_rev,
        "readme_latest_note": readme_note,
        "readme_latest_rev": readme_latest_rev,
        "warnings": warnings,
        "ok": len(warnings) == 0,
    }



def infer_rev() -> int:
    info = revision_sources()
    current_rev = info.get("current_rev")
    if isinstance(current_rev, int):
        return current_rev
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



def _load_portability_cases() -> list[dict[str, object]]:
    path = ROOT / "portability" / "kernel_cases.json"
    return json.loads(path.read_text(encoding="utf-8"))



def portability_snapshot() -> dict[str, object]:
    from micromax.portability_suite import boot_stdlib_manifest_inventory, boot_stdlib_word_specs

    cases = _load_portability_cases()
    category_counts = Counter(str(case.get("category") or "") for case in cases if str(case.get("category") or ""))
    tag_counts: Counter[str] = Counter()
    host_feature_counts: Counter[str] = Counter()
    for case in cases:
        tag_counts.update(str(tag) for tag in (case.get("tags") or []) if str(tag))
        host_feature_counts.update(str(feat) for feat in (case.get("host_features") or []) if str(feat))
    manifest = boot_stdlib_manifest_inventory(cases)
    specs = boot_stdlib_word_specs()
    alias_words = sorted(word for word, spec in specs.items() if str(spec.get("alias_of") or ""))
    max_depth = max((int(spec.get("stdlib_depth") or 0) for spec in specs.values()), default=0)
    return {
        "kernel_cases_path": "portability/kernel_cases.json",
        "case_count": len(cases),
        "category_counts": {name: int(category_counts[name]) for name in sorted(category_counts)},
        "tag_counts": {name: int(tag_counts[name]) for name in sorted(tag_counts)},
        "host_feature_counts": {name: int(host_feature_counts[name]) for name in sorted(host_feature_counts)},
        "boot_stdlib_manifest": {
            "word_count": int(manifest.get("word_count") or 0),
            "manifest_case_count": int(manifest.get("manifest_case_count") or 0),
            "all_cases_present": bool(manifest.get("all_cases_present")),
            "missing_words": [str(word) for word in (manifest.get("missing_words") or [])],
        },
        "boot_stdlib_source": {
            "source_path": "src/micromax/stdlib/core.mx",
            "word_count": len(specs),
            "alias_count": len(alias_words),
            "alias_words": alias_words,
            "max_dependency_depth": max_depth,
        },
    }



def payload() -> dict[str, object]:
    missing = missing_paths()
    revisions = revision_sources()
    return {
        "project": "micromax",
        "rev": infer_rev(),
        "latest_note": latest_note(),
        "current_priorities": current_priorities(),
        "docs": DOCS,
        "code": CODE,
        "run_commands": RUN_COMMANDS,
        "top_level": sorted(x.name for x in ROOT.iterdir() if not x.name.startswith('.')),
        "revision_sources": revisions,
        "checks": {
            "missing_paths": missing,
            "revision_warnings": list(revisions.get("warnings") or []),
            "ok": len(missing) == 0 and bool(revisions.get("ok")),
        },
        "portability": portability_snapshot(),
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
    revisions = data.get("revision_sources")
    if isinstance(revisions, dict) and not revisions.get("ok", True):
        print("Revision warnings:")
        for warning in revisions.get("warnings") or []:
            print(f"  - {warning}")
        print()
    portability = data.get("portability")
    if isinstance(portability, dict):
        print("Portability snapshot:")
        print(f"  - cases: {portability.get('case_count', 0)}")
        categories = portability.get("category_counts")
        if isinstance(categories, dict) and categories:
            joined = ", ".join(f"{name}={categories[name]}" for name in sorted(categories))
            print(f"  - categories: {joined}")
        manifest = portability.get("boot_stdlib_manifest")
        if isinstance(manifest, dict):
            status = "all manifest cases present" if manifest.get("all_cases_present") else f"missing words: {', '.join(manifest.get('missing_words') or []) or '(unknown)'}"
            print(
                "  - stdlib manifest: "
                f"{manifest.get('word_count', 0)} words / {manifest.get('manifest_case_count', 0)} case refs ({status})"
            )
        source = portability.get("boot_stdlib_source")
        if isinstance(source, dict):
            print(
                "  - stdlib source: "
                f"{source.get('word_count', 0)} defs, {source.get('alias_count', 0)} aliases, depth<= {source.get('max_dependency_depth', 0)}"
            )
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
        checks = data["checks"]
        missing = list(checks["missing_paths"])
        warnings = list(checks.get("revision_warnings") or [])
        if missing or warnings:
            if not args.json:
                if missing:
                    print()
                    print("Missing referenced paths:")
                    for rel in missing:
                        print(f"  - {rel}")
                if warnings:
                    print()
                    print("Revision warnings:")
                    for warning in warnings:
                        print(f"  - {warning}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
