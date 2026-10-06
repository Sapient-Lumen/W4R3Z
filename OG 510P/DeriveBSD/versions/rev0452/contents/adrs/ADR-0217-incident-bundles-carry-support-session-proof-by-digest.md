# ADR-0217: Incident bundles carry support-session proof by digest

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/291-remote-assistance-sessions-as-evidence.md` and `spec/support.session.schema.json` already made remote assistance a typed evidence lane:

- `support.session` is the session envelope,
- it points at consent/UI/network/recording/export evidence,
- and relay-backed support-peer publication already joins to exact support-session authority through `authority.support_session_digest`.

That still left one practical support/export gap:
**the official incident/support bundle contract could talk about remote assistance in prose, but it still had no typed place for the `support.session` digest itself.**

That omission is expensive because it quietly re-opens the same folklore boundary the archive already paid to close:

- incident bundles can say that remote assistance mattered without naming the exact bounded session envelope,
- responders fall back to ticket notes, chat transcripts, or collector-private metadata about who helped whom,
- the relay-backed `support_session_digest` join cannot compose cleanly into the final support handoff artifact,
- and remote-assistance evidence starts drifting back into "whatever the helper tool logged" rather than the official bundle contract.

The archive already has the right pattern for this.
We do **not** need a new support subsystem.
We need the official incident-bundle selector and metadata surfaces to carry the typed support-session join by digest.

## Decision

**Incident/support bundles may carry support-session proof by typed digest joins.**

Specifically:

1. Extend the canonical bundle include-knob surface.
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` must carry `support_sessions`.
   - Because `bundle.plan.selection.include` reuses that shape, official bundle planning inherits the same selector automatically.

2. Extend the canonical bundle metadata surface.
   - `incident.bundle.includes` must carry `support_session_digests`.
   - These digests point at `support.session` objects, not at collector-private notes or helper-tool dashboards.

3. Keep session proof distinct from the receipts/artifacts the session itself references.
   - `support_session_digests` identify the exact bounded remote-assistance session(s) that belong to the incident.
   - The referenced `support.session` object remains the place that points at consent/UI/network/recording/export receipts.
   - This keeps the incident bundle compact while preserving one canonical session envelope join.

4. Keep the rule conditional and narrow.
   - Incident bundles should include `support_session_digests` when remote assistance participated in the incident/support story.
   - This does not mean every bundle must always include every historical support session.

5. Do not flatten remote assistance and operator/breakglass lanes together.
   - This ADR only fixes the `support.session` join for remote assistance.
   - It does not decide any new `operator.session` or breakglass bundle join.

## Consequences

- Support bundles can now answer **whether remote assistance participated** and **which exact session envelope bounded it**.
- The official support handoff stays aligned with the existing remote-assistance lane instead of partially undoing it.
- `bundle.plan` / `incident.bundle` remain the one official bundle-selection and metadata contract for this evidence lane too.
- Relay-backed support publication now composes cleanly with final support handoff because both can point at the same exact `support.session` digest.

## What this does not decide

This ADR does **not** decide:

- the final UI for previewing remote-assistance participation in support tooling,
- whether every bundle template enables the selector by default,
- any richer export path for recordings or helper-specific diagnostics,
- or any new operator-session bundle join.

It only fixes the missing typed join between the already-decided `support.session` artifact and the already-decided incident/support bundle contract.
