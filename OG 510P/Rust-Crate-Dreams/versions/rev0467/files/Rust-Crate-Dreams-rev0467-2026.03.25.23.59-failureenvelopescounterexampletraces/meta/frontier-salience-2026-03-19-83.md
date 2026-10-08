# Frontier salience snapshot — 2026-03-19 (83)

This pass did **not** add another subscriber, another exporter, another backend integration, or another schema linter.
It sharpened a top-ranked support-surface lane:

- **P-0518 Crate Observability Surface Pack Kit** — because Rust now has real tracing / filtering / console / OpenTelemetry substrate, but still lacks one boring receiver-facing contract for **signal stability**, **activation truth**, **bridge-route truth**, **schema posture**, and **sensitivity boundaries**.

## Main judgment

The next worthy move here was **not** more telemetry plumbing.
That substrate already exists.

The sharper missing layer is the **joined observability-support contract** above today’s substrate, especially once five facts stay explicit:

- **signal-stability truth** — which names and fields are safe to query or alert on,
- **activation truth** — which features, filters, layers, runtimes, or cfgs are actually required,
- **bridge-route truth** — whether a signal reaches fmt/log output, console, traces, metrics, logs, or only manual-review territory,
- **schema-posture truth** — which semantic-convention and schema-URL claims the crate is really making,
- **sensitivity-boundary truth** — which fields are safe, payload-derived, hashed, dropped, or still manual-review territory.

That move is better grounded now because:

- the Rust vision-doc work explicitly calls for **supportive interfaces from crates**;
- the 2025 State of Rust survey still says online docs and code are the main learning surfaces and still names debugging/resource usage as recurring pain points;
- Tokio’s tracing docs still frame `tracing` as structured event-based diagnostics with routes into OpenTelemetry, Tokio Console, logging, and profiling;
- `EnvFilter` still makes filter posture concrete, including per-layer filtering and the warning that regex matching should be disabled for potentially untrusted input;
- `console-subscriber` still documents Tokio `tracing` + `tokio_unstable` as real activation requirements;
- `tracing-opentelemetry` still makes the bridge boundary explicit by not exporting logs;
- OpenTelemetry Rust still marks traces, metrics, and logs as beta;
- OpenTelemetry’s Rust libraries page still says the docs team does not know of any Rust library with native OpenTelemetry integrated by default;
- OpenTelemetry schema docs still tie meaning drift to schema URLs;
- OpenTelemetry’s sensitive-data guidance still puts field review responsibility on implementers.

So the gap is no longer “Rust lacks observability tools”.
The gap is that teams still rarely get a **reviewable crate-authored observability promise** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because start/stop truth is so often missing.
3. **P-0522 Crate Persistence Surface Pack Kit** — still one of the sharpest support-surface lanes now that durable-state promises are specific.
4. **P-0521 Crate Resource Surface Pack Kit** — still a strong support lane because waiting-room truth is concrete now.
5. **P-0524 Crate Example Surface Pack Kit** — still a strong first-success lane.
6. **P-0523 Crate Test Surface Pack Kit** — now much stronger because support-level and evidence-lineage truth are concrete.
7. **P-0518 Crate Observability Surface Pack Kit** — now much stronger because activation routes, bridge routes, and sensitivity boundaries are explicit rather than implied.
8. **P-0517 Crate Performance Envelope Pack Kit** — still unusually strong because measurement intent and workload lineage are finally explicit.
9. **P-0525 Crate Diagnosis Surface Pack Kit** — still a strong first-diagnosis lane.
10. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
11. **P-0483 Public API Readiness Bundle Kit** — still a strong joined release-review lane.
12. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest adoption-trust lanes.

## Why this won over adjacent candidates right now

- It beat a deeper **P-0519** pass because activation/route/sensitivity truth now looks unusually buildable thanks to current tracing + OTel docs and explicit bridge limitations.
- It beat another **foreign-package shipping** pass because the archive’s core support-surface stack still had a thinner emitted-signal lane than its first-success, testing, lifecycle, persistence, or performance lanes.
- It beat more **diagnosis** work because troubleshooting support is already much sharper than the support contract for what a crate is intentionally emitting and how another team can actually see it.
- It beat another **pathfinder** pass because choice is already strong enough that the next multiplier is improving what happens after adoption, when operators ask “what can I rely on and how do I turn it on safely?”

## What changed in the archive

Added:
- `entries/2026-03-19-263.md`
- `meta/frontier-salience-2026-03-19-83.md`
- `meta/crate-observability-surface-product-plan-2026-03-19.md`
- `fixtures/crate-observability-surface-pack-kit/README.md`
- `fixtures/crate-observability-surface-pack-kit/bridge-route.receipt.schema.json`
- `fixtures/crate-observability-surface-pack-kit/env_filter_default_hides_advertised_signal/activation-recipe.receipt.example.json`
- `fixtures/crate-observability-surface-pack-kit/console_recipe_requires_runtime_feature/activation-recipe.receipt.example.json`
- `fixtures/crate-observability-surface-pack-kit/semconv_schema_upgrade_changes_query_surface/schema-convention.profile.example.json`
- `fixtures/crate-observability-surface-pack-kit/otel_bridge_route_drops_logs_without_explicit_appender/`
- `fixtures/crate-observability-surface-pack-kit/untrusted_filter_input_requires_literal_mode_or_manual_review/`
- `fixtures/crate-observability-surface-pack-kit/payload_derived_user_id_requires_hash_or_drop/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-observability-surface-pack-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
