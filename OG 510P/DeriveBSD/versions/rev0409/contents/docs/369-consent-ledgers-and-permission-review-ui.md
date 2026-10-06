# Consent ledgers and permission review UI

DeriveBSD already treats dynamic authority as mediated:
- portals for user-facing access
- brokers for network, devices, and listening
- leases and receipts for operator access

What’s still easy to miss in a greenfield design is the *user/operator ergonomics* layer:

> If authority is granted dynamically, there must be a first-class way to **review**, **revoke**, and **audit** those grants.

## Existing building blocks

- portal sessions + permission store: `docs/210-portal-sessions-and-permission-store.md`
- persistent file capabilities (“bookmarks”): `docs/198-persistent-file-capabilities-bookmarks.md`
- network/device grants: `docs/281-network-egress-broker-and-consent.md`, `docs/278-device-grants-and-devfs-rulesets.md`
- evidence spine: `docs/229-evidence-spine-overview.md`

## Proposal: a single “consent ledger” surface

A consent ledger is a derived, queryable view over:
- portal permissions
- long-lived grants (bookmarks)
- operator/broker leases

It must support:
- **review** (what does app/service X currently have?)
- **revoke** (invalidate via indirection/lease expiry)
- **explain** (how was it obtained? which UI prompt? which policy?)
- **audit** (when was it used?)

This can be implemented as:
- the canonical permission store (for portals)
- plus a normalized “ledger view” generated from receipts/events

## UI/UX principle

Every grant should have:
- a human label (resource + purpose)
- a scope (time, frequency, session, device)
- a revoke button
- an evidence link (receipt/event)

If we can’t render it in the review UI, it’s probably too implicit.

## Lessons worth stealing

- XDG Desktop Portal “permission store” concept (free-form tables keyed by app IDs):
  - https://flatpak.github.io/xdg-desktop-portal/
  - https://github.com/flatpak/xdg-desktop-portal/wiki/The-Permission-Store

- macOS “Transparency, Consent, and Control” (TCC) as a reminder that permission systems need to be operable and auditable:
  - https://www.rainforestqa.com/blog/macos-tcc-db-deep-dive

- Qubes qrexec policy ergonomics (policy as a review surface, not just scattered files):
  - https://www.qubes-os.org/news/2020/06/22/new-qrexec-policy-system/

## Wiring to DeriveBSD policy

- “Grant exists” and “grant used” should both be queryable facts.
- policy can be written against:
  - principals (app/service id)
  - resource types
  - contract digests
  - time bounds

This is how we keep portal/broker systems from turning into a pile of silent, permanent exceptions.
