# Service world preview page — storage root, empty-state attribution, and observation grade

## Purpose

Preview the actual world the service seat is about to open so that `browser opened` or `service started` cannot impersonate continuity.

This page exists to answer:

- `which storage root will govern the service seat?`
- `what roster should appear if continuity is real?`
- `if the service opens empty, what is the most honest attribution?`
- `what observation grade will the service seat have after cutover?`
- `what exposure posture will the control surface adopt?`

## Required sections

### 1. Service world header

Must show:

- service world preview id
- target principal
- target storage root
- config authority class (`interactive-only`, `service-storage`, `config-owned`, `unknown`)
- expected roster class (`carried-forward`, `clean-empty`, `different-world-empty`, `partial`, `unknown`)

### 2. Storage root provenance

Must show:

- path or authority handle for the service storage root
- why this root was selected
- whether it already contains known state
- whether config mode will read from this root
- whether a new world will be created if the root is absent

### 3. Empty-state attribution ladder

Must distinguish at least:

- `clean branch by operator choice`
- `different principal / different storage world`
- `migration requested but not yet proved`
- `roster partially carried forward`
- `unexpected absence; inspect before reconnect`

This section must answer:

> if the service seat looks empty, what is the most honest reason right now?

### 4. Observation-grade preview

Must show:

- mapped-drive availability (`available`, `not available to service`, `not applicable`, `unknown`)
- notification grade (`native`, `degraded`, `rescan-only`, `restart-dependent`, `unknown`)
- rescan cadence or dependence
- subject classes most affected by downgraded detection

### 5. Control-surface preview

Must show:

- whether WebUI is loopback-only by default
- whether service restart is required for exposure change
- whether config or interactive setting currently wins
- audience grade after cutover

### 6. Follow-up obligations

Must show explicit post-cutover lanes such as:

- `no follow-up needed`
- `prove migrated roster`
- `review reconnect for affected subjects`
- `review listener widening separately`
- `inspect unexpected empty state before any reconnect`

## Required actions

- `Open principal switch review`
- `Approve service world and continue`
- `Abort and keep current runtime`
- `Export preview evidence`

## Guardrails

- Never let empty state inherit the label `no folders` without attribution.
- Never hide observation downgrade inside generic troubleshooting copy.
- Never treat service-storage selection as implementation trivia.
- Never let exposure widening piggyback silently on service cutover.

## Output

A preview page that names the actual storage world, expected roster, observation grade, and exposure posture before a service seat becomes the operator's assumed reality.
