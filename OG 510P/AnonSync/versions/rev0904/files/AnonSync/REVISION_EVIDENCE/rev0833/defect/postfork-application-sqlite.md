# Defect reproduction — application and SQLite work in fork-derived children

## Parent behavior

Rev0832 had four test call sites where the raw child executed substantial C++ or SQLite work before any exec boundary:

- atomic publication under concurrent writers;
- atomic publication under eleven crash cutpoints;
- payload-store commit and rollback crash recovery; and
- peer-schema attestation owner-close fail-stop.

Those paths inherited the parent process image, including library globals, allocator state, descriptors, signal state, and any thread-library bookkeeping. Several used blocking `waitpid` without a local timeout. The payload campaign closed its connection before fork, but SQLite had already been initialized in the process; a fresh image provides a materially stronger and simpler boundary than reasoning about every inherited global.

## Correction

Each campaign now launches the current executable through `SelfExecTestProcess`, verifies the fresh-image boundary before parsing an exact versioned instruction, reconstructs or validates all evidence, and uses a bounded exact-exit wait with kill-and-reap ownership.

## Proof

- exact source inventory declines from 20/13 to 16/9 raw calls/translation units;
- the four migrated files contain no raw fork or `waitpid`;
- direct runtime passes 327/327 checks;
- ten repeated executions of each changed runtime oracle pass; and
- the raw-fork and self-exec audits pass 10/10 and 30/30.
