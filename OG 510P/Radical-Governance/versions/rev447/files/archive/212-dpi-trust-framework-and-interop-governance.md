# DPI trust framework and interoperability governance

**Purpose:** specify the *operational* trust layer that makes Digital Public Infrastructure (DPI) interoperable across agencies, vendors, and jurisdictions — without turning DPI into a surveillance machine.

This memo is **additive** to the broader DPI-as-utility governance in `188-digital-public-infrastructure-governance.md` (and related rails).

DPI is often framed as foundational digital systems enabling secure interactions (identity, payments, data exchange, etc.). See UNDP’s DPI overview and SDG framing: [BIB-UNDP-DPI-PAGE], [BIB-UNDP-DPI-SDGS-2023].

## Core concept: a public Trust Framework

A DPI Trust Framework is a **public rulebook** that answers:
- *Who may connect?* (eligibility)
- *Under what security/privacy constraints?* (controls)
- *What must be logged and disclosed?* (observability)
- *How is conformance proven?* (tests + audits)
- *What happens when things go wrong?* (incident + redress)

### What the framework is NOT
- not a single central database
- not a “super-ID” mandate
- not an all-seeing integration bus

## Conformance layers

### L0 Interface conformance
- published specs + version policy
- open conformance tests runnable by any integrator
- mandatory deprecation windows

### L1 Security baseline
- minimum controls for authn/authz, key management, logging, patching, and incident response
- required third-party security review for high-criticality connectors

### L2 Privacy & rights baseline
- data minimization by default
- purpose binding + access scoping
- redress/appeal hooks for adverse outcomes attributable to DPI-mediated decisions

### L3 Resilience baseline (critical rails)
- multi-operator readiness and failure drills
- rollback discipline for releases
- continuity plans for enrollment and service access (offline/assisted)

## Interoperability governance

### 1) Building blocks, reference profiles, and conformance tests
To prevent “bespoke integration sprawl,” publish:
- **building-block** specs (component boundaries + responsibilities)
- **reference profiles** (minimal interoperable sets) for core exchanges
- **conformance tests** that any implementer can run

GovStack is a useful reference for a modular building-block approach and published specifications: [BIB-GOVSTACK-SPECS], [BIB-GOVSTACK-ITU].

### 2) Change control (treat DPI like critical infrastructure)
- public changelog + compatibility matrix
- canary deployments + rollback drills
- incident postmortems with mandated remediation deadlines

### 3) Dispute resolution for interoperability
Interop disputes are inevitable (agencies, vendors, jurisdictions). The Trust Framework must include:
- a timeline-bound arbitration path
- waiver discipline (time-bounded; published rationale)
- escalation to an independent inspectorate

## Certification and portability

**Rule:** procure **conformance**, not brands.

- components/operators receive time-bounded certificates (renewal required)
- certification includes *exit artifacts*: export formats, migration guides, and test fixtures
- “no certificate, no connection” for critical pathways

Digital Public Goods (DPG) alignment can be used as an *intake signal* (openness, privacy, “do no harm”), but does not replace local threat modeling: [BIB-DPGA-DPG-STANDARD], [BIB-UN-DIGITAL-PUBLIC-GOODS].

## Cross-jurisdiction linkage

When two jurisdictions interoperate (e.g., mutual recognition for credentials), they should sign a compact that binds:
- shared assurance levels
- audit reciprocity (minimum)
- incident notification + coordinated response
- lawful limits on re-use and joining

(See `203-mutual-recognition-of-credentials-licenses-and-status.md`.)

## Tests (add to Governance Test Suite)

- **T(DPI-TF).1 Public rulebook:** Trust Framework is published; changes are versioned and reviewable.
- **T(DPI-TF).2 Proof:** any connector can be validated via open conformance tests + audit evidence.
- **T(DPI-TF).3 Exit:** certification includes verified export/migration artifacts.
- **T(DPI-TF).4 Rights:** redress path exists for DPI-mediated adverse outcomes; timelines are enforced.
