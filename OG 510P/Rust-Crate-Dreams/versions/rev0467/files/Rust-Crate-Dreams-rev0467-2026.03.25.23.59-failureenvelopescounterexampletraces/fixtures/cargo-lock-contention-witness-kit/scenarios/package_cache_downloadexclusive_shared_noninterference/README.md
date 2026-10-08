# Scenario — package-cache download-exclusive activity should not be over-read as blocking a shared-read build

This scenario exists to force **P-0490** to keep **same package-cache root** separate from **actually interfering lock mode**.

Cargo’s current `cache_lock` docs say `DownloadExclusive` does **not** interfere with `Shared`.
So a bundle that only notices “package-cache activity happened” should not automatically classify the build as blocked by package-cache locking.
