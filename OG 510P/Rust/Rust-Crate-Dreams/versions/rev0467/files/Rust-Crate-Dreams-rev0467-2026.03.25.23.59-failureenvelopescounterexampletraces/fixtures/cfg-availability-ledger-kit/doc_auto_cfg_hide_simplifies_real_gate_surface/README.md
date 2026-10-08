# Scenario family — `doc(auto_cfg(hide(...)))` simplifies the visible gate surface

This fixture family exists for crates that deliberately simplify what rustdoc shows users.

It is meant to catch support drift such as:

- an item is guarded by a compound `cfg` expression,
- rustdoc auto-cfg is active and some terms are hidden or overridden for readability,
- the rendered documentation shows a shorter gate than the raw implementation gate,
- and a naive ledger mistakes the displayed marker for the full downstream-use condition.

A good availability ledger should make four things explicit:

1. which **slice witness** actually observed the item,
2. that the human-facing gate went through **normalization**,
3. whether the normalized gate is really equivalent to downstream use,
4. and whether manual review is needed before claiming the shorter gate is authoritative.
