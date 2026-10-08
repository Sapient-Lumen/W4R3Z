# error-surface-contract-kit lane boundaries — 2026-03-21

This note keeps **P-0533 Error Surface Contract Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable error-support contract** over one exported error surface.
It should answer:

- which identities/codes are public and stable,
- which audience each rendered or serialized surface is meant for,
- whether remediation/help is authoritative or ornamental,
- and whether the surface is safe to export without redaction.

## Keep this distinct from nearby lanes

### Distinct from `P-0004 diagnostic-kit`

`P-0004` is about diagnostic data models and renderer ergonomics.
`P-0533` is about what an error surface **promises** to receivers.

### Distinct from `P-0531 cli-surface-contract-kit`

`P-0531` is about command/output/terminal/exit behavior.
`P-0533` is about the meaning, actionability, and safety of the error itself.

### Distinct from `P-0525 crate-diagnosis-surface-pack-kit`

`P-0525` is about first-diagnosis workflow, self-check order, and troubleshooting bundles.
`P-0533` is about steady-state error identity, audience, remediation, and exposure posture.

### Distinct from generic secrets/redaction policy crates

This lane is not:

- another secrets-management crate,
- another structured-logging policy engine,
- or a universal PII classifier.

It should stay specific to **error/report exposure posture**.

## Four truths this lane must keep separate

1. **error identity** — public code/class compatibility and mapping basis;
2. **audience mode** — user, operator, developer, or machine-reader surface;
3. **remediation surface** — authoritative next steps versus helpful but non-binding prose;
4. **sensitivity posture** — what details may appear and whether export is safe.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- a derived public error type and a stable public error code contract,
- pretty terminal help text and actual retry/fix guidance,
- top-level `Display` output and machine-facing error identity,
- a rich report with backtrace/attachments and a safe-to-share report,
- docs links and compatibility promises.

## Preferred artifact vocabulary

- `error-identity.receipt`
- `audience-mode.receipt`
- `remediation-surface.report`
- `sensitivity-posture.receipt`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
