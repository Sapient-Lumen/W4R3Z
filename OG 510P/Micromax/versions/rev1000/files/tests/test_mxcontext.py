from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]



def _load_mxcontext_module():
    spec = importlib.util.spec_from_file_location('mxcontext_test_module', ROOT / 'tools' / 'mxcontext.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module



def _expected_rev() -> int:
    first = (ROOT / "TODO.md").read_text(encoding="utf-8").splitlines()[0]
    match = re.search(r"rev\s*(\d+)", first, flags=re.IGNORECASE)
    assert match is not None
    return int(match.group(1))



def test_mxcontext_cli_human_output_includes_rev_and_priorities() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / 'tools' / 'mxcontext.py')],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    assert 'micromax repo context' in proc.stdout
    assert f"Rev: {_expected_rev()}" in proc.stdout
    assert 'Current priorities:' in proc.stdout
    assert 'make context-json' in proc.stdout
    assert 'make context-check' in proc.stdout



def test_mxcontext_cli_can_emit_json_and_check_referenced_paths() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "mxcontext.py"), "--json", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    expected_rev = _expected_rev()

    assert payload["project"] == "micromax"
    assert payload["rev"] == expected_rev
    assert payload["checks"]["ok"] is True
    assert payload["checks"]["missing_paths"] == []
    assert payload["revision_sources"]["ok"] is True
    assert payload["revision_sources"]["todo_current_section_rev"] == expected_rev
    assert payload["revision_sources"]["todo_current_section_package_rev"] == expected_rev
    assert payload["revision_sources"]["todo_current_section_package_line"].startswith(
        "- [x] package rev"
    )
    assert payload["revision_sources"]["todo_package_section_mismatches"] == []
    assert payload["revision_sources"]["todo_recent_handoff_mismatches"] == []

    core_docs = {
        "README.md",
        "TODO.md",
        "docs/00-vision.md",
        "docs/security-boundaries.md",
        "docs/958-mission-product-reality-and-evidence-honesty-audit.md",
        "docs/01-llm-start-here.md",
        "docs/02-repo-map.md",
        "docs/43-worklist.md",
        "docs/revision-index.json",
        "docs/installed-help-manifest.txt",
        "docs/20-language-design.md",
        "docs/31-host-api.md",
        "docs/32-capabilities.md",
    }
    assert core_docs <= set(payload["docs"])

    revision_index = json.loads(
        (ROOT / "docs" / "revision-index.json").read_text(encoding="utf-8")
    )
    recent_docs = {
        rel
        for entry in revision_index["entries"][:11]
        for rel in entry.get("docs") or []
        if rel != "MICROMAX-CONTEXT.json" and not rel.startswith("docs/history/")
    }
    assert recent_docs <= set(payload["docs"])
    current_code = set(revision_index["entries"][0].get("code") or [])
    assert current_code <= set(payload["code"])

    # A compact context points to catalogs; it does not reproduce the catalog.
    assert len(payload["docs"]) <= 64
    assert len(payload["code"]) <= 64
    assert len(proc.stdout.encode("utf-8")) < 24_000
    assert not any(path.startswith("docs/history/") for path in payload["docs"])
    assert all((ROOT / rel).exists() for rel in payload["docs"] + payload["code"])

    inventory = payload["inventory"]
    assert inventory["docs"]["listed"] == len(payload["docs"])
    assert inventory["docs"]["files"] >= len(payload["docs"])
    assert inventory["source"]["files"] > 0
    assert inventory["tests"]["files"] > 0
    assert inventory["context"]["code_listed"] == len(payload["code"])
    assert inventory["context"]["recent_revision_entries"] == 11
    assert inventory["catalogs"] == {
        "installed_help": "docs/installed-help-manifest.txt",
        "revision_history": "docs/revision-index.json",
    }
    assert "make context-json" in payload["run_commands"]
    assert "make context-check" in payload["run_commands"]
    assert "make audit-metrics" in payload["run_commands"]
    assert "make repro-release" in payload["run_commands"]
    assert "make revzip-verify ZIP=Micromax-rev####-stamp-tag.zip" in payload["run_commands"]
    assert "tools/mxaudit.py" in payload["code"]
    assert payload["startup"]["stdlib"]["state"] == "loaded"
    assert payload["portability"]["case_count"] > 0
    assert payload["portability"]["boot_stdlib_manifest"]["all_cases_present"] is True

def test_todo_package_section_mismatch_parser_reports_history_drift() -> None:
    module = _load_mxcontext_module()
    original = module._read_text

    def fake_read_text(rel: str) -> str:
        if rel == 'TODO.md':
            return """Rev700 note: test

# TODO (rev700)
## Completed in this revision
- [x] package rev700

## Current priorities
1. verify publication evidence

# TODO (rev699)
- [x] package rev698

# TODO (rev698)
- [x] package rev698
"""
        if rel == 'README.md':
            return 'Rev700 note: test\n'
        return original(rel)

    module._read_text = fake_read_text
    try:
        mismatches = module._todo_package_section_mismatches()
        assert mismatches == [
            {
                'section_rev': 699,
                'package_rev': 698,
                'package_line': '- [x] package rev698',
                'heading': '# TODO (rev699)',
            }
        ]
        revisions = module.revision_sources()
    finally:
        module._read_text = original

    assert revisions['todo_current_section_rev'] == 700
    assert revisions['todo_current_section_package_rev'] == 700
    assert revisions['todo_package_section_mismatches'] == mismatches
    assert 'TODO.md section rev 699 has package bullet rev 698' in revisions['warnings']


def test_todo_recent_handoff_mismatch_parser_reports_orphan_blocks() -> None:
    module = _load_mxcontext_module()
    original = module._read_text

    def fake_read_text(rel: str) -> str:
        if rel == 'TODO.md':
            return """Rev702 note: test

Latest substantive landing (rev702): test

# TODO (rev702)
- [x] package rev702

Rev701 note: test

Latest tiny landing (rev701): test

Rev700 note: orphan

Latest tiny landing (rev700): orphan

# TODO (rev701)
- [x] package rev701

# TODO (rev600)
"""
        if rel == 'README.md':
            return 'Rev702 note: test\n'
        return original(rel)

    module._read_text = fake_read_text
    try:
        mismatches = module._todo_recent_handoff_mismatches()
        revisions = module.revision_sources()
    finally:
        module._read_text = original

    assert mismatches == [
        {
            'heading_rev': 701,
            'last_note_rev': 700,
            'last_landing_rev': 700,
            'extra_revs': [700],
        }
    ]
    assert revisions['todo_recent_handoff_mismatches'] == mismatches
    assert 'TODO.md handoff block before rev 701 has note rev 700' in revisions['warnings']
    assert 'TODO.md handoff block before rev 701 has landing rev 700' in revisions['warnings']
    assert 'TODO.md handoff block before rev 701 contains orphan rev block(s): rev700' in revisions['warnings']


def test_todo_recent_handoff_parser_accepts_current_and_historical_landing_labels() -> None:
    module = _load_mxcontext_module()
    original = module._read_text

    def fake_read_text(rel: str) -> str:
        if rel == 'TODO.md':
            return """Rev703 note: current wording

Latest substantive landing (rev703): current wording

# TODO (rev703)
- [x] package rev703

Rev702 note: historical wording

Latest tiny landing (rev702): historical wording

# TODO (rev702)
- [x] package rev702

# TODO (rev600)
"""
        if rel == 'README.md':
            return 'Rev703 note: current wording\n'
        return original(rel)

    module._read_text = fake_read_text
    try:
        assert module._todo_recent_handoff_mismatches() == []
        revisions = module.revision_sources()
    finally:
        module._read_text = original

    assert revisions['todo_recent_handoff_mismatches'] == []
    assert not any('TODO.md handoff block' in warning for warning in revisions['warnings'])


def test_mxcontext_current_revision_code_follows_revision_index() -> None:
    module = _load_mxcontext_module()
    revision_index = json.loads((ROOT / "docs" / "revision-index.json").read_text(encoding="utf-8"))
    expected: list[str] = []
    for entry in revision_index["entries"][: module.RECENT_REVISION_CODE_ENTRIES]:
        for rel in entry.get("code") or []:
            if isinstance(rel, str) and rel not in expected:
                expected.append(rel)

    assert expected
    assert module.recent_revision_code() == expected
    assert set(expected) <= set(module.context_code())
    assert "src/micromax_editor/discard_guard.py" in module.context_code()
    assert "src/micromax_editor/startup.py" in module.context_code()


def test_mxcontext_recent_revision_docs_follow_revision_index() -> None:
    module = _load_mxcontext_module()
    revision_index = json.loads((ROOT / 'docs' / 'revision-index.json').read_text(encoding='utf-8'))
    expected: list[str] = []
    for entry in revision_index['entries'][: module.RECENT_REVISION_DOC_ENTRIES]:
        for rel in entry.get('docs') or []:
            if (
                isinstance(rel, str)
                and rel != 'MICROMAX-CONTEXT.json'
                and not rel.startswith('docs/history/')
                and rel not in expected
            ):
                expected.append(rel)

    assert expected
    assert module.recent_revision_docs() == expected
    assert set(expected) <= set(module.context_docs())
