# PROFILE-DEFAULT-DISCOVERY-TEST

This note tests the next frontier after the archive classified both `profile_default` hooks.

The question is no longer where the hooks belong.
It is how participants learn about them or ask for them without widening the archive-wide core.

## Question

Does greenfield TimeSync need:
- no extra surface at all
- a small discovery/request surface
- or a fuller negotiation mechanism

for `profile_default` hooks?

## Comparison surface

### Case 1 — Profile-fixed default visibility
Some boundaries already want the extra semantics by default.

P5-like time-status paths are the clearest example:
if traceability- and accuracy-adjacent status is mandatory at the boundary,
then per-client negotiation does not buy much.
The profile simply requires the surface.

This means the archive should preserve **profile-fixed default visibility** where omission would already be misleading.

### Case 2 — Optional but native surfaces
NTPv5 points toward a different pattern.
It keeps a small core header but uses extension fields for optional features and future extensibility.
That is a useful model for the archive:
not every extra semantic belongs in the minimum exchange,
but there should be a native place for it when present.

### Case 3 — Explicit request when the profile expects it
Telecom timing gives a third pattern.
In the frequency profile, unicast message negotiation is used when slaves request synchronization service from masters.
That means some environments really do want explicit request behavior.
But even there, the request surface is narrow and profile-shaped,
not a general capability bazaar.

### Case 4 — Lightweight discovery rather than deep negotiation
Roughtime's version handling is another useful pattern.
Clients send supported versions and servers respond within that space.
That is not a giant negotiation subsystem.
It is a constrained discovery/compatibility surface.

## Archive judgment

The archive now has enough evidence for a middle answer:

### Yes to a small discovery/request surface
The greenfield track should assume a small native way to:
- discover whether `profile_default` surfaces are available
- or request them where a profile permits request-driven behavior

### No to a general negotiation subsystem
The archive does **not** yet need:
- a generic capability catalog
- free-form bilateral negotiation
- hook-by-hook bargaining logic
- or protocol-wide option choreography

### Keep profile-fixed defaults where they belong
If a profile already requires a surface by default,
that should stay profile-fixed.
Discovery/request should not weaken default-visible requirements.

## Smallest honest design rule

The current best rule is:
- **profile-fixed by default** where omission is unsafe or misleading
- **discoverable/requestable** where the profile allows optional extra surfaces
- **not generally negotiated** beyond that

This is a small rule.
It fits the archive's posture.

## What this means for the two current hooks

### `traceability_posture`
- profile-fixed at some P5-like boundaries
- discoverable/requestable in some lighter or integration-shaped boundaries
- not a reason for broad negotiation machinery

### `sync_dimension`
- often profile-declared already
- sometimes worth echoing or requesting explicitly at an interface
- again, not a reason for broad negotiation machinery

## Why this is enough for now

The archive does not yet need packet grammar.
It only needs to know whether ambiguity forces some additional surface.
The answer now looks like yes,
but only a small one.

That preserves:
- the small core
- the small middle tier
- and the archive's bias against feature sprawl

## What this still does **not** settle

This note still does not decide:
- the exact shape of the discovery/request surface
- whether it should be one field, one extension, or one profile-side rule
- whether the same surface should cover both discovery and request
- what the smallest legal response vocabulary should be

Those remain open.

## Next useful move

Sketch the thinnest possible discovery/request surface.
The next step should stay architectural:
- not a full packet layout
- not a capability catalog
- just enough structure to show how the archive means “discoverable/requestable but not broadly negotiated.”
