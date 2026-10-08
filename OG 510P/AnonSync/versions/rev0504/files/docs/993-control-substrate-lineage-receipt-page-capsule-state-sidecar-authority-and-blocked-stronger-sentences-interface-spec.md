# Control substrate lineage receipt page — capsule state, sidecar authority, and blocked stronger sentences

## Purpose

Emit a durable artifact after subject creation, rebind, repair, export, cleanup, or collision resolution so later operators do not need hidden-file folklore to understand what happened.

## Required receipt fields

### Subject identity

- subject name
- canonical subject identifier
- local path at time of receipt
- emitting runtime / seat

### Control substrate summary

- capsule state: `healthy`, `repaired`, `regenerated`, `forked`, `omitted`, `unknown`
- capsule owner / authority class
- dual-ownership evidence state

### Sidecar roster

For each relevant sidecar family preserve:

- family name
- authority class
- editability class
- activation class
- retroactivity class
- included / excluded / preserved / regenerated verdict

### Residue summary

- temporary transfer residue present or not
- metadata stub residue present or not
- archive/salvage relation if relevant

### Claim section

- strongest safe sentence
- blocked stronger sentence
- invalidators / reopen triggers

## Rendering rules

- the receipt must be human-readable before machine-readable detail.
- blocked stronger sentence must be rendered near the main claim, not buried in metadata.
- if continuity broke, the receipt must say `successor created` or `lineage forked`, not merely `updated`.

## Example claim shapes

- `Control capsule preserved; editable ignore policy carried forward unchanged; no dual-owner evidence at receipt time.`
- `Control capsule regenerated; prior continuity does not survive; archived salvage exported before apply.`
- `Bytes imported without prior capsule; new subject lineage begins here.`
