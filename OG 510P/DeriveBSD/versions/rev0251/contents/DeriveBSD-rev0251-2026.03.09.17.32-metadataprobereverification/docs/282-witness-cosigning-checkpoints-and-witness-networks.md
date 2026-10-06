# Witness cosigning checkpoints (witness networks as an operable split-view defense)

A transparency log that no one watches is just a database.
A transparency log that can show different clients different trees is worse.

DeriveBSD already models:
- inclusion proofs (`transparency.proof`)
- monitoring (`transparency.monitor.*`)
- witnessed checkpoints (`log.checkpoint.receipt`)
- witness trust (`witness.policy`)

This doc tightens the *operational* story: how witness cosigning becomes a practical, tunable security parameter.

## Lesson to steal

- **Witness cosigning**: a checkpoint is only “good” if a quorum of independent witnesses also signs it *and* each witness signs only checkpoints consistent with what it previously signed.
- **Witness networks** turn split-view defense from “hope someone gossips” into a concrete deployment pattern.

This is a proactive complement to retroactive gossip.

## DeriveBSD mapping

### The checkpoint receipt is the unit of offline verification

`log.checkpoint.receipt` is checkpoint-evidence-only. It proves witnessed log state for an entry or capsule digest, but it does not authorize publication by itself; that authority stays in `release.publish.receipt`.

DeriveBSD’s generic object:

- `log-checkpoint-receipt` (`spec/log.checkpoint.receipt.schema.json`)

captures:
- log identity + log-signed checkpoint
- witness signatures
- `witness_policy_digest`
- `quorum_verdict`
- optional digest of consistency proof material
- optional binding to an artifact digest or statement digest

### Witness selection is policy (not hard-coded)

A system that wants strong split-view defenses must decide:

- which witness operators are acceptable (diversity matters)
- quorum thresholds (what do we require to *publish* vs to *consume*)
- failure mode when witnesses are unavailable (degrade vs halt)

That contract now lives in `witness.policy`.
It is the portable review surface for:

- allowed logs
- witness roster + keys
- operator-diversity grouping
- quorum thresholds
- shortfall behavior
- optional rotation overlap constraints

Receipts report observed signatures; they do not silently redefine trust.

### Publication flow sketch

1) publisher submits entry to log
2) publisher fetches the current checkpoint
3) publisher requests witness cosigns for that checkpoint (or receives already-cosigned checkpoints)
4) publisher bundles:
   - inclusion proof (`transparency.proof`)
   - checkpoint receipt (`log.checkpoint.receipt`)
   - later, `release.publish.receipt` can reference both as the transparency gate summary
5) consumers verify offline:
   - inclusion proof
   - log signature
   - `witness_policy_digest`
   - `quorum_verdict`

Monitors independently verify:
- checkpoint consistency
- in-scope policy violations
- whether checkpoint receipts still match the pinned witness policy

See: `docs/259-transparency-monitors-and-witness-gossip.md`, `docs/187-witnessed-transparency-checkpoints.md`, `docs/490-witness-policy-and-roster-quorum-boundary.md`.

### Keep receipts small; store blobs by digest

Receipts should carry digests to bulky proof material (Merkle paths, consistency proofs, transcripts), not embed them.
This preserves:
- offline verification
- bounded incident bundles
- dedup-friendly evidence storage

## Decision now taken

DeriveBSD no longer leaves roster/quorum handling as folklore.
`witness.policy` is the authoritative object for witness trust, while `log.checkpoint.receipt` stays evidence-only and must bind back to that policy via `witness_policy_digest`.

Last updated: 2026-03-07r219

See also: `docs/488-release-transparency-evidence-and-monitor-gate-boundary.md`, `docs/490-witness-policy-and-roster-quorum-boundary.md`.
