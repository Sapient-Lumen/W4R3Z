# Overlap topology review page — parent share, child share, carried edits, and blocked assumptions

## Purpose

Force the operator to review the actual graph before creating or accepting nested overlap.

This page exists to answer:

- `am I creating one narrower audience or two real subjects?`
- `can edits from the child still escape into the parent audience?`
- `which common assumptions are false here?`

## Required review claims

Must present these claims explicitly and require acceptance or rejection for each:

1. `parent and child are separate subjects, not one subject with an internal label`
2. `direct child seeding from parent-only peers is not assumed`
3. `a bridge host that carries both subjects may propagate child edits into the parent audience`
4. `the overlapping host may pay duplicate indexing / rescanning cost`
5. `placeholder / selective modes that weaken the overlap contract are not silently tolerated`

## Required sections

### 1. Proposed topology card

Must show:

- parent audience summary
- child audience summary
- bridge host count
- whether the child audience is narrower, wider, or merely different

### 2. Carried-edit consequence

Must explain with concrete examples:

- child-only peer edits child
- bridge host lands the change in child subject
- same bytes then appear within parent subject on peers that only hold the parent

Must never describe this as `leak` or `bug` by default.
It is a topology consequence and must be described as such.

### 3. Blocked assumptions list

Must at minimum block these stronger assumptions unless separately proven:

- `child audience is fully isolated from parent audience`
- `parent-only peers can seed child-only peers directly`
- `overlap costs no extra local work`
- `path containment implies authority containment`

### 4. Decision footer

Must require one of:

- `accept overlap with bridge consequences`
- `flatten into parent only`
- `detach child into non-overlapping subject`
- `cancel`
