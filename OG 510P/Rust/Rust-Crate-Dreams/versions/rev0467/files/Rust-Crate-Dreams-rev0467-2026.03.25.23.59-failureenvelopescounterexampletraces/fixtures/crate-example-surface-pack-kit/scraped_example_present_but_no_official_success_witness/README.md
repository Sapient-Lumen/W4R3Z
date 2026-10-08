# Scenario — scraped example exists but no official success witness

An item in rustdoc shows a scraped example from `examples/`, but the crate has no explicit witness telling a user what successful execution looked like or whether the example is an official quickstart.

What this fixture should force the kit to make explicit:

- scraped presence is useful evidence,
- but scraped presence is not the same thing as an official first-success path,
- and `success-witness.receipt` must stay separate from docs/example linkage.

Expected artifact pressure:

- `docs-example-linkage.report` can be green while `success-witness.receipt` is still missing.
- `scenario-coverage.report` may classify the scenario as `reference_examples_only` instead of `official_quickstart_present`.
- `doctor` should point at `missing_success_witness` rather than pretending the path is fully supported.


Concrete example artifact in this archive:
- `example-support-check.report.example.json`
