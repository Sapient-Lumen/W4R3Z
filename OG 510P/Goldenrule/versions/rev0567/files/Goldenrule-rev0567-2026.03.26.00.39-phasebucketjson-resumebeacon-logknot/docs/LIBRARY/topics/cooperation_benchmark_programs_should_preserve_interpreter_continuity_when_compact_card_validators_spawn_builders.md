# Cooperation benchmark programs should preserve interpreter continuity when compact-card validators spawn builders

Compact-card validators often re-run the matching builder before checking the retained report and rendered handoff docs.
If those validators hardcode a fresh `python3` process instead of reusing the current interpreter, the archive quietly depends on ambient PATH state and wrapper inheritance rather than making its execution contract explicit.

That is fragile for inheritors.
A wrapper such as `./grpy` may intentionally carry bytecode, environment, or virtualenv policy, and validator subprocesses should preserve that same interpreter choice.
Otherwise the documented command surface says one thing while the validator implementation silently does another.

The compact fix is simple: when a validator respawns a builder, invoke `sys.executable` so the subprocess stays on the same interpreter lineage as the caller.
That keeps wrapper semantics, local environments, and no-bytecode policy coherent without inflating the archive or adding another toolchain surface.
