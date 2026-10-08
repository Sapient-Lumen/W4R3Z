# 0004 — Performance profiles and measured adaptation

- status: accepted
- date: 2026-03-08

## Context

AnonSync needs to matter on both low-memory devices and high-throughput desktop or NAS nodes. The product also keeps LAN discovery enabled by default, which means discovery behavior must be fast enough to feel responsive but conservative enough not to become gratuitous noise.

The project wants to learn from Resilio's operational posture, while also respecting Tor and I2P transport costs.

## Decision

AnonSync should adopt an explicit **resource-profile** model plus measured adaptation.

Accepted defaults in this revision:

- keep **multiple named profiles** rather than one global tuning compromise
- treat **desktop balanced**, **desktop throughput**, **mobile tor default**, and **mobile tor frugal** as first-class starting profiles
- keep Tor in **client posture** and keep bundled `i2pd` in **`notransit` posture by default**
- use a **small-file direct-send fast path** with a hard RAM budget
- use a **durable local SQLite index in WAL mode**
- use **BLAKE3** as the default hashing family for manifests and chunk verification unless later evidence overturns it
- treat **discovery adaptation** as event-driven bursts plus capped steady-state beaconing plus backoff, not as uncontrolled chatter

## Consequences

- benchmark work becomes mandatory early
- profile defaults must be machine-readable, not only prose
- discovery policy needs explicit cadence, backoff, and privacy guardrails
- any auto-tuning claims should be conservative and measurable
- exact piece size and concurrency limits remain benchmark questions, not settled facts
