# Reliance timeline page: publication, acknowledgement, supersession, and recall events interface spec

## Purpose

This timeline preserves the life of a published claim after it leaves the internal operator workspace.

## Event classes

- `draft-created`
- `published`
- `delivery-confirmed`
- `receipt-acknowledged`
- `custody-accepted`
- `packet-forwarded`
- `freshness-nearing-expiry`
- `superseded`
- `recalled`
- `recipient-still-unacknowledged`
- `stale-copy-detected`
- `retired`

## Each event row must show

- event time
- actor
- audience class affected
- claim envelope at that time
- whether exclusions were visible
- whether freshness was still valid
- new obligation created
- stronger blocked sentence still blocked or newly unblocked

## Special render rules

### Packet forwarded

If the system knows a packet was forwarded or exported beyond the original recipient set, show:

- original audience
- downstream audience if known
- whether the downstream packet preserved exclusions and freshness
- stale-forward risk upgrade

Hard rule:

Forwarding never inherits a stronger claim ceiling by default.

### Superseded

When a packet is superseded, keep both:

- new active charter pointer
- old packet's surviving historical meaning

Hard rule:

`Superseded` does not mean `never existed`.
The timeline must still preserve what action the old packet safely enabled at the time.

### Recalled

When recalled, show:

- recall trigger
- audience notified so far
- recipients still pending notice
- weaker sentence that survives until confirmation

Hard rule:

Recall completion is not the same as recall issued.

## Decision sentence

Use:

> This published claim entered the world at [time], enabled [audience action], and is now [active/superseded/recalled]. Remaining live obligations: [list].
