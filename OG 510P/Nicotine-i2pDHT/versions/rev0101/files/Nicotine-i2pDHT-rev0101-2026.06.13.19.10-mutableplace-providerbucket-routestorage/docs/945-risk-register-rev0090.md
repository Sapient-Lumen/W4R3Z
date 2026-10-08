# Risk register rev0090

Risk-first items:

- restart-discovered native artifact accidentally becomes dynamic load
- cold-start/probe/loader-GC evidence smuggles dispatch permission
- prior native lanes are not revalidated after restart
- loader-GC drops tombstone/fallback/quarantine/crash memory
- fold/audit drift hides the active native path

Mitigation in this cube:

- `nativehandoff.py` forbids load/dispatch at handoff
- `relaunchgate.py` requires prior-lane revalidation digests
- `loaderseal.py` preserves relaunch memory without granting load
- `nativefoldspine.py` audits the native branch sequence
