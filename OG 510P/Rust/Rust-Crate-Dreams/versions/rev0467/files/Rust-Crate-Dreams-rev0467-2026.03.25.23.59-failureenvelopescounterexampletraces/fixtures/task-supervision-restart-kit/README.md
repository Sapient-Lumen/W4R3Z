# Task Supervision & Restart Kit fixtures

These fixtures exercise the `0.1` artifact vocabulary for **P-0095 Task Supervision & Restart Kit**.

## Core schemas

- `supervision-topology.receipt.schema.json`
- `restart-policy.receipt.schema.json`
- `health-source.receipt.schema.json`
- `state-reset.receipt.schema.json`
- `shutdown-escalation.receipt.schema.json`
- `supervision-failure-bundle.manifest.schema.json`

## Scenario families

- `api_and_websocket_need_explicit_restart_blast_radius/` — dependent subsystems need explicit topology and readiness basis.
- `restart_storm_needs_meltdown_policy_and_failure_bundle/` — restart loops need backoff, meltdown windows, and support artifacts.
- `clone_restart_resets_plain_state_unless_externalized/` — clone-based restarts need state-reset honesty.
- `heartbeat_deadline_restart_is_not_panic_only_supervision/` — hung-task detection is a distinct health basis.
- `shutdown_timeout_can_stop_waiting_while_blocking_work_continues/` — graceful timeout aftermath needs explicit receipts.

The point of this fixture pack is to stop future passes from flattening:

- restart blast radius,
- restart triggers,
- health/readiness basis,
- restart-state retention,
- shutdown timeout aftermath,
- and support-bundle posture

into one fake “supports supervised tasks” story.
