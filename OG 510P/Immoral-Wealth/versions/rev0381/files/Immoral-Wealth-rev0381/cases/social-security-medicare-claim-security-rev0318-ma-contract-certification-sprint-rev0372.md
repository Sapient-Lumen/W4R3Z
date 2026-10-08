---
revision_current: rev0372
generated_at: 2026-06-18T17:44:00Z
title: Medicare Advantage contract-certification sprint
status: advanced_not_certified
---

# Medicare Advantage contract-certification sprint — rev0372

## Why this was riskiest

The Social Security/Medicare case can look safer than it is if Medicare Advantage is treated as a generic Medicare financing detail. The risk is that private-plan denial, appeal burden, coding/risk-score payment drift, RADV recovery, and beneficiary remedy are hidden inside aggregate trust-fund or premium discussions.

## What changed

Rev0372 binds seven new CMS record routes and eight new locator-bound evidence records. The work now has a concrete ladder: contract/enrollment denominator [S587], Part C organization-determination/reconsideration reporting [S584][S585], validated contract-level LDS access [S586], RADV audit/recovery route [S588][S589], and UM internal coverage-criteria submission [S590].

## Certification ladder

| Step | Gate | Current status |
|---|---|---|
| Contract denominator | contract_id / plan_id / parent / county / enrollment | Green locator, incomplete join |
| Denial and appeal counts | organization determinations, reconsiderations, dispositions | Amber: reporting route exists, public or LDS rows still needed |
| Service-level outcomes | service category, delay, harm, overturned care, beneficiary remedy | Red: not yet public and not acquired |
| Criteria and delegation | internal criteria, delegated entity, reviewer type | Amber: criteria route exists, outcome application missing |
| Payment integrity | RADV audited contracts, results, overpayments, recoveries | Amber: route exists, join to plan finances and claims missing |
| Public upside/remedy | recoupment, rate correction, penalties, automatic approval, compensation | Red: actual remedy records missing |

## Bottom line

This is real forward movement, but not a pass. The archive can now ask for exact rows instead of saying “MA needs more work.” Certification remains blocked until payment, denial, appeal, delay/harm, quality, and recovery ledgers are bound at contract or plan-service level.
