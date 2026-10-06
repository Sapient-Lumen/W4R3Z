# Incident bundles carry support-session proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, reproducibility  
**Patterns:** Plan→Apply→Receipt, Bundles, Capsule  

DeriveBSD already decided that remote assistance is a typed evidence lane and that `support.session` is the bounded session envelope.
This doc fixes the smaller but implementation-shaping support/export question the archive still left open:

**how does the official incident/support bundle contract name the exact remote-assistance session when help actually participated in the story?**

The answer is intentionally narrow.
It is not a new support subsystem and not a new product-profile key.
It is the missing digest join between the existing `support.session` artifact and the existing support-bundle contract.

See also:
- ADR: `adrs/ADR-0217-incident-bundles-carry-support-session-proof-by-digest.md`
- remote-assistance lane: `docs/291-remote-assistance-sessions-as-evidence.md`
- remote-assistance recording/detail posture: `docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`

## Why this needs a hard decision

`docs/291-remote-assistance-sessions-as-evidence.md` already fixed the core lane shape:

- `support.session` is the session envelope,
- it points at consent/UI/network/recording/export evidence,
- and relay-backed support-peer publication already joins to exact support-session authority through `authority.support_session_digest`.

But the official support/export contract still lagged behind that decision.
`incident.bundle` had room for event windows, trust-view proof, restore proof, and packet-capture joins, but not for the exact `support.session` digest itself.

That is expensive because it quietly pushes responders back toward ticket notes, helper dashboards, chat transcripts, or shell archaeology right after the archive had already paid to define a better answer.

A coherent archive should let support bundles answer both:

- **did remote assistance participate?**
- **which exact bounded support session was it?**

## Accepted boundary

### 1) Bundles carry the session envelope, not just its side receipts

Support bundles should not force readers to reconstruct remote assistance from the receipts the session referenced.

- `support_session_digests` name the exact `support.session` object(s) that belong to the incident.
- The referenced `support.session` object remains the place that points at consent/UI/network/recording/export receipts.

This keeps the official bundle contract compact while still naming the one canonical session envelope.

### 2) The official selector is now typed

The canonical include surface now carries `support_sessions`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same selector works both when planning a bundle and when recording what the final bundle included.

That keeps remote-assistance participation on the official support-bundle lane instead of in `extra` or collector-private rules.

### 3) Include session proof when remote assistance matters

The rule is intentionally conditional.
The archive does **not** require every incident bundle to include every historical support session.
Instead, bundles should carry `support.session` digests when remote assistance participated in or materially shaped the incident/support story.

Examples:

- a fleet issue was debugged through a brokered helper session before the fault was captured,
- a workstation support case needs to prove which exact remote helper session the user approved,
- a general-purpose install used remote assistance plus a support-peer publish session and the bundle should tie both to one exact session envelope,
- or an appliance/factory handoff needs to prove whether a maintenance help session participated in the incident window.

### 4) helper-private notes remain stronger/debugging evidence

This boundary does not promote helper dashboards, chat notes, or vendor-specific session portals into the official bundle truth model.
Free-text notes or product-private session summaries may still exist as explicit stronger/debugging evidence, but the default support-bundle join stays digest-first:

- exact `support.session` digest,
- with the session envelope itself pointing at its subordinate receipts,
- and optional event/export joins pointing at the same session proof.

That keeps helper tooling and support/export truth separate.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove whether brokered remote assistance actually participated in the failure or recovery story without normalizing helper dashboards as the truth surface.

### B / secure workstation

Workstation support cases can now export one exact user-approved `support.session` envelope instead of making support reconstruct who helped whom from UI receipts or ticket notes.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed remote-assistance story explicit in bundles without pretending every foreign helper inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes can now answer whether a maintenance help session participated in the incident window without collapsing the whole story into portal screenshots or bench folklore.

## Guardrail

- `tools/check_support_session_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces carry support-session proof explicitly, that the canonical bundle example binds the real `support.session` example digest, and that the relevant docs keep teaching the same remote-assistance-versus-bundle story.

## What remains open

This doc does **not** fix:

- the exact UI for previewing remote-assistance participation before export,
- whether every bundle template enables the selector by default,
- the richer export path for recordings or helper-private diagnostics,
- or any breakglass-specific bundle join. Operator-session proof is now decided separately in `docs/628-incident-bundles-carry-operator-session-proof-by-digest.md`.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention remote assistance only in prose while hand-waving the exact `support.session` envelope.

Last updated: 2026-03-21r358
