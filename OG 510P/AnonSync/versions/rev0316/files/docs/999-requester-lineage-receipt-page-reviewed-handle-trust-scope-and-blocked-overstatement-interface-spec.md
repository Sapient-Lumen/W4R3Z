# Requester lineage receipt page — reviewed handle, trust scope, and blocked overstatement

## Purpose

Emit a durable receipt after requester approval, trust reuse, collision handling, or trust expansion so later operators do not have to rely on memory, labels, or folklore.

## Required fields

### 1. Request context

Must include:

- subject identifier
- action time
- request lane
- requested capability ceiling

### 2. Reviewed identity bundle

Must preserve:

- human label at review time
- device label at review time
- canonical proof handle
- handle class (`seat`, `family`, `unknown`)

### 3. Decision summary

Must say one of:

- `approved current seat only`
- `approved exact handle reuse`
- `approved linked-family widening`
- `rejected due to collision`
- `approved as distinct new requester`

### 4. Collision and reuse facts

Must preserve:

- whether any label collision existed
- whether prior trust memory matched exactly
- whether any prior receipt was replaced, preserved, or superseded

### 5. Strongest safe sentence

Examples:

- `A single requester seat was approved; linked-family widening was not granted.`
- `Trust was widened to a reviewed linked family based on explicit family evidence.`
- `Matching labels alone were insufficient, so a new distinct requester receipt was created.`

### 6. Blocked stronger sentence

Examples:

- `The same name proved the same requester.`
- `All of this requester's linked devices were approved.`
- `Future requests may rely on label match alone.`

## Interaction rules

- receipts must be linkable from future approval/collision flows
- copied summaries must keep safe sentence and blocked sentence together
- superseding a receipt must never destroy the original reviewed handle bundle

## Reopen triggers

A receipt must be marked stale or reopen-required when:

- the proof handle changes
- a collision is later detected
- family association changes
- capability ceiling is widened
- the subject lineage changes enough to invalidate prior trust scope