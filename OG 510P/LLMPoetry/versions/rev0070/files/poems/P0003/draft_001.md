# Vacancy Journal

## Poem

VACANT

Room one: cleared
except for the nail's clean halo
where a calendar spent its years.

Room two: cleared
except the carpet keeps
the bed's four colder feet.

Kitchen: cleared.
Under the sink, a blue cup
has dried around its last inch.

No person remains.
The lock contains
three fresh brass filings.

No change is pending
in the body of the record.

The changes are committed
beside it.

## Disclosure

Disclosure: P0003-D001 / rev0062 is a machine-drafted SQLite write-ahead-log poem. The poem is packaged as `poems/P0003/artifact/vacancy.sqlite3` plus the required `vacancy.sqlite3-wal` sidecar: the main database alone reads a sparse clearance report, while the pair reads the committed poem printed above. The main database bytes were verified unchanged between the base checkpoint and the later commit. P0003-D001 is same-turn unjudged, not admitted, not evidence-ready, not an anthology candidate, and not a reader response.

SQLite preserves original content in the database file while changes are appended to a separate WAL file. A commit occurs when a special commit record is appended to the WAL. A checkpoint transfers transactions from the WAL back into the original database. The WAL file is part of the persistent state of the database and should be kept with the database when copied or moved. The shared-memory file contains no persistent content and can be recreated from the WAL.

No current/live reading is claimed; the verified states are packaged local artifacts, not a live database service. Use `tools/check_wal_poem.py` on disposable copies: an ordinary SQLite close may checkpoint and remove a copied WAL. P0002-D028 remains terminal, P0002-D010's real-reader response log remains empty, and no P0002-D029 is created.
