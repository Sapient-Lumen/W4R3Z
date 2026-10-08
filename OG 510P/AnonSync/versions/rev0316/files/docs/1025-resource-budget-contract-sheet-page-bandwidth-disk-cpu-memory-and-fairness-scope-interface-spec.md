# Resource budget contract sheet page — bandwidth, disk, CPU, memory, and fairness scope

## Purpose

Show, in one durable place, the exact scarcity contract currently governing a subject, a share, or a whole runtime.

This page exists to answer:

- `which resources can constrain this work?`
- `which limits are policy, which are pressure, and which are just observations?`
- `who shares this budget?`
- `what execution order or fairness promises are actually real?`

## Required sections

### 1. Budget header

Must show:

- budget object id
- scope (`runtime-global`, `share-local`, `lane-local`, `peer-class`, `device-class`, `other`)
- active time basis (`always`, `scheduled`, `while-on-battery`, `while-on-metered`, `until-manually-cleared`, `runtime-pressure-only`)
- current state (`inactive`, `armed`, `binding`, `degraded`, `starving`, `blocked`)

### 2. Lane matrix

Must list these lanes separately at minimum:

- WAN upload
- WAN download
- LAN upload
- LAN download
- disk read/write service
- hashing / indexing CPU
- metadata / merge work
- memory footprint
- free-space floor

Each row must show:

- current ceiling or floor
- unit (`MiB/s`, `ops bias`, `threads`, `MB free`, `queue slots`, `unbounded`, `unknown`)
- owner plane (`global prefs`, `schedule`, `share override`, `power-user`, `runtime pressure`, `internal exception`)
- fairness scope (`all shares`, `this share only`, `priority class`, `selected peers`, `unknown`)

### 3. Provenance ladder

Must show precedence from strongest to weakest, for example:

1. safety stop / free-space stop
2. explicit schedule cell
3. explicit share-local priority or override
4. global default budget
5. best-effort runtime scheduling
6. observation-only hint

The operator must never have to guess which plane wins.

### 4. Fairness and preemption block

Must show separately:

- whether higher-priority items can preempt active work
- whether visible list order matches execution order
- whether suspended work keeps its place or re-enters later
- whether low-priority work can starve indefinitely
- whether queue rebuild or hidden internal exceptions can reshuffle order

### 5. Strongest safe sentence

Examples:

- `WAN download for this share is currently capped by a scheduled policy cell; LAN traffic remains uncapped.`
- `The runtime is not bandwidth-limited by policy, but disk service is currently the bottleneck.`

### 6. Blocked stronger sentence

Examples:

- `This share is fully paused and no mutations will occur.`
- `The order shown in the visible queue is the real execution order.`
- `Network bandwidth is the only resource constraining progress.`

## Minimum interactions

The page must expose actions to:

- edit budget
- view budget provenance
- inspect current bottleneck proof
- preview starvation risk
- open latest resource receipt