---
id: P-0534
title: Service Readiness & Drain Contract Kit — activation-gate receipts, readiness-surface receipts, health-channel receipts, shutdown-trigger receipts, drain-policy receipts, and in-flight-fate reports
status: idea
domains: [async, networking, service, operations, deployment, runtime]
last_reviewed: 2026-03-21
evidence:
  - https://blog.rust-lang.org/2026/03/20/rust-challenges/
  - https://docs.rs/tower/latest/tower/trait.Service.html
  - https://docs.rs/tower/latest/tower/trait.ServiceExt.html
  - https://hyper.rs/guides/1/server/graceful-shutdown/
  - https://docs.rs/axum/latest/axum/serve/struct.WithGracefulShutdown.html
  - https://docs.rs/tonic-health/latest/tonic_health/server/
  - https://tokio.rs/tokio/topics/shutdown
  - https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
  - https://docs.rs/tokio-graceful-shutdown/latest/tokio_graceful_shutdown/
---

# Problem

Rust has excellent substrate for networked and long-lived services, but it still lacks one **boring, reviewable service-transition contract**.

Today the pieces are real but fragmented:

- the Rust project still treats async/networking ergonomics as a live frontier rather than a solved story;
- Tower makes **admission readiness** explicit via `poll_ready` / `ready`, but that is not the same thing as external readiness, startup completion, or drain state;
- hyper makes **graceful shutdown** concrete as “stop allowing new requests while allowing in-flight requests to complete”, but leaves bundleable review artifacts to each application;
- axum exposes server-level graceful shutdown, but does not itself answer how startup activation, probe routes, or timeout aftermath should be communicated to another team;
- tonic-health proves that gRPC health status is a real surface, but that still does not join service admission, listener readiness, startup warmup, or drain semantics into one contract;
- Tokio and `TaskTracker` make shutdown coordination and wait semantics concrete, but that is still substrate for applications, not one portable receiver-facing support artifact;
- partial crates like `tokio-graceful-shutdown` prove appetite for structured shutdown trees, but they still do not standardize activation gates, probe meaning, or in-flight fate claims.

That means a service can honestly say any of the following:

- “uses Tower readiness”,
- “supports graceful shutdown”,
- “has `/ready` and `/live` endpoints”,
- “exports gRPC health”,
- or “uses Tokio shutdown helpers”,

while another team still cannot answer several operationally crucial questions:

1. **When does the service become safe to advertise as ready?**
2. **Is external readiness derived from `poll_ready`, a manual gate, dependency warmup, or something else?**
3. **Which health surfaces exist and who are they for?**
4. **What actually triggers drain or full shutdown?**
5. **What happens to in-flight work during drain, timeout, and aftermath?**
6. **What bundle can another reviewer inspect without reconstructing behavior from framework folklore?**

The missing contribution is therefore **not** another web framework, **not** another probe-endpoint helper, and **not** only another graceful-shutdown crate.
It is a **Service Readiness & Drain Contract Kit**: one receiver-facing contract for activation gates, admission/readiness surfaces, health channels, shutdown triggers, drain policy, in-flight fate, and portable transition bundles.

# Main judgment

This lane is worthy because service operations still rely on several incompatible truths that look deceptively similar in prose:

- *ready to accept a request* is not the same as *safe for a load balancer to send production traffic*;
- *healthy* is not the same as *accepting new work*;
- *graceful shutdown enabled* is not the same as *we know what happens to each in-flight request after the deadline*;
- *gRPC health says serving* is not the same as *HTTP admission is open*;
- and *shutdown requested* is not the same as *all background work has actually drained*.

A worthy crate should therefore help other people review six separate truths before trusting a service-transition claim:

1. **activation gate** — what must become true before the service is considered safe to advertise;
2. **readiness surface** — how admission readiness is represented internally and externally;
3. **health channel** — which liveness/readiness channels exist, for whom, and with what update basis;
4. **shutdown trigger** — which events begin drain or broader shutdown;
5. **drain policy** — how new work is refused, how long grace lasts, and what timeout means;
6. **in-flight fate** — what happens to accepted work during drain and after timeout.

# What it provides

- `activation-gate.receipt.json` — startup/warmup gate class, success basis, and failure action.
- `readiness-surface.receipt.json` — admission basis, external readiness surface, and backpressure posture.
- `health-channel.receipt.json` — liveness/readiness channels, audience/exposure, and update basis.
- `shutdown-trigger.receipt.json` — signal/admin/failure/deploy trigger classes and escalation route.
- `drain-policy.receipt.json` — new-connection/new-request refusal posture, grace budget, keepalive policy, and timeout aftermath.
- `inflight-fate.report.json` — accepted-request fate during drain, timeout fate, client-visible signal, and retry-safety posture.
- `service-transition-bundle.manifest.json` — attached receipts, logs/timelines, redaction posture, and transition class.
- `transition.summary.md` — compact support/oncall handoff note.
- `transition.diff.json` — compares two bundles and classifies activation, readiness, health, trigger, drain, or in-flight-fate drift.
- `cargo service-contract receipt` — emits the compact receipts from a service scenario.
- `cargo service-contract doctor` — warns when readiness/drain claims overstate what the underlying service can actually guarantee.
- `cargo service-contract bundle` — emits one small review/support bundle.
- `cargo service-contract inspect` — summarizes what another reviewer can honestly rely on.

# What the crate should provide other people

1. **Activation honesty** so “listener bound”, “background tasks stable”, and “dependencies warmed” do not masquerade as the same startup state.
2. **Readiness honesty** so `poll_ready`, `/ready`, gRPC health, and operator toggles stop being flattened together.
3. **Health-channel honesty** so internal-only liveness, load-balancer readiness, and public status endpoints remain visibly different products.
4. **Drain honesty** so “graceful shutdown enabled” expands into real refusal, grace-budget, keepalive, and timeout semantics.
5. **In-flight-fate honesty** so another team can tell whether accepted work completes, may be cancelled, or becomes retry-unknown.
6. **One boring review vocabulary** that web, gRPC, service-mesh, operations, and platform teams can share.

# Personas / who it’s for

- service teams running HTTP, gRPC, or mixed-protocol Rust services;
- platform teams standardizing startup, readiness, and drain behavior across many services;
- framework authors who want to export service-transition semantics without forcing one framework stack;
- SRE/oncall teams who need compact bundles when a rollout, drain, or shutdown misbehaves;
- reviewers deciding whether a service is safe to deploy behind a load balancer or mesh.

# Users & user stories

- **Platform reviewer:** “Is `/ready` only checking that the port is bound, or that dependency warmup and background consumers are stable?”
- **Oncall engineer:** “During drain timeout, do in-flight requests finish, fail fast, or disappear into ‘best effort’ ambiguity?”
- **Service author:** “My Tower service uses `poll_ready`, but how do I say whether that truth is exported externally or only used internally?”
- **gRPC maintainer:** “I have `tonic-health`; how do I state whether gRPC health and HTTP load-balancer readiness are joined or separate?”
- **Rollout operator:** “What exact event begins drain — SIGTERM, admin command, subsystem failure, or all of the above?”

# Prior art (and why it’s insufficient)

- Tower `Service` / `ServiceExt::ready` give strong **admission** substrate, but not a portable explanation of startup activation, external health exposure, or drain aftermath.
- hyper documents graceful shutdown clearly, but leaves the receiver-facing policy artifact vocabulary to applications.
- axum provides server-level graceful shutdown support, but not a stable joined contract for warmup gates, health surfaces, and in-flight fate.
- tonic-health provides a concrete gRPC health service, but gRPC serving status is not automatically the same thing as HTTP admission, deployment readiness, or shutdown truth.
- Tokio graceful-shutdown guidance and `TaskTracker` make coordinated stop/wait concrete, but stop/wait substrate is not the same thing as a reviewable service-transition contract.
- `tokio-graceful-shutdown` proves appetite for structured shutdown trees and timeouts, but it still leaves readiness and probe truth application-specific.

What remains missing is the **activation gate + readiness surface + health channel + shutdown trigger + drain policy + in-flight fate** layer above today’s individual crates.

# Design goals

1. **Contract-first, not framework-first.** Start from what another team can review.
2. **Tower/Hyper/Tokio-grounded, vocabulary-portable.** Import today’s concrete semantics without forcing one stack.
3. **Activation honesty.** Startup warmup, listener bind, and manual flip must remain separate.
4. **Readiness honesty.** Internal backpressure/readiness and external probes must not be confused.
5. **Drain honesty.** Grace budgets and timeout aftermath must remain explicit.
6. **In-flight-fate honesty.** Accepted work, newly arriving work, and timeout aftermath must stay visibly distinct.
7. **Import, don’t replace.** Build above frameworks and shutdown helpers instead of demanding a new server runtime.
8. **Manual review over fake certainty.** When the tool cannot prove the claim, emit `manual_review_required`.
9. **Small bundles.** `0.1` should fit code review, CI artifacts, and rollout handoff.

# MVP surface

- Minimal types:
  - `ActivationGateReceipt`
  - `ReadinessSurfaceReceipt`
  - `HealthChannelReceipt`
  - `ShutdownTriggerReceipt`
  - `DrainPolicyReceipt`
  - `InflightFateReport`
  - `ServiceTransitionBundleManifest`
  - `TransitionDiff`
- Import adapters:
  - Tower `Service` / `poll_ready` / `ready` facts when present
  - hyper graceful-shutdown paths when present
  - axum serve/with-graceful-shutdown wrappers when present
  - tonic-health exposure when present
  - Tokio `CancellationToken` + `TaskTracker` shutdown paths when present
  - manual JSON/TOML descriptors for other stacks
- Outputs:
  - receipts/reports as JSON
  - a tiny `transition.summary.md`
  - one zip/tar support bundle format reusing the archive’s evidence-bundle vocabulary when useful

# Proposed fixture / artifact vocabulary

- `activation-gate.receipt.json`
- `readiness-surface.receipt.json`
- `health-channel.receipt.json`
- `shutdown-trigger.receipt.json`
- `drain-policy.receipt.json`
- `inflight-fate.report.json`
- `service-transition-bundle.manifest.json`
- `transition.summary.md`
- `transition.diff.json`

# Suggested commands

- `cargo service-contract receipt`
- `cargo service-contract doctor`
- `cargo service-contract bundle`
- `cargo service-contract inspect`
- `cargo service-contract diff`

# Adoption plan

## Who adopts it first

- Axum / Hyper / Tower services with hand-written readiness and drain logic.
- gRPC services that already expose `tonic-health` but still document shutdown/drain behavior in prose.
- platform teams trying to normalize rollout/drain semantics across many services.

## Why they adopt

- It shortens rollout and shutdown review: service-transition semantics stop living in tribal knowledge.
- It gives teams one portable way to say when traffic may begin, how drain behaves, and what in-flight work can expect.
- It lets current frameworks stay in place while exporting shared receipts.

## Path to ecosystem pull

- Start with Tower/Hyper/Tokio adapters plus one `tonic-health` import path.
- Ship doctor warnings that catch over-claims around external readiness, health exposure, and timeout aftermath.
- Publish tiny scenario bundles that maintainers can copy into docs and CI.
- Keep artifact vocabulary protocol-agnostic enough that other frameworks can import it without pretending feature parity.

# Maintenance plan

- Keep the core schema set tiny and versioned.
- Prefer adapters and vocabulary extensions over deep framework coupling.
- Treat doctor warnings as semver-sensitive public surface.
- Maintain explicit redaction guidance for transition bundles.

# Risks / sharp edges

- It is easy to over-claim because frameworks expose several similarly named but semantically different “ready/healthy” notions.
- External load balancers and meshes may interpret routes/status differently from the Rust service itself.
- Timeout aftermath is often less deterministic than application prose implies.
- Background workers, connection pools, and protocol servers may drain on different clocks.
- Too much framework ambition would turn this into another service platform instead of a contract lane.

# Non-goals

- a new web framework;
- a new gRPC framework;
- universal health-check protocol mediation;
- hosted deployment orchestration;
- process supervisor replacement;
- exact automatic inference of every readiness claim.

# Relationship to other proposals

- Distinct from **P-0520 Crate Lifecycle Surface Pack Kit**: lifecycle support is the broader crate-authored shutdown/background-work lane; **P-0534** is specifically the service-transition contract for activation, readiness, health channels, and drain/in-flight fate.
- Distinct from **P-0095 Task Supervision & Restart Kit**: supervision is about restart topology and child policy; **P-0534** is about service admission and drain semantics.
- Distinct from **P-0529 Channel Surface Contract Kit**: channels define delivery/backpressure truth, not service-transition truth for listeners and requests.
- Distinct from **P-0532 Async Runtime Assurance Profile Kit**: runtime assurance is about choosing and qualifying a runtime family; **P-0534** is about service behavior built on top of a runtime.
- Distinct from framework-specific shutdown helpers: those are substrate; **P-0534** is the portable review contract above them.

# What to leave for later

- richer protocol-specific client-fate taxonomies for HTTP/2, gRPC streaming, WebSockets, and raw TCP;
- generated docs/diagrams for rollout playbooks;
- mesh/load-balancer-specific adapters;
- stronger imported evidence from integration tests;
- formal service-state-machine export.

# Why this could be epic

Rust is already a serious language for long-lived services, but service behavior at rollout and shutdown boundaries is still too often explained with local folklore.
A crate that makes **activation**, **readiness**, **health**, **triggers**, **drain**, and **in-flight fate** compactly reviewable would help service teams ship more confidently without forcing them into one framework stack.
That is exactly the kind of boring, high-leverage crate the ecosystem is still missing.
