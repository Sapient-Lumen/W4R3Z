# ADR-0376: Removable-media local fallback post-detach terminal closure successor authority and reader admission schema split are typed

## Status

Accepted: 2026-05-30r532

## Context

r530 terminal closure made managed post-detach authority closed, and r531 added a per-attempt access gate that denies later use of old authority. That still left the safe positive path under-specified: after a post-closure denial, a broker could say "new authority was issued" without proving that the old handle stayed denied, the terminal closure remained terminal, the fresh-authority receipt was bound, and reader admission was required before any successor use.

The schema-refactor backlog also kept `spec/removable.media.local.post_detach.reader.admission.receipt.schema.json` as the highest-priority const-heavy post-detach runtime schema.

## Decision

Add `removable.media.local.post_detach.terminal.closure.successor.authority.receipt` with `post-detach-terminal-closure-successor-authority-positive-and-negative-fixture-guarded`. The receipt binds the r530 terminal closure capsule, r531 terminal-closure access receipt, r511 fresh-authority receipt, r524 denial reason registry, r525 denial-selection receipt, r526 rate-limit debit ledger receipt, r521 support projection, and r515 reader-admission receipt by computed digest. It then proves that a successor authority was issued only from fresh authority, not from old managed authority, and that terminal closure remains terminal.

Split the r515 reader-admission receipt schema into a runtime contract and an exact fixture schema. `spec/removable.media.local.post_detach.reader.admission.receipt.schema.json` becomes runtime-shaped, and `spec/removable.media.local.post_detach.reader.admission.receipt.fixture.schema.json` preserves the exact historical r515 fixture.

## Consequences

Post-closure recovery now has both sides of the gate: r531 denies old authority per attempt, and r532 proves the allowed successor path uses new authority only. A broker cannot resurrect an expired root, reopen terminal closure, carry old export approval forward, skip reader admission, or expose raw support material while claiming fresh post-closure authority.

The reader-admission schema is no longer a const-heavy production validator, while the exact r515 fixture remains reviewable and testable.

Last updated: 2026-05-30r532
