# ADR 0307: Witness signed route generations

- Status: accepted and implemented for the opt-in route-policy lane
- Date: 2026-09-02

## Context

IoTox already requires a stable-device-signed route-set artifact and keeps a separately signed
generation high-water checkpoint. That prevents ordinary rollback of only the artifact or only the
checkpoint. A complete filesystem snapshot can restore both valid files together, however, and can
therefore resurrect an old Tor/I2P/native topology, old route membership, or old capacity and
restart limits while the authority and session-incarnation witnesses remain current.

Route policy has a closed adoption boundary before route workers and RuntimeTree construction. Its
generation plus artifact digest form a natural externally witnessed head, but the shared witness
protocol accepts only exact one-step transitions. Allowing route generation gaps would make omitted
history indistinguishable from an intentional jump.

## Decision

Add the closed `route-generation` witness lane. A quiescent device-signed enrollment command reads
and verifies the current route artifact and any local high-water record without mutating either. It
enrolls the reviewed artifact's generation and digest, including when that exact artifact has not
yet been copied into the local checkpoint.

With `--witness-route-generation`, startup must authenticate that separately enrolled lane before
constructing routes. An artifact equal to the committed external head verifies or repairs a missing
or strictly older local checkpoint. Any later artifact must be exactly generation
`committed + 1`. Adoption performs:

1. verify the signed artifact and local signed checkpoint under the existing exclusive lock;
2. write and fsync a fixed device-signed intent containing both external heads, transaction nonce,
   and exact next 152-byte signed checkpoint;
3. external CAS from committed to pending;
4. atomically install and re-read the exact local checkpoint;
5. external CAS from pending to committed; and
6. fsync-unlink the intent.

Pending recovery requires the exact intent and exact signed next artifact. The local checkpoint may
be the exact old or new side (or absent); recovery installs the bound next checkpoint and completes
forward. Ambiguous CAS replies are resolved by authenticated query. A committed-next witness plus
retained intent repairs only the exact intended local state. Foreign selectors, missing pending
intent, forked digest, stale generation, deletion of required artifact, or an unrelated checkpoint
fail closed.

`--route-witness-intent` is optional and otherwise derives beside the route-generation state. The
lane reuses the ADR 0305 endpoint, pinned service key, create-once domain, epoch, and device request
signer, but it has an independent no-replace service enrollment and record. Configuration
commitment v4 records only whether the lane is enabled.

## Consequences

Four owned checks bring the direct registry to 776. They cover enrollment/adoption, sequential
advance, complete two-file rollback, skipped-generation refusal, same-domain-backend refusal,
interrupted-final-CAS recovery, CLI enrollment, and an actual authenticated TCP service advance.

The retained two-guest gate enrolls route generation one, starts the source-linked Agent with all
four current lanes, replaces the reviewed artifact with generation two, and commits it. It then
restores both valid generation-one route files while the witness remains at two and requires failure
before RuntimeTree. The two guests still share a physical/admin failure domain.

Route authoring remains deliberately offline and no-replace. Operators must create the next
artifact at a new path, review it, and atomically place it at the configured route path. A generation
gap must be re-authored; there is no bypass flag or counter reset. Terminal profiles/bindings, sync
policy/state, update state, and command-effect identity still need their own transaction designs.

