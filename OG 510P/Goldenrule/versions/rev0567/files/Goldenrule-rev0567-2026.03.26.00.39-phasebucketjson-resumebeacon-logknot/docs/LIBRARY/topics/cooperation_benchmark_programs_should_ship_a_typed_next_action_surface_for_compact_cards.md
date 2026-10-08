# Cooperation benchmark programs should ship a typed next-action surface for compact cards

Once a benchmark archive already has a compact-card control plane, inheritors still face one last avoidable burden: they must decide **what to do first**.

That choice is often obvious to the session that just refreshed the archive, but not to the inheritor who arrives later with only the retained surfaces in front of them.

A tiny typed next-action surface is therefore worth keeping.
It should not invent new citation semantics or new review semantics.
It should simply consume the existing compact-card control plane and grouped review queue, then emit one explicit first command together with a small fallback set.

That keeps the first reentry move machine-readable, inheritor-stable, and cheaper to recover after a long gap.
