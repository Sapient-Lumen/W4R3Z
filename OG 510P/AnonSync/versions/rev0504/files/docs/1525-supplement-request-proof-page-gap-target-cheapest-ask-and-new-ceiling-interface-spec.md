# Supplement request proof page: gap target, cheapest ask, and new ceiling interface spec

## Purpose

When a received packet is not yet sufficient, the operator needs a proof page that answers:

> what exactly are we asking for next, which gap does it close, why is it the cheapest useful ask, and what new ceiling could it unlock if it arrives?

## Core decision

Every non-trivial supplement request must produce one first-class **Supplement request proof**.
The request is not just a message; it is a typed evidentiary move.

## Fixed page order

1. **Request header**
2. **Blocked-gap card**
3. **Chosen-ask card**
4. **Rejected-alternatives card**
5. **Expected-uplift card**
6. **Expiry-and-fallback card**
7. **Decision sentence**

### 1) Request header

Show:

- supplement request id
- source intake id
- requester
- target audience or recipient
- current intake grade
- requested artifact or clarification class
- request status

Supported `request_status` values:

- `drafted`
- `sent-awaiting-reply`
- `partially-answered`
- `fully-answered`
- `expired`
- `withdrawn`
- `superseded`

### 2) Blocked-gap card

Required rows:

- exact named gap
- sentence blocked by this gap
- whether gap is singular or one of several blockers
- urgency of closure
- whether a non-response should lower confidence later

Hard rule:

A supplement request may not say only `need more detail`.
It must bind to one or more named blocked gaps.

### 3) Chosen-ask card

Required rows:

- chosen supplement
- why it is the cheapest useful ask
- collection channel
- expected collector or responder
- expected burden and intrusion
- expected turnaround horizon

Supported `chosen_ask_class` values:

- `context-addendum`
- `timestamp-addendum`
- `subject-identification-addendum`
- `fresh-log-window`
- `expanded-log-size-window`
- `raw-unredacted-packet`
- `new-world-capture`
- `crash-or-dump-artifact`
- `network-test-result`

Hard rule:

When a clarification note could close the gap, a new heavy artifact request must be justified explicitly.

### 4) Rejected-alternatives card

List:

- heavier asks rejected
- lower-value asks rejected
- asks deferred for privacy reasons
- asks impossible due to missing channel or authority

Hard rule:

The product must show why the chosen ask won, not just what was sent.

### 5) Expected-uplift card

Required rows:

- current sufficiency grade
- expected grade if answer lands fully
- expected grade if answer lands partially
- strongest new sentence it could unlock
- strongest sentence it still would not unlock

Hard rule:

The page must publish bounded uplift, not optimistic uplift.

### 6) Expiry-and-fallback card

Required rows:

- request expiry or stale-after time
- fallback sentence if no response arrives
- fallback sentence if incomplete response arrives
- next heavier ask after expiry, if any
- whether case should freeze, proceed, or close weakly on timeout

Hard rule:

Every supplement request must end with a timeout posture.

### 7) Decision sentence

Form:

> The packet is not yet sufficient because **[named gap]** blocks **[blocked sentence]**. The cheapest useful supplement is **[chosen ask]** via **[channel]**. If it arrives fully, the grade may improve from **[current grade]** to **[expected grade]**. If it does not arrive by **[expiry]**, the surviving sentence will remain **[fallback sentence]**.
