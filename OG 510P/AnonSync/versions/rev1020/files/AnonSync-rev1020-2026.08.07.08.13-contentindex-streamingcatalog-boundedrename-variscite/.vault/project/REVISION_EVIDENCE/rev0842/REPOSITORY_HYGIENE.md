# AnonSync rev0842 repository hygiene

- No VCS metadata, build tree, object file, static library, executable, Python bytecode,
  symlink, or temporary runtime artifact is intentionally packaged.
- Bundled SQLite 3.53.3 and all other bundled third-party files are unchanged.
- The active source patch changes 25 files, adds 3,912 lines, removes 881 lines, replays
  onto the sealed rev0841 parent, and matches all 246 active files byte-for-byte.
- Parent defect witnesses are short source excerpts and analysis only; no compiled witness
  binary is packaged.
- The three new persistence owners and shared primitive header are first-party C++20
  sources. Build products remain outside the package.
- Historical evidence remains disproportionately large: `REVISION_EVIDENCE` is about
  24.3 MB across 2,827 files before adding the current handoff. Rev0842 records this as
  repository debt and recommends content-addressed checkpoint archives.
- `MANIFEST.sha256` is generated after every package file is fixed and covers every file
  except itself.
