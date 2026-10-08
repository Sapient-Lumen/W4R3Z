---
id: P-0515
title: Crate Off-Ramp Pack Kit — successor maps, sunset receipts, and checked exit recipes for library authors
status: idea
domains: [crates, deprecation, migration, maintenance, rustsec, cargo, docs, supportiveness]
last_reviewed: 2026-03-23
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://blog.rust-lang.org/2026/03/20/rust-challenges/
  - https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
  - https://doc.rust-lang.org/rustc/lints/listing/warn-by-default.html#deprecated
  - https://doc.rust-lang.org/cargo/reference/semver.html
  - https://doc.rust-lang.org/cargo/commands/cargo-yank.html
  - https://doc.rust-lang.org/cargo/commands/cargo-update.html
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
  - https://docs.rs/crate/cargo-audit/latest
  - https://docs.rs/crate/cargo-deny/latest
  - https://docs.rs/crate/cargo-outdated/latest
  - https://rust-lang.github.io/rfcs/3416-feature-metadata.html
  - https://docs.rs/crate/sello-crypto/latest
---

# Problem

The archive now has much better answers for:

- **which crate to choose**,
- **what a crate claims to support**,
- **which shared interop profile it fits**,
- **what guidance it gives before failure**,
- **what it hands off after runtime failure**,
- and **how a downstream user should upgrade between releases**.

But there is still a conspicuous hole in the crate-supportiveness frontier:

- what a crate hands other people when it wants them to **stop depending on it**.

That hole matters because current Rust substrate already covers only fragments of the story:

1. Rust lets library authors mark items as `#[deprecated]`, and the official lint docs say that deprecations should usually include a note on what to use instead.
2. Cargo’s SemVer guidance explicitly treats newly introduced deprecations as a possible update hazard and even suggests feature-gating deprecations before a later removal.
3. Cargo can **yank** bad versions, but yanking only removes a version from new resolution; it does not delete the crate and it does not tell downstream users what successor path to take.
4. `cargo update` explicitly tells users to try a non-yanked version or seek help from maintainers when a yanked version is involved.
5. crates.io now exposes a Security tab with affected version ranges from RustSec, and the crates.io team says RustSec advisories remain the always-on communication path for removed malware crates.
6. Tools like `cargo-audit`, `cargo-deny`, and `cargo-outdated` can tell users that a problem exists or that a newer version exists, but not the crate-authored **exit contract** for leaving a crate.
7. Real crates sometimes write bespoke migration notes for renames or successors on docs.rs, but those are ad hoc and not reusable by tools.

The missing crate is therefore **not** another advisory client, **not** another outdated-version checker, and **not** just a prettier deprecation message.
It is a **Crate Off-Ramp Pack Kit**.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **Is this crate asking people to leave entirely, or only to leave a specific API/feature/version lane?**
2. **What successor crate, fork, façade, or maintained lane should people move to?**
3. **Which parts of the current crate have a direct replacement, and which require manual redesign?**
4. **Which exit recipes were actually checked, under which feature/target/runtime combinations?**
5. **What advisory, yank, or deprecation facts shaped this off-ramp recommendation?**
6. **How did the crate’s off-ramp surface change across releases?**

That is more valuable than another changelog paragraph or README warning block.

# What it provides

- `offramp-pack.toml` — versioned declaration of crate-level and item/feature-level off-ramp lanes, successor targets, sunset phases, checked matrices, recipe refs, and manual-review zones.
- `successor-map.report.json` — machine-readable map from deprecated crate/items/features to successor crate/items/features, including `compatible_shim`, `partial_replacement`, `fork_successor`, `security_only_last_safe_version`, and `no_successor` classes.
- `deprecation-surface.receipt.json` — observed receiver-facing off-ramp facts imported from `#[deprecated]` surfaces, docs anchors, feature metadata, yanked-version state, advisory references, and crate-authored notes.
- `offramp-recipe.manifest.json` — smallest before/after recipes for common leave-the-crate lanes such as crate rename, successor swap, last-safe pin, or manual containment.
- `successor-compat.report.json` — verifies whether advertised replacements actually satisfy the stated feature/target/runtime/profile lane and classifies `drop_in`, `adapter_needed`, `behavior_review_required`, `security_only_stopgap`, and `unsupported_exit_lane`.
- `sunset-check.report.json` — checks that off-ramp claims, docs links, successor versions, and recipe fixtures still resolve and remain coherent.
- `successor-authority.receipt.json` — records whether a successor/exit claim came from a crate-authored pack, rustdoc deprecation note, docs page, advisory stopgap, yank pressure, or third-party inference.
- `stopgap-horizon.report.json` — classifies whether a shim, last-safe pin, or migrate-now path is temporary, review-due, deadline-known, deadline-unknown, or still waiting on successor maturity.
- `recipe-witness.report.json` — records what exit recipe actually ran, under which feature/target/runtime axes, and where behavior or matrix review remains open.
- `offramp-support-bundle.manifest.json` — portable inventory that keeps successor class, authority basis, stopgap horizon, declared recipes, and witnessed recipe scope separate.
- `offramp-diff.report.json` — compares two off-ramp packs and classifies `successor_changed`, `sunset_phase_changed`, `recipe_changed`, `replacement_regressed`, `replacement_improved`, and `manual_review_boundary_changed`.
- `sunset-notes.summary.md` — compact human-facing explanation derived from the structured artifacts.
- `cargo off-ramp capture` — capture one crate’s off-ramp bundle from manifests, docs, advisories, and fixtures.
- `cargo off-ramp check` — verify the selected exit recipes and successor paths.
- `cargo off-ramp diff <old> <new>` — compare off-ramp surfaces across releases.
- `cargo off-ramp summary` — render a reviewable human summary from structured artifacts.

# What the crate should provide other people

1. **A crate-authored exit contract** above ad hoc README prose and below whole-product migration programs.
2. **A joined successor map** that tells users where to go, not just that something is deprecated.
3. **Off-ramp honesty** about `drop_in`, `adapter_needed`, `manual_review_required`, and `no_successor` cases.
4. **Checked exit recipes** for common situations like crate renames, security off-ramps, split successor crates, or temporary pins to a last safe version.
5. **A sunset-phase artifact** that tools and docs can import instead of scraping prose.
6. **A diffable off-ramp surface** so maintainers can review whether leaving the crate became clearer or more hazardous over time.
7. **A reusable import layer** for pathfinders, docs portals, support bots, advisory dashboards, and org-level dependency policies.

# Three first-class review objects

## 1) Successor intent map

The crate should publish one artifact that answers, without prose archaeology:

- what is being sunset,
- whether the successor is a `drop_in_successor`, `compatible_shim`, `partial_replacement`, `fork_successor`, `security_only_last_safe_version`, or `no_successor`,
- which lanes are truly covered,
- and where manual review starts.

This should become `successor-map.report.json`.

## 2) Stopgap-horizon receipt

The crate should make temporary answers visible instead of letting them masquerade as permanent replacements.
It should record:

- imported deprecation/advisory/yank facts,
- whether a shim or last-safe version is only transitional,
- what sunset phase is in force,
- and whether a deadline or successor maturity boundary is still unknown.

This should be represented by `deprecation-surface.receipt.json` plus `sunset-check.report.json`.

## 3) Exit recipe witness

The strongest successor claim is a small checked migration path.
The crate should record:

- the exact dependency rename or version pin,
- any import-path rewrite or feature remap,
- which target/feature/runtime matrix was exercised,
- and whether the result was `drop_in`, `adapter_needed`, `behavior_review_required`, or only a temporary stopgap.

This should become `offramp-recipe.manifest.json` plus `successor-compat.report.json`.

# Persona / who it’s for

- maintainers retiring, renaming, splitting, or superseding a library crate
- framework teams moving users to a successor crate or new major line
- security teams handling last-safe-version / migrate-now situations
- downstream teams who need a checked exit path rather than folklore
- tooling authors building advisory, docs, or dependency-governance workflows

# Users & user stories

- **Maintainer**: “We renamed the crate and kept a compatibility shim. Publish one off-ramp bundle so users and tools know the real successor path.”
- **Security engineer**: “Tell downstream teams whether they should pin the last safe version temporarily, jump to a successor crate, or remove the dependency entirely.”
- **Downstream adopter**: “Give me one compact exit pack with replacement choices, recipes, and explicit manual-review boundaries.”
- **Release/support reviewer**: “See whether the crate’s sunset story became clearer, riskier, or more fragmented.”
- **Tool author**: “Import a stable successor/off-ramp artifact instead of scraping blog posts, docs pages, and advisory text.”

# Prior art (and why it’s insufficient)

- `#[deprecated]`, rustdoc, and the warning machinery are the best current substrate for saying **this item should not be used**.
- Cargo’s yank flow and `cargo update` handle resolution pressure, but not successor planning.
- crates.io Security tabs, RustSec, `cargo-audit`, and `cargo-deny` identify risky crates or versions.
- `cargo-outdated` and similar tools detect newer versions.
- Some crates publish bespoke rename/migration notes on docs.rs.

What remains missing is the joined, receiver-facing artifact that says:

- whether the off-ramp is about an item, feature, whole crate, or version range,
- which successor path is recommended,
- which exit lanes were actually checked,
- whether an adapter or manual redesign is required,
- and where the maintainer still needs the user to decide.

That is a different lane from:

- **P-0011** crate health metadata,
- **P-0509** task-first crate choice,
- **P-0512** compile-time guidance packs,
- **P-0513** runtime handoff packs,
- **P-0514** release-to-release upgrade packs,
- advisory clients,
- or publish/yank tooling.

# Design goals

1. **Receiver-facing first** — optimize for downstream exit clarity, not maintainer virtue signaling.
2. **Join, don’t replace** — import deprecation, yank, advisory, and docs substrate where possible.
3. **Successor honesty** — permit `no_successor` and `manual_review_required` as first-class answers.
4. **Scope honesty** — preserve whether the off-ramp is item-level, feature-level, version-lane, or whole-crate.
5. **Recipe-backed** — the best successor claim is a small passing replacement recipe, not a prose suggestion.
6. **Sunset narrowness** — stay focused on one crate’s exit story, not ecosystem-wide maintenance scoring.
7. **Diffability** — support review of how the off-ramp surface changes over time.

# MVP surface

- Minimal types: `OffRampPack`, `SuccessorMapReport`, `DeprecationSurfaceReceipt`, `OffRampRecipeManifest`, `SuccessorCompatReport`, `SunsetCheckReport`, `OffRampDiffReport`, `SunsetNotesSummary`
- Minimal functions:
  - `load_offramp_pack()`
  - `import_deprecation_and_advisory_facts()`
  - `capture_deprecation_surface()`
  - `validate_offramp_recipes()`
  - `check_successor_paths()`
  - `diff_offramp_bundles()`
  - `render_sunset_summary()`
- Feature flags:
  - `serde`
  - `cargo`
  - `rustsec-import`
  - `docs-links`
  - `markdown`

# Compatibility story

- Should work in a stable-first mode by importing deprecation/advisory/yank facts available from manifests, docs, lockfiles, and registry metadata.
- Must preserve which off-ramp facts were **imported**, which were **observed**, and which were **maintainer-authored**.
- Should remain useful whether the change is a crate rename, successor split, security emergency, or slow retirement.
- Must remain honest when there is only a temporary stopgap and no good long-term replacement.
- Should be importable by pathfinder-style tools without pretending the successor is universally best for every task.

# 0.1 off-ramp families

1. `crate_rename_shim`
   - records renamed-crate successor, compatible shim status, and minimal rename recipe
   - supports direct import of docs.rs migration notes when present
2. `security_offramp`
   - records advisory refs, affected ranges, and whether the best immediate action is pin-last-safe, upgrade, or remove
   - keeps temporary stopgaps distinct from real successors
3. `successor_split_or_fork`
   - records one-to-many or fork-based successor paths
   - explicitly marks when an adapter or manual redesign is needed
4. `feature_or_api_sunset`
   - tracks feature/item deprecation lanes that imply a future crate-level or version-lane exit
   - keeps item-level deprecation distinct from whole-crate retirement
5. `no_successor_manual_containment`
   - reserved for cases where the honest answer is containment, vendoring, or replacement by local redesign

# Conformance & fixtures

- one renamed-crate shim fixture with a checked dependency and import rename
- one security off-ramp fixture with `last_safe_version` versus `migrate_now` lanes
- one successor-split fixture where only part of the old API is covered directly
- one no-successor fixture that deliberately stays `manual_review_required`
- goldens for `successor_present`, `drop_in`, `adapter_needed`, `security_only_stopgap`, `no_successor`, and `manual_review_required`

# Path to boring stability

- Stabilize the pack/check/diff schemas before adding registry or editor integrations.
- Start with import + recipe verification rather than trying to solve crate-transfer governance.
- Keep the first sunset vocabulary small and sharp.
- Treat “no successor” and “temporary stopgap only” as honest output, not failure.
- Add deeper advisory/registry adapters only after maintainers trust the artifact vocabulary.

# Why this could matter

This is the crate that would let maintainers say:

- “Yes, we are asking you to leave this crate.”
- “Here is the successor, or the honest reason there is none.”
- “Here is the smallest checked replacement recipe.”
- “Here is whether you can swap directly, need an adapter, or must review behavior manually.”
- “Here are the advisory/yank/deprecation facts that shaped this recommendation.”

That is the boring supportiveness layer missing between “a warning exists” and “good luck finding a replacement.”

# Why now

1. The official Rust vision work now names supportive crate interfaces directly.
2. The survey still says docs and code are the main learning surfaces, so off-ramp support should not be left to scattered prose.
3. crates.io now exposes richer security/advisory surface area while Cargo continues to distinguish yanks from deletion.
4. Cargo’s SemVer docs already treat deprecation as part of the update experience, which makes successor planning more valuable.
5. The ecosystem has real detection tools for risky/outdated crates but still lacks a stable maintainer-authored exit artifact.

# Sharp edges / open questions

- How should off-ramp packs represent one-to-many successors without pretending the choice is objective for every task?
- How should “last safe version” stopgaps expire or diff over time?
- What is the smallest compatibility vocabulary that still distinguishes `drop_in` from `adapter_needed` and `behavior_review_required`?
- How should a crate express “we are deprecated, but the successor is not yet mature enough for every lane”?
- Which off-ramp notes should remain local docs anchors versus copied into exported summaries?

# Suggested 0.1 deliverable

A crate and cargo subcommand that load one `offramp-pack.toml`, import deprecation/advisory/yank facts, validate a few before/after successor recipes, and emit:

- one `successor-map.report.json`,
- one `deprecation-surface.receipt.json`,
- one `offramp-recipe.manifest.json`,
- one `successor-compat.report.json`,
- one `sunset-check.report.json`,
- one `offramp-diff.report.json`,
- and one short `sunset-notes.summary.md`.

That would already be enough to prove the lane is real.

# Adoption plan

## 0.1
- schema + recipe verification
- deprecation/advisory/yank fact import
- compact summary generation
- docs.rs-friendly successor links

## 0.2
- adapter-needed compatibility checks
- last-safe-version stopgap vocabulary
- pathfinder import support
- org-policy hooks for sunset review

## 0.3
- richer one-to-many successor planning
- ecosystem policy adapters
- better docs-site / support-bot rendering
- cross-release off-ramp regression review


# Sharper reading after the latest 2026 signals

The March 2026 challenges write-up says ecosystem navigation and tacit knowledge are still live friction, which means crate sunset stories that depend on “just read the warning and infer the rest” are still too folkloric.
The January 2026 crates.io update adds richer receiver-visible substrate such as the Security tab, Trusted Publishing enhancements, and SLOC, but that still does not create a stable successor contract by itself.
The Rust Reference and rustc lint docs make deprecation notes more explicit than before — rustdoc shows `since` and `note`, and deprecations should usually say what to use instead — while Cargo’s SemVer guide now explicitly discusses staging deprecations and even suggests gating them behind a feature for major-version preparation.
Cargo’s yank docs remain equally clear that yanking affects new resolution without deleting the crate or telling downstream users what the real long-term exit path is.

That combination makes **P-0515** sharper as an **authority + horizon + witness** lane:
- **authority** — who actually authored the successor claim,
- **horizon** — whether the answer is permanent or only a stopgap,
- **witness** — what migration path really ran and what lanes remain open.

## Four review objects that should now be first-class

1. `successor-map.report.json` — what successor class is being claimed.
2. `successor-authority.receipt.json` — who or what made that claim visible.
3. `stopgap-horizon.report.json` — whether the current answer expires or requires reevaluation.
4. `recipe-witness.report.json` — what migration path actually ran and what scope it covered.

Treat `meta/crate-offramp-frontier-2026-03-23.md`, `meta/crate-offramp-authority-horizon-plan-2026-03-23.md`, and `meta/crate-offramp-claim-boundaries-2026-03-23.md` as the working refinement notes for this pass.
