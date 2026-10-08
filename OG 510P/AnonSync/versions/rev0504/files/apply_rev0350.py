from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'

files = {
'1240-resilio-reachability-provenance-discovery-route-relay-fallback-and-infrastructure-exposure-fragmentation-evaluation.md': r'''# Resilio reachability-provenance, discovery-route, relay-fallback, and infrastructure-exposure fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- peer discovery is not one thing: tracker introduction, LAN multicast discovery, and predefined hosts are all real and separately configurable
- tracker discovery means the tracker learns the share ID plus public and local IP:port information for the peer
- direct peer connection is preferred after discovery and may happen in LAN first when subnet matches
- if direct connection is not possible, Resilio can fall back to relayed transfer; the relay carries encrypted bytes and is not supposed to store or read them
- the product exposes some fragments of that truth, such as a relay icon in peer view and per-folder toggles for tracker, relay, LAN search, and predefined hosts
- some privacy-sensitive contact points are separate again: bootstrap config download, tracker metadata exchange, relay carriage, and link-landing indirection
- current mobile docs also make clear that a share can be constrained by allowed-network posture while still separately exposing tracker, relay, LAN, and predefined-host choices

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct several materially different questions from several different pages:

1. **how was this peer found?**
2. **how are bytes actually moving right now?**
3. **what outside infrastructure learned anything during that process?**
4. **what fallback path is still permitted if the current route fails?**
5. **which privacy claim is safe, and which stronger one is still blocked?**

Current Resilio docs still spread those answers across security architecture, folder preferences, mobile interface notes, and troubleshooting pages.

So a user can learn all the pieces and still not get one stable product answer to:

> this peer is reachable now, but was that because of tracker introduction, LAN witness, a predefined host, or relay fallback; and what exactly left the local trust boundary along the way?

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow four habits directly:

- **say openly which discovery mechanisms are allowed**
- **say openly which discovery mechanism actually produced the current peer path**
- **say openly when transport is relayed rather than direct**
- **say openly what third-party services learned metadata versus what never left the peer boundary**

But AnonSync should reject five weaker habits:

- boolean settings that do not produce one effective reachability sentence
- relay indicators that say nothing about discovery origin
- privacy language that collapses bootstrap, tracker, relay, and link-landing into one blob
- troubleshooting advice that requires the operator to infer the currently broken rung of the ladder
- route claims like `peer-to-peer` or `direct` when only policy preference, not current route witness, is known

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1241` — Reachability provenance contract sheet
- `1242` — Discovery path review
- `1243` — Transport route proof
- `1244` — Service-contact exposure review
- `1245` — Reachability lineage receipt

These pages keep the Resilio candor and reject the scattered-network-contract problem.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that peer finding, direct connection, relay fallback, and privacy contact points are all different truths; refuse any interface contract where the operator must reconstruct discovery origin, current byte route, and infrastructure exposure from scattered toggles, icons, and troubleshooting prose instead of one explicit reachability object.
''',
'1241-reachability-provenance-contract-sheet-page-discovery-basis-current-route-and-service-contact-exposure-interface-spec.md': r'''# Reachability provenance contract sheet page: discovery basis, current route, and service-contact exposure interface spec

## Purpose

The archive already has pages for path identity, interface affinity, queue policy, presence, and operator attestation.
What it still lacked was one ordinary page for the narrower question:

> how did this peer become reachable, how are bytes routed right now, which service contacts were involved, and what stronger privacy or directness sentence is still blocked?

Current official Resilio docs make this seam concrete.
They separately describe tracker discovery, LAN discovery, predefined hosts, relay fallback, bootstrap config lookup, and link-landing privacy behavior.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Reachability provenance contract sheet** whenever a subject or peer has active or recent network reachability.

The sheet exists to answer six things in one place:

1. what discovery basis introduced the peer
2. what transport route is currently witnessed
3. what service-contact exposure occurred
4. what fallback routes remain allowed
5. what privacy and performance ceilings follow from that state
6. what stronger sentence remains blocked

## Fixed page order

1. **Reachability header**
2. **Discovery basis card**
3. **Current transport card**
4. **Service-contact exposure card**
5. **Fallback ladder**
6. **Claim ceiling and action rail**

### 1) Reachability header

Show at minimum:

- `reachability_contract_id`
- local seat / peer refs
- subject ref
- current status (`unresolved`, `discoverable`, `reachable`, `active-transfer`, `degraded`, `offline`)
- strongest safe sentence
- blocked stronger sentence
- freshness of last route witness

Supported discovery bases must include:

- `tracker-introduced`
- `lan-multicast-introduced`
- `predefined-host-introduced`
- `mixed-or-redundant`
- `manual-imported-address`
- `unknown`

Supported current transport routes must include:

- `direct-lan`
- `direct-wan`
- `relay-carried`
- `route-unknown`
- `no-current-route`

### 2) Discovery basis card

Show discovery rows grouped by source:

- tracker witness
- LAN witness
- predefined-host witness
- manual address / import witness
- negative witness (`disabled`, `blocked`, `untested`)

Each row must show:

- whether the mechanism is allowed
- whether it was actually used
- freshness
- corroborating evidence
- why it won over alternatives

The operator must be able to answer:

> how did we actually find each other, not merely how could we have found each other?

### 3) Current transport card

Show:

- current route class
- directness grade
- last route switch
- current performance ceiling
- route witness source
- listener / address pair in use if safe to reveal
- whether the route is policy-preferred or only fallback

The operator must be able to answer:

> are bytes going direct right now or only relayed right now?

### 4) Service-contact exposure card

Separate these exposure classes explicitly:

- bootstrap config contact
- tracker metadata exchange
- relay carriage
- link-landing service use
- zero-third-party-contact witness
- unknown

Each row must show:

- what infrastructure was contacted
- what data class was exposed (`ip:port`, `share-id`, encrypted payload carriage, aggregate click only, none`)
- whether content bytes were exposed
- whether disablement is possible
- what operational consequence follows if disabled

The operator must be able to answer:

> what left the local trust boundary here?

### 5) Fallback ladder

Show the ordered ladder the system may still try:

- direct via existing peer addresses
- tracker reintroduction
- LAN rediscovery
- predefined-host dialout
- relay fallback
- no permitted fallback

Every rung must show allowed / disabled / unavailable / failed / current status.

### 6) Claim ceiling and action rail

Allowed examples:

- `Tracker introduced peer; current route is direct WAN.`
- `Peer is reachable only by relay-carried transport right now.`
- `No third-party byte carriage was witnessed on the current route.`
- `Bootstrap and tracker contact occurred; payload remained peer-encrypted.`

Blocked examples:

- `No third party learned anything.`
- `This peer is direct-only.`
- `This route is private from infrastructure metadata.`
- `The current fast path will persist.`

Primary actions may include:

- `Review discovery branch`
- `Inspect route proof`
- `Inspect exposure details`
- `Tighten allowed fallback`
- `Export reachability receipt`

## What this page prevents

Without this page, the product quietly conflates policy allowance, discovery origin, active route, and privacy posture.
AnonSync must instead publish one effective reachability sentence with one visible claim ceiling.
''',
'1242-discovery-path-review-page-tracker-lan-predefined-host-and-no-bootstrap-branches-interface-spec.md': r'''# Discovery path review page: tracker, LAN, predefined-host, and no-bootstrap branches interface spec

This page exists so four superficially similar connectivity setups stop pretending to mean the same thing:

- `Use tracker server`
- `Search LAN`
- `Use predefined hosts`
- `disable outside services`

All four affect peer discovery.
They do not create the same discovery contract.

## Operator question

> which discovery branch am I actually choosing here, what service contact does it require, and what reachability promise still remains blocked even if this branch is enabled?

## When this page must appear

Render whenever the operator is about to:

- disable tracker discovery
- disable LAN search in a topology that may still rely on it
- add or remove predefined hosts
- require peer finding to stay inside LAN only
- require discovery to work without contacting external discovery services
- diagnose a `peers not connecting` situation where multiple discovery rungs are plausible

## Fixed page order

1. **Branch chooser**
2. **What this branch requires**
3. **What this branch exposes**
4. **What this branch still does not prove**
5. **Safer weaker alternative**

## 1) Branch chooser

Offer mutually exclusive or explicitly combinable branches such as:

- `Tracker-assisted WAN discovery`
- `LAN-only discovery`
- `Predefined-host mesh`
- `Mixed discovery with fallback`
- `No external discovery services`
- `Abort and inspect current evidence`

The operator must be able to answer: **which discovery policy branch did I actually choose?**

## 2) What this branch requires

For the chosen branch, show minimum requirements:

- `Tracker-assisted WAN discovery` requires tracker reachability and publishes share-matching metadata to the tracker.
- `LAN-only discovery` requires multicast / broadcast visibility inside the target network.
- `Predefined-host mesh` requires accurate address:port knowledge on all peers and may still fail if direct reachability is blocked.
- `No external discovery services` requires that the product has some other provable peer-introduction basis; otherwise reachability is intentionally reduced.
- `Mixed discovery with fallback` requires the operator to accept that different peers may arrive through different origins at different times.

## 3) What this branch exposes

Show the data classes that leave the local trust boundary for this branch:

- tracker metadata only
- encrypted byte carriage possible later
- local multicast presence only
- manual address knowledge only
- no current outside-service contact

The operator must be able to answer: **what extra infrastructure knowledge am I authorizing by choosing this branch?**

## 4) What this branch still does not prove

Examples:

- enabling tracker does not prove direct transport will succeed
- enabling LAN search does not prove cross-subnet visibility
- entering predefined hosts does not prove the addresses are correct or reachable
- disabling tracker does not prove zero third-party contact if relay or link-landing still exists
- mixed discovery does not prove which branch will win for the next peer arrival

The product must say plainly when a branch is merely allowed, not yet witnessed.

## 5) Safer weaker alternative

Always show one weaker branch, for example:

- `Disable relay fallback but leave tracker discovery`
- `Use predefined hosts only for named peers`
- `Allow LAN discovery only on trusted interfaces`
- `Keep discovery unchanged; inspect route proof first`

## Commit rail

Example actions:

- `Commit tracker-assisted discovery`
- `Commit LAN-only policy`
- `Commit predefined-host branch`
- `Commit no-external-discovery policy`
- `Back out and gather more route evidence`

## What this page must never imply

It must never imply that these are the same:

- finding peers and transporting bytes
- disabling tracker and achieving total metadata isolation
- adding a predefined host and proving direct reachability
- seeing a peer once and preserving a durable discovery route forever
''',
'1243-transport-route-proof-page-direct-lan-direct-wan-relay-and-route-switch-evidence-interface-spec.md': r'''# Transport route proof page: direct LAN, direct WAN, relay, and route-switch evidence interface spec

This page exists so `connected` and `relay` stop pretending to answer the whole route question.
The operator often needs to know not only whether a peer is reachable, but **how bytes are actually moving right now** and whether that answer just changed.

## Operator question

> what route is currently carrying data, how strong is the witness for that claim, and what route switch just happened or remains likely?

## When this page must appear

Render whenever the product is about to:

- claim a direct route
- claim relay fallback
- explain a speed or latency drop
- justify why a privacy posture has changed
- explain why tracker success still did not yield transfer
- diagnose route switching between LAN, WAN, and relay states

## Fixed page order

1. **Current route verdict**
2. **Witness stack**
3. **Route-switch timeline**
4. **Performance and privacy ceilings**
5. **Blocked stronger sentence**

## 1) Current route verdict

Show one verdict:

- `direct LAN currently witnessed`
- `direct WAN currently witnessed`
- `relay-carried route currently witnessed`
- `transport reachable but current route unproved`
- `no active transfer route`

The operator must be able to answer: **what route is carrying bytes right now?**

## 2) Witness stack

Possible witness classes include:

- peer-list relay indicator
- negotiated socket witness
- matched local subnet witness
- observed relay endpoint witness
- successful direct transfer witness
- failed direct attempt with relay takeover
- stale configuration-only belief
- no recent witness

Each witness row must show freshness, confidence, and whether it supports directness, relay use, or only possibility.

## 3) Route-switch timeline

Show route transitions such as:

- `tracker introduced -> direct WAN`
- `direct WAN failed -> relay-carried`
- `LAN discovery -> direct LAN`
- `predefined host dialed -> no active transfer`
- `relay-carried -> direct WAN restored`

Each transition row must show cause if known:

- NAT / firewall refusal
- listener unavailable
- relay required
- network changed
- interface audience changed
- cause unknown

## 4) Performance and privacy ceilings

Publish separate ceilings for:

- speed expectation
- latency expectation
- third-party byte carriage
- metadata disclosure already incurred
- route persistence confidence

Examples:

- a direct route may still have metadata exposure from tracker introduction
- a relay route may preserve content confidentiality while losing no-third-party-carriage claims
- a current direct route does not prove the next session will also be direct

## 5) Blocked stronger sentence

Allowed examples:

- `Current transfer is relayed; content remains peer-encrypted.`
- `Direct WAN route is currently witnessed after tracker introduction.`
- `No recent route witness exists despite allowed direct policies.`

Blocked examples:

- `This peer never used relay.`
- `No infrastructure ever learned about this share.`
- `Direct route is guaranteed from now on.`
- `Current slow speed is caused only by relay.`

## Main actions

Examples:

- `Open discovery branch review`
- `Export route proof`
- `Tighten fallback ladder`
- `Inspect service-contact exposure`
''',
'1244-service-contact-exposure-review-page-bootstrap-tracker-relay-and-link-landing-disclosure-interface-spec.md': r'''# Service-contact exposure review page: bootstrap, tracker, relay, and link-landing disclosure interface spec

This page exists because `private`, `peer-to-peer`, and `encrypted` are not enough.
A system can keep payload content private while still contacting several outside services for bootstrap, metadata introduction, or relayed carriage.

## Operator question

> which external service contacts occurred or remain allowed here, what did each service learn, and which stronger privacy sentence is still blocked?

## When this page must appear

Render whenever the operator is about to:

- tighten or relax network privacy posture
- disable tracker or relay and expect a privacy win
- use link-based onboarding
- explain why a supposedly direct system still contacted Resilio-operated infrastructure
- claim `no third-party involvement` or reject that claim

## Fixed page order

1. **Exposure summary**
2. **Service rows**
3. **Content-exposure boundary**
4. **Disablement consequences**
5. **Claim ceiling**

## 1) Exposure summary

Show, at minimum:

- exposure verdict (`none witnessed`, `metadata only`, `encrypted byte carriage`, `mixed`, `unknown`)
- strongest safe sentence
- blocked stronger sentence
- whether the exposure is current, historical, or merely allowed

## 2) Service rows

Required service rows:

- bootstrap config service
- tracker service
- relay service
- link-landing service
- update / auxiliary service if relevant
- `none / disabled / unknown`

Each row must show:

- service class
- contacted / allowed / disabled / not witnessed status
- data classes exposed
- whether payload content was exposed
- whether peer addresses were exposed
- whether share identifier was exposed
- whether the contact is user-initiated, automatic, or inherited from onboarding

## 3) Content-exposure boundary

The page must explicitly separate:

- payload plaintext exposure
- payload encrypted carriage
- metadata exposure only
- aggregate click / landing exposure only
- no current witness

The operator must be able to answer:

> did any external service ever carry my bytes, or only metadata, or neither?

## 4) Disablement consequences

For each disablement option, show the reachable consequence:

- disabling tracker may reduce WAN peer introduction
- disabling relay may reduce last-resort transfer success
- avoiding link landing may change onboarding convenience
- disabling bootstrap / external service contact may require private replacement infrastructure or manual addressing
- none of these alone prove that all historical exposure is undone

## 5) Claim ceiling

Allowed examples:

- `Tracker learned peer-introduction metadata; payload remained peer-encrypted.`
- `Relay carried encrypted payload; plaintext remained unavailable to the service.`
- `Link landing counted access without seeing the anchor-contained share specifics.`

Blocked examples:

- `No third party learned anything at all.`
- `Encrypted relay use equals no external carriage.`
- `Disabling tracker after the fact erases prior metadata exposure.`
- `Private onboarding guarantees zero service contact everywhere.`

## Main actions

Examples:

- `Disable tracker for this subject`
- `Disable relay fallback`
- `Require manual addressing`
- `Export exposure receipt`
- `Open discovery branch review`
''',
'1245-reachability-lineage-receipt-page-discovery-basis-route-witness-and-exposure-ceiling-interface-spec.md': r'''# Reachability lineage receipt page: discovery basis, route witness, and exposure ceiling interface spec

Every network-reachability decision that materially affects connectivity claims or privacy claims must emit one durable receipt.
This receipt is the audit answer to:

> how was this peer found, what route was actually witnessed, what outside infrastructure was contacted, what fallback remained allowed, and what stronger sentence stayed blocked?

## Receipt fields

- `reachability_receipt_id`
- `reachability_contract_id`
- `subject_ref`
- `peer_ref`
- `discovery_basis`
- `discovery_evidence[]`
- `current_route_class`
- `route_witness[]`
- `service_contacts[]`
- `exposure_verdict`
- `fallback_ladder[]`
- `performance_ceiling`
- `privacy_ceiling`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `issued_at`

## Human-readable layout

### 1) Discovery summary

State in one sentence how the peer was introduced.

Example:

- `Peer was introduced by tracker and later moved onto a direct WAN route.`

### 2) Route witness

List the witness classes that justify the current route claim and keep stale or contradictory witnesses visible.

### 3) Service-contact exposure

List which outside services were contacted and what data classes each service could see.

### 4) Fallback ceiling

Show what still remains allowed after the current state:

- relay still allowed
- tracker still allowed
- predefined hosts still armed
- LAN rediscovery still armed
- no remaining fallback

### 5) Blocked stronger sentence

Keep the strongest forbidden sentence permanently adjacent to the receipt.

Example:

- `Blocked: no third-party service learned anything about this share or its peers.`

## Example compact receipt rows

```text
tracker-introduced     direct WAN currently witnessed     tracker saw share-introduction metadata     relay still allowed     blocked: direct-only private route
```

```text
predefined-host-introduced     no current route witness     no tracker contact witnessed     relay disabled     blocked: peer is presently reachable
```

```text
mixed discovery     relay-carried route witnessed     encrypted payload carried by relay     tracker historical contact present     blocked: zero third-party carriage
```

## Rules

### Rule 1 — receipts must separate discovery from transport

Do not let `relay` erase tracker introduction or let `tracker` imply direct transport.

### Rule 2 — receipts must separate metadata exposure from content exposure

A relay that cannot read content is still not the same as zero third-party carriage.

### Rule 3 — later directness does not erase earlier exposure

A direct route now does not cancel the fact that tracker or relay contact may already have occurred.
''',
}

status_addendum = r'''## Revision addendum — reachability provenance, discovery route, and infrastructure exposure truth after rev0349

This tranche locks the next seam around **reachability provenance and transport-exposure truth**.
The key decisions now made explicit in the archive are:

- **reachability provenance is a first-class product state rather than a side effect of `connected`, `offline`, or `relay` badges**
- **discovery basis, current transport route, infrastructure exposure, and policy allowance are different truths**
- **tracker introduction, LAN discovery, predefined-host dialout, mixed discovery, and no-current-witness are different origin classes**
- **direct route is weaker than privacy isolation proof, and relay encryption is weaker than no-third-party carriage**
- **every serious connectivity event now needs one receipt that preserves discovery basis, route witness, service-contact exposure, fallback ladder, and the blocked stronger sentence**

New docs added in this tranche:

- `1240-resilio-reachability-provenance-discovery-route-relay-fallback-and-infrastructure-exposure-fragmentation-evaluation.md`
- `1241-reachability-provenance-contract-sheet-page-discovery-basis-current-route-and-service-contact-exposure-interface-spec.md`
- `1242-discovery-path-review-page-tracker-lan-predefined-host-and-no-bootstrap-branches-interface-spec.md`
- `1243-transport-route-proof-page-direct-lan-direct-wan-relay-and-route-switch-evidence-interface-spec.md`
- `1244-service-contact-exposure-review-page-bootstrap-tracker-relay-and-link-landing-disclosure-interface-spec.md`
- `1245-reachability-lineage-receipt-page-discovery-basis-route-witness-and-exposure-ceiling-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `connected` can no longer hide whether peers were introduced by tracker, LAN discovery, or predefined hosts
- `relay` can no longer hide the difference between encrypted third-party carriage and true peer-direct transport
- privacy review now keeps config bootstrap, tracker metadata disclosure, relay carriage, and link-landing indirection adjacent instead of scattering them across security and troubleshooting prose
- route switches now publish whether the system merely allowed direct transport or actually proved a direct lane at this moment
- later operators can open one receipt and see how peers were found, how bytes were routed, what outside infrastructure was contacted, and what stronger sentence was still blocked

'''

for name, content in files.items():
    (DOCS / name).write_text(content.strip() + '\n', encoding='utf-8')

status_path = DOCS / '00-status.md'
old = status_path.read_text(encoding='utf-8')
if not old.startswith(status_addendum):
    status_path.write_text(status_addendum + old, encoding='utf-8')
