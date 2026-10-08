# Boot-authority replay review page — config-owned values, startup rebind, and world switch

## Purpose

Review what the next boot will actually reconstruct, especially when config files, service mode, or storage-home changes can create a different world than the currently running UI suggests.

This page exists to answer:

- `what will restart really replay?`
- `which values come from config or package authority rather than interactive state?`
- `will a service-user/storage-home switch create a different object world?`

## Required sections

### 1. Next-boot summary

Must show:

- current runtime world
- next-boot world
- continuity verdict (`same world`, `same values stronger plane`, `different storage world`, `different principal world`, `mixed/unknown`)

### 2. Replay roster

For each material field, show:

- current live value
- next-boot replay value
- replay source (`persisted storage`, `config file`, `package-enforced default`, `service principal storage`, `unknown`)
- whether operator edits in current UI can change that replay source

### 3. World-switch block

Must publish:

- storage home today
- storage home next boot
- identity / approval / share roster continuity posture
- objects that would disappear only because the runtime is entering a different world

### 4. Risk block

Examples of risk classes:

- `listener binds differently at next boot`
- `share roster comes from config and interactive changes disappear`
- `service account switch creates empty-looking world`
- `identity/approval memory belongs to old storage home`

### 5. Strongest safe sentence

Examples:

- `Next boot will not simply reopen the current interactive state; it will replay config-owned authority.`
- `Changing to this service world creates a different storage home, so prior folders and remembered state will not appear automatically.`

### 6. Blocked stronger sentence

Examples:

- `Restart will faithfully preserve everything exactly as currently shown.`
- `The empty-looking world after restart means the old state was lost.`

## Receipt obligations

Any receipt derived from this page must preserve:

- next-boot world verdict
- replay roster or digest
- world-switch posture
- strongest safe sentence
- blocked stronger sentence
