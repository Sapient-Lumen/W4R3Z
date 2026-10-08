# rev0163 — Rollback Declaration Snapshot

## Why this was the riskiest next seam

rev0162 made paid rollback receipts stronger by sealing `speculative_paid_action_declaration_hash` and the failed payment span. That was still not replay-complete enough: a verifier could see the committed rollback receipt and the declaration hash, but the discarded declaration payload itself was no longer present in committed `GameState`. The receipt was challengeable only by trusting the producer's side-channel memory of the discarded branch.

rev0163 closes that gap with a compact rollback-only declaration snapshot. Failed paid spell, activated-ability, and loyalty-ability transactions now retain enough declaration/cost-lock payload inside the terminal `PaidActionTransactionRecord` for a later validator, trace reader, or agent to recompute the discarded declaration hash.

## Code-bearing change

`PaidActionTransactionRecord` is now schema v3 and adds:

- `speculative_paid_action_declaration_snapshot_present`
- `speculative_paid_action_declaration_snapshot`

The snapshot is deliberately not appended to `paid_action_declaration_records`. It is audit/replay payload on the terminal rollback receipt, not a committed declaration. It carries the declaration identity, action kind, player/source/stack object identity, choice/cost-lock fields, and failed payment span context. It must not carry committed stack-placement links or its own committed declaration hash.

The validator now rejects rollback receipts that:

- omit the speculative declaration snapshot;
- seal a declaration hash that does not recompute from the snapshot;
- mismatch action kind, player, source object, or phase;
- carry committed stack-placement/declaration links inside the discarded snapshot;
- claim a total-cost lock without a valid locked cost payload.

Committed successful transactions are also guarded: they must not carry a speculative rollback snapshot.

## Rules grounding observed online

During this pass, the official Wizards rules page was rechecked. The current online Comprehensive Rules TXT observed for this session remains effective 2026-06-19. The local packaged rules metadata stays pinned to its existing 2026-04-17 source until a dedicated rules-refresh/diff revision.

The narrow spine used here is unchanged:

- 601.2f locks total cost before payment;
- 601.2g-h covers mana ability activation and payment;
- 602.2a-b puts activated abilities through the spell-casting steps where appropriate;
- 733.1-2 requires incomplete illegal actions to be reversed while preserving a reasoned audit trail in this engine.

## Audit/refactor result

This revision avoids another registry pass. The refactor is local and executable: one transaction schema bump, validator challenge checks, and strengthened paid rollback regressions. The release smoke stays all-in-one to avoid the cloudtainer waste of spawning a process per case.

## Remaining risk

The next replay risk is export/access. The engine now keeps the rollback snapshot in memory and validates it, but external trace/JSON surfaces still need a stable way to expose the snapshot so offline verifiers and agents can inspect it without linking directly against the C++ structs. Alternative/additional costs and cost modifiers remain future paid-transaction risk, but the rollback receipt spine is now materially more defensible.
