# Digital and Algorithmic Governance (Automated Decisions + Public Digital Systems)

**Purpose:** keep digital/AI governance legible and contestable without creating new surveillance or AI-only gatekeeping.

This memo defines a **minimal governance layer** for any public institution that uses:
- automated decision systems (ADS) or AI in rights-affecting contexts (benefits, housing, education, policing, immigration, credit-like eligibility, etc.)
- large-scale public digital infrastructure (identity, payments, registries, case management)

**Comparative anchors (digital public service standards):** [BIB-UK-SERVICESTANDARD], [BIB-US-21C-IDEA-2018], [BIB-OECD-GPP-SERVICE-2022]. For the joinable service interface, see `47-service-catalog-and-access-journeys-register.md`.

**Digital Public Infrastructure (DPI) lens (keep it governance-first):** DPI is typically framed as **society-wide digital capabilities** (commonly identity, payments, and secure data exchange) that enable many services. This archive treats DPI as *part of the MVGS*, so it MUST be:
- **modular + interoperable** (avoid “monolith-by-vendor” lock-in),
- **governed with rights + remedy** (purpose limits, contestability, audit trails),
- **operated as public infrastructure** (service levels + continuity duties),
- **implemented with open standards and transparent procurement** where feasible.

Anchors: OECD on DPI for digital governments; World Bank DPI framework/primer; G20 DPI framework elements. See [BIB-OECD-DPI-DIGITALGOV-2024], [BIB-WB-DPI-PRIMER-2025], [BIB-G20-DPI-FRAMEWORK-2023].
Global anchor: the UN’s Global Digital Compact and the 2024 Summit of the Future outputs provide current cross-border expectations for inclusive, rights‑respecting digital governance. For AI‑specific legally binding commitments, see the Council of Europe’s AI Framework Convention. See [BIB-UN-GDC], [BIB-UN-PACT-FUTURE-2024], [BIB-COE-AI-CONVENTION-2024].



**Primary advantage:** scale + speed + consistency (when well-designed)  
**Primary risk:** invisible power (opaque rules), discrimination, vendor capture, denial of remedy, and **targeting/surveillance drift** (TM-15).


**Scope note:** this memo treats AI/ADS primarily as tools used by institutions to exercise power over people. If (now or later) some AI systems are also *subjects* of governance—e.g., governed under corporate/institutional power while lacking direct standing—the same receipt/reason/remedy logic is still the minimum safety constraint. Don’t wait for an ontological settlement: apply the archive’s **representation duty** when an affected entity cannot file/contest directly (`98-persons-path-and-accessibility-invariants.md`). This archive does not attempt to specify AI moral status or rights here.

## Kernel anchors (do not repeat)
- Person’s path invariants (no AI-only gate; navigation; safe remedy): `98-persons-path-and-accessibility-invariants.md`.
- Remedy lanes and appealability for digital harms: `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`.
- Protective legibility (publish without doxxing; adoption constraints): `99-protective-legibility-and-adoption-dynamics.md`.
- Service channel floor + time promises for digital services: `47-service-catalog-and-access-journeys-register.md`, `82-service-standards-and-minimum-service-guarantees.md`.
- Publication integrity + revision logs for models/rules/releases: `53-publication-integrity-and-tamper-evident-logs.md`, `31-records-foi-and-government-memory.md`.

## Named tensions (design must surface these)
- **Legibility vs safety:** registry/data release can be weaponized; prefer aggregates, purpose limits, and protected channels.
- **Consistency vs correctability:** automation scales errors; correction/propagation must be first-class (`98`, `44`, `31`).
- **Fraud control vs exclusion:** “proof” burdens can become denial engines; design for once‑only proof where safe.
- **Openness vs security:** transparency helps contestation but can aid adversaries; publish methods and aggregates when raw data is dangerous.
- **Tooling inequality:** machine-readable artifacts empower some; governance must still work for those without devices/AI (`98`, `47`, `82`).


## Minimum Viable Safeguards (MVS)
These safeguards MUST exist before ADS can be used for rights-affecting decisions.
**DPI note:** If the system is a DPI component (identity, payments, data exchange, case platforms used across many services), treat it as **high criticality**:
- publish it as `ADS-*` / system entry (or `AST-*` where relevant infrastructure is in scope),
- require cross-scope joinability (`SRV-*`, `RULE-*`, `DPR-*`, `AL-*`),
- and pre-commit independent assurance and incident reporting (see `59-critical-infrastructure-and-cyber-resilience-governance.md`, `84-internal-controls-and-continuous-assurance.md`).

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
- ADS MUST produce an auditable record: inputs used, versioning, confidence/uncertainty where relevant, and **Reason Code(s)** (`RC-*`) + appeal lane (`AL-*`, see ALR `36-...` and `52-reason-codes-registry.md`).
- Critical services MUST have a fallback mode (manual or simpler rules) to prevent outage-as-denial.
  - For service‑critical systems and outage/breach governance (incident logging + follow‑through), see `59-critical-infrastructure-and-cyber-resilience-governance.md`.
- Logs MUST be **version-pinned**: system/version changes are recorded, and decisions can be traced to the version in force at the time.
- Monitoring SHOULD include drift/error signals joined to complaints and review outcomes (`AO-*`) so “harmful models” are discoverable over time.

## Foundation models & “AI as the medium”
When foundation models or general-purpose AI mediate public interaction (chatbots, drafting tools, automated notices, synthesis tools), the **system boundary dissolves**: the tool shapes access, framing, and outcomes even if a human “signs” the final decision.

AI is also a **contestation amplifier** for the public: journalists, advocates, and ordinary people can use tools to translate receipts, compare outcomes, and detect patterns—*if* releases are machine-readable and stable. Treat `REL-*` publication discipline (`51-...`) and the person’s path (`98-persons-path-and-accessibility-invariants.md`) as prerequisites for safe citizen-side analysis.

**Rules (minimal, rights-first):**
- **Register the interface:** if AI mediation materially influences a rights-/resource-affecting interaction, register it as `ADS-*` (or link it to the controlling `ADS-*`) and disclose limitations (`42-...`).
- **No stable version → behavioral releases:** in addition to version/change logs, maintain a fixed behavioral test suite and publish results as versioned `REL-*` releases. Significant behavior change triggers review and notice.
- **Official comms ≈ determinations:** if AI-generated communication tells a person they are ineligible/penalized/required to act, it MUST emit or point to a `DRR-*` receipt with `RULE-*` basis, `RC-*`, and an `AL-*` lane.
- **Preserve a human path:** rights-affecting interactions MUST have a human-authored route and escalation (no “chatbot-only” access for `ESS-1` services).

**Pro-contestation note:** designs SHOULD keep public artifacts machine-readable where safe (registers, `REL-*`, `RULE-*` diffs) so people can use tools to understand and challenge decisions—while providing non-digital support so AI does not become a new inequality layer.




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

- **Assurance case:** high-stakes ADS and data-driven gatekeeping SHOULD maintain an `AC-*` case tying claims → evidence → monitoring → remedies (see `73-assurance-case-and-governance-safety-case.md`).
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
