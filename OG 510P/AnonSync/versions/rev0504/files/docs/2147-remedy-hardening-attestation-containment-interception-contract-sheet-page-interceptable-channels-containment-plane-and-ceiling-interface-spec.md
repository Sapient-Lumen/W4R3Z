# Remedy-hardening-attestation containment-interception contract sheet page — interceptable channels, containment plane, and ceiling

## Purpose

This page is the operator-facing contract sheet for deciding whether known relapse channels are merely watched or can actually be contained before stale reliance spreads.
It exists to stop `we will probably notice later` from being mistaken for `the product can intercept this safely now`.

## Core question

The page must answer:

**what is the strongest honest sentence we can make about containment and automatic relapse interception for the named slice, and what stronger sentence is still blocked?**

## Required fields

The contract sheet must capture at least:

- stale artifact identifier
- corrected replacement identifier
- outsider / audience slice identifier
- watch horizon class
- containment plane class
- interceptable channel set
- non-interceptable channel set
- maximum spread before interception
- containment trigger class
- residue-after-containment class
- containment evidence artifact set
- fallback manual containment path
- strongest honest containment sentence
- blocked stronger containment sentence

## Containment plane classes

The sheet must preserve at least:

- no containment declared
- manual operator-only containment
- device-local containment only
- channel-narrowing without true interception
- automatic interception with residual spread
- automatic interception with auditable proof
- unknown containment plane

## Channel panel

The page must force explicit answers about whether the reviewed slice can actually intercept:

- offline peer comeback precedence
- archive restore replay
- reconnect to stale local path
- delayed rescan discovery
- pause / scheduler residual effects
- read-only divergence and suspended updates
- forwarded single-file residue or device-local copies
- disconnected or local-share residue outside the canonical path

## Hard rules

The page must never allow:

- `watched` to silently stand in for `intercepted`
- `paused` to silently stand in for `contained`
- `disconnected` to silently stand in for `cleaned up`
- `read-only` to silently stand in for `stale state cannot spread`
- `removed from UI` to silently stand in for `removed from device or audience`
