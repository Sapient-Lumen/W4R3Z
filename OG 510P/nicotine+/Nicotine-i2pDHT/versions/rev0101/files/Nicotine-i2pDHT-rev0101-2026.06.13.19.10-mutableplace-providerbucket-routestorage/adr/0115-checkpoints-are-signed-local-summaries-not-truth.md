# ADR 0115 — Checkpoints are signed local summaries, not truth

Accepted for rev0029.

Local checkpoints may summarize journal tips and evidence roots, but they must not erase monotonic memory.  Live tombstones and revocations are hard facts for local restart and must survive checkpoint compaction.
