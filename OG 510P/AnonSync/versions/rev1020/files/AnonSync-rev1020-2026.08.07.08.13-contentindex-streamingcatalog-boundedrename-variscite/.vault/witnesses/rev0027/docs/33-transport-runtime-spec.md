# Bundled transport runtime and session spec

This document makes the privacy-transport story concrete enough to guide implementation and interface design.

## Why this document exists

The archive already decided that:

- Tor and I2P are first-class
- clearnet WAN direct exists only as a manual speed option
- Linux is the primary environment

That still left an ambiguity:

> what exactly ships, starts, warms, stays alive, and explains itself when privacy routing is part of the product rather than bolted on?

This document answers that.

## Core contract

### 1) One delivered package per target, no runtime scavenger hunt

For a supported target, AnonSync should ship as one delivered package/artifact that already contains the transport pieces it intends to use.

The operator should not need to:

- install Tor separately
- install I2P separately
- reverse-engineer proxy environment variables
- guess which background helper is required for privacy-routed operation

That does **not** mean every engine must run the same way internally.

### 2) Tor and I2P may have different integration styles

The best current shape of the archive is:

- **Tor / Arti**: prefer an in-process Rust-native integration when feasible
- **I2P**: prefer a bundled helper/router runtime that the daemon manages explicitly, exposing a stable control boundary such as SAM

That yields one operator story while respecting that the transport technologies are not the same.

### 3) Engine, runtime, session, route, and override are separate objects

AnonSync should keep these distinct:

- **engine** — abstract transport class like `tor`, `i2p`, `clearnet`
- **runtime** — the concrete available implementation and its lifecycle state
- **session** — a live reusable communication context bound to some scope
- **route** — the path actually selected for a transfer or peer relationship
- **override** — a temporary operator choice that changes the route decision without rewriting durable policy

If these blur together, diagnostics will rot.

## Proposed runtime model

### Tor

Default assumption:

- Arti-style client capability is compiled into the daemon build for supported targets
- warm/cool lifecycle is managed by the daemon
- bootstrap and onion-service capability are visible in transport status
- no external `tor` dependency is required for the supported packaged experience

Preferred operator story:

- `transport show tor` explains compiled-in version/build facts
- `transport warm tor` moves Tor from lazy to ready without mutating durable policy
- route output can say whether Tor lost because policy ranked it lower, because bootstrap was incomplete, or because a temporary direct override won

### I2P

Default assumption:

- the product ships a bundled I2P-capable helper/runtime payload
- the daemon can activate it on demand and expose its local runtime path if one is created
- AnonSync talks to it through a stable application-facing interface such as SAM

Preferred operator story:

- `transport show i2p` explains whether the helper is present, extracted, running, warm, degraded, or failed
- the daemon can expose a runtime path only when necessary, rather than pretending no helper exists
- helper activation, version, digest, and failure state are inspectable

## Session model

### Session strategies

The archive should support three abstract strategies:

- `singleton` — one session for the whole daemon/runtime
- `shared-pool` — a very small number of reusable sessions shared by policy or share class
- `dedicated` — a special session for a peer/share/sensitive workflow

The product should default conservatively:

- Tor may use shared reusable client state internally while exposing route decisions clearly
- I2P should usually prefer `singleton` or `shared-pool`, not `dedicated` per transfer

### Why I2P should avoid per-transfer churn

I2P is not just “Tor but different.”
For this archive, the important practical rule is:

- do not create a unique I2P session per connection or per file transfer
- prefer a small number of long-lived sessions
- surface that choice publicly so operators know how much route reuse exists

That choice is not only about performance; it is also about being a better network citizen and avoiding needless complexity.

## Route classes

AnonSync should expose at least these route classes by name:

- `lan-direct`
- `known-host-direct`
- `private-relay`
- `public-relay`
- `tor`
- `i2p`
- `public-direct`

Interpretation:

- `lan-direct` is normal inside local-only policy
- `known-host-direct` is still clearnet direct, but bounded by operator-specified peers
- `public-direct` is the dangerous one for privacy expectations and should stay manual/non-default on WAN paths

## Manual direct-speed override

WAN clearnet direct should be reachable through a visible short-lived override.

The override should have:

- explicit scope
- explicit reason
- explicit expiry
- visible decision-trace consequences

That keeps “I needed speed for this transfer” from silently becoming the system’s ambient policy.

## Runtime paths and storage

If a helper runtime needs local on-disk state, the daemon should expose that deliberately.

Rules:

- runtime paths should be inspectable
- persistent state paths should be inspectable separately from ephemeral extracted payload paths
- creation time should be auditable
- payload digest/version should be inspectable
- cleanup should be a supported operation, not a mystery
- persistence should survive ordinary restart when the transport benefits materially from remembered state

### Persistence posture

For I2P in particular, the archive should assume that persistence is part of the normal supported contract, not an optional optimization.
The daemon should preserve the router/runtime data needed for good warm-start behavior and should say clearly when a transport is starting from cold empty state versus reusing prior state.

Tor may keep less visible durable state than I2P depending on integration style, but the same operator principle applies: if state matters to performance or trust, the daemon should expose that fact.

## Lifecycle and uptime posture

Bundled privacy transports should prefer long-lived readiness rather than repeated cold churn.
That means:

- `warm` is a first-class supported action
- `cool` is a first-class supported action
- the daemon should distinguish “not started yet” from “cold because the operator cooled it deliberately”
- graceful shutdown matters for helper-style runtimes, especially on Linux-first server/headless deployments

For I2P, the archive should explicitly assume that very short average uptime is a poor fit and that the user-facing surface should encourage longer-lived router/runtime reuse where practical.

## Update and provenance posture

Bundling a privacy runtime creates a trust and maintenance obligation.
The v1 default should therefore be conservative:

- transport provenance must be inspectable locally
- payload/build digest must be inspectable locally
- update mode must be inspectable locally
- bundled runtime updates should ordinarily ride normal AnonSync releases rather than a hidden transport-specific auto-updater

Later revisions may decide that independently updated payloads are worth the extra complexity.
For now, the archive should prefer one release train and explicit local verification.

## Router-implementation boundary

The operator contract should not leak unnecessary implementation detail.
For I2P especially, the public model should stay stable even if the shipped helper/router changes underneath later.

That means the interface should talk in terms of:

- engine
- runtime
- session
- persistence
- provenance
- warm/ready/degraded/failed state

rather than forcing the operator to care about whichever router implementation happens to be underneath v1.

## Failure semantics

The daemon should distinguish:

- engine unavailable by build/support
- engine present but policy-disabled
- engine cold
- engine warming
- engine ready but unused
- engine degraded
- engine failed
- engine bypassed by a manual direct-speed override

That is much more useful than “privacy transport unavailable.”

## Non-goals for v1

This archive does **not** currently require:

- every possible Tor/I2P tuning knob
- arbitrary pluggable proxy backends
- multi-hop policy synthesis beyond named route classes
- pretending that public discovery is required on day one

## Summary rule

The product should feel like this:

> privacy transports are built in, inspectable, reusable, and honestly modeled; direct clearnet speed is possible, but only when the operator says so.
