# AnonSync rev0844 repository hygiene

- Active implementation projection: 255 files / 17,317,398 bytes.
- Active source delta: 20 files / +4,380 / -413.
- Bundled third-party files changed: 0.
- New production namespace owner: 1,223 lines.
- New focused tests: 1,378 lines across three translation units, plus 91 lines
  added to the publication corpus.
- New structural audit: 628 lines and 37 obligations.
- Registered CTest inventory: 140; registered source/architecture audits: 40.
- `REVISION_EVIDENCE` before final rev0844 indexing: approximately 25 MiB and
  2,892 files.
- Package excludes `.git`, build trees, binaries, object files, Python caches,
  temporary logs, and cloudtainer work directories.

The revision deliberately accepts source growth to replace ambient pathname
operations with an explicit authority owner and executable crash corpus. That
trade should not become permanent accumulation: the next refactor should split
the namespace owner and replace source-spelling audit checks with semantic model
oracles where possible.
