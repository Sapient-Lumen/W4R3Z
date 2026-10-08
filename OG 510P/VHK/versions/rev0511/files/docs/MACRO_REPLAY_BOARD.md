# Macro replay board

`vhk macro-replay-board-json <project>` emits one project-wide replay-proof board keyed by each macro's own newest matching run.

Generated i3/X11 stacks expose the same surface as:

- `bin/macro_replay_board_json.sh`

## Why this exists

VHK already had project-wide latest-run helpers, but those answer a different question: *what happened most recently anywhere in this project?*

That was not enough for the resident runtime and a private LLM, because per-macro replay truth could drift toward whichever macro happened to run last. The replay board fixes that by tracking the newest matching run **per macro**.

## Replay posture ids

- `verified_recent`: the newest matching run is healthy enough to treat as current replay proof
- `verified_recent_target_unproven`: the newest matching run is healthy, but its newest replay proof still lacks current X11/i3 target authority for an explicit selector contract
- `warning_recent`: the newest matching run finished, but still carried flakiness or optimization warnings
- `failed_recent`: the newest matching run failed
- `unverified`: no matching run history exists yet for this macro


Revision 0473 extends that board one step further for the flagship X11/i3 lane: healthy replay proof is no longer treated as fully current just because the run finished cleanly. If the macro carries an explicit target selector and the newest run does not preserve a current target-authority witness for it, the board now marks that macro as `verified_recent_target_unproven` instead of flattening it into `verified_recent`.
Revision 0474 makes that posture actionable too: `verified_recent_target_unproven` now points at the bounded target-proof command (typically the checked-dispatch gate or report/trace followup), so replay triage stops falling back to generic history review when the real next question is whether the intended X11/i3 window/workspace was actually re-proven.

## Intended use

Use this surface before runtime posture when you need to answer:

- which macro has the strongest replay proof right now?
- does this macro have its own matching run, or am I looking at project-global noise?
- should I inspect run history first, or can I move on to dispatch/runtime posture?

Then layer the runtime board and checked dispatch gate on top of that replay truth.

## Non-claims

The replay board is still advisory.

- A `verified_recent` macro is not proof that the current desktop is already in the right state for the next replay.
- This board does not replace recorder review, cleanup review, or explicit dispatch gates.
- It is stronger than the single project-wide latest run for per-macro triage, but it is not a substitute for runtime readiness checks.
