# Rev0907 path-completion scan budget

Rev0907 closes one remaining broad-builder resource lane without adding a new
registry: command-prompt filesystem completion now uses the existing VM-tunable
editor scan budget before it iterates and sorts directory entries.

## Why this mattered

Rev0904 capped many hostcall row builders, and rev0906 capped executable source
load graphs.  Ordinary command prompt completion still had a smaller but real
hole: `open` / `save` / `cd` path completion outside script context called the
pure `path_completion_candidates()` helper, which converted `base.iterdir()` to
a full list before filtering, sorting, and returning only a visible page.  In a
large directory, one allowed completion request could still become an unbounded
snapshot and sort.

Online sources used for this cut:

- OWASP API4:2023 Unrestricted Resource Consumption —
  https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- MITRE CWE-400 Uncontrolled Resource Consumption —
  https://cwe.mitre.org/data/definitions/400.html
- VS Code Workspace Trust —
  https://code.visualstudio.com/docs/editing/workspaces/workspace-trust

The narrow lesson is not that Micromax gained hostile-code isolation.  It is
that resource limits need to cover the work done before an API returns: execution
time, record counts, candidate counts, and payload size must all be made visible
at the boundary.

## What changed

- `prompt_completion.path_completion_candidates()` now accepts `scan_limit` and
  iterates a directory lazily.  It stops before fetching more than the requested
  number of entries, then sorts only the bounded candidate set.
- `Editor._path_completion_candidates()` now passes
  `effective_editor_scan_max_rows(self.vm)` to ordinary command-prompt path
  completion.
- Script-context prompt completion keeps the explicit `cap.fs-list` and
  `cap.fs-root` checks, but now uses the same VM scan budget when calling
  `list_dir_contained()`.  If an embedding intentionally disables that VM scan
  cap, the old script-context hard stop of 1000 entries is preserved.
- `mxaudit --check` now hard-checks the `prompt_path_completion_scan_budget`
  seam separately from the broader `editor_scan_row_budget` seam.
- A small doc hygiene refactor removed a duplicate `cands` line from the
  Micromax prompt-completion plugin contract comment.

## Audit/refactor note

This deliberately reuses `editor_hostcall_scan_max_rows`; it does not add a
completion-only setting.  Completion is another broad host-state scan, so the
existing row-builder budget is the right owner.  The pure helper remains
editor-independent and archive-friendly: callers without a VM can pass no
`scan_limit` and keep historical behavior, while editor-backed completion gets
the same boundary as palette/docs/help/buffer scans.

## Evidence

Focused evidence for rev0907:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_prompt_completion.py tests/test_editor_script_context_fs_caps.py
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_prompt_completion.py tests/test_editor_script_context_fs_caps.py tests/test_mxaudit.py tests/test_mxcontext.py tests/test_revision_index.py tests/test_docs_living_hygiene.py
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxlint.py
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxaudit.py --check
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxcontext.py --check
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxportable.py --quiet
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxtimely.py --skip-doctor --skip-tests --summary-json .artifacts/mxtimely-summary.json
```

The focused suite covers:

- pure path completion returning no rows and not advancing directory iteration
  when `scan_limit=0`;
- pure path completion inspecting exactly the bounded subset before sorting;
- script-context command-prompt path completion passing the VM scan budget to the
  contained directory-list seam;
- existing script-context symlink-escape refusal remaining intact.

## Remaining risk

This is still cooperative in-process resource control, not wall-clock
cancellation.  A single allowed directory entry can still make filesystem
metadata calls slow on unusual filesystems, and normal interactive completion can
still be expensive when an embedding disables the scan cap.  The next high-risk
runtime lane is still true timeout/cancellation for host operations that can
block after count budgets have accepted the work.
