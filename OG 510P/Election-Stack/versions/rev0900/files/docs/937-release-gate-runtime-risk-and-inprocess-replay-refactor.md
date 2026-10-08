# 937 — Release-gate runtime risk and in-process replay refactor

**Track:** A — mission-kernel closeout and evidence intake.

The riskiest operational gap after v899 was no longer another missing doctrine surface. It was release closure itself: repeated turns could prove targeted checks and package a carrier, but the one-command gate was difficult to complete inside the cloudtainer because the newest evidence checks spawned additional Python interpreters for every positive and negative replay.

v900 reduces that completion risk without weakening the evidence claims. The release gate already isolates each child check in its own subprocess, so spawning more Python processes inside the child added runtime and fragility rather than material trust separation.

## Executable change

- `scripts/check_cdf_export_replay.py` now calls `tools/cdf_export_replay.build_report()` directly for the positive path and all CDF negative controls.
- `scripts/check_cdf_independent_replay_verifier.py` now calls `tools/cdf_replay_independent_verifier.build_report()` directly while still auditing the verifier source to ensure it does not import or execute the primary adapter.
- `scripts/check_ballot_accounting_reconciler.py` now calls `tools/ballot_accounting_reconciler.build_report()` directly for default and negative accounting fixtures.
- `scripts/check_election_event_log_reconciler.py` now calls `tools/election_event_log_reconciler.build_report()` directly for default and negative event-chain fixtures.

## Measured effect

On the v900 working tree, the four-step hot path run with `scripts/release_gate.py --only check_cdf_export_replay.py,check_cdf_independent_replay_verifier.py,check_ballot_accounting_reconciler.py,check_election_event_log_reconciler.py --skip-manifest --profile --progress` completed in about six seconds. The same v899-style nested-subprocess path had been roughly 34 seconds in this cloudtainer.

This is not a correctness shortcut. The same shipped reports, same current fixture sweep, and same fail-closed negative vectors remain gate-checked. The refactor removes redundant interpreter startup from inside already isolated release-gate child processes.

## Audit/refactor finding

The earlier design had become wasteful because it multiplied isolation layers without a corresponding evidence benefit. Nested subprocesses were useful while the tools were being stabilized, but once the release-gate child became the isolation boundary, the inner process fan-out increased the chance of timeout and incomplete release closure.

v900 therefore treats release completion as a mission-critical artifact: a verifier archive that cannot reliably close its own gate is at risk even if its individual reports are well designed.

## Remaining blockers

This refactor does not create live jurisdiction evidence, full NIST EEL/CDF conformance, a NIST CDF Test Method result, certification, outcome proof, current voter instruction, legal advice, or live-pilot authority. The largest remaining blockers are still authorized local exports and ballot-accounting/custody records, signer/trust-root governance, external reviewer transcripts, retention/redaction/legal approval, and a full-gate publication run that completes as a single command under the target environment.
