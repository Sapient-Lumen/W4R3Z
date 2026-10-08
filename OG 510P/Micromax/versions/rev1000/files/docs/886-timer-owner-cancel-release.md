# Rev0928 — timer owner cancellation release and heap-drift cap

## What changed

This revision moves the timer queue from a soft-cancel delayed callback ledger to
an explicit owner of live timer resources.

`src/micromax_editor/timers.py` now removes a canceled timer task from the live
`_tasks` map immediately.  The heap may retain a stale `(due, id)` tuple for the
normal `heapq` lazy-deletion pattern, but that tuple no longer points at the
quotation, plugin root, generation token, or script origin.  Repeated
schedule/cancel loops are bounded by `_maybe_compact_heap()`, which rebuilds the
heap from live tasks once stale ids outgrow a small floor.

The queue also exposes owner-level snapshot methods:

- `snapshot_state()` / `restore_state()` for all live timer rows;
- `snapshot_group_tasks()` / `restore_group_tasks()` for touched runtime groups;
- `retained_task_count()` and `heap_entry_count()` for diagnostic/resource tests.

`src/micromax_editor/plugin_runtime.py` now uses these owner methods for broad
runtime snapshots and touched group rollback instead of reaching first for
`_tasks`, `_heap`, and `_next_id`.  A fallback remains for legacy timer-like
objects, but the real editor timer path is now code-adjacent to the resource
owner.

## Why this was next

Rev0927 named timers as the strongest plugin-owned resource family to tackle
next because they combine deferred execution, unload/revoke semantics, stale
references, and pending-work budgets.

The concrete bug was not that canceled timers still fired.  They did not.  The
bug was lifetime and drift: `TimerQueue.cancel()` and `cancel_group()` marked
rows canceled but kept the task object in `_tasks` until the due time reached the
front of the heap.  A plugin could schedule a far-future callback and then be
canceled or unloaded, yet the canceled task row still retained its quotation and
captured plugin authority until some future pump pass.  A tight schedule/cancel
loop could also keep growing raw heap entries even with zero pending timers.

This is the kind of waste the cloudtainer should correct before adding more
registry doctrine.  Timers are delayed executable state; when the owner says the
row is canceled, the callback object should be released now.

## Online research used

Python's current `heapq` documentation still frames heaps as list-backed
priority queues and its implementation notes describe the usual mutable-priority
queue pattern: keep an entry dictionary, mark/remove entries, and skip stale heap
rows when popping.  That validates the lazy-id approach, but it also makes the
owner responsible for ensuring stale entries do not become an unbounded second
queue.  Source: https://docs.python.org/3/library/heapq.html

OWASP API4:2023 continues to describe unrestricted resource consumption in terms
of missing limits on execution time, memory, files/descriptors, processes,
operation counts, and returned records.  This timer change applies that lesson
to internal editor work: pending-count limits are not enough if canceled rows can
still retain large callback graphs or heap entries can grow without a live-task
counter.  Source:
https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

Current Python weak-reference guidance and common long-running application
practice treat unwanted strong references in caches, observer lists, and callback
registries as a leak pattern.  Micromax does not need weak references for timers
in this revision; it needs stricter ownership.  The new regression proves a
canceled timer releases a weak-referenceable payload after garbage collection.
Source: https://docs.python.org/3/library/weakref.html

## Audit/refactor notes

This is deliberately a small refactor, not a new effect registry.  The audit row
`timer_cancellation_releases_tasks` is backed by all of the following executable
facts:

- the timer queue has public state snapshot/restore methods;
- group-scoped plugin-runtime rollback uses the timer owner methods;
- cancellation pops task rows out of the live task map;
- stale heap entries are compacted under a bounded drift rule;
- tests prove canceled callback payloads are released; and
- tests prove repeated schedule/cancel loops keep raw heap entries bounded.

The fallback code in `plugin_runtime.py` still handles nonstandard timer-like
objects by direct attribute access.  That fallback is for defensive compatibility;
the editor's real `TimerQueue` no longer requires the lifecycle code to know its
private storage layout.

## Tests and audit

Focused timer and runtime validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q \
  tests/test_editor_timer_authority.py \
  tests/test_editor_highlight_and_timers.py \
  tests/test_runtime_registration_policy.py \
  tests/test_plugin_retired_wordlists.py \
  tests/test_plugin_runtime_group_policy.py::test_runtime_group_snapshot_captures_only_touched_action_keymap_timer_groups \
  tests/test_plugin_runtime_group_policy.py::test_runtime_group_restore_does_not_rewind_unrelated_action_keymap_timer_changes \
  tests/test_plugin_reload_recovery.py::test_plugin_reload_failure_cleans_staged_side_effects_and_keeps_old_runtime \
  tests/test_plugin_reload_recovery.py::test_plugin_unload_deinit_failure_keeps_plugin_loaded_and_restores_runtime
```

Result: 37 passed.

Full plugin runtime group policy validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_plugin_runtime_group_policy.py
```

Result: 37 passed.

Audit validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxaudit.py
PYTHONPATH=src python tools/mxaudit.py --check
```

Result: 2 passed, and `mxaudit --check` passed with `timer-release=True` in the
human output.

A selector typo run was also attempted for two nonexistent plugin reload test
names; pytest correctly reported no matching tests.  The valid selectors above
are the completed evidence for this archive.

## Remaining risk

Timers still execute in-process and callbacks still run with captured script or
plugin authority.  This revision fixes lifetime and owner boundaries for canceled
rows; it does not make timer callback execution hostile-code safe.

The next highest-leverage continuation is either:

1. consume the archive-member provenance that rev0926 started by adding a
   verifier/package-inspection lane; or
2. repeat this owner-refactor shape for another delayed family with large live
   graphs, such as prompt/history rows, macro slots, or active interactions.

The release-provenance path is probably the next best risk reducer because the
archive now contains member SHA-256 rows, but the toolchain still lacks a command
that verifies a shipped zip against its embedded manifest.
