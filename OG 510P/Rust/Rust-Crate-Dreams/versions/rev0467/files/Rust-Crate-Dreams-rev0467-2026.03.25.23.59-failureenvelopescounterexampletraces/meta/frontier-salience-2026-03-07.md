# Frontier salience scan — 2026-03-07

This file exists to resist archive sprawl.

The archive is now broad enough that a good pass should often **rank, compress, and redirect attention** rather than add another dozen proposals.

## External signals currently worth honoring

- The 2025 State of Rust survey says **resource usage (slow compile times and storage usage)** remains a major productivity problem, while **debugging** also remains near the top tier of pain.
- Rust’s 2026 flagship goals continue to promote more toolchain surfaces into explicit, machine-readable, or workflow-relevant seams (public dependencies, sanitizers, sized hierarchy, Wasm components).
- PyO3 + maturin and UniFFI + Apple XCFramework/SwiftPM docs show that Rust already has real cross-language substrate; the missing value is increasingly in **release contracts and coordination artifacts**, not raw foreign-function generation.
- Cargo's resolver docs, plumbing direction, relink goal, and build-dir-layout work together suggest another sharp seam: Rust increasingly has **substrate**, but ordinary teams still lack **compact explanation artifacts** for why Cargo resolved, rebuilt, or duplicated work the way it did.

Evidence anchors:

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://doc.rust-lang.org/cargo/reference/resolver.html
- https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://pyo3.rs/main/building-and-distribution
- https://www.maturin.rs/distribution.html
- https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
- https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages

## Ranking rules for the next few passes

Promote proposals when they satisfy most of these:

1. **daily pain** for ordinary Rust teams,
2. **clear substrate already exists**,
3. **MVP can ship as a crate + cargo subcommand**,
4. **artifact/receipt layer multiplies other crates**,
5. **adoption does not require waiting for language stabilization**.

Down-rank ideas when they are mostly:

- another parser/SDK where Rust already has one,
- a narrow protocol kit with little ecosystem leverage,
- or a speculative abstraction not anchored to current maintainer workflows.

## Tier A — strongest current bets

1. **P-0436 Target-Dir Lease & Shared Cache Coordination Kit**  
   The survey still points at compile/storage pain, and this proposal targets one of the most recurring everyday workflow seams.

2. **P-0428 Cargo Impact Planner Kit**  
   High leverage for CI and monorepo/workspace discipline; turns “what do we actually need to rebuild/retest?” into a reviewable artifact.

3. **P-0463 Libtest JSON Interop Kit**  
   Very broad upside because nearly every Rust team runs tests, and machine-readable output is finally becoming a sharper official seam.

4. **P-0434 Sanitizer Profile & Evidence Kit**  
   Strong debugging/reliability leverage; fits the survey’s persistent debugging pain and current toolchain direction.

5. **P-0466 Python Wheel ABI & Free-Threading ShipKit**  
   Huge bridge-to-adoption potential because Python remains one of the most important foreign ecosystems for Rust.

6. **P-0467 Apple XCFramework & SwiftPM ShipKit**  
   Strong SDK/mobile leverage where Rust substrate exists but release contracts are still improvised.

7. **P-0242 Reproducible Build Evidence Kit**  
   Remains one of the cleanest “trust + CI + enterprise” multipliers in the archive.

8. **P-0421 pprof + OpenTelemetry Profiling + Parca Interop Workbench Kit**  
   A strong debugging/profiling answer that is more likely to become a boring default than many protocol-specific ideas.

9. **P-0431 Public Dependency Boundary Kit**  
   Important because it converts a core library/release-management seam into an explicit workflow artifact.

10. **P-0001 Cargo Snapshot**  
    Still one of the most concrete, high-value enterprise/offline multipliers in the whole repo.

## Tier B — important, but only after Tier A keeps moving

- **P-0012 Desktop ShipKit** — valuable for product teams, but somewhat narrower than Python + Apple SDK release surfaces.
- **P-0121 FFI Boundary & Bindings Conformance Kit** — still strategically important, but should stay adapter/conformance-focused while sharper ecosystem-specific shipkits emerge.
- **P-0416 CloudEvents + CESQL + CDEvents Interop Workbench Kit** — strong standardization signal, but less universally painful than build/test/distribution workflows.
- **P-0408 XDG Desktop Portal Capability Portability Kit** — excellent Linux desktop leverage, but platform-specific.
- **P-0422 CEL Conformance & Portability Kit** — good multiplier if kept environment/receipt-first.

## What to de-emphasize for now

For the next few revisions, prefer **depth over breadth**:

- do not add many more narrow protocol interop kits unless they are unusually high-surface-area,
- do not add “yet another SDK” when the sharper missing layer is policy / bundle / receipt / replay,
- and do not treat official goals, guides, or generator crates as proof that maintainer workflows are already boring.

## Practical implication for future passes

A good next pass should usually do one of three things:

1. strengthen a Tier A proposal,
2. connect multiple existing proposals into a cleaner roadmap or incubator cluster,
3. or add one new proposal only if it is obviously Tier A or fills a genuinely missing adoption seam.


## Newly promoted after this pass

- **P-0469 Cargo Rebuild Explanation Kit** now belongs in the top frontier because it attacks one of the most recurring everyday questions in Rust teams: not “how fast is Cargo overall?” but **why did this particular build rebuild what it rebuilt?**
- **P-0468 Cargo Resolver Explanation Kit** also now belongs near the top frontier because Cargo increasingly has resolvers, trees, and plumbing surfaces, but still lacks a boring **cause-chain artifact** for feature activation, version choices, and duplicate-build splits.


## Newly promoted after this pass

- **P-0471 Cargo Artifact Handoff Kit** now belongs near the top frontier because Cargo increasingly has machine-readable output substrate, but ordinary CI/package-manager/build-system consumers still lack one compact artifact manifest they can trust and diff.
- **P-0470 Cargo Package Review Kit** rose because `cargo package` already creates the real shipped source bundle, yet maintainers still do publish review largely by hand; the sharper missing layer is a publish-readiness receipt, not another packager.


## Newly promoted after this pass

- **P-0472 Docs.rs Build Parity & Evidence Kit** rose because docs.rs now documents a rich build/metadata surface and even recommends `cargo docs-rs` in CI, while also explicitly saying that helper does not perfectly replicate the hosted environment. The sharper gap is a **preflight / drift / issue-bundle artifact**, not another docs runner.
- **P-0473 Cargo Lints Adoption Receipt Kit** rose because Cargo now has stable package/workspace lint policy plus an emerging Cargo-lint surface, but ordinary teams still lack a boring **inheritance / waiver / rollout receipt** for workspace-wide lint adoption.


## Newly promoted after this pass

- **P-0474 Cargo Config Layer Receipt Kit** rose because Cargo configuration has become a real operational surface—hierarchical files, includes, env precedence, `--config`, credential providers, and even an unstable viewer command exist—but ordinary teams still lack a compact **effective-config / origin-trace / redacted support bundle**.
- **P-0475 Rustdoc Mergeable Info Handoff Kit** rose because rustdoc and Cargo now have explicit `doc.parts` / merge / finalize substrate for cross-crate docs, but maintainers still lack a boring **manifest / compatibility / finalize receipt** for split or distributed documentation pipelines.


## Newly promoted after this pass

- **P-0476 Rustdoc Coverage Review Bundle Kit** rose because rustdoc now has machine-readable coverage output and a public JSON interface, but maintainers still lack a boring **API-aware docs debt / regression / review bundle**.
- **P-0477 Cargo Publish Receipt Join Kit** rose because local package review, registry checksums, trusted publishing, and new crates.io publish metadata now exist as real substrate, but maintainers still lack one boring **post-publish release receipt** that joins them.


## Frontier queue — 2026-03-07 (110)

1. **Docs coverage review bundles** — promoted to **P-0476** because rustdoc coverage JSON and rustdoc JSON now make a docs-review artifact sharper than another docs portal or dashboard.
2. **Publish-surface / provenance join layer** — promoted to **P-0477** because the sharper missing layer is now a local-review + registry-confirmation + publish-identity receipt.
3. **Artifact-sidecar contract kit** — still promising only if SBOM or adjacent sidecar conventions converge enough to justify a compact common vocabulary above P-0471.
4. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts and does not duplicate P-0469.
5. **Python/Apple release-drift diffing** — still promising follow-on work once P-0466 and P-0467 have stable receipt vocabularies.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-110)
- **P-0476 Rustdoc Coverage Review Bundle Kit** — strongest if it remains API-aware docs review and does not become a generic docs quality dashboard.
- **P-0477 Cargo Publish Receipt Join Kit** — strongest if it remains post-publish receipt / identity / checksum join work and does not become another publish orchestrator.


## Newly promoted after this pass

- **P-0478 Cargo Future-Incompat Triage Kit** rose because Cargo’s future-incompat report is now real and revisitable, but ordinary teams still lack a boring **owner / waiver / upgrade-path ledger** above that report.
- **P-0479 Cargo Artifact Sidecar Contract Kit** rose because Cargo’s artifact surface is increasingly producing attachable sidecars, especially SBOM precursors, but downstream tools still lack a compact **artifact-to-sidecar contract** with schema drift review.


## Frontier queue — 2026-03-07 (111)

1. **Cargo future-incompat triage** — promoted to **P-0478** because built-in report display now exists, and the sharper missing layer is ownership/waiver/remediation discipline rather than another diagnostics UI.
2. **Artifact-sidecar contract kit** — promoted to **P-0479** because SBOM precursor output and related sidecar signals now make a narrow attachment/schema contract sharper than another broad artifact exporter.
3. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts and does not duplicate P-0469.
4. **Python/Apple release-drift diffing** — still promising follow-on work once P-0466 and P-0467 have stable receipt vocabularies.
5. **Public-API release gate kit** — still promising above P-0431/P-0438 if it stays release-review-first.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-111)
- **P-0478 Cargo Future-Incompat Triage Kit** — strongest if it remains owner/waiver/remediation-first and does not become another generic report viewer.
- **P-0479 Cargo Artifact Sidecar Contract Kit** — strongest if it remains attachment/schema/diff-first and does not collapse back into a second artifact-handoff manifest.


## Newly promoted after this pass

- **P-0480 Cargo Global Cache Policy & GC Receipt Kit** rose because Cargo’s cache-GC story is now real enough that the sharper gap is no longer “some way to delete files,” but a boring **inventory / dry-run / exemption / receipt** workflow for Cargo home.
- **P-0481 Doctest Runtool Profile Kit** rose because rustdoc and Cargo now expose stable runner and cross-target doctest substrate, but maintainers still lack a boring **runner-profile / target-matrix / ignore-audit receipt** workflow.


## Frontier queue — 2026-03-07 (112)

1. **Cargo global-cache policy receipts** — promoted to **P-0480** because storage/resource pain remains real, Cargo now has actual GC substrate, and the sharper missing layer is inventory/policy/receipt discipline rather than another cleaner.
2. **Doctest runner profiles** — promoted to **P-0481** because stable `--test-runtool`, target-specific ignore attrs, and cross-target doctests now make a maintainer-facing support matrix sharper than another docs workflow wrapper.
3. **Python/Apple release-drift diffing** — still promising follow-on work once P-0466 and P-0467 have stable receipt vocabularies.
4. **Public-API release gate kit** — still promising above P-0431/P-0438 if it stays release-review-first.
5. **Debugger support-pack refresh** — promising only if it turns the 2026 debugging push into a compact compatibility/receipt workflow rather than another vague debugger wishlist.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-112)
- **P-0480 Cargo Global Cache Policy & GC Receipt Kit** — strongest if it remains inventory/policy/receipt-first and does not collapse back into a generic cache cleaner.
- **P-0481 Doctest Runtool Profile Kit** — strongest if it remains runner-profile/target-matrix/ignore-audit-first and does not become a full emulator orchestration layer.


## Newly promoted after this pass

- **P-0482 SDK Release Promise Drift Kit** rose because Python and Apple shipping substrate is now real enough that the sharper missing layer is a **consumer-promise diff / impact receipt**, not another builder or uploader.
- **P-0483 Public API Readiness Bundle Kit** rose because semver checks, public-API diffing, public/private dependency work, and docs-surface metrics now make a **joined release-review bundle** sharper than another stand-alone analyzer.


## Frontier queue — 2026-03-07 (113)

1. **Python/Apple release-promise drifting** — promoted to **P-0482** because foreign-SDK shipping is no longer blocked on raw builders; the sharper gap is a consumer-promise diff and impact receipt.
2. **Public-API release readiness bundles** — promoted to **P-0483** because public-surface review now has enough substrate that the next missing layer is a joined readiness artifact, not another one-off checker.
3. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts and does not duplicate P-0469 or P-0480.
4. **Debugger support-pack refresh** — promising only if it turns debugging friction into a compact compatibility/receipt workflow rather than another general debugger wishlist.
5. **Foreign-SDK consumer doctor** — promising follow-on work once P-0482 stabilizes its promise vocabulary and receipts.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-113)
- **P-0482 SDK Release Promise Drift Kit** — strongest if it remains promise/diff/impact-first and does not become a second shipkit.
- **P-0483 Public API Readiness Bundle Kit** — strongest if it remains joined public-contract review and does not collapse back into a general compatibility platform.


## Newly promoted after this pass

- **P-0484 Toolchain & Target Support Contract Kit** rose because rustup toolchain files, profiles, components, targets, docs.rs metadata, and target-policy expectations now give Rust real support substrate, but ordinary teams still lack one boring **support contract / environment receipt / drift bundle**.
- **P-0485 Verification Campaign Workbench Kit** rose because Rust now has meaningful Miri/Kani/Creusot/Prusti/Flux/BorrowSanitizer-era substrate, but maintainers still lack a boring **obligation / trust / evidence / drift artifact** across tools.

## Frontier queue — 2026-03-07 (114)

1. **Toolchain/target support contracts** — promoted to **P-0484** because `rust-toolchain.toml`, rustup targets/components/profiles, and docs.rs metadata now make a joined support artifact sharper than another installer or CI wrapper.
2. **Multi-verifier campaign bundles** — promoted to **P-0485** because Rust verification substrate is now broad enough that the sharper missing layer is a trust/evidence/diff workbench above individual tools.
3. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts rather than duplicating P-0469 or P-0480.
4. **Debugger support-pack refresh** — still promising only if it becomes a compact compatibility/receipt workflow above P-0083 rather than another general debugger wishlist.
5. **Foreign-SDK consumer doctor** — still promising follow-on work once P-0482 stabilizes its promise vocabulary and receipts.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-114)
- **P-0484 Toolchain & Target Support Contract Kit** — strongest if it remains support-contract/diff/bootstrap-first and does not become another installer or linker manager.
- **P-0485 Verification Campaign Workbench Kit** — strongest if it remains obligation/trust/diff-first and does not collapse into a giant replacement verifier.


## Added 2026-03-07 (115)
- **P-0486 Debuggability Support Contract Kit** rose because Cargo/rustc/debugger surfaces now already cover debug levels, split debuginfo, strip behavior, visualizers, and path sanitization, while debugging still ranks among Rust’s top productivity problems; the sharper gap is a **support-posture / symbol-sidecar / drift bundle**.
- **P-0487 Foreign SDK Consumer Doctor Kit** rose because Python packaging and Apple SDK distribution now already define a lot of consumer-facing contract surface, but downstream users still lack a boring **environment / artifact / mismatch diagnosis** bundle distinct from producer-side release drift.

### Queue shifts
1. **Debuggability support contracts** — promoted to **P-0486** because debugging pain remains real and Rust’s substrate is now rich enough that the next leverage point is a receipt and policy workflow rather than another debugger wish list.
2. **Foreign-SDK consumer diagnosis** — promoted to **P-0487** because P-0482 covered producer-side release promises, leaving consumer-side intake diagnosis as a distinct and still-missing seam.
3. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts rather than duplicating P-0469 or P-0480.
4. **Debugger UX refresh** — still promising only if it becomes a crisp formatter/conformance follow-on above P-0083 and P-0486 rather than another vague toolkit.
5. **Additional foreign package ecosystems** — promising only after Python and Apple diagnosis vocabulary in P-0487 proves stable enough to generalize.


## Added 2026-03-07 (116)
- **P-0488 Cargo Minimal-Version Witness Kit** rose because Cargo now has real lower-bound substrate (`direct-minimal-versions`, version-floor semantics, and `implicit_minimum_version_req`), but ordinary teams still lack a boring **policy / blame / waiver / diff witness** for dependency floors.
- **P-0489 Cargo Build-Dir Consumer Transition Kit** rose because Cargo now explicitly treats build-dir layout as internal while build-dir/new-layout work calls for a transition path for tooling that accesses intermediate artifacts; the sharper gap is a **consumer audit / path contract / transition receipt**.


## Frontier queue — 2026-03-07 (116)

1. **Lower-bound dependency witnesses** — promoted to **P-0488** because Cargo’s lower-bound substrate and new minimum-version lint now make a reviewable witness sharper than a generic dependency updater or compatibility platform.
2. **Build-dir consumer transitions** — promoted to **P-0489** because Cargo’s evolving build-dir story now clearly creates a tooling-migration seam distinct from cache policy or final-artifact handoff.
3. **Debugger formatter/conformance refresh** — still promising only if it becomes a clean follow-on above P-0083 and P-0486 instead of a broad debugger platform.
4. **Other foreign package ecosystems** — still promising only after the Python/Apple consumer-diagnosis vocabulary proves stable enough to generalize.
5. **Cargo cache contention explainer** — still promising if it stays narrowly on live blocking facts rather than duplicating P-0436, P-0480, or P-0489.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-116)
- **P-0488 Cargo Minimal-Version Witness Kit** — strongest if it remains lower-bound-proof/blame/waiver-first and does not turn into a generic dependency updater.
- **P-0489 Cargo Build-Dir Consumer Transition Kit** — strongest if it remains audit/path-contract/transition-first and does not collapse into another cache manager or profiler.


## Added 2026-03-07 (117)
- **P-0490 Cargo Lock Contention Witness Kit** rose because the sharper missing layer is no longer “Cargo caches are mysterious,” but a compact artifact for **who blocked whom, on which root, and what mitigation makes sense**.
- **P-0491 Debugger Visualizer Compatibility Kit** rose because stable embedded visualizer substrate now exists, but maintainers still cannot hand one another a boring **backend matrix / render-golden / drift receipt** for those assets.


## Frontier queue — 2026-03-07 (117)

1. **Cargo lock-contention witnesses** — promoted to **P-0490** because Cargo and rust-analyzer now document enough blocking substrate that the sharper missing layer is a live wait/collision/mitigation artifact.
2. **Debugger visualizer compatibility receipts** — promoted to **P-0491** because stable embedded NatVis/GDB support now makes a narrow backend-matrix follow-on sharper than another broad debugger toolkit.
3. **Other foreign package ecosystems** — still promising only after the Python/Apple consumer-diagnosis vocabulary proves stable enough to generalize.
4. **Cargo compile-time-deps workflow receipts** — still promising if it stays narrowly on tool-only build surfaces and does not collapse back into generic editor/Cargo performance tooling.
5. **Build-std adoption receipts** — still promising if the unstable substrate sharpens enough that a new workflow layer would not duplicate existing build-std workbench territory.

## Watchlist additions (2026-03-07-117)
- **P-0490 Cargo Lock Contention Witness Kit** — strongest if it remains live-blocking/wait/mitigation-first and does not become another profiler, scheduler, or cache manager.
- **P-0491 Debugger Visualizer Compatibility Kit** — strongest if it remains asset/back-end matrix first and does not collapse into P-0083’s formatter-pack ambition or P-0486’s broader support contract.


## Added 2026-03-07 (118)
- **P-0492 Cargo Registry Auth Doctor Kit** rose because Cargo’s registry-auth world now includes credential providers, authenticated sparse registries, and trusted-publishing-adjacent identity flows, but maintainers still lack a boring **provider-chain / stage / redacted diagnosis bundle**.
- **P-0493 Source Path Hygiene & Debug Source Kit** rose because remap-paths, trim-paths, virtual `/rustc/...` paths, and installable source components now make source lookup a real release/support surface, but maintainers still lack a boring **path-hygiene / virtual-source / component-hint receipt**.


## Frontier queue — 2026-03-07 (118)

1. **Registry-auth diagnosis receipts** — promoted to **P-0492** because Cargo now has enough registry/provider/authenticated-sparse substrate that the sharper missing layer is a redacted provider-chain and operation-stage diagnosis artifact.
2. **Source-path hygiene and debug-source receipts** — promoted to **P-0493** because remap-paths, trim-paths, and rustup source components now make a compact source-lookup/support artifact sharper than another broad debugger tool.
3. **Other foreign package ecosystems** — still promising only after the Python/Apple vocabulary in P-0482 and P-0487 proves stable enough to generalize.
4. **Cargo compile-time-deps workflow receipts** — still promising if it stays narrowly on tool-only build surfaces and does not collapse back into generic editor/Cargo performance tooling.
5. **Build-std adoption receipts** — still promising only if the unstable substrate sharpens enough that a new workflow layer would not duplicate P-0430.

## Watchlist additions (2026-03-07-118)
- **P-0492 Cargo Registry Auth Doctor Kit** — strongest if it remains provider-chain/stage/redaction-first and does not turn into a token manager, registry implementation, or generic security platform.
- **P-0493 Source Path Hygiene & Debug Source Kit** — strongest if it remains path-hygiene/virtual-source/component-hint-first and does not collapse into P-0486’s broader debuggability contract or a full debugger launcher.


## Added 2026-03-07 (119)
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** rose because Cargo now explicitly documents a tool-only compile surface for tools like rust-analyzer, but maintainers still cannot hand one another a boring **tool-build / parity / fallback receipt**.
- **P-0495 Cargo Artifact Dependency Adoption Kit** rose because Cargo artifact dependencies are no longer just RFC theory, but maintainers still cannot hand one another a boring **artifact contract / target matrix / env-var / stable fallback** bundle.


## Frontier queue — 2026-03-07 (119)

1. **Compile-time-deps workflow receipts** — promoted to **P-0494** because Cargo now explicitly documents a tool-only compile surface intended for tools, while the `cargo check` policy boundary keeps the missing layer firmly in parity/fallback artifacts rather than build correctness claims.
2. **Artifact-dependency adoption receipts** — promoted to **P-0495** because Cargo’s artifact-dependency substrate plus RFC 3028 / RFC 3176 now make a contract/target/env-var/fallback layer sharper than another generic build helper.
3. **Other foreign package ecosystems** — still promising once the Python/Apple and generic foreign-consumer vocabulary proves stable enough to generalize to Node/npm, NuGet, or similar ecosystems.
4. **Invocation-reuse compatibility kit** — still promising if the 2026 incremental-systems work sharpens a clean check/build/clippy reuse receipt distinct from P-0490 and P-0494.
5. **Build-std adoption receipts** — still promising only if a new workflow layer would sharpen support/adoption facts without duplicating P-0430 or related sanitizer/toolchain proposals.

## Watchlist additions (2026-03-07-119)
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — strongest if it remains tool-surface/parity/fallback-first and does not turn into a rust-analyzer fork, a new checker, or a false equivalence layer between `cargo check` and `cargo build`.
- **P-0495 Cargo Artifact Dependency Adoption Kit** — strongest if it remains contract/target/env-var/fallback-first and does not collapse into another final-artifact exporter, package manager, or Cargo syntax proposal.


## Added 2026-03-07 (120)
- **P-0496 Cargo Vendor & Source Parity Kit** rose because Cargo’s source replacement, directory sources, local registries, and `cargo vendor` substrate are already real, but maintainers still cannot hand one another a boring **source-origin / registry-equivalence / offline-readiness** bundle.
- **P-0497 CPU Baseline & Runtime Dispatch Contract Kit** rose because Rust already has `target-cpu`, `target-feature`, `cfg(target_feature)`, and runtime feature detection, but maintainers still cannot hand one another a boring **hardware support promise / dispatch manifest / illegal-instruction risk** artifact.


## Frontier queue — 2026-03-07 (120)

1. **Vendor/source-parity receipts** — promoted to **P-0496** because Cargo now has serious source-management substrate, while the sharper missing layer is a source-origin and offline-honesty artifact rather than another mirror or registry.
2. **CPU baseline/runtime-dispatch contracts** — promoted to **P-0497** because Rust already has codegen knobs and runtime detection, while the sharper missing layer is a downstream hardware-support promise rather than another SIMD abstraction.
3. **Other foreign package ecosystems** — still promising once the Python/Apple and generic foreign-consumer vocabulary proves stable enough to generalize to Node/npm, NuGet, or similar ecosystems.
4. **Invocation-reuse compatibility kit** — still promising if the 2026 incremental-systems work sharpens a clean check/build/clippy reuse receipt distinct from P-0490 and P-0494.
5. **Build-std adoption receipts** — still promising only if a new workflow layer would sharpen support/adoption facts without duplicating P-0430 or related sanitizer/toolchain proposals.

## Watchlist additions (2026-03-07-120)
- **P-0496 Cargo Vendor & Source Parity Kit** — strongest if it remains source-origin/parity/offline-honesty-first and does not collapse into another mirror, registry, or package-review system.
- **P-0497 CPU Baseline & Runtime Dispatch Contract Kit** — strongest if it remains hardware-support/dispatch/fallback-first and does not turn into another SIMD abstraction, benchmark harness, or compiler-wrapper fantasy.

## Added 2026-03-07 (121)
- **P-0498 Node-API Package & Prebuild Contract Kit** rose because Node.js already gives Rust an ABI-stable addon substrate and napi-rs already gives it mature authoring/build ergonomics, but maintainers still lack a boring **runtime contract / prebuild manifest / loader receipt / support-risk** bundle.
- **P-0499 NuGet Native Interop ShipKit** rose because Microsoft already gives Rust RID-aware native packaging and probing rules while csbindgen already smooths Rust→C# bindings, but maintainers still lack a boring **RID contract / binding receipt / native-load report / support-risk** bundle.


## Frontier queue — 2026-03-07 (121)

1. **Other foreign package ecosystems** — promoted into **P-0498** and **P-0499** because the sharper missing value turned out not to be “generic foreign bindings” but package-manager-specific release contracts for Node/npm and NuGet.
2. **Invocation-reuse compatibility kit** — still promising if the incremental-systems work sharpens a clean check/build/clippy reuse receipt distinct from P-0490 and P-0494.
3. **Build-std adoption receipts** — still promising only if a new workflow layer would sharpen support/adoption facts without duplicating P-0430 or sanitizer/toolchain support proposals.
4. **JAR/JNI ship contracts** — still promising once the archive wants another foreign package ecosystem and can keep the focus on package/runtime contracts rather than raw JNI bindings.
5. **Cross-ecosystem support-contract generalization** — still promising only after Python, Apple, Node/npm, and NuGet vocabularies prove stable enough to share more schema.

## Watchlist additions (2026-03-07-121)
- **P-0498 Node-API Package & Prebuild Contract Kit** — strongest if it remains runtime-contract/prebuild/loader-first and does not turn into another binding generator, npm publisher, or vague “Rust for JS” toolkit.
- **P-0499 NuGet Native Interop ShipKit** — strongest if it remains RID/binding/probing-first and does not collapse into a general .NET build system or another raw binding generator.

