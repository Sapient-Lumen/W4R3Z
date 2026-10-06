# ADR-0120: Hardware support qualification must be receipt-bound, not ticket-bound

- **Status:** Accepted
- **Date:** 2026-03-16
- **Deciders:** DeriveBSD archive maintainers

## Context

`adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md` fixed **where** support claims live: `hw.support.matrix` is the digest-bound catalog artifact.
`adrs/ADR-0119-hardware-support-promotion-and-qualification-boundary.md` fixed **what positive support labels must say**: positive entries now carry a typed `qualification` summary.

That still left one expensive gap.
A matrix summary can say `release-qualified` or `conditional`, but unless that summary points at a typed receipt, the real evidence still lives in lab tickets, spreadsheets, portal notes, or support-team memory.

That drift is costly in every product shape:

1. **A / fleet host** wants rollout cohorts that can point at a durable support-promotion receipt instead of reverse-engineering Jira comments.
2. **B / workstation** needs trusted-UI-visible explanations that can name the exact qualification receipt for display/input/boot/recovery claims rather than saying “the release team verified this somewhere.”
3. **C / general OS** benefits from better evidence while preserving explicit override and advisory posture.
4. **D / appliance factory / regulatory** needs offline bundles whose support claims survive audits without network reachability to a vendor portal.

Real ecosystems end up here too: Android couples public compatibility policy to public/ongoing test programs, Red Hat turns certification into model-specific test plans and published supported-feature statuses, Ubuntu publishes certified hardware and says certified systems are verified and continuously tested through the release life cycle, and Fuchsia keeps hardware matching explicit with bind rules instead of ambient probe folklore.

## Decision

DeriveBSD now makes one further narrow decision:

1. **Positive hardware support claims must be receipt-bound.**
   `hw.support.matrix.entries[].qualification` now requires `qualification.receipt_digest`, pointing at a typed `hw.support.qualification.receipt` object.

2. **The matrix stays summary-shaped.**
   `qualification` in the matrix remains the small catalog summary used for discovery, diff review, and offline support bundles. The receipt is the deeper evidence object, not the new catalog.

3. **Qualification receipts are evidence-only, not runtime authority.**
   `hw.support.qualification.receipt` records:
   - the target release/generation lineage,
   - the support claim (`entry_id`, support level, profiles, roles),
   - the typed qualification summary,
   - supporting evidence digests,
   - and the publication decision.

   It does **not** directly load drivers, widen device grants, or override host policy.

4. **Preflight should surface matched receipt digests.**
   `hw.compat.report.support_matrix` may now carry `matched_qualification_receipt_digests` so trusted-UI warnings, support bundles, and rollout explanations can point directly at the evidence object that backs a matched support claim.

5. **The receipt is the bridge between summary and bundle.**
   For B and D especially, the qualification receipt is the object that allows a release/reset/support bundle to say not just “this class is supported,” but “this is the typed evidence object backing that statement.”

## Consequences

### Positive

- Support promotion is no longer half in the matrix and half in external ticket systems.
- Workstation trusted-UI and recovery warnings can point at a real evidence object.
- Factory/regulatory bundles gain a stable offline artifact for support audits.
- Future diff/review surfaces can reason about support-promotion evidence without inventing a test-farm empire up front.

### Trade-offs

- Catalog authors now need one more typed object per promoted hardware claim.
- The receipt schema is intentionally summary-first; it does not replace deeper lab artifacts.
- Revocation/supersession lifecycle details remain to be fleshed out later.

## Non-goals

This ADR does **not** decide:

- the full hardware-certification/test-farm architecture,
- every possible supporting evidence kind,
- the final UI for rendering qualification receipts,
- or the full automation/notification lifecycle for aging or withdrawn hardware classes; `adrs/ADR-0123-hardware-support-qualification-status-boundary.md` now fixes the receipt-status semantics themselves.

It only fixes the missing join: positive support claims must have a typed receipt that can travel with the archive and with offline support bundles.
