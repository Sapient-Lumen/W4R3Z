# ADR-0233: Attestation reference selection stays exact-digest-pinned and no latest-wins

Status: Accepted  
Date: 2026-03-21

## Context

`ADR-0230`, `ADR-0231`, and `ADR-0232` fixed the authoring side of `attestation.reference`: routine references stay cohort-shaped and replay-first, non-baseline references are explicit timeboxed exceptions, and renewed exceptions mint fresh artifacts with digest-bound lineage.

That still left one expensive ambiguity: **how should a verifier or admission gate choose a reference when multiple artifacts share similar scope or selector hints?**

If the archive leaves that implicit, the real product quietly becomes:

- “newest matching selector wins”,
- “most specific host/deployment row wins”,
- “unexpired predecessor is still acceptable unless a backend flag says otherwise”,
- or a verifier-side named-policy database that only operators can untangle.

Keylime’s current measured-boot tooling shows both why generic event-log policy matters and why this seam is dangerous: static PCR allowlists are fragile, large deployments need event-log policy generic enough for sets of nodes, and named measured-boot policies can be stored in the verifier database itself. DeriveBSD should keep the portable truth on exact digests, not on overlap/recency folklore.

## Decision

**Attestation evaluation and admission remain pinned to an exact `attestation.reference` digest. `scope.selector` stays discovery metadata, not an implicit precedence rule.**

Concretely:

1. `attestation.receipt.reference_digest` remains the authoritative answer to **which reference was actually used**.
   - Verifiers and downstream gates must not summarize evaluation as “matched the latest canary policy” or similar selector prose when the exact digest is knowable.

2. `attestation.reference.scope.selector` remains a hint for packaging, discovery, or human review.
   - It is **not** a newest-match resolver key.
   - It is **not** a most-specific-match precedence key.
   - It is **not** sufficient to discover supersession on its own.

3. Overlap between references does not create implicit precedence.
   - Shared scope names, matching selectors, later `created_at`, unexpired predecessors, or reused `reference_id` values do not decide which reference a verifier should apply.

4. Successor lineage still matters, but does not become automatic selector resolution.
   - `exception.supersedes_reference_digest` explains reviewed succession between non-baseline exception artifacts.
   - It does **not** authorize a verifier to auto-rebind any matching selector to the successor by recency or convenience.

5. Any future reference-catalog or reference-selection helper must compile down to exact digest choice.
   - If DeriveBSD later adds higher-level authoring/assignment helpers, they remain a separate RFC surface and may not weaken the exact-digest evaluation contract.

## Consequences

- Measured-boot receipts stay portable: bundles/support/export surfaces can always point at the exact reviewed reference digest.
- Renewals no longer tempt operators into “the new row obviously replaced the old one everywhere” folklore.
- A/B/C/D keep flexible authoring shapes without inheriting hidden overlap rules in the verifier backend.
- The archive postpones any larger catalog/resolver subsystem until there is a real need and an RFC-worthy design.

## Rejected alternatives

- **Newest matching scope/selector wins.** Rejected: easy to implement, impossible to audit cleanly.
- **Host beats deployment beats cohort automatically.** Rejected: this turns selectors into hidden authority and normalizes backend precedence.
- **Unexpired predecessor remains acceptable until wall-clock expiry unless the verifier says otherwise.** Rejected: overlap state belongs in explicit control-plane choice, not implicit verifier ordering.
- **Invent a reference-catalog subsystem now.** Rejected for v0: too large when the immediate problem is stopping implicit resolver folklore.

## Status

Accepted and wired through the attestation docs, schema descriptions, runbook/hygiene guidance, and `tools/check_attestation_reference_selection_contract.py`.
