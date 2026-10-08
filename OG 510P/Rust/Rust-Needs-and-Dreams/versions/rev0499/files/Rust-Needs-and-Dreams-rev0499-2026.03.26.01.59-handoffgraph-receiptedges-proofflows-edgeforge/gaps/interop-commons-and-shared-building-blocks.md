# Gap: interop commons and shared building blocks

## What is missing
Rust increasingly has **good libraries** for the same problem space, but it still lacks a repeatable way to decide when the ecosystem needs a **neutral shared building block** instead of one more incompatible abstraction.

Today there is no standard way to describe, review, and ship:
- which ecosystem seam is mature enough to deserve a shared type/trait crate or common vocabulary,
- which semantics belong in that neutral layer and which should stay framework-specific,
- which adapters between existing crates are lossless, lossy, expensive, blocking, allocation-heavy, or feature-gated,
- which golden vectors or conformance cases should hold across adopters,
- which crates have actually implemented the common boundary,
- and which "interop" proposals are really just attempts to smuggle in one framework's design as the default.

Rust's own vision work now states the problem directly: part of helping users navigate crates.io is enabling **smoother interop**, potentially via key interop traits or standard building blocks, while acknowledging that coherence rules make ecosystem-introduced interop traits difficult to roll out incrementally.

That is a strong sign that the missing contribution is not merely curation.
It is a **disciplined path for creating shared building blocks without freezing the ecosystem too early**.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## The current seam is awkward
Rust already has examples showing that shared building blocks can work:
- the `http` crate explicitly positions itself as a general-purpose library of common HTTP types and says it is intended to be the “standard library” for HTTP clients and servers without dictating implementation,
- Tower says its `Service` and `Layer` traits are key integration points and keeps them in separate crates because stable integration points matter,
- `tower-http` says its middleware uses the `http` and `http-body` abstractions and is therefore compatible with ecosystems like Hyper, Tonic, and Warp,
- `axum` says using `tower::Service` lets it share middleware with Hyper and Tonic,
- and `tonic` explicitly exposes Tower service/layer integration.

So the ecosystem already knows how valuable neutral seams can be.
What it still lacks is the **reviewable artifact family that tells us when to create them, what they promise, how adapters behave, and what has actually been checked**.

Without that, interop still degenerates into one of four bad outcomes:
1. every stack invents its own surface and everyone writes bespoke adapters;
2. one crate becomes “the default” by inertia without explicit scope or stewardship;
3. an over-abstract common layer gets proposed too early and flattens real differences;
4. useful shared seams emerge, but only through folklore, scattered examples, and unofficial migration advice.

Sources:
- https://docs.rs/http
- https://docs.rs/tower
- https://docs.rs/tower-http
- https://docs.rs/axum/latest/axum/
- https://docs.rs/tonic/latest/tonic/service/index.html
- https://docs.rs/tonic/latest/tonic/transport/server/struct.Server.html

## Why this matters
This gap matters because Rust's ecosystem problems are often not "missing one more crate" problems.
They are **coordination and vocabulary** problems.

A good interop-commons layer would help with:
1. **ecosystem convergence without centralization** — multiple stacks can remain distinct while still sharing a common seam;
2. **adapter honesty** — conversions, wrappers, and middleware reuse can state where information is dropped or semantics diverge;
3. **faster experimentation** — new frameworks can compose with existing tooling faster if a neutral seam already exists;
4. **better recommendations** — Ecosystem Atlas-style guidance becomes much stronger when there are real shared building blocks to point at;
5. **maintainer leverage** — shared types/traits reduce duplicated compatibility glue, while still making stewardship and adoption explicit;
6. **future language/library evolution** — when Rust stabilizes features that unblock better interop, the ecosystem needs a prepared path for using them well instead of spawning another wave of incompatible abstractions.

The 2025 async project-goal updates are a strong warning here: the Rust project explicitly says progress toward the next generation of async libraries has been blocked on stable solutions for async traits and streams.
That is exactly the sort of ecosystem seam where a disciplined interop-commons approach matters.

Sources:
- https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- https://blog.rust-lang.org/2025/04/08/Project-Goals-2025-March-Update/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://docs.rs/tower/latest/tower/trait.Service.html
- https://docs.rs/http/latest/src/http/lib.rs.html

## What “good” looks like
A worthy contribution here is **not** another mega-abstraction crate, another universal facade over every framework, or a political process that simply "blesses" winners.

It is a shared interop-commons boundary:
- one `interop-seam/v0` describing the scope, invariants, and boundary of the seam,
- one `shared-building-block/v0` describing the neutral types, traits, errors, metadata, and semantic rules that belong in the common layer,
- one `adapter-profile/v0` describing how a specific crate maps to and from the shared building block,
- one `conformance-vector-set/v0` describing golden cases, edge cases, and invariants that adopters should satisfy,
- one optional `adoption-profile/v0` describing stewardship, versioning, MSRV, feature, and migration posture,
- one `interop-check-report/v0` recording what combinations were actually tested and where lossiness or incompatibility remains,
- and one `commons-pack/v0` bundle for docs, CI, migration notes, ecosystem guidance, and long-term archaeology.

That would let Rust teams treat shared interop seams as **reviewable ecosystem infrastructure** instead of prestige contests or accidental defaults.

## Non-goals
This gap should not be used to:
- flatten domain-specific surface kits (service, protocol, event, identity, dataset, replica, model, media, geospatial) into one giant schema,
- force every ecosystem seam into a single crate family,
- hide real semantic mismatches behind optimistic trait names,
- or relitigate standard-library expansion every time a common crate proves useful.

The job is smaller and more practical:
**identify the seams that merit common ground, make that common ground explicit, and keep adapters and evidence honest.**
