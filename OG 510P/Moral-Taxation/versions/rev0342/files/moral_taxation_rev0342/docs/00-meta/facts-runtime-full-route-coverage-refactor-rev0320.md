# Facts runtime, full route coverage, and case-audit refactor — rev0320

Rev0320 works on the highest-risk unfinished layer: the archive no longer gets credit merely for having route contracts. Every current route now has at least one active golden-case contract, and each case must pass two runtime checks.

## Priority changes made

1. Strengthened `tools/route_case.py` with a facts-only runtime pass. The combined pass may use normalized case axes; the facts-only pass ignores those axes and scores only the written title and fact pattern against the live route graph.
2. Reworked `tools/audit_case_contracts.py` around the two-mode runtime. A release now fails if expected routes are absent from the combined top-5 candidates or from the facts-only top-8 candidates.
3. Expanded golden cases from 101 to 122 and route expectations from 107 to 166, closing the uncovered-route backlog entirely: 155/155 current route records now have case coverage.
4. Converted the old thin-family risk list into concrete composite cases: controller-map packets, counter-map finality, public-input reciprocity, claim splitting, insurance failure waterfalls, care assessment units, wrongful levy/tip overreach, hidden fee relabeling, remitter-liability notices, third-party reporting escrow, proceeds hoarding, overlap netting, stale measurement/regressivity repair, status-proxy cliffs, same-facts reuse, promoter-list sampling, loss symmetry/stays, frontier scarcity, charitable surplus, and wealth/site-rent/indexation.
5. Raised the route-coverage floor to the current route count. Adding a route without a case is now a release-blocking regression rather than an invisible backlog.
6. Refactored expected flags in the added cases so they are route-backed values, not decorative labels.
7. Added `tools/answer_case.py`, a first answer-emission slice that produces candidate routes, accountable actors, default moves, blocked moves, guardrails, source IDs, unknowns, and must-not-answer warnings without reading answer contracts.

## Runtime result

- Runtime status: `facts_and_axes_candidate_router_invoked`
- Combined candidate limit: 5
- Facts-only candidate limit: 8
- Case contracts: 122
- Expected route obligations: 166
- Combined top-5 route recall: 166/166
- Facts-only top-8 route recall: 166/166
- Combined top-N exact cases: 115/122
- Combined primary matches: 121/122
- Facts-only primary matches: 104/122
- Candidate misses: 0
- Facts-only candidate misses: 0

## Coverage after this pass

- `controller_ai`: 21/21
- `cross_border_reporting`: 6/6
- `environment_climate_commons`: 10/10
- `financial_system_risk`: 8/8
- `labor_care_benefits`: 11/11
- `legal_enforcement_penalty`: 11/11
- `public_finance_core`: 44/44
- `public_procurement_industrial_policy`: 5/5
- `regulated_networks_platforms`: 4/4
- `release_integrity_currentness`: 4/4
- `social_floor_public_services`: 8/8
- `tax_administration_access`: 17/17
- `wealth_property_rent`: 6/6


## Audit/refactor performed

The case-contract audit was the refactor target. It now distinguishes three surfaces that were previously smeared together:

- **Written fact signal**: title and facts only, no normalized axis tags.
- **Normalized axis signal**: `cube_axes_raw` as a fact-normalization layer.
- **Answer contract**: expected routes, remedy profiles, flags, and must-not-answer rules.

That split matters because the old runtime could still pass if a case carried perfect tags but an underspecified fact pattern. Rev0320 blocks that failure mode by requiring facts-only recovery.

## Remaining riskiest gap

The next unfinished layer is no longer coverage. Rev0320 adds a first answer skeleton, but the remaining risk is final answer emission: precedence ordering, route selection beyond candidates, jurisdiction-specific citations, confidence, and quantitative fiscal estimates. The current skeleton is useful handoff material, not final advice.
