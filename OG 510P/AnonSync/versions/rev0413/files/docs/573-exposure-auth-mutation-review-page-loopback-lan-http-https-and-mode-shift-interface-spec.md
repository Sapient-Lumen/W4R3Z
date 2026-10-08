# Exposure/auth mutation review page — loopback, LAN, HTTP, HTTPS, and mode-shift interface spec

## Purpose

Review any change that alters the grade of the control surface, including:

- loopback-only to LAN reach
- LAN to loopback narrowing
- passwordless to passworded control
- password rotation with different collateral classes
- HTTP to HTTPS
- self-signed to trusted certificate
- live WebUI to config-owned / disabled WebUI
- config-file takeover that changes how control is administered

This page exists so a control-grade mutation cannot hide inside a generic `settings` action.

## Inputs

- current control grade object
- requested changes
- runtime profile and restart requirements
- credential source after change
- session impact forecast
- certificate source after change
- browser-residue forecast
- modality / feature parity deltas

## Primary questions this page must answer

1. What exact grade change is being requested?
2. Who gains or loses reach because of it?
3. What stronger claims become earned, and which still do not?
4. What session, browser, or runtime consequences follow?
5. Does this mutation preserve the same live control surface or substitute a new mode?

## Layout

### A. Current vs requested grade compare

Two-column compare showing:

- audience
- auth floor
- transport posture
- certificate class
- control modality
- fallback route

### B. Consequence forecast

Fields:

- audience delta (`narrowed`, `widened`, `unchanged`, `ambiguous`)
- trust delta (`weaker`, `stronger`, `mixed`, `unchanged`)
- session effect (`reauth`, `session-revoked`, `browser-warning-likely`, `none`, `unknown`)
- restart / reload need
- intake parity effect

### C. Safe-language ladder

Three explicit lines:

- requested operator phrase
- strongest approved phrase after apply
- stronger forbidden phrase and why

Example:

- requested: `make it securely reachable from the network`
- approved: `make it LAN-reachable over HTTPS with self-signed certificate warning`
- forbidden: `publish trusted secure remote administration` because trusted certificate distribution is still absent

### D. Mode-shift warning card

Render only when the mutation changes modality.

Examples:

- `config-owned shared folders disable live WebUI`
- `credential reset through storage-file deletion resets broader preferences`
- `trusted certificate path requires config-owned material`

### E. Apply gate

Apply button stays gated until the page can state:

- resulting control grade
- resulting fallback route
- collateral class of the chosen recovery path

## Required interactions

- `Use lower-collateral credential path`
- `Stay loopback only`
- `Proceed with LAN exposure`
- `Move to trusted certificate path`
- `Export pre/post compare`

## Guardrails

- Never let `enable HTTPS` imply trusted certificate by default.
- Never let `set password` imply safe remote reach by itself.
- Never let a config-owned mode shift look like a harmless credential edit.
- Never hide browser-residue cleanup behind endpoint-level transport language.

## Output

A reviewed mutation plan that states the resulting control grade, the exact collateral class, and the strongest sentence earned afterward.
