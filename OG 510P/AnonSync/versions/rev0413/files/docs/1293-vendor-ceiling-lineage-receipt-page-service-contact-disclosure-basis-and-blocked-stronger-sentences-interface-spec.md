# Vendor-ceiling lineage receipt page: service contact, disclosure basis, and blocked stronger sentences interface spec

## Purpose

Preserve one durable receipt for later operators who need to know:

- what service contacts were in scope
- what facts could be seen there
- what evidence was sent explicitly
- what intervention authority was absent
- what stronger sentence was blocked

## Receipt fields

Every receipt must preserve, in order:

1. `vendor_ceiling_receipt_id`
2. subject / mesh ref
3. review time
4. current service-contact set
5. service-visible facts summary
6. explicit evidence-send summary
7. intervention-boundary verdict
8. strongest safe sentence
9. blocked stronger sentence
10. reopen triggers

## Canonical sentence shapes

Allowed strongest safe sentences:

- `Vendor-operated services may learn routing/discovery metadata for this subject, but content remains device-held and relay-carried bytes are not proven readable there.`
- `Landing service contact occurred for this claim flow, but capability-bearing fragment material stayed browser-local.`
- `Diagnostic disclosure widened because the operator explicitly sent logs, but vendor-side direct mutation authority over the mesh remained absent.`

Allowed blocked stronger sentences:

- `We did not prove that no metadata ever left the device.`
- `We did not prove that vendor staff can revoke already-held peer knowledge or delete peer-held copies.`
- `We did not prove that optional telemetry disablement also disabled tracker or landing contact.`

## Reopen triggers

Reopen the receipt if any of the following changes:

- tracker, relay, landing, update, telemetry, or billing posture
- diagnostics send or crash-artifact export
- join artifact family or landing path
- vendor-service availability or policy
- mesh governance posture

## Acceptance test

This receipt is good enough when a later operator can answer, from one artifact alone:

- what vendor-adjacent services were involved
- what they could learn
- whether any artifact content was sent intentionally
- what intervention power was never proven
- what event would force a rereview
