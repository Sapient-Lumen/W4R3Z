---
id: P-0061
title: rclrs-extras-kit — ROS 2 “missing pieces” for Rust: actions, executors, launch ergonomics, and conformance fixtures
status: idea
domains: [robotics, middleware, async, tooling]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/ros2-rust/ros2_rust/issues/465
  - https://users.rust-lang.org/t/i-was-tired-of-ros2-so-i-rewrote-it-in-rust/135139
  - https://discourse.openrobotics.org/t/becoming-an-official-client-library/35521
needs:
  - Give Rust robotics developers a “default path” with feature completeness and predictable ergonomics.
  - Provide conformance fixtures and examples so rclrs-based projects are reliable and easier to teach.
risks:
  - ROS 2 surface area is huge; must avoid reimplementing everything or forking the world.
  - Close coordination with upstream ROS 2 and rclrs maintainers is needed to prevent divergence.
---

## Problem

Rust adoption in robotics is held back by missing or unstable ROS 2 client-library features and ecosystem tooling. Community discussions point out that Rust is often treated as a second-class citizen in ROS 2, and users hit missing APIs in practice. Meanwhile, becoming an “official” ROS 2 client library implies documentation/examples and inclusion expectations that go beyond “bindings compile”.

## Users & user stories

- **Robotics developers**: “I want to write ROS 2 nodes in Rust with the same core capabilities as C++/Python (actions, launch, lifecycle).”
- **Educators**: “I want teaching examples and starter templates that actually work across ROS 2 distributions.”
- **Platform teams**: “I need packaging and CI that proves conformance across OS/ROS distributions.”

## Prior art (and why it’s insufficient)

- `ros2_rust` / `rclrs` provides core bindings and examples, but issues and forum posts show missing functions or churn and gaps relative to first-class languages.  
  https://github.com/ros2-rust/ros2_rust/issues/465  
- The ROS community defines “official client library” expectations as including docs/examples and inclusion in default packages — a higher bar than mere bindings.  
  https://discourse.openrobotics.org/t/becoming-an-official-client-library/35521

## Design goals / non-goals

### Goals
- Provide **“missing pieces”** as an additive crate (or small set of crates) that layers on top of `rclrs`:
  - action client/server ergonomics,
  - robust executors/spinning patterns,
  - launch-file ergonomics (a Rust-first launch DSL and/or adapter),
  - common robotics patterns (parameter handling, lifecycle helpers).
- Ship with a **conformance fixture suite**:
  - canonical examples, integration tests, and behavior expectations.
- Keep upstream collaboration explicit: prioritize upstreaming where possible.

### Non-goals
- Replace ROS 2 or fully reimplement it in Rust.
- Create a new robotics middleware from scratch in v0.1.

## Architecture & API sketch

### Crates
- `rclrs-extras` (core):
  - `Executor` / `spin` wrappers with structured concurrency and cancellation.
  - Parameter helpers with typed defaults and validation.
- `rclrs-actions`:
  - typed action definitions and client/server helpers
  - timeouts/cancel semantics and tracing integration
- `rclrs-launch` (optional):
  - small launch DSL that can generate standard launch artifacts or drive a launcher
- `rclrs-fixtures`:
  - golden examples: pub/sub, services, actions, lifecycle node
  - CI matrix scripts for Linux/macOS/Windows where feasible

### Key design choice: async runtime neutrality
- Provide adapters for tokio and async-std where possible.
- When runtime coupling is unavoidable, isolate it behind feature flags.

## Security / safety model

- Prefer “safe defaults” in executor semantics:
  - bounded queues where appropriate,
  - explicit cancellation/shutdown,
  - avoid unbounded task spawning.
- Avoid hidden FFI safety hazards by keeping unsafe blocks small and audited.

## Maintenance & governance

- Treat `rclrs` upstream as the source of truth; this kit should be:
  - a proving ground for ergonomics + fixtures,
  - a staging area for upstreamable improvements.
- Keep a “compatibility ledger” per ROS 2 distribution to avoid silent breakage.

## MVP milestones

- **0.1**: Executor/spin patterns + one end-to-end example with structured shutdown; minimal fixture runner.
- **0.2**: Action client/server helpers + 2–3 fixtures + documentation cookbook.
- **0.3**: Launch ergonomics experiment + CI matrix expansion + upstream RFCs for improvements.
