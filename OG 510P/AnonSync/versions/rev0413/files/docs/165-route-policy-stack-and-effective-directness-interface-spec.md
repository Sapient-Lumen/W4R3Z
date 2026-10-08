# Route-policy stack and effective-directness interface spec

## Purpose

The archive already has route, disclosure, and transport objects.
What it still lacked was a concrete operator surface for the layered route-policy seam:

> if directness, discovery, and fallback are influenced by subject policy, machine defaults, temporary leases, known hosts, learned route memory, and public-discovery posture, what one page tells the operator **how this subject will actually try to move bytes now**?

Current Resilio docs keep this problem vivid.
Route truth still spans Folder Preferences, power-user settings, config mode, ports/protocols notes, LAN-only recipes, and cached-endpoint cleanup ritual.
AnonSync should not clone that archaeology.

## Core decision

Every subject with non-trivial route policy must have one canonical **effective route** surface.
That surface answers four questions together:

1. how this subject is currently allowed to discover peers
2. how it is currently allowed to move bytes
3. which stronger or weaker route classes are merely available versus actually preferred
4. what older learned route residue still survives after recent policy changes

The operator should never need to combine a share dialog, a global preferences page, a config file, and a support article just to answer `why is this share still going over that path?`

## The fixed explanation order

The effective-route surface should render the same sections in the same order:

1. **Effective route answer now**
2. **Allowed and blocked mechanisms**
3. **Winning route stack**
4. **Published and learned facts**
5. **Residue and expiry**
6. **Where to edit safely**
7. **How to narrow or widen deliberately**

## 1) Effective route answer now

Show, at the top:

- current route class (`lan-direct`, `known-host-direct`, `overlay`, `public-direct`, `relay`, `waiting`, `blocked`)
- whether this is preferred, tolerated fallback, or temporary lease behavior
- the strongest current bottleneck explanation
- whether the answer is stable, degraded, provisional, or residue-affected

The operator should be able to answer:

> how will this share most honestly try to find peers and move bytes right now?

## 2) Allowed and blocked mechanisms

The surface should then show a mechanism matrix such as:

- LAN discovery
- known-host dial
- overlay rendezvous
- public tracker discovery
- relay transfer
- cached learned endpoints
- manual peer pinning

For each mechanism, show:

- allowed / blocked / temporary / stale
- layer that decided it
- whether it affects discovery only, transfer only, or both
- whether it discloses endpoint or share facts to any audience outside the current trust boundary

This prevents one vague `LAN only` or `relay off` label from pretending the route story is finished.

## 3) Winning route stack

The surface should expose one ordered stack, for example:

1. emergency containment override
2. temporary transport lease
3. subject-local route exception
4. subject baseline policy
5. seat or machine transport default
6. rollout/imported baseline
7. built-in product default

For each layer show:

- requested discovery posture
- requested directness / relay posture
- route-class preference order
- whether the layer is winning, shadowed, or only constraining

A subject may have several layers that agree on `no public tracker` while disagreeing on known-host, overlay, or relay fallback.
The operator should be able to see that at one glance.

## 4) Published and learned facts

The route page should not talk only about connection success.
It should also say what route policy implies about fact exposure and learned state:

- which audiences may currently learn endpoint facts
- which audiences may learn share-membership or subject-presence facts
- whether the system is still carrying previously learned public endpoints
- whether manual known-host records remain active even though broader public discovery is off

This is where route truth and disclosure truth meet.
If the operator still has to leave the page to discover that a route narrowing did not clear older learned endpoints, the model is incomplete.

## 5) Residue and expiry

Every effective-route page should include a residue strip with answers like:

- `no known residue`
- `one retained public endpoint still eligible until TTL expires`
- `manual known-host pin still allows direct connection even though public discovery is off`
- `relay lease remains active for 18 more minutes`
- `policy narrowed, but cache clear still pending`

The strip should also say what will end the residue:

- wait for TTL
- clear learned endpoints now
- end temporary lease
- remove manual host record
- rotate route artifact / endpoint set
- re-evaluate once active session drains

## 6) Where to edit safely

The route surface should not offer one generic `Edit` button.
It should say what kind of edit the operator is about to perform:

- edit subject route baseline
- create subject exception
- issue temporary speed/directness lease
- edit machine transport defaults
- inspect known-host records
- inspect disclosure profile
- clear learned endpoint residue

This is how the product avoids recreating a route model where half the meaning hides behind whether the change was made per-share, globally, or in a config file.

## 7) How to narrow or widen deliberately

A route mutation drawer should preview:

- which discovery mechanisms stop immediately
- which transfer paths stop only after sessions drain
- which learned endpoint residue still survives
- whether a restart or daemon reload is required
- whether the action narrows only future discovery or also clears old learned state

The operator should never have to remember that one route change needs a second hidden cache action before it becomes semantically true.

## Dense table rules

Worklists may summarize route truth with compact chips:

- effective route class
- discovery posture
- source layer
- residue chip
- next safe action

Expanding the row should open the full route stack, not bounce the operator through several settings families.

## CLI rules

CLI should support:

```text
anonsync route show --subject shr_docs --effective --explain
```

The output should include:

- effective route class now
- allowed and blocked mechanisms
- winning layer stack
- active residue
- strongest next action if the operator wants narrower or broader posture

A headless operator should not be second-class here.

## What the product must refuse

- one `LAN-only` toggle whose real effect still depends on hidden global state
- route pages that show active transport but not why it is active
- policy pages that hide surviving learned endpoints after narrowing
- relay/direct labels with no indication whether they are preferred, tolerated, or only residue-backed
- separate discovery and transfer surfaces whose combined meaning is required to understand one subject

## Result

A good effective-route surface prevents five failures:

- route-policy archaeology across share, machine, config, and support surfaces
- confusing blocked public discovery with total lack of learned direct paths
- failing to notice that relay use is temporary lease behavior rather than standing baseline
- treating known-host pins and broader public discovery as the same kind of directness
- narrowing discovery policy without noticing that older learned endpoint residue still survives

If an operator still needs four different pages and one support memory to answer `why is this share taking this path right now?`, AnonSync has not yet made route truth inspectable enough.
