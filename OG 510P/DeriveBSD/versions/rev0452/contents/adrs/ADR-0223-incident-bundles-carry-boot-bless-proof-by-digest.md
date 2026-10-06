# ADR-0223: Incident bundles carry boot-bless proof by digest

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/112-health-gated-updates.md`, `docs/241-boot-try-counters-and-boot-assessment.md`, and `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md` already fixed the update-finalization side of the boot lane:

- `boot.health.report` is the richer report of required/wanted checks and evidence,
- `boot.bless.receipt` is the typed decision about whether a tentative boot was committed or treated as bad,
- and A/B-style or health-gated delivery only becomes real when that decision is explicit and receipted.

The official incident/support-bundle contract still lagged behind that decision.
`incident.bundle` could already carry `boot_health_report_digest`, but the archive still did not treat the exact `boot.bless.receipt` as official support-handoff proof when health-gated finalization or rollback materially shaped the incident.

That omission is expensive because it quietly blurs together three different questions:

- what health evidence the gate evaluated (`boot.health.report`),
- what exact boot-assessment decision was made (`boot.bless.receipt`),
- and what updater or bootloader counters happened to show on a dashboard, serial console, or helper log.

Without an explicit join, responders drift back toward greenboot status text, boot-counter folklore, loader-specific state inspection, or ticket prose.
That re-opens the exact entropy the archive already paid to close for restore, operator, breakglass, firmware-update, firmware-drift, and UEFI-variable proof.

We do **not** need a larger boot subprotocol or a generic “boot finalization blob.”
We need the already-existing support-handoff contract to name the exact bounded `boot.bless.receipt` artifact when that decision materially shaped the incident story.

## Decision

**Incident/support bundles may carry boot-assessment/finalization proof by typed digest join.**

Specifically:

1. Keep health evidence and finalization decision distinct.
   - `boot_health_report_digest` continues to point at the richer `boot.health.report` when that report belongs in the bundle.
   - `boot_bless_receipt_digests` point at the exact `boot.bless.receipt` objects when health-gated finalization, rollback, or repeated failed boots materially shaped the incident/support story.

2. Keep the selector real.
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` already carries `boot_bless_receipts`.
   - `bundle.plan.selection.include` must exercise that selector when the support handoff needs exact boot-assessment/finalization proof, not just the richer report or a later ticket summary.

3. Keep boot-assessment proof distinct from boot-health evidence.
   - `boot_health_report_digest` remains the typed join for richer gate input/output detail.
   - `boot_bless_receipt_digests` are the typed join for the exact good/bad commit decision.
   - This avoids re-collapsing “what checks ran” and “what decision committed or rolled back the boot” into one generic boot-health field.

4. Keep the rule conditional and narrow.
   - Bundles should include `boot_bless_receipt_digests` when health-gated finalization, rollback, or boot-assessment state materially participated in the incident/support story.
   - This does not mean every bundle must always include every historical boot-assessment decision.

5. Keep adapter counters and helper logs as side workflow, not official truth.
   - This ADR does not bless bootloader counters, greenboot status lines, console captures, or updater dashboards as the canonical support-handoff proof.
   - Those remain auxiliary aids unless they produce or reference the typed `boot.bless.receipt` object.

## Consequences

- Support bundles can now answer both **what health evidence was evaluated** and **what exact boot-assessment/finalization decision was made**.
- Health-gated updates stay on the same digest-first evidence graph as change receipts, rollouts, and incident bundles.
- The official support handoff no longer forces responders to infer the decisive boot commit/rollback outcome from bootloader state, dashboard text, or ticket prose.
- `bundle.plan` / `incident.bundle` remain the one official bundle-selection and metadata contract for this health-gated boot-finalization lane too.

## What this does not decide

This ADR does **not** decide:

- the final UI for previewing boot-health reports before export,
- whether every health-gated bundle template enables `boot_bless_receipts` by default,
- whether bundles should include multiple historical `boot.bless.receipt` objects in future,
- or the final implementation detail of any one boot counter backend.

It only makes the already-existing decision artifact (`boot.bless.receipt`) joinable through the official incident/support-bundle contract.
