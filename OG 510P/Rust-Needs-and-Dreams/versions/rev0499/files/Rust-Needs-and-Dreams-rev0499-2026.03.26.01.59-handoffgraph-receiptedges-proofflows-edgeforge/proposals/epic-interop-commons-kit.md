# Epic proposal: Interop Commons Kit

## Thesis
Rust’s ecosystem is broad enough that one of the highest-leverage missing contributions is no longer another framework for each domain.
The higher-leverage missing piece is a **portable interop-commons contract** that lets the ecosystem identify, specify, validate, and ship neutral shared building blocks: common types, traits, adapter rules, and conformance vectors that make otherwise independent libraries compose.

In other words: Rust needs a boring, attachable `commons-pack/v0` more than it needs another wave of incompatible “unifying” abstractions.

## Why now
The ecosystem signals line up:
- Rust’s own vision work says smoother interop is part of the answer to ecosystem navigation and explicitly points at interop traits and standard building blocks.
- The same vision work notes that coherence rules currently make incremental ecosystem interop traits hard.
- Async project-goal updates say the next generation of async libraries has been blocked on stable solutions for async traits and streams.
- The `http` crate already demonstrates the value of a neutral shared vocabulary for a major domain.
- Tower’s `Service`/`Layer` pair and `tower-http` show that stable integration points can unlock middleware sharing across many stacks.
- `axum` and `tonic` both demonstrate real reuse from those common seams.
- Cargo’s development updates keep stressing that plugins matter, which is a strong argument that ecosystem-side companion infrastructure can and should carry real weight here instead of waiting for a standard-library or Cargo monolith answer.

That means the missing substrate is not raw capability.
It is the **reviewable path for creating and validating shared ecosystem seams**.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- https://blog.rust-lang.org/2025/04/08/Project-Goals-2025-March-Update/
- https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- https://docs.rs/http
- https://docs.rs/tower
- https://docs.rs/tower-http
- https://docs.rs/axum/latest/axum/
- https://docs.rs/tonic/latest/tonic/service/index.html
- https://docs.rs/tonic/latest/tonic/transport/server/struct.Server.html

## What should be built
A first credible version should ship:
1. `interop-seam/v0`, `shared-building-block/v0`, `adapter-profile/v0`, `conformance-vector-set/v0`, `adoption-profile/v0`, `seam-readiness-report/v0`, `interop-check-report/v0`, and `commons-pack/v0`
2. reference adapters and examples for at least one already-proven seam (`http` / `http-body` / Tower-style service layers)
3. a readiness process for deciding whether a new seam is ready for a common layer or should remain a crate-specific concern
4. docs/reference generation for seam scope, semantics, adapter limitations, and tested combinations
5. CI examples showing conformance vectors run across multiple crates/versions
6. at least one Atlas integration pilot showing how a reference stack can point to a real shared building block rather than vague “these crates compose well” prose

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s shared seams legible together rather than replace every framework with a facade.

## Initial pilots
- one HTTP request/response/body pilot centered on `http` plus body adapter truth
- one Tower service/layer pilot proving middleware reuse and shared integration points across Axum/Hyper/Tonic-style stacks
- one seam-readiness pilot for a currently awkward area (likely async borrowing / sequence interop) that explicitly records why the ecosystem is not ready yet or what language/tooling blockers remain
- one Atlas integration pilot showing how a reference stack can point to a real shared building block rather than vague “these crates compose well” prose

Treat [`design/interop-commons-pilot-program.md`](../design/interop-commons-pilot-program.md) as the ranked execution anchor so commons work does not jump from abstract schemas straight to premature ecosystem standardization.

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve seam identity, neutral-core semantics, and adapter honesty
2. **v0.2 adapters + vectors**
   - ship HTTP/Tower-based pilots
   - run conformance vectors across multiple adopters
3. **v0.3 readiness + governance depth**
   - add seam-readiness reports and adoption/stewardship profiles
   - support diffing and migration notes across common-layer versions
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one exact framework stack

## Success metrics
- Teams can review a proposed shared seam as explicit artifacts instead of only issue threads and intuition.
- New crates/frameworks can plug into proven shared seams faster.
- Adapter costs and lossy edges become easier to see before integration work begins.
- Ecosystem guidance becomes more stable because Atlas/recommendation systems can point to actual common vocabulary.
- Rust avoids some future fragmentation by creating neutral shared layers only when evidence supports them.
- The system can clearly say “not ready yet” for one promising seam without treating that as failure.

## Archive fit
This proposal fills a real gap between existing archive kits:
- **Ecosystem Atlas Kit** handles guidance and reference stacks,
- **Build Interop Kit** handles build/workspace/plumbing boundaries,
- **Service/Protocol/Event/Identity/etc. kits** handle domain-specific surfaces,
- **Semantic Context Kit** helps tools harvest machine-usable facts,
- and **Runtime Capability / Policy / Support / Lifecycle proposals** handle runtime, governance, and evidence concerns.

But none of those is the portable contract for the **common vocabulary layer between competing crates**.
Interop Commons Kit is the missing substrate that lets Rust create and review shared building blocks deliberately instead of by folklore, inertia, or premature standardization.
