# Scenario: shared target dir / lock hint

Purpose:
- prove that rebuild explanation can surface **cache-conflict context** without replacing the more specialized lock-contention crate.

Expected output shape:
- `cache-conflict.report.json` should classify the situation as `cache_conflict_possible`
- the scenario may point to an imported contention witness rather than duplicating its internals
