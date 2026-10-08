# Vendor-ceiling contract sheet page: service-visible facts and intervention boundary interface spec

## Purpose

The archive already has pages for reachability provenance, disclosure boundary, diagnostic lane, and operator attestation.
What it still lacked was one ordinary page for the narrower question:

> what facts about this sync relationship can outside service infrastructure see, what can vendor staff inspect only after I explicitly send evidence, and what stronger intervention sentence remains blocked?

Current official Resilio docs make this seam concrete.
They separately describe tracker contact, relay carriage, link-fragment opacity, landing-page counting, update checks, license purchase disclosure, `send_statistics`, and user-sent debug bundles.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Vendor-ceiling contract sheet** whenever an operator is shown a privacy claim, service-contact switch, telemetry toggle, evidence-send flow, or abuse/intervention sentence.

The sheet exists to answer seven things in one place:

1. what service contacts exist right now
2. what service-visible facts each contact reveals
3. what remains device-local or fragment-local
4. what bytes may be carried but not inspectable
5. what user-initiated evidence-send lanes exist
6. what vendor intervention authority is actually absent
7. what stronger vendor sentence remains blocked

## Fixed page order

1. **Vendor-ceiling header**
2. **Service-contact matrix**
3. **Visibility and carriage split card**
4. **Intervention-boundary card**
5. **Optional disclosure rail**
6. **Blocked stronger sentence**

### 1) Vendor-ceiling header

Show at minimum:

- `vendor_ceiling_contract_id`
- subject ref or cohort ref
- actor / seat ref
- last service-contact witness time
- strongest safe sentence
- blocked stronger sentence
- current service-contact verdict
- current intervention-ceiling verdict

Supported headline states must include:

- `no-current-service-contact-witness`
- `tracker-visible-metadata-only`
- `relay-ciphertext-carriage`
- `fragment-opaque-landing`
- `user-sent-diagnostics-open`
- `vendor-noncontrol-proven`
- `mixed`
- `unknown`

Example safe sentence:

- `This share currently allows tracker contact and optional relay fallback, but vendor control remains weaker than deletion or revocation authority over user-held copies.`

### 2) Service-contact matrix

Separate these contacts explicitly:

- tracker
- relay
- update check
- landing page / handoff service
- license / billing service
- telemetry / anonymous statistics
- user-sent diagnostics
- vulnerability-report lane

Each row must show:

- contact currently allowed yes/no/unknown
- service-visible facts
- content visibility class (`none`, `metadata-only`, `ciphertext-carried`, `user-sent-artifact`, `unknown`)
- actor who initiated contact (`automatic`, `manual`, `purchase`, `support-send`, `unknown`)
- why it matters

Hard rule:

- one `private` or `cloudless` label must never appear without a visible service-contact matrix.

### 3) Visibility and carriage split card

Separate these truths explicitly:

- data at rest on vendor infrastructure
- metadata exposed during discovery
- ciphertext carriage through third-party services
- fragment-local capability material unseen by landing service
- diagnostics visibility created only by explicit send
- telemetry narrower than operational metadata

Each row must show:

- current verdict
- witness source
- freshness
- strongest safe sentence supported

### 4) Intervention-boundary card

Separate these intervention classes explicitly:

- can observe some metadata
- can count landings or purchases
- can receive evidence if user sends it
- can recommend operator action
- can revoke vendor-issued account or service access
- can directly block peer finding in all cases
- can delete or modify user-held sync data in the mesh

Each row must show:

- yes/no/conditional/unknown
- authority basis
- residual loophole or limitation
- blocked stronger sentence

Hard rule:

- `cannot see my files` must never be allowed to overclaim `cannot learn anything` or `cannot influence anything`.

### 5) Optional disclosure rail

Show optional disclosure surfaces in the order they widen knowledge:

1. allow service contact
2. allow telemetry
3. send debug logs
4. send crash/profiler artifacts
5. submit security disclosure or billing identity

Each item must show:

- who receives it
- what new facts become visible
- what does **not** become visible automatically
- how to reverse or narrow the lane

### 6) Blocked stronger sentence

Always end with one precise blocked stronger sentence, such as:

- `We proved that vendor infrastructure can help introduce or relay peers, but we did not prove vendor power to delete existing copies on user devices.`
- `We proved that no link-specific fragment reached the landing service, but we did not prove that no tracker metadata was ever disclosed.`

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- which vendor-operated or vendor-adjacent services are currently in the loop
- what each one can see
- whether any carried bytes remain unreadable there
- what vendor staff can only inspect after explicit evidence send
- what intervention power is truly absent
