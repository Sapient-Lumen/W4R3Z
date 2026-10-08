# Privacy-Preserving Federation and Consent Ledgers

**Purpose.** Specify rails for cross-domain and cross-scope data sharing (identity, benefits, licensing, education, health) that preserve rights, prevent silent function creep, and keep *consent and lawful basis* legible.

This memo is a bridge between:
- interoperability (`70-interoperability.md`)
- sensitive information governance (`77-*secrecy-governance.md`)
- algorithmic registries and audits (`191-*registry-and-audit-rails.md`)
- FOI/ATI and disclosure rails (`200-*foi-ati-rails.md`)

## Core model

### Federation is a policy problem first
Technical federation (tokens, assertions, APIs) must be bounded by:
- explicit legal basis
- published purposes
- retention limits
- auditable access
- proportionality and alternatives

### Consent ledgers as governance infrastructure
When consent is the lawful basis (or when consent artifacts are required alongside another basis), represent consent as:
- machine-readable records
- portable receipts
- revocation events

ISO/IEC TS 27560:2023 provides an interoperable structure for consent records/receipts; treat it as a reference format when building consent ledgers. citeturn0search3

## Rails

### R1. Purpose binding (query + contract)
Every federated request must include:
- purpose code (from a published taxonomy)
- minimal attribute set
- retention window
- audit handle

Reject requests that do not bind purpose.

### R2. Privacy-preserving verification patterns
Prefer patterns that avoid raw data movement:
- eligibility proofs (yes/no, threshold)
- selective disclosure
- pseudonymous identifiers per-domain
- offline verification where possible

### R3. Logging that is citizen-auditable
Maintain two complementary logs:
1. **System audit log** (tamper-evident, for inspectors)
2. **User-visible access ledger** (“who accessed what about me, when, and why”)

Default: individuals can see their ledger with near-real-time delay, with bounded exceptions for active investigations.

### R4. Revocation and withdrawal propagation
A consent withdrawal or legal-basis change must trigger:
- propagation to relying systems
- de-scoping of downstream processing
- deletion/archiving according to lawful retention rules

### R5. Interoperability profiles and conformance tests
Create a public profile set:
- minimum interface obligations per sector
- schema profiles
- security requirements
- conformance suite

### R6. Independent oversight for federation expansions
Any new federation corridor (new domain linkage) requires:
- pre-deployment safety case
- public impact assessment
- time-bounded pilot
- external review

## Failure modes

- **Function creep:** corridor expands quietly.
- **Silent coupling:** systems become dependent and fragile.
- **Coercive consent:** service access conditioned on unnecessary sharing.
- **Shadow scoring:** data used for undisclosed risk scoring.

Mitigations:
- corridor registry + change-release discipline (`208-*release-engineering*`)
- service SLOs for redress (`189-*redress-ops*`)
- algorithmic registry for any scoring (`191-*registry-and-audit-rails*`)

## Tests (add to governance test suite)

- **T?. Corridor registry:** can you list every active federation corridor and its authorized purposes?
- **T?. User ledger:** can an individual see access events with a clear purpose and authority?
- **T?. Consent portability:** can consent receipts be exported and understood across systems?

## References
- ISO/IEC TS 27560:2023 Consent record information structure. citeturn0search3turn0search15
