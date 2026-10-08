# Test Run Artifact Standard Kit — product plan (2026-03-21)

This note sharpens **P-0106 Test Run Artifact Standard Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0106** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to replace `cargo test`, become a universal event protocol for every runner, or standardize every historical test export in the ecosystem.
It should provide one boring, reviewable **test-run artifact contract** above today’s libtest, nextest, JUnit, and custom-harness substrate.

`0.1` should make four things first-class:

1. **run identity** — what exactly identifies one run and how that identity was imported;
2. **selection basis** — which workspace/packages/targets/tests/profile/platform filters actually defined the run;
3. **attempt topology** — whether retries, fail-fast, stress loops, setup scripts, or process model changed the meaning of the verdict;
4. **bundle sensitivity** — whether the artifact is portable only, internally shareable, or actually safe to export.

## What `0.1` should provide other people

- one compact `run-identity.receipt.json`
- one compact `selection-basis.receipt.json`
- one compact `attempt-topology.report.json`
- one compact `bundle-sensitivity.receipt.json`
- one compact `testrun-bundle.manifest.json`
- one compact `testrun.summary.md`
- one compact `testrun.diff.json`
- a portable CI/support/repro bundle

## Commands worth shipping first

- `cargo testrun capture`
- `cargo testrun import-nextest`
- `cargo testrun gate`
- `cargo testrun diff`
- `cargo testrun bundle`

## What to import, not reinvent

- `cargo test` / libtest selection and profile substrate
- `cargo metadata` workspace metadata when needed
- nextest recordings, run IDs, attempt IDs, retries, and stress metadata when present
- libtest JSON when available, but with explicit exactness/survival caveats
- JUnit only as a derivative export/import surface
- custom harness metadata from `libtest-mimic`-style or explicit adapter hooks

## Suggested `0.1` doctor warnings

- `portable_bundle_has_no_sensitivity_receipt`
- `selection_claim_is_exact_but_source_is_lossy_import`
- `custom_harness_mimics_libtest_without_harness_class_receipt`
- `retry_or_stress_behavior_missing_attempt_topology`
- `console_log_import_used_as_run_identity_without_basis`
- `junit_only_import_used_as_full_fidelity_contract`
- `run_bundle_publicly_shared_without_redaction_basis`

## First proving-ground scenarios

1. **A nextest portable recording is attachable to an issue, but still requires `redaction_required` because outputs may contain secrets or PII**
2. **A libtest-style JSON export exists, but the source remains unstable/experimental and must not be treated as one permanent stable contract**
3. **A custom harness mimics libtest output, but the run still needs explicit harness-class identity instead of bluffing built-in equivalence**
4. **Retries, fail-fast, and stress loops materially change the meaning of the final verdict and must survive export**

## What to leave for later

- one universal cross-runner event-stream protocol
- perfect replay for every historical artifact format
- first-class benchmark-result data modeling
- deep redaction/secret detection beyond typed sensitivity posture
- hosted dashboards, retention backends, or organization-specific policy planes
