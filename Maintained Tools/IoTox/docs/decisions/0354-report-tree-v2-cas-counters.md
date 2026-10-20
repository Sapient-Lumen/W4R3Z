# ADR 0354: Report tree-v2 CAS reconciliation counters

- Status: accepted and implemented
- Date: 2026-09-09

## Context

The tree-v2 scale frontier now has enough local optimizations that wall-clock regressions are no
longer self-explanatory. A reconcile can spend time in several content-free phases:

- walking selected source paths;
- hashing source file contents;
- importing or reusing immutable CAS objects;
- merging signed branch metadata;
- preserving sparse unselected local files; and
- rebuilding/exchanging the visible projection.

ADRs 0350 and 0352 exposed source-walk and preservation counters, but the local CAS import phase
remained hidden inside `reconcile_tree_v2_workspace()`. That made a no-op reconcile, a changed-file
reconcile that reuses existing CAS objects, and a changed-file reconcile that installs new CAS
objects look too similar from the operator surface.

## Decision

Add content-free CAS accounting to `TreeV2ReconcileResult` and `sync-publish`:

- `cas-inspected=N`;
- `cas-inspected-bytes=N`;
- `cas-installed=N`;
- `cas-installed-bytes=N`; and
- `cas-reused=N`.

These counters are populated only when reconciliation actually performs the CAS import/revalidation
phase. An unchanged stable tree-v2 workspace keeps all five counters at zero, preserving ADR 0342's
no-op skip signal. Counts and byte totals reveal shape and cost class only; they never expose paths,
object digests, filenames, writers, or content.

## Consequences

The ordinary `sync-publish` line can now distinguish:

- no-op source-watch wakeups that reused source digests and skipped CAS work;
- changed local files that installed new immutable objects;
- changed local files whose content was already present in CAS; and
- sparse projection bottlenecks where CAS was cheap but preservation/projection was not.

This does not add a durable CAS index, does not trust stale object inventories, and does not change
the final full-store revalidation rule before signed metadata or visible projection effects are
accepted. It is observability for the next optimization gate, not an authorization shortcut.

## Evidence

The owned unit/integration registry now verifies that initial tree-v2 reconciliation reports one
installed CAS object for a one-file workspace, while subsequent unchanged stable reconciliations
report zero CAS inspection, installation, and reuse after ADR 0342's no-op skip.

Accepted local check:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_tests && ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
```
