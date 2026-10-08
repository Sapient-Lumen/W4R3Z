# Loader seal restart memory

The loader seal turns handoff and relaunch-gate evidence into restart-sticky local memory.

It joins:

- native handoff report
- relaunch gate report
- probe-corpus report
- loader-GC report
- artifact/source/fallback/oracle digests
- tombstone/fallback/quarantine/crash preservation

A seal is not load permission. It is the evidence that a relaunch candidate survived local boundary checks and may later be reconsidered by the selection/load lanes.

The seal quarantines memory drop, digest drift, replay, rollback, sequence forks, previous-link mismatch, low diversity, and hard-negative pressure.
