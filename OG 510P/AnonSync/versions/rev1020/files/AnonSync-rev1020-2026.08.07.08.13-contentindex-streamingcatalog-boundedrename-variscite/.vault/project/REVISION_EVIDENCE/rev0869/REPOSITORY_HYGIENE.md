# Repository hygiene: AnonSync rev0869

The release package is built from a clean source staging root. Build trees,
CMake/Ninja state, compiler outputs, generated Python bytecode, VCS metadata,
symlinks, sockets, FIFOs, and device nodes are excluded.

The active implementation projection covers `.gitignore`, `CMakeLists.txt`, and
every regular file under `include/`, `src/`, `tests/`, `tools/`, `third_party/`,
and `fuzz/`. Documentation and historical evidence are outside that projection
but are covered by `MANIFEST.sha256`.

The exact rev0868 parent ZIP and extracted directory are independently verified.
A unified source patch is replayed against that parent in a separate directory,
and every final active file is compared byte-for-byte. The patch changes ten
active files and adds four.

The initial full-registry failure caused by the raw-fork crash probe and the
second failure caused by stale dependent audit counts are retained as evidence,
not erased. Final logs show the process-boundary correction and exact cross-audit
inventory update before the all-green registry run.

The deterministic ZIP has one `AnonSync/` root, unique safe paths, fixed member
timestamps, and no symlink entries.
