# Duplicate closure finality

`duplicateclosure.py` joins five surfaces at one exact boundary:

1. remote witness ledger;
2. repair outbox;
3. conflict cooldown;
4. repair publish gate;
5. repair ACK ledger.

Closure accepts only when repair ACK observations are diverse, previous-linked, digest-bound, and still carry contradiction memory.  The most important failure is the quiet one: a repair ACK arrives and compaction drops the contradiction that justified the repair.  rev0066 quarantines that case.

Duplicate closure is local finality, not network consensus.

Audit needle: duplicate closure.
