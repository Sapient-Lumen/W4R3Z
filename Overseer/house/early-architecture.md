# Architecture

## Status

Initial working shape. This is the system we are currently aiming toward, not a locked final design.

## High-level shape

The real Overseer should start as a host-native system with:

- one long-running main Overseer service
- durable local state and session artifacts
- a small file-based operator control surface
- readable outbox and recovery summaries
- a bounded context-pack surface for cold re-entry
- a bounded set of helper units only when they actually simplify recovery or capability separation

## Initial target topology

### 1. Main service

Provisional name: `overseer-main.service`

Responsibilities:

- maintain the long-running loop
- read current operator guidance
- keep session continuity records
- write summaries and status artifacts
- surface its current phase to the host

### 2. Control surface

The operator needs simple, durable inputs:

- current brief
- hold or pause signal
- stop signal
- priority or interruption note

These should be readable and writable without entering a raw internal state directory.

### 2.5. Credential surface

The system should treat `/home/overseer/authcreds/` as an operator-managed credential bundle for the Overseer.
Those files are authorized inputs, not accidental secret spillage.
The architecture should assume they may be rotated or replaced over time and should make that update path straightforward.

### 3. Outbox surface

The Overseer should always leave a readable current summary, plus timestamped summaries for historical continuity.

### 4. Recovery surface

The host should expose enough state to answer:

- Is the Overseer running?
- What was it doing?
- What session or turn was current?
- What failed most recently?
- What should the operator do next?
- Is the machine still online enough to research, download, and recover?

### 5. Session archive

The system should preserve:

- live session records
- condensed history
- recovery summaries
- important operator dialogue outcomes

This must survive ordinary restarts and should not depend on a single hidden vendor-specific state path.

## Likely implementation bias

Near-term bias:

- file-backed canonical artifacts
- `systemd` for lifecycle and visibility
- NixOS configuration for declared directories, units, and wiring
- local append-only logs or JSONL where sequence matters
- markdown summaries where humans need to read quickly
- structured JSON registries where cheap re-entry matters
- direct installation of required tooling when implementation work needs it
- practical internet access preserved as a first-class dependency

## Open shape questions

- whether the main Overseer should run as `overseer`, `root`, or a split profile by default
- where the canonical runtime and durable state roots should live
- how much raw dialogue should be retained versus summarized
- which host operations deserve dedicated gateways versus direct execution
- whether helper agents are useful early or should wait until the main loop is stable
