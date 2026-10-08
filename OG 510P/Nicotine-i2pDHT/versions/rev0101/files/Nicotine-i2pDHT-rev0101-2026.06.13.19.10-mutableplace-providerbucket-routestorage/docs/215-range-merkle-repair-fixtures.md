# Range Merkle repair fixtures

Range sketches are useful but too weak alone. A root mismatch only says “something in this region differs.” rev0024 adds a Merkle-ish fixture so repair can become exact:

```text
RangeMerkleLeaf -> leaf digest
RangeMerkleTree -> root digest + inclusion proofs
RangeMerkleSummary -> signed region root
RangeMerkleProof -> exact repair evidence
```

The tests cover inclusion proof verification, tamper failure, in-sync summaries, newer-root child repair, verified exact repair, tombstone-first proof handling, same-sequence root forks, bad proofs, and source-family monoculture.

The tombstone-first rule matters because stale provider or mutable-head evidence is operationally tempting. Deletion/revocation/compromise evidence must not be buried behind convenient liveness claims.

This remains a toy tree. The value is the pressure algebra, not the tree implementation.
