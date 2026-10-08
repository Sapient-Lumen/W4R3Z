# Receive inbox page: default path, fixed mobile store, and config-owner truth interface spec

## Purpose

This page answers:

> where do received handoff bytes land on this seat right now, who owns that default, and can it be changed from here?

The page exists because `Downloads`, `SyncDownloads`, `files_default_path`, and `default folder location` are not the same storage contract.

## Core rule

Every seat that can receive bounded handoffs must expose one first-class **Receive inbox** page.
That page owns:

- current landing root
- default-path owner
- fixed vs configurable posture
- local file-manager visibility
- cleanup / residue adjacency

## Primary layout

The page always renders the same regions:

1. inbox verdict
2. landing-root card
3. default-owner card
4. visibility and cleanup card
5. next review and receipt

### 1) Inbox verdict

Show:

- inbox label
- inbox verdict: `desktop-default-downloads`, `desktop-custom-default`, `config-owned-default`, `android-fixed-internal-inbox`, `ios-app-downloads`, `unknown`
- strongest honest operator summary
- one next honest action

### 2) Landing-root card

Show:

- exact current landing path or path family
- whether the path is user-configurable, config-owned, or fixed by the mobile lane
- whether change is possible from this surface
- whether the file manager / app view points to the same bytes

The operator must be able to answer: **where exactly will received bytes land?**

### 3) Default-owner card

Show:

- who owns the default: user settings / config file / NAS package / mobile platform lane / unknown
- whether this seat can override the default interactively
- whether a different runtime or deployment mode owns the path instead
- whether path change affects future receipts only or also existing rows

The operator must be able to answer: **who decided this inbox and what authority would change it?**

### 4) Visibility and cleanup card

Show:

- where these received bytes appear in UI
- whether clicking the row opens the same bytes in a file manager
- whether removing from the inbox clears bytes, rows, or both
- strongest related cleanup non-effect

The operator must be able to answer: **what exactly is this inbox showing, and what later cleanup acts on the same bytes?**

### 5) Next review and receipt

Show links to:

- Transfer history

After apply or change, emit a receipt that preserves:

- current landing root
- default-owner class
- fixed/configurable verdict
- visibility mapping summary

## Honest outputs

This page may conclude:

- `desktop receipts land in Downloads by default`
- `desktop receipts land in custom path owned by seat settings`
- `config-mode receipt path owned by files_default_path`
- `android receipts land in fixed internal SyncDownloads`
- `iOS receipts appear in app Downloads view`

It may not collapse these into one generic `download location` verdict.

## Rules

### Rule 1 — default owner must be named, not implied

If config or deployment mode owns the receive path, the page must say so directly.

### Rule 2 — fixed mobile inboxes must not pretend to be choices

A fixed mobile landing root is not the same thing as a remembered user preference.

### Rule 3 — visibility must stay adjacent to cleanup

If rows, downloads views, file-manager paths, and device bytes are not all the same object, the page must keep those distinctions visible next to removal actions.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- where new received bytes land on this seat
- whether that path is fixed, configurable, or config-owned
- who would need to change it
- whether UI rows and file-manager bytes are the same object here
- what cleanup action later targets this inbox
