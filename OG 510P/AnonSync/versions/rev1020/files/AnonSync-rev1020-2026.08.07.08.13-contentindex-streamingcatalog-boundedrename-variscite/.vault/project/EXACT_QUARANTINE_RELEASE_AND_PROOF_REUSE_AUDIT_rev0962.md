# Exact quarantine release and authoritative-proof reuse audit — rev0962

## Heart of the mission

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
product. Rev0961 made a proven corrupt payload operable by preserving its exact
wrong byte image outside payload authority while ordinary authenticated
convergence restored the expected digest. That operation was intentionally
bounded, but it left no supported way to reclaim its diagnostic capacity.
Eventually a healthy service could reach the quarantine frontier and require an
operator to edit the private store by hand. Rev0962 closes that lifecycle gap
without pretending to implement automatic retention or garbage collection.

The new owner command is:

```text
anonsync_sync quarantine-release --socket ABSOLUTE_SOCKET \
    --expected LOWERCASE_SHA256 --observed LOWERCASE_SHA256
```

It releases exactly one canonical expected/observed diagnostic image after the
active integrity alarm has been cleared. It does not choose evidence, infer age,
restore user data, collect reachable payloads, or delete automatically.

## Exact-pair product boundary

The two digests are mandatory, canonical, distinct, and map to exactly one
`.anonsync-payload-quarantine-v1-<expected>-<observed>` basename. The local
socket admits `quarantine-release EXPECTED OBSERVED\n` through the same
owner-only mode-0600 path, PID-bound response validation, action generation,
condition variable, and shutdown seal already used by drain, recheck, and
preserve. Preserve and release share one quarantine slot: the operation kind is
part of the mutex-linearized request identity, so a pending release cannot be
silently overwritten by a preserve request for the same digest pair.

Acceptance remains process-local scheduling evidence. Completion is reported
separately by live or terminal status.

## Active-fault release fence

Diagnostic bytes for any current unresolved payload-integrity incident are not
releasable. The exact owner-thread process witness is checked before acquiring
mutation authority. A present alarm returns typed `active_fault_present`
without removing any quarantine. For the same expected digest, status reports
the currently observed digest; an unrelated active fault does not invent a
current observation for the requested pair.

The command is therefore a post-recovery capacity operation, not a way to erase
evidence while authority remains blocked.

## Rooted exclusive release path

A permitted release uses the existing payload-store authority rather than a new
filesystem helper:

1. re-prove the retained root and exact reader-fenced identity;
2. reopen the same rooted authority;
3. acquire the existing exclusive mutation lease on the exact identity inode;
4. completely enumerate and validate the bounded quarantine namespace;
5. duplicate the rooted descriptor capability and retained mount identity;
6. open the exact quarantine as a private regular file beneath that root;
7. require the post-enumeration descriptor observation to match exactly;
8. re-prove the named private regular file immediately before mutation;
9. unlink only that scanned inode;
10. synchronize the root directory;
11. prove the exact name absent; and
12. re-prove lease, reopened root, and retained root at the terminal cutpoint.

A missing exact pair returns typed `exact_quarantine_absent`. A successful
unlink returns `released`, the exact basename, and the previously observed size.
`ReadOnlyInspect` cannot release bytes.

## Why release does not hash the diagnostic bytes

Preservation must hash bytes because a canonical filename is not evidence that
its contents match the claimed observed digest. Release is different: the owner
has supplied the exact canonical pair and is explicitly asking to discard that
diagnostic image. The safety obligation is to remove only the exact bounded,
private, rooted inode that was just enumerated and re-proved—not to spend I/O
re-establishing evidence that is about to be destroyed.

The release path therefore performs complete namespace and metadata authority
checks but no payload-content hash. This is not an authenticity claim about the
deleted bytes. It is a precise deletion claim about the selected private file.

## Adjacent waste audit: preserve no longer revokes unrelated byte proof

Rev0961 used a broad post-rename invalidation helper. A successful preserve
removed one authoritative digest, but it also discarded the entire process
verification generation. The next complete scan could rehash every unrelated
payload even though their names, metadata, bytes, root, identity, and process
owner had not changed. On a large healthy store, preserving one corrupt object
could turn recovery into a whole-store reread.

The audit separated three states that had been conflated:

- **authoritative namespace membership** changed because the corrupt digest name
  disappeared;
- **unrelated payload byte proof** remained exact and usable;
- **durable namespace checkpoint and scrub scheduling** needed refresh because
  count/byte membership changed and an active scrub might target the removed
  digest.

Rev0962 replaces whole-generation revocation with a narrow refresh. It forces a
new durable checkpoint observation, clears only stale publication-capacity
observation, clears active scrub continuation only when it names the removed
digest, and resets the scrub schedule. The old digest's cached entry grants no
authority because complete snapshots still enumerate the current namespace and
reuse requires an exact current regular-file observation. Unrelated entries
remain eligible for exact process-local reuse.

Exact quarantine release changes only the non-authoritative diagnostic
namespace. It therefore retains both process and durable authoritative payload
acceleration.

## One linearized local action lane

No second queue or daemon was added. `SyncLocalStatusSocketPayloadQuarantineOperation`
distinguishes `Preserve` and `Release` inside the existing quarantine request.
The combined action snapshot carries operation, pair, and generation under one
mutex. Same-operation/same-pair requests may coalesce; a different operation or
pair is rejected while pending. Owner completion is generation checked, drain
seals both forms, and post-seal requests do not advance state.

The socket worker still has no payload, folder, SQLite, TLS, route, scanner, or
effect capability. It only authenticates local pathname/PID framing and
publishes owner work.

## Status contract

Status advances to `anonsync.peer-service.status.v9`. The canonical live and
terminal quarantine renderers now include:

- action (`preserve` or `release`);
- requested, started, and completed generations;
- exact expected and observed digests;
- bounded retry state;
- typed last result;
- a retained basename only when the result proves one;
- images preserved; and
- images released.

The shipping release response has its own strict schema,
`anonsync.local-quarantine-release.response.v1`, so an older client cannot
mistake release admission for preserve admission.

## Mechanical runtime oracles

The focused payload-store regression establishes two payloads, proves both
bytes, corrupts and preserves one, and then proves:

- release is blocked while the active fault remains;
- the next complete snapshot hashes zero bytes and reuses the unrelated payload;
- exact release removes only the selected quarantine;
- the following complete snapshot still hashes zero bytes and reuses the
  unrelated payload;
- a second release returns typed exact absence; and
- forensic inspection cannot mutate.

The local-socket regression proves exact release request/response bytes,
operation-aware pending exclusion, shared generations, combined waits, drain
ordering, post-drain rejection, owner/mode/path checks, PID binding, malformed
response rejection, and client argument validation.

The real configured-service oracle preserves and re-admits a corrupt payload,
then invokes the shipping release command in the same healthy PID. It requires
exact generation/result status, absence of the diagnostic pathname, unchanged
authoritative payload bytes and inode, unchanged completed recheck evidence,
continued readiness, retained recovery history, release accounting, and clean
drain.

## Audit/refactor findings

1. **Capacity without release was not an operable bounded policy.** A hard
   quarantine frontier is safe but eventually unusable if the only supported
   reclamation path is private-store surgery. Exact explicit release fixes the
   product lifecycle while leaving policy choice with the owner.
2. **Rev0961's broad acceleration revocation was wasteful.** Namespace removal
   of one corrupt digest did not invalidate exact observations for every other
   payload. Narrow refresh preserves those proofs while forcing the namespace
   checkpoint to catch up.
3. **Preserve and release must be different action identities.** Pair-only
   coalescing could acknowledge the wrong requested operation. Operation is now
   carried through parser, combined snapshot, service owner, result, status,
   and process oracle.
4. **Deletion does not need a redundant content proof.** Hashing bytes solely to
   delete exact explicitly selected diagnostic evidence would spend I/O without
   strengthening the rooted unlink claim.
5. **An active fault is a global release fence.** The service cannot safely
   reclaim diagnostic evidence while any current payload authority incident is
   unresolved, even if the requested pair is different.

## What this proves

Rev0962 proves a bounded vertical C++ lifecycle from the owner CLI through the
local action linearization, service owner, exact reader-fenced lease, rooted
private-file unlink, status/accounting, real process, and package policy. It
also proves that preserving or releasing one diagnostic image need not force a
whole-store reread of unrelated payload bytes.

## What this does not prove

- There is no automatic retention, age policy, quota allocator, reachability
  graph, archive browser, restore command, version history, or garbage
  collector.
- Explicit release is irreversible; AnonSync does not yet preserve a second
  recoverable copy elsewhere.
- Requests and generations remain process-local.
- The same-effective-user boundary remains cooperative, not hostile same-UID
  protection.
- Linux `flock`, rooted `openat`/unlink behavior, Unix sockets, and directory
  synchronization are not a portable network-filesystem contract.
- Power-loss behavior still needs qualified filesystem/storage testing.
- Rename identity, directories, portable metadata, conflict UX, selective sync,
  changed-block transfer, many-share ownership, live Tor/I2P privacy
  qualification, and a named measured Resilio uninstall workflow remain open.
