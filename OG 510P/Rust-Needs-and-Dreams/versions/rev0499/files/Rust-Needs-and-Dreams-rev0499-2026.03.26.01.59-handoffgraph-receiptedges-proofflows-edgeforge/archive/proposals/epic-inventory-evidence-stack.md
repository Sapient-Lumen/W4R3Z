# Epic Proposal: Inventory Evidence Stack (`cargo inventory-evidence` + `inventory-evidence-pack/v0`)

## One-sentence pitch
Create a thin stack-level contract that makes Rust inventory continuity boring: a portable boundary that links **Cargo-native precursor capture**, **package admission**, **producer-side release attachments**, and **consumer-side install receipts** without flattening them into one SBOM, one scanner result, or one supply-chain verdict.

## Deliverables
- `cargo inventory-evidence` reference tool
- schemas:
  - `inventory-evidence-brief/v0`
  - `inventory-evidence-diff/v0`
  - `inventory-evidence-pack/v0`
  - `inventory-evidence-handoff/v0`
- adapters/importers for:
  - `inventory-pack/v0`
  - `package-admission-pack/v0`
  - `release-truth-pack/v0`
  - `distribution-contract-pack/v0`
  - selected `artifact-inventory-report/v0`, projected SPDX/CycloneDX documents, and binary-recovery attachments
- docs:
  - Cargo-precursor capture recipe
  - projection/lossiness guide
  - package→release attachment guide
  - package→release→install continuity recipe
  - incident/distro/support consumer guide

## Why now (signals)
- Rust’s 2026 flagship work explicitly includes **stabilize SBOM support**, and the goals page separately calls out **Stabilize Cargo SBOM precursor** as a concrete help-wanted track. That means Cargo-native inventory is now upstream strategy, not a side quest.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s unstable-book docs say `sbom` generates **SBOM pre-cursor files alongside each compiled artifact**. The tracking issue says the remaining work includes demonstrating end-to-end generation of an industry-standard SBOM from this data source and explicitly keeps non-Rust dependencies out of scope for the precursor itself. That is a strong signal that the missing contribution is not “pick the winner exporter,” but the continuity layer above the precursor.
  https://doc.rust-lang.org/cargo/reference/unstable.html
  https://github.com/rust-lang/cargo/issues/16565
- crates.io’s January 2026 update added a Security tab, GitLab Trusted Publishing support, Trusted Publishing-only mode, blocked risky GitHub triggers, and the `pubtime` field in the index. Those are not inventory by themselves, but they make package/release linkage, incident review, and downstream imports materially more realistic.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io’s February 2026 malicious-crate policy now says routine malware removals will always get a RustSec advisory. That raises the value of durable local artifacts and explicit handoffs over ambient blog awareness.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Cargo packaging/install docs still make lifecycle divergence plain: package creation normalizes the published package view, while `cargo install` ignores the packaged lockfile unless `--locked` is used. That means package, release, and install inventory can legitimately diverge in ordinary Rust workflows.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- `cargo-auditable` now explicitly points users at Cargo’s native SBOM precursor for more accurate recording and documents real adoption across multiple Linux distributions. That means artifact recovery is no longer hypothetical, but it is still not the same thing as package publication or consumer installation.
  https://github.com/rust-secure-code/cargo-auditable

## Non-goals
- replacing Cargo’s precursor with one universal SBOM format;
- turning SPDX or CycloneDX export into the only canonical representation;
- making binary recovery the whole truth;
- making crates.io or a container scanner the only inventory authority;
- collapsing trust, policy, advisories, provenance, and installation into one “supply-chain score”.

## Strategic value
This deserves promotion because it gives the archive a missing **inventory-continuity composition point**.
With it:
- Cargo-native precursor facts can stay canonical for build-lane inventory capture;
- package-admission review can attach graph/exposure/trust/policy context without pretending that is the same as shipped-artifact inventory;
- producer-side release packs can carry inventory attachments without silently becoming install receipts;
- consumer-side installation and incident/support tooling can import explicit summaries instead of reconstructing the story from raw SBOM files, binary scans, registry pages, and shell history.

The prize is not another exporter.
The prize is a durable continuity boundary that other tools can import.

## Proposed shape
Lower-layer lane map reminder: the stack now assumes the SBOM family is split by [`design/sbom-evidence-lane-map.md`](../design/sbom-evidence-lane-map.md) into Cargo-native precursor capture, source-project standards export, embedded binary recovery, release attachments, scanner/import views, and downstream consumer handoffs. The stack must coordinate them without letting one lane quietly replace every other subject.

Ship a narrowly scoped stack-level layer:
1. import `inventory-pack/v0` as the canonical build-lane inventory layer;
2. import `package-admission-pack/v0` as the canonical package-review layer;
3. import `release-truth-pack/v0` as the canonical producer-side artifact/rebuild/signature layer;
4. import `distribution-contract-pack/v0` as the canonical install-path/receipt layer;
5. preserve capture-vs-projection-vs-recovery-vs-install distinctions in stack-level diffs;
6. emit bounded handoffs for policy, incident, distro, support, and assistant consumers.

## Critical design bet
The critical bet is that **inventory-evidence truth stops at reviewable continuity across package, release, and install subjects**.
That means:
- Cargo precursor capture remains canonical for build-time Rust inventory facts,
- package admission remains canonical for publish-time package review,
- release truth remains canonical for producer-side artifacts and attached evidence,
- distribution remains canonical for consumer-side acquisition and installed-state receipts,
- stack-level packs coordinate them,
- but the stack does not become the sole owner of trust, policy, advisories, signatures, or support claims.

Without that boundary, the contribution either stays too weak to matter or bloats into a fake universal supply-chain platform.

## Milestones
1. **v0 stack pack + precursor lane**
   - `inventory-evidence-brief` / `inventory-evidence-pack`
   - import `inventory-pack/v0`
2. **v0.2 standards projection lane**
   - attach SPDX/CycloneDX projections with explicit exporter/lossiness notes
3. **v0.3 package/release continuity lane**
   - import package-admission + release-truth packs
   - preserve subject linkage without flattening verdicts and artifacts
4. **v0.4 artifact-recovery/install lane**
   - attach binary-recovery reports and distribution receipts
   - expose mismatch classes instead of hiding them
5. **v1 thin consumer handoffs**
   - emit incident/distro/policy/support/assistant summaries with explicit overclaim boundaries

## Execution order
Use [`design/inventory-evidence-pilot-program.md`](../design/inventory-evidence-pilot-program.md) as the stack-level rollout:
1. Cargo precursor capture lane,
2. industry-format projection lane,
3. binary-recovery / artifact-link cross-check lane,
4. package-to-release attachment lane,
5. distribution/install receipt lane.

Use [`design/sbom-evidence-kit.md`](../design/sbom-evidence-kit.md) as the lower-layer inventory capture guide beneath it.

## Success metrics
- package, release, and install subjects can travel together without collapsing into one lifecycle blob;
- projected SPDX/CycloneDX documents can summarize the truth without becoming the new source of truth;
- binary recovery and install receipts can corroborate or challenge earlier layers with explicit mismatch reports;
- policy, incident, distro, and support consumers can import the continuity boundary without re-scraping registries, CI, or binaries;
- the ecosystem gets one explainable inventory-continuity seam instead of disconnected precursor files, exporter outputs, release attachments, and scanner snapshots.
