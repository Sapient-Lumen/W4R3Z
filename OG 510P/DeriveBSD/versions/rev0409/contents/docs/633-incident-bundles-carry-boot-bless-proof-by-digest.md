# Incident bundles carry boot-bless proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility  
**Patterns:** Plan→Apply→Receipt, Bundles  

DeriveBSD already decided that health-gated finalization should be typed and explainable.
This doc fixes the smaller but implementation-shaping support/export question the archive still left fuzzy in practice:

**how does the official incident/support bundle contract name the exact `boot.bless.receipt` when boot assessment or rollback actually shaped the story?**

The answer is intentionally narrow.
It is not a new boot subsystem and not a generic “boot-health blob” field.
It is the missing decision to make the existing boot-assessment decision artifact joinable through the official support-handoff contract.

See also:
- ADR: `adrs/ADR-0223-incident-bundles-carry-boot-bless-proof-by-digest.md`
- health-gated updates: `docs/112-health-gated-updates.md`
- boot assessment + try counters: `docs/241-boot-try-counters-and-boot-assessment.md`
- boot assessment in practice: `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`
- update-delivery posture: `docs/472-update-delivery-and-release-posture-by-profile.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`

## Why this needs a hard decision

`boot.health.report` and `boot.bless.receipt` already split the boot-finalization story in the right place:

- `boot.health.report` captures what required/wanted checks ran and what evidence they referenced,
- `boot.bless.receipt` captures the exact commit-or-rollback decision for the tentative boot,
- and health-gated update posture only becomes operationally real when responders can carry both surfaces without guessing.

But the official support/export contract still lagged behind that design in practice.
`incident.bundle` could carry `boot_health_report_digest`, but the archive still did not explicitly teach that the bundle should also name the exact `boot.bless.receipt` when a commit, rollback, or repeated failed-boot sequence materially shaped the incident.

A coherent archive should let support bundles answer both questions distinctly:

- **what health evidence did the gate evaluate?**
- **what exact boot-assessment/finalization decision shaped the handoff?**

## Accepted boundary

### 1) Bundles may carry the exact boot-assessment/finalization decision artifact

Support bundles should not force readers to reconstruct the decisive boot outcome from bootloader counters, greenboot status text, or updater prose.

- `boot_bless_receipt_digests` names the exact `boot.bless.receipt` object or objects that belong to the incident.
- The referenced `boot.bless.receipt` remains the place that records the good/bad decision, tries-left/tries-done context, correlation ids, and the `boot_health_report_digest` that drove the decision when present.

This keeps the official bundle contract compact while still naming the canonical decision proof.

### 2) The official selector is now treated as real

The canonical include surface already carries `boot_bless_receipts`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same selector works both when planning the bundle and when recording what the final bundle included.

That keeps health-gated finalization on the official support-bundle lane instead of buried in `extra`, bootloader counters, greenboot status text, or ticket prose.

### 3) Keep report detail and finalization decision separate

This is the design cut worth preserving.
The archive does **not** collapse all boot-assessment evidence into one generic health field.

- `boot_health_report_digest` is the typed join for richer gate detail.
- `boot_bless_receipt_digests` are the typed join for the exact good/bad finalization decision.

That keeps “what the checks said” and “what decision committed or rolled back the boot” separately explainable.

### 4) Include boot-assessment proof when it materially shaped the story

The rule is intentionally conditional.
The archive does **not** require every incident bundle to include every historical `boot.bless.receipt`.
Instead, bundles should carry `boot_bless_receipt_digests` when health-gated finalization, rollback, or repeated failed boots materially participated in or shaped the incident/support story.

Examples:

- a fleet rollout halted because hosts failed health-gated finalization after reboot,
- a workstation support case needs to prove whether the new generation was actually committed or rolled back,
- a general-purpose install needs to tie a post-update failure to one explicit boot-assessment decision instead of a support engineer reading loader counters,
- or an appliance/factory incident needs to prove which exact post-boot gate decision justified rollback or escalation during an audit window.

### 5) Loader counters and status text remain side aids, not official truth

This boundary does not promote BLS counter state, greenboot status output, updater dashboards, or console screenshots into the official bundle truth model.
Those aids may still exist as auxiliary review material, but the default support-handoff join stays digest-first:

- exact `boot.bless.receipt` digest,
- with the receipt itself carrying the decision and correlation,
- and optional `boot_health_report_digest` providing the richer gate detail.

That keeps operator aids and official support/export truth separate.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove which exact boot-assessment decision committed or rolled back a cohort member instead of normalizing greenboot status text, dashboard output, or loader-state inspection as the official evidence.

### B / secure workstation

Workstation support handoff can now export one exact `boot.bless.receipt` when the user or support flow needs to know whether the tentative generation was really committed or automatically rolled back.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed health-gated story explicit in bundles without pretending every classic updater or loader helper inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes can now answer what exact boot-assessment decision shaped the incident handoff without collapsing the story into boot-counter dumps, console captures, or ticket notes.

## Guardrail

- `tools/check_boot_bless_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces keep `boot.bless.receipt` proof explicit, that the canonical bundle example binds the real `boot.bless.receipt` example digest, and that the relevant docs keep teaching the same health-gated/support-bundle story.

## What remains open

This doc does **not** fix:

- the exact UI for previewing boot-health reports before export,
- whether every bundle template enables the selector by default,
- whether future support handoffs should carry more than one `boot.bless.receipt`,
- or the final implementation detail of any one boot counter backend.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention health-gated finalization only in prose while hand-waving the exact `boot.bless.receipt` decision artifact.

Last updated: 2026-03-21r363
