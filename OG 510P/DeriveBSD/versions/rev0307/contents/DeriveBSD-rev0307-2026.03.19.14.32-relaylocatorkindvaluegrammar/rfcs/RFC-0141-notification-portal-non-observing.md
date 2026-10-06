# RFC-0141: Notification portal (non-observing)

Status: **Draft**  
Last updated: 2026-02-24

## Problem

Apps need notifications.
But if apps can observe presentation/click/dismissal, notifications become a side-channel and a surveillance channel.
If notifications are ambient, they become spam/DoS.

DeriveBSD needs a first-class, capability-mediated, **non-observing** notification service.

## Proposal

Add an optional Notification portal lane:

- a host broker accepts publish/withdraw requests
- policy enforces:
  - rate limits / quotas
  - category allowlists and priority ceilings
  - persistence limits
  - activation behavior constraints
- the workload receives no feedback about whether the notification was shown
- clicks route through intent routing/activation (receipted)

## Spec objects

- `ui.notification.grant` (optional; may be provisioned in the initial capset)
- `ui.notification.receipt`

See: `docs/206-notification-portal-non-observing.md`.

## Prior art

- XDG Desktop Portal Notification interface is explicitly non-observing.
  https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Notification.html

## Open questions

- how to represent “critical” notifications that require explicit allow
- how to handle notification persistence across upgrades/replacements of the app artifact
- what fields must be stable for policy matching (category strings vs typed enums)
