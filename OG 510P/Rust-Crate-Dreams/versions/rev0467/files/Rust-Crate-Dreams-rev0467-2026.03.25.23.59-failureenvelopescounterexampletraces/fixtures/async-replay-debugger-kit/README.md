
# Async Replay Debugger Kit fixtures

These fixtures exercise the `0.1` artifact vocabulary for **P-0073 Async Replay Debugger Kit**.

## Core schemas

- `schedule-basis.receipt.schema.json`
- `time-basis.receipt.schema.json`
- `instrumentation-coverage.report.schema.json`
- `effect-boundary.receipt.schema.json`
- `replay-fidelity.report.schema.json`
- `async-incident-bundle.manifest.schema.json`

## Scenario families

- `tokio_console_live_telemetry_is_not_offline_replay_bundle/` — live console telemetry is useful but still needs an honest fidelity claim.
- `spawned_future_without_in_current_span_creates_lineage_gap/` — missing span propagation should downgrade causal coverage.
- `paused_tokio_time_is_not_wall_clock_or_multithread_schedule_control/` — paused Tokio test time is a narrower time basis than generic incident replay.
- `shuttle_schedule_replay_without_effect_capture_stays_local/` — a strong schedule basis still needs effect-boundary honesty.
- `sturgeon_stream_timing_replay_is_slice_not_whole_program/` — a precise stream cassette is still only one effect slice.

The point of this fixture pack is to stop future passes from flattening:

- schedule authority,
- time authority,
- instrumentation completeness,
- effect capture,
- and replay fidelity

into one fake “we support async replay” story.
