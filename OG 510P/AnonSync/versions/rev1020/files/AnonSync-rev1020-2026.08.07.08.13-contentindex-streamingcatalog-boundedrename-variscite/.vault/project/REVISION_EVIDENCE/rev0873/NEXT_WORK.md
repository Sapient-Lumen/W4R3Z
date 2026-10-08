# Next work after rev0873

1. Replace caller-supplied epoch values with an owned clock observation record:
   source, boot/session identity, synchronization state, uncertainty, maximum
   forward step, anomaly quarantine, restart rule, and explicit recovery.
2. Add a retry-decision record that classifies failure, owns deterministic
   exponential backoff and jitter, caps attempt count and age, and transitions
   poison work to a bounded dead-letter/remediation state.
3. Build an indexed wake scheduler and automatic heartbeat owner using the exact
   lease receipt, retry provenance, and time fence. Test suspend, restart,
   rollback, forward anomaly, contention, and process death.
4. Add an authenticated terminal receiver record bound to exact operation bytes,
   sender attempt, receiver actor/key epoch, channel binding, and outcome.
5. Build the receiver idempotency/effect owner so crash after an external effect
   but before acknowledgment cannot duplicate that effect; include atomic
   visible-file publication and payload/chunk commitments.
6. Replace the full-history SQLite hot path with indexed point reads and exact
   conditional updates, keeping the current implementation as differential
   oracle, migration verifier, periodic auditor, and repair authority.
7. Implement membership/key lifecycle, authenticated transport, causal
   stability/compaction, old-replica rejoin policy, physical resource metering,
   and the privacy threat model. Do not treat the project name as assurance.
