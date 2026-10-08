# Scenario — only credentialed service path exists

A crate ships examples, but the only officially documented path requires a real credentialed service. There is no loopback/local starter path and no honest manual-review demotion.

What this fixture should force the kit to make explicit:

- having an example is not the same as covering the common first-success scenario,
- `scenario-coverage.report` must be able to say `no_honest_path_yet` or `manual_review_required`,
- and the summary should not oversell “easy getting started” when a safe local path does not exist.

Expected artifact pressure:

- `example-environment.report` should classify the path as `credentialed_service`.
- `scenario-coverage.report` should record the gap for local/loopback adoption.
- `doctor` should emit `scenario_without_official_path` rather than pushing users toward an unsafe or unavailable quickstart.


Concrete example artifact in this archive:
- `scenario-coverage.report.example.json`
