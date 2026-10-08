# Runtime stop receipt page: stop class, drain verdict, proof ceiling, and restart posture interface spec

## Purpose

After any meaningful stop, pause-to-stop transition, or revive-disabled shutdown, the operator needs a durable receipt that answers later:

> what exactly did we stop, what drain verdict was reached, what proof ceiling did we actually earn, and what restart posture still survived afterward?

## Receipt structure

### Header

Show:

- receipt id
- emitted time
- subject / scope
- action family (`projection-closed`, `runtime-stop-requested`, `runtime-stopped`, `service-retired`, `revive-disabled-stop`, `stop-blocked`)

### Stop summary

Render:

- targeted projection class
- targeted runtime class
- final runtime verdict
- drain verdict
- restart posture after action

### Before / after section

Show:

- prior projection state
- new projection state
- prior runtime state
- new runtime state
- prior restart posture
- new restart posture

### Proof and claim section

Show:

- strongest safe sentence after action
- stronger rejected sentence after action
- witness basis for stop proof
- witness basis for drain proof
- proof freshness window

### Risk and chronology section

Show:

- remaining revival mechanisms
- chronology / reopen risk note
- proof invalidators
- blocked stronger promises

### Follow-on section

Show:

- next proof refresh point
- related restart provenance page
- superseding receipts, if later emitted

## Rules

### Rule 1 — receipt preserves runtime meaning, not just a button press

The receipt must capture what was targeted and what was actually proven.

### Rule 2 — drain verdict survives later

A `stop requested` receipt and a `quiet boundary proven` receipt are not the same artifact.

### Rule 3 — surviving revival posture stays visible

If boot, service, or background revival still exists, the receipt must say so.

### Rule 4 — stronger rejected sentence remains durable

The product must preserve what it still refused to promise.

## Acceptance criteria

A later operator can:

- tell what stop class occurred
- tell whether drain finished
- tell what proof ceiling was earned
- tell what revival posture survived
- tell what stronger claim remained forbidden
