# Incident bundles carry breakglass proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, reproducibility  
**Patterns:** Plan→Apply→Receipt, Bundles, Capsule  

DeriveBSD already decided that breakglass is a typed evidence lane and that `breakglass.receipt` is the authoritative emergency-access authority record.
This doc fixes the smaller but implementation-shaping support/export question the archive still left loose:

**how does the official incident/support bundle contract name the exact breakglass authority record when emergency access actually participated in the story?**

The answer is intentionally narrow.
It is not a new recovery subsystem and not a new product-profile key.
It is the missing coherence pass that makes the existing `breakglass_receipts` / `breakglass_receipt_digests` join real instead of placeholder-shaped.

See also:
- ADR: `adrs/ADR-0219-incident-bundles-carry-breakglass-proof-by-digest.md`
- breakglass lane: `docs/236-breakglass-and-recovery-mode.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- breakglass recording/detail posture: `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`

## Why this needs a hard decision

The archive had already paid for most of this answer:

- `breakglass.receipt` exists,
- `incident.bundle` already had `breakglass_receipts` plus `breakglass_receipt_digests`,
- and breakglass docs already said emergency access should be auditable and should ride incident bundles.

But the final support-handoff surfaces still lagged that reality.
The canonical bundle example used a placeholder digest, `bundle.plan` did not exercise the selector, and the support-bundle docs still treated emergency-access proof as implied context rather than one exact typed join.

That is expensive because it quietly re-opens folklore:

- responders remember that breakglass happened but cannot point at the exact authority record,
- ticket notes and rescue-shell memory become the de facto truth surface,
- and richer emergency-session evidence gets mistaken for the authority record itself.

A coherent archive should let support bundles answer both:

- **did emergency access participate?**
- **which exact `breakglass.receipt` proved that authority?**

## Accepted boundary

### 1) Bundles carry the authority receipt, not console folklore

Support bundles should not force readers to reconstruct emergency access from side effects.

- `breakglass_receipt_digests` name the exact `breakglass.receipt` object(s) that belong to the incident.
- The referenced `breakglass.receipt` remains the authoritative typed record for the emergency-access act.

This keeps the official bundle contract compact while still naming the one canonical authority record.

### 2) Keep emergency authority proof separate from richer session evidence

This boundary is intentionally narrow.
`breakglass_receipt_digests` are **authority proof**, not a replacement for richer session evidence.

- terminal/console trails remain separate evidence,
- product-shaped recording/detail/export defaults still live in `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`,
- and official handoff should not flatten emergency authority proof and emergency-session bytes into one vague “recording” story.

### 3) The official selector must be exercised for real

Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same typed selector applies both when planning a support bundle and when recording what it actually included.

That means the archive should exercise `breakglass_receipts` in the canonical plan example instead of leaving the emergency-access lane half-implicit.

### 4) Include breakglass proof when emergency access mattered

The rule is conditional.
The archive does **not** require every incident bundle to include every historical breakglass record.
Instead, bundles should carry `breakglass_receipt_digests` when emergency access materially participated in the incident/support story.

Examples:

- a fleet host needed breakglass to recover a failed activation or a locked-out network posture,
- a workstation support case needs to prove that trusted-UI-visible emergency authority was exercised before a recovery action,
- a general-purpose install used a Derive-managed rescue path and the bundle should tie that act to one exact emergency authority record,
- or an appliance/factory handoff needs to prove whether approved emergency maintenance authority was invoked during the incident window.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove whether emergency access actually participated without normalizing rescue-shell folklore or bastion side notes as the truth surface.

### B / secure workstation

Workstation support export can now show one exact breakglass authority record instead of forcing support to infer emergency authority from UI screenshots or terminal snippets.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed emergency-access story explicit in bundles without pretending every foreign rescue path inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes can now answer whether approved emergency authority participated in the incident window without collapsing the whole story into bench notes or console memory.

## Guardrail

- `tools/check_breakglass_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces keep breakglass proof explicit, that the canonical bundle examples bind the real `breakglass.receipt` example digest, and that the relevant docs keep teaching the same emergency-authority-versus-session-evidence story.

## What remains open

This doc does **not** fix:

- the exact UI for previewing breakglass participation before export,
- whether every bundle template enables the selector by default,
- any richer export path for terminal/console trails,
- or any new breakglass artifact kind.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention emergency access only in prose while hand-waving the exact `breakglass.receipt` authority record.

Last updated: 2026-03-21r359
