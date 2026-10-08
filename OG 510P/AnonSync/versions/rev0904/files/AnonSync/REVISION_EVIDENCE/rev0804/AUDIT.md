# Rev0804 audit

## Scope

This revision audited two C++ lifetime boundaries and one build-ownership
boundary:

1. move assignment of process-bound SQLite connection and statement owners;
2. lifetime and generation ownership of peer-ingress schema attestation; and
3. focused build ownership for schema/digest proof code.

## Findings corrected

### Destination-first destruction

Database and statement move assignment could execute destination close/finalize
callbacks before rejecting an inherited or output-pending source. Preserved
executables prove both side effects in the parent revision and their absence in
rev0804.

Correction: complete source preflight, caller-visible source escrow, synchronized
destination-disposal fence, then install. Reentrant and concurrent owner entry
while close/finalize is in progress fails stopped.

### Raw-pointer schema attestation

Schema attestation held no typed owner-generation pin. Owner close succeeded
while the attestation remained live.

Correction: the move-only attestation owns `SyncSqliteSerializedDbBorrow` and
use-time verification matches both handle and generation. Owner close now
fails stopped until the attestation is released.

### Monolithic focused test

The schema test compiled the core monolith and duplicate schema-identity source
ownership remained in CMake.

Correction: digest and schema libraries own their exact translation units;
payload schema proof is separated from data operations; source reabsorption and
core dependencies are rejected by configuration audits.

## Machine-checked audits

- `sqlite_source_first_move.json`: 17/17.
- `peer_ingress_schema_owner_generation.json`: 25/25.
- `sqlite_process_authority.json`: 83/83.

## Residual risks

- Raw SQLite pointer compatibility paths can still create lifetimes outside the
  typed owner graph.
- Fail-stop callback reentrancy is intentional; application destructors must not
  recursively manipulate the owner whose SQLite resource is closing.
- The schema attestation is process-local and non-durable. Restart authority
  must be reconstructed from durable schema evidence.
- In-process hostile-database limits do not replace an OS-contained worker.
- No crash-cut VFS/domain oracle or executable convergence algebra exists yet.
