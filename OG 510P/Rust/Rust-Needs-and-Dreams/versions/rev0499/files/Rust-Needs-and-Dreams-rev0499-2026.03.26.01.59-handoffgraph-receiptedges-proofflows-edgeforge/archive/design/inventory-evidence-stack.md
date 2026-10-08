# Design: Inventory Evidence Stack (SBOM Evidence + Package Admission + Release Truth + Distribution Contract)

## Goal
## Lane-map correction (rev0341)
Read this stack together with [`design/sbom-evidence-lane-map.md`](./sbom-evidence-lane-map.md).
The stack now assumes the lower-layer inventory family has at least six distinct lanes that must not collapse into one lifecycle blob:
- Cargo-native precursor capture,
- source-project standards export,
- embedded binary recovery,
- release-attached standards documents / attestations,
- scanner/import views,
- and downstream consumer handoffs.

The stack’s job is to connect those lanes to Package Admission, Release Truth, and Distribution Contract **without** letting one lane quietly become the source of truth for every subject.

Treat **SBOM Evidence Kit** as the keystone inside a broader **Inventory Evidence Stack** spanning:
- [`design/sbom-evidence-kit.md`](./sbom-evidence-kit.md)
- [`design/package-admission-stack.md`](./package-admission-stack.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)

The missing contribution is **not** another one-shot SBOM exporter, another registry page, another binary scanner wrapper, or another release/install score.
It is a portable, reviewable stack that keeps these truths distinct while letting them compose across a Rust artifact's lifecycle:
- **inventory truth** — what components, scopes, and artifact links were captured, and how we know;
- **admission truth** — what package-side graph / exposure / trust / policy review happened when the `.crate` was published;
- **release truth** — what built artifacts, signatures, manifests, and rebuild attachments were shipped;
- **distribution truth** — what candidates a consumer saw, what path was chosen, and what actually landed on disk;
- **consumer truth** — what policy, incident, support, or downstream packaging tools may conclude from imported evidence.

That separation matters because the ecosystem now has real supply-chain motion, but still lacks one durable inventory handoff story:
- Cargo is growing a Rust-native SBOM precursor.
- Package publication is gaining more explicit trust and policy signals.
- Release tooling can already attach binary and manifest data.
- Install/distribution paths still change what users actually run.
- Binary/container scanners recover useful facts later, but often without strong package/release/install linkage.

The upstream signals are stronger than they were when this seam first entered the archive:
- Rust's 2026 goals now include a specific **Stabilize Cargo SBOM precursor** track, which makes Cargo-native inventory continuity an active upstream target instead of a vague future wish.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- crates.io's January 2026 development update added a Security tab, GitLab Trusted Publishing support, Trusted Publishing-only mode, blocked risky GitHub triggers, and the `pubtime` field. Those are not inventory themselves, but they materially improve the package/release side of the continuity story.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io's February 2026 malicious-crate policy now says routine malware removals will always get a RustSec advisory, which strengthens the case for durable local attachments and clear downstream handoffs instead of ambient blog awareness.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- `cargo-auditable` now explicitly points users at Cargo's native SBOM precursor for more accurate recording and documents real distro/container adoption, which makes the recovery lane a live import rather than a hypothetical future connector.
  https://github.com/rust-secure-code/cargo-auditable

## Why this seam matters now
Current official Rust/Cargo signals are unusually aligned here:
- Rust's 2026 flagships keep **Secure your supply chain** active, with milestones around **public/private dependencies** and **SBOM generation**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo's unstable `sbom` support emits precursor files **next to compiled artifacts**, exposes `CARGO_SBOM_PATH`, and explicitly allows the same crate to appear multiple times when compiled differently. That is strong evidence that Cargo is producing build-lane inventory inputs, not one fake universal package statement.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The SBOM tracking issue says the remaining work includes demonstrating **end-to-end generation of an industry-standard SBOM from this data source**, while explicitly keeping non-Rust dependencies out of scope for the precursor itself.
  https://github.com/rust-lang/cargo/issues/16565
- RFC 3553 is explicit that Cargo should emit a Cargo-specific precursor and let external tools project it into SPDX or CycloneDX. That is unusually clear evidence that the source-of-truth layer and export layers should stay separate.
  https://github.com/rust-lang/rfcs/pull/3553
- `cargo package` rewrites and normalizes the published manifest, removes `[patch]`, `[replace]`, and `[workspace]`, and always includes `Cargo.lock` unless explicitly excluded. Package truth is already not identical to repo truth.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- `cargo install` ignores the packaged lockfile by default and only uses it with `--locked`, which means consumer installation can legitimately diverge from package publication unless the path is made explicit.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- `cargo-auditable` proves that binary-recovered dependency evidence is practical, but it also says SBOMs do not by themselves prevent supply-chain attacks or even reliably capture malicious self-removal. That is strong evidence that inventory must stay distinct from trust and policy.
  https://github.com/rust-secure-code/cargo-auditable

Taken together, these signals say ideal Rust needs an **inventory continuity layer** above raw precursor/export tooling and below downstream policy/incident/support conclusions.

## What each layer owns
### SBOM Evidence Kit
[`design/sbom-evidence-kit.md`](./sbom-evidence-kit.md) owns:
- inventory subject identity,
- capture provenance,
- scope-aware component graphs,
- artifact linkage,
- export/lossiness reports,
- inventory diffs and packs.

Its question is:
> what components were present, in what scope, for which subject, and how do we know?

### Package Admission Stack
[`design/package-admission-stack.md`](./package-admission-stack.md) owns:
- package publication review,
- graph / public-contract / trust / policy composition,
- package-side decision packs,
- package-to-release handoff.

Its question is:
> what package was admitted, under what evidence and verdicts?

### Release Truth Stack
[`design/release-truth-stack.md`](./release-truth-stack.md) and adjacent release docs own:
- release subject identity,
- built artifacts,
- signatures and provenance,
- rebuild attachments,
- release-manifest truth.

Its question is:
> what shipped artifact set did we actually release, and what supporting evidence travels with it?

### Distribution Contract Stack
[`design/distribution-contract-stack.md`](./distribution-contract-stack.md) owns:
- visible channels/catalogs,
- mirror and fallback ordering,
- consumer selection/refusal reasons,
- verification posture,
- install receipts and installed-state truth.

Its question is:
> what did a consumer actually select, verify, and install?

## What the stack should make possible
A maintainer, packager, or incident responder should be able to answer all of these without diffing raw CycloneDX/XML, re-running scanners, or reconstructing Cargo state from CI logs:
1. What package/build/artifact/install subject are we talking about?
2. Which inventory facts were observed during Cargo build, inferred from metadata, recovered from binaries, or manually supplemented?
3. Which components are only package-graph facts versus actually linked to a released artifact?
4. Which installs reproduced package/release intent, and which diverged because of channel/fallback/lockfile choices?
5. Which downstream policy, trust, or incident conclusions were imported facts versus later judgments?
6. What changed between the previous package/release/install baseline and this one?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Shared design rules
1. **Inventory stays Rust-native first.** Cargo precursor, auditable extraction, metadata fallback, and manual supplements stay visible before projection into SPDX/CycloneDX or consumer-specific summaries.
2. **Package, release, and install subjects stay separate.** Publishing a `.crate`, shipping a signed binary, and installing a tool are related but not interchangeable acts.
3. **Lossiness stays attached.** Export collapse, build/runtime misclassification, native-dependency omission, and install-path divergence must remain explicit.
4. **Trust and policy are imports, not replacements.** Inventory evidence feeds Trust Signals, Policy, Incident, and Support consumers without silently becoming their verdicts.
5. **One stack, many consumers.** Package review, release review, distro ingestion, binary scanning, incident response, and support workflows should all import the same inventory evidence without inventing new semantics.

## Recommended execution posture
The stack now needs a shared rollout layer, captured in:
- [`design/inventory-evidence-pilot-program.md`](./inventory-evidence-pilot-program.md)
- [`proposals/epic-inventory-evidence-stack.md`](../proposals/epic-inventory-evidence-stack.md)

That pilot program should prove the stack in the following order:
1. **Cargo precursor capture lane**
2. **industry-format projection lane**
3. **binary-recovery / artifact-link cross-check lane**
4. **package-to-release attachment lane**
5. **distribution/install receipt lane**

That ordering is intentional.
The archive should not jump straight to one universal inventory registry, one container-only scanner view, or one supply-chain dashboard.
It should first prove that Rust-native inventory facts can survive package publication, release attachment, and consumer installation without being flattened into one document.

## What an epic contribution would look like in practice
The stack now has an explicit proposal-layer candidate in [`proposals/epic-inventory-evidence-stack.md`](../proposals/epic-inventory-evidence-stack.md).
A serious contribution here would:
- import Cargo precursor data rather than replacing it;
- attach inventory continuity to publish/release/install workflows without pretending they are the same subject;
- let binary/container recovery corroborate or challenge build-time capture with explicit mismatch reports;
- give policy/trust/incident consumers a stable import boundary instead of exporter-specific archaeology;
- and make package→release→install inventory drift reviewable in ordinary maintainer workflows.

## Anti-goals
Do not turn this stack into:
- one universal SBOM format,
- one fake supply-chain score,
- one container scanner monopoly,
- one registry-side truth engine,
- or one release/install wrapper that hides what evidence was actually imported.

The stack is an **inventory continuity boundary**, not a new compliance empire.
