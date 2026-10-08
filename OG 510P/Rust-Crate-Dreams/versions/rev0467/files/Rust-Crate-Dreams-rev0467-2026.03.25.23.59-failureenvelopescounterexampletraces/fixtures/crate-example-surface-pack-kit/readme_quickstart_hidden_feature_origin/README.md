# Scenario — README quickstart hides feature/prerequisite origin

A README quickstart looks green in a local clone, but only because a required feature or docs.rs metadata setting is already in place elsewhere in the workspace.

What this fixture should force the kit to make explicit:

- the quickstart may still be official,
- but the hidden prerequisite needs a `prerequisite-origin.receipt`,
- and that origin should not be silently rewritten into “the README itself explained it.”

Expected artifact pressure:

- `prerequisite-origin.receipt` should classify the hidden dependency as `cargo_manifest`, `package_metadata_docsrs`, or `manual_review_required`, not as a plain README fact.
- `example-support-check.report` should fail or warn if the README alone does not fully explain the path.
- `example-summary.md` should mention the missing prerequisite once confirmed.


Concrete example artifact in this archive:
- `prerequisite-origin.receipt.example.json`
