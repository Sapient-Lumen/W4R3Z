# REFERENCE-ANCHOR-TEST

This note asks whether `reference_anchor` can be reduced into categories without erasing the distinctions the archive still needs.

## Question

After thinning the evidence axis,
can the archive compress anchor names into a small category scheme,
or are literal names still too important to reduce?

## Current result

**Yes, with care.**

The archive can reduce `reference_anchor` into a small category set,
as long as it preserves three distinctions that current profiles still care about:
- named UTC realizations
- generic UTC claims
- profile-specific reference families

## Why full literal naming is too heavy

Literal names such as:
- UTC(NIST)
- UTC(USNO)
- UTC(k)
- PRTC
- private local references

are sometimes useful,
but they make the hook heavier than it needs to be.
The minimal hook should capture category first,
with literal names available as a profile-local overlay when needed.

## Why overcompression would fail

If the archive collapsed everything into just:
- public reference
- private reference
- unknown

it would lose meaningful distinctions.
A generic claim of UTC is not the same as a named UTC realization.
And a telecom profile reference such as PRTC is not the same thing as either of those.

## Reduced category set

The archive can currently justify this anchor category scheme:

### 1. `utc_named_realization`
Examples:
- UTC(NIST)
- UTC(USNO)
- UTC(k)
- another named laboratory realization

### 2. `utc_unqualified`
Examples:
- “UTC” with no named realization
- “UTC traceable” without a more specific realization in the hook itself

### 3. `profile_reference`
Examples:
- PRTC
- PRC
- another profile-specific recognized reference family

### 4. `local_private`
Examples:
- local holdover-only reference
- private internal reference
- disconnected or sovereign local timing basis

### 5. `unknown`
The hook cannot currently state a useful anchor category.

## Why this survives current profiles

### P3 finance
Named UTC realizations and national-laboratory references still matter.
That justifies `utc_named_realization`.

### P5 synchrophasor / power
A generic “traceable to UTC” style claim often matters more than a specific named realization at the hook layer.
That justifies `utc_unqualified`.

### P4 telecom
Profile-specific references such as PRTC remain distinct enough to deserve their own category.
That justifies `profile_reference`.

### Local / degraded cases
The archive still needs a place for local or private references.
That justifies `local_private`.

## Archive judgment

Reduce the anchor axis,
but do not overreduce it.

The minimal hook now prefers categories.
Literal names remain available as profile-local overlays where regulation, metrology, or deployment detail makes them necessary.

## Next useful move

Test whether this category scheme survives a more disconnected or local profile,
where `local_private` might need to do more work than it has so far.
