# Frontier salience snapshot — 2026-03-18 (68)

This pass did **not** promote a brand-new ecosystem-wide lane.
It sharpened another **shipping and adoption accelerator**:

- **P-0501 RubyGems Native Extension ShipKit** — because the archive still lacked a believable answer to “what exact Rust-backed gem support promise is this release making, and how can another maintainer review it without replaying gemspecs, lockfiles, CI, and local install folklore by hand?”

## Main judgment

The next worthy move here was **not** another Rust↔Ruby binding layer, another project skeleton, another CI release action, or another generic Ruby publishing helper.
Those either already exist in real form or are too broad for a believable artifact-bearing `0.1`.

The sharper missing layer is the **Ruby native shipping contract** above today’s substrate, especially once three more facts are kept explicit:

- **platform coverage** — which binary gems actually exist, which platforms still fall back to source builds, and where “fat gem” claims exceed the matrix;
- **resolver route** — whether Bundler engine/platform controls, lockfile platform targets, and source-build fallbacks actually route users where the README suggests;
- **extension residency** — whether gemspec platform, packaged extension filenames, copied `lib/` artifacts, require stubs, and runtime load locations still agree.

That move is better grounded now because:

- Bundler now officially scaffolds Rust extensions with `bundle gem --ext=rust`;
- RubyGems still documents platform gems, install-time extension builds, and `require_paths` behavior for copied extension files;
- Bundler’s current docs now state explicitly that Gemfile `platforms:` are implementation-like while `bundle lock --add-platform` uses OS/arch-oriented targets;
- Bundler’s cache docs make multi-platform caching and platform-specific remote fetch behavior explicit;
- RubyGems now documents trusted publishing with short-lived tokens;
- RubyGems also has a first-party `gem rebuild` command;
- and `rb-sys`, `magnus`, and oxidize.rb deployment docs make the authoring / fat-gem substrate obviously real.

So the gap is no longer “Rust cannot ship Ruby native gems.”
The gap is that teams still rarely get a **reviewable cargo-native Ruby bundle** above platform coverage, resolver-route truth, and extension-residency honesty.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest troubleshooting lanes.
5. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
8. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library shipping-kit lane with explicit policy pressure.
9. **P-0206 Wasm Component Contract & Conformance ShipKit** — still one of the clearest Wasm shipping-contract opportunities.
10. **P-0467 Apple XCFramework & SwiftPM ShipKit** — still one of the clearest Apple-SDK shipping-contract opportunities.
11. **P-0499 NuGet Native Interop ShipKit** — still one of the clearest .NET shipping-contract opportunities.
12. **P-0498 Node-API Package & Prebuild Contract Kit** — still one of the clearest npm-facing ship-contract opportunities.
13. **P-0502 Hex Native NIF ShipKit** — still one of the clearest BEAM-facing ship-contract opportunities.
14. **P-0500 JAR/JNI Native ShipKit** — still one of the clearest JVM-facing ship-contract opportunities.
15. **P-0526 R Package Native ShipKit** — now one of the clearest R/CRAN-facing ship-contract opportunities.
16. **P-0501 RubyGems Native Extension ShipKit** — now one of the clearest Ruby/RubyGems-facing ship-contract opportunities because the substrate exists but the boring contract above platform coverage, resolver routes, and extension residency still does not.

## Why this won over adjacent candidates right now

- It beat **cross-ecosystem support-contract generalization** because one more concrete language/package ecosystem still buys clearer vocabulary than an early abstraction pass.
- It beat **another Bundler/Ruby authoring helper** because authoring substrate already exists; the sharper pain is release-contract truth above it.
- It beat **generic gem publishing automation** because platform coverage, resolution routes, and extension residency are the more immediate downstream support bottlenecks.
- It beat **another build helper** because the key missing value is not producing artifacts but explaining what support promise those artifacts actually make.

## What changed in the archive

Added:
- `entries/2026-03-18-248.md`
- `meta/frontier-salience-2026-03-18-68.md`
- `meta/rubygems-native-extension-shipkit-product-plan-2026-03-18.md`
- `fixtures/rubygem-native-shipkit/platform-coverage.report.schema.json`
- `fixtures/rubygem-native-shipkit/resolver-route.report.schema.json`
- `fixtures/rubygem-native-shipkit/extension-residency.report.schema.json`
- `fixtures/rubygem-native-shipkit/scenarios/fat_gem_claim_hides_missing_linux_aarch64_binary/`
- `fixtures/rubygem-native-shipkit/scenarios/jruby_route_missing_from_lockfile_and_bundle_cache_story/`
- `fixtures/rubygem-native-shipkit/scenarios/extension_copied_under_old_name_after_rename/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/rubygems-native-extension-shipkit.md`
- `fixtures/rubygem-native-shipkit/README.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/prioritization.md`

## What this pass deliberately did not do

It did **not** collapse:

- gemspec platform,
- Bundler Gemfile `platforms:`,
- lockfile `add-platform` targets,
- copied extension files under `lib/`,
- trusted-publishing posture,
- and one successful local install

into one fake “Ruby support” story.
