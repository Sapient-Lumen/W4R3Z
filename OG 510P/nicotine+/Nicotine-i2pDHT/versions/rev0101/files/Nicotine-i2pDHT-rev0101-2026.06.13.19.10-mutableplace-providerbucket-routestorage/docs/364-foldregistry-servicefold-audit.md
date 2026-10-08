# Foldregistry and servicefold audit

The cube has many historical fold modules. Deleting them would hurt wake-from-amnesia, but letting every revision invent a new hidden fold shape creates drift.

rev0036 adds `foldregistry.py`, a small declarative registry of current modules/tests/docs for this revision. `servicefold.py` then uses it alongside `foldmap`, `surfaceledger`, and rev0035 `startfold` predecessor checks.

The goal is not to remove old folds yet. The goal is to make the current fold path navigable enough that future revisions can consolidate without losing history.
