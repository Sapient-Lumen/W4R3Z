# Cargo Event Stream fixtures

This fixture family is for **P-0042 cargo-event-stream**.
Its purpose is not to replace Cargo’s recorder.
Its purpose is to make the first **portable build-session event handoff** reviewable.

## Core bundle shape

- `event-stream-profile.toml` — capture, repair, redaction, and export policy
- `cargo-event-envelope.ndjson` — stable session event stream
- `foreign-output.record.json` — explicit capture of proc-macro/build-script/runner output
- `rendering-policy.receipt.json` — how diagnostics were rendered
- `event-stream-session.manifest.json` — command lane, workspace, profile, target posture, toolchain basis
- `redaction.receipt.json` — what export policy masked, preserved, or dropped
- `event-stream-bundle.manifest.json` — portable bundle that keeps those truths separate
- `notes.md` — compact scenario explanation

## Scenario families

- `proc_macro_stdout_is_captured_as_foreign_output_not_bare_text/` — proc-macro output should become explicit foreign-output records
- `json_render_diagnostics_requires_explicit_rendering_policy_receipt/` — rendering choices should not disappear during capture
- `build_script_metadata_and_artifact_events_share_session_identity/` — build-script and compiler-artifact events need one shared session story
- `portable_bundle_keeps_native_events_foreign_output_and_redaction_truth_separate/` — bundle shape keeps capture, contamination, and export policy distinct

## Schema starter set

- `cargo-event-envelope.schema.json`
- `foreign-output.record.schema.json`
- `rendering-policy.receipt.schema.json`
- `event-stream-session.manifest.schema.json`
- `event-stream-bundle.manifest.schema.json`
- `redaction.receipt.schema.json`
