# Epic crate receiver-value bar — 2026-03-23

This note sharpens a recurring archive question:

> What should a worthy crate provide **other people**?

The archive already had a contribution bar and delivery cards.
This note adds a stricter receiver-facing test.

## Main judgment

A crate should not be considered “epic” just because it is broad, technically interesting, or strategically phrased.
It should be considered epic when it gives a real downstream person a **portable review packet** they can use later.

## The five receiver classes

A serious crate should usually help at least **two** of these classes.

### 1. The adopter
This person is choosing a stack, tool, or migration route.

**Useful outputs:**
- `decision-brief.md`
- `starter-set.bundle.json`
- `manual-review.note.md`

### 2. The maintainer or support engineer
This person is responding to failures, questions, or support promises.

**Useful outputs:**
- `doctor.report.json`
- `support-bundle.manifest.json`
- `claim-ceiling.report.json`

### 3. The reviewer or approver
This person needs to check whether a claim is justified.

**Useful outputs:**
- `capability-witness.report.json`
- `parity-gap.report.json`
- `override-authority.receipt.json`
- `candidate-elimination.receipt.json`

### 4. The operator or integrator
This person keeps real systems working across environments.

**Useful outputs:**
- `external-prerequisite.report.json`
- `target-support.receipt.json`
- `native-resolution.report.json`
- `reresolution-risk.report.json`

### 5. The tool or assistant consumer
This is a machine surface: internal tooling, CI automation, knowledge systems, or assistants.

**Useful outputs:**
- `assistant-context.pack.json`
- `claim-trace.report.json`
- `citation-locator.receipt.json`
- `query-support.matrix.json`

## What passes the bar

A worthy crate contribution usually has these properties:

1. **named receivers** — it knows who benefits;
2. **portable artifacts** — its outputs can travel outside the original machine;
3. **review value** — a human can inspect what it says later;
4. **manual-review zones** — it knows when not to automate;
5. **refusal boundaries** — it knows what it cannot prove.

## What fails the bar

These ideas often sound good but fail the receiver-value test if they stop here:
- a ranking page with no frozen packet,
- a chat shell with no pinned evidence bundle,
- a wrapper crate with no support or migration packet,
- a dashboard with no diffable exports,
- a “helper” that hides the constraints it decided for you.

## Applying the bar to the current top frontier

### P-0509 Pathfinder
Passes because it can give adopters, reviewers, and future maintainers the same decision packet.

### P-0486 Debuggability Support
Passes because it can give maintainers and reviewers honest capability packets instead of folklore.

### P-0472 Docs.rs Build Parity
Passes because it can give maintainers and reviewers a concrete parity issue bundle.

### P-0538 Concurrency Contract
Passes when it ships scenario bundles and semantic evidence reports; fails if it becomes only an abstraction taxonomy.

### P-0536 Crate Knowledge Pack
Passes when it gives pinned, cited, target-aware machine bundles; fails if it becomes generic “crate chat.”

## Promotion rule

Before promoting a proposal, ask:

1. who receives value,
2. what file or packet they get,
3. what workflow the packet shortens,
4. what the crate refuses to claim,
5. whether the packet still matters six months later.

If the answers stay weak, do not promote it.

## Sources
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
