# Epic proposal: Publish Set Kit (`cargo publish-set`, `publish-pack/v0`)

## One-line thesis
Build a thin Cargo companion layer for **source-package publication truth** that links **selected publish subject**, **package payload identity**, **check / waiver posture**, **authority and registry-path facts**, **upload/index receipts**, and **later registry/index observation such as `pubtime`** into one portable review boundary without pretending release bundles, binary artifacts, trust verdicts, and install receipts are all the same thing.

## Why this is now worth doing
Rust now has enough real upstream motion around publication that the missing contribution looks like a **reviewable publish boundary above the ingredients** rather than one more ingredient:
- multi-package publishing is stable;
- `cargo publish` and `cargo package` have clear workspace-aware package-selection behavior;
- machine-readable package file listings are taking shape;
- workspace inheritance can materially change `version`, `publish`, `include`, and `exclude` posture;
- semver-checking is moving toward the publish workflow;
- crates.io’s authority and timing surfaces are getting stronger through Trusted Publishing and `pubtime`, while registry-index docs now specify that `pubtime` is the original publish time rather than a mutable later status field.

What is still missing is the **kit-level boundary that says one publish subject produced these `.crate` payloads, with these checks, through this authority path, and with these receipts**.

## Working name
- CLI: `cargo publish-set`
- primary artifact: `publish-pack/v0`

## Scope
### This epic should own
- selected package/workspace publish subject
- package order/grouping for multi-package publication
- packaged file truth and normalization notes
- publish-time check / waiver / skip / inconclusive truth
- registry selection and authority-path facts
- upload/index receipt capture and drift
- bounded handoffs to Release Truth, Library Productization, Publisher & Source Identity, Package Admission, and support consumers

### This epic should not own
- authored-manifest and discovery truth as such
- full semver/public-API meaning
- binary artifact release manifests or signatures
- consumer-side install/mirror/fallback receipts
- one registry dashboard or moderation workflow
- a fake “fully trusted publish” badge

## Candidate artifact family
### `publish-brief/v0`
Why this publish subject exists, what package set and registry were involved, and where uncertainty remains.

### `publish-subject/v0`
The exact workspace/package/version/registry/selection/authority intent being published.

### `package-file-report/v0`
One package payload with file inventory, origin, normalization notes, and optional best-effort VCS hints.

### `publish-check-report/v0`
Packaging verify, metadata, semver, policy, waiver, and inconclusive outcomes.

### `publish-receipt/v0`
Upload acceptance, authority path, polling/index visibility, and timeout/error facts.

### `publish-pack/v0`
The portable bundle linking subject, payloads, checks, receipts, raw evidence, and bounded handoff notes.

### `publish-diff/v0`
What changed between two publish attempts, with separate sections for:
- selected-subject drift
- package/order drift
- payload drift
- check/waiver drift
- authority/registry drift
- receipt/index drift

### `publish-handoff/v0`
Lossy summaries for Release Truth, Library Productization, Publisher & Source Identity, Package Admission, and support/incident consumers.

## Recommended rollout
1. single-package crates.io lane
2. workspace publish-set lane
3. trusted-publishing lane
4. semver-check lane
5. semver-check / waiver lane
6. receipt / `pubtime` lane
7. release/package-admission handoff lane
8. broader library/support consumers

This should be driven by [`design/publish-set-kit.md`](../design/publish-set-kit.md), [`design/publish-set-lane-map.md`](../design/publish-set-lane-map.md), and [`design/publish-set-pilot-program.md`](../design/publish-set-pilot-program.md), with Manifest Truth, Publisher & Source Identity, and Release Truth importing the result rather than replacing it.

## What makes this epic “epic” rather than incremental
An incremental tool would improve one lane:
- better version bumping,
- better publish GitHub Actions,
- better tarball inspection,
- or better registry dashboards.

An epic contribution here instead gives Rust one **portable source-publication contract** above those lanes.
That is strategically different because it can:
- let single-package and multi-package publishing share one subject boundary;
- keep packaged payload truth distinct from authored manifest truth;
- keep verify/semver/policy checks distinct from registry acceptance;
- let release/library/package-admission consumers reuse source-publication facts;
- and absorb future Cargo/crates.io publish features without forcing every downstream layer to reinvent the publish model.

## Design principles
- **Selected publish subject truth is not packaged payload truth.**
- **Check success is not registry acceptance.**
- **Authority path is not trust verdict.**
- **Release/install stories remain downstream.**
- **Lossiness and instability are explicit.**
- **The kit remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact package or workspace set we selected for publication,”
- “these are the packaged source payloads that were actually produced,”
- “here are the checks and waivers that applied,”
- “here is which registry and authority path were used,”
- “here is what upload/index receipt we got,”
- and “here is what downstream release/library/package-admission/support consumers may safely conclude,”

without reconstructing the story from manifests, `cargo package --list`, CI logs, registry pages, and local memory.

## Read this with
- `gaps/publish-sets-package-selection-contents-verification-and-registry-receipts.md`
- `design/publish-set-kit.md`
- `design/manifest-truth-stack.md`
- `design/publisher-source-identity-stack.md`
- `design/release-pipeline-kit.md`
- `design/release-truth-stack.md`
- `design/package-admission-stack.md`
