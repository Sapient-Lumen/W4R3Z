# Rev0815 repository hygiene

The active release projection binds `.gitignore`, `CMakeLists.txt`, and every
file under `include/`, `src/`, `tests/`, `tools/`, `third_party/`, and `fuzz/`.
It contains 156 files, 15,614,059 bytes, and digest
`2f4433dd281c096dccf58bfc292c2a71c9e39700f2d40743b3c50162f3cb69bf`.

The release archive excludes VCS metadata, build trees, CMake/Ninja generated
files, test runtime directories, object/static/shared files, executables, core
dumps, sanitizer profiles, Python bytecode and `__pycache__`, and temporary
SQLite databases or journals.

`MANIFEST.sha256` is regenerated only after the handoff evidence is complete and
lists every packaged file except itself. The release verifier rejects unsafe or
duplicate ZIP paths, symlinks, generated artifacts, revision drift, projection
drift, manifest inventory drift, file-hash mismatch, missing proof-surface
files, and ZIP CRC failure.

Build and validation trees remain outside the packaged source root under the
turn-specific `/tmp/anonsync-r0815/` workspace. The final package is built from
the reviewed source root into `/mnt/data` and is then independently reopened and
verified.
