# Proxy artifact receipt page — entry class, counterpart scope, and safe language

## Purpose

Produce a durable receipt that records what the visible entry actually was, what it stood for, what action scope was reviewed, and what sentence is safe to reuse later.

## Receipt fields

### Identity
- receipt id
- subject / lineage if known
- visible entry name and path
- reviewed seat and surface
- timestamp

### Artifact classification
- artifact class
- canonical-subject status
- counterpart description
- byte-presence here

### Reviewed scope
- requested verb
- effective action class
- affected scope
- safer substitute offered
- chosen path (`applied`, `declined`, `rerouted`, `inspect-only`)

### Strongest safe sentence
Examples:

- `This entry was a placeholder proxy rather than a full local file.`
- `Deleting this visible row would have had broader than local scope.`
- `This conflict derivative required counterpart review before cleanup.`

### Forbidden overclaims
Examples:

- `This was just a local duplicate.`
- `Delete would only affect this device.`
- `This row was a full local copy.`
- `This hidden state was safe to remove.`

### Follow-up pointers
- better next surface if needed
- healthier counterpart to inspect
- witness still required
- last-full-copy warning if still open

## Entry points

This receipt must be reachable from:

- file list context menus
- cleanup pages
- conflict repair pages
- placeholder / selective-sync pages
- witness and recovery flows

## Success condition

A future reader should be able to tell, without re-reading several help articles or reopening the row, what kind of artifact it was and what the visible action actually meant.
