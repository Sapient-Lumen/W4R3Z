# Repository hygiene: AnonSync rev0870

The release package is staged from one canonical source root. Build trees,
CMake/Ninja state, compiler outputs, generated Python bytecode, VCS metadata,
symlinks, sockets, FIFOs, and device nodes are excluded.

The active implementation projection covers `.gitignore`, `CMakeLists.txt`, and
every regular file under `include/`, `src/`, `tests/`, `tools/`, `third_party/`,
and `fuzz/`. It contains 337 files and 18,680,561 bytes. Documentation and
historical evidence are outside that projection but are covered by
`MANIFEST.sha256`.

The exact rev0869 parent ZIP and extracted directory are independently verified.
A unified source patch is replayed against that parent in a separate directory,
and all 337 final active files are compared byte-for-byte. The patch changes ten
active files, adds four, and removes none.

The complete registered test claim is deliberately split: the main invocation
was observed through test 146 before the command window closed, and tests
147–174 passed in an isolated tail invocation. The package does not claim one
uninterrupted 174-test run. Likewise, the owner-test static-analyzer command is
retained but its completion is not claimed.

The final ZIP has one `AnonSync/` root, unique normalized paths, fixed member
timestamps, ordinary-file modes, and no symlink entries.
