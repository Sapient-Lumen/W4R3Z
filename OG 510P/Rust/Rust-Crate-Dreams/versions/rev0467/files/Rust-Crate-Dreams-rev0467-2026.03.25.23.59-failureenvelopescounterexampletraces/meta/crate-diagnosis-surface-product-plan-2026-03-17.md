# Crate diagnosis-surface product plan — 2026-03-17

This note exists to keep **P-0525 Crate Diagnosis Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing troubleshooting / symptom / self-check support contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0525** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which symptoms the crate officially recognizes,
- what a downstream user should inspect first,
- which self-checks the maintainer actually stands behind,
- which signals or diagnostic codes matter for each symptom,
- what evidence is safe to capture,
- and what changed between releases.

It should **not** try to become a hosted support portal, generic incident-management system, debugger replacement, or magical root-cause engine.
Those are adjacent imports, not the core product.

## What the crate should provide other people

For downstream users, the crate should provide:

1. **One official symptom vocabulary** instead of issue-thread folklore.
2. **Ordered first-inspection paths** so “what should I look at first?” has a reviewable answer.
3. **Maintainer-endorsed self-checks** instead of vague “turn on more logs” advice.
4. **Signal / code / warning linkage** so traces, metrics, runtime warnings, and diagnostic codes become usable support surfaces.
5. **Safe support bundles** with explicit redaction and opt-in boundaries.
6. **Release diffs** so troubleshooting support regressions become reviewable.
7. **A short human summary** that can be pasted into docs, issue templates, or release review.

For maintainers, the crate should provide:

1. a compact pack file that is cheap to review,
2. small receipts and reports rather than a giant support site,
3. a way to import existing tracing/metrics/error substrate instead of replacing it,
4. a conservative `manual_review_required` escape hatch,
5. and a release-review diff that makes support downgrades loud.

## Recommended `0.1` command surface

### `cargo diagnosis-surface init`
Create a starter `diagnosis-surface-pack.toml` by importing obvious candidates from:

- troubleshooting / FAQ docs,
- issue-template or support text already living in the repo,
- `miette`-style diagnostic codes and URLs when present,
- declared self-check or doctor entrypoints,
- and tracing / metrics / runtime-monitor signal names when explicitly configured.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` instead of guessed.

### `cargo diagnosis-surface check`
Run the local validation pass:

- do declared symptom classes parse,
- do self-check entrypoints still exist,
- do referenced traces, metrics, diagnostic codes, or runtime warnings resolve,
- do triage sequences stay coherent,
- do capture-policy rules parse and remain explicit,
- and which parts remain manual-review-only?

### `cargo diagnosis-surface triage <symptom>`
Render the receiver-facing “inspect first / inspect next / escalate with bundle” flow for one symptom.
This is the shortest path from machine-readable support metadata to something a human can act on.

### `cargo diagnosis-surface doctor`
Run declared self-checks for one symptom family and emit a conservative local result.
In `0.1`, this should prefer bounded config sanity, loopback probes, and runtime snapshots over clever host scraping.

### `cargo diagnosis-surface summary`
Render a short crate-level diagnosis summary for docs, release notes, or issue templates.
This should be boring enough to paste into support docs without a separate website.

### `cargo diagnosis-surface diff <old> <new>`
Compare two receipts or packs and classify:

- `symptom_added`
- `symptom_removed`
- `symptom_class_changed`
- `triage_sequence_changed`
- `signal_map_changed`
- `self_check_changed`
- `remediation_changed`
- `capture_policy_changed`
- `manual_review_required`

### `cargo diagnosis-surface bundle --symptom <name>`
Materialize one conservative support bundle recipe for a declared symptom.
In `0.1`, this should bias toward:

- config summaries,
- version fingerprints,
- filtered logs/traces,
- selected metrics snapshots,
- and explicit refusal when capture would exceed the declared safety boundary.

It should **not** behave like an unbounded host scraper.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `diagnosis_surface_model`
  - shared Rust types for packs, receipts, reports, triage steps, taxonomy profiles, and capture policy
- `diagnosis_surface_discovery`
  - import logic for troubleshooting docs, diagnostic codes, self-check entrypoints, and signal declarations
- `diagnosis_surface_check`
  - verification of signal references, self-check manifests, triage sequences, and capture policies
- `diagnosis_surface_bundle`
  - bundle manifests, markdown summary rendering, diffing, bundle-safety evaluation, and conservative capture adapters
- `cargo-diagnosis-surface`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core format is trusted:

- `diagnosis_surface_tracing`
- `diagnosis_surface_metrics`
- `diagnosis_surface_tokio_console`
- `diagnosis_surface_tokio_metrics`
- `diagnosis_surface_miette`
- `diagnosis_surface_tracing_error`

## `0.1` artifact set

The archive already has the right center of gravity.
`0.1` should revolve around these files:

- `diagnosis-surface-pack.toml`
- `symptom-catalog.receipt.json`
- `symptom-class.policy.json`
- `self-check.manifest.json`
- `signal-map.report.json`
- `triage-origin.receipt.json`
- `remediation-playbook.manifest.json`
- `support-capture.report.json`
- `bundle-safety.report.json`
- `diagnosis-check.report.json`
- `diagnosis-surface-diff.report.json`
- `diagnosis-summary.md`

This pass adds six more important artifacts:

- `symptom-taxonomy.profile.json` — aliases, ambiguity notes, automation levels, and “symptom is not root cause” discipline.
- `symptom-class.policy.json` — class-level meaning and explicit rules against pretending that a symptom bucket is already a proved root cause.
- `capture-policy.profile.json` — allowed capture classes, sensitivity levels, opt-in requirements, and redaction posture.
- `triage-sequence.manifest.json` — ordered “run this check / inspect this signal / capture this bundle / escalate now” flow for each recognized symptom.
- `triage-origin.receipt.json` — provenance for each triage step, so “inspect this first” can be traced back to docs, code, runtime warnings, or manual review.
- `bundle-safety.report.json` — concrete verdict on whether a declared support bundle stays inside the pack’s safety boundary.

Those files matter because diagnosis support becomes vague again if the archive only records symptoms and signals but not:

- how symptom classes are defined,
- where the first-inspection path came from,
- and whether the support bundle is actually safe to attach.

## Discovery order

A disciplined import order helps prevent platform creep and false confidence.

1. **Troubleshooting and FAQ docs** — likely where support guidance already leaks into prose.
2. **Structured diagnostic metadata** — `miette` codes, help text, and URLs when present.
3. **Self-check entrypoints** — dry runs, config sanity checks, loopback probes, “doctor” commands, and runtime snapshots.
4. **Tracing / metrics / warning surfaces** — declared spans, events, counters, gauges, histograms, runtime metrics, and tokio-console warning classes.
5. **Bundle capture adapters** — only the allow-listed evidence classes a crate explicitly supports.

The importer should prefer surfacing uncertainty over synthesizing false confidence.

## Symptom policy

The first implementation should treat **symptoms as first-class review objects** and keep them distinct from root-cause claims.

### What should count as a symptom in `0.1`

- `startup_stall`
- `request_hang`
- `retry_storm`
- `queue_growth`
- `idle_but_busy`
- `high_cpu`
- `auth_drift`
- `config_mismatch`
- `resource_exhaustion`
- `manual_review_required`

### What should *not* be auto-classified in `0.1`

- root-cause certainty such as “DNS is definitely broken” or “the scheduler is at fault”
- broad “the app is slow” labels without a crate-specific interpretation
- arbitrary regex mining over unrelated logs
- vendor-specific support-desk playbooks with no stable crate-owned vocabulary
- hidden ML ranking of likely causes

The taxonomy profile should be explicit, versioned, and diffable.
If a crate needs dozens of root-cause guesses to look useful, the diagnosis surface is probably overreaching.

## Capture policy

The first implementation should treat capture as an explicit allow-list, not an implementation convenience.

### What should be capturable in `0.1`

- config summaries
- selected logs and traces
- selected counters / gauges / histograms
- runtime snapshots explicitly declared as safe
- version and environment fingerprints that help support without exposing secrets

### What should *not* be captured automatically

- raw credentials or token-shaped strings
- whole environment dumps
- full request / response bodies unless explicitly declared safe
- arbitrary host files
- unrestricted network probes
- memory dumps or panic artifacts outside the declared policy

The capture policy should be explicit, versioned, diffable, and conservative by default.
If a maintainer has to over-collect to make diagnosis useful, the symptom contract is probably underspecified.

## Proving-ground archetypes

A worthy first implementation should prove itself against at least five archetypes:

1. **Async client crate**
   - `request_hang` versus `retry_storm`
   - traces, runtime metrics, tokio-console warnings, and loopback probes
2. **Worker / queue crate**
   - `queue_growth` versus `consumer_starvation`
   - gauges, histograms, and concurrency reduction guidance
3. **CLI crate**
   - `startup_stall` versus `config_mismatch`
   - dry-run, config-sanity, and bounded capture recipes
4. **SDK / service crate**
   - `auth_drift` versus `endpoint_mismatch`
   - diagnostic codes, support URLs, and safe redacted capture
5. **Embedded / device-aware crate**
   - host-only versus board-only diagnosis honesty
   - bundle recipes that stop at `manual_review_required` when hardware is unavoidable

If `0.1` cannot survive those five, the vocabulary is still too narrow.

## Adoption staircase

Do not require the ecosystem to jump to a fully automated support workflow at once.

### Stage 1 — import and annotate
- generate a starter pack
- let maintainers mark recognized symptoms and manual-review zones

### Stage 2 — local checks
- verify signal references, self-check paths, and capture-policy parseability
- keep symptom vocabulary explicit

### Stage 3 — triage and summary output
- render human-facing troubleshooting flows from the declared metadata
- keep symptom-to-signal order reviewable

### Stage 4 — release diffs
- compare current release versus previous release
- make support downgrades visible

### Stage 5 — optional runtime adapters
- import `tracing`, `metrics`, tokio-console, tokio-metrics, `miette`, and `tracing-error`
- remain adapter-first, not replacement-first

## What should wait until later

Leave these for later unless `0.1` proves cramped without them:

- hosted support portals
- full incident timelines
- automatic root-cause ranking engines
- registry-wide crawling of every crate’s symptom data
- debugger plugins / IDE panels
- fleet dashboards and backend storage
- issue deduplication or support-ticket automation platforms

## Good failure modes

The crate should fail conservatively.
Preferred failure behavior:

- unresolved signal reference → `manual_review_required`
- capture request exceeds declared policy → refuse and explain the boundary
- ambiguous symptom with no maintainer-owned taxonomy entry → `manual_review_required`
- runtime-only self-check on the wrong host/device class → explicit environment mismatch
- symptom disappeared between releases → `symptom_removed`

## Why this still looks worth building

The adjacent tools are real, which is exactly why this proposal now looks sharper rather than weaker.

- Rust’s own guidance explicitly calls for more supportive interfaces from crates.
- The 2025 survey still says docs and code are where people learn, while debugging remains a visible pain point.
- Tokio’s tracing guidance already explains structured spans and events.
- Tokio Console already provides runtime warnings and async-state views.
- `tokio-metrics` already exposes task and runtime metrics.
- `miette` already provides diagnostic codes, help text, and URLs.
- `tracing-error` already carries `SpanTrace` alongside errors.

That combination strengthens the case that the missing value is the **crate-authored troubleshooting contract above them**, not another attempt to replace them.

## Non-goals for `0.1`

- not a replacement for `tracing`, `metrics`, tokio-console, `miette`, or `tracing-error`
- not a hosted support portal
- not a generalized incident-management suite
- not a magical auto-remediator
- not a promise that every symptom can be diagnosed automatically on every machine

## Sources

- Rust vision-doc post: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026: https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Tokio tracing docs: https://tokio.rs/tokio/topics/tracing
- Tokio Console announcement: https://tokio.rs/blog/2021-12-announcing-tokio-console
- `console-subscriber` docs: https://docs.rs/console-subscriber/latest/console_subscriber/
- `tokio-metrics` docs: https://docs.rs/tokio-metrics/latest/tokio_metrics/
- `miette` docs: https://docs.rs/miette/latest/miette/
- `miette::Diagnostic` docs: https://docs.rs/miette/latest/miette/trait.Diagnostic.html
- `tracing-error` docs: https://docs.rs/tracing-error/latest/tracing_error/
- `tracing-error::TracedError` docs: https://docs.rs/tracing-error/latest/tracing_error/struct.TracedError.html
