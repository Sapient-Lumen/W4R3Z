# 0002 — Provider strategy

## Why this exists

The product goal is a sealed bundled application that internally supervises the anonymity runtimes it needs.

## Current provider split

### I2P provider
Canonical path:
- bundled `i2pd`
- internal config generation
- SAM bridge boundary for the Rust side
- no user-exposed router management

### Tor provider
Canonical path:
- bundled stable tor daemon
- internal config generation
- provider trait around daemon lifecycle and reachability
- no user-exposed daemon management

Future path:
- evaluate Arti migration without destabilizing the sync core

## Why this is useful

- preserves a one-product UX promise
- keeps implementation realistic without forcing premature single-process embedding
- allows later runtime swaps while keeping application logic stable
- enforces user-hidden transport complexity
