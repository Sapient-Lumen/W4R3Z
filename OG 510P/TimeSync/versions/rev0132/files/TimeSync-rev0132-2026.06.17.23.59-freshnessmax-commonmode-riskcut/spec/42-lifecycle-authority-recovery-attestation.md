# 42. Lifecycle-authority recovery attestation boundary

Normative in rev0079.

## Purpose

rev0078 allowed a lifecycle-authority compromise response to be summarized as unresolved, contained, historical, contested, or unknown, but it did not provide a compact way to bind a contained compromise to a recovery statement. rev0079 adds a digest-bound recovery-attestation reference so a receiver can distinguish recovered-current replay visibility from historical-only or contested replay visibility without importing incident-response records.

## Object placement

A recovery attestation reference appears under:

`transparency_trust_policy_reference.lifecycle_authority_reference.rotation_delegation_status.compromise_response.recovery_attestation_reference`

It may also be returned by discovery as `policy_lifecycle_authority_recovery_attestation`.

It is not part of TimeState, profile assessment, evidence-summary input evidence, transport metadata, or profile compatibility negotiation.

## Required boundary

A recovery attestation reference is summary-only and digest-bound. It records:

- affected lifecycle-authority digest,
- recovery or successor authority digest,
- compromise-response digest,
- recovery-attestation digest,
- bounded incident-window posture,
- replay-visibility effect,
- portability posture.

It must not export authority key material, authority rosters, delegation chains, incident forensics, legal-authority detail, external incident records, policy repositories, status endpoints, trust anchors, witness/monitor rosters, verifier identities, salts, preimages, gossip transcripts, or external provenance semantics.

## Replay-visibility effects

`recovered_current` means the contained compromise has a current, digest-bound recovery attestation whose incident window is bounded and whose attestation status is current.

`historical_only` means the replay event may remain reviewable as historical replay visibility, but cannot be treated as current replay visibility.

`contested_visibility` means the compromise response or recovery posture is still disputed or under review.

`unknown` cannot support current replay visibility.

## Current replay visibility rule

If `anchor_evaluation.current_visibility_status` is `current_at_evaluation` and lifecycle-authority compromise state is `confirmed_contained`, then:

- `compromise_response.replay_visibility_effect` must be `recovered_current`,
- `recovery_attestation_reference` must be present,
- `recovery_attestation_reference.attestation_status` must be `current`,
- the incident window must be bounded,
- affected authority, recovery authority, and response digests must match the compromise response,
- portability must be same-operator or compatibility-statement bound.

Historical-only or contested recovery posture cannot be promoted to current replay visibility.

## Cross-operator portability

A recovery attestation is same-operator by default. Cross-operator use requires `portability.operator_scope: compatible_operator_bound` and a `compatibility_statement_digest`. This digest only authorizes replay-visibility interpretation of the recovery-attestation reference. It does not equate incident forensics, authority rosters, key material, legal authority, policy language, profile evidence, or provenance.

## Validator coverage

The rev0079 validator rejects:

- contained compromise without `recovery_attestation_reference`,
- current replay visibility with historical-only or contested recovery posture,
- recovered-current posture with expired, revoked, unknown, or under-review attestation status,
- open or unknown incident windows for recovered-current posture,
- recovery/compromise digest mismatch,
- cross-operator recovery portability without compatibility-statement digest,
- incident-forensics/key/roster/delegation/legal detail export,
- recovery-attestation evidence classes used as profile-obligation evidence,
- malformed discovery-returned recovery attestation references.
