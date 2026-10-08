# Frontier salience snapshot — 2026-03-17 (53)

This pass did **not** promote a new lane.
It sharpened an existing high-value cross-cutting proposal:

- **P-0525 Crate Diagnosis Surface Pack Kit** — because the archive still needed a more reviewable answer to the common state where a crate is already running, but users need an official troubleshooting path that is neither compile-time guidance nor a post-crash bundle.

## Main judgment

The next worthy move here was **not** another telemetry façade, another debugger helper, another hosted support workflow, or another generic “doctor” command.
Those pieces already exist in partial form.

The sharper missing layer is the **crate-authored diagnosis contract** above them:

- explicit symptom-class meaning,
- explicit triage-origin receipts,
- explicit signal maps,
- explicit bundle-safety evaluation,
- and explicit boundaries between troubleshooting, compile-time guidance, example surfaces, observability, and runtime handoff.

That move is better grounded now because:

- Rust’s 2025 vision work explicitly argues for more **supportive interfaces from crates**, not only more power or abstraction substrate;
- the 2025 State of Rust survey still says **online documentation** and **studying the code** are the main learning surfaces, while debugging remains a meaningful productivity problem;
- the February 2026 debugging survey still says Rust debugging quality varies across debuggers, operating systems, async support, and expression evaluation;
- Tokio’s tracing guidance explicitly presents `tracing` as the path for debugging applications and using Tokio Console;
- `console-subscriber` says the easiest path is `console_subscriber::init()` but also requires a runtime that emits compatible tracing events;
- `metrics` already gives libraries a façade over counters, gauges, and histograms;
- `tokio-metrics` already provides task and runtime interval metrics;
- and `miette` already exposes diagnostic codes, help, and URLs that can serve as diagnosis-entry points.

So the gap is no longer “Rust has no signals” or “Rust has no debugging tooling”.
The gap is that maintainers still rarely publish a **reviewable symptom / triage / safe-capture contract** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest ambient-power review lanes.
5. **P-0451 Cfg Availability Ledger Kit** — still one of the highest-leverage conditional-API truth lanes.
6. **P-0510 Crate Capability Contract & Interop Profile Kit** — still the strongest producer-side fact surface for a single crate.
7. **P-0525 Crate Diagnosis Surface Pack Kit** — now more believable as a receiver-facing troubleshooting contract because class meaning, triage provenance, and bundle safety are separate review objects instead of one vague “doctor” story.
8. **P-0513 Crate Runtime Handoff Pack Kit** — still the strongest post-failure support-bundle lane.
9. **P-0512 Crate Guidance Pack Kit** — now a stronger compile-time recovery lane, but still distinct from live troubleshooting.
10. **P-0511 Crate Interop Profile Pack Kit** — still a strong shared-boundary lane once per-crate support truth is in place.

## Why this won over adjacent candidates right now

- It beat **example-surface follow-ons** because the archive had already made first-success support more concrete than first-troubleshooting support.
- It beat **more runtime-handoff follow-ons** because the missing question here happens even when nothing crashed.
- It beat **more observability follow-ons** because emitted signals still do not tell a downstream user which symptom bucket they should inspect first.
- It beat **more debugger-specific work** because the archive needed a cross-domain troubleshooting contract, not a narrower tool integration story.

## What changed in the archive

Added:
- `meta/crate-support-surface-boundaries-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-53.md`
- `entries/2026-03-17-233.md`
- `fixtures/crate-diagnosis-surface-pack-kit/README.md`
- `fixtures/crate-diagnosis-surface-pack-kit/symptom-class.policy.schema.json`
- `fixtures/crate-diagnosis-surface-pack-kit/triage-origin.receipt.schema.json`
- `fixtures/crate-diagnosis-surface-pack-kit/bundle-safety.report.schema.json`
- `fixtures/crate-diagnosis-surface-pack-kit/console_recipe_declared_but_runtime_not_instrumented/`
- `fixtures/crate-diagnosis-surface-pack-kit/timeout_bucket_hides_dns_vs_tls_triage_split/`
- `fixtures/crate-diagnosis-surface-pack-kit/bundle_capture_exports_secret_shaped_env/`

Updated:
- `proposals/crate-diagnosis-surface-pack-kit.md`
- `meta/crate-diagnosis-surface-product-plan-2026-03-17.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- compile-time guidance,
- runtime handoff,
- observability surfaces,
- official example paths,
- and diagnosis support

into one fake “supportiveness” lane.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://tokio.rs/tokio/topics/tracing
- https://docs.rs/console-subscriber/latest/console_subscriber/fn.init.html
- https://docs.rs/console-subscriber/latest/console_subscriber/struct.Builder.html
- https://docs.rs/metrics/latest/metrics/
- https://docs.rs/tokio-metrics/latest/tokio_metrics/struct.RuntimeMonitor.html
- https://docs.rs/miette/latest/miette/trait.Diagnostic.html
