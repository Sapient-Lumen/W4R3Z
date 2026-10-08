# Sibling runtime roster page — same-host namespaces, storage lineage, and subject overlap interface spec

## Purpose

Show all known or plausible runtime namespaces on one host so the operator can stop reasoning from memory.
This page answers:

- how many runtimes this host currently has or recently had
- which storage roots and principals define them
- which subjects each runtime owns or has touched
- where overlap, ambiguity, or empty-state surprise exists

## Inputs

- host identifier
- observed namespace rows
- for each row: runtime label, principal, storage root, control endpoint, ports, config path, first-seen / last-seen, share count, identity label if known
- subject overlap map
- namespace-confidence flags
- recommended consolidation / separation actions

## Primary questions this page must answer

1. What runtime namespaces exist on this host?
2. Which ones are clearly separate versus probably the same?
3. Which subjects are owned by which namespace?
4. Where is overlap dangerous or already present?
5. Which namespace should the operator treat as authoritative for the next task?

## Layout

### A. Host roster verdict strip

Fields:

- host label
- namespace count
- highest-risk overlap verdict
- authoritative namespace recommendation if one exists
- strongest safe sentence

Example verdicts:

- `One known namespace; no sibling runtime evidence`
- `Two sibling runtimes; separate storage roots, no subject overlap yet`
- `Overlap risk present; one local subject is claimed by more than one runtime lane`
- `Roster incomplete; control surfaces discovered but storage lineage still uncertain`

### B. Namespace roster table

Columns:

- namespace label
- principal / service account
- storage root
- control endpoint
- share / subject count
- lineage status
- last observed
- next safest action

Rows should be sortable by:

- current activity
- collision risk
- storage-root similarity
- control-endpoint similarity

### C. Subject overlap card

For each high-risk subject show:

- local path / subject identifier
- namespace already associated
- namespace now attempting admission
- overlap class (`none`, `same-subject-reopen`, `duplicate-id-block`, `hidden-spine-collision-risk`, `unknown`)
- safe next step

### D. Namespace comparison card

Side-by-side compare for two selected namespaces:

- storage roots
- principals
- config roots
- ports/endpoints
- share roster similarity
- log lineage similarity
- known continuity evidence

### E. Consolidation / separation guidance

Show three lanes:

- `treat as same namespace`
- `keep as deliberate sibling runtime`
- `block until overlap reviewed`

## Required interactions

- `Set authoritative namespace for this task`
- `Open instance namespace review`
- `Review overlap admission for selected subject`
- `Export namespace roster receipt`

## Guardrails

- Never collapse two runtimes just because they share a host name.
- Never hide storage-root differences in a collapsed row.
- Never list a subject under multiple runtimes without an explicit overlap verdict.
- Never let an empty roster silently read as `nothing here` when another sibling namespace exists.

## Output

A durable same-host roster that keeps runtime namespaces, their state loci, and their overlap risks visible enough that later actions no longer depend on folklore.
