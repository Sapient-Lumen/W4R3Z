# Breakglass supplementary accepted case-object proof keeps visible remote protection exact to the same object revision

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
`docs/718` then fixed that the same accepted-case-object lane must stay remote-protection-shaped when the adapter can see a protection / retention / hold posture for that exact accepted object.

That still leaves one small but expensive seam:
**if the portable story already names the exact accepted object, its visible validator, and a visible protection posture, can that protection posture still collapse back into ambient case/container/bucket policy rather than the same accepted object revision/version?**

## Accepted boundary

Keep visible accepted-case-object protection posture **exact to the same accepted object revision/version**.

If richer supplementary breakglass adapter/runtime material travels portably and the payload anchor uses accepted case-object proof, keep the exact accepted remote attachment/object/message-part identity from `docs/716`.
Then, when the adapter can also see a revision/version/generation/ETag-like validator for that exact accepted object, keep it pinned as `docs/717` already requires.
And when the adapter can also see a protection / retention / hold posture, keep that posture exact to the same accepted object revision/version rather than satisfying the rule with only a parent case policy, container-wide hold, or bucket default.

The portable story should still read like:

- exact `breakglass.receipt` digests for typed emergency authority proof,
- typed `redaction.receipt` / `export.receipt` / `transport.receipt` handling proof,
- an object-exact accepted case-object proof when that lane stands in for payload identity,
- the strongest visible remote validator for that exact accepted object when the adapter can actually see one,
- and the strongest visible remote protection posture for that same accepted object revision/version when the adapter can actually see one.

## What this means in practice

### Ambient policy is context, not object-exact proof

A parent case SLA, container-level legal hold, or bucket default retention can still be useful context.
But if the adapter can see a stronger posture on the exact accepted object revision/version, that is the posture the portable story should carry.
Do not let ambient storage policy masquerade as object-exact evidence.

### Object-exact + validator-pinned are still the floor

This cut does not weaken `docs/716` or `docs/717`.
The accepted-case-object lane still has to name the exact remote attachment/object/message-part, and when a revision/version/generation/ETag-like validator is visible it still has to keep that validator pinned.
A parent case/ticket/thread/container id is still context only.

### Keep the strongest honest object-version posture, not a fake one

This rule is conditional on visibility.
If the adapter can honestly bind a retain-until window, legal hold, policy-locked retention, append-only posture, versioned noncurrent retention, or another opaque reviewed protection claim to the same accepted object revision/version, preserve it.
If the adapter can only see an ambient case/container/bucket policy and cannot honestly bind it to the accepted object revision/version, do not promote that policy into fake object-exact proof.
In that case the archive keeps `docs/716` + `docs/717` and carries the ambient policy only as context.

### This still stops short of remote-locator continuity or reverification

This cut does **not** require the whole stronger packet-export closure stack for breakglass supplementary evidence.
It does not standardize remote-locator continuity or metadata-only reverification here.
It only fixes the smaller next floor worth locking now:
visible protection posture should stay exact to the same accepted object revision/version instead of collapsing into ambient storage policy.

## Why this is the right narrow cut

The same object-vs-container lesson already exists in current storage systems.
Amazon S3 Object Lock stores lock information in the metadata for the object version and says explicit object-version settings override bucket defaults.
Azure documents both version-level and container-level immutability and says policy precedence is Blob -> Container -> Account.
Google Cloud Storage separates Object Retention Lock from Bucket Lock for the same reason: per-object retention truth is different from a bucket-wide default.
DeriveBSD does not copy any one provider API, but it should keep the same boring truth surface here:
**if accepted case-object proof is going to stand in for payload identity and the adapter can see recipient-side overwrite/delete-resistance posture for that exact accepted object revision/version, keep that object-exact posture instead of collapsing durable-evidence claims back into ambient store folklore.**

## First spec cut

The implementation cut is intentionally small:

- tighten `incident.bundle.includes.extra[]` and nearby bundle/breakglass docs so accepted case-object proof keeps visible protection posture exact to the same accepted object revision/version when the adapter can honestly see that binding
- refresh the example bundle so the richer breakglass side-evidence trail shows an object-exact accepted-case-object proof placeholder that stays validator-pinned and remote-protection exact to the same object revision
- add a guardrail that fails if the archive stops saying object-version-exact visible protection posture on accepted external objects must stay aligned instead of being replaced by ambient case/container/bucket policy

## What this does *not* decide

This cut does **not** decide:

- the future typed family for richer breakglass adapter-side evidence
- the exact typed schema for accepted case-object proof in that future family
- whether breakglass supplementary evidence should later require remote-locator continuity too
- or which support portals/case systems are approved to host accepted external case objects

It decides only the smaller boundary worth locking now:
**when accepted case-object proof is already object-exact and validator-pinned and the adapter can see a recipient-side protection posture, keep that posture exact to the same accepted object revision/version rather than letting ambient storage policy stand in for it.**

## Related docs

- ADR: `adrs/ADR-0309-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md`
- accepted-case-object exactness floor: `docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md`
- accepted-case-object validator continuity floor: `docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md`
- accepted-case-object visible protection floor: `docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md`
- packet-capture remote-protection inspiration: `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`
- authority-first bundle contract: `docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`
- receipt-first supplementary export boundary: `docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`
- payload-anchor boundary: `docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support bundle contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- guardrail: `tools/check_breakglass_adapter_case_object_remote_protection_exactness_boundary.py`

## References

- AWS S3 Object Lock (individual object-version settings, legal holds, and bucket defaults): https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
- Azure immutable storage overview (version-level vs container-level WORM and Blob -> Container -> Account precedence): https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview
- Google Cloud Storage Object Retention Lock (per-object retention) + Bucket Lock (bucket-wide retention): https://docs.cloud.google.com/storage/docs/object-lock and https://docs.cloud.google.com/storage/docs/bucket-lock

Last updated: 2026-03-23r450
