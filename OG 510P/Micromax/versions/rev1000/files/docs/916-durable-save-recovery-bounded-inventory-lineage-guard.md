# Durable save recovery, bounded inventory, and lineage guard (rev0960)

## Executive judgment

The heart of Micromax is unchanged: build a calm editor in which end-user
configuration, macros, and plugins are powerful because effects are explicit,
attributable, finite, and recoverable—not because the host quietly grants broad
authority. Trust still comes before taste and flow.

The riskiest unfinished trust path was the boundary between a live edit, a failed
save, process restart, and the next safe user decision. Rev0959 added a useful
standalone journal engine, but the ordinary editor save path did not call it.
That made the evidence stronger than the product. Rev0960 turns that mechanism
into a complete headless product journey and corrects adjacent durability,
authority, startup, worker, and release-lineage defects.

## What had gone severely wrong or become wasteful

### 1. Recovery existed beside the product rather than in it

The rev0959 journal could checkpoint, classify, restore, and dismiss records in
isolation. A normal `save`, however, did not create those records. A user could
still lose the only in-memory copy after a write failure and restart. This was
the largest gap because the roadmap and evidence vocabulary suggested a recovery
capability that the daily path did not yet possess.

### 2. Journal retirement could outrun durable document commit

The standalone path treated writer return as sufficient to remove the recovery
record. That is weaker than the intended crash model: a write or atomic rename
can return before data and directory metadata are forced to stable storage. The
correct order is now checkpoint durability, document write, document/rename
flush, exact-byte verification, then journal retirement. A leftover record means
“classify this interrupted transaction,” not “blindly replay it.”

### 3. A naïve integration would have broken symlink-preserving saves

The editor already preserves the authority of a symlink's concrete target while
leaving the link in place. The journal initially reasoned only about a canonical
path. Wiring it in directly would have made recovery and normal save disagree
about which object was authoritative. Rev0960 checkpoints the concrete write
authority, records the requested nominal path as metadata, and keeps a recovered
buffer bound to the original target even if the nominal symlink is later
retargeted.

### 4. Startup recovery discovery was an availability hazard

Full discovery decoded records and fingerprinted document targets. Applied at
startup, an oversized or adversarial state directory could cause thousands of
reads and hashes before the user reached a buffer. Startup now performs only a
bounded filename count. The explicit `recoveries` command performs validation
under separate limits for directory entries, selected records, decoded record
bytes, and aggregate target-comparison bytes, and reports omissions instead of
pretending the inventory is complete.

### 5. Failed save-as attempts could survive after later success

A failed save-as created a valid checkpoint keyed to the abandoned path. A later
successful save elsewhere retired only its own row, leaving the old row to be
shown on a future restart. Durable success now retires every valid journal row
owned by that buffer through a target-free cleanup lane. Cleanup failure is a
warning, not a false claim that the already-durable document save failed.

### 6. The cloudtainer itself was producing mixed-generation work

Long-lived orphaned tests and refactor processes from prior worktrees were still
using CPU and writing source while this revision was being assembled. That is a
concrete lineage failure, not just an inconvenience: a recursive zip over a live
mutating tree can combine files from incompatible generations. The active tree
was moved to an isolated snapshot, stale processes were terminated, and
`mkrevzip` now rejects symlink/non-regular members, fingerprints source bytes,
copies verified bytes into a private build snapshot, packages only that
snapshot, verifies the archive, and aborts when live membership or bytes change
at any checked phase.

### 7. Fork-first timeout workers were unsafe in the editor process

Several bounded filesystem and regex operations selected `fork` even though the
TUI can be multithreaded. Forking a multithreaded Python process can inherit
locks without their owning threads. A shared per-operation worker-context policy
now prefers `forkserver`, then `spawn`, and permits `fork` only for a
single-threaded non-importable shell entrypoint where spawn-style reconstruction
cannot work. The compatibility re-export prevents another duplicate policy.

### 8. The diagnostic screen graph was being mistaken for product truth

The full headless screen model is valuable for diagnosis but is very large and
sparse. Rev0960 adds `micromax.screen.v1`: visible rows, one cursor, source
coordinates, and non-empty cues under a packaged JSON Schema. The CLI defaults
`--dump-screen` to this compact contract; the large graph remains available only
through explicit diagnostic expansion. This is a product/API reduction, not a
new registry.

## Landed behavior

- Explicit dirty, forced, missing-target, recovered, and save-as writes create a
  private durable checkpoint before document commit.
- Recovery payload bytes preserve exact pre-normalization editor text, including
  surrogate code points; separately fingerprinted commit bytes represent
  encoding, line-ending, trailing-space, and EOF-newline normalization.
- An active checkpoint forces file and atomic-rename durability before it can be
  retired. Writer authority and exact committed bytes are verified.
- `recoveries`, `recover [#N|ID]`, and `recoverdismiss [#N|ID]` are interactive
  only. Recovery opens a dirty buffer and never overwrites disk automatically.
- Changed or unreadable targets require review plus `save!` at the same authority
  or an explicit `saveas FILE`; recovery buffers are excluded from autosave.
- Recovery records, roots, and target fingerprint reads use bounded no-follow
  file-descriptor paths where available. A root replaced by a symlink is
  rejected.
- Clean saves of an existing unchanged file avoid journal churn and an extra
  forced synchronization.
- Successful saves retire stale checkpoints for the same buffer without
  rehashing document targets.
- Worker process selection is shared and avoids multithreaded fork by default.
- The compact screen contract has a version, schema resource, deterministic
  projection, explicit diagnostic fallback, and focused tests.
- Revision packaging uses verified source bytes and refuses mixed-generation or
  symlink-bearing trees.

## Research anchors and design implications

The implementation follows primary or project-authoritative sources rather than
inventing a recovery protocol from names alone:

- SQLite atomic commit describes the rollback-journal ordering that matters here:
  make recovery material durable before changing authoritative content, flush
  the committed content, and treat journal deletion as the commit boundary.
  https://www.sqlite.org/atomiccommit.html
- Linux `fsync(2)` notes that synchronizing a file does not necessarily
  synchronize the directory entry containing it; the parent directory requires
  a separate flush for rename/create durability.
  https://man7.org/linux/man-pages/man2/fsync.2.html
- Linux `open(2)` documents `O_NOFOLLOW`; opening first and validating with
  `fstat` narrows the check-then-open symlink race compared with `lstat` followed
  by a path-based read.
  https://man7.org/linux/man-pages/man2/open.2.html
- The XDG Base Directory specification defines `XDG_STATE_HOME` for persistent
  application state that is not portable configuration or shareable data. A
  relative value is ignored rather than treated as ambient authority.
  https://specifications.freedesktop.org/basedir-spec/latest/
- GNU Emacs recovery loads auto-save data into a buffer for inspection and an
  explicit later save; it does not silently overwrite the visited file.
  https://www.gnu.org/software/emacs/manual/html_node/emacs/Recover.html
- Vim's recovery documentation likewise treats swap recovery as an inspection
  and reconciliation workflow.
  https://github.com/vim/vim/blob/master/runtime/doc/recover.txt
- Python's multiprocessing documentation states that safely forking a
  multithreaded process is problematic and, from Python 3.14, uses `forkserver`
  as the POSIX default where available.
  https://docs.python.org/3/library/multiprocessing.html

These sources support the direction; they do not prove power-loss behavior on
every filesystem, mount mode, kernel, storage cache, or operating system.

## Speculation worth testing

1. **Recovery is the best first typed resource owner.** It already has stable
   identity, origin, target authority, lifetime, cleanup, rollback scope, and
   byte budgets. A small shared retained-resource seam may emerge from this
   concrete shape, but it should be generalized only after a second resource
   family becomes smaller.
2. **Crash testing should become a release lane.** Run saves in a subprocess,
   terminate at named fault points, restart from the same state root, and assert
   journal/document classification. Add a small real-filesystem matrix before
   making broad durability claims.
3. **The screen contract should stay projection-only.** Let renderers and test
   consumers adopt `micromax.screen.v1`; do not make editor semantics depend on
   serialization or inflate v1 to mirror the diagnostic graph.
4. **Extension isolation comes after interface reduction.** The safer worker
   policy removes one immediate fork hazard, but plugins remain in-process.
   Process or WebAssembly isolation becomes tractable only after stable hostcall,
   lifecycle, and screen surfaces are deliberately smaller.
5. **Release inputs should become content-addressed earlier.** The snapshot guard
   prevents a mixed archive in this tool. A future build lane could materialize
   a declared source tree once, then derive wheel, archive, tests, and provenance
   from the same digest rather than repeatedly walking a live checkout.

## Highest remaining risks

1. Complete the restricted-plugin product journey: scan, denial, visible origin,
   grant, reload, revocation, and cleanup. This is now the highest unfinished
   trust promise.
2. Add subprocess crash/fault-injection journeys and a supported-filesystem
   durability matrix. Current tests simulate failures and verify ordering, but
   do not simulate sudden power loss.
3. Pin compatibility consumers and golden-size budgets for
   `micromax.screen.v1`, then define one restrained highlight precedence.
4. Add current CI, reproducible wheel construction, and a compact provenance
   statement before public release claims.
5. Audit the remaining recovery quarantine/delete path races and remote/special
   filesystem behavior. The core reads fail closed, but no path API can erase
   every concurrent namespace race without stronger OS primitives.
6. Prove—not merely name—one typed retained-resource owner seam that removes
   duplicated lifecycle code.

Focused evidence is recorded in `REV0960_TESTS.md`. No full-suite or universal
power-loss guarantee is claimed.
