# ADR-0232: Attestation reference renewals stay digest-linked and successor-shaped

Status: Accepted  
Date: 2026-03-21

## Context

`ADR-0230` fixed the anti-snowflake baseline for `attestation.reference`, and `ADR-0231` fixed the next boundary: any non-baseline reference must carry a typed, timeboxed, approval-shaped `exception`.

That still left one expensive ambiguity: **what makes an exception renewal the successor of a prior exception instead of just another overlapping reference row?**

If the archive leaves that implicit, the real product quietly becomes:

- “latest matching verifier row wins”,
- reused `reference_id` strings with no digest-bound lineage,
- ticket comments saying “extended for another week”,
- or overlapping exception references that only backend state can untangle.

That would put renewal truth back into verifier-side databases right after we finished pulling exception authority into the reviewed artifact.

## Decision

**Renewed non-baseline attestation references must mint a fresh artifact and carry explicit digest-bound lineage to the prior exception they supersede.**

Concretely:

1. `attestation.reference.exception` now requires `renewal_posture`.
   - Allowed values: `fresh-exception`, `supersedes-prior-exception`.

2. `renewal_posture = fresh-exception` means the non-baseline reference starts a new exception story.
   - It does **not** silently borrow continuity from matching scope, matching selector, reused `reference_id`, or nearby timestamps.

3. `renewal_posture = supersedes-prior-exception` means the artifact is a reviewed successor.
   - It must carry `exception.supersedes_reference_digest`.
   - That digest names the exact prior `attestation.reference` being replaced as the currently reviewed exception authority.

4. Renewal happens by **new artifact**, not in-place extension.
   - A renewed exception gets a new digest, new `created_at`, fresh `exception.expires_at`, and fresh approvals.
   - “Extend the old row” is not the archive contract.

5. The ordinary baseline remains boring.
   - Routine cohort + `manifest-replay-first` references still carry no `exception` at all.

## Consequences

- Renewed exceptions become queryable and portable across bundle/export/support surfaces because lineage is in the signed artifact.
- Verifiers no longer need “newest row wins” folklore to explain why one exception displaced another.
- A/D can stage rollout or regulatory renewals without normalizing hidden per-host policy ledgers.
- B/C can still opt into attestation without inheriting a backend-only renewal model.

## Rejected alternatives

- **Infer renewal from shared `reference_id` / selector / timestamps.** Rejected: ambiguous and verifier-private.
- **Allow in-place expiry extension.** Rejected: destroys digest-bound review history.
- **Invent a standalone renewal service now.** Rejected for v0: too large when a typed successor field on the artifact solves the ambiguity directly.

## Status

Accepted and wired through `spec/attestation.reference.schema.json`, a canonical non-baseline example, the measured-boot/attestation docs, and `tools/check_attestation_reference_renewal_contract.py`.
