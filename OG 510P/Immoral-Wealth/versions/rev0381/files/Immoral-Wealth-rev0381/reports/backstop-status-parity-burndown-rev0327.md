---
status: active
claim_kind: audit_report
route_role: archive_governance_core
route_refs: [archive_governance_core, public_balance_sheet_core]
revision_current: rev0355
source_refresh_due: 2026-09-30
---

# Backstop status-parity burndown — rev0355

## Finding

The rev0327 audit found a structural completion gap: many case memos were already marked `active_case` while their paired scoreboards still said `seed`. That is dangerous because downstream users certify from scoreboards, not from narrative intent.

## What this revision corrected

Rev0327 promotes the highest-risk public-backstop subset from seed to active:

- `ai-data-center-grid-water-public-backstop-rev0320`
- `us-climate-residual-insurance-public-backstop-rev0319`
- `private-equity-hospital-public-backstop-rev0320`
- `critical-minerals-industrial-policy-public-upside-rev0320`

These were selected because they combine active public-balance-sheet exposure, current regulatory or market movement, and high odds of being left unfinished if the project kept adding doctrine instead of closing cases.

## Refactor rule

This is not a mass status flip. Remaining mismatches stay visible in `reports/status-parity-audit-rev0327.json`. A scoreboard should become active only when it contains case-specific evidence, blocked passes, proof debt, and source-refresh discipline.

## Added sources

- `S445` FERC large-load interconnection docket
- `S446` FERC co-location/data-center AI docket
- `S447` NAIC 2026 homeowners/residual-insurance market data call
- `S448` DOE critical minerals and materials accelerator

## Validator lock

`tools/validate_archive.py` now requires the four promoted cases to remain active, cite their currentness sources, and use the correct refresh cadence.

<!-- current_revision: rev0327; codename: compute-climate-health-minerals-backstop-burndown -->
