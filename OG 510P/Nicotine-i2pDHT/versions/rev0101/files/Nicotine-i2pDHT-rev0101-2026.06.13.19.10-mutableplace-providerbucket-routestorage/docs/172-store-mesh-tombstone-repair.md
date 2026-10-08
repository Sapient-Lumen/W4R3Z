# rev0019 — store mesh and tombstone repair

Sibling acknowledgements answer a narrow question: did this sibling claim to store this exact digest? That is necessary but not enough when mutable heads, tombstones, provider claims, and repair work interact.

`storemesh.py` joins sibling-cast acknowledgement reports into typed store rounds. The important posture is: **do not let mutable-head or provider storage outrun tombstone repair.** Tombstones remain evidence, not global deletion truth, but live tombstone evidence should block convenient resurrection through stale mutable/provider records.

The mesh currently recognizes immutable, provider, mutable-head, tombstone, and contact-lease records. It accepts when the required rounds are exact-digest and family-diverse; continues when tombstone repair or store pressure is incomplete; holds when useful refusals dominate; and quarantines contradictory acknowledgements or resurrection pressure.
