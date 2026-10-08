# Storage lineage forecast page — profile switch, share carryover, and identity surface

## Purpose

Before the operator changes runtime profile, service account, or storage path, forecast whether the product will keep the same effective profile or present a fresh one.

## Typical triggers

- foreground app -> Windows service
- service current user -> Local System / Local Service
- default storage root -> configured `storage_path`
- localhost-only WebUI -> broader listen scope with config mode
- uninstall / replacement planning where old profile roots may remain

## Questions this page must answer

1. What profile switch is being requested?
2. Which storage root will be authoritative afterward?
3. Will shares, databases, and identity carry over, migrate, or disappear from the active surface?
4. Will the result still count as the same reviewed seat continuity?
5. What manual follow-up work becomes mandatory if the carryover is not complete?

## Forecast classes

- `same-profile same-root`
- `same-profile migrated-root`
- `fresh-runtime-profile same-host`
- `fresh-service-profile`
- `fresh-config-profile`
- `retired-profile with residue left behind`
- `ambiguous until launch`

## Layout

### A. Requested switch card

Fields:

- current profile
- requested profile
- requested reason
- strongest forecast class

### B. Storage-root comparison

Columns:

- current root
- future root
- continuity effect
- evidence basis

### C. Carryover forecast

Rows:

- identity surface
- share catalog
- share databases
- advanced-folder availability
- WebUI reach
- shell / notification behavior
- offline ghost residue on other peers

Each row must say `carry`, `migrate`, `fresh`, `narrows`, `widens`, or `unknown`.

### D. Follow-up obligations block

Examples:

- `Manual re-share and reconnect required.`
- `Retire previous offline row after cutover.`
- `Delete old storage root if true replacement is intended.`
- `Review LAN exposure before widening WebUI reach.`

## Actions

- `Accept forecast and continue`
- `Choose migrate path`
- `Choose clean-install path`
- `Retain old profile and compare later`
- `Cancel`

## Guardrails

- Never let `install service` imply `shares preserved` unless migration evidence is present.
- Never let `change storage path` imply same continuity unless the product can prove carryover.
- Never let `unlink/uninstall later` stay implicit when old offline residue will remain visible elsewhere.
- Never hide `Advanced folders unavailable in config mode` behind a generic expert setting.

## Result

A typed continuity forecast that makes runtime-profile switching legible before the operator crosses the storage-root boundary.
