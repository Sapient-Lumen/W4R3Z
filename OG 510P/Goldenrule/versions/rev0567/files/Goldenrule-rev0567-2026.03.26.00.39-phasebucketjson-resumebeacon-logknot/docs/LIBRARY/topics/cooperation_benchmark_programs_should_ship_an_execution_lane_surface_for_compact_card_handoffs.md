# Cooperation benchmark programs should ship an execution-lane surface for compact-card handoffs

Compact-card governance is already doing a lot of work for future inheritors: cards are schema-valid, claim-ready cards can be frozen, lineages have operational and citation heads, unresolved state sits in review queues, and the stack now emits fused control-plane and first-reentry surfaces.

One more tiny surface is worth adding: **publish the current execution lanes for that stack, and keep them observational rather than aspirational**.

That means:

- distinguish the light lane that can rebuild and verify compact-card surfaces from the deeper lane that can exercise the wider harness or Rust engine;
- record what is actually present now (for example native Rust, existing JuNest-backed Rust, or neither) instead of treating setup scripts as proof;
- emit stable blocking reason codes and recovery commands when a deeper lane is unavailable;
- thread that truth into handoff / control-plane / next-action surfaces so recommended commands do not silently outrun the environment that is supposed to execute them.

This keeps the compact-card stack session-honest: the archive does not just say what is citable or what should be done next, it also says **which validation lane is honestly live right now**.
