# Frontier salience snapshot — 2026-03-19 (76)

This pass did **not** add another logger, another metrics façade, another debugger helper, or another hosted support platform.
It sharpened a top-ranked support-surface lane:

- **P-0525 Crate Diagnosis Surface Pack Kit** — because Rust now has real diagnosis substrate, but still lacks one boring receiver-facing contract for recognized symptoms, first-inspection order, instrumentation honesty, and safe support bundles.

## Main judgment

The next worthy move here was **not** more substrate.
That substrate already exists.

The sharper missing layer is the **joined diagnosis-support contract** above today’s substrate, especially once five facts are kept explicit:

- **symptom truth** — what problem class the crate officially recognizes,
- **triage-order truth** — what should be inspected first and why,
- **signal truth** — which traces, metrics, warnings, or diagnostic codes actually matter,
- **instrumentation truth** — whether the advertised console/tracing/metrics path is really supported,
- **bundle-safety truth** — what evidence may be attached safely versus only after redaction or manual review.

That move is better grounded now because:

- the Rust vision-doc work explicitly asks for **supportive interfaces from crates**;
- the 2025 State of Rust survey still shows debugging as a meaningful productivity problem while docs and code stay the main learning surfaces;
- the 2026 debugging survey still says debugger support, async debugging, visualizers, and expression evaluation are unfinished;
- Tokio’s tracing docs now present tracing as the path for logging, profiling, collectors, and **debugging with Tokio Console**;
- `console-subscriber` now makes the easy-path requirement visible: the runtime must emit compatible tracing events;
- `tokio-metrics` already exposes interval runtime/task metrics;
- `miette::Diagnostic` already gives crates a code/help/URL vocabulary;
- and `tracing-error::SpanTrace` already captures logical async context above ordinary stack frames.

So the gap is no longer “Rust lacks diagnostics”.
The gap is that teams still rarely get a **reviewable crate-authored troubleshooting promise** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0525 Crate Diagnosis Surface Pack Kit** — now a stronger implementation-ready support-truth lane because the signal substrate below it is real and the receiver-facing contract above it is still weak.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — still a strong product-level support surface.
5. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
6. **P-0483 Public API Readiness Bundle Kit** — now a stronger joined release-review lane after the latest pass.
7. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
8. **P-0027 text-input-kit** — still one of the clearest end-user product-engineering opportunities.
9. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
10. **P-0515 Crate Off-Ramp Pack Kit** — still a strong survivability / supportiveness follow-on.
11. **P-0071 MCP Guard Kit** — still a strong modern protocol/deployment-support lane.
12. **P-0012 Desktop ShipKit** — still a strong desktop release/adoption lane.

## Why this won over adjacent candidates right now

- It beat a deeper **P-0524** pass because the archive’s top support stack still lacked an equally concrete answer for “first diagnosis” after “first success”.
- It beat a deeper **P-0519** pass because authority posture is strategically important but currently less timely than crate-authored troubleshooting support backed by today’s live substrate.
- It beat a deeper **P-0520** pass because lifecycle contracts matter most after teams can first recognize and carry the ordinary symptom/support path.
- It beat another **foreign-package shipping** pass because the archive already had several fresh shipping-contract revisions and still needed a stronger core supportiveness lane.

## What changed in the archive

Added:
- `entries/2026-03-19-256.md`
- `meta/frontier-salience-2026-03-19-76.md`
- `meta/crate-diagnosis-surface-product-plan-2026-03-19.md`
- `fixtures/crate-diagnosis-surface-pack-kit/retry_storm_client/triage-sequence.manifest.example.json`
- `fixtures/crate-diagnosis-surface-pack-kit/queue_growth_worker/signal-map.report.example.json`
- `fixtures/crate-diagnosis-surface-pack-kit/local_cli_startup_stall/support-capture.report.example.json`
- `fixtures/crate-diagnosis-surface-pack-kit/console_recipe_declared_but_runtime_not_instrumented/diagnosis-check.report.example.json`
- `fixtures/crate-diagnosis-surface-pack-kit/bundle_capture_exports_secret_shaped_env/bundle-safety.report.example.json`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-diagnosis-surface-pack-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
- `fixtures/crate-diagnosis-surface-pack-kit/README.md`
- the relevant scenario READMEs under `fixtures/crate-diagnosis-surface-pack-kit/`
