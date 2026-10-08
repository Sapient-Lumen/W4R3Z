# Structural audit rev0311 — counterevidence adjudication and kill-switch refactor

Created: 2026-06-04T06:12:00-04:00

## Main correction

Rev0310 could model closure, retest, public claim gating, and blocker burn-down. The dangerous missing behavior was the reverse path: a closure packet needed to be able to fail later when contrary operational evidence appears. Rev0311 adds that path.

## What changed

- `nuclear-emergency-counterevidence-ledger-rev0311.csv` adds 64 synthetic counterevidence rows linked to exact local-evidence sample ids.
- `nuclear-local-evidence-status-site-sample-adjudicated-rev0311.csv` preserves all 1,056 local rows but reopens selected rows when counterevidence is attached.
- `nuclear-emergency-readiness-scorecard-adjudicated-rev0311.csv` recomputes floor and site scores after reopening.
- `nuclear-emergency-public-claim-gate-adjudicated-rev0311.csv` prevents public green claims when P0/P1 or failed-retest evidence remains.
- `nuclear-emergency-operational-bottleneck-stress-test-rev0311.csv` adds alert, route, AFN, CRC, ingestion, healthcare, and recovery capacity checks.
- `nuclear-emergency-readiness-kill-switch-rule-rev0311.csv` states the practical rules that override averages.

## Refactor/audit correction

The source register was stale: `source.csv` had S979-S990 while `sources/register.md` stopped at S978. Rev0311 patches the register through S995 and adds a consistency audit. The three 114,494-row legacy nuclear crossproduct tables remain retained for compatibility, but the new deprecation shim makes the sparse/local/adjudicated path the emergency-readiness route.

## Caveat

All rev0309-rev0311 site rows remain synthetic fixtures. They test the mechanics of evidence intake, closure, counterevidence, scoring, and publication control. They are not real-world findings about any nuclear site.

## ROP / emergency-preparedness PI source-freshness correction

Rev0311 added a current ROP emergency-preparedness PI crosswalk after identifying a stale-risk surface: EP03 must not be treated as an active current PI after its January 1, 2025 retirement, while EP04 facility/equipment readiness must be carried as a current signal. The correction added S996-S999, `nuclear-emergency-rop-ep-pi-signal-crosswalk-rev0311.csv`, two kill-switch rows, a SQLite view, and a source-register consistency audit row.
