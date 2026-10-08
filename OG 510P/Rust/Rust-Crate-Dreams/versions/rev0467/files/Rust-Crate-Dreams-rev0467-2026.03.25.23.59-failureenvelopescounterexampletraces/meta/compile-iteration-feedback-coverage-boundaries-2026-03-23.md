# Compile Iteration Feedback coverage boundaries (2026-03-23)

When future passes touch **P-0537** again, keep these lanes explicit:

1. **coverage scope** — what surfaces, routes, crates, or exports are actually under the live-update regime;
2. **coverage ceiling** — what support claims are explicitly out of bounds;
3. **activation / generation / retirement / drain** — what code became reachable, what generation is claimed, and whether old work is gone;
4. **live-update outcome / degraded mode** — what happened on one attempt and what posture the process is in now;
5. **restart fallback** — what deterministic recovery path exists when live update is not safe.

Do not let any of the following stand in for an honest coverage answer by themselves:

- “the framework supports hot reload,”
- “one annotated function updated,”
- “the dylib reloaded,”
- “the workspace compiled,”
- “the macros are present in source,”
- or “the demo route looked live.”

A pass may truthfully show a completed reload, a visible update, and a healthy process while still lacking an honest answer about what coverage the current regime actually had.
