# Rev0925 — contained metadata, docs fallback, and fresh handoff evidence

## What changed

Optional plugin metadata existence now uses the contained plugin-file seam instead
of an ambient `Path.exists()` probe.

`src/micromax_editor/plugin_meta.py` now decides whether `plugin.json` is present
with `plugin_file_exists(meta_path, root)`.  That keeps the optional metadata path
on the same nominal-root and fd-target containment path already used for plugin
entry validation.

`src/micromax_editor/plugin_io.py` also tightens `plugin_file_exists()`: missing
files still return `False`, but containment failures no longer collapse into
absence.  A `plugin.json` symlink or fd target that escapes the plugin directory
is malformed package state and fails closed.  This matters because optional
metadata is policy-relevant: treating an escaping metadata file as merely absent
would let the package load with default metadata and bypass the warning/error
surface.

`src/micromax_editor/docs_index.py::_scan_doc_file()` also moved off direct
`Path.read_text()` and onto `read_file_prefix_contained()` with
`DOCS_SCAN_MAX_FILE_BYTES`. The public `scan_docs()` path already used bounded
records; this closes the private compatibility escape hatch instead of carrying
it forward as a recurring survivor note.

The same pass fixed a handoff-evidence waste path in `tools/mxtimely.py`.
`mxtimely` already bounded each child process, but it only wrote
`.artifacts/mxtimely-summary.json` after every step completed. If an outer
cloudtainer/tooltimer killed the run during `doctor` or a later optional test
slice, the archive could retain the previous revision's summary while the
console showed newer partial work. The runner now writes the summary after each
completed child and again at normal completion. That is not product progress,
but it is a real correction to the evidence lane: future sessions can tell which
short-window checks actually completed for the current revision.

## Why this was next

Rev0924 identified this as the smallest real survivor in the plugin-loading
path.  It was not worth starting a broad effect registry while this visible
capability-sensitive probe remained.  The path is small, user-influenced, and
security-adjacent: restricted startup and plugin inventory intentionally inspect
metadata without running plugin code, so metadata observation should not use a
different authority seam from source and entry checks.

The important lesson from the implementation audit is subtle: replacing
`Path.exists()` with a helper is not enough if the helper treats all exceptions
as `False`.  Optional resources still need three states:

- absent and harmless,
- present and contained, and
- present/malformed or escaping, which must fail closed.

That third state is the part most likely to be missed in future survivor sweeps.

The `mxtimely` change came from re-running `make timely` in this cloudtainer:
context, audit, lint, and portability completed, then the outer environment
terminated the run while the doctor child was still inside its own bounded
timeout. The stale `.artifacts/mxtimely-summary.json` left behind from rev0924 was
exactly the kind of severe but correctable waste named in rev0924. Persisting
summary evidence incrementally is a small refactor that prevents stale evidence
from poisoning the next handoff without expanding doctrine or adding another
registry.

## Online research used

Current Python `pathlib` documentation continues to describe existence/kind
helpers as high-level path observations: `Path.is_file()` normally follows
symlinks, and false can mean invalid, inaccessible, missing, or the wrong kind.
That supports Micromax's preference for a contained stat/read seam when the path
is plugin or workspace controlled rather than relying on a bare boolean helper.
Source: https://docs.python.org/3/library/pathlib.html

Python's `subprocess` timeout documentation still warns that process creation
itself may not be interruptible even when a timeout is supplied; that keeps the
project's worker-timeout claims honest and argues for small, explicit filesystem
surfaces rather than broad worker multiplication.  Source:
https://docs.python.org/3/library/subprocess.html

Python's `concurrent.futures` documentation now includes explicit
`ProcessPoolExecutor.terminate_workers()` and `kill_workers()` methods in the
3.14 series, reinforcing that running work needs a process-owned teardown story,
not just a future cancellation story.  Source:
https://docs.python.org/3/library/concurrent.futures.html

OWASP API4:2023 continues to frame missing execution-time, memory, file, process,
payload, and operation limits as unrestricted resource-consumption risk.  The
plugin metadata existence fix is not an API rate limit, but it follows the same
shape: user-influenced observation must have bounded/centralized semantics and
must not silently downgrade malformed authority state.  Source:
https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

WASI's public introduction still describes applications as starting with no
ambient authority and receiving only explicit host grants.  That remains a good
north star for the eventual plugin-process/component boundary, but this revision
keeps the work at the current in-process seam instead of freezing a premature
component API.  Source: https://wasi.dev/

## Audit/refactor notes

The focused code audit checked the current direct filesystem survivors again.
Most remaining direct reads/probes are either tooling/test surfaces or already
named lower-priority candidates:

- `src/micromax_editor/resource_roots.py` still uses direct implicit
  installed-resource `cand.is_dir()` selection.  This is one-shot startup
  discovery, not a plugin/workspace file read, so it remains lower risk than the
  plugin metadata path.
- `src/micromax_editor/docs_index.py::_scan_doc_file()` no longer uses direct
  `Path.read_text()`.  It now reuses contained prefix reads with the docs
  per-file byte budget, so the private compatibility helper matches the live
  catalog path instead of remaining a survivor.
- `src/micromax_editor/prompt_completion.py` still has a direct no-timeout
  standalone path.  Existing audit evidence checks that editor hostcall paths use
  the timeout branch; this is a future split/refactor candidate if standalone
  callers grow.
- `micromax.vm.VM._load_stdlib()` still reads trusted packaged stdlib resources
  directly.  That should be classified as trusted package loading, not confused
  with user/plugin filesystem authority.

`tools/mxaudit.py --check` now includes `plugin_optional_meta_exists_contained`,
covering the absence of `meta_path.exists()`, use of `plugin_file_exists()` for
optional metadata, fail-closed containment handling in the helper, and focused
regression coverage. It also includes the release-hygiene key
`timely_summary_incremental`, covering the incremental `mxtimely` summary write
and the regression that simulates interruption after the first completed child.
The existing `docs_catalog_scan_timeout_boundary` check now also covers the
private `_scan_doc_file()` fallback regression.

## Tests and audit

Focused validation run for the plugin metadata landing:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_plugin_json_schema.py tests/test_plugin_containment_and_caps.py::test_plugin_json_symlink_escape_is_not_read tests/test_mxaudit.py::test_mxaudit_json_reports_repeatable_structural_signals tests/test_mxaudit.py::test_mxaudit_human_output_names_major_pressure_surfaces
```

Result: 10 passed, with the existing multiprocessing fork deprecation warnings
on Python 3.13.

Focused validation for the docs fallback and incremental timely-summary refactors:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_docs_index.py tests/test_mxtimely.py tests/test_mxaudit.py
```

Result: 23 passed across the later combined run; the focused docs-index/mxaudit run also passed before the broader sweep.

Broader handoff validation later in the same cloudtainer:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxtimely.py tests/test_docs_index.py tests/test_plugin_json_schema.py tests/test_plugin_containment_and_caps.py::test_plugin_json_symlink_escape_is_not_read tests/test_mxaudit.py tests/test_revision_index.py tests/test_docs_living_hygiene.py
PYTHONPATH=src python tools/mxaudit.py --check
PYTHONPATH=src python tools/mxcontext.py --check
PYTHONPATH=src python tools/mxlint.py
PYTHONPATH=src python tools/mxtimely.py --skip-doctor
```

Result: 35 passed for the pytest group, `mxaudit --check` / `mxcontext --check` / `mxlint` passed, and `mxtimely --skip-doctor` passed with context, audit, lint, and portability rows written to `.artifacts/mxtimely-summary.json`.

## Remaining risk

This revision does not add an OS sandbox and does not claim hostile plugin
containment.  Plugin code still executes in-process after trust/grant decisions.
The direct-survivor list is smaller, but not gone; the next high-leverage work
is to split or fence the prompt-completion no-timeout standalone branch only if it
becomes capability-sensitive, and to classify trusted bundled stdlib resource
loading separately from workspace/plugin authority. `mxtimely --skip-doctor` is useful fresh handoff evidence
for this archive, but it is not a full `make timely` or full-suite claim. After
that, build a compact generated/resource-budget contract from existing code/test
facts rather than another hand-maintained prose registry.
