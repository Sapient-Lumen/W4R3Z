# Next work after rev0872

1. Replace caller-supplied lease time with an owned observation record: clock
   source, boot identity, synchronization state, uncertainty, forward-jump
   quarantine, restart policy, and operator recovery must be explicit.
2. Add an authenticated terminal receiver record bound to exact operation
   bytes, sender attempt receipt, receiver actor epoch, channel binding, key
   epoch, and terminal/nonterminal outcome.
3. Build the receiver idempotency/effect owner so crash after an external effect
   but before acknowledgment cannot duplicate the effect.
4. Add an owned automatic wake/heartbeat scheduler using the exact receipt and
   durable fence; test suspend, restart, rollback, forward anomaly, contention,
   and process death.
5. Replace the full-history SQLite reference path with indexed point reads and
   an incremental projector, retaining the current owner as a differential
   oracle. Measure rows, I/O, WAL growth, allocations, and lock residence.
6. Persist retry provenance or use a pure attempt/age/dead-letter policy so
   restore can prove why a retry time is legal.
7. Continue toward membership, key lifecycle, authenticated peer transport,
   causal stability/compaction, metadata threat modeling, and the actual
   anonymity/privacy protocol. Do not treat the project name as an assurance.
