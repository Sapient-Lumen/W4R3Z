# rev0867 repository and package hygiene

The release package is built from a clean staging copy that excludes `.git`, all
`build-*` trees, CMake products, binaries, object files, Python bytecode/cache,
and symlinks. `MANIFEST.sha256` enumerates every packaged file except itself.
The package verifier recomputes the manifest, active implementation projection,
revision-scoped required files, forbidden-artifact inventory, canonical root,
ZIP member uniqueness/path safety, symlink absence, and ZIP CRC integrity.

The active projection covers `.gitignore`, `CMakeLists.txt`, and all regular
files under `include/`, `src/`, `tests/`, `tools/`, `third_party/`, and `fuzz/`.
Documentation and historical evidence are intentionally outside that projection
but remain bound by the package manifest.

The rev0867 source patch contains only the ten intended active paths. It was
replayed against the exact verified rev0866 parent before packaging. No generated
file is used as source authority, and the final GCC dependency-closure build
reports `ninja: no work to do.`
