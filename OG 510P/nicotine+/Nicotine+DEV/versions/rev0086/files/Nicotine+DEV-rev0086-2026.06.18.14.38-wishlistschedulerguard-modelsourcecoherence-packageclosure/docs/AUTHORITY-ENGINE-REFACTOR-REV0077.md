# Packet-authority engine refactor — rev0077

## The maintenance defect

Rev0076 correctly introduced a machine-readable disposition ledger, but its validator encoded the current revision, source ref, exact packet IDs, shared-document exception, and buddy-search assertions directly in Python. Its JSON Schema also used revision and source-ref `const` values.

That design made every future revision choose between two bad outcomes:

1. copy and edit another validator, growing an append-only family of near-duplicates; or
2. keep running a stale validator whose hard-coded authority silently describes an older cube.

The machine-readable ledger had therefore moved policy out of prose but not yet separated **validation mechanism** from **current policy data**.

## Rev0077 architecture

```text
REVISION.txt
  derives current revision and snapshot/output filenames

data/current_packet_dispositions.schema.json
  revision-neutral structural contract; no concrete revision or commit

data/current_packet_disposition_contract.json
  current packet set and packet-specific exact assertions

data/current_packet_dispositions.json
  human/machine current authority

data/rev0077_packet_dispositions.json
  immutable current-revision snapshot

tools/validate_current_packet_dispositions.py
  stable, packet-agnostic validation mechanism
```

Per-packet source overrides now allow the ledger's primary `3.3.x` authority to coexist honestly with a master-only research packet. `SEARCH-AGAIN-SELF-01` records both the visible public head and the executable proxy rather than pretending one global source ref covers every packet.

## Invariants enforced by the generic engine

- `REVISION.txt` and ledger revision agree.
- The derived revision snapshot is byte-canonical and structurally equal to the current ledger.
- Source refs and optional executable refs are 40-character lowercase hexadecimal IDs.
- Packet IDs are unique and match the data-driven contract.
- Open or retired packets cannot select patches.
- Current-document and selected-artifact paths are relative, traversal-free, and present.
- Missing-evidence entries are strings and unique.
- The schema itself contains no concrete revision or source-ref constant.
- The contract, not Python, owns exact packet statuses and selected artifacts.

## Mutation testing

The rev0077 authority audit deliberately injects:

```text
duplicate packet ID
missing current document
selected patch on an open packet
snapshot divergence
contract/ledger divergence
revision mismatch
revision-hardcoded schema
```

Every mutant must be rejected for the intended invariant while the unmodified authority passes. The generic validator source is also scanned to ensure it contains neither current packet IDs nor a concrete revision literal.

## Historical preservation

The rev0076 validator remains in the cube as historical executable evidence. Its hard-coded schema was archived under `docs/archive/rev0076-status-authority/`. It is no longer a current entrypoint.

## Forward rule

Future revisions should update the ledger, its same-revision snapshot, and the JSON contract. They should not fork the generic validator unless the validation language itself needs a reviewed capability change.
