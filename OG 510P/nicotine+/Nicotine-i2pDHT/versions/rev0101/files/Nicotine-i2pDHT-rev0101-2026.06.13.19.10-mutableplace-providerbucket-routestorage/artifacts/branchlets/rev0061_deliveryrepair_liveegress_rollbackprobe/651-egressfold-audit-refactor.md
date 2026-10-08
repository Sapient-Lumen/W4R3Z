# egressfold audit/refactor

`egressfold.py` is the rev0061 current-path fold.  It checks that the delivery repair, rollback probe, live egress, tests, docs, public pointers, fold map, fold registry, and surface ledger all expose the same current seam.

It also runs the rev0060 `fenceaudit` predecessor.  This keeps the send-fence restart-memory boundary visible while adding the new repair/retry path.
