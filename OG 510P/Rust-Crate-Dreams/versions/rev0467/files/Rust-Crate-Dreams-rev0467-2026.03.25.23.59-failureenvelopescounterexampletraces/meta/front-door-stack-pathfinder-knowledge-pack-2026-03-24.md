# Front-door stack — Pathfinder + Crate Knowledge Pack (2026-03-24)

This note answers a practical repo question:

> if we only deepen one coupled product seam next, which pair of crates should be designed together?

## Main judgment

The answer is:
- **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**, and
- **P-0536 Crate Knowledge Pack Kit**.

These should now be treated as the archive’s **front-door stack**.

Not because they are the same crate.
But because the first real packet another engineer receives is usually:
1. a decision packet,
2. backed by a pinned review packet.

Without both, the value blurs.

## Why this pairing matters

### Pathfinder without knowledge packs drifts
A pathfinder packet can look good while still depending on:
- floating docs.rs `latest` routes,
- target-blind links,
- weak citation basis,
- stale README snippets,
- or support claims that cannot be reopened later.

### Knowledge packs without pathfinder stay too abstract
A crate knowledge pack can be technically rich but still fail to answer:
- which decision this evidence supported,
- which alternatives were ruled out,
- what starter set was chosen,
- and when the team should revisit that choice.

So the front door is strongest when these two crates are designed as adjacent packet producers.

## Receiver workflows

### Workflow 1 — stack selection
Receiver:
- staff engineer, maintainer, consultant, or platform lead.

P-0509 provides:
- `decision-brief.md`
- `starter-set.bundle.json`
- `candidate-elimination.receipt.json`

P-0536 provides:
- `review-packet.manifest.json`
- `citation-locator.receipt.json`
- `query-support.matrix.json`
- `answer-boundary.note.md`

Result:
- the receiver gets both the answer and the pinned support basis.

### Workflow 2 — ADR / review board
Receiver:
- architecture reviewer, principal engineer, platform committee.

P-0509 provides:
- the frozen decision packet.

P-0536 provides:
- claim traces, materials basis, and manual-review zones.

Result:
- the reviewer can reopen the packet without needing a search expedition.

### Workflow 3 — later re-evaluation
Receiver:
- long-lived team or regulated adopter.

P-0509 provides:
- re-entry policy and as-of replay posture.

P-0536 provides:
- pinned locators and version-aware review packet members.

Result:
- a future pass can compare what changed without silently swapping in new authority surfaces.

## What each crate should provide other people

### P-0509 Pathfinder should provide
- a small decision packet,
- a frozen starter-set shape,
- elimination and re-entry logic,
- revisit triggers,
- and adoption checklists.

### P-0536 Crate Knowledge Pack should provide
- the pinned review packet that makes the above decision packet auditable,
- answerability and citation ceilings,
- materials basis and claim traces,
- and compact machine-facing slices that remain honest about exclusions.

## Narrow `0.1` build plan

### Step 1 — lock the packet handshake
Define how a pathfinder packet references a knowledge review packet.
Do not build a big service.
Just freeze the handoff.

### Step 2 — pilot in scenario packs already in the repo
Best early proving grounds:
- desktop GUI
- Wasm component / plugin host
- mixed-language interop
- safety-critical boundary stacks
- air-gapped enterprise stacks

### Step 3 — keep debugging next in line
Once the front-door packet handshake is stable, the next lane to align is **P-0486** so debug capability packets use the same bundle semantics.

## What this pairing should refuse to claim

The front-door stack must refuse to claim:
- that it can choose a crate for all teams forever,
- that a pinned packet replaces experimentation,
- that a citation-ready packet makes performance/security/safety answers automatic,
- or that docs.rs and crates.io surfaces alone settle task fit.

## Product rule

If the archive cannot show how a pathfinder packet and a knowledge review packet fit together, then its top practical queue is still under-specified.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
