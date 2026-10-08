# License-topology review page — owner, seat, family lane, and revocation authority

## Review question

> what entitlement topology is actually governing this node or feature, and where are the real revocation and support boundaries?

## Topology classes that must stay separate

### 1) Personal-key topology

Use when one person's personal-use entitlement covers their own devices.
Required fields:

- entitlement source
- whether multi-device use is allowed
- whether other persons are out of scope
- whether the current node is independent or identity-linked

This topology is **personal entitlement**, not family or business delegation.

### 2) Family-pack topology

Use when entitlement may span multiple family members.
Required fields:

- family-capable source
- family-member ceiling
- whether the current participant is within that family scope
- whether the current feature depends on shared family legitimacy or only device count

This topology is **multi-person home lane**, not broad social sharing.

### 3) Business-owner topology

Use when one identity becomes license owner and linked devices inherit from that owner automatically.
Required fields:

- owner identity handle
- whether the current node is the owner or a linked device
- ownership-takeover risk if the key is applied elsewhere
- whether current features depend on owner continuity

This topology is **owner-centered authority**, not a symmetric seat mesh.

### 4) Shared-seat topology

Use when another identity gets Pro features only because the owner shared a seat.
Required fields:

- owner authority
- seat status
- reclaimability
- whether over-sharing or owner expiry can collapse the seat

This topology is **delegated and revocable**, not durable independence.

### 5) Wrong-support topology

Use when entitlement is applied but the platform/support lane is insufficient for the requested feature set.
Required fields:

- requested platform/support lane
- license qualifier actually present
- what features are stopped or blocked
- what upgrade or lane change would cure it

This topology is **misqualified activation**, not ordinary expiration.

### 6) Trial topology

Use when the feature works only within a time-limited evaluation window.
Required fields:

- trial scope
- expiry date or horizon
- cliff behavior on expiry
- durable entitlement path

## Review output sentence

The page must end with one sentence in this shape:

> `Current entitlement topology is <class>; stronger sentence <durable / independent / server-qualified / legitimate-for-lane> is blocked because <missing proof>.`

## Things the page must refuse to say

- `licensed` when the node only has a reclaimable shared seat
- `supported` when platform/server qualifiers still fail
- `free` when activation still depends on site-issued non-commercial licensing
- `independent` when the owner can revoke or steal the governing entitlement by reapplying elsewhere
