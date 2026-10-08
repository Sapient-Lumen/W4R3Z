# Service-visible-facts review page: tracker, relay, landing, telemetry, and support-send interface spec

## Purpose

This page exists for the ordinary dispute:

> the product says `private`, but I still want the exact list of facts that outside services can learn, carry, count, or receive.

## Core decision

AnonSync must expose one **Service-visible facts review** whenever privacy or cloudlessness language is shown next to active discovery, relay, landing, billing, telemetry, or support-send lanes.

## Review rails

### Rail 1 — discovery-visible facts

Show exactly what tracker-like services may learn:

- public IP address
- local IP address if applicable
- listening port
- share / subject identifier class
- contact freshness
- whether the service learns content or only routing/discovery metadata

Allowed verdicts:

- `metadata-only-discovery`
- `discovery-contact-disabled`
- `discovery-visibility-unknown`

### Rail 2 — carriage-visible facts

Show exactly what relay-like services may do:

- carry ciphertext yes/no
- store content at rest yes/no/unknown
- decrypt capability yes/no/unknown
- route witness available yes/no
- route icon or other proof surface

Allowed verdicts:

- `ciphertext-carried-not-readable`
- `direct-only-no-relay-witness`
- `relay-eligibility-open-but-not-currently-witnessed`

### Rail 3 — landing and fragment-visible facts

Show exactly what a landing page or browser handoff service sees:

- click count or landing count
- browser and timestamp class if known
- whether capability-bearing material is entirely after a `#` fragment
- whether the service sees share/folder identity or only a generic landing request

Hard rule:

- capability-bearing fragment opacity must stay separate from overall service invisibility.

### Rail 4 — telemetry and update-visible facts

Show exactly what optional update/telemetry lanes expose:

- update-check enabled yes/no
- anonymous statistics enabled yes/no
- OS / version / active-state style facts exposed
- billing identity or license email exposed
- user-controlled narrowing switch

### Rail 5 — explicit evidence-send facts

Show exactly what support-send changes:

- debug logs
- crash dumps
- profiler traces
- redaction status
- recipient lane
- staffed review certainty vs no-certainty

## Output contract

The page must end with five short answers:

1. `Services contacted automatically:`
2. `Services contacted only by explicit user send:`
3. `Facts visible without any user send:`
4. `Facts still opaque to services:`
5. `Strongest blocked stronger sentence:`

## Honest outputs

This page may conclude:

- `tracker sees routing metadata but not content`
- `relay can carry ciphertext without decrypt authority`
- `landing service counts link visits but not fragment-contained capability material`
- `telemetry is narrower than tracker metadata and separately controllable`
- `vendor staff gain artifact visibility only after explicit evidence send`

It may not compress these into one generic `vendor cannot see anything` or `vendor can see metadata` sentence.
