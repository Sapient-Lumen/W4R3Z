# Rev771 — fd-contained file access, mkparents, and explicit require authority

## Why this mattered

The previous containment work moved the low-level writer and several script file operations toward final cap-root checks, but three trust edges were still too easy to miss.

First, script-visible reads, directory lists, stats, recovery reads, and open-directory preflights still had places where the high-level capability check and the actual filesystem operation were separated by ordinary path use. A symlink or parent component could change between those moments.

Second, save-as/create paths knew when a target was missing at the freshness boundary, but an atomic `os.replace(...)` could still overwrite a file created in the tiny window after the final freshness check. That is the rare kind of race that does not show up in ordinary testing but is exactly what a data-loss boundary should defend.

Third, `mkparents` still created missing save-parent directories before the low-level writer got control. A scripted save could pass the early `cap.fs-root` preflight and then, if a parent component was swapped to a symlink before the parent-creation step, create directories through ambient process authority before the writer refused the final save.

A separate authority problem lived next to those file edges: `ed.require` reads and evaluates Micromax source. That is stronger than plain text read access, so it should not piggyback on `cap.fs-read`.

## What changed

New module:

`src/micromax_editor/file_access.py`

It centralizes fd-backed contained reads, directory listings, and stats. When a `cap.fs-root`/containment root is active, the helper performs the nominal path preflight, opens the target, checks the opened fd target through `/proc/self/fd` where available, and only then reads, lists, or stats from that fd. `ed.fs-read`, `ed.fs-list`, `ed.fs-stat`, recovery reads, and script/cap-root open directory preflight now share that seam.

`src/micromax_editor/file_write.py` now treats a previously missing target as a create-only commit. Direct writes use `O_EXCL` on that path. Atomic writes attempt a hard-link create from the same-directory temp file before falling back to replace, and a same-turn target creation becomes `FileFreshnessConflict` rather than an overwrite.

`file_write.ensure_parent_directory(...)` is now the parent-creation seam for save paths. Interactive saves keep ordinary `mkdir -p` behavior. Script/capability saves pass `containment_root`; on POSIX-capable hosts the helper walks from an opened root directory fd, creates missing components with `dir_fd`, and opens each component without following symlinks where supported. The fallback path still rechecks containment before and after creation.

`ed.require` now requires:

`cap.fs-require`

The hostcall still uses the same nominal `cap.fs-root` path policy and contained fd read path before evaluating source, but it no longer becomes available merely because `cap.fs-read` is enabled. The capability registry advertises `ed.require` through `cap.fs-require`, and `host.feature?` tracks that option.

`tools/mxtest.py` also gained `--max-new-chunks` for bounded aggregate probes. The runner can now execute only a requested number of fresh chunks and mark the remaining chunks as explicit `not_run` records in the manifest instead of implying completion or tempting callers to widen a diagnostic run.

## Regression coverage

Focused regressions cover:

- final-open symlink swaps for `ed.fs-read`, `ed.fs-list`, `ed.fs-stat`, and recovery reads;
- `ed.fs-list` continuing to classify child symlinks without following outside targets;
- save-as target creation after the final freshness check being refused without replacing the new file;
- scripted `save` with `mkparents` refusing a parent-component symlink swap without creating the would-be missing directory outside the root;
- `ed.require` disabled by default, enabled by `cap.fs-require`, rooted by `cap.fs-root`, and closed against late symlink swaps before outside source can be evaluated;
- docs-index cache-token behavior living in `tests/test_docs_index.py`;
- `mxtest --max-new-chunks` producing partial/not-run manifest evidence and refusing use without `--run-chunks`.

## Remaining risk

This remains an application-level containment boundary, not an OS sandbox. On platforms without `/proc/self/fd` or descriptor-relative directory creation support, the fallback checks are still safer than the previous raw path use but cannot close races as tightly as the POSIX fd path.

The hard-link create step for missing-target atomic saves depends on filesystem support for same-directory hard links. Where unavailable, the writer still has the existing freshness checks and direct-write `O_EXCL` path, but the atomic missing-target create race is strongest on filesystems that support the link step.

Core VM `include` / `require` / `reload` remain language-level file-loading primitives for ordinary Micromax execution. This revision hardens the editor bridge hostcall `ed.require`; a later design pass should decide whether editor-owned VMs should shadow or policy-wrap the core file-loading words when running untrusted script contexts.
