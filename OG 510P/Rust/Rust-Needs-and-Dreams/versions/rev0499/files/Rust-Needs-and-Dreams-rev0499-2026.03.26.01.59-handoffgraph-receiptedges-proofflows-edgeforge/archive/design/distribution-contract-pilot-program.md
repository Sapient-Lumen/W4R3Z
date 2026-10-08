# Design: Distribution Contract Pilot Program (`distribution-contract-pack/v0`, built on `install-pack/v0`)

## Goal
Define the first executable **stack-level composition layer** above the archive’s leaf consumer-install work and producer-side release evidence.

The archive already has strong ideas about:
- what packages were admitted,
- what releases were cut,
- what artifacts were signed,
- and how restricted-network mirrors should behave.

What is still missing is a disciplined way to turn those truths into a portable answer to:
> how should leaf install receipts, signed-binary evidence, release truth, mirror posture, and downstream handoffs compose without pretending they are the same thing?

This pilot program exists to prove that **ordinary install packs, mirror fallbacks, package-manager imports, and restricted-network consumers** can all compose into one stack-level distribution contract without flattening leaf receipts.

## Core artifacts

This pilot now assumes the leaf acquisition/install artifacts come from [`design/consumer-install-kit.md`](./consumer-install-kit.md). The stack-level pilot should therefore focus on composition and handoff above those leaf packs.
### 1) `distribution-contract-brief/v0`
A concise stack-level summary.

Fields:
- imported install-pack ids
- imported release/signature/airgap evidence ids
- selected channel/host/mirror summary
- verification posture summary
- ownership/managed-content summary
- downstream handoff readiness markers

Design rule: this layer summarizes and composes; it does not replace leaf install subjects or receipts.

### 2) `distribution-contract-diff/v0`
Compare multiple install events or imported evidence sets.

Fields:
- compared install-pack / install-receipt ids
- host / mirror / channel differences
- verification differences
- managed-content / ownership differences
- release/signature/airgap import differences
- downstream-impact hints

Design rule: diffs should explain changes without pretending they are already update-continuity verdicts.

### 3) `distribution-contract-handoff/v0`
Bounded export for downstream consumers.

Fields:
- imported install / release / signature / airgap ids
- consumer type (`SUPPORT`, `INCIDENT`, `POLICY`, `INVENTORY`, `ATLAS`, `ASSISTANT`)
- allowed conclusions
- explicit unknowns / lossy imports
- review timestamps and integrity metadata

Design rule: downstream consumers should import stack truth rather than re-scrape logs or hosts.

### 4) `distribution-contract-pack/v0`
Bundle format:
- `distribution-contract-brief/v0`
- optional `distribution-contract-diff/v0`
- zero or more `distribution-contract-handoff/v0`
- imported evidence pointers:
  - `install-pack/v0`
  - `install-receipt/v0`
  - `release-pack/v0`
  - `binpack/v0`
  - `binverify-report/v0`
  - `airgap-pack/v0`

Design rule: stack packs compose leaf truths; they do not overwrite them.

## Reference UX
### `cargo distribution-contract`
Reference composer UX:
- `cargo distribution-contract compose --install-pack <path>`
- `cargo distribution-contract diff --left <pack> --right <pack>`
- `cargo distribution-contract handoff --to <consumer>`
- `cargo distribution-contract pack`

This layer should begin as a **composer and handoff emitter**, not as a replacement for `cargo install`, `cargo-binstall`, package managers, or rustup.

## Ranked pilot rollout
### 1) Leaf install-pack lane
Prove the stack can compose a single real `install-pack/v0` without erasing leaf truth.

Success bar:
- stack-level brief imports rather than rewrites leaf install data;
- release/signature imports remain explicit;
- allowed downstream conclusions stay bounded.

### 2) Mirror / host fallback composition lane
Prove that host/mirror differences can be compared above multiple install packs.

Success bar:
- candidate ordering differences are explicit;
- host failure versus policy preference is distinguishable;
- the stack preserves which host or mirror actually served the installed artifact.

### 3) Package-manager / install-script import lane
Prove that non-Cargo install lanes can become explicit imported install packs.

Success bar:
- imported lanes stay visibly lossy rather than pretending to be native Cargo installs;
- verification and mutation lossiness is recorded;
- support consumers can still tell what happened.

### 4) Restricted-network consumer lane
Connect ordinary install packs with airgapped or mirrored environments.

Success bar:
- `distribution-contract-pack` can import `airgap-pack` truths without collapsing online and restricted-network assumptions;
- exact-copy mirror posture remains explicit;
- local-only or mirror-only selection is reviewable.

### 5) Support / incident / archaeology consumer lane
Widen only after the earlier lanes are solid.

Success bar:
- support tooling can explain what a user installed without reverse-engineering shell history;
- incident tooling can tell whether affected users came through source builds, mirrors, or signed binaries;
- archaeology tools can compare stack-level handoffs across time or channels.

## Scorecard
A pilot graduates only when it can show all of the following:
1. imported install-pack truth,
2. honest producer-side imports,
3. explicit host/mirror/verification differences when they exist,
4. bounded downstream handoffs,
5. at least one real downstream consumer.

A pilot that only prints “installed successfully” or a single chosen URL has **not** graduated.

## Why this would be worthy
Rust already has real ingredients for producer-side release truth, signed-binary verification, and restricted-network mirroring.
What it still lacks is the stack-level composition layer that lets leaf install packs, producer evidence, and downstream handoffs stay honest together.

A good distribution-contract pilot would not just make installs smoother.
It would make them **legible and reusable**.
