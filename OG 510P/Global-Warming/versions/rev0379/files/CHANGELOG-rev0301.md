# CHANGELOG — rev0301

Created: 2026-05-30T17:05:00-04:00

## Added

- Five nuclear climate-resilience canon files, `489`–`493`.
- Thirty nuclear climate-resilience service floors.
- Eighteen nuclear assurance gates, `NG_173`–`NG_190`.
- Climate-hazard site screen, cooling-water/ultimate heat sink, station blackout, spent-fuel cooling, compound-hazard PRA, emergency-planning access, climate CAPEX, exception, source-authority, scorecard, gap, traceability, and maturity-cap tables.
- SQLite query views for rev0301 climate-resilience analysis.

## Refactored / audited

- Made climate-resilience gates apply to every nuclear service floor.
- Rebuilt global nuclear gate evaluations, gap backlogs, and traceability matrices.
- Rebuilt normalized file/source/route/tag tables from front matter.
- Fixed a register drift issue: S889–S900 were present in `cube/source.csv`; rev0301 adds their human-readable entries to `sources/register.md` and adds S901–S912.

## Policy effect

Nuclear remains preferred, but climate hazard reanalysis, flood/heat/drought/wildfire resilience, station blackout coping, backup power, spent-fuel cooling, emergency-planning access, and public exception handling now cap maturity where evidence is missing.
