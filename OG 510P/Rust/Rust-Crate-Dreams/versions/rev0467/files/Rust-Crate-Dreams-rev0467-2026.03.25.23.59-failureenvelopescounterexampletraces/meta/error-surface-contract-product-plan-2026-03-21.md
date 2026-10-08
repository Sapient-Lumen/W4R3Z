# Error Surface Contract Kit — product plan (2026-03-21)

This note sharpens **P-0533 Error Surface Contract Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0533** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to replace `thiserror`, become a universal reporting runtime, or standardize every error string in the Rust ecosystem.
It should provide one boring, reviewable **error-support contract** above today’s `std::error`, derive, context, report, and renderer substrate.

`0.1` should make four things first-class:

1. **error identity** — which public codes/classes are actually durable enough to automate against;
2. **audience mode** — which error surface is for end users, operators, developers, or machine readers;
3. **remediation surface** — whether a hint, retry path, workaround, or docs route is authoritative, speculative, or missing;
4. **sensitivity posture** — whether paths, snippets, user data, attachments, or backtraces are safe to expose.

## What `0.1` should provide other people

- one compact `error-identity.receipt.json`
- one compact `audience-mode.receipt.json`
- one compact `remediation-surface.report.json`
- one compact `sensitivity-posture.receipt.json`
- one compact `error-surface.summary.md`
- one compact `error-surface.diff.json`
- a portable support / release-review bundle

## Commands worth shipping first

- `cargo error-surface inspect`
- `cargo error-surface explain <code>`
- `cargo error-surface gate`
- `cargo error-surface diff`
- `cargo error-surface bundle`

## What to import, not reinvent

- `std::error::Error` identity/source/provide substrate
- `thiserror`-derived public error definitions when present
- `anyhow` application context layering when present
- `miette` diagnostic metadata such as codes/help/docs URLs when present
- `error-stack` attachments / context stack when present
- `snafu` report/backtrace/help posture when present

## Suggested `0.1` doctor warnings

- `public_error_has_no_stable_identity_receipt`
- `human_report_and_machine_payload_share_same_audience_claim`
- `hint_text_present_but_remediation_authority_missing`
- `backtrace_or_attachment_exposure_missing_sensitivity_receipt`
- `display_text_used_as_public_contract_without_code_or_policy`
- `docs_link_exists_but_error_code_route_is_unstable`
- `operator_only_detail_exposed_on_user_safe_surface`

## First proving-ground scenarios

1. **A public `thiserror` type has stable codes while local `anyhow` context remains intentionally unstable**
2. **A `miette` help string and docs URL do not automatically mean retryability or fix guidance exists**
3. **Human CLI rendering and machine JSON payloads must not share the same audience-mode receipt**
4. **`error-stack` attachments or backtraces require a sensitivity receipt before logs or bundles can claim user-safe export**

## What to leave for later

- automatic source-to-code extraction from arbitrary enum names
- framework-specific integrations for every web stack or RPC protocol
- localization policy beyond stable-code routing
- a global centralized registry of Rust error codes
- magical secret-detection beyond typed error/report posture
