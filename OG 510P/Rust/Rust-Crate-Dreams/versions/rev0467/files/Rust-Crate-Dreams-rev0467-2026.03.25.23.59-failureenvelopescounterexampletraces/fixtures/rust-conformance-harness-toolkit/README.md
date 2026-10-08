# Rust Conformance Harness Toolkit fixtures

This fixture family exists to make **P-0264 Rust Conformance Harness Toolkit** concrete.

The goal is **not** to replace libtest, nextest, or property-testing frameworks.
The goal is to prove that a Rust-native crate can:

- publish a suite with stable case IDs,
- classify unsupported/environment-missing/failed outcomes honestly,
- emit one compact `*.conformbundle.zip` artifact for a failing case,
- and export comparison findings without pretending incomparable runs are directly equivalent.

## Intended first scenarios

1. `capability_missing_not_failure` — an implementation never claimed a required capability, so the result must not be recorded as an implementation failure.
2. `environment_missing_external_service` — a required external service or simulator lane is absent, and the environment receipt must say so explicitly.
3. `same_case_two_impls_diverge` — two implementations ran the same case and produced different outputs that require human review.
4. `upstream_bug_bundle_minimal_repro` — one failing case emits a compact repro bundle suitable for issue filing.

## Minimal pack for 0.1

- `suite.json`
- `case.json`
- `observed.json`
- `environment.receipt.json`
- `verdict.json`
- `notes.md`

## Design rules

- Prefer **stable case identity** over clever macro magic.
- Preserve whether a case was **unsupported**, **environment-missing**, **failed**, or **passed**.
- Treat JUnit and terminal output as export lanes, not the canonical semantic model.
- Keep cross-implementation comparison conservative when environments are mismatched.
