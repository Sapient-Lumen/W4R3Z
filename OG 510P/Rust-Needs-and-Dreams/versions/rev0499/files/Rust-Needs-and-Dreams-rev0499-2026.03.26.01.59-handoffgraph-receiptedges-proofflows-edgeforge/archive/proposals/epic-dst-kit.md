# Epic Proposal: DST Kit (`cargo dst`, `dst-pack/v0`)

## One-sentence pitch
Give Rust a standard way to run, replay, shrink, and publish deterministic simulation tests so concurrency and distributed-system failures stop living as folklore, flaky CI, and one-off harnesses.

## Deliverables
- `cargo dst` reference tool
- Schemas:
  - `dst-seed/v0`
  - `dst-config/v0`
  - `dst-net-model/v0`
  - `dst-history/v0`
  - `dst-report/v0`
  - `dst-policy/v0`
  - `dst-pack/v0`
- Adapters for:
  - Loom
  - Shuttle
  - Tokio paused-time tests
  - Turmoil
  - MadSim
  - experimental Moonpool-style simulation
- Docs:
  - backend capability matrix
  - seed/replay/shrinking playbook
  - CI recipes and artifact hygiene

## Why now (signals)
- Rust is still investing in async ecosystem maturity and explicitly wants to unblock the next generation of async libraries.
  https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- Debugging remains one of the main productivity problems reported by Rust users, which makes reproducible failure-finding strategically valuable.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The ecosystem already has meaningful building blocks at different scales:
  - Loom for concurrent execution exploration,
  - Shuttle for deterministic schedule reproduction,
  - Tokio paused time for async tests,
  - Turmoil for host/time/network simulation,
  - MadSim for runtime-level simulation,
  - Moonpool for fault-injecting multi-seed exploration.
  https://docs.rs/loom/latest/loom/
  https://docs.rs/shuttle/latest/shuttle/
  https://docs.rs/tokio/latest/tokio/time/fn.pause.html
  https://tokio.rs/blog/2023-01-03-announcing-turmoil
  https://github.com/madsim-rs/madsim
  https://docs.rs/moonpool_sim/latest/moonpool_sim/
- Because those tools already exist, the high-leverage contribution is a **shared artifact + orchestration layer**, not a replacement runtime.

## Non-goals
- Replacing Loom, Shuttle, Turmoil, MadSim, or Tokio
- Claiming all backends provide identical determinism guarantees
- Building a mandatory hosted service
- Solving full formal verification or model checking in one kit

## Strategic value
This is a worthy contribution because it helps teams answer practical questions with **portable evidence**:
- “Can we reproduce this timeout/partition bug with one seed?”
- “Did our retry logic survive the same failure model across revisions?”
- “Which failures were explored in CI, and which were not?”
- “Did this flaky test actually become deterministic?”

That leverage is broad: async libraries, network services, databases, storage systems, and infra crates all benefit, while the current ecosystem still makes teams choose between incompatible harnesses and ad hoc scripts.

## Milestones
1. **v0 schemas + replay path**
   - seed/config/report/pack
   - one reference backend pair
2. **v0.2 histories + CI gating**
   - history streams
   - backend capability descriptors
   - policy/gate semantics
3. **v1 ecosystem convergence**
   - more adapters
   - shrink/reduce hooks
   - attachments into Replay/Fuzz/Cargo report workflows
