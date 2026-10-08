# DISCOVERY-REUSE-TEST

This note tests whether `boundary_context` can reuse the archive's existing small discovery/request surface.

The archive already has:
- a small discovery/request sketch for optional visibility
- `profile_default` hooks that use that pattern
- `boundary_context` as a requestable-by-default explanatory wrapper

The remaining question is whether explanation visibility now needs a second discovery channel.

## Question

Can `boundary_context` reuse the existing discovery/request surface,
or does it need separate visibility semantics of its own?

## Source pattern

The source base continues to favor reuse over multiplication.

- NTPv5 optional chain context is already exchanged through additional request/response material rather than through a wholly separate discovery subsystem.
- Telecom profiles use narrow signaling/negotiation surfaces when extra synchronization service or context is needed, rather than inventing a second negotiation plane for every different semantic category.
- The archive's own current distinction is not between two fundamentally different transport problems; it is between two kinds of thing being exposed: state and explanation.

That is a naming / scoping problem more than a protocol-surface problem.

## Smallest answer that survives the pressure

Yes.
`boundary_context` should reuse the existing small discovery/request surface.

The archive does **not** need a second discovery channel.
It only needs to keep the requested subjects distinct.

## How reuse should work

The current best rule is:

> one shared discovery/request surface, with separate requested subjects for state visibility and explanation visibility

That means the archive may keep the same compact visibility vocabulary,
while asking for different things such as:
- a hook or state surface
- or `boundary_context`

The reuse is in the mechanism,
not in pretending state and explanation are identical.

## Why reuse is better than a second channel

### 1. The archive already has the right size mechanism
The existing discovery/request surface is already small enough for optional visibility.
A second surface would add structure faster than it adds understanding.

### 2. Explanation visibility is not a different transport class
`boundary_context` is different in meaning,
not in the basic shape of optional visibility.
The archive can say “request this too” without inventing “explanation discovery” as a new subsystem.

### 3. Reuse preserves the archive's design style
The archive has repeatedly preferred:
- one small shared surface
- separate semantics at the subject level
- and profile-local strengthening only when necessary

This result continues that pattern.

## Current archive judgment

`boundary_context` should reuse the archive's existing discovery/request surface.

The archive should therefore keep:
- one small discovery/request mechanism
- one compact visibility vocabulary
- separate requested subjects for state/hook visibility versus explanation visibility

## What this still does **not** settle

This note still does not decide:
- whether the shared surface needs explicit namespaces for state versus explanation
- whether all profiles should expose `boundary_context` support in the same way
- whether operator-facing and machine-facing request patterns should fully match

## Next useful move

Test whether the shared surface needs explicit namespace separation,
or whether one request list with distinct item names is already enough.
