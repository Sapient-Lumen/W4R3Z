# Toolchain & target support product plan — 2026-03-17

This note exists to keep **P-0484 Toolchain & Target Support Contract Kit** disciplined.
The archive already decided that the missing value is a **whole-project support contract** for toolchains, targets, docs posture, and contributor bootstrap.
This pass answers a narrower question:

> If somebody actually started building **P-0484** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps project maintainers publish one reviewable answer to:

### 2026-03-22 refinement — target-readiness should now be first-class

The latest 2026 support signals make one more artifact worth promoting into `0.1`: a **target-readiness report**.
A project-level support contract is stronger when it can also answer the target-focused checklist implied by the January 2026 safety-critical guidance:

- which Rust-project tier the target belongs to,
- whether the lane is `std` or `no_std`,
- what the last known tested environment was,
- which blockers still matter,
- and whether the project’s real lane is fully supported, compile-only, or still manual review.

That should stay inside **P-0484** because it is a whole-project support question, not a separate linker doctor or MSRV-only lane.


- which Rust toolchains they actually support,
- which targets are first-class versus weaker support lanes,
- which extra components, runners, SDKs, linkers, or manual steps are really required,
- which docs.rs target posture the project is implicitly or explicitly publishing,
- which claims are merely declared versus locally observed versus CI-verified,
- and what changed between releases.

It should **not** try to become an installer, cross-linker manager, hosted matrix dashboard, or docs.rs emulator.
Those are adjacent imports, not the core product.

## What the crate should provide other people

For downstream users, contributors, and integrators, the crate should provide:

1. **One compact support contract** instead of a scavenger hunt across `rust-toolchain.toml`, `.cargo/config.toml`, docs.rs metadata, CI YAML, and issue comments.
2. **Evidence classes for support claims** so “supported” does not blur together declared policy, local observation, docs-only visibility, and real CI verification.
3. **External-prerequisite honesty** about linkers, runners, SDKs, sysroots, and board/device requirements.
4. **Docs-surface truth** so a project can see what docs.rs target/default-target posture it is currently publishing.
5. **Bootstrap hints** that say what a contributor must install versus what is optional.
6. **Release diffs** so widening, narrowing, or muddying support becomes visible in code review and release review.
7. **A short human summary** that can be pasted into README sections, release notes, or support issue templates.

For maintainers, the crate should provide:

1. a compact policy file that is cheap to review,
2. small receipts/reports rather than a giant support portal,
3. a way to import rustup, Cargo, docs.rs, and CI facts without pretending they mean the same thing,
4. a conservative `manual_review_required` escape hatch,
5. and a drift report that makes support regressions loud.


## 2026-03-22 refinement — imported authority, public docs surface, and bundle shape should now be first-class

The latest official toolchain/target signals make three more `0.1` artifacts worth promoting:

- **`upstream-support-authority.import.json`** — imported Rust-project / rustup / docs.rs / Cargo facts that shape interpretation of the support story;
- **`public-docs-surface.receipt.json`** — what docs.rs is actually exposing, whether defaults were implicit, and which hosted limits mattered;
- **`toolchain-support-bundle.manifest.json`** — the portable support handoff inventory tying authority, local policy, docs posture, route/topology, readiness, and prerequisites together.

Those artifacts matter because “supported target” keeps becoming vague when a reviewer cannot tell:

- which facts came from upstream authority,
- what the project itself is claiming,
- what docs.rs is publicly exposing by default,
- and what one complete review bundle should contain.

## Recommended `0.1` command surface

### `cargo toolchain-support init`
Create a starter `toolchain-support.toml` by importing obvious candidates from:

- `rust-toolchain.toml` / `rust-toolchain`,
- `Cargo.toml` fields like `rust-version`,
- docs.rs metadata,
- `.cargo/config.toml`,
- and optional CI target declarations when explicitly pointed at them.

The generated contract should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` instead of guessed.

### `cargo toolchain-support capture`
Emit one normalized support bundle from the current workspace/repository state.
This should capture:

- toolchain intent,
- current environment facts,
- target posture,
- docs posture,
- and explicit external prerequisites.

### `cargo toolchain-support check`
Run the local validation pass:

- do declared channels / versions / target names parse,
- do requested components and targets match the active toolchain model,
- is `path`-toolchain behavior handled honestly,
- does docs.rs metadata imply a different public target surface than the contract says,
- do runner/linker requirements exist for the targets that claim more than compile-only support,
- and which parts remain manual-review-only?

### `cargo toolchain-support doctor`
Render the receiver-facing warnings for suspicious situations such as:

- `path_toolchain_ignores_profile`
- `docsrs_default_target_drift`
- `missing_required_component`
- `missing_required_target`
- `manual_linker_or_sdk_required`
- `runner_required_for_tests`
- `workspace_rust_version_policy_split`
- `support_claim_without_evidence`

`doctor` should be a human-first renderer over the checked artifacts, not a separate inference engine.

### `cargo toolchain-support import-authority`
Emit imported-upstream authority receipts for target-tier, rustup-host, docs.rs default-target, and Cargo path/config facts. These receipts should stay explicit about what the imported fact does **not** prove.

### `cargo toolchain-support docs-surface`
Emit the public docs-surface receipt from docs.rs metadata and known hosted-build rules. This command should keep hosted visibility separate from runtime or test support.

### `cargo toolchain-support summary`
Render a short contributor/downstream support summary.
This should be boring enough to paste into project docs without requiring a hosted dashboard.

### `cargo toolchain-support diff <old> <new>`
Compare two receipts or packs and classify:

- `toolchain_channel_changed`
- `rust_version_changed`
- `resolver_policy_changed`
- `component_requirement_changed`
- `target_added`
- `target_removed`
- `target_support_class_changed`
- `docs_posture_changed`
- `external_prerequisite_changed`
- `evidence_class_changed`
- `manual_review_required`

### `cargo toolchain-support pack`
Emit one compact `.supportbundle.zip` for CI artifacts, release review, contributor onboarding, or downstream packaging review.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `toolchain_support_model`
  - shared Rust types for policies, receipts, reports, evidence classes, support classes, and diffs
- `toolchain_support_discovery`
  - import logic for rustup files, Cargo manifests, Cargo config, docs.rs metadata, and optional CI hints
- `toolchain_support_check`
  - validation of components, targets, resolver/rust-version posture, docs target posture, and prerequisite declarations
- `toolchain_support_pack`
  - report writing, markdown summary rendering, diffing, and bundle emission
- `cargo-toolchain-support`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core format is trusted:

- `toolchain_support_rustup`
- `toolchain_support_docsrs`
- `toolchain_support_ci_github_actions`
- `toolchain_support_ci_generic`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should revolve around these files:

- `toolchain-support.toml`
- `toolchain-intent.snapshot.json`
- `toolchain-environment.receipt.json`
- `support-surface.report.json`
- `target-readiness.report.json`
- `support-drift.diff.json`
- `bootstrap-hints.md`
- `support-summary.md`
- `upstream-support-authority.import.json`
- `public-docs-surface.receipt.json`
- `toolchain-support-bundle.manifest.json`

This pass adds three more important artifacts:

- `support-class.policy.json` — what the support classes mean (`fully_supported`, `ci_verified`, `docs_default_surface`, `docs_only`, `compile_only`, `manual_setup_required`, `nightly_only`, `unknown`) and what minimum evidence each class expects.
- `support-evidence.report.json` — where each claim came from: declaration, local observation, docs.rs metadata, CI import, or manual note.
- `external-prerequisite.manifest.json` — explicit linkers, runners, SDKs, env vars, board requirements, and manual setup classes per target or host lane.
- `override-lineage.receipt.json` — which rustup selector actually won and which project requests were shadowed or ignored.
- `component-availability.report.json` — requested versus effective component/toolchain state, including nightly fallback or unavailable extras.
- `exercise-scope.report.json` — which scopes are truly covered for a lane (`compile`, `docs`, `run`, `test`, `bench`, `host_build_script`, `host_proc_macro`).

Those files matter because toolchain support becomes vague again if the archive only records toolchain names and targets but not:

- what support classes actually mean,
- what evidence backs the class,
- what non-Rust prerequisites still block real success,
- which selector actually made the current toolchain effective,
- whether the requested components were actually available,
- and which exercise scopes were really covered.

## Discovery order

A disciplined import order helps prevent false confidence.

1. **Effective override lineage**
   - `cargo +toolchain` shorthand
   - `RUSTUP_TOOLCHAIN`
   - directory overrides
   - `rust-toolchain.toml` / `rust-toolchain`
   - default toolchain
2. **Project-declared intent**
   - `rust-toolchain.toml` / `rust-toolchain`
   - `Cargo.toml` (`rust-version`, edition, workspace resolver)
3. **Cargo config**
   - target-specific `linker`, `runner`, `rustflags`, `rustdocflags`, `build.target`
4. **docs.rs posture**
   - `default-target`, `targets`, `additional-targets`, feature / rustdoc flags
5. **Observed local environment**
   - active toolchain, installed components, installed targets, host triple
6. **Optional CI/imported evidence**
   - explicit matrix entries or known checks when maintainers opt in
7. **Manual policy notes**
   - what still requires human review or external setup

The importer should prefer surfacing uncertainty over synthesizing false confidence.

## Support-class policy

The first implementation should treat **support classes as first-class review objects** and keep them distinct from Rust target tiers.

### What should count as support classes in `0.1`

- `fully_supported`
- `ci_verified`
- `docs_default_surface`
- `docs_only`
- `compile_only`
- `manual_setup_required`
- `nightly_only`
- `unknown`
- `manual_review_required`

### What should *not* be encoded as support classes in `0.1`

- “Tier 1 therefore supported by this project”
- “target exists in rustup therefore fully supported”
- “docs.rs built it therefore runtime-usable”
- “local machine had the linker once therefore everyone is fine”
- “Cargo can parse the target therefore the project stands behind it”

The policy file should be explicit, versioned, and diffable.
If a maintainer cannot explain why a target has a given class, the class should fall back to `manual_review_required` or `unknown`.

## Override-lineage policy

The first implementation should treat **effective selector lineage** as a first-class receipt rather than an implementation detail.

### What should be expressible in `0.1`

- `cli_shorthand`
- `env_toolchain`
- `directory_override`
- `toolchain_file`
- `default_toolchain`
- `manual_review_required`

plus notes about:

- proximity wins between directory overrides and toolchain files,
- `path` toolchains shadowing `components` / `targets` / `profile`,
- and requested-versus-effective toolchain drift.

### What should *not* be flattened together in `0.1`

- the repository pin,
- the active rustup selector,
- the installed default toolchain,
- and the toolchain a contributor actually used for a given capture.

If those disagree, the receipt should say so explicitly instead of collapsing back to one guessed “current toolchain”.

## Component-availability policy

The first implementation should treat **requested components** and **effective component availability** as separate review objects.

### What should be expressible in `0.1`

- requested profile
- requested extra components
- installed components
- unavailable components
- fallback_due_to_missing_component
- effective toolchain after fallback
- manual_review_required

### What should *not* be treated as the same thing in `0.1`

- “the project asked for clippy”
- “clippy exists on this channel/host/date”
- “rustup picked an older nightly so clippy exists”
- “the contributor actually has clippy installed now”

Those are related facts, but they are not interchangeable.

## Evidence policy

The first implementation should treat **evidence provenance** as an explicit report, not an implementation detail.

### Evidence classes worth modeling in `0.1`

- `declared`
- `observed_local`
- `observed_ci`
- `docsrs_metadata`
- `docsrs_default_inferred`
- `manual_note`

### What should *not* be treated as strong evidence in `0.1`

- one successful build on one laptop as proof of full support
- Rust target tier alone as project support proof
- docs visibility alone as runtime support proof
- a checked-in target name without matching prerequisites
- old release notes with no current repository evidence

If the evidence is weaker than the support class implies, `check` should emit a warning instead of silently upgrading the claim.

## External-prerequisite policy

The first implementation should treat non-Rust prerequisites as a separate artifact.

### What should be expressible in `0.1`

- linker required
- runner required
- SDK / NDK required
- custom target spec required
- board/device required
- environment variable or tool required
- manual install steps required

### What should *not* be auto-inferred confidently in `0.1`

- exact linker package names across every operating system
- vendor SDK install recipes for every target
- target usability from `cc`-crate presence alone
- detailed board flashing procedures
- global machine state outside explicitly configured Cargo/rustup inputs

If a project cannot state the prerequisite precisely, it should still be able to say `manual_setup_required` without pretending more.

## Exercise-scope policy

The first implementation should treat **what was actually exercised** as separate from the broad support class.

### What should count as exercise scopes in `0.1`

- `compile`
- `docs`
- `run`
- `test`
- `bench`
- `host_build_script`
- `host_proc_macro`
- `manual_review_required`

### What should *not* be flattened together in `0.1`

- “Cargo compiled the target”
- “docs.rs rendered the API”
- “cargo test could actually execute via a runner”
- “build scripts and proc macros received the same flags as the target lane”

If those differ, the report should preserve the split instead of upgrading everything to one broad support verdict.

## Proving-ground archetypes

A worthy first implementation should prove itself against at least five archetypes:

1. **Cross-platform library**
   - stable channel
   - docs.rs target drift risk
   - multiple docs targets but narrow runtime support
2. **Cross-compiled application**
   - installed Rust target but missing external linker / SDK
   - compile-only versus runnable support boundary
3. **Virtual workspace**
   - `resolver = "3"` and mixed `rust-version` policies
   - shared dependency selection side effects
4. **Embedded / device-aware crate**
   - runner or board requirement
   - host build success but device-only runtime truth
5. **Custom or path-toolchain project**
   - local toolchain path
   - `components`, `targets`, and `profile` in the file that actually have no effect

If `0.1` cannot survive those five, the vocabulary is still too narrow.

## Adoption staircase

Do not require the ecosystem to jump to a fully automated installation workflow at once.

### Stage 1 — import and annotate
- generate a starter contract
- let maintainers mark support classes and manual-review zones

### Stage 2 — local capture and checks
- capture intent and current environment
- verify docs.rs posture and prerequisite declarations
- keep evidence classes explicit

### Stage 3 — summary and bootstrap hints
- render contributor/downstream guidance from the declared contract
- make manual setup boundaries obvious

### Stage 4 — release diffs
- compare current release versus previous release
- make support drift visible

### Stage 5 — optional CI evidence imports
- import GitHub Actions or generic matrix evidence
- remain adapter-first, not CI-platform-first

## What should wait until later

Leave these for later unless `0.1` proves cramped without them:

- automated installer flows
- linker package provisioning
- full docs.rs build replay
- hosted dashboards
- registry-wide crawling of all crates
- vendor-specific SDK installers
- rich policy-as-code enforcement beyond the small support vocabulary

## Good failure modes

The crate should fail conservatively.
Preferred failure behavior:

- `path` toolchain with declared components/targets/profile → `path_toolchain_ignores_profile`
- target installed but linker/runner unclear → `manual_setup_required`
- docs.rs default-target posture left implicit → `docsrs_default_target_drift`
- support class stronger than evidence class → `support_claim_without_evidence`
- mixed workspace policies with unclear top-level effect → `workspace_rust_version_policy_split`
- unsupported or unknown target name → explicit parse / validation error

## Why this still looks worth building

The adjacent substrate is real, which is exactly why this proposal now looks sharper rather than weaker.

- Rust’s vision-doc work explicitly argues for more supportive interfaces from crates.
- The 2025 survey still shows that docs and code dominate how people learn Rust.
- rustup already models channels, profiles, components, targets, and `path` toolchain caveats.
- Cargo already exposes `rust-version`, resolver behavior, hierarchical config, target-specific linker/runner settings, and workspace-wide effects.
- docs.rs already exposes metadata knobs, current default-target behavior, nightly build context, cross-compilation behavior, and sandbox limits.
- the target-tier policy already explains what Rust-the-project means by tiered support, which helps clarify what a crate-local support contract is **not**.

That combination strengthens the case that the missing value is the **project-authored support contract above these pieces**, not another attempt to replace them.

## Non-goals for `0.1`

- not a replacement for rustup
- not a replacement for Cargo config
- not a replacement for docs.rs
- not a linker or SDK installer
- not a full CI orchestrator
- not a docs.rs parity emulator
- not a universal portability proof

## Recommended first proving fixtures

The archive’s fixture pack should keep growing around named awkward cases.
This pass especially strengthens the case for:

- `minimal_profile_missing_dev_components`
- `path_toolchain_ignores_components_and_targets`
- `compile_only_target_missing_linker`
- `docsrs_default_target_drift_after_2025_change`
- `virtual_workspace_resolver3_msrv_split`
- `cross_target_runner_required_for_tests`
- `official_rustup_host_exists_but_project_unclaimed`

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
- https://rust-lang.github.io/rustup/overrides.html
- https://rust-lang.github.io/rustup/concepts/profiles.html
- https://rust-lang.github.io/rustup/concepts/components.html
- https://rust-lang.github.io/rustup/cross-compilation.html
- https://doc.rust-lang.org/cargo/reference/rust-version.html
- https://doc.rust-lang.org/cargo/reference/config.html
- https://doc.rust-lang.org/cargo/reference/resolver.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://rust-lang.github.io/rfcs/2803-target-tier-policy.html
