# Specific Items of Disagreement

## Poem

MOVE-OUT INSPECTION

ITEM | MOVE-OUT | COST TO CORRECT
WALLS/COVERINGS | GOOD | 0
FLOOR/COVERINGS | GOOD | 0
ELECTRICAL OUTLETS | GOOD | 0
HARDWARE/LOCKS | GOOD | 0
TOTAL | | 0

AGREE WITH MOVE-OUT INSPECTION [ ]
DISAGREE WITH MOVE-OUT INSPECTION [X]

SPECIFIC ITEMS OF DISAGREEMENT

WALLS/COVERINGS
one rectangle less faded,
four holes at its corners.

FLOOR/COVERINGS
four squares of standing pile.

ELECTRICAL OUTLETS
one plate darkened below the socket.

HARDWARE/LOCKS
fresh brass at the keyway.

VACANCY STATUS
occupied by persons
with usual residence elsewhere

## Disclosure

Disclosure: P0003-D002 / rev0063 is a machine-drafted SQLite write-ahead-log poem. Its draft-specific artifact is `poems/P0003/artifact/d002/specific_items.sqlite3` plus the required `specific_items.sqlite3-wal` sidecar. The main database alone holds the zero-cost move-out inspection with both response boxes blank. The WAL transaction changes only the disagreement box and appends the listed particulars and vacancy status. The main database bytes were verified unchanged before checkpoint. P0003-D002 is same-turn unjudged, not admitted, not evidence-ready, not an anthology candidate, and not a reader response.

The source pressure is literal. The HUD move-in/move-out inspection form uses the fields Item, Condition, Move-In, Move-Out, and Cost to Correct. Its move-out section provides Agree with move-out inspection and Disagree with move-out inspection choices. It instructs a disagreeing party to list specific items of disagreement. The Census Bureau's Housing Vacancy Survey definitions allow a vacant housing unit to be entirely occupied by persons who have a usual residence elsewhere. SQLite documents the WAL as part of persistent database state that must stay with the database when copied or moved. SQLite also warns that separating a database from its journal state can lose committed transactions or produce corruption.

No current/live reading is claimed; the verified states are packaged local artifacts, not a live service. Use `tools/check_wal_poem.py` on disposable read-only copies. P0003-D001 has received a later-turn revise-not-promote review; P0002-D010's real-reader response log remains empty; P0002-D028 remains terminal; and no P0002-D029 is created.
