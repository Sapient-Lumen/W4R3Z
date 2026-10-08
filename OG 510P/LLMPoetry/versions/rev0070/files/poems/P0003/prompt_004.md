# P0003-D004 prompt / subtraction brief

Preserve D001, D002, and D003 draft and artifact bytes. Do not promote D003.

Subtract the HUD inspection branch, all room-trace imagery, and all explanatory ending. Keep only the strongest unresolved pressure in D003: a housing unit can be classified vacant while people are living in it because every occupant's usual residence is elsewhere.

The base database must already contain people living in the unit, every occupant's usual residence here, zero departure records, and an OCCUPIED generated status. The WAL may execute one explicit UPDATE only: change every occupant's usual residence from here to elsewhere. An AFTER UPDATE trigger must record the generated OCCUPIED-to-VACANT transition. The departures table must remain empty in both states. Render the page from a SQL view.

Use the new exhaustive state contract to enumerate every user table and prove which tables changed and which did not. The surface should be short enough that the classification—not the apparatus—carries the poem. Same-turn judgment is prohibited.
