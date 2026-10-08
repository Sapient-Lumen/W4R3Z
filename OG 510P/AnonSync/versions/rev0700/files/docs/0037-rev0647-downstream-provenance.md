# Rev0647 — downstream provenance boundary hardening

## Why this was prioritized

Rev0646 closed the local service-path replay/ledger dual-write seam. The next highest-risk unfinished area was the relay/downstream boundary: after an outbox claim, the system wrote to a deterministic local SQLite downstream journal and later replayed that row to close the transition. That proved a local harness observation, but the row digest did not bind enough operator provenance to distinguish "same effect under the same adapter boundary" from "same effect key observed under a different adapter/config/handle arrangement."

The goal for rev0647 is deliberately narrow and practical: make the local downstream harness more honest and less replayable across adapter provenance drift, while avoiding another registry-only/doctrine pass.

## Substantive changes

1. **Provenance-bound result material.** Downstream result material moved from v1 to `anonsync-relay-downstream-result-v2-provenance-bound`. The digest now includes:
   - effect idempotency key;
   - prepared sequence;
   - prepared entry hash;
   - terminal state;
   - adapter id;
   - adapter kind;
   - adapter config SHA-256;
   - config handle;
   - registry SHA-256.

2. **Schema v2 downstream journal.** `downstream_profile` now records store format `anonsync-relay-downstream-store-v2-provenance-bound` and schema version 2. `downstream_effects` now records result material version plus adapter id/kind/config digest/handle/registry digest.

3. **Existing-row provenance check.** A replayed downstream row must match the current adapter provenance. If an operator changes adapter id, config digest, handle, or registry digest while pointing at the same downstream journal, the old row is rejected instead of being treated as a safe replay under the new boundary.

4. **Pre-claim symlink-family rejection.** Validation found that the first hardening pass rejected a downstream symlink only after claiming the outbox row. Rev0647 now rejects downstream SQLite symlink-family hazards before claim mutation, and the actual downstream open still uses `SQLITE_OPEN_NOFOLLOW` where available.

5. **WAL/FULL verification.** The downstream store verifies WAL mode and `synchronous=FULL`, sets a busy timeout, and uses `FULLMUTEX` on open.

6. **Report honesty.** The handle-bound relay report now emits revision `rev0647` and includes the provenance fields used in the downstream result digest.

## Audit/refactor slice

The relay path now carries one `RelayAdapterProvenance` object through digest generation, downstream store insertion/replay, and report emission. This is a small refactor but useful: the material that defines the boundary is no longer reassembled independently in each location.

The package validator was also turned into an adversarial regression rather than a metadata check. It verifies:

- exact v41 capability requirements;
- crash-after-downstream leaves an inflight claim and a provenance-bound downstream row;
- recovery under the same provenance replays the row and keeps the digest stable;
- a downstream symlink is rejected before outbox claim mutation;
- a retry under a different adapter/config/registry provenance rejects the existing row without mutating it;
- the original provenance can still recover afterward;
- v40/v1 downstream capability downgrade is rejected.

## What this does not solve

Rev0647 still does not implement a real external downstream adapter. The downstream store is local SQLite evidence, not proof that Stripe, a bank, a queue, or any remote service committed an effect. It also does not solve credentials, HSM custody, remote idempotency APIs, timeout/unknown-outcome reconciliation, or distributed failover.

The next risky step is still to build one real adapter with downstream-native idempotency and unknown-outcome reconciliation. Rev0647's value is that the local harness can no longer silently replay a downstream row across adapter provenance drift while pretending it is the same boundary.

## Validation

- Release-O0 CTest: 26/26 passed.
- `tools/validate_rev0647_downstream_provenance.py`: passed.
- Fresh extracted package validator: passed.
- Fresh extracted source rebuild and CTest: 26/26 passed.

Sanitizer coverage was not rerun in this revision; rev0647 does not claim ASAN/UBSAN evidence.
