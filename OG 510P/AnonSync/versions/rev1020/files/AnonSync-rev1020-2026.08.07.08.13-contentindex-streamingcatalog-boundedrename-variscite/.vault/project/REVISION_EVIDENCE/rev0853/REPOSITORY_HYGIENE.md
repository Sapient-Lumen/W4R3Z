# Rev0853 repository hygiene

The active release projection contains **277 files / 17,640,630 bytes**. The
source delta is confined to **16 active files**, with **476 insertions** and
**60 deletions**. Bundled third-party source is unchanged.

The exact active patch applies to the sealed rev0852 parent and reproduces all
**277/277** active files by path, byte count, and SHA-256. During replay, four
Python bytecode files created by local audit imports appeared under `tools/`.
They were removed before projection and packaging; no `__pycache__` or `.pyc`
entry is admitted to the release.

The revision adds one 27-line shared callback-slot header and removes three
private copies of protocol identifiers. It centralizes eight direct
busy-timeout mutations behind one gateway, reducing the reviewed primitive
surface even though support and audit code grow.

The largest change amplifiers remain the monolithic domain, selftest, replay,
and CMake translation/registration surfaces. Historical `REVISION_EVIDENCE`
continues to dominate package file count. It preserves lineage, but routine
handoffs should eventually use immutable evidence roots and selective retrieval
rather than recursively copying every historical execution artifact.
