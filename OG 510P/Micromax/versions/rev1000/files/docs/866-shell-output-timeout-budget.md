# Rev0908 shell output and timeout budget

Rev0908 narrows the riskiest still-enabled host operation: `ed.shell`.  It is
already behind `cap.shell`, but once a trusted user enables it the old bridge
used `subprocess.run(..., capture_output=True, timeout=5)`.  That gave the child
a wall timeout, but stdout/stderr were still buffered before the VM's shared
post-hostcall result budget could inspect them, and timeout teardown only acted
through the immediate child process.

## Why this cut

Online research reinforced treating `ed.shell` as a resource endpoint, not just a
capability endpoint:

- Python's subprocess documentation says `run(..., timeout=...)` passes the
  timeout to `Popen.communicate()`, and the child is killed and waited for after
  timeout.  It also documents `start_new_session` as a POSIX process-session
  primitive.  That is useful, but it does not make post-return result budgets a
  pre-capture memory boundary.  Source: https://docs.python.org/3/library/subprocess.html
- OWASP API4:2023 defines unrestricted resource consumption around missing or
  inappropriate limits on execution timeout, memory, file descriptors, process
  count, upload/request size, operation count, and returned records.  That maps
  directly to a local VM-to-host shell API.  Source:
  https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- Python issue 37424 documents the familiar shell-timeout trap: killing the
  shell can leave a grandchild process behind.  Source:
  https://bugs.python.org/issue37424

## Landing

- `src/micromax_editor/host_process.py` is a new small process helper for editor
  hostcalls.  It starts shell children in their own process group/session when
  supported, streams stdout/stderr into bounded byte buffers, and tears down the
  process tree on timeout or output-budget exhaustion.
- `src/micromax_editor/hostcall_boundary.py` now owns VM-tunable shell defaults:
  `DEFAULT_SHELL_COMMAND_MAX_BYTES`, `DEFAULT_SHELL_OUTPUT_MAX_BYTES`, and
  `DEFAULT_SHELL_TIMEOUT_SECONDS`, plus operand-preserving command preflight and
  effective timeout/output helpers.
- `src/micromax_editor/micromax_bridge.py` installs those VM defaults and routes
  `ed.shell` through `run_shell_command_bounded()` instead of direct
  `subprocess.run(..., capture_output=True)`.
- `tools/mxaudit.py` hard-checks the `shell_output_timeout_budget` seam so later
  revisions cannot silently drop it while reporting all budget work as green.
- `tests/test_editor_shell_hostcall_budget.py` covers command-byte preflight with
  stack preservation, output truncation before the VM result budget, timeout
  error tuples, and POSIX detached-grandchild reaping.

## Guarantees

- Capability-denied `ed.shell` still preserves the command argument.
- Enabled `ed.shell` rejects oversized command strings before process creation
  and before consuming the operation argument.
- Enabled `ed.shell` bounds combined stdout/stderr capture before returning to
  the VM, so a successful child cannot allocate arbitrary output in the editor
  process before the shared hostcall result budget runs.
- Timeout and output-budget failures return non-fatal shell tuples:
  - `124, stdout, err` for timeout;
  - `125, stdout, err` for output-budget exhaustion.
- POSIX timeout teardown signals escaped descendant process groups before the
  direct shell group, matching the cloudtainer timeout lesson from rev0897.

## Risks left

- `cap.shell` remains intentionally powerful.  This is not a sandbox for hostile
  shell commands, native code, network access, or deliberately daemonized
  orphan processes that exit their parent before the timeout window.
- The output cap is disabled by setting `editor_shell_output_max_bytes <= 0`; that
  should only be used by embeddings with stronger external containment.
- Filesystem metadata and other accepted host operations still need true
  wall-clock cancellation beyond row/byte counts.
- Similar process-control logic still exists in tooling runners.  Do not spend
  another session centralizing every copy unless a failing test proves the need;
  the product boundary was the higher-risk path this turn.

## Validation

Focused validation run during the rev0908 landing:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_shell_hostcall_budget.py
```

Additional validation should run before calling this a release-wide checkpoint:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_shell_hostcall_budget.py tests/test_editor_hostcall_boundary.py tests/test_mxaudit.py tests/test_mxcontext.py tests/test_revision_index.py
python tools/mxaudit.py --check
python tools/mxcontext.py --check
python tools/mxlint.py
```
