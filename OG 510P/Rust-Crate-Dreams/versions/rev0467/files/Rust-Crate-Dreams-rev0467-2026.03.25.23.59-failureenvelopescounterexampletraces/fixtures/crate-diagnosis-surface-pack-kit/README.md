# Crate diagnosis-surface pack kit fixtures

This fixture pack exists to keep **P-0525 Crate Diagnosis Surface Pack Kit** concrete.
It models receiver-facing troubleshooting support for the awkward middle state where a crate is running but something is wrong.

## Core review objects

- `symptom-taxonomy.profile.schema.json` — recognized symptom names, aliases, ambiguity notes, and automation posture.
- `symptom-class.policy.schema.json` — class-level meaning for symptom buckets and rules for keeping symptoms separate from claimed root causes.
- `triage-sequence.manifest.schema.json` — ordered “inspect first / inspect next / escalate now” flows.
- `triage-origin.receipt.schema.json` — provenance for triage steps imported from docs, code, checks, warnings, or signal surfaces.
- `signal-map.report.schema.json` — which traces, metrics, warnings, or runtime facts matter for each symptom.
- `capture-policy.profile.schema.json` — allow-listed capture classes and sensitivity posture.
- `support-capture.report.schema.json` — concrete bundle recipes and redaction posture.
- `bundle-safety.report.schema.json` — whether a declared support bundle stays within the pack’s safety boundary.
- `self-check.manifest.schema.json` — supported local checks or doctor-style actions.
- `remediation-playbook.manifest.schema.json` — remediation classes the maintainer actually stands behind.
- `diagnosis-check.report.schema.json` and `diagnosis-surface-diff.report.schema.json` — local verification and release-to-release drift reports.

## Fixture families

- `async_request_hang/` — hang versus slow-progress distinctions.
- `async_runtime_console_metrics_alignment/` — tracing/runtime/console signal alignment.
- `auth_expiry_vs_endpoint_mismatch/` — ambiguity between auth drift and endpoint/config mistakes.
- `embedded_board_only_capture_boundary/` — explicit board-only or manual-review-only honesty.
- `local_cli_startup_stall/` — dry-run/config-sanity style troubleshooting for local tools, now with a support-capture example.
- `queue_growth_worker/` — backlog growth and worker starvation support, now with a signal-map example.
- `retry_storm_client/` — retry-amplification support and first-inspection signals, now with a triage-sequence example.
- `console_recipe_declared_but_runtime_not_instrumented/` — tokio-console path claimed without compatible runtime signal emission, now with a diagnosis-check example.
- `timeout_bucket_hides_dns_vs_tls_triage_split/` — one vague symptom bucket that should really be split into two troubleshooting flows.
- `bundle_capture_exports_secret_shaped_env/` — support bundle capture that crosses the declared safety boundary, now with a bundle-safety example.

## Working rule

These fixtures should keep diagnosis support conservative.
If a scenario needs magical host scraping, hidden root-cause certainty, or unrestricted capture to look useful, the lane is drifting away from the crate-authored support contract the archive is trying to design.
