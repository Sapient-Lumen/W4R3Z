---
revision_current: rev0372
generated_at: 2026-06-18T17:44:00Z
title: MA contract-level claim-security and validator pruning sprint
status: current_release_report
---

# MA contract-level claim-security and validator pruning sprint — rev0372

## Why this was the priority

The riskiest unfinished work is Medicare Advantage inside the Social Security/Medicare claim-security case. Aggregate Medicare solvency can conceal contract-level denial, appeal, coding, payment-integrity, recovery, and remedy allocation.

## Substantive forward movement

Rev0372 adds seven CMS source routes (`S584`–`S590`) and eight locator-bound evidence records (`VCEDGE-rev0372-0172`–`VCEDGE-rev0372-0179`). The sprint binds the exact contract-level ladder: Part C reporting, CY2026 organization-determination/reconsideration specifications, contract-level LDS access, monthly enrollment denominators, RADV audit/recovery data, and Part C UM internal coverage criteria.

## Audit/refactor

The live-surface validator had been importable but silent when executed, and it still hardcoded the rev0371 semantic-audit file. Rev0372 makes `tools/validate_live_surfaces.py` executable, prints a pass/fail result, and resolves the semantic-boundary audit path from the current revision. This is a small refactor, but it corrects a real operator-surface risk.

## Certification boundary

The case is **not certified current**. The next decisive records are contract-level LDS/public rows, service-level denial/appeal/delay/harm outcomes, UM criteria application records, RADV recovery joins, plan finance/quality context, and beneficiary/public remedies.
