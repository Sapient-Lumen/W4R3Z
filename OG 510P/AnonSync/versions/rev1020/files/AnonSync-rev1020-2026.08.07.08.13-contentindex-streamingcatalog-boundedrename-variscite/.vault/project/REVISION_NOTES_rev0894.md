# AnonSync rev0894 — serialized payload capacity and independent scan cursors

## Mission

AnonSync remains an authority-accounting system. Exact authorized history and
live owned capabilities govern identity, content availability, selection,
attempt, retry, receipt, and visible effect. Digests, indexes, directory
listings, locks, and test reports are subordinate evidence; none may silently
manufacture authority.

## Primary correction

Rev0893's durable payload owner performed an exact full scan before each put,
but aggregate entry and byte capacity was not serialized across processes. Two
cooperative writers could both approve the same remaining budget before either
published.

Rev0894 uses the exact immutable folder-identity marker as a versioned,
fail-fast advisory lease anchor:

- snapshots hold a shared lease through their complete scan and immutable
  snapshot construction;
- puts hold an exclusive lease from exact full-store preflight through
  create-new publication or exact reconciliation;
- an independently opened marker must reject the opposite lock mode before the
  lock is trusted;
- every ordinary scan receives the move-only lease witness and re-proves that
  the marker pathname still names the exact locked inode after traversal;
- snapshot construction and every publication/reconciliation terminal path
  re-prove the exact lock inode again at their final authority cutpoint;
- lock contention fails explicitly through a typed busy error rather than
  blocking indefinitely or requiring diagnostic-text parsing; and
- the lease protocol is included in snapshot digest evidence.

The durable identity generation is also advanced from v1 to v2 and binds the
exact lease protocol in its bytes. A rev0893 root is refused without mutation
and requires an explicit offline migration; a rev0893 process likewise treats
the v2 marker as unknown. Mixed-version writers can therefore no longer share a
root while silently disagreeing about whether capacity must be serialized.

This serializes aggregate-budget decisions among cooperative owners on a
filesystem whose observed `flock(2)` semantics provide independent-open
exclusion. It is not hostile-writer security or mandatory locking.

## Severe scan defect corrected

The new repeated-scan regression exposed a rev0893 ownership error. The scanner
passed a duplicate of the retained root descriptor to `fdopendir()`. Duplicated
descriptors share one open file description and directory offset, so the first
`readdir()` traversal could leave the long-lived root cursor at end-of-directory.
A later scan could then omit the identity marker or payload entries.

The scanner now reopens and fully attests an independent matching root before
creating its directory stream. It re-proves both the temporary scan authority
and the retained authority at the final cutpoint. Repeated scans no longer
inherit a consumed cursor.

## Audit and refactor work

- Two private copies of the privileged directory-descriptor duplication bridge
  have been retired. `SyncDirectoryAuthority` now owns one internal move-only
  RAII result whose type and method name explicitly state that `dup` shares the
  existing open file description. Atomic publication and the payload store use
  that bridge for descriptor-relative syscalls, while the scanner must first
  reopen an independently positioned directory authority before `fdopendir()`.
- The duplicated retained-directory descriptor bridge formerly copied between
  atomic publication and the payload store is now one move-only internal RAII
  owner named `SyncDirectorySharedOpenDescriptionLease`; its API and audit make
  shared offsets/status flags explicit and forbid treating `dup` as a fresh
  observation cursor.
- Exact identity-marker validation is shared by scan and lease paths.
- The raw namespace scanner is now an explicit bootstrap-only primitive.
  Snapshot and put paths can only traverse through a lease-witness wrapper that
  checks the required shared/exclusive mode and re-proves the locked anchor at
  both scan cutpoints.
- The put path consumes the internal full-scan result directly instead of
  constructing a public snapshot, duplicate digest vector, content inventory,
  and snapshot digest solely for capacity checks.
- The audit now distinguishes descriptor ownership from independent open-file-
  description state, inventories the shared/exclusive lease sequence, and
  records that this is the active tree's only production `fdopendir()` owner.
- The package verifier requires the complete rev0894 implementation, runtime
  matrix, parent design record, and lease/cursor audit.
- Test-only descriptor cleanup was corrected to avoid retrying `close()` after
  `EINTR`, which could act on a reused descriptor number on platforms where the
  close had already taken effect.
- Repeated validation exposed a separate test-control race in the atomic
  publication campaign: the start-gate pathname became visible before its
  three-byte payload was complete. The gate is now written and synchronized
  under a private staging name, closed, and atomically published with
  `renameat2(RENAME_NOREPLACE)` before any worker can observe it. This removes
  false product failures without weakening the worker-side identity proof.
- Sanitizer stress exposed a brittle TLS regression that required a positive
  `accept4()` attempt even though the API accepts absolute deadlines. The test
  now distinguishes diagnostic attempt counts from authority progress, covers
  the already-expired zero-attempt result explicitly, and captures membership
  authority before starting the no-peer timeout budget.

## Validation

The final source passed:

- the complete GCC 14.2 Debug registry, **213/213**, in one invocation;
- the complete audit/policy selection, **84/84**, in one invocation;
- **2,220/2,220** focused assertions independently under GCC 14.2 Debug,
  Clang 17 Release C++ `-Werror`, and GCC ASan/UBSan with leak detection;
- **25/25** repeated GCC Debug authority runs spanning atomic publication,
  payload-store mutation, and file-delivery composition (**5,100/5,100**
  assertions);
- **5/5** repeated GCC ASan/UBSan authority runs spanning atomic publication,
  payload-store mutation, and real TLS transport (**10,400/10,400**
  assertions);
- **328/328** selected source-audit and package-path-policy checks, plus the
  independent **13/13** release-verifier policy matrix; and
- the exact rev0893 parent archive under the current verifier, **26/26**.

One earlier complete-registry invocation was terminated by the cloudtainer's
outer command window after 141 successful results and before CTest emitted a
terminal result. It is retained only as an interrupted observation, not counted
as a pass or a product failure. The scheduler-policy test then passed alone, and
the complete 213-test registry passed in a fresh final invocation. The final
all-target Debug dependency-closure rerun reported no work. Exact logs,
toolchains, parent verification, changeset, active projection, and package
claims are bound in `RELEASE_GATE.json` and
`REVISION_EVIDENCE/rev0894/validation/VALIDATION_SUMMARY.json`.

## Explicit nonclaims

Rev0894 does not provide a production daemon, defense against noncooperating
same-UID or privileged writers, universal NFS/SMB/FUSE lock semantics,
filesystem mandatory locking, fairness, busy-lease retry scheduling, disk-space
reservation, reachability ownership, garbage collection, an indexed fast path,
cross-resource atomicity, exactly-once network delivery, signed local-store
provenance, streaming/chunk trees, hash agility, at-rest encryption, anonymity,
unlinkability, endpoint hiding, traffic-analysis resistance, Windows runtime
coverage, external build provenance, or formal proof.

Mixed-version coexistence is durably refused, but rev0894 does not implement the
offline migration itself. An operator must stop every legacy writer, verify the
root against the rev0893 full-scan oracle, and deliberately migrate the identity
generation before the existing content can be adopted by rev0894.

Every snapshot and put still performs an O(total indexed bytes) scan and hash.
That is intentional: this owner remains the full-scan oracle. A future indexed
production owner should be separate and continuously differentially checked
against it.

## Next high-value milestone

Compose the causal SQLite owner, durable payload store, authenticated TLS
transport, receiver effect owner, and terminal receipt path into the shipped
executable's sole replica authority. In parallel, design explicit content
reachability and garbage collection, then add an indexed catalog under the same
writer lease and test it against the full-scan oracle.
