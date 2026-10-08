# 0003 — Product defaults

## Current defaults

- sharing is invite-only
- LAN discovery is enabled by default
- LAN discovery beacons are invite-scoped, rotating, and should avoid stable share identifiers
- mobile is first-class
- mobile defaults to Tor transport
- mobile I2P is opt-in
- permissions should mirror Resilio's RO / RW / Owner posture as closely as practical
- selective sync / placeholder mode is the default mobile posture
- encrypted sink mode comes before richer untrusted live-peer semantics
- users are not expected to understand Tor or I2P internals

## Why this matters

These defaults should shape protocol and UI decisions early so future revisions do not drift into a generic sync tool with anonymity bolted on later.
