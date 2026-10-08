# FT-0075 closure — transparency trust-policy lifecycle

FT-0075 asked whether TimeSync should represent transparency trust-policy expiry, revocation, retirement, and drift explicitly, or leave them entirely to external local policy.

rev0076 closes the ticket by adding explicit lifecycle summaries while keeping policy repositories and trust frameworks out of TimeSync.

## Decision

Add `lifecycle_status` to `transparency_trust_policy_reference`.

Add `policy_lifecycle_equivalence` to `transparency_policy_equivalence` inside profile compatibility statements.

## Boundary

Lifecycle metadata is digest-bound review metadata. It can constrain whether replay visibility is current, historical, contested, or unknown. It cannot update TimeState, profile conformance, validity horizon, current actionability, source diversity, traceability, verifier authorization, or TimeSync provenance.

## Validator-backed outcomes

rev0076 rejects:

- expired policy reference treated as current replay visibility,
- revoked policy reference treated as current replay visibility,
- unknown or unchecked drift treated as current replay visibility,
- digest rollover without compatibility-backed equivalence,
- expired or drifted compatibility policy-lifecycle equivalence treated as current.
