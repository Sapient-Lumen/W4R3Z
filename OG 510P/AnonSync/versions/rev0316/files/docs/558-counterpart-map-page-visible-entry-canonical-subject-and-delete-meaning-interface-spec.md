# Counterpart map page — visible entry, canonical subject, and delete meaning

## Purpose

When a visible entry stands for something else, this page makes the relationship explicit before the operator acts.

## When this page appears

Show this page when the reviewed artifact class is any of:

- `placeholder-proxy`
- `placeholder-subtree`
- `conflict-derivative`
- `archive-witness`
- `hidden-service-state`
- `unknown / needs deeper inspection`

## Questions this page must answer

1. What is the visible entry?
2. What canonical subject or witness class does it point to?
3. Where do the real bytes or affected copies actually live?
4. What scope does delete or move have from this page?
5. Which safer alternatives preserve operator intent with less collateral effect?

## Layout

### A. Two-column identity frame
Left column: **visible entry**

- name shown to operator
- path / surface
- artifact class
- byte-presence here

Right column: **canonical subject / counterpart**

- subject id or counterpart description
- current host class or peer scope
- witness / live role
- authority gate

### B. Effect-topology rail
A compact graph with nodes such as:

- `this row`
- `local bytes here`
- `other peer bytes`
- `remote real counterpart`
- `Archive witness`
- `service-state only`

Edges are labeled by action effect:

- `delete here only`
- `revert to placeholder`
- `delete across peers`
- `risk deleting remote counterpart`
- `inspect only`
- `unsafe to mutate`

### C. Delete-meaning comparison
For the current entry, compare:

- **what the operator probably means**
- **what the product would actually do**
- **best lower-risk substitute**

Examples:

- `I only want to free local space` → `use local eviction / revert to placeholder`
- `I want this confusing .Conflict row gone` → `review healthy counterpart first; plain delete is unsafe`
- `I want to inspect old versions` → `open witness, do not treat this as live delete`

### D. Affected-copy inventory
List the likely affected classes:

- local copy here
- placeholder only here
- peer copies elsewhere
- remote conflict counterpart
- witness / Archive copies
- service-state continuity

## Actions

- `Choose local-only alternative`
- `Open healthier counterpart`
- `Open witness instead`
- `Proceed to action substitution`
- `Export counterpart map`

## Guardrails

- Never let one visible row imply one affected object.
- Never let the page hide affected remote scope behind a generic `delete` button.
- Never let `counterpart unknown` silently collapse into `safe local cleanup`.
- Never let service-state mutation sit next to user-content actions without a class boundary.

## Result

A typed map of what the visible entry actually stands for and what action on it would mean across local, remote, and witness planes.
