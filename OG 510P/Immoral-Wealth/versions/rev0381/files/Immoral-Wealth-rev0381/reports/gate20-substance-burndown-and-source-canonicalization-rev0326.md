---
status: active
claim_kind: audit_report
route_role: public_balance_sheet_core
route_refs:
- public_balance_sheet_core
- source_governance_core
- case_calibration_core
revision_current: rev0355
source_refresh_due: 2026-09-30
---

# Gate 20 substance burndown and source canonicalization — rev0355

Generated: `2026-06-12T23:11:58Z`  
Codename: `gate20-backstop-burndown-and-source-canonicalization`

## Priority judgment

The riskiest unfinished area was not another missing registry. It was a cluster of high-consequence Gate 20 scoreboards that still carried `seed` status while their memos already asserted active public-balance-sheet risk. This pass spends the revision budget on turning that cluster into usable evidence: stablecoin/MMF/Treasury liquidity, private credit/nonbank backstop, tax expenditures, and a Federal Reserve status reconciliation.

## Substantive changes

1. **Stablecoins/MMF/Treasury liquidity** now uses a live GENIUS Act rulemaking pack. The case records reserve, redemption, capital, risk-management, AML/sanctions, custody/safekeeping, pass-through-insurance, and state/federal oversight rails, but still blocks comfort until the stress waterfall and public-upside recovery are specified. [S359] [S368] [S375] [S441] [S442] [S443] [S444]
2. **Private credit/nonbank backstop** now cites concrete market-size, semi-liquid retail-vehicle, redemption-cap, bank-linkage, and FSB vulnerability evidence instead of generic opacity language. [S359] [S376]
3. **Tax expenditures** now treats JCT tax-expenditure estimates as public-spending-equivalence evidence and requires claimant, nonclaimant, direct-spending-comparator, sunset, and public-upside-recovery analysis. [S378]
4. **Federal Reserve quasi-fiscal visibility** is status-reconciled from seed to active because the memo and scoreboard already had the Gate 20 register and waterfall; the correction-required verdict did not soften. [S359] [S360] [S361] [S362] [S368] [S372]

## Audit/refactor result

Active duplicate-source references were canonicalized without destructive renumbering: S377 active references moved to S359, and S438 active references moved to S378. S377 and S438 remain in `SOURCES.json` as retained aliases for historical traceability, but no active case memo or scoreboard should cite them after this revision.

## Completion-risk result

The pass promotes four high-risk scoreboards from `seed` to `active`. Remaining seed scoreboards are not hidden; they are now more clearly a future substance backlog rather than silently counted as complete coverage.

## Validator change

`tools/validate_archive.py` now contains a narrow rev0326 check that enforces: stablecoin live-rulemaking sources are present; stablecoin refresh is 2026-09-30; the Gate 20 burndown scoreboards are active; and active case payloads do not cite canonicalized duplicate aliases S377 or S438.

<!-- current_revision: rev0326; codename: gate20-backstop-burndown-and-source-canonicalization -->
