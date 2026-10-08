Rev0893 note: saved macros from retired plugin generations now prune before playback/read/list exposure, and ed.after has a host-owned pending timer budget.

# LLM start here (rev0893)

## Heart of the project

Micromax is a least-authority automation language with a recoverable editor host. The small concatenative VM is intended to be one substrate for configuration, macros, and plugins. The editor is the proving ground for explicit effects, capability checks, provenance, headless truth, and honest recovery.

Do not reduce the mission to “build a terminal editor.” Do not describe the current in-process capability model as a hostile-code sandbox.

## Current landing

Rev0893 closes another stale delayed-execution lane.  Saved macro slots can carry plugin root/generation provenance and later replay command or action steps.  They now stale-check before playback, raw read, detail, or list exposure; reinserted macro rows from a retired plugin generation fail with a clear `macro play: stale plugin macro ...` message and are removed.

The same revision adds a concrete pending-work budget for timer callbacks.  `ed.after` no longer appends directly to the timer queue; it goes through `Editor.schedule_timer_checked()`, which refuses new delayed work once `max_pending_timers` is full.  This is intentionally a host-owned pressure limit, not a claim of hostile-code containment.

Focused rev0893 lane:

```bash
PYTHONPATH=src pytest -q tests/test_editor_timer_authority.py tests/test_editor_macro_authority.py tests/test_editor_macros_named.py tests/test_plugin_runtime_group_policy.py tests/test_plugin_retired_wordlists.py tests/test_mxaudit.py
python tools/mxaudit.py --check
python tools/mxcontext.py --check
python tools/mxlint.py
```

## Highest-leverage next work

1. Enumerate remaining plugin-owned resource handles outside dictionary words, generated callbacks, active interactions, and macro steps.
2. Split one real broad source/lifecycle effect family into typed capture/commit/abort helpers with the broad snapshot as an oracle.
3. Add host-owned payload/result/output/prompt/buffer/cancellation budgets before isolation work.
4. Build the effect lifecycle matrix only where it removes implementation risk.
5. Add lock/CI/provenance and a package-version versus archive-revision policy.
6. Compact historical docs and evidence machinery.
7. Extract only contract-backed responsibilities from `Editor`, with measured ownership reduction.

## Avoid

- deleting or compacting runtime objects without proving stale references fail or are metadata-only;
- another sidecar-specific rollback patch without placing the sidecar under its owning transaction;
- a universal untyped ownership registry;
- broad `Editor` rewrites;
- treating more revision notes or evidence-runner features as product progress;
- claiming that snapshots cover arbitrary edits, durable/external effects, wall-clock blocking, memory pressure, or hostile code;
- moving the current implicit internal API wholesale into a process or Wasm boundary.
