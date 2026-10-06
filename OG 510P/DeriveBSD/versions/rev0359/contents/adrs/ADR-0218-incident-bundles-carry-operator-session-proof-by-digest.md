# ADR-0218: Incident bundles carry operator-session proof by digest

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/311-operator-access-leases-and-ssh-certs.md` and `spec/operator.session.schema.json` already made privileged operator access a typed evidence lane:

- `operator.session` is the bounded admin/session envelope,
- it points at lease, identity, scope, and optional TTY-recording evidence,
- and adjacent admin/share flows already join to exact `operator_session_digest` authority when publication or maintenance actions are bounded by one operator session.

That still left one practical support/export gap:
**the official incident/support bundle contract could talk about privileged admin work in prose, but it still had no typed place for the `operator.session` digest itself.**

That omission is expensive because it quietly re-opens the same folklore boundary the archive already paid to close:

- incident bundles can say that operator work mattered without naming the exact bounded admin session envelope,
- responders fall back to bastion dashboards, ticket notes, shell logs, or portal metadata about who did the work,
- TTY-recording / lease / approval evidence can no longer compose cleanly into the final support handoff artifact,
- and operator-access evidence starts drifting back into "whatever the bastion recorded" rather than the official bundle contract.

The archive already has the right pattern for this.
We do **not** need a new admin subsystem.
We need the official incident-bundle selector and metadata surfaces to carry the typed operator-session join by digest.

## Decision

**Incident/support bundles may carry operator-session proof by typed digest joins.**

Specifically:

1. Extend the canonical bundle include-knob surface.
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` must carry `operator_sessions`.
   - Because `bundle.plan.selection.include` reuses that shape, official bundle planning inherits the same selector automatically.

2. Extend the canonical bundle metadata surface.
   - `incident.bundle.includes` must carry `operator_session_digests`.
   - These digests point at `operator.session` objects, not at bastion-private notes, dashboards, or shell transcripts.

3. Keep session proof distinct from the receipts/artifacts the session itself references.
   - `operator_session_digests` identify the exact bounded privileged operator session(s) that belong to the incident.
   - The referenced `operator.session` object remains the place that points at lease, identity, scope, and optional TTY-recording evidence.
   - This keeps the incident bundle compact while preserving one canonical session envelope join.

4. Keep the rule conditional and narrow.
   - Incident bundles should include `operator_session_digests` when privileged admin work materially participated in the incident/support story.
   - This does not mean every bundle must always include every historical operator session.

5. Do not flatten operator and support/breakglass lanes together.
   - This ADR only fixes the `operator.session` join for privileged operator/admin work.
   - It does not decide any new breakglass bundle join.

## Consequences

- Support bundles can now answer **whether privileged operator access participated** and **which exact session envelope bounded it**.
- The official support handoff stays aligned with the existing operator-access lane instead of partially undoing it.
- `bundle.plan` / `incident.bundle` remain the one official bundle-selection and metadata contract for this evidence lane too.
- Operator-session-bound publication or maintenance flows now compose cleanly with final support handoff because both can point at the same exact `operator.session` digest.

## What this does not decide

This ADR does **not** decide:

- the final UI for previewing operator-session participation in support tooling,
- whether every bundle template enables the selector by default,
- any richer export path for TTY recordings or bastion-private diagnostics,
- or any breakglass-specific bundle join.

It only fixes the missing typed join between the already-decided `operator.session` artifact and the already-decided incident/support bundle contract.
