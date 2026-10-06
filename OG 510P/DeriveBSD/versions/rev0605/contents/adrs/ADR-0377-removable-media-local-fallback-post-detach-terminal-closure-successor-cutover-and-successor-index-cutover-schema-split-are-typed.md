# ADR-0377: Removable-media local fallback post-detach terminal closure successor cutover and successor-index cutover schema split are typed

## Status

Accepted: 2026-05-30r533

## Context

r532 added the safe positive path after terminal closure: successor authority can be issued only from fresh authority after old managed authority has been denied. That still left one activation gap. A broker could bind the successor-authority receipt while failing to prove that successor-index cutover, checkpoint, and reader admission were all observed before the successor became usable.

The schema-refactor backlog also kept `spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json` as the highest-priority const-heavy post-detach runtime schema.

## Decision

Add `removable.media.local.post_detach.terminal.closure.successor.cutover.receipt` with `post-detach-terminal-closure-successor-cutover-positive-and-negative-fixture-guarded`. The receipt binds the r532 terminal-closure successor-authority receipt, the r513 successor-index cutover receipt, the r514 successor-index checkpoint receipt, the r515 reader-admission receipt, and the r521 support projection by computed digest.

The receipt proves that successor-index cutover was observed before activation, the checkpoint was observed before broker use, reader admission was bound before use, old handles stayed terminal, no dual-active window was accepted, support remained digest-only, and the activation ledger advanced by compare-and-swap.

Split the r513 successor-index cutover receipt schema into a runtime contract and an exact fixture schema. `spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json` becomes runtime-shaped, and `spec/removable.media.local.post_detach.successor.index.cutover.receipt.fixture.schema.json` preserves the exact historical r513 fixture.

## Consequences

Post-closure recovery now has a gated positive path from denial to fresh authority to successor authority to cutover/checkpoint/admission activation. A broker cannot treat new successor authority as live while skipping the successor-index fence, accepting a dual-active index, broadening successor scope, using a stale checkpoint, or using a reader before admission.

The successor-index cutover schema is no longer a const-heavy production validator, while the exact r513 fixture remains reviewable and testable.

Last updated: 2026-05-30r533
