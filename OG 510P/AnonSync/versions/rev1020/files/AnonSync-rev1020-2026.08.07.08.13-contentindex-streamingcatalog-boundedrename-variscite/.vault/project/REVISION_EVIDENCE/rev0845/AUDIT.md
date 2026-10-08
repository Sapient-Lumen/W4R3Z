# AnonSync rev0845 deep audit

## Executive verdict

AnonSync's strongest implemented law remains:

> A transition may consume only authority frozen from the exact bytes, object,
> identity, lifetime, namespace, policy, resource budget, and durability facts
> that the transition will actually use.

Rev0845 applies that law one layer lower than rev0844. A directory is no longer
ambient deployment context around the local JSONL protocol; it is a typed,
process-bound, sampled authority whose exact observed loss permanently revokes
the object. This is a real implementation advance and a useful refactor.

It is not the product-defining finish line. The cube still implements a strong
local integrity/recovery kernel more completely than it implements distributed
convergence or anonymity.

## The policy-to-runtime gap

Rev0844's audit correctly admitted that same-directory concurrent writers were
outside the proof and prescribed a writer-exclusive parent directory. The
runtime, however, accepted any parent it could traverse. Several production
selftests created ledgers directly under shared `/tmp`, so the repository's own
executable examples contradicted the documented requirement.

The correction is intentionally narrower and more honest than claiming
exclusivity. `LocalJsonlReplayDirectoryAuthority::open_or_throw` freezes one
attestation over the retained directory descriptor and requires:

- owning UID equals the process effective UID;
- owner read, write, and search bits are present;
- group and other write bits are absent;
- the observed mount is not read-only; and
- the selected absolute path can be traversed component-by-component without a
  symlink and reaches the same object.

Before use, the owner repeats `fstat`, filesystem observations, and path
traversal, then requires exact agreement with the frozen attestation. This
turns a formerly ambient assumption into an executable fail-closed boundary.

The attestation records device/inode, owning and effective UID/GID, permission
mode, filesystem ID, mount flags, filesystem name maximum, and path name
maximum. Exact comparison intentionally treats drift as authority loss rather
than deciding that a subset of changed metadata is probably harmless.

## Sticky revocation closes restoration gaps

An ordinary check-then-retry owner has a dangerous ambiguity. Suppose mode,
directory binding, or lock binding changes; a proof fails; the attacker restores
the visible state; and the caller retries on the same object. A later exact
comparison can no longer prove what happened during the failed interval.

Both the directory authority and composed namespace now remember any failed
reproof. Once revoked, every later use fails even after exact visible restoration.
The same rule covers a retained lock pathname that is unlinked and recreated.
This is not merely defensive state: it preserves the meaning of “continuous
authority” by refusing to infer continuity from two matching snapshots around a
known breach.

Move operations transfer revocation state. Fork inheritance remains fail-stop:
the process-incarnation owner prevents a child from using or destroying a
parent's capability as if it had created it.

## Path meaning is validated before normalization

Lexical normalization is not security-neutral when the original spelling is the
object of policy. A parent such as `a/symlink/../safe` can discard the symlink
component before descriptor traversal. The normalized destination may be
benign, but it is not the path the caller supplied.

Rev0845 rejects `..` parent components before normalization in both the direct
directory owner and the ledger selection path. The rule is conservative and
portable: the implementation either inspects every supplied component under its
no-symlink policy or rejects the spelling; it never silently validates a
rewritten path instead.

## Refactor quality

The new authority is an independent CMake leaf with a direct executable test,
not a textual helper hidden inside the old namespace translation unit.
`LocalJsonlReplayNamespace` now composes it and routes member operations through
the retained descriptor. The namespace implementation falls from 1,223 to
1,125 lines; the extracted directory owner is 456 lines.

This split makes ownership and dependency direction enforceable. The direct
23-check corpus covers construction policy, exact attestation, move-only
semantics, moved-from denial, permission broadening, otherwise-safe mode drift,
restore-after-failure revocation, rename/recreate, symlink parents, lexical
traversal, and fork inheritance. The composed namespace corpus now reports 58
checks and proves that an exact lock-name restoration cannot resurrect a
revoked owner.

## The audit of the audits

The refactor broke two lexical audits even though their protected runtime
invariants remained intact:

1. the bounded-reader audit delimited a CMake target by an adjacent comment, so
   inserting a new independent leaf caused another target's dependency list to
   be attributed to the reader; and
2. the replay-load audit required namespace code to own a raw
   `parent_descriptor_` field instead of accepting a composed typed directory
   capability.

Both audits are now composition-aware. The first proves the bounded reader's own
target membership; the second proves descriptor-relative access through the
new owner. This is a concrete example of source-spelling audits becoming change
amplifiers: they can freeze accidental adjacency and private representation
instead of the invariant.

The 44-obligation local JSONL audit remains useful as a release pin, but it
should be progressively replaced by target-graph assertions, public type
properties, generated registration data, and semantic model oracles.

## Selftest policy was part of production quality

A grep limited to obvious `.jsonl` literals initially missed crash-injection and
backend-interface fixtures that assembled direct `/tmp` paths indirectly. Full
registry execution exposed both. All local JSONL runtime fixtures now use a
single RAII private-directory owner built with atomic 0700 `mkdtemp` creation.
The structural audit rejects regression of the two formerly hidden bypasses.

This matters beyond test neatness. Security policy that production tests evade
is usually either untestable, inaccurately stated, or likely to regress. Here it
also hid the fact that the deployment contract had never become code.

## What the capability does not prove

The name “directory authority” must not be read as a lease or sandbox.

- The same effective UID can generally mutate the directory.
- Privileged capabilities can bypass discretionary access controls.
- POSIX mode bits do not describe every ACL, idmapped-mount, LSM, or namespace
  condition.
- `fstatvfs` mount flags are useful drift observations, not a unique mount ID.
- A controller of an ancestor can change future pathname traversal.
- Every proof is sampled; mutation can race after the final check.
- POSIX still lacks a general unlink-if-inode or rename-if-identity primitive.

The capability therefore proves that the exact observations required by the
current local policy held when sampled and that known failure is sticky. A
strong deployment still needs an enforced single-writer boundary, preferably a
small broker holding the directory descriptor and exposing only typed mutation
commands.

## Validation interpretation

The complete registry contains 141 tests. Exact non-overlapping ranges
1–30, 31–60, 61–90, 91–120, and 121–141 all passed, including all 40 registered
source/architecture audits. One single-invocation attempt was externally
interrupted after 29 passes and is explicitly excluded from accounting.

The focused boundary reports 205 executable checks under GCC, Clang 17 with
`-Werror`, and GCC ASan+UBSan+LSan. This is strong changed-boundary evidence, not
a full-project sanitizer, race detector, power-loss, or release-optimization
claim.

## Waste and change amplification

The largest active concentration points remain:

- `src/sync_domain.cpp`: 15,287 lines;
- `src/sync_domain_selftests.cpp`: 9,348 lines;
- `src/sqlite_replay_ledger.cpp`: 4,527 lines;
- `src/reporting_selftests.cpp`: 4,992 lines;
- `CMakeLists.txt`: 2,492 lines;
- `src/persistence/local_jsonl_replay_namespace.cpp`: 1,125 lines;
- `src/persistence/local_jsonl_replay_directory_authority.cpp`: 456 lines;
- 41 `audit_*.py` tools; and
- `REVISION_EVIDENCE` around 25.3 MiB before final indexing.

The evidence history is several times larger than the active first-party
implementation. Recursive evidence is valuable for forensic continuity, but it
also increases every handoff's hashing, manifest, verification, transfer, and
review cost. A content-addressed evidence store with a compact current index
would preserve lineage more efficiently.

## Product-level mission still missing

The heart of the intended product is convergence under distrust, not merely
safe local mutation. AnonSync still needs:

- a formal operation algebra for update, delete, recreation, rename, duplicate
  delivery, causal gaps, concurrency, schema epochs, and key epochs;
- a deterministic reference model checked against C++ under reorder, retry,
  partition, crash, and restart histories;
- one cross-resource crash oracle covering SQLite, WAL/checkpoint state, files,
  directories, manifests, receipts, and external effects;
- hostile-input interpretation in disposable, resource-limited workers; and
- a device/key/privacy protocol for membership, rotation, revocation, state
  loss, forward secrecy, post-compromise recovery, metadata leakage, backup
  custody, rollback resistance, and realistic erasure limits.

Authentication and replay resistance do not establish anonymity. Local
recoverability does not establish convergence. These distinctions should remain
explicit in product language and release gates.

## Speculative destination

A coherent next architecture would split two planes:

- an encrypted, content-addressed data plane carrying opaque chunks; and
- a compact authenticated control plane carrying causal operations, object and
  key epochs, revocation facts, authority capsules, and explicit convergence
  semantics.

Locally, a directory broker could receive one sealed descriptor and bounded
commands such as `publish_witness`, `replace_ledger`, and
`retire_exact_member`. On modern Linux it could combine `openat2` resolution,
`statx` mount identity, dropped capabilities, namespace restrictions, Landlock,
and seccomp. These mechanisms would narrow authority; they would not replace the
operation model or storage crash oracle.
