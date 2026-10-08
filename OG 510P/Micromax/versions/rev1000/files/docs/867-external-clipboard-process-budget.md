# Rev0909 external clipboard process budget

Rev0909 narrows the next process boundary after `ed.shell`: the optional
`clipboard=external` integration.  External clipboard copy/paste is user-visible
and capability-gated for script-originated reads/writes, but it still launched
`wl-copy`/`xclip`/`pbcopy`/PowerShell-style helpers with
`subprocess.run(..., capture_output=True)`.  That meant import output and tool
stderr were buffered before the editor could apply a local byte budget, and
export could stream an arbitrarily large internal clipboard into an external
process.

## Why this cut

Online research reinforced treating clipboard helpers as resource endpoints, not
just UX conveniences:

- Python's subprocess docs describe process spawning, pipe connection, and
  timeout behavior around child processes.  The useful primitive here is not
  `capture_output=True`, but a `Popen`-level stream loop that can stop before a
  captured pipe grows without bound.  Source:
  https://docs.python.org/3/library/subprocess.html
- OWASP API4:2023 names execution timeout, memory, process count, payload size,
  operation count, and returned records as resource controls.  A local editor
  clipboard subprocess is not a web API, but it has the same shape: an input
  payload, an output payload, and a spawned helper competing for host resources.
  Source:
  https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- OSC 52 implementations often carry explicit maximum sequence sizes to avoid
  runaway terminal clipboard payloads.  Micromax already had an OSC 52 max; the
  missing sibling was an equivalent cap for external clipboard tools.  Source:
  https://chromium.googlesource.com/apps/libapps/+/HEAD/hterm/etc/osc52.el

## Landing

- `src/micromax_editor/host_process.py` now exposes `BoundedProcessResult` and
  `run_argv_bounded()`, the argv/non-shell sibling of `run_shell_command_bounded()`.
  It shares bounded stdout/stderr capture plus timeout/process-tree teardown with
  the shell helper, and adds optional stdin text piping for clipboard export.
- `src/micromax_editor/editor.py` routes `clipboard_external_export()` and
  `clipboard_external_import_text()` through `run_argv_bounded()` instead of
  direct `subprocess.run(..., capture_output=True)` calls.
- `src/micromax_editor/options_default.py` adds protected user-tunable knobs:
  `clipboard.external.inputmax` for copy/export payloads and
  `clipboard.external.outputmax` for combined stdout/stderr capture from helper
  tools.  Non-positive values disable the corresponding byte cap for embeddings
  with stronger external containment.
- `src/micromax_editor/option_policy.py` protects those options from
  script-originated mutation or reads, matching the existing external clipboard
  command and timeout knobs.
- `tools/mxaudit.py` hard-checks `external_clipboard_process_budget` so future
  revisions cannot report the process-boundary lane as green while silently
  reverting clipboard helpers to unbounded `capture_output`.

## Guarantees

- Script-originated external clipboard export remains gated by
  `cap.clipboard-write`.
- Script-originated external clipboard import remains gated by
  `cap.clipboard-read`.
- External clipboard export rejects oversized clipboard text before launching the
  helper process.
- External clipboard import bounds stdout/stderr before returning text to the
  editor action or `ed.clipboard-import` hostcall.
- External clipboard helper timeouts now use the same process-tree teardown seam
  as `ed.shell`, instead of relying on `subprocess.run()`'s immediate-child
  behavior.

## Risks left

- External clipboard tools are intentionally ambient OS integrations.  These
  caps do not sandbox the helper, prevent it from reading its own environment, or
  prevent platform clipboard races outside Micromax.
- Filesystem metadata/stat/open operations are still accepted host work without
  wall-clock cancellation.  That remains the higher-risk non-process lane.
- The old `Editor` class still owns these methods.  A future refactor could move
  external clipboard execution into a dedicated small module, but only after the
  executable boundary has been proven stable.

## Validation

Focused validation run during the rev0909 landing:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_host_process.py tests/test_editor_clipboard_external_export.py tests/test_editor_clipboard_external_import.py tests/test_mxaudit.py
```

Additional validation before release-wide claims:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_host_process.py tests/test_editor_clipboard_external_export.py tests/test_editor_clipboard_external_import.py tests/test_editor_option_authority.py tests/test_mxaudit.py tests/test_mxcontext.py tests/test_revision_index.py
python tools/mxaudit.py --check
python tools/mxcontext.py --check
python tools/mxlint.py
```
