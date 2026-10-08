---
status: active_bridge
claim_kind: program_protocol
route_role: score_mediated_exclusion_core
canonical_anchor: false
route_refs:
- score_mediated_exclusion_core
- case_calibration_core
supersedes: null
depends_on:
- verdict-engine-and-certification-gates.md
- scoreboard-schema.json
source_refresh_due: 2026-12-31
case_pressure: rev0315_score_mediated_exclusion
---


# Tenant screening, clean-slate, and housing-entry router

Use this router when a case claims housing affordability, vouchers, social housing access, or renter security but does not score screening barriers.[S286][S287]

## Housing-entry test

A household clears the affordability test only if it can also clear screening without hidden or overbroad exclusion. Test:

- credit score and credit history;
- eviction filings, judgments, dismissals, sealed records, and satisfied debts;
- criminal records, arrests without conviction, old records, sealed/expunged records, and relevance to tenancy;
- income-estimation tools and voucher discrimination;
- proprietary resident risk scores;
- landlord override ability;
- pre-denial notice and dispute timing;
- application-fee loss after opaque denial.

## Clean-slate rails

- seal or suppress dismissed eviction filings and non-final records;
- suppress old, irrelevant, sealed, or expunged criminal records;
- require individualized assessment and mitigation evidence where records are accurate but weakly predictive;
- require transparent criteria before fees are paid;
- require vendor and landlord disparate-impact monitoring;
- preserve unit availability during plausible disputes;
- prohibit off-the-shelf denial where law requires individualized judgment.

## Case route

If tenant screening blocks access, route to Gate 17 and Gate 5 before declaring housing affordability, renter security, or place-public-finance progress.
