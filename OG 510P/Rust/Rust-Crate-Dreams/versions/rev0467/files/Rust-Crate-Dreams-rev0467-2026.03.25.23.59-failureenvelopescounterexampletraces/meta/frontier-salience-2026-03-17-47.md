# Frontier salience snapshot — 2026-03-17 (47)

This pass did **not** promote a new lane.
It sharpened an existing high-value cross-cutting proposal:

- **P-0516 Crate Configuration Scenario Pack Kit** — because the archive still lacked a good implementation-ready artifact for the ordinary maintainer question that sits between “the crate has features and docs” and “a downstream user can actually succeed quickly”: *which setup lane is the honest default, which alternatives are real, and how much of that matrix was actually checked?*

## Main judgment

The next worthy move in this frontier was **not** another feature-doc renderer, another powerset executor, another generic Cargo config explainer, or another docs portal.
Those pieces already exist in partial form.

The sharper missing layer is the **configuration-scenario contract** above them:

- explicit scenario classes,
- recipe manifests,
- origin receipts,
- matrix-fidelity reports,
- conflict classifications,
- and release-to-release scenario diffs.

That move is now better grounded because:

- the Rust vision-doc work explicitly treats supportive interfaces from crates as part of Rust’s product experience,
- the 2025 State of Rust survey still says documentation and code are the main learning surfaces,
- Cargo’s official docs already make features, `required-features`, and stable metadata part of the real setup surface,
- docs.rs explicitly documents meaningful build/customization knobs plus hosted-vs-local drift,
- RFC 3416 exists because feature documentation and deprecation structure are still incomplete,
- `document-features` already keeps feature docs close to `Cargo.toml`,
- and `cargo-feature-combinations` / `cargo-hack` already make combinatorial checking real without deciding what the intended receiver-facing scenarios are.

So the gap is no longer “Rust has no feature/config tooling”.
The gap is that maintainers still rarely publish a **reviewable scenario / provenance / fidelity artifact** above that substrate.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0519 Crate Authority Surface Pack Kit** — still one of the most believable ambient-power review lanes.
5. **P-0451 Cfg Availability Ledger Kit** — still a highly leverageful way to make conditional API truth reviewable.
6. **P-0521 Crate Resource Surface Pack Kit** — still one of the best capacity/support contracts in the frontier.
7. **P-0516 Crate Configuration Scenario Pack Kit** — now a much more believable `0.1` crate for official setup lanes, backend choices, and docs-surface honesty.
8. **P-0517 Crate Performance Envelope Pack Kit** — still a strong workload/metric honesty lane.
9. **P-0084 Memory Observability Kit** — still a strong heap-evidence and regression-review lane.

## Why this won over adjacent candidates right now

- It beat **more upgrade/off-ramp follow-ons** because many teams still struggle before version transitions ever begin: they are not yet sure which setup lane is the intended one.
- It beat **more guidance/diagnosis follow-ons** because ordinary setup ambiguity often precedes both compile-time guidance and runtime troubleshooting.
- It beat **more example-surface follow-ons** because official quickstarts still need a more formal scenario/provenance boundary underneath them.
- It beat several strong **domain workbenches** because setup ambiguity cuts across servers, CLIs, embedded, SDKs, proc-macro ecosystems, and docs-heavy crates rather than one protocol family at a time.

## What changed in the archive

Added:
- `meta/crate-configuration-scenario-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-47.md`
- `entries/2026-03-17-227.md`
- `fixtures/crate-configuration-scenario-pack-kit/scenario-class.policy.schema.json`
- `fixtures/crate-configuration-scenario-pack-kit/config-origin.receipt.schema.json`
- `fixtures/crate-configuration-scenario-pack-kit/matrix-fidelity.report.schema.json`
- `fixtures/crate-configuration-scenario-pack-kit/docsrs_all_features_vs_minimal_default/`
- `fixtures/crate-configuration-scenario-pack-kit/tls_backends_compile_together_but_policy_picks_one/`
- `fixtures/crate-configuration-scenario-pack-kit/no_std_builds_but_examples_need_std/`

Updated:
- `proposals/crate-configuration-scenario-pack-kit.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- task-first crate choice,
- feature-doc rendering,
- generic Cargo config provenance,
- docs.rs hosting/parity work,
- powerset execution,
- and receiver-facing scenario contracts

into one fake “better setup docs” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/cargo/reference/features.html
- https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://rust-lang.github.io/rfcs/3416-feature-metadata.html
- https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- https://docs.rs/crate/document-features/latest
- https://docs.rs/cargo-feature-combinations
- https://crates.io/crates/cargo-hack
