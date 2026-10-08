# 40 — Vote buying and pattern attacks against E2E systems

**Track:** B (Remote return / hard-mode research)


**Human framing:** coercion is not only a crypto failure mode; it is a lived experience of fear and dependency.
If this risk matters in your jurisdiction, read `07-coercion.md` before choosing publication granularity or protocol mitigations.



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

End-to-end verifiability (E2E) improves detectability of outcome manipulation, but does **not** automatically prevent:
- vote buying
- coercion
- pattern attacks (e.g., “Italian” attacks), especially when detailed tallies are published

This document consolidates defenses and the “do not claim” boundaries.

## Threats

### T1 — Receipt-as-proof
Attackers try to convert a receipt or tracker into a **transferable proof** of vote choice.

### T2 — Pattern attacks via outcome disclosure
If the system publishes granular results (precinct-level, batch-level, or round-by-round for ranked-choice), a coercer can require a unique vote pattern and verify it statistically.

### T3 — Assisted voting misuse
Accessibility helpers, family members, or “vote assistance” services can become coercion channels.

## Defensive principles

1. Receipts MUST be **non-transferable** and MUST NOT encode vote content.
2. Published results MUST be bounded by a pre-committed **DisclosurePolicy**.
3. Provide an **escape hatch**: supervised override or in-person fallback.

## Normative requirements

### Receipt safety
- Receipts MUST enable “recorded-as-cast” checking without revealing vote content.
- The system MUST NOT provide any feature that outputs a vote-encoding string (including QR codes) that could act as a receipt.

### Tally disclosure policy (required)
- Before ballots are cast, election officials MUST publish a DisclosurePolicy stating:
  - what breakdowns will be published (jurisdiction/precinct/batch)
  - minimum cell sizes (k-anonymity thresholds)
  - whether intermediate tallies will be published
- The system MUST enforce the DisclosurePolicy in the official publication pipeline.

### Tally hiding (recommended for high-risk contexts)
For elections susceptible to coercion/vote buying:
- Prefer publishing only totals/winners unless the disclosure policy allows more.
- Consider risk-limiting / masked publication techniques where appropriate.

### Accessibility and assistance
- Assisted voting flows MUST be designed so the helper cannot obtain transferable proof.
- Consider supervised accessible kiosks as an alternative to unsupervised remote assistance.

## Evidence artifacts

- `34-tally-hiding-and-pattern-attacks.md`
- `schemas/EvidenceBundleManifest.json` (publication is signed and content-addressed)
