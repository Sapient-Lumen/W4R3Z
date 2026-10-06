# RFC-0122: Witnessed transparency checkpoints (split-view defense)

Status: **draft**

## Motivation

Transparency logs are only as strong as their split-view defenses.
If a log can equivocate (show different trees to different clients), targeted signing attacks may remain hidden.

DeriveBSD already treats transparency as optional evidence.
This RFC adds a generic evidence format for **witness-cosigned checkpoints** so policy can require it
in high-assurance channels.

## Goals

- Define a generic checkpoint receipt evidence object.
- Enable policy rules like “require >= N witness signatures”.
- Keep the verification story offline-capable.

## Non-goals

- Defining one universal witness network.
- Replacing existing transparency lanes (Rekor/Sigsum/SCITT).

## Proposal

### Evidence object: log.checkpoint.receipt

A receipt binds:
- a log checkpoint (tree head)
- the log’s signature
- a set of witness signatures attesting to consistency

Policy can enforce:
- witness threshold
- freshness window
- acceptable witness sets per channel

### Storage and bundling

- receipts and proofs are content-addressed blobs
- artifacts/attestations reference receipts by digest

### Relationship to existing lanes

- Rekor: receipt can represent a Rekor checkpoint if a witness layer is used
- Sigsum: maps naturally (tree head + witness signatures)
- SCITT: remains separate (statement registry receipts), but can also be witness-augmented

## References

- Sigsum design notes (gossip/witness): https://git.sigsum.org/sigsum/tree/doc/design.md
- Witness networks discussion: https://blog.transparency.dev/can-i-get-a-witness-network
