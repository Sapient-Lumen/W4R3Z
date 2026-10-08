# AnonSync rev0841 repository hygiene

- No build directory, object, static library, executable, Python bytecode, VCS metadata,
  symlink, or temporary test artifact is intentionally packaged.
- The parent defect witness includes source and text output only; its compiled executable
  is excluded.
- Bundled SQLite 3.53.3 is unchanged.
- The active source patch changes six files and replays exactly onto the sealed rev0840
  parent.
- Historical evidence remains large; rev0841 adds a compact current handoff and recommends
  content-addressed archival rather than recursive growth in future normal revisions.
- `MANIFEST.sha256` is generated last and covers every packaged file except itself.
