# Digital Identity + Credentials as a Public Utility (Privacy-Preserving, Portable, Contestable)

**Stack relation:** use `287-dpi-identity-and-trust-family-map.md` for the canonical route across the DPI / identity / trust family. This memo is the identity-as-utility and person-path layer; `164` is the architectural front door; `188` is the compact rails companion; `210` is the identity / credentialing rails memo; `211` is federation and access-ledger discipline; `212` is trust/conformance architecture; `213` is DPG intake/certification discipline.

**Purpose:** make identity/eligibility checks usable across services **without** turning the state (or vendors) into a surveillance platform.

**Person served:** the person who needs to prove *one* fact (age, residency, eligibility, qualification) but is routinely forced to disclose far more, or is excluded by device/bandwidth/paperwork.

**From-below:** if the system says “cannot verify”, you get a human/offline path, a receipt, a time-bound SLA, and no penalties for refusal to over-disclose.

---

## Design stance

Treat identity as **digital public infrastructure** (DPI) only when it behaves like a utility:

- **Non‑exclusion by design:** offline path + assisted path; disability and low‑bandwidth defaults.
- **Portability:** people can move between jurisdictions and providers without losing access to services.
- **Minimal disclosure:** services ask for *claims*, not dossiers.
- **Contestability:** every denial produces a reason + appeal path + fix‑forward lane.
- **Non‑capture:** open standards; replaceable vendors; public interfaces.

**Anchors:** NIST digital identity guidelines (assurance and federation) [BIB-NIST-800-63-4]; W3C Verifiable Credentials model (claim-based credentials) [BIB-W3C-VC-DM-2-0]; EU digital identity wallet direction (interoperable wallet + relying party rules) [BIB-EC-EUDI-REGULATION]; OECD privacy principles as baseline constraints [BIB-OECD-PRIVACY-PRINCIPLES].

---

## What an “identity system” should *actually* do

Split the problem into separate, governable components:

1. **Identity proofing / enrollment** (high-friction, rare).
2. **Authentication** (frequent; should be low-friction and safe).
3. **Authorization / eligibility** (service-specific rules).
4. **Credentials / attestations** (portable claims).
5. **Relying party governance** (who is allowed to ask for what, and why).
6. **Revocation + recovery** (lost device, coercion, compromised identifiers).

**Rule:** never let “authentication strength” quietly become “surveillance strength”.

---

## Core invariants (hard requirements)

### I1. Minimal disclosure by default
- Prefer **selective disclosure**: prove *age ≥ 18* not *date of birth*.
- Prefer **pairwise identifiers** (no universal cross-service correlator).
- “Data minimization” is enforced at the **relying party** boundary with audits and penalties.

### I2. Relying party registration + purpose binding
Any entity that can demand a claim must:
- register, publish purpose + legal basis,
- declare what it requests and retention rules,
- be subject to automated and human audits.

The public must be able to see *who can ask for what*.

### I3. No silent lockout
Loss, fraud flags, or mismatches must not silently cut people off from essentials:
- **grace windows**, **rapid restoration lanes**, and **assisted recovery** are mandatory.
- Denial receipts + appeal in days, not months.

### I4. Firewall essential services
Identity infrastructure cannot be used as an enforcement dragnet.
- Enforce **service firewalls** for health, schooling, basic utilities, and reporting harm.
- “Access logs” cannot become a generalized social graph.

### I5. Multi-provider + exit
People can:
- change wallet providers,
- re-issue credentials,
- rotate identifiers,
- migrate with continuity (see `109-portability-and-cross-jurisdiction-continuity.md`).

---

## Institutional architecture (recommended)

### A. A public “Identity Utility Regulator”
Mandate: prevent coercive over-collection and vendor lock-in.

Minimum powers:
- approve relying party classes and claim menus,
- set default disclosure minimization rules,
- run red‑team programs and publish incident dockets,
- enforce portability and non-discrimination.

### B. A standards + interoperability council (open, multi-stakeholder)
- adopts open standards (W3C VC ecosystem as a baseline) [BIB-W3C-VC-DM-2-0]
- publishes conformance tests; avoids bespoke formats

### C. An independent ombuds lane for identity harms
Identity failures create second-order harms (missed benefits, eviction, detention, job loss).
This lane provides:
- emergency relief orders,
- restoration SLAs,
- systemic issue escalation to regulator.

---

## The “claim menu” pattern

Instead of a universal ID, publish a **bounded menu of standard claims** (examples):

- Age over threshold
- Residency within a boundary
- Eligibility for program X (time-bound)
- Professional qualification / license
- Student status
- Relationship/guardianship status (with heightened protections)
- Payment account validity (without exposing full account identity)

Each claim has:
- allowed relying party classes,
- retention cap,
- revocation rules,
- abuse signals and penalties.

---

## Operational doctrine (how it stays safe)

### Incident response for identity
Treat major outages as critical infrastructure incidents:
- clear comms, rollback capability, manual fallback,
- postmortems, compensation rules, and systemic fixes (see `154-critical-infrastructure-resilience-compacts.md`).

### Coercion and duress
Support “duress-safe” recovery:
- ability to replace identifiers/credentials after coercion,
- protective holds that don’t cut off essentials,
- strong anti-impersonation while minimizing biometrics overuse.

### Auditing without surveillance
- audit *systems* and relying parties, not individuals.
- publish aggregate transparency reports and relying party violation dockets.

---

## Scope fit (micro-local → global)

- **Micro-local:** eligibility and access for local services; strongest need for assisted/offline paths.
- **Regional/national:** portability + equal access; firewalls against mission creep.
- **Supranational:** interoperability compacts; mutual recognition of claims with dispute mechanisms.
- **Global:** narrow “travel + qualification” claim rails; avoid one-world identifier fantasies.

EU wallet implementations and implementing acts are a live case study for supranational portability constraints [BIB-EC-EUDI-IMPLEMENTING-REGS].

---

## Threat model checklist

- **Linkage / correlation:** can two services quietly collude to track people?
- **Function creep:** do new purposes appear without legislative re-approval?
- **Vendor capture:** can a vendor become the de facto sovereign?
- **Exclusion:** what happens to people without devices, documents, stable housing?
- **Coercion:** can an abuser control access via the identity layer?
- **Data breach:** can stolen data re-identify across services?

Tie to `04-threat-models.md` and `06-digital-and-algorithmic-governance.md`.

---

## Minimal public artifacts (to keep it legible)

- **Relying Party Register** (who can ask for what; retention; legal basis)
- **Claim Menu Registry** (standard claims + versions)
- **Denial Receipt Schema** (reason codes + fix-forward lane)
- **Portability/Exit Spec** (provider switching, export/import, escrow-free)
- **Incident Docket** (outages, breaches, abuse findings, remedies)

---

## Tests to add to the governance test suite

1. Minimal disclosure: can a service obtain more than it needs?
2. Portability: can a person switch wallet/provider without losing eligibility?
3. No silent lockout: do denials generate receipts and fast appeal?
4. Firewall: can enforcement access service interaction logs?
5. Offline path: can a person complete the process without a smartphone?
6. Abuse & coercion: can a person safely recover after coercion?

(See `107-governance-test-suite.md`.)

---

## See also

- `06-digital-and-algorithmic-governance.md` (automated decisions, DPI discipline)
- `109-portability-and-cross-jurisdiction-continuity.md` (continuity primitives)
- `115-information-integrity-and-record-interfaces.md` (records + interfaces)
- `154-critical-infrastructure-resilience-compacts.md` (resilience + incident doctrine)
