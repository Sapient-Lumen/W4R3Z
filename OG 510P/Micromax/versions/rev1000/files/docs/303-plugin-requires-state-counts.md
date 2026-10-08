# Rev361: plugin dependency counts should be state-aware

This is a tiny trust/flow follow-up to rev359 and rev360.

## What changed

`plugin info NAME` already had a count-aware dependency header:

- `requires: 0`
- `requires: N`

And rev359 already made each dependency row honest:

- loaded known dependency
- broken known dependency
- available-but-not-loaded known dependency
- truly missing dependency

Rev361 makes the header itself more glanceable when there are several requirements.

Examples:

- `requires: 0`
- `requires: 3 (1 loaded, 1 error, 1 missing)`
- `requires: 2 (1 loaded, 1 available)`

## Why it matters

Without this, the detail path is honest but still mildly high-friction: you must read every dependency row before you know the overall shape.

That is acceptable for large debugging sessions, but the whole plugin honesty pass has been about making ordinary inspection more glanceable:

- inventory should not require manual counting
- success/failure paths should not require immediate follow-up commands
- detail views should not hide the shape of the state they are showing

This change keeps the implementation deliberately small while making plugin detail more scan-friendly for both humans and future LLMs.
