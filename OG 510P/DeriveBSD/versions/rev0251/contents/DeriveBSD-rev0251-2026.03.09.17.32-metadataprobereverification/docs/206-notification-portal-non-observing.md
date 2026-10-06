# Notification portal (non-observing) as a first-class primitive

Notifications are an essential ecosystem feature (apps need to tell you something).
But they are also an information channel:
- if the app can observe presentation/dismissal/clicks, it becomes a side-channel
- if notifications are ambient, they become a spam/DoS vector

DeriveBSD should treat notifications as a **capability-mediated, non-observing** service.

## Lessons to steal

- **XDG Desktop Portal** has a Notification interface explicitly designed so:
  - sandboxed apps can send/withdraw notifications
  - the app cannot learn whether the notification was presented to the user
  - notifications may outlast the process; clicking can re-activate the app
  References:
  - https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Notification.html
  - https://sources.debian.org/src/xdg-desktop-portal/1.2.0-1/data/org.freedesktop.portal.Notification.xml

## Model

### 1) A host notification broker, not a UI library

A host-side `derive-notifyd` broker (name placeholder):

- accepts *publish* and *withdraw* requests
- enforces policy:
  - rate limits / quotas
  - category allowlists and priority ceilings
  - persistence limits (how long a notification may live)
  - activation behavior constraints
- emits **receipts** for audit and debugging

The requesting workload never speaks directly to a compositor/desktop environment.

### 2) Non-observing by default

Non-observing means:
- the workload does not learn whether a notification was shown
- the workload does not learn whether it was clicked
- the workload does not learn when/if it was dismissed

If the user clicks a notification, the resulting action should flow through **intent routing**:
- notification click → `intent.request` for activation
- handler selection + handoff is mediated (and receipted)

See: `docs/199-intent-routing-and-plumbing.md`.

### 3) “Outlast the process” is a feature, not a bug

Notifications should be durable user-facing state.
If the app exits, the notification may remain.
If the user clicks later, the app can be re-activated through the activation broker / intent router.

This makes notifications compatible with:
- crash-only services
- activation + escrow (restart-safe handles)

See: `docs/196-capability-activation-and-escrow.md`.

## Evidence objects

- `ui.notification.grant` — optional grant describing *whether* a workload may publish notifications and under what constraints.
  - in practice this can be provisioned as part of the initial capset
- `ui.notification.receipt` — host-issued record that a publish/withdraw occurred (for auditing and reproducibility)

Schemas:
- `spec/ui.notification.grant.schema.json`
- `spec/ui.notification.receipt.schema.json`

## Practical ergonomics (so people use it)

- apps should treat notifications as “fire-and-forget”; no feedback loops
- provide a CLI tool (`derive-notify`) for terminals
- expose a host-level “notification center” UI that is clearly outside the sandbox
- policy should support:
  - per-app quotas
  - per-category limits (e.g., disallow persistent marketing spam)
  - “critical” categories that require explicit allow

See also:
- portals/powerbox: `docs/179-portals-and-powerbox.md`
- observability non-ambient philosophy: `docs/192-observability-as-capability.md`
