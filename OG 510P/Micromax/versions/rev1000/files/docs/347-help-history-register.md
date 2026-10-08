# Help history register

Micromax already had the right tiny docs-history semantics by rev404: exact back/forward entries, explicit session-only scope, and same-page help destinations that counted as real retraceable targets.

The remaining seam was not semantic; it was **visibility**.
A human in the editor could still inspect only the current status head or try `helpback` / `helpforward` experimentally, while scripts and future UIs had to choose between the compressed `help_*` status heads and poking private stacks.

Rev405 adds one small register-shaped surface instead of a bigger browser subsystem:

- plain `helphistory` now prints a count-aware inventory of the current docs target plus actionable back/forward rows
- `help_history_rows()` returns the same ordered rows inside the editor
- `ed.helphistory-rows` exposes that row surface to Micromax scripts and future UIs

The rows stay intentionally tiny:

- `current` — the active docs page/position when the current buffer is a help buffer
- `back` — immediate back target first, then older entries
- `forward` — immediate forward target first, then older entries

Each row carries only `lane`, `depth`, `topic`, `title`, and `position`.
That is enough to witness the local trail without pretending that Micromax now owns a persisted browsing log, a richer docs browser, or a separate queue subsystem.

The design goal is simple: if docs history matters, it should be visible as a tiny register, not only as a hidden stack.
