# ADR-0293: Crypto compatibility agents stay local-session projections and not ambient remote authority

- Status: Accepted
- Date: 2026-03-23

## Context

`docs/462-private-key-and-crypto-op-posture-by-profile.md` already fixed the large product-default question:
DeriveBSD prefers brokered, non-exportable crypto operations over raw private-key files.

But one costly implementation loophole remained open in `docs/266-open-questions-and-risk-register.md`:

> how do remembered approvals and classic `ssh-agent` / `gpg-agent` compatibility paths map onto leases without silently recreating ambient signing authority?

If the archive leaves that vague, the product drifts back toward the very thing the broker model was meant to replace:

- risky compartments talking to long-lived compatibility sockets as if they *were* the authority object
- remembered prompts stretching across unrelated sessions because the agent happened to stay alive
- remote forwarding being treated as convenience first and reviewable authority second

The archive already had the right pieces:

- `crypto.op.request` / `crypto.op.receipt`
- lease-bound temporary authority
- explicit adapter lanes for legacy interop

What was missing was one typed boundary for compatibility agents.

## Decision

1. **Compatibility agents are projections, not authority.**
   Classic `ssh-agent` and `gpg-agent` sockets may exist only as adapters over the brokered crypto path.
   They do not become the reviewed authority object.

2. **The baseline projection scope is `local-session-only`.**
   A compatibility projection is valid only for the current local session surface that created it.
   It is not a durable host-global capability.

3. **Remembered approvals stay `same-lease-only`.**
   Any approval remembered through a compatibility path is bounded to the exact active lease.
   A later lease, reboot, reconnect, or separately forwarded session must ask again.

4. **Remote agent forwarding is not the reviewed baseline.**
   The archive does not treat forwarded compatibility sockets as the normal authority model.
   If a future remote-use lane is worth standardizing, it must be explicit and separately typed.

5. **Typed projection metadata belongs on request/receipt surfaces.**
   `crypto.op.request` and `crypto.op.receipt` may carry a `compatibility_projection` object with:
   - `adapter_protocol`
   - `projection_scope`
   - `remembered_approval_scope`

## Consequences

- Compatibility remains possible for legacy tools without letting legacy transport shape redefine DeriveBSD authority.
- Support and forensics can tell whether an operation came through a projection path and what its bounded scope was.
- Workstation convenience remains possible, but the archive no longer leaves “ambient local agent forever” as the accidental default.
- Remote/fleet/factory product shapes keep a safer floor because classic forwarding folklore is no longer implicitly blessed.

## Why this is narrow enough

This ADR does **not** decide:

- the final UI for local approval prompts
- exact receipt-detail defaults by profile
- which key classes require quorum by default
- any future explicit remote projection lane

It only closes the smallest high-leverage loophole that would otherwise hollow out the crypto broker model:
compatibility exists, but only as a local-session projection with same-lease remembered approval.
