---
status: active_case
claim_kind: case_memo
route_role: enforcement_remedy_core
canonical_anchor: false
route_refs:
- enforcement_remedy_core
- certification_core
- measurement_uncertainty_core
supersedes: null
depends_on:
- ../docs/20-program/enforcement-capacity-and-remedy-gate.md
- ../docs/20-program/verdict-engine-and-certification-gates.md
source_refresh_due: 2026-09-30
case_pressure: rev0309_enforcement_case
---


# United States beneficial-ownership reversal case — rev0355

## Verdict

**Verdict:** `correction_required` as an ownership-visibility subsystem case.  
**Mode:** registry durability and legal-design repair.  
**Dominant breach:** enacted beneficial-ownership visibility can collapse when implementation is narrowed, domestically exempted, or non-enforced.  
**Fastest washout:** shell/entity opacity returns before tax, procurement, AML, asset-recovery, and top-tail measurement systems can use the data.

## Why this case was added

rev0308 made owner-control visibility a measurement gate. rev0309 adds the implementation warning: a registry is not durable simply because a statute exists.

FinCEN's current BOI page states that all entities created in the United States, including entities previously known as domestic reporting companies, and their beneficial owners are exempt from reporting BOI to FinCEN; foreign reporting companies remain covered under revised deadlines.[S169] FinCEN's March 2025 press release and the Federal Register interim final rule explain the narrowed reporting-company definition and interim process.[S170][S433]

This is a clean stress case for legal attack surface, enforcement discretion, and registry durability.

## Gate readings

| Gate | Reading | Reason |
|---|---|---|
| Gate 10 — owner-control visibility | fail for domestic entity coverage | domestic reporting-company coverage was removed |
| Gate 11 — enforceability | fail for registry durability | statutory ambition did not survive implementation/litigation/political pressure intact |
| Gate 6 — wealth-to-rule | warning | opaque domestic entities remain usable by top-tail controllers and procurement actors |

## Proof debt

1. Track final rule status and litigation status.
2. Determine whether alternative state-level or sectoral registries fill any gap.
3. Determine whether tax, procurement, property, and AML authorities can still identify domestic controllers.
4. Compare U.S. domestic coverage with FATF/OECD beneficial-ownership expectations.
5. Track enforcement actions or penalties under the narrowed rule.

## Opening package

Do not count U.S. BOI as a strong ownership-visibility rail without stating the domestic-entity exemption. Route to legal-durability repair, state/sectoral registries, procurement disclosure, property ownership transparency, and tax information returns.


## Rev0344 source-use burn-down note

Rev0344 binds formerly unused direct/context sources into this active case so the source ledger no longer carries high-value evidence outside the case/evidence/currentness lineage: [S158]. These bindings do not relax the verdict; they clarify which measurement, authority, or context burden the source supports.

## Rev0346 currentness note

Rev0346 adds FinCEN IFR Q&A because the narrowed BOI posture is broader than a domestic-company carveout: domestic entities and their beneficial owners are exempt from initial, updated, and corrected BOI reports, and reporting companies do not report BOI of U.S. persons. That makes the ownership-visibility failure a U.S.-person reporting gap as well as a domestic-entity gap.[S491]

## Rev0362 claim-edge migration note

Rev0362 adds **5 locator-bound verified claim edges** for the current FinCEN BOI perimeter. The case now has exact support for domestic-entity exemption, foreign-only reporting-company coverage, U.S.-person beneficial-owner non-reporting, and interim-rule currentness. It remains `not_certified_current` because final rule/litigation status, alternative domestic ownership rails, access/verification implementation, and trust/legal-arrangement visibility are not yet bound. [S169] [S433] [S491]
