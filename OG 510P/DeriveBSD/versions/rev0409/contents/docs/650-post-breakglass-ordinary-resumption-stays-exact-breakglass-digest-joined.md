# Post-breakglass ordinary resumption stays exact-breakglass-digest joined

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt

The archive already decided that breakglass is explicit and non-sticky:
ordinary secret and workload-identity lanes must use a fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`.

What still needed one more small hard decision was the phrase **relevant breakglass receipt** itself.
If the consuming receipt stays silent, implementations drift back toward “latest breakglass wins”, host-history scans, or dashboard folklore.

Related:
- ADR: `adrs/ADR-0240-post-breakglass-ordinary-resumption-stays-exact-breakglass-digest-joined.md`
- prior resumption boundary: `docs/649-breakglass-does-not-silently-reopen-ordinary-attestation-gated-authority.md`
- consuming attestation tuple: `docs/645-attestation-consuming-action-receipts-pin-the-exact-decision-tuple.md`
- pinned verdict mirror: `docs/648-attestation-consuming-action-receipts-carry-the-exact-pinned-attestation-verdict.md`

## The boundary

When breakglass materially gated or explained a later ordinary attestation-gated authority decision, the ordinary consuming receipt now carries:

- `attestation_verification.relevant_breakglass_receipt_digest`

That field means:

- the consuming receipt names the exact `breakglass.receipt` whose `created_at` formed the resumption barrier,
- detached tooling can compare the joined breakglass `created_at` with the pinned `attestation.receipt` timestamp,
- and implementations do **not** get to rediscover the governing emergency session from dashboards, host history, or “latest breakglass for this host” resolver rules.

## Why this matters

### 1) It removes another hidden resolver

Requiring fresh post-breakglass attestation is not enough if responders still need a service database to know which breakglass session counted.
The exact digest join keeps the ordinary authority story portable.

### 2) It keeps repeated emergency recovery auditable

Hosts can accumulate multiple breakglass sessions over time.
An exact `relevant_breakglass_receipt_digest` keeps later ordinary secret/identity decisions tied to the right emergency crossing instead of whichever session an implementation happens to pick.

### 3) It stays small

This does not invent a new resumption catalog, session index, or denial subsystem.
It only makes one exact join explicit where the archive was still implying a lookup.

## Schema/example consequence

The ordinary attestation-gated authority schemas now define the exact join point:

- `spec/secret.receipt.schema.json`
- `spec/workload.identity.issue.receipt.schema.json`

The canonical accepted examples now exercise that exact join directly:

- `spec/examples/secret.receipt.json`
- `spec/examples/workload.identity.issue.receipt.json`

## Guardrail

`tools/check_breakglass_resumption_join_contract.py`

This guardrail checks that:

- ordinary secret/identity authority schemas define `relevant_breakglass_receipt_digest`,
- the descriptions keep teaching that the field prevents latest-session folklore,
- the canonical accepted examples carry the computed digest of the canonical `breakglass.receipt` example,
- and the nearby attestation/breakglass/runbook docs keep teaching the same exact-join boundary.

## What stays open

This cut does **not** yet settle:

- whether there should be a dedicated denied ordinary-authority receipt for “fresh post-breakglass attestation still missing”,
- every future authority lane that may eventually consume `attestation_verification`,
- or how UI should best present post-breakglass resumption context across A/B/C/D.

The next coherence cuts now exist too: `docs/651-post-breakglass-ordinary-resumption-stays-same-host-bound.md` makes that exact join same host bound, and `docs/652-post-breakglass-ordinary-resumption-stays-time-ordered.md` makes the breakglass → attestation → ordinary-authority chain time-ordered, so the joined receipts may not drift into cross-host join folklore or backend-reconstructed freshness.

It only makes one narrow decision now:
**post-breakglass ordinary resumption stays exact-breakglass-digest joined instead of latest-session folklore.**

Last updated: 2026-03-21r382
