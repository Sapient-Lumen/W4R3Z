# Project Charter

## Working thesis

Build a peer-to-peer file synchronization system with a user experience close to Resilio Sync, but architected around anonymous or pseudonymous network transports from the start, especially bundled Tor and bundled I2P via `i2pd`.

## Core goals

- Cross-platform Rust-first implementation.
- Public-facing one-product / one-bundle experience.
- Private-by-default synchronization between peers.
- Strong separation between sync logic and transport logic.
- A repository that can survive hundreds of iterative archive revisions.
- Noob-safe abstraction of Tor and I2P details.
- High throughput when hardware permits, without pretending RAM is free.

## Non-goals for early revisions

- Requiring users to install or manage external anonymity routers.
- Depending on Java I2P.
- Shipping a production-ready GUI before core protocol clarity.
- Committing to a permanent wire format before threat model review.
- Claiming metadata privacy beyond what the design actually provides.
- Claiming magical auto-tuning without a benchmarked control loop.

## Early architectural principle

The project should evolve in layers:

1. sync model
2. identity and capability model
3. transport provider interfaces
4. runtime orchestration
5. packaging and UX
6. measured profile adaptation

## Baseline threat assumptions

- Untrusted networks
- Honest-but-curious observers
- Unreliable connectivity
- Partial peer availability
- Long-lived repos with many editors and imperfect memory
- Noob users who should not be exposed to transport internals

## Questions still intentionally open

- Exact folder capability encoding
- Exact LAN beacon token wire format
- Exact piece size and scheduler weights
- Conflict resolution semantics
- Metadata leakage budget
- Tor-to-Arti migration conditions
- Licensing choice

## Success condition for this revision

A future editor can enter cold, understand the repo, validate it, and continue work without relying on transient chat memory, while also seeing which product defaults and performance defaults are already fixed.
