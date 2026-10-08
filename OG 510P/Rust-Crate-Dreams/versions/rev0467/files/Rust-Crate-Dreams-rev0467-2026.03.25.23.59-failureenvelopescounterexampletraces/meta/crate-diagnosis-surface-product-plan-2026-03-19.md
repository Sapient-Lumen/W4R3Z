# Crate diagnosis-surface product plan — 2026-03-19

This note exists to keep **P-0525 Crate Diagnosis Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing troubleshooting contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0525** this week, what should version `0.1` look like, what should it provide other people, and what details make it meaningfully better than “just emit more logs”?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which symptoms the crate officially recognizes,
- which symptom buckets are aliases rather than root causes,
- which self-checks or “doctor” actions are actually supported,
- which traces, metrics, warnings, runtime metrics, or diagnostic codes matter first,
- whether an advertised console/tracing/metrics path is really supported,
- which support bundle is safe to attach,
- and what changed between releases.

It should **not** try to become a new telemetry backend, a new debugger, a new hosted support desk, or an automatic root-cause engine.
Those are adjacent imports, not the product.

## Why this is better timed now

This lane is more credible in March 2026 because the live substrate is now strong enough to support a boring contract layer above it:

- the Rust vision-doc work now explicitly asks for **supportive interfaces from crates**;
- the 2025 State of Rust survey still shows debugging as a meaningful productivity problem while docs and code stay the main learning surfaces;
- the 2026 debugging survey still highlights async debugging, visualizers, debugger/OS variability, and expression-evaluation gaps;
- Tokio’s tracing docs now present tracing as the path to logging, collectors, profiling, and **debugging with Tokio Console**;
- `console-subscriber` now makes the easy path very clear: it only works if the runtime emits compatible tracing events;
- `tokio-metrics` already exposes interval runtime/task metrics rather than forcing each crate to invent its own counters;
- `miette::Diagnostic` already gives crates stable **code / help / url** hooks for user-facing diagnosis vocabulary, and `JSONReportHandler` already makes structured rendering plausible;
- `tracing-error::SpanTrace` already preserves logical async context that ordinary backtraces often lose.

That means the missing crate is no longer “support Rust diagnostics somehow”.
The sharper missing crate is a **crate-authored promise** above the substrate.

## What the crate should provide other people

For downstream users, release reviewers, and support/tool authors, the crate should provide:

1. **One compact symptom contract** instead of folklore scattered across README notes, issue templates, log-filter snippets, and maintainer memory.
2. **A first-inspection order** so users know what to check before they escalate.
3. **Instrumentation honesty** so “use Tokio Console” or “inspect runtime metrics” only appears when the crate/runtime actually supports that path.
4. **Safe support bundles** with explicit redaction or block rules instead of “attach everything you can find”.
5. **Stable diagnosis vocabulary** with codes/aliases/manual-review boundaries that docs portals or bots can import.
6. **A release diff** that makes support regressions loud when symptoms, checks, or capture rules change.
7. **A short human summary** that can be pasted into docs, issue templates, release notes, or dependency-adoption review.

For maintainers, the crate should provide:

1. a small policy file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake confidence,
3. one place to declare self-checks, signal maps, and bundle rules,
4. one place to record runtime / target / board-only support limits,
5. and a CI gate for “this release changed the diagnosis surface”.

## Recommended `0.1` command surface

### `cargo diagnosis-surface init`
Create a starter `diagnosis-surface-pack.toml` by importing obvious candidates from:

- documented symptom names,
- README / guide troubleshooting sections,
- `miette` diagnostic codes or help URLs,
- declared tracing / metrics / console guidance,
- and maintainer-declared self-check entrypoints.

The generated pack should be incomplete on purpose.
Anything uncertain should become `manual_review_required` rather than guessed.

### `cargo diagnosis-surface check`
Run the local validation pass:

- do symptom classes parse,
- do aliases collide incorrectly,
- do triage steps reference known checks/signals,
- does any console/tracing/metrics guidance require compatibility that is not witnessed,
- do support bundles stay within the declared capture policy,
- and which parts remain manual-review-only?

### `cargo diagnosis-surface doctor <symptom>`
Render the ordered first-inspection path for one symptom.
A good doctor output answers:

- what the symptom means,
- which check to run first,
- which signal to inspect next,
- when a broad timeout bucket should be split into a narrower path,
- and when escalation requires a capture bundle.

### `cargo diagnosis-surface capture <symptom>`
Emit one support bundle according to the declared policy.
It must keep:

- capture classes,
- opt-in posture,
- redaction profile,
- blocked classes,
- and `manual_review_required`

explicit in the output.

### `cargo diagnosis-surface diff <old> <new>`
Compare two diagnosis surfaces and classify:

- `symptom_added`
- `symptom_removed`
- `triage_order_changed`
- `signal_map_changed`
- `self_check_changed`
- `capture_policy_changed`
- `bundle_safety_changed`
- `instrumentation_support_changed`
- `manual_review_boundary_changed`

### `cargo diagnosis-surface pack`
Emit one compact `.diagnosissurface.zip` bundle for PR review, dependency review, support handoff, or issue-template attachment.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `diagnosis_surface_model`
  - Rust types for symptom packs, triage flows, signal maps, capture reports, safety reports, and diffs
- `diagnosis_surface_discovery`
  - import logic for docs, `miette` codes/help/urls, and declared tracing/metrics guidance
- `diagnosis_surface_check`
  - policy validation, instrumentation-honesty checks, and bundle-safety checks
- `diagnosis_surface_render`
  - short summaries, doctor output, and markdown rendering
- `diagnosis_surface_pack`
  - diffing, zip emission, and bundle assembly
- `cargo-diagnosis-surface`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `diagnosis_surface_miette`
- `diagnosis_surface_tracing`
- `diagnosis_surface_console`
- `diagnosis_surface_tokio_metrics`
- `diagnosis_surface_metrics`

## `0.1` artifact set

`0.1` should revolve around these files:

- `symptom-taxonomy.profile.json`
- `symptom-class.policy.json`
- `triage-sequence.manifest.json`
- `triage-origin.receipt.json`
- `signal-map.report.json`
- `self-check.manifest.json`
- `support-capture.report.json`
- `bundle-safety.report.json`
- `remediation-playbook.manifest.json`
- `diagnosis-check.report.json`
- `diagnosis-surface-diff.report.json`
- `diagnosis-summary.md`

The key move in this pass is to make **instrumentation honesty** and **bundle safety** first-class review objects.
The crate should be able to say things like:

- “Tokio Console is documented, but runtime compatibility is not witnessed, so that triage step downgrades to manual review.”
- “Runtime metrics exist, but they are interval snapshots and should not be interpreted as timeless state.”
- “A config summary bundle is allowed after redaction, but a runtime snapshot remains blocked because it may contain credentials.”

Without those review objects, a diagnosis surface quickly turns back into folklore.

## Proving-ground archetypes

A worthy first implementation should prove itself against at least five archetypes:

1. **Retry storm client**
   - separate retry amplification from endpoint mismatch and auth drift
2. **Queue-growth worker**
   - separate backlog growth from scheduler starvation and external broker lag
3. **Local CLI startup stall**
   - keep dry-run/config-summary/version-fingerprint capture boring and safe
4. **Console recipe declared but runtime not instrumented**
   - downgrade false confidence when console guidance is not actually supported
5. **Bundle capture exports secret-shaped env**
   - keep support-capture boundaries conservative and reviewable

If `0.1` cannot survive those five, the product vocabulary is still too vague.

## What should wait until later

Leave these for later unless `0.1` proves cramped without them:

- automatic root-cause inference,
- hosted dashboards or support portals,
- automatic runtime scraping across arbitrary hosts,
- remote support-session orchestration,
- and broad observability schema governance that belongs in adjacent lanes.

## Working rule

When future revisions touch **P-0525**, prefer adding:

- more precise symptom meaning,
- stronger first-inspection order,
- clearer instrumentation-compatibility receipts,
- safer bundle examples,
- and release-diff evidence

before inventing another neighboring support crate.
