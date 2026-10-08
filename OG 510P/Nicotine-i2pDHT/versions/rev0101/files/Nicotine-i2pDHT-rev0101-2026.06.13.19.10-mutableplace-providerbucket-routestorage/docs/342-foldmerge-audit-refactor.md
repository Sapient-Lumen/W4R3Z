# Foldmerge audit/refactor

The cloudtainer contained a second rev0033 branchlet named `persistjoin-foldreduce-samprobe`.  rev0034 folds that branchlet instead of discarding it:

- `persistjoin.py`, `samprobe.py`, and `foldreduce.py` are active source surfaces.
- The branchlet docs are preserved under `artifacts/branchlets/rev0033_persistjoin_samprobe/`.
- `foldmerge.py` audits the active rev0034 surfaces and the folded branchlet paths.
- `foldmap.py` and `surfaceledger.py` now know rev0034.

The refactor rule is to keep wake-from-amnesia value without letting duplicate branchlets silently diverge.
