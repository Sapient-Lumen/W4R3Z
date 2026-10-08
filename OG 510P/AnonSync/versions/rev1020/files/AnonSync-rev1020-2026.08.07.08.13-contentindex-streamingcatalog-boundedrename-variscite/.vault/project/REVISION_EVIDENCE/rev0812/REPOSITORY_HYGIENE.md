# Rev0812 repository hygiene

The release archive contains one canonical root, `AnonSync/`, and the complete
source, test, audit, evidence, and bundled SQLite trees required to reproduce the
current graph.

Excluded from the package:

- build directories and CMake/Ninja generated files;
- object files, static/shared libraries, executables, debug symbols, profiles,
  coverage output, and core dumps;
- VCS metadata;
- Python cache files;
- temporary databases, logs outside revision evidence, sanitizer scratch trees,
  and package staging directories.

The active implementation projection has 154 files and 15,514,571 bytes. It
contains 49 production C++ files, 38 production headers, 32 C++ test files, and
5 fuzz C++ files. Bundled SQLite 3.53.3 is retained unchanged.

`MANIFEST.sha256` lists every package file except itself and is the exact package
inventory. `tools/verify_release_package.py` recomputes every manifest hash,
active projection, revision binding, safety exclusion, canonical root, and ZIP
CRC before publication.
