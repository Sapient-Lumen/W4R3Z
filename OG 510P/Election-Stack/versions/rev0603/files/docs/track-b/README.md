# Track B — Remote Return / Hard-mode Research Annex

**Track:** B (Research annex)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](../167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](../229-experiment-to-spec-promotion-protocol.md).

## Quick navigation
- [Curated bundle](BUNDLE.md)

This track contains research on remote ballot return / online interaction surfaces.
It is intentionally separated so the archive never “accidentally” over-claims what
is safe to deploy.

## Core posture (research statements + explicit non-claims)

Canonical statement of claims/non‑claims:
- `../166-scope-and-claims-contract.md`
- `../167-non-claims-and-boundaries.md`

**Read `167` N‑2 (coercion) before reading any Track B protocol spec.**

Track B documents must include:
- explicit non‑claims,
- scoped threat model,
- what evidence would upgrade a statement to conditional/hard,
- abuse cases (“how this could go wrong socially”).


Track B **does not claim** to solve:
- coercion
- malware on voter devices
- large-scale disruption by capable adversaries

Track B is about tightening evidence, constraints, and assumptions so that if remote return is used
in limited contexts, failures become **loud and provable**.

## Recommended read order
1. `../154-project-scope-and-track-map.md` (Track B assumptions)
2. `../07-coercion.md` (why this track is hard)
3. `../06-client-security.md`
4. `../03-protocol-spec.md` (remote surfaces in context)
5. `../110-outage-attestations-and-probe-corroboration.md` + `../115-unreachability-proofs.md`

## What we want from Track B
- Honest boundaries: every major claim is linked to a Proof Obligation + hazard.
- A clear ethics posture and stakeholder impact analysis for any field experiments.
