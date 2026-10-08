# State lineage receipt page — export capsule, import review, and rejected raw-clone claim

## Purpose

Preserve durable proof of what state-continuity action was reviewed, what source was used, what became live, and what stronger clone-style sentence was refused.

## Receipt fields

Must preserve:

- receipt id
- action kind (`export-successor-capsule`, `verify-capsule`, `activate-successor`, `inspect-backup`, `block-duplicate-seat`, `start-clean-seat`)
- source artifact or path
- reviewed classification
- chosen action
- resulting world id if any
- predecessor reference if any
- seat-lineage verdict
- carried-forward rows summary
- dropped/narrowed rows summary
- strongest safe sentence
- blocked stronger sentence
- follow-up obligations
- recorded time

## Required sections

### 1. What was reviewed

Show:

- source kind and provenance
- why the system opened review
- key evidence rows the operator saw

### 2. What was chosen

Show:

- export, inspect, activate, rebirth, retire-other-first, or block
- whether live activation occurred
- whether predecessor continuity was narrowed or broken

### 3. What is now true

Show:

- live world / seat result
- subject continuity result
- trust/cache/history result
- pending obligations

### 4. Blocked overstatement

Show the stronger rejected sentence verbatim enough that later operators do not reconstruct the wrong story from memory.

## Example summary lines

- `Reviewed raw storage copy; classified concurrent duplicate risk; live activation blocked.`
- `Reviewed successor capsule; activated reborn replacement seat with carried-forward subject roster.`
- `Reviewed old backup; opened inspect-only; no same-seat continuity claimed.`
