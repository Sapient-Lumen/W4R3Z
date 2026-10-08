# Path liveness lineage receipt page: loss cause, root return, rebind result, and blocked-stronger-sentences interface spec

## Purpose

This receipt preserves exactly what the product knew when a subject path disappeared, returned, or was rebound.
It exists so later operators do not have to reverse-engineer whether the product treated the event as deletion, move, remount, or fresh adoption.

## Mandatory receipt fields

### Identity and timing

- receipt id
- subject ref
- seat ref
- created-at
- operator / automation actor

### Before state

- prior bound path
- prior root witness summary
- prior continuity class

### Event classification

- event class (`missing-path`, `same-root-move`, `cross-root-rehome`, `returned-removable-root`, `fresh-bind`, `unknown`)
- loss-cause hypothesis and confidence
- whether trash / recycle recovery was available

### Review outcome

- reviewed candidate path
- candidate root witness summary
- witness comparison verdict
- proof rung achieved
- reconnect-cost class
- committed action (`restore`, `retarget`, `reviewed-rebind`, `fresh-bind`, `remove-readd`, `defer`)

### Safe language

- strongest safe sentence
- blocked stronger sentence

## Example blocked stronger sentences

- `This path was definitely the same subject.`
- `Nothing continuity-bearing was lost.`
- `Resume cost was zero.`
- `External return was harmless.`

## Rendering rule

The receipt must show the blocked stronger sentence directly next to the committed action so later readers know what the product explicitly refused to overclaim.
