# ADR-0119: Hardware support promotion is qualification-shaped, not folklore

- **Status:** Accepted
- **Date:** 2026-03-16
- **Deciders:** DeriveBSD archive maintainers

## Context

`adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md` fixed **where** approved-hardware/support claims live: `hw.support.matrix` is now the digest-bound catalog artifact instead of release-note prose, vendor spreadsheets, or per-host allowlists.

That still left an uncomfortable gap:
what keeps `supported`, `conditional`, and `canary-only` from turning into vibes?

Without a second narrow boundary, three bad outcomes remain likely:

1. **B / workstation** support claims drift into marketing language instead of a typed statement that the trusted-display / trusted-input / boot-storage floor was actually rechecked on the release train.
2. **A / fleet host** cohorts start depending on folk knowledge about which hardware classes were only canary-tested versus fully promoted.
3. **D / appliance-factory** approval bundles say a platform is supported, but nobody can tell whether that means “passed lab boot once” or “release-qualified with recovery evidence.”

The archive already had the right ingredients:

- `hw.support.matrix` as the catalog surface,
- `hw.compat.report` as the join/gating surface,
- `restore.drill.receipt` and other release evidence lanes for recovery/regression facts,
- and product-default hardware posture fixed in `docs/479-hardware-compatibility-posture-by-profile.md`.

What was missing was a very small typed story for **promotion maturity**.

## Decision

DeriveBSD now fixes that missing boundary as follows:

1. **Positive support claims must carry a typed qualification summary.**
   Any `hw.support.matrix` entry whose `support_level` is `supported`, `conditional`, `canary-only`, or `maintenance-only` must include a `qualification` object.

2. **Support labels are constrained by qualification stage.**
   The v0 stage vocabulary is intentionally small:
   - `lab-validated`
   - `canary-observed`
   - `release-qualified`
   - `field-sustained`

   The required mapping is:
   - `canary-only` → `canary-observed`
   - `supported` → `release-qualified` or `field-sustained`
   - `conditional` → at least `lab-validated`
   - `maintenance-only` → `release-qualified` or `field-sustained`

3. **Qualification must say which roles were truly rechecked.**
   `qualification.verified_roles` records the subset of matrix roles that were actually part of the promotion evidence. This keeps “supported” from quietly meaning “booted once, but nobody rechecked display/input/recovery.”

4. **Qualification must declare a small evidence floor.**
   `qualification.evidence_floor` uses a short controlled vocabulary (`boot`, `generation-switch`, `rollback-or-recovery`, `trusted-ui-basic`, `network-basic`, `device-mediation-basic`, `suspend-resume`) so the matrix can say what was revalidated without inventing a giant certification DSL.

5. **Trusted-UI and recovery claims get stricter by design.**
   If an entry claims `trusted-display`, `trusted-input`, or `boot-storage` for B or D, the qualification floor must include `rollback-or-recovery`. If trusted UI roles are present, the qualification floor must also include `trusted-ui-basic`.

6. **Qualification is still catalog metadata, not runtime authority.**
   The new summary does not make the matrix a live control plane. It only keeps support promotion reviewable and bundle-friendly.

## Consequences

### Positive

- B gets a non-handwavy answer to “why is this laptop supported enough for the trusted UI floor?”
- A can distinguish canary cohorts from genuinely promoted cohorts without host-specific folklore.
- D can ship approval/support bundles that say not just *that* a class is supported, but *how far it was qualified*.
- Future diff/review surfaces can reason about support promotion without reverse-engineering ticket notes.

### Trade-offs

- Catalog authors must now be explicit about qualification stage and evidence floor.
- Some messy hardware will remain `conditional` or `canary-only` longer, which is good discipline but less flattering marketing.
- This still does not encode every lab workflow or vendor program; those stay behind the catalog.

## Non-goals

This ADR does **not** decide:

- the full certification/test-farm architecture,
- the exact machine-readable format of every underlying test receipt,
- the final UI for rendering qualification details to operators or workstation users,
- or every future evidence-floor token.

It only fixes the missing contract: support promotion must be typed, stage-bounded, and explicit about what floor was actually revalidated.
