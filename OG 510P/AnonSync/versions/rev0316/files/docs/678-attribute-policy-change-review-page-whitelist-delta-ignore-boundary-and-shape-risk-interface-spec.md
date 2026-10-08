# Attribute-policy change review page — whitelist delta, ignore boundary, and shape risk interface spec

## Purpose

When metadata-carriage policy changes, the product must review more than a toggle.
It must review meaning.

## Core decision

Every non-trivial metadata-policy change should open an **Attribute-policy change review** page before apply.

The review must publish:

- the channel delta
- the policy basis delta
- ignore-boundary truth
- seat-class change
- object-shape risk

## Fixed review order

1. **Change being proposed**
2. **Affected channels and seats**
3. **Boundary with ordinary exclusion policy**
4. **Visible object-shape consequences**
5. **Commit sentence and receipt preview**

### 1) Change being proposed

Render the exact change as a before/after set:

- channels added
- channels removed
- channels moved from required to optional
- channels moved from visible policy to imported-legacy or vice versa

### 2) Affected channels and seats

Show which seats would move between:

- native preserver
- courier-only relay
- reduced-fidelity holder
- blocked

### 3) Boundary with ordinary exclusion policy

The review must say plainly whether the proposed change:

- is unrelated to ordinary file exclusion rules
- narrows only the attribute plane
- also changes payload visibility
- would leave Ignore-style expectations unchanged

This section exists so the operator never confuses `do not sync this file` with `sync the file but weaken its meaning plane`.

### 4) Visible object-shape consequences

Examples:

- `bundle may appear as ordinary directory`
- `tags may relay onward but not render locally`
- `metadata may persist only as courier residue on seats A/C`
- `local edits on seat B may not round-trip full meaning`

### 5) Commit sentence and receipt preview

Before apply, the product must preview the strongest safe post-apply sentence.
Examples:

- `After apply, this subject will remain fully preserved on all required seats.`
- `After apply, seats B and C will carry required metadata only as courier relays.`
- `After apply, this subject will be present on seat D under reduced meaning fidelity.`
