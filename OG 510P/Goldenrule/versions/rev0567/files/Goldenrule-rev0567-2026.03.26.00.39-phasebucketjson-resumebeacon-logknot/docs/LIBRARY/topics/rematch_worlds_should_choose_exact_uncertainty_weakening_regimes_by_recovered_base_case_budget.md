# Rematch worlds should choose exact uncertainty weakening regimes by recovered base-case budget

## Claim
Once the archive already exposes the exact five-case weakening recovery ladder, future inheritors should choose weakening regimes by the number of deferred base weakening cases they are willing to restore rather than by raw threshold numerology.

## Why
- the current weakening menu is a serial, prefix-closed ladder of exactly `5` recoverable base weakening cases,
- every integer budget from `0` through `5` maps to exactly one named regime with no skipped counts and no redundant budgets,
- so a governance statement like “recover at most `2` deferred weakenings” is now mechanically equivalent to a unique threshold/regime choice,
- and the marginal cost of relaxing policy becomes auditable one recovered case at a time.

## Current archive consequence
- the archive now carries a weakening-budget selector that returns the most permissive named regime whose recovered-case footprint stays within a stated budget,
- budget `2` is the highest setting that still forbids neutral-anchor relaxed release,
- budget `3` is the first that admits neutral-anchor relaxed release,
- budget `4` is the first that admits direct entry-boundary relaxed release, and budget `5` recovers the full base controller.

## Operational rule
1. decide how many concrete deferred base weakening cases governance is willing to restore,
2. choose the unique regime returned by that recovered-case budget,
3. name the next locked case explicitly so future relaxation has a visible marginal meaning,
4. treat any future policy revision that skips a budget count or makes two budgets equivalent as a substantive redesign.

## Pointers
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector_snapshot_20260308.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector.py`
