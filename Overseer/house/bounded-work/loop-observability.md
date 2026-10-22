# Loop Observability

## Purpose

Provide one compact derived room for bounded-loop state that is cheaper to spider than reopening every loop run by hand.

This room exists because the house now has enough bounded-loop machinery that:

- raw loop status is too expensive to reopen constantly,
- the attention room should not have to summarize every loop directly,
- the audit room benefits from a small visible ingress for explicit audit priorities,
- and bounded workers need a truthful steering seam that does not pretend `codex exec` is an interactive TTY.

This room also now consumes the loop-class maturity registry:

- `/home/overseer/docs/registries/loop-class-maturity.json`

That lets the room keep trusted workers prominent while still remembering older
prototype residue when it is still active enough to matter.

The room now also owns the smallest truthful view of loop-control mechanism
posture:

- held-loop launcher status
- audit-loop cadence status

Those mechanism surfaces still exist as rooms and routes, but they no longer
need to compete directly with `loop-observability` at the front desk.

## Current Packet

- `generated_at = 2026-04-18T01:56:04Z`
- `observability_level = error`
- `running_loop_count = 2`
- `held_loop_count = 1`
- `failed_recent_count = 1`
- `stale_failed_count = 53`
- `superseded_failed_count = 702`
- `active_group_count = 1`
- `held_loop_launcher_status = no_candidate`
- `audit_loop_cadence_status = deadman_pressure_present`
- `recommended_actions = inspect-failed-loops, review-stale-failed-loops, review-superseded-loop-failures, review-prototype-loop-residue, review-held-or-waiting-loops, review-audit-findings`

## Live surface

- placard: `/home/overseer/OBSERVABILITY.md`
- compiler: `/home/overseer/scripts/compile_loop_observability_brief.py`
- state root: `/home/overseer/state/loop-observability/`
- latest JSON: `/home/overseer/state/loop-observability/latest.json`
- latest Markdown: `/home/overseer/state/loop-observability/latest.md`
- history: `/home/overseer/state/loop-observability/history.jsonl`

## Tiers

The room is intentionally tiered:

- `hot`
  - running loops
  - explicitly held loops
  - recent failed or blocked loops
  - the current audit priority note, if one exists
- `warm`
  - waiting-for-capacity loops
  - other planned loops
  - stale failed prototype or superseded loops that still deserve memory but not front-desk alarm
  - active and paused groups
  - the current audit-room summary
  - held-loop launcher status
  - audit-loop cadence status
- `cold`
  - recent completed loops
  - the freshest completed audit loop

That lets the house spend tokens proportionally:

- `attention` can lift only the hottest signals
- loop repair can reopen the room before raw run state
- deep audit can still drop to raw loop receipts when it needs truth
- active loop-control notes can bubble up without forcing the front desk to spelunk raw note files

The room should be skeptical without becoming hysterical.
Older prototype failures are still real history, but they should not dominate `hot` forever once newer bounded work has proven the same surface more truthfully.
So the room now distinguishes:

- `failed_recent`, which can still raise `error`
- `stale_failed`, which remain visible in `warm` and still deserve reconciliation, but do not automatically make the room scream
- `superseded_failed`, which remain visible in `warm` as memory, but have already been overtaken by a later successful worker of the same class and trust tier
- `prototype_residue`, which keeps older generic failures visible without
  letting them masquerade as the current trusted worker ecology while they are
  still live in the active ledgers

Prototype residue may still recommend review while it remains live, but by
itself it should not raise the whole room to `watch`. That pressure is reserved
for live held or waiting work, explicit control input, recent failures, or
stale failures from the trusted worker classes.

Once prototype proof work has been superseded and archived out of the active
loop ledgers, it should stop appearing here at all. The room is for living loop
pressure first, not for permanent museum duty.

Running-loop summaries should also lift the two cheapest live progress signals the control plane already has:

- active load-balancer run metadata, when a bounded worker still has an `active.json`
- latest semantic checkpoint phase and age, even after the active run file is gone

The active run surface now also carries heartbeat-oriented timestamps, so room-level `active_run_age_seconds` can reflect a living worker rather than only the moment its `active.json` was first written.

That keeps a healthy long turn from looking frozen just because the room is cheaper than the raw run tree.

## Refresh posture

This room is now refreshed in two ways:

- loop-control note writes attempt an immediate room refresh
- the host refreshes the loop rooms on `overseer-loop-room-refresh.timer`

That keeps active notes, active runs, and room posture from drifting stale
between manual reopen passes.

## Auditor note ingress

The audit room now has a narrow explicit note surface:

- `/home/overseer/state/audit-loop/priority-note.json`
- `/home/overseer/state/audit-loop/priority-note.md`
- `/home/overseer/scripts/write_audit_priority_note.py`

This is not a hidden scheduler.
It is a visible request surface for the skeptical worker.

It should be used for things like:

- "look at this weak control-plane seam first"
- "stress this failure family"
- "check whether this room is lying"

It should not be used to smuggle broad governance or silent repair orders into the audit worker.

## Loop-control note ingress

Bounded worker steering now also has a first visible ingress:

- `/home/overseer/state/loop-control/notes/`
- `/home/overseer/scripts/write_loop_control_note.py`

This is for turn-boundary control only.

It may:

- cancel a loop before the next turn
- stop a loop after the current turn
- hold a loop after the current turn
- focus the next turn once
- persist a lightweight informative note across turns

It may not:

- type live into the middle of a running `codex exec` turn
- become a hidden scheduler
- silently outrank the primary interactive thread

## Derived, not sovereign

This room may:

- summarize loop state
- expose the hottest loop signals
- bubble a note toward the audit room
- make reopen order cheaper
- surface active profile, active age, and checkpoint age for running workers

It may not:

- spawn or cancel loops
- clear failures
- mutate allocation posture
- or silently decide that a note must be obeyed

## Current recommendation

Use this room as the first reopen surface for loop state once bounded workers start overlapping more often.

The intended order is:

1. `ATTENTION.md`
2. `OBSERVABILITY.md`
3. `AUDIT.md`
4. only then raw loop/group receipts if needed
