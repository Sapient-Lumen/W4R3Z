# Worked Example Independent Verification, Sampling & Replay Packets


**Purpose:** make claimed fixes independently checkable by defining what must be replayable and how closed cases should be sampled.

**Person served:** auditors, inspectors, ombuds staff, public-accountability teams, and implementers.

---

## Replay packet
A replay packet should let an independent checker reconstruct the before state, the claimed fix, the downstream systems that were supposed to update, and the evidence that the person was actually restored. Use risk-plus-random sampling for closed cases that involved stop-rule breaches, proof failures, vendor seams, or restoration lag.
