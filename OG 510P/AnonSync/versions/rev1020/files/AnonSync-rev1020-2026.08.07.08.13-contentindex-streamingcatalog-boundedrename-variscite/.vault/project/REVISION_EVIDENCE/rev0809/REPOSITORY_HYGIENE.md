# Rev0809 repository hygiene

- Active implementation projection v2 binds **151**
  files and **15358250** bytes, including fuzz sources.
- No source symlinks, build trees, object files, binaries, `.pyc` files, or
  `__pycache__` directories are intended in the sealed package.
- The source parent is the complete verifier-clean rev0807 archive; build
  products were not used as source.
- Third-party source is unchanged. Bundled SQLite 3.53.3 hashes remain pinned by
  CMake.
- The manifest is regenerated only after all handoff evidence is finalized and
  is verified against the exact package inventory.
- The ZIP is created with one `AnonSync/` root, normalized relative paths,
  deterministic member order, no symlinks, and verified CRCs.
