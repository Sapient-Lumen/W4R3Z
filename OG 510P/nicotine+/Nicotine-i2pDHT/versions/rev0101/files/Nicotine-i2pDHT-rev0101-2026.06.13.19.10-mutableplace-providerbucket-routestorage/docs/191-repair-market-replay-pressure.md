# Repair-market replay pressure

`repairmarket.py` evaluates one set of garden repair offers.  `repairreplay.py` evaluates repeated repair windows.

The new pressure surface catches:

- the same offer digest replayed across too many windows;
- repair offer sequence rollback for a garden key;
- repeated one-family repair abundance;
- useful-refusal backoff that should be honored instead of flooded through;
- not enough windows to form a local judgment.

The word “market” still does not mean money or global reputation.  It means local capacity selection with replay memory.
