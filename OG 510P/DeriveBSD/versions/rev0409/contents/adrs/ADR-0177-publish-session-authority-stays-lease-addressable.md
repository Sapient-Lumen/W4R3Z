# ADR-0177: Publish-session authority stays lease-addressable

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 introduced `net.publish.session` so temporary sharing could stop collapsing into shadow
tunnels or casual public listeners.
ADR-0154 then made those shares reboot-cleared and explicitly bounded.
ADR-0176 then fixed the authority lane so `authority.trigger` and the joined digest family tell one
singular story.

One smaller but still expensive ambiguity remained in that same authority object:

**if temporary sharing is leased, what keeps the receipt from omitting the actual lease handle and
forcing revoke/query/support tooling to rediscover the share through looser timestamp, endpoint, or
operator-session clues?**

Without one more narrow decision, publish sessions can still be bounded in prose yet omit the one
compact identifier that lease registries, support bundles, revocation flows, and forensic queries use
to say *which temporary authority instance are we talking about?*

DeriveBSD does not need a larger maintenance-window object or richer sharing transaction here, but it
does need every publish session to stay addressable through the same lease vocabulary the rest of the
archive already uses for bounded authority.

## Decision

1. `net.publish.session.authority.lease_id` is now required for every publish session.

2. That lease handle is the compact cross-lane answer for:
   - revoking the still-live temporary share,
   - correlating the share with other lease-shaped evidence,
   - and naming the bounded authority instance in support/export/forensics.

3. `authority.trigger` and any joined digest fields still explain **why** the share was allowed.
   `lease_id` explains **which bounded temporary authority instance** remained in force.

4. This ADR does **not** invent a new maintenance-window evidence object, richer revocation object,
   or broader lease registry schema for publish sessions.
   It only makes the existing leased temporary-sharing story mechanically present in every receipt.

## Consequences

- Temporary publish sessions now stay easy to revoke/query without scraping hostnames, relay hints,
  timestamps, or operator-session folklore.
- Support bundles can now name the bounded share instance directly even when the share lane is
  trusted-UI, policy, operator-session, support-session, or future maintenance-window shaped.
- The authority surface becomes more coherent: `expires_at` no longer appears without the companion
  lease identifier that makes that bounded window operational.

## Alternatives considered

- **Leave `lease_id` optional beside `expires_at`.** Rejected because it keeps leased temporary
  sharing only half-addressable and pushes revocation/support back toward heuristics.
- **Infer the lease handle from other joined evidence.** Rejected because consent, policy,
  operator-session, and support-session receipts explain authorization, not the publish-session lease
  instance itself.
- **Invent a richer publish-session revocation transaction now.** Rejected as too wide for this
  round.
