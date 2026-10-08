# Digital and Algorithmic Governance (Automated Decisions + Public Digital Systems)

This memo defines a **minimal governance layer** for any public institution that uses:
- automated decision systems (ADS) or AI in rights-affecting contexts (benefits, housing, education, policing, immigration, credit-like eligibility, etc.)
- large-scale public digital infrastructure (identity, payments, registries, case management)

**Primary advantage:** scale + speed + consistency (when well-designed)  
**Primary risk:** invisible power (opaque rules), discrimination, vendor capture, and denial of remedy.

## Minimum Viable Safeguards (MVS)
These safeguards MUST exist before ADS can be used for rights-affecting decisions.

1) **Legal basis + purpose limitation**
- A public legal basis MUST specify purpose, affected populations, and decision authority.

2) **System register (public inventory)**
- Government MUST maintain a public register of ADS used in public decisions: purpose, legal basis, vendor, data sources, risk tier, evaluation status, and appeal path.

3) **Risk-tiering and bans**
- High-risk uses MUST require an impact assessment and independent review.
- Certain uses MAY be prohibited (e.g., systems that cannot be audited or that require pervasive surveillance to function).

4) **Meaningful human review + appeal**
- Individuals MUST have a clear path to challenge an outcome, obtain a timely human review with authority to overturn, and access remedy (`LAW-3`, `ACC-3`).

5) **Auditability by design**
- ADS MUST produce an auditable record: inputs used, versioning, confidence/uncertainty where relevant, and reason codes.
- Critical services MUST have a fallback mode (manual or simpler rules) to prevent outage-as-denial.

6) **Procurement constraints (anti-vendor-capture)**
- Contracts MUST require: logging access, independent testing rights, portability/exit clauses, security obligations, and transparency for evaluation.

## Recommended architecture (tight)
### A) The ADS Lifecycle Gate
A single, reusable gate used at municipal → national → global program levels.

**Gate outputs (publishable):**
- **Impact assessment** (rights, equity, error costs, security, accessibility)
- **Model/system card** (what it does; what it does not do; known failure modes)
- **Decision + remedy map** (who decides; who can override; escalation ladder)
- **Monitoring plan** (drift checks; complaint signals; incident triggers)

**Default rule:** the higher the discretion and the higher the stakes, the stronger the review requirements.

### B) Two registers instead of infinite paperwork
1) **System Register (public)**: which systems exist and where used.
2) **Exception Ledger (public)**: when the system deviates (emergency overrides, manual overrides, outages, model updates).

### C) Rights-preserving service design
- Provide non-digital access routes for essential services.
- Publish service standards (timelines, reasons for denial, error correction).
- Ensure accessibility and language coverage.

### D) Public digital infrastructure as common rails
When building shared infrastructure (`IOP-4`):
- use open standards and public-interest governance
- separate identity/authentication from surveillance
- treat audit logs and access controls as first-class public goods

## Cross-scope implications (small)
- **Micro-local:** digital tools SHOULD be voluntary, non-coercive, and auditable by members.
- **Municipal/Regional:** ADS most often appears in permitting, benefits, housing allocation, and service triage → require the MVS.
- **National:** enforce baseline rights and remedy standards; forbid un-auditable systems in high-stakes domains.
- **Supranational/Global:** promote interoperable safety/assessment standards and mutual recognition only with rights-preserving safeguards.

## Hooks into the toolkit
- `IOP-5` Automated decision systems governance (core controls)
- `OPEN-5` Information integrity (provenance + correction discipline)
- `LAW-1/2/3` Rights + courts + fast administrative review
- `ACC-1/2/4/5` Audit + integrity + influence transparency
- `IOP-4` Digital public infrastructure

## Anchors (citations)
- OECD Recommendation on AI / AI Principles (2019): https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0449
- NIST AI Risk Management Framework (AI RMF 1.0): https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf
- EU AI Act (Regulation (EU) 2024/1689): https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng
- Council of Europe Framework Convention on AI (CETS 225): https://rm.coe.int/1680afae3c
