# BROADER-OBJECT-TEST

This note asks whether the archive now has enough pressure to draft a broader object around the provisional pair.

## Question

Now that the archive thinks the provisional pair adds value beyond `applicability`,
should it be promoted into a more concrete broader object,
or should it remain explicitly hypothetical?

## Current result

**Keep it hypothetical at archive scope for now.**

rev0026 strengthens the reason:
not only is the first clear widened boundary profile-local,
but the next candidate profiles do not yet repeat the same shape of boundary pressure.

## Why the pair looks real

### 1. Some systems explicitly expose time uncertainty to clients or applications
The source base includes systems and guidance where uncertainty values are not hidden implementation details.
They affect what the consumer is allowed or willing to do.

### 2. Some profiles already use explicit quality / tolerance surfaces
The source base includes profile-local signals that effectively expose time-related usability ranges.
This supports the idea that bound-bearing information is operationally meaningful.

### 3. The archive now has one clear runtime widened boundary
P5 shows that explicit time-error-bearing semantics can become part of a live interface,
not merely a nicer explanation in the archive.

## Why the object is still premature

### 1. The first clear case is still profile-local
The strongest current case comes from P5.
That is not yet enough recurrence.

### 2. The nearest other profiles press different boundary kinds
P3 currently presses traceability and audit evidence.
P4 currently presses control/distribution semantics.
Those matter,
but they do not yet cleanly repeat the same broader-object shape.

### 3. Promotion should follow repeated same-shape boundary change
A broader object should be drafted when the pair changes:
- multiple client contracts
- multiple deployment boundaries
- or multiple migration boundaries

and does so with recognizably similar semantics.

The archive is not there yet.

## Current archive posture

Keep:
- the provisional pair
- the broader-state sketch
- the current narrow waist
- the idea of a profile-local widened boundary

Do **not** yet draft:
- a normative broader object
- a serialized schema for the pair
- a new required archive-wide API surface

## What would change this

The archive should promote a broader object when it finds repeated independent cases where:
- the current narrow waist plus `applicability` is no longer enough,
- the provisional pair is no longer merely explanatory,
- and the same general widened semantic contract appears across more than one profile or boundary family.
