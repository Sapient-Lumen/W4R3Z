# ADR-0242: Post-breakglass ordinary resumption stays time-ordered

- Status: Accepted
- Date: 2026-03-22
- Deciders: DeriveBSD archive maintainers

## Context

`ADR-0239` already decided that breakglass is not sticky ordinary authority:
later ordinary secret or workload-identity lanes must consume a fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`.

`ADR-0240` then made the governing emergency session exact through `relevant_breakglass_receipt_digest`.
`ADR-0241` then made that exact join same-host bound.

One more quiet implementation choice still remained open:
**how do we prove the post-breakglass resumption story is actually time-ordered instead of only narratively fresh?**

Without one more narrow cut, implementations can still drift toward folklore such as:

- pinning the right breakglass digest and the right attestation digest but not proving the attestation actually happened after the breakglass barrier,
- minting an ordinary secret or workload identity receipt whose own timestamp predates the attestation receipt it claims to have consumed,
- or relying on verifier dashboards, agent state, or backend event order to explain freshness after the fact.

That leaves a hidden causality seam alive exactly where the archive has been trying to remove hidden state.

## Decision

**In v0, post-breakglass ordinary resumption stays time-ordered.**

That means:

1. When an ordinary secret or workload-identity receipt carries `attestation_verification.relevant_breakglass_receipt_digest`, the pinned `attestation.receipt.created_at` must be **strictly later** than the joined `breakglass.receipt.created_at`.
2. The consuming ordinary authority receipt must not predate the pinned attestation receipt it claims to have consumed.
   - `secret-receipt.emitted_at >= attestation.receipt.created_at`
   - `workload-identity-issue-receipt.issued_at >= attestation.receipt.created_at`
   - `workload-identity-issue-receipt.captured_at >= attestation.receipt.created_at`
3. Post-breakglass freshness may not be recovered from verifier row order, “latest successful attestation” dashboards, or host-local memory. The portable artifacts themselves must tell a causally ordered story.
4. The canonical examples and nearby docs must teach the same temporal boundary so detached tooling can explain why an ordinary authority act was fresh after breakglass without reopening backend state.

## Consequences

### Positive

- “Fresh after breakglass” stops being prose-only and becomes a portable time-order claim.
- Detached support/export tooling can explain the post-breakglass story from exact joined receipts plus their timestamps.
- A/B/C/D stay coherent because emergency recovery does not silently become a standing freshness waiver.

### Negative / limits

- JSON Schema still cannot prove arbitrary cross-object temporal ordering; the archive teaches and checks the boundary through reviewed examples and guardrails.
- This does not yet create a dedicated typed denial object for stale post-breakglass ordinary resumption attempts.
- The archive still leaves freshness-window tuning (for example maximum age between attestation and authority) open for later, profile-aware work.

## Why this is the right small hard decision now

The archive already removed hidden selection, hidden subject joins, and hidden breakglass-session discovery.
The next expensive ambiguity is quieter: whether the same exact digests can still be paired in a causally impossible order and then explained away by backend folklore.
This cut answers that narrowly and usefully:
**post-breakglass ordinary resumption stays time-ordered instead of prose-only freshness.**
