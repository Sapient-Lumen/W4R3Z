# CHANGELOG — rev0292

Created: 2026-05-30T08:20:00-04:00

Rev0292 is a nuclear bankability/buildability/market-design refactor. It keeps the cube explicitly nuclear-positive while making the financing and construction burden of proof machine-readable.

## Added

- Canon files `444`–`448`.
- Nuclear assurance gates `NG_29`–`NG_40`.
- 22 nuclear service floors.
- New finance, offtake, large-load, construction, supply-chain, project-controls, risk-allocation, ratepayer/public-value, cost-overrun and stage-gate tables.
- `cube/nuclear-finance-buildability-propagation-audit.csv`.
- `cube/query-views-rev0292.sql` and `cube/datacube-rev0292.sqlite`.

## Refactored

- Route graph now routes core nuclear and clean-firm files into `444`–`448`.
- Nuclear service floor map now binds the new bankability/buildability gates.
- Nuclear gap backlog and traceability matrix were regenerated against the expanded gate set.
- Scorecards and maturity rows now expose nuclear finance/buildability evidence gaps.

## Caveat

All new local/project evidence rows are templates. The cube favors nuclear pathways but does not certify any real project.
