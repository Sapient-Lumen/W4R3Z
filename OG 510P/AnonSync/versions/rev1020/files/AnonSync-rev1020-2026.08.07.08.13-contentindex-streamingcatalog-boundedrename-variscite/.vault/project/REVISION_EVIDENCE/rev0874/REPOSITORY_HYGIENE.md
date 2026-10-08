# AnonSync rev0874 repository hygiene

The release staging policy excludes VCS metadata, build trees, CMake-generated
state, object/static/shared libraries, executables, core dumps, coverage data,
Python bytecode/cache directories, and symlinks.

The three build trees used for validation live outside the source tree:

- `/mnt/data/build0874-debug`
- `/mnt/data/build0874-clang`
- `/mnt/data/build0874-asan`

The release verifier independently rejects forbidden paths and suffixes, unsafe
ZIP member spelling, duplicate ZIP members, symlinks, wrong canonical root,
manifest inventory mismatch, manifest digest mismatch, release-gate mismatch,
active-projection mismatch, and missing revision-scoped source/evidence.

`MANIFEST.sha256` intentionally excludes itself. Final directory and ZIP
verification reports are emitted outside the sealed artifact; embedding them
would mutate the bytes they attest.
