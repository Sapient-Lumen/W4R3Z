# Defect reproduction: release and cascade erased owner authority

## Prior release trace

1. Session `s` acquires owner generation `g`.
2. The exact generation is released.
3. Durable owner row remains with `lock_state='released'`.
4. Prior recipient policy accepts an empty capability for mutation.

Observed defect: crossing into owner-fenced mode was reversible through normal
release, without an administrative transition.

Rev0811 expected result: the independent mode row remains
`ownership_mode='owner-required'`, `latest_owner_lock_epoch=g`; empty capability
is rejected; a successor must be acquired.

## Prior checkpoint replacement trace

Schema relationship:

```sql
sync_session_resume_transfer_daemon_owner_locks.session_id
  REFERENCES sync_session_checkpoints(session_id) ON DELETE CASCADE
```

Trace:

1. Session `s` owns generation `g`.
2. Replacement executes:

   ```sql
   DELETE FROM sync_session_checkpoints WHERE session_id=?;
   ```

3. SQLite cascades deletion to the owner-lock child.
4. Replacement recreates the checkpoint root.
5. No durable owner row remains; the session can appear never owned.
6. A later acquisition can restart from generation 1.

Observed defect: destructive root reset erased both current authority and the
only monotonic generation memory.

## Rev0811 proof trace

1. Acquire generation `g`; create independent mode row with latest `g`.
2. Authorize reset with the exact capability inside a typed immediate write
   transaction.
3. Consume a private reset permit and delete the root.
4. Confirm the real cascade removes the owner-lock row.
5. Compare-and-replace the independent mode timestamp and reload exact evidence.
6. Commit replacement.
7. Reject empty-capability mutation because owner-required mode survives.
8. Acquire successor generation `g+1`.
9. Reject stale capability `g`; accept exact successor `g+1`.
10. Reject reuse of the consumed reset permit.

The focused SQLite test executes this trace against bundled SQLite and also
proves rollback, legacy backfill, transaction-generation binding, out-of-range
reset rejection before delete, and administrative-disabled mode behavior.
