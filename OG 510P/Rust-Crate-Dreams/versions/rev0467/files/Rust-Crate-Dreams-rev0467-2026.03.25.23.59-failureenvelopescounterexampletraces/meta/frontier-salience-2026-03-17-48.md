# Frontier salience snapshot — 2026-03-17 (48)

This pass did **not** promote a new lane.
It sharpened an existing high-value cross-cutting proposal:

- **P-0514 Crate Upgrade Pack Kit** — because the archive still lacked a good implementation-ready artifact for the moment after a crate is chosen and adopted but before an upgrade is trustworthy: *which release-to-release lane was actually checked, what automation really exists, and where a human still needs to read, edit, or validate behavior?*

## Main judgment

The next worthy move in this frontier was **not** another semver checker, another changelog generator, another release bot, or a universal codemod platform.
Those pieces already exist in partial form.

The sharper missing layer is the **upgrade contract** above them:

- explicit hazard classes,
- explicit fixup-capability receipts,
- explicit migration-lane manifests,
- explicit lane-fidelity reports,
- and explicit manual-review boundaries.

That move is now better grounded because:

- the Rust vision-doc work explicitly treats supportive interfaces from crates as part of Rust’s product experience,
- the 2025 State of Rust survey still says documentation and code are the main learning surfaces,
- Cargo’s semver guidance and the cargo-semver-checks goal make publish-path compatibility evidence more real,
- `cargo fix`, edition migration, rustc JSON diagnostics, and rustfix make machine-fix substrate concrete without solving the receiver-facing migration artifact,
- and release-plz / cargo-release make release automation more real without deciding what a downstream user should actually do.

So the gap is no longer “Rust has no release tooling”.
The gap is that maintainers still rarely publish a **reviewable hazard / fixup / checked-lane artifact** above that substrate.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0519 Crate Authority Surface Pack Kit** — still one of the most believable ambient-power review lanes.
5. **P-0451 Cfg Availability Ledger Kit** — still a highly leverageful way to make conditional API truth reviewable.
6. **P-0521 Crate Resource Surface Pack Kit** — still one of the best capacity/support contracts in the frontier.
7. **P-0516 Crate Configuration Scenario Pack Kit** — still one of the strongest setup-honesty lanes now that it has an implementation-ready shape.
8. **P-0514 Crate Upgrade Pack Kit** — now a much more believable `0.1` crate for release-to-release hazards, machine-fix boundaries, and checked migration-lane honesty.
9. **P-0517 Crate Performance Envelope Pack Kit** — still a strong workload/metric honesty lane.
10. **P-0084 Memory Observability Kit** — still a strong heap-evidence and regression-review lane.

## Why this won over adjacent candidates right now

- It beat **off-ramp / successor follow-ons** because many teams struggle before they ever decide to leave a crate: they still need one good path from the current release to the next one.
- It beat **generic fix-orchestration follow-ons** because many upgrade problems are not pure lint campaigns; they involve manifest edits, config shifts, behavior review, or partial workspace coverage.
- It beat **example-surface follow-ons** because examples help after the migration story already exists, but they do not by themselves classify hazards or prove a lane was checked.
- It beat several strong **domain workbenches** because upgrade pain cuts across servers, CLIs, embedded, SDKs, frameworks, and workspaces rather than one protocol family at a time.

## What changed in the archive

Added:
- `meta/crate-upgrade-pack-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-48.md`
- `entries/2026-03-17-228.md`
- `fixtures/crate-upgrade-pack-kit/hazard-class.policy.schema.json`
- `fixtures/crate-upgrade-pack-kit/fixup-capability.receipt.schema.json`
- `fixtures/crate-upgrade-pack-kit/lane-fidelity.report.schema.json`
- `fixtures/crate-upgrade-pack-kit/machine_fix_applies_but_manifest_feature_rename_remains/`
- `fixtures/crate-upgrade-pack-kit/semver_green_but_behavior_review_required/`
- `fixtures/crate-upgrade-pack-kit/workspace_recipe_checks_lib_lane_not_binary_lane/`

Updated:
- `proposals/crate-upgrade-pack-kit.md`
- `fixtures/crate-upgrade-pack-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- SemVer/public-API evidence,
- lint-fix orchestration,
- release automation,
- changelog generation,
- and receiver-facing upgrade contracts

into one fake “better release tooling” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- https://doc.rust-lang.org/beta/rustc/json.html
- https://docs.rs/rustfix/latest/rustfix/enum.Filter.html
- https://release-plz.dev/docs/usage/update
- https://crates.io/crates/cargo-release
