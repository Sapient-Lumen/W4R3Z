# rev0062 cleanroom runner notes

The full cleanroom replay evidence was generated as three per-lane standalone runner invocations from `handoff/rev0062/cleanroom-kit/run_cleanroom_replay.py` using the uploaded `/mnt/data/Nicotine-source(1).zip` source bundle. The combined aggregate is stored in `evidence/rev0062-cleanroom-replay-rerun/cleanroom_replay_summary.json` and copied into `data/rev0062_cleanroom_replay_summary.json`.

Summary:

```text
patch apply rows: 12/12 pass
patched file hash rows: 15/15 pass
fixed regression rows: 21/21 pass
```

The package helper `tools/probe_rev0062_cleanroom_replay.py` defaults to a one-lane smoke replay so post-extract package checks remain practical. It accepts `--lanes all` when the caller wants a full replay and has a large enough local time budget.
