# Scenario — source fix is observed, but manifest/docs/feature follow-through remains

This scenario freezes another common false-positive story for **P-0514**:

- `cargo fix` / `rustfix` can apply a machine-applicable source rewrite,
- but the migration still requires a manifest feature rename and docs/example follow-through,
- so the upgrade lane is not honestly “fully automated”.

Why it matters:

The Rust/Cargo substrate is real here.
But it is still mostly **source-suggestion** substrate.
A trustworthy upgrade pack therefore needs to say what the automation touched and what it did not.
