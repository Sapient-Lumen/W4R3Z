# Route narrowing, residue, and clearance review interface spec

## Purpose

The archive already has disclosure and route objects.
What it still lacked was a concrete mutation review for this specific operator problem:

> when the operator narrows a subject from broader discovery to LAN-only, known-host-only, or overlay-only posture, what review surface proves **what stops immediately**, **what older route residue survives**, and **what additional clearance step is still required**?

Current Resilio guidance still treats this as multi-step ritual.
One article says to disable tracker and relay in share preferences and power-user settings, another adds config-mode keys, and another explains that learned public endpoints can persist until peer-expiration is reset and the client restarted.
AnonSync should expose that as one reviewed mutation instead of scattered lore.

## Core decision

Any meaningful route narrowing must create a first-class **route narrowing review**.
That review previews three distinct effects:

1. future publication/discovery narrowing
2. active-session drain or interruption
3. old learned-route residue clearance

The product should never imply that flipping one policy toggle immediately clears all older path memory.

## The fixed review order

The narrowing review should always render in this order:

1. **Requested narrower posture**
2. **Immediate mechanism changes**
3. **Active session consequences**
4. **Residual learned state**
5. **Required clearance steps**
6. **Receipt semantics**

## 1) Requested narrower posture

Show exactly what is being requested:

- disable public tracker
- disable relay fallback
- allow LAN discovery only
- allow known-host direct only
- prefer overlay only
- remove manual known-host record
- expire temporary public-direct lease

The operator should see the semantic intent before the product talks about restarts or cache actions.

## 2) Immediate mechanism changes

Preview which mechanisms will change as soon as the mutation applies:

- no new public tracker publication
- no new relay transfer attempts
- no new public-direct attempts
- LAN multicast remains allowed
- known-host direct remains allowed
- overlay rendezvous remains allowed

This section answers `what stops being newly allowed the moment I commit?`

## 3) Active session consequences

The review must then say what happens to sessions already in flight:

- drain and do not renew
- interrupt immediately
- survive until lease expiry
- survive because manual pin still permits them

This keeps the operator from mistaking policy narrowing for instant session disappearance.

## 4) Residual learned state

The surface should list residue explicitly, such as:

- retained public endpoint memory
- retained peer-address cache
- surviving manual known-host records
- surviving route lease receipts
- publication artifacts or invitations that still authorize broader arrival

For each residue item show:

- why it still matters
- which broader path it could still enable
- whether it decays naturally or needs explicit clearance

## 5) Required clearance steps

The review should then group the next steps under one of:

- `none required`
- `clear learned endpoints`
- `remove manual known-host pin`
- `end temporary lease`
- `wait for TTL`
- `restart or reload required`
- `rotate route/publication artifact`

The operator should not need to remember a second hidden procedure after a successful route edit.

## 6) Receipt semantics

The resulting receipt must distinguish:

- posture narrowed successfully
- sessions still draining
- residue still present
- clearance completed
- restart still pending

A route mutation is not fully done until the receipt can honestly say whether only the policy changed or the residue was actually cleared too.

## Good primary actions

Good actions include:

- `Narrow and clear learned endpoints`
- `Narrow now, let sessions drain`
- `Narrow and remove manual host pins`
- `Preview narrower posture`
- `Acknowledge residual risk`

Poor actions include:

- `LAN only`
- `Disable relay`

when those labels hide that several distinct effects still remain unresolved.

## Workbench rules

The review should be reachable from:

- subject route page
- machine transport defaults page
- disclosure / publication page
- active-session page when residue is blocking a narrower truth claim

No matter where the operator starts, they should land in the same review grammar.

## CLI rules

CLI should support:

```text
anonsync route narrow --subject shr_docs --allow lan-direct,known-host-direct --clear-residue --plan
```

The plan output should include:

- requested narrower route classes
- active sessions affected
- residual learned state
- whether restart/reload is needed
- what the post-apply receipt will still *not* prove unless clearance completes

## Result

A good route-narrowing review prevents five failures:

- policy edits that sound narrower than the actual effective posture
- operators forgetting that learned public endpoints may survive
- active sessions making a route page look inconsistent with recent policy edits
- manual known-host pins quietly keeping broader directness alive
- receipts claiming a stronger narrowed truth than the system has actually proven yet

If narrowing route policy can still leave the operator asking `did I really make this LAN-only, or did I only ask for it?`, AnonSync has not yet made route mutation honest enough.
