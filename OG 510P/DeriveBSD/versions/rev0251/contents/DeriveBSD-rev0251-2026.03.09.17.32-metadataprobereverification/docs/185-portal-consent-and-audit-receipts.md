# Portal consent + audit receipts (make "ask" explainable)

Portals/powerbox brokers keep capability sandboxes usable by allowing **mediated** dynamic access.

The trap: once you add an interactive "ask" path, you often lose explainability:
- *Who approved it?*
- *What exactly did they approve?*
- *Was this a one-shot or a lasting grant?*
- *Would the same prompt appear after an upgrade?*

This doc proposes a small, optional primitive: **consent receipts**.


For long-lived sessions and “remember my choice” storage, see: `docs/210-portal-sessions-and-permission-store.md`.

## Lesson to steal

Desktop sandboxes (e.g. Flatpak) converged on **portals**: a well-known broker API that can route decisions to a UI backend.
The portal service is separate from the sandbox, and the approval flow is mediated.

DeriveBSD should steal the separation (broker API ↔ UI backend) but also add what workstation stacks often lack: *receipt-quality audit trails*.

## Proposed contract

### 1) Consent is a structured event

If a portal decision is made via interactive "ask", the portal should emit:

- `portal.consent` (a receipt)
- and then (if allowed) the normal `portal.grant`

Receipts are content-addressed, signed, and safe to store.
They must never contain secret bytes; they may contain:
- request digest
- prompt template id/version
- user identity (local uid + optional human label)
- decision (allow/deny)
- constraints applied (ttl, rights, scope)

Schema sketch: `spec/portal.consent.schema.json`.

### 2) Prompt text must be versioned

To prevent "prompt drift" (meaning changes across updates), the UI backend should reference a **prompt template id** and version.
Receipts then bind to that id+version, so audits can reconstruct what was shown.

### 3) Receipts compose with leases

If a grant creates a `lease_id`:
- the consent receipt should reference that lease id
- revocation (`portal.revoke`) remains the way to end authority early

## Why bake this in

Without receipts, the "ask" path becomes the soft underbelly of a least-authority system:
- invisible approvals
- hard-to-review exceptions
- operator folklore instead of evidence

With receipts, DeriveBSD gets:
- postmortems that can answer "who approved what"
- diff/review on *interactive* authority the same way we diff plans
- a clean interface boundary for workstation vs server deployments

## Pointers

- Portal broker: `docs/179-portals-and-powerbox.md`
- Leases + revocation: `docs/182-capability-leases-and-revocation.md`
- Explainability contract: `docs/95-explainability-contract.md`

Last updated: 2026-02-24
