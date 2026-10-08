---
id: P-0513
title: Crate Runtime Handoff Pack Kit — redacted runtime context, panic handoff receipts, and support-bundle diffs for library authors
status: idea
domains: [crates, diagnostics, dx, error-handling, panic, tracing, supportiveness, docs]
last_reviewed: 2026-03-17
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://doc.rust-lang.org/std/error/index.html
  - https://doc.rust-lang.org/std/error/trait.Error.html
  - https://doc.rust-lang.org/std/backtrace/index.html
  - https://doc.rust-lang.org/std/panic/fn.set_hook.html
  - https://doc.rust-lang.org/std/error/struct.Request.html
  - https://doc.rust-lang.org/beta/std/error/struct.Report.html
  - https://rust-lang.github.io/rfcs/3192-dyno.html
  - https://docs.rs/error-stack/latest/error_stack/
  - https://docs.rs/miette/latest/miette/struct.JSONReportHandler.html
  - https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTrace.html
  - https://docs.rs/human-panic/latest/human_panic/
  - https://docs.rs/color-eyre/latest/color_eyre/fn.install.html
  - https://docs.rs/color-eyre/latest/color_eyre/config/struct.HookBuilder.html
---

# Problem

The archive now has a much better story for **choosing crates** and for **compile-time guidance from crates**.
It still lacks a good answer to the next receiver-facing question:

> “Once the program has already failed at runtime, what exactly should the crate hand another person or tool?”

That gap matters because official Rust signals now line up around a sharper runtime-supportiveness problem.

The December 2025 vision-doc work says Rust should expand extensibility to cover **supportive interfaces** from crates.
The 2025 State of Rust survey says debugging remains a notable productivity problem, and that online documentation and studying code are still the main learning path.
That combination means runtime recovery is not merely an ops concern; it is part of the crate’s support surface.

Rust’s standard library now has meaningful substrate for runtime failure reporting:

- `std::error` explicitly frames `Result` + `Error` as the system for **anticipated runtime failure modes**,
- `Error::source()` is documented as the way to cross abstraction boundaries honestly,
- `std::backtrace` exists but capture is environment-controlled because it can be expensive,
- `std::panic::set_hook` lets applications customize panic reporting with payload and source location,
- and `std::error::Request` exists because generic runtime context like backtraces, suggestions, or environment-like state is useful across error boundaries.

But that substrate still does **not** give maintainers one boring workflow for questions like:

- which runtime facts should be captured when an error crosses a public boundary,
- which facts are exact captured values versus inferred summaries,
- which pieces are safe to hand to support or issue trackers by default,
- how panic-path reports and error-path reports differ,
- how async/logical context should be attached when stack traces are noisy,
- and how the crate’s runtime support surface changed across releases.

The worthy crate is therefore **not** another pretty error renderer and **not** another whole observability stack.
It is a **Crate Runtime Handoff Pack Kit**: a crate that helps maintainers author, test, redact, diff, and export the receiver-facing runtime failure material their crate gives other people.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What runtime facts does this crate promise to hand another person or tool after failure?**
2. **Which facts are exact captures, and which are maintainer-authored or inferred summaries?**
3. **What is safe to share by default, and what must be redacted or omitted?**
4. **What recovery step should a blocked user try next?**
5. **What changed in the runtime support surface across releases?**

That is more valuable than another custom formatter.

See `meta/crate-runtime-handoff-product-plan-2026-03-17.md` for the current `0.1` build sketch; it sharpens the lane around **capture exactness**, **share safety**, and **handoff fidelity** instead of flattening everything into a vague "helpful crash report" story.

# What it provides

- `runtime-handoff.pack.toml` — versioned declaration of failure classes, capture promises, redaction defaults, and recovery-step anchors.
- `runtime-context.receipt.json` — observed runtime error receipt: error class, source-chain shape, backtrace status, context attachments, and evidence class.
- `panic-handoff.receipt.json` — panic-path receipt: location, payload class, hook mode, report-file path if any, and redaction notes.
- `recovery-step.manifest.json` — the smallest supported next steps after common runtime failures.
- `redaction-profile.toml` — fields, patterns, and classes that are safe, unsafe, hashed, or omitted-by-default.
- `capture-exactness.policy.json` — states whether a field is an exact capture, an exact capture with redaction, a maintainer summary, an inferred summary, or still manual-review-only.
- `share-safety.receipt.json` — records whether each field is safe, local-only, hashed, truncated, omitted, or manual-review territory, and where that classification came from.
- `handoff-fidelity.report.json` — records how complete a post-failure bundle really is across error-chain capture, backtrace/span context, panic receipts, redaction application, and recovery-step linkage.
- `runtime-handoff-check.report.json` — verifies that fixtures still capture the promised facts and respect redaction policy.
- `failure-shape-diff.report.json` — compares two releases and classifies `capture_added`, `capture_removed`, `redaction_changed`, `panic_path_changed`, `recovery_step_changed`, and `manual_review_required`.
- `handoff.summary.md` — short human-facing explanation of what the crate can safely hand off on runtime failure.
- `cargo runtime-handoff capture` — capture one runtime handoff bundle from fixtures or sample runs.
- `cargo runtime-handoff check` — verify the pack against fixtures and golden redaction expectations.
- `cargo runtime-handoff diff <old> <new>` — show how the support surface changed.
- `cargo runtime-handoff summary` — render the user-facing summary from the pack.

# What the crate should provide other people

1. **A receiver-facing runtime support contract** above ad hoc logs, screenshots, and “please rerun with env var X” folklore.
2. **A redacted support bundle** that can be shared without making maintainers improvise privacy policy in issue comments.
3. **A joined error + panic handoff story** that stays honest about which path produced which receipt.
4. **A runtime recovery manifest** that turns “it crashed” or “it returned an error” into “here is the next supported step”.
5. **A diffable runtime support surface** so maintainers can review whether a release became easier or harder to debug safely.
6. **Importable runtime-support vocabulary** for docs portals, issue templates, support bots, and pathfinder-style tools.

# Persona / who it’s for

- library authors whose public APIs return rich runtime errors
- framework maintainers whose users regularly file “works locally / fails in prod” issues
- CLI maintainers who want panic reports that are useful but privacy-honest
- async library authors who need logical context, not only executor backtraces
- app teams maintaining internal foundational crates with support obligations

# Users & user stories

- **Library maintainer**: “Prove that our public errors always hand downstream users a stable error code, source-chain shape, and safe troubleshooting note.”
- **Async maintainer**: “Capture logical span context when runtime stack traces are noisy, and verify we do not leak secrets.”
- **CLI maintainer**: “When a panic happens, emit a redactable report that a user can actually attach to a bug report.”
- **Support engineer**: “Compare two failure bundles and tell whether the support surface changed or the user environment changed.”
- **Docs/tool author**: “Import machine-readable runtime recovery steps rather than scraping issue templates and README troubleshooting prose.”

# Prior art (and why it’s insufficient)

- `std::error` explicitly covers anticipated runtime failure modes.
- `Error::source()` already gives an abstraction-boundary story for nested runtime errors.
- `std::backtrace` offers standard backtraces, but capture is gated by environment variables because of runtime cost.
- `std::panic::set_hook` lets authors customize panic reporting with payload and location.
- `std::error::Request` and RFC 3192 show pressure for richer typed runtime context such as backtraces, runtime state, environment facts, and help-text suggestions.
- `std::error::Report` exists on nightly, but is still an experimental report surface rather than a stable crate-author workflow.
- `error-stack` captures contexts and arbitrary attachments as errors propagate.
- `miette` can render machine-readable JSON reports.
- `tracing-error` captures `SpanTrace`, which can be more informative than raw stack backtraces in async code, and `SpanTraceStatus` makes unsupported-versus-empty status explicit.
- `human-panic` can generate a user-submittable crash report file and explicitly frames privacy as user-consent-based.
- `color-eyre` can install panic/error report hooks early and attach support-oriented custom panic sections or issue-reporting metadata.

What remains missing is a **crate-authored runtime handoff workflow** above those pieces:

- author one runtime support contract,
- capture it against fixtures,
- classify redaction and exactness,
- export stable receipts,
- and diff the handoff surface over time.

# Design goals

1. **Receiver-facing runtime support first** — optimize for the person or tool receiving a failure handoff, not just the code emitting it.
2. **Redaction-first honesty** — every field should be classed as safe, sensitive, hashed, omitted, or manual-review.
3. **Exact versus inferred honesty** — distinguish captured runtime facts from maintainer-authored summaries or heuristics.
4. **Error-path and panic-path separation** — keep recoverable-error receipts and panic receipts visibly distinct.
5. **Async-aware context import** — allow logical span context and request IDs without pretending stack traces always tell the truth.
6. **Adapter-friendly** — compose with `error-stack`, `miette`, `tracing-error`, `human-panic`, and future `std` surfaces instead of replacing them.
7. **Narrow enough to ship** — start with capture/redaction/check/diff before incident portals, telemetry backends, or hosted support systems.

# MVP surface

- Minimal types: `RuntimeHandoffPack`, `RuntimeFailureCase`, `RuntimeContextReceipt`, `PanicHandoffReceipt`, `RedactionProfile`, `RuntimeHandoffCheckReport`, `FailureShapeDiffReport`, `HandoffSummary`
- Minimal functions:
  - `load_runtime_handoff_pack()`
  - `capture_runtime_context_receipt()`
  - `capture_panic_handoff_receipt()`
  - `apply_redaction_profile()`
  - `check_runtime_handoff_cases()`
  - `diff_failure_shapes()`
  - `render_handoff_summary()`
- Feature flags:
  - `serde`
  - `cargo`
  - `backtrace`
  - `panic-hook`
  - `tracing`
  - `markdown`

# Compatibility story

- Works above `std::error`, `std::backtrace`, and `std::panic` rather than replacing them.
- Must stay useful even when no backtrace is available, because backtrace capture may be disabled or too expensive.
- Must preserve whether a runtime fact came from exact error attachments, a panic hook, span context, or maintainer-authored recovery notes.
- Should interoperate with renderer crates and issue/report tooling by exporting small machine-readable artifacts.
- Must remain honest when a crate’s runtime support surface is incomplete and still requires manual review or application-local instrumentation.

# 0.1 failure families

1. `runtime_error_chain`
   - expected source-chain capture, public error code/class, and backtrace status
   - recovery step points to the smallest supported next action
2. `async_logical_context`
   - optional span-trace or request-context capture when executor stacks are noisy
   - receipt must say `captured`, `empty`, or `unsupported`
3. `panic_user_report`
   - expected panic location/payload classification and report-file handoff if configured
   - receipt must distinguish default-hook passthrough vs custom hook behavior
4. `config_or_environment_mismatch`
   - expected safe environment/config receipt with explicit redaction classes
   - recovery step points to the smallest valid config repair
5. `manual_review_required`
   - app- or org-specific fields that are intentionally not auto-exported

# Conformance & fixtures

- one error-chain fixture with explicit source-boundary and backtrace-status expectations
- one async span-context fixture with `captured`, `empty`, and `unsupported` cases
- one panic-hook fixture that emits a redactable report artifact
- one config/environment mismatch fixture proving secrets are omitted or hashed
- goldens for `capture_present`, `capture_missing`, `redaction_violation`, `recovery_step_missing`, `panic_hook_drift`, and `manual_review_required`

# Path to boring stability

- Stabilize the pack/capture/check/diff schemas before adding adapters for many error libraries.
- Start with local fixture-driven capture before hosted report collection or remote support flows.
- Treat panic receipts and error receipts as separate artifact families even if a UI later presents them together.
- Keep privacy defaults conservative and explicit.
- Add richer adapters only after the base exactness/redaction vocabulary proves useful.

# Why this could matter

This is the crate that would let maintainers say:

- “When our crate fails at runtime, here is exactly what we hand other people.”
- “Here is what is safe to share.”
- “Here is how panic reports differ from ordinary errors.”
- “Here is the next supported recovery step.”
- “Here is how the runtime support surface changed since the last release.”

That is the kind of boring supportiveness layer that makes Rust feel more usable in real systems.

# Why now

1. The official vision-doc work now names **supportive interfaces from crates** as a missing extensibility frontier.
2. The 2025 survey still reports debugging as a meaningful productivity pain, while docs and source remain the main learning path.
3. The `std` substrate for runtime failure reporting is real, but still fragmented across `Error`, backtraces, and panic hooks.
4. The RFC trail around generic member access shows there is demand for richer typed runtime context without exploding traits with ad hoc methods.
5. Existing crates already prove the pieces are useful; what is missing is the maintainer-facing pack/check/redact/diff workflow.

# Sharp edges / open questions

- Which capture facts deserve stable field names versus free-form attachments?
- How should hashed redaction classes be represented so diffs remain useful without leaking raw values?
- How much runtime fixture execution is acceptable before this drifts into a heavy test harness?
- Which recovery-step anchors should be local docs versus external docs URLs?
- How should no-std or embedded panic paths be represented in a later extension without overfitting the first release?

# Suggested 0.1 deliverable

A crate and cargo subcommand that load one `runtime-handoff.pack.toml`, run a tiny fixture set that exercises error and panic paths, apply a redaction profile, and emit:

- one `runtime-context.receipt.json`,
- one `panic-handoff.receipt.json`,
- one `runtime-handoff-check.report.json`,
- one `failure-shape-diff.report.json`,
- and one short `handoff.summary.md`.

That would already be enough to prove the lane is real.

# Adoption plan

1. Start with crate authors who already use `error-stack`, `miette`, `tracing-error`, or custom panic hooks.
2. Publish tiny example packs for one library crate, one async service crate, and one CLI crate.
3. Add issue-template and docs-portal integrations only after the core receipt schemas stabilize.
4. Encourage downstream tooling to consume the exported vocabulary instead of scraping prose.
5. Keep a public fixture corpus for runtime error-chain, async-context, panic-report, and redaction cases.

# Non-goals

- Not a hosted crash-report collector.
- Not a full observability backend.
- Not a generic terminal renderer.
- Not a replacement for tracing, logging, or metrics.
- Not a guarantee that every runtime failure can be auto-diagnosed.
- Not a privacy waiver for collecting arbitrary runtime context.

# Relationship to other proposals in this archive

- **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** answers **which crate to choose**.
- **P-0510 Crate Capability Contract & Interop Profile Kit** answers **what a crate claims to support**.
- **P-0511 Crate Interop Profile Pack Kit** answers **what shared ecosystem profile a crate fits**.
- **P-0512 Crate Guidance Pack Kit** answers **what compile-time / early failure guidance a chosen crate gives**.
- **P-0513** answers **what runtime failure material the chosen crate hands off after the program has already failed**.

That separation should remain explicit.

# Sources

- Rust vision-doc post on supportiveness, crate guidance, and ecosystem orientation: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `std::error` module docs: https://doc.rust-lang.org/std/error/index.html
- `std::error::Error` docs: https://doc.rust-lang.org/std/error/trait.Error.html
- `std::backtrace` docs: https://doc.rust-lang.org/std/backtrace/index.html
- `std::panic::set_hook` docs: https://doc.rust-lang.org/std/panic/fn.set_hook.html
- `std::error::Request` docs: https://doc.rust-lang.org/std/error/struct.Request.html
- nightly `std::error::Report` docs: https://doc.rust-lang.org/beta/std/error/struct.Report.html
- RFC 3192 / dyno generic member access background: https://rust-lang.github.io/rfcs/3192-dyno.html
- `error-stack` docs: https://docs.rs/error-stack/latest/error_stack/
- `miette` JSON report handler docs: https://docs.rs/miette/latest/miette/struct.JSONReportHandler.html
- `tracing-error` SpanTrace docs: https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTrace.html
- `human-panic` docs: https://docs.rs/crate/human-panic/latest
