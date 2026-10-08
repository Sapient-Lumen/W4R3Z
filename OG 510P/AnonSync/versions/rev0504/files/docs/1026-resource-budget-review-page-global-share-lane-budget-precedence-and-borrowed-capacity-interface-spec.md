# Resource budget review page — global, share, lane, precedence, and borrowed capacity

## Purpose

Review a pending budget change before it takes effect.

This page exists to answer:

- `what exactly am I throttling or prioritizing?`
- `what other planes already constrain this work?`
- `what capacity am I borrowing from lower-priority or background work?`
- `what stronger reading should I stop believing after apply?`

## Inputs the page must accept

- target scope (`runtime`, `share`, `peer class`, `lane`, `battery/metred context`, `schedule cell`)
- budget type (`hard cap`, `soft preference`, `priority boost`, `low-priority bias`, `free-space stop`, `queue limit`, `other`)
- candidate value
- activation basis (`immediate`, `scheduled`, `contextual`, `next restart`, `future-only`)

## Required review sections

### 1. Proposed delta

Must show old value, new value, effective units, and affected lanes separately.

### 2. Precedence preview

Must show:

- stronger planes already present
- weaker planes that will become shadowed
- whether the new rule overrides or merely biases scheduling
- whether the rule applies to WAN only, LAN only, or both

### 3. Borrowed-capacity explanation

Must state explicitly which work may slow down because this change wins resources, such as:

- low-priority downloads
- background hydration
- indexing/merge work
- LAN peers when local-peer limiting is enabled
- disk service for other shares when low-priority bias is removed

### 4. Contention counterfactuals

Must answer at least these:

- `if I do nothing, what remains the bottleneck?`
- `if I apply this, which bottleneck is likely to dominate next?`
- `does this create starvation risk or just reduce average throughput?`

### 5. Strongest safe sentence

Example:

- `This change caps WAN upload for all shares during the selected schedule window and may delay lower-priority downloads indirectly through reduced peer reciprocity.`

### 6. Blocked stronger sentence

Examples:

- `This makes the runtime quiet.`
- `This only affects the share currently on screen.`
- `This guarantees the selected files finish first with no queue exceptions.`

## Minimum interactions

The page must expose actions to:

- apply change
- stage change without applying
- inspect affected lanes
- open starvation warning
- export planned budget receipt