# 935 — Reporting-unit CDF replay and gate-runtime risk audit

**Track:** A — mission-kernel closeout and evidence intake.

v895 through v897 built a useful CDF replay chain, but the riskiest remaining blind spot was structural: the primary adapter and independent verifier compared CVR-derived votes to ERR votes by contest/option aggregate. That catches changed totals, but it can miss a precinct/reporting-unit swap where aggregate totals remain unchanged.

v898 changes the replay contract to compare by `reporting_unit_id`, `contest_id`, and `option_id`.

## Executable change

- `artifacts/examples/example_county_2026_municipal_pilot/cdf/ballot-definition-minimal.json` now has two synthetic precincts.
- `artifacts/examples/example_county_2026_municipal_pilot/cdf/cast-vote-records-minimal.json` now has six synthetic CVRs across those precincts.
- `artifacts/examples/example_county_2026_municipal_pilot/cdf/election-results-minimal.json` reports precinct-level rows.
- `tools/cdf_export_replay.py` now emits comparison rows keyed by reporting unit.
- `tools/cdf_replay_independent_verifier.py` independently recomputes the same reporting-unit rows and checks the primary report and CRO.
- `artifacts/test-vectors/cdf-replay/election-results-unit-swap-total-preserving.json` moves one synthetic vote between precincts while preserving the aggregate total; the gate requires it to fail.

## Audit/refactor finding

The contest-only comparison was a real mission risk because closeout evidence often needs to identify where a discrepancy occurred, not only whether the countywide total changed. A reporting-unit swap could mislead canvass, audit, recount, public notice, or incident triage even when headline totals looked stable.

The release-gate risk is also operational: one-command completion has been repeatedly hard to demonstrate in this cloudtainer because the gate launches many isolated child processes and several packaging probes build or verify full carriers. v898 does not solve that whole runtime problem. It keeps the fix focused on the evidence blind spot and records the gate-runtime pressure as future work rather than papering it over with a claimed full-gate pass.

## Remaining blockers

This still is not full NIST CDF conformance, a NIST CDF Test Method result, live jurisdiction export evidence, certification, outcome proof, current voter instruction, or legal advice. The next live-readiness blockers remain actual jurisdiction exports, authorized local ballot-accounting and custody records, external reviewer execution, public-release approval, and retention/redaction/legal review.
## Source-byte history compaction audit

After the v898 replay fixtures and current source-byte reports were regenerated, the governed tree exceeded the release size budget. Rather than delete history or add another prose-only exception, v898 compacts 84 superseded rev0895-rev0897 source-byte/cache reports and workpack files into `artifacts/history/rev0898-sourcebyte-fixture-history.tar.gz`.

The shipped stubs bind each original path, size, SHA-256 digest, bundle path, and tar member path, and `scripts/check_retrievable_history_compaction.py` verifies recovery. Current v898 reports remain complete and un-compacted.

