# Digital Identity and Credentialing Rails

**Purpose.** Define governance rails for digital identity systems and credential ecosystems that are *usable*, *privacy-preserving*, *anti-capture*, and *interoperable* across scopes.

This memo is not an endorsement of any single architecture (centralized IDs, federated identity, decentralized identifiers, etc.). It specifies **governance invariants** and **control points** that must hold for any architecture adopted.

## Invariants

### I1. Minimization by default
- Systems must support **selective disclosure** and **purpose limitation** (prove *eligibility* without exposing full identity when possible).
- Every relying-party request is expressed as a **bounded query** (fields, purpose, retention).

### I2. User agency with revocation
- Individuals must be able to view, contest, and revoke credentials and authorizations.
- Revocation must be **fast** and **propagated** to relying parties via standard mechanisms.

### I3. Plural issuers, constrained verifiers
- Prevent monopoly issuance or monopoly verification.
- Relying parties (verifiers) are treated as **regulated consumers** of identity evidence, with audit duties.

### I4. Non-discrimination and accessibility
- Identity rails must be accessible to people without smartphones, stable housing, bank accounts, or standard documents.
- Offer **multiple channels** (in-person, paper fallback, assisted digital) and **language access**.

### I5. Separation of powers inside the identity stack
- Split:
  - policy authority (rules)
  - operators (systems)
  - auditors (assurance)
  - ombuds/redress (remedy)
- No single actor should control issuance, infrastructure, and audit.

## System components

### Identity proofing and assurance levels
Adopt explicit assurance tiers for:
- identity proofing / enrollment
- authentication
- federation assertions

Use a public assurance framework aligned to modern practice (e.g., NIST SP 800-63 Revision 4 suite for identity proofing, authentication, and federation). citeturn0search0turn0search4turn0search8

### Credentials
Credentials represent claims (age, license, degree, residency, authority) and must support:
- issuer authentication
- tamper-evidence
- expiry
- revocation
- presentation constraints (what can be presented to whom)

For interoperable credentials, use recognized open standards where feasible (e.g., W3C Verifiable Credentials Data Model v2.0). citeturn0search1turn0search5

### Wallet / agent governance
If a wallet model is used:
- wallet codebases and update pipelines must be auditable
- no dark patterns in consent
- export and portability
- incident response playbooks

Example: the EU digital identity framework requires member states to offer at least one wallet and sets a public interoperability agenda; treat this as a reference case for governance obligations and timelines. citeturn0search2

## Governance rails

### R1. Identity system charter
Every identity program must publish a charter that includes:
- scope (what it is for)
- prohibited uses
- retention rules
- threat model
- audit cadence
- redress path
- deprecation/sunset criteria

### R2. Prohibited or constrained uses
Default constraints (unless explicit constitutional authorization):
- no generalized location tracking
- no real-time mass identification
- no linking across domains without a published lawful basis

If a government insists on high-risk uses, require:
- special legislative procedure
- time-bounded authorization
- independent pre-deployment safety case

### R3. Influence and vendor capture controls
- procurement must avoid single-vendor lock-in (open interfaces, escrow, portability)
- ban vendor-operated “black box” risk scoring for eligibility determinations
- create an **issuer diversity requirement** for critical credential classes

### R4. Data linkage discipline
- linkage needs explicit authorization + public rationale + measured benefits
- keep a public **linkage register** (what links exist, why, who approved)

### R5. Security + privacy assurance
- publish a safety case and recurring assurance evidence (see `73-*safety-case.md`)
- external red teams for identity abuse scenarios
- credential issuance anomaly detection (fraud, coercion, discriminatory denial)

### R6. Redress as a first-class system
- lost credential, stolen device, coercion, false denial, and fraud recovery must be tested as first-class flows
- set time-budgets and service levels for restoration

## Cross-scope assignment

**Micro-local:** assisted enrollment, identity recovery hubs, community verifiers (constrained).

**Municipal/Regional:** primary service integration; fraud analytics (with oversight); accessibility programs.

**National:** standards, root trust governance, passport/registry coordination, security incident coordination.

**Supranational/Global:** mutual recognition compacts, interoperability profiles, and portability protections.

(See `203-mutual-recognition-*` for credential recognition across borders.)

## Tests (add to governance test suite)

- **T?. Identity minimization:** can eligibility be proven without universal identifiers?
- **T?. Revocation:** can a coerced or compromised credential be revoked quickly and verifiers reliably learn it?
- **T?. Anti-capture:** can the system survive vendor/operator compromise without losing auditability and portability?

## References
- NIST Digital Identity Guidelines (SP 800-63 Revision 4 and 800-63-4 online suite). citeturn0search0turn0search8
- W3C Verifiable Credentials Data Model v2.0. citeturn0search1
- EU Digital Identity Framework Regulation: entry into force and wallet obligation timeline. citeturn0search2
