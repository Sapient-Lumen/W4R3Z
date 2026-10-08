# Digital and Algorithmic Governance (Automated Decisions + Public Digital Systems)

This memo defines a **minimal governance layer** for any public institution that uses:
- automated decision systems (ADS) or AI in rights-affecting contexts (benefits, housing, education, policing, immigration, credit-like eligibility, etc.)
- large-scale public digital infrastructure (identity, payments, registries, case management)

**Comparative anchors (digital public service standards):** [BIB-UK-SERVICESTANDARD], [BIB-US-21C-IDEA-2018], [BIB-OECD-GPP-SERVICE-2022]. For the joinable service interface, see `47-service-catalog-and-access-journeys-register.md`.

**Primary advantage:** scale + speed + consistency (when well-designed)  
**Primary risk:** invisible power (opaque rules), discrimination, vendor capture, denial of remedy, and **targeting/surveillance drift** (TM-15).

## Minimum Viable Safeguards (MVS)
These safeguards MUST exist before ADS can be used for rights-affecting decisions.

1) **Legal basis + purpose limitation**
- A public legal basis MUST specify purpose, affected populations, and decision authority.
- For high-stakes systems, the legal basis SHOULD reference relevant **`DPR-*` IDs** (personal-data processing inventory) and retention class (`OPEN-9`) (see `33-data-protection-and-personal-data-governance.md`).

2) **System register (public inventory)**
- Government MUST maintain a public `ADS-*` register for systems used in public decisions.
- **Canonical spec:** `42-automated-decision-systems-and-model-registry.md` (joins to `DRR`, `RULE`, `AL-*`, `DPR-*`, `CON-*`).
- Minimal publication discipline SHOULD be compatible with the UK ATRS template (see [BIB-UK-ATRS]).

**No policy-by-software (legal legibility constraint)**
If an ADS or case-management workflow materially depends on **internal manuals, frontline scripts, or configuration tables** that determine outcomes, those artifacts MUST be inventoried in the Public Rules Register (often flagged `GLAW`) and linked to the relevant `SRV-*`/`ADS-*`/`IDN-*` entries (see `39-rulebook-and-instruments-registry.md`). Otherwise “the algorithm” becomes a shadow rulebook.

#### Constrained explainability (don’t confuse “a lane exists” with meaningful remedy)
A receipt that says “denied because ADS-0047 scored you high-risk” is **not** adequate notice. Minimum practice:
- provide a plain-language **factors list** (what drove the outcome),
- publish versioned `ADS-*`/`MOD-*` entries and log major model changes,
- require independent audits where transparency cannot be made fully case-level,
- ensure a **human review** path exists for high-stakes denials, with deadlines and logged outcomes (`AO-NORESP` if missed).

Canonical register spec: `42-automated-decision-systems-and-model-registry.md`.






2a) **Model/version disclosure for high-risk systems**
- If an `ADS-*` system materially depends on a model (ML/AI), the register SHOULD disclose a **model/version pointer** sufficient for audit (vendor name/lineage, version/date, and update/change log).
- For **high-risk** uses, contracts SHOULD guarantee oversight bodies access to enough technical detail to test for error, bias, drift, and security issues (even when public disclosure is limited).

3) **Risk-tiering and bans**
- High-risk uses MUST require an impact assessment and independent review.
- Certain uses MAY be prohibited (e.g., systems that cannot be audited or that require pervasive surveillance to function).

4) **Meaningful human review + appeal**
- Individuals MUST have a clear path to challenge an outcome, obtain a timely human review with authority to overturn, and access remedy (`LAW-3`, `ACC-3`).
- When a challenge/review is decided, issue a review-result `DRR` that includes `AO-*` + the challenged `DRR`, and reference the system (`ADS-*`) so error patterns can be measured.


**Substantive notice rule:** a person-facing decision receipt MUST be more than “the algorithm said no.” It should include:
- the cited legal basis (`RULE-*` as‑of) and the system ID (`ADS-*`),
- the portable reason code(s) (`RC-*`) and the main factor categories (without disclosing sensitive security details),
- what data sources were used (high level), how to correct them, and what to submit on appeal, and
- a clear statement of **recourse** (what changes could alter the outcome, if any) or an explicit “no recourse” explanation.

**When explainability is technically constrained:** the minimum becomes (a) validated performance reporting (overall + by relevant groups/contexts where lawful), (b) independent testing rights, and (c) a real override path with authority to change outcomes.

5) **Auditability by design**
- ADS MUST produce an auditable record: inputs used, versioning, confidence/uncertainty where relevant, and **Reason Code(s)** (`RC-*`) + appeal lane (`AL-*`, see ALR `36-...` and `70-interoperability.md`).
- Critical services MUST have a fallback mode (manual or simpler rules) to prevent outage-as-denial.
- Logs MUST be **version-pinned**: system/version changes are recorded, and decisions can be traced to the version in force at the time.
- Monitoring SHOULD include drift/error signals joined to complaints and review outcomes (`AO-*`) so “harmful models” are discoverable over time.


6) **Procurement constraints (anti-vendor-capture)**
- Contracts MUST require: logging access, independent testing rights, portability/exit clauses, security obligations, and transparency for evaluation.
- For rights-affecting systems delivered/operated by vendors, contracts SHOULD carry the **CLC pack** (receipt/record emission, rule-traceability for scripts/config, FOI/records continuity) so “the vendor system” cannot become a shadow rulebook (see `38-...`).

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
2) **Exception Ledger (public)**: when the system deviates (emergency overrides, manual overrides, outages, model updates). Align with the Emergency Measures Register pattern (`23-emergency-governance-and-exceptions.md`).

### C) Rights-preserving service design
- Provide non-digital access routes for essential services.
- Publish service standards (timelines, reasons for denial, error correction).
- Ensure accessibility and language coverage.

### D) Public digital infrastructure as common rails
When building shared infrastructure (`IOP-4`):
- use open standards and public-interest governance (see `27-standards-and-technical-governance.md`)
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
- `LAW-8` Personal data governance baseline (`DPR-*` IDs + purpose limitation + enforceable correction) (see `33-data-protection-and-personal-data-governance.md`).
- `ACC-1/2/4/5` Audit + integrity + influence transparency
- `IOP-4` Digital public infrastructure

## Anchors (citations)
- See: [BIB-OECD-AI]; [BIB-NIST-AIRMF]; [BIB-EU-AIACT]; [BIB-COE-AI].; [BIB-ENGSTROM-HO-ALGOACC-2019]; [BIB-GFI-AI-RULEMAKING-2025].

## H) Rules as Code (RaC) for service delivery (derivative; traceable)
If automated systems determine eligibility, obligations, or sanctions, publish a **derivative implementation** only if it is:
- traceable to `RULE` IDs + versions (PRR `39-...`),
- shipped with public test cases + change logs, and
- explicitly subordinate to the authoritative legal text.

This reduces vendor lock-in and “frontline discretion drift” while keeping remedy meaningful. See [BIB-CIGI-RAC-2025].
