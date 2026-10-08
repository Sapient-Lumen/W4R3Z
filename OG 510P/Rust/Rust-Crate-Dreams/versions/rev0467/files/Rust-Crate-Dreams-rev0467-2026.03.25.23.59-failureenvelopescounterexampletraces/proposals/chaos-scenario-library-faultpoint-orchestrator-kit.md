---
id: P-0133
title: Chaos Scenario Library & Faultpoint Orchestrator Kit (CI-first chaos with portable failure bundles)
status: idea
domains: [reliability, testing, devtools, distributed-systems, chaos-engineering]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/turmoil/latest/turmoil/
  - https://crates.io/crates/faine
  - https://aws.amazon.com/blogs/mt/bootstrap-your-chaos-engineering-journey-with-aws-fault-injection-service-scenarios-library/
  - https://technology.riotgames.com/news/controlled-chaos-fault-injection-testing
  - https://linkerd.io/2-edge/features/fault-injection/
---

# Problem

Rust has many **fault injection** and **simulation** components, but production-grade “chaos” practice still lacks:

- a shared *scenario library* (“this is what we run to validate resilience”),
- a portable artifact format for failures (so maintainers can reproduce),
- and a cohesive way to apply faultpoints across runtimes (async, services, embedded).

Chaos engineering has matured into reusable scenario catalogs (e.g., scenario libraries), but Rust doesn’t have a crate-level, CI-first version of that idea.

# What it should provide other people

## 1) A scenario library format + runner

A `chaos.toml` (or YAML) format describing:
- targets (process, service endpoints, network links, clocks)
- actions (latency, loss, corruption, restarts, clock skew, CPU starvation)
- success criteria (SLO-ish checks, invariants)
- duration and sampling

Provide `cargo chaos run` to execute scenarios locally or in CI.

## 2) Cross-layer fault injection adapters

- in-process failpoints (compile-time or runtime toggles)
- network shaping (simulated networks / proxy-based shaping)
- scheduler/time perturbations (paired with deterministic simulation kits)
- “host actions” as optional plugins (container restarts, resource limits)

## 3) Portable failure artifacts

- `hardship.zip`-style bundles (align with P-0114) but for chaos:
  - scenario spec
  - event log
  - captured metrics snapshots
  - minimized repro (best-effort)
- `chaos-report.json` summary: scenario, outcome, invariants violated, key timings

# MVP scope

- Library + CLI that runs *in-process* scenarios (failpoints + time/scheduler perturbations)
- One “network” adapter: integrate with a simulation harness approach
- A starter scenario catalog (5–10) focused on typical Rust services:
  - retry storms
  - partial outage
  - slow dependency
  - leader failover
  - clock skew

# v1 scope

- Distributed runner (multi-process) with deterministic replay where possible
- Interop with service meshes / sidecars as adapters
- Scenario “profiles” for common environments (k8s, bare metal, local docker)

# Testing and conformance

- Scenario determinism checks (same seed ⇒ same event schedule)
- Regression tests on the scenario library itself (expected outcomes)
- Compatibility matrix for adapters (what OS/runtime features are required)

# Risks and constraints

- Non-determinism in real environments: emphasize artifact capture + best-effort minimization.
- Safety: make “blast radius” explicit and default to safe/local modes.

