# Lifecycle validation runbook — rev0017

Run `make lint` before packaging. The validator now checks the rev0017 lifecycle surfaces in addition to earlier release invariants.

The validator is still not full JSON Schema enforcement. It does, however, now verify that lifecycle states exist, transitions reference known states, crosswalk rows reference known states, promotion templates are unused in rev0017, and forbidden transitions do not accidentally permit public claims or person/incident creation.

Future validators should turn the promotion receipt templates into enforceable checks before any live people, incidents, lawsuit merits, settlement amounts, Brady/Giglio records, or public displays are admitted.
