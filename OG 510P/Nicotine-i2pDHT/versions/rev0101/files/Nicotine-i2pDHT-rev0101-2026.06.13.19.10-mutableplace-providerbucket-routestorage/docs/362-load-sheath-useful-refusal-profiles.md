# Load sheath and useful-refusal profiles

A service catalog without a load sheath is a denial-of-service invitation. rev0036 adds a local per-window sheath that says how many units and streams each service class will accept, how much protected reserve it has, and how many useful refusals are permitted before the refusal lane itself becomes suspicious.

The load sheath is deliberately joined to the catalog digest. A valid load decision must not be transferable to a different service catalog or start profile.

Risk-first cases pinned by tests:

- protected seed/head/witness work survives overflow,
- overflow becomes useful refusal instead of silent drop,
- refusal-only loops are held,
- raw-key exposure budget overflows are quarantined,
- replayed windows are quarantined,
- every advertised service must have a budget.

Design guess: useful refusal is contribution evidence only when bounded. Infinite useful refusal is just a polite failure loop.
