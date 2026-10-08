# Non-authority edit receipt page — local-change verdict, continuity status, and claim ceiling interface spec

## Purpose

This page answers one ordinary question later:

> what non-authority local-edit policy was in force, what local change or review happened, and what is the strongest honest sentence now?

The page exists because later operators should not have to reconstruct a frozen path, reverted file, or preserved local-only copy from logs and memory.

## Core decision

Every meaningful non-authority edit event must emit one durable **Non-authority edit receipt**.
That includes:

- reviewed local edits on non-authority seats
- policy changes that alter local-edit fate
- auto-heal events that revert local managed bytes
- continuity-freeze outcomes for affected paths

## Fixed page order

1. event summary
2. posture in force
3. affected paths and outcomes
4. continuity status
5. claim ceiling
6. reopening conditions

### 1) Event summary

Show:

- subject
- seat
- event type
- time
- operator intent in plain language

### 2) Posture in force

Show:

- authority grade
- local-edit mode
- whether auto-heal was disabled, enabled, or forced
- whether hardwired limits removed safer alternatives

### 3) Affected paths and outcomes

Show:

- changed / reviewed path set
- per-path or grouped verdicts
- whether edits were preserved, reverted, frozen, or left as local-only residue
- whether upstream state continued or stopped per path

### 4) Continuity status

Show:

- whether subject-wide continuity remained intact
- whether only some paths froze
- whether later repair is required
- whether repair was completed, deferred, or declined

### 5) Claim ceiling

Show:

- strongest safe sentence now
- stronger unsupported sentences
- what evidence would be needed to regain them

### 6) Reopening conditions

Show:

- what would restore full continuity for affected paths
- whether moving work to a writable seat or unmanaged lane is required
- whether current posture can ever provide a safer route later

## Public object

### `non_authority_edit_receipt`

Fields:

- `non_authority_edit_receipt_id`
- `subject_ref`
- `seat_ref`
- `event_type`
- `operator_intent`
- `authority_grade`
- `local_edit_mode`
- `auto_heal_mode`
- `affected_path_outcomes[]`
- `continuity_status`
- `repair_status`
- `claim_ceiling`
- `reopen_conditions[]`
- `issued_at`

## Honest outputs

The receipt may conclude:

- `Local edits on this non-authority seat were reviewed. Two managed paths froze for future upstream continuity; one added file remained local-only.`
- `This seat auto-healed the edited managed copy under forced posture. Strongest safe sentence: upstream state remains authoritative here; local changes were not retained in the managed lane.`
- `Safer alternative unavailable: this posture did not offer selective materialization or writable-seat substitution on-device.`

It may not reduce the event to `read-only sync completed` or `changes overwritten`.
