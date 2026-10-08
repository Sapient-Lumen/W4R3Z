# AnonSync rev0844 deep audit

## Executive verdict

AnonSync's strongest implemented law remains the right one:

> A transition may consume only authority frozen from the exact bytes, object,
> identity, lifetime, namespace, policy, resource budget, and durability facts
> that the transition will actually use.

Rev0844 applies this law to the local JSONL replay backend as a whole. The result
is materially safer than a collection of individually hardened file calls: one
retained owner now binds the directory, lock, ledger, temporary, journal,
staging publication, rename, unlink, and directory durability sequence.

## The severe ordering defect

The first implementation direction created and published the journal before the
replacement temporary was complete. That makes the journal's temporary name
look like recovery authority before the named object has proved its bytes.
Pre-commit rollback could consequently unlink a partial object, or—after
same-directory rebinding—unrelated bytes that merely occupied the nominated
name.

The correction is architectural rather than a local condition: complete and
fsync the replacement first, then publish a witness that binds its digest,
canonical chain, previous payload digest, and implementation-minted name.
Recovery re-reads and validates the exact temporary before every retirement.
This changes the authority direction from “journal names something deletable”
to “a complete object may be retired only after proving it is the object the
journal described.”

## Retained namespace authority

`LocalJsonlReplayNamespace` converts the selected ledger spelling to one
absolute lexical path, opens the root, and traverses parent components using
`fstatat(AT_SYMLINK_NOFOLLOW)` plus `openat(O_DIRECTORY|O_NOFOLLOW)`. It retains
the final parent descriptor and identity. Every later operation:

1. verifies the descriptor is still the retained directory;
2. retraverses the absolute parent without symlinks;
3. proves that spelling still reaches the same `(device,inode)`; and
4. performs the member operation relative to the retained descriptor.

This closes parent-directory rename/rebind attacks that separate validation from
mutation. It also converts fork inheritance into a fail-stop boundary by binding
the owner and every opened member to the creating process incarnation.

The lock is treated as namespace authority rather than merely an integer file
descriptor. While held, each namespace proof confirms that the lock pathname
still denotes the descriptor on which `flock` was acquired. An unlink/recreate
attempt therefore fails instead of silently allowing two cooperating writers to
hold locks on different inodes under the same name.

## Crash-complete journal v3

Journal v3 adds the exact previous payload SHA-256 and the temporary basename.
The basename is not accepted by prefix alone: it must be exactly the grammar the
implementation can mint, with canonical positive decimal PID and sequence
components, byte budget, and `NAME_MAX` compliance.

Journal publication uses a complete fsynced staging inode, then `linkat` to the
final name. Unlike rename, the link edge cannot overwrite an existing witness.
The authorized intermediate topology is exactly two reserved names, the same
inode, and link count two. Recovery either completes that publication by
retiring the staging name or rejects every other multiply-linked/two-name shape.

The directory barriers are explicit:

- after journal publication, covering the previously created temporary plus the
  final journal name and staging retirement;
- after temporary-to-ledger rename; and
- after journal unlink.

That ordering makes journal existence, ledger replacement, and journal
retirement separate durable state transitions rather than optimistic side
assumptions around file fsync.

## Recovery classification

Recovery first classifies journal topology as absent, staging-only, final-only,
or the exact linked pair. A staging-only object never crossed the no-overwrite
publication edge; it is preserved without interpretation or deletion. An
unbound pre-journal temporary is likewise not scanned or guessed.

For a final v3 journal, the current ledger payload must match either:

- `previous_payload_sha256`, authorizing a pre-rename rollback; or
- `payload_sha256`, authorizing post-rename completion.

In both cases any still-present temporary must match the intended digest and
validate as the complete canonical next ledger, including line count, head,
prefix head, and last-entry predecessor. Only then can recovery retire it. The
journal itself is retired only after the relevant temporary proof, followed by
another directory fsync.

Legacy v2 remains readable only on the post-commit side where its payload digest
matches the committed ledger. It does not gain new rollback authority that the
old format never encoded.

## Independent runtime and structural audit

The focused runtime corpus reports:

- canonical publication: 42 checks;
- namespace owner: 48 checks;
- backend integration: 30 checks; and
- crash state machine: 52 checks.

The 37-obligation structural audit pins dependency direction, descriptor-relative
operations, journal versions, publication ordering, all three directory
barriers, exact temporary grammar, recovery digest/chain proof, stale loaded
state, residue preservation, lock rebinding, fork inheritance, CTest
registration, and package inventory.

Tests include parent-component symlinks, parent rename/replacement, lock
unlink/recreate, hard-link topology, linked journal recovery, partial staging,
pre-journal temporary orphans, every named pre/post durability cutpoint, forged
temporary names, and replacement of a journal-bound temporary with hostile
bytes. The hostile bytes and dirty witness are preserved on rejection.

## Remaining local correctness boundary

POSIX supplies descriptor-relative lookup but not an atomic
“unlink this name only if it still denotes inode X” or “rename only if both
source and destination retain these identities.” A hostile actor with concurrent
write authority in the retained directory can race between a final identity
check and a name-based mutation. The current protocol is therefore safe against
parent-path rebinding and non-cooperating stale state, but deployment must still
make the directory writer-exclusive. A stronger future design could place all
mutations in a narrowly privileged helper, add Linux-specific exchange/quarantine
protocols, or use filesystem/OS capabilities with stricter directory authority.

Logical fault injection also cannot prove all persistence behaviors of every
filesystem, mount option, controller cache, or storage device. A future crash
oracle should run the protocol against power-cut/fault-injection filesystems and
record the recovered state at every persisted subset permitted by the target
storage model.

## Waste and change amplification

The refactor removes broad path choreography from `replay_ledger.cpp`, but the
new namespace owner is itself 1,223 lines because descriptor lifetime, path
traversal, topology, locking, reading, publication, and mutation are still in
one unit. It is a stronger boundary, not the end of decomposition.

The largest active concentration points remain:

- `src/sync_domain.cpp`: 15,287 lines;
- `src/sync_domain_selftests.cpp`: 9,348 lines;
- `src/sqlite_replay_ledger.cpp`: 4,527 lines;
- `src/reporting_selftests.cpp`: 4,897 lines;
- `CMakeLists.txt`: 2,448 lines;
- `src/persistence/local_jsonl_replay_namespace.cpp`: 1,223 lines;
- 41 `audit_*.py` tools; and
- revision evidence around 25 MiB before the current handoff.

The 628-line new lexical audit is useful as a release pin, but it also illustrates
proof-cost growth. Once the state machine has a small executable model and the
namespace API is split into typed capabilities, source-spelling obligations
should be retired in favor of semantic oracles and build-graph constraints.

## Product-level mission still missing

Local authenticity and recoverability are prerequisites, not convergence or
anonymity. AnonSync still needs an operation algebra for update, delete,
recreation, rename, duplicate delivery, causal gaps, concurrency, schema epochs,
and key epochs; a deterministic model checked against production under
reordering, retry, partition, and restart; and a device/key protocol covering
membership, rotation, revocation, state loss, forward secrecy,
post-compromise recovery, payload encryption, metadata leakage, backup custody,
and rollback resistance.

A coherent destination remains a ciphertext/content-addressed data plane plus a
small authenticated causal control plane. The operation model should define the
protocol; local file and SQLite mechanisms should implement it rather than
silently becoming it.
