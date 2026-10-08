# No Cost to Correct

## Poem

MOVE-OUT INSPECTION

ITEM | MOVE-OUT | COST TO CORRECT
WALLS/COVERINGS | GOOD | 0
FLOORS/COVERINGS | GOOD | 0
HARDWARE/LOCKS | GOOD | 0
TOTAL | | 0

AGREE WITH MOVE-OUT INSPECTION [ ]
DISAGREE WITH MOVE-OUT INSPECTION [X]

SPECIFIC ITEMS OF DISAGREEMENT

WALLS/COVERINGS | GOOD | 0
one rectangle of first color,
four pinholes at its corners.

FLOORS/COVERINGS | GOOD | 0
four squares of pile
still pointing upward.

HARDWARE/LOCKS | GOOD | 0
one crescent at the keyway
polished back to brass.

NORMAL WEAR | YES
TOTAL COST TO CORRECT | 0

PERSONS PRESENT | YES
USUAL RESIDENCE | ELSEWHERE
VACANCY STATUS | VACANT

## Disclosure

Disclosure: P0003-D003 / rev0064 is a machine-drafted relational SQLite write-ahead-log poem. Its draft-specific artifact is `poems/P0003/artifact/d003/no_cost_to_correct.sqlite3` plus the required `no_cost_to_correct.sqlite3-wal` sidecar. The main database does not store a pre-rendered poem: it stores normalized inspection, response, disagreement, and occupancy relations, and a read-only SQL view renders the surface. The database alone contains three GOOD, zero-cost, normal-wear inspection rows and two blank response boxes. The WAL checks disagreement, inserts six detail rows and one occupancy row, and changes no inspection row. A VIRTUAL generated column computes `VACANT` when persons are present and their usual residence is elsewhere. The main database bytes were verified unchanged before checkpoint. P0003-D003 is same-turn unjudged, not admitted, not evidence-ready, not an anthology candidate, and not a reader response.

The source pressure is literal. HUD's move-in/move-out form records item, move-out condition, cost to correct, agreement or disagreement, and specific items of disagreement; its resident statement excepts normal wear from the duty to keep the unit in good condition and refers to restoring damage to original condition. HUD damage-claim guidance distinguishes extraordinary repairs from normal wear and routine maintenance. The Census Bureau's Housing Vacancy Survey definitions classify a unit temporarily occupied by persons whose usual residence is elsewhere as vacant. SQLite documents that VIRTUAL generated columns are computed when read, that a view is a named SELECT usable as a table source, and that a WAL is persistent database state that must remain paired with its database.

The packaged Python runtime reports SQLite 3.46.1. SQLite’s current WAL documentation places that version in a range affected by a rare concurrent write/checkpoint WAL-reset race; this build used one connection, no concurrent writer, disabled automatic checkpointing, and no checkpoint during the committed transition, so it did not exercise the documented trigger.

No current/live reading is claimed; no current/live housing value is claimed. The verified states are packaged local artifacts, not a service or empirical reader result. Use `tools/check_wal_poem.py` on disposable read-only copies. P0003-D002 has received a later-turn `revise_not_promote` review; P0002-D010's real-reader response log remains empty; P0002-D028 remains terminal; and no P0002-D029 is created.
