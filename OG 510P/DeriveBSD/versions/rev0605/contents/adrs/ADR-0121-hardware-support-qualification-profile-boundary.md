# ADR-0121: hardware support qualification profile boundary

Date: 2026-03-16
Status: Accepted

## Context

`adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md` fixed **where** supported-hardware claims live: `hw.support.matrix` is the digest-bound catalog artifact.
`adrs/ADR-0119-hardware-support-promotion-and-qualification-boundary.md` fixed that positive entries must carry a typed `qualification` summary.
`adrs/ADR-0120-hardware-support-qualification-receipt-boundary.md` fixed that the summary must point at a typed `hw.support.qualification.receipt`.

That still left one expensive ambiguity: a receipt can prove **that** some qualification happened without stating the stable qualification **standard** it was meant to satisfy. In practice that means `release-qualified` can still quietly degrade into “we ran some tests somewhere.”

Real ecosystems do not leave that part implicit. Android pairs a release compatibility definition with explicit test suites, Ubuntu certification is tied to a continuous lab-tested program over the release lifecycle, Red Hat creates official test plans from certification policy and submitted hardware details, and Windows compatibility uses official HLK playlists/test passes rather than informal lab judgement.

## Decision

Accept a new typed qualification-standard artifact: `hw.support.qualification.profile`.

1. **`hw.support.qualification.profile` becomes the typed qualification standard.**
   It defines the release-train qualification floor as digest-bound scope (`profiles`, `support_levels`, `roles`) plus `required_checks` with stable `check_id`, `purpose`, accepted evidence kinds, and blocking/non-blocking posture.

2. **Positive support claims must now point at both the standard and the proof.**
   `hw.support.matrix.entries[].qualification` now requires `profile_digest` as well as `receipt_digest`.

3. **Qualification receipts must name which profile they satisfied.**
   `qualification.profile_digest` points at the profile digest, and `check_results[]` records which `check_id`s were satisfied and which supporting evidence digests were used.

4. **This remains evidence-policy, not runtime authority.**
   Qualification profiles do not load drivers, change device authority, widen update policy, or become a live certification service. They exist so that support promotion means the same thing across labs, bundles, and release trains.

## Consequences

Good:
- B/workstation trusted-UI floor claims now point at both the evidence receipt and the typed standard that defined the check set.
- D/appliance bundles can ship the support catalog, the receipt, and the qualification profile offline without ticket-system dependencies.
- A/fleet cohorting can compare support claims across trains without rediscovering what each team meant by “qualified”.
- The archive can now mechanically catch drift between qualification vocabulary and receipt evidence vocabulary.

Trade-offs:
- This adds one more artifact to the hardware-support lane.
- The profile is intentionally small and abstract; it does not replace deeper lab automation, certification portals, or future RFC work on broader test harnesses.

## Follow-up

This ADR does **not** decide:
- the full hardware-class canonicalization algorithm,
- a universal certification portal or lab runner,
- every possible qualification check purpose,
- or how automation should discover and publish replacement receipts after field regressions; `adrs/ADR-0123-hardware-support-qualification-status-boundary.md` now fixes what superseded/revoked means once published.

It only fixes the missing standard/proof split so the support lane stays reviewable.
