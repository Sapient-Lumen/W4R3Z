# rev0048 redress GC hard-negative retention

`redressgc.py` makes redress and moderation cleanup a protocol boundary.

Memory minimization is useful, but live hard negatives, active redress receipts, fork evidence, quarantine facts, and watch decisions must not be silently garbage-collected because a public bridge side effect depends on that local history.

Current test surface: `tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py`.
