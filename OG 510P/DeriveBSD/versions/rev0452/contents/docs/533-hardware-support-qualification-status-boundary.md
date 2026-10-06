# Hardware support qualification status boundary

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate

`docs/532-hardware-support-qualification-freshness-boundary.md` fixed when support qualification stops counting as fresh.
This doc makes the next small hard decision:
**support qualification receipts must also have an operational publication status, so `accepted`, `superseded`, and `revoked` change what a positive hardware-support claim means instead of sitting as unused schema vocabulary.**

See also:
- ADR: `adrs/ADR-0123-hardware-support-qualification-status-boundary.md`
- support-catalog boundary: `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`
- promotion semantics: `docs/529-hardware-support-promotion-and-qualification-boundary.md`
- qualification receipt boundary: `docs/530-hardware-support-qualification-receipt-boundary.md`
- qualification profile boundary: `docs/531-hardware-support-qualification-profile-boundary.md`
- qualification freshness boundary: `docs/532-hardware-support-qualification-freshness-boundary.md`
- hardware compatibility preflight: `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`
- workstation viability: `docs/410-desktop-viability-checklist.md`
- qualification receipt shape: `spec/hw.support.qualification.receipt.schema.json`
- compatibility report shape: `spec/hw.compat.report.schema.json`

## Why this needs a hard decision

The archive can now answer three support questions with typed artifacts:

- which hardware-class support entry matched,
- which typed qualification standard defined the floor,
- and which typed receipt proved that floor, with freshness attached.

But there was still no typed answer for a fourth question:

- **is that receipt still the current publication state for this support claim?**

Without that boundary, several bad outcomes remain likely:

- a workstation trusted-UI claim keeps sounding current even after a better replacement receipt exists,
- a factory support bundle carries a receipt that has been actively withdrawn for a recovery-floor regression,
- and preflight/reporting can only say “stale” even when the problem is stronger: the evidence was replaced or revoked.

That is too much ambiguity for A/B/D and too much hidden support drift for C when it opts into typed support posture.

## Accepted boundary

Across all profiles:

- `hw.support.qualification.receipt.decision.status` is now operational lifecycle state, not decorative metadata,
- `decision.status_effective_at` records when that lifecycle state took effect,
- `decision.reason_code` explains why a receipt stopped being current,
- `decision.replacement_receipt_digest` is required when the status is `superseded`,
- `hw.support.matrix.entries[].qualification.receipt_digest` may only point at a receipt whose `decision.status` is `accepted` for current positive publication,
- and `hw.compat.report` may emit `qualification-superseded` or `qualification-revoked` when a matched support claim points at a non-current receipt.

The point is narrow:
**freshness and publication state are different questions, and the archive now has typed answers for both.**

## Minimal v0 contract worth implementing

### `hw.support.qualification.receipt.decision`

The receipt decision block now has real semantics:

- `accepted` = current proof that may back a positive support claim
- `superseded` = historical proof replaced by a newer receipt, with `replacement_receipt_digest`
- `revoked` = proof must no longer back a positive support claim, with a typed `reason_code`

`status_effective_at` makes the transition auditable instead of implicit.

### `hw.support.matrix`

The matrix stays compact.
It does **not** gain a live advisory overlay.
Instead, the rule is simple: a currently positive matrix entry must point at an `accepted` receipt.
If support changes, the next published matrix/bundle updates the digest, downgrades the support level, or removes the positive claim.

That keeps the archive release-shaped rather than portal-shaped.

### `hw.compat.report`

Preflight/reporting now has two findings that are intentionally stronger than `qualification-stale`:

- `qualification-superseded`
- `qualification-revoked`

Those findings answer publication-state questions, not age questions.
A support proof can be fresh-but-revoked, or stale-but-not-revoked.
The archive should not collapse those into one warning.

## Product-shape fit

### A) Secure fleet host

- rollout cohorts can distinguish old-but-still-current evidence from evidence that has been actively replaced or withdrawn
- breakglass and override posture stays explicit instead of hiding support withdrawal in notes

### B) Secure workstation

- trusted-UI consent can say “this support proof was replaced” or “this proof was withdrawn” instead of overloading `qualification-stale`
- support claims for the trusted display/input floor become more honest when regressions are found after publication

### C) General-purpose OS

- explicit local override still exists
- stronger publication-state warnings help without forcing C into factory-style hard gates

### D) Appliance factory / regulatory

- offline support bundles can explain why a previously positive claim no longer counts
- audits can distinguish natural evidence aging from active support withdrawal or replacement

## Why this is the right small hard decision

This does not invent a new certification portal or live support service.
It simply makes the existing receipt lifecycle fields matter.

The support lane now has typed answers for:

- where support claims live,
- how they are promoted,
- which proof and standard back them,
- when they stop counting as fresh,
- and whether the proof is still the current published support evidence.

That is enough to keep future implementation work honest without widening scope.

## External practice that shaped this cut

- Android CTS overview and production-testing guidance (current compatibility requires current passing runs, not stale past success): https://source.android.com/docs/compatibility/cts
- Ubuntu Certified / lifecycle testing posture (certified hardware remains continuously tested through the release lifecycle): https://ubuntu.com/certified
- Windows HLK compatibility-playlist guidance (qualification tracks the current official playlist, not a timeless old run): https://learn.microsoft.com/en-us/windows-hardware/test/hlk/what-s-new-in-the-hardware-lab-kit

Last updated: 2026-03-17r262
