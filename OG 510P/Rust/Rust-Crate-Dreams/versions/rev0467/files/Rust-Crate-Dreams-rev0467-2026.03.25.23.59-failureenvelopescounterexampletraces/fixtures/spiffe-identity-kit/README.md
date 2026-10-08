# spiffe-identity-kit fixtures

These fixtures keep **P-0134 spiffe-identity-kit** grounded in reviewable, non-magical support objects.

The point is not to model every SPIFFE/SPIRE deployment.
The point is to keep a few dangerous collapses from re-entering future archive passes:

- live Workload API identities versus static/dev identities,
- bundle-set-wide federation acceptance versus narrowed trust-domain policies,
- verifier-only identity checks versus application-visible peer-identity handoff,
- and vague “automatic rotation” claims versus explicit fresh-handshake / source-loss posture.

Core schemas:
- `identity-source.receipt.schema.json`
- `trust-domain-policy.receipt.schema.json`
- `peer-identity.receipt.schema.json`
- `rotation-state.report.schema.json`
