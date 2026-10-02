# ADR 0091: reserve synchronization authority without widening v2

- Status: accepted and implemented by authority-ledger v3
- Date: 2026-08-20
- Scope: durable capability allocation for integrated IoTox synchronization
- Preserves: authority-ledger v1 and v2 byte and policy contracts

## Context

Integrated synchronization needs four distinct decisions: administering local namespace policy,
publishing a signed revision, subscribing to a remote namespace, and activating locally verified
content. Friendship, Tox file acceptance, writer pinning, owner status, Ratox terminal authority, and
the historical `install.firmware` capability do not imply any of those rights.

Authority-ledger v2 deliberately recognizes only bits 0 through 7 and rejects every unknown bit. Its
documented mask is exactly `0xff`; its signed migration adds only `interactive.terminal`; and its
source-level `all` remains the v1 mask forever. Reinterpreting bits in v2 would make old binaries reject
new valid records, make the same format byte mean different policy on different releases, and violate
the explicit non-widening migration contract.

## Decision

1. Reserve the following durable capability names and bit positions for the next authority-ledger
   format that implements synchronization:

   | Bit | Name | Meaning |
   |---:|---|---|
   | 8 | `sync.admin` | install, replace, or remove host-local namespace policy |
   | 9 | `sync.publish` | request creation and advertisement of a signed namespace revision |
   | 10 | `sync.subscribe` | request metadata/object convergence from an authorized writer |
   | 11 | `sync.activate` | request the explicit local switch to an exact verified accepted revision |

2. Do not add these bits to `AuthorityLedgerFormat::v2`, `kAuthorityV2Capabilities`, `all-v2`, any v2
   role ceiling, v2 parsing/rendering, feature bit 24, or any existing record. A v1 or v2 ledger cannot
   authorize integrated synchronization.
3. The future format transition must be signed, replayable, one-way, non-widening, and covered by the
   rollback guard. Migration preserves every active principal's exact capability mask. A separate later
   grant is required before any principal, including an owner, receives a synchronization bit.
4. `all` permanently remains the v1 mask and `all-v2` permanently remains the v2 mask. The future
   format receives its own explicit aggregate spelling; recompilation must never silently widen an
   existing source-level grant.
5. Keep the four rights independent. In particular, `sync.subscribe` may admit bytes to a bounded
   private store but grants neither `sync.activate` nor `install.firmware`; `sync.publish` grants no
   local policy administration; and `sync.admin` does not imply publication or activation.
6. Namespace writer/subscriber lists remain a second mandatory local constraint. A principal must pass
   both the exact-head authority-ledger capability check and the namespace policy check. Neither check
   substitutes for the other.
7. Activation must additionally name the exact currently accepted HEAD and pass the host-local
   activation mode and verified-object transaction. A capability authorizes a request, not its effect.
8. Authority-ledger v3 implements this allocation through feature bit 25 and signed action
   `migrate-v3`. Its exact format, role ceilings, ceremonies, compatibility checks, and nonclaims are
   frozen in `protocol-authority-v3.md`.

## Consequences

- The numeric allocation is no longer ambiguous, and no historical capability is overloaded.
- Current v2 peers continue to reject sync bits exactly as documented.
- The local namespace, HEAD, install, and activation primitives can mature independently while network
  synchronization remains impossible to authorize accidentally.
- The first networked vertical slice depends on a reviewed next authority-ledger format; it may not
  bypass that dependency with owner-only shortcuts or friendship-derived authority.

## Rejected alternatives

### Extend the meaning of authority-ledger v2

Rejected because v2's exact `0xff` mask and unknown-bit rejection are durable compatibility and
security contracts.

### Reuse `install.firmware`

Rejected because ordinary file synchronization is not firmware installation, and receiving,
publishing, administering, and activating are separate powers.

### Treat namespace membership as sufficient authority

Rejected because host-local namespace policy is a constraint and routing configuration, not signed
delegation history. Compromise or misconfiguration of one file must not manufacture ledger authority.

### Give owners implicit synchronization rights

Rejected because migration must not widen any principal. Explicit grants preserve reviewable intent
and match the v2 terminal precedent.
