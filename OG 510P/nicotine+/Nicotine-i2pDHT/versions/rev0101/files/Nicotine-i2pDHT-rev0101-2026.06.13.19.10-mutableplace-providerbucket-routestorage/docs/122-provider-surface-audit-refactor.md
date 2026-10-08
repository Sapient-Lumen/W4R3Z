# Provider surface audit/refactor

The cube has two historically useful provider modules:

```text
providerpoison.py   # earlier provider semantic-poison batch pressure
provider_poison.py  # newer provider memory/backoff/quarantine surface
```

The near-duplicate names are now an explicit audit/refactor debt, not an accidental ambiguity.

`HISTORICAL_SUPERSESSION.json` already marks `provider_poison.py` as the active surface.  rev0015 adds `provider_refactor.py`, which imports both modules, compares their public symbols, and records the current decision:

```text
keep_legacy_until_callers_are_migrated
```

This is not the final refactor.  It is the safety pin before the refactor: tests now make the overlap visible so a later revision can turn the legacy module into a compatibility wrapper or migrate callers module by module.

## Why not delete the old module now?

The cube is wake-from-amnesia documentation as much as code.  Deleting historical surfaces too early can erase why a design moved.  The right move is:

1. map supersession;
2. pin behavior with tests;
3. expose active/canonical surface;
4. migrate callers;
5. turn old surface into a wrapper or delete it once history is captured elsewhere.
