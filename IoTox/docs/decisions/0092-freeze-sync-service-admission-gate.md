# ADR 0092: freeze synchronization service admission before transport

- Status: accepted and implemented as a pure gate
- Date: 2026-08-20
- Scope: authorization immediately before a synchronization effect is admitted
- Depends on: authority-ledger v3, ADR 0091, canonical namespace policy

## Context

Authority-ledger v3 answers whether a freshly proven principal possesses one synchronization right.
The local namespace record independently answers which stable principals may write or subscribe and
whether activation is enabled. Either answer alone is insufficient. Deferring their composition until
network handlers exist would invite friendship shortcuts, stale-proof reuse, or inconsistent checks
between control, protocol, and worker entrances.

## Decision

1. Every synchronization service entrance evaluates one common admission primitive immediately
   before it admits work. Callers serialize that evaluation with any concurrently exposed authority
   or namespace-policy replacement.
2. All operations require a valid canonical namespace policy, an initialized v3 ledger, a connected
   and authorized directional proof negotiated with both the v2 lineage and v3 feature, and an exact
   match to the current local format, ownership epoch, sequence, and tail digest.
3. Operations map to exactly one capability:

   | Operation | Capability | Additional namespace constraint |
   |---|---|---|
   | administer | `sync.admin` | proposed/existing policy must be valid |
   | publish | `sync.publish` | proven principal is an exact writer |
   | subscribe | `sync.subscribe` | proven principal is an exact subscriber |
   | activate | `sync.activate` | proven principal is an exact subscriber and mode is `manual` |

4. Capabilities do not substitute for one another. Membership cannot substitute for a capability,
   and capability possession cannot substitute for membership or host activation policy.
5. The gate returns a bounded content-free decision name and the required capability. It does not
   mutate policy, accept a HEAD, reserve storage, install bytes, or activate content.
6. No sync packet family or service entrance is allocated by this decision. When those entrances are
   added, tests must show they cannot reach an effect without this gate.

## Consequences

- The security composition is executable and directly testable before transport complexity arrives.
- V1/v2 ledgers, stale or denied proofs, wrong principals, disabled activation, malformed policy, and
  unknown operations fail before effect admission.
- Namespace administration deliberately does not require writer/subscriber membership: it governs
  the local policy that defines those sets and instead requires `sync.admin` plus a valid resulting
  policy. The durable local mutation ceremony remains future work.
- A successful decision is authorization evidence only. All HEAD, signature, linkage, quota,
  filesystem, cancellation, and atomic-transaction checks remain mandatory at their own boundaries.

## Rejected alternatives

### Treat owner status or friendship as sufficient

Rejected because neither transport friendship nor an implicit owner shortcut grants a v3 sync bit or
binds the request to the current signed head.

### Use one aggregate synchronization capability

Rejected because publication, convergence, activation, and policy administration have different
effects and were deliberately allocated as independent durable rights.

### Put writer/subscriber membership in the signed ledger

Rejected because namespace topology and host-local storage policy change independently of global
principal delegation. Requiring both stores limits compromise instead of making either one ambient
authority.
