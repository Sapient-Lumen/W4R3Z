# Setting-route review page — desktop, folder, mobile, config, and service branches

## Review question

> why is this setting edited through this route rather than another one, and what exactly changes if I use this route?

## Mandatory review branches

### 1) Desktop global preferences branch

Use when the setting belongs to installation-wide desktop preferences.
Required outputs:

- exact desktop route
- global scope touched
- whether WebUI or mobile can only witness
- whether this route merely opens a deeper advanced route

### 2) Desktop folder preferences branch

Use when the setting belongs to one share/folder on desktop.
Required outputs:

- selected subject/share
- share-only scope
- whether a global default exists above it
- whether the current edit detaches this share from that default

### 3) Power-user preferences branch

Use when the setting lives in the advanced/preferences substrate.
Required outputs:

- canonical key name
- whether this is a default or absolute owner
- whether a restart or other activation rung applies
- whether search found it by alias rather than by exact key

### 4) Mobile global settings branch

Use when the setting belongs to device-level mobile settings.
Required outputs:

- mobile platform
- exact mobile route
- device-local scope
- desktop/config/service limits

### 5) Mobile per-share advanced branch

Use when the setting lives inside a selected share on mobile.
Required outputs:

- selected share
- share-local scope
- interaction with global mobile settings
- whether desktop has a stronger or merely parallel route

### 6) Config-file startup branch

Use when `sync.conf` or equivalent startup-authored config owns the value.
Required outputs:

- config file location
- startup-authored scope
- whether the current runtime can only witness
- restart/startup boundary

### 7) Service-owned branch

Use when service storage, service principal, or service restart owns the edit route.
Required outputs:

- service world identity
- service storage location
- service restart requirement
- whether the interactive client can only observe consequences

### 8) Witness-only / not-editable-here branch

Use when the current surface can explain or display the setting but cannot author it.
Required outputs:

- current surface
- actual winning surface elsewhere
- why this surface is weaker
- exact stronger sentence refused

## Required review outputs

Every route review must end with:

- canonical setting id
- winning surface
- scope class
- current edit route
- nearest false-friend route
- activation rung
- blocked stronger sentence

## False-friend examples the page must catch

- `Settings` when the real owner is `Folder Preferences`
- `Power user default` when a specific share is manually detached
- `I saw it in WebUI` when WebUI cannot author it
- `sync.conf` when the running service still has not restarted
- `same label on mobile` when the mobile route only governs the local device
