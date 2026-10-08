# Durable cyclic remote apply, catalog predecessor reproof, and payload snapshot audit — rev0951

## Mission boundary

AnonSync exists to replace Resilio Sync in one named, measured workflow with a
practical C++ folder-synchronization product. Direct TCP, Tor, and I2P remain
routes into the same authenticated synchronization semantics. This revision
changes the retained shipping folder owner; it does not add another daemon,
route-specific sync engine, or operator-facing scheduler knob.

## Finding 1: bounded prefix progress was not fair progress

Rev0950 changed an all-or-nothing remote byte check into bounded prefix work.
That guaranteed suffix progress only while already-applied prefix values stayed
stable. Under sustained early-path churn, a successor near namespace start could
spend the remote effect allowance on every pass and starve a later eligible path.

Rotating only the old post-scan missing-file planner was insufficient. Local
traversal still applied causal remote successors inline, so an early local path
could consume the same frontier before a rotating planner ran. Fairness required
one ownership refactor as well as durable scheduling state.

## Durable cyclic remote effect owner

Catalog schema v4 owns one exact-schema singleton:

```text
sync_replica_folder_catalog_remote_apply_progress
    id = 1
    resume_after_path = last successfully selected canonical path
```

The cursor is scheduling state only. It is schema-attested and canonical-path
validated, but deliberately excluded from catalog content identity. It can
change work order; it cannot authorize an operation, payload, predecessor,
rooted path, or filesystem publication.

Before post-scan effects, the owner still reconstructs and hard-validates the
complete sole-visible remote projection. Candidate selection then starts at the
first canonical path strictly after the durable cursor and wraps at namespace
end. Count and aggregate-byte frontiers select at most one cyclic segment. Every
remote file and tombstone effect goes through this planner and the existing
rooted apply owners. Local traversal no longer spends remote effect capacity.

The cursor is published after every selected apply owner completes. A crash
after effects but before cursor publication may replay idempotent work; it does
not skip an uncommitted effect. Cursor movement joins the sync-once cutpoint so
scheduling progress is not mislabeled as a no-op.

## Finding 2: remote replacement was coupled to local scan-journal lifetime

The first cyclic implementation allowed replacement of a present local file
only when the current invocation's local traversal had opened and hashed that
exact catalog predecessor. That rule protected local edits, but it also coupled
remote liveness to an unrelated local scan epoch.

An incomplete authenticated scan journal survives restart, yet a completed epoch
is intentionally reset before the next epoch begins. Therefore a crash, payload
frontier, or remote count frontier immediately after completion could leave a
late-path remote successor behind a newly reset local cursor. The successor
could wait for an entire new rooted epoch even though the durable catalog still
named the exact predecessor. An attempted journal-membership exception was also
insufficient because completion deletes those rows.

The retained correction removes journal lifetime from remote apply nomination:

1. A current-pass local observation remains the strongest nomination because it
   already hashed the exact catalog predecessor.
2. Otherwise a present catalog `File` entry may nominate work only after a fresh
   rooted descriptor observation reproduces its durable source-snapshot digest.
3. The planner must still prove that the visible remote operation is distinct
   from and causally supersedes the catalog predecessor.
4. Immediately before effect, the exact apply owner reopens the path, hashes all
   bytes, reloads the predecessor, and compares the result again.

Fresh metadata is therefore a cheap scheduling filter, not byte authority. A
same-size or same-metadata local mutation can pass nomination, but the complete
rehash fails closed before publication. A metadata mismatch is reported as a
conflict and the remote effect is skipped. The scan journal returns to its proper
roles: resumable local traversal and complete-epoch absence proof.

Restart-backed tests prove both incomplete-epoch and completed-epoch-reset cases.
In the latter, the old epoch completes, resets, the owner restarts, and a late
`c.txt` successor applies while the new scan has reached only `a.txt`. A separate
same-path local edit proves that stale catalog metadata cannot authorize an
overwrite.

## Finding 3: one remote pass could rescan the payload namespace per file

`apply_visible_regular_file_or_throw` previously created a complete verified
payload-store snapshot for each selected file. A pass applying N files could
therefore enumerate, open, stat, and on cold observations hash the append-only
payload namespace N times. That was correct but severely wasteful at the exact
frontier introduced to make remote work bounded.

The convergence pass now retains one frozen verified payload inventory for all
remote file readiness checks and selected applies. If local publication inserted
new payloads earlier in the pass, the stale inventory is discarded and rebuilt
at most once before remote planning. The public one-operation API still creates
its own snapshot, preserving its standalone contract.

A visible file operation whose digest is absent from the frozen inventory is
ordinary scheduling remainder rather than an exception. It increments
`deferred_remote_payload_candidate_count` and does not block a ready cyclic
suffix. Payload arrival after the frozen observation is visible on the next
pass. Inventory membership is still not content authority: each selected apply
opens the digest-named payload through the retained snapshot and re-proves exact
size, digest, descriptor identity, and rooted publication boundaries.

## Schema migration and proof refactor

The v3 catalog already had the final file/tombstone entry representation and an
authenticated scan journal. Rewriting that journal merely to add scheduling
state would add I/O and migration failure surface. The v3→v4 transaction:

1. proves exact v3 schema, catalog digest, entries, and scan continuation;
2. renames only the metadata table;
3. creates v4 metadata and remote-cursor genesis;
4. recomputes the catalog digest in the v4 domain;
5. retains scan-progress and seen-path rows in place;
6. drops old metadata; and
7. re-proves the migrated catalog, exact scan continuation, and cursor genesis
   before commit.

Exact v1 and v2 databases migrate directly to v4. Near-match schemas remain
rejected. The repeated v2/v3/v4 catalog row walk is consolidated in one modern
catalog loader parameterized by exact schema and digest domain; the genuinely
different v1 file-only decoder remains separate.

## Reporting, settlement, and idle truthfulness

Pass and service JSON now expose:

- remote payload snapshot observations and frozen entry count;
- remote candidates deferred for missing payload bytes;
- catalog predecessors nominated through fresh metadata reproof;
- starting/resulting remote cursor and projection wrap; and
- the existing count, byte, and stop-reason frontiers.

`sync-once` treats missing-payload candidates as unresolved scheduling work. The
speculative idle path re-proves catalog, replica, payload inventory, remote
cursor, and the authenticated local scan journal before returning no work. These
owners are read sequentially; this is not a cross-database atomic snapshot.

## Executable evidence

New and strengthened tests prove:

- persistent cyclic service of a later path under sustained early-path churn;
- exact v3→v4 preservation of a non-genesis authenticated scan journal;
- invalid cursor path tampering fails closed;
- independent local-scan and remote-effect limits compose;
- one payload inventory serves multiple selected files;
- a missing-payload prefix does not block a ready suffix;
- restart after an incomplete scan does not force a catalog predecessor to wait
  for scan wrap;
- completed epoch reset plus restart does not recreate that delay;
- a local edit is not overwritten even when the catalog path is nominated;
- sync-once counts cursor movement and missing-payload remainder truthfully; and
- the real two-process path binds cursor and payload-inventory diagnostics.

The lexical structural audit now contains 70 checks. It checks source ownership
and vocabulary only; it is not a semantic, filesystem, cryptographic,
transactional, concurrency, or crash proof.

## Exact nonclaims and next work

Rev0951 does not make each pass cheap. It still reconstructs and hard-validates
the complete remote projection, replays local rooted prefixes, completely
buffers and sorts each immediate directory, and performs restart-cold complete
payload observations. The payload snapshot is frozen; newly arriving bytes may
wait one pass. A mutation between metadata nomination and exact apply causes a
fail-closed retry, not race-free progress. Cursor publication is not atomic with
catalog, replica, payload, or filesystem effects.

There is still no durable exact payload index, monotonic remote-work index,
rotating integrity scrub, coordinated retention/restore/garbage collection,
changed-block production transfer, identity-preserving rename, complete
directory/metadata semantics, selective sync, many-share device owner, or named
workload qualification.

The next scale owner should be a crash-consistent exact metadata/subtree,
remote-work, and payload index with monotonic sequence numbers and bounded
queues. Descriptor-rooted complete scanners must remain rebuild and rotating-
scrub oracles. Retained versions, restore, reachability, quarantine, and garbage
collection should be designed as one recovery system rather than independent
optimizations.
