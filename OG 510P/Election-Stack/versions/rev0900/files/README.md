# The Election Stack

Current revision: `v900`.

The current priority is substance over registry expansion. v895 created a primary synthetic CDF replay bridge, v896 added a separate independent replay verifier, v897 added ballot-accounting reconciliation, v898 closed reporting-unit swap risk, v899 added a digest-bound synthetic event-chain witness, and v900 reduces the release-completion risk by removing redundant nested subprocess fan-out from the newest replay/accounting/event gate checks.

## Current synthetic evidence lane

- Primary CDF replay: `tools/cdf_export_replay.py` and `artifacts/reports/cdf-export-replay-report-rev0900.json`
- Independent replay verifier: `tools/cdf_replay_independent_verifier.py` and `artifacts/reports/cdf-independent-replay-verifier-rev0900.json`
- Ballot-accounting reconciliation: `tools/ballot_accounting_reconciler.py` and `artifacts/reports/ballot-accounting-reconciliation-rev0900.json`
- Event-chain reconciliation: `tools/election_event_log_reconciler.py` and `artifacts/reports/election-event-log-reconciliation-rev0900.json`
- Runtime-risk audit: `docs/937-release-gate-runtime-risk-and-inprocess-replay-refactor.md`


## History compaction / package-budget control

- v900 compaction report: `artifacts/reports/rev0900-retrievable-history-compaction.json`
- v900 preserved-byte bundle: `artifacts/history/rev0900-release-gate-hotpath-history.tar.gz`

The compaction only affects superseded non-current source-byte, trust-policy, replay, and provenance history. Current v900 reports and examples remain complete.

## Boundaries

All Example County evidence remains synthetic. This archive is not live election evidence, not a voting system certification, not full NIST EEL/CDF conformance, not the NIST CDF Test Method, not outcome proof, not current voter instruction, not legal advice, and not live-pilot authorization.

## Mission-kernel closeout lane

- Mission closeout map: `artifacts/reports/mission-kernel-closeout-gaps-rev0900.json` and `artifacts/examples/example_county_2026_municipal_pilot/mission-kernel-closeout-index.json`
- Live evidence intake: `artifacts/reports/mission-kernel-live-workqueue-rev0900.json`, `artifacts/reports/mission-kernel-live-evidence-intake-rev0900.json`, and the deliberately empty Example County submission template
- Full non-production drill replay: `artifacts/reports/mission-kernel-full-drill-replay-audit-rev0900.json` and `artifacts/examples/example_county_2026_municipal_pilot/public-full-closeout-drill-replay.md`

Run the release gate with `python3 scripts/release_gate.py`. For publication, use `python3 scripts/release_gate.py --write-manifest --build-zip /absolute/path/to/The-Election-Stack-rev0900-....zip`.
