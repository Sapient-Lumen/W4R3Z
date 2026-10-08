# Native handoff relaunch candidate

Native handoff is the boundary between restart-time evidence and a future relaunch plan.

It joins:

- native cold-start report
- probe-corpus report
- loader-GC report
- artifact/source/fallback digests
- Python oracle digest
- tombstone/fallback/quarantine/crash memory preservation
- exact operation boundary

The handoff can output `accept_relaunch_candidate`, but that still means:

```text
fallback active
native load forbidden
dispatch forbidden
candidate only
```

Dangerous cases are quarantined: digest drift, replay, rollback, same-sequence fork, previous-link mismatch, low diversity, memory drop, and any load/dispatch attempt.
