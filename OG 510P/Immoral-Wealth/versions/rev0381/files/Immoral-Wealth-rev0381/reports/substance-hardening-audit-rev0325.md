---
status: audit_report
claim_kind: release_audit
route_role: case_calibration_core
canonical_anchor: false
route_refs:
- case_calibration_core
- temporal_currentness_core
- dynastic_opacity_core
- source_governance_core
supersedes: rev0324
depends_on:
- REVISION-RECEIPT.json
- cases/estate-gift-gst-exemption-currentness-rev0323-case.md
- cases/dynasty-trust-perpetuity-gst-lock-in-rev0323-case.md
- cases/beneficial-ownership-trust-entity-visibility-rollback-rev0323-case.md
- cases/donor-advised-fund-private-foundation-public-subsidy-rev0323-case.md
source_refresh_due: 2026-12-31
---

# Substance hardening audit — rev0355

## Priority choice

The riskiest unfinished work was the rev0323 case family. Those cases created the right doctrinal surface—temporal currentness, dynasty trust duration, BOI visibility, and charitable-vehicle public subsidy—but still read like seed stress tests. rev0325 converts them into active case memos and active scoreboards without adding new sources, cases, or schema fields.

## Substantive changes

- `estate-gift-gst-exemption-currentness-rev0323` now blocks stale transfer-tax conclusions unless the case names current-law date, effective date, exemption surface, source date, and recertification trigger. [S427] [S428] [S429] [S430]
- `dynasty-trust-perpetuity-gst-lock-in-rev0323` now requires a trust-control map for duration, GST lock-in, directed-trust powers, decanting/migration, and claimant information rights. [S427] [S428] [S431] [S439] [S440]
- `beneficial-ownership-trust-entity-visibility-rollback-rev0323` now treats BOI as a current-law perimeter map with domestic entity, foreign company, U.S.-person, and trust/legal-arrangement lanes scored separately. [S431] [S432] [S433]
- `donor-advised-fund-private-foundation-public-subsidy-rev0323` now treats charitable vehicles as public-subsidy timing infrastructure and requires a deduction-to-benefit waterfall rather than aggregate payout comfort. [S434] [S435] [S436] [S437] [S438]

## Audit/refactor performed

The refactor is intentionally small but enforcement-bearing:

- Memo/scoreboard `source_refresh_due` disagreement is now a validator error.
- `SOURCES.md` is now a current-release surface and must show the active revision.
- Source publication dates must be `undated`, `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`; ranges and update/access notes must move to `date_notes`.
- The BOI case memo refresh date was corrected from `2026-12-31` to `2026-09-30`.
- The macro-consistent wealth accounts memo was corrected from `2026-09-30` to `2026-12-31` to match its scoreboard.
- `SOURCES.json`, `SOURCES.md`, `source-use-register`, `EVIDENCE_LEDGER`, `field-use-ledger`, `field-registry`, `currentness-ledger`, `source-duplicate-audit`, and `route-ledger` were regenerated.

## What remains risky

The next highest-risk work is empirical compression: the cube should identify which older cases are still substantively active, which are merely pattern seeds, and which should be retired or demoted. rev0325 deliberately did not start that portfolio triage because the rev0323 case family was more likely to remain unfinished if not hardened now.
