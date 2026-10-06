# Post-breakglass ordinary resumption stays same-host bound

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt

The archive already decided two important post-breakglass facts:
ordinary secret and workload-identity lanes must use a fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`,
and when breakglass materially mattered the consuming receipt must carry `relevant_breakglass_receipt_digest`.

What still needed one more small hard decision was the **subject join** itself.
An exact breakglass digest is still not enough if the archive quietly allows a breakglass receipt from one host to be paired with an attestation receipt from another host.
The next quiet failure mode after that is the **time chain**: even the same host can still tell a causally impossible freshness story unless the portable receipts stay time-ordered.

Related:
- ADR: `adrs/ADR-0241-post-breakglass-ordinary-resumption-stays-same-host-bound.md`
- prior exact-join boundary: `docs/650-post-breakglass-ordinary-resumption-stays-exact-breakglass-digest-joined.md`
- prior resumption boundary: `docs/649-breakglass-does-not-silently-reopen-ordinary-attestation-gated-authority.md`
- attestation evidence boundary: `docs/492-attestation-results-evidence-and-admission-issue-boundary.md`

## The boundary

When an ordinary secret or workload-identity receipt carries:

- `attestation_verification.relevant_breakglass_receipt_digest`

that exact breakglass receipt must be for the **same host** as the pinned `attestation.receipt`.
In concrete terms:

- joined `breakglass.receipt.session.host_id` and joined `attestation.receipt.subject.host_id` must match,
- the breakglass receipt is not just nearby emergency context,
- and implementations do **not** get to explain post-breakglass ordinary authority through cross-host joins, fleet-role similarity, or inventory folklore.

## Why this matters

### 1) Exact digests still need exact subject meaning

`relevant_breakglass_receipt_digest` already removed “latest breakglass wins” folklore.
The next hidden failure mode is subtler: a service can still pin one breakglass digest and one attestation digest while leaving responders to discover later that they were not even about the same host.

### 2) It keeps emergency authority local to the actual machine

Breakglass is a host-local emergency crossing.
Ordinary resumption after that crossing must stay bound to the same host whose emergency session created the barrier.
Otherwise fleets normalize cross-host rescue folklore exactly where portable evidence should stay crisp.

### 3) It stays small

This does not add a session catalog, a host resolver service, or a new receipt kind.
It only teaches one more exact join invariant: the joined breakglass receipt and the joined attestation receipt must name the same host.

## Schema/example consequence

The ordinary attestation-gated authority schemas now teach the same-host rule in the `relevant_breakglass_receipt_digest` descriptions:

- `spec/secret.receipt.schema.json`
- `spec/workload.identity.issue.receipt.schema.json`

The canonical examples now exercise the same-host join coherently too:

- `spec/examples/attestation.receipt.json`
- `spec/examples/breakglass.receipt.json`
- `spec/examples/secret.receipt.json`
- `spec/examples/workload.identity.issue.receipt.json`

## Guardrail

`tools/check_breakglass_resumption_subject_binding_contract.py`

This guardrail checks that:

- ordinary secret/identity authority schemas teach that `relevant_breakglass_receipt_digest` is same-host bound,
- the canonical breakglass and attestation examples now name the same host,
- the canonical secret/workload examples keep pointing at those exact joined artifacts,
- and the nearby attestation/breakglass/runbook docs keep teaching the same no-cross-host-join boundary.

## What stays open

This cut does **not** yet settle:

- whether ordinary denied attempts should get a dedicated typed “wrong host / stale barrier” denial receipt,
- how a future non-host-shaped attestation subject should express the equivalent subject-binding rule,
- or how UI should best present same-host post-breakglass proof across A/B/C/D.

It only makes one narrow decision now:
**post-breakglass ordinary resumption stays same-host bound instead of cross-host join folklore.**

The next coherence cut now exists too: `docs/652-post-breakglass-ordinary-resumption-stays-time-ordered.md` makes that same-host join carry a portable time chain instead of backend-reconstructed freshness.

Last updated: 2026-03-21r382
