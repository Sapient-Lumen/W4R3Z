# Renewal receipt: conservative installable CLI product (2026-03-22)

## Subject
- default card: `defaults/conservative-installable-cli-product-2026Q1.md`
- review date: 2026-03-22
- archive revision: rev0382
- scope: public or semi-public Rust CLI applications whose release/distribution route matters as much as their internal crate ergonomics
- non-goal: blessing this as the default for internal tools, GUI apps, or every platform-package-manager workflow

## Renewal verdict
**add as new card**

The defaults corpus needed a public-binary card because it had become stronger for internal tools and libraries than for one of Rust’s most visible success lanes.
The correct lane-level answer for this scope is now:

- `cargo-dist` as the default release/distribution layer,
- explicit supported install routes,
- `cargo install --locked` as the documented source fallback,
- optional `cargo-binstall` support as a separate maintained route,
- and explicit route-specific ownership/update posture instead of a hidden updater by default.

## Canon import checked this round
Primary surfaces re-read:
- Cargo install:
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- Cargo uninstall:
  https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html
- Cargo package:
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- cargo-dist book:
  https://axodotdev.github.io/cargo-dist/book/
- cargo-dist supply-chain security:
  https://axodotdev.github.io/cargo-dist/book/supplychain-security/index.html
- cargo-binstall overview:
  https://github.com/cargo-bins/cargo-binstall
- cargo-binstall support metadata:
  https://github.com/cargo-bins/cargo-binstall/blob/main/SUPPORT.md
- cargo-binstall signing:
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md

Canon judgment:
- Cargo’s own install/package/uninstall docs already expose enough consumer-lifecycle truth that a maintained public-binary lane is now justified;
- `cargo-dist` is currently the clearest reusable release/distribution companion for this scope because it separates plan/build/host/publish/announce and emits machine-readable manifests;
- `cargo-binstall` is real enough to name, but it should remain an optional route layer rather than the core of the default card.

## Registry / supply-chain import
Public ecosystem signals checked:
- Rust challenges post:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- What people love about Rust:
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

Imported judgments:
- Rust is still explicitly strong for CLI tools, which means the missing contribution here is less “invent CLI support” and more “turn a successful lane into a reviewable default”;
- crates.io’s stronger review surfaces — Security tab, Trusted Publishing improvements, SLOC, `pubtime`, and Browse source links — make release/distribution review more practical than it used to be;
- this receipt is still a **lane judgment**, not a package-admission or product-security signoff for any one binary.

## Route / lifecycle import
Relevant lifecycle signals checked:
- Cargo 1.86 development-cycle note:
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- `design/consumer-lifecycle-continuity-bundle.md`
- `design/distribution-contract-stack.md`
- `design/distribution-route-mobility-stack.md`

Imported judgments:
- installed-binary update continuity still sits partly in plugin/adjacent-tool territory, so the conservative default should not pretend lifecycle unification already exists;
- because `cargo uninstall` only covers `cargo install`-managed packages, uninstall truth remains route-specific;
- the correct default posture is therefore explicit route support plus explicit update/uninstall docs, not a stealth universal updater.

## Maintenance / support-envelope import
Support-envelope facts that still hold:
- this lane is strongest when a team needs a boring installable product surface, not only a good crate-internal CLI architecture;
- the card is intentionally conservative about update claims because support burden grows faster than release-tool enthusiasm;
- route multiplication should be treated as real maintenance load, not free ecosystem reach.

Maintenance judgment:
- the lane deserves a maintained default card because it connects one of Rust’s strongest public domains to reviewable lifecycle/route discipline;
- the card should remain `default-with-caveats` until the lifecycle side becomes more unified and machine-receiptable.

## Freshness / replay notes
Fresh inputs checked on 2026-03-22:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://doc.rust-lang.org/cargo/commands/cargo-install.html
- https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://axodotdev.github.io/cargo-dist/book/
- https://axodotdev.github.io/cargo-dist/book/supplychain-security/index.html
- https://github.com/cargo-bins/cargo-binstall
- https://github.com/cargo-bins/cargo-binstall/blob/main/SUPPORT.md
- https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md
- https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/

Replay notes:
- renew this receipt when Cargo’s install/update/uninstall story changes materially;
- renew when `cargo-dist` changes enough to alter the conservative default route set;
- renew when `cargo-binstall` support/signing expectations shift enough to promote or demote it in the card;
- renew sooner if the archive gains a more concrete machine-readable lifecycle receipt family for public binaries.

## Lane judgment
Add the card as a maintained public default.

Why:
- it fills the biggest remaining public-binary gap in the current defaults corpus;
- it grounds older archive work on consumer lifecycle and distribution in a real recurring project class;
- and it does so without pretending there is already one universal installer or updater.

## Open watch items
- whether this lane should later split into **developer-distributed CLI** versus **mass-consumer installable CLI**;
- whether `cargo-binstall` support should remain a serious optional route or become stronger in the default;
- whether future lifecycle receipts should turn route/ownership/update posture into a more portable machine-readable bundle.
