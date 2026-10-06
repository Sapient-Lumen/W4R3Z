# ADR-0374: Removable-media local fallback post-detach terminal closure and denial receipt schema split are typed

## Status

Accepted: 2026-05-30r530

## Context

r529 gave export-bundle deletion its own receipt, but the lane still lacked one terminal capsule that summarized closure after deletion, denial selection, support projection, transition witness, and scenario replay all agreed. A reviewer could inspect the parts, but no single artifact said that managed post-detach authority was closed and future access required new authority.

The schema-refactor backlog also kept `spec/removable.media.local.post_detach.denial.receipt.schema.json` as the highest-priority const-heavy post-detach runtime schema.

## Decision

Add `removable.media.local.post_detach.terminal.closure.capsule` with `post-detach-terminal-closure-positive-and-negative-fixture-guarded`. The capsule binds the r529 export-bundle deletion receipt, the denial-selection receipt, denial reason registry, support projection, transition witness, and scenario replay by computed digest. It proves managed export closure, future-access denial without new authority, no expired-root resurrection, support-safe visibility, and CAS-rooted terminal closure ledger advancement.

Split the r510 denial receipt schema into a runtime contract and an exact fixture schema. `spec/removable.media.local.post_detach.denial.receipt.schema.json` becomes runtime-shaped, and `spec/removable.media.local.post_detach.denial.receipt.fixture.schema.json` preserves the exact historical r510 fixture.

## Consequences

A completed managed export now has an end-state capsule rather than only a deletion receipt. The capsule does not claim erasure of unmanaged offline copies; it denies future managed authority and requires new authority for new access.

The denial receipt schema is no longer a const-heavy production validator, while the exact r510 fixture remains reviewable and testable.

Last updated: 2026-05-30r530
