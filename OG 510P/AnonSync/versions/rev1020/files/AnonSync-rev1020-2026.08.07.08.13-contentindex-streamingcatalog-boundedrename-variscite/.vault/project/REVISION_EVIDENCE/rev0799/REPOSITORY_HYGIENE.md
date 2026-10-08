# Rev0799 repository hygiene

The release tree contains no build directories, object files, static/shared
libraries, executables, Python bytecode/cache directories, VCS metadata, or
symlinks. All build trees and verbose validation logs remain outside the release
root. The active implementation projection is recomputed from package bytes.
`MANIFEST.sha256` is generated last and lists every other file exactly once.
