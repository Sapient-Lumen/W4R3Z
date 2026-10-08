# Macro replay board

`vhk macro-replay-board-json <project>` emits one project-wide replay-proof board keyed by each macro's own newest matching run.

Generated i3/X11 stacks expose the same surface as:

- `bin/macro_replay_board_json.sh`

## Why this exists

VHK already had project-wide latest-run helpers, but those answer a different question: *what happened most recently anywhere in this project?*

That was not enough for the resident runtime and a private LLM, because per-macro replay truth could drift toward whichever macro happened to run last. The replay board fixes that by tracking the newest matching run **per macro**.

## Replay posture ids

- `verified_recent`: the newest matching run is healthy enough to treat as current replay proof
- `warning_recent`: the newest matching run finished, but still carried flakiness or optimization warnings
- `failed_recent`: the newest matching run failed
- `unverified`: no matching run history exists yet for this macro

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
