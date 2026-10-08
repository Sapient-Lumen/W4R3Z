# Rev770 — mxtest interrupt cleanup, plugin dictionary rollback, and pycache waste control

## Why this mattered

The remaining high-risk gaps were not registry/documentation problems. They were state-boundary problems:

1. an interrupted `mxtest` parent could leave a live pytest child behind when the cloudtainer killed the parent process;
2. plugin reload/unload rollback covered editor registrations, but failed plugin source or lifecycle code could still leave VM dictionary/module changes behind;
3. normal test/doctor runs created `.pyc` churn that the archive already filters out, but that still wastes cloudtainer I/O and makes working trees noisy.

## What changed

`tools/mxtest.py` now installs temporary signal handlers while a pytest child is active. `SIGTERM`, `SIGINT`, and `SIGHUP` clean the confirmed child process group before `mxtest` exits with the conventional signal return code. For aggregate `--run-chunks` runs, an interrupt during a chunk now rewrites the JSON manifest with a partial interrupted chunk record instead of leaving only a stale `running` checkpoint.

`src/micromax_editor/plugin_runtime.py` now snapshots VM dictionary/module topology: wordlists, wordlist names, modules, search order, current wordlist, next wordlist id, module stack, loaded paths, and dictionary version. `PluginManager` uses that snapshot with the existing runtime-registration snapshot, so failed load/reload/unload transitions roll back both editor registrations and VM dictionary state.

The pytest isolation helpers in `tools/mxtest.py`, `tools/mxdoctor.py`, and `scripts/test.sh` now default `PYTHONDONTWRITEBYTECODE=1` alongside `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`. This does not replace archive filtering, but it reduces recurring pycache churn during normal handoff validation.

## Regression coverage

Focused regressions cover:

- signal cleanup of a live mxtest child before `MxtestInterrupted` propagates;
- partial aggregate manifest records for interrupted chunks;
- plugin source failure rolling back modules/wordlists/loaded paths;
- plugin unload `deinit` failure rolling back dictionary mutations while keeping the old plugin alive;
- plugin reload deinit failure preserving the old plugin dictionary and runtime state;
- the no-bytecode default in mxtest/doctor test environments.

A live probe also used `timeout --preserve-status` around a sleeping pytest child. The revised mxtest exited with code `143`, printed the cleanup message, wrote a partial JSON run manifest, and left no matching sleep-test pytest process behind.

The direct signal-cleanup regression stays in the focused mxtest validation lane, but is intentionally not part of the default `mxdoctor` preflight. That test probes process-termination semantics and can interact poorly with wrapper process groups; doctor should stay a reliable handoff command, not a self-signal stress probe.

## Remaining risk

This is still process-management best effort, not a supervisor. If the host sends an uncatchable signal such as `SIGKILL`, Python cannot clean descendants or write a final checkpoint. The improvement is that normal cloudtainer/CI termination signals now clean up the child group and leave explicit partial evidence.

The plugin dictionary snapshot is intentionally topological. It restores word/module/search-order state, but it does not deep-copy arbitrary mutable Python objects captured inside word implementations. That is the right boundary for now; a full VM transaction would be a larger design lane.
