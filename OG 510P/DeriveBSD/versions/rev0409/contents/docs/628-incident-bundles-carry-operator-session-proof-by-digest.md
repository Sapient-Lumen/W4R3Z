# Incident bundles carry operator-session proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, reproducibility  
**Patterns:** Plan→Apply→Receipt, Bundles, Capsule  

DeriveBSD already decided that operator access is a typed evidence lane and that `operator.session` is the bounded privileged-session envelope.
This doc fixes the smaller but implementation-shaping support/export question the archive still left open:

**how does the official incident/support bundle contract name the exact operator session when privileged admin work actually participated in the story?**

The answer is intentionally narrow.
It is not a new admin subsystem and not a new product-profile key.
It is the missing digest join between the existing `operator.session` artifact and the existing support-bundle contract.

See also:
- ADR: `adrs/ADR-0218-incident-bundles-carry-operator-session-proof-by-digest.md`
- operator-access lane: `docs/311-operator-access-leases-and-ssh-certs.md`
- operator recording/detail posture: `docs/617-operator-access-recording-detail-and-export-posture-by-profile.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`

## Why this needs a hard decision

`docs/311-operator-access-leases-and-ssh-certs.md` already fixed the core lane shape:

- `operator.session` is the session envelope,
- it points at lease, identity, scope, and optional TTY-recording evidence,
- and adjacent publication/maintenance flows can already join to exact operator-session authority through `operator_session_digest`.

But the official support/export contract still lagged behind that decision.
`incident.bundle` had room for event windows, trust-view proof, restore proof, remote-assistance proof, and packet-capture joins, but not for the exact `operator.session` digest itself.

That is expensive because it quietly pushes responders back toward ticket notes, bastion dashboards, shell transcripts, or portal archaeology right after the archive had already paid to define a better answer.

A coherent archive should let support bundles answer both:

- **did privileged operator work participate?**
- **which exact bounded operator session was it?**

## Accepted boundary

### 1) Bundles carry the session envelope, not just its side receipts

Support bundles should not force readers to reconstruct privileged operator work from the receipts the session referenced.

- `operator_session_digests` name the exact `operator.session` object(s) that belong to the incident.
- The referenced `operator.session` object remains the place that points at lease, identity, scope, and optional TTY-recording evidence.

This keeps the official bundle contract compact while still naming the one canonical session envelope.

### 2) The official selector is now typed

The canonical include surface now carries `operator_sessions`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same selector works both when planning a bundle and when recording what the final bundle included.

That keeps privileged admin participation on the official support-bundle lane instead of in `extra`, bastion-private notes, or collector-private rules.

### 3) Include session proof when operator work matters

The rule is intentionally conditional.
The archive does **not** require every incident bundle to include every historical operator session.
Instead, bundles should carry `operator.session` digests when privileged admin work participated in or materially shaped the incident/support story.

Examples:

- a fleet issue was investigated or mitigated through a brokered operator shell before the fault snapshot was captured,
- a workstation incident needs to prove which exact remote or breakglass operator session changed host policy,
- a general-purpose install used a Derive-managed admin session alongside restore or trust-view changes and the bundle should tie those actions to one exact session envelope,
- or an appliance/factory handoff needs to prove whether an approved maintenance operator session participated in the incident window.

### 4) bastion-private notes remain stronger/debugging evidence

This boundary does not promote bastion dashboards, chat notes, or vendor-specific admin portals into the official bundle truth model.
Free-text notes or product-private session summaries may still exist as explicit stronger/debugging evidence, but the default support-bundle join stays digest-first:

- exact `operator.session` digest,
- with the session envelope itself pointing at its subordinate lease/TTY receipts,
- and optional event/export joins pointing at the same session proof.

That keeps bastion tooling and support/export truth separate.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove whether brokered operator access actually participated in the failure or mitigation story without normalizing bastion dashboards as the truth surface.

### B / secure workstation

Workstation incident and recovery handoff can now export one exact operator-session envelope instead of making support reconstruct privileged host changes from TTY recordings or ticket notes alone.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed operator story explicit in bundles without pretending every foreign bastion inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes can now answer whether an approved maintenance operator session participated in the incident window without collapsing the whole story into portal screenshots or bench folklore.

## Guardrail

- `tools/check_operator_session_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces carry operator-session proof explicitly, that the canonical bundle example binds the real `operator.session` example digest, and that the relevant docs keep teaching the same operator-access-versus-bundle story.

## What remains open

This doc does **not** fix:

- the exact UI for previewing operator-session participation before export,
- whether every bundle template enables the selector by default,
- the richer export path for TTY recordings or bastion-private diagnostics,
- or any richer breakglass console/TTY export path.

The metadata-first breakglass authority join is now decided separately in `docs/629-incident-bundles-carry-breakglass-proof-by-digest.md`.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention privileged operator work only in prose while hand-waving the exact `operator.session` envelope.

Last updated: 2026-03-21r359
