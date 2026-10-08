# Invocation profile contract sheet page — launch intent, world lineage, visibility, and control exposure

## Purpose

Show, in one durable place before or immediately after launch, the exact truths an operator may rely on about the runtime they are opening.

This page exists to answer:

- `what launch intent is being applied?`
- `which state world will this invocation use?`
- `how visible or hidden will the runtime be?`
- `what control exposure follows?`
- `what stronger continuity or safety sentence is blocked?`

## Required sections

### 1. Invocation header

Must show:

- invocation profile id
- invocation family (`desktop-visible`, `desktop-minimized`, `silent-background`, `service`, `headless`, `maintenance`, `recovery`, `other`)
- requested intent (`same-world reopen`, `new world`, `inspect only`, `service promotion`, `config-owned boot`, `other`)
- current verdict (`same-world`, `guarded`, `fork`, `blocked`, `unknown`)

### 2. World lineage block

Must show separate rows for:

- chosen state root
- identity lineage
- config authority class
- expected share / subject roster basis
- overlap or collision risk

Each row must publish:

- current value
- provenance
- confidence class
- whether it is safe to treat as same-world continuity

### 3. Visibility block

Must distinguish at least:

- foreground visible
- minimized but locally reachable
- hidden background runtime
- service runtime with external control channel
- headless runtime with local or remote workbench only
- inspect-only / no live mutation surface

This block must answer:

> what will the operator see, and what absence is merely projection absence rather than process absence?

### 4. Control exposure block

Must show:

- listener posture (`loopback-only`, `selected-interface`, `all-interfaces`, `none`, `unknown`)
- reachability scope (`local-seat-only`, `same-host`, `LAN-reviewed`, `broader-reviewed`, `unknown`)
- auth floor
- transport posture
- whether exposure came from standing policy, launch override, or ambient default

### 5. State-root authority block

Must show:

- explicit state-root path or authority handle
- whether the root is default, launch-overridden, config-owned, service-owned, or adopted from an earlier receipt
- whether launch would create a new root if absent
- whether launch is safe only because the root already exists and matches a prior world

### 6. Strongest safe sentence

Examples:

- `This launch reopens the same reviewed state world but with a quieter projection.`
- `This launch will open a sibling runtime because it points at a different state root.`
- `This launch keeps control loopback-only; it does not expose reviewed LAN control.`
- `This launch is blocked because the target root would collide with an existing runtime world.`

### 7. Blocked stronger sentence

Examples:

- `Hidden start means Sync is not really running.`
- `Using a different storage path is just a cosmetic convenience.`
- `Opening browser control means the endpoint is safely reachable from elsewhere.`
- `Foreground absence proves stop.`

## Interaction rules

- any invocation that is not obviously same-world must link to a dedicated review
- hidden or minimized starts must still keep stop-proof and exposure links visible
- world-lineage rows must remain exportable in text and CLI/TUI surfaces
- the page must not bury state-root authority or exposure behind advanced disclosure

## Receipt obligations

Any receipt derived from this page must preserve:

- reviewed invocation family
- requested intent
- world-lineage verdict
- visibility posture
- control-exposure posture
- strongest safe sentence
- blocked stronger sentence
