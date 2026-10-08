# Rev0817 repository hygiene

- Active implementation projection: 162 files, 15729241 bytes.
- Active projection SHA-256: `7ebb652ec446505677e7660e6fb82f0af3752ea24e23cbaedad6c012bd85b1e7`.
- Changed active files: 8 (1399 inserted, 119 removed lines).
- Bundled third-party files changed: 0.
- Build trees, binaries, object files, VCS metadata, symlinks, and Python cache files are excluded from the release root.
- Runtime reproducer binaries remain outside the package; only source and logs are retained.
- `MANIFEST.sha256` is generated last and excludes itself.
- The package verifier recomputes the active projection and exact manifest inventory.
