# AnonSync rev0769 — connection incarnation and cohost authority manifest fence

## Mission boundary

AnonSync treats transport, callbacks, and process-local object identity as observations rather than authority. A state transition is authorized only by durable, generation-specific, content-bound evidence that remains reconstructible after interruption. This revision tightens the SQLite-side capability boundary: a raw `sqlite3*` address and a mutable schema cookie are not identities.

## Recovered implementation direction

The unfinished predecessor work was retained and reconciled rather than replaced. It separates three concepts that were previously liable to collapse into one another:

1. **Connection incarnation** — a non-reusable logical lifetime for one opened handle, independent of allocator address reuse.
2. **Authorizer generation/ownership** — the currently installed policy instance; alien replacement, disablement, or stale generation is not silently accepted.
3. **Canonical bounded container manifest** — exact normalized authority-bearing metadata for the full SQLite container, not just an optimistic `schema_version` observation.

Peer-ingress attestation must bind recognized cohost authority metadata as well as DDL. Unknown or over-budget metadata is a fail-closed condition, because omission would turn the manifest into an allow-list bypass.

## Audit findings

- Pointer-keyed capability registries have a classic ABA exposure: close and reopen can reuse an address while stale process-local state survives.
- SQLite exposes one authorizer callback slot per connection. A later caller can replace or disable it; therefore successful installation is not durable evidence of continued ownership.
- `PRAGMA schema_version` is an optimization cookie, not a collision-resistant container identity. A snapshot hash must cover canonical rows and limits, and verification must occur at the authorization boundary.
- Cohost tables/triggers/views can alter effective authority even if AnonSync-owned DDL is unchanged. Exact recognized metadata belongs in the attestation input.
- The lifecycle/domain translation unit remains a concentration risk. This revision keeps connection fencing and manifest construction independently testable so their invariants do not require repeated recompilation of the monolith.

## Refactor boundary

Connection-capability ownership and manifest canonicalization are separate modules/tests. The peer-ingress layer consumes their typed results; it must not recreate token comparison, pointer maps, SQL normalization, or truncation policy.

## Speculative next steps

- Replace all remaining process-local connection registries with scoped RAII registrations whose destructor invalidates the incarnation before `sqlite3_close`.
- Add deterministic fault points around open/register/install/probe/attest/commit/close and compare restart traces with an executable state-machine oracle.
- Bind the container manifest to the durable payload receipt and claim generation, producing one evidence envelope rather than adjacent booleans.
- Consider a monotonically allocated, random-salted 128-bit incarnation token if in-process monotonic counters can be restored from snapshots or crossed through FFI.
- Add a manifest format version and explicit domain separators before any hash input becomes externally persisted.

## External design references

- SQLite C interface: `sqlite3_set_authorizer` — https://sqlite.org/c3ref/set_authorizer.html
- SQLite pragma semantics: `schema_version` and `data_version` — https://sqlite.org/pragma.html
- SQLite schema table representation — https://sqlite.org/schematab.html
- CWE-367 (time-of-check/time-of-use), useful as a broad taxonomy rather than an exact diagnosis — https://cwe.mitre.org/data/definitions/367.html

## Source selection

- Baseline archive: `AnonSync-rev0769-2026.07.13.16.30-connection-incarnation-cohost-authority-manifestfenceforge.zip`
- Selected recovered tree: `/mnt/data/_rev0769_finish/extracted/AnonSync-rev0769`
- Selection score: `18061`
- Pre-validation source bytes: `14316292`

See `evidence/rev0769/` in the packaged revision for exact commands, logs, scans, checksums, and gate status.
