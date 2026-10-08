## Execution addendum (rev0443)
For questions about **what this promoted seam should actually ship in theory and practice**, read `design/cargo-artifact-contract-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- this file remains the frontier/strategy note;
- the sharper build answer is now spelled out as **reference layer + report/pack command + acceptance corpus**;
- and future edits should preserve selected subject, evidence path, final artifact identity, origin/staging, sidecar attachment, and bounded consumer handoff as separate truth classes.

# Design: Cargo Artifact Contract 2026Q1

## Thesis
The next worthy Rust ecosystem contribution in this band is **not** another target-dir scraper, release wrapper, or hosted build dashboard.
It is a thin **Cargo artifact contract** that turns Cargo's scattered output/plumbing surfaces into one reviewable boundary for:
- the **selected build subject**,
- the **phase or evidence path** used to learn about that subject,
- the **final artifacts Cargo exposed**,
- the **origin / staging / uplift posture** of those artifacts,
- attached **artifact-sidecars**,
- and bounded **downstream handoffs**.

This is the archive's existing **Artifact Surface Kit** promoted into a concrete frontier note because the upstream shape is now clearer than the repo used to admit.

## Why now
The official signals have converged unusually well:
- Rust's 2026 flagship “Building blocks” roadmap explicitly includes **prototype cargo plumbing commands** so Cargo can integrate better with larger build systems.  
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The accepted Cargo plumbing goal already splits a build into explicit phases—locate project, read manifests, read/write lockfile, resolve features, plan a build, execute a build, and **stage final artifacts**—and says later commands should accept the outputs of earlier ones.  
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- The 2025 GSoC plumbing prototype implemented seven such subcommands through `plan-build`, but **not** the final-artifact stage, and documented blockers in current Cargo APIs.  
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo's external-tools docs still say the stable integration surfaces are mainly `cargo metadata`, `--message-format=json`, and custom subcommands. Those are useful, but they do not yet give downstream tools one stable final-artifact subject/handoff contract.  
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo 1.93's custom-final-artifacts discussion makes clear that Cargo is already reasoning about **artifact staging, collision checks, selected-package rules, and Cargo-mediated uplift** rather than treating final outputs as a pure implementation detail.  
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The March 13, 2026 build-dir-layout-v2 testing call says many projects still rely on unspecified build-dir details due to missing Cargo features, and it names artifact lookup failure modes explicitly while also saying the layout of final artifacts in `target-dir` is **not** what is changing.  
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo's docs now distinguish **intermediate build artifacts** in `build-dir` from public-facing final artifacts, and nightly rustc's Cargo layout docs say `artifact-dir` is considered part of the public API.  
  https://doc.rust-lang.org/cargo/reference/build-cache.html  
  https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/layout/index.html
- Cargo's unstable docs say `--artifact-dir` exists because exact filenames are otherwise awkward to determine, and those same docs now tie SBOM precursor files to executable/linkable outputs uplifted into the target or artifact directories.  
  https://doc.rust-lang.org/cargo/reference/unstable.html

Together, those signals say the missing thing is no longer “some tool should probably parse Cargo output better someday.”
The missing thing is a bounded, reusable **artifact/plumbing contract** above the current ingredients.

## What this frontier is actually changing
This note promotes the repo's earlier artifact work as the next **build-system/plumbing-shaping** move.
It does **not** claim to be:
- the new overall #1 ecosystem need,
- a replacement for Build-State Evidence,
- a release/distribution manager,
- or a universal external-build-system interface.

The frontier change is narrower:
- keep **Build-State Evidence** as the strongest broad/buildable contribution;
- keep **Rust inner-loop contract** as the clearest build/debug bundle-shaping move;
- but promote **Artifact Surface Kit** as the clearest next **build-system/plumbing-shaping** move beneath **Build Interop + Artifact Surface + Release/Inventory/Repro handoff corridors**.

## Problem statement
Today, a serious downstream tool that wants to answer “what did Cargo actually produce for this build subject?” still has to reconstruct that story from a patchwork of:
- `cargo metadata`,
- `--message-format=json` build events,
- `--artifact-dir` copies,
- build-script environment variables,
- package file listings,
- unstable artifact-dependency environment variables,
- and target-dir/build-dir folklore.

That patchwork is enough to build point tools.
It is not enough to create one durable import layer for:
- release tooling,
- SBOM/inventory tools,
- reproducibility verification,
- support / incident intake,
- productization lanes,
- CI glue,
- or future editors/agents.

## The worthy contribution
The worthy contribution is a thin artifact family centered on the archive's existing `artifact-pack/v0` idea.

### Core truths that must stay separate
1. **Build subject truth**  
   Which workspace/package selection, target tuple(s), profile, features, toolchain, and command class were actually in scope.

2. **Phase / evidence-path truth**  
   Whether the result came from native Cargo JSON messages, a collected manifest pass, nightly artifact-dir copies, package listings, or bounded imports from adjacent tooling.

3. **Final artifact identity truth**  
   Which final outputs exist as outputs of the selected subject, including executable, linkable, docs, or packaged outputs.

4. **Origin / staging / uplift truth**  
   Whether an output is Cargo-native, rustdoc/package-native, or Cargo-mediated uplift from build-script staging or adjacent mechanisms.

5. **Sidecar truth**  
   Which sidecars actually attach to an artifact entry—for example SBOM precursor files—without pretending the sidecar replaces the artifact identity.

6. **Downstream handoff truth**  
   What Release, Inventory, Repro, Support, and productization consumers may conclude from the artifact surface without re-deriving the build.

## Reference shape
A first serious version should still look like the archive's earlier artifact family, but with plumbing-awareness made explicit:
- `artifact-brief/v0`
- `artifact-subject/v0`
- `artifact-entry/v0`
- `artifact-manifest/v0`
- `artifact-report/v0`
- `artifact-pack/v0`
- `artifact-handoff/v0`

What changes in this revision is the emphasis:
- treat these as the likely **companion layer above current Cargo plumbing surfaces**;
- and treat “stage final artifacts” as the missing seam between Cargo's explicit plumbing phases and the archive's downstream release/inventory/repro stacks.

## MVP in theory and practice
A worthy MVP would prove five concrete things.

### 1. One selected subject can be frozen honestly
The tool must identify the selected build subject without relying on path inference.
That means recording package selection, command class, target(s), profile, features, and toolchain posture explicitly.

### 2. Final outputs can be named without target-dir archaeology
The tool must enumerate final outputs and classify them, while admitting when it relied on unstable or lossy evidence paths.

### 3. Origin and copy behavior are reviewable
The tool must separate “Cargo produced this”, “Cargo copied this into artifact-dir”, and “Cargo mediated uplift/staging for this” instead of flattening them into one blob of files.

### 4. Sidecars attach without swallowing the story
The tool must link SBOM precursor or similar artifact-sidecars without pretending they fully define the artifact or the package.

### 5. Downstream consumers can import bounded summaries
The tool must produce handoffs that downstream consumers can reuse, rather than forcing each release/support/repro lane to re-scan paths and re-interpret Cargo behavior for itself.

## Recommended CLI posture
A reference implementation could still expose the previously proposed commands:
- `cargo artifacts collect`
- `cargo artifacts report`
- `cargo artifacts diff`
- `cargo artifacts handoff`
- `cargo artifacts pack`

But the frontier lesson here is more important than the exact spelling:
- the first implementation should import native Cargo surfaces where possible,
- state which parts remain unstable,
- and fail closed when it cannot safely widen from observed outputs to stronger artifact claims.

## What this should not become
Do **not** turn this into:
- another release orchestrator,
- another target-dir scraping helper sold as a standard,
- a universal build-system replacement,
- a hidden artifact score,
- or a hosted artifact inventory empire.

The right contribution is thinner and more reusable than that.

## Why this matters strategically
This frontier is “epic” because it sits exactly where several other archive priorities keep needing the same truth:
- Build-State / inner-loop work needs honest output boundaries.
- Release Truth needs a reusable import for Cargo-managed outputs.
- Inventory / SBOM work needs artifact-linked, not artifact-substituting, sidecars.
- Reproducibility verification needs a clean final-output set before it can compare rebuilds.
- Support and productization lanes need a handoff they can cite without replaying the build.

That is why this revision promotes the seam now instead of leaving it as a clever lower-level note.

## Read this with
- `design/artifact-surface-kit.md`
- `gaps/final-artifact-surface-identity-selection-outputs-and-handoffs.md`
- `proposals/epic-artifact-surface-kit.md`
- `design/build-interop-kit.md`
- `design/release-truth-stack.md`
- `design/inventory-evidence-stack.md`
- `design/repro-build-kit.md`
