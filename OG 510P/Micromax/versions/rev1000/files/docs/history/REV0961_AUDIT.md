# Revision 0961 focused audit

## Selected risk

The selected risk was restricted plugin execution because rev0960 named it as
the next trust gap and the existing implementation still separated package
verification from later file evaluation. A second audit followed the worker and
revocation edges rather than adding another policy registry.

## Severe findings corrected

1. **Check/use split.** A grant fingerprinted live files, then startup or lazy
   include reopened paths later. Concurrent change could make checked bytes and
   executed bytes differ.
2. **Callback resource amplification.** Restricted callbacks could trigger whole
   package work even when they used only already-evaluated words.
3. **Queue-order deadlock.** A snapshot worker can return several MiB through
   `multiprocessing.Queue`; joining before draining can deadlock while the child
   feeder waits for pipe capacity.
4. **Revoke that only changed a label.** A grant could be marked revoked while
   already registered commands, timers, hooks, bindings, and wordlists remained
   live until a separate unload.
5. **Approval/activation blur.** Reapproving changed bytes could partially deny
   lazy source for the still-committed generation before reload.
6. **Symlink reclassification escape.** After capture, replacing an approved
   lexical member with an outside-pointing symlink could make the source reader
   classify it as non-package-local and fall back to live bytes. A regression
   first demonstrated execution of the unapproved target; package membership is
   now classified against the frozen lexical snapshot instead of live resolution.
7. **Stale grant replay.** An embedder retaining an immutable grant object could
   replay it after revoke or supersession. Restricted load/reload now require the
   presented issuance token and authority fields to match the manager's current
   live grant before capture or evaluation.
8. **Broken worker-pipe cleanup.** A receive failure could leave a started child
   and queue resources behind. All start/get/join error paths now terminate the
   child when needed and close the queue before surfacing the error.
9. **Zero-coordinate collapse.** Flattened screen models used `value or -1` for
   cursor coordinates, so a valid cursor at `(0, 0)` became absent. A shared
   integer-coercion seam now preserves zero across viewport/display/screen rows
   and the curses renderer instead of encoding coordinate presence as truthiness.

## Corrected invariants

1. Metadata-only discovery is not code evaluation.
2. Approval names one bounded immutable package byte snapshot.
3. Metadata validation, entry selection, source evaluation, lifecycle source,
   and package-local deferred reads use that same snapshot.
4. Live filesystem drift, including post-approval symlink retargeting, cannot
   reclassify a captured member or retarget a committed generation.
5. Revoked or superseded grant issuance cannot be replayed by a retained object.
6. Replacement approval does not mutate or disable the committed generation;
   reload is the explicit activation transition.
7. Ordinary callbacks perform no plugin package filesystem or worker work.
8. Revocation removes managed runtime without asking the plugin to run more code.
9. Cleanup failure leaves runtime and grant unchanged rather than reporting a
   false revoke.
10. Retired plugin object identity cannot regain current-generation authority.
11. Worker result payloads are consumed before process join and remain bounded by
    file, byte, retention, and wall-clock limits.
12. Screen coordinates are numeric data: zero remains a valid cursor, row, and
    column value throughout flattened models and terminal placement.

## Refactors

- `plugin_package.py` owns package capture and immutable source access.
- `plugin_meta.py` owns pure metadata parsing plus the small disk-backed adapter.
- `plugins.py` owns approval, generation commit, reload, grant identity, and
  transactional host cleanup.
- `vm_load_policy.py` serves package-local source from the active snapshot at the
  existing source-read boundary and classifies containment lexically, without
  following a namespace that can change after approval.
- `editor.py` owns user-visible approval/reload/unload/revoke transitions and
  now uses one zero-preserving model-coordinate coercion seam.
- `tui.py` applies the same zero-preserving rule when consuming screen positions.

## Cloudtainer waste removed

The callback path no longer launches package fingerprint workers or repeatedly
walks plugin trees. The large-result regression test also protects the session
from hidden worker accumulation caused by join-before-drain hangs. Final archive
cleanup removes caches, build products, and transient test logs rather than
shipping session residue.

## Severe cloudtainer correction

Three parentless pytest processes from abandoned rev0960 worktrees were still
consuming substantial CPU while this revision was being validated. Removing
those exact old-tree processes cut a representative callback rollback test from
the cloud command ceiling to about six seconds. The repository already had
process-group cleanup in `tools/mxtest.py`; the waste came from the ordinary
`make test` path bypassing it. `scripts/test.sh` now delegates to that runner so
an outer timeout or interruption tears down the active pytest process group
instead of abandoning descendants. No normal-exit descendant-reaping claim is
made.

## Residual risk

- Package capture is a bounded multi-file observation, not an atomic directory
  snapshot against a hostile concurrent local mutator.
- Plugin code is in-process and can consume CPU/memory or exploit allowed host
  effects; no Python/native sandbox is claimed.
- Host-owned cleanup covers registered/owned Micromax editor surfaces, not
  arbitrary external side effects already performed by plugin code.
- Session grants are neither durable per-plugin policy nor signed publisher or
  supply-chain identity.
- Dependencies and plugin-to-plugin revocation policy remain deliberately small;
  loaded dependents can block non-force cleanup rather than being silently torn
  down.
- The audit rejected an unrelated fork-first worker optimization: Python's
  documented multithreaded-process hazards outweigh a small startup win, so the
  existing forkserver/spawn-first policy remains intact for importable workers.

See `docs/917-immutable-plugin-package-revoke-queue-drain.md` for the product
journey, research, implementation map, and next priorities.
