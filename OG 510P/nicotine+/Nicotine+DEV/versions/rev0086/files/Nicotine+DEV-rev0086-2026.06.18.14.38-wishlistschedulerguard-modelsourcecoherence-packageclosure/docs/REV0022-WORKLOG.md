# rev0022 worklog

## Goal

Finish the rev0009 open question for **U-269**: whether completed advertised-size upload connections are merely bounded by idle timeout, or whether a receiving peer can keep the completed upload active by keeping the F socket alive.

## Work performed

```text
- Built maintainer-style pytest witness for TRANSFER-COMPLETE-LIFETIME-01 / U-269.
- Ran it against github-tag-3.3.10, github-branch-3.3.x, and github-branch-master.
- Captured source trace for slskproto upload completion, F-input, idle cleanup, recv, and close behavior.
- Refreshed public-overlap status for upload completion/stuck/incorrect-stat symptoms.
- Refactored transfer lifecycle cluster to keep U-269 separate from U-251/U-107/U-198 and strict U-123.
- Updated ranked queue, strict promotions, START-HERE, and next-revision queue.
```

## Result

```text
github-tag-3.3.10:   5 passed
github-branch-3.3.x: 5 passed
github-branch-master: 5 passed
```

Newly confirmed:

```text
- exact advertised-size upload write leaves upload active;
- silent completed upload eventually closes through idle timeout;
- one byte of invalid post-completion F input before each idle window keeps the completed upload active beyond the idle window;
- those post-completion bytes are discarded after FileOffset but still refresh activity;
- remote close retires the slot and reports non-timeout close.
```

## Decision

**U-269 remains audited backlog, not strict.** The behavior is real, but it is availability/slot-lifetime hardening for a peer already receiving an allowed upload, and public upload-completion/stuck symptom history is adjacent.

## Next target

**DOWNLOAD-INCOMPLETE-PROVENANCE-01**:

```text
U-226  incomplete resume trusts existing partial bytes by username/path
U-230  incomplete file entry opened without no-follow/regular-file/inode checks
U-250  advisory lock failure logged but ignored before writing remote data
U-253  ambiguous username/path boundary and basename truncation collisions
support checks: U-222, U-249
```
