# Provider surface audit/refactor — rev0017

The cube intentionally grew both `providerpoison.py` and `provider_poison.py` while tests were pinning behavior. rev0014 made the duplicate surface visible with `HISTORICAL_SUPERSESSION.json`. rev0016 scanned remaining imports. rev0017 makes the scan more useful.

`ProviderLegacyImport` now includes:

```text
historical: bool
```

`ProviderMigrationPlan` now exposes:

```text
legacy_import_count
historical_legacy_import_count
active_legacy_import_count
```

The current historical import is the rev0011 behavior-pinning test. That still counts as legacy usage, but it is different from new code accidentally importing the old surface.

The migration is not complete. The new distinction means the next refactor can choose one of two clean paths:

1. preserve old names with explicit adapters, then convert `providerpoison.py` into a compatibility wrapper;
2. migrate historical tests to canonical names while keeping a wake-from-amnesia note for the old behavior.
