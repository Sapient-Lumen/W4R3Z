# Toolchain & target support authority / docs-surface plan — 2026-03-22

This note deepens **P-0484 Toolchain & Target Support Contract Kit** around a sharper receiver-facing question:

> when a project says “we support this toolchain/target lane”, which parts came from **upstream authority**, which parts are the project’s **own support promise**, what **public docs surface** is actually exposed, and what single **portable bundle** should another engineer review?

## Main judgment

The lane is strongest when it stops flattening three different kinds of truth:

1. **imported upstream authority** — Rust-project target tiers, rustup-supported hosts, docs.rs default-target behavior, Cargo path/config rules;
2. **project-local support class** — what the project itself promises after interpreting those upstream facts;
3. **public docs surface** — what docs.rs metadata and hosted-build posture expose to users even when runtime support remains weaker.

A worthy crate in this lane should therefore promote three more review objects into first-class status.

## New first-class artifacts

### `upstream-support-authority.import.json`

This should capture imported upstream facts that materially shape a support story:

- Rust-project target tier policy or target-status announcements,
- rustup-supported host availability,
- docs.rs default-target behavior and metadata rules,
- Cargo build/target-dir rules that shape artifact routes or host/target scope.

It should explicitly say:

- what source was imported,
- what question the import can answer,
- what it does **not** prove,
- whether the fact can change without a project release,
- and whether local manual review is still required.

The point is to stop a project from pretending that “officially available” means “project-supported”.

### `public-docs-surface.receipt.json`

This should capture what the project is publicly exposing through docs.rs:

- whether docs.rs metadata was explicit or implicit,
- what the effective default target is,
- which targets are built,
- whether defaults were inherited,
- which sandbox/resource limits materially shaped the build,
- and how the docs surface relates to the broader support contract.

This keeps **hosted documentation posture** separate from runtime, test, or device support.

### `toolchain-support-bundle.manifest.json`

The lane now wants one compact portable manifest so another tool or human can consume the support bundle without guessing which receipts are expected.

A good `0.1` bundle manifest should inventory:

- the local support contract,
- imported upstream authority,
- current toolchain/environment receipts,
- public docs surface receipts,
- target-readiness reports,
- exercise-scope and prerequisite manifests,
- topology/route receipts,
- and any manual-review gaps or sensitivity constraints.

## Product stance

Do not turn **P-0484** into:

- an installer,
- a CI matrix generator,
- a docs.rs replay service,
- or a native-build fixer.

The crate should stay **read-first, evidence-first, bundle-first**.

## Receiver-facing value

### For maintainers
Make upstream changes visible when they alter the *interpretation* of a support story:
- a target demotion,
- a docs.rs default-target change,
- a newly available rustup host,
- or a Cargo path rule that changes route/topology meaning.

### For contributors
Show what to install, what the project actually promises, and what docs.rs is publicizing without implying stronger support than exists.

### For downstream integrators
Separate “the target exists upstream” from “this project claims to support it” and from “docs for it are hosted”.

### For regulated and long-lived teams
Produce a portable support pack that can be archived, diffed, and reviewed later without scraping changing upstream services.

## MVP boundaries

### Include
- imported-upstream authority receipts;
- public docs surface receipts;
- portable bundle manifests;
- conservative drift/readiness interpretation.

### Exclude
- automatic CI reconfiguration;
- target promotion/demotion forecasting;
- docs.rs failure reproduction;
- full linker or SDK diagnosis.

## Good first fixture set

1. An implicit docs.rs default target list changes, widening or shifting the visible public docs surface without a project release.
2. rustup offers an official host toolchain, but the project still leaves support class as `unknown`.
3. A portable bundle keeps upstream authority, public docs surface, and local support promises separate so reviewers do not over-read hosted docs or official host availability.

## Sources

- https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
- https://rust-lang.github.io/rustup/overrides.html
- https://doc.rust-lang.org/cargo/reference/build-cache.html
- https://doc.rust-lang.org/cargo/reference/config.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://rust-lang.github.io/rfcs/2803-target-tier-policy.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
