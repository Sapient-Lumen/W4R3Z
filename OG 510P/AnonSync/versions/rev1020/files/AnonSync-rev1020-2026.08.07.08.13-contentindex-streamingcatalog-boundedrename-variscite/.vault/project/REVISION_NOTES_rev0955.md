# AnonSync rev0955

Rev0955 adds a durable byte-bounded rotating payload scrub to the shipping C++
payload store. It adds bounded coverage of rev0954's explicit
metadata-preserving-integrity boundary without promoting partial hash state or
checksum-framed scheduling records into payload authority.

## Primary implementation

- Added provider-independent resumable SHA-256 continuation with a canonical
  checkpoint, the exact SHA-256 byte-aligned message ceiling, NIST vectors,
  padding-boundary coverage, restart cutpoints, malformed-state cases, and an
  independent OpenSSL oracle.
- Added `.anonsync-payload-scrub-state-v1`, a fixed-size checksum-framed record
  bound to the exact store identity marker and canonical eleven-field POSIX
  metadata. It persists generation, completed cycles, fair cursor, exact active
  payload/offset/hash state, and terminal mismatch evidence.
- Centralized the eleven-field POSIX metadata projection used by both durable
  v1 records in `sync_posix_regular_file_snapshot_codec`. The shared canonical
  codec preserves the exact 88-byte big-endian layout and owns private mode-0600,
  single-link, timestamp, and optional size-ceiling validation.
- Added strict per-attempt byte and distinct-entry limits. The production helper
  enables 4 MiB and four entries; disabled and asymmetric configurations are
  explicit and validated.
- Runs optional scrub only after the complete shared snapshot lease is released,
  then re-proves root, identity, directory, state metadata, payload descriptor,
  pathname, and exclusive lease cutpoints.
- Keeps scrub reports and state outside canonical snapshot identity. `ReadOnlyInspect`
  remains acceleration-cold, hashes every payload byte during each complete
  forensic scan, and does not advance scrub state.
- Treats torn, malformed, identity-rebound, or stale state as disposable bounded
  work. Product bootstrap rejects a preexisting unbound scrub record.
- Persists an exact mismatch witness when possible and throws a typed integrity
  error without deleting or silently quarantining the sole payload. A matching
  witness forces a current full-byte recheck; repaired bytes clear it without a
  duplicate scrub read.
- Retains an independent process-local fail-closed mismatch witness. Durable
  scrub-record loss or failed publication cannot let an unchanged warm metadata
  generation regain authority; complete scans and mutation preflights hash the
  faulted digest until current good bytes or absence clear it, while targeted
  access rejects that exact digest. Verification-checkpoint publication is also
  suppressed while the witness is live.
- Makes that witness allocation-independent. The first representation stored
  both digests in heap-owning strings and could advance revocation state before
  allocation completed. The final representation uses two fixed inline
  64-character arrays, compile-time nonthrowing optional assignment, and an
  explicitly `noexcept` retention path, so memory pressure cannot discard the
  exact fail-closed target at the mismatch boundary.
- Moves retention to the allocation-free mismatch cutpoint itself. Resumable
  SHA-256 now exposes a fixed-width terminal hex form, the scrubber compares it
  and advances the process witness before assigning durable-state strings,
  serializing the failure record, or constructing the typed integrity exception.
  The optional-attempt catch rethrows every later failure while a witness or
  exhausted epoch is live; post-alarm allocation or publication failure can no
  longer be downgraded to an optional scrub deferral.
- Advances a non-wrapping owner-local integrity epoch on each newly retained
  mismatch and binds every writable snapshot to its issuance epoch. Every
  future method call on a live pre-fault snapshot is permanently rejected—even
  after later repair—and only a newly completed leased scan can issue replacement
  snapshot authority. This closes the metadata-only inventory/digest bypass left
  by the first witness implementation. Values or references already returned and
  already-opened payload descriptors remain explicit non-revocable capability
  nonclaims.
- Process-throttles attempts before lease acquisition so contention or I/O
  failure cannot turn a hot snapshot path into an unbounded retry loop. A fresh
  owner may immediately resume durable progress.

## Audit/refactor

The scrub continuation, binary state grammar, and shared POSIX metadata codec
are independent linked leaves rather than more parsers embedded in the large
store owner. The codec removes duplicate serializer/parser/validator logic from
the verification index and scrub record without changing either v1 layout. The
focused verification-index matrix directly proves exact width, negative-time
round trip, framing rejection, and private-file validation. The leaves are part
of the product target and sanitizer compile inventory; executable tests retain
sanitizer final-link closure. The complete scanner and staged-prefix observer share the
reserved internal-basename policy and final pathname reproof.

The audit found and fixed a severe cyclic liveness defect in the first
implementation. At one-entry wraparound, the old cycle cursor equaled the newly
active digest. Canonical state validation rejected publication, so every fresh
owner could reread the same bounded prefix forever. Entering a new cycle now
clears the old cursor before selecting the first entry; compiled restart tests
prove offsets 10, 20, 30, terminal completion, and next-cycle progress for a
37-byte payload under a 10-byte budget.

The audit also corrected two authority/accounting defects before sealing:
matching persisted failure evidence now reports `failure_persisted=true` only
when the current mismatch exactly reproduces it, and a current full-byte repair
proof is reused to clear failure state without a duplicate scrub read rather
than hashing the same payload twice. A process-local mismatch witness now
survives loss or failed publication of the best-effort durable record. The
exception-safety audit also replaced its heap-owning digest strings with fixed
inline storage and made retention nonthrowing; advancing the integrity epoch can
no longer outrun publication of the exact blocking observation. A second pass
found that this was still too late while retention occurred only after the typed
integrity exception had been constructed: message or digest-string allocation
could fail and fall into the ordinary optional-attempt catch. The final ordering
uses allocation-free hash finalization and retains the witness at the exact
comparison cutpoint. A toolchain-calibrated allocation sweep exercises the
publication/exception tail and proves a persisted or process-revoked alarm never
returns a snapshot as an optional scrub deferral. A regression
deliberately removes the committed record after detection, proves
that both the next snapshot and a mutation preflight still fail closed, repairs
the bytes, and proves that exactly one complete rehash clears the witness.
A second regression proves that an earlier-path mismatch cannot displace an
older unresolved later-path witness; the oldest blocked digest remains
fail-closed until its own current-byte or absence proof completes.
An additional live-capability regression retains a snapshot before an in-place
corruption, proves the complete scanner records the typed process alarm, proves
both metadata-only and rooted methods reject the old snapshot, repairs the bytes,
and proves the old capability remains revoked while a replacement snapshot works.
The adjacent thread-affinity audit then caught a race introduced by that repair:
metadata-only snapshot methods now read the intentionally mutex-free revocation
epoch, but previously had no reason to prove their documented exact-thread
ownership. The centralized snapshot state gate and pass-scoped targeted-access
gate now perform the directory authority's cheap owner-only proof before any
cache read. A foreign-thread canonical-digest regression proves rejection occurs
at that boundary without adding filesystem I/O or a mutex to the normal path.

The process-harness audit found a separate startup-readiness race. The retained
service exposes its authenticated network listener while the configured local
status server is still being constructed. The provisioning proof had treated
listener visibility as authority to issue an owner-only drain and could race a
not-yet-published status socket. The first repair proved the control endpoint at
startup but then carried that witness across a bounded 24-second convergence
wait inside a 30-second service lifetime. Under registry load, orderly runtime
shutdown could remove the socket before the later drain. A centralized helper
now establishes both startup endpoints, the test retains a bounded 60-second
service horizon, and the source status socket is re-proved immediately after
convergence at the drain cutpoint. Each proof requires a live process plus an
exact non-symbolic mode-0600 Unix socket; listener readiness is not control-plane
readiness, and an earlier readiness observation is not durable authority.

The retained I2P-ingress oracle had a separate scheduling-margin defect: its
blocked-direct probe allowed three seconds for the local repair pass and the
connector attempt together. Concurrent compilation could exhaust that horizon
before pull began, yielding `command_deadline_before_pull` with no reconciliation
evidence. The test-only command horizon is now eight seconds with a 15-second
process guard; it still requires an attempted reconciliation, nonzero completion,
and no successful direct TLS handshake. Five consecutive focused repetitions
passed before the final registry reproof.

The sanitizer validation audit found that the generated network model's full
differential corpus completes in about 21 seconds under Clang ASan/UBSan but
inherited a generic 20-second CTest timeout. The corpus was not weakened or
sharded around the failure; its qualified timeout frontier now matches the
existing 60-second graph-oracle frontier and is structurally audited.

The documentation audit also reclassified an unscoped rev0881 ‘largest product
gap’ section as superseded history. It had remained grammatically current long
after the shipping `anonsync_sync` service spine was composed and could steer a
future session back toward solving an already-closed composition problem.

## Exact nonclaims

The scrub state checksum is not a MAC, `flock(2)` remains advisory, and rev0955
is not hostile same-UID writer defense. Detection is rotating rather than
instantaneous; there is no coverage-age SLO yet. A digest resumed across several
attempts is not a point-in-time byte snapshot, so its mismatch is an integrity
alarm whose witness forces one current full-file scanner reproof. A mismatch is
reported and retained, not automatically quarantined or repaired. The complete payload scan
still performs O(total indexed namespace) metadata work.

This revision does not add garbage collection, version retention/restore,
reachability pins, block-level reuse for changed files, rename identity,
directories, selective sync, many-share device ownership, cross-platform
qualification, or a named measured Resilio uninstall workload.

## Validation

Final frozen-source GCC, Clang ASan/UBSan, focused runtime, structural audit, and
wrapper-aware package results are recorded in
`REVISION_EVIDENCE/rev0955/validation/VALIDATION_SUMMARY.json` and the release
gate. See `DURABLE_BYTE_BOUNDED_PAYLOAD_SCRUB_AUDIT_rev0955.md`.
