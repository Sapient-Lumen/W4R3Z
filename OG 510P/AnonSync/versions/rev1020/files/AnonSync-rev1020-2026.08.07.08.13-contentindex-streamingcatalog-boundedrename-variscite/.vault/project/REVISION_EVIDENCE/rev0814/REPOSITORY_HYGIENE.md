# Rev0814 repository hygiene

The release projection contains `.gitignore`, `CMakeLists.txt`, and all files
under `include/`, `src/`, `tests/`, `tools/`, `third_party/`, and `fuzz/`.
`ACTIVE_IMPLEMENTATION_PROJECTION.json` binds every active path, size, and digest.

The archive excludes `.git`, build directories, `CMakeFiles`, `Testing`, object
files, static/shared libraries, executables, core dumps, Python bytecode,
`__pycache__`, sanitizer profiles, and temporary SQLite artifacts. The package
manifest lists every archive file except itself. The release verifier rejects
unsafe/duplicate ZIP paths, symlinks, generated artifacts, revision drift,
projection drift, manifest drift, hash mismatch, and CRC failure.
