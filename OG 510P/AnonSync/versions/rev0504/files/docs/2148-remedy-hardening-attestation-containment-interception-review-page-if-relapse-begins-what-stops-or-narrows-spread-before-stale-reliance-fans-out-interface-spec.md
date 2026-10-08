# Remedy-hardening-attestation containment-interception review page — if relapse begins, what stops or narrows spread before stale reliance fans out?

## Review goal

This page is the explicit review surface for deciding whether relapse control is real containment or merely later discovery.
The page must foreground interception, narrowing, residue, and proof.

## Review questions

The page must ask, in direct language:

- if stale state starts moving again, what exact mechanism stops it or narrows it before audience reliance fans out?
- which channels are actually interceptable right now and which only become visible later?
- what stale residue survives even after the best available containment step?
- what proof survives after the live UI, temporary history, or operator memory is gone?
- what exact stronger sentence remains blocked because containment is incomplete, slow, or unauditable?

## Required review sections

### 1. Interceptable now

Require a row for each named channel with one of these verdicts:

- intercepted before spread
- narrowed after some spread
- only detectable after spread
- only containable with operator help
- not containable
- unknown

### 2. Spread budget

Require the reviewer to state:

- maximum honest spread before interception
- whether spread can occur to one device, many linked devices, local shares, or forwarded copies
- whether spread can occur while UI still appears calm or paused

### 3. Residue after containment

Require explicit answers about whether containment leaves behind:

- local device copies
- placeholders still capable of re-fetch
- archive versions
- disconnected folders still accessible in the filesystem
- forwarded single-file copies or local-share derivatives
- ambiguity about which audience slices remain dirty

### 4. Evidence and auditability

Require the reviewer to name:

- durable proof of interception
- durable proof of narrowed spread
- durable proof of residual stale state still remaining
- missing evidence that blocks a stronger sentence

### 5. Strongest sentence panel

The review must end with:

- strongest honest containment sentence
- blocked stronger sentence
- exact blockers
- next intercept hardening task

## Failure pattern warnings

The page must visibly warn against at least:

- treating pause or scheduler posture as full containment
- treating read-only divergence as safe cleanup rather than a fork / suspension state
- treating disconnect as audience cleanup when files remain locally accessible
- treating UI removal as device removal or reliance retirement
