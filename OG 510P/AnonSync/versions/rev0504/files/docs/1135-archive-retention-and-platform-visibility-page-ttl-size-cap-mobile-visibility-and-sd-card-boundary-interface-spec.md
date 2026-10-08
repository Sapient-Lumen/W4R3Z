# Archive retention and platform visibility page: TTL, size cap, mobile visibility, and SD-card boundary interface spec

## Purpose

This page exists because operators routinely overestimate how long Archive survives, where it is browsable, and which file classes were ever versioned at all.
It answers one ordinary question:

> how long should this archived history exist, where can I actually see it from this platform, and what coverage holes already make the archive weaker than it sounds?

## When this page must appear

Trigger this page for:

- retention changes
- archive-enabled/disabled review
- cross-platform recovery planning
- any claim that Archive can be relied on as history or local safety

## Fixed page order

1. retention summary header
2. TTL and size-cap card
3. platform visibility card
4. residue and storage-growth card
5. next-safe action rail

### 1) Retention summary header

Show:

- subject / seat / platform class
- TTL class (`desktop-default`, `mobile-default`, `custom`, `never-auto-delete`, `unknown`)
- version-size cap class (`covered`, `size-excluded`, `unknown`)
- visibility class (`desktop-ui`, `file-browser only`, `webui/file-browser`, `not-accessible-on-this-platform`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) TTL and size-cap card

Render rows for:

- current TTL days
- desktop/mobile default comparison
- never-auto-delete override
- max file size for versioning
- whether oversized files are expected to have no archived history

### 3) Platform visibility card

Render rows for:

- desktop `Open Archive` availability
- WebUI/file-browser visibility
- iOS accessibility absence
- Android SD-card limitation
- hidden `.sync/Archive` path reminder

### 4) Residue and storage-growth card

Show:

- hidden archive survives app uninstall unless `.sync` is manually removed
- archive may grow over time and occupy real disk space
- hidden history should be reviewed before cleanup language is allowed

### 5) Next-safe action rail

Offer:

- `Open archive restore review`
- `Open archive salvage proof`
- `Emit archive lineage receipt`

## Rules

### Rule 1 — retention and visibility must stay public

Operators must not have to open power-user settings or KB pages to learn whether history is still expected.

### Rule 2 — access surface is not the same as coverage

Being able to browse Archive does not prove a given file was versioned or still retained.

### Rule 3 — hidden residue must be visible before cleanup claims

If uninstall leaves archive survivors behind, the page must say so.
