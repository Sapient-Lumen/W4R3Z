# Mutation durability receipt page — live, persistence, boot authority, and world scope

## Purpose

Emit one durable record that captures exactly how far a mutation really went.

This receipt exists so later operators do not have to reconstruct whether `applied`, `saved`, `restart-safe`, and `boot-authoritative` were all actually the same claim.

## Required fields

- receipt id
- object / field mutated
- requested value
- live verdict
- persisted verdict
- boot-authoritative verdict
- storage-home identifier
- runtime principal
- next-boot world verdict
- strongest safe sentence
- blocked stronger sentence
- reopen triggers / invalidators

## Example summary sentences

- `Applied live and persisted on the current storage home; next boot still replays config-owned authority for listener binding.`
- `Applied live only; destructive follow-through was allowed under explicit live-only review and is not restart-safe.`
- `Persisted successfully, but a service-user switch will enter a different storage world with a different roster.`

## Rendering rules

- compact rows may abbreviate wording, but may not hide the difference between live, persisted, and boot-authoritative verdicts
- if any world-switch risk exists, the receipt must display it without requiring expansion
- exports must keep storage-home and principal provenance
