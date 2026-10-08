# Shared substrate topology review page: SMB notification floor, service namespace, and authoritative write lane interface spec

## Purpose

This review appears whenever an operator adds, migrates, rehomes, or reclassifies a synced subject onto a shared or indirect substrate.
The review exists to answer one ordinary question before commit:

> what topology am I creating here, which runtime will touch it, which notification grade will remain, and which write path am I declaring authoritative?

## Trigger conditions

Open this review when any of the following become true:

- the destination is a network share or UNC path
- the runtime identity changes from interactive user to service / system / container
- the chosen path is not visible in the same way to the current projection and the runtime
- filesystem notifications are absent or degraded
- a second write lane to the same bytes is detected or declared

## Fixed page order

1. topology delta header
2. runtime-identity migration card
3. notification-floor card
4. authoritative-write-lane card
5. decision footer

### 1) Topology delta header

Show:

- current topology
- requested topology
- changed risk class
- strongest safe sentence after apply
- stronger rejected sentence after apply

Example safe sentence:

- `After this change, Sync will reach the subject through a service-visible UNC path and detect updates primarily through rescan rather than immediate filesystem notifications.`

### 2) Runtime-identity migration card

Show:

- current runtime identity
- requested runtime identity
- whether storage/state location changes
- whether prior shares or receipts remain visible there
- required re-add / re-share consequences

If a runtime change effectively creates a new state world, render that plainly rather than as a surprise after apply.

### 3) Notification-floor card

Show:

- current detection class
- requested detection class
- fallback mechanism
- expected discovery latency band
- what evidence supports the classification

Possible grades:

- `event-driven`
- `event-driven with rescan backup`
- `rescan-backed`
- `restart-biased`
- `unknown / unproven`

### 4) Authoritative-write-lane card

Show each candidate lane:

- runtime direct access
- SMB / UNC mediated access
- host-local side writer
- user interactive alias path
- automation / service helper

For each lane show:

- whether it is authoritative, tolerated, degraded, or forbidden
- rollback / corruption suspicion
- notification implications
- which receipt or warning it feeds

### 5) Decision footer

Available decisions:

- `Accept topology`
- `Accept with degraded detection`
- `Block mixed writers and continue`
- `Return to local path`
- `Emit reviewed boundary receipt`

## Rules

### Rule 1 — topology review must compare before and after, not just show the target path

The operator must see what semantic grade they are losing or gaining.

### Rule 2 — runtime state split is first-class

If moving to a service or Local System runtime changes storage folder or visible shares, the page must say that explicitly before apply.

### Rule 3 — authoritative write lane is chosen, not inferred later

The product must not let two plausible write lanes silently coexist without a declared boundary.

### Rule 4 — degraded detection is not a footnote

Rescan dependence must appear in the main claim, not buried in secondary help.

## Acceptance criteria

A later operator can:

- tell what topology changed
- tell whether runtime identity and state world changed
- tell what notification floor applies after the change
- tell which write lane is authoritative
- tell whether any mixed-writer lane is blocked or merely tolerated
- tell what claim remained forbidden
