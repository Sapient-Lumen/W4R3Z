# Store debt and repair pressure

`storedebt.py` joins store repair plans, replica receipt counts, custody proof counts, tombstone pressure, source/path family diversity, and local replay/fork checks.

It prevents a future repair loop from saying:

```text
we saw one useful store fact, so repair is done
```

The ledger distinguishes:

```text
accept_no_store_debt
plan_repair_replicas
plan_custody_audit
hold_useful_refusal_backoff
hold_need_family_diversity
quarantine_live_tombstone
quarantine_repair_plan
```

The important rule is tombstone-first: live tombstone pressure blocks stale storage convenience from becoming acceptance.
