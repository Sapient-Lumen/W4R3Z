# Frontier salience snapshot — 2026-03-17 (50)

This pass did **not** promote a new lane.
It sharpened an existing high-value cross-cutting proposal:

- **P-0511 Crate Interop Profile Pack Kit** — because the archive still lacked a good implementation-ready artifact for the moment after a maintainer can describe one crate honestly but before multiple crates can say *they meet at the same ecosystem boundary* in a reusable, reviewable way.

## Main judgment

The next worthy move in this frontier was **not** another ranking formula, another producer-side metadata contract, another semver checker, or another domain-specific conformance suite.
Those pieces already exist in partial form.

The sharper missing layer is the **shared interop-profile contract** above them:

- explicit profile classes,
- explicit boundary obligations,
- explicit static conformance receipts,
- explicit pair-compatibility reports,
- explicit pair-fidelity reports,
- and explicit migration hazards.

That move is now better grounded because:

- the Rust vision-doc work explicitly recommends helping users navigate crates **and** enabling smoother interop between libraries,
- the 2025 State of Rust survey still says online documentation and studying the code are the dominant learning surfaces,
- the EII goal and evolving-traits work both point toward more explicit, evolvable ecosystem customization points,
- the `http`, `tower-service`, `tower`, `futures-core`, and Serde crates already provide shared substrate,
- and current framework docs like `axum` explicitly market cross-framework reuse through those shared building blocks.

So the gap is no longer “Rust has no shared building blocks”.
The gap is that maintainers still rarely publish a **reviewable profile / obligation / pair-fidelity artifact** above those building blocks.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0519 Crate Authority Surface Pack Kit** — still one of the most believable ambient-power review lanes.
5. **P-0451 Cfg Availability Ledger Kit** — still a highly leverageful way to make conditional API truth reviewable.
6. **P-0510 Crate Capability Contract & Interop Profile Kit** — still the strongest producer-side fact surface for a single crate.
7. **P-0511 Crate Interop Profile Pack Kit** — now a much more believable `0.1` crate for shared ecosystem boundaries, adapter obligations, and pair-fidelity honesty.
8. **P-0521 Crate Resource Surface Pack Kit** — still one of the best capacity/support contracts in the frontier.
9. **P-0516 Crate Configuration Scenario Pack Kit** — still one of the strongest setup-honesty lanes now that it has an implementation-ready shape.
10. **P-0514 Crate Upgrade Pack Kit** — still a strong release-to-release hazard and checked-lane honesty lane.

## Why this won over adjacent candidates right now

- It beat **more capability-contract follow-ons** because the archive still needed the reusable shared vocabulary that single-crate support contracts would import.
- It beat **more example/guidance follow-ons** because examples can teach one crate, but they do not define a stable ecosystem boundary multiple crates can fit together.
- It beat **more semver/public-API follow-ons** because API drift tools still do not say whether two crates meet at the same boundary or merely compile separately.
- It beat several strong **domain workbenches** because shared interop profiles cut across async, HTTP, SDK, middleware, data-model, embedded-adapter, and future ecosystem building-block lanes.

## What changed in the archive

Added:
- `meta/crate-interop-profile-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-50.md`
- `entries/2026-03-17-230.md`
- `fixtures/crate-interop-profile-pack-kit/profile-class.policy.schema.json`
- `fixtures/crate-interop-profile-pack-kit/boundary-obligation.receipt.schema.json`
- `fixtures/crate-interop-profile-pack-kit/pair-fidelity.report.schema.json`
- `fixtures/crate-interop-profile-pack-kit/public_tokio_type_leaks_runtime_neutral_profile/`
- `fixtures/crate-interop-profile-pack-kit/tower_http_pair_matches_service_but_misses_body_shape/`
- `fixtures/crate-interop-profile-pack-kit/serde_models_expose_format_specific_helpers/`

Updated:
- `proposals/crate-interop-profile-pack-kit.md`
- `fixtures/crate-interop-profile-pack-kit/README.md`
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
- producer-side capability contracts,
- shared ecosystem interop profiles,
- semver/public-API evidence,
- and domain-specific conformance kits

into one fake “better compatibility tooling” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- https://docs.rs/http/latest/http/
- https://docs.rs/tower-service/latest/tower_service/trait.Service.html
- https://docs.rs/tower/latest/tower/
- https://docs.rs/axum/latest/axum/
- https://docs.rs/futures-core/latest/futures_core/stream/trait.Stream.html
- https://docs.rs/serde/latest/serde/
