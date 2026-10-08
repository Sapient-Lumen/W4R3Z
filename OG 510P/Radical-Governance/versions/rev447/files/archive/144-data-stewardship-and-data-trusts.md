# Data stewardship, data trusts, and “information utilities” (governance for shared data)

**Material floor (one sentence):** If data is used to govern people, then data infrastructure must itself be governed—via stewardship roles, assurance, rights, and redress.

## Why this belongs in governance design
Modern governance depends on data flows across agencies, vendors, and jurisdictions; failures show up as discrimination, insecurity, illegibility, and loss of trust (see `06-digital-and-algorithmic-governance.md`, `115-information-integrity-and-record-interfaces.md`).

## Core pattern: stewardship over ownership
Treat high-impact datasets as **stewarded commons**:
- defined purpose + scope limits,
- clear controllers/processors,
- public interest duties (including *non-extraction* constraints),
- contestability + redress,
- audited access and use logs.

ODI provides practical “responsible data stewardship” framing, and argues for assurance approaches that build trust in data practices. See [BIB-ODI-RESPONSIBLE-DATA-STEWARD-2023], [BIB-ODI-DATA-ASSURANCE-2023].

## Data trust / stewardship body: minimal spec
A data trust (or functionally similar steward) is a governed operator with:
1. **Mandate** (what problems; beneficiaries; prohibited uses).
2. **Fiduciary-like duties** (act for beneficiaries/public purpose; conflicts controls).
3. **Access governance** (tiered access; purpose limitation; data minimization; privacy/security).
4. **Assurance & audit** (independent audits; published assurance statements).
5. **Representation & participation** (stakeholder council; affected-groups veto triggers for high-risk uses).
6. **Incident response** (breach/abuse handling; notification; remedies). See `139-risk-and-safety-assurance-governance.md`.
7. **Exit/portability** (sunset, revocation, and transfer protocols). See `109-portability-and-cross-jurisdiction-continuity.md`.

For a concentrated hub of background and early “data trust” thinking, see the Data Trusts Initiative publication list [BIB-DATATRUSTS-UK-PUBS].

## AI-readiness is a governance problem, not a technical checklist
Governments are publishing practical guidelines for preparing datasets for AI uses; these tend to surface the same governance pillars: legality, security, data quality, accountability, and public confidence. See [BIB-UK-GOV-AI-DATASETS-READY-2026].

## Failure modes
- **Shadow data markets** (vendors become de facto governors) → procurement + audit + disclosure (`110-…`, `130-…`).
- **Mission creep** → purpose docket + renewals + public consultation (`118-rulemaking-and-change-control.md`).
- **Opaque model/data pipelines** → record interfaces + explainability + contestability (`06-…`, `115-…`).

## Cross-scope note
Micro-local: community data co-ops and municipal data stewards.  
Regional/national: statutory data stewards with strong audit + redress.  
Global: interoperable stewardship compacts (baseline rights + portability), coordinated via polycentric governance (`136-polycentric-…`).
