# ADR 0229: Reuse verified range manifests locally

Status: accepted implementation, deterministic failure coverage, and genuine Sandwurm
qualification, 2026-08-29.

## Context

ADR 0228 closes fail-closed loss and explicit fresh recovery for a concrete I2P range. Its accepted
proof also exposes avoidable work: the failed job had already verified and durably committed the
786,496-byte immutable successor manifest before its range lane was lost, but the fresh job fetched
that exact manifest again before requesting the 1,048,576-byte range. No safety rule requires a
second transport copy when the digest-named local object still proves its signed identity.

## Decision

- Range and whole-object pulls apply the same local reuse rule to every prerequisite they schedule:
  open the exact digest-named object under the namespace transaction, verify its strict shape, size,
  and SHA-256 identity, and mark it committed in the new scheduler only after that proof succeeds.
- A present but malformed object is a hard local failure. The subscriber does not hide corruption by
  asking a publisher to overwrite immutable local truth; repair or quarantine remains explicit.
- The namespace transaction is released before scheduler assignment reserves its durable attempt ID.
  Both use the same non-recursive local lock, so this scope boundary is part of the implementation
  contract and is exercised by the monolithic contamination-oracle test run.
- If range mode reuses its manifest, HEAD-result handling immediately verifies the target and basis,
  prepares the bounded range or whole-object fallback, and returns that request. It no longer waits
  for a network manifest terminal that cannot occur. A locally present target can still complete with
  no transport request.
- `requested` continues to count transport object/range requests, not locally reused objects.
  `committed` continues to count scheduler truth. HEAD acceptance still requires both artifact and
  manifest committed, complete object verification, range-manifest semantic verification, and the
  signed parent/generation checks. Activation remains a separate exact-token operation.
- No peer frame, feature bit, signed record, authority rule, or failed-range cleanup rule changes.

Accepted proof `pair.ip5q0at9` runs clean source revision
`704a3c72fdb7e3e6ef9f05ed12ad12608430e91e` in two simultaneous Sandwurm/KVM guests with identical
binary SHA-256 `3f09780dc67293c7ec62ca2bf55be91d80e6ca8b8ae1964ebac95b4bc4a559a6`.
After a live range reached 71,292 bytes, the client router was replaced over preserved state. The
blocked job was explicitly cancelled and a distinct same-carrier job reported exactly one requested
object and two committed objects, with `manifest_reused_locally=true`. It fetched only the complete
1,048,576-byte fresh range, reused 3,145,728 basis bytes, reconstructed and accepted the exact
4,194,304-byte artifact, and explicitly activated generation 2. Raw and 23,199,744-byte compact
proofs independently pass the strict verifier.

## Consequences

Fresh recovery now avoids 786,496 transport bytes and one complete object-transfer round trip in the
qualified fixture. The prior recovery transported 1,835,072 prerequisite-plus-range bytes; the new
path transports 1,048,576, a 42.86% reduction for that phase. This is a deterministic byte reduction,
not a latency or throughput SLA.

The failed 71,292-byte range prefix is still discarded. This decision does not add same-attempt
continuation, failed-prefix reuse, restart-persistent range staging, cross-carrier striping, implicit
retry, production `tox/i2p`, anonymity, availability, or fleet qualification.

ADR 0230 later qualifies one exact prefix across an ordinary same-job/same-carrier bounded retry.
It does not alter this decision's explicit fresh-job I2P carrier-loss cleanup or nonclaims.
