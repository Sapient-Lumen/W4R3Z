# Custody/evidence GC join

`src/i2p_dht_lab/custodygc.py` normalizes custody audit reports, tombstone-mesh reports, witness-cache summaries, and revocation-head verdicts into ordinary `EvidenceItem` records before running `evidencegc.py`.

The design guess is conservative:

```text
hard negative evidence should be synthesized early and retained before convenience evidence gets a vote.
```

The module does not decide deletion truth or custody truth. It only prevents local memory hygiene from becoming a resurrection surface. Quarantined custody proofs, tombstones that block resurrection, witness contradictions, and risky revocation-head verdicts become typed local evidence.
