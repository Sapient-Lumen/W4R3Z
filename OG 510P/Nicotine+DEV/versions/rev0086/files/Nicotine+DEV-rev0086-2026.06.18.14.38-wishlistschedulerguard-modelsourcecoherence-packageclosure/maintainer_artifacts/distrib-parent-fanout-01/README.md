# DISTRIB-PARENT-FANOUT-01 maintainer artifact

Current-behavior pytest witness for rev0027. Run against a Nicotine+ checkout with:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q test_distributed_parent_fanout_reproducer.py
```

The assertions describe current behavior, not a proposed patch. They cover:

- `PossibleParents` lists larger than the documented maximum of 10 causing one outbound distributed-parent connection attempt per distinct listed user.
- Distinct claimed distributed-child usernames filling the distributed-child slot limit.
- Duplicate claimed distributed-child username replacement, which is PB-01 support rather than a new standalone report.
- `DistribBranchRoot` propagation of oversized branch-root strings from the current parent.
- 3.3.10-only server `EmbeddedMessage` forwarding of unsupported distributed message types, kept as a backport/support note because current/future lanes changed this behavior.
