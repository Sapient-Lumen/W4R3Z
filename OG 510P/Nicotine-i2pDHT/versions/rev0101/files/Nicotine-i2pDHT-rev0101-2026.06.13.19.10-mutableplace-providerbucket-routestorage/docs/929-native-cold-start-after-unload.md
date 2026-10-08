# Native cold-start after unload

Native cold-start is a restart boundary.  A native artifact may be discovered on disk, but discovery cannot dynamically load it, dispatch it, or weaken Python fallback memory.

The cold-start capsule binds:

```text
unload digest
sandbox-stub digest
crash-GC digest
artifact/source/fallback digests
profile/operation/request boundary
fallback/quarantine/crash-memory preservation
family/path-family diversity
```

Accepted cold-start remains fallback-first.  If native is enabled and an artifact is present, the result is `hold_probe_required`, not load permission.
