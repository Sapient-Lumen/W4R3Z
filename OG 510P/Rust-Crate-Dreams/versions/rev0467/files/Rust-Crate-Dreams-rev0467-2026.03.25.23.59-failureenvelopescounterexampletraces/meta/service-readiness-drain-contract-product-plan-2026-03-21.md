# Service Readiness & Drain Contract Kit — product plan (2026-03-21)

This note sharpens **P-0534 Service Readiness & Drain Contract Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0534** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not become a framework, a health-check platform, or a deployment control plane.
It should provide one boring, reviewable **service-transition contract** above today's Tower/Hyper/Axum/Tonic/Tokio substrate.

`0.1` should make six things first-class:

1. **activation gate** — what must become true before the service is safe to advertise;
2. **readiness surface** — what internal/external readiness surfaces exist and how they relate;
3. **health channel** — which liveness/readiness channels are exposed, to whom, and how they are updated;
4. **shutdown trigger** — which events begin drain or broader shutdown;
5. **drain policy** — how new work is refused, how grace is budgeted, and what timeout means;
6. **in-flight fate** — what accepted work experiences during drain and timeout aftermath.

## What `0.1` should provide other people

- one compact `activation-gate.receipt.json`
- one compact `readiness-surface.receipt.json`
- one compact `health-channel.receipt.json`
- one compact `shutdown-trigger.receipt.json`
- one compact `drain-policy.receipt.json`
- one compact `inflight-fate.report.json`
- one compact `service-transition-bundle.manifest.json`
- one compact `transition.summary.md`
- one compact `transition.diff.json`
- one portable review/support bundle

## Commands worth shipping first

- `cargo service-contract receipt`
- `cargo service-contract inspect`
- `cargo service-contract doctor`
- `cargo service-contract diff`
- `cargo service-contract bundle`

## What to import, not reinvent

- Tower `Service::poll_ready` / `ServiceExt::ready` semantics when present
- hyper graceful-shutdown facts when present
- axum `WithGracefulShutdown` service-level facts when present
- tonic-health exposure/update facts when present
- Tokio shutdown / `TaskTracker` wait semantics when present
- `tokio-graceful-shutdown` subsystem-tree trigger/timeout facts when present
- manual JSON/TOML descriptors for other stacks instead of forcing one framework model

## Suggested `0.1` doctor warnings

- `poll_ready_claimed_as_external_ready_without_probe_basis`
- `ready_endpoint_claims_dependency_warmup_without_activation_gate`
- `grpc_health_claimed_as_full_service_readiness_without_route_scope`
- `graceful_shutdown_claim_hides_timeout_aftermath`
- `shutdown_trigger_missing_for_drain_claim`
- `inflight_completion_claim_missing_client_visible_failure_mode`
- `health_channels_share_one_name_but_different_audiences`

## First proving-ground scenarios

1. **A Tower service with `poll_ready` still needs a distinct external readiness/probe story.**
2. **A service that binds the listener early still needs an activation gate for dependency warmup or background-worker stabilization.**
3. **gRPC health exposure is not automatically the same as HTTP admission or load-balancer readiness.**
4. **hyper/axum graceful shutdown still needs an explicit timeout-aftermath and in-flight-fate report.**
5. **OS-signal, admin-command, and subsystem-failure triggers need distinct shutdown-trigger receipts.**

## What to leave for later

- deep protocol-specific streaming/WebSocket fate vocabularies
- mesh/load-balancer vendor adapters
- visual deployment/runbook tooling
- cross-process or multi-host orchestration
- automatic inference of every readiness or health claim
