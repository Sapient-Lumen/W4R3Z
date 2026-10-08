## Execution addendum (rev0455)
For questions about **what the archive's release-truth seam should actually ship once “package publication, binaries, signatures, rebuilds, and SBOMs all matter” is no longer enough**, read `design/release-truth-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- the broad stack is unchanged;
- this revision says more explicitly what **Release Truth** should become in theory and practice;
- treat it as **reference layer + report/pack command + attachment/import corpus**;
- keep **Publisher & Source Identity**, **Cargo Artifact Contract**, **Distribution Contract**, **Repro Build**, and **Inventory Evidence** adjacent but distinct;
- and refuse the tempting wrong shapes first: another release bot, one host page, one provenance badge, or one supply-chain platform that erases producer-side boundaries.

# Design note: Release Truth Stack (Release Pipeline + Signed Binaries + Repro Build, with Inventory / Distribution handoffs)

## Goal
Treat Rust release work as one explicit **producer-side truth stack** spanning:
- [`design/publish-set-kit.md`](./publish-set-kit.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)
- [`design/release-pipeline-pilot-program.md`](./release-pipeline-pilot-program.md)
- [`design/signed-binaries-kit.md`](./signed-binaries-kit.md)
- [`design/repro-build-kit.md`](./repro-build-kit.md)
- [`design/repro-build-lane-map.md`](./repro-build-lane-map.md)
- [`design/repro-build-pilot-program.md`](./repro-build-pilot-program.md)
- [`design/inventory-evidence-stack.md`](./inventory-evidence-stack.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)

The worthy contribution here is **not** another release GitHub Action, another hosted release page, another installer wrapper, or another provenance badge.
It is a thin composition layer that lets Rust projects publish a **reviewable release story**:
- what source package or package set was published,
- what publication subject/payload/check/receipt facts belong to that source publication,
- what built artifacts belong to that same release subject,
- what signatures or attestations exist for installable binaries,
- what independent rebuild evidence exists,
- what SBOM / inventory evidence is attached,
- and where producer-side truth stops so consumer-side install truth can begin.

## Why this note is needed now
The archive already had strong release leaves, but the surrounding ecosystem signals are now unusually aligned:
- Cargo publishing remains permanent and starts from a concrete package boundary.
  https://doc.rust-lang.org/cargo/reference/publishing.html
  https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- `cargo package` makes it explicit that package truth is curated and normalized: it rewrites the manifest, removes `[patch]`, `[replace]`, and `[workspace]`, and includes `Cargo.lock` by default.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- crates.io has moved quickly on release identity and authorization: Trusted Publishing, GitLab CI/CD support, Trusted-Publishing-only mode, and blocked risky GitHub Actions triggers all sharpen who is allowed to publish and from where.
  https://blog.rust-lang.org/2025/07/11/crates-io-development-update-2025-07/
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Rust’s 2026 flagship work keeps **public/private dependencies** and **SBOM support** in the active supply-chain agenda, which means “what exactly shipped?” is becoming a first-class ecosystem question rather than a release-engineering niche.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo already exposes a concrete machine-facing package/build surface and is exploring better artifact uplift and build-analysis/report lanes. That makes a thin release-truth composition layer more realistic than it would have been a year earlier.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The ecosystem already has serious point tools: `release-plz`, `cargo-release`, `cargo-dist`, and `cargo-binstall` are strong evidence that the missing layer is now **shared composition and reviewability**, not raw tool existence.
  https://github.com/release-plz/release-plz
  https://crates.io/crates/cargo-release
  https://docs.rs/cargo-dist-schema/latest/cargo_dist_schema/
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md

Those signals justify promoting **Release Truth Stack** from an implicit frontier phrase into an explicit archive seam.

## What each layer owns
### 1) Release Pipeline Kit: release subject, intent, manifest, and policy
[`design/release-pipeline-kit.md`](./release-pipeline-kit.md) owns:
- the release subject,
- intended release shape,
- the actual release manifest,
- release readiness policy,
- and `release-pack/v0`.

Its core question is:
> what producer-side release are we describing, and what artifacts/evidence belong to it?

### 2) Signed Binaries Kit: installable-artifact issuer and verification truth
[`design/signed-binaries-kit.md`](./signed-binaries-kit.md) owns:
- `binpack/v0`,
- `binverify-report/v0`,
- issuer/key/algorithm posture,
- and verification outcomes for downloadable binaries.

Its core question is:
> which installable binaries were signed by whom, and what did verification actually conclude?

### 3) Repro Build Kit: independent rebuild truth
[`design/repro-build-kit.md`](./repro-build-kit.md), [`design/repro-build-lane-map.md`](./repro-build-lane-map.md), and [`design/repro-build-pilot-program.md`](./repro-build-pilot-program.md) own:
- source-package reproducibility posture,
- `repro-subject/v0`,
- `repro-run-report/v0`,
- `repro-compare-report/v0`,
- optional attestation-link and offline-bundle posture,
- `repro-pack/v0`,
- and explicit diff reasons / inconclusive / superseded states.

Its core question is:
> which rebuild-adjacent claim is being made — package reproducibility, artifact equivalence, provenance attachment, SBOM attachment, offline verification, or lifecycle status — and what actually justified it?

### 4) Inventory Evidence Stack: attached inventory continuity
[`design/inventory-evidence-stack.md`](./inventory-evidence-stack.md) should remain an import, not a hidden sub-layer.
It owns:
- SBOM precursor/import/export truth,
- package→release→install inventory continuity,
- artifact linkage,
- and projection/lossiness reports.

Its core question is:
> what component inventory facts travel with this release, and how did they move from package/build truth into release artifacts and later consumers?

### 5) Distribution Contract Stack: consumer-side install truth
[`design/distribution-contract-stack.md`](./distribution-contract-stack.md) stays adjacent rather than absorbed.
It owns:
- visible channels,
- mirror ordering,
- fallback behavior,
- verification posture at install time,
- and install receipts.

Its core question is:
> what did a consumer actually select, verify, and install?

Design rule: **Release Truth Stack stops before channel choice, fallback, and installed-state claims.**

## Shared design rules
1. **Package publish, built artifacts, signatures, rebuilds, and installs are related but not identical truths.**
2. **Producer-side truth stays reconstructible offline.** Hosted pages may mirror it, but should not be the only authoritative record.
3. **Signatures, provenance, and SBOM attachments do not replace rebuild evidence.** Reproducibility remains an attached verdict with its own compare modes and failure modes.
4. **Inventory stays attached, not flattened.** SBOM or precursor exports should travel with the release pack, not silently become the release pack or the rebuild verdict.
5. **Distribution remains a downstream import.** Release tools should not pretend that publishing or uploading is the same as a consumer successfully installing.
6. **Crate-only releases remain first-class.** The stack must not force every library into a binary-installer worldview.

## What an epic contribution should look like in practice
A worthy contribution here would be a thin **`cargo release-truth` / `release-truth-pack/v0`** layer above the existing leaves.
It should:
- import `publish-pack/v0` for source-publication truth and `release-pack/v0` for broader release truth rather than replacing `cargo ship` / release-orchestrator tools,
- attach `binpack/v0` / `binverify-report/v0` when prebuilt binaries exist,
- attach `repro-pack/v0` when independent rebuild evidence exists,
- attach SBOM / inventory evidence packs without collapsing them,
- emit explicit handoff pointers for downstream Distribution Contract and Policy consumers,
- and make release-to-release diffs reviewable at the producer boundary.

The missing artifact family is not large:
- `release-truth-brief/v0`
- `release-truth-diff/v0`
- `release-truth-pack/v0`
- `release-truth-handoff/v0`

Those should mostly reference lower-layer artifacts instead of replacing them.

## Reference CLI shape
- `cargo release-truth collect`
  - import `release-pack/v0` and attached evidence packs
- `cargo release-truth verify`
  - validate boundary completeness and required attachments
- `cargo release-truth diff --against <ref|tag|path>`
  - summarize release drift without flattening signatures/rebuilds/inventory into one bit
- `cargo release-truth handoff --to distribution|policy|incident|support`
  - emit bounded downstream-facing summaries
- `cargo release-truth pack`
  - bundle `release-truth-pack/v0`

This should remain a **composition and handoff layer**, not a new release engine.

## Ranked first execution lanes
1. **crate-only publish lane**
   - prove package publish → release subject → attached evidence continuity without binary complexity.
2. **source + binary lane**
   - prove one release subject can cover `.crate` publication and downloadable binary artifacts together.
3. **signed-binary lane**
   - prove issuer and verification metadata attach cleanly without becoming the whole release status.
4. **independent rebuild lane**
   - prove provenance/signature truth and rebuild truth can coexist without being conflated.
5. **inventory + distribution handoff lane**
   - prove the producer boundary can hand off to downstream inventory/policy/install consumers without silently swallowing them.

## Non-goals
- replacing `release-plz`, `cargo-release`, `cargo-dist`, `cargo-packager`, or `cargo-binstall`;
- declaring one universal installer, updater, or package-manager format;
- turning release truth into a registry-only or GitHub-only dashboard;
- flattening signatures, provenance, SBOMs, and rebuild evidence into one fake “trusted release” badge.

## Archive fit refresh
The archive already had the right leaf kits.
What it was missing was the synthesis note saying:
- where producer-side release truth starts,
- where it stops,
- how signature / rebuild / inventory layers attach,
- and how distribution or policy consumers should import it without redefining it.

That is why this stack now deserves an explicit root design note, pilot note, and epic candidate instead of remaining only a phrase inside frontier prose.
