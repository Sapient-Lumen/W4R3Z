# Frontier salience snapshot — 2026-03-17 (49)

This pass did **not** promote a new lane.
It sharpened an existing high-value cross-cutting proposal:

- **P-0510 Crate Capability Contract & Interop Profile Kit** — because the archive still lacked a good implementation-ready artifact for the moment when a crate author wants to publish one machine-readable, reviewable support story rather than scattering it across `Cargo.toml`, docs.rs settings, API docs, and issue replies.

## Main judgment

The next worthy move in this frontier was **not** another registry feature, another ranking formula, another item-level cfg matrix, another whole-project support matrix, or another slice-specific analyzer.
Those pieces already exist in partial form.

The sharper missing layer is the **producer-side capability contract** above them:

- explicit claim classes,
- explicit support-obligation receipts,
- explicit interop export maps,
- explicit profile-fidelity reports,
- and explicit manual-review boundaries.

That move is now better grounded because:

- the Rust vision-doc work explicitly argues both that users need help navigating crates and that Rust needs smoother library interop,
- the 2025 State of Rust survey still says docs and code are the main learning surfaces,
- the Externally Implementable Items goal underscores that library customization points are becoming more public and documentable,
- Cargo/docs.rs already expose real substrate (`package.metadata`, `rust-version`, `build`, `links`, docs.rs metadata, rustdoc JSON, `cargo metadata`),
- and crates.io is surfacing more decision-relevant facts such as security advisories.

So the gap is no longer “Rust has no crate metadata”.
The gap is that maintainers still rarely publish a **joined, reviewable support / interop contract** above today’s substrate.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0519 Crate Authority Surface Pack Kit** — still one of the most believable ambient-power review lanes.
5. **P-0451 Cfg Availability Ledger Kit** — still a highly leverageful way to make conditional API truth reviewable.
6. **P-0510 Crate Capability Contract & Interop Profile Kit** — now a much more believable `0.1` crate for maintainer-published support profiles, hidden obligation receipts, and profile-fidelity honesty.
7. **P-0521 Crate Resource Surface Pack Kit** — still one of the best capacity/support contracts in the frontier.
8. **P-0516 Crate Configuration Scenario Pack Kit** — still one of the strongest setup-honesty lanes now that it has an implementation-ready shape.
9. **P-0514 Crate Upgrade Pack Kit** — still a strong release-to-release hazard and checked-lane honesty lane.
10. **P-0517 Crate Performance Envelope Pack Kit** — still a strong workload/metric honesty lane.

## Why this won over adjacent candidates right now

- It beat **shared interop profiles** because the archive still needed the more basic maintainer-published fact surface that those profiles would consume.
- It beat **example-surface follow-ons** because examples help teach a crate after the support story is honest, but they do not by themselves surface hidden obligations or claim-class drift.
- It beat **off-ramp / successor work** because many teams first need an honest statement of what the current crate already demands before they can sensibly decide whether to leave it.
- It beat more **domain-specific workbenches** because capability contracts cut across async, CLI, embedded, Wasm, GUI, data, SDK, and native-linkage-heavy crates.

## What changed in the archive

Added:
- `meta/crate-capability-contract-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-49.md`
- `entries/2026-03-17-229.md`
- `fixtures/crate-capability-contract-kit/claim-class.policy.schema.json`
- `fixtures/crate-capability-contract-kit/support-obligation.receipt.schema.json`
- `fixtures/crate-capability-contract-kit/profile-fidelity.report.schema.json`
- `fixtures/crate-capability-contract-kit/tokio_internal_runtime_neutral_public_api/`
- `fixtures/crate-capability-contract-kit/no_std_alloc_with_docsrs_target_overlay/`
- `fixtures/crate-capability-contract-kit/build_rs_links_proc_macro_hidden_obligations/`

Updated:
- `proposals/crate-capability-contract-kit.md`
- `fixtures/crate-capability-contract-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- task-first crate selection,
- producer-side support contracts,
- shared ecosystem interop profiles,
- item-level availability matrices,
- whole-project support matrices,
- and slice tools such as MSRV/API/security analyzers

into one fake “better crate metadata” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://doc.rust-lang.org/cargo/reference/rust-version.html
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
