#!/usr/bin/env python3
"""mxcontext.py

Emit a compact, catalog-backed repo-context snapshot for humans and LLMs.

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
    "README.md",
    "TODO.md",
    "docs/43-worklist.md",
    "docs/00-vision.md",
    "docs/security-boundaries.md",
    "docs/958-mission-product-reality-and-evidence-honesty-audit.md",
    "docs/01-llm-start-here.md",
    "docs/02-repo-map.md",
    "docs/revision-index.json",
    "docs/installed-help-manifest.txt",
    "docs/20-language-design.md",
    "docs/21-language-spec-sketch.md",
    "docs/22-two-tier-execution.md",
    "docs/23-data-model.md",
    "docs/24-bytecode-format.md",
    "docs/26-modules-and-hooks.md",
    "docs/30-editor-integration.md",
    "docs/31-host-api.md",
    "docs/32-capabilities.md",
    "docs/40-roadmap.md",
    "docs/41-decisions-log.md",
    "docs/42-portability-ledger.md",
    "docs/50-editor-behaviors.md",
    "docs/55-editor-command-bar.md",
    "docs/64-editor-prompt-completion.md",
    "docs/66-editor-micromax-commands.md",
    "docs/70-tutorial.md",
    "docs/71-cookbook.md",
    "docs/87-editor-config.md",
    "docs/95-plugin-json.md",
    "docs/98-help-browser.md",
    "docs/102-portability-suite.md",
    "docs/269-editor-goals-taste-trust-flow.md",
]

CODE = [
    "pyproject.toml",
    "Makefile",
    "src/micromax/vm.py",
    "src/micromax/core.py",
    "src/micromax/core_registry.py",
    "src/micromax/portability_suite.py",
    "src/micromax/stdlib/core.mx",
    "src/micromax_editor/__main__.py",
    "src/micromax_editor/editor.py",
    "src/micromax_editor/query_replace.py",
    "src/micromax_editor/default_keybindings.py",
    "src/micromax_editor/effect_contracts.py",
    "src/micromax_editor/buffer.py",
    "src/micromax_editor/command_dispatcher.py",
    "src/micromax_editor/micromax_bridge.py",
    "src/micromax_editor/capabilities.py",
    "src/micromax_editor/hostcall_boundary.py",
    "src/micromax_editor/file_access.py",
    "src/micromax_editor/fs_hostcalls.py",
    "src/micromax_editor/host_process.py",
    "src/micromax_editor/hostcall_transactions.py",
    "src/micromax_editor/plugin_runtime.py",
    "src/micromax_editor/plugin_grants.py",
    "src/micromax_editor/plugins.py",
    "src/micromax_editor/prompt_suggestions.py",
    "src/micromax_editor/resource_roots.py",
    "src/micromax_editor/workspace_trust.py",
    "src/micromax_editor/startup.py",
    "src/micromax_editor/discard_guard.py",
    "tools/mxcontext.py",
    "tools/mxaudit.py",
    "tools/mxeffects.py",
    "tools/mxtest.py",
    "tools/mxdoctor.py",
    "tools/mxtoolrun.py",
    "tools/mxtimely.py",
    "tools/mxrelease.py",
    "tools/mxrepro.py",
    "tools/mkrevzip.py",
    "tools/mxportable.py",
    "portability/kernel_cases.json",
    "tests/test_revision_index.py",
    "tests/test_docs_living_hygiene.py",
    "tests/test_mxcontext.py",
    "tests/test_mxaudit.py",
    "tests/test_effect_contracts.py",
    "tests/test_mkrevzip.py",
    "tests/test_mxrepro.py",
    ".github/workflows/reproducible-release.yml",
    "tests/test_editor_capabilities_registry.py",
    "tests/test_editor_default_keybindings_core.py",
    "tests/test_plugin_containment_and_caps.py",
    "tests/test_mxtest.py",
]

RUN_COMMANDS = [
    "make timely",
    "make timely-tests",
    "make release-suite",
    "make release-verify",
    "make release-next",
    "make release-inputs",
    "make repro-release",
    "python tools/mxrelease.py --package-inputs --package-inputs-json",
    "python tools/mxrelease.py --manifest .artifacts/mxrelease-full-suite.json --summary",
    "make test",
    "make doctor",
    "make test-all-chunks",
    "make test-verify-current",
    "python tools/mxtest.py --run-chunks 64 --strategy segment --isolate-files --resume --checkpoint-tests --max-new-tests 60 --max-new-files 4 --test-batch-size 10 --file-timeout 45 --max-runtime-seconds 18 --json .artifacts/mxtest-all-64.json",
    "python tools/mxtest.py --manifest-summary .artifacts/mxtest-all-64.json",
    "make context",
    "make context-json",
    "make context-check",
    "make audit-metrics",
    "make effect-contracts",
    "python tools/mxeffects.py --json --check",
    "python tools/mxlint.py",
    "python tools/mxportable.py --json",
    "python -m micromax_editor --help-doc docs/70-tutorial.md --dump-screen 24 80",
    "make revzip TAG=foobarnamesummaryhighlightcodename",
    "make revzip-verify ZIP=Micromax-rev####-stamp-tag.zip",
]



def _read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")




RECENT_REVISION_DOC_ENTRIES = 11
RECENT_REVISION_CODE_ENTRIES = 1
CONTEXT_DOC_LIMIT = 64
CONTEXT_CODE_LIMIT = 64
DERIVED_CONTEXT_PATHS = {"MICROMAX-CONTEXT.json"}
CORE_CONTEXT_DOCS = [
    "README.md",
    "TODO.md",
    "docs/43-worklist.md",
    "docs/00-vision.md",
    "docs/security-boundaries.md",
    "docs/958-mission-product-reality-and-evidence-honesty-audit.md",
    "docs/01-llm-start-here.md",
    "docs/02-repo-map.md",
    "docs/revision-index.json",
    "docs/installed-help-manifest.txt",
    "docs/20-language-design.md",
    "docs/31-host-api.md",
    "docs/32-capabilities.md",
]


def _dedupe_paths(paths: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for rel in paths:
        path = str(rel).strip()
        if not path or path in seen:
            continue
        seen.add(path)
        out.append(path)
    return out


def _load_revision_index() -> dict[str, object]:
    try:
        data = json.loads(_read_text("docs/revision-index.json"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def recent_revision_docs(*, entries: int = RECENT_REVISION_DOC_ENTRIES) -> list[str]:
    """Return docs referenced by the newest revision-index entries.

    The context snapshot used to require a manual docs-list edit for every
    revision note.  The revision index is already the authoritative revision
    ledger, so derive the newest handoff docs from it and keep the static list
    reserved for stable design docs. History paths stay catalog-only.
    """

    data = _load_revision_index()
    raw_entries = data.get("entries")
    if not isinstance(raw_entries, list):
        return []
    docs: list[str] = []
    for entry in raw_entries[: max(0, int(entries))]:
        if not isinstance(entry, dict):
            continue
        for rel in entry.get("docs") or []:
            if not isinstance(rel, str):
                continue
            path = rel.strip()
            if (
                path
                and path not in DERIVED_CONTEXT_PATHS
                and not path.startswith("docs/history/")
            ):
                docs.append(path)
    return _dedupe_paths(docs)


def context_docs() -> list[str]:
    """Return a compact handoff that always retains core and recent docs.

    Recent revision entries are the executable handoff and therefore outrank
    lower-priority stable reading.  Fill any remaining slots from ``DOCS``
    rather than allowing the context payload to grow forever as the ledger
    advances.  When core plus recent docs alone exceed the declared limit,
    return them all so the existing size regression fails visibly instead of
    silently dropping current evidence.
    """

    required = _dedupe_paths([*CORE_CONTEXT_DOCS, *recent_revision_docs()])
    if len(required) >= int(CONTEXT_DOC_LIMIT):
        return required
    required_set = set(required)
    remaining = [rel for rel in DOCS if rel not in required_set]
    return [*required, *remaining[: int(CONTEXT_DOC_LIMIT) - len(required)]]


def recent_revision_code(*, entries: int = RECENT_REVISION_CODE_ENTRIES) -> list[str]:
    """Return code/test paths from the newest revision-index entries.

    Stable entrypoints alone can omit the exact new owner a future agent most
    needs to inspect. Keep only the newest revision dynamic so the handoff stays
    compact while making the current landing executable rather than prose-only.
    """

    data = _load_revision_index()
    raw_entries = data.get("entries")
    if not isinstance(raw_entries, list):
        return []
    code: list[str] = []
    for entry in raw_entries[: max(0, int(entries))]:
        if not isinstance(entry, dict):
            continue
        for rel in entry.get("code") or []:
            if isinstance(rel, str) and rel.strip():
                code.append(rel.strip())
    return _dedupe_paths(code)


def context_code() -> list[str]:
    """Keep current touched code while bounding the generated handoff list.

    The current revision is executable handoff evidence and therefore required.
    Fill the remaining slots from the stable catalog in its existing order.  A
    revision that alone exceeds the ceiling remains visible as an over-budget
    result rather than silently dropping its changed surfaces.
    """

    required = recent_revision_code()
    if len(required) >= int(CONTEXT_CODE_LIMIT):
        return required
    required_set = set(required)
    stable = [rel for rel in CODE if rel not in required_set]
    stable_slots = int(CONTEXT_CODE_LIMIT) - len(required)
    return [*stable[:stable_slots], *required]


def _inventory_stats(base: Path) -> dict[str, int]:
    """Return cache-independent file and byte counts below ``base``."""

    ignored_parts = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    files = [
        path
        for path in base.rglob("*")
        if path.is_file()
        and not ignored_parts.intersection(path.parts)
        and path.suffix not in {".pyc", ".pyo"}
    ]
    return {
        "files": len(files),
        "bytes": sum(path.stat().st_size for path in files),
    }


def repo_inventory() -> dict[str, object]:
    """Summarize the full tree without enumerating it in the handoff payload."""

    docs = _inventory_stats(ROOT / "docs")
    source = _inventory_stats(ROOT / "src")
    tests = _inventory_stats(ROOT / "tests")
    docs["listed"] = len(context_docs())
    return {
        "docs": docs,
        "source": source,
        "tests": tests,
        "context": {
            "code_listed": len(context_code()),
            "commands": len(RUN_COMMANDS),
            "recent_revision_entries": RECENT_REVISION_DOC_ENTRIES,
        },
        "catalogs": {
            "revision_history": "docs/revision-index.json",
            "installed_help": "docs/installed-help-manifest.txt",
        },
    }

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



def _todo_section_entries() -> list[dict[str, Any]]:
    """Return parsed ``# TODO (revN)`` blocks in top-to-bottom order.

    Each checklist block is part of the archive's handoff trail. Surface the
    heading rev plus any explicit ``package rev...`` bullet so repo checks can
    spot stale packaged-rev claims in older recent sections too, not just the
    newest block.
    """

    lines = _read_text("TODO.md").splitlines()
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_lines: list[str] = []

    def finish() -> None:
        nonlocal current, current_lines
        if current is None:
            return
        entry = dict(current)
        entry["lines"] = list(current_lines)
        entry.setdefault("package_rev", None)
        entry.setdefault("package_line", "")
        entries.append(entry)
        current = None
        current_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# TODO'):
            finish()
            current = {
                "heading": stripped,
                "section_rev": _extract_rev(stripped),
            }
            continue
        if current is None:
            continue
        # Subheadings are presentation inside one revision handoff.  Only a
        # new top-level non-TODO document section ends the block; the next
        # ``# TODO`` was already handled above.
        if stripped.startswith('# ') and not stripped.startswith('# TODO'):
            finish()
            continue
        current_lines.append(line)
        if not stripped.startswith('- ['):
            continue
        if 'package rev' not in stripped.lower():
            continue
        pkg_rev = _extract_rev(stripped)
        if pkg_rev is not None:
            current["package_rev"] = pkg_rev
            current["package_line"] = stripped
        elif not current.get("package_line"):
            current["package_line"] = stripped
    finish()
    return entries



def _current_todo_section_lines() -> tuple[int | None, list[str]]:
    """Return the newest ``# TODO (revN)`` block as ``(rev, lines)``.

    The top checklist block is the closest thing this archive has to an explicit
    handoff contract for the next packaging loop. Keeping that block parseable
    lets ``mxcontext --check`` notice stale checklist bullets before they get
    baked into another release zip.
    """

    entries = _todo_section_entries()
    if not entries:
        return None, []
    first = entries[0]
    return first.get("section_rev"), list(first.get("lines") or [])



def _todo_current_section_package_rev() -> tuple[int | None, str]:
    """Return the packaged-rev checklist bullet from the newest TODO block."""

    entries = _todo_section_entries()
    if not entries:
        return None, ''
    first = entries[0]
    pkg_rev = first.get("package_rev")
    if isinstance(pkg_rev, int):
        return pkg_rev, str(first.get("package_line") or '')
    return None, str(first.get("package_line") or '')



def _todo_package_section_mismatches() -> list[dict[str, Any]]:
    """Return TODO sections whose explicit package bullet drifts from the heading rev."""

    mismatches: list[dict[str, Any]] = []
    for entry in _todo_section_entries():
        section_rev = entry.get("section_rev")
        package_rev = entry.get("package_rev")
        if not isinstance(section_rev, int) or not isinstance(package_rev, int):
            continue
        if section_rev == package_rev:
            continue
        mismatches.append(
            {
                "section_rev": section_rev,
                "package_rev": package_rev,
                "package_line": str(entry.get("package_line") or ''),
                "heading": str(entry.get("heading") or ''),
            }
        )
    return mismatches






def _todo_recent_handoff_blocks() -> list[dict[str, Any]]:
    """Return recent TODO handoff blocks from the checklist-era trail.

    The newest part of ``TODO.md`` uses a repeated pattern of:
    ``RevN note`` → ``Latest … landing (revN)`` → ``# TODO (revN)``.
    Historical entries used ``tiny`` while substantive landings now say
    ``substantive``; both labels carry the same revision-currentness contract.
    Future humans/LLMs rely on that top trail as the archive's most legible
    handoff lane, so ``mxcontext --check`` should notice orphaned or mismatched
    preambles there too, not just stale package bullets inside checklist blocks.
    """

    lines = _read_text("TODO.md").splitlines()
    heading_re = re.compile(r'^# TODO \(rev(\d+)\)$')
    note_re = re.compile(r'^Rev(\d+) note:')
    landing_re = re.compile(r'^Latest (?:substantive|tiny) landing \(rev(\d+)\):')
    blocks: list[dict[str, Any]] = []
    outside_lines: list[str] = []
    in_recent_section = False
    recent_started = False

    for line in lines:
        heading_match = heading_re.match(line)
        if heading_match:
            heading_rev = int(heading_match.group(1))
            if heading_rev <= 600:
                break
            recent_started = True
            note_revs = [int(m.group(1)) for m in map(note_re.match, outside_lines) if m]
            landing_revs = [int(m.group(1)) for m in map(landing_re.match, outside_lines) if m]
            blocks.append(
                {
                    'heading_rev': heading_rev,
                    'note_revs': note_revs,
                    'landing_revs': landing_revs,
                    'last_note_rev': note_revs[-1] if note_revs else None,
                    'last_landing_rev': landing_revs[-1] if landing_revs else None,
                    'preamble_lines': [line for line in outside_lines if line.strip()],
                }
            )
            outside_lines = []
            in_recent_section = True
            continue
        if not recent_started:
            outside_lines.append(line)
            continue
        if in_recent_section:
            if note_re.match(line) or landing_re.match(line):
                in_recent_section = False
                outside_lines = [line]
            continue
        outside_lines.append(line)
    return blocks



def _todo_recent_handoff_mismatches() -> list[dict[str, Any]]:
    """Return recent handoff-block mismatches from the TODO checklist trail."""

    mismatches: list[dict[str, Any]] = []
    for block in _todo_recent_handoff_blocks():
        heading_rev = block['heading_rev']
        note_revs = list(block.get('note_revs') or [])
        landing_revs = list(block.get('landing_revs') or [])
        extra_revs = sorted((set(note_revs) | set(landing_revs)) - {heading_rev}, reverse=True)
        if block.get('last_note_rev') != heading_rev or block.get('last_landing_rev') != heading_rev or extra_revs:
            mismatches.append(
                {
                    'heading_rev': heading_rev,
                    'last_note_rev': block.get('last_note_rev'),
                    'last_landing_rev': block.get('last_landing_rev'),
                    'extra_revs': extra_revs,
                }
            )
    return mismatches
def revision_sources() -> dict[str, Any]:
    todo_lines = _read_text("TODO.md").splitlines()
    todo_first_line = todo_lines[0].strip() if todo_lines else ""
    readme_note = latest_note() or ""
    todo_first_rev = _extract_rev(todo_first_line)
    todo_heading_rev = _todo_heading_rev()
    todo_section_rev, _todo_section_lines = _current_todo_section_lines()
    todo_package_rev, todo_package_line = _todo_current_section_package_rev()
    todo_package_section_mismatches = _todo_package_section_mismatches()
    todo_recent_handoff_mismatches = _todo_recent_handoff_mismatches()
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
        if todo_section_rev is not None and todo_section_rev != current_rev:
            warnings.append(
                f"TODO.md current-section rev {todo_section_rev} does not match current rev {current_rev}"
            )
        for mismatch in todo_package_section_mismatches:
            section_rev = mismatch.get("section_rev")
            package_rev = mismatch.get("package_rev")
            warnings.append(
                f"TODO.md section rev {section_rev} has package bullet rev {package_rev}"
            )
        for mismatch in todo_recent_handoff_mismatches:
            heading_rev = mismatch.get("heading_rev")
            last_note_rev = mismatch.get("last_note_rev")
            last_landing_rev = mismatch.get("last_landing_rev")
            extra_revs = mismatch.get("extra_revs") or []
            if last_note_rev != heading_rev:
                warnings.append(
                    f"TODO.md handoff block before rev {heading_rev} has note rev {last_note_rev}"
                )
            if last_landing_rev != heading_rev:
                warnings.append(
                    f"TODO.md handoff block before rev {heading_rev} has landing rev {last_landing_rev}"
                )
            if extra_revs:
                extras = ', '.join(f"rev{rev}" for rev in extra_revs)
                warnings.append(
                    f"TODO.md handoff block before rev {heading_rev} contains orphan rev block(s): {extras}"
                )
    return {
        "current_rev": current_rev,
        "todo_first_line": todo_first_line,
        "todo_first_line_rev": todo_first_rev,
        "todo_heading_rev": todo_heading_rev,
        "todo_current_section_rev": todo_section_rev,
        "todo_current_section_package_rev": todo_package_rev,
        "todo_current_section_package_line": todo_package_line,
        "todo_package_section_mismatches": todo_package_section_mismatches,
        "todo_recent_handoff_mismatches": todo_recent_handoff_mismatches,
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
    """Return the numbered current-work list from the living TODO.

    The heading is prose, not a schema.  Accept the recent names used by the
    living handoff so a wording cleanup cannot silently erase priorities from
    human/JSON context output.
    """

    headings = {
        "## current priorities",
        "## highest-value next work",
        "## next up (high leverage)",
    }
    lines = _read_text("TODO.md").splitlines()
    in_section = False
    priorities: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.lower() in headings:
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
    for rel in context_docs() + context_code():
        if not (ROOT / rel).exists():
            missing.append(rel)
    return missing



def _load_portability_cases() -> list[dict[str, object]]:
    path = ROOT / "portability" / "kernel_cases.json"
    return json.loads(path.read_text(encoding="utf-8"))



def startup_snapshot() -> dict[str, object]:
    from micromax import VM

    vm = VM(strict_stdlib=True)
    return {
        "stdlib": vm.stdlib_health(),
        "diagnostics": list(vm.startup_diagnostics),
        "has_finally": vm.find_word("finally") is not None,
        "has_2drop": vm.find_word("2drop") is not None,
    }


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
        "docs": context_docs(),
        "code": context_code(),
        "run_commands": RUN_COMMANDS,
        "inventory": repo_inventory(),
        "startup": startup_snapshot(),
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
    inventory = data.get("inventory")
    if isinstance(inventory, dict):
        docs = inventory.get("docs")
        context = inventory.get("context")
        tests = inventory.get("tests")
        print("Curated handoff scope:")
        if isinstance(docs, dict):
            print(
                "  - docs: "
                f"{docs.get('listed', 0)} listed / {docs.get('files', 0)} in repository; "
                "full ledger: docs/revision-index.json"
            )
        if isinstance(context, dict):
            print(f"  - code entrypoints: {context.get('code_listed', 0)}")
        if isinstance(tests, dict):
            print(f"  - test files: {tests.get('files', 0)} (summarized, not enumerated)")
        print()
    startup = data.get("startup")
    if isinstance(startup, dict):
        stdlib = startup.get("stdlib")
        if isinstance(stdlib, dict):
            print("Startup snapshot:")
            print(
                "  - stdlib: "
                f"{stdlib.get('state', 'unknown')} "
                f"({stdlib.get('resource', 'unknown')})"
            )
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
    print("Curated document entrypoints:")
    for p in data["docs"]:
        print(f"  - {p}")
    print()
    print("Curated code entrypoints:")
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
