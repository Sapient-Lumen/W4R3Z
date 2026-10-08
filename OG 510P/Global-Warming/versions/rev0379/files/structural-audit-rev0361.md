# Structural audit rev0361

This revision advances the rev0360 one-command preflight from a point-in-time result into a repeatable one-shot watchdog layer. The strongest correction is operational: a green-looking check row now means only **capture-ready / claim-frozen**, never readiness.

## Added

- Live watchdog invariant catalog.
- Packet drift alarm board for all 60 must-capture packets.
- Shift handoff board for 20 operator roles.
- Watchdog validator with 54 non-closure tests.
- SQLite views for leak, loss cap, claim freeze, handoff, drift alarm, and workorder counts.

## Risk deliberately not closed

No real or anonymized June 2026 exercise packets were imported. All readiness, pass, green, safe, sufficient, certified, demonstrated, released, and closed language remains embargoed.
