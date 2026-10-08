# Design: Publish Set Lane Map (single-package publish, workspace publish sets, alternative registries, trusted publishing, checks/waivers, and index receipts)

## Goal
Make the archive more precise about **what kind of publication claim is actually being made**.

Rust source-package publication is getting richer, but the phrase "publish support" still hides too much.
A `cargo publish` from a single crate on crates.io, a workspace-wide multi-package publish, an alternative-registry publish that depends on a credential provider, a Trusted Publishing OIDC flow, a `--no-verify` waiver, a later `pubtime` index observation, and a best-effort import from CI logs are **different but connected** lanes.

The worthy contribution here is therefore not another release bot, one more registry dashboard, or a fake universal publishing badge.
It is a **portable lane map and evidence boundary** that lets tools say which publication lane they occupy, what assumptions attach to it, where adapters are lossy, and which downstream consumers may reuse the claim honestly.

Read this together with:
- [`design/publish-set-kit.md`](./publish-set-kit.md)
- [`design/publish-set-pilot-program.md`](./publish-set-pilot-program.md)
- [`design/manifest-truth-stack.md`](./manifest-truth-stack.md)
- [`design/publisher-source-identity-stack.md`](./publisher-source-identity-stack.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`design/package-admission-stack.md`](./package-admission-stack.md)
- [`proposals/epic-publish-set-kit.md`](../proposals/epic-publish-set-kit.md)

## Why this note is needed now
The current Cargo/crates.io signals line up around one conclusion: Rust needs a better **source-publication contract**, not just better wrappers around `cargo publish`.

- Cargo’s unstable-feature docs now say `package-workspace` is stabilized and that **multi-package publishing** landed in Rust 1.90.0.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo publish` now documents workspace-aware default package selection, explicit `--workspace` / `--exclude`, `--dry-run`, `--no-verify`, explicit registry/index selection, authentication requirements, and client polling while waiting for the package to appear in the index.
  https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- Cargo’s changelog says `cargo publish` now blocks until it sees the published package in the index and later fixed `wait-for-publish` with sparse registries. That means receipt and index-visibility semantics are a real public lane, not just background transport trivia.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- `cargo package` now exposes registry-aware packaging for multiple inter-dependent crates, a machine-readable `--message-format json` for `--list`, and explicit generated/copied file provenance in that JSON shape.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Cargo release notes say `cargo-package` should now be independently reproducible, and later notes say generated `.cargo_vcs_info.json` is always included plus nonexistent `license-file` / `readme` paths are rejected during packaging. That makes payload truth more concrete than a tarball hash alone.
  https://doc.rust-lang.org/beta/releases.html
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo’s registry-auth docs make credential providers, authenticated alternative registries, and `auth-required` sparse indexes explicit. That means "published to another registry" is not the same lane as "published to crates.io with a stored token".
  https://doc.rust-lang.org/cargo/reference/registry-authentication.html
  https://doc.rust-lang.org/cargo/reference/registry-index.html
- The January 2026 crates.io update added GitLab Trusted Publishing, Trusted-Publishing-only mode, and blocked risky GitHub triggers. That means CI/OIDC authority posture is now materially different from legacy token publishing.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The same crates.io update, Cargo’s unstable-feature docs, and the registry-index docs now make `pubtime` explicit. The index docs say `pubtime` is the original publish time and should not change on later status changes like `yanked`.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://doc.rust-lang.org/cargo/reference/unstable.html
  https://doc.rust-lang.org/cargo/reference/registry-index.html
- The 2025H2 `cargo-semver-checks` goal says the Cargo team wants SemVer compliance integrated into the `cargo publish` workflow by default, with an override flag. That turns check/waiver posture into a future core publication lane, not optional side folklore.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html

## The lane map

### Lane 1 — Single-package direct-publish lane
**What it is**
- One selected package, one selected version, one registry target, and one direct Cargo publish attempt.
- This is the clearest baseline lane for crates.io publishing from a local checkout.

**Why it matters**
- Most higher-level discussions still assume this is the whole publish story.
- It is the right baseline for package-selection truth, payload truth, check truth, and initial receipt capture.

**What the archive should preserve**
- selected package identity,
- cwd / manifest-path / default-member posture,
- selected registry/index,
- direct authentication posture,
- upload result and initial index wait outcome.

**What it should not pretend**
- that the source tarball is the full release,
- that package verification is the same thing as registry acceptance,
- or that one local publish proves the whole workspace/release story.

### Lane 2 — Workspace publish-set lane
**What it is**
- Multi-package publication where one publish subject is a workspace-derived set instead of one crate.
- May involve `--workspace`, `--exclude`, default-members, package ordering, and registry-aware lockfile generation for inter-dependent crates.

**Why it matters**
- Rust 1.90 made this stable, which means publication can no longer be modeled as only one package per event.
- The selected set and package order are now first-class facts.

**What the archive should preserve**
- selected package set,
- ordering or grouping,
- inter-package dependency assumptions,
- inherited workspace.package effects,
- and per-package versus aggregate receipts.

**What it should not pretend**
- that a workspace tag or root manifest diff equals the actual publish set,
- that all packages in a set share one identical receipt,
- or that single-package and multi-package publication are interchangeable lanes.

### Lane 3 — Alternative-registry / credential-provider lane
**What it is**
- Publication that depends on non-default registry/index selection, explicit registry configuration, sparse authentication, and credential-provider resolution.

**Why it matters**
- Cargo now makes registry authentication posture explicit, especially for authenticated alternative registries.
- This is a real authority-path and registry-path lane, not just a configuration footnote.

**What the archive should preserve**
- registry identity and protocol posture,
- `auth-required` sparse-index posture when known,
- credential-provider family,
- fallback or override behavior,
- and lossy imports where auth/provider behavior came from CI or environment rather than direct observation.

**What it should not pretend**
- that crates.io and alternative registries share identical authority semantics,
- that a token environment variable is the same thing as credential-provider resolution,
- or that an index URL alone proves who was actually authorized.

### Lane 4 — Trusted-publishing / OIDC lane
**What it is**
- Publication whose authority path flows through a supported CI OIDC issuer instead of a long-lived API token.
- Includes GitHub Actions and GitLab CI/CD support plus Trusted-Publishing-only crate posture.

**Why it matters**
- This is now an upstream, user-facing crates.io capability.
- It changes the authority-path story, the kinds of failure that matter, and what downstream consumers can conclude.

**What the archive should preserve**
- CI provider family,
- trusted-publishing versus token posture,
- TP-only requirement,
- blocked trigger or issuer mismatch facts,
- and imported-versus-observed authority evidence.

**What it should not pretend**
- that OIDC publishing is the whole trust story,
- that a CI badge equals a publish receipt,
- or that all CI-trigger shapes are equally safe.

### Lane 5 — Check / waiver lane
**What it is**
- The family of pre-upload or upload-adjacent checks that may pass, fail, warn, be skipped, or be waived.
- Includes `cargo package` verification, metadata warnings, `--no-verify`, semver checks, and policy imports.

**Why it matters**
- Publication quality now spans more than "could this tarball build from scratch?"
- The semver-checks roadmap makes this lane more central over time.

**What the archive should preserve**
- which checks ran,
- which checks were skipped or waived,
- which failures were fatal versus advisory,
- whether the result came from direct execution or imported CI evidence,
- and what remained inconclusive.

**What it should not pretend**
- that one `cargo publish --dry-run` equals a full publish verdict,
- that semver compatibility and package verification are the same check family,
- or that warning-free metadata proves a crate should be admitted downstream.

### Lane 6 — Upload / index-receipt lane
**What it is**
- The post-upload lane where the registry accepted or rejected the publish request, Cargo waited for index visibility, and later observations such as `pubtime` or sparse-index presence become relevant.

**Why it matters**
- Cargo now blocks until index visibility is observed, but the docs also say the client may timeout while the upload still succeeded.
- The registry index now carries `pubtime`, which is a richer receipt layer than a shell transcript alone.

**What the archive should preserve**
- upload acceptance versus rejection,
- wait-for-publish success versus timeout,
- sparse or git index posture when relevant,
- observed `pubtime` / version-seen facts,
- and later-drift notes such as yanked status remaining separate from original publish time.

**What it should not pretend**
- that upload success and index visibility are identical,
- that a later registry page is the only receipt,
- or that status changes rewrite the original publish event.

### Lane 7 — Imported / forensic / handoff lane
**What it is**
- Publication truth reconstructed from CI logs, registry pages, release pages, or manually attached artifacts when direct machine-readable records are incomplete.

**Why it matters**
- Real teams often need archaeology, not just fresh publication.
- Downstream consumers like Release Truth and Package Admission still need bounded facts even when the producer-side record is incomplete.

**What the archive should preserve**
- imported source family,
- direct-versus-inferred posture,
- missing receipts,
- missing payload detail,
- and handoff lossiness to release/support/admission consumers.

**What it should not pretend**
- that imported CI logs are first-party publish receipts,
- that registry-page metadata fully reconstructs packaged payloads,
- or that forensic reconstruction deserves the same confidence as direct capture.

## Cross-lane adapter risks
The archive should make at least these transitions explicit:
1. **authored manifest ↔ packaged payload**
   - normalization, generated files, include/exclude rules, and `.cargo_vcs_info.json` can change what is actually shipped.
2. **single-package ↔ workspace publish set**
   - package grouping, order, and registry-aware lockfile assumptions appear.
3. **token/credential-provider ↔ trusted publishing**
   - changes authority-path semantics without becoming the full trust verdict.
4. **checks ↔ receipts**
   - passing checks is not the same as being accepted and indexed.
5. **upload receipt ↔ later registry/index observation**
   - timeouts, sparse-index lag, and later `pubtime` discovery can change what is known without changing what happened.
6. **direct capture ↔ imported forensics**
   - confidence and completeness change, so downstream consumers must inherit explicit lossiness.

## What should change elsewhere in the archive
- **Publish Set Kit** should remain the base artifact family, but it should now cite this lane map as the rule for what must stay separate.
- **Manifest Truth Stack** should export authored/package diffs into Publish Set without claiming publish receipts itself.
- **Publisher & Source Identity Stack** should export authority/source posture into Publish Set without claiming packaged payload truth.
- **Release Truth Stack** should import publish-set facts instead of re-synthesizing source-publication stories from release pages.
- **Package Admission Stack** should import publish-set facts plus graph/API/trust/policy facts instead of quietly turning publish-side evidence into one hidden verdict.
- **Support and archaeology consumers** should import the forensic lane with explicit uncertainty rather than retroactively inventing a cleaner publish history than the evidence supports.
