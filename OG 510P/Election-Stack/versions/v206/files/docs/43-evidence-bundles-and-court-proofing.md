# 43 — Evidence bundles and court-proofing (operational)

**Track:** A (Deployable core)


This document defines the operational requirements for producing evidence bundles that remain verifiable under adversarial conditions (including litigation and disinformation campaigns).

## Requirements

- Evidence MUST be content-addressed and immutable once published.
- Evidence MUST be signed by multiple roles (at minimum: log operator + witness quorum).
- Evidence MUST be mirrored by independent parties.
- Evidence MUST be publishable in “offline” form (USB / DVD / printed hashes) for courts and observers.

## Bundle contents (minimum)

1. Election parameters: ballot definitions, crypto policy, trustee roster, witness policy
2. PBB artifacts: STH sequence, checkpoints, inclusion/consistency proofs
3. Tally artifacts: shuffle proofs or homomorphic proofs; threshold decryption proofs
4. Revocation and eligibility artifacts: public revocation set; token policy
5. Audit artifacts: RLA seed selection transcript; sample list; discrepancy logs
6. Verifier artifacts:
   - VerifierReports (tool identity + conformance) from at least two independent implementations
   - PacketVerificationReports (bundle-scoped pass/fail + reason codes) for the shipped evidence packet(s)

## Publication schedule

- Publish periodic witness checkpoints during voting (cadence defined in policy).
- Publish close-of-polls final checkpoint.
- Publish tally proof bundle.
- Publish audit bundle(s) as available.

See also: `docs/211-court-evidence-bundle-recipes.md` for **bounded, claim-first** bundle recipes aligned to the catastrophe ordering.


## Schemas

- `schemas/EvidenceBundleManifest.json` — the manifest is the root of the bundle.