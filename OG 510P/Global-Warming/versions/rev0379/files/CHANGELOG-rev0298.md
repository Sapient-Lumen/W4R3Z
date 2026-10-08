# CHANGELOG — rev0298

## Summary

Rev0298 nuclearizes the cube's human-capital plane. Nuclear remains a preferred clean-firm and strategic option, but the new revision makes people and institutions binding maturity gates.

## Added

- Canon files `474`–`478`.
- Sources `S864`–`S875`.
- 30 nuclear human-capital service floors.
- Gates `NG_119`–`NG_136`.
- Workforce, operator licensing, regulator-capacity, quality-culture, knowledge-management, apprenticeship and publication-control tables.
- `cube/nuclear-human-capital-scorecard.csv`.
- `cube/nuclear-workforce-gap-backlog.csv`.
- `cube/nuclear-human-capital-maturity-cap-execution.csv`.
- Current SQLite mirror `cube/datacube-rev0298.sqlite`.

## Refactored

- Nuclear service-floor map now binds human-capital gates to all nuclear floors.
- Nuclear gate evaluations, assurance backlog and traceability matrix were regenerated.
- Route/source/tag edges were refreshed from the current index.
- Source-use ledger and resource manifest were regenerated.

## Guardrail

The revision favors nuclear more strongly when workforce and regulator evidence exists, but blocks false maturity where people, training, safety culture, knowledge retention or institutional capacity are missing.
