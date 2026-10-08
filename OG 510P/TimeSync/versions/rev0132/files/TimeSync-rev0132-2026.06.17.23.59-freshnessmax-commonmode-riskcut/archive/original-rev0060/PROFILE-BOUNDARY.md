# PROFILE-BOUNDARY

This note records the current boundary between the invariant core, explicit profiles, and tiny extension hooks.

## Rule

If a requirement appears across all six scenarios, it is a candidate for the core.
If it binds mainly one or two scenarios, it belongs in a profile unless there is a strong reason otherwise.
If a profile repeatedly needs the same very small extra handle, that handle may become an extension hook.

## What belongs in the core

The core should carry:
- bounded time semantics
- timescale semantics
- freshness
- operating regime
- coarse source posture
- coarse downstream applicability
- minimal policy surfaces for source selection, error acceptability, holdover, regime transitions, and downstream consequence

## What belongs in profiles

Profiles should carry most of the density around:
- sector-specific thresholds
- traceability requirements
- audit and retention depth
- phase / frequency extensions
- topology and path assumptions
- compliance-specific acceptance logic
- detailed source families and deployment patterns
- operator and incident workflow detail

## What belongs in extension hooks

A hook belongs between core and profile when:
- multiple demanding profiles need it
- the hook can stay very small
- and the hook helps prevent larger profile-specific substructures from leaking upward

The current hook set has now been tightened again in `EXTENSION-HOOKS.md`.

## Boundary discipline

The archive should resist three failure modes:

1. **profile leakage into the core**
2. **core evasion into profiles**
3. **hook inflation into hidden mini-specs**

## Current live edge

The sharpest unresolved edge remains whether `sync_dimension` stays a hook or eventually forces a broader core object.
