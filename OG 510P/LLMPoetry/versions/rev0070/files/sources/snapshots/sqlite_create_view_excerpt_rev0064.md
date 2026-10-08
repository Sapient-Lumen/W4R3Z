# SQLite CREATE VIEW — named read-only SELECT (rev0064)

Source: official SQLite CREATE VIEW documentation.
Accessed: 2026-06-18T02:33:00-04:00.
Evidence reference: turn685308view4 lines 103–111.

Bounded observations used in P0003-D003:

- CREATE VIEW assigns a name to a SELECT statement.
- A view can be used in another SELECT in place of a table name.
- SQLite views are read-only unless behavior is supplied through an INSTEAD OF trigger.

D003’s visible surface is rendered by a named view over normalized relations. This note is not a full SQL reference or quality evidence.
