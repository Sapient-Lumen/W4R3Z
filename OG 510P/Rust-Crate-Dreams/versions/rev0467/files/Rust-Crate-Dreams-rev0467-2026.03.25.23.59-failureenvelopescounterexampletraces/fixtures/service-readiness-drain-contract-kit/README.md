# Service Readiness & Drain Contract Kit fixtures

These fixtures exercise the `0.1` artifact vocabulary for **P-0534 Service Readiness & Drain Contract Kit**.

## Core schemas

- `activation-gate.receipt.schema.json`
- `readiness-surface.receipt.schema.json`
- `health-channel.receipt.schema.json`
- `shutdown-trigger.receipt.schema.json`
- `drain-policy.receipt.schema.json`
- `inflight-fate.report.schema.json`
- `service-transition-bundle.manifest.schema.json`

## Scenario families

- `tower_poll_ready_is_not_external_probe_or_warmup_gate/` — Tower admission readiness is not the whole startup/readiness story.
- `listener_bound_early_still_needs_activation_gate_for_dependency_warmup/` — bound listener is not the same as safe traffic admission.
- `grpc_health_serving_is_not_same_as_http_admission_or_mesh_readiness/` — gRPC health and HTTP readiness must stay separate.
- `hyper_graceful_shutdown_needs_timeout_aftermath_and_client_fate_receipts/` — graceful shutdown still needs explicit drain and timeout truth.
- `signal_and_subsystem_failure_need_distinct_shutdown_trigger_receipts/` — shutdown trigger classes must remain explicit.

The point of this fixture pack is to stop future passes from flattening:

- activation gates,
- readiness surfaces,
- health channels,
- shutdown triggers,
- drain policy,
- and in-flight request fate

into one fake “service is healthy and supports graceful shutdown” story.
