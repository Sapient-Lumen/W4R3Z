# Digital Public Goods intake and certification rails

**Stack relation:** use `287-dpi-identity-and-trust-family-map.md` for the canonical route across the DPI / identity / trust family. This memo is the DPG intake and certification layer; `164` is the architectural front door; `188` is the compact rails companion; `160` and `210` form the identity subfamily; `211` governs federation and access ledgers; `212` governs trust/conformance.

**Purpose:** establish a rigorous but lightweight process for approving *Digital Public Goods* (DPGs) and other reusable components used by government.

DPGs are commonly framed as open source software/open data/open AI/open standards/open content that meet privacy and “do no harm” expectations and support public value. See: [BIB-DPGA-DPG-STANDARD], [BIB-UN-DIGITAL-PUBLIC-GOODS].

This archive’s stance: **DPG is a procurement + governance category**, not a marketing label.

## Intake pipeline (minimal)

1. **Eligibility screen** (fast)
 - license and openness check
 - basic maintenance signals (activity, issue handling)
 - clear threat model / security posture statement

2. **Conformance review** (technical)
 - interface and data standards alignment
 - interoperability tests runnable by government
 - deployability constraints (on-prem/cloud neutrality when feasible)

3. **Risk & rights review** (governance)
 - privacy/security controls, data minimization
 - safety / “do no harm” assessment
 - redress and accountability paths

4. **Operational readiness** (sustainment)
 - release process, SBOM availability where applicable
 - incident handling + disclosure policy
 - support model (community/commercial) and continuity plan

5. **Decision + publication**
 - approve / approve-with-conditions / reject
 - publish rationale, conformance results, and renewal date

## Certification levels

- **L1 Candidate:** open + documented; basic security posture.
- **L2 Conformant:** passes conformance + interop tests; reliable releases.
- **L3 Critical:** suitable for national-scale DPI; additional requirements: independent security review, audited incident response, multi-operator readiness.

## Renewal and sunset

- **Renewal cadence:** 12–24 months (risk-based).
- **Auto-suspend triggers:** unpatched critical vulnerabilities, abandoned maintenance, repeated interoperability failures.
- **Sunset protocol:** publish migration guides; provide at least one supported exit path.

## Procurement integration (how this changes outcomes)

- procure against **interfaces + conformance**, not brand names
- require vendors to support **component swapability** and data portability
- treat conformance test results as a contract deliverable

## Tests (add to Governance Test Suite)

- **T(DPG).1 Legibility:** any adopted DPG has a public decision record + renewal date.
- **T(DPG).2 Assurance:** critical components have reproducible builds/SBOM or a documented equivalent assurance case.
- **T(DPG).3 Exit:** every critical adoption includes an exit plan and migration budget line.

## Notes

This memo intentionally avoids long policy catalogs. It is designed to be “attachable” to procurement rules and DPI governance without inflating the archive.
