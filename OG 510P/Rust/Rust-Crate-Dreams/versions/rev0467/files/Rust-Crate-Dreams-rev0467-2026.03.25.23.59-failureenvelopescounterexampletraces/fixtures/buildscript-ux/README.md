# Buildscript UX fixtures

This fixture family exists to make **P-0046 buildscript-ux-kit** more concrete.

The goal is not to reimplement Cargo. The goal is to produce one boring report that tells another human:

- what directive and message classes were observed,
- what was visible by default versus hidden unless verbose/failure,
- whether the observation came from a live run or cached Cargo JSON,
- what the likely actionable fix is,
- which details were redacted or truncated,
- and whether workspace policy was violated.

## Intended first scenarios

1. `pkg_config_missing_lib` — actionable package-install help is present but buried.
2. `transitive_warning_hidden` — a warning exists but would normally be invisible without `-vv`.
3. `cargo_error_exitcode_mismatch` — `cargo::error` exists, but the non-zero exit path still produces noisy output.
4. `rerun_noise_overwhelms_failure` — hundreds of `rerun-if-*` lines obscure the real error.
5. `cached_buildscript_output_not_run` — Cargo surfaced cached build-script results even though the script did not run this time.
6. `workspace_policy_gate` — a workspace member emits warnings that should fail CI.
7. `secretish_output_redaction` — build script prints env/path values that should be normalized or redacted.

## Minimal bundle for 0.1

- `buildscript-report.json`
- `policy-gate.report.json`
- `buildscript-summary.txt`
- `notes.md`

## Design rules

- Prefer a **coarse but trustworthy summary** over pretending Cargo already exposes a perfect structured causal model.
- Treat Cargo JSON as the preferred source for parsed directives when available.
- Always distinguish live capture from cached/imported observations.

## Included examples

- `scenarios/pkg_config_missing_lib/` — smallest possible actionable-failure example bundle.
- `scenarios/cargo_error_exitcode_mismatch/` — proves that `cargo::error` does not automatically solve noisy failure presentation.
- `scenarios/cached_buildscript_output_not_run/` — proves why capture-origin is part of the contract.
