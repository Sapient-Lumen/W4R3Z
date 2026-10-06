# RFC-0135: Secure time bootstrapping (NTS + Roughtime)

Status: **Draft**  
Last updated: 2026-02-24

## Problem

DeriveBSD uses time in multiple security-critical decisions (transparency, anti-rollback, certificate validation, replay artifacts). Classic NTP is not cryptographically protected.

We need a way to:
- obtain time from authenticated sources
- decide “good enough” under policy (quorum + skew bounds)
- record evidence so later verifiers can understand why time was accepted

## Proposal

Introduce an optional lane:
- `time-source-policy` (signed): defines acceptable time sources and decision rules
- `time-proof-bundle` (signed by `system.time`): captures observations + computed agreement
- extend `time-snapshot` with an optional `proof_bundle_digest`

`system.time` is responsible for producing proofs and for enforcing the policy; consumers only need the snapshot and digest.

## Non-goals

- Designing a new time protocol.
- Forcing secure time on all deployments; this is a policy lane.

## Threat model highlights

- MITM time manipulation
- compromised or misconfigured time server
- split-view / equivocation across sources
- attacker-induced time jumps to bypass revocation / expiration / rollback checks

## Data model

See:
- `spec/time.source.policy.schema.json`
- `spec/time.proof.bundle.schema.json`
- `spec/time.snapshot.schema.json` (extended)

## Rollout plan

1) Accept policy + proof bundle as “optional evidence” (verifiers ignore if absent).
2) Allow policies to require proof bundles for selected channels (e.g., `public/stable`).
3) Add UI/ops ergonomics: explain “why time was accepted” (skew, quorum membership).

## Open questions

- Do we require diversity (operator/vendor) in the quorum rules?
- How do we present misbehavior proofs to operators without turning it into an alert fatigue machine?
