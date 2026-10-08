# Crate runtime-handoff product plan — 2026-03-17

This note exists to keep **P-0513 Crate Runtime Handoff Pack Kit** disciplined.
The archive already decided that the missing value is a **crate-authored runtime failure handoff contract** above generic error, panic, tracing, and report-rendering substrate.
This pass answers a narrower question:

> If somebody actually started building **P-0513** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which runtime failure classes the crate intentionally hands off,
- which fields are exact captures versus maintainer summaries or heuristics,
- which fields are safe to share, hashed, truncated, omitted, or manual-review-only,
- which parts of the bundle came from ordinary error paths versus panic hooks,
- how much fidelity a given handoff bundle really has,
- and what changed between releases.

It should **not** try to become a hosted crash collector, a generic error renderer, a full tracing backend, or a universal incident-management platform.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, support engineers, docs/tool authors, and maintainers, the crate should provide:

1. **One compact runtime-handoff contract** instead of ad hoc screenshots, log snippets, support-template prose, and “rerun with env var X” folklore.
2. **Capture-exactness policy** so `exact_capture`, `exact_capture_with_redaction`, `maintainer_summary`, `inferred_summary`, `sampled_capture`, and `manual_review_required` stop being implicit vibes.
3. **Share-safety receipts** so each important field says whether it is safe by default, local-only, hashed for support, truncated, omitted, or still manual-review territory.
4. **Distinct error-path and panic-path receipts** so support bundles stay honest about how they were produced.
5. **Handoff-fidelity reports** so teams can see whether a bundle includes only an error chain, includes backtrace/span context, includes a panic-report artifact, or still lacks witness evidence.
6. **Recovery-step manifests** so a blocked user can see the smallest supported next action after a runtime failure.
7. **Release-to-release diffs** so runtime support regressions become reviewable like API drift.
8. **A small portable bundle** that issue templates, docs portals, support bots, and CI can all import.

For maintainers, the crate should provide:

1. a compact pack file that is cheap to review,
2. conservative `manual_review_required` escape hatches instead of fake certainty,
3. a way to import panic-hook, error, span-trace, and attachment facts instead of replacing them,
4. one place to state what is safe to hand off publicly,
5. and a CI gate for “this release changed what support receives after failure.”

## Recommended `0.1` command surface

### `cargo runtime-handoff init`
Create a starter `runtime-handoff.pack.toml` from either:

- a minimal maintainer-authored seed,
- imported adapter hints from selected libraries,
- or an existing handoff pack.

The generated pack should stay intentionally narrow.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo runtime-handoff capture`
Emit one normalized runtime handoff bundle from fixtures or sample runs.
This should capture:

- failure class,
- error-chain shape,
- backtrace and span-trace status,
- panic location / payload class when relevant,
- report-file path or issue-url facts when present,
- redaction outcomes,
- and maintainer-authored recovery notes.

### `cargo runtime-handoff check`
Run the local validation pass:

- does the pack parse,
- do declared recovery steps still resolve,
- do fixtures still emit the promised handoff facts,
- do redaction policies actually remove or hash the intended values,
- and which fields remain inferred-only or manual-review-only?

### `cargo runtime-handoff doctor`
Render human-facing warnings for suspicious situations such as:

- `panic_hook_present_but_report_bundle_path_missing`
- `spantrace_declared_but_error_layer_missing`
- `error_attachment_present_but_share_safety_unclassified`
- `recovery_step_missing_for_public_error_class`
- `redaction_profile_hashes_value_but_summary_still_leaks_raw_text`
- `panic_payload_class_unknown`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo runtime-handoff summary`
Render a short receiver-facing note that answers:

- which runtime failure classes are intentionally handed off,
- which fields are exact versus summarized,
- what is safe to share by default,
- what extra runtime context may appear,
- and where manual review still begins.

### `cargo runtime-handoff diff <old> <new>`
Compare two receipts or packs and classify:

- `capture_exactness_changed`
- `share_safety_changed`
- `error_chain_surface_changed`
- `panic_path_changed`
- `report_artifact_path_changed`
- `recovery_step_changed`
- `handoff_fidelity_changed`
- `manual_review_boundary_changed`

### `cargo runtime-handoff pack`
Emit one compact `.runtimehandoff.zip` bundle for CI artifacts, support handoff, docs generation, and release review.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `runtime_handoff_model`
  - shared Rust types for packs, receipts, reports, redaction classes, and diffs
- `runtime_handoff_capture`
  - error/panic/span-context import logic and adapter shims
- `runtime_handoff_check`
  - redaction verification, recovery-step validation, fidelity classification, and doctor warnings
- `runtime_handoff_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-runtime-handoff`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `runtime_handoff_error_stack`
- `runtime_handoff_tracing_error`
- `runtime_handoff_human_panic`
- `runtime_handoff_color_eyre`
- `runtime_handoff_miette`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should still revolve around:

- `runtime-handoff.pack.toml`
- `runtime-context.receipt.json`
- `panic-handoff.receipt.json`
- `redaction-profile.toml`
- `runtime-handoff-check.report.json`
- `failure-shape-diff.report.json`
- `handoff.summary.md`

This pass adds three more important artifacts:

- `capture-exactness.policy.json` — what `exact_capture`, `exact_capture_with_redaction`, `maintainer_summary`, `inferred_summary`, `sampled_capture`, and `manual_review_required` mean and what minimum evidence each class expects.
- `share-safety.receipt.json` — where fields came from and whether they are safe, local-only, hashed, truncated, omitted, or still manual-review territory.
- `handoff-fidelity.report.json` — how complete a handoff bundle really is across error-chain capture, backtrace/span-trace presence, panic receipts, artifact paths, redaction application, and recovery-step linkage.

Those files matter because runtime support stories get vague again if the archive only records that “a report exists” but not:

- how exact the captured facts really are,
- which parts are actually safe to share,
- and how complete a given handoff bundle really was.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Direct runtime facts**
   - error class / code
   - source-chain shape
   - panic location / payload class
2. **Context facts**
   - backtrace status
   - span-trace status
   - explicit attachments
3. **Artifact facts**
   - report-file path
   - issue-url or support-bundle location
   - log / json report references
4. **Redaction facts**
   - field class
   - hash/truncate/omit policy
   - post-redaction witness
5. **Recovery facts**
   - minimal supported next step
   - docs anchor or recipe reference
6. **Manual-review zones**
   - organization-specific fields
   - app-local incident context
   - support-only metadata not safe for public export

The importer should prefer visible uncertainty over synthesis.

## Capture-exactness policy

The first implementation should treat **capture exactness** as a first-class review object and keep it separate from raw field presence.

### What should count as capture-exactness classes in `0.1`

- `exact_capture`
- `exact_capture_with_redaction`
- `maintainer_summary`
- `inferred_summary`
- `sampled_capture`
- `manual_review_required`

### What should *not* count as exact capture in `0.1`

- “the panic hook probably had this information”
- “the tracing stack was enabled somewhere”
- “support usually asks users for this field manually”
- “the report renderer prints something similar”

## Share-safety policy

The first implementation should treat **share safety** as explicit review material.
A good `0.1` should model classes such as:

- `safe_by_default`
- `safe_if_local_only`
- `hashed_for_support`
- `truncated_for_support`
- `omitted_by_default`
- `manual_review_required`

with origins such as:

- `error_attachment_observed`
- `panic_hook_observed`
- `span_context_observed`
- `report_file_observed`
- `redaction_policy_declared`
- `maintainer_declared`
- `manual_review_required`

If a field is only known safe because a maintainer said so, the receipt should say so.
`0.1` should prefer “this value was hashed for support” over pretending the raw value is safe to publish.

## Handoff-fidelity policy

The first implementation should treat **handoff completeness** as a first-class review object.
A good `0.1` should model fidelity classes such as:

- `error_chain_only`
- `error_plus_backtrace`
- `error_plus_span_context`
- `panic_receipt_only`
- `runtime_bundle_complete`
- `sampled_fixture_only`
- `manual_review_required`

with checked dimensions such as:

- `error_code_or_class`
- `source_chain`
- `backtrace_status`
- `spantrace_status`
- `panic_location`
- `panic_payload_class`
- `report_artifact_path`
- `redaction_applied`
- `recovery_step_linked`
- `manual_review_boundary_recorded`

If a bundle lacks a report-file path, lacks span context, or only exercised one fixture lane, that should lower fidelity rather than staying hidden.

## Recommended proving grounds

The best early proving grounds are crates that already expose some runtime-support substrate but still leave the final handoff story scattered:

1. **CLI tools** using panic hooks or user-facing report handlers.
2. **Async services** where span traces can be more useful than stack traces.
3. **Library crates** using `error-stack`-style attachments or layered context.
4. **Framework crates** with public runtime error classes but inconsistent support-template guidance.
5. **Privacy-sensitive applications** where raw config/env/user identifiers must not leak into support bundles.

## `0.1` scenario families

The archive should keep stressing the lane with small scenarios such as:

- `error_chain_runtime_context`
- `async_span_handoff`
- `panic_report_redaction`
- `error_stack_attachment_secret_needs_hash_redaction`
- `spantrace_declared_but_error_layer_missing`
- `panic_hook_present_but_report_bundle_path_missing`

The point is not to capture every runtime failure shape.
The point is to force the first artifact vocabulary to be honest about exactness, share safety, and completeness.

## Adoption plan

1. Start with crate authors who already use `error-stack`, `tracing-error`, `human-panic`, `color-eyre`, or custom panic hooks.
2. Publish tiny example packs for one library crate, one async service crate, and one CLI crate.
3. Encourage issue templates and docs portals to import the structured bundle instead of asking for arbitrary screenshots.
4. Keep privacy defaults conservative until field-class vocabularies prove stable.
5. Add richer adapters only after the base exactness/share-safety/fidelity vocabulary survives real review.

## What to keep separate

- Keep **P-0513** separate from compile-time guidance (**P-0512**).
- Keep **P-0513** separate from generic error renderers and pretty reports.
- Keep **P-0513** separate from full tracing / observability platforms.
- Keep **P-0513** separate from domain-specific incident or replay bundles.
- Keep **P-0513** separate from crate off-ramp / upgrade support.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/std/error/index.html
- https://doc.rust-lang.org/std/error/trait.Error.html
- https://doc.rust-lang.org/std/backtrace/index.html
- https://doc.rust-lang.org/std/panic/fn.set_hook.html
- https://docs.rs/error-stack/latest/error_stack/
- https://docs.rs/error-stack/latest/error_stack/struct.Report.html
- https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTrace.html
- https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTraceStatus.html
- https://docs.rs/human-panic/latest/human_panic/
- https://docs.rs/color-eyre/latest/color_eyre/fn.install.html
- https://docs.rs/color-eyre/latest/color_eyre/config/struct.HookBuilder.html
