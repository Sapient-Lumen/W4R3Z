# Dependency lifecycle transition product plan — 2026-03-23

## Purpose

This note turns **P-0535 Dependency Lifecycle Transition Kit** into a more concrete product plan.

The core idea is simple:

> a worthy crate here should help another team live through dependency change over time, not just capture one static posture.

## Product idea in one sentence

A first useful **P-0535** should emit **transition review packets** that connect:
- the currently frozen basis,
- the current dependency anchor,
- newly imported external signals,
- re-resolution risk,
- and the team’s next posture decision.

## Why now

The current Rust substrate and ecosystem pressures fit this much better than they did even a year ago.

Signals that matter:
- Rust users still struggle with crate choice, trust, and uneven domain maturity.
- Safety-critical users explicitly describe “use early, narrow or replace later” dependency patterns.
- Cargo is moving toward richer programmatic plumbing and build-analysis surfaces.
- Cargo semver-checks work is explicitly about stronger change discipline in publishing.
- crates.io trust surfaces are stronger, but do not settle architecture placement.
- alternate registries and older Cargo versions remain part of the risk picture.

That means the missing crate is not “just another dependency audit”.
It is a **reviewable transition control plane**.

## Receiver cohorts

### 1. Platform architect
Needs one artifact saying which third-party crates are still acceptable in each lane and what containment exists.

### 2. Release / build engineer
Needs one artifact saying whether the currently green build depends on lock-only posture, local overrides, alternate registries, or other fragile anchors.

### 3. Regulated / safety-heavy adopter
Needs one artifact saying what remains external, what is contained, what is planned for replacement, and what evidence still requires manual review.

### 4. Staff maintainer / reviewer
Needs one artifact saying whether a new release, advisory, docs change, or Rust-floor change should reopen review.

## Repeated painful workflows

A good first release should shorten these workflows:

1. “We already chose this dependency last quarter. Does anything force review now?”
2. “We pinned this crate locally. Is that a shared policy or a fragile operator trick?”
3. “This crate is fine in tools and sidecars, but not in our control core. Can we prove containment?”
4. “A new release exists. Are we still intentionally staying behind, or have we just drifted?”
5. “An advisory or trust signal changed. Does it force a transition, or just refresh a note?”

## First usable release contract

A credible `0.1.0` should support:
- one workspace,
- one restricted lane,
- one shared or local anchor story,
- one imported-signal refresh,
- one transition packet,
- and one explicit manual-review ceiling.

It should not try to automatically replace dependencies or infer global architecture truth.

## Proposed artifact family

### Core packet
- `transition-review-packet.manifest.json`

### Basis / anchor lane
- `basis-lock.manifest.json` (imported, not reinvented)
- `selection-anchor.receipt.json`
- `reresolution-risk.report.json`

### Policy / review lane
- `transition-plan.manifest.json`
- `replacement-readiness.report.json`
- `abstraction-seam.receipt.json`
- `criticality-boundary.report.json`
- `dependency-exception.ledger.json`

### Refresh / signal lane
- `imported-signal.receipt.json`
- `signal-freshness.report.json`
- `exception-reevaluation.report.json`
- `decision-revalidation.report.json`
- `lifecycle-drift.diff.json`

### Human-facing lane
- `transition-summary.md`
- `manual-gap.note.md`

## Suggested packet semantics

### `transition-review-packet.manifest.json`
This should answer:
- what package or dependency family is under review,
- what prior decision or basis lock it references,
- what trigger opened the review,
- what disposition the team chose,
- and which detailed supporting artifacts back that choice.

Suggested dispositions:
- `keep_with_refresh`
- `contain_further`
- `pin_and_monitor`
- `replace_planned`
- `vendor_or_fork`
- `manual_review_required`

### `decision-revalidation.report.json`
This should answer whether the old choice still stands under the **same task and policy**.
It should not silently smuggle in a new task profile.

### `selection-anchor.receipt.json`
This should keep checked-in policy separate from local-only hacks.
Examples:
- lockfile
- root manifest patch
- config-only patch
- source replacement
- git revision pin
- manual operator step

### `reresolution-risk.report.json`
This should answer what happens if the lockfile is refreshed, the Rust floor changes, or the selected registry path changes.

## Suggested CLI shape

```text
cargo dep-lifecycle capture --workspace . --emit out/current
cargo dep-lifecycle refresh --basis-lock out/current/basis-lock.manifest.json --emit out/refresh
cargo dep-lifecycle transition-review --dependency foo --trigger advisory,new_release --emit out/transition
cargo dep-lifecycle diff old/transition-review-packet.manifest.json new/transition-review-packet.manifest.json
```

The important part is not the exact flags.
It is the packet family:
**capture → refresh → transition-review → diff**.

## What this crate should provide other people

For another team, this crate should provide:
- a **shared transition packet** instead of local folklore,
- a clear **anchor story** instead of “it works on my machine,”
- a clear **revalidation result** instead of re-deciding from scratch every time,
- a clear **transition posture** instead of vague “replace later” promises,
- and a clear **manual-review ceiling**.

## Non-claims

This crate should not claim:
- that trust signals settle architecture fit,
- that one green lockfile implies future clean-resolve durability,
- that a local patch equals a shared policy,
- that advisories or new releases always force replacement,
- or that seam presence alone proves replacement is easy.

## Best immediate implementation hooks

The most credible narrow hook is:
- import `basis-lock.manifest.json` from **P-0536**,
- import current graph/topology facts from Cargo,
- emit one `transition-review-packet.manifest.json`,
- and keep everything else as supporting receipts.

That is small enough for `0.1`, but still useful.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
