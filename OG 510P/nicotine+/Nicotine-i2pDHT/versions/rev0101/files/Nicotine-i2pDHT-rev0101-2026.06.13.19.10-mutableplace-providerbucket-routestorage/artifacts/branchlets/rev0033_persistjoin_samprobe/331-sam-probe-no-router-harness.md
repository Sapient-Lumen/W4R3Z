# SAM probe no-router harness

`samprobe.py` adds a no-network plan for the eventual live SAM harness. The first probe should be safe even when no router exists, because most developer and CI environments will not have I2P running.

The rev0033 profile is intentionally narrow:

- loopback SAM endpoint by default;
- streaming-first;
- persistent or imported destination material;
- Ed25519 `SIGNATURE_TYPE=7`;
- no HTTP proxy exposure;
- no datagram-primary assumption.

A local unavailable router can be an accepted probe result. A non-loopback SAM endpoint, transient destination, datagram-primary plan, or option drift is quarantined before live code can make it normal.

This is still not a SAM client. It is a transcript classifier and command planner that keeps future live transport from smuggling assumptions into the DHT core.
