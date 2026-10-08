# Repository hygiene

- Active implementation projection: **288 files**, **17764059 bytes**, SHA-256 `ff1638dcaec749cf2b7a87a07d2e02ed10ef1ff379ebe4a0915e9069df8ad91f`.
- Active source delta: **9 files**, **1,498 insertions**, **36 deletions**; bundled third-party changes: **0**.
- Generated Python bytecode, VCS metadata, build trees, object files, executables, and sanitizer outputs are excluded from the package.
- An audit-created `tools/__pycache__` directory was detected and removed before projection and manifest generation.
- The immutable handoff retains the interrupted foreground attempts as operational evidence but does not count them as passing gates.
- The source patch was generated with new files explicitly represented, applied to the verified rev0855 parent, and compared byte-for-byte for all nine changed paths.
- Build products remain outside the source tree. The release archive has one `AnonSync/` root and no symlinks.
