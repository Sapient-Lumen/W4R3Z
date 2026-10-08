# rev0062 trace-packet QK native replay

This experiment closes the local QK-measurement gap left by rev0061.  The rev0061 replay consumed precomputed materialized scores; this replay captures a fresh local tiny-transformer packet with query vectors, key caches, and values, then times native C++ paths that compute QK scores inside the row-attention loop.

Measured paths:

- dense online QK attention;
- materialized score-histogram sparse attention, which computes all QK scores and stores them;
- streaming recompute histogram attention, which avoids global score storage but pays repeated QK passes.

Scope limits remain strict: this is CPU native evidence on a local tiny model.  It is not public/pretrained trace evidence and not GPU/fused-kernel timing.
