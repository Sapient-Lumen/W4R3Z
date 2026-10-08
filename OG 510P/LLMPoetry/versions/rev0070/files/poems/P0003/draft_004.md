# No One Left

## Poem

HOUSING UNIT

PERSONS LIVING IN UNIT | YES
EVERY OCCUPANT'S USUAL RESIDENCE | ELSEWHERE
DEPARTURES RECORDED | 0

PRIOR STATUS | OCCUPIED
CURRENT STATUS | VACANT

## Disclosure

Disclosure: P0003-D004 / rev0065 is a machine-drafted relational SQLite write-ahead-log poem. Its draft-specific artifact is `poems/P0003/artifact/d004/no_one_left.sqlite3` plus the required `no_one_left.sqlite3-wal` sidecar. The database alone already contains people living in the unit, every occupant's usual residence here, no departure rows, and a VIRTUAL generated status of OCCUPIED. The WAL executes one explicit UPDATE: it changes only the usual-residence field to elsewhere. An AFTER UPDATE trigger records the generated OCCUPIED-to-VACANT change. No housing-unit row is removed; the persons-living field remains YES and the departures table remains empty. The main database bytes were verified unchanged before checkpoint. P0003-D004 is same-turn unjudged, not admitted, not evidence-ready, not an anthology candidate, and not a reader response.

The source pressure is literal and bounded. Current Census Housing Vacancy Survey definitions say that an occupied unit's residents must consider it their usual residence or have no usual residence elsewhere, while a unit may be classified vacant when it is entirely occupied by people whose usual residence is elsewhere. SQLite documents that VIRTUAL generated columns are computed when read, that UPDATE triggers may use OLD and NEW row values, and that the WAL is part of persistent database state and must remain with the database. The D004 artifact uses a canonical exhaustive table-state contract: the tools snapshot every column and every row of every user table in primary-key order in both the database-alone and database/WAL states, so the unchanged zero-row departures table is verified rather than inferred.

The packaged Python runtime reports SQLite 3.46.1, a version within SQLite's documented WAL-reset-bug range. The build used one database connection, no concurrent writer, disabled automatic checkpointing, and no checkpoint during the committed transition, so it did not exercise the documented multi-connection write/checkpoint trigger. Inspect only disposable read-only copies with `tools/check_wal_poem.py`. No current/live housing value or real person's housing status is claimed. P0003-D003 has received one internal later-turn `revise_not_promote` review; P0002-D010's real-reader response log remains empty; P0002-D028 remains terminal; and no P0002-D029 is created.
