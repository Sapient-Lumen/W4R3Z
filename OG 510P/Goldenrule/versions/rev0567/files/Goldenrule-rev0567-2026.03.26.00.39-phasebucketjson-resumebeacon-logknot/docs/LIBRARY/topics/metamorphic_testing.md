# Metamorphic Testing (Oracle-Free Invariants)

Why this matters:
- In many social-dilemma simulations, the “correct answer” is not known.
- Metamorphic relations let us test *consistency properties* without requiring an oracle.

What Concord should build (concrete):
- Expand the metamorphic catalog beyond `player_swap_symmetry` and `scaling_prefix_stability`.
- Add eligibility rules as first-class outputs (why a check is “skipped”).
- Add metamorphic checks that specifically target:
  - RNG stream hygiene (adding unused randomness must not change outcomes),
  - symmetry under renaming strategy ids,
  - monotonicity under “more information” worlds (when applicable),
  - invariance of deterministic worlds under trace collection toggles.

Key references (local, open-access):
- General motivation for oracle-free testing in the project:
  - `docs/DEFINITIONS.md`
  - `crates/gr_engine/src/metamorphic.rs`

Notes:
- This topic is also a “project philosophy”: if we can’t specify what should happen, we should still be able to specify what must *not* happen.

