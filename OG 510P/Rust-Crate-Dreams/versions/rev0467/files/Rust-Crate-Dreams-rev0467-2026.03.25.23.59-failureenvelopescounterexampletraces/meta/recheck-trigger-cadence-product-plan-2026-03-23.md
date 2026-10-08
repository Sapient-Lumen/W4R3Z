# Recheck trigger / cadence product plan — 2026-03-23

## Purpose

This note turns the practical seam between **P-0509 Pathfinder**, **P-0536 Crate Knowledge Pack**, and **P-0535 Dependency Lifecycle Transition Kit** into a more concrete product plan.

The point is not to invent another generic monitoring service.
The point is to define the smallest honest crate surface that tells another team:
- what changed,
- why they should look again,
- what packet opens next,
- and what still requires manual review.

## Product idea in one sentence

A first useful implementation should emit **trigger-intake receipts** and **recheck tickets** that connect frozen basis locks to later review packets without silently replacing the old answer.

## Why now

The current Rust substrate makes this much more believable than it used to be.

Signals that matter:
- `cargo metadata` has a stable, versioned format and explicitly warns consumers to pass `--format-version`.
- Cargo’s external-tools reference documents JSON build messages and says build scripts can report native-dependency results there.
- Cargo build-analysis planning is explicitly about persisting rebuild reasons, CLI context, and per-run identifiers so later analysis is possible.
- crates.io now records `pubtime`, which supports cooldowns and “as-of” replay.
- crates.io also exposes a Security tab, but that still does not settle task fit or posture.
- crates.io intentionally reduced routine malware blog-post noise, which means teams need their own local refresh discipline instead of waiting for public broad announcements.
- docs.rs now exposes structured build rules, targets, metadata knobs, and rustdoc JSON that can shift a support story over time.
- Cargo is actively asking users to test build-dir layout changes because many tools still rely on internal details.

Together, that means a worthy crate can now standardize **when to review** almost as well as it standardizes **what to review**.

## Receiver cohorts

### 1. Platform / architecture lead
Needs a compact ticket showing which frozen crate choice needs attention and why.

### 2. Release / build engineer
Needs a signal that distinguishes “informative substrate drift” from “urgent review because the current route may no longer be supportable”.

### 3. Security / trust reviewer
Needs one object separating imported advisories and trust signals from the actual posture decision.

### 4. Regulated or safety-heavy adopter
Needs a shared queue of review openings so later evidence updates do not disappear into local folklore.

## Repeated painful workflows

A good first release should shorten these workflows:

1. “A new version exists. Is that merely informative or does it force review?”
2. “The docs.rs/default-target/build story changed. Does this affect our frozen task fit?”
3. “A RustSec advisory landed. Is the result refresh-only, or do we open a transition packet now?”
4. “Cargo/build-dir/toolchain substrate changed. Which packets are now suspect?”
5. “We have a local incident or failing CI path. How do we open a shared review packet instead of writing Slack lore?”

## First usable release contract

A credible `0.1.0` should support:
- one frozen pathfinder decision,
- one imported basis lock,
- one watch/cadence policy,
- one trigger-intake receipt,
- one recheck ticket,
- one later revalidation packet,
- and one explicit manual-review ceiling.

It should not try to become a hosted dashboard, a vulnerability scanner, or an auto-remediation bot.

## Proposed artifact family

### Intake lane
- `trigger-intake.receipt.json`
- `signal-import.receipt.json`
- `packet-cadence.policy.json`

### Ticket lane
- `recheck-ticket.manifest.json`
- `basis-delta.report.json`
- `ticket-priority.report.json`

### Review handoff lane
- `decision-revalidation.report.json` (import / reuse)
- `transition-review-packet.manifest.json` (open only when needed)
- `manual-gap.note.md`

## Suggested semantics

### `trigger-intake.receipt.json`
This should answer:
- what signal was observed,
- where it came from,
- when it was observed,
- which frozen packet or dependency family it touches,
- and whether the signal is merely informative or opens a real review.

Important rule:
**trigger intake is not posture.**
It records facts and triage class, not the final architectural answer.

### `recheck-ticket.manifest.json`
This should answer:
- which frozen basis lock or decision packet is being revisited,
- what trigger set opened the ticket,
- who should look,
- what the next packet family is,
- and whether the recommended path is:
  - keep and record,
  - rerun comparison,
  - open transition review,
  - or manual review required.

### `packet-cadence.policy.json`
This should answer:
- which surfaces are watched,
- what cadence applies,
- which classes are urgent,
- which classes are batched,
- and what dedupe/coalescing rules keep repeated signals from becoming noise.

### `basis-delta.report.json`
This should summarize the difference between:
- the frozen basis,
- the newly imported facts,
- and the parts still unknown.

It should not pretend to settle whether the old choice still stands.
That belongs to revalidation or transition review.

## Suggested trigger classes

The first release only needs a small trigger vocabulary:
- `new_release`
- `advisory`
- `docs_surface_shift`
- `support_surface_shift`
- `build_substrate_change`
- `target_or_msrv_shift`
- `local_incident`
- `manual_recheck_request`

The point is not to be exhaustive.
The point is to stop later passes from calling every new fact “fresh data” without saying what kind.

## Suggested CLI shape

```text
cargo pathfinder trigger-import --basis-lock out/basis-lock.manifest.json --emit out/intake
cargo pathfinder open-recheck --intake out/trigger-intake.receipt.json --emit out/ticket
cargo pathfinder revalidate --ticket out/recheck-ticket.manifest.json --emit out/revalidation
cargo dep-lifecycle transition-review --ticket out/recheck-ticket.manifest.json --emit out/transition
```

The exact flags can change.
The important part is the sequence:
**intake → ticket → revalidate → transition-if-needed**.

## What this crate should provide other people

For other people, this crate should provide:
- a **typed review opening** instead of vague “we should revisit this” chatter,
- a **shared cadence policy** instead of tribal memory,
- a **basis delta** instead of forcing a full re-compare every time,
- a **clear handoff** into revalidation or transition packets,
- and an explicit **manual-review ceiling**.

## Non-claims

This crate should not claim:
- that every new release deserves adoption,
- that every advisory implies replacement,
- that docs/build/support shifts automatically overturn task fit,
- that public trust surfaces settle architecture placement,
- or that a local signal stream is equivalent to universal registry monitoring.

## Best immediate implementation hooks

The narrowest believable `0.1` is:
- import one frozen `basis-lock.manifest.json` from **P-0536**,
- import one current signal set from Cargo/docs.rs/crates.io/RustSec-facing surfaces,
- emit one `trigger-intake.receipt.json`,
- emit one `recheck-ticket.manifest.json`,
- and stop there unless a human opens `decision-revalidation` or `transition-review`.

That is small, but already useful.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
