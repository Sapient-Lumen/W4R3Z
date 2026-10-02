# ADR 0324: Supersede unfinished authority rounds

- Status: accepted and implemented
- Date: 2026-09-03

## Context

Authority is directional. After a local ledger mutation, the verifier invalidates every proof bound
to the prior exact head and sends a fresh challenge. The claimant originally accepted that newer
challenge only after its proof for the prior head had reached the local toxcore send queue.

The recovery rehearsal exposed a valid ordering that violates that timing assumption. A full-mesh
share can grant two peers in quick succession. The second durable grant advances the verifier's
ledger again while one claimant is still preparing or enqueueing its proof for the first grant. On a
slower two-vCPU VM, the claimant treated the second challenge as conflicting and remained poisoned
for that online epoch. The verifier then waited forever for a proof to its current head. One node
retained only its own branch while the other two exchanged with each other.

Reconnection happened to repair the condition, but requiring it would make an ordinary sequence of
authorized mutations timing-dependent and leave synchronization liveness to an unrelated transport
event.

## Decision

A structurally valid challenge may supersede an unfinished frozen claimant round when all of these
conditions hold:

- it belongs to the same confirmed online-session transcript;
- it names the same verifier stable-device principal;
- its authority-ledger format is equal or newer, never a downgrade; and
- its `(ownership epoch, sequence)` is strictly newer.

The claimant discards the prior frozen challenge and any prepared proof, then signs only the exact
successor challenge. Byte-identical repetition remains idempotent. A changed challenge at the same
or an older authority head, verifier replacement, transcript change, or format downgrade remains a
protocol conflict. The verifier still checks the proof against its exact current local ledger, so a
claimant signature over an invented future head cannot authorize an effect.

The existing ledger-mutation owned test now injects a second grant after challenge receipt but
before proof preparation. It requires successor adoption and exact authorization, then verifies
that a nonce change at the same head is still refused. The registry remains 831 checks.

## Consequences

Consecutive grants, revocations, or other legitimate forward ledger mutations no longer require a
disconnect to repair an in-flight proof round. This changes state-machine acceptance, not authority
framing or the signed proof format.

A clean replacement 2-vCPU/2-GiB Sandwurm run crosses the original rapid-grant boundary, survivor
restart/re-proof, one-node replacement, complete live-node loss, and a final fresh six-edge mesh. It
completes the recovery phase in 97.238 seconds with no authority session left awaiting proof. This
system result complements the deterministic registry test; it does not exhaust every schedule.

It does not add a proof-verification receipt, live clone lease, trusted clock, remote ledger
attestation, or availability guarantee. A malicious connected peer can already disconnect or send a
conflicting challenge; accepting a higher head does not grant that peer a capability on this
device. Exact-head verifier checks remain the effect boundary.
