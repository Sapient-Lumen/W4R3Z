# 009 — Threshold credentials and the death of document copies

**Status:** canon

## Thesis

As digital wallets, mobile credentials, and verifiable-credential standards spread, many institutions will increasingly request **cryptographically verifiable proofs of specific attributes or thresholds** — over 18, licensed, resident, student, policyholder — instead of scans of whole identity documents.
The access primitive shifts from “show me your papers” to “prove this claim.”

## Why it matters

This changes the politics of identity and access.
Many organisations do not actually need a full dossier about a person; they need a trustworthy answer to a narrow question.
If wallets can provide that answer with less fraud and less oversharing, then onboarding, KYC, age gates, service access, and eligibility checks become a new kind of infrastructure.

## Mechanism sketch

- W3C’s Verifiable Credentials 2.0 family now provides a machine-verifiable, privacy-respecting standard with selective disclosure and combination of credentials.
- The EU Digital Identity Framework mandates Member States to provide European Digital Identity Wallets by the end of 2026.
- EU wallet materials already position the system for public administration, banking, education, healthcare, and supplier-legitimacy/KYC use cases.
- The EU’s age-verification manual explicitly describes proving that a user is over a threshold such as 18, 21, or 16 without revealing full birthdate or other excess identifying information.
- NIST’s mDL work treats mobile credentials as cryptographically verifiable, selective-disclosure tools that can serve finance, healthcare, government services, and other online transactions.
- NIST’s digital identity model now explicitly describes subscriber-controlled wallets, pseudonymous identifiers, and derived attribute values as reasons to use federated identity flows instead of copying account values into every application.
- The UK Online Safety Act already creates live legal demand for highly effective age assurance, showing that threshold proofs are not only theoretical.

The deeper pattern is that cheap forgery and data-minimisation pressure now point in the same direction.
Once document images are easy to fake and full-document collection looks excessive, narrower proofs become more attractive than broader identity capture.

## What this speculation predicts

1. High-friction onboarding flows will increasingly shift from document upload toward wallet prompts, verifier flows, or cryptographic age/attribute checks.
2. More services will ask for fewer raw identifiers but stronger issuer trust, possession checks, and revocation signals.
3. “Wallet-ready” verification will become a procurement or compliance category across finance, government, education, and online safety.
4. Political conflict will move toward interoperability, issuer authority, recovery, exclusion, and which claims can be demanded by default.

## Watchpoints

- wallet or mDL acceptance expanding in banking, public services, or education
- regulatory demand for age assurance, residency proof, enrolment proof, or other threshold checks
- service-provider tooling built around selective disclosure, verifier trust, and credential revocation
- fights over recovery, exclusion, device loss, pseudonymity, and coercive over-requesting of attributes

## What would weaken this

- fragmentation or repeated interoperability failure across wallet ecosystems
- institutions continuing to prefer screenshots, manual review, or database lookups because integration costs stay too high
- major privacy, civil-liberties, or security backlash preventing broad reliance on wallet-mediated proofs

## Source anchors

- [SRC-028](../00-meta/bibliography.md#src-028)
- [SRC-029](../00-meta/bibliography.md#src-029)
- [SRC-030](../00-meta/bibliography.md#src-030)
- [SRC-031](../00-meta/bibliography.md#src-031)
- [SRC-032](../00-meta/bibliography.md#src-032)
- [SRC-033](../00-meta/bibliography.md#src-033)
- [SRC-034](../00-meta/bibliography.md#src-034)
