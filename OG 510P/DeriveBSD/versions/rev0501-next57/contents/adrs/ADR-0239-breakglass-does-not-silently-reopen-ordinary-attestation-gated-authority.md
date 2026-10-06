# ADR-0239: Breakglass does not silently reopen ordinary attestation-gated authority

- Status: Accepted
- Date: 2026-03-22
- Deciders: DeriveBSD archive maintainers

## Context

Recent attestation cuts already removed several hidden implementation choices:

- decisive consuming receipts pin the exact requirement/receipt/policy digest tuple,
- they mirror the exact pinned verifier verdict,
- degraded admission stays requirement-shaped,
- and ordinary secret/identity lanes stay fail-closed on rejected posture while breakglass remains the explicit emergency lane.

That still left one quiet loophole after the emergency crossing itself:
**how do ordinary attestation-gated lanes become eligible again after a breakglass session happened?**

Without one more narrow boundary, implementations drift toward folklore such as:

- reusing a previously accepted or degraded `attestation.receipt` that predates the breakglass session,
- treating successful breakglass as an implicit waiver that reopens ordinary secret or workload-identity lanes,
- or making operators consult dashboards/tickets/session memory to infer whether a later ordinary action really had fresh post-recovery posture.

That would make the emergency lane sticky in exactly the way this archive has been trying to avoid.

## Decision

**In v0, breakglass never silently reopens ordinary attestation-gated authority.**

That means:

1. `breakglass.receipt` now carries `ordinary_resumption_posture = fresh-attestation-after-breakglass-created-at-required`.
2. The boundary timestamp is the breakglass receipt `created_at`.
3. Any later ordinary attestation-gated authority receipt (for example `secret-receipt` or `workload-identity-issue-receipt`) must consume a fresh `attestation.receipt` issued after that breakglass `created_at`.
4. Implementations may not reuse pre-breakglass accepted/degraded attestation evidence as the basis for ordinary post-breakglass authority.
5. Breakglass remains an explicit emergency lane, not standing ordinary authority and not an ambient verifier-side waiver.

## Consequences

### Positive

- Emergency recovery no longer has an implicit “and now we are back to normal” side effect.
- A/B/C/D can explain post-breakglass ordinary resumption from portable receipt data instead of ticket prose or backend state.
- The archive keeps converging on exact reviewed artifacts rather than helper-side timestamps and remembered operator intent.

### Negative / limits

- This does not yet define a dedicated denied/resumption receipt for “ordinary lane attempted too early after breakglass”.
- This duplicates one small recovery fact into `breakglass.receipt` as a fixed evidence field.
- Cross-object time ordering still remains an implementation/checker concern rather than something JSON Schema alone can fully prove.

## Why this is the right small hard decision now

The expensive ambiguity is no longer whether breakglass is explicit; it is whether breakglass has hidden after-effects.
This cut answers that narrowly and usefully without inventing a larger verifier/catalog/session-history subsystem:
**breakglass is terminal for ordinary attestation-gated authority until fresh post-breakglass attestation evidence exists.**
