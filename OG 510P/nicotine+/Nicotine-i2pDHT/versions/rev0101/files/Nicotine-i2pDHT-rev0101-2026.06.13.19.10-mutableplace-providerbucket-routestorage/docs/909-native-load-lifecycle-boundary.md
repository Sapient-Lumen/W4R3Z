# Native load lifecycle boundary

Native load is modeled as a dry, no-network permission. A native artifact must still bind to native selection, native promotion, fallback-journal memory, artifact/source/fallback digests, loader identity, sequence memory, and family/path diversity before it may even be considered loadable.

The design intentionally keeps Python fallback bound even when native load is accepted.
