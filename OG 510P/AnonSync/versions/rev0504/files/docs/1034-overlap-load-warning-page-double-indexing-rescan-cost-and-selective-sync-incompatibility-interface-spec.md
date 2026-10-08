# Overlap load warning page — double indexing, rescan cost, and selective-sync incompatibility

## Purpose

Warn clearly when nested overlap adds local work or relies on posture combinations that the system refuses to support.

This page exists to answer:

- `what extra work will this overlap create on the bridge host?`
- `what settings or modes make the overlap contract invalid or unsafe?`

## Required warning sections

### 1. Cost summary

Must show:

- expected duplicate indexing cost
- expected duplicate rescan cost
- expected duplicate metadata / hashing churn
- which host or hosts pay the cost

### 2. Incompatibility summary

Must show explicitly whether overlap is blocked by:

- placeholder / selective posture
- insufficient authority class
- unresolved path collision
- missing bridge proof
- resource budget floor

### 3. Blast-radius summary

Must show:

- whether carried edits can enlarge the effective audience of child changes
- whether any peers will observe indirect propagation they cannot directly seed back

### 4. Operator actions

Must provide only topology-safe choices:

- keep overlap and accept cost
- convert to single parent subject
- detach child to non-overlapping root
- postpone until resource budget or mode changes

## Copy rule

Never reduce this page to a small inline tooltip.
If duplicate work or topology surprise is real, this warning must own a full review surface.
