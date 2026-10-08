# Archive lineage receipt page: version origin, restore authority, retention class, and blocked stronger sentences interface spec

## Purpose

This receipt preserves the archive story after the operator leaves the review flow.
It must answer later:

> what archived version was seen, what did it witness, who could restore it, what retention/visibility limits applied, and what stronger safety or recovery claim was explicitly refused?

## Receipt fields

Required fields:

- receipt id
- subject id / seat id / runtime id
- archived object path / version label if available
- provenance verdict
- restore-authority verdict
- retention class
- visibility class
- runtime requirement for restore
- survivor map summary
- strongest safe sentence
- blocked stronger sentence
- evidence freshness
- operator action taken / declined

## Example safe sentence

- `Archived bytes for this path were visible on this seat as historical witness of a remote change, but authoritative restore may still require a running RW seat and retention coverage was time- and size-bounded.`

## Rules

### Rule 1 — receipts must preserve blocked stronger language

Examples:

- `backed up here forever`
- `this seat can fully restore the file`
- `history survives uninstall`

### Rule 2 — receipts must preserve provenance and authority separately

A later reader must be able to see both what the bytes witnessed and whether this seat could act on them.

### Rule 3 — cleanup actions must not erase the record

Even if `.sync` or Archive is later removed, the receipt keeps the previous evidence boundary visible.
