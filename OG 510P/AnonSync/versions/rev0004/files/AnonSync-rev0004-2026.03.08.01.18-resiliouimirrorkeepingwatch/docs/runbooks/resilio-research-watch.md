# Resilio Research Watch Runbook

## Purpose

Keep AnonSync aligned with Resilio's proven product behavior without relying on stale memory.

## When to use this runbook

Use it whenever a revision touches any of the following:
- UI flows
- invite/share flows
- permissions
- placeholders / selective sync
- mobile ergonomics
- LAN discovery ergonomics
- product defaults that claim to be "Resilio-like"

## Minimum revisit set

Before making material product-surface changes, revisit:
- Resilio Sync functionality in detail
- Resilio Sync main desktop view
- Resilio Sync share dialog
- Resilio Sync preferences
- Resilio folder preferences
- Resilio selective sync desktop and mobile docs
- Resilio power user preferences
- Resilio change log

## What to record

If the research changed the repo direction, update:
- `docs/research/` with a dated note
- `metadata/link-registry.json` if a new canonical source matters
- `metadata/project-state.json` if a product default changed
- `docs/decisions/` if the change is high-cost or durable

## Questions to ask

- Are we copying a Resilio pattern that still exists today?
- Are we diverging for a real anonymity/mobile reason, or just inventing?
- Did Resilio's change log reveal a prior pain point we are about to recreate?
- Are desktop, NAS, and mobile still sharing one coherent mental model?
- Did we keep transport internals hidden from the noob user?
