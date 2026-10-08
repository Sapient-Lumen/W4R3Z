# Rev0913 — open and prompt filesystem timeout boundaries

Date: 2026-07-08

## Decision

Rev0913 keeps momentum on the riskiest unfinished filesystem seam from the
rev0912 audit: accepted editor command work still had ordinary `Path.exists`,
`Path.is_dir`, `Path.iterdir`, and direct read paths after capability preflight.
The change is deliberately practical rather than doctrinal.  Instead of adding a
new registry, it moves open/revert/source/user-init reads and broad prompt/palette
path completion onto the existing fd-backed, VM-tunable filesystem timeout
helpers, while refactoring palette/recent-file truth probes onto the central
fd-bound stat helper instead of scattered `Path.exists()` checks.

The heart of the mission remains least-authority end-user automation.  This
landing is one more host-effect boundary where the host can say: this operation
has an owner, a capability shape, a row or byte budget, and a wall-clock limit.

## Online research implication

OWASP API4:2023 frames missing or inappropriate resource limits as a resource
consumption vulnerability, including execution timeouts and file descriptors.
VS Code Workspace Trust and extension guidance reinforce the product lesson that
trust state and disabled/restricted capabilities must be enforced at execution,
not only hidden in UI.  WASI filesystem preopens remain a useful later shape for
explicit filesystem authority, but Micromax still needs to finish naming and
bounding its Python reference host effects before moving them across an isolation
adapter.

Sources reviewed during the landing:

- https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- https://code.visualstudio.com/docs/editing/workspaces/workspace-trust
- https://code.visualstudio.com/api/extension-guides/workspace-trust
- https://github.com/WebAssembly/wasi-filesystem
- https://github.com/WebAssembly/WASI

## What changed

- `src/micromax_editor/file_recovery.py` accepts an optional
  `timeout_seconds` argument and routes editor reads through
  `read_file_bytes_contained_bounded()` when supplied.
- `src/micromax_editor/editor.py` uses bounded stat/read seams for `open_file()`,
  `_read_current_disk_file()`, and user init loading, so open/revert/startup
  reads now share the VM-tunable filesystem stat/read timeout dials instead of
  direct path probes and direct byte loading.
- `src/micromax_editor/editor.py` moves command-palette broad path detection and
  open-path completion enumeration onto `stat_path_contained_bounded()` and
  `list_dir_contained_bounded()`, and centralizes recent/known-path truth cues
  on fd-bound `stat_path_contained()` rather than repeated `Path.exists()` /
  `Path.is_dir()` probes.
- `src/micromax_editor/prompt_completion.py` adds an optional timeout-backed path
  completion mode.  The direct `Path.iterdir` path remains only for simple
  standalone callers that do not supply a timeout.
- Script-context command-prompt path completion now uses
  `list_dir_contained_bounded()` with the existing scan budget and filesystem
  list timeout.
- `ed.require` and script-context core `include`/`require`/`reload` source path
  resolution now uses bounded stat before accepted source reads, and source reads
  pass the same read timeout into `read_file_for_editor()` while preserving
  source byte/depth/total/eval-step budgets.
- `tools/mxaudit.py` now hard-checks three executable seams:
  `editor_open_read_timeout_boundary`,
  `prompt_path_completion_timeout_worker`,
  `editor_user_init_timeout_boundary`, and
  `source_load_stat_timeout_boundary`.

## Guarantees

- Command-prompt and command-palette path completion still require `cap.fs-list`
  when running under script context or through palette filesystem rows.
- Path completion keeps the existing scan-row budget before sorting or row
  construction.
- `open_file()` still opens missing files as new empty buffers, but existing file
  reads now use the VM read-timeout dial.
- Revert/read-current-disk paths use the same bounded read path as open.
- Source loading keeps its executable source byte, graph, and eval-step budgets;
  the new stat/read timeouts bound accepted file observation before evaluation.
- User init loading keeps the same trusted-startup policy, but its accepted read
  now goes through the shared stat/read timeout path.
- Non-positive filesystem timeout values still disable the reference worker
  boundary for embedders with stronger external containment.

## Residual risk

- Save/write commit paths are still not a killable worker boundary.  The writer
  already has fd/dirfd containment and freshness checks, but wall-clock blocking
  during accepted write/fsync/rename work remains the next filesystem risk.
- Recent/known-path palette truth cues are centralized on fd-bound stat, but they
  deliberately do not spawn one timeout worker per visible row; a future pass
  should cache/batch these probes or make row-level stat timeout-safe without a
  process storm.
- The multiprocessing workers are reference-host recovery boundaries, not
  hostile-code or hostile-filesystem sandboxes.
- The project still needs a generated filesystem effect slice so audit checks do
  not keep growing as ad-hoc string predicates.

## Validation

Focused validation run during the rev0913 landing:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_prompt_completion.py tests/test_command_palette_path_completion.py tests/test_editor_script_context_fs_caps.py::test_script_command_prompt_path_completion_uses_vm_scan_budget tests/test_editor_script_context_fs_caps.py::test_script_command_prompt_path_completion_refuses_symlink_escape tests/test_editor_fs_open_save.py::test_open_file_uses_vm_read_timeout_boundary tests/test_editor_user_init.py tests/test_mxaudit.py -q
```

Result: focused lanes passed, with expected multiprocessing fork warnings in
timeout-worker lanes.

Additional handoff checks for this revision should include:

```bash
python tools/mxaudit.py --check
python tools/mxcontext.py --check
python tools/mxlint.py
```

## Next

1. Put save/write commit work behind a bounded ownership seam without weakening
   the existing dirfd containment and freshness contracts.
2. Batch or cache recent/known-path palette stat probes before adding per-row
   timeout workers.
3. Create the first data-backed filesystem effect slice and make `mxaudit` read
   it instead of adding another string predicate.
4. Compact old single-revision notes into living resource-boundary docs once the
   revision index carries the historical evidence.
