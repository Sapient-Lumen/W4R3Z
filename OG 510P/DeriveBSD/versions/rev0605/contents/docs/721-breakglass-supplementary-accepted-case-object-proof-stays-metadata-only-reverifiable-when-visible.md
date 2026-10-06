# Breakglass supplementary accepted case-object proof stays metadata-only reverifiable when visible

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
`docs/719` then fixed that the same visible protection posture must stay exact to the same accepted object revision/version rather than collapsing into ambient case/container/bucket policy.
`docs/720` then fixed that, when the adapter can also see a safe redacted/non-secret passive locator for that same accepted object revision/version, the portable story must keep that object-exact locator aligned too rather than sending later review back to parent-page folklore.

That still leaves one small but expensive seam:
**if the portable story already names the exact accepted object, its visible validator, any object-exact visible protection posture, and a safe object-exact locator, can later follow-up still collapse back into screenshots, portal clicking, or another body download instead of one typed metadata-only reverification of the same accepted object revision/version?**

## Accepted boundary

Keep accepted-case-object follow-up on **metadata-only reverification when visible**.

If richer supplementary breakglass adapter/runtime material travels portably and the payload anchor uses accepted case-object proof, keep the exact accepted remote attachment/object/message-part identity from `docs/716`.
Then, when the adapter can also see a revision/version/generation/ETag-like validator for that exact accepted object, keep it pinned as `docs/717` already requires.
And when the adapter can also see a protection / retention / hold posture, keep that posture exact to the same accepted object revision/version as `docs/719` already requires.
And when the adapter can also see a safe redacted/non-secret passive locator for that same accepted object revision/version, keep that locator aligned as `docs/720` already requires.
Finally, when the adapter can later metadata-check that same accepted object revision/version without re-downloading the body, the canonical follow-up evidence object is `transport.reverification.receipt` with `reverification.body_downloaded = false`.

The portable story should still read like:

- exact `breakglass.receipt` digests for typed emergency authority proof,
- typed `redaction.receipt` / `export.receipt` / `transport.receipt` handling proof,
- an object-exact accepted case-object proof when that lane stands in for payload identity,
- the strongest visible remote validator for that exact accepted object when the adapter can actually see one,
- the strongest visible remote protection posture for that same accepted object revision/version when the adapter can actually see one,
- the strongest honest redacted/non-secret locator for that same accepted object revision/version when the adapter can actually see one,
- and, when the adapter can later re-check that same accepted object revision/version without another artifact/body download, a typed `transport.reverification.receipt` proving metadata-only reverification of the same accepted object.

## What this means in practice

### Screenshots and body re-downloads are no longer the canonical follow-up proof

This cut does not ban screenshots or later downloads from existing somewhere else in the world.
It does make them non-canonical for this lane.
If the adapter can honestly re-check the same accepted object revision/version over metadata only, the archive should use `transport.reverification.receipt` rather than treating UI screenshots or another body download as equivalent portable proof.

### The same accepted object continuity floor still applies

This cut does not weaken `docs/716` through `docs/720`.
The accepted-case-object lane still has to stay object-exact, validator-pinned when visible, protection-exact when visible, and remote-locator-continuous when visible.
Metadata-only reverification is follow-on evidence about that same accepted object revision/version, not a looser alternative to those earlier boundaries.

### Keep reverification honest and metadata-first

If the adapter can honestly do a `HEAD`-style or metadata-API check for the same accepted object revision/version, preserve the result as `transport.reverification.receipt`.
If the adapter must download the body, click through a browser portal manually, or use a secret-bearing/live-control lane just to prove the object still exists, do not pretend that is the same thing.
In that case omit reverification and keep the earlier floor only.

### This still stops short of profile-required polling or a new typed family

This cut does **not** require every product shape or adapter to perform scheduled reverification.
It does **not** mint a breakglass-specific reverification schema.
It simply fixes the next coherence boundary worth standardizing now:
when metadata-only reverification of the same accepted object revision/version is honestly visible, keep later proof on typed `transport.reverification.receipt` instead of screenshots, portal clicking, or another artifact/body download.

## Why this is the right narrow cut

The same metadata-first lesson already exists in common protocols and stores.
RFC 9110 defines `HEAD` as a method that returns representation metadata without a response body.
Amazon S3 `HeadObject` retrieves object metadata without returning object bytes and keeps object-version lookup explicit through `versionId`.
Azure `Get Blob Properties` likewise returns properties/metadata without blob content for the specified blob or version.
DeriveBSD does not copy any one provider API, but it should keep the same boring truth surface here:
**if accepted case-object proof is going to stand in for payload identity and the adapter can later re-check that same accepted object revision/version over metadata only, keep that follow-up proof on typed `transport.reverification.receipt` instead of another body download or portal screenshot ritual.**

## First spec cut

The implementation cut is intentionally small:

- tighten `incident.bundle.includes.extra[]` and nearby bundle/breakglass docs so accepted case-object proof can carry typed metadata-only reverification when visible
- add dotted generic examples showing a breakglass accepted-case-object export / acceptance / reverification chain on the same object-exact revision
- add a guardrail that fails if the archive stops saying the same accepted object revision/version should use `transport.reverification.receipt` with `reverification.body_downloaded = false` instead of screenshots or body-download folklore

## What this does *not* decide

This cut does **not** decide:

- the future typed family for richer breakglass adapter-side evidence
- whether every adapter or product profile must perform periodic accepted-case-object reverification
- whether metadata-only reverification should later require a fresh remote digest when one is available
- or which support portals/case systems are approved to host accepted external case objects

It decides only the smaller next boundary worth locking now:
**when accepted case-object proof is already object-exact, validator-pinned when visible, protection-exact when visible, locator-continuous when visible, and the adapter can later re-check that same accepted object revision/version over metadata only, keep the follow-up proof on `transport.reverification.receipt` instead of letting later review regress into screenshots or body-download folklore.**

## Related docs

- ADR: `adrs/ADR-0311-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md`
- accepted-case-object exactness floor: `docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md`
- accepted-case-object validator continuity floor: `docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md`
- accepted-case-object visible protection floor: `docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md`
- accepted-case-object visible protection exactness floor: `docs/719-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md`
- accepted-case-object visible locator floor: `docs/720-breakglass-supplementary-accepted-case-object-proof-stays-remote-locator-continuous-when-visible.md`
- packet-capture remote-reverification inspiration: `docs/525-packet-capture-strong-export-remote-reverification-boundary.md`
- transport reverification receipt: `spec/transport.reverification.receipt.schema.json`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support bundle contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- guardrail: `tools/check_breakglass_adapter_case_object_reverification_boundary.py`

## References

- RFC 9110: HTTP Semantics (HEAD returns representation metadata without a response body): https://www.rfc-editor.org/rfc/rfc9110
- Amazon S3 `HeadObject` (retrieve object metadata without returning object bytes): https://docs.aws.amazon.com/AmazonS3/latest/API/API_HeadObject.html
- Azure `Get Blob Properties` (returns metadata/properties without returning blob content): https://learn.microsoft.com/en-us/rest/api/storageservices/get-blob-properties

Last updated: 2026-03-23r452
