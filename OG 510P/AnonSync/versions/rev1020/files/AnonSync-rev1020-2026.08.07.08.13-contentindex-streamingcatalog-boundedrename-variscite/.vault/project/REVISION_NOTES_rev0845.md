# AnonSync rev0845

## Mission increment

A retained directory descriptor is not, by itself, authority to mutate a
security-sensitive namespace. The exact directory identity, ownership,
permission surface, mount observations, path meaning, process incarnation, and
continued name binding must be frozen and re-proved before each namespace
transition. Once a proof fails, restoring visible state later must not recreate
authority across the unobserved interval.

Rev0845 turns rev0844's deployment prose into an explicit C++ capability. It
also states the ceiling honestly: the capability proves a sampled,
owner-controlled mutation surface, not process exclusivity against the same UID,
privileged actors, ACLs outside the sampled mode proof, or mutation between
observations.

## Severe defects found and corrected

Rev0844 required a writer-exclusive parent directory in documentation, but the
runtime did not attest that condition. Several integrated selftests even opened
local JSONL ledgers directly beneath shared `/tmp`, silently demonstrating that
the stated policy was neither executable nor consistently exercised.

A second authority defect was subtler. Directory or lock identity could fail a
reproof, be restored, and then be accepted by the same owner on a later retry.
That erased the evidence that an unobserved authority interval had occurred.
Rev0845 makes failed directory and namespace reproof sticky: the affected object
is permanently revoked.

A third path-meaning defect came from lexical normalization. A supplied parent
containing `..` could discard an earlier component before descriptor traversal.
If that discarded component was a symlink, the implementation could accept a
different lexical meaning instead of inspecting and rejecting the original
selection. Parent traversal components are now rejected before normalization.

## Delivered

- Added `LocalJsonlReplayDirectoryAuthority`, a move-only,
  process-incarnation-bound owner of one retained directory descriptor.
- Added `LocalJsonlReplayDirectoryAttestation`, freezing device/inode,
  effective and owning UID/GID, permission mode, filesystem ID, mount flags,
  and filesystem/path name limits.
- Opening requires the effective UID to own the directory, owner
  read/write/search permissions, no group/other write bit, and no observed
  read-only mount flag.
- Every proof rechecks the retained descriptor, exact attestation, and an
  independently re-traversed no-symlink absolute spelling.
- Any failed directory reproof permanently revokes the directory owner. Any
  failed composed namespace or retained-lock proof permanently revokes the
  namespace owner.
- Rejects lexical parent traversal components before normalization.
- Refactors `LocalJsonlReplayNamespace` to compose the directory capability;
  its implementation falls from 1,223 to 1,125 lines and no longer owns the
  traversal/attestation machinery internally.
- Replaces local JSONL selftest fixtures beneath shared `/tmp` with atomic,
  unique 0700 `mkdtemp` workspaces and RAII cleanup.
- Adds a direct 23-check directory-capability corpus and extends namespace
  tests to 58 checks, including restored-mode, restored-lock, rename/recreate,
  symlink, movement, and fork-inheritance cases.
- Makes two adjacent lexical audits composition-aware. They had encoded
  accidental source adjacency and private-field ownership, causing valid
  decomposition to look like a security regression.
- Extends the local JSONL structural audit to 44 obligations, including the
  private-fixture policy and the explicit non-claim of process exclusivity.

## Validation

The exact record is in
`REVISION_EVIDENCE/rev0845/validation/VALIDATION_SUMMARY.json`.

The final active source passed a GCC 14.2 Debug all-target build and a final
zero-compile/zero-link dependency closure, all **141 registered tests** in exact
non-overlapping ranges, all **40 registered source/architecture audits**, a
Clang 17 `-Werror` focused lane, and a GCC 14 ASan+UBSan+LSan focused lane.

The changed local JSONL boundary reports **205 direct executable checks**:
publication 42, directory authority 23, namespace 58, backend integration 30,
and crash state machine 52. The local protocol audit passes **44/44**, the
replay-load authority audit **28/28**, and the bounded-reader regression audit
**23/23**.

One attempted single all-registry CTest invocation was externally interrupted by
the cloudtainer after 29 passing tests, with no failed assertion and no surviving
process. It is retained as non-gating evidence and is not counted as a complete
run; release accounting uses the five exact, non-overlapping successful ranges.

## Scope limits

Mode, UID/GID, `fstat`, `fstatvfs`, and path re-traversal are sampled
observations. They do not prove an exclusive lease, prevent same-UID or
privileged mutation, describe every ACL or Linux security module decision,
uniquely identify a mount, or close the race between final observation and a
name-based mutation. A mutable ancestor can also change future pathname
meaning. Stronger deployment should place all ledger-family mutation behind a
narrow broker or other enforced writer boundary.

The Linux 4.4 host cannot execute an `openat2`/`statx` lane. Rev0845 also does
not claim arbitrary power-loss completeness, Windows runtime coverage,
distributed convergence, payload confidentiality, anonymity, metadata hiding,
forward secrecy, post-compromise recovery, hostile-parser isolation, or secure
erasure.
