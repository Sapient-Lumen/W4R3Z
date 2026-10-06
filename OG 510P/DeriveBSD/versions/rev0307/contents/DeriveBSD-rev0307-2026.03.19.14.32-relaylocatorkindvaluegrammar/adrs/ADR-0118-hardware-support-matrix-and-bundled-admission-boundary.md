# ADR-0118: Hardware support matrices are digest-bound admission catalogs, not live authority

- **Status:** Accepted
- **Date:** 2026-03-16
- **Deciders:** DeriveBSD archive maintainers

## Context

`adrs/ADR-0069-hardware-compatibility-posture-by-profile.md` fixed the **strength** of hardware compatibility posture across A–D, but it intentionally left one implementation detail open: how do approved-hardware claims and bundled support posture become a typed, reviewable artifact instead of ticket notes, vendor spreadsheets, or portal folklore?

That gap mattered in three places at once:

1. **D / appliance-factory** needs an offline, shippable support/admission story that travels with release bundles and reset media.
2. **A / fleet host** needs cohorting/support facts that are more stable than ad-hoc hostnames but less privacy-toxic than per-host allowlists.
3. **B / workstation** needs a humane way to say “this generation is supported for the trusted UI floor” before a human consents to a risky switch.

The archive already had the raw ingredients:

- `hw.inventory.receipt` for privacy-safe observed hardware truth,
- `hw.compat.report` for target-specific preflight findings,
- profile defaults in `docs/479-hardware-compatibility-posture-by-profile.md`,
- and firmware / release bundle lanes that already assume some hardware targeting story exists.

What was still missing was a **bounded catalog artifact** that says which hardware classes are supported, under what floor roles, and with what recovery expectations — without turning that catalog into a new ambient authority source.

## Decision

DeriveBSD now fixes that boundary as follows:

1. **`hw.support.matrix` is the canonical support/admission catalog artifact.**
   It is a digest-bound artifact that describes supported hardware classes for a specific release/generation/reset bundle target.

2. **The matrix keys on hardware-class summaries, not raw host identity.**
   Matching may use stable class identifiers such as PCI IDs, USB IDs, ACPI HIDs, SMBIOS CHIDs, board products, and coarse virtualization posture — not serial-number allowlists.

3. **`hw.support.matrix` is not execution authority.**
   It does not load drivers, mutate kernel policy, or override inventory truth. It only supplies a reviewable catalog that `hw.compat.report` may join when deciding support/admission posture.

4. **`hw.compat.report` may now record explicit matrix join state.**
   When a support matrix participates in a preflight/admission decision, the report records the matrix digest, match state, and matched entry ids rather than burying that logic in notes.

5. **B’s trusted-UI floor is now first-class in the vocabulary.**
   The compatibility lane may emit `trusted-ui-floor-risk` and `recovery-path-missing` findings so workstation support decisions stop collapsing display/input/recovery concerns into generic “good luck” warnings.

## Consequences

### Positive

- D finally gets a portable, offline support/admission object instead of ticket-bound support folklore.
- A gets a cleaner hardware-class cohorting/support lane without per-host inventory sprawl.
- B gets a narrow typed place to say “supported for trusted display/input/storage floor” before rebooting into uncertainty.
- The archive can keep one hardware story across A–D without pretending all profiles need identical gate strength.

### Trade-offs

- This introduces one more artifact kind that must remain small and conservative.
- Catalog authors now have to be explicit about support level and recovery expectations instead of hiding ambiguity in prose.
- Some truly messy compatibility cases will still live in C-style explicit override lanes instead of fitting neatly into the matrix.

## Non-goals

This ADR does **not** decide:

- the exact collector or canonicalization algorithm that produces hardware-class summaries,
- the exact certification workflow for vendors or partners,
- the final UX for how trusted-UI warnings are rendered on B,
- or the full reason-code taxonomy for every possible compat failure.

It only fixes the missing boundary: approved-hardware/support claims are typed, digest-bound, and matched against stable class summaries, while runtime authority still belongs to inventory truth, policy decisions, and explicit activation/update lanes.
