# Remedy-hardening-attestation closure-proof timeline page — intercept, revoke, expire, confirm, nonresponse, residue discover, and horizon close events

## Purpose

This page makes closure legible over time.
It exists so the archive can show not only that containment happened, but also whether later evidence actually closed the governed audience or merely narrowed it.

## Timeline events the page must support

The page must support at least:

- containment event fired
- share or approval revoked
- link expired
- click budget exhausted
- linked-device folder removed
- unlinked peer confirmed clean
- recipient confirmed retirement
- local-share residue discovered
- forwarded artifact discovered
- audience slice marked nonresponsive
- survivor ledger revised
- closure horizon closed
- late survivor discovered after closure

## Event requirements

Each event row must preserve:

- timestamp or bounded time window
- actor / audience slice / surface
- event class
- affected carrier class
- whether the event widened closure proof, narrowed it, contradicted it, or only changed future-access posture
- whether the strongest honest closure sentence changed

## Closure rule

The timeline must not allow `closure horizon closed` unless it also records:

- which slices were confirmed closed
- which slices remained unknown but tolerated
- what residual carriers still survived
- what evidence justified the final sentence anyway
- what stronger sentence stayed blocked despite closure

## Visual emphasis

The page should visually distinguish:

- containment events
- future-access-blocking events
- recipient confirmation events
- nonresponse / unknown-survivor events
- late-survivor discovery events
- final closure event
