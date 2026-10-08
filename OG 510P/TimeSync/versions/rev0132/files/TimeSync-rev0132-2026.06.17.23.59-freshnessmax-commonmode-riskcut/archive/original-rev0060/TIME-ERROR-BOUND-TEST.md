# TIME-ERROR-BOUND-TEST

This note tries to break the archive's new phase-side field candidate.

## Question

Can `time_error_bound` really carry the phase-side pressure by itself,
or do hard Lane B / P5 cases force another promoted semantic such as static/dynamic decomposition or an explicit quality field?

## Current result

`time_error_bound` survives **provisionally**.

The source base shows more structure inside time error than the field itself exposes,
but not yet enough to force a second promoted phase-side semantic.

## What the hard cases showed

### 1. Time error is richer than a single scalar story
The source base explicitly decomposes time error into constant and dynamic components.
This means the field cannot be treated as if no deeper structure exists.

### 2. Hard quality signaling exists in some domains
Some demanding profiles use more detailed time-quality indications tied to usable ranges.
This proves that profile-local detail can become quite dense.

### 3. Frequency behavior still leaks into phase/time behavior
The source base also reminds us that time-side statistics can depend on frequency accuracy and stability.
That means the phase-side candidate cannot be interpreted in isolation from the rate side.

## Why the candidate still survives

### 1. The field is consequence-facing, not a full diagnostic surface
The archive only needs the thinnest first-class signal that downstream systems can act on.
It does not need to expose every decomposition at the narrow waist.

### 2. Static and dynamic time-error structure can remain profile-local
The archive has not yet found a case where users cannot act correctly from a bound, plus existing neighboring semantics, without demanding first-class decomposition.

### 3. Domain-specific quality tiers do not yet force a generic archive field
Rich quality encodings exist, but the archive still reads them as domain-local elaborations rather than proof of a second generic phase-side semantic.

## Current archive posture

Keep:
- `time_error_bound`
- `freshness`
- `regime`
- `holdover_class`

Do **not** yet promote:
- static time error field
- dynamic time error field
- generic phase-quality field

## What would overturn this result

The archive should reverse this note if it finds a phase-side case where:
- `time_error_bound` remains present,
- the neighboring semantics remain present,
- and users still cannot act correctly without separate promoted structure for time-error components or quality.
