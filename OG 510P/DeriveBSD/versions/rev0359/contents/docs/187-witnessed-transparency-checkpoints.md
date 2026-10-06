# Witnessed transparency checkpoints (split-view defense lane)

Transparency logs help detect unexpected signing events.
But append-only logs have a well-known pitfall: a malicious/compromised log can present **split views**
(different clients see different trees) unless there is **gossip** or **witnessing**.

This doc captures an optional lane: require **witness-cosigned checkpoints** (or equivalent gossip proofs)
for high-assurance channels.

## Lesson to steal

Modern transparency systems increasingly rely on:
- **checkpoints** (signed tree heads)
- **consistency proofs** (append-only proofs between checkpoints)
- **witness cosigning** (independent parties co-sign checkpoints only after verifying consistency)

Sigsum explicitly builds gossip/witnessing into its design.
The broader transparency ecosystem is also converging on witness networks.

## DeriveBSD mapping

DeriveBSD already treats transparency as *optional evidence*.
This lane tightens the evidence definition so policy can require split-view defenses.

### Evidence object: log checkpoint receipt

Define a generic evidence object that can represent:
- a Sigsum tree head + witness signatures
- a Rekor checkpoint + witness signatures (if operating behind a witness network)
- other Merkle-log checkpoints

`log.checkpoint.receipt`:
- `log_id`
- `checkpoint` (tree_size, root_hash, timestamp)
- `log_signature`
- `witness_signatures[]` (threshold policy decides how many)
- `consistency_proof_digest` (optional; for audits / monitors)

Schema sketch: `spec/log.checkpoint.receipt.schema.json`.

### Policy use

Policy can express:
- “promotion into channel X requires a checkpoint receipt with >= N witness sigs"
- “consumption on fleet Y requires receipt freshness <= T"

### Offline verification

To preserve DeriveBSD’s offline story:
- store proof material as content-addressed blobs
- bind receipts to artifact digests (or statement digests for attestation logs)
- keep verifiers simple: validate signatures + membership proofs + witness threshold

## Where this plugs in

- cache publishing: attach checkpoint receipts to published artifacts/attestations
- verification: `derive verify` can require witnessed checkpoints for high-assurance channels
- monitoring: third parties can verify that a channel is not accepting unwitnessed checkpoints

Pointers:
- Rekor lane: `docs/59-transparency-log-rekor.md`
- Sigsum lane: `docs/131-sigsum-lightweight-transparency.md`
- SCITT receipts lane: `docs/132-scitt-ledger-receipts.md`

Last updated: 2026-02-24
