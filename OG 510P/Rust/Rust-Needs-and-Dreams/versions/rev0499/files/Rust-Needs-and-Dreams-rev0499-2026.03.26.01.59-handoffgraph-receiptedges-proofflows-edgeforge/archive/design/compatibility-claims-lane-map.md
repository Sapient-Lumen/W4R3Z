# Design: Compatibility Claims lane map (dev-host, source-build, release-artifact, docs-surface, runtime-floor, debugger tuples, acceptance profiles, consumer views)

## Goal
Sharpen **Compatibility Claims Stack** so the archive stops treating “supported” as one bucket.
The live Rust ecosystem now has several materially different compatibility-adjacent lanes, and they differ in **what subject is being judged**, **whether the claim is declared or observed**, **which toolchain / provisioning / docs / debugger / compiler-lane context produced it**, and **how safely the result can be compressed for downstream consumers**.

The archive should therefore keep compatibility work grounded in a lane map instead of one flattened support matrix or badge.

## Signals from the current ecosystem
- Rust’s target-tier policy already distinguishes different guarantee levels and explicitly treats **host tools** as an extra tier-sensitive promise. That means “the target exists” and “the toolchain you need is supported” are already different lanes upstream.
  https://doc.rust-lang.org/rustc/target-tier-policy.html
- The rustc platform-support pages already record target-specific **runtime-floor and environment requirements** for at least some targets — for example Linux kernel, glibc, SDK, or CPU assumptions. That means platform compatibility is not reducible to a triple alone.
  https://doc.rust-lang.org/beta/rustc/platform-support.html
  https://doc.rust-lang.org/beta/rustc/platform-support/s390x-unknown-linux-gnu.html
  https://doc.rust-lang.org/beta/rustc/platform-support/windows-msvc.html
- docs.rs metadata already lets crate authors choose `default-target`, `targets`, and `additional-targets`, and the docs.rs build docs say `#[cfg(docsrs)]` only applies to the final rustdoc invocation and not to dependencies or workspace members. That is direct evidence that docs builds are a distinct compatibility lane, not merely a side effect of ordinary builds.
  https://docs.rs/about/metadata
  https://docs.rs/about/builds
- docs.rs changed its default target list in October 2025, proving that docs-target posture is a public ecosystem-facing signal that can drift even when a crate’s source code does not.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- The Rust 2024 edition guide says `edition = "2024"` implies resolver `3`, which enables a Rust-version-aware dependency resolver. Cargo’s resolver/reference docs also say different workspace members’ `rust-version` settings can influence chosen dependency versions. That means source-build compatibility can vary materially by toolchain/MSRV lane even when the source tree is the same.
  https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
  https://doc.rust-lang.org/cargo/reference/resolver.html
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- The Rust Reference exposes `debugger_visualizer`, and the compiler dev guide says Rust supports three major debuggers with different constraints and debug-info realities. That means debugger-facing compatibility is a real public lane rather than purely local setup lore.
  https://doc.rust-lang.org/reference/attributes/debugger.html
  https://rustc-dev-guide.rust-lang.org/debuginfo/intro.html
- The 2026 debugging survey explicitly asks about debugger-version and OS support, quality visualizers, async debugging, and Rust expression evaluation. Even before results, the questionnaire itself is a strong signal that the community already experiences debugger support as a multi-lane compatibility boundary.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The 2026 flagships and 2025H2 goals keep next-solver, Polonius, and evolving trait hierarchies active. That means compiler-pattern acceptance remains a moving compatibility boundary for advanced crates and frameworks.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
  https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
  https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while editor/LLM workflows continue to rise. That increases the value of attachable compatibility truth instead of prose-only caveats.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The March 2026 “Rust’s challenges” writeup says expert pain shifts toward domain-specific and ecosystem-maturity issues rather than disappearing with experience. Compatibility-claim drift is exactly that kind of advanced-user problem.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- Cargo’s `supported-targets` RFC remains a demand signal for first-class target-support declarations, but it still only covers one slice of the wider compatibility-claims problem.
  https://github.com/rust-lang/rfcs/pull/3759

## The lanes

### 1) Development-host lane
This is the lane where the question is: can maintainers and contributors develop on this host with the expected host tools?

What defines it:
- host triple and host-tool posture
- rustc/cargo/clippy/rustfmt/rustdoc/rust-analyzer expectations
- local-native versus wrapper-assisted development posture
- editor/diagnostic friendliness where intentionally claimed

Why it deserves its own lane:
- developer-host claims are not the same as source-build claims or shipped-artifact claims
- target-tier policy already separates host-tools guarantees from weaker target existence
- teams routinely overclaim by publishing end-user support matrices that say nothing about contributor-host reality

Design rule:
- keep dev-host support distinct from source-build, release-artifact, docs, and debugger claims

### 2) Source-build lane
This is the lane where the question is: can this project be built from source for the target under a named toolchain / provisioning / MSRV posture?

What defines it:
- toolchain channel/version and `rust-version` posture
- resolver/MSRV-sensitive dependency selection
- native build versus cross/build-std/custom-target posture
- build/test/package/run-smoke evidence strength

Why it deserves its own lane:
- resolver `3` and Rust-version-aware resolution mean source-build compatibility can change with the toolchain even before runtime or debugger concerns appear
- custom targets, `build-std`, zig/xwin/cross, and similar lanes are real but non-equivalent
- “compiles for the target” is not the same as “we ship and support a release artifact for users on that target”

Design rule:
- keep source-build truth distinct from dev-host comfort, runtime floors, and shipped release claims

### 3) Release-artifact lane
This is the lane where the question is: what prebuilt artifact or package family is actually shipped and supported for end users?

What defines it:
- binary/library/package subject identity
- target triple and packaging/distribution form
- built/package/signed/attested/notarized posture where relevant
- install/update/support attachment points

Why it deserves its own lane:
- a project may support source builds without shipping binaries
- a project may ship a binary while explicitly not supporting arbitrary local source builds
- user-facing compatibility decisions often depend on shipped artifacts and installers, not just on whether CI compiled something

Design rule:
- keep release-artifact truth distinct from both source-build and downstream install/update conclusions

### 4) Docs-surface lane
This is the lane where the question is: what documentation build/target/configuration is publicly presented as canonical or representative?

What defines it:
- docs.rs `default-target`, `targets`, `additional-targets`
- docs-only cfg behavior like `#[cfg(docsrs)]`
- docs-target selection and omissions
- local-docs versus docs.rs differences where known

Why it deserves its own lane:
- docs.rs metadata and defaults are public-facing compatibility signals
- docs.rs build behavior differs from ordinary local builds in important ways
- documentation may imply or hide support posture if this lane is left implicit

Design rule:
- keep docs-surface truth distinct from source-build, release-artifact, and debugger truth

### 5) Runtime-floor lane
This is the lane where the question is: what minimum OS / kernel / libc / SDK / CRT / ABI / CPU assumptions are attached to the support claim?

What defines it:
- minimum runtime versions where known
- ABI or toolchain-runtime assumptions
- CPU-feature or emulator assumptions where relevant
- whether the floor is declared, derived, or observed

Why it deserves its own lane:
- rustc platform-support pages already record runtime floors for some targets
- a supported target triple can still hide meaningful runtime preconditions
- this lane is strategically important for long-lived, regulated, and enterprise adopters

Design rule:
- keep runtime-floor facts distinct from target-triple labels and from release/install UX

### 6) Debugger-tuple lane
This is the lane where the question is: which debugger family/version/OS/target/toolchain tuples are expected to work, with what visualizer and async-inspection posture?

What defines it:
- debugger family/version/OS/target/toolchain tuple
- visualizer availability and format
- async-debug and expression-evaluation posture
- native debugger support versus side-channel/runtime-inspection support

Why it deserves its own lane:
- the Rust docs and survey material already treat debugger behavior as plural rather than universal
- code can compile and run while debugging remains partial or broken
- visualizers are public artifacts now, not hidden maintainers’ local hacks

Design rule:
- keep debugger tuple truth imported and explicit rather than silently implied by platform support

### 7) Acceptance-profile lane
This is the lane where the question is: which advanced trait/borrow/solver-sensitive patterns are intentionally accepted on which compiler lanes?

What defines it:
- stable/beta/nightly/next-solver/Polonius/experimental lane identity
- pattern catalogs and expected pass/fail/xfail posture
- workaround truth and migration notes
- reason-coded semantic diffs across lanes or releases

Why it deserves its own lane:
- compiler-pattern acceptance remains a moving compatibility boundary for advanced crates
- “works on stable” and “works on nightly with next-solver” are materially different claims
- workaround-heavy support should not be hidden behind one green badge

Design rule:
- keep acceptance truth distinct from support/debugger truths and from mere stderr-snapshot churn

### 8) Consumer-view lane
This is the lane where compatibility truth is compressed for docs, release notes, support pages, CI, policy, audit, or assistants.

What defines it:
- consumer class
- permitted claims and mandatory caveats
- links back to support/debugger/acceptance evidence
- forbidden automatic conclusions

Why it deserves its own lane:
- this is where the ecosystem is most tempted to invent one fake “supported” verdict
- different consumers need different compression rules
- honest consumer views remain downstream and bounded rather than becoming the source of truth

Design rule:
- keep rendered views thin, explainable, and explicitly downstream of the canonical lanes

## Cross-lane adapter risks
The archive should make at least these risks explicit:
1. **dev-host ↔ source-build**
   - “contributors can work on this host” is not the same claim as “users can build this from source for that target”.
2. **source-build ↔ release-artifact**
   - green CI or cross-build output is not automatically a shipped/supported artifact contract.
3. **source-build ↔ docs-surface**
   - docs.rs cfgs and target choices can diverge from local or CI build posture.
4. **target triple ↔ runtime floor**
   - a target label does not fully describe runtime-version or ABI expectations.
5. **platform support ↔ debugger tuple**
   - compile/run posture does not imply stable debugger/version/visualizer support.
6. **platform/debugger ↔ acceptance profile**
   - public runtime support does not imply advanced-pattern acceptance on every compiler lane.
7. **any evidence lane ↔ consumer summary**
   - docs/support/release/policy/assistant summaries must not silently replace the canonical evidence with one badge.

## What should change elsewhere in the archive
- **Compatibility Claims Stack** should cite this lane map as the rule for what must stay separate.
- **Support Envelope Kit** should remain the owner of dev-host, source-build, release-artifact, docs-surface, and runtime-floor truth, but should now read through this lane map when claiming “support”.
- **Debuggability Stack** should keep owning debugger family/version/OS/visualizer/async-inspection evidence and export it into compatibility claims rather than being silently absorbed.
- **Acceptance Surface Kit** should keep owning compiler-lane/pattern/workaround truth and export it into compatibility claims rather than becoming one more support table column.
- **Release Truth**, **Distribution Contract**, **DocProof**, **Safety Evidence**, **Policy**, and **Support Envelope consumers** should import bounded compatibility views rather than each narrating a hidden universal compatibility model.

## Worthy contribution, sharpened
The worthy contribution here is **not** another platform matrix, debugger dashboard, UI-test harness, or compatibility badge.
It is a thin `cargo compat` / `compat-pack/v0` layer whose lane catalogs, imported claim registers, diffs, and bounded consumer summaries let Rust teams compare compatibility claims honestly across development hosts, source builds, release artifacts, docs surfaces, runtime floors, debugger tuples, and compiler-pattern acceptance without semantic collapse.
