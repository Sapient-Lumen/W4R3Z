# Epic crate delta and carry-forward doctrine — 2026-03-25

This note answers the practical question:

**What should a worthy crate provide other people when something changes, so they do not have to rereview everything from zero?**

## Core claim

A worthy crate should increasingly provide a **delta contract**.
That contract sits above raw evidence, conformance claims, policy verdicts, review packets, and renewal reminders.
It tells a downstream team:
- what class of change occurred,
- what still carries forward,
- what must be replayed,
- what must be downgraded or reset,
- and how the new result supersedes the old one.

## What the crate should provide other people

### 1. A named change-class vocabulary

The crate should not emit only “changed”.
It should classify changes into review-meaningful buckets.
A useful first vocabulary is:
- `documentation-basis`,
- `build-substrate`,
- `public-api`,
- `target-support`,
- `source-route-parity`,
- `advisory-or-trust`,
- `policy-only`,
- `unknown-manual-review`.

Without a named change class, every rerun becomes a bespoke interpretation exercise.

### 2. A carry-forward decision

A worthy crate should explicitly say whether prior conclusions:
- carry forward unchanged,
- carry forward with downgrade,
- require one narrow rerun slice,
- or require confidence reset and manual review.

This is stronger than just “due” or “stale”.
It tells the downstream team how much of the old packet remains meaningful.

### 3. A minimum rerun slice

A worthy crate should not default to “rerun everything”.
It should define the **smallest honest replay** for each change class.

Examples:
- docs.rs metadata/default-target change → rerun docs/build/target basis slice first;
- advisory or alternate-registry route change → rerun parity and trust slice first;
- public API or semver warning → rerun boundary and review packet slice;
- debugger upgrade on one tuple → rerun only that tuple’s corpus slice.

### 4. A supersession diff

A worthy crate should not replace old packets with a silent overwrite.
It should emit a compact **supersession diff** that says:
- which packet or summary it supersedes,
- what changed materially,
- which prior sections still carry,
- and which sections were reopened or invalidated.

### 5. A confidence-reset record

Some changes are too large or too ambiguous for cheap carry-forward.
The crate should expose a stable record for:
- “no honest carry-forward”,
- “confidence reset”,
- “manual review required”,
- or “old result retired pending new basis”.

This prevents quiet optimism.

### 6. A short human delta summary

Most teams do not want to diff every JSON blob by hand.
The crate should provide a short summary that says:
- what changed,
- what stayed invariant,
- what is newly uncertain,
- what was rerun,
- and what now supersedes the prior result.

### 7. A refusal boundary

The crate should refuse to:
- infer support carry-forward across unknown route or parity changes,
- flatten prototype substrate movement into stable semantic equivalence,
- treat policy-only edits as evidence refresh,
- or silently reuse prior approvals when the change class is unknown.

## Release ladder

### Honest `0.1`
- one narrow receiver,
- three or four change classes,
- one carry-forward decision vocabulary,
- one rerun-slice object,
- one supersession diff,
- explicit reset / manual-review states.

### Honest `0.3`
- multiple change classes,
- imported review and renewal context,
- narrow basis diffs plus reopened-section mapping,
- profile overlays such as `ci-minimal`, `enterprise-offline`, `safety-case`.

### Honest `1.0`
- stable change-class semantics,
- stable carry-forward vocabulary,
- stable supersession diff semantics,
- clear cross-tool import/export routes,
- and narrow enough boundaries that organizations can wrap their own policy around it.

## Package topology in practice

A delta-worthy crate family will often want:
- one **CLI** for diff / rerun-slice / carry-forward operations,
- one **core library** for change classification and slice planning,
- one **schema crate** for delta packet types,
- bounded **adapter crates** for docs.rs / crates.io / Cargo / local receipts,
- and one **scenario corpus** for carry-forward, reset, and supersession behavior.

This should stay a small suite, not a policy engine.

## Why this doctrine matters now

The official Rust substrate is getting more machine-usable, and official tooling work increasingly cares about **what changed enough to matter**:
- SemVer checking is being pushed toward `cargo publish`,
- build analysis explicitly explains why crates rebuilt,
- relink-don't-rebuild is about avoiding unnecessary blast radius,
- default target and build-dir changes show substrate drift can selectively invalidate old conclusions,
- and StableMIR points toward more durable analysis surfaces.

That means the archive should not only ask “can we renew this?”
It should ask:

**can another team tell exactly what changed, preserve what still stands, and rerun only the slice that became uncertain?**

That is why delta and carry-forward now deserve to be first-class in the repo.
