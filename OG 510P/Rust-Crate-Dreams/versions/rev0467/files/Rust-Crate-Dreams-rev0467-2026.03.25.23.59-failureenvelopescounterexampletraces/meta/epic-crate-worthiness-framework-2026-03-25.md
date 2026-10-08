# Epic crate worthiness framework — 2026-03-25

This file answers the archive’s sharper question after the broad territory scan:

> what would count as a worthy, maybe even epic, crate contribution to the Rust ecosystem now?

## Main judgment

A worthy crate is not just:
- broadly useful,
- emotionally appealing,
- or attached to a painful sector.

It should provide a **stable reusable thing** that other people can actually adopt.
In this archive, the strongest such things are usually:
- a **decision family**,
- an **artifact family**,
- an **interop/conformance family**,
- a **transition family**,
- or a **support/evidence family**.

## Ten tests for worthiness

### 1. Receiver test
Can you name the receiving team clearly?
Not “the Rust ecosystem”, but something like:
- teams choosing among service crates,
- maintainers qualifying target support,
- plugin authors shipping cross-host bundles,
- or enterprise teams mirroring sources offline.

### 2. Repeated pain test
Is the pain repeated across many teams, or just dramatic for one project?
A worthy crate removes recurring friction, not a one-off inconvenience.

### 3. Artifact or decision seam test
What durable output does the crate produce?
Examples:
- a receipt,
- a witness bundle,
- a policy pack,
- a conformance report,
- a decision packet,
- a migration bundle,
- or a boundary manifest.

If no durable output exists, explain the decision seam equally clearly.

### 4. Evidence basis test
Can a claim be replayed later?
A worthy crate should have fixtures, reports, example bundles, or explicit basis locks.

### 5. Adoption ladder test
Can a team start small?
The first release should solve one narrow, useful slice without requiring ecosystem-wide buy-in.

### 6. Refusal boundary test
What will the crate explicitly not do?
A strong crate refuses to become a workflow platform, framework replacement, package manager, policy oracle, or giant abstraction umbrella by accident.

### 7. Substitution test
What existing work does it sit beside rather than erase?
A worthy crate should state its relationship to adjacent tools, official surfaces, and sector incumbents.

### 8. Governance honesty test
Could maintainers actually keep the promises this crate makes?
If the crate implies perpetual protocol tracking or universal compatibility, that burden must be explicit.

### 9. Cross-sector leverage test
Would the crate matter in more than one setting, or at least export lessons another setting can reuse?
Horizontal kits score highly here.

### 10. Memory / explanation test
Would another person understand what this crate provides without reading archive history?
If not, the idea is still too foggy.

## What a worthy crate should provide other people

At minimum, it should provide one or more of these:
- **portable artifacts** people can review, store, diff, or pass around;
- **decision outputs** that make choice and re-check less folkloric;
- **interop outputs** that reduce ecosystem boundary pain;
- **transition outputs** that help teams move safely from one posture to another;
- **debug/support outputs** that make promises and limits explicit.

## Strong crate shapes

### A. Control-plane / decision crates
Best when they answer:
- what should we choose,
- why,
- on what basis,
- what changed,
- and what remains uncertain.

### B. Evidence / conformance crates
Best when they answer:
- what was tested or qualified,
- against which fixture or peer,
- with what support ceiling,
- and in what exportable format.

### C. Boundary / transition crates
Best when they answer:
- what interface, dependency, source, or ABI boundary exists,
- what must change,
- how the migration proceeds,
- and which receipts document that movement.

### D. Packaging / shipkit crates
Best when they answer:
- what artifact another team needs,
- how it is bundled,
- what assumptions it encodes,
- and what environments it is honest about.

## Common anti-patterns

Do not promote a proposal merely because it is:
- broad,
- exciting,
- attached to a fast-growing area,
- or frustratingly fragmented.

Especially suspect are:
- giant umbrella crates,
- vague recommendation engines with no replayable basis,
- “one true stack” pitches,
- and crates whose first release would already require solving multiple unsolved governance problems.

## First-release planning rule

For archive purposes, a proposal gets much stronger once it can specify:
1. the first release’s receiver,
2. the first release’s artifact family,
3. a tiny but real adoption path,
4. a refusal boundary,
5. and the first example or fixture set.

That is the minimum bridge from dream to contribution.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://www.arewewebyet.org/
- https://www.areweguiyet.com/
- https://arewegameyet.rs/
- https://github.com/rust-embedded/not-yet-awesome-embedded-rust
- https://automerge.org/
- https://blog.rust-lang.org/inside-rust/2025/11/24/safety-critical-rust-in-2025/
