# Stolen ideas reconciliation ledger

Revision: rev0028

## Purpose

This ledger records useful ideas that BrowserRT is stealing, what they become inside the cube, and what must not be copied blindly.

| Source family | Idea to steal | BrowserRT translation | What not to copy |
|---|---|---|---|
| CDP | Programmatic browser control | one-shot browser fixture lane | browser tests as fragile ad hoc scripts |
| Chromium Telemetry | Managed browser lifecycle plus metrics | fixture owns launch, page action, timing, teardown | giant benchmark suite before tiny proofs |
| WPT | Page-test timeouts and conformance discipline | manifest timeout classes and narrow browser slices | pretending BrowserRT is a standards suite |
| WebContainers | Browser-hosted runtime ambition | tab-local substrate ambition | cloning Node or shell scope too early |
| workerd | Standards-shaped runtime APIs | preserve web-shaped lanes and capabilities | server runtime semantics that do not fit pages |
| WASI Component Model | typed component boundaries | future plugin/kernel ABI pressure | building Wasm plugin machinery before JS proofs |
| Ray | tasks, actors, object refs | BrowserRT primitives and data-plane refs | distributed cluster promises |
| Erlang/OTP | supervisors and child specs | agent lifecycle and restart policy | infinite restart loops without budgets |
| Kubernetes | reconcile desired and observed state | mesh/storage/fixture maintenance loops | YAML-like complexity or cluster language |
| Tokio | runtime bundle, scheduler, timers, drivers | one BrowserRT kernel with lanes/providers | requiring Rust-style ownership in public JS APIs |
| Bazel | test environment contract | manifest fields, timeouts, inputs, outputs | heavyweight build-system scope |
| Nx/Turbo | affected work and caching | impact map and local timing history | remote services or dependency on hosted cache |
| Temporal | durable workflow history, retries, signals | future job history/replay contract | hosted workflow/server scope |
| Orleans | virtual actor identity | future logical AgentRef decoupled from worker instance | distributed cloud actor promises |
| Akka | supervision separated from work | supervisor policy as decoration around agents | policy hidden inside business kernels |
| LMAX Disruptor | sequenced ring/cursors | future SAB mailbox cursor and backpressure rules | low-latency claims before wraparound tests |
| OpenTelemetry | trace/span vocabulary | BrowserRT semantic trace attributes | external telemetry dependency |
| FoundationDB simulation | fake time/providers and deterministic replay | future simulator before mesh/storage complexity | using simulation as a substitute for browser proofs |
| Jepsen | histories and checkers | future chaos artifacts with invariant checkers | chaos as random failure with no checker |
| CockroachDB | metamorphic testing | randomized legal scheduler/queue/provider variants | golden-output bloat |

## Reconciliation rule

A stolen idea must be reduced to one of these forms before it is allowed to guide implementation:

1. a named runtime primitive,
2. a manifest field,
3. a provider contract,
4. a trace event kind,
5. a small proof task,
6. a non-claim.

If it cannot be reduced, it stays in research notes only.

## Current reductions in rev0025

- Browser module Worker agent proof became `browser:worker-agent-proof`.
- Transferable browser data-plane proof became `REV0039-BROWSER-WORKER-AGENT-PROBE.json`.
- CDP became `browser:cdp-boot-report`.
- Browser fixture ownership became `docs/40-validation/browser-cdp-boot-slice.md`.
- Managed URL policy became `docs/40-validation/browser-policy-relaxation.md`.
- Browser timing became a JSON artifact, not a prose claim.
- One-runtime ambition became provider/fallback architecture pressure.
