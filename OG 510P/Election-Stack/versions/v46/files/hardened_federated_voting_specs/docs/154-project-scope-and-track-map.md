# 154. Project scope and track map

**Track:** Shared


This archive is **not** “just internet voting” and it is **not** “just audits”.

It is a **full election stack**, expressed as **evidence infrastructure**:

> Assume compromise happens. Design so outcome-changing attacks are either impossible or **loudly provable**, with a recovery path.

## 154.1 What the project is really about

A concise thesis:

1. **Elections are socio-technical systems**, but the *thing we can ship* is **verifiable evidence** that lets diverse parties (courts, candidates, press, public, auditors) independently check key claims.
2. The hardest class of attacker wins by **corrupting the verification ecosystem** (selective disclosure, challenge grinding, split-worlds), not by “changing a tally in secret”.
3. Therefore the core deliverable is a **transparency + evidence layer** that wraps the whole stack:
   - registration/eligibility (without long-term credential → ballot links)
   - ballot definition integrity
   - casting and recording (with inclusion proofs)
   - tabulation + results publication
   - audits/recounts + dispute resolution
   - incident communications (signed, accountable, deadline-bound)

If you want a single phrase: **Evidence-based elections, with CT-style transparency and adversarial monitoring.**

## 154.2 The three-track framing

These tracks share primitives (logs, evidence bundles, monitors), but make different assumptions.

### Track A — Deployable Core (evidence-based elections)

Assumptions:
- paper ballot of record (or voter-verifiable paper record) exists for binding public elections
- cryptography strengthens transparency and early detection, not “faith in software”

Deliverables:
- verifiable publication of election parameters (EPB)
- receipts/inclusion proofs that resist equivocation
- ENR/results pipeline hardening + audience parity monitoring
- witness/monitor ecosystem + inspections + suppression proofs
- court-usable evidence bundles and dispute process

### Track B — Remote Return Research Annex (hard-mode experiments)

Assumptions:
- coercion/malware risks are real; the archive must not pretend otherwise
- constrained contexts may still demand remote return (e.g., special populations)

Deliverables:
- explicit risk posture + ethics guardrails
- narrow-scope protocols and mitigations
- instrumentation and evidence collection for learning

### Track C — North Star (fully electronic voting “done right”)

Assumptions:
- we are allowed to build the missing ecosystem: attestable devices, transparent manufacturing, robust verification

Deliverables:
- remote attestation evidence flow (RATS roles)
- attestation claims format (EAT profiles) + reference values and endorsements
- supply-chain provenance (in-toto statements; SLSA-style predicates)
- endorsement/reference-value transparency with split-world resistance (SCITT/CT patterns)

See `155–157` for the concrete North Star plan.

## 154.3 “We are not backing away from the full stack”

This archive continues to cover the full election system surface area.
The refactor is about **how it is organized** and **what it claims**, not about deleting scope.

- Track A is the “how to deploy safely now” narrative.
- Track C is the “what would have to be true to go fully electronic” narrative.
- The underlying technical artifacts stay shared wherever possible.

## 154.4 Refactor checklist (what to do next)

1. Tag every doc as A/B/C (or shared) in `13-artifact-index.md`.
2. Expand `../artifacts/claims/claim-evidence-matrix.csv` until every major claim is traceable.
3. Keep `evidence/lock/external-sources.toml` pinned; treat upstream drift as an ADR trigger.