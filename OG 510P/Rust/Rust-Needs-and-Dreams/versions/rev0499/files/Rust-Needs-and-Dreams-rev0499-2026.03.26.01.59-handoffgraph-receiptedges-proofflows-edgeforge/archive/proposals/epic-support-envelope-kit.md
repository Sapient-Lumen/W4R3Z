# Epic proposal: Support Envelope Kit

## Thesis
Rust already has substantial platform machinery:
- target triples and target tiers,
- host-tool distinctions,
- docs.rs target metadata,
- `supported-targets` design work,
- cross-compilation wrappers,
- `build-std` / custom-target lanes,
- and target-aware dependency policy tools.

What it still lacks is a **shared support-contract layer** that makes platform promises durable, diffable, and reviewable.

That is the worthy contribution here.
Not another wrapper.
Not another badge.
A support-contract substrate.

## Why this deserves promotion
This thread started as a sensible Tier 1/2 idea.
It now looks stronger than that because the surrounding ecosystem has matured in a revealing way:
- Rust’s own target map is changing over time,
- docs.rs target defaults now change in response to platform reality,
- Cargo is actively exploring declaration of supported targets,
- and serious provisioning tools already exist.

That means the bottleneck is no longer “nobody can build for anything.”
The bottleneck is “projects still cannot state, verify, and diff what they support in a way other tools can consume.”

Sources:
- https://doc.rust-lang.org/beta/rustc/platform-support.html
- https://doc.rust-lang.org/beta/rustc/target-tier-policy.html
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://github.com/rust-lang/rfcs/pull/3759
- https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- https://doc.rust-lang.org/rustc/targets/custom.html
- https://github.com/cross-rs/cross
- https://github.com/rust-cross/cargo-zigbuild
- https://github.com/rust-cross/cargo-xwin
- https://doc.rust-lang.org/beta/releases.html

## Proposed shape
Ship a narrowly scoped reference stack:
1. `support-envelope/v0` for the declared support contract
2. `runtime-floor-report/v0` for explicit OS/kernel/libc/SDK/ABI/CPU-feature floors
3. `support-observation-report/v0` for actual validation evidence, by lane and backend
4. `support-diff-report/v0` for support drift between releases or between claim vs evidence
5. optional `support-waiver/v0` for time-bounded exceptions
6. `support-pack/v0` bundle for CI, release review, docs, policy, and discoverability

The strongest version is boring, adapter-heavy, and explicit about uncertainty.
It should turn today’s support signals into one reviewable story rather than trying to replace them.

## The critical design bet
The kit should make **support-lane identity** first-class.
At minimum it must separate:
- `dev-host`
- `source-build`
- `release-artifact`
- `docs-surface`

Without that split, the ecosystem will keep lying accidentally.
A package that compiles under `zigbuild` from Linux to Windows is not making the same promise as a package that officially supports native Windows development or ships supported Windows binaries.

## Why the runtime-floor layer matters
A plain target triple is not a full support contract.
For real projects, users care about:
- minimum glibc or musl story,
- minimum macOS / Windows / SDK floor,
- kernel floors,
- CPU-feature assumptions,
- system-library / runner assumptions,
- whether the artifact was merely compiled or actually run.

This is especially important because some of those floors appear today only as:
- rustc target notes,
- tool-specific flags,
- CI image choices,
- or maintainer folklore.

A strong `runtime-floor-report/v0` turns those hidden assumptions into something that release tooling and users can review.

## Pilot-program refresh
The archive should no longer treat Support Envelope as just a schema set waiting for generic adoption. The next credible move is a ranked pilot program with explicit evidence policies and scorecards.

Use [`design/support-envelope-pilot-program.md`](../design/support-envelope-pilot-program.md) as the execution anchor and keep [`design/compatibility-claims-pilot-program.md`](../design/compatibility-claims-pilot-program.md) as the broader cross-stack frame.

The recommended rollout is now:
1. released-binary support lane
2. source-build / custom-target lane
3. docs-surface lane
4. runtime-floor derivation lane
5. long-lived / support-window lane

That order matters. It starts where user-facing support claims are easiest to misuse, proves docs and runtime-floor truth as first-class support facts, and only then widens toward longer-horizon support governance.

## Initial pilots
- one CLI application shipping Linux/macOS/Windows binaries with explicit release-artifact support diffs
- one mixed workspace containing host tools, Wasm crates, and firmware/custom-target crates
- one library that customizes docs.rs targets and wants the docs surface connected to the real support contract
- one Linux-first project that needs explicit glibc-floor evidence
- one project using `cargo-xwin` or `cargo-zigbuild` that wants provisioning truth kept separate from official support claims

Treat those as ranked pilot slots rather than as five obligations for one tool to solve simultaneously.

## Milestones
1. **v0 schemas + examples**
   - publish `support-envelope/v0`, `runtime-floor-report/v0`, `support-observation-report/v0`
   - include examples showing dev-host vs source-build vs artifact vs docs separation
2. **v0.2 adapters**
   - ingest docs.rs metadata, explicit target declarations, CI matrices, release manifests
   - attach simple runtime-floor evidence and raw attachments
3. **v0.3 provisioning integration**
   - adapters for `cross`, `cargo-zigbuild`, `cargo-xwin`, `build-std`, custom-target-json lanes
   - preserve backend choice as evidence, not as the support contract itself
4. **v0.4 diff + waiver workflows**
   - support release-to-release diffing, narrowed/widened support, raised floors, package changes, docs-target changes
5. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one deployment domain or one provisioning backend

## Success metrics
- teams can review support changes as explicit lane/runtime/docs diffs instead of scattered prose
- docs.rs target choices and CI matrices can be tied back to one declared support contract
- runtime-floor changes such as raised glibc or minimum-OS assumptions stop being hidden release hazards
- policy / trust / atlas tooling can consume support evidence without scraping READMEs
- users can get a better answer to “is this crate supported on my platform, in what sense, and with what confidence?”

## Archive fit
This proposal now fits the archive better as a **Tier 0/1 substrate** than as a side-thread.
The repo already has strong kits for:
- cross-toolchain provisioning,
- sysroot/std reuse,
- docs verification,
- release evidence,
- trust/policy,
- lifecycle metadata,
- and ecosystem navigation.

Support Envelope Kit is the missing contract that lets those kits talk about platform support without quietly redefining it.

## Archive fit refresh
This proposal should now be read not only as a platform-support kit, but as the platform/runtime half of a shared **compatibility-claims** frontier together with Acceptance Surface Kit. The strongest next execution move is a pilot program that proves released-artifact lanes, debugger-related support lanes, runtime floors, and support diffs can all be published without flattening them into one badge.

See also: `design/support-envelope-pilot-program.md` and `design/compatibility-claims-pilot-program.md`.
