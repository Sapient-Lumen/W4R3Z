# Cross-domain receiver needs map — 2026-03-25

This note exists to keep the archive broad without getting vague.

The user asked for extreme variety of use cases and topics.
The right response is not to manufacture one new mega-crate per sector.
It is to compare sectors and ask where the real missing seam still is.

## Reading rule

This note is **not** evidence that every domain is healthy or mature.
It is evidence that many domains already have active centers of gravity,
which means the strongest missing crate may often be cross-cutting and receiver-facing.

## Domain snapshots

### 1. Web backends
Signal:
- AreWeWebYet says Rust has mature production-ready frameworks such as Actix Web and Axum.

Receiver need that still looks missing:
- decision packets for crate/stack choice;
- support envelopes around docs/build/target/runtime expectations;
- continuity packets when dependencies or operational assumptions drift.

### 2. GUI applications
Signal:
- AreWeGuiYet still describes multiple approaches and a fragmented stack picture.
- The March 2026 challenges post says GUI developers especially feel compile-time pain in visual workflows.

Receiver need that still looks missing:
- visual-iteration truth;
- platform/support envelopes;
- debug and repro packets for GUI-specific feedback loops.

### 3. Game development
Signal:
- AreWeGameYet still frames the ecosystem as young but viable enough for experimentation.

Receiver need that still looks missing:
- platform/build/tooling support envelopes;
- asset-pipeline and debug support packets;
- target-specific continuity/recheck truth.

### 4. IDE/editor tooling
Signal:
- AreWeIDEYet shows a wide feature matrix across editors and tooling.

Receiver need that still looks missing:
- receiver-facing capability packets;
- stable support ceilings for debugging, completions, formatting, and docs features;
- evidence-based handoff artifacts for toolchain/editor integration choices.

### 5. Geospatial
Signal:
- GeoRust is an ecosystem of geospatial tools and libraries written in Rust.

Receiver need that still looks missing:
- target/data-format compatibility envelopes;
- maintenance and selection truth across many interrelated crates;
- offline/support continuity packets for operational users.

### 6. Local-first / sync-heavy applications
Signal:
- Automerge positions itself as a local-first sync engine that works offline and mirrors data across clients.

Receiver need that still looks missing:
- storage/network adapter support envelopes;
- offline/reconnect/sync-failure scenario corpora;
- reviewable claims around durability, convergence, and environment support.

### 7. Embedded systems
Signal:
- The Rust challenges post says embedded developers often face constrained resources, difficulty using much of the ecosystem, and harder debugging.

Receiver need that still looks missing:
- no-std / target / resource support envelopes;
- build-std and toolchain truth packets;
- debugging and component-availability ceilings.

### 8. Safety-critical
Signal:
- the January 2026 safety-critical post says tooling for qualification and certification is still maturing;
- the March 2026 challenges post says the biggest issue is the lack of availability or maturity for tools to certify Rust code.

Receiver need that still looks missing:
- bounded evidence packets;
- decomposed support envelopes;
- explicit non-claim language and certification-prep artifacts.

### 9. Rust for Linux / kernel-adjacent work
Signal:
- the Rust-for-Linux goals page emphasizes stable tooling, compiler-version support, and the need for a blessed way to rebuild std.

Receiver need that still looks missing:
- toolchain and compiler-flag support envelopes;
- stable-build witness packets;
- boundary and lifecycle truth for very strict low-level environments.

### 10. Registry / namespace / publication ecosystem
Signal:
- crates.io now has stronger Trusted Publishing controls, SLOC, and `pubtime`;
- goals continue around semver checks, public/private dependencies, open namespaces, and verifiable mirroring.

Receiver need that still looks missing:
- publication/trust continuity packets;
- namespace and API-boundary support envelopes;
- mirror/source parity and lifecycle-transition bundles.

## Cross-domain synthesis

Across all ten domains, the repeated missing seams cluster around:

- choosing crates honestly;
- freezing the basis for a choice;
- explaining hosted/local/target/toolchain reality;
- maintaining the answer over time;
- and handing a bounded packet to the next reviewer.

That is why the archive still keeps control-plane crates in front.

## What would count as epic here?

An epic crate contribution is not necessarily the broadest framework.
It is more likely the crate that can help many very different receivers do one hard thing honestly:

- select,
- verify,
- freeze,
- support,
- recheck,
- or transition

under bounded evidence.

## Practical implication for the repo

Future broad scans should not add a new top-ranked domain lane unless that lane beats the current frontier on:
- receiver value,
- bounded first release,
- evidence import quality,
- and handoff durability.

## Sources

- https://www.arewewebyet.org/
- https://areweguiyet.com/
- https://arewegameyet.rs/
- https://areweideyet.com/
- https://georust.org/
- https://automerge.org/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rust-lang.github.io/rust-project-goals/2025h1/open-namespaces.html
- https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- https://rust-lang.github.io/rust-project-goals/2025h2/pub-priv.html
