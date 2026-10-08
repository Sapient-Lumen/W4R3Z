# Crate Example Surface Pack Kit fixtures

These fixtures exist to keep **P-0524** concrete.

The point is not to prove that Rust lacks examples.
The point is to keep a sharper question reviewable:

> what is the smallest officially supported path from zero to first success, what does it really require, and what evidence proves that it still works?

## Schema families

- `example-surface-pack.schema.json` — declared official examples and support levels
- `quickstart-path.manifest.schema.json` — smallest official paths per adoption goal
- `quickstart-authority.receipt.schema.json` — what source actually blesses a path as the official start
- `adoption-scenario.manifest.schema.json` — scenario grouping / class
- `example-environment.report.schema.json` — local vs loopback vs credentialed vs board/device truth
- `prerequisite-origin.receipt.schema.json` — where prerequisite knowledge came from
- `success-witness.receipt.schema.json` — what counted as proof of life
- `docs-example-linkage.report.schema.json` — README/rustdoc/guide/example linkage health
- `entrypoint-viability.matrix.schema.json` — command/focus/lane viability versus mere visibility
- `visibility-surface.report.schema.json` — rustdoc/docs.rs visibility basis and hosted-surface limits
- `scenario-coverage.report.schema.json` — whether a scenario has an honest official path
- `example-output.report.schema.json` — what success looked like
- `example-normalization.profile.schema.json` — what dynamic output may be normalized
- `example-support-check.report.schema.json` — joined local verdict
- `example-surface-diff.report.schema.json` — release-to-release drift

## Scenario families with concrete example artifacts

- `cli_quickstart/`
  - `quickstart-path.manifest.example.json`
  - `success-witness.receipt.example.json`
- `async_client_happy_path/`
  - `adoption-scenario.manifest.example.json`
  - `example-environment.report.example.json`
- `readme_quickstart_hidden_feature_origin/`
  - `prerequisite-origin.receipt.example.json`
- `dynamic_cli_output_normalization/`
  - `example-normalization.profile.example.json`
- `guide_book_plus_examples/`
  - `docs-example-linkage.report.example.json`
- `proc_macro_getting_started/`
  - `example-output.report.example.json`
- `embedded_no_std_demo/`
  - `example-environment.report.example.json`
- `credentialed_service_only_path_needs_scenario_honesty/`
  - `scenario-coverage.report.example.json`
- `scraped_example_present_but_no_official_success_witness/`
  - `example-support-check.report.example.json`
- `scenarios/readme_start_is_official_but_docsrs_visibility_is_partial/`
  - `quickstart-authority.receipt.example.json`
- `scenarios/example_target_hidden_by_required_features_needs_viability_truth/`
  - `entrypoint-viability.matrix.example.json`
- `scenarios/scraped_visibility_requires_docsrs_flags_and_is_not_local_run_proof/`
  - `visibility-surface.report.example.json`

## Working rule

Do **not** let these fixtures collapse into another generic docs/testing/tutorial bucket.

They are here to keep these review objects separate:

1. official quickstart,
2. prerequisite origin,
3. success witness,
4. environment class,
5. docs/example linkage,
6. scenario coverage,
7. authority truth.
8. entrypoint viability.
9. hosted visibility basis.
10. normalization boundary.
