# Foldreduce audit/refactor

The cube has many historical fold modules because each revision pinned wake-from-amnesia navigation. That history is useful, but active navigation should not require a reader to mentally execute every old fold.

`foldreduce.py` creates a rev0033 current fold around:

- `persistjoin.py`
- `samprobe.py`
- `foldreduce.py`
- `tests/test_rev0033_persistjoin_samprobe_foldreduce.py`
- docs `329` through `332`

It also checks predecessor folds rather than deleting them. The intent is fold reduction without amnesia: current path stays obvious; old path remains regression-visible.
