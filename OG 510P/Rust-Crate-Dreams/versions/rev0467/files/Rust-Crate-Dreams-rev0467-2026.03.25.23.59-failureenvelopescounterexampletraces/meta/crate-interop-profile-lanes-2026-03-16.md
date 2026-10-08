# Crate interop profile lanes — shared ecosystem profiles, producer-side contracts, task-first selection, and trait-evolution neighbors (2026-03-16)

The archive now has enough adjacent crate-ecosystem ideas that future passes could easily flatten them into one fake “interop solved” story.
This note exists to keep the missing-crate story honest.

## Main distinction

The new **crate interop profile pack lane** is about a **shared, versioned ecosystem contract** for how multiple crates meet at a library boundary.
It is not the same lane as producer-side capability contracts, task-first crate selection, trait-evolution planning, or general semver linting.

## Separate lanes to keep distinct

### 1. Crate interop profile pack lane (**P-0511**)

Question answered:
- “What does it mean to participate in this library ecosystem lane, and can we verify that one crate or crate pair actually does?”

Primary artifacts:
- `interop-profile-pack`
- `static-conformance.receipt`
- `behavioral-probe.report`
- `pair-compatibility.report`
- `migration-hazards.report`

This lane should own:
- shared profile vocabularies for library ecosystems
- required public traits/types and forbidden public coupling
- provider/consumer pair checks
- profile-pack drift and migration hazards
- profile-scoped behavioral probes when static checks are insufficient

This lane should **not** own:
- crate ranking or starter-set choice
- one crate’s whole support contract
- raw semver witness generation by itself
- language-feature migration planning by itself
- domain-protocol conformance suites

### 2. Producer-side capability contract lane (**P-0510**)

Question answered:
- “What does this crate claim to support or expose, what can tools observe, and where do those differ?”

A capability contract may reference interop ecosystems like `serde`, `http`, or `tower-service`.
But it does **not** define the whole shared profile pack for those ecosystems.
P-0510 is producer-side truth.
P-0511 is shared ecosystem contract truth.

### 3. Task-first decision-pack lane (**P-0509**)

Question answered:
- “Given this task and these constraints, which crates are the best candidates and why?”

P-0509 may import profile-pack results.
It should not become the place where the ecosystem’s reusable profile definitions live.

### 4. Trait evolution and customization-point migration lanes (**P-0449** and **P-0452**)

Questions answered:
- “How can a library evolve a trait hierarchy without breaking everyone?”
- “How can a crate expose or migrate a customization point cleanly?”

These lanes are about **changing or introducing extension points**.
P-0511 is about **checking whether ordinary crates line up at an existing ecosystem boundary**.
Do not collapse trait-supertrait migration planning or EII adoption into profile-pack conformance.

### 5. Public-API / semver slice tools

Question answered:
- “Did this public API change in a semver-breaking way?”

Tools like `cargo-semver-checks` are adjacent and valuable.
They help detect API drift.
But they do not by themselves define which shared ecosystem profile a crate is trying to satisfy, or whether two crates actually meet the same boundary.

### 6. Domain-specific protocol conformance kits

Question answered:
- “Did this crate/system conform to protocol or specification X?”

Those kits target standards like FHIR, OpenADR, EBICS, or DASH.
P-0511 is narrower and more general: library-ecosystem interop *inside Rust*.

## Recommended fixture pressure

A serious interop-profile-pack proposal should include at least four scenario types:

1. **Runtime-neutral async public API**
   - internal Tokio use is hidden while public API stays `Future` / `Stream` oriented
2. **HTTP / tower service boundary**
   - request/response/service abstractions are shared without bespoke wrapper lock-in
3. **Serde model boundary**
   - models stay format-neutral even though adapters exist for JSON, YAML, or other formats
4. **Profile drift across releases**
   - a crate silently adds runtime-specific or format-specific coupling

## Recommended archive stance

When future passes propose crate-ecosystem interop work, they must state explicitly whether the new artifact is primarily:

1. a **shared ecosystem interop profile pack**,
2. a **producer-side capability contract**,
3. a **task-first decision pack**,
4. a **trait-evolution or customization-point migration planner**,
5. a **public-API / semver slice tool**,
6. or a **domain-specific protocol conformance kit**.

Do not let the archive silently compress those into one vague “interop support” story.
The sharp missing value is often the **coordination artifact between them**.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://docs.rs/http
- https://docs.rs/tower-service
- https://docs.rs/futures-core/latest/futures_core/stream/trait.Stream.html
- https://docs.rs/serde
