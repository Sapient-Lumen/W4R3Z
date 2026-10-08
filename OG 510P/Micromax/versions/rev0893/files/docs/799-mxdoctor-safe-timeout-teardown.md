# rev0840 mxdoctor safe timeout teardown

## Why

`mxdoctor` now has bounded child commands, but its timeout cleanup still used the child PID as a process-group id directly. That usually works when `start_new_session=True`, yet it is a bad handoff primitive: if process-group creation fails, is unavailable, or races with child exit, a blind `killpg(pid, ...)` can signal something other than the intended pytest/lint child group.

`mxtest` already learned this lesson for aggregate pytest children. The doctor lane should use the same shape before it becomes the default rescue path for long or stuck preflight runs.

## Change

`tools/mxdoctor.py` now confirms that the child process group id exists and equals the child pid before using `killpg`. If that confirmation is unavailable, timeout teardown falls back to signaling only the direct child with `terminate()` / `kill()`.

The default `run()` path records the confirmed child process-group id immediately after `Popen`, then passes that specific id to timeout teardown. This keeps timeout cleanup bounded without relying on a later, potentially stale PID assumption.

## Audit/refactor note

This is a small code refactor, not a new policy layer. It removes one duplicated docstring line and adds focused tests around the timeout teardown primitive. The intent is to make the existing doctor timeout lane safer, not to widen the preflight registry.

## Current evidence lane

The aggregate manifest is still the riskiest unfinished item. After this source change, refresh `.artifacts/mxtest-all-64.json` with the standard resume command and verify it with `--verify-current` before packaging.
