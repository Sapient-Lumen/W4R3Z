# Rev0798 repository hygiene

The release tree contains no build directories, object files, static/shared
libraries, executables, Python bytecode/cache directories, VCS metadata, or
symlinks. Build products and final package-verifier reports remain outside the
release root. `MANIFEST.sha256` is generated last and lists every other file
exactly once.
