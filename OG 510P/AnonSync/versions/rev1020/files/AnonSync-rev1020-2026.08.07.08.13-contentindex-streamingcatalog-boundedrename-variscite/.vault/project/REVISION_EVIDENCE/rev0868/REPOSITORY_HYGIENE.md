# Repository hygiene: AnonSync rev0868

The release package is constructed from a clean staging copy of the source
root. Build directories, compiler products, CMake/Ninja state, generated Python
bytecode, VCS metadata, symlinks, sockets, FIFOs, and device nodes are excluded.

The active implementation projection includes `.gitignore`, `CMakeLists.txt`,
and every regular file under `include/`, `src/`, `tests/`, `tools/`,
`third_party/`, and `fuzz/`. Documentation and historical evidence are outside
that projection but remain covered by `MANIFEST.sha256`.

The parent rev0867 ZIP and extracted directory are independently verified before
lineage is asserted. A unified source patch is generated against the exact
parent, replayed in a separate copy, and all final active files are compared
byte-for-byte. Final directory and ZIP package verification are run only after
projection, release gate, evidence index, and manifest publication.

The final archive has one canonical `AnonSync/` root and contains no duplicate
paths or unsafe path components.
