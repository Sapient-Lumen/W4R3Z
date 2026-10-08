# rustdoc note and security stopgap do not settle long-term successor authority

This scenario shows why P-0515 needs `successor-authority.receipt.json`.

A deprecation note and an advisory can both tell downstream users to move.
But they do not carry the same authority class:
- rustdoc deprecation note: visible crate-authored deprecation surface,
- advisory: can justify a stopgap or migrate-now lane,
- off-ramp pack: can declare the long-term successor contract.

The fixture keeps those claims separate instead of flattening them into one fake “the successor is obvious” verdict.
