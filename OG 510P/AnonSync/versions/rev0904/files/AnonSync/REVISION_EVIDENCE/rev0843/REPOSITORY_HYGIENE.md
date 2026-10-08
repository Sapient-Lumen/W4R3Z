# AnonSync rev0843 repository hygiene

The sealed handoff excludes `.git`, compiler/linker products, CMake build trees,
Python bytecode, sanitizer traces, and symlinks. `MANIFEST.sha256` enumerates
every packaged regular file other than itself, and the release verifier
recomputes each digest plus the exact active implementation projection.

The active change adds three production files and modifies six active files. It
does not modify bundled third-party sources. Build directories used for GCC,
Clang, and sanitizer validation remain outside the packaged `AnonSync/` root.

Historical evidence remains intentionally present for lineage compatibility and
is still a major footprint concern. Rev0843 does not claim that recursive
historical handoffs are the desired long-term distribution model.
