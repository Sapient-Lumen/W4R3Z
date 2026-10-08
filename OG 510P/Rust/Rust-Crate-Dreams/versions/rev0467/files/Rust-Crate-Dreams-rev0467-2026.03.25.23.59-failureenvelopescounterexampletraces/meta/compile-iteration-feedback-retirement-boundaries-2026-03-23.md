# Compile Iteration Feedback Kit — retirement-boundary reminders (2026-03-23)

When future passes deepen **P-0537** again, keep these truths separate:

1. **activation boundary** — when fresh code becomes reachable on some route;
2. **generation witness** — what evidence identifies the code epoch of that route or library;
3. **retirement boundary** — when older code is expected to stop being reachable for that route class;
4. **old-generation drain** — whether pre-reload work was actually observed drained or only partially rewound;
5. **mixed-generation risk** — whether old and new generations may coexist across routes.

Do not let any of the following masquerade as a complete answer by themselves:

- “the hot reload completed,”
- “the library was swapped,”
- “the latest pointer is in the jump table,”
- “the new code is active now,”
- or “a before/after reload hook ran.”

A pass may truthfully show a successful patch, a visible update, and even a route-level generation witness while still lacking an honest answer to:

- whether older callbacks/tasks are still in flight,
- whether retirement is stack-scoped or process-scoped,
- whether a reload event only bracketed a handoff,
- and whether full drain completeness remains unknown.
