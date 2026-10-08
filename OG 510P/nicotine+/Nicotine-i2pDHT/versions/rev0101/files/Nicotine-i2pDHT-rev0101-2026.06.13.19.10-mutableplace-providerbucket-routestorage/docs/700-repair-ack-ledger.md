# Repair ACK ledger

`repairackledger.py` adds ACK memory for the repair publication itself.

A repair ACK is local evidence, not truth.  The ledger distinguishes:

- repair ACKed;
- repair NACKed;
- repair absent;
- mixed or undecided observations;
- replay and sequence forks;
- one-family ACK monoculture;
- hard-negative pressure.

The important rule is that a repair publication can be ready and still have no usable remote evidence.  NACK or mixed evidence keeps the system watchful instead of letting a retry/repair loop become fake progress.

Audit needle: repair ACK ledger.
