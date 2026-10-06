# Breakglass supplementary accepted case-object proof stays remote-protection-shaped when visible

**Tier:** B (Cross-cutting breakglass/export boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Bundles, Broker→Lease→Receipt, Adapter→Shadow→Replace

`docs/711` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`docs/712` then fixed that supplementary breakglass adapter/runtime material stays receipt-first on typed redaction/export/transport proof when it travels.
`docs/713` then fixed that the same portable story still needs the exact `breakglass.receipt` digest.
`docs/714` then fixed that portable supplementary evidence stays artifactized and off live control locators.
`docs/715` then fixed that portable supplementary evidence must stay payload-anchored to at least one passive artifact digest or accepted case-object proof.
`docs/716` then fixed that accepted case-object proof must stay object-exact on the accepted remote attachment/object/message-part.
`docs/717` then fixed that the same accepted-case-object lane must stay validator-pinned when the adapter can see a stronger revision/version/generation/ETag-like validator for that exact accepted object.

That still leaves one small but expensive seam:
**if the portable story already names the exact accepted object and its visible validator, can it still quietly treat any accepted portal copy as durable evidence even when the adapter can also see a protection / retention / hold posture for that same accepted object?**

## Accepted boundary

Keep accepted case-object proof **remote-protection-shaped when visible**.

If richer supplementary breakglass adapter/runtime material travels portably and the payload anchor uses accepted case-object proof, keep the exact accepted remote attachment/object/message-part identity from `docs/716`.
Then, when the adapter can also see a recipient-side protection / retention / hold posture for that same accepted remote object, keep that posture aligned too.

The portable story should still read like:

- exact `breakglass.receipt` digests for typed emergency authority proof,
- typed `redaction.receipt` / `export.receipt` / `transport.receipt` handling proof,
- an object-exact accepted case-object proof when that lane stands in for payload identity,
- the strongest visible remote validator for that exact accepted object when the adapter can actually see one,
- and the strongest visible remote protection posture for that same accepted object when the adapter can actually see one.

## What this means in practice

### Object-exact and validator-pinned are still the floor

This cut does not weaken `docs/716` or `docs/717`.
The accepted-case-object lane still has to name the exact remote attachment/object/message-part, and when a revision/version/generation/ETag-like validator is visible it still has to keep that validator pinned.
A parent case/ticket/thread/container id is still context only.

### Accepted does not automatically mean durable

Some portals or object stores expose explicit hold/retention/immutability posture for the accepted remote object.
If the adapter can see that stronger recipient-side posture, keep it.
Do not quietly treat any accepted portal object as durable evidence by implication when the same remote system is already saying something more specific about overwrite/delete resistance.

### Keep the strongest visible protection posture, not a fake one

This rule is conditional on visibility.
If the adapter can see a retain-until window, legal hold, policy-locked retention, append-only posture, versioned noncurrent retention, or another opaque reviewed protection claim for the exact accepted object, preserve it.
If the adapter cannot see one, do not invent a pretend durability claim just to satisfy the archive.
In that case the `docs/716` object-exact floor and `docs/717` validator-pinned floor still apply.

### This still stops short of the stronger packet-export stack

This cut does **not** require the whole stronger packet-export continuity stack for breakglass supplementary evidence.
It does not standardize remote locator continuity or metadata-only reverification here.
It only fixes the smaller next floor worth locking now:
accepted case-object proof should keep the strongest visible remote protection posture for that exact accepted object when the adapter can see one.

## Why this is the right narrow cut

The same durability lesson already exists elsewhere.
`docs/523` fixed stronger packet-capture export so recipient-side proof must keep one explicit `remote_protection` posture instead of calling any accepted upload durable evidence by implication.
Current object stores expose the same distinction in different words: Amazon S3 Object Lock separates retention periods from legal holds and says those controls prevent object versions from being overwritten or deleted; Azure immutable blob storage documents time-based retention and legal holds as WORM posture; and Google Cloud Storage Object Retention Lock lets objects retain a configuration that can keep retention from being reduced or removed.
DeriveBSD does not copy any one provider API, but it should keep the same boring truth surface here:
**if accepted case-object proof is going to stand in for payload identity and the adapter can see recipient-side overwrite/delete-resistance posture for that exact accepted object, keep it too instead of collapsing durable-evidence claims back into portal folklore.**

## First spec cut

The implementation cut is intentionally small:

- tighten `incident.bundle.includes.extra[]` and nearby bundle/breakglass docs so accepted case-object proof stays remote-protection-shaped when the adapter can see a protection / retention / hold posture for the same accepted object
- refresh the example bundle so the richer breakglass side-evidence trail shows an object-exact accepted-case-object proof placeholder that is validator-pinned and remote-protection-shaped
- add a guardrail that fails if the archive stops saying visible protection posture on accepted external objects must stay aligned instead of being dropped

## What this does *not* decide

This cut does **not** decide:

- the future typed family for richer breakglass adapter-side evidence
- the exact typed schema for accepted case-object proof in that future family
- whether breakglass supplementary evidence should later require remote-locator continuity too
- or which support portals/case systems are approved to host accepted external case objects

It decides only the smaller boundary worth locking now:
**when accepted case-object proof is already object-exact and validator-pinned and the adapter can see a recipient-side protection posture, keep that posture aligned too.**

## Related docs

- ADR: `adrs/ADR-0308-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md`
- accepted-case-object exactness floor: `docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md`
- accepted-case-object validator continuity floor: `docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md`
- packet-capture remote-protection inspiration: `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`
- authority-first bundle contract: `docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`
- receipt-first supplementary export boundary: `docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`
- payload-anchor boundary: `docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support bundle contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- guardrail: `tools/check_breakglass_adapter_case_object_remote_protection_boundary.py`

## References

- AWS S3 Object Lock (retention periods + legal holds): https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
- Azure immutable blob storage overview (time-based retention + legal holds as WORM posture): https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview
- Google Cloud Storage Object Retention Lock (retention configuration on objects): https://docs.cloud.google.com/storage/docs/object-lock

Last updated: 2026-03-23r449
