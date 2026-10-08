# Rev0904 scan-row budget

Rev0904 closes the next resource-exhaustion gap after the query byte budget:
bounded query strings can still drive broad candidate scans before the shared
post-call result budget runs.

## Why this mattered

`ed.fs-list` historically had a fixed returned-row cap, but the low-level helper
could still materialize a whole directory name list before slicing.  Palette path
completion had the same shape: a small query such as `./f` could call
`list(base.iterdir())` on a huge directory, then sort and slice.  Broad picker
hostcalls also accepted VM-owned limits in individual row builders but did not
have a single embedding-visible default for hostcall-driven scans.

This is the same class of failure described by OWASP API4:2023 unrestricted
resource consumption: endpoints need limits on records, payloads, CPU, memory,
file descriptors, and related resources before backend work scales with a client
request.  MITRE CWE-400 and CWE-834 frame the same issue as failing to track and
restrict resource consumption or loop iteration counts.  VS Code's Workspace
Trust docs remain the product-adjacent reminder that editor surfaces exposed to
workspace-driven code need explicit limits even when the feature is "just"
observational.

Sources checked during this landing:

- OWASP API4:2023 Unrestricted Resource Consumption — https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- MITRE CWE-400 Uncontrolled Resource Consumption — https://cwe.mitre.org/data/definitions/400.html
- MITRE CWE-834 Excessive Iteration — https://cwe.mitre.org/data/definitions/834.html
- VS Code Workspace Trust — https://code.visualstudio.com/docs/editing/workspaces/workspace-trust

## What changed

- `hostcall_boundary.py` now owns `DEFAULT_EDITOR_SCAN_MAX_ROWS`,
  `DEFAULT_FS_LIST_MAX_ROWS`, `effective_editor_scan_max_rows()`, and
  `effective_fs_list_max_rows()`.
- `install_editor_hostcalls()` installs VM-tunable defaults for
  `editor_hostcall_scan_max_rows` and `editor_hostcall_fs_list_max_rows`.
- Broad query/picker hostcalls route through the shared scan-row default when
  calling existing row builders.
- Recent-file prompt hostcalls pass the scan limit separately from their legacy
  prompt output cap, so a broad VM budget cannot widen the older 40-row prompt
  contract.
- `ed.fs-list` reads its limit from the VM and passes it through the filesystem
  hostcall layer.
- `list_dir_contained()` uses descriptor-bound `os.scandir(fd)` and stops after
  the row budget instead of materializing every directory name first.
- Command-palette path completion stops directory iteration after the scan budget
  and no longer calls `list(base.iterdir())` before filtering/slicing.
- `mxaudit --check` now hard-checks the scan-row-budget seam.

## Audit/refactor note

This landing deliberately keeps the boundary small.  It does not create another
registry.  The hostcall boundary module is the shared place for embedding-tunable
resource dials; the bridge is the single fan-out point from VM calls to editor
row builders; and `file_access.py` owns the fd-bound filesystem traversal detail.

One semantic tradeoff is intentional: extremely large directories may now return
an ordered subset of the first budgeted directory entries rather than sorting the
entire directory before slicing.  That is the point of the boundary.  A future UI
can add explicit pagination if it needs complete deterministic directory walks.

## Evidence

Focused evidence for rev0904:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_hostcall_boundary.py tests/test_editor_fs_list.py tests/test_command_palette_path_completion.py tests/test_mxaudit.py
```

The focused suite covers:

- scan budgets passed from bridge hostcalls into row builders;
- recent prompt hostcalls preserving their legacy output cap while passing the
  scan limit to the underlying section builder;
- disabled scan budgets passing `None` for embeddings with stronger external
  containment;
- `ed.fs-list` using the VM-tunable row budget;
- palette path completion not walking beyond the VM scan budget;
- audit output and hard-check coverage for `editor_scan_row_budget`.

## Remaining risk

The new row/candidate limits are not wall-clock cancellation.  A single allowed
row can still be expensive if its builder performs costly per-row work.  The
next high-risk lane is still `ed.require`: source load/eval needs a separate
size and execution-time story because it is executable authority rather than
plain observation.
