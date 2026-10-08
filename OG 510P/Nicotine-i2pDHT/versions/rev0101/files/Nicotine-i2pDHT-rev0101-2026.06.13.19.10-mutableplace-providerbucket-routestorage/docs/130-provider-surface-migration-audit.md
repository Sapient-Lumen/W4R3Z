# Provider surface migration audit

The cube has two provider-plane modules because earlier revisions intentionally explored two shapes:

```text
providerpoison.py    # legacy batch challenge/receipt analysis
provider_poison.py   # canonical current provider memory/quarantine/book surface
```

rev0015 made the duplication visible. rev0016 makes migration status executable.

`provider_refactor.py` now includes:

```text
find_provider_legacy_imports(root)
plan_provider_surface_migration(root)
ProviderMigrationPlan
```

The plan is intentionally lexical, not a full import graph. It scans `src/` and `tests/` for remaining imports of `i2p_dht_lab.providerpoison`. The current recommendation is:

```text
migrate_legacy_callers_before_wrapper
```

That is correct because `tests/test_rev0011_providerpoison_gardenrefusal.py` still pins historical legacy behavior. The cube should not delete that history casually. The next reasonable move is either:

1. add explicit adapters from canonical names to legacy behavior; or
2. migrate the rev0011 tests to a compatibility layer and turn `providerpoison.py` into a small wrapper.

The audit/refactor principle remains:

```text
supersede history before deleting history
```
