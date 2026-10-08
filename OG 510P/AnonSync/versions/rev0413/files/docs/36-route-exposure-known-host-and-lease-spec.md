# Route exposure, known-host, and lease spec

## Purpose

This document makes one narrow but important part of the interface explicit:

- what AnonSync publishes about reachability
- which route classes it is actually allowed to dial
- how peer-pinned direct paths differ from ambient public direct
- how temporary direct-speed exceptions stay visibly temporary

The archive already had route objects, transport-runtime objects, and override leases.
This document sharpens the specific transport-policy seam that still mattered after `rev0025`.

## Why this needs its own spec

Resilio's official docs are enough to reconstruct a real route model:

- Sync learns tracker/relay locations from `sync.conf`
- Sync tells trackers about public/local IPs and share presence
- Sync then prefers direct peer connection and falls back to relay
- LAN-only mode requires disabling tracker/relay and clearing remembered global endpoints if they were learned earlier
- power-user preferences expose knobs such as `tunnel_protocols`, `folder_defaults.known_hosts`, `folder_defaults.use_tracker`, and `folder_defaults.use_relay`

That is not trivial capability.
It is a serious operator model.
But it is still too easy to answer the wrong question.
A user often does **not** just want to know:

> “can it connect?”

They want to know:

> “who learns about this share/device relationship, through what infrastructure, and why is this route eligible at all?”

AnonSync should therefore publish those answers directly.

## Core rules

### 1) Publication and dialing are different surfaces

A policy may publish very little yet still dial several route classes.
A policy may also publish broad reachability and still reject some dial classes.
These must not be collapsed into one vague “networking” toggle.

### 2) Known-host direct is not the same as ambient public direct

A peer-pinned direct path means:

- a specific peer is allowed at a specific address or host
- within a defined scope
- for a defined time or until revoked

That is narrower than general public direct eligibility.
The interface must preserve that distinction.

### 3) A temporary direct exception is a lease, not a hidden policy edit

If an operator opens a speed window for one bulk transfer, the durable privacy posture should remain intact.
The system should show:

- what the baseline policy is
- what temporary lease widened it
- when the lease ends
- whether the lease exhausted by time, bytes, or explicit cancelation

### 4) Retained endpoint memory is visible state

A narrowed policy should not quietly continue using a wider remembered endpoint without saying so.
The control plane must show:

- cached endpoint entries still influencing eligibility
- whether a cache clear is recommended or required
- whether current behavior differs from baseline only because of remembered state

### 5) WAN privacy defaults remain overlay-first

For privacy-oriented defaults:

- LAN direct may remain ordinary on local networks
- Tor and/or I2P should be the ordinary WAN route classes
- public direct should be disabled or lease-only by default
- peer-pinned known-host direct should require explicit admission

## Surface decomposition

### Publication profile

A supported object, or a supported inline sub-object of discovery policy, describing what reachability facts AnonSync publishes.

Fields:

- `publication_profile_id`
- `scope_type` (`system`, `policy`, `share`)
- `scope_id` nullable
- `publish_presence_via[]` (`lan`, `private-discovery`, `public-tracker`, `tor-onion`, `i2p-destination`)
- `publish_endpoint_classes[]` (`lan-addresses`, `approved-known-hosts`, `tor-onion`, `i2p-destination`)
- `share_membership_visibility` (`none`, `approved-peers-only`, `discovery-service-visible`)
- `accept_inbound_from` (`none`, `approved-peers`, `known-hosts-only`, `policy-bound`)
- `endpoint_cache_policy` (`disabled`, `ephemeral`, `retained-with-ttl`, `retained-until-cleared`)
- `clear_cache_on_narrowing` (`true`, `false`)
- `provenance_ref` nullable

Questions it answers:

- who can learn that this device/share is reachable?
- which service class learns that fact?
- which endpoint classes are being published right now?
- could remembered endpoint state survive a later policy narrowing?

### Dial policy

The dial half of discovery policy.
This already overlaps with the archive's existing discovery object, but this document makes the decomposition explicit.

Fields:

- `dial_preference_order[]` (`lan-direct`, `tor`, `i2p`, `known-host-direct`, `private-relay`, `public-relay`, `public-direct`)
- `allow_public_direct` (`disabled`, `lease-only`, `allowed`)
- `allow_known_host_direct` (`disabled`, `allowed`)
- `accept_tracker_learned_endpoints` (`never`, `when-policy-allows`, `always`)
- `relay_pool` (`none`, `private`, `public`, `mixed`)
- `overlay_requirement` (`none`, `preferred`, `required`)
- `route_reuse_policy` (`reuse-ok`, `prefer-fresh`, `clear-on-narrowing`)
- `fallback_visibility_guard` (`strict`, `warn`, `off`)

### Known-host record

A first-class record authorizing a peer-pinned direct path without implicitly turning on public direct everywhere.

Fields:

- `known_host_id`
- `peer_id`
- `address`
- `scope_type` (`system`, `policy`, `share`, `peer-share`)
- `scope_id` nullable
- `address_kind` (`ip-port`, `dns-port`)
- `allowed_use` (`dial-only`, `dial-and-accept`)
- `origin` (`manual`, `recovery`, `import`, `policy-derived`)
- `created_by`
- `created_at`
- `expires_at` nullable
- `last_verified_at` nullable
- `health_state` (`unknown`, `reachable`, `stale`, `failed`)
- `provenance_ref` nullable

Rules:

- a known-host record never widens unrelated shares or peers implicitly
- expiration removes eligibility cleanly
- stale records remain visible until removed or replaced
- a peer-pinned path should appear distinctly in route/explain output

### Route lease

A temporary route or exposure exception.
This is more specific than the archive's generic maintenance override.

Fields:

- `route_lease_id`
- `effect` (`allow-public-direct`, `prefer-known-host`, `prefer-overlay`, `suspend-public-discovery`, `drain-route-class`)
- `subject_type` (`system`, `policy`, `share`, `peer`, `peer-share`)
- `subject_id` nullable
- `peer_id` nullable
- `known_host_ref` nullable
- `reason`
- `created_by`
- `created_at`
- `expires_at` nullable
- `byte_cap` nullable
- `transfer_cap` nullable
- `exhaustion_policy` (`expire`, `re-evaluate`, `hold-until-cancelled`)
- `effective_state_ref`
- `provenance_ref` nullable

Rules:

- every direct-speed lease must carry an explicit reason
- a lease should normally have a TTL and may also have a byte cap
- the lease should be visible in `status`, `route show`, `exposure show`, and audit
- policy reads must distinguish durable baseline from lease-modified effective state

### Exposure report

A preview or status object answering what a route posture reveals.

Fields:

- `exposure_report_id`
- `subject_type` (`policy`, `share`, `peer`, `route`)
- `subject_id`
- `baseline_publication_profile_ref`
- `active_route_leases[]`
- `currently_published_to[]` (`lan`, `approved-peer`, `private-infra`, `public-infra`)
- `published_endpoint_classes[]`
- `candidate_route_classes[]`
- `widening_steps[]`
- `cached_endpoint_findings[]`
- `recommended_actions[]`
- `generated_at`
- `decision_trace_ref` nullable

Questions it answers:

- if I apply this policy or lease, who learns what?
- which candidates require public infrastructure versus peer-pinned knowledge?
- what remembered state is still relevant?
- what must I clear or revoke to actually narrow exposure?

## Effective route semantics

### Baseline privacy-oriented order

A conservative privacy-oriented policy should generally behave like this:

1. allow LAN direct on real local networks
2. prefer Tor and/or I2P for WAN
3. allow private relay where configured
4. allow peer-pinned known-host direct only when policy or lease explicitly says so
5. keep public direct disabled unless a manual lease or explicit non-private policy allows it

The important point is **not** the exact scoring formula.
The important point is that the operator can inspect both:

- the chosen route class
- the exposure consequences that made it eligible

### Known-host direct path

A peer-pinned known-host path should be able to exist in a middle posture:

- more explicit and narrower than public direct
- faster than overlay in some trusted cases
- still clearly visible as clearnet direct in route output

That gives AnonSync a better answer than “never direct” versus “ambient public direct”.

### Temporary direct-speed lease

A manual speed window should ordinarily compile to a route lease.
The interface should show:

- baseline: `public-direct = disabled` or `lease-only`
- lease: `allow-public-direct` for a concrete subject
- current route: `public-direct active because lease rls_... is in effect`

When the lease ends, the active route should be re-evaluated without mutating the baseline policy object.

## CLI contract

### `anonsync exposure`

```text
anonsync exposure show --policy privacy-mixed
anonsync exposure show --share media --effective
anonsync exposure show --peer laptop --json
```

Expectations:

- output distinguishes baseline policy from active leases
- output says which infrastructure classes can currently learn reachability
- output shows whether cached endpoints could keep an old wider posture alive

### `anonsync route known-host`

```text
anonsync route known-host add --peer laptop --addr sync.example.net:3847 --share media --ttl 7d --reason "trusted home uplink"
anonsync route known-host list --peer laptop
anonsync route known-host show kh_01J...
anonsync route known-host remove kh_01J...
```

Expectations:

- adding a known host does not implicitly enable public tracker/direct behavior
- route output can say when this pin is the reason a direct candidate exists
- stale or expired records remain explainable instead of disappearing mysteriously

### `anonsync route lease`

```text
anonsync route lease create --effect allow-public-direct --share media --peer laptop --ttl 90m --byte-cap 250GiB --reason "trusted bulk transfer"
anonsync route lease list
anonsync route lease show rls_01J...
anonsync route lease cancel rls_01J...
```

Sugar commands such as `anonsync route allow-clearnet-direct ...` may exist, but they should compile into an ordinary first-class route lease.

## API mapping

Suggested resources:

```text
GET    /v1/exposure/reports
POST   /v1/exposure/reports
GET    /v1/exposure/reports/{exposure_report_id}
GET    /v1/known-hosts
POST   /v1/known-hosts
GET    /v1/known-hosts/{known_host_id}
DELETE /v1/known-hosts/{known_host_id}
GET    /v1/route-leases
POST   /v1/route-leases
GET    /v1/route-leases/{route_lease_id}
DELETE /v1/route-leases/{route_lease_id}
```

`POST /v1/route-leases` should accept at least:

- effect
- scope / subject
- peer reference where relevant
- TTL
- optional byte cap or transfer cap
- reason
- expected baseline policy version where relevant

## Non-goals for v1

This document does **not** require:

- a perfect universal route-scoring formula up front
- per-connection I2P sessions
- hidden automatic escalation from known-host direct to public direct
- ambient tracker usage merely because a peer once needed it
- public-discovery defaults for Linux-first v1

## Bottom line

The point of this spec is simple:

> AnonSync should make “what gets published”, “what may be dialed”, “which direct path is explicitly trusted”, and “which temporary speed exception is currently active” into first-class supported state.

That is a concrete reason not to merely copy Resilio's more fragmented but still real route-control story.
