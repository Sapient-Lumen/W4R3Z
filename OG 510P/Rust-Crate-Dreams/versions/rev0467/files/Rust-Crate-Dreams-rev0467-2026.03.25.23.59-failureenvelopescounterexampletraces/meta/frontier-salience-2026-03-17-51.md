# Frontier salience snapshot — 2026-03-17 (51)

This pass did **not** promote a new lane.
It sharpened an existing high-value cross-cutting proposal:

- **P-0513 Crate Runtime Handoff Pack Kit** — because the archive still lacked a good implementation-ready artifact for the moment after a program has already failed but before support can do anything trustworthy with the result.

## Main judgment

The next worthy move in this frontier was **not** another pretty error renderer, another tracing stack, another hosted crash collector, or another generic incident bundle.
Those pieces already exist in partial form.

The sharper missing layer is the **crate-authored runtime handoff contract** above them:

- explicit capture-exactness classes,
- explicit share-safety receipts,
- explicit error-path and panic-path boundaries,
- explicit handoff-fidelity reports,
- explicit recovery-step manifests,
- and explicit release-to-release handoff diffs.

That move is now better grounded because:

- Rust’s vision-doc work explicitly argues that crates need more **supportive interfaces**, not only powerful abstractions,
- the 2025 State of Rust survey still says **debugging remains a notable productivity problem** and that **online documentation and code** are the main learning surfaces,
- `std::panic::set_hook` makes crate-authored panic capture and customization a real surface,
- `error-stack` makes context and attachment propagation explicit,
- `tracing-error` shows that logical span context can sometimes be more useful than raw stacks,
- `SpanTraceStatus` makes empty-versus-unsupported status explicit,
- `human-panic` shows that user-submittable crash reports are already practical,
- and `color-eyre` shows that panic/error hooks can already attach custom sections and issue-reporting metadata.

So the gap is no longer “Rust has no runtime failure tooling”.
The gap is that maintainers still rarely publish a **reviewable exactness / share-safety / fidelity artifact** above today’s runtime error and panic substrate.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0519 Crate Authority Surface Pack Kit** — still one of the most believable ambient-power review lanes.
5. **P-0451 Cfg Availability Ledger Kit** — still a highly leverageful way to make conditional API truth reviewable.
6. **P-0510 Crate Capability Contract & Interop Profile Kit** — still the strongest producer-side fact surface for a single crate.
7. **P-0513 Crate Runtime Handoff Pack Kit** — now a much more believable `0.1` crate for exact runtime receipts, safe-to-share bundles, and fidelity-aware failure handoff.
8. **P-0511 Crate Interop Profile Pack Kit** — still a strong shared-boundary lane once single-crate and failure-support truth are in place.
9. **P-0521 Crate Resource Surface Pack Kit** — still one of the best capacity/support contracts in the frontier.
10. **P-0516 Crate Configuration Scenario Pack Kit** — still one of the strongest setup-honesty lanes now that it has an implementation-ready shape.

## Why this won over adjacent candidates right now

- It beat **compile-time guidance follow-ons** because the archive still lacked the equally disciplined artifact for failures that occur after a successful build.
- It beat **off-ramp follow-ons** because runtime failure handling is a more immediate cross-domain pain for teams who are still actively depending on a crate.
- It beat **more observability follow-ons** because ongoing telemetry is not the same lane as a safe, support-ready post-failure bundle.
- It beat several strong **domain incident workbenches** because runtime handoff cuts across CLIs, services, libraries, internal platforms, and privacy-sensitive support flows rather than one protocol family at a time.

## What changed in the archive

Added:
- `meta/crate-runtime-handoff-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-51.md`
- `entries/2026-03-17-231.md`
- `fixtures/crate-runtime-handoff-pack-kit/capture-exactness.policy.schema.json`
- `fixtures/crate-runtime-handoff-pack-kit/share-safety.receipt.schema.json`
- `fixtures/crate-runtime-handoff-pack-kit/handoff-fidelity.report.schema.json`
- `fixtures/crate-runtime-handoff-pack-kit/error_stack_attachment_secret_needs_hash_redaction/`
- `fixtures/crate-runtime-handoff-pack-kit/spantrace_declared_but_error_layer_missing/`
- `fixtures/crate-runtime-handoff-pack-kit/panic_hook_present_but_report_bundle_path_missing/`

Updated:
- `proposals/crate-runtime-handoff-pack-kit.md`
- `fixtures/crate-runtime-handoff-pack-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- compile-time guidance packs,
- generic report renderers,
- tracing / observability stacks,
- hosted crash collectors,
- and domain-specific incident or replay bundles

into one fake “better runtime errors” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/std/panic/fn.set_hook.html
- https://docs.rs/error-stack/latest/error_stack/
- https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTrace.html
- https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTraceStatus.html
- https://docs.rs/human-panic/latest/human_panic/
- https://docs.rs/color-eyre/latest/color_eyre/fn.install.html
- https://docs.rs/color-eyre/latest/color_eyre/config/struct.HookBuilder.html
