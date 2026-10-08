# Resilio control-endpoint attribution, browser target, and runtime watermark evaluation

## Why this pass exists

The archive already had control launch, listener endpoint, control-grade, runtime profile, and access-recovery pages.
What it still did not own cleanly enough was one ordinary operator question that sits underneath all of them:

- which runtime am I actually controlling from this browser surface
- what durable storage and identity world back that endpoint
- did a service/profile/config change keep me in the same control world or move me to a sibling one
- is the current warning or auth problem about endpoint mismatch, transport trust, or genuine state loss
- what sentence is the product actually allowed to let me say about this surface right now

Current official Resilio docs still make that seam materially real.
They still say WebUI defaults differ by host class and install lane.
They still say Linux can run multiple instances and that later instances need manually separated ports.
They still say storage path and config path determine where settings, identity details, and logs live.
They still say service install on Windows may migrate the old world or instead open a clean one in a new browser tab.
They still say password-reset paths have materially different side effects.
They still say HTTPS browser warnings may be about self-signed posture or browser residue rather than one flat endpoint truth.
And the current v3 line still appears active through `3.1.2.1076`.

That candor is useful.
The non-clone problem is workflow ownership.
Resilio still leaves the ordinary browser/admin sentence spread across several articles instead of one stable page family.

## What current Resilio gets right

Resilio is not pretending that control is simple.
Its current docs still acknowledge at least these real boundaries:

- `host:port` is configurable and host-class dependent
- loopback and LAN-visible listener scopes are materially different
- `service`, `app`, `config-mode`, and `headless Linux` are materially different control lanes
- storage-root choice changes which settings and identity details are active
- browser-trust recovery and credential recovery have different collateral effects
- a newly opened control tab after service install may represent migrated continuity or a clean service world

That is good product honesty.
AnonSync should keep that level of candor.

## What current Resilio still leaves fragmented

Current official docs still make the operator reconstruct the full answer to `which control world is this?` from several places:

- `Configuring WebUI` explains default endpoints, listener widening, password optionality, HTTPS posture, and browser-link limitations.
- `Guide to Linux` explains no-GUI operation, multiple instances, explicit storage, and listener/bind failure conditions.
- `Running Sync as a service on Windows` explains migrate-vs-clean service install and that WebUI opens in a new browser tab.
- `Running Sync in configuration mode` explains how config and storage_path define a new settings world.
- `CLI on Windows` explains launch switches that select config/storage behavior.
- `How do I reset my WebUI password?` explains that different recovery paths hit different state and have different collateral effects.
- `Browser warning` explains that certificate/trust problems may be endpoint posture, click-through, or browser residue.

The operator therefore still has to do archaeology to answer one simple question:

> this tab accepted my login and loaded a page, but what exactly have I reached?

## Why this is a strong non-clone reason

This is not just an admin convenience issue.
It changes claim ceilings.
Without a first-class endpoint-attribution object, the product can accidentally let operators say things that are stronger than the evidence supports, such as:

- `I am controlling the same seat as before`
- `this password reset fixed the right runtime`
- `this empty roster means data is gone`
- `this browser warning means the endpoint itself is wrong`
- `this service install preserved continuity`

All of those can be false for reasons the docs themselves already admit are real.

## Better product move for AnonSync

AnonSync should not clone a browser/admin contract that treats the URL, the tab, or successful auth as enough identity.
It should instead make **control-endpoint attestation** first-class.

That means every serious control entry should publish, in one stable reviewed object:

- runtime watermark
- storage lineage
- seat-lineage verdict
- endpoint audience/auth/transport grade
- browser-residue delta when relevant
- strongest safe sentence
- stronger forbidden sentence

## New page family required

This pass therefore adds four explicit replacements:

1. **Control endpoint attestation** — what runtime world this endpoint belongs to now.
2. **Endpoint switch review** — what changes if port/listener/profile/storage/config moves.
3. **Browser target proof** — whether this tab/handler/manual open matched the intended runtime.
4. **Control endpoint receipt** — durable post-action language and evidence bundle.

## Condensed design verdict

Borrow Resilio's candor that ports, listeners, service profiles, config paths, storage roots, and browser-trust states are materially real.
Do not clone a product contract where the operator still has to reconstruct endpoint identity from six help articles and a remembered URL.