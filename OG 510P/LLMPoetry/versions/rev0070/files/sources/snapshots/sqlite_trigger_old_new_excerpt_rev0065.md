# SQLite UPDATE triggers and OLD/NEW values — bounded documentation note (rev0065)

Source: official SQLite documentation, *CREATE TRIGGER*.
Accessed: 2026-06-18T04:34:00-04:00.
Evidence reference: turn515699view2 lines 199–212.

Bounded observations used in P0003-D004:

- An UPDATE trigger fires for updated rows; `UPDATE OF` restricts firing to a named field appearing in the SET clause.
- UPDATE triggers may read both OLD and NEW row values.
- D004 uses an AFTER UPDATE trigger to record the generated status before and after the one explicit field update.

This note verifies trigger semantics only; it is not literary evidence.
