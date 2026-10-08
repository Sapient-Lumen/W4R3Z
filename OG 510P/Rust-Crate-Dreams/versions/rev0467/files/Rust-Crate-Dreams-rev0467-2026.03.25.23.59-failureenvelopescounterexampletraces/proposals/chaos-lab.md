---
id: P-0025
title: chaos-lab
status: idea
domains: [testing, async, reliability, observability]
last_reviewed: 2026-03-01
evidence:
  - https://www.reddit.com/r/rust/comments/1p3e8or/fracture_deterministic_chaos_testing_for_async/
  - https://docs.rs/tower-resilience-chaos
  - https://pierrezemb.fr/posts/writing-rust-fdb-workloads-that-find-bugs/
  - https://technology.riotgames.com/news/controlled-chaos-fault-injection-testing
---

# Problem
Teams want to test that their async services behave correctly under failure (timeouts, dropped packets, partial writes, reordered events).
But in Rust, chaos/fault injection is split across:
- service-layer injectors (Tower layers),
- runtime-level shims that require patching Tokio across the dependency tree,
- large bespoke simulation frameworks.

What’s missing is a cohesive “lab” that:
1) makes chaos tests easy to write, and
2) produces **reproducible artifacts** that make failures debuggable.

# Users & user stories
- **Backend engineer**: “I want to prove retries, timeouts, and idempotency work under real failure patterns.”
- **Library author**: “I want to offer deterministic chaos tests for my async primitives.”
- **SRE/QA**: “When a chaos test fails in CI, I want a replayable artifact.”

# Prior art (and why it’s insufficient)
- `tower-resilience-chaos`: good for injecting faults into Tower services, but doesn’t unify runtime-level control.
- `Fracture`: deterministic chaos testing at runtime level, but requires patching Tokio and leaves gaps for external IO.
- FoundationDB simulation patterns show how valuable “fault injection + invariants” can be, but are domain-specific.

# Design goals
1. **Unified fault model**: a single “fault script” can target time, IO, and service layers.
2. **Deterministic scheduling mode** (where possible) + **record/replay** when not.
3. **Reproducer artifacts**: minimal logs + seeds + fault script + version metadata.
4. **Layered integrations**:
   - Tower layer (easy win),
   - Tokio runtime shim (optional),
   - adapters for popular clients (reqwest, database drivers) as they allow.
5. **Observability-first**: tight integration with `tracing` so failures are explainable.

# Non-goals
- Perfect simulation of the entire OS/network stack.
- Replacing fuzzing; instead, complement fuzzing with *scenario-based* fault models.

# Architecture & API sketch
## Core crate
- `FaultScript`: declarative definition (YAML/JSON/TOML) + Rust builder API
- `ChaosContext`: seeded RNG + virtual clock + event recorder
- `Inject<T>` adapters: wrap services/clients with fault injection

## Tower example
```rust
use chaos_lab::{FaultScript, tower::ChaosLayer};

let script = FaultScript::from_str(r#"
  seed = 1
  [[fault]]
  kind = "latency"
  p = 0.05
  ms = [50, 500]
"#)?;

let svc = my_service().layer(ChaosLayer::new(script));
```

## Reproducer format
- `repro.json`: versions, seeds, enabled adapters
- `events.log`: compact event stream (time, fault decisions, key spans)
- `script.toml`: the original script

# Security / safety model
- Chaos tests must be opt-in; never enable in production by accident.
- Redact sensitive values from logs by default; log only structured keys.
- Deterministic mode should avoid UB by staying within safe Rust abstractions.

# Maintenance & governance plan
- Keep core small; adapters and runtime shims in feature flags / subcrates.
- Build a fixture suite: “retry works”, “timeout works”, “idempotency works”.
- Encourage community-contributed adapters with conformance tests.

# Milestones
- **0.1**: Tower layer + fault script + event logging + replay of script decisions.
- **0.2**: Deterministic virtual time for timers + `tokio::time` interception (where feasible).
- **0.3**: Reproducer artifact CLI: `chaos-lab run --repro out/`.
- **0.4**: Shrinking/minimization heuristics (reduce fault list while preserving failure).
- **1.0**: Stable repro format + cookbook of failure patterns.

# Open questions
- How far can runtime interception go without forking/shimming Tokio?
- What’s the minimal “event vocabulary” that makes repro artifacts portable?

# Sources
- Deterministic chaos testing and tokio patching (Fracture) — https://www.reddit.com/r/rust/comments/1p3e8or/fracture_deterministic_chaos_testing_for_async/
- Service-layer fault injection (Tower) — https://docs.rs/tower-resilience-chaos
- Simulation workload design (faults + invariants) — https://pierrezemb.fr/posts/writing-rust-fdb-workloads-that-find-bugs/
- Fault injection motivation (industry example) — https://technology.riotgames.com/news/controlled-chaos-fault-injection-testing
