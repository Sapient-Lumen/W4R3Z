# 2026-03-08 — Resilio UI and change-tracking note

## Why this note exists

The archive now treats Resilio UI and behavior tracking as a recurring practice, not a one-time analogy.

## Current takeaways from Resilio's public docs

### Desktop main view

Resilio's documented desktop main view includes:
- add folder / connect entry point
- a control panel with connected-disconnected filtering, search, and column controls
- menu areas for folders, shared files, history, and settings / license
- a global pause button
- peer counts with online versus total peers
- context menus for share management and preferences

These are not superficial details. They define the product's daily working shape.

### Share dialog

Resilio's documented desktop share flow includes:
- link for desktop sharing and QR for mobile sharing
- explicit permission choice: Read Only, Read & Write, Owner
- grouped security options
- copy / email sharing actions

This is the strongest current model for AnonSync's invite flow.

### Folder and sync preferences

Resilio separates:
- global preferences
- folder preferences
- power-user preferences

That split is worth preserving. Folder preferences are where peer search, archive behavior, and file treatment live. Global preferences are where rates, schedules, startup, and listening behavior live.

### Mobile behavior

Resilio's mobile docs reinforce several important ideas:
- placeholders / selective sync are the practical mobile default
- per-share network policy matters
- simplified "simple mode" can reduce friction for noob users
- mobile and desktop should still share the same folder-centric mental model

## Current takeaways from Resilio's change log

Resilio's change log suggests several durable lessons:
- UI flows get redesigned when they are too awkward, for example the add-folder flow
- power-user preferences needed their own clearer design over time
- search and richer columns became important enough to add later
- share-dialog memory and fewer reloads in Linux/NAS web UI mattered
- desktop/mobile synchronization and high-DPI polish were worth explicit fixes

## Archive practice implied by this

When editing AnonSync's product surface, compare the proposed change against:
1. current Resilio main-view shape
2. current Resilio share dialog
3. current Resilio desktop/mobile selective-sync behavior
4. current Resilio preferences split
5. relevant change-log items that hint at past UX pain

## Direction for AnonSync

AnonSync should usually copy Resilio's information architecture first, then diverge only where:
- anonymity requirements demand it
- bundled transport abstraction demands it
- mobile battery / storage constraints demand it
- invite-only semantics demand it
