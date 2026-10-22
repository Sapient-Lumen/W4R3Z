# Loop Control

## Purpose

Name the truthful control seam for bounded loopers.

This room exists because `codex exec` is a bounded non-interactive transport.
The house can steer loops between turns.
The house must not pretend it can type live into the middle of a running `exec` turn when that surface does not exist.

## Current control model

- one active control note per loop
- note lives under `state/loop-control/notes/<loop_id>.json`
- markdown mirror lives beside it for cheap reopening
- finite-loop executor consumes notes only at turn boundaries
- control-note writes refresh the loop room briefs immediately when possible
- the host also refreshes the loop room briefs on `overseer-loop-room-refresh.timer`

That means:

- `cancel-before-turn` is real
- `stop-after-turn` is real
- `hold-after-turn` is real
- `focus-next-turn` is real
- persistent `inform` notes are real
- mid-turn live prompting is not claimed

## Current writer

- `/home/overseer/scripts/write_loop_control_note.py`

Example:

```bash
python3 /home/overseer/scripts/write_loop_control_note.py \
  --loop-id loop-EXAMPLE \
  --action focus-next-turn \
  --summary "Start from the model-timing room first." \
  --body "Prefer timing drift and contention over generic repo cleanup."
```

Clear a note:

```bash
python3 /home/overseer/scripts/write_loop_control_note.py \
  --loop-id loop-EXAMPLE \
  --clear
```

## Actions

- `inform`
  - include the note in every subsequent turn prompt until cleared
- `focus-next-turn`
  - inject one bounded steering note into the next turn prompt, then consume it
- `stop-after-turn`
  - allow the current turn to finish, then terminate the loop cleanly as cancelled
- `hold-after-turn`
  - allow the current turn to finish, then persist a hold record and exit
- `cancel-before-turn`
  - cancel the loop before another model turn begins

## Observability

Loop observability lifts active control-note pressure.

Read:

- `/home/overseer/state/loop-observability/latest.json`
- `/home/overseer/state/loop-observability/latest.md`

## Current limit

This is not a hidden supervisor shell.

Still missing:

- control-note queues rather than one active note
- richer control-note acknowledgements in room briefs
- deliberate child-loop steering
- any claim of true mid-turn interaction
