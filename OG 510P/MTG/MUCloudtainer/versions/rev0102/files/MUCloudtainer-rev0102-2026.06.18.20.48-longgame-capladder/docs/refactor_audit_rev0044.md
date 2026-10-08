# rev0044 refactor and audit notes

The useful refactor is in:

```text
src/muc5/action_hard_racing.py
```

The old hard-frame online collector mixed two concerns:

```text
public hard-frame selection
expensive branch racing / C++ shadow checking
```

rev0044 extracts:

```text
_race_selected_snapshots(...)
```

so future selectors can rerank a public-safe candidate pool without duplicating the branch rollout machinery.  `collect_hard_frame_online_racing(...)` still behaves as before; it now calls the helper internally.

New audit checks verify:

```text
margin-screen model JSON exists
historical label rows were used
holdout rows were written
selected/candidate/branch/allocation/C++ rows match summary counts
branch truncations are zero
C++ skipped/mismatch counts are zero
decisive label count is nonzero
required rev0044 docs/scripts/tests are present
```
