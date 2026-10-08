# Proxy artifact review page — entry class, counterpart, and action scope

## Purpose

Give the operator one reviewed answer to:

- what class of artifact this visible entry actually is
- whether it is the canonical subject, a proxy for it, a derivative, a witness, or service state
- what action scope attaches to the obvious verbs on this entry
- what stronger assumptions remain forbidden before action

## Inputs

- current seat identity
- current UI surface (`desktop app`, `web`, `android`, `ios`, `file browser`, `service shell`)
- selected entry path and displayed name
- extension and artifact hints (`.rsls`, `.rlsc`, `.Conflict`, hidden `.sync`, Archive path, ordinary file, ordinary folder)
- current authority posture on the subject (`read only`, `read & write`, `encrypted custody`, etc.)
- share lineage and canonical subject identifier if known
- witness inventory and byte-presence inventory
- conflict and placeholder state
- last-full-copy and retention risks if known

## Primary questions this page must answer

1. What artifact class is this row?
2. Is it the canonical subject, a proxy, a derivative, a witness, or critical service state?
3. What does `open`, `delete`, `move`, `rename`, and `remove from this device` mean here?
4. What scope would the most obvious action have?
5. What is the strongest safe sentence **before** action?

## Artifact classes

At minimum:

- `plain-local-material`
- `placeholder-proxy`
- `placeholder-subtree`
- `conflict-derivative`
- `archive-witness`
- `hidden-service-state`
- `unknown / needs deeper inspection`

## Layout

### A. Entry truth card
Top card with:

- displayed entry name
- artifact class badge
- canonical-subject status
- strongest safe sentence

Example sentences:

- `This entry is a placeholder proxy, not a full local file.`
- `This entry is a conflict derivative corresponding to a real remote file.`
- `This entry is hidden service state, not ordinary user content.`

### B. Action-scope strip
For the most likely verbs, show one line each:

- requested verb
- actual effect class
- affected scope
- safer alternative if one exists

Effect classes:

- `inspect only`
- `local eviction`
- `local rename only`
- `all-peer delete`
- `remote-counterpart delete risk`
- `service-state damage risk`

### C. Counterpart summary pane
Show:

- canonical subject identifier if known
- where real bytes currently live
- whether this entry stands in for another object
- whether the action touches witness stores or only live material

### D. Forbidden assumption pane
Examples:

- `Deleting this will only clean up this device`
- `This row is a harmless duplicate`
- `This is a full local file`
- `This hidden folder is disposable clutter`

## Required interactions

- `Review counterpart map`
- `Choose safer action`
- `Keep narrow claim`
- `Continue to action substitution`
- `Export artifact truth receipt`

## Guardrails

- Never let filename appearance imply local-only scope.
- Never let `.Conflict` display as harmless clutter.
- Never let `.rsls` display as a full local copy.
- Never let hidden `.sync` display as ordinary user content.
- Never let `delete` proceed without showing effective scope when the class is not `plain-local-material`.

## Output

A reviewed artifact-class and action-scope classification that downstream delete, cleanup, restore, or handoff surfaces must inherit without reinterpretation.
