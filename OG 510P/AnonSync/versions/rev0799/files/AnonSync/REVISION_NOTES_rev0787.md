# AnonSync rev0787 — sealed peer-ingress connection profile

Parent: `AnonSync-rev0786-2026.07.14.14.41-observed-sqlite-mutex-generation-capabilityfenceforge.zip`  
Prepared: `2026-07-14T17:22:58.375484-04:00`

## Mission boundary

The transition being hardened is **SQLite connection publication**. Requested flags and a successful
`sqlite3_open_v2` call are not evidence that the resulting handle has the authority the caller believes
it has. Peer-ingress now opens a private candidate, pins the selected VFS by concrete name, observes the
main schema's actual read-only state and VFS stack, and publishes the handle only after those observations
match the request.

## Implementation

- Added `src/persistence/peer_ingress_connection_profile.*` as the sole first-party raw-open boundary for
  `src/sync_domain.cpp`.
- Routed 65 peer-ingress open call(s) through the signature-compatible verified wrapper.
- Added post-open access-mode evidence via `sqlite3_db_readonly` and VFS evidence via
  `SQLITE_FCNTL_VFSNAME`.
- Added a non-copyable, non-movable operation-scoped busy-handler guard. It deliberately does not claim to
  restore an unknowable previous callback; reset clears the callback and therefore must be used only while
  the connection's existing generation/operation mutex is held.
- Added a standalone adversarial test and a source-level authority audit.

## Audit finding

The lifecycle unit remains structurally expensive at 24529 lines. This revision does not
perform a cosmetic split. It removes one authority-bearing responsibility—connection opening and
post-open attestation—into an invariant-owned module. Remaining direct busy-handler call sites are recorded
for a later operation-scope migration because mechanically rewriting callback lifetime would be less safe
than leaving explicit debt.

## Primary references

- SQLite C API: Opening A New Database Connection (`sqlite3_open_v2`)
- SQLite C API: Determine if a database is read-only (`sqlite3_db_readonly`)
- SQLite file-control opcode: `SQLITE_FCNTL_VFSNAME`
- SQLite C API: Register a callback to handle `SQLITE_BUSY` errors
- SQLite threading modes and `SQLITE_OPEN_FULLMUTEX`

The evidence directory records exact commands, exit codes, source metrics, and package verification.
