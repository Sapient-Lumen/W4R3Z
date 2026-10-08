# Frontier salience snapshot — 2026-03-17 (52)

This pass did **not** promote a new lane.
It sharpened an existing high-value cross-cutting proposal:

- **P-0512 Crate Guidance Pack Kit** — because the archive still lacked a good implementation-ready artifact for the moment when a user is blocked **at compile time** and needs an official smallest path forward.

## Main judgment

The next worthy move in this frontier was **not** another renderer, another proc-macro diagnostics helper, another docs portal, or another support bot.
Those pieces already exist in partial form.

The sharper missing layer is the **crate-authored compile-time guidance contract** above them:

- explicit guidance-authority policy,
- explicit recovery-origin receipts,
- explicit recipe-fidelity reports,
- explicit smallest-good-path recipes,
- and explicit release-to-release support-surface diffs.

That move is now better grounded because:

- Rust’s vision-doc work explicitly argues that crates need more **supportive interfaces**, especially better diagnostics and guidance,
- the 2025 State of Rust survey still says **debugging** remains a real productivity problem,
- the same survey still says **online documentation** and **studying the code** are the main learning surfaces,
- RFC 3368 and the Reference now give crates a stable `#[diagnostic]` namespace with `#[diagnostic::on_unimplemented]`,
- the Reference documents `#[diagnostic::do_not_recommend]` as a way to suppress misleading trait-impl suggestions,
- rustdoc `compile_fail` examples prove that failure-path examples can be tested but also note that code failing today may compile in a future release,
- `trybuild` and `ui_test` already make compile-fail stderr a first-class testable surface,
- `miette` already exposes diagnostic code/help/URL metadata,
- and `proc-macro-error2` already offers a more structured proc-macro error path than plain panics.

So the gap is no longer “Rust cannot show better messages”.
The gap is that maintainers still rarely publish a **reviewable guidance / recovery / recipe-fidelity artifact** above today’s attributes, compile-fail tests, docs examples, and diagnostics crates.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0519 Crate Authority Surface Pack Kit** — still one of the most believable ambient-power review lanes.
5. **P-0451 Cfg Availability Ledger Kit** — still a highly leverageful way to make conditional API truth reviewable.
6. **P-0510 Crate Capability Contract & Interop Profile Kit** — still the strongest producer-side fact surface for a single crate.
7. **P-0513 Crate Runtime Handoff Pack Kit** — still the strongest post-failure support-bundle lane.
8. **P-0512 Crate Guidance Pack Kit** — now a much more believable `0.1` crate for exact-vs-advisory guidance, recovery provenance, and checked recipe fidelity.
9. **P-0511 Crate Interop Profile Pack Kit** — still a strong shared-boundary lane once single-crate and early-failure support truth are in place.
10. **P-0521 Crate Resource Surface Pack Kit** — still one of the best capacity/support contracts in the frontier.

## Why this won over adjacent candidates right now

- It beat **more runtime-support follow-ons** because the archive had already made runtime handoff much more buildable than compile-time guidance.
- It beat **more docs/adoption follow-ons** because docs browsing is not the same lane as verified failure-path recovery.
- It beat **more proc-macro-specific crates** because trait-heavy libraries, feature-rich crates, and target/cfg-limited crates share this gap too.
- It beat **more release/migration follow-ons** because leaving or upgrading a crate is downstream of first getting unstuck at the moment of misuse.

## What changed in the archive

Added:
- `meta/crate-guidance-pack-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-52.md`
- `entries/2026-03-17-232.md`
- `fixtures/crate-guidance-pack-kit/guidance-authority.policy.schema.json`
- `fixtures/crate-guidance-pack-kit/recovery-origin.receipt.schema.json`
- `fixtures/crate-guidance-pack-kit/recipe-fidelity.report.schema.json`
- `fixtures/crate-guidance-pack-kit/compile_fail_doctest_catches_failure_but_not_message_drift/`
- `fixtures/crate-guidance-pack-kit/do_not_recommend_hides_blanket_impl_but_recipe_missing/`
- `fixtures/crate-guidance-pack-kit/proc_macro_diagnostic_url_points_to_stale_syntax/`

Updated:
- `proposals/crate-guidance-pack-kit.md`
- `fixtures/crate-guidance-pack-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- generic diagnostic rendering,
- docs portals,
- support bots,
- proc-macro error helpers,
- runtime handoff,
- and task-first crate choice

into one fake “better DX” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rfcs/3368-diagnostic-attribute-namespace.html
- https://doc.rust-lang.org/reference/attributes/diagnostics.html
- https://doc.rust-lang.org/beta/releases.html
- https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
- https://docs.rs/trybuild/latest/trybuild/
- https://docs.rs/ui_test/latest/ui_test/
- https://docs.rs/miette/latest/miette/trait.Diagnostic.html
- https://docs.rs/proc-macro-error2/latest/proc_macro_error2/
