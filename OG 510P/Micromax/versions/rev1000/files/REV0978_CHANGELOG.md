# Rev0978 changelog — result drainage and pipe-owner teardown

## Filesystem workers

- Added one shared receive-before-join collector for contained stat, access,
  batched stat, read, and directory-list workers.
- Removed join-before-drain false timeouts for large queue payloads.
- Added finite receive, short reap grace, terminate/kill fallback, malformed
  result checks, and queue/process close behavior on every path.
- Preserved direct mode, containment, file-size, row, and timeout contracts.
- Added real large-result regressions through `Editor.open_file`, `ed.fs-read`,
  and `ed.fs-list`, plus abnormal IPC lifecycle coverage.

## Bounded subprocess capture

- Named capture I/O threads and joined them against one absolute drain deadline.
- On missing EOF, use the confirmed process group as a portable fallback and,
  on Linux, signal only exact processes holding Micromax's anonymous capture
  pipes through pidfds when available.
- Escalate ignored TERM under short finite grace periods.
- Prefer pidfd-stable signaling after pipe revalidation; on older Linux, recheck
  both `/proc` start time and exact pipe ownership immediately before numeric
  signaling to narrow—but not eliminate—the reuse race.
- Preserve successfully launched background jobs that redirected all standard
  descriptors, including a same-group sibling beside another child that retained
  a capture pipe.
- Added argv and shell regressions for same-group and new-session pipe owners,
  ignored TERM, no thread residue, and detached-job preservation.

## Audit and documentation

- Added structural checks for filesystem queue ordering and subprocess pipe
  ownership.
- Added the online-research, measured-failure, implementation, evidence, and
  residual-risk record in
  `docs/935-process-capture-pipe-ownership.md`.
- Updated current mission, roadmap, decisions, security boundary, worklist,
  revision index, README, TODO, and generated context.
- Added the rev0978 evidence triplet to the curated handoff and rotated rev0972
  evidence into `docs/history/`, preserving the 64-document context ceiling.
