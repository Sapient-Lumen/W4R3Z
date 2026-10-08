# TimeSync rev0120 audit — challenge receipt portability refactor

## Focus

rev0120 continues the mutation-survivor line by targeting detached authorized-verifier challenge/result records and their replay boundary. The goal was not to add a registry or a new challenge workflow; it was to prevent schema-shaped relabeling of existing salt/preimage challenge receipts into contradictory or stronger current-use claims.

## Findings

### Result-bearing records could be relabelled as bare challenges

The schema required `challenge_result` when `record_kind` was `authorized_verifier_challenge_result`, but it did not reject the inverse: a record with a full `challenge_result` could be mutated to `authorized_verifier_challenge` and still pass. That made the record kind weaker than the actual payload and could confuse downstream replay/audit handling.

### Matched results could carry non-matched disclosure rows

A `matched` challenge result could survive mutations that changed the top-level result to `mismatch`, or changed the only disclosure row to `not_verified`, without a consistency error. That was the highest-risk issue in this pass because it undermined the actual verification meaning while preserving the portable-result surface.

### Receipt flavor and digest binding were too loose

For salt/preimage review records, `authorization_scope`, requested material, `result_basis`, `receipt_kind`, and `receipt.digest.binds` were independently schema-valid. Mutating one field could re-label the same receipt as an external-system or selective-disclosure artifact while keeping the rest of the salt/preimage semantics.

### Not-portable boundaries could still advertise replay use

A portability boundary could be mutated to `not_portable` while leaving `result_may_be_replayed_for: [commitment_verification_only]`. The object then denied portability and advertised replay at the same time.

### Disclosure rows did not prove they pointed at the receipt digest

A disclosure row's `receipt_digest_value` could be changed away from `challenge_result.receipt.digest.value` and still pass. That left a row-level pointer unbound from the receipt it was supposed to summarize.

## Changes

- Added `tools/authorized_verifier_result_semantics.py` to own non-temporal authorized-verifier challenge/result semantics.
- `tools/validate_archive.py` now calls the new result-semantics helper alongside the existing temporal helper.
- Result-bearing records with `record_kind: authorized_verifier_challenge` now fail.
- `matched`, `mismatch`, `external_system_verified`, and `not_disclosed` challenge-result outcomes now have disclosure-row consistency checks.
- Salt/preimage verifier records now keep `authorization_scope`, requested material, result basis, receipt kind, and receipt digest binding aligned.
- `not_portable` or `not_replayable` boundaries cannot continue advertising replay uses.
- Disclosure-row `receipt_digest_value` must match `challenge_result.receipt.digest.value`.
- Extended mutation-survivor probes from 22 to 29.
- Added seven derivation-checked negative fixtures and semantic vectors `TV-N336` through `TV-N342`.

## Result

The revision validates with 361 semantic vectors and 29 mutation probes. The main risk closed is not a missing policy rule; it is contradictory verifier-result packaging where a current/portable commitment-verification receipt could be relabelled or internally weakened while staying schema-shaped.
