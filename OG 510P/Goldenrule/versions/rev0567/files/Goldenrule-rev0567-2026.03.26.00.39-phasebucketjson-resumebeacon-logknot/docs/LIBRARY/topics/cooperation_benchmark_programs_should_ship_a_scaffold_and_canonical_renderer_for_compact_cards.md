# Cooperation benchmark programs should ship a scaffold and canonical renderer for compact cards

Once the archive already has one machine-checkable compact card schema, the next low-byte/high-leverage move is to remove avoidable friction from **filling** and **reviewing** those cards.

The archive should therefore keep one tiny operational pair next to the schema:

1. one **scaffold** path that emits a valid compact card with every required field present;
2. one **canonical renderer** that turns any valid card into a stable human-readable markdown review surface.

Why this belongs in the archive:

- `RS-GR-111` says benchmark documentation becomes more interpretable when it follows a standardized structure, which points toward deterministic field names and deterministic review surfaces.
- `RS-GR-112` says many benchmarks still do not make replication easy, which points toward minimizing inheritor-side setup work when a new result needs to be recorded.
- `RS-GR-114` says machine-actionable metadata improves reuse by both people and machines, which points toward a schema-backed object that can also be rendered consistently for human inspection.

So the benchmark program should not stop at a schema and worked JSON example alone.
It should also ship one **small scaffold command** and one **canonical markdown render path**.

The scaffold prevents future sessions from reintroducing silent omissions, ad hoc field renaming, or inconsistent placeholder conventions.
The renderer prevents every inheritor from inventing a new one-off human summary layer around the same JSON object.

Keep both tools compact and deterministic:

- no bulky benchmark-specific payload generation;
- no network dependence;
- no hidden defaults that erase required fields;
- explicit `not applicable: ...` strings instead of silent omission when a required row does not apply.

A scaffold plus a canonical renderer make the compact card easier to instantiate, diff, audit, and hand off **without widening the archive**.
