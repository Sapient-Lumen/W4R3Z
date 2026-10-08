# 0005 — UI surface and information architecture

## Current stance

AnonSync should treat the product surface as a shared **local-web UI** that can be packaged for:

- desktop application shells
- NAS / headless local web access
- mobile shells or embedded web views with native affordances where needed

This is not a commitment to one exact frontend framework yet. It is a commitment to one coherent information architecture.

## Design goals

- feel close to Resilio's product model
- keep Tor and I2P internals abstracted away from noob users
- support desktop, NAS, and mobile without three unrelated UX models
- make selective sync, placeholders, permissions, and folder states legible
- preserve room for diagnostics without overwhelming the default surface

## Shared information architecture

### Main view

The main view should revolve around folders first, not accounts first.

Expected primary zones:
- add/connect entry point
- folder list with statuses and columns
- peer count / health summary
- search and filter controls
- history / recent activity view
- settings / diagnostics / license or build details
- global pause / resume

### Folder detail / peer detail

Each folder should expose:
- permission posture
- current sync mode: disconnected, placeholder/selective, fully synced
- peer set and health
- transfer activity
- local path and storage posture
- folder-level preferences

### Share / invite flow

The invite flow should stay close to Resilio's shape:
- link or QR as the default human-share surfaces
- explicit permission choice: RO / RW / Owner-like
- security options grouped together
- language that describes the share without transport jargon

### Preferences model

The product needs both global and per-folder preferences.

Global examples:
- default storage location
- bandwidth limits and schedules
- LAN discovery policy
- update and startup behavior
- privacy / telemetry policy if ever introduced

Per-folder examples:
- sync mode
- archive behavior
- network or transport policy
- local path behavior
- permission / access review

## Desktop posture

Desktop should expose the richest operational surface while still feeling ordinary:
- multi-column folder list
- history and peer inspection
- right-click or overflow actions
- keyboard-shortcut-friendly layout later
- placeholder-first support without requiring shell-extension tricks in the first version

## Mobile posture

Mobile should preserve the same conceptual model with a smaller surface area:
- placeholders/selective sync on by default
- tap-to-fetch full file behavior
- obvious per-share network policy
- simplified add/connect flow
- clear folder state badges
- battery- and storage-aware defaults

## Diagnostics posture

Diagnostics should be available but not lead the product.
Transport or router internals should be translated into user-safe health states such as:
- ready
- connecting
- degraded
- blocked by network policy
- needs attention

## Intentional likely divergences from Resilio

AnonSync is likely to diverge in these places:
- LAN discovery token semantics, for privacy reasons
- language around transports, because Tor and I2P must remain abstracted
- mobile I2P being opt-in rather than assumed
- future anonymity/privacy settings that Resilio does not need
