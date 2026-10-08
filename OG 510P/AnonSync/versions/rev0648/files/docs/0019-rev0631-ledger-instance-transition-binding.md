# rev0631 ledger-instance-bound terminal transition intents

## Risk addressed

rev0629 and rev0630 required signed transition intents and disabled raw terminal transition APIs. The remaining local replay seam was that a valid signed transition intent was bound to ledger heads and prepared row evidence, but not to a durable identity for the SQLite/WAL ledger instance that produced the pending-effect recovery report. A separately initialized ledger with compatible local evidence should not be able to consume an intent created for another ledger instance.

## Change

rev0631 introduces a persistent `ledger_identity` table and a generated lowercase SHA-256 `ledger_instance_id` for each new SQLite/WAL ledger. Pending-effect recovery reports expose the verified id. Signed transition-intent payloads include the id in the RS256 signing input. Terminal transition rows store the id, include it in the transition hash material, and are checked by mutable reload and the read-only snapshot verifier. Transition intent ids are unique within the ledger.

## Audit/refactor notes

The refactor keeps the decision ledger append-only and keeps effect transitions as their own append-only chain. It also makes read-only verification and mutable reload share the same ledger-instance equality invariant, reducing the chance that recovery reports, transition writing, and snapshot verification disagree about which ledger an effect belongs to.

## Remaining boundary

This does not solve exact byte-for-byte clone replay because a full copy carries `ledger_identity` with it. Preventing that requires an external monotonic root, hardware-backed key custody, distributed consensus, or a deployment-level anti-clone protocol. The purpose here is narrower: prevent signed terminal intents from being replayed across different initialized local ledger instances.
