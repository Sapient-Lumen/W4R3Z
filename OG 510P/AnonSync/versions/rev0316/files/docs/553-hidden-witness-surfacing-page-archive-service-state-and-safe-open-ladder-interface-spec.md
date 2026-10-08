# Hidden witness surfacing page — Archive, service-state, and safe open ladder

## Purpose

When evidence exists but is not yet directly visible, this page gives the operator a safe ladder for surfacing it without pretending that all hidden state is safe to poke blindly.

## When this page appears

Show this page when any witness class is marked:

- `hidden-but-openable-here`
- `reachable-only-via-file-browser`
- `service-state-present`
- `residual-after-uninstall`
- `critical-hidden-state`

## Ladder structure

### 1. Witness target
The page names the target exactly:

- Archive in hidden `.sync/Archive`
- service-state in `.sync`
- hidden residual share folder after uninstall
- hidden log / support residue
- export already created but off-surface

### 2. Safe open method
For each target, show the least-destructive open path first.

Examples:

- `Desktop app → Open Archive`
- `File browser → reveal hidden items → open .sync/Archive`
- `Switch to desktop/file browser; current Web surface cannot inspect directly`
- `Do not move or delete .sync while inspecting`

### 3. Destructive-risk banner
If the target includes critical service material, the page must say:

- opening is safe
- moving is unsafe
- deleting changes product state
- some surfaces can inspect but not administer safely

### 4. Inspection intent
Ask the operator to choose one:

- verify existence only
- inspect candidate versions
- export proof bundle
- prepare restore handoff
- confirm residue before cleanup

## Evidence list pane

For Archive candidates, show:

- seat
- folder / subject
- visibility method
- latest indexed candidate count if known
- whether authorship is still missing and needs History

For `.sync` service-state, show:

- criticality class
- hidden-path location
- whether touching it can break sync
- safest read-only inspection method

## Required warnings

- `Archive available` is not the same as `Archive accessible from this surface`.
- `Hidden` is not the same as `safe to remove`.
- `Inspect` is not the same as `restore`.
- `Residual after uninstall` is not the same as `program still installed`.

## Completion states

- surfaced successfully
- routed to better surface
- operator declined surfacing
- blocked by platform or permissions
- blocked because surfacing would be too destructive without escalation

## Receipt link

On completion, always generate or update an evidence-access receipt summarizing what became visible and what stayed off-surface.
