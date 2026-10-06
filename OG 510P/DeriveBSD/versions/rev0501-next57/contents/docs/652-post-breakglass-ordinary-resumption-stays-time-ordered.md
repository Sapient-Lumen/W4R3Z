# Post-breakglass ordinary resumption stays time-ordered

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt

The archive already decided three important post-breakglass facts:
ordinary secret and workload-identity lanes must use a fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`,
that later ordinary receipt must carry `relevant_breakglass_receipt_digest` when breakglass materially formed the resumption barrier,
and the joined breakglass and attestation receipts must still name the same host.

What still needed one more small hard decision was the **time chain** itself.
Exact digests and same-host joins are still not enough if the archive quietly allows an ordinary authority receipt to predate the fresh attestation receipt it claims to have consumed.

Related:
- ADR: `adrs/ADR-0242-post-breakglass-ordinary-resumption-stays-time-ordered.md`
- prior same-host boundary: `docs/651-post-breakglass-ordinary-resumption-stays-same-host-bound.md`
- prior exact-join boundary: `docs/650-post-breakglass-ordinary-resumption-stays-exact-breakglass-digest-joined.md`
- prior resumption boundary: `docs/649-breakglass-does-not-silently-reopen-ordinary-attestation-gated-authority.md`

## The boundary

When an ordinary secret or workload-identity receipt carries:

- `attestation_verification.relevant_breakglass_receipt_digest`

then the portable evidence must tell one causally ordered story:

- joined `attestation.receipt.created_at` is **strictly later** than joined `breakglass.receipt.created_at`,
- `secret-receipt.emitted_at` must not predate the pinned `attestation.receipt.created_at`,
- `workload-identity-issue-receipt.issued_at` and `captured_at` must not predate the pinned `attestation.receipt.created_at`,
- and responders should not need dashboards, verifier row order, or host-local memory to infer whether the attestation was actually fresh after breakglass.

## Why this matters

### 1) Freshness should be portable, not rhetorical

The archive already said “fresh after breakglass.”
The next hidden failure mode is subtler: one can still pin the right breakglass receipt digest and the right attestation receipt digest while leaving time order to backend folklore.

### 2) Ordinary authority should not predate the evidence it claims to consume

A `secret-receipt` or `workload-identity-issue-receipt` that appears earlier than the attestation receipt it claims to have consumed is not merely sloppy logging.
It makes the portable evidence story self-contradictory and pushes the real product back into service dashboards and operator memory.

### 3) It stays small

This does not add a session catalog, a freshness ticket, or a replay service.
It only teaches one more exact invariant: post-breakglass ordinary authority must stay causally ordered in the portable receipts themselves.

## Schema/example consequence

The ordinary attestation-gated authority schemas now teach the time-order rule in the `attestation_verification` descriptions:

- `spec/secret.receipt.schema.json`
- `spec/workload.identity.issue.receipt.schema.json`
- `spec/breakglass.receipt.schema.json`

The canonical examples now exercise the same temporal story coherently too:

- `spec/examples/breakglass.receipt.json`
- `spec/examples/attestation.receipt.json`
- `spec/examples/secret.receipt.json`
- `spec/examples/workload.identity.issue.receipt.json`
- `spec/examples/incident.bundle.json`

## Guardrail

`tools/check_breakglass_resumption_temporal_contract.py`

This guardrail checks that:

- ordinary secret/identity authority schemas teach that post-breakglass resumption is time-ordered,
- the canonical breakglass, attestation, secret, and workload examples now tell that causal story in timestamp order,
- the canonical support bundle stays wired to the refreshed canonical digests,
- and the nearby attestation/breakglass/runbook docs keep teaching the same no-backend-folklore temporal boundary.

## What stays open

This cut does **not** yet settle:

- whether stale post-breakglass ordinary attempts should get their own typed denial receipt,
- whether profile-specific maximum attestation age should become explicit later,
- or how UI should best visualize the breakglass → attestation → authority time chain across A/B/C/D.

It only makes one narrow decision now:
**post-breakglass ordinary resumption stays time-ordered instead of prose-only freshness.**

Last updated: 2026-03-21r382
