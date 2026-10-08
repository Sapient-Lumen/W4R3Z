# Rollback probe before retry

A retry after missing ACK can duplicate a public side effect unless local memory first asks whether a remote commit may already have happened.  `rollbackprobe.py` models that as no-network observations:

```text
no_remote_commit_seen
remote_commit_seen
endpoint_unreachable
payload_mismatch_seen
```

These observations are not global truth.  They are exact-boundary evidence.  `remote_commit_seen` and `payload_mismatch_seen` quarantine the retry path.  `endpoint_unreachable` holds instead of granting retry authority.

needle: rollback probe
