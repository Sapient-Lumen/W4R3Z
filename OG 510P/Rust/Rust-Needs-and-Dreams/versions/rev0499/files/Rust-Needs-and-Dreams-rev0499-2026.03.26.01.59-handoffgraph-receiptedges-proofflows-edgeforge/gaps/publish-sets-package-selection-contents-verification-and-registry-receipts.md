# Gap: Rust still lacks a portable publish-subject contract above `cargo publish`

## Summary
Cargo can now publish **multiple workspace packages on stable**, and crates.io has stronger authority and timing signals than it used to. But the ecosystem still lacks a portable, reviewable contract for **what source packages were actually selected for publication, what exactly was packaged, which checks and waivers applied, which authority path was used, and what receipt came back from the registry/index**.

Today serious teams still reconstruct that story from some mix of:
- workspace/package selection rules,
- manifest `publish` / `include` / `exclude` fields,
- `cargo package --list` output,
- CI-specific Trusted Publishing setup,
- semver or policy checks glued on externally,
- upload logs,
- and later registry/index observations.

That is enough to ship, but it is not yet a clean answer to the questions downstream consumers actually ask:
- which package or workspace set was intended for publication;
- which files and generated metadata were actually in each `.crate` payload;
- which registry and authority path were used;
- which checks were required, skipped, waived, or still inconclusive;
- which upload or index receipts exist;
- and what Release / Library / Package-Admission / Support consumers may safely import next.

## Ecosystem signals
- Cargo’s unstable-feature docs now say **multi-package publishing** was stabilized in Rust 1.90.0. That is strong evidence that publication is no longer only a single-package edge case.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo publish` now documents workspace-aware default package selection, explicit `--workspace` / `--exclude`, registry selection, `--dry-run`, `--no-verify`, upload polling, and index appearance waiting. That is a real publish-control surface, not just a thin upload wrapper.
  https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- `cargo package` now documents workspace-aware package selection and an unstable `--message-format json` for `--list`, plus registry-aware packaging for multiple inter-dependent crates. Its docs also spell out generated-versus-copied file provenance, packaged `Cargo.toml` normalization, `.cargo_vcs_info.json`, and lockfile posture. That is enough evidence that package payload truth is becoming machine-readable, but not yet a full publish contract.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo manifest docs make `include`, `exclude`, and `publish` explicit publish-facing controls, and workspace docs show `workspace.package` can inherit `version`, `publish`, `include`, and `exclude`. Registry-authentication and registry-index docs also make credential providers, authenticated sparse indexes, and `auth-required` explicit. That means publish truth is partly authored at package level, partly inherited from workspace policy, and partly shaped by registry authority configuration.
  https://doc.rust-lang.org/cargo/reference/manifest.html
  https://doc.rust-lang.org/cargo/reference/workspaces.html
  https://doc.rust-lang.org/cargo/reference/registry-authentication.html
  https://doc.rust-lang.org/cargo/reference/registry-index.html
- The 2025H2 cargo-semver-checks goal explicitly says the Cargo team wants SemVer compliance merged into the `cargo publish` workflow. That means publish-time checking is getting broader than “did it compile from the tarball?”
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- The January 2026 crates.io development update added GitLab Trusted Publishing, Trusted-Publishing-only mode, blocked risky GitHub triggers, and `pubtime` in the index. The registry-index docs now specify that `pubtime` is the original publish time and should not change on later status changes like `yanked`. That means publish authority and publish-time/index visibility are now materially richer than they were even a year ago.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://doc.rust-lang.org/cargo/reference/registry-index.html

## What is missing
The missing contribution is a thin **Publish Set Kit** above Cargo packaging and registry upload.

It should make seven truths portable without flattening them together:
1. selected publish subject truth;
2. package payload truth;
3. check / waiver / verification truth;
4. authority and registry-path truth;
5. upload / index receipt truth;
6. later registry/index observation truth (including `pubtime`);
7. bounded downstream handoff truth.

## What “good” looks like
- A machine-readable publish plan for one package or a workspace publish set.
- Explicit separation between **authored manifest truth** and **packaged publish payload truth**.
- Explicit separation between **publish checks** (package verify, semver, policy, metadata warnings) and **registry acceptance**.
- Explicit handling of single-package and multi-package topo-order publication without pretending release bundles or installer artifacts are the same thing.
- Honest lossiness notes when a consumer is inferring from logs, best-effort VCS hints, or partially visible registry/index state.
- Diffable reports that say whether change happened in subject selection, packaged files, checks/waivers, authority path, or receipts.

## Candidate contribution
Promote a **Publish Set Kit** with:
1. `publish-subject/v0` for selected packages, versions, registries, and workspace-selection truth,
2. `package-file-report/v0` for packaged file lists, generated files, and manifest normalization/import notes,
3. `publish-check-report/v0` for verify / semver / policy / metadata / waiver outcomes,
4. `publish-receipt/v0` for upload acceptance, polling/index visibility, and authority/issuer facts,
5. `publish-pack/v0` for bounded downstream handoff, with explicit direct-versus-imported evidence posture.

## Distinction from nearby archive entries
- **Not Manifest Truth Stack:** that stack owns authored-manifest truth, packaged-manifest diffs, discovery/context, and consumer-import lossiness. Publish Set Kit starts when concrete package(s) are selected for packaging/publication.
- **Not Publisher & Source Identity Stack:** that stack owns project-family claims, publish authority, namespace/source posture, and trust/policy imports. Publish Set Kit imports those facts into one actual publish attempt or publish set.
- **Not Release Pipeline Kit:** that kit owns the broader release subject including binary artifacts, installers, signatures, provenance, SBOMs, and release manifests. Publish Set Kit stops at source-package publication and registry/index receipts.
- **Not Package Admission Stack:** that stack owns the consumer or registry-facing review of package intake and graph/policy meaning. Publish Set Kit is producer-side publication truth.
- **Not Distribution Contract Stack:** that stack owns consumer-side selection, mirrors, fallback, verification, and install receipts.
