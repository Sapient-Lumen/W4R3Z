# ADR-0241: Post-breakglass ordinary resumption stays same-host bound

- Status: Accepted
- Date: 2026-03-22
- Deciders: DeriveBSD archive maintainers

## Context

`ADR-0239` already made post-breakglass ordinary authority non-sticky:
later ordinary secret or workload-identity lanes must consume a fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`.

`ADR-0240` then made the governing breakglass session exact:
ordinary consuming receipts now carry `relevant_breakglass_receipt_digest` when breakglass materially formed the resumption barrier.

That still left one more quiet implementation choice open:
**what proves that the joined breakglass receipt and the joined attestation receipt are about the same host?**

Without one more narrow cut, implementations can still drift toward folklore such as:

- joining a fresh attestation receipt from one host with a breakglass receipt from another host,
- treating `relevant_breakglass_receipt_digest` as just an emergency-context hint rather than a same-subject barrier,
- or relying on backend inventory/host history to explain whether the breakglass/attestation join was even about the same machine.

That would keep a cross-host resolver seam alive exactly where the archive has been trying to remove hidden state.

## Decision

**In v0, post-breakglass ordinary resumption stays same-host bound.**

That means:

1. When an ordinary secret or workload-identity receipt carries `attestation_verification.relevant_breakglass_receipt_digest`, the joined `breakglass.receipt.session.host_id` and the joined `attestation.receipt.subject.host_id` must name the same host.
2. `relevant_breakglass_receipt_digest` is not merely context about some nearby emergency session; it names the exact breakglass receipt whose host and `created_at` formed the barrier for the pinned ordinary attestation receipt.
3. Implementations may not justify post-breakglass ordinary authority through cross-host joins, inventory side tables, or “same fleet / same role / same rack” folklore.
4. The canonical examples and nearby docs must teach the same same-host boundary, so support/export tooling can explain the join from portable artifacts instead of backend memory.

## Consequences

### Positive

- The exact breakglass join now also has an exact subject boundary instead of only an exact digest boundary.
- Detached tooling can explain post-breakglass ordinary authority without reopening inventory or host-history state just to prove the two joined receipts refer to the same machine.
- A/B/C/D stay coherent for fleets, workstations, general OS, and factory/regulatory shapes because emergency recovery cannot silently spill across host boundaries.

### Negative / limits

- JSON Schema still cannot prove arbitrary cross-object identity equality; the archive teaches and checks the boundary through reviewed examples and guardrails.
- This still does not define a dedicated denied receipt for “wrong-host breakglass join” attempts.
- Future non-host-shaped attestation subjects may need a more general subject-binding rule; v0 only settles the host case now.

## Why this is the right small hard decision now

The expensive ambiguity is no longer whether breakglass matters, whether the exact emergency session is named, or whether fresh attestation exists.
It is whether the joined breakglass and attestation evidence can quietly drift across host boundaries.
This cut answers that narrowly and usefully:
**post-breakglass ordinary resumption stays same-host bound instead of cross-host join folklore.**
