# RFC-0073: Builder strategy tiers (jails + microVM builders)

- Status: draft
- Author(s):
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary

Define two sandbox tiers for builds: jail-backed as default, microVM-backed as optional high-assurance mode.

## Motivation

- Jails are fast and practical (poudriere demonstrates this pattern).
- For high-risk toolchains or “hostile builder” assumptions, microVM builders can shrink blast radius further.

## Goals / Non-goals

Goals:
- Tier 1 (jail) must deny network by default and never inject secrets
- Tier 2 (microVM builder) must be policy-selectable per target
- both tiers produce the same evidence objects and are verified the same way

Non-goals:
- requiring microVM builders for all builds

## Proposal

- Extend sandbox policy to include `builder_tier: jail|microvm`.
- Provide a standard builder image (microVM) pinned by Lock.
- Verification rules:
  - outputs must match Plan digests
  - closure proofs must validate

## Alternatives considered

- microVM-only builders (too slow for iteration)
- jail-only builders (insufficient for some threat models)

## Backwards compatibility

Additive; Tier 1 is default.

## Security considerations

- tier selection is part of Plan digest
- microVM builder images must be signed and policy-checked

## Open questions

- how to structure “builder image” as an artifact target
- default policy heuristics for tier selection
