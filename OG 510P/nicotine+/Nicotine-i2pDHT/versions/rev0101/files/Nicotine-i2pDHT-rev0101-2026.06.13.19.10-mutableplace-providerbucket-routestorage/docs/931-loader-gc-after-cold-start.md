# Loader-GC after cold-start

Loader-GC separates soft loader cleanup from sticky tombstone and fallback memory.  Unloading native code does not make the artifact disappear as protocol evidence.

Loader-GC preserves:

```text
fallback route memory
cold-start memory
crash/quarantine memory when faults exist
unloaded/faulted artifact tombstones
```

Active loader handles are held, not garbage-collected as soft state.  Dropping the tombstone for a faulted or unloaded artifact quarantines.
