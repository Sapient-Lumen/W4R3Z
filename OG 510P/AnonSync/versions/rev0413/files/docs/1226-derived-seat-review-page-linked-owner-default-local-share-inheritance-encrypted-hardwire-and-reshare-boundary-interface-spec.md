# Derived-seat review page — linked-owner default, local-share inheritance, encrypted hard-wire, and reshare boundary

## Purpose

Some seats are not ordinary direct grants at all.
This page exists for cases where a peer posture is derived from topology or share family: linked-device owner default, local-share inheritance, or encrypted hard-wiring.
The operator must see derivation class before trying to edit rights or predict behavior.

## Cases that must open this page

- a linked device unexpectedly behaves like Owner;
- someone attempts to create a read-only seat inside one linked family;
- a local share downshifts after the source seat is narrowed;
- user management cannot edit a local share as expected;
- an encrypted node is being treated like a normal backup writer or normal selective-sync seat;
- reshare expectations depend on whether the seat is direct or derived.

## Inputs the page must collect

### Derivation facts

- direct grant versus linked-family default versus local-share derivation versus encrypted hard-wire
- source seat and its current posture, if any
- whether the seat lives inside one identity family
- whether the seat was created by manual key/link intake rather than by ordinary linked appearance

### Editability facts

- whether posture may be edited live through user management
- whether re-share / remove-and-reshare is required for posture change
- whether narrowing cascades automatically from source to derivative
- whether the derivative can ever hold Owner

### Capability facts

- can onward-share at all
- if onward-share exists, is it ordinary or encrypted-only
- can Selective Sync be used
- does delete-following or overwrite-heal become mandatory

## Decision ladder

### Branch 1 — linked-family owner default

Use this branch when a seat appears because devices are linked under one identity.
The page should show:

- that Owner-like posture came from family linkage rather than ordinary invitation;
- why creating a RO seat requires breakout into another artifact path;
- what stronger claims about independent review or revocation are blocked.

### Branch 2 — local-share inheritance

Use this branch when the seat is derived from a parent source on the same machine.
The page should show:

- inherited permission floor;
- inability to receive Owner;
- automatic downshift if the source is narrowed;
- whether remove-and-reshare is required for a change.

### Branch 3 — encrypted hard-wire

Use this branch when the seat is an encrypted node.
The page should show:

- hard-wired RO posture;
- mandatory overwrite-heal and delete-following implications;
- no Selective Sync;
- encrypted-only onward share boundary;
- why archive visibility is weaker than republish authority.

### Branch 4 — derivation unresolved

Use this branch when the seat presents mixed signals and the operator may be about to edit the wrong control plane.
The page should show:

- missing proof required;
- cheapest next question;
- blocked stronger sentence until derivation is proven.

## Required warnings

- `owner-like` is weaker than `directly granted owner`.
- `local share` is weaker than `ordinary remote peer`; its ceiling comes from the parent source.
- `can store ciphertext` is weaker than `can republish plaintext or restored deletes`.
- `I can see this seat in UI` is weaker than `I can edit its rights live`.
- `break out a RO seat` may require a new artifact path rather than an in-place permission flip.

## Review outputs

- `derivation_class`
- `live_editability_class`
- `cascade_behavior_class`
- `reshare_boundary_class`
- `strongest_safe_sentence`
