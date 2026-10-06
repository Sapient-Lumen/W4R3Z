# ADR-0375: Removable-media local fallback post-detach terminal closure access and fresh authority schema split are typed

## Status

Accepted: 2026-05-30r531

## Context

r530 added a terminal closure capsule, but that capsule was still an end-state assertion. A later query, export, rehydration, observation, managed-copy, or support-debug attempt could claim it honored terminal closure without leaving a per-attempt receipt that proved the old managed authority was denied, rate-limited, and support-safe.

The schema-refactor backlog also kept `spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json` as the highest-priority const-heavy post-detach runtime schema.

## Decision

Add `removable.media.local.post_detach.terminal.closure.access.receipt` with `post-detach-terminal-closure-access-positive-and-negative-fixture-guarded`. The receipt binds the r530 terminal closure capsule, r529 export deletion receipt, r525 denial-selection receipt, r524 denial reason registry, r526 rate-limit debit receipt, and r521 support projection by computed digest. It records a post-closure attempt, applies `terminal-closure-managed-authority-closed`, denies old managed authority, requires new authority for successor access, requires new approval for export/managed-copy, advances a CAS-rooted access ledger, and preserves digest-only support projection.

Split the r511 fresh-authority receipt schema into a runtime contract and an exact fixture schema. `spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json` becomes runtime-shaped, and `spec/removable.media.local.post_detach.fresh.authority.receipt.fixture.schema.json` preserves the exact historical r511 fixture.

## Consequences

Terminal closure now has both a closeout capsule and a per-attempt access gate. A broker cannot merely cite terminal closure in prose; it must emit a receipt proving that old authority did not query, export, rehydrate, observe, leak raw support data, or mint a successor.

The fresh-authority schema is no longer a const-heavy production validator, while the exact r511 fixture remains reviewable and testable.

Last updated: 2026-05-30r531
