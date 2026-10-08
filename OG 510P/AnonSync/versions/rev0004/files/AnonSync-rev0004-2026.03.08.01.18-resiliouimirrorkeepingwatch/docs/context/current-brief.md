# Current Brief

## What this repo is

A continuity-first design archive for AnonSync: a future Rust-first sync tool designed around bundled Tor and bundled I2P via `i2pd`, with a user experience intentionally close to Resilio Sync.

## What is settled right now

- the repo is archive-first and continuity-oriented
- the sync core should remain transport-agnostic
- the product posture is fully bundled and noob-safe
- I2P is bundled through `i2pd` and reached through a SAM seam
- Tor starts as a bundled stable tor daemon, with Arti deferred
- invite-only sharing is canonical
- LAN discovery is on by default, but beacons must represent invite-derived rotating tokens, not stable share IDs
- permissions and placeholder ergonomics should closely follow Resilio's model
- file notifications accelerate sync, but durable index + periodic rescan preserve correctness
- mobile is first-class, Tor-default, and I2P opt-in
- encrypted sink mode should come before a fuller untrusted live-peer mode
- performance is now treated as named resource profiles plus measured adaptation
- current performance defaults assume direct small-file send with hard RAM caps, local SQLite WAL state, and BLAKE3 as the default hash family
- UI is a first-class workstream, with a shared local-web surface across desktop and mobile as the current posture
- the archive now treats Resilio UI and change tracking as a recurring research practice, not a one-time analogy

## What is not settled

- the exact invite object format
- the exact beacon token format and rotation schedule
- exact profile auto-selection rules
- sync protocol wire details
- key hierarchy and recovery model
- conflict-resolution semantics
- license

## Next priorities

1. draft the shared UI information architecture and first screen flows
2. write the invite/capability schema and examples
3. define LAN discovery beacon token semantics and privacy budget
4. benchmark the profile and discovery skeletons
5. specify supervised child-process orchestration for tor + `i2pd`
6. define index, placeholder, and periodic-rescan semantics
