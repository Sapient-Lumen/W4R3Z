# Remedy-hardening-attestation supersession-trust contract sheet page — outsider-verifiable successor proof and explanation ceiling

## Purpose

This page is the operator-facing sheet for deciding whether a late outsider who reaches the corrected replacement can tell, from that surface itself, what it supersedes and why to trust the supersession claim.
It exists to stop `they found the corrected thing` from being mistaken for `they can understand and trust why it is the right thing`.

## Core question

The page must answer:

**for this named outsider-facing surface, what is the strongest honest sentence about whether the corrected replacement is self-explaining and trustable as the legitimate successor?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- stale artifact identifier
- corrected replacement identifier
- outsider-facing surface identifier
- canonical correction identifier
- successor proof class (`signed supersession receipt`, `same-surface supersession banner`, `linked authority receipt`, `operator note only`, `none`)
- explanation carrier set (`replacement header`, `adjacent banner`, `landing-page notice`, `embedded watermark`, `linked receipt`, `manual explanation only`, `none`)
- authority source class (`same authority as stale artifact`, `delegated authority`, `replacement-only authority`, `unclear`, `none`)
- outsider-verifiable trust class
- intended trust coverage threshold
- current trust coverage threshold
- unresolved trust blocker count
- highest-risk unresolved trust blocker
- strongest honest trust sentence now
- blocked stronger self-explaining sentence now

## Standing ladder

The page must support at least these distinct standings:

- corrected replacement exists only
- corrected replacement is reachable but trust is unexplained
- supersession is claimed but authority remains opaque
- explanation exists but only with operator-side context
- named surface carries a self-explaining supersession claim
- named surface carries outsider-verifiable supersession proof
- broader outsider-trust sentence still blocked
- later contradiction reopened trust risk
- receipt superseded

## Required comparisons

The sheet must compare:

- replacement routed versus replacement explained
- explanation shown versus authority proved
- operator-verifiable trust versus outsider-verifiable trust
- one named surface proof versus broader outsider-trust coverage
- current best sentence versus blocked stronger self-explaining sentence

## Required layout

### Header

Show:

- correction name
- stale artifact name
- corrected replacement name
- current supersession-trust standing
- strongest honest trust sentence now

### Left column — intended trust contract

Show:

- required successor proof class
- required explanation carrier set
- required authority source class
- required outsider-verifiable trust class
- required trust coverage threshold

### Center column — observed trust facts

Show:

- visible supersession statement now
- visible authority statement now
- visible stale-artifact reference now
- linked receipt or proof availability
- local-only naming dependence
- operator-context dependence
- evidence freshness for trust surface

Every row in this column must have:

- current value
- evidence source
- whether it strengthens or weakens outsider trust

### Right column — consequence for truth

Show:

- whether only replacement reachability is proven
- whether explanation exists without outsider-verifiable authority
- whether the named surface is self-explaining now
- whether broader outsider trust is still blocked
- what stronger sentence remains blocked

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- replacement exists only
- replacement reachable only
- supersession explained only with operator context
- named surface self-explaining
- named surface outsider-verifiable
- broader outsider-trust sentence still blocked

## Interaction requirements

The interface must support:

- clicking any successor-proof chip to open proof class, authority source, evidence age, and exclusions
- comparing several explanation carriers side by side
- filtering blockers to missing explanation, missing authority, naming ambiguity, or operator-context dependence
- opening the blocked stronger sentence and seeing exactly which trust blockers keep it blocked

## Hard rules

The page must never allow:

- route success to silently become trust success
- operator-side fingerprint review to silently become outsider-visible authority proof
- local custom naming to silently become stable successor identity
- one good trust surface to silently become broader outsider-trust safety
