# Rev0801 repository hygiene

The release tree contains no symlinks, VCS metadata, build directories,
executables, object/static/shared libraries, CMake cache files, sanitizer
profiles, core files, or Python bytecode caches. Build products remain outside
the package root.

The active implementation projection binds `.gitignore`, `CMakeLists.txt`, and
every file under `include/`, `src/`, `tests/`, `tools/`, `third_party/`, and
`fuzz/`. `MANIFEST.sha256` separately binds every packaged file except itself.
