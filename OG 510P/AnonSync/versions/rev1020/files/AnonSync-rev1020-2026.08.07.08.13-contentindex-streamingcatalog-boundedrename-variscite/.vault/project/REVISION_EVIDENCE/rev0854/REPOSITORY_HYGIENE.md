# Rev0854 repository hygiene

The active release projection contains **279 files / 17,684,657 bytes**. The
source delta is confined to **23 active files**, with **1,161 insertions** and
**176 deletions**. Bundled third-party source is unchanged.

The exact active patch applies to the sealed rev0853 parent and reproduces all
**279/279** active files by path, byte count, and SHA-256. The patch application
records executable-mode warnings for two Python audits because the extracted
ZIP normalizes those modes; content comparison is exact and the release package
contains no symlinks or generated executables.

Audit imports created seven Python bytecode files under `tools/__pycache__`
during development. They were removed before active projection and packaging.
No `.pyc`, `__pycache__`, build tree, object file, test executable, VCS metadata,
or other generated binary is admitted by the release verifier.

The refactor adds one 152-line guard implementation and one 82-line public
internal header, while deleting two private scoped-mutex classes and forcing all
retained client-data claim operations through a compile-time mutex witness. The
new boundary reduces implementation duplication and makes a missing transition
fence a compiler error rather than a convention.

Historical `REVISION_EVIDENCE` remains much larger than the active first-party
implementation. Future handoffs should preserve cryptographic lineage while
considering external archival or deduplicated evidence storage so verification
history does not dominate routine source transfer.
