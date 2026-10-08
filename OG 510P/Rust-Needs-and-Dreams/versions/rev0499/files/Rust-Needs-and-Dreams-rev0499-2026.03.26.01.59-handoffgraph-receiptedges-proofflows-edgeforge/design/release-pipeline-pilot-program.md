# Design: Release pipeline pilot program (release-truth lanes)

## Why this needs a pilot program
The archive already had the right instinct: Rust has credible publishing, release, packaging, signing, and provenance tools, but still lacks one **portable release boundary** that ties them together.

What changed is that the official/effective ecosystem signals are now strong enough to justify treating this as a real frontier instead of a nice-to-have integration story:
- Cargo publishing is permanent and starts from a concrete `.crate` package boundary.
  https://doc.rust-lang.org/cargo/reference/publishing.html
  https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- crates.io now supports stronger Trusted Publishing controls, including GitLab CI/CD support, TP-only mode, and blocking risky GitHub Actions triggers.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo is exploring more explicit final-artifact handling for build scripts, which is exactly the kind of plumbing a release-boundary contract needs to compose with instead of re-implementing privately.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo’s unstable `sbom` support already emits precursor files beside compiled artifacts, and the `artifact-dir` direction keeps making built outputs easier to collect coherently.
  https://doc.rust-lang.org/beta/cargo/reference/unstable.html
- The ecosystem already has machine-readable release/building blocks: `release-plz`, `cargo-dist`’s schema, `cargo-binstall` signature support, and attachable SBOM / OmniBOR / provenance surfaces.
  https://github.com/release-plz/release-plz
  https://docs.rs/cargo-dist-schema/latest/cargo_dist_schema/
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md
  https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md
- Even the infrastructure side is saying the crates.io package format may not be in its final state for all Rust use cases, especially when precompiled material is involved.
  https://blog.rust-lang.org/2025/11/25/interview-with-jan-david-nose/

That combination argues for a **ranked release-truth pilot program** instead of a giant “ship everything” umbrella.

## Stack boundaries
This pilot program treats three existing archive kits as one execution band:
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md) owns release intent, manifest, policy, and pack boundaries.
- [`design/signed-binaries-kit.md`](./signed-binaries-kit.md) owns prebuilt-binary signature metadata and verification reports.
- [`design/repro-build-kit.md`](./repro-build-kit.md) owns independent rebuild subjects, verdicts, and diff reasons.

Design rule: **release truth is not one artifact**.
The release boundary should stay broad enough to describe what was shipped, while signature verification and rebuild verification remain attachable truths with their own failure modes.

## Ranked pilots

### Pilot 1 — Crate-only publish lane
**Who this is for:** ordinary library maintainers publishing to crates.io.

**Why first:**
- It is the smallest lane that still exercises permanent publishing, identity, CI provenance, attached API/policy evidence, and release policy decisions.
- It does not require any binary installer or app-bundle story.

**Required artifacts**
- `release-intent/v0`
- `release-manifest/v0` with `.crate` publish record
- optional attached packs like `api-pack/v0`, `policy-pack/v0`, `sbom-evidence-pack/v0`
- bundled as `release-pack/v0`

**Acceptance bar**
- A maintainer can answer “what did we publish, from which commit/CI identity, with which attached evidence, and under what release policy?” from one pack.
- No hosted dashboard scraping is required to reconstruct the release.

### Pilot 2 — CLI binary lane
**Who this is for:** crates that publish source and also ship downloadable binaries.

**Why second:**
- This is where Rust’s release fragmentation becomes obvious in practice: crates.io publish, GitHub release assets, checksums, installer metadata, and `cargo-binstall` expectations all need to line up.
- The ecosystem already has point tools here, so the missing work is convergence rather than invention.

**Required additions**
- import `dist-manifest.json` or equivalent machine-readable artifact inventory
- explicit target-triple / archive / checksum inventory
- `binpack/v0` attachment for signed-binary lanes when present
- install-channel metadata where available

**Acceptance bar**
- A user or CI system can verify that the binary artifacts attached to a release actually belong to the same release subject as the crate publish and release notes.

### Pilot 3 — Signed-install lane
**Who this is for:** teams that want policyable prebuilt installs.

**Why third:**
- Signature support exists, but the ecosystem still lacks a clean shared place to record “these are the installable artifacts, these are the keys/issuers, and this is what passed verification.”
- This is the point where `Signed Binaries Kit` becomes a real attachment rather than an isolated idea.

**Required additions**
- `binpack/v0`
- `binverify-report/v0`
- issuer / key-rotation notes
- release-policy rules for required signatures / issuer classes / provenance presence

**Acceptance bar**
- A consumer can enforce “only signed installs from these issuers” without reverse-engineering bespoke release metadata.
- Verification failures explain whether the problem is missing metadata, bad signatures, unknown issuer, weak algorithm, or hash drift.

### Pilot 4 — Independent rebuild lane
**Who this is for:** security-sensitive publishers, downstream packagers, and skeptical consumers.

**Why fourth:**
- Provenance and signatures tell you who shipped something; they do not prove a second builder obtained the same artifact.
- This is where the stack stops pretending release evidence and reproducibility are the same thing.

**Required additions**
- `repro-subject/v0`
- `repro-run-report/v0`
- `repro-compare-report/v0`
- `repro-pack/v0` attached from the release pack when available
- strong/weak rebuild-mode truth plus diff reasons

**Acceptance bar**
- A reviewer can tell whether a release has only provenance, provenance plus signatures, or provenance plus signatures plus an actual independent rebuild verdict.

### Pilot 5 — Multi-channel / installer / mirror lane
**Who this is for:** desktop apps, multi-platform CLIs, and organizations with mirrors or offline distribution needs.

**Why fifth:**
- This is strategically important, but too broad for the first pilot.
- It is where app bundles, installers, mirrors, updater feeds, and offline verification start to matter.

**Required additions**
- package-manager / installer channel metadata
- mirror or alternate-host pointers
- explicit offline verification bundle rules
- attachment rules for app-bundle artifacts that are not equivalent to a `.crate`

**Acceptance bar**
- One release can honestly describe crate publishing, downloadable artifacts, installers, mirrors, and verification bundles without pretending they are all the same surface.

## Shared design rules across pilots
- **Keep source publish separate from built artifacts.** The `.crate` upload, generated archives/installers, and post-build packaging steps are related but not interchangeable truths.
- **Treat signatures and rebuilds as attachments, not implicit badges.** `release-pack/v0` should point to `binpack` / `binverify-report` / `repro-pack`, not absorb them into one fake green status.
- **Make release identity explicit.** Commit, tag, CI subject, registry target, artifact list, and hosting/mirror pointers must be attached to the same release subject.
- **Allow crate-only releases to stay small.** v0 should not force every library into a binary/install/update worldview.
- **Prefer importers over rewrites.** If `cargo-dist`, `release-plz`, `cargo-release`, or future Cargo outputs already describe part of the release, ingest them.
- **Offline verification must remain possible.** A release should not require GitHub or any other host to remain the source of truth forever.

## What this pilot program should prevent
- Another giant release wrapper that tries to replace `release-plz`, `cargo-dist`, `cargo-release`, and `cargo-binstall` all at once.
- Pretending that signatures, attestations, SBOMs, and reproducibility are one thing.
- Treating GitHub Releases or any other host page as the canonical release record.
- Smuggling app-installer complexity into the minimal crate-publish lane.

## Immediate archive decision
Treat [`design/release-pipeline-kit.md`](./release-pipeline-kit.md) and [`proposals/epic-release-pipeline-kit.md`](../proposals/epic-release-pipeline-kit.md) as the schema/epic anchors, and treat this file as the **execution order** for the archive’s release-truth work. The next credible move is not “another Rust release tool”; it is making `release-pack/v0` good enough to survive Pilot 1 and Pilot 2 without flattening signed-binary and reproducibility truth.
