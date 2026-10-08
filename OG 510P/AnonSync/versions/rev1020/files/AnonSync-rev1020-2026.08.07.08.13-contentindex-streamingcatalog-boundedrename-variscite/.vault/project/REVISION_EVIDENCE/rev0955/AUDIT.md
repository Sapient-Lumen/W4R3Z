# Rev0955 implementation and audit record

## Mission boundary

The shipping objective remains replacing Resilio Sync in a named real workflow,
not building a second synchronization framework. Rev0955 stays inside the
existing C++ payload-store and linked-peer service spine. Direct, Tor, and I2P
remain routes into one authenticated reconciliation semantics.

## Active-source review

The exact parent-to-candidate active projection contains 19 paths: eleven modified,
eight added, and none removed. The patch is retained as
`SOURCE_DIFF_rev0954_to_rev0955.patch`. The new computation and record grammars
are narrow linked leaves rather than parsers embedded further into the large
payload-store owner:

- `resumable_sha256` owns provider-independent SHA-256 continuation;
- `sync_posix_regular_file_snapshot_codec` owns the canonical eleven-field POSIX
  observation encoding and validation shared by both durable metadata records;
- `sync_replica_file_payload_scrub_state` owns fixed-size framing, checksum,
  store-identity binding, fair continuation, and mismatch evidence; and
- the existing payload store remains the only rooted namespace, lease,
  publication, snapshot, mutation, and extraction authority.

## Defects found and corrected

Review and compiled regressions cover several defects that would otherwise have
survived a superficially successful implementation:

1. A one-entry cyclic scrub could republish an invalid cursor and reread the
   same prefix after every restart. New-cycle entry now clears the prior cursor.
2. Best-effort durable mismatch-record loss could restore warm metadata
   acceleration. An independent process-local witness keeps exact-digest access
   fail-closed until a current complete-byte or absence proof clears it.
3. That first witness owned both digests as heap-allocating strings and advanced
   its revocation epoch before allocation was guaranteed. Memory pressure could
   lose the exact blocking target at the safety boundary. Fixed inline digest
   arrays and a compile-time nonthrowing retention path now make witness and
   epoch publication indivisible with respect to allocation failure.
4. Retaining that fixed witness only in the caller's typed-error catch was still
   too late: failure-record serialization or typed exception construction could
   allocate after current bytes mismatched but before revocation. Fixed-width
   SHA finalization now installs the witness at the exact comparison cutpoint,
   and an allocation-fault sweep proves every later failure escapes instead of
   becoming an optional scrub deferral.
5. A live writable snapshot issued before corruption retained metadata-only and
   rooted methods after repair. A non-wrapping owner-local integrity epoch now
   permanently revokes that capability; only a new leased scan can issue a
   replacement snapshot.
6. The new revocation epoch is intentionally mutex-free, but metadata-only
   snapshot methods initially read it without proving exact-thread ownership.
   Centralized snapshot and targeted-access gates now perform the cheap directory
   authority owner/thread proof before any cache read.
7. A provisioning proof first confused authenticated listener readiness with
   local owner-only status-socket readiness, then carried its repaired startup
   witness across a bounded convergence wait inside nearly the same service
   runtime horizon. Loaded validation could observe orderly socket removal before
   drain. The harness now proves startup endpoints, uses a bounded 60-second
   lifetime, and re-proves the live exact nonsymbolic mode-0600 source socket at
   the post-convergence drain cutpoint.
8. The full sanitizer network-model corpus inherited an unqualified generic
   timeout. Its measured frontier now matches the existing heavy graph oracle;
   coverage was not deleted or weakened.
9. The native-I2P negative-control oracle allowed only three seconds for local
   repair plus connector scheduling. Under concurrent compilation it could stop
   before pull began and omit reconciliation evidence. The bounded test horizon
   is now eight seconds with a 15-second process guard, while an actual failed
   reconciliation and no completed direct handshake remain mandatory.
10. Current handoff prose repeatedly called `ReadOnlyInspect` “byte-cold,” even
    though its deliberate forensic contract bypasses both verification caches
    and hashes every payload byte on every complete scan. The current README,
    restart page, rev0955 notes, and scrub audit now use “acceleration-cold” and
    state the byte-verification behavior explicitly. The structural tripwire is
    bound to the compiled repeated-inspection hash counters so this terminology
    cannot drift back into an operationally false cost claim.
11. The first release-evidence pass retained a source patch generated before the
    final provisioning tripwire was strengthened. The active-file inventory was
    still correct, but replaying the patch reconstructed only 18 of 19 final
    files exactly. The patch was regenerated from the verified rev0954 parent;
    an isolated apply-and-byte-compare proof now reconstructs all 19 active
    rev0955 files exactly.

The final structural audit is recorded by the validation summary. It is a
source-shape tripwire, not a substitute for compiled tests, sanitizers, or
release-package verification.

## Authority and nonclaims

The durable scrub record is scheduling evidence, not payload truth. Its checksum
is not a MAC, `flock(2)` is advisory, and same-UID or privileged hostile writers
remain outside the claim. A digest resumed across restart-separated ranges is
not a point-in-time snapshot; a completed mismatch therefore raises an alarm
whose witness forces a current full-file reproof. Detection is rotating rather
than instantaneous, and there is no coverage-age service-level objective.

Rev0955 does not add retention/restore/garbage collection, reachability pins,
block-level changed-file reuse, rename identity, directories, selective sync,
many-share supervision, cross-platform qualification, or the first measured
Resilio uninstall workload.
