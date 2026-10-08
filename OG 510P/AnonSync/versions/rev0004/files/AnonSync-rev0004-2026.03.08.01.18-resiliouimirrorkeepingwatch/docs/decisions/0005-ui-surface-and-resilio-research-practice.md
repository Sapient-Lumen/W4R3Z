# 0005 — UI surface and Resilio research practice

- status: accepted
- date: 2026-03-08

## Context

AnonSync aims to be close in spirit and day-to-day usability to Resilio Sync, not just vaguely inspired by it. The desktop and mobile product surface therefore needs to be treated as first-class architecture, not as a late veneer.

The project also needs a durable anti-amnesia habit: whenever user-facing behavior is changed, the archive should revisit what Resilio currently documents and what its change log suggests they learned the hard way.

## Decision

AnonSync accepts the following UI and research posture:

- UI is a first-class workstream from now on.
- A shared **local-web product surface** is acceptable for both desktop and mobile, provided packaging keeps the experience sealed and noob-safe.
- The default information architecture should intentionally track Resilio's proven shape where practical:
  - desktop main view centered on folders, peers, history, search, filter, status, and settings
  - a share flow centered on link or QR invite exchange, permission choice, and security options
  - per-folder preferences for sync, archive, discovery, and network policy
  - mobile selective-sync / placeholder-first behavior with simple per-share network controls
- Product/UI work should **tend to copy Resilio's flow and semantics** unless AnonSync has a concrete anonymity, transport, or mobile reason to diverge.
- The archive must maintain a recurring **Resilio comparison and change-tracking practice**. Product-facing revisions should revisit the current Resilio docs and change log before making major UX claims.

## Consequences

- UI architecture notes and product IA docs now belong in the repo early, not later.
- Future revisions should keep desktop and mobile views in the same conceptual model unless a divergence is deliberate.
- Product-facing design notes should explain when AnonSync is copying Resilio, when it is abstracting transport complexity, and when it is diverging for anonymity or mobile constraints.
- Research notes should record meaningful Resilio UI changes so the archive does not drift into stale imitation.
