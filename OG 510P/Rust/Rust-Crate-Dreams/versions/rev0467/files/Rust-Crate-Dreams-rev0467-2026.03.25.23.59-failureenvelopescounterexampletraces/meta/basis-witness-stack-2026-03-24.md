# Basis witness stack — 2026-03-24

## Why this note exists

The archive keeps converging on packet-producing crates.
That makes one question increasingly important:

> when a crate emits a decision packet, review packet, doctor report, or support contract, what exact evidence-bearing basis is it standing on?

Current Rust substrate is finally rich enough that the archive should stop saying “grounded” in the abstract and start naming concrete witness layers.

## The basis witness stack

A worthy packet-producing crate should think in terms of a **basis witness stack**.
Not every crate needs every layer, but the top front-door lanes should use most of them.

### 1. Workspace topology witness

Purpose:
- say what package graph and target filter the packet was reasoning about.

Suggested sources:
- `cargo metadata --format-version 1`
- `cargo metadata --filter-platform <triple>` when target-specific reasoning matters

Good emitted artifact:
- `workspace-topology.receipt.json`

Why this matters:
- Cargo explicitly treats `cargo metadata` as a machine-readable surface and recommends callers pass `--format-version` explicitly.
- The output can be filtered by target, which means a packet should stop pretending that one dependency graph always speaks for all targets.

### 2. Build witness

Purpose:
- show what the build actually produced or declared, including build-script side channels.

Suggested sources:
- Cargo `--message-format=json`
- build-script result messages

Good emitted artifact:
- `build-witness.receipt.json`

Why this matters:
- Cargo’s external-tools docs say the JSON stream includes compiler messages, produced artifacts, and build-script results such as native dependency information.
- This is a much stronger basis than trying to infer build behavior from file layout or ad hoc log scraping.

### 3. Hosted docs witness

Purpose:
- say what documentation surface was actually in scope for the packet.

Suggested sources:
- docs.rs rustdoc JSON
- docs.rs metadata recipe
- docs.rs hosted-build caveats and target settings

Good emitted artifacts:
- `docs-witness.receipt.json`
- `citation-locator.receipt.json`
- `conditioned-availability.report.json`

Why this matters:
- docs.rs hosts rustdoc JSON and says the format version matters.
- docs.rs also exposes build metadata and hosted-build constraints.
- A packet that cites docs without saying which hosted surface or recipe was used is weaker than it looks.

### 4. Release witness

Purpose:
- pin the release identity another engineer is being asked to review.

Suggested sources:
- registry index entry
- checksum-bearing download route
- `pubtime` when time-window reasoning matters

Good emitted artifact:
- `release-witness.receipt.json`

Why this matters:
- Cargo registry docs define the index and checksum-bearing download model.
- The crates.io development update says `pubtime` is now recorded in index entries and enables time-aware replay use cases.

### 5. Packaged-state witness

Purpose:
- distinguish the crate as published from the crate as casually browsed in a repository checkout.

Suggested sources:
- `cargo package`
- included-file list
- `.cargo_vcs_info.json`

Good emitted artifact:
- `package-witness.receipt.json`

Why this matters:
- `cargo package` builds from a pristine extracted package, checks that build scripts did not modify source files, and includes `.cargo_vcs_info.json` for checkout provenance.
- This is exactly the kind of boundary regulated or long-lived adopters need.

### 6. Imported trust / advisory witness

Purpose:
- keep trust and security signals visible without letting them silently settle task fit.

Suggested sources:
- crates.io Security tab / advisory imports
- trusted publishing posture
- publishing restrictions or provenance signals

Good emitted artifact:
- `trust-surface.import.json`

Why this matters:
- crates.io trust surfaces are increasingly useful, but they are still imported evidence, not proof that a crate is the right choice for a task, target, or lifecycle.

## The artifact family this note recommends

For the top front-door lanes, the archive should prefer a compact family like this:
- `basis-lock.manifest.json`
- `workspace-topology.receipt.json`
- `build-witness.receipt.json`
- `docs-witness.receipt.json`
- `release-witness.receipt.json`
- `package-witness.receipt.json`
- `trust-surface.import.json`
- `answer-boundary.note.md`

The lock should name the basis members, their versions, filters, and known incompletenesses.

## What a worthy crate should provide other people

For this layer, the crate should provide:
- a **reviewable basis lock** another engineer can inspect,
- **witness receipts** that say where the packet got its facts,
- **explicit imports** for upstream trust/advisory signals,
- and an **answer boundary note** explaining what remains manual-review-only.

That is a much more useful gift to another team than “we looked at docs, registry data, and some CI output”.

## Non-claims

This stack should not claim:
- that a captured witness set proves runtime correctness,
- that no target-specific drift exists beyond the chosen filters,
- that trust surfaces settle task fit,
- or that repository state is identical to packaged state unless packaging witnesses say so.

## Recommended next implementation hook

The best immediate hook is **P-0536 Crate Knowledge Pack Kit** with a `basis-lock.manifest.json`, implemented in lockstep with **P-0509 Pathfinder** so decision packets can point to one frozen evidence basis.

## Sources

- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/registries.html
- https://doc.rust-lang.org/cargo/reference/registry-index.html
- https://doc.rust-lang.org/cargo/reference/registry-web-api.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
