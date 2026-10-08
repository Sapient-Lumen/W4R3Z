# Setting-locator contract sheet page — canonical setting, scope, and edit route

## Purpose

This page answers one ordinary question:

> what exact setting object is this, where does it live, what scope does it govern, which surface currently wins, and where can I edit it right now?

The page exists because `Preferences`, `Advanced`, `Folder Preferences`, `Settings`, `sync.conf`, and `service config` are not interchangeable.

## Core decision

Every serious settings sentence must render one first-class **Setting locator contract sheet**.
The page owns:

- canonical setting identity
- aliases
- scope
- winning surface
- witness-only surfaces
- current edit route
- activation rung
- strongest safe sentence now

## Fixed page order

1. setting strip
2. route card
3. scope card
4. authority card
5. witness-surface card
6. activation card
7. receipts

### 1) Setting strip

Show:

- canonical setting id: `transfer-priority`, `listen-port`, `use-tracker`, `archive-enabled`, `check-updates`, `default-folder-location`, `unknown`
- operator query text
- aliases: menu labels, config keys, old labels, mobile labels
- current value
- allowed value family
- surface class of the current viewer

### 2) Route card

Show:

- primary edit surface: `desktop-global-preferences`, `desktop-folder-preferences`, `power-user-preferences`, `mobile-global-settings`, `mobile-share-advanced`, `config-file`, `service-config`, `not-editable-here`
- exact navigation route
- required prerequisite: `select share`, `open advanced`, `edit sync.conf`, `restart service`, `desktop only`, `mobile only`, `unknown`
- whether deep-link can open this route directly

### 3) Scope card

Show:

- scope class: `installation-global`, `share-local`, `device-local`, `identity-local`, `service-world`, `startup-authored`, `unknown`
- subject set touched by this edit
- whether this route creates an override, changes a default, or only edits the local witness

### 4) Authority card

Show:

- winning surface
- losing surfaces
- override relationship: `inherits`, `manual-override`, `detached-from-default`, `startup-owned`, `service-owned`, `parallel`, `unknown`
- strongest safe statement about who owns the value now

### 5) Witness-surface card

Show:

- surfaces that can see the value
- surfaces that can describe the value but not edit it
- surfaces where the setting is absent
- why absence exists: `product-lane`, `platform`, `current-scope-mismatch`, `service-world`, `WebUI omission`, `unknown`

### 6) Activation card

Show:

- activation rung
- next required event
- proof class currently available
- blocked stronger sentence

### 7) Receipts

Emit a compact receipt with:

- canonical setting id
- query alias matched
- winning surface
- scope class
- edit route
- activation rung
- strongest safe sentence
- blocked stronger sentence

## Copy rules

- Never collapse `found in this menu` into `editable here`.
- Never collapse `editable here` into `winning authority here`.
- Never collapse `same label` into `same governance lineage`.
- Never collapse `share override exists` into `global default changed`.
- Never collapse `visible in WebUI` into `WebUI can author it`.

## Example strongest-safe sentence patterns

- `This setting is currently editable in desktop folder preferences for this share only.`
- `This setting is visible here, but the winning authority is startup config.`
- `This setting is available on mobile per share and absent from the current desktop route.`
- `This setting has a global power-user default, but this share is manually detached from it.`
