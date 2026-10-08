# Closure audit restart boundary

`closureaudit.py` joins repair settlement, closure archive, repair prune, archive journal, and prune replay.  Each component may be locally valid alone; closure audit asks whether all of them are valid for one exact object after restart.

It quarantines if contradiction memory is missing at any component or marker, if boundaries drift, if component digests drift, if marker chains fork, or if hard-negative pressure appears.

Design guess: **closure is a local audit result, not a cleanup side effect**.
