# Rev0858 repository hygiene

- No bundled third-party file changed.
- A final consistency pass found one generated `tools/__pycache__/*.pyc` file
  that an earlier projection had accidentally classified as active source. It
  was deleted before publication; the projection was recomputed from the clean
  tree and now binds exactly 299 files and 17,857,830 bytes.
- No generated Python bytecode, build tree, compiler output, VCS metadata, or
  executable is present in the release archive.
- The active implementation projection binds `.gitignore`, `CMakeLists.txt`,
  `include/`, `src/`, `tests/`, `tools/`, `third_party/`, and `fuzz/`.
- Historical evidence remains outside the active implementation projection.
- The active source delta is 7 files, 1,559 insertions, and 189 deletions.
- The source patch applies cleanly to the sealed rev0857 parent and all 7
  changed active files compare byte-for-byte with the final tree.
- The package root must be exactly `AnonSync/`; archive members must be unique,
  relative, nonsymlink, and represented exactly once in `MANIFEST.sha256`.
