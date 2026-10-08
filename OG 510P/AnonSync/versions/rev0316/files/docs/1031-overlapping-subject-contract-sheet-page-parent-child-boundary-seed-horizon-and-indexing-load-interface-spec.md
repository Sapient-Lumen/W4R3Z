# Overlapping subject contract sheet page — parent-child boundary, seed horizon, and indexing load

## Purpose

Show, in one durable place, the actual contract created when one sync subject lives inside the path of another.

This page exists to answer:

- `how many sync subjects exist here?`
- `which paths overlap and which subject owns each scope?`
- `who can seed whom directly?`
- `which host is bridging the overlap?`
- `what extra indexing / rescanning cost is created?`

## Required sections

### 1. Overlap header

Must show:

- overlap object id
- parent subject id
- child subject id
- overlap path boundary
- current posture (`proposed`, `active`, `blocked`, `degraded`, `retired`)

### 2. Subject boundary map

Must show separately:

- parent root path
- child root path
- whether child is fully contained inside parent
- whether any sibling overlaps also exist
- whether either subject is currently placeholder / selective / partial-only

### 3. Membership and seed-horizon matrix

Must list at minimum these peer classes:

- peers with parent only
- peers with child only
- peers with both parent and child
- peers with neither subject but visible metadata only

For each class show:

- direct seeding allowed? (`yes`, `no`, `only-via-bridge`, `unknown`)
- may receive carried edits from the other subject through a bridge? (`yes`, `no`, `conditional`)
- proof basis

### 4. Bridge-host section

Must show:

- which host or hosts currently belong to both subjects
- whether bridge carriage is required for propagation across the audience split
- whether losing the bridge would strand any flow
- whether bridge state is currently healthy enough to support the claimed path

### 5. Workload section

Must show:

- duplicate indexing risk
- duplicate rescan risk
- extra hashing / metadata work risk
- whether overlap is blocked because the cost exceeds current budget

### 6. Safety language

Must show:

- strongest safe sentence
- blocked stronger sentence
- invalidators
