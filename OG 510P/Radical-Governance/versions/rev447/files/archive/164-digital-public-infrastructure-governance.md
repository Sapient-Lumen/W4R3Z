# Digital Public Infrastructure governance (DPI as a public utility)

**Merge relation:** canonical architectural entry for the DPI cluster. Pair with `188-digital-public-infrastructure-governance.md` for the shorter rails layer, `212-dpi-trust-framework-and-interop-governance.md` for conformance/trust architecture, and `213-digital-public-goods-intake-and-certification-rails.md` for intake/procurement discipline.


**Scope:** any jurisdiction building or adopting foundational digital rails (identity, payments, data exchange, registries, messaging, credentialing, service orchestration) intended for broad public benefit.

**Why this memo exists:** DPI is *not* just software procurement. It is a **public utility** with power to exclude, surveil, or monopolize. Treat it like a high‑risk, high‑leverage infrastructure layer: govern it with *utility obligations*, *anti‑capture structure*, and *remedy-by-design*.

Key references: UNDP DPI framing [BIB-UNDP-DPI-SDGS-2023], the G20 DPI framework’s “technology + governance + community” triad [BIB-G20-DPI-FRAMEWORK-2023], DPG definition + standard [BIB-DPGA-DPG-DEFINITION-2021] [BIB-DPGA-DPG-STANDARD], DPI safeguards initiative [BIB-UNDP-OSET-DPI-SAFEGUARDS], and MOSIP principles as a concrete DPI identity example [BIB-MOSIP-PRINCIPLES-2025].

---

## Design intent: DPI as **joinable rails**, not a monopoly stack

**A. Modularity first (replaceable layers).**
- Split rails into components with explicit interfaces: identity/credentials, payments, data exchange, registries, consent/authorization, audit.
- Require **hot‑swappable providers** behind stable interfaces (avoid “single vendor as state”).
- Enforce “no silent swap” discipline: material interface or risk changes require public change notes + impact assessment + rollback plan (see `74-sunsetting-and-deprecation-discipline.md`).

**B. Interop as a constitutional obligation.**
- Interoperability is not a feature; it’s the mechanism that prevents dependency lock‑in and enables exit/voice/fork (`117-exit-voice-fork-federation.md`).
- Interop obligations should be *justiciable*: agencies must either comply or publish a reasoned, time‑bounded waiver (`85-waivers-variances-and-exceptions-discipline.md`).

**C. Open where it matters, protected where it must.**
- Treat “open” as layered: open standards + open APIs + open governance + (often) open source.
- “Open” does **not** mean public data. Personal data is protected; system behavior is inspectable.

---

## DPI governance skeleton (minimum viable constitutional layer)

### 1) Public value charter (what DPI is *for*)
A short, binding charter that specifies:
- **Non‑exclusion**: no one is denied essential services solely due to DPI failure modes.
- **Proportionality**: DPI cannot become a de facto internal passport unless authorized with strict necessity tests.
- **Accessibility & inclusion**: offline/assisted pathways and disability access (`98-persons-path-and-accessibility-invariants.md`).

### 2) Operator/Steward split (anti‑capture by structure)
- **Steward** sets interfaces, security baselines, audit expectations, portability rules, and dispute resolution.
- **Operators** compete or are replaceable service providers behind those interfaces.
- Steward mandate includes: interop enforcement, procurement guardrails, and “system integrity” (security + privacy + continuity).

### 3) Rights, remedy, and grievance-by-default
- **Right to explanation** for adverse outcomes attributable to DPI-mediated decisions (tie to `66-justice...` + `08-remedy...`).
- **Fast lanes** for urgent harms (benefits cutoff, ID lockout): time‑bounded restoration and human review.
- Clear liability: when a DPI component fails, *someone* is accountable; users don’t litigate architecture.

### 4) Assurance case + continuous audit
- Maintain a public **assurance case** for core rails (`73-assurance-case-and-governance-safety-case.md`).
- Independent audits at least annually; publish high-level findings and remediation deadlines.
- Security/privacy baselines must be versioned and enforced across all operators.

### 5) Data minimization + separation of powers (anti-surveillance)
- **Separation**: do not centralize identity, payments, health, education, law enforcement data into a single “master” database.
- Use *claims* and *credentials* where possible; avoid raw identifier re-use across domains (`109-portability...` + `160-digital-identity-credentials-privacy-utility.md` lineage).

---

## DPI procurement & market design: make “good” the default

**Procurement is governance.** High-level rules:
- Require open standards and exportability (data + configuration + audit logs) as contract conditions.
- Prohibit exclusivity clauses that block multi-vendor operation.
- Mandate escrow / reproducible builds / build transparency for high-criticality components.
- Embed performance + inclusion requirements as *service standards* (`82-service-standards...`).

**DPG alignment as a filter, not a halo.**
- Use the DPG definition + standard as a procurement screen for openness, privacy, and “do no harm” claims [BIB-DPGA-DPG-DEFINITION-2021] [BIB-DPGA-DPG-STANDARD].
- Still require local threat modeling + red‑team exercises (`04-threat-models.md`).

---

## Threat model: DPI failure modes that matter politically

- **Exclusion cascade:** identity outage → benefits denial → housing/health spiral. Design “service continuity” failsafes.
- **Function creep:** the rail becomes an enforcement tool (immigration, policing) without democratic authorization.
- **Monopoly capture:** vendor or ministry becomes irreplaceable; interop erodes; oversight weakens.
- **Surveillance by joining:** cross-domain identifier reuse enables tracking.
- **Denial as leverage:** officials or operators can “turn off” opponents.

Mitigation pattern: treat each as a **constitutional risk** with explicit controls, audits, and remedies.

---

## Implementation checklist (tight)

1. Publish DPI charter + scope limits + non‑exclusion rule.
2. Define interface constitution: stable APIs/standards, versioning, deprecation rules.
3. Establish steward/operator split; publish steward decision process.
4. Put portability in law/contract: export, migration, and multi‑operator capability.
5. Set baseline privacy/security controls; require independent audits.
6. Build grievance fast lanes (restoration timelines + human review).
7. Require procurement clauses: open standards, non-exclusivity, escrow/build transparency.
8. Publish a living assurance case + change logs for material updates.

