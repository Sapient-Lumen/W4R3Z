---
id: P-0067
title: Kube Integration Testkit — black-box integration tests for kube-rs controllers (Kind-first)
status: idea
domains: [kubernetes, testing, devtools, cloud]
last_reviewed: 2026-03-01
evidence:
  - https://kube.rs/controllers/testing/
  - https://www.reddit.com/r/rust/comments/1pgsls0/rust_kubernetes_integration_testing_setup_with/
  - https://github.com/kube-rs/controller-rs
---

# Problem
Rust Kubernetes controller development has good libraries (`kube`, reference controllers), but **black-box integration testing** remains bespoke:
- setting up clusters (Kind/k3d), CRDs, RBAC, test dependencies
- capturing events/logs and asserting on cluster state
- deterministic cleanup and parallel test isolation

kube-rs documentation covers testing patterns and explicitly notes limitations for truly black-box integration testing.

# Users & user stories
- Operator authors: “I want tests that create CRs and assert on resulting resources/events without reaching into reconcile internals.”
- Platform teams: “I need CI-friendly, reproducible integration tests that don’t require Terraform glue.”
- Maintainers: “I want a standard harness so examples across repos look the same.”

# Prior art (and why it’s insufficient)
- `kube` docs provide patterns, but do not ship a ready-to-use cluster harness and fixture model.
- Teams publish blog-post harnesses (Kind + extra tooling) because there’s no canonical crate/tooling path.

# Design goals
- **Kind-first harness** with a clean abstraction for other backends (k3d/minikube).
- **Fixture model**:
  - apply YAML/JSON resources, wait for conditions, assert invariants
  - golden tests for status fields and events
- **Isolation & cleanup**:
  - per-test namespace, label-based sweeping, TTL cleanup hooks
  - parallel-safe by default
- **Observability capture**:
  - collect controller logs, K8s events, and resource snapshots into a run artifact
- **Local dev UX**: `cargo test` should “just work” with one env var.

# Non-goals
- Replacing Helm/kustomize.
- Full end-to-end deployment frameworks (focus on controller/service tests).

# Architecture
- `kube-testkit` library:
  - `Cluster` trait (Kind impl), `NamespaceGuard`
  - `Fixture` runner with `apply`, `wait_for`, `assert_resource`, `assert_event`
- `cargo kube-test` (optional binary):
  - preflight checks (docker, kubectl), cluster cache, artifact collection

# MVP plan
## 0.1
- Kind backend + per-test namespace + resource apply + wait-for condition helpers
- Artifact bundle (events + resource YAML dumps on failure)

## 0.2
- Log capture integration and snapshotting
- Pluggable backends (k3d) + parallel cluster pool

# Adoption plan
- Provide a reference template repo (controller-rs style) using testkit in `tests/`.
- Make it easy to vendor into CI (GitHub Actions snippet).
