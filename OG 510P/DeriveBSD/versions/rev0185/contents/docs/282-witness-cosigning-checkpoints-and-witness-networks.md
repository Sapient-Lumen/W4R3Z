# Witness cosigning checkpoints (witness networks as an operable split-view defense)

A transparency log that no one watches is just a database.
A transparency log that can show different clients different trees is worse.

DeriveBSD already models:
- inclusion proofs (`transparency.proof`)
- monitoring (`transparency.monitor.*`)
- witnessed checkpoints (`log.checkpoint.receipt`)

This doc tightens the *operational* story: how witness cosigning becomes a practical, tunable security parameter.

## Lesson to steal

- **Witness cosigning**: a checkpoint is only “good” if a quorum of independent witnesses also signs it *and* each witness
  signs only checkpoints consistent with what it previously signed.
- **Witness networks** turn split-view defense from "hope someone gossips" into a concrete deployment pattern.

This is a proactive complement to retroactive gossip.

## DeriveBSD mapping

### The checkpoint receipt is the unit of offline verification

DeriveBSD’s generic object:

- `log-checkpoint-receipt` (`spec/log.checkpoint.receipt.schema.json`)

captures:
- log identity + log-signed checkpoint
- witness signatures
- optional digest of consistency proof material
- optional binding to an artifact digest or statement digest

A high-assurance channel can require:
- witness quorum `>= N`
- freshness window `<= T`

### Witness selection is policy (not hard-coded)

A system that wants strong split-view defenses must decide:

- which witness operators are acceptable (diversity matters)
- quorum thresholds (what do we require to *publish* vs to *consume*)
- failure mode when witnesses are unavailable (degrade vs halt)

This should be expressed as policy in the same way we treat cache trust and release authority.

### Publication flow sketch

1) publisher submits entry to log
2) publisher fetches the current checkpoint
3) publisher requests witness cosigns for that checkpoint (or receives already-cosigned checkpoints)
4) publisher bundles:
   - inclusion proof (`transparency.proof`)
   - checkpoint receipt (`log.checkpoint.receipt`)
5) consumers verify offline:
   - inclusion proof
   - log signature
   - witness threshold

Monitors independently verify:
- checkpoint consistency
- in-scope policy violations

See: `docs/259-transparency-monitors-and-witness-gossip.md`, `docs/187-witnessed-transparency-checkpoints.md`.

### Keep receipts small; store blobs by digest

Receipts should carry digests to bulky proof material (Merkle paths, consistency proofs, transcripts), not embed them.
This preserves:
- offline verification
- bounded incident bundles
- dedup-friendly evidence storage

## Open questions (to push into ADRs)

- Do we require cosigned checkpoints for *publish*, *consume*, or both?
- What are the default witness sets for community channels vs private fleets?
- How do we rotate witness keys and witness membership without bricking verification?

Last updated: 2026-02-25
