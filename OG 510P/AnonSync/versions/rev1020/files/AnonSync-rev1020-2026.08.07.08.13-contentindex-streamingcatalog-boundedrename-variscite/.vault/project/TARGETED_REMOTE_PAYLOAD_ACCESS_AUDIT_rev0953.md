# Targeted remote payload access audit — rev0953

## Decision

A remote-only convergence pass should not enumerate and hash the complete
private payload namespace merely to answer whether one already-admitted digest
is present and to open that exact file for publication. Rev0953 adds a narrow,
pass-scoped capability for that question while preserving the complete payload
snapshot as the only namespace-health, capacity, and full-digest-inventory
oracle.

This is a bounded-read optimization, not a new payload-store truth model.

## Defect corrected

Before this revision, any remote file candidate without a retained local payload
snapshot forced `snapshot_or_throw()`. That operation walks every payload-root
entry, opens and stats every admitted object, and hashes every cold or changed
payload. A one-file remote delivery therefore paid work proportional to all
retained payload history. A tombstone-only local catalog could trigger the same
cold inventory even though local traversal had no file bytes to publish.

The first rev0953 implementation removed that complete scan but repeated store
identity reconciliation, marker durability work, root reopening, and descriptor
duplication for every probe and every selected apply. A pass with N ready files
could perform roughly 2N independent store preflights. That was correct but
wasteful and enlarged the number of cutpoints that had to agree.

The final refactor introduces one move-only
`SyncReplicaFilePayloadStoreTargetedAccess` per convergence pass. Its birth:

1. verifies the product-bound source authority;
2. performs identity bootstrap/reconciliation once when the store disposition
   requires durable observation;
3. reopens one matching rooted authority;
4. acquires one observation-only shared-lease cutpoint;
5. freezes the exact identity-marker observation; and
6. retains one descriptor sharing the selected root open-file description.

Each exact-name probe or selection then acquires a fresh fail-fast shared lease,
requires the marker inode and full observation to match the birth cutpoint,
opens only the lowercase SHA-256 basename beneath the retained descriptor, and
re-proves the name, lease, mount, and root. The access itself retains no store
lease across planning or destination I/O.

## Authority and nonclaims

The targeted lane may answer only one of two things:

- the exact admitted digest name is absent at the bounded lease/root cutpoint; or
- the exact name is a private regular file with the operation's expected size,
  and an opened descriptor can be retained for the apply owner.

It does **not** prove:

- that unrelated payload-root entries are valid;
- that the namespace is within entry or byte capacity;
- that the selected file's bytes match its digest before consumption;
- that the payload store is free of stale partials or hostile extra names;
- that advisory locking constrains a non-cooperating writer; or
- that one observation remains current after its descriptor or lease is gone.

`SyncReplicaFilePayloadStoreSnapshot::snapshot_or_throw()` remains the complete
namespace scanner and health oracle. Tests deliberately place an invalid
unrelated entry beside a valid selected digest: targeted apply succeeds, while a
subsequent complete snapshot rejects the namespace. That separation prevents a
bounded point lookup from being mislabeled as an audit.

## Byte proof and publication

The targeted probe checks type, ownership/privacy policy, exact size, name-to-
inode stability, mount containment, marker identity, and root authority without
hashing bytes. Selection repeats the exact-name open under a fresh lease. The
borrowed descriptor then crosses the existing atomic publication boundary,
which streams the source once, checks SHA-256, publishes beneath the rooted
folder authority, and verifies the resulting destination before catalog
advancement.

This avoids a redundant pre-publication whole-file read while still making the
publisher the only component allowed to convert selected bytes into visible
filesystem state. Same-size corruption reaches that boundary and fails closed;
the destination and catalog remain unchanged.

## Missing-payload scheduling

Remote evidence can precede payload delivery. Exact absence during planning is
ordinary unresolved scheduling work and does not spend an effect slot or block a
ready suffix. Presence at probe followed by absence at selection also produces
unresolved remainder rather than publication. The durable cyclic cursor and
inspection-sweep rules cause later reconsideration; targeted absence is never
catalog or content authority.

A retained complete payload snapshot still wins when local work already needed
one and it remains valid. The negative telemetry proof requires such a pass to
report zero targeted accesses, probes, selections, and selected bytes. A remote-
only pass with multiple probes and selections must report exactly one targeted
access.

## POSIX primitive audit

Rev0953 factors required and optional regular-file component opening through one
implementation. Optional open returns `nullopt` only for `ENOENT` during the
bounded no-follow inspection/open sequence. Symlinks, non-regular entries,
permission errors, mount crossings, unsafe components, and identity races remain
errors. Linux uses the retained `openat2`/mount-id capability where available;
the fallback preserves `O_NOFOLLOW`, before/after inode comparison, and retained
mount proof.

The fresh shared lease on every probe/selection is intentional. Linux `flock`
locks are associated with open-file descriptions; separately opened descriptors
are treated independently. The pass-scoped capability therefore amortizes root
and identity setup without pretending one released preflight lock protects later
operations.

## Telemetry

Pass and CLI JSON now distinguish:

- complete payload snapshot observations and entries;
- targeted access births;
- targeted exact-name probes;
- targeted descriptor selections;
- operation bytes represented by successful selections; and
- missing-payload deferrals.

“Selected bytes” is admitted operation size, not a claim that every selected
byte was read in cases where an exact destination already made the apply a no-op.
The atomic publisher's SHA-256 check remains the content proof when publication
consumes the descriptor.

## Tests and structural checks

The focused runtime suite covers:

- exact optional regular-file presence and absence;
- symlink and directory refusal in the optional primitive;
- missing prefix with ready suffix progress;
- one access serving two probes and one selection;
- one access serving two probes and two zero-byte selections;
- complete-snapshot reuse with zero targeted work;
- invalid unrelated namespace entry as an explicit nonclaim;
- same-size selected-payload corruption caught only at publication;
- tombstone-only local state avoiding a complete inventory; and
- process JSON exposure.

The lexical structural audit checks ordering and vocabulary around the targeted
access birth, per-operation leases, identity reproof, absence semantics,
telemetry, and sole publisher hashing. It is a regression tripwire, not semantic,
filesystem, concurrency, cryptographic, or crash proof.

## Remaining cost and next product edge

This revision removes a pathological cold complete scan from remote-only point
work, but it does not create the durable payload index the product still needs.
A large remote projection still performs one pathname probe per file candidate,
and ready files are opened again for selection. Complete local/snapshot lanes
still enumerate the payload namespace; restart loses the process-local
verification cache; retained history is append-only; changed files still move as
whole payloads; and no rotating byte scrub detects latent corruption between
complete reads.

The next scale move should be a crash-consistent payload metadata index with a
monotonic change sequence, exact descriptor-bound observations, rebuild from the
complete scanner, and a bounded rotating byte scrub. Retention, restore,
quarantine, and garbage collection must be designed together so that an index
never silently turns stale history into missing recovery data.
