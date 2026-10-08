
# Python surface added in rev0008

New module:

```text
src/i2p_dht_lab/mutable_future.py
```

New tests:

```text
tests/test_mutable_future.py
```

New objects:

```text
OpenQuestion
MutableDream
SeedPortfolioEntry
SeedPortfolio
PolicyPointer
PolicyPortfolio
HeadObservation
HeadHealth
```

New helpers:

```text
open_question_register()
dream_register()
slot_salt()
analyze_head_observations()
```

The code remains toy scaffolding. The important point is that seed portfolios, policy portfolios, and rollback/fork detection are now executable surfaces rather than prose only.
