# IoTox everyday synchronization

Status: one-writer mirrors and bounded tree-v2 read-write synchronization are implemented. The
unattended one-writer UDP/TCP restart gate, dedicated two-Sandwurm-guest writable pair gate, and real
three-daemon full-mesh gate pass.
Checkpoint floors, explicit pins, recoverable GC quarantine/restore, exact local writer cutoffs,
recipient-local selection rules, exact private owner-mode metadata, and a bounded Linux source-watch
wake path are implemented. The finite adversarial/scale matrix and a two-hour networkless
IoTox/Resilio shadow now pass. This closes the founding-machine synchronization roadmap; it does not
turn synchronization into versioned recovery custody.
Updated 2026-09-25.

ADR 0284 and `sync-trust-graduation.md` own the separate question of when a specific dataset may be
promoted from experimentation to an important working set. Founding-roadmap completion is not that
promotion.

## What IoTox can synchronize

IoTox now has two deliberately different synchronization products.

The established one-writer path publishes immutable signed revisions. A regular file uses
`content-v2`; a directory uses `treepack-v1`. Authorized followers pull, verify, and optionally
activate those revisions. This remains the right shape for software distribution and read-only
replicas. Retained immutable revisions can contribute to a backup policy, but synchronization alone
is not a backup.

The new read-write path uses `tree-v2`: per-file SHA-256 CAS objects, one signed monotonic branch per
stable device, causal observations, signed tombstones, and a deterministic writable projection. It
does not use receipt time or wall-clock last-writer-wins. Unequal concurrent changes remain visible
as conflicts until a later ordinary edit causally observes and resolves them.

## Start a pairwise read-write sync

Both devices choose their own local path. Neither peer can select a path on the other machine. The
peers must already have a confirmed IoTox application session with authority-v3 and tree-v2 feature
negotiation.

On device A:

```bash
iotox sync-create field-notes /srv/field-notes read-write 30
cat A_RECALLROOT.txt | \
  iotox sync-share field-notes B read-write
```

On device B:

```bash
iotox sync-create field-notes /srv/field-notes read-write 30
cat B_RECALLROOT.txt | \
  iotox sync-share field-notes A read-write
```

`30` is the periodic reconciliation interval in seconds and defaults to 30. `A` and `B` may be a
friend number, exact public key, or whatever unambiguous selector the ordinary friend resolver
accepts. `sync-create` requires an existing absolute private directory. Source and managed state
roots may not contain one another.

For a selected subtree with exact private owner read/write/execute bits, put the interval before the
versioned projection policy:

```bash
iotox sync-create field-notes /srv/field-notes read-write 30 owner-mode-v2 \
  include=documents include=scripts exclude=documents/cache
```

Rules are canonical relative component-prefixes, not shell globs. Empty includes mean the whole
ordinary tree; exclude always wins. Each device owns its own selection policy and may select a
different subset. A newly excluded local path is preserved during atomic projection, and an already
known hidden signed entry remains in causal history rather than becoming a deletion. The default
`executable-v1` mode retains the historical `0600`/`0700` behavior. `owner-mode-v2` preserves exactly
`0400`, `0500`, `0600`, or `0700` for regular files. It does not add symlinks, ACLs, xattrs,
timestamps, ownership translation, special files, or remote-selected paths.

ADR 0295 makes those rules control file-object custody as well as projection. Inspect or replace the
local rules after creation with `sync-interest`; use `sync-interest-clear` for complete intent, then
`sync-pull PEER NAMESPACE` for immediate on-demand backfill. Signed metadata remains complete, while
status/repair/GC report selected and skipped objects explicitly. ADR 0296 adds complementary
primary-lane sources through authenticated exact-object probes and `sync-pull-multi`. ADR 0297 adds
durable signed `sync-health` without treating partial custody as corruption or backup. See
`sync-sparse-custody.md` and `sync-health.md`.

The two `sync-share` commands are intentionally reciprocal. Each reconstructs that device's active
owner from RecallRoot, binds the live friend selector to the transcript-proven stable device
principal, grants that principal both `sync.subscribe` and `sync.publish`, adds it to the namespace's
subscriber and writer sets, and changes local automation from `writable` to `bidirectional` bound to
that exact principal. Exact retries are idempotent. Sharing with another authorized writer adds its
principal to the canonical set; it does not replace or renumber an existing source.
The examples use `A_RECALLROOT.txt`, `B_RECALLROOT.txt`, and `RECALLROOT.txt`
only as ceremony placeholders. The command reads RecallRoot from standard
input; do not pass the phrase as an argument or environment variable, and
protect or destroy any temporary local file used to feed stdin.

The peers may start with different content. Their initial branches then converge as concurrent
history rather than silently choosing the peer that connected last.

## Start a three-node read-write sync

Create the same namespace independently on A, B, and C, with any local absolute path each owner
chooses:

```bash
# A
iotox sync-create field-notes /srv/field-notes read-write 30
cat A_RECALLROOT.txt | iotox sync-share field-notes B read-write
cat A_RECALLROOT.txt | iotox sync-share field-notes C read-write

# B
iotox sync-create field-notes /srv/field-notes read-write 30
cat B_RECALLROOT.txt | iotox sync-share field-notes A read-write
cat B_RECALLROOT.txt | iotox sync-share field-notes C read-write

# C
iotox sync-create field-notes /srv/field-notes read-write 30
cat C_RECALLROOT.txt | iotox sync-share field-notes A read-write
cat C_RECALLROOT.txt | iotox sync-share field-notes B read-write
```

That is a full mesh: three friendship edges and six directional owner grants. Each node stores the
other two exact stable principals and recognizes all three signed writer branches. The ordinary
construction is bounded to 16 writers total (the local writer plus at most 15 automatic remote
sources). A partial mesh is not the documented setup ceremony because a node must authorize every
writer whose branch it may receive.

If all three nodes edit the same path while mutually offline, all three signed branches survive. The
canonical ordinary path is deterministic and two alternatives appear under `.iotox-conflicts` on
every node. Wait until all three frontiers and alternatives are visible before making the ordinary
edit that resolves the conflict; editing independently on multiple nodes creates a new concurrent
conflict, as it should.

## Start a one-writer sync

Create an authoritative file or directory publication:

```bash
iotox sync-create release-mirror /srv/release-mirror 30
```

Grant a current peer read-only access:

```bash
cat RECALLROOT.txt | \
  iotox sync-share release-mirror READER read-only
```

The recipient still chooses its local root, installs its reviewed namespace policy, grants the
writer `sync.publish`, and selects `pull` or `verified` activation through the expert commands. ADR
0293's signed peer invitation can establish transport friendship and an alias, but deliberately does
not install any of this synchronization state. A future sync-specific review plan may shorten setup,
but must not let a sender choose a remote filesystem path or activation policy.

## Inspect and control it

```text
iotox sync-status
iotox sync folder-status NAMESPACE PATH read-write 30
iotox sync-namespaces
iotox sync-automation
iotox sync-publish NAMESPACE
iotox sync-pull FRIEND NAMESPACE
iotox sync-repair NAMESPACE
iotox sync-checkpoint NAMESPACE
iotox sync-retention NAMESPACE
iotox sync-gc NAMESPACE dry-run|quarantine
iotox sync-restore NAMESPACE
iotox sync-history NAMESPACE [LIMIT]
iotox sync-diff NAMESPACE FROM_RECORD_HEX TO_RECORD_HEX
iotox sync-conflicts NAMESPACE [RECORD_HEX]
iotox sync-conflicts-summary NAMESPACE [RECORD_HEX]
iotox sync-conflict-explain NAMESPACE PATH [RECORD_HEX]
iotox sync freeze NAMESPACE --reason REASON
iotox sync unfreeze NAMESPACE --reason REASON
iotox sync safe-delete NAMESPACE TARGET --quarantine-root DIR [--reason LABEL]
iotox sync-restore-plan NAMESPACE RECORD_HEX
iotox sync-restore-forward NAMESPACE RECORD_HEX PLAN_ID_HEX
iotox sync-automation-remove NAMESPACE
```

`sync-status` exposes content-free aggregate publisher, receiver, and automation counters. Tree-v2
pull rows identify state, object counts, bytes, accepted branches, and conflict counts without
publishing paths or content. ADR 0356 adds `reconcile-` prefixed source, CAS, projection, conflict,
and preservation counters to retained tree-v2 pull rows so final local apply cost is visible beside
transfer cost. `sync-repair` first authenticates current
branch pointers, immutable records/manifests, signed workspace, and signed
maintenance state, then revalidates every unique referenced CAS object. It
does not repair or overwrite corrupt signed metadata. `sync-publish` on a tree-v2 namespace performs a local writable reconciliation; a
tree-v2 `sync-pull` first does the same, ensuring an offline local edit is committed against the
frontier the user actually saw before remote branches are accepted.

The expert one-writer automation surface remains:

```text
iotox sync-auto-publish NAMESPACE PATH [INTERVAL_SECONDS]
iotox sync-follow FRIEND NAMESPACE pull|verified [INTERVAL_SECONDS]
iotox sync-automation
iotox sync-automation-remove NAMESPACE
```

Removing automation writes a higher-generation disabled record. Absence is not revocation truth.

`sync folder-status` is the daily dashboard for one folder. It composes the
source doctor, local freeze record, live Agent status when reachable, conflict
commands, precious-data status command, and safe-delete command without
printing content. `sync freeze` writes a local operator brake. Native sync
mutator CLIs now refuse namespaces frozen in the default runtime freeze state,
including publish, activate, follow, pin/unpin, writer cutoff, repair,
interest changes, checkpoint, restore-forward, quarantine GC, namespace
removal, and safe-delete. The brake does not stop already-running Agent jobs
or remote peers by itself.

If repair or startup reports a signed metadata family as corrupt, stop the
namespace and preserve the corrupt image. Restore only reviewed byte-exact
metadata from a known external generation, then rerun startup and
`sync-repair`. Do not expect another peer to overwrite the record
automatically: that could hide rollback or erase the only retained frontier,
pin, or writer cutoff. ADR 0337 proves one exact-restoration laboratory
ceremony; it does not authenticate backup selection or provenance.

## Conflict and deletion semantics

For one path with unequal concurrent candidates, IoTox chooses one canonical ordinary projection so
every peer presents the same pathname. Every unselected live value, directory marker, or tombstone
is retained beneath:

```text
.iotox-conflicts/by-origin/WRITER/GENERATION/KIND/PATH
```

The canonical choice is a display rule, not data loss and not a claim that one writer was newer. A
normal edit made after both branches are visible creates a new local event that observes both and
therefore resolves the conflict causally. The conflict directory is regenerated from signed state;
editing it is not a resolution API.

For a smaller human view, use:

```sh
iotox sync-conflicts-summary field-notes
iotox sync-conflict-explain field-notes documents/today.md
```

The summary lists visible conflict paths and candidate counts. The explainer
shows the writer generations and object classes for one ordinary path, then
repeats the safe resolution rule: wait until the alternatives are visible, pick
the desired content in the normal worktree, and make one ordinary later edit.
These commands are read-only porches over `sync-conflicts`; they do not edit
`.iotox-conflicts` and do not invent a merge policy.

Deleting a normal path creates a signed tombstone. A causally later deletion removes the path on the
other peer. A deletion concurrent with a live edit preserves both outcomes: the ordinary projection
prefers the live entry while the tombstone remains in conflict provenance. There is no
delete-everywhere or permanent-purge command. Retention pins exact branch records and recoverable GC
archives only objects outside every authenticated live closure; neither changes logical deletion
semantics.

For a human-reviewed local delete before any publish, use:

```sh
iotox sync safe-delete field-notes /srv/field-notes/obsolete.txt \
  --quarantine-root /srv/.iotox-delete-quarantine \
  --reason reviewed-delete
```

This is a recoverable local move into a namespace-labeled quarantine plus a
receipt. It does not author a signed sync tombstone by itself; after review,
the next normal reconciliation/publish observes the path absence as the local
writer's deliberate state.

## Durable ordering and recovery

The receiver walks a bounded authenticated graph. It fetches exact signed branch records and their
predecessor/observation closure, then manifests, then missing file objects. File content commits to
CAS before branch metadata; complete verified branch proofs commit before writer-current pointers;
workspace reconciliation is the last effect. A same-writer fork, gap, stale substitution, invented
observation, unauthorized writer, conflicting signed size, over-quota graph, changed authority
epoch, or malformed transfer binding fails the pull closed.

`IOTXTWS1` signs the exact frontier represented by the current writable directory. This distinction
keeps a received-but-not-yet-visible branch from becoming a false parent of a local offline edit.
Projection is prepared beside the worktree, journaled, and switched with same-parent
`renameat2(RENAME_EXCHANGE)`. Startup revalidates markers and signed pending state before choosing
an orientation. Canonically named crash-left receive parts are removed at the next serialized pull;
unrelated entries are not treated as garbage.

The durable automation record stores a canonical set of stable remote principals, never process-local
friend numbers. After restart it reselects only current sessions whose transcript and exact authority
proof match those principals. One serialized lane protects each writable namespace, while a fair
round-robin scheduler and independent per-peer retry clocks prevent an unavailable writer from
delaying healthy writers. The first reconciliation is immediate; later attempts use the configured
interval and bounded backoff. Work remains off the Agent service thread.

On Linux, automation also installs a best-effort source-tree watcher for local `publish`,
`writable`, and `bidirectional` policies. A source event wakes the existing automation lane on the
next service cycle through a 250 ms non-sliding debounce. A write burst therefore coalesces into one
near-term publish instead of postponing indefinitely or emitting one publish per event. For
bidirectional namespaces, that wake creates a local publish/reconcile action; remote writer pulls
remain separate round-robin work. Unsupported or exhausted watchers, deleted roots, and dropped
events fall back to the interval scan, so correctness still comes from signed state and periodic
reconciliation rather than from inotify.

For tree-v2, source changes observed during an active local publish now cool down for 5 seconds
after that publish completes before the next local republish. That prevents large write bursts from
creating too many intermediate signed heads while a directory is still being populated. It does not
slow remote peer pulls in bidirectional automation, and it is not part of the signed automation
record.

ADR 0344 adds a volatile source digest cache to reduce the cost of those repeated reconciles. The
Agent reuses a file digest only when a private cache entry from an earlier verified scan matches the
same namespace, source, projection policy, path, inode/device, mode, owner, link count, size, mtime,
and ctime. Whole projection exchange clears the cache because visible files may have new identities.
`sync-publish` reports `source-inspected=`, `source-hashed=`, and `source-reused=` so operators can
see whether the local walk is pruning entries and whether it is still reading file contents. ADR
0354 extends the same line with `cas-inspected=`, `cas-inspected-bytes=`, `cas-installed=`,
`cas-installed-bytes=`, and `cas-reused=`. Those counters distinguish a true no-op wake from a
changed-file reconcile that paid object-store work, without exposing object identities or paths. ADR
0355 also reports `projection-dirs=`, `projection-files=`, `projection-bytes=`,
`projection-conflict-files=`, and `projection-conflict-tombstones=` so selected projection rebuilds
can be separated from CAS and source-walk costs. ADRs 0356--0357 carry the same final apply shape
into retained tree-v2 pull status and Sandwurm receipts. ADR 0358 then gives subscriber-side pull
completion its own volatile source digest cache, so repeated no-op applies can reuse unchanged
selected file identities instead of hashing every file again.

ADR 0345 removes another local scale tax by grouping tree-v2 path work before scan, merge, summary,
and projection decisions. The change avoids repeated extraction of the same canonical manifest
candidates while preserving complete filesystem walks, signed manifest semantics, conflict handling,
and whole-projection exchange rules.

ADR 0346 applies the same principle to manifest validation: live nested directory ancestry is proved
through one directory-path set rather than repeated manifest searches. The accepted/refused tree
semantics are unchanged.

ADR 0347 extends grouped indexing into branch-store transition validation so carried historical
entries and dropped-value refusal use per-path baseline, successor, and proof indexes instead of
repeated whole-manifest searches.

ADR 0348 applies grouped per-path indexes to retained-history `sync-diff`, reducing operator
inspection and restore-planning overhead without changing forward-only restore semantics.

ADR 0350 targets positive sparse source walks. When includes are non-empty, the scanner observes
required ancestors and descends only into included roots/subtrees; unrelated siblings below selected
ancestors stay outside source-scan custody and are still preserved during projection exchange.

ADR 0351 removes an empty projection cost for complete tree-v2 policies. When both `includes` and
`excludes` are empty, there are no unselected user paths to preserve, so projection exchange skips
the unselected-preservation and unselected-compare walkers while retaining baseline, visible, and
old-side validation. Sparse projection still preserves exclusions and unrelated local paths.

ADR 0352 makes that preservation visible at the operator boundary. Tree-v2 reconcile and
`sync-publish` now report content-free preserved-entry, directory, file, and byte counters. Complete
projection should report zeros; sparse projection reports the amount of excluded/unrelated local data
copied across the exchange without revealing paths or contents.

## Checkpoint, retention, and writer retirement

Use maintenance only after ordinary convergence and repair:

```bash
iotox sync-checkpoint field-notes
iotox sync-retention field-notes
iotox sync-gc field-notes dry-run
iotox sync-gc field-notes quarantine
iotox sync-restore field-notes
```

A checkpoint is a signed conflict-free frontier and graph floor. It refuses unresolved conflicts;
it does not choose a winner. Feature bit 31 makes checkpoint exchange explicit, while ordinary
format-1 branch and peer-frame bytes remain unchanged. GC roots current branches, explicit pins,
and every active or pending signed workspace manifest/frontier. It stops predecessor traversal only
at an authenticated checkpoint. `quarantine` uses no-replace renames and never unlinks;
`sync-restore` reauthenticates every object before returning it.

That command repairs GC quarantine only. ADR 0294's historical-content ceremony is deliberately
separate: inspect `sync-history`/`sync-diff`/`sync-conflicts`, pin the target if it must survive later
GC, obtain `sync-restore-plan`, then pass its exact ID to `sync-restore-forward`. A dirty worktree or
any intervening frontier/policy/maintenance/workspace/object change invalidates the plan. Success
authors the chosen conflict-free projection as a new higher local generation; it never rewinds the
target branch. See `sync-time-machine.md`.

Pin an exact historical record before checkpointing if its complete closure must remain live:

```bash
iotox sync-pin field-notes BRANCH_RECORD_HEX
iotox sync-unpin field-notes BRANCH_RECORD_HEX
```

To retire C, first let every survivor observe C and create its own checkpoint, then run on every
surviving device:

```bash
iotox sync-writer-cutoff field-notes C_STABLE_DEVICE_PUBLIC_KEY_HEX
```

The cutoff signs C's exact terminal generation/record, retires its current pointer, removes C from
that survivor's local automation, and refuses every later C record. It retains C in historical
writer policy so old signatures remain verifiable. This is local policy, not distributed consensus:
missing one survivor leaves that survivor willing to accept C. It also does not revoke unrelated
authority; use the separate authority revocation ceremony when that is intended.

Quiet remote observation no longer authors an acknowledgement-only branch. A merged workspace
manifest is retained under its signed journal, and only a real visible edit advances the local
writer. This prevents a full mesh from growing history merely because peers repeatedly observe one
another.

## What is still missing

This is a usable bounded full-mesh construction and an accepted incumbent replacement for one
noncritical private Linux regular-file directory. It is not a drop-in claim for every Resilio Sync
deployment. The important remaining product boundaries are:

- case-insensitive/Unicode-normalizing portability and metadata beyond private regular-file owner
  `r/w/x`; ADR 0318's doctor now refuses ASCII collisions, links, special files, ACL/xattrs, and
  sparse layout while reporting normalized ownership/modes and discarded timestamps;
- deeper incremental branch scanning and projection; ADRs 0341--0348 add bounded Linux
  filesystem-watch wakeups, 250 ms debounce, no-op refresh skipping, and volatile per-file digest
  reuse plus grouped path/ancestor/branch-validation/diff work, and ADR 0353 reduces tree-v2
  busy-republish churn, but each real reconcile still walks the complete selected tree and may
  rebuild the complete projection even though network/storage transfer is per-file;
- topology-management UX beyond explicit bilateral full-mesh sharing; the transport-only ADR 0293
  invitation is not a group-membership transaction and creates no automatic transitive trust;
- chunk/range transfer and multiple auxiliary lanes for tree-v2 file objects; ADR 0329 implements
  bounded same-source primary-lane object pipelining, but routed tree-v2 transfer and intra-object
  striping remain future work;
- sync-specific review/accept UX for recipient policy installation without remote path selection;
- physical power-cut and dishonest-storage qualification beyond the named deterministic crash
  layouts, process interruption, and same-machine KVM lifecycle evidence;
- continuously open file descriptors across projection exchange; ADR 0322 preserves a path-based
  edit made after exchange, but a process can keep writing the now-staged old directory and IoTox
  must refuse an inexact old side rather than delete it;
- operational key custody for the implemented fscrypt-v2 boundary, independently deployed witness
  persistence, broader namespace-state freshness beyond ADRs 0312/0314, and executable witness
  replacement/re-anchor ceremonies; and
- independently retained backup selection/provenance and repeated recovery operations around ADRs
  0319/0323: the bounded harness now recreates authority, reseeds one and then all replacement
  nodes, verifies every view, and safely retires obsolete writers, but its backup is still in the
  same storage/administration domain.

Keep an independent copy of important data. IoTox now qualifies as the synchronization path within
the bounded model, but a valid authorized deletion or corruption can propagate just as it can
through the incumbent product. Before using a real working directory, follow the inventory, restore-
drill, rehearsal, repair, capacity, and writer-retirement checklist in
`sync-trust-graduation.md`; the bounded verifier contract is in `sync-recovery-rehearsal.md`.

## Ordered qualification gates

1. Signed automation codec/store, deterministic scheduler, retry, replacement, and restart:
   **complete**.
2. Owner-managed one-writer create and RecallRoot read-only share: **complete**.
3. Unattended two-guest one-writer mutation, verified activation, and independent publisher/replica
   Agent restart over direct UDP and forced TCP: **complete** (ADR 0276 and
   `evidence/2026-09-01-sandwurm-sync-automation.md`).
4. Local tree-v2 CAS, signed branches, causal merge, tombstones, projection, and crash journal:
   **complete** (ADR 0272).
5. Bounded tree-v2 peer frames, authenticated graph publisher/subscriber, primary-lane transfer,
   status, repair, and exact authority fencing: **complete**.
6. `sync-create ... read-write`, reciprocal `sync-share ... read-write`, and durable pair-bound
   automation: **complete** (ADR 0273).
7. Owned local and mock-Agent tests for sequential exchange, repeated pulls, offline concurrent
   edits, deterministic conflict preservation, later resolution, deletion, zero-byte objects,
   malformed control, restart policy, and authorization: **complete**.
8. Two isolated Sandwurm guests repeating the reciprocal ceremony, stopping both daemons for
   concurrent edits, restarting, resolving, deleting, and repairing without manual publish/pull:
   **complete** (`evidence/2026-08-31-sandwurm-sync-bidirectional.md`).
9. Signed automation-v2, additive full-mesh sharing, independent per-peer backoff, all six local
   three-writer arrival orders, and a real three-daemon conflict/resolution gate: **complete**
   (ADR 0274 and `evidence/2026-08-31-sandwurm-sync-three-writer.md`).
10. Negotiated conflict-free checkpoint floors, workspace-aware multi-branch reachability, explicit
   pins, recoverable GC quarantine/restore, exact local writer cutoff, candidate bound, and an
   accelerated three-daemon lifecycle: **complete** (ADR 0275 and
   `evidence/2026-09-01-sandwurm-sync-three-writer-lifecycle.md`). The accepted networkless
   2-vCPU/2-GiB cell rotates 24 edits, propagates a checkpoint, quarantines/restores exact ancestors,
   applies matching cutoff on both survivors, and refuses retired-writer re-entry. One preceding
   cell exposed an intermittent pending exchange; ADRs 0320--0322 now add a persistent-ext4
   512-file/8-MiB full-mesh cell, batched derived-tree durability, and a watchdog restart that
   preserves the path-based local write and completes the exact cycle. ADRs 0280--0281 close the
   finite named crash/fork/conflict matrix, 16-candidate ceiling, 128 arrival permutations, and
   4,096-file local tree. ADR 0328 closes the direct post-scan source-descriptor mutation refusal,
   ADR 0329 adds bounded tree-v2 exact-object lane pipelining without changing peer frames, and
   ADRs 0341--0348 add watched source wakeups with debounce, safe no-op refresh skips, volatile
   stable-file digest reuse, and grouped local tree-v2 path/ancestor/branch-validation/diff work.
   ADR 0353 adds a tree-v2 busy-republish cooldown and reruns current near-ceiling cap 4/8/16; cap 8
   remains viable and has the best accepted sample in the 2-vCPU/2-GiB profile, but later repeats
   keep cap 4 versus cap 8 open as an operational default. Cap 16 is retained as a negative scaling
   proof.
   ADRs 0356--0358 expose and reduce repeated subscriber-side final-apply hashing during recurring
   no-op pull cycles.
   The established 512-file Sandwurm guest has since passed with the default cap-4 lane window.
   Cold/near-ceiling repetition, physical power cuts, projection/remount descriptor behavior, and
   dishonest storage remain outside the supported claim. A direct 3,500-file diagnostic timed out
   during follower object catch-up; the first source-linked four-lane direct retry passed in
   1,050.374 seconds and is retained as bottleneck evidence until the one-lane/four-lane Sandwurm
   repeat is accepted.
11. Canonical local include/exclude projection and regular-file owner-mode manifest v2:
    **complete** (ADR 0278). Existing v1 bytes remain accepted and default; deterministic worktree
    and live Agent tests prove hidden-state retention, excluded-local survival, and mode fidelity.
12. Hours-long shadow of a noncritical real directory against the incumbent product: **complete**
    (ADRs 0282--0283 and `evidence/2026-09-01-sandwurm-iotox-resilio-shadow.md`). The networkless
    2-vCPU/2-GiB cell completes 240 exact cycles over 7,200,096 ms, alternates six restarts per IoTox
    role, uses no post-setup manual transfer command, and records 356 replay-window evictions.

## Exit for the current milestone

A bounded full mesh of owner-authorized stable devices independently chooses local directories,
survives simultaneous offline edits and daemon restart, converges the same ordinary projection
without losing alternate content, resolves by a later causal edit, and passes signed frontier/CAS
repair with bounded work and no manual publish or pull after setup. The retained pair gate also
propagates deletion and an empty file. All founding-machine qualification gates are complete; the
limitations above remain product boundaries rather than open roadmap checkboxes.
