# Design: Public API pilot program (publish-admission lanes)

## Why this needs a pilot program
The archive now reads **Public API Kit** as the substrate beneath the explicit **Public API Contract** frontier. The missing piece is no longer “is API evidence important?” but **how to introduce it without boiling the ocean**.

Current official Rust signals point to a staged rollout rather than a giant all-at-once merge:
- 2026 flagships keep **public/private dependencies** alive as a live supply-chain goal.
- `cargo-semver-checks` is still working through blockers for eventual `cargo publish` integration, including cross-crate provenance and type-sensitive witness checking.
- Cargo’s unstable `public-dependency` feature already feeds `exported_private_dependencies`, and Cargo’s changelog now notes that public/private dependency status is exposed through `cargo metadata`.
- docs.rs now builds and hosts rustdoc JSON, which lowers the friction for tool-facing API evidence but does **not** eliminate format/version/provenance concerns.
- Witness-generation work is real, but still selective and expensive enough that it should be introduced where it pays for itself first.

That combination argues for a **ranked pilot program**: introduce reviewable API evidence in the places where it immediately answers existing maintainer / publisher / downstream questions, then widen the consumer set once the artifacts stabilize.

## Ranked pilots

### Pilot 1 — Single-crate release gate
**Who this is for:** maintainers of ordinary published libraries.

**Why first:**
- This is the smallest lane that still exercises the full story: public surface export, semver classification, witness escalation, and MSRV verification.
- It aligns directly with the long-term `cargo publish` direction without requiring Cargo itself to absorb every piece on day one.

**Required artifacts**
- `api-surface/v0`
- `api-diff-report/v0`
- `semver-report/v0`
- `msrv-report/v0`
- optional `api-witness-report/v0` when reason codes require it
- bundled as `api-pack/v0`

**Acceptance bar**
- A maintainer can answer “what changed, what is breaking, what needs a waiver, and whether our MSRV claim held” from one pack attached to CI or a release.
- Overrides stay explicit and human-authored; the pilot must never force a fake green result.

### Pilot 2 — Workspace release group
**Who this is for:** workspaces with multiple related library crates and reexports.

**Why second:**
- Workspace release reality is where cross-crate provenance, reexports, and package-selection problems become painful.
- Cargo is also investing in workspace/package workflows, making this a good place for companion artifacts.

**Required additions**
- package-selection and baseline rules
- aggregation rules for multiple `api-pack/v0` files
- explicit cross-crate provenance / unresolved-lane markers
- release-group summary that does **not** erase per-crate truth

**Acceptance bar**
- A workspace release can publish a small family of packs and one summary without flattening per-crate waivers or provenance gaps.

### Pilot 3 — Downstream packaging / distro intake
**Who this is for:** distros, enterprise package curation, and long-lived downstream consumers.

**Why third:**
- Downstreams care about API change, public exposure, MSRV reality, and support posture, but they should not need to reconstruct those from changelogs and CI logs.
- This pilot tests whether `api-pack/v0` is genuinely useful outside the publisher’s own CI.

**Required additions**
- stable attachment and checksum conventions
- explicit toolchain / target / feature / cfg matrix policy
- clearer release-to-release comparison subject identity
- downstream-readable waiver and unsupported-lane semantics

**Acceptance bar**
- A downstream reviewer can decide whether to ingest, delay, patch, or flag a release without rerunning the publisher’s whole toolchain pipeline.

### Pilot 4 — Policy / trust / inventory correlation
**Who this is for:** orgs or services making explainable policy decisions.

**Why fourth:**
- By this point the API pack should be stable enough to serve as one input to `cargo policy`, trust, lifecycle, or inventory review.
- This is the moment to test correlation, **not** to turn API evidence into a single ecosystem score.

**Required additions**
- optional digest/pointer links from `api-pack/v0` to inventory/trust/policy evidence
- stable reason-code mapping into policy rules
- visible distinction between imported evidence and derived decision

**Acceptance bar**
- Policy tools can say “this rule fired because public dependency exposure drifted” or “this release was waived for reason X” without scraping freeform logs.

### Pilot 5 — Change-impact / relink consumer lane
**Who this is for:** build-analysis and rebuild-scope tooling.

**Why fifth:**
- This is a high-leverage consumer, but it depends on the API boundary being trustworthy first.
- It is where the archive’s Public API work composes with `relink-don’t-rebuild` and broader build-state evidence rather than trying to replace them.

**Required additions**
- interface-hash or equivalent comparison hooks
- explicit “public-surface unchanged” evidence that build tooling can consume
- honest unsupported markers for lanes where structural diffing is insufficient

**Acceptance bar**
- Build tooling can consume API evidence as one input for smarter rebuild/relink decisions without pretending API evidence alone explains all rebuild behavior.

## Shared design rules across pilots
- **Per-crate truth survives aggregation.** Workspace and downstream summaries must never erase crate-local waivers, unsupported lanes, or provenance gaps.
- **Witnesses stay selective.** Witness generation is for ambiguous/type-sensitive cases, not a mandatory step for every trivial additive change.
- **Release identity must be explicit.** Comparison target, features, cfgs, target triple, toolchain, and rustdoc/adapter compatibility must be attached to every pack.
- **Publish override posture must remain visible.** The point is to make overrides reviewable, not impossible.
- **Consumer boundaries stay separate.** Publisher CI, downstream review, policy intake, and build/relink consumers may read the same pack, but they should not force one another into the same verdict model.

## What this pilot program should prevent
- Shipping another one-off API diff tool with bespoke terminal output and no portable attachment format.
- Pretending that semver reasoning, witness proofs, MSRV verification, and public-dependency exposure all collapse into one badge.
- Jumping straight to core-Cargo monopoly before the pack and reason codes are stable enough for multiple consumers.
- Treating docs.rs rustdoc JSON or StableMIR as a magical complete answer to public-API truth; they are inputs and enablers, not the whole lane.

## Immediate archive decision
Treat [`design/public-api-kit.md`](./public-api-kit.md) and [`proposals/epic-public-api-kit.md`](../proposals/epic-public-api-kit.md) as the schema/epic anchors, and treat this file as the **execution order** for the next serious Public API work. The next credible move is not inventing more semver lints in isolation; it is making `api-pack/v0` good enough to survive Pilot 1 and Pilot 2 honestly.
