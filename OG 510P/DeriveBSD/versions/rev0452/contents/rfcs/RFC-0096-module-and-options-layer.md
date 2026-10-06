# RFC-0096: Module + options layer

## Summary
Provide a NixOS-like composition layer (modules + discoverable options) that compiles to canonical Spec JSON.

## Motivation
Configuration must compose and remain explorable:
- “what can I set?”
- “where is this value set?”
- “why did this win?”

## Proposal
- module fragments merge deterministically
- an options registry is generated from schemas
- CLI exposes `derive options`, `derive config show`, `derive config trace`

See: `docs/161-module-and-options-layer.md`.
