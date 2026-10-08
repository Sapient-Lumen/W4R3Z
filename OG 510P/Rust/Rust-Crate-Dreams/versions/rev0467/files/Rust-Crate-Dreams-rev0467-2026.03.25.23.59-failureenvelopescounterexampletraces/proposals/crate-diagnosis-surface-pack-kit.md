---
id: P-0525
title: Crate Diagnosis Surface Pack Kit — symptom catalogs, self-check receipts, and diagnosis-surface diffs for library authors
status: idea
domains: [crates, dx, diagnostics, debugging, troubleshooting, observability, supportiveness]
last_reviewed: 2026-03-19
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
  - https://tokio.rs/tokio/topics/tracing
  - https://docs.rs/console-subscriber/latest/console_subscriber/
  - https://docs.rs/tracing/latest/tracing/
  - https://docs.rs/metrics/latest/metrics/
  - https://docs.rs/tokio-metrics/latest/tokio_metrics/
  - https://tokio.rs/blog/2021-12-announcing-tokio-console
  - https://docs.rs/miette/latest/miette/
  - https://docs.rs/miette/latest/miette/trait.Diagnostic.html
  - https://docs.rs/miette/latest/miette/struct.JSONReportHandler.html
  - https://docs.rs/tracing-error/latest/tracing_error/
  - https://docs.rs/tracing-error/latest/tracing_error/struct.TracedError.html
  - https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTrace.html
  - https://docs.rs/console-subscriber/latest/console_subscriber/struct.Builder.html
  - https://docs.rs/tokio-metrics/latest/tokio_metrics/struct.RuntimeMonitor.html
---

# Problem

The archive now has much stronger receiver-facing lanes for:

- choosing crates,
- understanding support claims,
- fitting interop profiles,
- getting compile-time guidance,
- handling runtime failure handoff,
- upgrading,
- leaving a crate,
- choosing setup scenarios,
- reasoning about performance posture,
- understanding observability surfaces,
- reviewing authority / determinism posture,
- reviewing lifecycle / shutdown behavior,
- reviewing resource / saturation posture,
- reviewing persistence / durability posture,
- reviewing downstream test support,
- and reviewing official example / quickstart support.

It still lacks a good answer to another ordinary downstream question:

> “The crate does not just fail fast — it stalls, floods, retries forever, goes quiet, or behaves weirdly. What symptoms does this crate officially recognize, what should I inspect first, and what evidence should I capture before I file an issue?”

That gap matters because Rust’s diagnostics substrate is real but unevenly turned into crate-authored support.
The December 2025 Rust vision-doc work explicitly recommends more **supportive interfaces from crates**.
The 2025 State of Rust survey says debugging remains a notable productivity problem while documentation and code remain the main learning surfaces.
The February 2026 Rust debugging survey says Rust still needs stronger support across debuggers, operating systems, visualizers, async debugging, and expression evaluation.
Tokio’s tracing guidance and the `tracing` ecosystem already provide structured diagnostic emission.
`console-subscriber` / tokio-console already provide one concrete async debugging and profiling path.
`metrics` gives libraries a lightweight façade and lets executables choose exporters.
`tokio-metrics` already exposes runtime and task metrics.

But that substrate still does **not** give maintainers one boring workflow for questions like:

- which symptoms are *officially recognized* versus merely folklore from old issues,
- which self-checks a downstream user should run before opening a ticket,
- which traces, events, counters, gauges, histograms, or runtime snapshots are authoritative for a given symptom,
- which remediation classes are officially supported versus best-effort guesses,
- which evidence can be bundled safely without oversharing secrets,
- and how a crate’s diagnosis surface changed across releases.

The worthy crate is therefore **not** another debugger, **not** another telemetry backend, **not** another distributed tracing stack, and **not** just a nicer logging façade.
It is a **Crate Diagnosis Surface Pack Kit**: a crate that helps maintainers author, verify, diff, and export the receiver-facing troubleshooting / symptom / self-check / remediation support contract their crate gives other people.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What symptoms does this crate officially recognize?**
2. **What self-checks or “doctor” actions exist for those symptoms?**
3. **What signals should a downstream user inspect first?**
4. **What remediation classes are officially recommended?**
5. **What support-capture bundle can be produced safely?**
6. **Which parts of diagnosis are automated versus manual-review-only?**
7. **How did that diagnosis surface change across releases?**

That is more valuable than leaving users to reconstruct troubleshooting paths from issue threads, log folklore, metrics dashboards, and maintainer memory.

# What it provides

- `diagnosis-surface-pack.toml` — versioned declaration of supported symptoms, self-check families, signal maps, remediation classes, and capture policy.
- `symptom-catalog.receipt.json` — observed receipt for symptoms the crate chooses to recognize explicitly.
- `self-check.manifest.json` — named checks such as `config_sanity`, `runtime_snapshot`, `loopback_probe`, `feature_matrix_review`, or `manual_review_required`.
- `signal-map.report.json` — maps each symptom to traces, events, metrics, runtime facts, or manual-review guidance.
- `remediation-playbook.manifest.json` — suggested remediation classes such as `adjust_config`, `enable_signal`, `reduce_concurrency`, `capture_bundle`, `switch_topology`, or `manual_review_required`.
- `support-capture.report.json` — explicit description of what evidence is safe and useful to attach for a given symptom family.
- `symptom-taxonomy.profile.json` — aliases, ambiguity notes, automation levels, and “symptom is not root cause” discipline.
- `symptom-class.policy.json` — class-level meaning that keeps a vague symptom bucket from pretending to be a proved root cause.
- `capture-policy.profile.json` — explicit allow-listed capture classes, sensitivity levels, opt-in rules, and redaction posture.
- `triage-sequence.manifest.json` — ordered “inspect first / inspect next / escalate with bundle” flow for a recognized symptom.
- `triage-origin.receipt.json` — provenance for each first-inspection step so troubleshooting order does not silently drift away from the code/docs that justified it.
- `bundle-safety.report.json` — verdict on whether a declared support bundle is actually safe to attach.
- `diagnosis-check.report.json` — verifies that declared self-checks, signal maps, triage sequences, and capture policies are still coherent and reviewable.
- `diagnosis-surface-diff.report.json` — compares two releases and classifies `symptom_added`, `symptom_removed`, `symptom_class_changed`, `triage_sequence_changed`, `signal_map_changed`, `self_check_changed`, `remediation_changed`, `capture_policy_changed`, and `manual_review_required`.
- `diagnosis-summary.md` — short human-facing explanation of which symptoms are recognized, what to inspect first, and what bundle to capture.
- `cargo diagnosis-surface check` — verify self-check manifests, signal maps, and capture policy.
- `cargo diagnosis-surface diff <old> <new>` — show how official troubleshooting surfaces changed.
- `cargo diagnosis-surface summary` — render a concise troubleshooting guide for downstream users.

# What the crate should provide other people

1. **An official symptom catalog** above issue-search folklore.
2. **Self-checks maintainers actually stand behind** instead of asking users to “turn on more logs and see”.
3. **Signal-to-symptom maps** so tracing and metrics become receiver-facing support rather than mere implementation detail.
4. **Safe support-capture bundles** so downstream users know what to attach and what to redact.
5. **A diffable diagnosis surface** so release reviewers can see when recognized symptoms, self-checks, or remediation guidance changed.
6. **Importable vocabulary** for docs portals, support bots, release review, and crate-support packs.
7. **A support-level taxonomy** so maintainers can distinguish automated self-checks, partial checks, and manual-review-only troubleshooting.

# Persona / who it’s for

- async library authors whose users report stalls, hangs, and scheduler weirdness
- SDK/client maintainers who need official guidance for retry storms, endpoint misconfiguration, auth drift, or connection pool saturation
- CLI/tool maintainers whose users report “it freezes” or “it waits forever” without clear reproduction
- database/storage/message-queue crate maintainers who need symptom-to-signal maps for backlog growth or timeout confusion
- downstream teams that need a smallest-credible troubleshooting path before escalating to maintainers
- support/tool authors who want stable diagnosis metadata instead of scraping issue templates heuristically

# Users & user stories

- **Async client maintainer**: “Declare `request_hang`, `retry_storm`, and `idle_but_busy` as recognized symptoms, publish the first traces and runtime facts users should inspect, and ship a support-capture recipe.”
- **Worker-queue crate maintainer**: “Tell users how to distinguish `queue_growth` from `consumer_starvation`, which gauges or histograms matter, and which self-checks are safe to run locally.”
- **CLI maintainer**: “Publish the difference between `startup_stall`, `config_mismatch`, and `external_service_wait`, plus the official dry-run and loopback probes.”
- **Embedded/network maintainer**: “Mark which diagnosis steps are host-only, board-only, or manual-review-only so users do not assume magic local automation.”
- **Downstream integrator**: “Diff two releases and see whether the official troubleshooting path for a timeout or retry problem changed.”

# Prior art (and why it’s insufficient)

- Tokio’s tracing docs and the `tracing` ecosystem already explain how to emit structured diagnostic information.
- tokio-console / `console-subscriber` already provide rich async debugging and profiling data for instrumented Tokio applications.
- `metrics` already gives library authors a common emission façade.
- `tokio-metrics` already exposes runtime and task metrics.
- Many projects also publish ad hoc “doctor” commands, issue templates, FAQ pages, or log-env-var recipes.

What remains missing is a **crate-authored diagnosis support contract workflow** above those pieces:

- author one per-crate pack that declares recognized symptoms,
- classify self-checks and manual-review boundaries,
- map symptoms to signals and remediation classes,
- export a small machine-readable troubleshooting catalog,
- and diff that support surface across releases.

# Why now

This is better timed than it would have been a year earlier because the ecosystem now has enough visible diagnostics substrate to make the missing layer obvious, and the archive now has enough adjacent support-surface lanes that diagnosis needs sharper boundaries of its own.
Rust is publicly talking about supportive interfaces from crates.
The survey still says debugging matters and docs/code are where people learn.
Tokio, `tracing`, `metrics`, and tokio-console already supply real signal infrastructure.
So the remaining gap is not “invent diagnostics” but “make crate-authored diagnosis support reviewable, conservative, and portable”.

# The receiver-facing artifact model

A strong design here should be deliberately small.
The first version does **not** need to become a full support platform.
It needs to make diagnosis-support surfaces exportable and diffable.

Recommended first artifact vocabulary:

- `support_level`: `official_self_check`, `official_signal_map`, `partial_support`, `manual_review_required`
- `symptom_class`: `startup_stall`, `request_hang`, `retry_storm`, `high_cpu`, `idle_but_busy`, `queue_growth`, `resource_leak`, `manual_review_required`
- `check_kind`: `pure_local_check`, `config_sanity_check`, `loopback_probe`, `runtime_snapshot`, `manual_review_required`
- `signal_kind`: `counter`, `gauge`, `histogram`, `trace_span`, `trace_event`, `runtime_metric`, `manual_review_required`
- `remediation_kind`: `adjust_config`, `enable_signal`, `capture_bundle`, `reduce_concurrency`, `switch_topology`, `manual_review_required`

Minimal pack sketch:

```toml
schema_version = "0.1"
crate = "example-crate"

[[symptoms]]
name = "request_hang"
symptom_class = "request_hang"
support_level = "official_signal_map"

[[checks]]
name = "loopback_probe"
check_kind = "loopback_probe"
```

For a more implementation-ready build sketch, see `meta/crate-diagnosis-surface-product-plan-2026-03-19.md`.

# Minimum lovable MVP

1. **Catalog the diagnosis surface** in a small explicit declaration.
2. **Let maintainers mark recognized symptoms** explicitly.
3. **Capture self-checks** in a reviewable vocabulary.
4. **Capture signal maps** in a reviewable vocabulary.
5. **Capture remediation classes and support bundles** conservatively.
6. **Produce a release diff** that spots changed or removed troubleshooting paths.
7. **Render one short human summary** for downstream users.

If version one does only that, it is already useful.

# Architecture sketch

Possible implementation layers:

1. **Declaration layer**
   - let maintainers declare symptoms, support levels, check kinds, signal maps, and capture policies;
   - keep the pack small enough to review in code review.

2. **Verification layer**
   - verify that referenced traces/metrics/check entrypoints exist where possible;
   - record partial or manual-review-only status when runtime or environment constraints prevent deeper verification;
   - keep “evidence exists” separate from “the system auto-diagnosed the bug”.

3. **Capture layer**
   - define safe support-capture classes;
   - bias toward declarative bundles, redaction hooks, and explicit manual review instead of scraping everything from the host.

4. **Diff/report layer**
   - compare two diagnosis surfaces;
   - render release-review summaries;
   - export machine-readable reports for support tooling or docs portals.

# Compatibility story

This should work for more than one archetype:

- **async client crates** with tracing spans, runtime metrics, and loopback probes,
- **CLI/tooling crates** with dry-run checks and config sanity reviews,
- **SDK crates** with retry, timeout, and endpoint-auth diagnosis surfaces,
- **queue / worker libraries** with backlog-growth or saturation symptom classes,
- **embedded / device-aware crates** with board-only capture paths and manual-review boundaries,
- **storage crates** with recovery posture and timeout-vs-backlog distinction.

A truly worthy crate here wins by making those archetypes comparable without pretending they all have identical runtime powers.

# Security / safety model

The crate should bias toward **declaring** safe diagnosis paths, not automatically collecting every host secret or runtime artifact it can reach.
It should make external network use, credential dependence, runtime snapshots, and redaction boundaries explicit.
When full verification or capture is unsafe or impractical, it should emit `manual_review_required` instead of guessing.

# Maintenance expectations

The key to long-term usefulness is **boring update discipline**:

- symptom catalogs should be cheap to review,
- self-check manifests should stay small,
- signal maps should be easy to diff,
- remediation downgrades should be noisy,
- and support-capture policy should never hide inside prose.

# Why this beats adjacent candidates right now

This lane beats “another telemetry crate” because the missing problem is not emission substrate alone.
It beats “another debugger helper” because debugger support is only one slice of receiver-facing troubleshooting.
It beats “another runtime-handoff bundle” because many painful problems are **steady-state diagnosis** problems, not crash-only failures.
And it beats “just document the logs” because signal lists without symptom/self-check/remediation contracts still leave users guessing.

# Relation to adjacent archive lanes

- **P-0512** explains failure paths and recovery guidance. **P-0525** explains steady-state symptom recognition and diagnosis support.
- **P-0513** explains runtime failure handoff bundles. **P-0525** explains symptom catalogs, self-checks, and troubleshooting bundles even when nothing crashed.
- **P-0518** explains observability surfaces. **P-0525** imports those signals into user-facing diagnosis contracts.
- **P-0486** explains debuginfo, visualizers, and debugger posture. **P-0525** explains what symptoms to diagnose and what evidence to inspect.
- **P-0523** explains downstream test support. **P-0525** explains downstream troubleshooting support in live or quasi-live conditions.
- **P-0524** explains official example / quickstart support. **P-0525** explains official symptom / troubleshooting support once the happy path no longer holds.

# Scorecard

- **Cross-domain applicability:** 5/5
- **Supports users without becoming a giant platform:** 5/5
- **Fits the “boring but epic” test:** 5/5
- **Builds on existing diagnostics substrate instead of ignoring it:** 5/5
- **Produces reviewable artifacts rather than vibes:** 5/5
- **Risk of becoming a giant auto-support system:** 2/5 (good, if kept disciplined)

**Total:** 27/30

That is strong enough to merit promotion.

# Non-goals

- not a hosted support portal
- not a replacement for `tracing`, tokio-console, or `metrics`
- not a universal incident-management system
- not an always-on host scraper
- not a magical auto-remediator that claims to infer every root cause automatically

# Open questions

- Should self-check manifests point to real commands, code paths, or only abstract recipes in v0.1?
- Should diagnosis surfaces import redaction policy directly from observability/runtime-handoff lanes or duplicate a small local vocabulary?
- Should symptom classes be global, per-domain, or mixed with allow-listed extension points?
- How much automatic “signal existence” verification is practical without forcing crates into one tracing or metrics stack?
- Should release diffs classify support downgrades more explicitly than generic `signal_map_changed` or `self_check_changed`?

# Suggested fixtures / starter scenarios

The archive should carry starter examples for:

- `async_request_hang`
- `retry_storm_client`
- `queue_growth_worker`
- `local_cli_startup_stall`
- `console_recipe_declared_but_runtime_not_instrumented`
- `timeout_bucket_hides_dns_vs_tls_triage_split`
- `bundle_capture_exports_secret_shaped_env`

Those scenarios together stress:

- async runtime signals,
- retry and endpoint confusion,
- backlog / saturation troubleshooting,
- and local dry-run or config-sanity support.

# Sources

- Rust vision-doc post: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026: https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Tokio tracing docs: https://tokio.rs/tokio/topics/tracing
- `console-subscriber`: https://docs.rs/console-subscriber/latest/console_subscriber/
- `console-subscriber::Builder`: https://docs.rs/console-subscriber/latest/console_subscriber/struct.Builder.html
- `tracing`: https://docs.rs/tracing/latest/tracing/
- `metrics`: https://docs.rs/metrics/latest/metrics/
- `tokio-metrics`: https://docs.rs/tokio-metrics/latest/tokio_metrics/
- `tokio-metrics::RuntimeMonitor`: https://docs.rs/tokio-metrics/latest/tokio_metrics/struct.RuntimeMonitor.html
- `miette::JSONReportHandler`: https://docs.rs/miette/latest/miette/struct.JSONReportHandler.html
- `tracing-error::SpanTrace`: https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTrace.html
