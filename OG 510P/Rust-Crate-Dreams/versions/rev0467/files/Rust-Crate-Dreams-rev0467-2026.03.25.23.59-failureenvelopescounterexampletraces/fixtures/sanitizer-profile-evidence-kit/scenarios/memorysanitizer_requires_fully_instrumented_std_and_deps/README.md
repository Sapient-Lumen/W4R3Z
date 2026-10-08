# MemorySanitizer requires fully instrumented std and dependencies

This scenario keeps a strong MSan-specific truth visible:
a run with only the workspace target instrumented is not strong evidence.

The receipt should make explicit that:

- `std` instrumentation is required, not merely nice to have;
- dependency coverage is only partial;
- the resulting evidence strength is advisory or manual-review territory, not strong.
