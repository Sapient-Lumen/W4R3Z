# Restart chaos crash-cut boundary

`restartchaos.py` models restart as an adversarial schedule. A handler replay report, side-effect journal report, handler quench report, and fuzz-ledger report can each be accepted while a crash still leaves sticky local memory unsafe.

The lane checks:

- required component acceptance and digest binding;
- prepared-only side effects that must not advance after restart;
- replay, rollback, sequence fork, previous-link mismatch, and phase drift;
- exact profile/service/scope/request binding;
- family/path diversity before restart memory is treated as useful.

This is not a database journal and not live transport. It is a local algebra for the hardest restart states before an I2P/SAM side effect exists.
