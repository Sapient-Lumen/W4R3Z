# Incident bundles carry lease-snapshot authority context by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, reproducibility  
**Patterns:** Broker→Lease→Receipt, Bundles  

DeriveBSD already decided that temporary authority should be bounded, typed, and queryable.
This doc fixes the smaller but implementation-shaping support/export question the archive still left fuzzy in practice:

**how does the official incident/support bundle contract name the exact `lease.snapshot` that says what temporary authority was still live at capture time?**

The answer is intentionally narrow.
It is not a new authority-debug subsystem and not a generic bastion dump.
It is the missing decision to make the existing lease snapshot joinable through the official support-handoff contract.

See also:
- ADR: `adrs/ADR-0226-incident-bundles-carry-lease-snapshot-authority-context-by-digest.md`
- lease registry: `docs/249-lease-registry-and-cross-lane-revocation.md`
- lease envelopes: `docs/252-lease-envelope-and-cross-lane-joins.md`
- lease evidence receipts: `docs/449-lease-issue-and-use-receipts.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- bundle plans: `docs/253-bundle-plans-and-deterministic-exports.md`
- evidence spine: `docs/229-evidence-spine-overview.md`

## Why this needs a hard decision

The lease lane already existed:

- `lease.envelope` gives a cross-lane join surface,
- `lease.issue.receipt` and `lease.use.receipt` keep issuance and use explainable,
- `lease-revoke-event` keeps revocation explicit,
- and `lease-snapshot` is already the safe metadata surface for “what authority is live?”.

But the official support/export contract still lagged behind that design in practice.
`incident.bundle` could already carry `lease_snapshot_digest`, and canonical bundle plans already exercised `lease_snapshot`, but the archive still did not explicitly teach that support handoff should use that typed join when live temporary authority materially shaped the incident.

A coherent archive should let support bundles answer two different questions distinctly:

- **what exact bounded support/operator/breakglass/secret actions participated?**
- **what temporary authority was still live at capture time, even if it had not yet been exercised?**

## Accepted boundary

### 1) Bundles may carry exact temporary-authority context

Support bundles should not force readers to infer live authority from bastion dashboards, control-plane screenshots, operator memory, or chat archaeology.

- `lease_snapshot_digest` names the exact `lease.snapshot` object that belongs to the incident.
- The referenced `lease.snapshot` remains the place that lists the bounded live leases and their metadata-only scope at capture time.

That keeps the official support contract compact while still naming the canonical temporary-authority context.

### 2) The official selector is now treated as real

The canonical include surface already carries `lease_snapshot`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same typed selector applies both when planning a support bundle and when recording what the final bundle included.

That keeps live-authority context on the official support-bundle lane instead of buried in `extra`, dashboards, or ticket prose.

### 3) Keep current live-authority context separate from participation proof

This is the design cut worth preserving.
The archive does **not** collapse all temporary-authority evidence into one generic field.

- `support_session_digests`, `operator_session_digests`, `breakglass_receipt_digests`, `secret_receipt_digests`, and related fields prove which exact bounded actions or sessions participated.
- `lease_snapshot_digest` is the typed join for what temporary authority was still live at capture time.

That keeps “what exact bounded session/action happened” and “what temporary authority was still live” separately explainable.

### 4) Include snapshot context when it materially shaped the story

The rule is intentionally conditional.
The archive does **not** require every incident bundle to include every `lease.snapshot`.
Instead, bundles should carry `lease_snapshot_digest` when live temporary authority materially participated in or shaped the incident/support story.

Examples:

- a fleet incident needs to show that a breakglass lease was still live when rollback and support capture happened,
- a workstation support case needs to show that a support-session authority window or secret-materialization lease was still open when the user exported a bundle,
- a general-purpose install needs to tie confusing follow-on behavior to one still-live temporary grant instead of a responder reconstructing it from shell history,
- or an appliance/factory handoff needs to prove what temporary operator or maintenance authority remained live when a regulated export or field replacement decision was made.

### 5) Side dashboards remain stronger side evidence

This boundary does not promote bastion dashboards, control-plane screenshots, or chat notes into the official bundle truth model.
Put differently: keep those aids out of the routine support-handoff truth surface.
Those aids may still exist as auxiliary review material, but the default support-handoff join stays digest-first:

- exact `lease.snapshot` digest for live temporary-authority context,
- plus exact session/receipt digests for the individual bounded actions that participated.

That keeps operator aids and official support/export truth separate.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove what temporary support/operator/breakglass authority was still live when capture happened instead of normalizing control-plane dashboards or operator notes as the official evidence.

### B / secure workstation

Workstation support handoff can now export one exact `lease.snapshot` when the user or support flow needs to explain what temporary authority window was still open instead of making support infer it from helper UIs or chat history.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed temporary-authority story explicit in bundles without pretending every foreign bastion, support tool, or admin dashboard inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes can now answer what live temporary authority surrounded the incident handoff without collapsing the story into screenshots, ticket notes, or bench folklore.

## Guardrail

- `tools/check_lease_snapshot_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces keep live temporary-authority context explicit, that the canonical bundle example binds the real `lease.snapshot` example digest, and that the relevant docs keep teaching the same lease/support-bundle story.

## What remains open

This doc does **not** fix:

- the exact UI for previewing live temporary-authority context before export,
- whether every bundle template enables `lease_snapshot` by default,
- whether future support handoffs should join specific `lease.envelope` digests in addition to the snapshot,
- or broader support-handoff joins for richer bastion or control-plane diagnostics.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention temporary authority only in prose while hand-waving the exact `lease.snapshot` context.

Last updated: 2026-03-21r366
