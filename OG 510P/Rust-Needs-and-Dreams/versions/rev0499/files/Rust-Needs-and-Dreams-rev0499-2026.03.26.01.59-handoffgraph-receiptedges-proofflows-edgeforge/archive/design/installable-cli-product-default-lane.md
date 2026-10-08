# Design: Installable CLI product default lane

## Thesis
The defaults corpus now covers:
- internal CLI work,
- conservative HTTP/services,
- single-file script/repro utilities,
- publishable libraries,
- and polyglot components.

What it still under-served was the lane Rust is already publicly famous for:
**installable CLI products that need to reach real users across release, route, ownership, and update boundaries.**

That is not the same thing as the existing internal CLI card.
A public installable CLI needs a default lane that is less about parser choice and more about:
- release/build orchestration,
- install route clarity,
- source-fallback truth,
- ownership/update posture,
- and supply-chain receipts.

In other words:
what is missing is not “another nice CLI crate set”.
It is a **reviewable boring-default lane for Rust binaries that are meant to be installed and supported by people outside one repo**.

Read with:
- `design/consumer-lifecycle-continuity-bundle.md`
- `design/distribution-contract-stack.md`
- `design/distribution-route-mobility-stack.md`
- `design/reviewable-lane-defaults-corpus.md`
- `defaults/conservative-installable-cli-product-2026Q1.md`
- `evidence/conservative-installable-cli-product-2026Q1-renewal-2026-03-22.md`

## Why this now
Several current Rust signals converge hard on this seam.

1. Rust’s March 20, 2026 challenges post still says the ecosystem is excellent for **CLI tools and web backends**, while navigation still suffers from **choice paralysis** and **tacit knowledge**.
   https://blog.rust-lang.org/2026/03/20/rust-challenges/

2. Rust’s December 2025 vision work says users still need help getting oriented in crates.io and finding a good “starter set” of crates and workflows.
   https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/

3. Cargo’s own docs already make the consumer-side contract explicit in pieces: `cargo install` has route/root precedence, ignores packaged lockfiles unless `--locked` is used, and ignores project-local config discovery for non-`--path` installs.
   https://doc.rust-lang.org/cargo/commands/cargo-install.html

4. `cargo uninstall` only understands packages installed with `cargo install`, which means ownership and uninstall truth are route-specific rather than universal.
   https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html

5. `cargo package` now clearly states that `Cargo.lock` is always included by default, that `--exclude-lockfile` is not for general use, and that packaging emits `.cargo_vcs_info.json` plus a pristine-state rebuild. That gives product lanes a stronger source-package contract than many teams still assume.
   https://doc.rust-lang.org/cargo/commands/cargo-package.html

6. `cargo-dist` has matured into an unusually coherent release/distribution companion: it plans, builds, hosts, publishes, and announces releases; generates installers and machine-readable manifests; and has first-class supply-chain hooks for signing, SBOMs, attestations, and auditable binaries.
   https://axodotdev.github.io/cargo-dist/book/
   https://axodotdev.github.io/cargo-dist/book/supplychain-security/index.html

7. `cargo-binstall` now provides a low-complexity prebuilt-binary installation path that can use repository releases, manifest metadata, and optional signature verification, while falling back to `cargo install` as a last resort.
   https://github.com/cargo-bins/cargo-binstall
   https://github.com/cargo-bins/cargo-binstall/blob/main/SUPPORT.md
   https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md

Taken together, the next worthy corpus move is not another application framework card first.
It is an **installable CLI product lane**.

## The missing problem
Rust teams can usually build excellent CLIs.
What they still lack is a boring shared answer to:
- how should a public CLI be released so prebuilt binaries, source installs, and uninstall/update expectations stay explicit?
- when should `cargo install --locked` be documented as the source fallback instead of treated as an afterthought?
- when is `cargo-dist` the right default release layer, and when is it too much?
- when should `cargo-binstall` metadata/signing be treated as worth the maintenance cost?
- what should be considered the default ownership/update posture when consumer lifecycle remains route-specific?

Existing advice is usually split across:
- Cargo install/uninstall docs,
- release-tool docs,
- package-manager folklore,
- and maintainers’ README snippets.

The defaults corpus can do something better:
**one reviewable lane card plus one readable receipt**.

## What the default lane should optimize for
This lane is for binaries that value:
- boring user acquisition,
- cross-platform prebuilt releases where practical,
- explicit fallback/source routes,
- and supportable update/uninstall expectations.

It should optimize for:
- a release layer that emits machine-readable artifacts and receipts;
- clear supported install routes;
- an explicit source fallback;
- minimum viable supply-chain evidence;
- and visible route/ownership caveats instead of pretending all installs behave the same.

It should not optimize for:
- maximum packaging reach on day one,
- bundling every installer and updater format by default,
- or hiding route differences behind a magical one-click story.

## Proposed lane shape
The lane should keep six truths separate.

### 1. Release/build truth
The lane should prefer a release layer that can:
- plan a release,
- build binaries and installers,
- publish/host artifacts,
- and emit a machine-readable manifest.

Today the strongest reusable answer here is `cargo-dist`.
Its value is not just “it makes installers”, but that it keeps **plan/build/host/publish/announce** explicit and replayable.

Canon:
- https://axodotdev.github.io/cargo-dist/book/

### 2. Install-route truth
A public CLI should name its supported routes explicitly.
For many Rust apps the conservative route set is:
- prebuilt installer/script routes for ordinary users,
- plus an explicit `cargo install --locked` source route for Rust users.

The point is not to maximize route count.
The point is to avoid pretending `curl | sh`, Homebrew, `cargo install`, and a package-manager formula are the same ownership story.

Canon:
- https://doc.rust-lang.org/cargo/commands/cargo-install.html
- https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html

### 3. Source-fallback truth
When a product is on crates.io, the lane should treat source installation as a real fallback, not a hidden backup.
That means:
- document `cargo install --locked` when lockfile reproducibility matters;
- do not make source builds guess at route-specific behavior;
- keep local config-discovery caveats visible because install behavior differs from normal project builds.

Canon:
- https://doc.rust-lang.org/cargo/commands/cargo-install.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html

### 4. Fast-path / cargo-native prebuilt truth
If the product wants a Cargo-native prebuilt path, the lane should treat `cargo-binstall` support as a distinct, optional layer:
- explicit metadata,
- exact artifact naming/layout,
- optional signing,
- and fallback semantics.

This should be treated as a real route with its own maintenance cost, not free magic.

Canon:
- https://github.com/cargo-bins/cargo-binstall
- https://github.com/cargo-bins/cargo-binstall/blob/main/SUPPORT.md
- https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md

### 5. Supply-chain truth
The default lane should normalize:
- checksums at minimum,
- optional SBOM and auditable-binary support when warranted,
- optional attestation/signing hooks when the support envelope calls for them.

Canon:
- https://axodotdev.github.io/cargo-dist/book/supplychain-security/index.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

### 6. Ownership/update truth
The lane should be explicit that update/uninstall posture is route-specific.
A public CLI should not ship a hidden self-updater by default just because lifecycle continuity is still fragmented.
The default should be:
- publish clear route-specific update instructions,
- publish clear ownership scope,
- and only add a stronger updater lane when the product genuinely needs it.

Canon:
- https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html
- https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- `design/consumer-lifecycle-continuity-bundle.md`

## A thin companion-tool shape
If this became a tool contribution, the right shape would be thin:
- `cargo product-dist`
- or `installable-cli-pack/v0`

It should do boring import-and-check work:
- inspect package/install route declarations;
- collect release artifacts and checksums;
- normalize a dist-style manifest when available;
- record source-fallback posture;
- record binstall metadata/signing posture when present;
- and emit a readable route/ownership receipt.

It should **not** become:
- a universal installer,
- a hidden updater,
- a package-manager replacement,
- or a hosted release portal pretending to be ecosystem infrastructure.

## MVP for this archive
The archive does not need the tool first.
The MVP is:
1. a design note for the lane;
2. a default card;
3. a first receipt;
4. frontier updates so later revisions renew it rather than forget it.

## Why this is worthy
This would be a worthy Rust ecosystem contribution because it would:
- sharpen one of Rust’s strongest public domains instead of only admiring it;
- connect Cargo’s install/package semantics to actual release/distribution practice;
- reduce route confusion without blessing one universal installer;
- and create a real bridge between the defaults corpus and older archive work on **Consumer Lifecycle**, **Distribution Contract**, and **Distribution-Route Mobility**.

It also learns the right lesson from the present moment:
ideal Rust does not just need more install routes.
It needs more **reviewable route and ownership defaults** around the binaries people already want to ship.

## Non-goals
- choosing a universal package manager for every platform;
- declaring `cargo-dist` the answer for every binary release shape;
- forcing `cargo-binstall` support into every CLI project;
- pretending one card replaces package-admission or security review;
- or saying this lane matters more than the archive’s long-running Build-State Evidence frontier.
