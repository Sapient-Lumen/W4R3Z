# rev0019 — signed garden budget receipts

Garden nodes should be allowed to say no well. A region-sweep audit can decide that a plan is overweight, tombstones are late, a family dominates, or there is nothing useful to do. rev0019 adds signed budget receipts so a garden can explain what it accepted, deferred, reordered, or refused.

`budgetreceipt.py` creates `GardenBudgetReceipt` and `BudgetReceiptBook`. A receipt binds to the sweep-audit transcript digest and source region-ledger report digest. It carries a monotonic sequence, scheduling window, action, accepted/deferred batch counts, and a signature.

The receipt is not currency, not global reputation, and not authority. It is local operator/debug evidence. The book rejects audit mismatches, action mismatches, stale sequences, bad signatures, and same-sequence forks.
