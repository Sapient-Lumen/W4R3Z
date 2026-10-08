# Immutable plugin packages, decisive revoke, and queue-drain ordering (rev0961)

## Why this was the right risk

Rev0960 made save/restart recovery real and named the restricted-plugin journey
as the next trust gap. The important unfinished question was not another
capability label. It was whether the bytes a user approved were the bytes the
editor actually executed, and whether “revoke” removed executable state.

The product promise is now:

> unfamiliar workspaces may expose inert plugin metadata; an interactive user
> approves one exact bounded package generation; that generation stays stable
> until an explicit replacement commit; revocation removes managed runtime
> without executing more plugin code.

## The old failure shape

The previous path computed an aggregate package digest and later reopened the
entry or helper source. That left a check-to-use interval. It also made deferred
callbacks pay for package verification even when no new source was consumed.

The first snapshot draft still had a subtler escape. Its source reader resolved
an approved lexical path through the *current* filesystem before deciding
whether the path was package-local. Replacing `helper.mx` with an outside-pointing
symlink after approval therefore made the reader classify the path as external
and fall back to live bytes. A regression test was deliberately written before
the repair and executed the unapproved target. Snapshot containment now uses
frozen lexical membership and never consults post-approval symlink targets.

A retained immutable grant object also remained replayable after the manager had
revoked or superseded it. That was not a byte-integrity failure, but it was an
authority-lifetime failure. The presented issuance token and authority-bearing
fields must now match the manager's current live grant before disk capture,
reload, or evaluation begins.

The worker implementation had a separate availability hazard. A package snapshot
can be several MiB. Python documents that joining a process which has put a large
item on a `multiprocessing.Queue` before consuming the item can deadlock: the
child may wait for its feeder thread to flush while the parent waits for child
exit. The safe order is receive, then join.

Finally, a grant-only revoke was semantically weak. Already registered commands,
actions, bindings, hooks, timers, delayed rows, and wordlists could remain live,
so the UI could say “revoked” while executable authority survived.

## Landed product journey

1. `--trust restricted` calls `PluginManager.scan_tree()`. It reads contained
   metadata only and evaluates no plugin source.
2. Interactive `plugin load NAME` captures one package snapshot under file-count,
   total-byte, retained-byte, and worker-time budgets.
3. `plugin.json` parsing and entry resolution operate on the captured bytes.
4. Initial source, lifecycle words, and package-local `include`/`require` read
   from the same immutable snapshot. A later symlink retarget cannot make an
   approved lexical member fall through to live filesystem bytes.
5. The committed `Plugin` record retains generation, root, digest, file count,
   and the snapshot object. Registration inspection still shows plugin group and
   source span.
6. Later disk edits cannot alter that generation. A callback either uses already
   evaluated words or reads the old snapshot; it performs no live walk, hash, or
   worker launch.
7. Running `plugin load NAME` for a changed loaded package creates a pending
   replacement approval. The live generation remains fully functional and keeps
   its own bytes.
8. `plugin reload NAME` first rejects revoked or superseded grant issuance,
   verifies that live files still match the pending approval, and then
   stages/commits the retained snapshot. A later race cannot substitute unchecked
   bytes; at worst the committed approved snapshot differs from files that
   changed after verification and explicit inventory reports that drift.
9. `plugin unload NAME` is graceful and may run the committed generation's
   `deinit` from its snapshot.
10. `plugin revoke NAME` is the authority-withdrawal lane. It skips `deinit`,
    transactionally removes host-managed state, then marks the grant revoked. If
    cleanup fails, the plugin and grant remain live and the failure is visible.

The headless journey in `tests/test_restricted_plugin_journey.py` exercises
metadata inspection, absent command, approval, visible origin, callback use,
disk drift, stale reload, replacement approval, old-generation continuity,
reload commit, changed behavior, revoke, cleanup, and command disappearance.

## Implementation map

- `plugin_package.py` — immutable `PluginPackageSnapshot`, bounded membership and
  bytes, digest, source resolution, direct/worker capture.
- `plugin_meta.py` — pure `parse_plugin_meta()` plus disk-backed adapter.
- `plugins.py` — grants, pending approvals, loaded generation identity,
  retention budget, load/reload/unload, and worker result ordering.
- `vm_load_policy.py` — package-local source resolution/read from the active
  snapshot at the normal VM source boundary.
- `editor.py` and `plugin_commands.py` — user-visible command transitions and
  prompt-safe versus explicit live grant inventory.
- `editor.py` and `tui.py` — zero-preserving coordinate coercion across flattened
  headless screen rows and curses placement.

## Audit/refactor findings

### 1. Approval and activation are different states

A pending replacement must not retarget a callback, but it also must not break
the old generation. The live plugin record is the committed byte authority; the
manager's latest approved snapshot is the future reload authority. Revocation is
separate and decisive.

### 2. Identity and issuance are part of authority

A retired `Plugin` object can remain reachable in a stale callback or embedder.
Name, root, and digest equality are insufficient. Package authorization accepts
only the exact object currently advertised in `PluginManager.plugins`.

Likewise, an immutable `PluginLoadGrant` can be retained after revoke or
replacement. Restricted load/reload accepts it only when its session issuance
token and authority-bearing fields still match the manager's current grant. The
check happens before snapshot capture, so stale authority cannot even cause a
new package walk.

### 3. Prompt paths must not walk package trees

Grant completion and ordinary status rows use the in-memory grant/snapshot view.
Only explicit `plugin grants`, new approval, and reload freshness checks inspect
live package files.

### 4. Large worker results reverse the usual join order

`_collect_plugin_worker_result()` starts the worker, drains its bounded queue
result, then joins. Timeout, broken receive, malformed/no-result, start, and join
failure paths close the queue and terminate a started live child when needed. A
multi-megabyte regression protects receive-before-join; a fake broken-pipe
regression protects teardown when no usable result arrives.

### 5. Snapshot containment is lexical, not live-resolved

Once bytes are captured, the relevant question is whether a requested lexical
name belongs to the snapshot—not where the current filesystem would resolve
that name. `PluginPackageSnapshot.relative_name()` normalizes `.` and `..`
without following symlinks. Membership and reads are then answered only from the
frozen `(relative-name, bytes)` rows. Missing names fail closed.

### 6. One owner extraction deleted duplication

Package walk/digest/read logic moved out of the 1,500-line plugin manager into
`plugin_package.py`. Metadata parsing no longer requires disk I/O. This is the
kind of refactor the cube needs: one coherent owner that removes a race and
repetition, not a new abstract lifecycle registry.

### 7. Secondary screen audit found a truthiness boundary bug

The plugin work touched flattened editor evidence, so the adjacent screen-model
boundary was audited rather than left implicit. Several conversions used
`int(value or -1)`. That idiom is valid for optional text but wrong for numeric
coordinates: row or column zero is real data, not absence. A cursor at `(0, 0)`
therefore disappeared from flattened rows and could make the curses consumer use
fallback window coordinates.

One small `_model_int()` seam in each ownership layer now distinguishes
conversion failure from numeric zero. Headless and curses regressions exercise
the actual model/renderer boundary. This is intentionally not a new screen
registry or schema version; it repairs the existing contract at its consumers.

## Research applied

- Python 3.14.6 `multiprocessing` guidance warns that a process which puts a
  large queue item can deadlock when joined before the item is consumed; its
  corrected example receives before joining. The same documentation warns that
  safely forking a multithreaded process is problematic, supporting retention of
  the project's forkserver/spawn-first policy for importable workers (accessed
  2026-07-17):
  https://docs.python.org/3/library/multiprocessing.html
- MITRE CWE-367 frames time-of-check/time-of-use as checking a resource and then
  using a potentially different state. The relevant mitigation is to ensure the
  checked resource is the one used; its related link-following cases also match
  the post-approval symlink reclassification failure found here (accessed
  2026-07-17):
  https://cwe.mitre.org/data/definitions/367.html
- The Update Framework's target metadata binds names to hashes and lengths, and
  its consistent-snapshot model reinforces unique content addressing. Micromax
  is not implementing TUF here, but the same narrow lesson applies: approval
  should identify immutable content, not a mutable pathname:
  https://theupdateframework.github.io/specification/latest/ (accessed 2026-07-17)
- VS Code's Workspace Trust guidance distinguishes restricted mode from merely
  hiding UI: commands can still be invoked by other means, so unsafe execution
  must be blocked or not registered. Micromax therefore keeps restricted startup
  metadata-only and tests command absence before approval:
  https://code.visualstudio.com/api/extension-guides/workspace-trust (accessed 2026-07-17)
- Python `importlib.metadata` demonstrates the useful architectural separation
  between inspecting distribution metadata and importing/executing modules:
  https://docs.python.org/3/library/importlib.metadata.html (accessed 2026-07-17)

## Honest limits and speculation

The package walker reads files one by one. A hostile process can mutate the tree
during capture and produce a snapshot assembled from different moments. The
important closed gap is that the grant names exactly that assembled byte set and
all later evaluation uses it. Stronger atomic package acquisition would require a
versioned/published artifact, filesystem snapshot, signed manifest, or separate
installation pipeline—not more callback checks.

A process/Wasm extension host may eventually be valuable, but only after the
extension interface is smaller and classified. Moving today's broad internal
Python surface out of process would fossilize too much accidental API. Near-term
work should instead finish crash/restart filesystem evidence, stabilize compact
screen consumers, and derive release artifacts from one declared source
snapshot.

## Next priorities

1. Subprocess fault points and a declared local-filesystem recovery matrix.
2. Real `micromax.screen.v1` consumers, compatibility/golden budgets, and one
   restrained highlight hierarchy.
3. Reproducible wheel/archive/CI provenance from a single source snapshot.
4. Extension-surface classification before isolation.
