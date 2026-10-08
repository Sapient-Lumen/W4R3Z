# Posture drift timeline page — runtime, path, power, and network change lineage interface spec

## Purpose

The archive already had incident timeline and route evidence.
What it still lacked was the timeline view for the narrower question:

> over the life of this incident, which posture changes could have changed observation quality, and in what order did they happen?

AnonSync should therefore issue a dedicated **posture drift timeline** whenever freshness, lateness, or stale-view claims span multiple environments or runtime states.

## Timeline payload

The timeline must preserve ordered events such as:

- watcher warning appeared / cleared
- path class changed (local-native, SMB, UNC, removable, NAS)
- runtime changed (desktop app, service user, Local System, config-mode profile)
- rescan cadence changed
- sleep / battery posture changed
- network-policy eligibility changed
- restart / wake / manual rescan / healthy notification witness occurred
- prior receipt issued, weakened, expired, or superseded

## Required sections

### 1) Drift events lane

Render one ordered lane with timestamps, scope, and posture impact.
Each event must carry:

- event kind
- source of evidence
- affected scope
- whether it widened, narrowed, or restored observation quality

### 2) Receipt lineage lane

Show prior freshness receipts on the same timeline and mark them as:

- `current`
- `weakened`
- `expired`
- `superseded`

### 3) Coverage epochs

Group the timeline into epochs such as:

- `notification-backed epoch`
- `rescan-backed epoch`
- `manual-probe-only epoch`
- `no-observation / ineligible epoch`

### 4) Revalidation windows

Mark windows where new evidence would be considered load-bearing again.
Examples:

- after watcher repair and first healthy notification
- after next scheduled rescan under stable cadence
- after mobile wake on allowed network

## Compact rendering obligations

Any compact timeline chip must still preserve:

- current epoch label
- most recent invalidator
- current receipt state
- next revalidation window

## Anti-clone rule

Do not clone incident views where posture drift is implicit and old freshness receipts remain visually current because the product never gave the operator one lineage of observation-affecting changes.
